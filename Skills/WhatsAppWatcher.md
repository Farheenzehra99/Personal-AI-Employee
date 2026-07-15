---
name: WhatsAppWatcher
description: Monitor WhatsApp Web for urgent messages using Playwright and create action files.
---

## Purpose
Watch WhatsApp Web for unread messages containing urgent keywords and save them as `.md` files in `/Needs_Action/`.

## Trigger
Run continuously via `watchers/whatsapp_watcher.py` — polls every 30 seconds.

## Keywords to Watch
`urgent`, `asap`, `invoice`, `payment`, `help`, `important`, `deadline`

## Steps

1. **Launch Playwright** with persistent session from `WHATSAPP_SESSION_PATH` (in `.env`).

2. **Open WhatsApp Web** at `https://web.whatsapp.com` — wait for chat list to load.

3. **Find all unread chats** using selector: `[aria-label*="unread"]`

4. **For each unread chat** containing a keyword:
   - Extract: sender name, message text, timestamp
   - Create file: `Needs_Action/WHATSAPP_<sender>_<timestamp>.md`

5. **File format to create:**
```
---
type: whatsapp
from: <sender_name>
received: <ISO timestamp>
priority: high
keywords_matched: [urgent, payment]
status: pending
---

## Message
<message_text>

## Suggested Actions
- [ ] Draft reply
- [ ] Escalate to human approval if payment-related
- [ ] Archive after processing
```

6. **Close browser** session after each check to save memory.

## Security Note
- Never store WhatsApp session in the Obsidian vault or commit to Git.
- Session path must be outside the vault directory.

## Error Handling
- If WhatsApp session expired: write `Needs_Action/ALERT_whatsapp_session_expired.md`.
- If page fails to load within 30s: log and skip cycle.

## Output
- New `.md` files in `/Needs_Action/` for each urgent WhatsApp message.
