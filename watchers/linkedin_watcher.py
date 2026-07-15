#!/usr/bin/env python3
"""
LinkedIn Watcher - Monitors LinkedIn for new messages and connection requests
Creates .md files in Needs_Action/ folder for Claude to process

Note: This uses LinkedIn website automation via Playwright.
Be aware of LinkedIn's terms of service when using automation.
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


class LinkedInWatcher(BaseWatcher):
    # Keywords that indicate important messages
    IMPORTANT_KEYWORDS = [
        'opportunity', 'position', 'job', 'role', 'interview',
        'project', 'collaboration', 'partnership', 'meeting',
        'call', 'connect', 'interested', 'hire', 'freelance',
        'contract', 'proposal', 'budget', 'rate', 'pricing'
    ]
    
    # Keywords that indicate potential spam
    SPAM_KEYWORDS = [
        'crypto', 'blockchain', 'investment', 'trading', 'forex',
        'mlm', 'opportunity of a lifetime', 'guaranteed', 'rich'
    ]
    
    def __init__(self, vault_path: str, session_path: str = None):
        super().__init__(vault_path, check_interval=900)  # 15 min default
        
        # Session path for persistent login
        if session_path is None:
            session_path = self.vault_path / '.linkedin_session'
        else:
            session_path = Path(session_path)
        
        self.session_path = session_path
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Load state
        self.state_file = self.vault_path / 'Logs' / 'linkedin_state.json'
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
        """Check LinkedIn for new messages and connection requests"""
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.warning("Playwright not installed. Run: pip install playwright && playwright install")
            return []
        
        items = []
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                # Using headless=False for visible browser (debugging)
                browser = p.chromium.launch_persistent_context(
                    self.session_path,
                    headless=False,  # Changed to visible browser
                    viewport={'width': 1280, 'height': 720}
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to LinkedIn
                self.logger.info("Navigating to LinkedIn...")
                page.goto('https://www.linkedin.com', timeout=60000)

                # Wait for page to load
                time.sleep(5)
                
                # Check if logged in by URL or page content
                current_url = page.url
                if 'login' in current_url or 'checkpoint' in current_url:
                    self.logger.info("Login page detected - waiting 120 seconds for manual login...")
                    # Wait longer for user to login
                    for i in range(120):
                        current_url = page.url
                        if 'feed' in current_url or 'mynetwork' in current_url:
                            self.logger.info("Login successful!")
                            break
                        time.sleep(1)
                    else:
                        self.logger.warning("Login timeout - browser will close")
                
                if 'feed' in current_url or 'mynetwork' in current_url or 'messaging' in current_url:
                    self.logger.info("Successfully logged in to LinkedIn")
                else:
                    self.logger.warning(f"Unexpected URL: {current_url}")
                
                # Check for notifications bell
                try:
                    notification_bell = page.query_selector('[data-control-name="notifications"]')
                    if notification_bell:
                        has_notifications = 'notification-badge' in notification_bell.inner_html()
                        if has_notifications:
                            self.logger.info("New notifications detected")
                except:
                    pass
                
                # Navigate to messaging page
                try:
                    page.goto('https://www.linkedin.com/messaging/', timeout=30000)
                    time.sleep(2)
                    
                    # Find unread conversations
                    try:
                        unread_conversations = page.query_selector_all('[aria-label*="unread"]')
                        
                        for conv in unread_conversations:
                            try:
                                # Get sender name
                                name_elem = conv.query_selector('[aria-label*="Message from"]')
                                if not name_elem:
                                    name_elem = conv.query_selector('span[dir="auto"]')
                                
                                sender_name = name_elem.inner_text() if name_elem else "Unknown"
                                
                                # Get message preview
                                msg_elem = conv.query_selector('span:last-child')
                                msg_preview = msg_elem.inner_text() if msg_elem else ""
                                
                                # Check if important
                                msg_lower = msg_preview.lower()
                                is_important = any(kw in msg_lower for kw in self.IMPORTANT_KEYWORDS)
                                is_spam = any(kw in msg_lower for kw in self.SPAM_KEYWORDS)
                                
                                msg_id = f"msg_{sender_name}_{datetime.now().strftime('%Y%m%d%H%M')}"
                                
                                if msg_id not in self.processed_ids and not is_spam:
                                    items.append({
                                        'type': 'message',
                                        'id': msg_id,
                                        'sender': sender_name,
                                        'message': msg_preview,
                                        'is_important': is_important,
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    self.processed_ids.add(msg_id)
                                    
                            except Exception as e:
                                self.logger.debug(f"Error processing conversation: {e}")
                                continue
                                
                    except Exception as e:
                        self.logger.debug(f"No unread conversations: {e}")
                    
                except Exception as e:
                    self.logger.error(f"Error accessing messaging: {e}")
                
                # Check for connection requests
                try:
                    page.goto('https://www.linkedin.com/mynetwork/', timeout=30000)
                    time.sleep(2)
                    
                    # Look for connection request cards
                    connection_requests = page.query_selector_all('[data-control-name="connection_requests"]')
                    
                    for req in connection_requests[:5]:  # Limit to 5
                        try:
                            name_elem = req.query_selector('a[href*="/in/"] span')
                            requester_name = name_elem.inner_text() if name_elem else "Unknown"
                            
                            req_id = f"conn_{requester_name}_{datetime.now().strftime('%Y%m%d')}"
                            
                            if req_id not in self.processed_ids:
                                items.append({
                                    'type': 'connection_request',
                                    'id': req_id,
                                    'requester': requester_name,
                                    'timestamp': datetime.now().isoformat()
                                })
                                self.processed_ids.add(req_id)
                                
                        except Exception as e:
                            self.logger.debug(f"Error processing connection request: {e}")
                            continue
                            
                except Exception as e:
                    self.logger.debug(f"No connection requests: {e}")
                
                browser.close()
                
                # Save state
                self._save_state()
                
        except Exception as e:
            self.logger.error(f"LinkedIn check failed: {e}")
        
        return items
    
    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """Create a .md action file for the LinkedIn item"""
        try:
            if item['type'] == 'message':
                content = f'''---
type: linkedin_message
from: {item['sender']}
received: {item['timestamp']}
priority: {"high" if item['is_important'] else "normal"}
status: pending
linkedin_id: {item['id']}
---

## LinkedIn Message

**From:** {item['sender']}  
**Received:** {item['timestamp']}

---

**Message Preview:**

{item['message']}

---

## Suggested Actions
- [ ] Reply to sender
- [ ] Schedule call/meeting
- [ ] Archive after processing

## Notes
'''
                
                if item['is_important']:
                    content += '''
⚠️ **IMPORTANT CONTENT DETECTED**

This message mentions business opportunities, projects, or collaborations.
Consider prioritizing this response.
'''
                else:
                    content += '''
- Standard professional message
- Safe to auto-reply with polite response
'''
                
                # Sanitize filename
                sender = "".join(c for c in item['sender'] if c.isalnum() or c in ' -_').strip()[:30]
                filepath = self.needs_action / f'LINKEDIN_MSG_{sender}_{item["id"][-6:]}.md'
                
            elif item['type'] == 'connection_request':
                content = f'''---
type: linkedin_connection
from: {item['requester']}
received: {item['timestamp']}
priority: normal
status: pending
linkedin_id: {item['id']}
---

## LinkedIn Connection Request

**From:** {item['requester']}  
**Received:** {item['timestamp']}

---

## Suggested Actions
- [ ] Accept connection
- [ ] Ignore/Decline
- [ ] Review profile first

## Notes
- Check if sender is in your industry
- Review profile for mutual connections
- Consider accepting if relevant to your network
'''
                
                # Sanitize filename
                requester = "".join(c for c in item['requester'] if c.isalnum() or c in ' -_').strip()[:30]
                filepath = self.needs_action / f'LINKEDIN_CONN_{requester}_{item["id"][-6:]}.md'
            
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
    
    parser = argparse.ArgumentParser(description='LinkedIn Watcher for AI Employee')
    parser.add_argument('--vault-path', default=str(Path(__file__).parent.parent.absolute()),
                        help='Path to vault directory')
    parser.add_argument('--session-path', default=None,
                        help='Path to store LinkedIn session')
    parser.add_argument('--once', action='store_true',
                        help='Run once and exit (for cron)')
    parser.add_argument('--interval', type=int, default=900,
                        help='Check interval in seconds (default: 15 min)')
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
    watcher = LinkedInWatcher(
        vault_path=args.vault_path,
        session_path=args.session_path
    )
    
    if args.once:
        # Run once mode (for cron)
        count = watcher.run_once()
        print(f"LinkedIn check complete. Found {count} new items.")
        sys.exit(0)
    else:
        # Continuous mode
        watcher.run()


if __name__ == "__main__":
    main()
