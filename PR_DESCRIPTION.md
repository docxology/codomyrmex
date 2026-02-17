# Pull Request: Local Web Viewer for Education Modules

## Description
Add a browser-based local web viewer for the Codomyrmex education system. Extends the existing `WebsiteServer` with REST API endpoints, Jinja2 templates, and vanilla JS for curriculum management, interactive tutoring, assessment/certification, and a content browser. Includes light/dark theme toggle and a startup script.

## Type of Change
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [x] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🎨 Code style/formatting
- [ ] ♻️ Refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [x] 🧪 Test updates
- [ ] 🔧 Build/CI changes
- [ ] 📦 Dependencies update

## Related Issues
Implements the local-web-viewer spec (`.kiro/specs/local-web-viewer/`).

## Changes Made

### New Files
- `src/codomyrmex/website/education_provider.py` — EducationDataProvider bridging API layer to education modules (curriculum, tutoring, assessment, content browsing)
- `src/codomyrmex/website/__main__.py` — Entry point for `python -m codomyrmex.website`
- `src/codomyrmex/website/assets/js/education.js` — Frontend JS: theme toggle, curriculum CRUD, quiz interaction, exam submission, learning path rendering, content browser, error notifications
- `src/codomyrmex/website/templates/curriculum.html` — Curriculum management page
- `src/codomyrmex/website/templates/tutoring.html` — Interactive tutoring page
- `src/codomyrmex/website/templates/assessment.html` — Assessment and certification page
- `src/codomyrmex/website/templates/content.html` — Content browser with file tree and preview
- `start_viewer.sh` — Startup script (dependency check, port check, server launch, browser open)

### New Test Files
- `src/codomyrmex/tests/test_education_provider.py` — Properties 2-5: curriculum CRUD round trips
- `src/codomyrmex/tests/test_education_tutoring.py` — Properties 8-11: session creation, quiz, answer evaluation, progress
- `src/codomyrmex/tests/test_education_assessment.py` — Properties 12-14: exam questions, grading invariants, certificate round trip
- `src/codomyrmex/tests/test_education_learning_path.py` — Properties 6-7: prerequisite ordering, level filtering
- `src/codomyrmex/tests/test_education_api.py` — Properties 15-16: API JSON structure, error handling
- `src/codomyrmex/tests/test_content_browser.py` — Properties 17-18: content tree/file correctness
- `src/codomyrmex/tests/test_service_browser.py` — Property 1: resource field completeness
- `src/codomyrmex/tests/test_theme.py` — Property 19: theme toggle logic

### Modified Files
- `src/codomyrmex/website/server.py` — Added education API endpoints (18 handlers), `do_PUT` method, `EducationDataProvider` init, CORS updates
- `src/codomyrmex/website/generator.py` — Added education templates to pages list
- `src/codomyrmex/website/templates/base.html` — Added Education nav group, theme toggle button, two-row header layout
- `src/codomyrmex/website/assets/css/style.css` — Added CSS custom properties for light/dark themes, theme toggle styles, notification banner styles, improved nav layout
- `src/codomyrmex/education/curriculum/curriculum.py` — Fixed learning path level-skip bug (`>` → `min()`)
- `src/codomyrmex/education/tutoring/tutor.py` — Fixed `datetime.utcnow()` deprecation → `datetime.now(timezone.utc)`
- `src/codomyrmex/education/certification/assessment.py` — Fixed `datetime.utcnow()` deprecation → `datetime.now(timezone.utc)`

### Spec Files
- `.kiro/specs/local-web-viewer/requirements.md`
- `.kiro/specs/local-web-viewer/design.md`
- `.kiro/specs/local-web-viewer/tasks.md`

## Module(s) Affected
- [x] Website (`src/codomyrmex/website/`)
- [x] Education (`src/codomyrmex/education/`)
- [x] Tests (`src/codomyrmex/tests/`)

## Testing

### Test Coverage
- [x] Unit tests added/updated
- [x] Integration tests added/updated
- [x] Property-based tests added (Hypothesis)
- [x] All existing tests pass

### Test Results
28 tests, 28 passed, 0 failed, 2 warnings (unrelated deprecation notices from cloud/infomaniak and embodiment modules).

19 correctness properties validated via Hypothesis property-based testing covering curriculum CRUD, tutoring sessions, assessment grading, API structure, content browsing, and theme toggle.

## Documentation
- [x] Spec documents created (requirements, design, tasks)
- [x] No external documentation changes needed

## Breaking Changes
None — all changes are additive. Existing pages and API endpoints are unaffected.

## Performance Impact
- [x] No performance impact on existing functionality

## Security Considerations
- [x] Content browser validates paths to prevent directory traversal
- [x] API origin validation on POST/PUT requests
- [x] HTML output uses `escapeHtml()` to prevent XSS

## Deployment Notes
- [x] No new dependencies required
- [x] Run via `./start_viewer.sh` or `python -m codomyrmex.website`

## Checklist

### Code Quality
- [x] Code follows the project's coding standards
- [x] Self-review completed
- [x] Code is properly commented
- [x] No debugging code left in
- [x] Error handling implemented appropriately

### Testing
- [x] All tests pass locally
- [x] New tests added for new functionality
- [x] Edge cases considered and tested
- [x] Test coverage is adequate

### Documentation
- [x] Documentation updated where necessary
- [x] API changes documented in design.md
- [ ] CHANGELOG.md updated
- [x] Commit messages follow conventional format

### Dependencies and Security
- [x] No new dependencies added
- [x] Security implications considered
- [x] No sensitive information exposed

### Collaboration
- [x] PR title clearly describes the change
- [x] PR description is comprehensive
- [ ] Reviewers assigned
- [ ] Labels added appropriately

---

**By submitting this pull request, I confirm that:**
- [x] I have read the Contributing Guidelines
- [x] My code follows the Contributing Guidelines
- [x] I have followed the Code of Conduct
- [x] My contribution is made under the same license as the project (MIT)
- [x] I am willing to address feedback and make necessary changes
