# Quickstart: ACA Scaling Dashboard v2 — Manual Testing Scenarios

**Date**: 2026-04-30  
**Objective**: Verify all v2 features work end-to-end on desktop (1280px) and mobile (375px)  
**Prerequisites**: Flask app running on http://localhost:5000, ACA API mocked or available

---

## Test Environment Setup

```bash
# Start the Flask dev server
cd personal_website
python app.py

# In another terminal, optionally set background polling interval
export BACKGROUND_POLLING_INTERVAL_MS=5000  # 5 seconds for faster testing
```

---

## Feature 1: Background Polling (US1)

**Scenario**: Metrics update continuously when no scaling event is active.

### Desktop Test (1280px)
1. Open http://localhost:5000/scaling
2. Observe the page loads with:
   - Queue depth and replica count visible in metric panels
   - Either real values or placeholders (see Feature 2)
   - Send messages form visible
3. Wait 5-10 seconds without submitting
4. Verify metric values update (queue depth should change if ACA is sending data)
5. **Expected**: Metrics update every ~30 seconds (or BACKGROUND_POLLING_INTERVAL_MS)

### Mobile Test (375px)
1. Open DevTools (F12) → Responsive mode → select 375px (iPhone SE)
2. Navigate to http://localhost:5000/scaling
3. Verify metric panels are visible and readable
4. Wait 5-10 seconds
5. Verify metrics update on mobile (same interval as desktop)
6. **Expected**: Metrics update every ~30 seconds, layout remains responsive

---

## Feature 2: Placeholders (US2)

**Scenario**: Page loads immediately with placeholder content, then replaces with real data.

### Desktop Test (1280px)
1. Open http://localhost:5000/scaling in a fresh browser tab
2. Note the time of page load
3. Observe metric panels:
   - Check for "Loading…" placeholder text with gray background
   - OR real values if API is extremely fast
4. Wait <500ms
5. Verify placeholders are replaced with real values (queue depth and replica count numbers)
6. **Expected**: No layout shift; metrics appear smoothly within 500ms

### Mobile Test (375px)
1. In DevTools responsive mode (375px), hard refresh (Ctrl+Shift+R)
2. Observe metric panels load immediately
3. Verify placeholders (if visible) have sufficient height to prevent layout shift
4. Verify placeholder text and real values don't overflow on narrow screen
5. **Expected**: Responsive layout, no overflow, clean transition

---

## Feature 3: Eager Chart Polling (US4)

**Scenario**: Chart data accumulates immediately upon form submission, before 202 response.

### Desktop Test (1280px)
1. Navigate to /scaling
2. Fill form with a valid count (e.g., 100)
3. Click "Send messages"
4. Observe:
   - Form disappears immediately
   - Chart section appears immediately
   - Status message shows "Messages sent — monitoring scaling activity."
   - **Timing**: All changes happen instantly (before 202 response)
