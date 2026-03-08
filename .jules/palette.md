## 2024-10-27 - ARIA Alert Role on Dynamic Banners
**Learning:** Dynamically injected error banners (like the Ollama offline warnings) need `role="alert"` so screen readers immediately announce them to users.
**Action:** Always verify dynamically inserted DOM elements conveying critical system states include the appropriate ARIA live region attributes (`role="alert"` or `aria-live="assertive"`).