#!/bin/bash
# Gold Tier Verification Script
# Run this to check if all Gold Tier requirements are complete

echo "🔍 Gold Tier Verification"
echo "========================"
echo ""

PASS=0
WARN=0
FAIL=0

# Check function
check_item() {
    local name="$1"
    local condition="$2"
    
    if eval "$condition"; then
        echo -e "✅ $name"
        PASS=$((PASS + 1))
    else
        echo -e "❌ $name"
        FAIL=$((FAIL + 1))
    fi
}

warn_item() {
    local name="$1"
    local condition="$2"
    
    if eval "$condition"; then
        echo -e "✅ $name"
        PASS=$((PASS + 1))
    else
        echo -e "⚠️  $name"
        WARN=$((WARN + 1))
    fi
}

# Core Requirements
echo "📋 Core Requirements"
echo "-------------------"
check_item "Silver Tier Complete" "[ -f '/mnt/d/personal-ai-employee/SILVER_TIER_COMPLETE.md' ]"
check_item "Gold Tier Documentation" "[ -f '/mnt/d/personal-ai-employee/GOLD_TIER_COMPLETE.md' ]"
check_item "Completion Plan Created" "[ -f '/mnt/d/personal-ai-employee/GOLD_TIER_COMPLETION_PLAN.md' ]"
echo ""

# Watchers
echo "👁️  Watcher Scripts"
echo "-------------------"
check_item "Gmail Watcher" "[ -f '/mnt/d/personal-ai-employee/watchers/gmail_watcher.py' ]"
check_item "WhatsApp Watcher" "[ -f '/mnt/d/personal-ai-employee/watchers/whatsapp_watcher.py' ]"
check_item "LinkedIn Watcher" "[ -f '/mnt/d/personal-ai-employee/watchers/linkedin_watcher.py' ]"
check_item "Facebook Watcher" "[ -f '/mnt/d/personal-ai-employee/watchers/facebook_watcher.py' ]"
check_item "Instagram Watcher" "[ -f '/mnt/d/personal-ai-employee/watchers/instagram_watcher.py' ]"
check_item "Twitter Watcher" "[ -f '/mnt/d/personal-ai-employee/watchers/twitter_watcher.py' ]"
echo ""

# Posters
echo "📱 Social Media Posters"
echo "-----------------------"
check_item "LinkedIn Poster" "[ -f '/mnt/d/personal-ai-employee/watchers/linkedin_poster.py' ]"
check_item "Facebook Poster" "[ -f '/mnt/d/personal-ai-employee/watchers/facebook_poster.py' ]"
check_item "Instagram Poster" "[ -f '/mnt/d/personal-ai-employee/watchers/instagram_poster.py' ]"
check_item "Twitter Poster" "[ -f '/mnt/d/personal-ai-employee/watchers/twitter_poster.py' ]"
echo ""

# MCP Servers
echo "🔌 MCP Servers"
echo "--------------"
check_item "Email MCP Server" "[ -f '/mnt/d/personal-ai-employee/watchers/email_mcp_server.py' ]"
check_item "Browser MCP Server" "[ -f '/mnt/d/personal-ai-employee/watchers/browser_mcp_server.py' ]"
check_item "Calendar MCP Server" "[ -f '/mnt/d/personal-ai-employee/watchers/calendar_mcp_server.py' ]"
check_item "Odoo MCP Server" "[ -f '/mnt/d/personal-ai-employee/odoo/odoo_accounting.py' ]"
echo ""

# Gold Tier Features
echo "🏆 Gold Tier Features"
echo "---------------------"
check_item "CEO Briefing Generator" "[ -f '/mnt/d/personal-ai-employee/watchers/ceo_briefing_generator.py' ]"
warn_item "Odoo Config" "[ -f '/mnt/d/personal-ai-employee/odoo/odoo_config.json' ]"
warn_item "Twitter Config" "[ -f '/mnt/d/personal-ai-employee/twitter_config.json' ]"
echo ""

# Ralph Wiggum
echo "🔄 Ralph Wiggum Loop"
echo "--------------------"
check_item "Ralph Wiggum Plugin" "[ -f '/mnt/d/personal-ai-employee/.claude/plugins/ralph-wiggum' ]"
check_item "Ralph Wiggum Executable" "[ -x '/mnt/d/personal-ai-employee/.claude/plugins/ralph-wiggum' ]"
echo ""

