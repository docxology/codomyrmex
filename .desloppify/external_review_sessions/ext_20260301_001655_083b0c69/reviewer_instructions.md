# External Blind Review Session

Session id: ext_20260301_001655_083b0c69
Session token: e0a09e5d696080027d5906a6749b7b68
Blind packet: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/review_packet_blind.json
Template output: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/external_review_sessions/ext_20260301_001655_083b0c69/review_result.template.json
Claude launch prompt: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/external_review_sessions/ext_20260301_001655_083b0c69/claude_launch_prompt.md
Expected reviewer output: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/external_review_sessions/ext_20260301_001655_083b0c69/review_result.json

Happy path:
1. Open the Claude launch prompt file and paste it into a context-isolated subagent task.
2. Reviewer writes JSON output to the expected reviewer output path.
3. Submit with the printed --external-submit command.

Reviewer output requirements:
1. Return JSON with top-level keys: session, assessments, findings.
2. session.id must be `ext_20260301_001655_083b0c69`.
3. session.token must be `e0a09e5d696080027d5906a6749b7b68`.
4. Include findings with required schema fields (dimension/identifier/summary/related_files/evidence/suggestion/confidence).
5. Use the blind packet only (no score targets or prior context).
