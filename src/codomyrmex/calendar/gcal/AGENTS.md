# Google Calendar Submodule Testing Rules

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Instructions

1. This module connects directly to the authenticated Google Calendar API.
2. Under the "Zero-Mock" architecture of Codomyrmex, these API calls must never be intercepted or mocked with fake responses.
3. Test failures due to lack of environment credentials should gracefully report `SkipTest` or utilize `@pytest.mark.skipif`.
