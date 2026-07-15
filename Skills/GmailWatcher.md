---
name: GmailWatcher
description: Monitor Gmail for unread important emails and create action files in Needs_Action folder.
---

## Purpose
Watch Gmail inbox for unread/important emails and save them as `.md` files in `/Needs_Action/` for Claude to process.

## Trigger
Run continuously via `watchers/gmail_watcher.py` or triggered by cron every 2 minutes.

## Steps

1. **Connect to Gmail API** using OAuth credentials from `.env`:
   - `GMAIL_CLIENT_ID`
   - `GMAIL_CLIENT_SECRET`

2. **Fetch unread important emails** with query: `is:unread is:important`

3. **For each new email** (not already in processed_ids):
   - Extract: From, Subject, Snippet, Message ID
   - Create file: `Needs_Action/EMAIL_<message_id>.md`

4. **File format to create:**
```
---
type: email
from: <sender>
subject: <subject>
received: <ISO timestamp>
priority: high
status: pending
---

## Email Content
<snippet>

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
```

5. **Mark email ID as processed** to avoid duplicates.

6. **Update Dashboard.md** — increment "Pending Emails" count.

## Error Handling
- If Gmail API is down: log error to `Logs/YYYY-MM-DD.json`, skip and retry next cycle.
- If credentials expired: write `Needs_Action/ALERT_gmail_auth_expired.md` and pause.

## Output
- New `.md` files in `/Needs_Action/` for each unread email.
- Dashboard.md updated with email count.
