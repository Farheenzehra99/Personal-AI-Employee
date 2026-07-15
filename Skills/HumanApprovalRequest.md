---
name: HumanApprovalRequest
description: Create a human-in-the-loop approval request file for sensitive actions. Claude waits for human to move file to /Approved or /Rejected before acting.
---

## Purpose
For any sensitive action (payments, new contacts, bulk sends, social posts), Claude writes an approval request file and STOPS. It does not act until a human approves.

## Trigger
Called by `ReasoningLoop` or any skill when a sensitive action is detected.

## Sensitive Actions That Always Require Approval
- Any payment or financial transaction (any amount)
- Emails to new/unknown contacts
- Bulk email sends (>1 recipient)
- WhatsApp messages mentioning "payment", "invoice", "transfer"
- LinkedIn or social media posts
- Deleting or moving files outside the vault
- Anything flagged in `Company_Handbook.md`

## Steps

1. **Identify the sensitive action** — what needs to be done, why, and what the risk is.

2. **Create approval request file** in `Pending_Approval/`:
   - Filename: `APPROVAL_<action_type>_<context>_<YYYY-MM-DD>.md`
   - Example: `APPROVAL_PAYMENT_ClientA_2026-02-25.md`

3. **File format:**
```
---
type: approval_request
action: <payment | email_send | linkedin_post | whatsapp_reply | other>
created: <ISO timestamp>
expires: <24 hours from created>
status: pending
risk_level: high | medium
---

## What Claude Wants to Do
<Clear plain-English description of the action>

## Details
- Amount / Recipient / Target: <value>
- Reason: <why this action is needed>
- Source task: <original Needs_Action file name>

## Context
<Relevant excerpt from the original task file>

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder.

## Auto-Expires
If not actioned by <expiry timestamp>, this request will be archived automatically.
```

4. **Update `Dashboard.md`** — increment "Pending Approvals" counter.

5. **DO NOT execute the action.** Claude waits.

6. **When file moves to `/Approved/`:**
   - Execute the approved action using the relevant MCP server or skill.
   - Log result to `Logs/YYYY-MM-DD.json`.
   - Move original task to `Done/`.

7. **When file moves to `/Rejected/`:**
   - Log the rejection.
   - Move original task to `Done/` with status: rejected.
   - Do not retry.

8. **If expired (>24 hours, no action):**
   - Move to `Done/` with status: expired.
   - Log alert to `Dashboard.md`.

## Output
- `Pending_Approval/<filename>.md` created.
- Dashboard updated with pending count.
- Action held until human responds.
