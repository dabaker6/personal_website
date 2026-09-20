---
title: "Homelab Project: Minecraft Part I"
date: 2026-07-10
tags:
  - Minecraft  
  - homelab

summary: Setting up a self hosted Minecraft server
---

# Running a Minecraft Classic server for an LLM to build in

This is the first in a short series on a project I've been building: letting an LLM construct things in a Minecraft world from natural-language prompts. Before any of the AI parts, I needed a server — and a copy of Minecraft.

## The problem: a family server without buying the game four times

The plan was a small world on my homelab for a few family members. As this is a small test project, and just for the family I didn't want to have to buy a copy per person. The modern Java/Bedrock Minecraft needs authentication through Mojang's servers, so I took a look at what free, self-hostable alternatives existed.

## Classic vs. ClassiCube vs. the real game

Mojang's original **Minecraft Classic** is the 2009 version, which is creative-only, has a handful of block types, no survival and no mobs. There's an official free browser version, but it can't connect to anything self hosted.

**ClassiCube** is a free, open-source, actively maintained reimplementation of that classic-era game, and crucially it's fully self-hostable. Players connect with a free client (desktop or browser) and — for a LAN server — no account at all. This makes it the right starting point, with no one having to buy or register anything to join.

The server software is **MCGalaxy**, a mature C# server that speaks the Classic protocol. The tradeoff is it's a much simpler game than modern Minecraft — creative block-building, no survival etc... But it's free and as a sandbox for an LLM to draw in, it's ideal. Moving to a modern-game path stays open if anyone gets hooked.

## Running MCGalaxy in Docker

MCGalaxy is a .NET application that runs under Mono, so rather than install a runtime on the host I used a community image (`rdebath/mcgalaxy`) and ran it as another container on a Wyse thin client, alongside the rest of my homelab.

Two gotchas cost me time, both worth recording because they produce *confusing* failures rather than obvious ones, and annoyingly both resulting from mistyping parameters in the docker image.

**Silent volume-path bug.** My first compose file mounted the data directory with a leading slash — an absolute path from the filesystem root — instead of a path relative to the compose file. Docker's response to a bind-mount source that doesn't exist is not to error: it *silently creates* the directory, owned by root. So the container got a brand-new empty root-owned folder, the non-root user inside couldn't write to it, and I got a permission-denied on startup while my *actual* data sat untouched somewhere else entirely. A single missing `./` and the symptom was "permission error and an empty data directory," which points nowhere near the real cause. Lesson learned: `/data` and `./data` results Docker not telling you when you've picked the wrong one.

**The crossed port mapping.** The mapping is `host:container`, and MCGalaxy listens on 25565 inside the container. I wanted host port 25566 (keeping 25565 free for a future modern-Minecraft server), so the correct mapping is `25566:25565` — host 25566 forwarded to the container's 25565. I'd written `25566:25566`, which forwarded to a container port where nothing was listening, so connections silently failed. What cracked it was the server console, not the client: the client just said "failed to connect," but `docker compose ps` showed the mapping forwarding to the wrong port.

## The account and permission model

A couple of MCGalaxy specifics that matter for a LAN setup:

- **`verify-names = false`.** By default MCGalaxy checks connecting players against ClassiCube accounts. Turning this off lets family members (and, later, my bot) connect with any username and no account — right for a LAN, and the whole point of choosing this stack. It also means the server should never be exposed to the internet, since anyone could then impersonate anyone.
- **MCGalaxy rewrites its config on shutdown.** Editing `server.properties` while the server is running gets overwritten when it stops. The fix is stop-first, then edit, then start — otherwise your change vanishes and you're left baffled as to why `verify-names` keeps reverting.

## Where things stand

The server runs as a container on the homelab, allowing family members to connect with a free client and no account, with the world persisting after disconnecting. It's a deliberately modest game with just creative building — but that's exactly the blank canvas I wanted.

The interesting realisation from this phase was how much of "set up a game server" turned out to be *choosing the right game*: the free-and-no-account property of ClassiCube is what makes the whole project approachable, and it's the reason the later AI work could happen without a licensing question hanging over every test.

Next up: turning "a server I can connect to" into "a build engine I can call" — the geometry, the block-placement queue, and wrapping it all in an API.