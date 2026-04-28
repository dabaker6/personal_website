# Implementation Tasks: ACA Scaling Dashboard v2 — Enhanced Monitoring & Navigation

**Feature**: ACA Scaling Dashboard v2 Enhancements  
**Plan**: [plan.md](plan.md) | **Spec**: [spec.md](spec.md)  
**Date**: 2026-04-28  
**Branch**: `006-scaling-enhancements`

## Overview

19 discrete tasks organized by user story priority (P1 first, then P2). Each task is independently implementable with clear file paths and completion signals. Parallelizable tasks marked [P] can run in parallel within the same phase.

**Task Distribution**:
- Phase 2 (Foundational + Research): 2 tasks
- Phase 3 (US1 - Live Metrics): 4 tasks
- Phase 4 (US2 - Placeholders): 3 tasks
- Phase 5 (US4 - Eager Polling): 3 tasks
- Phase 6 (US6 - Queue Updates): 1 task (integrated with US1)
- Phase 7 (US3 - Form Restoration): 2 tasks
- Phase 8 (US5 - Navigation): 3 tasks
- Phase 9 (Final Docs & Tests): 3 tasks

**MVP Scope**: Phases 2–6 (US1, US2, US4, US6) deliver foundational live metrics and responsive UX with placeholders and eager polling. Phase 7–8 (US3, US5) add polish and IA improvements. Phase 9 ensures quality.

---

## Phase 2: Foundational Configuration

### Background Polling Environment Variable & Research Documentation

- [x] T001 Add `BACKGROUND_POLLING_INTERVAL_MS` environment variable and pass to template in `app.py` /scaling route

- [x] T018 Write `specs/006-scaling-enhancements/research.md` documenting decisions on placeholder design, polling interval defaults, eager polling mechanism (client-side), and navigation scope impact

**→ STOP & REVIEW**: After T001–T018 complete, review research.md to validate design decisions before proceeding with implementation.

---

## Phase 3: User Story 1 — Live Metrics Throughout Session (P1)

**Story Goal**: Queue depth and replica count update continuously throughout user session on /scaling, with separate, slower background polling interval when no scaling event is active.

**Independent Test Criteria**:
1. Navigate to /scaling with no active scaling event; observe metrics panel updates every 5 seconds
2. Submit a message; polling interval increases to faster rate (1–3x per second)
3. Wait for queue to clear; polling resumes slower background interval
4. Navigate away and return; background polling resumes with fresh state

**Task Sequence**:

- [x] T002 Create `startBackgroundPolling()` function in `static/js/scaling.js` that polls `/scaling/api/status` at `background_polling_interval_ms` and updates metric panels

- [x] T003 Handle background polling errors silently in `static/js/scaling.js` without interrupting active monitoring

- [x] T004 [P] Integrate background polling start into page load lifecycle in `static/js/scaling.js` (start before any submission, pause during monitoring, resume after)

- [x] T005 [P] Add tests to `tests/test_routes.py` confirming background polling config is passed to template and `/scaling/api/status` is called correctly

---

## Phase 4: User Story 2 — Graceful Initial Load with Placeholders (P1)

**Story Goal**: /scaling page displays immediately with placeholder content, then real metrics replace placeholders within 500ms without jank.

**Independent Test Criteria**:
1. Navigate to /scaling; page renders with visually distinct placeholder in under 500ms
2. Backend API call completes; placeholders replaced with real values without flash
3. Backend API fails; error message replaces placeholder gracefully
4. Mobile (375px): placeholders render and update without overflow

**Task Sequence**:

- [x] T006 [P] Add placeholder markup for queue-depth and replica-count metric panels in `templates/scaling.html`

- [x] T007 [P] Add CSS styling for placeholders with gray background, loading indicator, and same height as real metrics in `static/css/site.css`

- [x] T008 Create JavaScript logic in `static/js/scaling.js` to replace placeholders with real metric values after initial API call completes without page reload

---

## Phase 5: User Story 4 — Eager Chart Data Collection (P1)

**Story Goal**: Chart polling begins immediately on form submission, not waiting for 202 response. First reading has elapsed_ms ≈ 0.

