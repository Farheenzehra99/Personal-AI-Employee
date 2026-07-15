# 🚀 AI Employee - Step by Step Setup & Testing Guide

**Date:** March 6, 2026  
**Status:** Ready for Manual Testing

---

## 📋 Quick Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    SETUP FLOW                               │
├─────────────────────────────────────────────────────────────┤
│  Step 1: Install Python Dependencies (5 min)                │
│  Step 2: Install Playwright Browsers (3 min)                │
│  Step 3: Setup Gmail Credentials (10 min)                   │
│  Step 4: Test Bronze Tier (5 min)                           │
│  Step 5: Test Silver Tier (10 min)                          │
│  Step 6: Setup Cron Jobs (Optional, 5 min)                  │
└─────────────────────────────────────────────────────────────┘
                    Total Time: ~40 minutes
```

---

## 📦 STEP 1: Install Python Dependencies

### Option A: Using Virtual Environment (Recommended)

```bash
# Navigate to project directory
cd /mnt/d/personal-ai-employee

# Activate virtual environment (already created)
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### Option B: System-wide (Not Recommended)

```bash
pip install -r requirements.txt --break-system-packages
```

### Expected Output
```
Successfully installed watchdog-4.x.x google-api-python-client-2.x.x ...
```

---

## 🌐 STEP 2: Install Playwright Browsers

Playwright is needed for WhatsApp and LinkedIn watchers.

```bash
# Install Chromium browser for Playwright
./venv/bin/playwright install chromium

# (Optional) Install system dependencies if prompted
./venv/bin/playwright install-deps chromium
```

### Expected Output
```
Downloading Chromium 121.0...
Chromium 121.0 downloaded successfully
```

---

## 📧 STEP 3: Setup Gmail Credentials (Optional)

Skip this step if you don't want Gmail integration.

### 3.1: Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Create new project (e.g., "AI Employee")
3. Enable **Gmail API**
4. Go to **Credentials** → **Create Credentials** → **OAuth Client ID**
5. Application type: **Desktop App**
6. Download the JSON file
7. Save as: `/mnt/d/personal-ai-employee/gmail_credentials.json`

### 3.2: First-Time Authentication

```bash
# Run Gmail watcher (will open browser for authentication)
./venv/bin/python watchers/gmail_watcher.py --once --verbose
```

This will:
- Open a browser window
- Ask you to login with Google account
- Save token to `token.json`

---

## 🥉 STEP 4: Test Bronze Tier

### 4.1: Create Test File

```bash
# Create a test task file
echo "Please summarize this document and create 3 action items" > Inbox/test_bronze_001.txt
```

### 4.2: Run Filesystem Watcher

```bash
# Run watcher to detect the file
./venv/bin/python watchers/filesystem_watcher.py --once --verbose
```

### Expected Output
```
Watcher started... Monitoring /mnt/d/personal-ai-employee/Inbox
New file detected: /mnt/d/personal-ai-employee/Inbox/test_bronze_001.txt
Watcher completed single check
```

### 4.3: Verify File Moved

```bash
# Check if file was copied to Needs_Action
ls -la Needs_Action/
```

You should see: `FILE_test_bronze_001.md`

### 4.4: Process with Claude Code

```bash
# Run Claude Code to process the task
claude --print "Use BasicTaskProcessor to process FILE_test_bronze_001.md in Needs_Action folder"
```

### 4.5: Verify Results

```bash
# Check if Plan.md was created
cat Plan.md

# Check if Dashboard.md was updated
cat Dashboard.md

# Check if file moved to Done
ls -la Done/
```

---

## 🥈 STEP 5: Test Silver Tier

### 5.1: Test All Watchers Individually

```bash
# Test Gmail Watcher
./venv/bin/python watchers/gmail_watcher.py --once --verbose

# Test WhatsApp Watcher (requires WhatsApp Web login)
./venv/bin/python watchers/whatsapp_watcher.py --once --verbose

# Test LinkedIn Watcher (requires LinkedIn login)
./venv/bin/python watchers/linkedin_watcher.py --once --verbose

# Test Orchestrator (processes approved files)
./venv/bin/python watchers/orchestrator.py --once --verbose
```

### Expected Outputs

**Gmail Watcher:**
```
Gmail check complete. Found 0 new emails.
```

**WhatsApp Watcher:**
```
WhatsApp check complete. Found 0 urgent messages.
```

**LinkedIn Watcher:**
```
LinkedIn check complete. Found 0 new items.
```

**Orchestrator:**
```
Orchestrator complete. Processed 0 approved file(s).
```

### 5.2: Test Full Silver Flow

#### Create Multiple Test Files

```bash
# Create email simulation
cat > Inbox/email_test.md << 'EOF'
---
type: email
from: client@example.com
subject: Meeting Request
---

Hi, can we schedule a meeting next week?
EOF

# Create file drop task
echo "Draft a LinkedIn post about Q1 goals" > Inbox/linkedin_task.txt

# Create WhatsApp simulation
cat > Inbox/whatsapp_test.md << 'EOF'
---
type: whatsapp
from: Ali Khan
---

Hey, did you receive my invoice?
EOF
```

#### Run All Watchers

```bash
# Run filesystem watcher
./venv/bin/python watchers/filesystem_watcher.py --once

# Run reasoning loop (via Claude)
claude --print "Use ReasoningLoop to process all pending tasks in Needs_Action"
```

#### Check Results

```bash
# View created plan
cat Plan.md

# Check pending approvals
ls -la Pending_Approval/

# View approval file content
cat Pending_Approval/*.md
```

### 5.3: Test Approval Workflow

