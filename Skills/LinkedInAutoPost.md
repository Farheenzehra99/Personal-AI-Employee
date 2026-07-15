---
name: LinkedInAutoPost
description: Automatically draft and post business content on LinkedIn to generate sales and visibility.
---

## Purpose
Generate and publish a LinkedIn post about the business based on recent activity, goals, or a given topic. Requires human approval before posting.

## Trigger
- Called by scheduler (e.g., every Monday/Wednesday/Friday at 9:00 AM)
- OR manually triggered by dropping a file: `Inbox/linkedin_post_request.md`

## Steps

1. **Read context sources:**
   - `Company_Handbook.md` — brand voice, tone, niche
   - `Business_Goals.md` — current focus areas
   - `Done/` folder — recent completed tasks for content ideas
   - `Dashboard.md` — recent wins or metrics to highlight

2. **Draft a LinkedIn post** following these rules:
   - Professional but conversational tone
   - 150–300 words
   - Include a hook (first line must grab attention)
   - End with a call-to-action (e.g., "DM me", "Comment below", "Link in bio")
   - Add 3–5 relevant hashtags

3. **Write approval request file:**
   ```
   Pending_Approval/LINKEDIN_POST_<YYYY-MM-DD>.md
   ```
   Format:
   ```
   ---
   type: approval_request
   action: linkedin_post
   created: <ISO timestamp>
   expires: <24 hours later>
   status: pending
   ---

   ## Drafted Post
   <post content here>

   ## To Approve
   Move this file to /Approved folder.

   ## To Reject or Edit
   Move this file to /Rejected or edit content and move to /Approved.
   ```

4. **Watch for approval:**
   - If file appears in `/Approved/`: publish via LinkedIn API.
   - If file appears in `/Rejected/`: log and skip. Do not retry.

5. **After posting:**
   - Log post URL and timestamp to `Dashboard.md`
   - Move approval file to `Done/`

## LinkedIn API Action
```
POST https://api.linkedin.com/v2/ugcPosts
Authorization: Bearer <LINKEDIN_ACCESS_TOKEN>
Body: { author, lifecycleState: "PUBLISHED", specificContent: { text } }
```

## Error Handling
- If API fails: log to `Logs/YYYY-MM-DD.json`, write alert to `Needs_Action/ALERT_linkedin_post_failed.md`.
- Never auto-retry a post (risk of duplicate).

## Output
- Post published on LinkedIn.
- `Dashboard.md` updated with post record.
- Task moved to `Done/`.