5. Wait 2-3 seconds
6. Verify chart shows data points (line or dots, depending on # of readings)
7. **Expected**: Chart has at least 1-2 points with elapsed_ms ≈ 0-3000ms

### Mobile Test (375px)
1. In DevTools responsive mode (375px)
2. Fill form and submit
3. Verify form transitions to chart view immediately
4. Verify chart is readable on narrow screen (responsive width)
5. Verify chart data accumulates (points appear over time)
6. **Expected**: Chart is responsive and data updates visible

---

## Feature 4: Queue Depth Live Updates (US6)

**Scenario**: Queue depth metric updates with each polling cycle during monitoring.

### Desktop Test (1280px)
1. Navigate to /scaling
2. Submit messages (e.g., count=50)
3. Observe chart and queue depth metric in real-time:
   - Queue depth number updates every ~5 seconds (pollingIntervalMs)
   - Chart receives new data point each poll
   - Queue depth value matches latest chart reading
4. Continue monitoring until queue reaches 0 or timeout
5. Verify final queue depth remains visible after monitoring stops
6. **Expected**: Queue metric updates in sync with chart, final value is 0

### Mobile Test (375px)
1. Submit messages on mobile (375px)
2. Verify queue depth metric is visible and readable
3. Verify updates happen without jank
4. Verify metric value stays in sync with chart
5. **Expected**: Responsive layout, smooth updates

---

## Feature 5: Form Restoration (US3)

**Scenario**: Send form reappears after scaling event completes, allowing multiple tests.

### Desktop Test (1280px)
1. Navigate to /scaling and submit a test (count=10)
2. Monitor until queue clears (or timeout after 120 seconds)
3. Observe:
   - Status message: "Queue cleared — scaling event complete." (if queue=0)
   - OR "Monitoring ended — maximum duration reached..." (if timeout)
   - Chart remains visible
   - Form reappears within 500ms
   - Input field is empty
   - Button is enabled
4. Submit a second test (count=20)
5. Verify the second scaling event works identically to the first
6. **Expected**: Form restoration works; user can run multiple tests on same page

### Mobile Test (375px)
1. Submit messages and wait for completion
2. Verify form reappears and is fully interactive
3. Verify form doesn't overflow on narrow screen
4. Submit a second test
5. **Expected**: Form restoration works on mobile; multiple tests possible

---

## Feature 6: Navigation Redesign (US5)

### Desktop Test (1280px)
1. Open http://localhost:5000/ (home page)
2. Observe navigation bar at top:
   - "Home" visible and linked
   - "Demos" visible with dropdown arrow
   - "About", "Contact", "Updates" visible
   - Scaling not visible as top-level item
3. Hover over "Demos"
   - Submenu appears with "Cricket Data" and "Scaling" options
   - Arrow points down (or rotates)
4. Click "Scaling" in submenu
   - Navigate to /scaling page
   - "Scaling" link is highlighted (active state)
   - On /scaling, Demos submenu is open/active
5. Return to home page
   - "Demos" is no longer active
   - "Home" is highlighted (active)
6. **Expected**: Hover shows submenu; keyboard focus also works; active states correct

### Mobile Test (375px)
1. Open http://localhost:5000/ in responsive mode (375px)
2. Observe "Demos" in navigation
3. Tap "Demos" button
   - Submenu expands (slides down or fades in)
   - Arrow rotates to point up
4. Verify "Cricket Data" and "Scaling" are visible and tappable
5. Tap "Scaling"
   - Navigate to /scaling
   - Mobile nav may collapse or stay open
6. Return to home
7. Tap "Demos" again
   - Submenu collapses
   - Arrow rotates back down
8. **Expected**: Toggle works on mobile; submenu visible/hidden correctly; responsive

---

## Error Handling Scenarios

### Scenario: Backend API fails during background polling
1. Navigate to /scaling
2. (Optional) Mock backend API to fail or simulate error
3. Observe metrics don't update, but page doesn't break
4. Status message may appear (depends on implementation)
5. **Expected**: Silent error; page remains functional

### Scenario: Backend API fails during monitoring
1. Submit messages and start monitoring
2. (Optional) Stop backend or simulate 500 error
3. Observe:
   - Polling stops
   - Status message: "Monitoring stopped — unable to reach the scaling service."
   - Form reappears
4. **Expected**: Error handled gracefully; form restored; user can retry

### Scenario: Queue never clears (zero replicas)
1. Submit messages
2. Observe replicas drop to 0
3. After 30 seconds of zero replicas:
   - Status message: "Replicas did not recover — scaling may have stalled."
   - Monitoring stops
   - Form reappears
4. **Expected**: Timeout prevents indefinite monitoring

---

## Automated Test Coverage

Run the test suite to verify all scenarios programmatically:

```bash
# All scaling tests
pytest tests/test_routes.py -k "scaling" -v

# Specific features
pytest tests/test_routes.py -k "background_polling" -v
pytest tests/test_routes.py -k "placeholder" -v
pytest tests/test_routes.py -k "eager_polling" -v
pytest tests/test_routes.py -k "form_restoration" -v

# Full suite (all routes)
pytest tests/test_routes.py -v
```

**Test Expectations**:
- All scaling tests pass (15/15)
- No regressions in existing routes (home, about, contact, matches, updates)
- Navigation structure correctly rendered

---

## Responsive Design Verification Checklist

- [ ] Mobile (375px): All elements fit without horizontal scroll
- [ ] Mobile (375px): Touch targets are at least 44px × 44px
- [ ] Mobile (375px): Form inputs are readable and usable
- [ ] Mobile (375px): Chart is visible and responsive
- [ ] Mobile (375px): Navigation toggle works and submenus are accessible
- [ ] Tablet (768px): Layout looks good at intermediate size
- [ ] Desktop (1280px+): Dropdowns/hovers work on all interactive elements
- [ ] Desktop (1280px+): Chart is readable with sufficient width
- [ ] All breakpoints: Text is legible, colors meet contrast requirements

---

## Performance Notes

- **Placeholder load**: <500ms from page load to API replacement
- **Chart rendering**: <100ms per data point (client-side)
- **Background polling**: 30 second interval to avoid server load
- **Active monitoring**: 5 second interval for real-time feedback
- **Mobile responsiveness**: Tap/click events should respond within 200ms

---

## Common Issues & Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Placeholders never replace | API failing silently | Check browser console for fetch errors |
| Form doesn't restore | Event completion not detected | Verify queue reaches 0 or timeout fires |
| Submenu doesn't open on desktop | CSS not loaded | Verify site.css is linked and includes submenu styles |
| Submenu toggle not working on mobile | JavaScript not running | Check site_nav.js is loaded; verify no JS errors |
| Chart data missing initial points | Eager polling didn't start | Verify monitoringStart captured before fetch |

---

## Sign-Off

Once all scenarios pass on desktop and mobile, the ACA Scaling Dashboard v2 is ready for production.

**Tester**: [Name]  
**Date**: [Date]  
**Devices tested**: [List]  
**Issues found**: [List or "None"]
