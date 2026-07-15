# Skill: SubscriptionAuditor

## Purpose
Audit and analyze business subscriptions to identify unused services, cost increases, and optimization opportunities.

## When to Use
- Monthly subscription review
- Cost optimization initiatives
- Budget planning
- Identifying unused services
- Vendor consolidation

## Capabilities
- Scan transactions for subscriptions
- Identify recurring payments
- Track subscription costs
- Flag unused services
- Detect price increases
- Recommend cancellations

## Usage

### Monthly Audit
```
Use SubscriptionAuditor to review all subscriptions for this month
```

### Cost Analysis
```
Use SubscriptionAuditor to analyze subscription costs by category
```

### Unused Services
```
Use SubscriptionAuditor to find subscriptions not used in 30+ days
```

## Workflow

1. **Transaction Analysis**
   - Scan bank transactions
   - Identify recurring payments
   - Match against known subscription patterns

2. **Usage Check**
   - Check last login date
   - Verify active usage
   - Compare cost vs value

3. **Flag Issues**
   - No login in 30+ days
   - Price increase >20%
   - Duplicate functionality

4. **Generate Report**
   - List all subscriptions
   - Total monthly cost
   - Recommendations

## Subscription Patterns

```python
SUBSCRIPTION_PATTERNS = {
    'netflix.com': 'Netflix - $15.99/mo',
    'spotify.com': 'Spotify - $9.99/mo',
    'adobe.com': 'Adobe Creative Cloud - $54.99/mo',
    'notion.so': 'Notion - $15.00/mo',
    'slack.com': 'Slack - $8.75/mo',
    'linkedin.com': 'LinkedIn Premium - $39.99/mo',
    'github.com': 'GitHub Pro - $4.00/mo',
    'aws.amazon.com': 'AWS - Variable',
    'cloud.google.com': 'Google Cloud - Variable',
}
```

## Example Report

```markdown
# 💳 Subscription Audit Report

**Generated:** 2026-03-12
**Period:** February 2026

## Summary

| Metric | Value |
|--------|-------|
| Total Subscriptions | 12 |
| Monthly Cost | $234.89 |
| Unused (30+ days) | 2 |
| Price Increases | 1 |

## All Subscriptions

| Service | Cost | Last Used | Status |
|---------|------|-----------|--------|
| Netflix | $15.99 | 3 days ago | ✅ Active |
| Spotify | $9.99 | 1 day ago | ✅ Active |
| Adobe CC | $54.99 | 45 days ago | ⚠️ Unused |
| Notion | $15.00 | 2 days ago | ✅ Active |
| Slack | $8.75 | 1 day ago | ✅ Active |
| LinkedIn | $39.99 | 5 days ago | ✅ Active |

## Flags

### ⚠️ Unused Subscriptions
- **Adobe Creative Cloud** - No login in 45 days
  - Cost: $54.99/month
  - Recommendation: Cancel or downgrade

### 📈 Price Increases
- **Netflix** - Increased from $13.99 to $15.99
  - Change: +14%
  - Effective: March 1, 2026

## Recommendations

1. **Cancel Adobe Creative Cloud** - Save $54.99/month
2. **Review Netflix plan** - Consider basic plan
3. **Consolidate tools** - Check for overlap

## Potential Savings

| Action | Monthly Savings |
|--------|-----------------|
| Cancel Adobe CC | $54.99 |
| Netflix downgrade | $6.00 |
| **Total** | **$60.99** |
```

## Files
- Script: `watchers/subscription_auditor.py` (create)
- Config: `Business_Goals.md` (subscription list)
- Output: `Reports/Subscription_Audit_*.md`

## Integration

### With CEO Briefing
- Include in monthly briefing
- Use CEOBriefingGenerator skill

### With Accounting
- Pull transaction data
- Use OdooAccounting skill (future)

## Related Skills
- CEOBriefingGenerator
- WeeklyBusinessAudit
