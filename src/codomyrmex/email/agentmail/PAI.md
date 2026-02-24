# AgentMail — PAI Algorithm Integration

## Module Role in PAI Phases

| Phase | AgentMail Capability | PAI Usage |
|-------|---------------------|-----------|
| OBSERVE | `list_messages`, `list_threads` | Gather incoming information context |
| THINK | `get_message`, `get_thread` | Deep-read specific messages for analysis |
| PLAN | `list_drafts`, `create_draft` | Draft responses before committing to send |
| BUILD | `update_draft`, `send_draft` | Refine and finalize outgoing communications |
| EXECUTE | `send_message`, `reply_to_message`, `forward_message` | Deliver actions via email |
| VERIFY | `get_message` (confirm delivery) | Check sent messages exist and look correct |
| LEARN | `get_inbox_metrics` | Analyze email performance and patterns |

## MCP Tools Mapping

| PAI Need | MCP Tool |
|----------|----------|
| Check inbox | `agentmail_list_messages` |
| Read a message | `agentmail_get_message` |
| Reply to context | `agentmail_reply_to_message` |
| Send update | `agentmail_send_message` |
| Create workspace | `agentmail_create_inbox` |
| Monitor inbox | `agentmail_create_webhook` |
| Browse conversations | `agentmail_list_threads` |
| Audit inboxes | `agentmail_list_inboxes` |

## ISC Criteria Examples

When building Ideal State Criteria involving email:

```
ISC-Email-1: Incoming messages processed within 30 seconds of receipt
ISC-Email-2: Replies contain original message context in thread
ISC-Email-3: No API credentials appear in any outgoing email body
ISC-A-Email-1: No emails sent without explicit user approval
ISC-A-Email-2: No inbox deleted without confirmation checkpoint
```

## Recommended Capability Selection

For email-related tasks in the PAI Algorithm:

- **OBSERVE phase**: Use `agentmail_list_messages` to surface new context
- **EXECUTE phase**: Use `agentmail_send_message` or `agentmail_reply_to_message`
- **VERIFY phase**: Use `agentmail_get_message` to confirm delivery

## Security Notes

1. `AGENTMAIL_API_KEY` must never appear in PRD files, task descriptions, or logs
2. Treat inbox contents as sensitive — avoid logging full message bodies
3. Webhook endpoints must use HTTPS
4. Pod IDs and inbox IDs are safe to log (non-sensitive identifiers)
