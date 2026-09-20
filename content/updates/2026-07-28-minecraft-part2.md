---
title: "Homelab Project: Minecraft Part II"
date: 2026-07-28
tags:
  - Minecraft
  - homelab

summary: Creating a Minecraft build engine
---

# From a game server to a build engine: shapes, queues and an API

This is the second post in a series on getting an LLM to build in Minecraft Classic. [The first](https://david-baker.co.uk/updates/2026-07-10-minecraft-part1) covered choosing and running the server. This one is about turning "a server I can connect to" into "a build engine I can call" — the geometry, the block-placement mechanics, and the API that wraps them. The AI comes later; first it needed something worth driving.

## Talking to the world as a player

Modern Minecraft has RCON — a remote console for issuing server commands. Minecraft Classic doesn't. Instead, you connect a bot that speaks the Classic protocol *as if it were a player*, and place blocks by sending the same packets a human client would. I used `pyclassic`, a Python implementation of the protocol.

This framing matters for everything that follows: there's no server-side "fill this region" command to lean on. Every block is placed individually, by my code, one packet at a time. A cuboid isn't a primitive — it's a loop I write that emits a block per coordinate.

The first thing that caught me out was trivial and instructive: my test block never appeared. The reason was the coordinate system — in Classic, **Y is the vertical axis**, not Z as I'd assumed. My block was being placed twenty blocks underground, dutifully, invisibly. A ten-second fix once I understood it, but a good reminder to verify assumptions against the actual system rather than the one in my head.

## Pacing: you can't just place blocks as fast as you like

Placing blocks in a tight loop gets the bot kicked. Servers watch for clients modifying the world faster than a human could, and treat it as griefing. `pyclassic` handles this with a threaded queue that drains block placements at a paced rate (around 30ms apart) tuned to stay under those limits.

So the shape of building became: geometry produces a *list* of blocks, the list goes to the queue, the queue drains it safely in the background. The important consequence is that placement is asynchronous — you hand off the work and it completes over the following seconds, which shapes a lot of the later design.

## Layering: geometry, service, transport

The design decision I'm happiest with is a clean separation into three layers, each ignorant of the ones above it:

- **Geometry** — pure functions that turn parameters into coordinates. A triangle is maths: given a size and orientation, produce the blocks. No connection, no queue, no knowledge of anything else. This makes it trivially testable — pass coordinates in, assert on coordinates out, no server required.
- **The build service** — orchestration. It takes the blocks geometry produced, enforces a build zone (out-of-bounds blocks are dropped and counted), validates block IDs against a palette, snapshots for undo, and hands the list to the queue.
- **The transport** — HTTP (and later possibly MCP). It receives requests, calls the service, shapes responses. It knows nothing about *how* a triangle is built.

I also built the geometry and service anticipating a second backend. Minecraft Classic uses numeric block IDs; modern Java uses namespaced strings. So block IDs are strings throughout and the service sits behind an interface — if I ever add an RCON/Java backend, the transport and geometry don't change, only the implementation underneath. It's deliberately *not* built yet — but the interface is there, allowing RCON to be plumbed in.

## Orientation without a mess of if-statements

Adding directional shapes (a slope that can face any way) tempted me toward a branch per direction. The cleaner answer was vectors: a direction is a little arrow — north is `(0, 0, -1)`, east is `(1, 0, 0)` — and building "in a direction" becomes adding a scaled vector to coordinates. For slopes the perpendicular axis (a slope's width runs at right angles to its climb) also needed calculating. The API parameter is a named cardinal direction with the service translating the names to vectors allowing the geometry stays pure arithmetic.

## Undo, and a lesson in shared state

I wanted undo — build a house as separate calls (walls, roof, stairs) and revert any part. The mechanism is snapshots: before a build, read the current blocks in the region it will touch, store them, and undo becomes "replay the stored blocks." Deleting is just placing air; *reversing* a delete needs the before-state, which is why the read-first step exists.

The interesting bug was in how I first structured the build. I'd split it across two calls — one to stage blocks, one to execute — with a shared list on the service holding the pending blocks between them. Under concurrent requests this scrambled: one request's execute could sweep up another's staged blocks. I'd been reaching for locks to guard the shared list. The better fix was to *remove the shared state*: pass the blocks straight through as a parameter to a single atomic build call, so there's no cross-call list to corrupt. The bug didn't get *guarded against* — it stopped being expressible. 

## Wrapping it in FastAPI

The API layer is FastAPI, with Pydantic schemas doing the validation. The shapes are a discriminated union — each shape carries a `type` field, and Pydantic routes each request to the right schema and validates its specific fields. Malformed requests get rejected at the boundary with clear errors, before any build logic runs. That precise, per-shape validation feedback turned out to matter enormously once an LLM was the thing making mistakes — but that's the next post.

## Where things stand

There's now a build engine: describe shapes as structured requests, and they appear in the world, safely paced, bounds-checked, validated, and undoable. It's layered so the geometry knows nothing of the transport, the service knows nothing of HTTP, and a second backend or a second interface can slot in without disturbing the core.

The recurring theme of this phase was that most of the good decisions were about *boundaries* — geometry vs. orchestration vs. transport, names vs. vectors, and passing data rather than sharing it. Get the boundaries right and the later work (an entirely new interface for an LLM) becomes an addition rather than a rewrite.

Next: handing this engine to a language model via the Model Context Protocol — and discovering that a robust connection matters far more when a server runs for days than when you restart it by hand.