**Independent Test Criteria**:
1. Submit a message; chart data accumulation starts immediately (before 202 response)
2. First chart reading has elapsed_ms within 500ms of submission
3. No data loss if 202 response delayed; all readings visible on chart
4. Chart renders correctly even with single early data point

**Task Sequence**:

- [x] T009 Implement eager chart polling: on form submit (before fetch completes), start polling `/scaling/api/status` in parallel in `static/js/scaling.js`

- [x] T010 Ensure first chart reading has `elapsed_ms` ≈ 0 in `static/js/scaling.js` by capturing submission timestamp at form submit (not waiting for 202)

- [x] T011 Add tests to `tests/test_routes.py` confirming chart receives first reading immediately and no data loss if 202 is delayed

---

## Phase 6: User Story 6 — Live Queue Depth Metric Updates (P1)

**Story Goal**: Queue depth metric panel updates with each polling cycle during active monitoring, showing real-time queue state.

**Independent Test Criteria**:
1. During active monitoring, queue depth number updates every polling interval
2. Queue depth value matches latest data point on chart
3. Final queue value remains visible after monitoring stops

**Note**: This feature is integrated into T002 (background polling updates both replica count and queue depth panels). This phase confirms and validates the queue depth update behavior.

- [x] T012 [P] Verify queue depth metric updates in `static/js/scaling.js` `pollStatus()` function and add integration tests to `tests/test_routes.py`

---

## Phase 7: User Story 3 — Resubmit Messages After Completion (P2)

**Story Goal**: Send message form reappears after scaling event completes, allowing users to submit again without page reload.

**Independent Test Criteria**:
1. Scaling event completes (queue reaches 0 or timeout); form transitions from hidden to visible within 500ms
2. Form is reset: input cleared, button enabled
3. New submission works on same page
4. Form fully interactive and button not obscured on mobile (375px)

**Task Sequence**:

- [ ] T013 Add form restoration logic in `static/js/scaling.js` to show form and reset state after monitoring stops (queue=0, timeout, or error)

- [ ] T014 Add tests to `tests/test_routes.py` confirming form reappears after scaling event and second submission works

---

## Phase 8: User Story 5 — Navigation Redesign: Demo Section with Submenus (P2)

**Story Goal**: Navigation menu features top-level "Demos" section with Cricket Data and Scaling as submenus, accessible and responsive on desktop (1280px) and mobile (375px).

**Independent Test Criteria**:
1. Desktop (1280px): "Demos" appears as top-level nav item with dropdown submenu on hover/focus
2. Mobile (375px): "Demos" appears as expandable item; tap reveals Cricket Data and Scaling links
3. Active link highlighted when on Scaling page
4. Submenu opens/closes within 300ms with no layout shift

**Task Sequence**:

- [ ] T015 Restructure navigation in `templates/base.html` to add top-level "Demos" item with Cricket Data and Scaling as submenus

- [ ] T016 [P] Update navigation hierarchy in `content.py` to include Demos section and ensure active nav state for Cricket Data and Scaling pages

