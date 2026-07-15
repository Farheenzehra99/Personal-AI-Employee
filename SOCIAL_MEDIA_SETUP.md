# Social Media Automation - Complete Setup Guide

## 📋 Overview

This guide covers complete automation setup for:
- ✅ LinkedIn (Working)
- ✅ WhatsApp (Working)
- ✅ Facebook (New)
- ✅ Instagram (New)

---

## 🚀 Quick Start

### **Step 1: Install Dependencies**
```bash
cd /mnt/d/personal-ai-employee
source venv/bin/activate
pip install playwright
playwright install chromium
```

---

## 🔐 Step 2: Login to Each Platform

### **LinkedIn Login**
```bash
# Account 1 (Default)
python watchers/linkedin_login.py --session-path .linkedin_session --timeout 300

# Account 2 (if needed)
python watchers/linkedin_login.py --session-path .linkedin_session_account2 --timeout 300
```

### **WhatsApp Login**
```bash
python watchers/whatsapp_login.py
```
**Scan QR code** with WhatsApp mobile app.

### **Facebook Login**
```bash
python watchers/facebook_login.py --session-path .facebook_session --timeout 300
```

### **Instagram Login**
```bash
python watchers/instagram_login.py --session-path .instagram_session --timeout 300
```

---

## 📡 Step 3: Monitoring (Watchers)

### **LinkedIn Watcher**
```bash
python watchers/linkedin_watcher.py --once --verbose
```
- Checks messages & connection requests
- Creates files in `Needs_Action/`

### **WhatsApp Watcher**
```bash
python watchers/whatsapp_watcher.py --once --verbose
```
- Monitors urgent messages
- Flags financial content

### **Facebook Watcher**
```bash
python watchers/facebook_watcher.py --once --verbose
```
- Checks Messenger & notifications
- Creates action files

### **Instagram Watcher**
```bash
python watchers/instagram_watcher.py --once --verbose
```
- Monitors DMs & notifications
- Detects collaboration requests

---

## 📤 Step 4: Posting

### **LinkedIn Post**
```bash
# With image
python watchers/linkedin_post_with_image.py --content post_content.txt --image linkedin_images/ai_agents.png

# Without image
python watchers/linkedin_poster.py --content "Your post here" --verbose

# Process approved queue
python watchers/linkedin_poster.py --process-queue --verbose
```

### **Facebook Post**
```bash
# Create post (creates approval file)
python watchers/facebook_poster.py --content "Your post here" --image photo.jpg --verbose

# Approve
mv Pending_Approval/FACEBOOK_POST_*.md Approved/

# Publish
python watchers/facebook_poster.py --process-queue --verbose
```

### **Instagram Post**
```bash
# Create post (requires image)
python watchers/instagram_poster.py --caption "Your caption #here" --image photo.jpg --verbose

# Approve
mv Pending_Approval/INSTAGRAM_POST_*.md Approved/

# Publish
python watchers/instagram_poster.py --process-queue --verbose
```

---

##  File Structure

```
/mnt/d/personal-ai-employee/
├── watchers/
│   ├── linkedin_watcher.py      # LinkedIn messages
│   ├── linkedin_poster.py       # LinkedIn posts
│   ├── linkedin_login.py        # LinkedIn login
│   ├── whatsapp_watcher.py      # WhatsApp messages
│   ├── whatsapp_sender.py       # WhatsApp replies
│   ├── whatsapp_login.py        # WhatsApp login
│   ├── facebook_watcher.py      # Facebook messages
│   ├── facebook_poster.py       # Facebook posts
│   ├── facebook_login.py        # Facebook login
│   ├── instagram_watcher.py     # Instagram DMs
│   ├── instagram_poster.py      # Instagram posts
│   ├── instagram_login.py       # Instagram login
│   └── linkedin_post_with_image.py  # LinkedIn with images
├── linkedin_images/             # Generated AI images
│   ├── ai_robot.png
│   ├── ai_agents.png
│   └── automation.png
├── .linkedin_session/           # LinkedIn session data
├── .whatsapp_session/           # WhatsApp session data
├── .facebook_session/           # Facebook session data
├── .instagram_session/          # Instagram session data
├── Needs_Action/                # Pending items
├── Pending_Approval/            # Awaiting approval
├── Approved/                    # Approved for posting
└── Done/                        # Completed items
```

---

## 🔄 Automation Workflow

