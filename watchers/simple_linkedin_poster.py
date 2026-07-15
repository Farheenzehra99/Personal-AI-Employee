#!/usr/bin/env python3
"""
Simple LinkedIn Poster - Direct approach using LinkedIn share URL
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


class SimpleLinkedInPoster:
    def __init__(self, vault_path: str, session_path: str = None):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if session_path is None:
            session_path = self.vault_path / '.linkedin_session'
        else:
            session_path = Path(session_path)
        
        self.session_path = session_path
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved_folder = self.vault_path / 'Approved'
        self.done_folder = self.vault_path / 'Done'
        
        for folder in [self.pending_approval, self.approved_folder, self.done_folder]:
            folder.mkdir(parents=True, exist_ok=True)

    def post(self, content: str) -> bool:
        """Post to LinkedIn - returns True if successful"""
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not installed")
            return False
        
        try:
            with sync_playwright() as p:
                # Launch visible browser
                browser = p.chromium.launch_persistent_context(
                    self.session_path,
                    headless=False,
                    viewport={'width': 1280, 'height': 800}
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Step 1: Go to LinkedIn and ensure logged in
                self.logger.info("Opening LinkedIn...")
                page.goto('https://www.linkedin.com/feed', timeout=60000)
                time.sleep(5)
                
                # Check login
                if 'login' in page.url:
                    self.logger.error("Not logged in! Please login in the browser.")
                    self.logger.info("Waiting 120 seconds for manual login...")
                    for i in range(120):
                        if 'feed' in page.url:
                            self.logger.info("Login detected!")
                            break
                        time.sleep(1)
                    
                    if 'login' in page.url:
                        self.logger.error("Login timeout")
                        browser.close()
                        return False
                
                self.logger.info("Logged in successfully")
                time.sleep(2)
                
                # Step 2: Click "Start a post"
                self.logger.info("Opening post creator...")
                
                # Try multiple selectors
                post_triggers = [
                    'button:has-text("Start a post")',
                    '.share-box-feed-entry__trigger',
                    '[data-control-name="updates_v2_post_trigger"]',
                    'button[aria-label="Create a post"]'
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
                    # Fallback: Go directly to create URL
                    self.logger.info("Trying direct URL...")
                    page.goto('https://www.linkedin.com/feed/update/urn:li:share:create/', timeout=30000)
                
                time.sleep(3)
                
                # Step 3: Enter text
                self.logger.info("Entering post content...")
                
                # Try to find and fill the text field
                text_fields = [
                    '[aria-label="What do you want to share?"]',
                    '[aria-label="What would you like to share?"]',
                    '[aria-label*="share"]',
                    '.ql-editor',
                    'div[contenteditable="true"]'
                ]
                
                filled = False
                for selector in text_fields:
                    try:
                        field = page.query_selector(selector)
                        if field:
                            field.fill('')
                            field.fill(content)
                            self.logger.info(f"Filled text in: {selector}")
                            filled = True
                            break
                    except:
                        continue
                
                if not filled:
                    # Keyboard fallback
                    self.logger.info("Using keyboard input...")
                    page.keyboard.press('Tab')
                    page.keyboard.press('Tab')
                    page.keyboard.press('Tab')
                    time.sleep(1)
                    page.keyboard.type(content, delay=30)
                
                time.sleep(2)

                # Step 4: Submit post
                self.logger.info("=== Submitting post ===")
                
                post_submitted = False
                
                # Click Post button (opens settings modal)
                self.logger.info("Clicking Post button...")
                try:
                    post_btn = page.query_selector('button:has-text("Post")')
                    if post_btn:
                        post_btn.click(force=True)
                        time.sleep(3)
                except:
                    pass
                
                # Handle settings modal - try everything to close it
                self.logger.info("Handling settings modal...")
                done_clicked = False
                
                for attempt in range(20):
                    settings = page.query_selector('text="Post settings"')
                    if not settings:
                        self.logger.info("✓ Settings modal closed!")
                        done_clicked = True
                        break
                    
                    # Try ALL methods to click Done
                    try:
                        done_btn = page.query_selector('button:has-text("Done")')
                        if done_btn:
                            # Method 1: Regular click
                            done_btn.click()
                            time.sleep(1)
                            
                            # Method 2: Force click
                            done_btn.click(force=True)
                            time.sleep(1)
                            
                            # Method 3: JS dispatch
                            page.evaluate('''() => {
                                const btn = Array.from(document.querySelectorAll('button'))
                                    .find(b => b.textContent.trim() === "Done");
                                if (btn) {
                                    btn.click();
                                    btn.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                                }
                            }''')
                            time.sleep(2)
                            
                    except Exception as e:
                        self.logger.debug(f"Done click: {e}")
                    
                    time.sleep(1)
                
                if not done_clicked:
                    self.logger.warning("⚠ Settings modal still open - manual action needed")
                    self.logger.info(">>> PLEASE CLICK 'Done' AND THEN 'Post' IN THE BROWSER <<<")
                    # Wait for manual action
                    for i in range(90):
                        modal = page.query_selector('div[role="dialog"]')
                        if not modal:
                            self.logger.info("✓ Modal closed by user!")
                            post_submitted = True
                            break
                        time.sleep(1)
                else:
                    # Click Post to submit
                    self.logger.info("Clicking Post to submit...")
                    try:
                        post_btn = page.query_selector('button:has-text("Post")')
                        if post_btn:
                            post_btn.click(force=True)
                            self.logger.info("✓ Clicked Post button")
                    except:
                        pass
                    
                    # Wait for submission
                    for i in range(60):
                        try:
                            modal = page.query_selector('div[role="dialog"]')
                            if not modal:
                                self.logger.info("✓ Modal closed - post submitted!")
                                post_submitted = True
                                break
                        except:
                            pass
                        time.sleep(1)
                
                if not post_submitted:
                    self.logger.warning("⚠ Post may not have submitted")

                # Wait a bit more for post to process
                time.sleep(3)

                # Take screenshot
                screenshot = self.vault_path / 'linkedin_post_screenshot.png'
                page.screenshot(path=str(screenshot))
                self.logger.info(f"Screenshot saved: {screenshot}")

                browser.close()

                return post_submitted

        except Exception as e:
            self.logger.error(f"Error: {e}")
            return False

    def create_approval_file(self, content: str) -> Path:
        """Create approval file"""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
        filepath = self.pending_approval / f'LINKEDIN_POST_{timestamp}.md'
        
        content_text = f'''---
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
Move this file to `/Approved` folder.

## To Reject  
Delete this file.
'''
        filepath.write_text(content_text)
        return filepath

    def process_queue(self) -> int:
        """Process approved posts"""
        count = 0
        
        for filepath in self.approved_folder.glob('LINKEDIN_POST_*.md'):
            content = filepath.read_text()
            
            # Extract post content between "## Post Content" and "---"
            lines = content.split('\n')
            in_content = False
            post_lines = []
            
            for line in lines:
                if '## Post Content' in line:
                    in_content = True
                    continue
                elif in_content and line.startswith('---'):
                    break
                elif in_content:
                    post_lines.append(line)
            
            post_content = '\n'.join(post_lines).strip()
            
            if post_content:
                self.logger.info(f"Processing: {filepath.name}")
                success = self.post(post_content)
                
                if success:
                    filepath.rename(self.done_folder / filepath.name)
                    count += 1
                    self.logger.info("✓ Posted successfully")
                else:
                    self.logger.error("✗ Failed to post")
        
        return count


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple LinkedIn Poster')
    parser.add_argument('--vault-path', default=str(Path(__file__).parent.parent.absolute()))
    parser.add_argument('--content', type=str, help='Content to post')
    parser.add_argument('--process-queue', action='store_true', help='Process approved queue')
    parser.add_argument('--verbose', '-v', action='store_true')
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    poster = SimpleLinkedInPoster(vault_path=args.vault_path)
    
    if args.content:
        poster.create_approval_file(args.content)
        print(f"Approval file created. Move to /Approved to post.")
    elif args.process_queue:
        count = poster.process_queue()
        print(f"Posted {count} update(s)")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
