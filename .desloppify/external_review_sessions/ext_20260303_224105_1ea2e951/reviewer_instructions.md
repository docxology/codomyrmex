# External Blind Review Session

Session id: ext_20260303_224105_1ea2e951
Session token: 8d285fc2e1977559a31b6f02f9918f0b
Blind packet: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/review_packet_blind.json
Template output: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/external_review_sessions/ext_20260303_224105_1ea2e951/review_result.template.json
Claude launch prompt: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/external_review_sessions/ext_20260303_224105_1ea2e951/claude_launch_prompt.md
Expected reviewer output: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/external_review_sessions/ext_20260303_224105_1ea2e951/review_result.json

Happy path:
1. Open the Claude launch prompt file and paste it into a context-isolated subagent task.
2. Reviewer writes JSON output to the expected reviewer output path.
3. Submit with the printed --external-submit command.

Reviewer output requirements:
1. Return JSON with top-level keys: session, assessments, findings.
2. session.id must be `ext_20260303_224105_1ea2e951`.
3. session.token must be `8d285fc2e1977559a31b6f02f9918f0b`.
4. Include findings with required schema fields (dimension/identifier/summary/related_files/evidence/suggestion/confidence).
5. Use the blind packet only (no score targets or prior context).
