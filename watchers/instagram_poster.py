#!/usr/bin/env python3
"""
Instagram Poster - Posts content to Instagram via Playwright automation
Supports feed posts with images and captions
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


class InstagramPoster:
    def __init__(self, vault_path: str, session_path: str = None):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Session path
        if session_path is None:
            session_path = self.vault_path / '.instagram_session'
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

    def post_content(self, caption: str, image_path: str, wait_for_approval: bool = True) -> bool:
        """Post content to Instagram"""
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not installed")
            return False
        
        if not image_path or not Path(image_path).exists():
            self.logger.error("Image path required for Instagram")
            return False
        
        if wait_for_approval:
            approval_file = self.create_approval_file(caption, image_path)
            self.logger.info(f"Created approval file: {approval_file}")
            self.logger.info(f"Move to /Approved folder to post")
            return False
        
        return self._post_to_instagram(caption, image_path)

    def create_approval_file(self, caption: str, image_path: str) -> Path:
        """Create approval file"""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
        filepath = self.pending_approval / f'INSTAGRAM_POST_{timestamp}.md'
        
        approval_content = f'''---
type: instagram_post_approval
created: {datetime.now().isoformat()}
status: pending
action: post_to_instagram
image: {image_path}
---

# Instagram Post Approval Required

## Caption

{caption}

## Image
{image_path}

---

## To Approve
Move this file to `/Approved` folder.

## To Reject
Delete this file.
'''
        filepath.write_text(approval_content)
        return filepath

    def _post_to_instagram(self, caption: str, image_path: str) -> bool:
        """Actually post to Instagram"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    self.session_path,
                    headless=False,
                    viewport={'width': 1280, 'height': 800}
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Go to Instagram
                self.logger.info("Opening Instagram...")
                page.goto('https://www.instagram.com', timeout=60000)
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
                
                self.logger.info("Logged in to Instagram")
                time.sleep(3)
                
                # Click "New" (+) button to create post
                self.logger.info("Opening post creator...")
                
                # Try to find the create button
                create_btn = page.query_selector('button[aria-label="New post"], button[aria-label="Create"], svg[aria-label="New post"]')
                
                if not create_btn:
                    # Try direct URL
                    self.logger.info("Creating post via URL...")
                    page.goto('https://www.instagram.com/create/details/', timeout=30000)
                    time.sleep(3)
                else:
                    create_btn.click()
                    time.sleep(3)
                
                # Upload image
                self.logger.info(f"Uploading image: {image_path}")
                
                file_input = page.query_selector('input[type="file"]')
                if file_input:
                    file_input.set_input_files(str(image_path))
                    self.logger.info("✓ Image uploaded")
                    time.sleep(3)
                else:
                    self.logger.warning("Could not find file input")
                
                # Wait for image to process
                time.sleep(3)
                
                # Click "Next" if present
                next_btn = page.query_selector('button:has-text("Next")')
                if next_btn:
                    next_btn.click()
                    self.logger.info("Clicked Next")
                    time.sleep(2)
                
                # Enter caption
                self.logger.info("Entering caption...")
                
                caption_field = page.query_selector('textarea[aria-label*="caption"], textarea[placeholder*="Caption"]')
                if caption_field:
                    caption_field.fill(caption)
                    self.logger.info("✓ Caption added")
                else:
                    self.logger.warning("Could not find caption field")
                
                # Add hashtags if not in caption
                time.sleep(2)
                
                # Ready to share
                self.logger.info("="*60)
                self.logger.info("POST READY!")
                self.logger.info("="*60)
                self.logger.info("Please click the 'Share' button manually")
                self.logger.info("Waiting 90 seconds...")
                
                # Wait for user to click Share
                shared = False
                for i in range(90):
                    try:
                        # Check if modal is gone
                        modal = page.query_selector('[role="dialog"]')
                        if not modal:
                            self.logger.info("✓ Post submitted!")
                            shared = True
                            break
                    except:
                        pass
                    time.sleep(1)
                
                if not shared:
                    self.logger.warning("Timeout - post may not have been submitted")
                
                # Screenshot
                screenshot = self.vault_path / 'instagram_post_screenshot.png'
                page.screenshot(path=str(screenshot))
                self.logger.info(f"Screenshot: {screenshot}")
                
                browser.close()
                return shared
                
        except Exception as e:
            self.logger.error(f"Error posting to Instagram: {e}")
            return False

    def process_queue(self) -> int:
        """Process approved posts"""
        count = 0
        
        for filepath in self.approved_folder.glob('INSTAGRAM_POST_*.md'):
            content = filepath.read_text()
            
            # Extract caption and image
            lines = content.split('\n')
            caption = []
            image_path = None
            in_caption = False
            
            for line in lines:
                if '## Caption' in line:
                    in_caption = True
                    continue
                elif in_caption and line.startswith('## Image'):
                    image_path = line.split(':', 1)[1].strip()
                elif in_caption and line.startswith('---'):
                    break
                elif in_caption and line.strip():
                    caption.append(line)
            
            caption_text = '\n'.join(caption).strip()
            
            if caption_text and image_path:
                self.logger.info(f"Processing: {filepath.name}")
                success = self._post_to_instagram(caption_text, image_path)
                
                if success:
                    filepath.rename(self.done_folder / filepath.name)
                    count += 1
                    self.logger.info("✓ Posted successfully")
                else:
                    self.logger.error("✗ Failed to post")
        
        return count


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Instagram Poster')
    parser.add_argument('--vault-path', default=str(Path(__file__).parent.parent.absolute()))
    parser.add_argument('--caption', type=str, help='Post caption (or file path)')
    parser.add_argument('--image', type=str, help='Image path (required)')
    parser.add_argument('--session-path', type=str, help='Instagram session path')
    parser.add_argument('--process-queue', action='store_true', help='Process approved queue')
    parser.add_argument('--verbose', '-v', action='store_true')
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    poster = InstagramPoster(vault_path=args.vault_path, session_path=args.session_path)
    
    if args.caption:
        # If caption is a file, read it
        if Path(args.caption).exists():
            args.caption = Path(args.caption).read_text()
        
        poster.post_content(args.caption, args.image, wait_for_approval=True)
    elif args.process_queue:
        count = poster.process_queue()
        print(f"Posted {count} Instagram update(s)")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
