#!/usr/bin/env python3
"""
LinkedIn Quick Poster - Manual assistance for posting
This script opens LinkedIn, you login once, then it helps you post quickly.
"""

import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)


def quick_post(content: str, vault_path: str):
    """Open LinkedIn and help post content"""
    
    vault = Path(vault_path)
    session_path = vault / '.linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*60)
    print("LINKEDIN QUICK POSTER")
    print("="*60)
    print(f"\nContent to post ({len(content)} chars):\n")
    print(content)
    print("\n" + "="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            str(session_path),
            headless=False,
            viewport={'width': 1280, 'height': 800}
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # Go to LinkedIn
        print("\nOpening LinkedIn...")
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        time.sleep(3)
        
        # Check if logged in
        if 'login' in page.url:
            print("\n⚠️  Please login to LinkedIn in the browser...")
            print("   (Session will be saved for next time)")
            for i in range(120):  # Wait 2 min max
                if 'feed' in page.url:
                    print("✓ Logged in!")
                    break
                time.sleep(1)
            else:
                print("Login timeout. Please run again.")
                browser.close()
                return
        
        print("\nOpening post creator...")
        
        # Click "Start a post"
        try:
            page.click('button:has-text("Start a post")')
            time.sleep(2)
        except:
            print("Could not open post creator. Please click 'Start a post' manually.")
            time.sleep(5)
        
        # Fill content
        print("Entering content...")
        try:
            text_field = page.query_selector('.ql-editor, [aria-label*="share"]')
            if text_field:
                text_field.fill(content)
                print("✓ Content entered")
        except Exception as e:
            print(f"Could not enter content: {e}")
            print("Please paste the content manually.")
        
        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("1. Click 'Post' button in the browser")
        print("2. If settings modal appears, click 'Done' then 'Post'")
        print("3. Script will detect when post is submitted")
        print("="*60)
        
        # Wait for post submission
        print("\nWaiting for post submission...")
        for i in range(120):  # Wait 2 min
            try:
                modal = page.query_selector('div[role="dialog"]')
                if not modal:
                    print("\n✓ Post submitted successfully!")
                    
                    # Take screenshot
                    screenshot = vault / 'linkedin_post_screenshot.png'
                    page.screenshot(path=str(screenshot))
                    print(f"Screenshot saved: {screenshot}")
                    
                    break
            except:
                pass
            time.sleep(1)
        else:
            print("\n⚠️  Timeout - please confirm post was submitted")
        
        browser.close()
    
    print("\n✓ Done!\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Quick Poster')
    parser.add_argument('--content', type=str, required=True, help='Post content')
    parser.add_argument('--vault-path', default=str(Path(__file__).parent.parent.absolute()))
    
    args = parser.parse_args()
    
    quick_post(args.content, args.vault_path)