```bash
# 1. Check what needs approval
ls -la Pending_Approval/

# 2. Review the file
cat Pending_Approval/LINKEDIN_POST_*.md

# 3. Approve by moving to Approved folder
mv Pending_Approval/LINKEDIN_POST_*.md Approved/

# 4. Run orchestrator to execute
./venv/bin/python watchers/orchestrator.py --once --verbose

# 5. Check if moved to Done
ls -la Done/
```

---

## ⏰ STEP 6: Setup Cron Jobs (Optional)

### 6.1: Verify Cron is Available

```bash
# Check if crontab is available
which crontab

# If not found, install cron
sudo apt-get install cron  # Ubuntu/Debian
```

### 6.2: Setup Automated Schedule

```bash
# Run the setup script
./setup_cron.sh
```

### Expected Output
```
Setting up AI Employee cron entries...
✓ Cron entries added successfully!

Scheduled tasks:
  • Gmail watcher: Every 2 minutes
  • WhatsApp watcher: Every 5 minutes
  • LinkedIn watcher: Every 15 minutes
  • Reasoning loop: Every 10 minutes
  • LinkedIn posts: Mon/Wed/Fri at 9 AM
  • Dashboard refresh: Every hour
  • Approval expiry: Every 6 hours
  • Orchestrator: Every minute
```

### 6.3: Verify Cron Jobs

```bash
# View current crontab
crontab -l

# View logs
tail -f Logs/cron_*.log
```

### 6.4: Remove Cron Jobs (If Needed)

```bash
./setup_cron.sh --remove
```

---

## 🔧 Troubleshooting

### Issue: ModuleNotFoundError

```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Watcher not detecting files

```bash
# Check if Inbox folder exists
ls -la Inbox/

# Create Inbox if missing
mkdir -p Inbox

# Run watcher with verbose mode
./venv/bin/python watchers/filesystem_watcher.py --once --verbose
```

### Issue: Gmail authentication fails

```bash
# Delete old token
rm -f token.json

# Re-run authentication
./venv/bin/python watchers/gmail_watcher.py --once --verbose
```

### Issue: Playwright browser errors

```bash
# Reinstall Chromium
./venv/bin/playwright install chromium --force

# Install system dependencies
./venv/bin/playwright install-deps chromium
```

### Issue: Claude Code not found

```bash
# Check if Claude Code is installed
claude --version

# If not installed, install via npm
npm install -g @anthropic/claude-code
```

---

## 📊 Quick Reference Commands

### Watchers

```bash
# File Drop Watcher
./venv/bin/python watchers/filesystem_watcher.py --once

# Gmail Watcher
./venv/bin/python watchers/gmail_watcher.py --once

# WhatsApp Watcher
./venv/bin/python watchers/whatsapp_watcher.py --once

# LinkedIn Watcher
./venv/bin/python watchers/linkedin_watcher.py --once

# Orchestrator
./venv/bin/python watchers/orchestrator.py --once
```

### Claude Commands

```bash
# Process pending tasks
claude --print "Use ReasoningLoop to process all pending tasks in Needs_Action"

# Draft LinkedIn post
claude --print "Use LinkedInAutoPost to draft today's LinkedIn post"

# Refresh Dashboard
claude --print "Refresh Dashboard.md with latest stats"

# Check approval expiry
claude --print "Use HumanApprovalRequest to expire pending approvals older than 24 hours"
```

### Utility Commands

```bash
# View folder contents
ls -la Inbox/ Needs_Action/ Done/ Approved/ Pending_Approval/

# View logs
tail -f Logs/cron_*.log

# View today's audit log
cat Logs/$(date +%Y-%m-%d).json

# Check virtual environment
which python
```

---

## ✅ Testing Checklist

```
┌─────────────────────────────────────────────────────────────┐
│  TESTING CHECKLIST                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SETUP                                                      │
│  ☐ Python dependencies installed                            │
│  ☐ Playwright browsers installed                            │
│  ☐ Gmail credentials configured (optional)                  │
│  ☐ Virtual environment activated                            │
│                                                             │
│  BRONZE TIER                                                │
│  ☐ Test file created in Inbox/                              │
│  ☐ Filesystem watcher detects file                          │
│  ☐ File copied to Needs_Action/                             │
│  ☐ Claude processes task                                    │
│  ☐ Plan.md created/updated                                  │
│  ☐ File moved to Done/                                      │
│                                                             │
│  SILVER TIER                                                  │
│  ☐ Gmail watcher runs successfully                          │
│  ☐ WhatsApp watcher runs successfully                       │
│  ☐ LinkedIn watcher runs successfully                       │
│  ☐ ReasoningLoop creates Plan.md                            │
│  ☐ Approval file created in Pending_Approval/               │
│  ☐ Approval moved to Approved/                              │
│  ☐ Orchestrator executes action                             │
│  ☐ File moved to Done/                                      │
│  ☐ Audit log written to Logs/                               │
│                                                             │
│  CRON (OPTIONAL)                                            │
│  ☐ Cron jobs added via setup_cron.sh                        │
│  ☐ Cron jobs verified with crontab -l                       │
│  ☐ Logs being written to Logs/cron_*.log                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Next Steps After Testing

1. **Add Real API Tokens**
   - LinkedIn API token in `.claude/settings.json`
   - Gmail credentials from Google Cloud

2. **Configure MCP Servers**
   - Enable LinkedIn MCP for real posting
   - Enable Email MCP for sending

3. **Setup Production Schedule**
   - Run `./setup_cron.sh` for automation

4. **Start Using Daily**
   - Drop files in `Inbox/` for processing
   - Check `Pending_Approval/` for items needing review
   - Review `Dashboard.md` for status

---

**Guide Created:** March 6, 2026  
**Estimated Setup Time:** 40 minutes  
**Skill Level:** Beginner-friendly
