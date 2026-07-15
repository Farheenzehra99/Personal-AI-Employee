#!/usr/bin/env python3
"""
WhatsApp Sender - Sends replies via WhatsApp Web
"""

import os
import sys
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class WhatsAppSender:
    def __init__(self, vault_path: str, session_path: str = None):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if session_path is None:
            session_path = self.vault_path / '.whatsapp_session'
        else:
            session_path = Path(session_path)
        
        self.session_path = session_path
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved_folder = self.vault_path / 'Approved'
        self.done_folder = self.vault_path / 'Done'
        self.needs_action = self.vault_path / 'Needs_Action'
        
        for folder in [self.pending_approval, self.approved_folder, self.done_folder]:
            folder.mkdir(parents=True, exist_ok=True)

    def send_message(self, contact_name: str, message: str, wait_for_approval: bool = True) -> bool:
        """
        Send WhatsApp message
        
        Args:
            contact_name: Contact name to search for
            message: Message to send
            wait_for_approval: If True, create approval file first
            
        Returns:
            True if sent successfully
        """
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not installed")
            return False
        
        if wait_for_approval:
            approval_file = self.create_approval_file(contact_name, message)
            self.logger.info(f"Created approval file: {approval_file}")
            self.logger.info(f"Move to /Approved folder to send message")
            return False
        
        return self._send_whatsapp_message(contact_name, message)

    def _send_whatsapp_message(self, contact_name: str, message: str) -> bool:
        """Actually send message via WhatsApp Web"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    self.session_path,
                    headless=False,  # Visible browser
                    viewport={'width': 1280, 'height': 720}
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Go to WhatsApp
                self.logger.info("Opening WhatsApp Web...")
                page.goto('https://web.whatsapp.com', timeout=60000)
                
                # Wait for login
                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=60000)
                    self.logger.info("Logged in to WhatsApp")
                except PlaywrightTimeout:
                    self.logger.error("Not logged in to WhatsApp")
                    browser.close()
                    return False
                
                time.sleep(3)
                
                # Search for contact
                self.logger.info(f"Searching for contact: {contact_name}")
                
                # Click on search box
                search_box = page.query_selector('[role="searchbox"]')
                if not search_box:
                    search_box = page.query_selector('[data-testid="search"]')
                
                if search_box:
                    search_box.click()
                    time.sleep(1)
                    
                    # Type contact name
                    page.keyboard.type(contact_name, delay=50)
                    time.sleep(2)
                    
                    # Click on first result
                    try:
                        first_result = page.query_selector('[data-testid="chat-list"] [role="link"]')
                        if first_result:
                            first_result.click()
                            self.logger.info(f"Opened chat with {contact_name}")
                        else:
                            self.logger.error(f"Contact {contact_name} not found")
                            browser.close()
                            return False
                    except Exception as e:
                        self.logger.error(f"Error selecting contact: {e}")
                        browser.close()
                        return False
                else:
                    self.logger.error("Search box not found")
                    browser.close()
                    return False
                
                time.sleep(2)
                
                # Type message
                self.logger.info("Typing message...")
                
                # Find message input
                message_input = page.query_selector('[data-testid="message-input"]')
                if message_input:
                    message_input.fill(message)
                    time.sleep(1)
                    
                    # Click send button
                    send_button = page.query_selector('[data-testid="compose-btn-send"]')
                    if send_button:
                        send_button.click()
                        self.logger.info("Message sent!")
                        time.sleep(2)
                        
                        # Take screenshot
                        screenshot = self.vault_path / 'whatsapp_sent_screenshot.png'
                        page.screenshot(path=str(screenshot))
                        self.logger.info(f"Screenshot: {screenshot}")
                        
                        browser.close()
                        return True
                    else:
                        self.logger.error("Send button not found")
                        browser.close()
                        return False
                else:
                    self.logger.error("Message input not found")
                    browser.close()
                    return False
                
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False

    def create_approval_file(self, contact_name: str, message: str) -> Path:
        """Create approval file for WhatsApp message"""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
        filepath = self.pending_approval / f'WHATSAPP_SEND_{timestamp}.md'
        
        content = f'''---
type: whatsapp_send_approval
created: {datetime.now().isoformat()}
status: pending
action: send_whatsapp
contact: {contact_name}
---

# WhatsApp Message Approval Required

## Send To
{contact_name}

## Message
{message}

---

## To Approve
Move this file to `/Approved` folder.

## To Reject
Delete this file.
'''
        filepath.write_text(content)
        return filepath

    def process_queue(self) -> int:
        """Process approved WhatsApp messages"""
        count = 0
        
        for filepath in self.approved_folder.glob('WHATSAPP_SEND_*.md'):
            content = filepath.read_text()
            
            # Extract contact and message
            lines = content.split('\n')
            contact = None
            message = None
            in_message = False
            
            for i, line in enumerate(lines):
                if line.startswith('contact:'):
                    contact = line.split(':', 1)[1].strip()
                elif '## Message' in line:
                    in_message = True
                elif in_message and line.startswith('---'):
                    break
                elif in_message and line.strip():
                    message = line.strip() if message is None else message + '\n' + line.strip()
            
            if contact and message:
                self.logger.info(f"Sending to {contact}: {message[:50]}...")
                success = self._send_whatsapp_message(contact, message)
                
                if success:
                    filepath.rename(self.done_folder / filepath.name)
                    count += 1
                    self.logger.info("✓ Message sent")
                else:
                    self.logger.error("✗ Failed to send")
            else:
                self.logger.error(f"Could not parse: {filepath.name}")
        
        return count

    def reply_to_message(self, action_file: Path) -> bool:
        """Reply to a WhatsApp message from Needs_Action folder"""
        content = action_file.read_text()
        
        # Extract info from frontmatter
        lines = content.split('\n')
        contact = None
        requires_approval = False
        
        for line in lines:
            if line.startswith('from:'):
                contact = line.split(':', 1)[1].strip()
            elif line.startswith('requires_approval:'):
                requires_approval = 'true' in line.lower()
        
        if not contact:
            self.logger.error("Could not find contact in action file")
            return False
        
        # Generate reply (simple template for now)
        reply = f"Thank you for your message. We will get back to you soon."
        
        if requires_approval:
            # Create approval file
            approval = self.create_approval_file(contact, reply)
            self.logger.info(f"Approval required: {approval}")
            return False
        else:
            # Send directly
            return self._send_whatsapp_message(contact, reply)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='WhatsApp Sender')
    parser.add_argument('--vault-path', default=str(Path(__file__).parent.parent.absolute()))
    parser.add_argument('--to', type=str, help='Contact name')
    parser.add_argument('--message', type=str, help='Message to send')
    parser.add_argument('--process-queue', action='store_true', help='Process approved queue')
    parser.add_argument('--reply-to', type=str, help='Reply to action file')
    parser.add_argument('--verbose', '-v', action='store_true')
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    sender = WhatsAppSender(vault_path=args.vault_path)
    
    if args.to and args.message:
        sender.send_message(args.to, args.message, wait_for_approval=True)
    elif args.process_queue:
        count = sender.process_queue()
        print(f"Sent {count} message(s)")
    elif args.reply_to:
        sender.reply_to_message(Path(args.reply_to))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
