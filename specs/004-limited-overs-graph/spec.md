# Feature Specification: Limited Overs Innings Progress Graph

**Feature Branch**: `004-limited-overs-graph`  
**Created**: 2026-04-10  
**Status**: Draft  
**Input**: User description: "I want to update the 003-cricket-api. Branch from main and reference the existing personal website in specs\001-personal-website. Please create a new spec 004 and follow the expected templates and processes. For limited overs matches, i.e. ODI, T20, IT20 and ODM I want there to be an additional graph underneath the scoresheet. This graph should have on the y axis, total cummulative runs scored, and on the x axis I want the score grouped by overs, so for instance in a 20 over match there would be twenty data points. The graph should be a line graph with a line for each innings. If a wicket falls in the over an indicator should be present for the user and there should be a tooltip that contains information about the wicket, such as batsman, bowler, method of dismisal etc... Please be aware multiple wickets can occur in an over. Please create the spec and let me review"

**References**: [001-personal-website spec](../001-personal-website/spec.md), [003-cricket-api spec](../003-cricket-api/spec.md)

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Compare Innings Run Progression (Priority: P1)

As a cricket-following visitor viewing a limited-overs match, I want to see a cumulative runs-by-over line graph under the scoresheet, so I can quickly compare how each innings progressed over time.

**Why this priority**: The graph is the core user-facing value of this feature and the main reason for the enhancement request.

**Independent Test**: Open a limited-overs match detail page with innings data and verify the chart appears below the scoresheet with one line per innings and over-grouped points.

**Acceptance Scenarios**:

1. **Given** a visitor opens a limited-overs match detail page, **When** innings scoring data is available, **Then** a run progression graph is displayed directly beneath the scoresheet.
2. **Given** the graph is rendered, **When** the visitor views the axes, **Then** the x-axis represents overs and the y-axis represents cumulative runs scored.
3. **Given** a 20-over innings is shown, **When** the data is plotted, **Then** the innings line contains one data point per over, resulting in twenty points.
4. **Given** both innings are present, **When** the chart is displayed, **Then** each innings is represented by its own distinct line so progression can be compared.

---

### User Story 2 - Understand Wicket Context (Priority: P2)

As a visitor analyzing momentum shifts, I want wickets to be visibly marked on the progression graph with rich tooltip details, so I can understand where and how dismissals changed the innings.

**Why this priority**: Wicket markers convert a basic progression chart into a match-insight view by adding key contextual events.

**Independent Test**: Open a limited-overs match with wicket events and verify wicket indicators appear on the chart at the relevant over positions, including support for multiple wickets in one over.

**Acceptance Scenarios**:

1. **Given** one or more wickets fall in an over, **When** the graph is shown, **Then** each wicket is represented by a visible indicator on the innings line at the corresponding over.
2. **Given** a visitor inspects a wicket indicator, **When** they hover or focus on it, **Then** a tooltip presents wicket information including dismissed batter, bowler, and dismissal method where available.
3. **Given** multiple wickets occur in the same over, **When** the graph is displayed, **Then** each wicket remains individually represented and discoverable in the chart interaction model.

---

### User Story 3 - Preserve Existing Match Detail Experience (Priority: P3)

As a site visitor, I want the new graph enhancement to appear only where relevant and without disrupting existing match detail behavior, so the experience stays consistent with the existing personal website.

**Why this priority**: The feature builds on an existing route and should not degrade established browse/detail flows.

**Independent Test**: Verify limited-overs matches gain the graph while non-limited-overs matches still render a complete, understandable detail page and existing scoresheet behavior remains intact.

**Acceptance Scenarios**:

1. **Given** a match is not ODI, T20, IT20, or ODM, **When** the detail page renders, **Then** the page remains usable and the limited-overs progression graph is not required.
2. **Given** a limited-overs match has partial or missing over-level data, **When** the detail page loads, **Then** the visitor sees a clear graph-unavailable or partial-data state without breaking the rest of the match detail page.
3. **Given** the visitor views match detail on desktop or mobile, **When** the graph and scoresheet are rendered together, **Then** both remain readable and navigable.

