#!/usr/bin/env python3
"""
Twitter/X Poster - Posts tweets via Playwright automation
Supports text, images, and threads
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


class TwitterPoster:
    def __init__(self, vault_path: str, session_path: str = None):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Session path
        if session_path is None:
            session_path = self.vault_path / '.twitter_session'
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

    def post_tweet(self, content: str, image_path: str = None, wait_for_approval: bool = True) -> bool:
        """Post a tweet"""
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not installed")
            return False
        
        if wait_for_approval:
            approval_file = self.create_approval_file(content, image_path)
            self.logger.info(f"Created approval file: {approval_file}")
            self.logger.info(f"Move to /Approved folder to post")
            return False
        
        return self._post_tweet(content, image_path)

    def create_approval_file(self, content: str, image_path: str = None) -> Path:
        """Create approval file"""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
        filepath = self.pending_approval / f'TWITTER_TWEET_{timestamp}.md'
        
        image_info = f"\n**Image:** {image_path}" if image_path else ""
        
        # Check character count
        char_count = len(content)
        char_warning = ""
        if char_count > 280:
            char_warning = f"\n⚠️ **WARNING:** {char_count} characters (Twitter limit: 280)"
        
        approval_content = f'''---
type: twitter_post_approval
created: {datetime.now().isoformat()}
status: pending
action: post_to_twitter
image: {image_path if image_path else "none"}
character_count: {char_count}
---

# Twitter Post Approval Required

## Tweet Content

{content}
{image_info}
{char_warning}

---

## To Approve
Move this file to `/Approved` folder.

## To Reject
Delete this file.

## Notes
- Twitter character limit: 280 characters
- Images count as 24 characters
- Threads can be used for longer content
'''
        filepath.write_text(approval_content)
        return filepath

    def _post_tweet(self, content: str, image_path: str = None) -> bool:
        """Actually post to Twitter"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    self.session_path,
                    headless=False,
                    viewport={'width': 1280, 'height': 800}
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Go to Twitter
                self.logger.info("Opening Twitter/X...")
                page.goto('https://twitter.com', timeout=60000)
                time.sleep(5)
                
                # Check login
                if 'login' in page.url or 'i/flow/login' in page.url:
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
                
                self.logger.info("Logged in to Twitter")
                time.sleep(3)
                
                # Click "Post" or "Tweet" button (home page)
                self.logger.info("Opening tweet composer...")
                
                # Navigate to home if not already
                if 'home' not in page.url:
                    page.goto('https://twitter.com/home', timeout=30000)
                    time.sleep(3)
                
                # Find tweet box
                tweet_box = page.query_selector('[data-testid="tweetTextarea_0"]')
                if not tweet_box:
                    # Try alternative
                    tweet_box = page.query_selector('[placeholder*="Tweet"]')
                
                if tweet_box:
                    tweet_box.click()
                    time.sleep(1)
                else:
                    self.logger.warning("Tweet box not found, trying Post button")
                    post_btn = page.query_selector('[data-testid="SideNav_NewTweet"]')
                    if post_btn:
                        post_btn.click()
                        time.sleep(2)
                
                # Upload image if provided
                if image_path and Path(image_path).exists():
                    self.logger.info(f"Uploading image: {image_path}")
                    
                    # Click media button
                    media_btn = page.query_selector('[data-testid="toolBarImages"]')
                    if media_btn:
                        media_btn.click()
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
                        self.logger.warning("Could not find media button")
                
                # Enter tweet content
                self.logger.info("Entering tweet content...")
                
                tweet_input = page.query_selector('[data-testid="tweetTextarea_0"]')
                if tweet_input:
                    # Clear and fill
                    tweet_input.fill('')
                    tweet_input.fill(content)
                    self.logger.info("✓ Tweet content entered")
                else:
                    self.logger.warning("Could not find tweet input, using keyboard")
                    page.keyboard.type(content, delay=50)
                
                time.sleep(2)
                
                # Check character count
                char_limit_indicator = page.query_selector('[data-testid="postCharacterCount"]')
                if char_limit_indicator:
                    char_text = char_limit_indicator.inner_text()
                    self.logger.info(f"Character count: {char_text}")
                
                # Ready to post
                self.logger.info("="*60)
                self.logger.info("TWEET READY!")
                self.logger.info("="*60)
                self.logger.info("Please click the 'Post' button manually")
                self.logger.info("Waiting 90 seconds...")
                
                # Wait for user to click Post
                posted = False
                for i in range(90):
                    try:
                        # Check if composer is gone
                        composer = page.query_selector('[data-testid="tweetTextarea_0"]')
                        if not composer:
                            self.logger.info("✓ Tweet submitted!")
                            posted = True
                            break
                    except:
                        pass
                    time.sleep(1)
                
                if not posted:
                    self.logger.warning("Timeout - tweet may not have been submitted")
                
                # Screenshot
                screenshot = self.vault_path / 'twitter_post_screenshot.png'
                page.screenshot(path=str(screenshot))
                self.logger.info(f"Screenshot: {screenshot}")
                
                browser.close()
                return posted
                
        except Exception as e:
            self.logger.error(f"Error posting to Twitter: {e}")
            return False

    def process_queue(self) -> int:
        """Process approved tweets"""
        count = 0
        
        for filepath in self.approved_folder.glob('TWITTER_TWEET_*.md'):
            content = filepath.read_text()
            
            # Extract content and image
            lines = content.split('\n')
            tweet_content = []
            image_path = None
            in_content = False
            
            for line in lines:
                if '## Tweet Content' in line:
                    in_content = True
                    continue
                elif in_content and line.startswith('**Image:**'):
                    image_path = line.split(':', 1)[1].strip()
                    if image_path == 'none':
                        image_path = None
                elif in_content and line.startswith('---'):
                    break
                elif in_content and line.strip():
                    tweet_content.append(line)
            
            tweet_text = '\n'.join(tweet_content).strip()
            
            if tweet_text:
                self.logger.info(f"Processing: {filepath.name}")
                
                # Check character count
                if len(tweet_text) > 280:
                    self.logger.warning(f"Tweet is {len(tweet_text)} characters (limit: 280)")
                    self.logger.info("Consider using a thread for longer content")
                
                success = self._post_tweet(tweet_text, image_path)
                
                if success:
                    filepath.rename(self.done_folder / filepath.name)
                    count += 1
                    self.logger.info("✓ Tweet posted successfully")
                else:
                    self.logger.error("✗ Failed to post")
        
        return count


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Twitter/X Poster')
    parser.add_argument('--vault-path', default=str(Path(__file__).parent.parent.absolute()))
    parser.add_argument('--content', type=str, help='Tweet content (or file path)')
    parser.add_argument('--image', type=str, help='Image path (optional)')
    parser.add_argument('--session-path', type=str, help='Twitter session path')
    parser.add_argument('--process-queue', action='store_true', help='Process approved queue')
    parser.add_argument('--verbose', '-v', action='store_true')
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    poster = TwitterPoster(vault_path=args.vault_path, session_path=args.session_path)
    
    if args.content:
        # If content is a file, read it
        if Path(args.content).exists():
            args.content = Path(args.content).read_text()
        
        poster.post_tweet(args.content, args.image, wait_for_approval=True)
    elif args.process_queue:
        count = poster.process_queue()
        print(f"Posted {count} tweet(s)")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
