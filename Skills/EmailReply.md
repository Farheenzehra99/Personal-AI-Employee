---
name: EmailReply
description: Draft and send email replies via Gmail MCP server. Routes through HumanApprovalRequest for new contacts.
---

## Purpose
Read an email task file from `Needs_Action/`, draft an appropriate reply, and send it via the Gmail MCP server (or queue for approval).

## Trigger
Called by `ReasoningLoop` when a file with `type: email` is found in `Needs_Action/`.

## Steps

1. **Read the email task file** — extract: from, subject, snippet, message_id.

2. **Check if sender is a known contact:**
   - Known contact = previously replied to, or in `Company_Handbook.md` contacts list.
   - Unknown contact → route to `HumanApprovalRequest` skill.

3. **Draft reply** following Company_Handbook.md tone rules:
   - Professional and polite
   - Concise (under 150 words unless detailed response needed)
   - Address the sender's specific question or request

4. **For known contacts — send directly via Gmail MCP:**
   ```
   Use MCP tool: email_send
   to: <sender_email>
   subject: Re: <original_subject>
   body: <drafted_reply>
   ```

5. **For unknown contacts — create approval file:**
   ```
   Pending_Approval/APPROVAL_EMAIL_<sender>_<date>.md
   ```
   Include the drafted reply for human review.

6. **Log action** to `Logs/YYYY-MM-DD.json`:
   ```json
   {
     "timestamp": "<ISO>",
     "action_type": "email_send",
     "actor": "claude_code",
     "target": "<sender_email>",
     "approval_status": "auto_approved | pending_human",
     "result": "sent | queued"
   }
   ```

7. **Move task file to `Done/`** after sending or queuing.

8. **Update `Dashboard.md`** — decrement pending emails, increment processed.

## MCP Server Required
- Server: `email-mcp`
- Capabilities: `email_send`, `email_draft`, `email_search`

## Output
- Email sent or queued for approval.
- Log entry created.
- Task moved to `Done/`.
