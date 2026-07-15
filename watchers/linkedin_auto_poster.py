#!/usr/bin/env python3
"""
LinkedIn Auto Poster - Clean implementation with manual assist
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Installing playwright...")
    os.system('pip install playwright && playwright install chromium')
    from playwright.sync_api import sync_playwright

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def post_to_linkedin(content: str, vault_path: str = None) -> bool:
    """Post to LinkedIn with browser automation"""
    
    if vault_path is None:
        vault_path = str(Path(__file__).parent.parent.absolute())
    
    vault = Path(vault_path)
    session_path = vault / '.linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Posting content ({len(content)} chars)...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                str(session_path),
                headless=False,
                viewport={'width': 1280, 'height': 800}
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # Step 1: Go to LinkedIn
            logger.info("Opening LinkedIn...")
            page.goto('https://www.linkedin.com/feed', timeout=60000)
            time.sleep(5)
            
            # Step 2: Check login
            if 'login' in page.url:
                logger.info("Waiting for login (120 seconds)...")
                for i in range(120):
                    if 'feed' in page.url:
                        logger.info("✓ Logged in!")
                        break
                    time.sleep(1)
                else:
                    logger.error("Login timeout")
                    browser.close()
                    return False
            
            # Step 3: Open post creator
            logger.info("Opening post creator...")
            try:
                page.click('button:has-text("Start a post")')
                time.sleep(3)
            except:
                logger.warning("Could not auto-open post creator")
            
            # Step 4: Enter content
            logger.info("Entering content...")
            try:
                text_field = page.query_selector('.ql-editor, [aria-label*="share"], [contenteditable="true"]')
                if text_field:
                    text_field.fill(content)
                    logger.info("✓ Content entered")
                    time.sleep(2)
            except Exception as e:
                logger.error(f"Could not enter content: {e}")
                browser.close()
                return False
            
            # Step 5: Click Post button
            logger.info("Clicking Post button...")
            try:
                page.click('button:has-text("Post")', force=True)
                time.sleep(2)
            except:
                pass
            
            # Step 6: Handle settings modal
            logger.info("Handling settings modal...")
            settings_closed = False
            
            for i in range(10):
                settings = page.query_selector('text="Post settings"')
                if not settings:
                    logger.info("✓ Settings closed")
                    settings_closed = True
                    break
                
                # Try clicking Anyone to enable Done
                try:
                    page.click('text="Anyone"', force=True)
                    time.sleep(1)
                except:
                    pass
                
                # Try clicking Done
                try:
                    page.click('button:has-text("Done")', force=True)
                    logger.info("Clicked Done")
                    time.sleep(2)
                except:
                    pass
                
                # Try JS click
                try:
                    page.evaluate('''() => {
                        const btn = Array.from(document.querySelectorAll('button'))
                            .find(b => b.textContent.trim() === "Done");
                        if (btn) btn.click();
                    }''')
                    logger.info("JS clicked Done")
                    time.sleep(2)
                except:
                    pass
                
                time.sleep(1)
            
            if not settings_closed:
                logger.warning("Settings still open - waiting for manual action...")
                logger.info(">>> Please click 'Done' then 'Post' in the browser <<<")
                
                # Wait for manual completion
                for i in range(90):
                    modal = page.query_selector('div[role="dialog"]')
                    if not modal:
                        logger.info("✓ Modal closed by user!")
                        break
                    time.sleep(1)
            
            # Step 7: Click Post again if needed
            if settings_closed:
                logger.info("Clicking Post to submit...")
                try:
                    page.click('button:has-text("Post")', force=True)
                    logger.info("✓ Post button clicked")
                except:
                    pass
            
            # Step 8: Wait for submission
            logger.info("Waiting for post submission...")
            submitted = False
            
            for i in range(60):
                modal = page.query_selector('div[role="dialog"]')
                if not modal:
                    logger.info("✓ Post submitted!")
                    submitted = True
                    break
                time.sleep(1)
            
            # Screenshot
            screenshot = vault / 'linkedin_post_screenshot.png'
            page.screenshot(path=str(screenshot))
            logger.info(f"Screenshot: {screenshot}")
            
            browser.close()
            
            return submitted
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def process_approved_queue(vault_path: str = None):
    """Process approved posts from Approved folder"""
    
    if vault_path is None:
        vault_path = str(Path(__file__).parent.parent.absolute())
    
    vault = Path(vault_path)
    approved_folder = vault / 'Approved'
    done_folder = vault / 'Done'
    
    approved_folder.mkdir(parents=True, exist_ok=True)
    done_folder.mkdir(parents=True, exist_ok=True)
    
    count = 0
    
    for filepath in sorted(approved_folder.glob('LINKEDIN_POST_*.md')):
        logger.info(f"Processing: {filepath.name}")
        
        content = filepath.read_text()
        
        # Extract post content
        lines = content.split('\n')
        in_content = False
        post_lines = []
        
        for line in lines:
            if '## Post Content' in line or '## Drafted Post' in line:
                in_content = True
                continue
            elif in_content and line.startswith('##'):
                break
            elif in_content:
                post_lines.append(line)
        
        post_content = '\n'.join(post_lines).strip()
        
        if not post_content:
            logger.warning("No content found")
            continue
        
        # Post
        success = post_to_linkedin(post_content)
        
        if success:
            # Add post info
            timestamp = datetime.now().isoformat()
            updated = content + f"\n\n## Posted\n- Time: {timestamp}\n"
            filepath.write_text(updated)
            
            # Move to Done
            filepath.rename(done_folder / filepath.name)
            logger.info(f"✓ Moved to Done/")
            count += 1
        else:
            logger.error("✗ Failed to post")
    
    return count


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Auto Poster')
    parser.add_argument('--content', type=str, help='Post content')
    parser.add_argument('--process-queue', action='store_true', help='Process approved queue')
    parser.add_argument('--vault-path', default=str(Path(__file__).parent.parent.absolute()))
    parser.add_argument('--verbose', '-v', action='store_true')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.content:
        # Create approval file
        vault = Path(args.vault_path)
        pending = vault / 'Pending_Approval'
        pending.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
        filepath = pending / f'LINKEDIN_POST_{timestamp}.md'
        
        filepath.write_text(f'''---
type: linkedin_post_approval
created: {datetime.now().isoformat()}
status: pending
action: linkedin_post
---

## Drafted Post

{args.content}

---

Move to /Approved to post.
''')
        
        print(f"Approval file created: {filepath}")
        print("Move to Approved/ folder to post")
        
    elif args.process_queue:
        count = process_approved_queue(args.vault_path)
        print(f"Posted {count} update(s)")
    
    else:
        parser.print_help()
