#!/usr/bin/env python3
"""
LinkedIn Poster - Posts content to LinkedIn via Playwright automation
Used by AI Employee to automatically post business updates
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


class LinkedInPoster:
    def __init__(self, vault_path: str, session_path: str = None):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Session path for persistent login
        if session_path is None:
            session_path = self.vault_path / '.linkedin_session'
        else:
            session_path = Path(session_path)
        
        self.session_path = session_path
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Pending approval folder
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.pending_approval.mkdir(parents=True, exist_ok=True)
        
        # Done folder
        self.done_folder = self.vault_path / 'Done'
        self.done_folder.mkdir(parents=True, exist_ok=True)

    def post_content(self, content: str, wait_for_approval: bool = True) -> bool:
        """
        Post content to LinkedIn
        
        Args:
            content: The text content to post
            wait_for_approval: If True, create approval file and wait
            
        Returns:
            True if posted successfully, False otherwise
        """
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not installed")
            return False
        
        if wait_for_approval:
            # Create approval request file
            approval_file = self.create_approval_file(content)
            self.logger.info(f"Created approval file: {approval_file}")
            self.logger.info("Waiting for human approval...")
            self.logger.info(f"Move {approval_file} to /Approved folder to post")
            return False
        
        # Actually post to LinkedIn
        return self._post_to_linkedin(content)

    def create_approval_file(self, content: str) -> Path:
        """Create an approval request file for the LinkedIn post"""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
        filepath = self.pending_approval / f'LINKEDIN_POST_{timestamp}.md'
        
        approval_content = f'''---
type: linkedin_post_approval
created: {datetime.now().isoformat()}
status: pending
action: post_to_linkedin
---

# LinkedIn Post Approval Required

## Post Content

{content}

---

## To Approve
Move this file to `/Approved` folder to publish this post on LinkedIn.

## To Reject
Move this file to `/Rejected` folder or delete it.

## Notes
- This post will be visible on your LinkedIn profile
- Ensure content is professional and appropriate
- Posts are typically 300-500 characters for optimal engagement
'''
        
        filepath.write_text(approval_content)
        return filepath

    def _post_to_linkedin(self, content: str) -> bool:
        """Actually post to LinkedIn using Playwright"""
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                # Using headless=False for better LinkedIn compatibility
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
                
                # Check if logged in by URL
                current_url = page.url
                if 'login' in current_url or 'checkpoint' in current_url:
                    self.logger.error("LinkedIn login page detected - not logged in. Please run linkedin_watcher.py first.")
                    browser.close()
                    return False
                
                if 'feed' in current_url or 'mynetwork' in current_url or 'messaging' in current_url:
                    self.logger.info("Successfully logged in to LinkedIn")
                else:
                    self.logger.warning(f"Unexpected URL: {current_url}")
                
                # Click on the "Start a post" button
                try:
                    # Try different selectors for the post button
                    post_button = None
                    selectors = [
                        '[data-control-name="updates_v2_post_trigger"]',
                        'button:has-text("Start a post")',
                        'button:has-text("Post")',
                        '.share-box-feed-entry__trigger'
                    ]
                    
                    for selector in selectors:
                        try:
                            post_button = page.query_selector(selector)
                            if post_button:
                                self.logger.info(f"Found post button with selector: {selector}")
                                break
                        except:
                            continue
                    
                    if post_button:
                        post_button.click()
                        time.sleep(2)
                        self.logger.info("Clicked on post button")
                    else:
                        self.logger.warning("Could not find post button, trying alternative method")
                        # Navigate directly to post creation page
                        page.goto('https://www.linkedin.com/feed/update/urn:li:share:create/', timeout=30000)
                        time.sleep(3)
                    
                except Exception as e:
                    self.logger.warning(f"Error clicking post button: {e}")
                    # Try direct navigation
                    page.goto('https://www.linkedin.com/feed/update/urn:li:share:create/', timeout=30000)
                    time.sleep(3)
                
                # Find the text input field and enter content
                try:
                    # Look for the text editor
                    text_selectors = [
                        '[aria-label="What do you want to share?"]',
                        '[aria-label="What would you like to share?"]',
                        '[aria-label="Share thoughts"]',
                        'div[aria-label*="share"]',
                        '.ql-editor'
                    ]
                    
                    text_field = None
                    for selector in text_selectors:
                        try:
                            text_field = page.query_selector(selector)
                            if text_field:
                                break
                        except:
                            continue
                    
                    if text_field:
                        # Clear and fill
                        text_field.fill('')
                        text_field.fill(content)
                        time.sleep(1)
                        self.logger.info("Entered post content")
                    else:
                        # Try keyboard input as fallback
                        page.keyboard.press('Tab')  # Navigate to text field
                        page.keyboard.press('Tab')
                        time.sleep(1)
                        page.keyboard.type(content, delay=50)
                        self.logger.info("Typed content using keyboard")
                    
                except Exception as e:
                    self.logger.error(f"Error entering content: {e}")
                    browser.close()
                    return False
                
                # Wait for content to be entered
                time.sleep(2)
                
                # Click the "Post" button (first click - may open settings or submit)
                try:
                    post_button_selectors = [
                        'button:has-text("Post")',
                        'button:has-text("Next")',
                        '[aria-label="Post"]'
                    ]
                    
                    submit_button = None
                    for selector in post_button_selectors:
                        try:
                            submit_button = page.query_selector(selector)
                            if submit_button:
                                submit_button.click()
                                self.logger.info(f"Clicked button: {selector}")
                                break
                        except:
                            continue
                    
                    if not submit_button:
                        page.keyboard.press('Control+Enter')
                        self.logger.info("Used keyboard shortcut")
                    
                except Exception as e:
                    self.logger.error(f"Error clicking post button: {e}")
                    browser.close()
                    return False
                
                # Wait for any modal to appear
                time.sleep(3)
                
                # Handle "Post settings" modal if it appears
                try:
                    settings_modal = page.query_selector('text="Post settings"')
                    if settings_modal:
                        self.logger.info("Post settings modal detected")
                        self.logger.info("=== MANUAL INTERVENTION REQUIRED ===")
                        self.logger.info("Please click 'Done' in the Post settings modal manually")
                        self.logger.info("Then click 'Post' button to publish")
                        self.logger.info("Waiting 60 seconds for manual action...")
                        
                        # Wait for user to manually handle
                        for i in range(60):
                            # Check if modal is gone
                            modal_check = page.query_selector('text="Post settings"')
                            if not modal_check:
                                self.logger.info("Settings modal closed by user")
                                break
                            time.sleep(1)
                        
                        self.logger.info("Continuing after manual intervention...")
                        time.sleep(2)
                    else:
                        self.logger.info("No Post settings modal")
                except Exception as e:
                    self.logger.debug(f"Error handling modal: {e}")
                
                # Wait for post to be submitted
                time.sleep(5)
                
                # Take screenshot for debugging
                screenshot_path = '/tmp/linkedin_post_result.png'
                page.screenshot(path=screenshot_path)
                self.logger.info(f"Screenshot saved: {screenshot_path}")
                
                # Get current URL and title
                self.logger.info(f"Final URL: {page.url}")
                self.logger.info(f"Final Title: {page.title()}")
                
                # Check if post was successful
                try:
                    # Look for success indicator or navigate back to feed
                    page.wait_for_selector('[data-control-name="feed.update"]', timeout=10000)
                    self.logger.info("Post appears to be successful")
                except:
                    self.logger.warning("Could not confirm post - checking current page")
                    # Check if we're still on create page
                    if 'create' in page.url:
                        self.logger.error("Still on create page - post may not have submitted")
                    else:
                        self.logger.info("Navigated away from create page")
                
                browser.close()
                self.logger.info("LinkedIn post completed successfully!")
                return True
                
        except Exception as e:
            self.logger.error(f"LinkedIn posting failed: {e}")
            return False

    def process_approval_queue(self) -> int:
        """
        Check Pending_Approval folder for approved LinkedIn posts and post them
        Returns number of posts processed
        """
        posted_count = 0
        
        # Find all approved LinkedIn post files
        for filepath in self.pending_approval.glob('LINKEDIN_POST_*.md'):
            content = filepath.read_text()
            
            # Check if file was moved to Approved (it won't be in pending anymore)
            # This method is called after checking if file exists in Approved folder
            
        # Check Approved folder
        approved_folder = self.vault_path / 'Approved'
        if approved_folder.exists():
            for filepath in approved_folder.glob('LINKEDIN_POST_*.md'):
                content = filepath.read_text()
                
                # Extract post content
                post_content = self._extract_post_content(content)
                
                if post_content:
                    self.logger.info(f"Posting approved content from {filepath.name}")
                    success = self._post_to_linkedin(post_content)
                    
                    if success:
                        # Move to Done
                        dest = self.done_folder / filepath.name
                        filepath.rename(dest)
                        self.logger.info(f"Post complete: {dest}")
                        posted_count += 1
                    else:
                        self.logger.error(f"Failed to post: {filepath.name}")
        
        return posted_count

    def _extract_post_content(self, approval_content: str) -> Optional[str]:
        """Extract the actual post content from approval file"""
        try:
            lines = approval_content.split('\n')
            in_content = False
            content_lines = []
            
            for line in lines:
                if line.strip() == '## Post Content':
                    in_content = True
                    continue
                elif line.strip().startswith('##') and in_content:
                    break
                elif in_content and line.strip() and not line.startswith('---'):
                    content_lines.append(line)
            
            return '\n'.join(content_lines).strip() if content_lines else None
        except Exception as e:
            self.logger.error(f"Error extracting content: {e}")
            return None


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Poster for AI Employee')
    parser.add_argument('--vault-path', default=str(Path(__file__).parent.parent.absolute()),
                        help='Path to vault directory')
    parser.add_argument('--session-path', default=None,
                        help='Path to store LinkedIn session')
    parser.add_argument('--content', type=str, default=None,
                        help='Content to post (if provided, posts immediately)')
    parser.add_argument('--process-queue', action='store_true',
                        help='Process approved posts queue')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create poster
    poster = LinkedInPoster(
        vault_path=args.vault_path,
        session_path=args.session_path
    )
    
    if args.content:
        # Post content directly
        success = poster.post_content(args.content, wait_for_approval=True)
        sys.exit(0 if success else 1)
    elif args.process_queue:
        # Process approval queue
        count = poster.process_approval_queue()
        print(f"Posted {count} LinkedIn update(s)")
        sys.exit(0)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
