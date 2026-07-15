# Skill: CEOBriefingGenerator

## Purpose
Generate comprehensive weekly business audits and Monday Morning CEO Briefings automatically.

## When to Use
- Every Monday morning (scheduled)
- On-demand business reviews
- Weekly team meetings
- Investor updates
- Personal productivity review

## Capabilities
- Analyze completed tasks from past week
- Review pending tasks and bottlenecks
- Track social media activity
- Monitor subscription costs
- Identify business bottlenecks
- Generate actionable insights
- Create executive summaries

## Usage

### Weekly Briefing
```
Use CEOBriefingGenerator to create this week's CEO Briefing
```

### Custom Period
```
Use CEOBriefingGenerator to analyze the last 14 days of business activity
```

### Specific Focus
```
Use CEOBriefingGenerator to review social media performance and pending approvals
```

## Workflow

1. **Data Collection**
   - Scan `Done/` folder for completed tasks
   - Scan `Needs_Action/` for pending items
   - Scan `Pending_Approval/` for awaiting approval
   - Count social media posts by platform

2. **Analysis**
   - Calculate completion rate
   - Identify bottlenecks
   - Track metrics vs targets
   - Analyze subscription costs

3. **Report Generation**
   - Create `Briefings/CEO_Briefing_YYYY-MM-DD.md`
   - Include executive summary
   - List completed tasks
   - Highlight pending items
   - Provide proactive suggestions

4. **Distribution**
   - Save to Briefings folder
   - Optionally email to stakeholders
   - Add to Monday meeting agenda

## Briefing Sections

### Executive Summary
- Overall productivity assessment
- Key achievements
- Major concerns

### Revenue Tracking
- Monthly goal progress
- Current MTD revenue
- Pipeline overview

### Completed Tasks
- Total count
- List of major completions
- Time to completion metrics

### Pending Tasks
- Total pending count
- Awaiting approval count
- Priority items

### Social Media Activity
- Posts per platform
- Total posts vs target
- Engagement metrics (future)

### Subscription Audit
- Monthly costs
- Unused services
- Recommendations

### Bottlenecks
- Identified issues
- Root causes
- Suggested fixes

### Action Items
- Priority tasks for the week
- Decisions needed
- Meetings to schedule

## Metrics Tracked

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Tasks Completed/Week | 10+ | <5 |
| Social Posts/Week | 5+ | <3 |
| Pending Tasks | <5 | >10 |
| Approval Turnaround | <24 hours | >48 hours |
| Response Time | <24 hours | >48 hours |

## Example Output

```markdown
# 📊 Monday Morning CEO Briefing

**Period:** 2026-03-05 to 2026-03-12

## Executive Summary
Good progress. 10 tasks completed this week.

## Completed Tasks (10)
- [x] LinkedIn posts: 10
- [x] Email responses: 5
- [x] WhatsApp replies: 3

## Pending Tasks (8)
- [ ] 7 emails need response
- [ ] 1 approval awaiting review

## Social Media
| Platform | Posts | Target |
|----------|-------|--------|
| LinkedIn | 10 | 5 ✅ |
| Facebook | 0 | 5 ❌ |

## Bottlenecks
- 8 pending tasks need attention

## Action Items
- [ ] Review pending approvals
- [ ] Respond to urgent emails
- [ ] Schedule Facebook posts
```

## Scheduling

### Cron (Every Monday 8 AM)
```bash
0 8 * * 1 cd /mnt/d/personal-ai-employee && \
  python watchers/ceo_briefing_generator.py --days 7
```

### Manual
```bash
python watchers/ceo_briefing_generator.py --days 7 --verbose
```

## Files
- Script: `watchers/ceo_briefing_generator.py`
- Goals: `Business_Goals.md`
- Output: `Briefings/CEO_Briefing_*.md`

## Integration

### With Email
- Email briefing to stakeholders
- Use EmailResponder skill

### With Calendar
- Schedule review meetings
- Use Calendar MCP

### With Accounting
- Pull revenue data
- Use OdooAccounting skill (future)

## Related Skills
- WeeklyBusinessAudit
- SubscriptionAuditor
- SocialMediaSummary
- HumanApprovalRequest
