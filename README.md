# AI Employee Vault

A local AI-powered autonomous task processing system using Claude Code, watchdog, and MCP integrations.

## Tiers

| Tier | Status | Description |
|------|--------|-------------|
| Bronze | ✅ Complete | File drop → Watcher → BasicTaskProcessor → Done |
| Silver | ✅ Complete | Multi-channel inputs → ReasoningLoop → Approval Gate → MCP Actions → Scheduler |
| Gold | 🔜 Planned | Full autonomy: memory, multi-agent, voice, CRM integrations |

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
playwright install  # For WhatsApp/LinkedIn watchers

# 2. Setup cron jobs (Linux/Mac)
./setup_cron.sh

# 3. Or run watchers manually
python watchers/gmail_watcher.py --once
python watchers/whatsapp_watcher.py --once
python watchers/linkedin_watcher.py --once
python watchers/orchestrator.py --once
```

---

## Bronze Tier (Complete)

Basic file-processing pipeline.

### Setup
1. Run `claude` in this folder.
2. Install watchdog:
   ```bash
   pip install watchdog
   ```

### Architecture
- **Vault folders:** `Inbox/` → `Needs_Action/` → `Done/`
- **Watcher:** `watchers/filesystem_watcher.py` monitors `Inbox/` and moves files to `Needs_Action/`
- **Skills:** `BasicTaskProcessor`, `MoveToDone`, `ReadNeedsAction`, `WritePlanOrSummary`
- **Dashboard:** `Dashboard.md` tracks processed tasks

### How to Test (Bronze)
1. Drop a file into `Inbox/`
2. Run the watcher:
   ```bash
   python watchers/filesystem_watcher.py
   ```
3. Trigger Claude: _"Use BasicTaskProcessor to process incoming tasks"_
4. Claude reads `Needs_Action/`, creates `Plan.md`, updates `Dashboard.md`, moves files to `Done/`

---

## Silver Tier (Complete)

Multi-channel inputs, intelligent reasoning, human-in-the-loop approval, MCP actions, and scheduled automation.

### New Capabilities
- **Multi-channel watchers:** Gmail, WhatsApp, LinkedIn, file drops
- **ReasoningLoop:** Classifies tasks by type, decides auto-execute vs. approval routing
- **HumanApprovalRequest:** Sensitive actions gate on human approval via `Pending_Approval/` folder
- **MCP Actions:** LinkedIn post publishing via MCP tool (`mcp_linkedin__create_post`)
- **CronScheduler:** Full schedule for all watchers and recurring tasks
- **AuditLogger:** JSON logs in `Logs/YYYY-MM-DD.json`
- **Orchestrator:** Watches `/Approved` folder and executes approved actions

### Watchers

| Watcher | File | Interval | Description |
|---------|------|----------|-------------|
| File Drop | `filesystem_watcher.py` | Continuous | Monitors `Inbox/` for new files |
| Gmail | `gmail_watcher.py` | 2 min | Checks for unread important emails |
| WhatsApp | `whatsapp_watcher.py` | 5 min | Scans for urgent messages |
| LinkedIn | `linkedin_watcher.py` | 15 min | Checks messages and connection requests |
| Orchestrator | `orchestrator.py` | 1 min | Executes approved actions |

### Silver Architecture

```
Inbox/ (file drop)  ─┐
Gmail Watcher        ├──→ Needs_Action/ ──→ ReasoningLoop ──→ Plan.md
WhatsApp Watcher     │                          │
LinkedIn Watcher ────┘                          ├──→ Auto-execute (email/whatsapp reply)
                                                │
                                                └──→ Pending_Approval/ ──→ [Human reviews]
                                                          │                      │
                                                          ▼                      ▼
                                                      Approved/             Rejected/
                                                          │
                                                          ▼
                                                    Orchestrator
                                                    (watches Approved)
                                                          │
                                                          ▼
                                                    MCP Action
                                                 (LinkedIn post, etc.)
                                                          │
                                                          ▼
                                                       Done/
```

### Folder Structure (Silver)

```
personal-ai-employee/
├── watchers/
│   ├── filesystem_watcher.py   ← File drop monitoring
│   ├── gmail_watcher.py        ← Gmail API integration
│   ├── whatsapp_watcher.py     ← WhatsApp Web automation
│   ├── linkedin_watcher.py     ← LinkedIn Web automation
│   └── orchestrator.py         ← Executes approved actions
├── Skills/
│   ├── BasicTaskProcessor.md
│   ├── MoveToDone.md
│   ├── ReadNeedsAction.md
│   ├── WritePlanOrSummary.md
│   ├── ReasoningLoop.md          ← Core AI brain
│   ├── HumanApprovalRequest.md   ← Approval gate
│   ├── LinkedInAutoPost.md       ← Auto-posting
│   ├── GmailWatcher.md           ← Skill doc
│   ├── WhatsAppWatcher.md        ← Skill doc
│   ├── LinkedInWatcher.md        ← Skill doc
│   ├── CronScheduler.md          ← Schedule mgmt
│   ├── EmailReply.md             ← Email replies
│   ├── AuditLogger.md            ← Audit trail
│   └── Orchestrator.md           ← NEW (optional skill doc)
├── .claude/
│   └── settings.json             ← MCP server config
├── Inbox/                        ← Drop zone for files
├── Needs_Action/                 ← Pending tasks
├── Pending_Approval/             ← Awaiting human approval
├── Approved/                     ← Approved actions (orchestrator watches)
├── Rejected/                     ← Rejected actions
├── Done/                         ← Completed tasks
├── Logs/                         ← JSON audit logs
├── Briefings/                    ← CEO briefings
├── requirements.txt              ← Python dependencies
├── setup_cron.sh                 ← Cron setup script
├── Company_Handbook.md
├── Dashboard.md
├── Plan.md
└── README.md
```

### How to Test (Silver) — Full Flow

#### Option A: Manual Testing

1. **Simulate inputs** — drop files into `Inbox/`:
   ```bash
   echo "Task: Draft Q1 LinkedIn post" > Inbox/my_task.txt
   ```

2. **Run watchers** (or let cron handle it):
   ```bash
   python watchers/filesystem_watcher.py
   ```

3. **Trigger ReasoningLoop:**
   ```
   Use ReasoningLoop to process all pending tasks in Needs_Action
   ```

4. **Review Plan.md** — Claude creates a full action plan with approval flags.

5. **Check Pending_Approval/** — review any sensitive actions (LinkedIn posts, bulk emails, payments).

6. **Approve:** Move file to `Approved/` → Orchestrator executes MCP action.
   **Reject:** Move file to `Rejected/` → Claude skips and logs.

7. **Verify Done/** — all processed files archived.

8. **Check Logs/** — audit trail in `Logs/YYYY-MM-DD.json`.

#### Option B: Test Individual Watchers

```bash
# Test Gmail watcher (requires credentials setup)
python watchers/gmail_watcher.py --once --verbose

