---
name: AuditLogger
description: Log every AI action to a structured JSON audit log for security, review, and debugging.
---

## Purpose
Every action taken by the AI Employee must be logged. This skill writes structured log entries to `Logs/YYYY-MM-DD.json`.

## Trigger
Called by any skill after completing (or failing) an action.

## Log Entry Format
```json
{
  "timestamp": "2026-02-25T09:30:00Z",
  "action_type": "email_send | linkedin_post | whatsapp_reply | file_move | approval_created | approval_executed | approval_rejected",
  "actor": "claude_code",
  "target": "<email address | LinkedIn profile | file name>",
  "parameters": {
    "subject": "...",
    "amount": "...",
    "post_content": "..."
  },
  "approval_status": "auto_approved | human_approved | pending | rejected | expired",
  "approved_by": "human | auto",
  "source_task": "<original Needs_Action filename>",
  "result": "success | failed | queued",
  "error": null
}
```

## Steps

1. **Receive action details** from calling skill (action_type, target, parameters, result).

2. **Determine log file path:**
   - `Logs/YYYY-MM-DD.json` (one file per day)
   - Create `Logs/` folder if it doesn't exist.

3. **Append log entry** to today's file (JSON array format).

4. **If action was a failure:**
   - Set `result: "failed"` and populate `error` field.
   - Write alert to `Needs_Action/ALERT_action_failed_<timestamp>.md`.

5. **Retention:** Log files older than 90 days should be archived to `Logs/Archive/`.

## Summary in Dashboard.md
After logging, update `Dashboard.md`:
```
## Audit Log Summary
- Actions today: <count>
- Failures today: <count>
- Pending approvals: <count>
- Last action: <timestamp> — <action_type>
```

## Output
- Structured JSON log entry written to `Logs/YYYY-MM-DD.json`.
- Dashboard.md updated with summary.
