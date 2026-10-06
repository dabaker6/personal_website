---
title: "Consolidating Azure Billing"
date: 2026-09-16
tags: 
 - learning
  - deployment
summary: My latest statement from Azure, was higer than I was expecting, here's what I found
---

# Trimming £135 a Year Off a Hobby Azure Bill

My personal site runs on Azure, and alongside it I keep a small demo that shows Azure Container Apps autoscaling on Service Bus queue depth. This demo is only run occassionally, but it was up 24/7 and costing money.

The bill broke down like this (UK South, retail prices in GBP):

| **Resource** | **Cost** | **Monthly Cost**
|:---:|:---:|:---:|
| App Service Plan (B1, Linux) | £0.0133/hr  | **£9.71/mo** |
| Container Registry (Basic) | £0.1241/day  | **£3.78/mo** |
| Service Bus (Standard) | standing charge  |**£7.53/mo**  |
| | | **≈ £21/mo** |

The App Service plan is required as I have a custom domain, and B1 is the lowest tier that offers custom domains. The Free tier doesn't support custom domains at all, and Shared D1 supports the domain but not TLS on it, which makes it useless. B1 also gets you free App Service Managed Certificates, so the cert costs nothing.

That leaves the other two, which between them were £11.31/month for services I barely used.

A note on that B1 line, incidentally: the Linux plan is £0.0133/hr and the **Windows** plan is £0.0692/hr — £9.71 versus £50.52 a month, because the Windows price bundles an OS licence. My app service plan is already running on Linux, confirmed with: 
`az appservice plan show -g <rg> -n <plan> --query "[sku.name,kind,reserved]"`.

---

## Service Bus: £7.53/month for an idle queue

The Service Bus Standard tier has a base charge that applies whether or not a single message flows through it. At £0.0101/hour, that's £7.53/month for a namespace that, in my case, sat idle except when I ran the demo.

Standard also bundles 13 million operations a month, so the base unit *was* the entire bill.

The Basic tier has **no standing charge at all** — you pay £0.0376 per million operations and nothing else. An idle Basic namespace is free. A demo pushing a few thousand messages essentially rounds to zero; I'd need to run around 27 million operations to reach £1.

The catch is what Basic gives up:

| Feature | Basic | Standard |
|:---:|:---:|:---:|
| Queues | ✅ | ✅ |
| Scheduled messages | ✅ | ✅ |
| Topics / subscriptions | ❌ | ✅ |
| Sessions | ❌ | ✅ |
| Transactions | ❌ | ✅ |
| Duplicate detection | ❌ | ✅ |
| ForwardTo / SendVia | ❌ | ✅ |
| AutoDeleteOnIdle | ❌ | ✅ |
| Message TTL | max 14 days | effectively unlimited |
| Message size | 256 KB | 256 KB |
| Ops/sec | 1,000 | 1,000 |

My demo sends messages to a queue and a worker receives them. There are no topics, sessions, or transactions, so Basic covers it completely.

### The downgrade is in-place

The tier change is an in-place update. The namespace keeps its name, which matters enormously, because both my apps authenticate with managed identity against that fully-qualified namespace. Role assignments live on the namespace resource. Had the namespace been replaced, every `Azure Service Bus Data Sender` / `Data Receiver` / `Data Owner` assignment would have gone with it, and the apps would have started fine and then 403'd on first use. Because it's an in-place update, none of that applies. No config changes, no re-granting, no downtime.

---

## The Terraform changes

The first attempt failed with a 409:

```
Namespace cannot be downgraded because at least one queue
'sb://<my-namespace>.servicebus.windows.net/sbq-scaling' has
DefaultMessageTimeToLive set with an invalid value, the value need to be
between 00:00:01 and 14.00:00:00.
```

This shows it's a *validation* failure, not a refusal. Azure is willing to do the downgrade; it just won't accept a queue that violates Basic's constraints.

### The offending value

My queue's TTL was:

```hcl
default_message_ttl = "P10675199DT2H48M5.4775807S"
```

That's `TimeSpan.MaxValue` — `Int64.MaxValue` ticks at 100ns each, or about **29,227 years**. This is the maximum representable timespan, i.e. where "no-expiry" is set, and is the Standard/Premium default. I did not explicitly set this value, so it must have been set on creation of the resource.

Basic caps TTL at 14 days, so:

```hcl
default_message_ttl = "P14D"
```

Note the Terraform argument is **`default_message_ttl`**, which doesn't match the ARM property name (`defaultMessageTimeToLive`) or the CLI flag (`--default-message-time-to-live`). 

Going from "never expires" to 14 days means messages left in the queue after an abandoned demo run will eventually expire into the dead-letter queue rather than sitting there indefinitely. For a demo that gets drained within minutes, the difference between 14 days and 29,227 years is academic — but it explains a populated DLQ if you ever see one after a long gap.

**Result: £7.53/month → approximately £0.**

---

## ACR → GHCR