```
┌─────────────────────────────────────────────────────────┐
│                    WATCHERS (Monitor)                    │
├─────────────┬─────────────┬──────────────┬──────────────┤
│  LinkedIn   │  WhatsApp   │   Facebook   │  Instagram   │
│  Messages   │  Messages   │   Messages   │     DMs      │
└──────┬──────┴──────┬──────┴───────┬────────────┬───────┘
       │             │              │             │
       ▼             ▼              ▼             ▼
┌─────────────────────────────────────────────────────────┐
│           Needs_Action/ Folder (Action Files)            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Claude Code (Reasoning Loop)                │
│         - Reads pending items                           │
│         - Drafts responses                              │
│         - Creates approval files                        │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│          Pending_Approval/ (Human Review)                │
└─────────────────────────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
        [Approved]                 [Rejected]
              │                         │
              ▼                         │
┌─────────────────────┐                 │
│   POSTERS (Auto)    │                 │
│ - LinkedIn Poster   │                 │
│ - Facebook Poster   │                 │
│ - Instagram Poster  │                 │
│ - WhatsApp Sender   │                 │
└──────────┬──────────┘                 │
           │                            │
           ▼                            ▼
      [Done/]                     [Deleted]
```

---

## ⏰ Cron Setup (Optional)

For 24/7 automation with visible browsers, you need Xvfb:

```bash
# Install Xvfb
sudo apt-get install xvfb

# Create cron wrapper script
cat > /mnt/d/personal-ai-employee/run_with_xvfb.sh << 'EOF'
#!/bin/bash
export DISPLAY=:99
Xvfb :99 -screen 0 1280x720x24 &
XVFB_PID=$!
sleep 2
$@
kill $XVFB_PID
EOF
chmod +x /mnt/d/personal-ai-employee/run_with_xvfb.sh
```

**Example Cron Jobs:**
```bash
# LinkedIn check every 15 minutes
*/15 * * * * cd /mnt/d/personal-ai-employee && source venv/bin/activate && ./run_with_xvfb.sh python watchers/linkedin_watcher.py --once

# Facebook check every 10 minutes
*/10 * * * * cd /mnt/d/personal-ai-employee && source venv/bin/activate && ./run_with_xvfb.sh python watchers/facebook_watcher.py --once

# Instagram check every 10 minutes
*/10 * * * * cd /mnt/d/personal-ai-employee && source venv/bin/activate && ./run_with_xvfb.sh python watchers/instagram_watcher.py --once

# WhatsApp check every 5 minutes
*/5 * * * * cd /mnt/d/personal-ai-employee && source venv/bin/activate && ./run_with_xvfb.sh python watchers/whatsapp_watcher.py --once
```

---

## 📊 Platform Comparison

| Platform | Watcher | Auto-Post | Images | Login Method |
|----------|---------|-----------|--------|--------------|
| LinkedIn | ✅ | ✅ | ✅ | Browser Session |
| WhatsApp | ✅ | ✅ | ❌ | QR Code |
| Facebook | ✅ | ✅ | ✅ | Browser Session |
| Instagram | ✅ | ✅ | ✅ (Required) | Browser Session |

---

## 🎯 Quick Commands Reference

### **All-in-One Check (Manual)**
```bash
source venv/bin/activate

# Check all platforms
python watchers/linkedin_watcher.py --once --verbose
python watchers/whatsapp_watcher.py --once --verbose
python watchers/facebook_watcher.py --once --verbose
python watchers/instagram_watcher.py --once --verbose
```

### **Post to All Platforms**
```bash
# LinkedIn
python watchers/linkedin_post_with_image.py --content post.txt --image ai_agents.png

# Facebook
python watchers/facebook_poster.py --content post.txt --image photo.jpg

# Instagram
python watchers/instagram_poster.py --caption "Caption #here" --image photo.jpg
```

### **Process All Approved**
```bash
# Move all approvals
mv Pending_Approval/*.md Approved/

# Post everywhere
python watchers/linkedin_poster.py --process-queue
python watchers/facebook_poster.py --process-queue
python watchers/instagram_poster.py --process-queue
```

---

## 🔧 Troubleshooting

### **Browser closes immediately**
- Ensure `headless=False` in watcher scripts
- Check if session folder exists and has data

### **Login not detected**
- Wait for full page load (feed/home page)
- Check URL doesn't contain 'login' or 'checkpoint'

### **Image upload fails**
- Verify image path is absolute
- Check file exists and is readable
- LinkedIn: Click media button manually if needed

### **Session expires**
- Re-run login helper script
- Delete old session folder and re-login

---

## 📝 Notes

1. **Human-in-the-Loop:** All posts require manual approval before publishing
2. **Manual Final Click:** Due to platform security, final "Post" button requires manual click
3. **Session Persistence:** Sessions are saved and reused until logout
4. **Rate Limits:** Don't post too frequently (wait 5-10 min between posts)

---

## 🎉 Success Indicators

| Platform | Success Looks Like |
|----------|-------------------|
| LinkedIn | "Posted 1 LinkedIn update(s)" + screenshot saved |
| WhatsApp | "Message sent!" + screenshot saved |
| Facebook | "✓ Post submitted!" + screenshot saved |
| Instagram | "✓ Post submitted!" + screenshot saved |

---

**Happy Automating! 🚀**
