# Data Model: ACA Scaling Dashboard v2

**Last Updated**: 2026-04-30  
**Scope**: Polling configuration, placeholder states, form restoration, and navigation hierarchy

---

## Polling Configuration Entity

**Purpose**: Centralized configuration for background and active monitoring polling behavior.

**Fields**:
- `backgroundPollingIntervalMs` (int): Interval for background polling when no scaling event is active. Default: 30000ms (30 seconds).
  - Consumed by: `/scaling` route, passed to template via `data-background-polling-interval-ms`
  - Used by: `static/js/scaling.js` to configure `setInterval()` for `backgroundPollStatus()`
  
- `pollingIntervalMs` (int): Interval for active monitoring polling during scaling events. Default: 5000ms (5 seconds).
  - Consumed by: `/scaling` route, passed to template via `data-polling-interval-ms`
  - Used by: `static/js/scaling.js` to configure `setInterval()` for `pollStatus()`
  
- `maxMonitoringSeconds` (int): Maximum duration to poll for queue clearing. Default: 120 seconds.
  - Consumed by: `/scaling` route, passed to template via `data-max-monitoring-seconds`
  - Used by: `static/js/scaling.js` to detect timeout condition
  
- `zeroReplicaTimeoutSeconds` (int): Duration to wait if replicas drop to 0 before stopping monitoring. Default: 30 seconds.
  - Consumed by: `/scaling` route, passed to template via `data-zero-replica-timeout-seconds`
  - Used by: `static/js/scaling.js` to trigger warning and stop polling
  
- `minMessages` (int): Minimum message count for form validation. Default: 1.
  - Consumed by: `/scaling` route, passed to template via `data-min-messages`
  - Used by: `static/js/scaling.js` to validate user input and `templates/scaling.html` for input min attribute
  
- `maxMessages` (int): Maximum message count for form validation. Default: 1000.
  - Consumed by: `/scaling` route, passed to template via `data-max-messages`
  - Used by: `static/js/scaling.js` to validate user input and `templates/scaling.html` for input max attribute

**Lifecycle**:
1. Created in `app.py` `scaling_config` dictionary
2. Passed to template via route context unpacking: `**scaling_config`
3. Read by JavaScript from `data-*` attributes on `.dashboard-container` element
4. Parsed to integers on page load in `static/js/scaling.js`

---

## Placeholder State Machine

**Purpose**: Manage visual feedback during asynchronous metric panel population.

**States**:

### Rendering State (Server-side, template)
- **Initial render**: Metric panel `.metric-value` has `.placeholder` class if `queue_depth is none` or `replica_count is none`
- **Placeholder content**: "Loading…" text indicates data is being fetched
- **Placeholder styling**: Gray background (rgba with 0.15 opacity), matching height of real metrics, flexbox centered

### Runtime State (Client-side, JavaScript)
- **Placeholder exists**: `.metric-value.placeholder` is visible, contains "Loading…"
- **API call pending**: `replacePlaceholders()` fetch is in-flight to `/scaling/api/status`
- **Placeholder removed**: On 200 response, `classList.remove("placeholder")` and `textContent` updated to real value

**CSS Classes**:
- `.metric-value.placeholder`: Applied during server render if data is `none`
  - `background: rgba(24, 22, 26, 0.15)`
  - `border-radius: 0.25rem`
  - `padding: 0.5rem`
  - `min-height: 3.5rem`
  - `display: flex; align-items: center; justify-content: center;`

**Edge Cases**:
1. API fails during `replacePlaceholders()`: Placeholder remains visible (silent error handling)
2. User submits form while placeholder is visible: Monitoring state starts immediately regardless of placeholder status
3. Backend returns different data between renders: Placeholder replaced with new value; no flicker due to flexbox centering

---

## Form Restoration State Machine

**Purpose**: Enable multiple scaling experiments without page reload by restoring form after each event completes.

**States**:

### Idle State
- Form visible: `form.hidden = false`
- Chart hidden: `chartSection.hidden = true`
- Input cleared: `countInput.value = ""`
- Button enabled: `sendButton.disabled = false`
- Error cleared: `inlineError.hidden = true`
- Background polling active: `backgroundPollingTimer !== null`

### Monitoring State
- Form hidden: `form.hidden = true`
- Chart visible: `chartSection.hidden = false`
- Button disabled: `sendButton.disabled = true`
- Status message shown: `statusMessage.hidden = false`
- Active polling: `pollTimer !== null`
- Background polling stopped: `backgroundPollTimer === null`

### Restoration Trigger Events
1. **Queue cleared**: `queueLength === 0` after polling
   - Call `restoreForm()` → transition to Idle State
   - Show message: "Queue cleared — scaling event complete."
   - Resume background polling

2. **Monitoring timeout**: `elapsed >= maxMonitoringSeconds * 1000`
   - Call `restoreForm()` → transition to Idle State
   - Show message: "Monitoring ended — maximum duration reached without the queue clearing."
   - Resume background polling

