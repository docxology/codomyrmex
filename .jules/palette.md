## 2024-02-23 - Visual Feedback for Async Buttons
**Learning:** In async contexts (like chat submissions), simply disabling the input field isn't enough UX feedback. If the submit button itself isn't disabled and lacks a loading indicator, users might attempt double submissions or think the app is unresponsive.
**Action:** Always pair `input.disabled = true` with a disabled submit button state, ideally injecting a `.loader` visual indicator and updating the button text (e.g. 'Sending...'). Re-enable in the `finally` block to ensure recovery on error.
