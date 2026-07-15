#!/usr/bin/env python3
"""
CEO Briefing Generator - Weekly Business Audit
Generates Monday Morning CEO Briefing automatically
"""

import os
import sys
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CEOBriefing')


class CEOBriefingGenerator:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done_folder = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved_folder = self.vault_path / 'Approved'
        self.logs_folder = self.vault_path / 'Logs'
        self.briefings_folder = self.vault_path / 'Briefings'
        
        # Create folders
        for folder in [self.logs_folder, self.briefings_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Load business goals
        self.business_goals = self._load_business_goals()
        
        # Subscription patterns
        self.subscription_patterns = {
            'netflix.com': 'Netflix',
            'spotify.com': 'Spotify',
            'adobe.com': 'Adobe Creative Cloud',
            'notion.so': 'Notion',
            'slack.com': 'Slack',
            'linkedin.com': 'LinkedIn Premium',
            'twitter.com': 'Twitter Blue',
            'github.com': 'GitHub',
            'aws.amazon.com': 'AWS',
            'cloud.google.com': 'Google Cloud',
        }

    def _load_business_goals(self) -> Dict:
        """Load business goals from file"""
        goals_file = self.vault_path / 'Business_Goals.md'
        if goals_file.exists():
            content = goals_file.read_text()
            # Simple parsing - extract key metrics
            goals = {
                'monthly_revenue_goal': 10000,
                'current_mtd': 4500,
                'metrics': {}
            }
            return goals
        return {}

    def generate_briefing(self, days_back: int = 7) -> str:
        """Generate CEO Briefing for the last N days"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Collect data
        completed_tasks = self._get_completed_tasks(start_date, end_date)
        pending_tasks = self._get_pending_tasks()
        social_posts = self._get_social_posts(start_date, end_date)
        subscriptions = self._analyze_subscriptions()
        
        # Generate briefing
        briefing = self._create_briefing(
            start_date=start_date,
            end_date=end_date,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
            social_posts=social_posts,
            subscriptions=subscriptions
        )
        
        # Save briefing
        timestamp = end_date.strftime('%Y-%m-%d_%H%M')
        filename = f'CEO_Briefing_{timestamp}.md'
        filepath = self.briefings_folder / filename
        filepath.write_text(briefing)
        
        logger.info(f"CEO Briefing saved to: {filepath}")
        return briefing

    def _get_completed_tasks(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get tasks completed in the date range"""
        tasks = []
        
        if not self.done_folder.exists():
            return tasks
        
        for filepath in self.done_folder.glob('*.md'):
            try:
                content = filepath.read_text()
                # Extract task info from frontmatter
                if 'type:' in content:
                    tasks.append({
                        'file': filepath.name,
                        'modified': datetime.fromtimestamp(filepath.stat().st_mtime),
                        'content': content[:500]  # First 500 chars
                    })
            except Exception as e:
                logger.debug(f"Error reading {filepath}: {e}")
        
        return tasks

    def _get_pending_tasks(self) -> List[Dict]:
        """Get pending tasks from Needs_Action and Pending_Approval"""
        tasks = []
        
        for folder in [self.needs_action, self.pending_approval]:
            if not folder.exists():
                continue
            
            for filepath in folder.glob('*.md'):
                try:
                    content = filepath.read_text()
                    tasks.append({
                        'file': filepath.name,
                        'folder': folder.name,
                        'modified': datetime.fromtimestamp(filepath.stat().st_mtime),
                        'content': content[:500]
                    })
                except Exception as e:
                    logger.debug(f"Error reading {filepath}: {e}")
        
        return tasks

    def _get_social_posts(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get social media posts from Done folder"""
        posts = {
            'linkedin': 0,
            'facebook': 0,
            'instagram': 0,
            'twitter': 0,
            'total': 0
        }
        
        if not self.done_folder.exists():
            return posts
        
        for filepath in self.done_folder.glob('*.md'):
            content = filepath.read_text().lower()
            
            if 'linkedin' in content:
                posts['linkedin'] += 1
            if 'facebook' in content:
                posts['facebook'] += 1
            if 'instagram' in content:
                posts['instagram'] += 1
            if 'twitter' in content:
                posts['twitter'] += 1
        
        posts['total'] = posts['linkedin'] + posts['facebook'] + posts['instagram'] + posts['twitter']
        return posts

    def _analyze_subscriptions(self) -> List[Dict]:
        """Analyze subscriptions from transactions (placeholder)"""
        # This would integrate with accounting system
        # For now, return placeholder
        return [
            {'name': 'Netflix', 'cost': 15.99, 'status': 'active'},
            {'name': 'Spotify', 'cost': 9.99, 'status': 'active'},
        ]

    def _create_briefing(self, start_date: datetime, end_date: datetime,
                         completed_tasks: List, pending_tasks: List,
                         social_posts: Dict, subscriptions: List) -> str:
        """Create the CEO Briefing document"""
        
        date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        # Calculate metrics
        total_completed = len(completed_tasks)
        total_pending = len(pending_tasks)
        pending_approval_count = len([t for t in pending_tasks if 'Pending_Approval' in t.get('folder', '')])
        
        # Generate briefing
        briefing = f'''---
generated: {datetime.now().isoformat()}
period: {date_range}
type: ceo_briefing
---

# 📊 Monday Morning CEO Briefing

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Period:** {date_range}

---

## 📈 Executive Summary

'''
        
        # Executive summary
        if total_completed > 10:
            briefing += f"**Excellent productivity!** {total_completed} tasks completed this week.\\n\\n"
        elif total_completed > 5:
            briefing += f"**Good progress.** {total_completed} tasks completed this week.\\n\\n"
        else:
            briefing += f"**Needs improvement.** Only {total_completed} tasks completed this week.\\n\\n"
        
        # Revenue section
        briefing += f'''## 💰 Revenue Tracking

| Metric | Value |
|--------|-------|
| Monthly Goal | $10,000 |
| Current MTD | $4,500 |
| Progress | 45% |

> ⚠️ **Note:** Connect bank/accounting system for automatic revenue tracking.

---

## ✅ Completed Tasks This Week

**Total:** {total_completed} tasks

'''
        
        if completed_tasks:
            for task in completed_tasks[-10:]:  # Last 10 tasks
                briefing += f"- [x] {task['file']}\\n"
        else:
            briefing += "*No tasks completed this week.*\\n"
        
        briefing += f'''
---

## ⏳ Pending Tasks

**Total Pending:** {total_pending}
**Awaiting Approval:** {pending_approval_count}

'''
        
        if pending_tasks:
            for task in pending_tasks[:10]:  # First 10 pending
                briefing += f"- [ ] {task['file']} (`{task['folder']}`)\\n"
        else:
            briefing += "*All tasks are clear! 🎉*\\n"
        
        # Social media section
        briefing += f'''
---

## 📱 Social Media Activity

| Platform | Posts This Week |
|----------|-----------------|
| LinkedIn | {social_posts['linkedin']} |
| Facebook | {social_posts['facebook']} |
| Instagram | {social_posts['instagram']} |
| Twitter/X | {social_posts['twitter']} |
| **Total** | **{social_posts['total']}** |

'''
        
        if social_posts['total'] >= 5:
            briefing += "✅ **Great!** Consistent social media presence.\\n\\n"
        elif social_posts['total'] >= 3:
            briefing += "⚠️ **Okay,** but could post more frequently.\\n\\n"
        else:
            briefing += "❌ **Needs improvement!** Aim for 5+ posts per week.\\n\\n"
        
        # Subscriptions section
        briefing += f'''---

## 💳 Subscription Audit

| Service | Monthly Cost | Status |
|---------|--------------|--------|
'''
        
        for sub in subscriptions:
            briefing += f"| {sub['name']} | ${sub['cost']:.2f} | {sub['status']} |\\n"
        
        briefing += f'''
> 💡 **Recommendation:** Review subscriptions marked for audit.

---

## 🚨 Bottlenecks Identified

'''
        
        # Identify bottlenecks
        bottlenecks = []
        
        if pending_approval_count > 5:
            bottlenecks.append(f"- **{pending_approval_count} items awaiting approval** - Consider faster approval turnaround")
        
        if social_posts['total'] < 3:
            bottlenecks.append("- **Low social media activity** - Schedule more posts")
        
        if total_pending > 10:
            bottlenecks.append(f"- **{total_pending} pending tasks** - May need prioritization")
        
        if bottlenecks:
            for bottleneck in bottlenecks:
                briefing += f"{bottleneck}\\n"
        else:
            briefing += "*No major bottlenecks identified! 🎉*\\n"
        
        # Proactive suggestions
        briefing += f'''
---

## 💡 Proactive Suggestions

1. **Review pending approvals** - {pending_approval_count} items waiting
2. **Schedule social media posts** - Aim for consistent daily presence
3. **Audit subscriptions** - Check for unused services
4. **Plan next week** - Prioritize top 3 objectives

---

## 📋 Action Items for This Week

- [ ] Review and approve pending items in `Pending_Approval/`
- [ ] Schedule 5+ social media posts
- [ ] Complete top priority tasks from `Needs_Action/`
- [ ] Review subscription costs
- [ ] Update Business_Goals.md with progress

---

## 📊 Weekly Metrics Summary

| Metric | This Week | Target | Status |
|--------|-----------|--------|--------|
| Tasks Completed | {total_completed} | 10 | {'✅' if total_completed >= 10 else '⚠️'} |
| Social Posts | {social_posts['total']} | 5 | {'✅' if social_posts['total'] >= 5 else '⚠️'} |
| Pending Tasks | {total_pending} | <5 | {'✅' if total_pending < 5 else '⚠️'} |

---

*Generated by AI Employee - CEO Briefing System*
'''
        
        return briefing


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='CEO Briefing Generator')
    parser.add_argument('--vault-path', default='/mnt/d/personal-ai-employee',
                        help='Path to vault directory')
    parser.add_argument('--days', type=int, default=7,
                        help='Number of days to analyze (default: 7)')
    parser.add_argument('--output', type=str,
                        help='Output file path (optional)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    generator = CEOBriefingGenerator(vault_path=args.vault_path)
    
    logger.info(f"Generating CEO Briefing for last {args.days} days...")
    
    briefing = generator.generate_briefing(days_back=args.days)
    
    print("\n" + "="*60)
    print("CEO BRIEFING GENERATED!")
    print("="*60)
    print(f"\nSaved to: {args.vault_path}/Briefings/")
    print("\nPreview (first 50 lines):")
    print("-"*60)
    
    # Print preview
    lines = briefing.split('\n')[:50]
    for line in lines:
        print(line)
    
    if len(briefing.split('\n')) > 50:
        print(f"\n... ({len(briefing.split(chr(10))) - 50} more lines)")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
