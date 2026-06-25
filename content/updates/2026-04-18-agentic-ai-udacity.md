---
title: "Udacity Agentic AI Nanodegree"
date: 2026-05-21
tags:
  - learning
  - development

summary: I Completed the Udacity Agentic AI Nanodegree — Here's What I Built
---

After completing coursework, hand-on projects and ..... I've finished Udacity's **Agentic AI Nanodegree** — and I wanted to write up what the experience involved.

TL;DR this course takes you from "I know how to prompt a chatbot" to "I can architect and build coordinated teams of AI agents that reason, plan, use tools, and talk to each other."

---

## Course 1 — Prompting for Effective LLM Reasoning and Planning

The first course was about going deeper on prompting than most tutorials bother with. The key techniques covered were:

- **Chain-of-Thought (CoT)** — structuring prompts so the model reasons step-by-step rather than jumping to answers
- **ReAct (Reason + Act)** — a framework that lets agents alternate between thinking and taking actions, which is foundational to real agentic behaviour
- **Role-based prompting** — controlling tone, style, and expertise by giving the model a well-defined persona
- **Prompt chaining** — linking the output of one prompt to the input of the next to build multi-step workflows, with Pydantic-based validation gates between stages
- **Feedback loops** — building self-improving systems where an agent evaluates its own output and iterates until it meets a quality bar

The hands-on exercises were genuinely practical. One involved refining a generic recipe analyser into a structured dietary consultant outputting validated JSON. Another built an automated feedback loop where an AI generated Python code, ran it against unit tests, and debugged itself based on the results.

**Capstone project: AgentsVille Trip Planner** — a full multi-agent travel assistant system, pulling together everything from the course.

---

## Course 2 — Agentic Workflows

Course two moved from individual prompts to full workflow architecture. The big patterns covered were:

- **Prompt Chaining** — sequential pipelines where each agent's output feeds the next, with validation at each handoff
- **Routing** — a router agent classifies an incoming task and dispatches it to the right specialist
- **Parallelisation** — running multiple agents concurrently (using Python's threading module) and synthesising their outputs
- **Evaluator-Optimizer** — a two-agent loop where a creator generates a solution and a critic provides structured feedback until constraints are met
- **Orchestrator-Workers** — the most advanced pattern, where a central orchestrator dynamically plans, delegates to specialist workers, and synthesises their findings

Each pattern had both a conceptual lesson and a hands-on implementation exercise. The parallelisation exercise involved multiple specialist agents analysing a document concurrently, and the orchestrator exercise built a market analysis report generator.

**Capstone project: AI-Powered Agentic Workflow for Project Management** — building a reusable library of agent types and using them to manage a technical project end-to-end.

---

## Course 3 — Building Agents

Course three was the most technically dense, covering the internals of what makes a capable agent:

- **Tool use and function calling** — extending agents beyond text to take real-world actions via API calls
- **Structured outputs with Pydantic** — generating validated, typed JSON from LLM responses
- **State management** — using state machines to track conversation context, instructions, and tool results across complex workflows
- **Short-term memory** — managing session context for coherent multi-turn interactions
- **External APIs and MCP** — integrating real-time data sources; also an introduction to the Model Context Protocol as a standard for tool interoperability
- **Web search agents** — grounding agent responses in live data using the Tavily API
- **Database agents** — converting natural language to SQL using SQLAlchemy and text2SQL to query structured data
- **Agentic RAG** — going beyond standard retrieval-augmented generation by adding reflection, query reformulation, and retry loops
- **Long-term memory** — storing semantic, episodic, and procedural memories in vector databases for personalised, persistent interactions
- **Agent evaluation** — systematically assessing task completion, tool use, and output quality using response, step, and trajectory-based strategies

**Capstone project: UdaPlay** — a stateful AI research agent for the video game industry, combining web search, database access, and long-term memory.

---

## Course 4 — Multi-Agent Systems

The final course brought everything together at scale, focusing on coordinating teams of agents:

- **Architecture design** — defining the components of a multi-agent system and designing their interactions at a high level before writing any code
- **Orchestration patterns** — applying sequential, parallel, and conditional orchestration to complex multi-step workflows
- **Routing and data flow** — configuring how data moves between agents and how requests get directed to the right specialist
- **State coordination** — managing shared state across multiple agents running concurrently, including conflict detection and resolution
- **Multi-agent RAG** — distributing retrieval tasks across specialised agents, each focused on different knowledge sources, with a synthesis agent combining their findings

**Capstone project: The Beaver's Choice Paper Company Sales Team** — a complete automated sales system incorporating orchestration, routing, state management, and multi-agent RAG.

---

## Reflections

The course is genuinely intermediate-to-advanced. It assumes you're comfortable with Python, have used an LLM API before, and understand the basics of things like Pydantic and async patterns. If you come in with that foundation, the progression from single prompts to full multi-agent systems feels natural rather than overwhelming.

The ideas, concepts and patterns will be particuarly useful, and have given me a number of ideas for side projects to include in the site.

And finally a link to the certificate...

https://www.udacity.com/certificate/e/4c29853e-4f6b-11f1-af3c-3fd9b932afba