The Container Registry was £3.78/month on Basic for four pretty small images. GitHub Container Registry stores public images for free, with no bandwidth metering either.

### The workflow changes

My Actions workflows already used Azure OIDC login, which made this relatively painless. The change is essentially swapping the registry authentication and build steps; the Azure deployment steps stay as they were.

Before:

```yaml
      - name: Build and push image
        run: |
          az acr login --name $ACR_NAME
          IMAGE="$ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_TAG"
          docker build -t $IMAGE ./aca_scaling_api
          docker push $IMAGE
```

After:

```yaml
permissions:
  id-token: write    # Azure OIDC
  contents: read     # checkout
  packages: write    # push to ghcr.io

env:
  IMAGE: ghcr.io/dabaker6/aca_scaling_api-api
  TAG: v1.${{ github.sha }}

# ...

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Set up Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: ./aca_scaling_api
          push: true
          tags: ${{ env.IMAGE }}:${{ env.TAG }}
          labels: |
            org.opencontainers.image.source=https://github.com/${{ github.repository }}
            org.opencontainers.image.revision=${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

Three things worth focusing on:

**Pushing needs no PAT.** `secrets.GITHUB_TOKEN` is built in and authenticates to GHCR, provided the job declares `packages: write`. If your repository default workflow permission is read-only, the explicit `permissions:` block still grants it — no need to loosen the repo-wide setting.

**The `org.opencontainers.image.source` label is functional, not decorative.** GHCR reads that specific key to link the package to its repository, and a linked package inherits the repo's access permissions so later workflow runs keep access automatically. Without it you can end up fixing permissions by hand in the package settings.

**Buildx layer caching is a real win.** On a multi-stage .NET build, `cache-from`/`cache-to: type=gha` took my job from around three minutes to well under one. Keep it as `type=gha` rather than `type=registry` — the latter would push intermediate SDK layers, complete with your full source tree, to the public package.

### The Azure side

For a **public** package, neither App Service nor Container Apps needs any registry configuration. They pull anonymously. The deploy steps are unchanged:

```yaml
      - name: Point Web App at the GHCR image
        env:
          WEBAPP_NAME: ${{ vars.WEBAPP_NAME }}
          RESOURCE_GROUP: ${{ vars.RESOURCE_GROUP }}
          IMAGE_REF: ${{ env.IMAGE }}:${{ env.TAG }}
        run: |
          az webapp config container set \
            --name "$WEBAPP_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --container-image-name "$IMAGE_REF"
```

Passing values through `env:` rather than interpolating `${{ }}` straight into the shell is worth doing as a habit — it fixes the command's structure at author time, so a stray character in a value can't break the line continuations.

What *does* need doing is clearing the old ACR authentication, which otherwise lingers and conflicts, which was all done through updating terraform. Also while I was there I set `ignore_change` on all the container names, as they are based on the commit sha then this constantly changed throwing off the terraform state.

## Pros and cons of the GHCR move

**In favour:**

- Free storage and unmetered bandwidth for public images. Nobody can run up a bill by pulling.
- No pull credentials anywhere in Azure — nothing to rotate, expire, or leak.
- The registry lives next to the source, so the package page carries the README and links back to the repo.
- Pushing uses the built-in `GITHUB_TOKEN`, so CI needs no extra secret.

**Against:**

- **You lose managed-identity pull.** ACR integrates with Entra ID; GHCR does not, for any tier. For a public image that's moot, but it's a genuine capability I gave up, but for a small personal website this was acceptable.
- **The image is world-readable.** Anyone can pull it and unpack every layer — compiled assemblies, your full dependency graph with exact versions, and the base image digest. That last one is the real consideration: it hands anyone an accurate CVE inventory with no probing required.
- **Whatever ships is public forever.** Package versions persist until explicitly deleted, and public is irreversible. One build that bakes in something it shouldn't is permanently, publicly pullable — fixing the repository afterwards does nothing.
- **The pull crosses the public internet** rather than staying inside Azure.

For a demo whose source is already on GitHub, the exposure is close to zero incremental and the trade is clearly worth it. If the apps were carrying credentials or unreleased code in an image, then this security posture wouldn't be wise and ACR Basic at £3.78/month is buying you something real.

---

## Where it landed

| | Before | After |
|---|---|---|
| App Service (B1 Linux) | £9.71 | £9.71 |
| Container Registry (Basic) | £3.78 | £0.00 |
| Service Bus (Standard → Basic) | £7.53 | ~£0.00 |
| **Monthly** | **£21.02** | **£9.71** |

About **£135 a year**, for an evening's work and no loss of function. The App Service plan is now essentially the whole bill, which is the right shape — it's the only thing that genuinely runs continuously.

If I wanted to go further, Azure Container Apps could be used for the site as well. They support custom domains, free managed certificates, and a monthly free grant that a low-traffic blog fits inside comfortably. The cost is a cold start on the first request after an idle period due to the app scaling to zero. For a personal site that may well be an acceptable trade — but that's for another day.