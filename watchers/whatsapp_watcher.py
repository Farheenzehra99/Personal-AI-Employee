#!/usr/bin/env python3
"""
WhatsApp Watcher - Monitors WhatsApp Web for urgent messages
Creates .md files in Needs_Action/ folder for Claude to process

Note: This uses WhatsApp Web automation via Playwright.
Be aware of WhatsApp's terms of service when using automation.
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


class WhatsAppWatcher(BaseWatcher):
    # Keywords that indicate urgent/important messages
    URGENT_KEYWORDS = [
        'urgent', 'asap', 'emergency', 'help', 'invoice', 'payment',
        'deadline', 'meeting', 'call', 'important', 'quick', 'soon',
        'today', 'tomorrow', 'reply', 'response', 'update'
    ]
    
    # Keywords that indicate financial content (requires approval)
    FINANCIAL_KEYWORDS = [
        'payment', 'invoice', 'bill', 'money', 'transfer', 'bank',
        'pay', 'paid', 'amount', 'due', 'receipt', 'transaction'
    ]
    
    def __init__(self, vault_path: str, session_path: str = None):
        super().__init__(vault_path, check_interval=30)
        
        # Session path for persistent login
        if session_path is None:
            session_path = self.vault_path / '.whatsapp_session'
        else:
            session_path = Path(session_path)
        
        self.session_path = session_path
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Load previously processed messages
        self.state_file = self.vault_path / 'Logs' / 'whatsapp_state.json'
        self._load_state()
    
    def _load_state(self):
        """Load state from file"""
        if self.state_file.exists():
            try:
                state = json.loads(self.state_file.read_text())
                self.processed_ids = set(state.get('processed_ids', []))
                self.logger.info(f"Loaded state: {len(self.processed_ids)} processed messages")
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
        """Check WhatsApp Web for new urgent messages"""
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.warning("Playwright not installed. Run: pip install playwright && playwright install")
            return []
        
        messages = []
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    self.session_path,
                    headless=False,
                    viewport={'width': 1280, 'height': 720}
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to WhatsApp Web
                self.logger.info("Navigating to WhatsApp Web...")
                page.goto('https://web.whatsapp.com', timeout=60000)

                # Wait for chat list (indicates login)
                self.logger.info("Waiting for WhatsApp to load... (up to 5 minutes)")
                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=300000)
                    self.logger.info("WhatsApp Web loaded successfully")
                except PlaywrightTimeout:
                    # Try alternative selector
                    try:
                        page.wait_for_selector('#pane-side', timeout=30000)
                        self.logger.info("WhatsApp Web loaded (alternative selector)")
                    except PlaywrightTimeout:
                        self.logger.warning("WhatsApp Web not loaded or not logged in")
                        self.logger.info("Waiting 60 seconds for manual login...")
                        for i in range(60):
                            if page.query_selector('[data-testid="chat-list"]'):
                                self.logger.info("Login detected!")
                                break
                            time.sleep(1)
                        else:
                            browser.close()
                            return []

                # Small delay for content to load
                time.sleep(5)
                
                # Find all chat items with unread messages
                try:
                    # Look for unread indicators
                    unread_chats = page.query_selector_all('[aria-label*="unread"]')
                    
                    for chat in unread_chats:
                        try:
                            # Get chat name
                            name_elem = chat.query_selector('[dir="auto"]')
                            chat_name = name_elem.inner_text() if name_elem else "Unknown"
                            
                            # Get message preview
                            msg_elem = chat.query_selector('[dir="auto"]:last-child')
                            msg_text = msg_elem.inner_text() if msg_elem else ""
                            
                            # Check if contains urgent keywords
                            msg_lower = msg_text.lower()
                            is_urgent = any(kw in msg_lower for kw in self.URGENT_KEYWORDS)
                            
                            if is_urgent:
                                # Check for financial content
                                is_financial = any(kw in msg_lower for kw in self.FINANCIAL_KEYWORDS)
                                
                                # Create unique ID
                                msg_id = f"{chat_name}_{datetime.now().strftime('%Y%m%d%H%M')}"
                                
                                if msg_id not in self.processed_ids:
                                    messages.append({
                                        'id': msg_id,
                                        'chat_name': chat_name,
                                        'message': msg_text,
                                        'is_financial': is_financial,
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    self.processed_ids.add(msg_id)
                        except Exception as e:
                            self.logger.debug(f"Error processing chat: {e}")
                            continue
                    
                except Exception as e:
                    self.logger.error(f"Error finding unread chats: {e}")
                
                browser.close()
                
                # Save state
                self._save_state()
                
        except Exception as e:
            self.logger.error(f"WhatsApp check failed: {e}")
        
        return messages
    
    def create_action_file(self, message: Dict[str, Any]) -> Path:
        """Create a .md action file for the WhatsApp message"""
        try:
            # Determine priority
            priority = 'high' if message['is_financial'] else 'normal'
            
            # Create content
            content = f'''---
type: whatsapp
from: {message['chat_name']}
received: {message['timestamp']}
priority: {priority}
status: pending
whatsapp_id: {message['id']}
requires_approval: {str(message['is_financial']).lower()}
---

## WhatsApp Message

**From:** {message['chat_name']}  
**Received:** {message['timestamp']}

---

**Message:**

{message['message']}

---

## Suggested Actions
- [ ] Reply to sender
- [ ] Flag for follow-up
- [ ] Archive after processing

## Notes
'''
            
            if message['is_financial']:
                content += '''
⚠️ **FINANCIAL CONTENT DETECTED** ⚠️

This message mentions payment/invoice/banking.
Per Company_Handbook.md rules, this requires human approval before responding.

**Recommended:** Route to Pending_Approval/ folder.
'''
            else:
                content += '''
- No financial content detected
- Safe to auto-reply if sender is known contact
'''
            
            # Sanitize filename
            chat_name = "".join(c for c in message['chat_name'] if c.isalnum() or c in ' -_').strip()[:30]
            filepath = self.needs_action / f'WHATSAPP_{chat_name}_{message["id"][-6:]}.md'
            filepath.write_text(content)
            
            self.logger.info(f"Created action file: {filepath.name}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='WhatsApp Watcher for AI Employee')
    parser.add_argument('--vault-path', default=str(Path(__file__).parent.parent.absolute()),
                        help='Path to vault directory')
    parser.add_argument('--session-path', default=None,
                        help='Path to store WhatsApp session')
    parser.add_argument('--once', action='store_true',
                        help='Run once and exit (for cron)')
    parser.add_argument('--interval', type=int, default=30,
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
    watcher = WhatsAppWatcher(
        vault_path=args.vault_path,
        session_path=args.session_path
    )
    
    if args.once:
        # Run once mode (for cron)
        count = watcher.run_once()
        print(f"WhatsApp check complete. Found {count} urgent messages.")
        sys.exit(0)
    else:
        # Continuous mode
        watcher.run()


if __name__ == "__main__":
    main()
