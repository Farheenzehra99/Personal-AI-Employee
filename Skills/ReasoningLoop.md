---
name: ReasoningLoop
description: Claude's core reasoning loop — reads Needs_Action, creates Plan.md with step-by-step actions, then executes or routes for approval.
---

## Purpose
The reasoning brain of the AI Employee. For every file in `Needs_Action/`, Claude reads it, understands the task type, creates a `Plan.md`, and either executes or routes to human approval.

## Trigger
- Triggered by watcher detecting new file in `Needs_Action/`
- OR run manually: "Use ReasoningLoop to process all pending tasks"

## Steps

1. **Scan `Needs_Action/` folder** — list all `.md` files not yet in progress.

2. **For each file**, read its frontmatter to determine `type`:
   - `email` → use EmailReply skill
   - `whatsapp` → use WhatsAppReply skill
   - `linkedin_message` → use LinkedInAutoPost or draft reply
   - `linkedin_connection` → evaluate and accept/ignore
   - `file_drop` → use BasicTaskProcessor skill
   - `approval_request` → skip (already waiting for human)

3. **Create or update `Plan.md`** with this structure:
   ```
   ---
   generated: <ISO timestamp>
   tasks_found: <count>
   ---

   # Today's Action Plan

   ## Pending Tasks
   | File | Type | Proposed Action | Approval Needed |
   |------|------|-----------------|-----------------|
   | EMAIL_abc123.md | email | Reply to sender | No |
   | WHATSAPP_Ali.md | whatsapp | Draft reply re: invoice | Yes |

   ## Execution Order
   1. [ ] Process EMAIL_abc123.md
   2. [ ] Process WHATSAPP_Ali.md — await approval
   ```

4. **Execute low-risk tasks automatically** (per Company_Handbook.md rules):
   - Reply to known email contacts
   - Archive processed emails
   - Accept LinkedIn connections (non-spammy profiles)

5. **Route high-risk tasks to approval** using `HumanApprovalRequest` skill:
   - Payments > $50
   - New email contacts
   - WhatsApp messages mentioning payment/invoice
   - Social media posts

6. **Update `Dashboard.md`** with:
   - Tasks processed today
   - Tasks pending approval
   - Last reasoning loop run time

7. **Move completed task files to `Done/`** using `MoveToDone` skill.

## Decision Rules (from Company_Handbook.md)
- Always be polite in replies.
- Flag any payment mention for human approval.
- Never send bulk emails.
- Post on LinkedIn max 3x per week.

## Output
- Updated `Plan.md` with today's action plan.
- Low-risk tasks executed.
- High-risk tasks queued in `Pending_Approval/`.
- `Dashboard.md` updated.
