---
name: LinkedInWatcher
description: Monitor LinkedIn for new messages, connection requests, and mentions — create action files.
---

## Purpose
Watch LinkedIn for incoming messages, connection requests, and post mentions that need a response or action.

## Trigger
Run via cron every 15 minutes: `watchers/linkedin_watcher.py`

## Steps

1. **Connect to LinkedIn API** using credentials from `.env`:
   - `LINKEDIN_ACCESS_TOKEN`
   - `LINKEDIN_CLIENT_ID`
   - `LINKEDIN_CLIENT_SECRET`

2. **Check for:**
   - New unread messages (LinkedIn Messaging API)
   - Pending connection requests
   - Post comments/mentions on your recent posts

3. **For each new item**, create file in `Needs_Action/`:
   - Messages: `LINKEDIN_MSG_<sender_id>_<timestamp>.md`
   - Connections: `LINKEDIN_CONN_<person_id>_<timestamp>.md`
   - Mentions: `LINKEDIN_MENTION_<post_id>_<timestamp>.md`

4. **File format:**
```
---
type: linkedin_message | linkedin_connection | linkedin_mention
from: <sender_name>
received: <ISO timestamp>
priority: medium
status: pending
---

## Content
<message or context>

## Suggested Actions
- [ ] Reply to message
- [ ] Accept/ignore connection request
- [ ] Comment on mention
```

5. **Update Dashboard.md** — log LinkedIn activity count.

## Error Handling
- If token expired: write `Needs_Action/ALERT_linkedin_token_expired.md`.
- Rate limit hit: back off for 15 minutes.

## Output
- Action files in `/Needs_Action/` for each LinkedIn interaction.
