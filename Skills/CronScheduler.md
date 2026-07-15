---
name: CronScheduler
description: Define and manage scheduled tasks for the AI Employee using cron (Linux/Mac) or Task Scheduler (Windows).
---

## Purpose
Set up recurring automated tasks so the AI Employee runs on a schedule without manual triggering.

## Scheduled Tasks (Silver Tier)

| Task | Schedule | Cron Expression | Description |
|------|----------|-----------------|-------------|
| Gmail Watcher | Every 2 min | `*/2 * * * *` | Check for new emails |
| LinkedIn Watcher | Every 15 min | `*/15 * * * *` | Check messages/mentions |
| Reasoning Loop | Every 10 min | `*/10 * * * *` | Process Needs_Action files |
| LinkedIn Post | Mon/Wed/Fri 9AM | `0 9 * * 1,3,5` | Draft and queue LinkedIn post |
| Dashboard Refresh | Every hour | `0 * * * *` | Update Dashboard.md summary |
| Approval Expiry Check | Every 6 hours | `0 */6 * * *` | Archive expired approvals |

## How to Set Up (Linux/WSL)

1. **Open crontab editor:**
   ```bash
   crontab -e
   ```

2. **Add these lines:**
   ```bash
   */2 * * * * cd /mnt/d/personal-ai-employee && python watchers/gmail_watcher.py --once >> Logs/cron.log 2>&1
   */15 * * * * cd /mnt/d/personal-ai-employee && python watchers/linkedin_watcher.py --once >> Logs/cron.log 2>&1
   */10 * * * * cd /mnt/d/personal-ai-employee && claude --print "Use ReasoningLoop to process all pending tasks in Needs_Action" >> Logs/cron.log 2>&1
   0 9 * * 1,3,5 cd /mnt/d/personal-ai-employee && claude --print "Use LinkedInAutoPost to draft today's LinkedIn post" >> Logs/cron.log 2>&1
   0 */6 * * * cd /mnt/d/personal-ai-employee && claude --print "Use HumanApprovalRequest to check and expire pending approvals older than 24 hours" >> Logs/cron.log 2>&1
   ```

## How to Set Up (Windows Task Scheduler)

1. Open **Task Scheduler** → Create Basic Task
2. Set trigger: Daily / repeating every N minutes
3. Action: Start a program
   - Program: `wsl.exe`
   - Arguments: `-e bash -c "cd /mnt/d/personal-ai-employee && python watchers/gmail_watcher.py --once"`

## Verify Cron is Running
```bash
crontab -l           # List all scheduled tasks
tail -f Logs/cron.log  # Watch live cron output
```

## Notes
- All watchers should support `--once` flag to run a single check and exit (for cron use).
- Logs are written to `Logs/cron.log` and `Logs/YYYY-MM-DD.json`.
- Never schedule payment actions — those always require manual trigger + approval.

## Output
- Automated execution of watchers and reasoning loop on schedule.
- Logs updated with each run.
