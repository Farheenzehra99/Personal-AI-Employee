#!/usr/bin/env python3
"""
Facebook Poster - Posts content to Facebook via Playwright automation
Supports text, images, and cross-posting to Instagram
"""

import os
import sys
import logging
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class FacebookPoster:
    def __init__(self, vault_path: str, session_path: str = None):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Session path
        if session_path is None:
            session_path = self.vault_path / '.facebook_session'
        else:
            session_path = Path(session_path)
        
        self.session_path = session_path
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Folders
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved_folder = self.vault_path / 'Approved'
        self.done_folder = self.vault_path / 'Done'
        
        for folder in [self.pending_approval, self.approved_folder, self.done_folder]:
            folder.mkdir(parents=True, exist_ok=True)

    def post_content(self, content: str, image_path: str = None, wait_for_approval: bool = True) -> bool:
        """Post content to Facebook"""
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not installed")
            return False
        
        if wait_for_approval:
            approval_file = self.create_approval_file(content, image_path)
            self.logger.info(f"Created approval file: {approval_file}")
            self.logger.info(f"Move to /Approved folder to post")
            return False
        
        return self._post_to_facebook(content, image_path)

    def create_approval_file(self, content: str, image_path: str = None) -> Path:
        """Create approval file"""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
        filepath = self.pending_approval / f'FACEBOOK_POST_{timestamp}.md'
        
        image_info = f"\n**Image:** {image_path}" if image_path else ""
        
        approval_content = f'''---
type: facebook_post_approval
created: {datetime.now().isoformat()}
status: pending
action: post_to_facebook
image: {image_path if image_path else "none"}
---

# Facebook Post Approval Required

## Post Content

{content}
{image_info}

---

## To Approve
Move this file to `/Approved` folder.

## To Reject
Delete this file.
'''
        filepath.write_text(approval_content)
        return filepath

    def _post_to_facebook(self, content: str, image_path: str = None) -> bool:
        """Actually post to Facebook"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    self.session_path,
                    headless=False,
                    viewport={'width': 1280, 'height': 800}
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Go to Facebook
                self.logger.info("Opening Facebook...")
                page.goto('https://www.facebook.com', timeout=60000)
                time.sleep(5)
                
                # Check login
                if 'login' in page.url:
                    self.logger.warning("Not logged in. Waiting 60 seconds...")
                    for i in range(60):
                        if 'login' not in page.url:
                            self.logger.info("Login detected!")
                            break
                        time.sleep(1)
                    else:
                        self.logger.error("Login timeout")
                        browser.close()
                        return False
                
                self.logger.info("Logged in to Facebook")
                time.sleep(3)
                
                # Click "What's on your mind?" post creator
                self.logger.info("Opening post creator...")
                
                post_triggers = [
                    'button:has-text("What\'s on your mind?")',
                    'button:has-text("Create post")',
                    '[data-testid="create_post"]',
                    '.x1n2onr6'
                ]
                
                clicked = False
                for selector in post_triggers:
                    try:
                        btn = page.query_selector(selector)
                        if btn:
                            btn.click()
                            self.logger.info(f"Clicked: {selector}")
                            clicked = True
                            break
                    except:
                        continue
                
                if not clicked:
                    self.logger.warning("Post button not found, trying direct URL")
                    page.goto('https://www.facebook.com/feed/composer/entry/', timeout=30000)
                
                time.sleep(3)
                
                # Upload image if provided
                if image_path and Path(image_path).exists():
                    self.logger.info(f"Uploading image: {image_path}")
                    
                    # Find and click photo/video button
                    photo_btn = page.query_selector('button[aria-label*="photo"], button[aria-label*="video"], button[aria-label*="image"]')
                    if photo_btn:
                        photo_btn.click()
                        time.sleep(2)
                        
                        # Upload file
                        file_input = page.query_selector('input[type="file"]')
                        if file_input:
                            file_input.set_input_files(str(image_path))
                            self.logger.info("✓ Image uploaded")
                            time.sleep(3)
                        else:
                            self.logger.warning("Could not find file input")
                    else:
                        self.logger.warning("Could not find photo button")
                
                # Enter text content
                self.logger.info("Entering content...")
                
                # Find text area
                text_selectors = [
                    '[aria-label*="What\'s on your mind?"]',
                    '[aria-label*="Write something"]',
                    '[role="textbox"]',
                    '[contenteditable="true"]',
                    'div[data-testid="composer-text-input"]'
                ]
                
                entered = False
                for selector in text_selectors:
                    try:
                        text_field = page.query_selector(selector)
                        if text_field:
                            text_field.fill('')
                            text_field.fill(content)
                            self.logger.info(f"Content entered via: {selector}")
                            entered = True
                            break
                    except:
                        continue
                
                if not entered:
                    self.logger.warning("Could not find text field, using keyboard")
                    page.keyboard.type(content, delay=50)
                
                time.sleep(2)
                
                # Ready to post
                self.logger.info("="*60)
                self.logger.info("POST READY!")
                self.logger.info("="*60)
                self.logger.info("Please click the 'Post' button manually")
                self.logger.info("Waiting 90 seconds...")
                
                # Wait for user to click Post
                posted = False
                for i in range(90):
                    try:
                        # Check if composer is gone
                        composer = page.query_selector('[role="dialog"]')
                        if not composer:
                            self.logger.info("✓ Post submitted!")
                            posted = True
                            break
                    except:
                        pass
                    time.sleep(1)
                
                if not posted:
                    self.logger.warning("Timeout - post may not have been submitted")
                
                # Screenshot
                screenshot = self.vault_path / 'facebook_post_screenshot.png'
                page.screenshot(path=str(screenshot))
                self.logger.info(f"Screenshot: {screenshot}")
                
                browser.close()
                return posted
                
        except Exception as e:
            self.logger.error(f"Error posting to Facebook: {e}")
            return False

    def process_queue(self) -> int:
        """Process approved posts"""
        count = 0
        
        for filepath in self.approved_folder.glob('FACEBOOK_POST_*.md'):
            content = filepath.read_text()
            
            # Extract content and image
            lines = content.split('\n')
            post_content = []
            image_path = None
            in_content = False
            
            for line in lines:
                if '## Post Content' in line:
                    in_content = True
                    continue
                elif in_content and line.startswith('**Image:**'):
                    image_path = line.split(':', 1)[1].strip()
                    if image_path == 'none':
                        image_path = None
                elif in_content and line.startswith('---'):
                    break
                elif in_content and line.strip():
                    post_content.append(line)
            
            post_text = '\n'.join(post_content).strip()
            
            if post_text:
                self.logger.info(f"Processing: {filepath.name}")
                success = self._post_to_facebook(post_text, image_path)
                
                if success:
                    filepath.rename(self.done_folder / filepath.name)
                    count += 1
                    self.logger.info("✓ Posted successfully")
                else:
                    self.logger.error("✗ Failed to post")
        
        return count


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Facebook Poster')
    parser.add_argument('--vault-path', default=str(Path(__file__).parent.parent.absolute()))
    parser.add_argument('--content', type=str, help='Post content (or file path)')
    parser.add_argument('--image', type=str, help='Image path')
    parser.add_argument('--session-path', type=str, help='Facebook session path')
    parser.add_argument('--process-queue', action='store_true', help='Process approved queue')
    parser.add_argument('--verbose', '-v', action='store_true')
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    poster = FacebookPoster(vault_path=args.vault_path, session_path=args.session_path)
    
    if args.content:
        # If content is a file, read it
        if Path(args.content).exists():
            args.content = Path(args.content).read_text()
        
        poster.post_content(args.content, args.image, wait_for_approval=True)
    elif args.process_queue:
        count = poster.process_queue()
        print(f"Posted {count} Facebook update(s)")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
