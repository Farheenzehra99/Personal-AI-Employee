# AI Employee - Agent Skills (Gold Tier)

This folder contains all Claude Code Agent Skills for the AI Employee system.

## Skills Overview

### Bronze Tier Skills
- `BasicTaskProcessor.md` - Process simple tasks
- `FileOrganizer.md` - Organize files in vault

### Silver Tier Skills
- `EmailResponder.md` - Handle email responses
- `LinkedInAutoPost.md` - Auto-post to LinkedIn
- `WhatsAppResponder.md` - Handle WhatsApp messages
- `HumanApprovalRequest.md` - Manage approval workflow

### Gold Tier Skills (NEW)
- `TwitterAutoPost.md` - Auto-post to Twitter/X
- `FacebookAutoPost.md` - Auto-post to Facebook
- `InstagramAutoPost.md` - Auto-post to Instagram
- `CEOBriefingGenerator.md` - Generate weekly CEO briefings
- `RalphWiggumLoop.md` - Multi-step task completion
- `SocialMediaSummary.md` - Generate social media reports
- `SubscriptionAuditor.md` - Audit subscriptions
- `WeeklyBusinessAudit.md` - Weekly business review

### Platinum Tier Skills (Future)
- `CloudSync.md` - Sync with cloud agent
- `OdooAccounting.md` - Accounting integration
- `MultiAgentCoordination.md` - Coordinate multiple agents

## How to Use

1. Open Claude Code
2. Reference the skill: "Use [SkillName] to..."
3. Claude will follow the skill instructions

## Example Usage

```bash
# Generate CEO Briefing
claude "Use CEOBriefingGenerator to create this week's business audit"

# Post to social media
claude "Use LinkedInAutoPost to draft and post about our latest achievement"

# Review pending approvals
claude "Use HumanApprovalRequest to process all pending approvals"
```
