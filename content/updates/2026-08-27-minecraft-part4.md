---
title: "Homelab Project: Minecraft Part IV"
date: 2026-08-27
tags:
  - Minecraft
  - homelab

summary: Improving stability and resilience of the MCP server
---
# Keeping a bot connected: the unglamorous half of the project

The latest post in a series on getting an LLM to build in Minecraft Classic. Previous posts covered the [server](https://david-baker.co.uk/updates/2026-07-10-minecraft-part1), the [build engine](https://david-baker.co.uk/updates/2026-07-28-minecraft-part2), and exposing it to a [language model via MCP](https://david-baker.co.uk/updates/2026-08-19-minecraft-part3). This one is about the part that took up a suprising amount of time: keeping the bot connected to the server reliably, for days, while it mostly does nothing.

## Why this suddenly mattered

While developing, the bot connected when I started it and I restarted it whenever anything went wrong. That's fine for a script druing development. But the finished thing is meant to run continuously — sitting idle, waiting for someone to occasionally ask the LLM to build something. A server that runs for days has failure modes a script you restart by hand never exposes. Specifically to Minecraft the bot gets idle-kicked after a set time, also the MCP server and Minecraft server were on separate machines so experienced network blips. Each of these left the bot in a broken state that continual restarting during development had been quietly papering over.

## Failure one: idle kicks

If the bot does nothing the server eventually drops it for inactivity. My first instinct was a keepalive: a background thread sending a harmless packet periodically to keep the connection warm.

It worked, but I now had *multiple threads sharing one socket*. A listener thread receiving the world's updates, the build queue's worker sending block placements, and now a keepalive also sending. Two threads writing to the same socket at once corrupts the protocol. The keepalive had to skip while a build was draining (a build is already keeping the connection busy), and the "harmless packet" had to be genuinely harmless — my first version teleported the bot to the map origin on every keepalive, which is not what "no-op" means.

Then I questioned whether I needed the keepalive at all. As this is on a homelab (and the kids aren't sat on it all the time!) builds are occasional and gap-heavy; a keepalive spends effort preventing kicks during idle time nobody's using. The simpler design was to reconnect *on demand*: check the connection at the start of each build, and reconnect if it's dead. The first build after a long gap pays a few seconds to reconnect; every other build is fine. Less code, no background thread, no socket-sharing race. For this workload that was the better trade — and it turned out to be better for correctness too, which I'll come back to.

## Failure two: the connection dies mid-build

Pull the network cable halfway through a build and things get messier. Some blocks placed, some didn't, and — the real problem — the build queue's worker thread died from the send failure *before* it reached the line that resets its own state. That left the queue believing a build was still running, forever. Every subsequent build was rejected as "busy," and my own liveness check was fooled into thinking the connection was fine because it saw the stuck thread.

One dead thread, and two separate systems drew the wrong conclusion from it. The fix was to detect the difference between a *genuinely running* build and a *dead* thread — a thread object exists in both cases, but only one is actually alive — and to reset the queue's state on reconnect. The deeper lesson was that a library's cleanup code only runs if the thread reaches it; an exception mid-flight skips it, and you have to clean up from the outside.

I decided a half-completed build was acceptable as long as it was logged and the service recovered — but a stuck service was not.

## Failure three: the server is simply gone

The nastiest case. If the game server itself is unreachable, reconnection *can't* succeed — and my reconnect code assumed it would. A failed reconnect left a half-started listener thread and a registered event hook lying around, and because the server stayed down, every subsequent request tried again, leaking another thread each time. A slow accumulation that would eventually degrade the process.

The fix was to make connecting **atomic**: either it fully succeeds, or it fully cleans up after itself and raises. A connection attempt that fails now tears down the listener it started and disconnects the half-open bot before propagating a clear "server unavailable" error, rather than leaving debris. The principle is the same one that governs a database transaction — a partial operation that fails should leave no trace, not a half-applied mess.

## An unexpected correctness bonus

Reconnecting has a consequence for undo. My undo feature works by snapshotting the world before each build so it can be reversed. But after a disconnection, the world may have changed — another player might have built something, or the interrupted build left things half-done. Replaying old snapshots onto a changed world would restore the wrong state.

So the reconnect clears the undo history. And this is where the on-demand-reconnect decision paid off unexpectedly: a keepalive, by *preventing* idle kicks, would have preserved undo snapshots across exactly the long idle gaps where they're most likely to have gone stale. Reconnecting on demand means long idles naturally flush the undo stack via the kick-then-reconnect path. The simpler design was also the more correct one — the two arguments pointed the same way.

## Where things stand

The bot now survives idle kicks, mid-build network drops, and full server outages, reconnecting on demand and cleaning up cleanly when it can't. None of this shows in a demo — a demo is a happy path — but it's the difference between a script you babysit and a service that runs.

The theme of this phase, and honestly of the whole project, is that robustness lives in the failure paths, and the failure paths are where the real design work hides. Getting a bot to place a block is an afternoon. Getting it to place a block reliably, next week, after the network blipped and the server restarted twice, is the actual engineering — and it's mostly invisible, which is exactly why it's worth writing down.

That closes the series, for now. From choosing a free, no-account game server, through a layered build engine, to a curated MCP interface and the connection handling that holds it all together — a small project that turned out to have a surprising amount of design in it, most of it in the parts you don't see.