- [ ] T017 [P] Add CSS styling for submenu appearance and JavaScript toggle for mobile in `static/css/site.css` and `static/js/site_nav.js` (or inline JS if file doesn't exist)

---

## Phase 9: Final Documentation, Testing & Validation

### Design Documentation

- [ ] T019 Write `specs/006-scaling-enhancements/data-model.md` documenting polling configuration entity, placeholder states, form restoration state machine, and navigation hierarchy

### Integration & Quality Assurance

- [ ] T020 Write `specs/006-scaling-enhancements/quickstart.md` with test scenarios: background polling updates metrics every 30s, placeholders appear/disappear, form restoration workflow, eager polling behavior, nav Demo section access on desktop and mobile

- [ ] T021 Run full pytest suite; verify all existing v1 tests pass, all new tests pass, no regressions; manual verification of quickstart scenarios; responsive layout checked at 375px and 1280px

---

## Dependencies & Parallelization

### Sequential Gating
- **T001** must complete before other tasks (environment variable needed for T002–T004)
- **T006–T007** (placeholder markup and CSS) should precede **T008** (placeholder replacement logic)
- **T013** (form restoration) depends on T002–T005 (monitoring lifecycle established)
- **T015** (base.html nav) should precede **T016** (content.py nav structure)

### Parallel Opportunities Within Phases

**Phase 3 (US1)**:
- T002–T003 can run in parallel (different functions in scaling.js)
- T004–T005 can run in parallel after T002 (JS integration + tests)

**Phase 4 (US2)**:
- T006–T007 can run in parallel (markup + CSS for placeholders)
- T008 depends on T006–T007

**Phase 5 (US4)**:
- T009–T010 can run in parallel (eager polling logic + elapsed_ms handling)
- T011 depends on T009–T010

**Phase 8 (US5)**:
- T016–T017 can run in parallel after T015 (content.py + CSS/JS styling)

**Phase 9**:
- T018–T019 can run in parallel (separate documentation files)
- T020 depends on T018–T019
- T021 depends on all other tasks

### Example Parallel Execution Paths

**Review & MVP Path**:
```
T001 → T018 → [⏸️ REVIEW research.md] 
     → (T002–T005 parallel) → (T006–T008 parallel) → (T009–T012 parallel)
```

**Full Path (all features)**:
```
T001 → T018 → [⏸️ REVIEW] 
     → (T002–T005) → (T006–T008) → (T009–T012) 
     → (T013–T014) → (T015, T016–T017 parallel) 
     → (T019–T020 parallel) → T021
```

---

## Implementation Strategy

### MVP: Phases 2–6 (Features T001–T018, then T002–T012)
1. **Setup & Review** (T001, T018): Add background polling config and write research.md documenting design decisions
2. **⏸️ REVIEW CHECKPOINT**: Review research.md to validate decisions before implementation
3. **Implement** (T002–T012): Deliver live metrics (background polling), responsive initial load (placeholders), and eager chart polling

This satisfies **all P1 user stories** and success criteria SC-001 through SC-006, with documented rationale for design choices.

### Polish: Phases 7–8 (Features T013–T017)
Adds form restoration and navigation IA improvements (P2 stories). Enhances discoverability and multi-experiment workflows.

### Quality: Phase 9 (Features T019–T021)
Final documentation, integration testing, regression validation, and responsive design verification.

---

## Task Status Tracking

Use this checklist to track progress:

**Phase 2 (Foundational)**:
- [x] T001 - Background polling env variable
- [x] T018 - research.md documentation (⏸️ REVIEW CHECKPOINT)

**Phases 3–8 (User Stories & Features)**:
- [x] T002 - Background polling loop
- [x] T003 - Background polling error handling
- [x] T004 - Background polling lifecycle
- [x] T005 - Background polling tests
- [x] T006 - Placeholder markup
- [x] T007 - Placeholder styling
- [x] T008 - Placeholder replacement logic
- [x] T009 - Eager chart polling start
- [x] T010 - Chart elapsed_ms ≈ 0
- [x] T011 - Eager polling tests
- [x] T012 - Queue depth update validation
- [ ] T013 - Form restoration logic
- [ ] T014 - Form restoration tests
- [ ] T015 - Navigation base.html restructure
- [ ] T016 - Navigation content.py update
- [ ] T017 - Navigation styling and JS

**Phase 9 (Final Documentation & Testing)**:
- [ ] T019 - data-model.md documentation
- [ ] T020 - quickstart.md documentation
- [ ] T021 - Full test suite validation

---

## Next Steps

**1. Create foundational setup + research.md**:
```bash
/speckit-implement specs/006-scaling-enhancements/tasks.md T001 T018
```

**2. Review research.md** to validate design decisions before implementation begins

**3. Execute remaining tasks by phase** via `/speckit-implement`:
```bash
/speckit-implement specs/006-scaling-enhancements/tasks.md T002-T005    # US1 (Live metrics)
/speckit-implement specs/006-scaling-enhancements/tasks.md T006-T008    # US2 (Placeholders)
/speckit-implement specs/006-scaling-enhancements/tasks.md T009-T012    # US4 & US6 (Eager polling + queue updates)
/speckit-implement specs/006-scaling-enhancements/tasks.md T013-T014    # US3 (Form restoration)
/speckit-implement specs/006-scaling-enhancements/tasks.md T015-T017    # US5 (Navigation redesign)
/speckit-implement specs/006-scaling-enhancements/tasks.md T019-T021    # Final documentation & testing
```

Ready to begin with T001 + T018 for the review checkpoint?

