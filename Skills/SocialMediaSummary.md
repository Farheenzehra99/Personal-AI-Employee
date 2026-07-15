# Skill: SocialMediaSummary

## Purpose
Generate comprehensive reports summarizing social media activity across all platforms.

## When to Use
- Weekly social media reviews
- Monthly performance reports
- Campaign analysis
- Stakeholder updates
- Content strategy planning

## Capabilities
- Aggregate posts from all platforms
- Calculate engagement metrics
- Identify top-performing content
- Track posting frequency
- Generate visual summaries
- Provide recommendations

## Usage

### Weekly Summary
```
Use SocialMediaSummary to generate this week's social media report
```

### Platform-Specific
```
Use SocialMediaSummary to analyze LinkedIn performance for last 30 days
```

### Campaign Report
```
Use SocialMediaSummary to report on the AI Employee launch campaign
```

## Workflow

1. **Data Collection**
   - Scan `Done/` folder for posted content
   - Extract platform, date, content
   - Count posts per platform

2. **Analysis**
   - Calculate posting frequency
   - Identify best performing posts
   - Track consistency
   - Compare vs targets

3. **Report Generation**
   - Create summary document
   - Include metrics table
   - List top posts
   - Provide recommendations

4. **Distribution**
   - Save to `Reports/Social_Media_*.md`
   - Share with team
   - Add to weekly briefing

## Metrics Tracked

### Per Platform
| Metric | Description |
|--------|-------------|
| Total Posts | Count of posts |
| Posting Frequency | Posts per week |
| Best Day | Highest engagement day |
| Best Time | Highest engagement time |
| Top Hashtags | Most used hashtags |

### Overall
| Metric | Target |
|--------|--------|
| Total Posts/Week | 20+ |
| Platforms Active | 4+ |
| Consistency Score | 80%+ |
| Content Variety | Mixed |

## Example Report

```markdown
# 📱 Social Media Weekly Summary

**Period:** 2026-03-05 to 2026-03-12

## Overview

| Platform | Posts | Target | Status |
|----------|-------|--------|--------|
| LinkedIn | 10 | 5 | ✅ |
| Facebook | 5 | 5 | ✅ |
| Instagram | 3 | 5 | ⚠️ |
| Twitter | 0 | 5 | ❌ |
| **Total** | **18** | **20** | ⚠️ |

## Top Performing Posts

### LinkedIn
🚀 Just Built My AI Employee - 100+ likes
✅ Best post: AI Agents explanation

### Facebook
📊 CEO Briefing System launch - 50+ reactions

## Posting Consistency

| Day | Posts |
|-----|-------|
| Monday | 3 |
| Tuesday | 4 |
| Wednesday | 2 |
| Thursday | 5 |
| Friday | 4 |
| Weekend | 0 |

## Recommendations

1. **Increase Instagram posting** - Only 3 posts this week
2. **Start Twitter activity** - No tweets posted
3. **Maintain LinkedIn momentum** - Excellent performance
4. **Weekend posting** - Consider light weekend content
```

## Files
- Script: `watchers/social_media_summary.py` (create)
- Output: `Reports/Social_Media_*.md`
- Data: `Done/` folder

## Integration

### With CEO Briefing
- Include in weekly briefing
- Use CEOBriefingGenerator skill

### With Content Planning
- Inform next week's strategy
- Use ContentPlanner skill

## Related Skills
- CEOBriefingGenerator
- LinkedInAutoPost
- FacebookAutoPost
- InstagramAutoPost
- TwitterAutoPost
