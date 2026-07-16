---
title: "Homelab Project: update monitoring"
date: 2026-06-10
tags:
  - learning
  - homelab

summary: Update Monitoring, Pinning Strategy, and Two Container Migrations
---

This post covers applying automatic updates and notifications to my homelab servers. It ended up touching almost every service on my two Wyse thin clients: a custom update monitor with Pushover notifications, unattended security upgrades, a Docker image pinning strategy, and migrating both my Samba and Unbound containers off abandoned images.

---

## The problem: updates without bricking things

My core worry was simple. The Wyse boxes run the house's DNS, DHCP, VPN, file shares, and game servers. I want to keep everything patched, but I don't want an automatic update to silently break something — especially since the primary server uses LUKS full-disk encryption, so an unexpected reboot leaves it sitting at a passphrase prompt until I intervene.

I started down the road of email notifications (msmtp with Gmail, then M365 so alerts could come from my own domain), but pivoted to [Pushover](https://pushover.net/) — phone notifications with no mail server dependencies, and a dead-simple HTTP API. There's a 30 day free trial, then a flat one off fee of around £5 for each device you require notifications to be sent to.

---

## Am I reinventing the wheel?

Before building anything, I wanted to be sure there wasn't already an existing service. There is partial coverage; DIUN watches Docker images, newreleases.io watches GitHub repos, apticron covers apt. But nothing combined all three sources into one local database with the workflow I wanted:

- Check apt packages, GitHub releases, and Docker image digests
- Write findings to SQLite with a unique key per item (package + version), so re-runs don't duplicate
- Notify anything not yet actioned
- I do the update, then mark it actioned

That "actioned" flag is the heart of it. Updates are never applied automatically — the system nags me, I review release notes, I update deliberately, I mark it done. An audit trail instead of silent changes. By including a database backend there's the possibility of making an interactive front end to manage the pending updates.

---

## The design

A single Python script with no dependencies beyond the standard library, with SQLite as the database. `INSERT OR IGNORE` was used on a unique key column to give deduplication. The unique key is constructed slightly differently for each source, but is generally source:repo:version. Cron is set to run daily at 8am, deliberately *after* the apt-daily timers and unattended-upgrades have done their morning check, so the notification reflects the true remaining backlog.

Sources checked:

- **apt** — `apt list --upgradable`, one row per pending package version
- **GitHub releases** — the API's `/releases/latest` per watched repo
- **Docker digests** — compare the local image digest against what the registry currently serves for the same tag
- **Reboot required** — `/var/run/reboot-required`, keyed by date so it re-nags daily until I actually reboot

Later I added configurable re-notification: items unactioned after N days (per source — GitHub daily, apt weekly) get re-armed and appear in the next notification. Persistent means persistent.

---

## Automated Security Patches

The one thing I do let run automatically is `unattended-upgrades`, restricted to the `-security` pocket. Security fixes close real vulnerabilities faster than I'd respond to a notification, and they very rarely break anything. Crucially, `Automatic-Reboot` stays `false` — a kernel update installs, the reboot-required flag appears, my phone pings, and I reboot on my schedule. Third-party repos (Docker, Azure CLI) have their own apt origins that don't match the allowed list, so they stay in the notify-and-decide workflow — which is right, because a `docker-ce` upgrade restarts the daemon and every container on the box.

---

## Pinning Docker Images

The digest checker raised a design question: if I pin an image to an exact version, the registry never repoints that tag, so the digest check never flags anything. So for critical containers that need pinning, a notification channel is needed. The model I landed on:

- **Critical services get pinned** (Pi-hole, Unbound, WireGuard, samba) — they only change when I edit the tag, and their GitHub repos go in the monitor's watch list so releases still reach my phone. These critical services keep my home network running and allow remote vpn access, so a manual assesment of when to update is required.
- **Low-stakes services ride mutable tags** (Minecraft) — the digest checker catches those.

This does require attention to detail, as any pinned images that don't have their repo watched will mean updates are missed.

---

## Discovery of abandoned images

Working through the GitHub watch list surfaced an issue in that two of my images were abandoned. The `/releases/latest` endpoint returned 404 for my Unbound image's repo — because the maintainer never made formal releases — and closer inspection showed the repo hadn't been updated in two years while Unbound itself kept releasing. My Samba image (`dperson/samba`) turned out to be in the same state.

An unmaintained image means the bundled software silently stops receiving security fixes. Both were LAN-only behind the firewall, so no emergency — but a file server holding family data on an aging SMB daemon isn't a place to stay.

---

### Samba: dperson → dockur/samba

The old image configured everything through command-line flags in the compose file. The new one uses proper config files: `users.conf` for accounts (a colon-separated format — six fields, including an optional homedir and a standard `smb.conf` for shares.

This updated format allows for separation of concerns: `users.conf` handles authentication (who exists), `smb.conf` handles authorisation (`valid users` per share), and the compose file maps host paths into the container namespace that `smb.conf`'s `path` directives refer to. Two namespaces meeting in the middle — the smb.conf never mentions host paths, the compose file never mentions share names.

Gotchas collected: bind-mounting a config file that doesn't exist yet makes Docker create it as a root-owned *directory* and the container fails confusingly; when overriding smb.conf, start from the image's own file so you keep the `[global]` settings it depends on; and host filesystem permissions apply on top of Samba's checks, producing "access denied" errors that look identical to auth failures. I also dropped port 139 — NetBIOS-era SMB1 transport that nothing modern needs.

---

### Unbound: mvance → klutchell/unbound

I'd accumulated a tuned Unbound config over time — threading, cache sizes, hardening options, as there had been issues with unbound. Then my ISP confirmed my router was faulty and sent a replacement. I decided to keep the stock configuration for the new image and only add settings back if the same issues recur on healthy hardware. The klutchell image made this natural — instead of replacing the whole `unbound.conf`, you drop fragments into a `custom.conf.d/` directory that the base config includes. My entire custom config shrank to three lines:

```
server:
  port: 5335
  interface: 127.0.0.1
```

Port 5335 because Pi-hole owns 53 on the same host; loopback-only because Pi-hole is Unbound's sole client. Checking the image's base config confirmed my hardening settings (`harden-glue`, `harden-dnssec-stripped`, EDNS buffer sizing) were already there. I also dropped my weekly root-hints update cron: the hints change infrequently and a maintained image refreshes them with each release anyway. The mvance-era advice to manage your own hints existed *because* that image went stale.

The old mount had also let the container scribble runtime artifacts (a chroot's `dev/` directory, pid files) all over my host directory. The new arrangement mounts one directory, read-only.

---

## Script Implementation

Files were organised under the Filesystem Hierarchy Standard (FHS) 
- `/etc` for config, 
- `/usr/local/bin` for admin-installed executables, 
- `/var/lib` for persistent state, 
- `/var/log` for logs 

This is opposed to the `/opt` self-contained style used for docker.

**Cron.** Each user has a separate crontab; jobs touching docker and root-owned files belong in root's (`sudo crontab -e`). Cron is silent by design so the output was redirected to a log file. 

**Windows/Linux friction.** I stumbled accross the CRLF / LF differences between windows and linux. I used a mix of `dos2unix` to fix and `.gitattributes` forcing LF to prevent the issue.

## Where things stand

Security patches now flow automatically. Everything else lands in a deduplicated SQLite audit trail and reaches my phone, with per-source re-nagging until I deal with it. Critical images are pinned with their repos watched; both abandoned images are replaced with maintained ones on minimal, deliberate configs. And the server will not reboot without manual intervention.