---

### Edge Cases

- What happens when innings data includes fewer completed overs than the scheduled over limit?
- What happens when a wicket event does not contain one or more optional details (for example, missing bowler or dismissal text)?
- What happens when an over includes multiple wickets, including wickets that occur on consecutive deliveries?
- How should the chart behave when one innings has over-level progression data and the other innings does not?
- What happens when over numbering in source data contains interruptions or non-standard sequencing?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST add a limited-overs innings progression graph to the existing match detail experience defined in the cricket API feature.
- **FR-002**: The system MUST only require this graph for limited-overs match types: ODI, T20, IT20, and ODM.
- **FR-003**: For each innings shown in a qualifying match, the graph MUST plot cumulative runs against overs.
- **FR-004**: The graph x-axis MUST represent over groups, and the y-axis MUST represent cumulative runs scored.
- **FR-005**: Each innings in a qualifying match MUST be represented as a separate line so visitors can compare innings progression.
- **FR-006**: For innings with a known fixed over limit, the graph MUST provide one plotted point per over group across the innings progression.
- **FR-007**: Wickets MUST be indicated on the innings line at the over in which they occur.
- **FR-008**: Interacting with a wicket indicator MUST reveal tooltip details that include dismissed batter, bowler, and dismissal method when those values are available.
- **FR-009**: When multiple wickets occur in the same over, the graph MUST preserve each wicket as a distinct event so visitors can inspect each dismissal.
- **FR-010**: The progression graph MUST appear beneath the match scoresheet on the detail page for qualifying match types.
- **FR-011**: If qualifying match data is insufficient to build a complete progression graph, the detail page MUST display a clear graph-unavailable or partial-data state while preserving the rest of the detail content.
- **FR-012**: Non-qualifying match types MUST continue to render the existing detail experience without requiring a progression graph.
- **FR-013**: The new graph and wicket interactions MUST preserve usability across common desktop and mobile viewport sizes used by the existing personal website.
- **FR-014**: The enhancement MUST remain aligned with the existing personal website experience and must not remove or obscure currently displayed scoresheet information.

### Key Entities

- **Limited Overs Progression Series**: Over-by-over innings progression points for a single innings, with each point representing cumulative runs at a specific over group.
- **Wicket Event Marker**: A plotted dismissal event linked to an innings and over group, including display attributes and contextual tooltip details.
- **Wicket Tooltip Detail**: Human-readable dismissal context shown to visitors, including dismissed batter, bowler, and dismissal method when present.
- **Match Detail Graph Section**: A dedicated section beneath the existing scoresheet that presents innings progression lines and wicket indicators for qualifying match types.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In acceptance testing with qualifying matches, 100% of ODI, T20, IT20, and ODM detail views show a progression graph beneath the scoresheet when required scoring data is present.
- **SC-002**: In sampled limited-overs innings, plotted points match the expected over grouping model with one point per over group and accurate cumulative run totals in at least 95% of validated innings.
- **SC-003**: In sampled wicket events for qualifying matches, at least 95% of wicket indicators display discoverable tooltip content with available dismissal context.
- **SC-004**: For test matches and other non-qualifying formats, 100% of detail pages continue to render core scoresheet content with no progression-graph requirement.
- **SC-005**: In responsive validation, the scoresheet plus graph layout remains readable and operable on both desktop and mobile viewport tests for all qualifying and non-qualifying scenarios.

## Assumptions


- This feature extends the existing cricket match detail flow established in the prior cricket API feature and does not replace it.
- Match type classification for ODI, T20, IT20, and ODM is available from existing match metadata and is reliable enough to determine graph applicability.
- Over-level scoring and wicket event data are available from existing match detail data for at least a representative subset of limited-overs matches.
- Tooltip content may omit unavailable fields while still presenting the remaining known wicket details.
- The first release focuses on visualizing completed innings progression and wicket context, not predictive analytics or advanced comparison tooling.
