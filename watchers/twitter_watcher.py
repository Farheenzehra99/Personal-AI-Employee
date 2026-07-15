#!/usr/bin/env python3
"""
Twitter/X Watcher - Monitors Twitter for DMs and mentions
Creates .md files in Needs_Action/ folder for Claude to process
"""

import os
import sys
import logging
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class BaseWatcher:
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        self.processed_ids = set()

    def run_once(self):
        """Run a single check (for cron mode)"""
        try:
            items = self.check_for_updates()
            for item in items:
                self.create_action_file(item)
            return len(items)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            return 0

    def run(self):
        """Run continuously"""
        self.logger.info(f'Starting {self.__class__.__name__}')
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                self.logger.error(f'Error: {e}')
            time.sleep(self.check_interval)


class TwitterWatcher(BaseWatcher):
    # Keywords that indicate important messages
    IMPORTANT_KEYWORDS = [
        'collab', 'collaboration', 'sponsor', 'paid', 'partnership',
        'opportunity', 'project', 'business', 'deal', 'urgent',
        'asap', 'meeting', 'call', 'interview', 'job', 'hire'
    ]

    # Keywords that indicate financial content
    FINANCIAL_KEYWORDS = [
        'payment', 'pay', 'price', 'budget', 'rate', 'fee',
        'money', 'invoice', 'bill', 'transfer', 'bank', '$'
    ]

    def __init__(self, vault_path: str, session_path: str = None):
        super().__init__(vault_path, check_interval=300)  # 5 min default

        # Session path for persistent login
        if session_path is None:
            session_path = self.vault_path / '.twitter_session'
        else:
            session_path = Path(session_path)

        self.session_path = session_path
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Load state
        self.state_file = self.vault_path / 'Logs' / 'twitter_state.json'
        self._load_state()

    def _load_state(self):
        """Load state from file"""
        if self.state_file.exists():
            try:
                state = json.loads(self.state_file.read_text())
                self.processed_ids = set(state.get('processed_ids', []))
                self.logger.info(f"Loaded state: {len(self.processed_ids)} processed items")
            except Exception as e:
                self.logger.warning(f"Failed to load state: {e}")
                self.processed_ids = set()
        else:
            self.processed_ids = set()

    def _save_state(self):
        """Save state to file"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            state = {'processed_ids': list(self.processed_ids)}
            self.state_file.write_text(json.dumps(state, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """Check Twitter for new DMs and mentions"""
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.warning("Playwright not installed")
            return []

        items = []

        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    self.session_path,
                    headless=False,  # Visible browser
                    viewport={'width': 1280, 'height': 720}
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                # Navigate to Twitter
                self.logger.info("Navigating to Twitter/X...")
                page.goto('https://twitter.com', timeout=60000)

                # Wait for login
                try:
                    page.wait_for_selector('[data-testid="primaryColumn"]', timeout=300000)
                    self.logger.info("Twitter loaded")
                except PlaywrightTimeout:
                    self.logger.warning("Twitter not loaded or not logged in")
                    self.logger.info("Waiting 60 seconds for manual login...")
                    for i in range(60):
                        if 'twitter.com' in page.url and 'login' not in page.url:
                            self.logger.info("Login detected!")
                            break
                        time.sleep(1)
                    else:
                        browser.close()
                        return []

                time.sleep(5)

                # Check for DMs
                try:
                    self.logger.info("Checking Direct Messages...")
                    
                    # Navigate to DMs
                    page.goto('https://twitter.com/messages', timeout=30000)
                    time.sleep(3)

                    # Find unread conversations
                    unread_chats = page.query_selector_all('[aria-label*="unread"], [data-testid="AppTabBar_Messages_badge"]')

                    for chat in unread_chats[:10]:  # Limit to 10
                        try:
                            # Get sender name
                            name_elem = chat.query_selector('[dir="auto"]')
                            sender_name = name_elem.inner_text() if name_elem else "Unknown"

                            # Get message preview
                            msg_elem = chat.query_selector('span[dir="auto"]:last-child')
                            msg_preview = msg_elem.inner_text() if msg_elem else ""

                            # Check if important
                            msg_lower = msg_preview.lower()
                            is_important = any(kw in msg_lower for kw in self.IMPORTANT_KEYWORDS)
                            is_financial = any(kw in msg_lower for kw in self.FINANCIAL_KEYWORDS)

                            msg_id = f"tw_dm_{sender_name}_{datetime.now().strftime('%Y%m%d%H%M')}"

                            if msg_id not in self.processed_ids:
                                items.append({
                                    'type': 'message',
                                    'id': msg_id,
                                    'sender': sender_name,
                                    'message': msg_preview,
                                    'is_important': is_important,
                                    'is_financial': is_financial,
                                    'timestamp': datetime.now().isoformat()
                                })
                                self.processed_ids.add(msg_id)

                        except Exception as e:
                            self.logger.debug(f"Error processing chat: {e}")
                            continue

                except Exception as e:
                    self.logger.debug(f"Error accessing DMs: {e}")

                # Check for mentions/notifications
                try:
                    self.logger.info("Checking mentions and notifications...")
                    
                    page.goto('https://twitter.com/notifications', timeout=30000)
                    time.sleep(3)

                    # Find recent notifications (mentions, replies)
                    notifs = page.query_selector_all('[data-testid="tweet"], [role="article"]')

                    for notif in notifs[:5]:  # Limit to 5
                        try:
                            notif_text = notif.inner_text()[:200]
                            
                            # Check if it's a mention or reply
                            is_mention = '@you' in notif_text.lower() or 'mentioned' in notif_text.lower()
                            is_reply = 'replied' in notif_text.lower()
                            
                            if is_mention or is_reply:
                                notif_id = f"tw_notif_{datetime.now().strftime('%Y%m%d%H%M%S')}"

                                if notif_id not in self.processed_ids:
                                    items.append({
                                        'type': 'mention',
                                        'id': notif_id,
                                        'content': notif_text,
                                        'is_mention': is_mention,
                                        'is_reply': is_reply,
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    self.processed_ids.add(notif_id)

                        except Exception as e:
                            self.logger.debug(f"Error processing notification: {e}")
                            continue

                except Exception as e:
                    self.logger.debug(f"Error accessing notifications: {e}")

                browser.close()

                # Save state
                self._save_state()

        except Exception as e:
            self.logger.error(f"Twitter check failed: {e}")

        return items

    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """Create a .md action file for the Twitter item"""
        try:
            if item['type'] == 'message':
                content = f'''---
type: twitter_dm
from: {item['sender']}
received: {item['timestamp']}
priority: {"high" if item['is_important'] else "normal"}
status: pending
twitter_id: {item['id']}
requires_approval: {str(item['is_financial']).lower()}
---

## Twitter Direct Message

**From:** {item['sender']}
**Received:** {item['timestamp']}

---

**Message Preview:**

{item['message']}

---

## Suggested Actions
- [ ] Reply to sender
- [ ] Flag for follow-up
- [ ] Archive after processing

## Notes
'''

                if item['is_financial']:
                    content += '''
⚠️ **FINANCIAL CONTENT DETECTED**

This message mentions payment/business.
Requires human approval before responding.
'''
                elif item['is_important']:
                    content += '''
⚠️ **IMPORTANT CONTENT DETECTED**

This message mentions collaboration or business opportunity.
Consider prioritizing this response.
'''

                sender = "".join(c for c in item['sender'] if c.isalnum() or c in ' -_').strip()[:30]
                filepath = self.needs_action / f'TWITTER_DM_{sender}_{item["id"][-6:]}.md'

            elif item['type'] == 'mention':
                content = f'''---
type: twitter_mention
received: {item['timestamp']}
priority: normal
status: pending
twitter_id: {item['id']}
is_mention: {str(item['is_mention']).lower()}
is_reply: {str(item['is_reply']).lower()}
---

## Twitter Mention/Reply

**Received:** {item['timestamp']}

---

**Content:**

{item['content']}

---

## Suggested Actions
- [ ] Review mention/reply
- [ ] Respond if needed
- [ ] Like or retweet if relevant
- [ ] Mark as processed

## Notes
'''
                filepath = self.needs_action / f'TWITTER_MENTION_{item["id"][-6:]}.md'

            else:
                self.logger.warning(f"Unknown item type: {item['type']}")
                return None

            filepath.write_text(content)
            self.logger.info(f"Created action file: {filepath.name}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Twitter/X Watcher for AI Employee')
    parser.add_argument('--vault-path', default=str(Path(__file__).parent.parent.absolute()),
                        help='Path to vault directory')
    parser.add_argument('--session-path', default=None,
                        help='Path to store Twitter session')
    parser.add_argument('--once', action='store_true',
                        help='Run once and exit (for cron)')
    parser.add_argument('--interval', type=int, default=300,
                        help='Check interval in seconds')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create watcher
    watcher = TwitterWatcher(
        vault_path=args.vault_path,
        session_path=args.session_path
    )

    if args.once:
        count = watcher.run_once()
        print(f"Twitter check complete. Found {count} new items.")
        sys.exit(0)
    else:
        watcher.run()


if __name__ == "__main__":
    main()
