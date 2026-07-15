# Skill: WeeklyBusinessAudit

## Purpose
Conduct comprehensive weekly business audits analyzing all aspects of the AI Employee system.

## When to Use
- End of week review (Friday/Saturday)
- Weekly planning (Sunday/Monday)
- Performance optimization
- Stakeholder reporting

## Capabilities
- Aggregate all business metrics
- Analyze task completion rates
- Review financial performance
- Assess social media presence
- Identify system bottlenecks
- Generate improvement recommendations

## Usage

### Weekly Audit
```
Use WeeklyBusinessAudit to conduct this week's business review
```

### Full Report
```
Use WeeklyBusinessAudit to generate comprehensive weekly report with recommendations
```

### Quick Summary
```
Use WeeklyBusinessAudit for a quick 5-minute summary of key metrics
```

## Workflow

1. **Data Aggregation**
   - Collect completed tasks
   - Gather pending items
   - Pull social media stats
   - Review financial data
   - Check subscription costs

2. **Analysis**
   - Calculate completion rates
   - Identify trends
   - Compare vs targets
   - Find bottlenecks
   - Assess productivity

3. **Report Generation**
   - Executive summary
   - Key metrics
   - Achievements
   - Challenges
   - Recommendations

4. **Action Planning**
   - Priority tasks for next week
   - Process improvements
   - Resource allocation
   - Goal adjustments

## Audit Sections

### 1. Executive Summary
- Overall assessment
- Key wins
- Major concerns
- Week rating (1-10)

### 2. Task Metrics
| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| Completed | 25 | 20 | +25% |
| Pending | 8 | 12 | -33% |
| Approval Time | 12h | 18h | -33% |

### 3. Social Media Performance
| Platform | Posts | Engagement | Status |
|----------|-------|------------|--------|
| LinkedIn | 10 | High | ✅ |
| Facebook | 5 | Medium | ✅ |
| Instagram | 3 | Low | ⚠️ |
| Twitter | 0 | N/A | ❌ |

### 4. Financial Summary
- Revenue tracked
- Expenses categorized
- Subscription costs
- Cash flow status

### 5. System Health
- Watcher uptime
- Error rates
- Failed posts
- Recovery actions

### 6. Recommendations
- Process improvements
- Tool optimizations
- Priority shifts
- Resource needs

## Example Output

```markdown
# 📊 Weekly Business Audit

**Week:** 2026-W10 (Mar 5-12)
**Generated:** 2026-03-12

## Executive Summary

**Week Rating:** 8/10 ⭐

Strong performance across most metrics. LinkedIn posting exceeded targets. 
Some bottlenecks in email response time need attention.

## Task Completion

| Category | Completed | Pending | Rate |
|----------|-----------|---------|------|
| Emails | 15 | 5 | 75% |
| Social Posts | 18 | 2 | 90% |
| Approvals | 12 | 0 | 100% |
| **Total** | **45** | **7** | **87%** |

## Social Media Summary

**Total Posts:** 18 (Target: 20) ⚠️

| Platform | Actual | Target | Status |
|----------|--------|--------|--------|
| LinkedIn | 10 | 5 | ✅ +100% |
| Facebook | 5 | 5 | ✅ 100% |
| Instagram | 3 | 5 | ⚠️ 60% |
| Twitter | 0 | 5 | ❌ 0% |

## Financial Overview

| Category | Amount |
|----------|--------|
| Revenue (MTD) | $4,500 |
| Expenses (MTD) | $1,200 |
| Subscriptions | $235 |
| **Net** | **$3,065** |

## System Health

| Component | Status | Issues |
|-----------|--------|--------|
| Gmail Watcher | ✅ | 0 |
| WhatsApp Watcher | ✅ | 0 |
| LinkedIn Watcher | ✅ | 0 |
| Facebook Watcher | ⚠️ | 1 timeout |
| Instagram Watcher | ✅ | 0 |

## Bottlenecks Identified

1. **Email Response Time** - Average 36 hours (Target: 24h)
2. **Instagram Posting** - Inconsistent schedule
3. **Twitter Integration** - Not yet implemented

## Recommendations

### High Priority
1. Implement email auto-responder for common queries
2. Schedule Instagram posts in advance

### Medium Priority
3. Evaluate Twitter API for automation
4. Review Facebook posting times

### Low Priority
5. Explore new social platforms
6. Test video content

## Next Week Goals

1. Complete 50+ tasks
2. Post 20+ social media updates
3. Reduce email response time to <24h
4. Launch Twitter presence
5. Audit all subscriptions

## Wins This Week 🎉

- ✅ LinkedIn engagement up 40%
- ✅ Zero pending approvals
- ✅ CEO Briefing system launched
- ✅ 10+ automated posts published
```

## Files
- Script: `watchers/weekly_business_audit.py` (create)
- Output: `Reports/Weekly_Audit_*.md`
- Input: All `Done/`, `Needs_Action/`, `Logs/` folders

## Integration

### With CEO Briefing
- Input for Monday briefing
- Use CEOBriefingGenerator skill

### With Goal Setting
- Inform next week's goals
- Update Business_Goals.md

## Related Skills
- CEOBriefingGenerator
- SocialMediaSummary
- SubscriptionAuditor
- RalphWiggumLoop
