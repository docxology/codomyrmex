# External Blind Review Session

Session id: ext_20260304_000256_b2b7c5ac
Session token: 0256aa6d0928ca2e30c3dc567bf227ab
Blind packet: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/review_packet_blind.json
Template output: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/external_review_sessions/ext_20260304_000256_b2b7c5ac/review_result.template.json
Claude launch prompt: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/external_review_sessions/ext_20260304_000256_b2b7c5ac/claude_launch_prompt.md
Expected reviewer output: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/external_review_sessions/ext_20260304_000256_b2b7c5ac/review_result.json

Happy path:
1. Open the Claude launch prompt file and paste it into a context-isolated subagent task.
2. Reviewer writes JSON output to the expected reviewer output path.
3. Submit with the printed --external-submit command.

Reviewer output requirements:
1. Return JSON with top-level keys: session, assessments, findings.
2. session.id must be `ext_20260304_000256_b2b7c5ac`.
3. session.token must be `0256aa6d0928ca2e30c3dc567bf227ab`.
4. Include findings with required schema fields (dimension/identifier/summary/related_files/evidence/suggestion/confidence).
5. Use the blind packet only (no score targets or prior context).
