<!--
Sync Impact Report
Version change: 1.0.0 -> 2.0.0
Modified principles:
- I. Static Delivery -> I. Server-Side Rendering Required
- II. Accessible Responsive UI -> II. Accessible Responsive UI
- III. Minimal Client-Side Complexity -> III. Server-First Simplicity
- IV. Basic Quality Verification -> IV. Route and Rendering Verification
- V. Safe Public Deployment -> V. Safe Server Deployment
Added sections:
- None
Removed sections:
- None
Templates requiring updates:
- None. Existing templates in .specify/templates remain compatible with this constitution.
Follow-up TODOs:
- None
-->

# test Server-Rendered Web App Constitution

## Core Principles

### I. Server-Side Rendering Required
The application MUST render its primary user-facing pages on the server. Landing, about,
contact, and other top-level routes MUST return usable HTML from a server-side runtime.
Accepted implementations include server-rendered approaches such as Flask templates or
Blazor with server-side rendering. Client-only rendering MAY enhance the experience, but
it MUST NOT be the sole delivery mechanism for core routes.

### II. Accessible Responsive UI
Every shipped page MUST work on current desktop and mobile browsers, use semantic HTML where practical, and keep the primary user flow usable with keyboard navigation. Content and controls MUST remain readable and functional at common mobile widths.

### III. Server-First Simplicity
Implementation MUST prefer the smallest server-rendered architecture that satisfies the
feature. Frameworks such as Flask or Blazor are acceptable when they keep routing,
templating, and integration boundaries clear. Additional client-side frameworks, heavy
hydration, or duplicate frontend/backend application layers MUST have a clear feature need;
convenience alone is not sufficient justification.

### IV. Route and Rendering Verification
Each feature change MUST include a documented verification path for the affected server-
rendered routes before release. Primary pages MUST be verified for direct navigation,
correct server-rendered content, and responsive behavior. If a change adds non-trivial
server logic, rendering conditions, or interactive client-side behavior, it SHOULD include
automated checks; otherwise manual browser verification is the minimum acceptable gate.

### V. Safe Server Deployment
The shipped app MUST be safe to run as a public web application. Secrets, private keys,
connection strings, and server configuration MUST NOT be committed. Server-side
integrations MUST use explicit configuration boundaries and fail in a way that preserves a
usable or clearly degraded page response.

## Technical Constraints

- Output MUST run in an environment that supports server-side HTML rendering.
- Core routes MUST render meaningful HTML on the first server response.
- Source files SHOULD remain easy to inspect and edit by a small team.
- Performance work SHOULD prioritize fast first render and avoiding unnecessary JavaScript
	on first load.

## Delivery Workflow

- Specifications and plans MUST describe the pages, user flows, server-rendered route
	behavior, and any backend or external integrations.
- Tasks MUST keep work scoped so a page or user flow can be verified independently.
- Reviews MUST confirm server-side rendering for primary routes, responsive behavior, and
	the stated verification path.

## Governance

This constitution overrides conflicting local practices for this repository. Changes to it MUST be made in .specify/memory/constitution.md, include a short rationale, and update the semantic version and amendment date. Compliance MUST be checked during planning and review, and any exception MUST be called out explicitly in the relevant plan or change description.

**Version**: 2.0.0 | **Ratified**: 2026-03-30 | **Last Amended**: 2026-03-30