# Documentation
echo "📚 Skill Documentation"
echo "----------------------"
SKILL_COUNT=$(ls -1 /mnt/d/personal-ai-employee/Skills/*.md 2>/dev/null | wc -l)
if [ "$SKILL_COUNT" -ge 20 ]; then
    echo -e "✅ Skill Docs: $SKILL_COUNT files (target: 20+)"
    PASS=$((PASS + 1))
else
    echo -e "⚠️  Skill Docs: $SKILL_COUNT files (target: 20+)"
    WARN=$((WARN + 1))
fi

# Check specific Gold tier skills
echo ""
echo "🎯 Gold Tier Skills"
echo "-------------------"
check_item "CEOBriefingGenerator" "[ -f '/mnt/d/personal-ai-employee/Skills/CEOBriefingGenerator.md' ]"
check_item "RalphWiggumLoop" "[ -f '/mnt/d/personal-ai-employee/Skills/RalphWiggumLoop.md' ]"
check_item "FacebookAutoPost" "[ -f '/mnt/d/personal-ai-employee/Skills/FacebookAutoPost.md' ]"
check_item "InstagramAutoPost" "[ -f '/mnt/d/personal-ai-employee/Skills/InstagramAutoPost.md' ]"
check_item "OdooAccounting" "[ -f '/mnt/d/personal-ai-employee/odoo/OdooAccounting.md' ]"
check_item "WeeklyBusinessAudit" "[ -f '/mnt/d/personal-ai-employee/Skills/WeeklyBusinessAudit.md' ]"
check_item "ErrorHandlingAndAuditLogging" "[ -f '/mnt/d/personal-ai-employee/Skills/ErrorHandlingAndAuditLogging.md' ]"
check_item "MCPServersIntegration" "[ -f '/mnt/d/personal-ai-employee/Skills/MCPServersIntegration.md' ]"
echo ""

# Generated Output
echo "📄 Generated Output"
echo "-------------------"
check_item "CEO Briefing Generated" "ls /mnt/d/personal-ai-employee/Briefings/CEO_Briefing_*.md 1>/dev/null 2>&1"
check_item "Audit Logs" "[ -f '/mnt/d/personal-ai-employee/Logs/2026-02-27.json' ] || [ -f '/mnt/d/personal-ai-employee/Logs/2026-03-*.json' ]"
echo ""

# Dashboard
echo "📊 Dashboard Status"
echo "-------------------"
warn_item "Dashboard Updated to Gold" "grep -q 'Tier:.*GOLD' /mnt/d/personal-ai-employee/Dashboard.md"
echo ""

# Configuration
echo "⚙️  Configuration Files"
echo "----------------------"
check_item "Gmail Credentials" "[ -f '/mnt/d/personal-ai-employee/gmail_credentials.json' ]"
check_item "Token File" "[ -f '/mnt/d/personal-ai-employee/token.json' ]"
check_item "MCP Settings" "[ -f '/mnt/d/personal-ai-employee/.claude/settings.json' ]"
check_item "Requirements.txt" "[ -f '/mnt/d/personal-ai-employee/requirements.txt' ]"
echo ""

# Summary
echo "════════════════════════════════════"
echo "📊 VERIFICATION SUMMARY"
echo "════════════════════════════════════"
echo -e "✅ Passed: $PASS"
echo -e "⚠️  Warnings: $WARN"
echo -e "❌ Failed: $FAIL"
echo ""

TOTAL=$((PASS + WARN + FAIL))
if [ $TOTAL -gt 0 ]; then
    PERCENTAGE=$((PASS * 100 / TOTAL))
    echo "Completion: $PERCENTAGE%"
    echo ""
    
    if [ $FAIL -eq 0 ] && [ $WARN -le 2 ]; then
        echo -e "🎉 ${GREEN}GOLD TIER READY!${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Configure Odoo (see odoo_config.json)"
        echo "2. Update Dashboard.md to show Gold tier"
        echo "3. Test Ralph Wiggum loop"
        echo "4. Record demo video"
    elif [ $FAIL -gt 0 ]; then
        echo -e "🔧 ${YELLOW}INCOMPLETE${NC}"
        echo ""
        echo "Fix the failed items above to complete Gold Tier"
    fi
fi

echo ""
echo "════════════════════════════════════"
