# Tasks: Updates Page

**Input**: Design documents from `/specs/002-updates-page/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Include route-level tests because the feature adds new server-rendered routes, resilient content loading behavior, and non-trivial client-side interactions.

**Organization**: Tasks are grouped by user story so each story can be implemented and verified independently by an AI coding agent.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel when the tasks touch different files and have no direct dependency.
- **[Story]**: User story identifier from the spec (`US1`, `US2`, etc.).
- Every task includes exact file paths.

## Phase 1: Setup

**Purpose**: Add the minimal project scaffolding needed for Markdown-backed updates.

- [X] T001 Update `requirements.txt` with Markdown and frontmatter parsing dependencies.
- [X] T002 Update `README.md` with local run and verification notes for the Updates feature.
- [X] T003 Create the `content/updates/` directory and add two valid sample entries for local development.

---

## Phase 2: Foundational

**Purpose**: Build the shared content-loading infrastructure that all routes depend on.

**⚠️ CRITICAL**: No user story work should start until this phase is complete.

- [X] T004 Create `updates.py` with entry parsing, frontmatter validation, slug generation, and date normalization helpers.
- [X] T005 [P] Add malformed-entry skipping and draft exclusion behavior in `updates.py`.
- [X] T006 [P] Add feed-level helpers in `updates.py` for sorted published entries and unique tag aggregation.
- [X] T007 Update `content.py` navigation data to include the `Updates` nav item while preserving the existing structure.

**Checkpoint**: Feed and detail routes can now be built against a stable content source.

---

## Phase 3: User Story 1 - Browse the Updates Feed (Priority: P1) 🎯 MVP

**Goal**: Deliver a server-rendered updates feed with visible timestamps, tags, summaries, and navigation integration.

**Independent Test**: Open `/updates` and verify the page returns HTML showing published entries newest-first with title, date, tags, and summary, plus an `Updates` nav link.

### Tests for User Story 1

- [X] T008 [P] [US1] Extend `tests/test_routes.py` with coverage for `GET /updates`, navigation visibility, and newest-first feed ordering.

### Implementation for User Story 1

- [X] T009 [US1] Add the `/updates` route to `app.py` and connect it to the loader in `updates.py`.
- [X] T010 [US1] Create `templates/updates.html` for the server-rendered feed layout and empty state.
- [X] T011 [US1] Extend `static/css/site.css` with feed-page styling that matches the existing visual system.

**Checkpoint**: User Story 1 is fully functional and testable on its own.

---

## Phase 4: User Story 2 - Read a Single Update Entry (Priority: P2)

**Goal**: Let visitors open a full entry detail page rendered from Markdown.

**Independent Test**: Open an entry from `/updates` and verify the title, date, tags, Markdown body, and back-navigation render correctly.

### Tests for User Story 2

- [ ] T012 [P] [US2] Extend `tests/test_routes.py` with coverage for `GET /updates/<slug>` success and 404 handling for missing slugs.

### Implementation for User Story 2

- [ ] T013 [US2] Add Markdown-to-HTML rendering and single-entry lookup helpers to `updates.py`.
- [ ] T014 [US2] Add the `/updates/<slug>` route to `app.py` with published-only access rules.
- [ ] T015 [US2] Create `templates/update_detail.html` with entry metadata, rendered body, tag links, and a back-to-feed control.
- [ ] T016 [US2] Extend `static/css/site.css` with detail-page typography and metadata styling.

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Search and Filter Entries (Priority: P3)

**Goal**: Add no-reload search and tag filtering on top of the server-rendered feed.

**Independent Test**: On `/updates`, type a known term and click a tag; verify visible results update instantly without a page reload, with a clear no-results state.

### Tests for User Story 3

- [ ] T017 [P] [US3] Extend `tests/test_routes.py` to verify the feed HTML exposes the search field, tag controls, and searchable content markers needed by the client-side behavior.

### Implementation for User Story 3

- [ ] T018 [US3] Update `templates/updates.html` to emit search input, tag controls, empty-filter state, and searchable entry metadata attributes.
- [ ] T019 [US3] Create `static/js/updates.js` with client-side text filtering and tag-toggle behavior.
- [ ] T020 [US3] Update `templates/base.html` or `templates/updates.html` so the updates script only loads where needed.
- [ ] T021 [US3] Extend `static/css/site.css` with search, tag, and empty-filter styling.

**Checkpoint**: User Stories 1 through 3 are all independently usable.

---

## Phase 6: User Story 4 - Sort Entries (Priority: P4)

**Goal**: Let visitors switch between newest-first and oldest-first ordering without a page reload.

**Independent Test**: Change the sort control on `/updates` and verify the currently visible set reorders immediately.

### Tests for User Story 4

- [ ] T022 [P] [US4] Extend `tests/test_routes.py` to verify the sort control is present in the feed HTML.

### Implementation for User Story 4

- [ ] T023 [US4] Update `templates/updates.html` with a sort control that works with the existing client-side filter model.
- [ ] T024 [US4] Extend `static/js/updates.js` to support newest-first and oldest-first ordering for the currently filtered results.
- [ ] T025 [US4] Extend `static/css/site.css` with sort-control styling.

**Checkpoint**: Sorting works alongside search and tag filtering.

---

## Phase 7: User Story 5 - Add a New Entry Without Touching App Code (Priority: P5)

**Goal**: Make the content workflow additive so new valid Markdown files appear automatically and invalid ones fail safely.

**Independent Test**: Add a new `.md` file to `content/updates/`, reload `/updates`, and verify the entry appears without any code changes; add a malformed or draft file and verify safe behavior.

### Tests for User Story 5

- [ ] T026 [P] [US5] Extend `tests/test_routes.py` with coverage for draft exclusion and malformed-entry resilience using temporary content fixtures or overrides.

### Implementation for User Story 5

- [ ] T027 [US5] Update `updates.py` to support configurable content roots for testing and future reuse.
- [ ] T028 [US5] Add sample draft and malformed fixture content under test-controlled paths or helper setup in `tests/test_routes.py`.
- [ ] T029 [US5] Update `README.md` with the authoring workflow for adding a new update file without code changes.

**Checkpoint**: The authoring workflow is verified end-to-end.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, resilience, and verification work across all stories.

- [ ] T030 [P] Run the full pytest suite and fix any regressions in `tests/test_routes.py` or related feature files.
- [ ] T031 Review templates and CSS for mobile readability, keyboard navigation, and empty-state clarity across `/updates` and `/updates/<slug>`.
- [ ] T032 Validate `quickstart.md` against the implemented workflow and align documentation if any paths or filenames changed.

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup can begin immediately.
- Foundational depends on Setup and blocks all story work.
- User stories then proceed in priority order, though some tasks within each story can run in parallel.
- Polish depends on the completion of all desired stories.

### User Story Dependencies

- US1 depends on Foundational only.
- US2 depends on Foundational and reuses the parsed entry model from US1.
- US3 depends on US1 because it enhances the feed template.
- US4 depends on US3 because sorting extends the same client-side feed behavior.
- US5 depends on Foundational and should land after US1 so the workflow can be observed on the real feed.

### Within Each User Story

- Tests should be added before or alongside the implementation they verify.
- Loader helpers precede route wiring.
- Route wiring precedes template polish.
- Template data hooks precede client-side enhancement logic.

## Parallel Opportunities

- T005 and T006 can run in parallel once `updates.py` exists.
- T008 can run in parallel with T010 and T011 after the route shape is agreed.
- T012 can run in parallel with T013.
- T019 and T021 can run in parallel after the feed markup is stabilized.
- T026 can run in parallel with T029.

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 to ship a fully server-rendered feed.
3. Validate `/updates` independently before expanding scope.
4. Add the detail route in Phase 4.
5. Layer in progressive enhancement only after the server-rendered experience is stable.

### Agent-Friendly Slices

1. One agent can own `updates.py` and foundational parsing behavior.
2. A second agent can own feed templates and CSS once route data is available.
3. A third agent can add route tests in `tests/test_routes.py` in parallel with UI work.
4. Client-side enhancement work remains isolated to `static/js/updates.js` and feed-template hooks.
