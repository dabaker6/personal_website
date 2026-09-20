---
title: "Homelab Project: Minecraft Part III"
date: 2026-08-19
tags:
  - Minecraft
  - homelab

summary: Wrapping build service in MCP
---

# Handing the build engine to an LLM with MCP

Third in a series on getting a language model to build in Minecraft Classic. [The first](https://david-baker.co.uk/updates/2026-07-10-minecraft-part1) covered the server, [the second](https://david-baker.co.uk/updates/2026-07-28-minecraft-part2) the build engine and its API. This post is about the actual goal: letting an LLM take a prompt like *"build a small house with a pointed roof"* and construct it — using the Model Context Protocol (MCP) to expose the engine as tools the model can call.

## What MCP is, and what it isn't

MCP is a standard way to give a language model a set of tools it can invoke. You run a server that exposes tools (actions) and resources (readable data); an MCP client — Claude Desktop, in my case — connects to it and lets the model call those tools during a conversation. This is a classic client-server setup, allowing different clients to be connected. This could be in the form of other desktop clients, or bespoke agents. The MCP server exposes `build` and `undo` and the client then calls an LLM and decides when to initiate tool calls. So my code never calls an LLM at all, and can be model agnostic. 

## Auto-generate, or hand-write?

FastMCP (the framework I used) can generate an MCP server directly from an existing FastAPI app — it reads the OpenAPI spec and turns each endpoint into a tool. It's genuinely a few lines, and for a quick internal tool it'd be the obvious choice.

I deliberately didn't use it for two reasons. First, this is a portfolio piece, and "I wired up a converter" demonstrates less than building the server. Secondly, and more substantively, FastMCP's own documentation is blunt that LLMs perform noticeably better with *curated* tools than with auto-converted ones. Auto-generation gives you tools shaped like your API; what an LLM wants is tools shaped like its *task*, with descriptions written for a model rather than a developer.

So I hand-wrote the tools. The engine underneath is identical — the MCP server calls the same build service the HTTP API does — but the tool layer is designed for the model. This allows it to either be spun up as an API, or an MCP server.

## Writing instructions a model can actually use

This was the part I underestimated. A tool is only as good as how well the model understands it, and I found the guidance has to reach the model through three distinct channels, each doing a different job:

- **The tool's input schema** (Pydantic field descriptions) — precise, per-parameter specification: *"size: base width, must be odd for a pointed apex."* This is validation-backed, so it's both documentation and enforcement, and the model sees it every time it considers a call.
- **The tool's description** — concise, always-relevant strategy: build multi-part structures as separate calls so parts can be undone independently; check the result; the coordinate system has Y as height.
- **A resource** — the full shape catalogue and block palette, which the model reads *on demand* when it needs detail, rather than bloating every tool call.

I kept the block palette and shape catalogue in JSON, loaded at startup and exposed as resources. The reasoning: those are the things I'd tweak most often as I refined how the model understood the world, and keeping them as editable data rather than code means adjusting the model's guidance without a code change. The precise, validation-bound parameter specs stayed in code where they belong; the evolving prose guidance lives in JSON. Different things that change for different reasons, kept in different places.

## The feedback loop is the point

The design detail I'm most pleased with is that the tools give the model *actionable feedback*, and the model uses it to correct itself.

When a build has blocks outside the world's bounds, the response reports how many were dropped. When a block ID doesn't exist, the request is rejected with a clear message naming the problem. Because I'd built precise validation into the engine (from the previous post), that feedback was already there — the MCP layer just had to surface it legibly. The result is a loop: the model builds, sees "12 blocks were out of bounds," and adjusts, or picks a different block after being told its choice doesn't exist. The validation I wrote for the API's benefit turned out to be exactly what lets the LLM self-correct.

This also shaped how I instruct it to build. Rather than one giant build call, the tool description nudges the model to build components separately — walls, then windows, then roof, then stairs. Each build is one undo entry, so the model can revert or adjust individual parts. "The stairs are in the wrong place, move them" becomes undo-then-rebuild, cleanly, because the stairs were their own build.

## A caching gotcha worth knowing

One thing that briefly convinced me I had a bug: I updated a tool's description, restarted everything, and the model kept reporting the *old* description. My in-memory tests showed the server serving the new description correctly, so the code was right — but the running conversation disagreed.

The answer is that tool definitions are loaded into a conversation's context *once, at the start*, and stay fixed for that conversation's life. Restarting the server doesn't change what an existing conversation already loaded, and — the part that fooled me — *calling* a tool never surfaces a new description, because calls return results, not definitions. A new conversation picks up the updated tools immediately. Tool definitions are deliberately stable within a session so the model isn't reasoning against a moving target. The lesson was to test description changes with the framework's in-memory client (instant, no restart) and verify in a fresh conversation.

## Where things stand

The build engine is now exposed as a curated MCP server: hand-written tools designed for a model, guidance layered across schema, description and resources, and a feedback loop that lets the LLM correct its own mistakes. Drop it into Claude Desktop, ask for a house, and it builds one — in stages, checking as it goes.

The theme of this phase was that exposing a capability to an LLM is a *design* task, not a wiring task. The engine was the same; the work was in shaping how the model perceives and is guided by it — and in realising that the validation and feedback I'd built for other reasons were the very things that made the model competent.

There's one more post to come, on the least glamorous but most necessary part: keeping the bot connected. A server you restart by hand tolerates a lot; a server meant to run for days, waiting for an LLM to occasionally build something, does not — and getting reconnection right was a saga of its own.