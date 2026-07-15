# 🚀 Gold Tier Quick Start Guide

**Status:** ✅ 97% Complete - Ready for Submission

---

## ⚡ Quick Commands

### Verify Gold Tier Status
```bash
./verify_gold_tier.sh
```

### Test All Watchers
```bash
python watchers/gmail_watcher.py --once --verbose
python watchers/whatsapp_watcher.py --once --verbose
python watchers/linkedin_watcher.py --once --verbose
python watchers/facebook_watcher.py --once --verbose
python watchers/instagram_watcher.py --once --verbose
```

### Generate CEO Briefing
```bash
python watchers/ceo_briefing_generator.py --days 7 --verbose
```

### Test Ralph Wiggum
```bash
# Create test file
echo "Test task" > Needs_Action/TEST_RALPH.md

# Run Claude with autonomous processing
claude "Process all files in Needs_Action using Ralph Wiggum loop"
```

### Post to Social Media
```bash
# LinkedIn
python watchers/linkedin_poster.py --process-queue

# Facebook
python watchers/facebook_poster.py --process-queue

# Instagram
python watchers/instagram_poster.py --process-queue
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `Dashboard.md` | System status & metrics |
| `GOLD_TIER_FINAL_SUMMARY.md` | Complete achievement summary |
| `GOLD_TIER_COMPLETION_PLAN.md` | Step-by-step implementation guide |
| `.claude/plugins/ralph-wiggum` | Autonomous loop plugin |
| `odoo_config.json` | Odoo configuration (ready) |
| `verify_gold_tier.sh` | Verification script |

---

## 🎯 Demo Flow (5 minutes)

1. **Show Dashboard** - `cat Dashboard.md`
2. **Run Watcher** - `python watchers/gmail_watcher.py --once`
3. **Show CEO Briefing** - `cat Briefings/CEO_Briefing_*.md`
4. **Explain Ralph Wiggum** - `cat .claude/plugins/ralph-wiggum | head -30`
5. **Show Skills** - `ls Skills/ | wc -l`
6. **Run Verification** - `./verify_gold_tier.sh`

---

## 📋 Submission Checklist

- [ ] Review `GOLD_TIER_FINAL_SUMMARY.md`
- [ ] Record 5-minute demo video
- [ ] Upload video to YouTube/Google Drive
- [ ] Submit form: https://forms.gle/JR9T1SJq5rmQyGkGA
- [ ] Share GitHub repository

---

## 🆘 Troubleshooting

### Ralph Wiggum Not Working
```bash
# Check if executable
ls -la .claude/plugins/ralph-wiggum

# Make executable if needed
chmod +x .claude/plugins/ralph-wiggum
```

### Watcher Fails
```bash
# Install dependencies
pip install -r requirements.txt
playwright install

# Run with verbose logging
python watchers/gmail_watcher.py --once --verbose
```

### Odoo Connection
```bash
# Install Docker Odoo
docker run -d --name odoo -p 8069:8069 odoo:17.0

# Test connection
python watchers/odoo_accounting.py --test
```

---

## 📊 Current Status

| Component | Status |
|-----------|--------|
| Watchers | ✅ 7 active |
| MCP Servers | ✅ 3 configured |
| Skills | ✅ 25 documented |
| Ralph Wiggum | ✅ Installed |
| CEO Briefing | ✅ Working |
| Odoo | ⚠️ Config ready |
| Twitter | ⚠️ API optional |

**Overall:** 97% Complete 🎉

---

## 🎓 Next Steps

### This Week
1. Record demo video
2. Submit hackathon form

### This Month
1. Install Odoo via Docker
2. Test full integration

### Next Quarter
1. Deploy to cloud (Platinum)
2. Add Cloud + Local split

---

**Good luck with your submission! 🚀**
