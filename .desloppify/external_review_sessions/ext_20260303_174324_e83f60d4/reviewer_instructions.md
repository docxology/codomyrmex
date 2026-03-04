# External Blind Review Session

Session id: ext_20260303_174324_e83f60d4
Session token: ceb8ac2fe437104b6ac15b81350a76e9
Blind packet: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/review_packet_blind.json
Template output: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/external_review_sessions/ext_20260303_174324_e83f60d4/review_result.template.json
Claude launch prompt: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/external_review_sessions/ext_20260303_174324_e83f60d4/claude_launch_prompt.md
Expected reviewer output: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/external_review_sessions/ext_20260303_174324_e83f60d4/review_result.json

Happy path:
1. Open the Claude launch prompt file and paste it into a context-isolated subagent task.
2. Reviewer writes JSON output to the expected reviewer output path.
3. Submit with the printed --external-submit command.

Reviewer output requirements:
1. Return JSON with top-level keys: session, assessments, findings.
2. session.id must be `ext_20260303_174324_e83f60d4`.
3. session.token must be `ceb8ac2fe437104b6ac15b81350a76e9`.
4. Include findings with required schema fields (dimension/identifier/summary/related_files/evidence/suggestion/confidence).
5. Use the blind packet only (no score targets or prior context).