3. **Zero replicas timeout**: `replicaCount === 0` for `zeroReplicaTimeoutSeconds`
   - Call `restoreForm()` → transition to Idle State
   - Show message: "Replicas did not recover — scaling may have stalled."
   - Resume background polling

4. **API error during monitoring**: Status code !== 200
   - Call `restoreForm()` → transition to Idle State
   - Show message: "Monitoring stopped — [error details]"
   - Resume background polling

5. **Submission error**: 400/429/500 on `/scaling/api/send`
   - Call `restoreForm()` → transition to Idle State
   - Show inline error or status message
   - Resume background polling

6. **Network error**: `.catch()` on fetch to `/scaling/api/send`
   - Call `restoreForm()` → transition to Idle State
   - Show message: "Request failed. Check your connection and try again."
   - Resume background polling

**Implementation**:
- `restoreForm()` function encapsulates all transitions:
  ```javascript
  function restoreForm() {
      form.hidden = false;
      countInput.value = "";
      sendButton.disabled = false;
      clearInlineError();
  }
  ```
- Called from 7 completion points throughout the monitoring lifecycle
- Ensures consistent UX across all exit paths

---

## Navigation Hierarchy Entity

**Purpose**: Represent top-level and submenu navigation structure for desktop and mobile views.

**Structure**:
```javascript
"navigation": [
    {"label": "Home", "endpoint": "home", "slug": "home"},
    {
        "label": "Demos",
        "slug": "demos",
        "submenu": [
            {"label": "Cricket Data", "endpoint": "matches", "slug": "matches"},
            {"label": "Scaling", "endpoint": "scaling", "slug": "scaling"},
        ]
    },
    {"label": "About", "endpoint": "about", "slug": "about"},
    {"label": "Contact", "endpoint": "contact", "slug": "contact"},
    {"label": "Updates", "endpoint": "updates", "slug": "updates"},
]
```

**Navigation Item Fields**:
- `label` (string): Display text for nav link
- `endpoint` (string): Flask route endpoint for `url_for()`
- `slug` (string): Unique identifier used for active state detection
- `submenu` (array, optional): Child items for nested navigation

**Active State Detection**:
- Top-level: Item marked active if `item.slug == page_name`
- Submenu: Item marked active if `subitem.slug == page_name`
- Active items get `is-active` CSS class for styling

**Desktop Behavior** (`min-width: 861px`):
- Demos item shows as button with dropdown arrow
- Submenu appears on hover/focus via CSS `:hover` and `:focus-within`
- Arrow rotates to indicate open state

**Mobile Behavior** (`max-width: 860px`):
- Demos item shows as button with toggle arrow
- Submenu toggled via JavaScript click handler
- Arrow rotates on `aria-expanded="true"`
- Submenu indented with left border for visual hierarchy

**Accessibility**:
- Toggle buttons have `aria-expanded` attribute
- Submenus have `aria-hidden` attribute
- Links maintain semantic `<a>` tags for direct navigation
- Keyboard navigation supported via focus-within

---

## Relationships & State Flow

```
┌─ Polling Config ───────────────┐
│  • Background interval: 30s     │ ← Environment variable (app.py)
│  • Monitoring interval: 5s      │ ← Passed to template
│  • Max monitoring: 120s         │ ← Read by JavaScript
│  • Min/Max messages: 1/1000     │
└─────────────────────────────────┘
         ↓
┌─ Placeholder State ────────────┐
│  1. Initial render: "Loading…" │ ← Server-side class
│  2. API call: /status          │ ← Client replaces on 200
│  3. Final: Real values         │ ← Remove .placeholder class
└─────────────────────────────────┘
         ↓
┌─ Form Restoration State ───────┐
│  1. Idle: Form visible         │ ← Background polling
│  2. Monitoring: Form hidden    │ ← Active polling
│  3. Restore: Form visible      │ ← Event completes
│  4. Repeat: Ready for new test │ ← User can resubmit
└─────────────────────────────────┘
         ↓
┌─ Navigation Hierarchy ─────────┐
│  • Top-level: Home, Demos, ... │ ← Always visible
│  • Submenu: Cricket Data, ...  │ ← Toggle on mobile
│  • Active state: Highlight     │ ← Detect page_name
└─────────────────────────────────┘
```

---

## Configuration Defaults

See `app.py` `scaling_config` dictionary for current values:
```python
scaling_config = {
    'backgroundPollingIntervalMs': int(os.getenv('BACKGROUND_POLLING_INTERVAL_MS', 30000)),
    'pollingIntervalMs': 5000,
    'maxMonitoringSeconds': 120,
    'zeroReplicaTimeoutSeconds': 30,
    'minMessages': 1,
    'maxMessages': 1000,
}
```

Environment variables:
- `BACKGROUND_POLLING_INTERVAL_MS`: Override background polling interval (milliseconds)