# Test WhatsApp watcher (requires WhatsApp Web login)
python watchers/whatsapp_watcher.py --once --verbose

# Test LinkedIn watcher (requires LinkedIn login)
python watchers/linkedin_watcher.py --once --verbose

# Test orchestrator (processes approved files)
python watchers/orchestrator.py --once --verbose
```

#### Option C: Setup Automated Schedule

```bash
# Add cron jobs (Linux/Mac)
./setup_cron.sh

# View logs
tail -f Logs/cron_*.log

# Remove cron jobs
./setup_cron.sh --remove
```

### Schedule Setup (Silver)

Add to crontab (`crontab -e`):
```bash
*/2 * * * *     cd /mnt/d/personal-ai-employee && python watchers/gmail_watcher.py --once >> Logs/cron.log 2>&1
*/15 * * * *    cd /mnt/d/personal-ai-employee && python watchers/linkedin_watcher.py --once >> Logs/cron.log 2>&1
*/10 * * * *    cd /mnt/d/personal-ai-employee && claude --print "Use ReasoningLoop to process all pending tasks in Needs_Action" >> Logs/cron.log 2>&1
0 9 * * 1,3,5   cd /mnt/d/personal-ai-employee && claude --print "Use LinkedInAutoPost to draft today's LinkedIn post" >> Logs/cron.log 2>&1
0 * * * *       cd /mnt/d/personal-ai-employee && claude --print "Refresh Dashboard.md with latest stats" >> Logs/cron.log 2>&1
0 */6 * * *     cd /mnt/d/personal-ai-employee && claude --print "Use HumanApprovalRequest to expire pending approvals older than 24 hours" >> Logs/cron.log 2>&1
```

### MCP Integration

To enable real LinkedIn posting, add to `.claude/settings.json`:
```json
{
  "mcpServers": {
    "linkedin": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-linkedin"],
      "env": {
        "LINKEDIN_ACCESS_TOKEN": "<your_token>"
      }
    }
  }
}
```

Then Claude can call `mcp_linkedin__create_post` directly after approval.

### Silver Flow Test Results (2026-02-27)

| Step | Description | Result |
|------|-------------|--------|
| 1 | File/email/WhatsApp dropped in Inbox | ✅ Pass |
| 2 | Watchers detected and moved to Needs_Action | ✅ Pass |
| 3 | ReasoningLoop classified tasks, created Plan.md | ✅ Pass |
| 4 | Auto-executed email + WhatsApp replies | ✅ Pass |
| 5 | LinkedIn post routed to Pending_Approval | ✅ Pass |
| 6 | Human approval simulated (moved to Approved/) | ✅ Pass |
| 7 | MCP LinkedIn post action simulated | ✅ Pass |
| 8 | Schedule verified (CronScheduler) | ✅ Pass |
| 9 | Audit log written to Logs/2026-02-27.json | ✅ Pass |
| 10 | Dashboard.md updated | ✅ Pass |

**Silver Tier: COMPLETE ✅**

---

## Skills Reference

| Skill | Tier | Description |
|-------|------|-------------|
| BasicTaskProcessor | Bronze | Process any file_drop task |
| ReadNeedsAction | Bronze | List and read pending tasks |
| WritePlanOrSummary | Bronze | Write Plan.md or summaries |
| MoveToDone | Bronze | Archive processed files |
| ReasoningLoop | Silver | Core AI brain — classify and route all tasks |
| HumanApprovalRequest | Silver | Gate sensitive actions on human approval |
| LinkedInAutoPost | Silver | Draft and post LinkedIn content |
| GmailWatcher | Silver | Monitor Gmail for important emails |
| WhatsAppWatcher | Silver | Monitor WhatsApp for messages |
| LinkedInWatcher | Silver | Monitor LinkedIn messages/connections |
| EmailReply | Silver | Draft and send email replies |
| CronScheduler | Silver | Manage recurring scheduled tasks |
| AuditLogger | Silver | Log all actions to JSON audit trail |
| Orchestrator | Silver | Execute approved actions via MCP |

### Setup Checklist

- [ ] Install Python dependencies: `pip install -r requirements.txt`
- [ ] Install Playwright browsers: `playwright install`
- [ ] Setup Gmail credentials (download from Google Cloud Console)
- [ ] Configure MCP servers in `.claude/settings.json`
- [ ] Run `./setup_cron.sh` to enable automated scheduling
- [ ] Test each watcher individually with `--once --verbose` flags
