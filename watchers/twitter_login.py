#!/usr/bin/env python3
"""
Twitter/X Login Helper - Opens Twitter for manual login
Usage: python watchers/twitter_login.py --session-path .twitter_session
"""

import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed. Run: pip install playwright")
    sys.exit(1)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Twitter/X Login Helper')
    parser.add_argument('--session-path', default='.twitter_session',
                        help='Path to store session')
    parser.add_argument('--timeout', type=int, default=600,
                        help='Timeout in seconds (default: 10 minutes)')
    
    args = parser.parse_args()
    
    session_path = Path(args.session_path)
    session_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("TWITTER/X LOGIN HELPER")
    print("=" * 60)
    print(f"Session will be saved to: {session_path.absolute()}")
    print(f"Browser will stay open for {args.timeout} seconds")
    print("")
    print("INSTRUCTIONS:")
    print("1. Browser will open")
    print("2. Login to Twitter/X with your account")
    print("3. Wait until you see your home feed")
    print("4. Browser will close automatically after login")
    print("=" * 60)
    print("")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # Hide automation flags
        page.add_init_script('''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        ''')
        
        print("Opening Twitter/X...")
        page.goto('https://twitter.com', timeout=60000)
        
        print(f"Waiting for login... (up to {args.timeout} seconds)")
        print("Login karo aur home feed ka intezar karo...")
        print("")
        
        logged_in = False
        for i in range(args.timeout):
            current_url = page.url
            
            # Check if logged in (home feed visible)
            if 'twitter.com' in current_url or 'x.com' in current_url:
                if 'login' not in current_url and 'i/flow/login' not in current_url:
                    # Wait a bit more to confirm
                    time.sleep(3)
                    # Check for home feed indicators
                    if 'home' in current_url or page.query_selector('[data-testid="primaryColumn"]'):
                        print("")
                        print("✓ Login successful!")
                        print(f"  Logged in at: {current_url}")
                        logged_in = True
                        # Wait to ensure session is saved
                        print("Saving session...")
                        time.sleep(5)
                        break
            
            # Show progress every 15 seconds
            if (i + 1) % 15 == 0:
                print(f"  Waiting... {i + 1}/{args.timeout} seconds (Browser open hai, login karo!)")
            
            time.sleep(1)
        
        if not logged_in:
            print("")
            print("✗ Login timeout - session may not be saved properly")
            print("  Try again with longer timeout: --timeout 900")
        
        browser.close()
    
    print("")
    print("=" * 60)
    if logged_in:
        print("✓ Session saved successfully!")
        print(f"  Use this session with: --session-path {session_path}")
    else:
        print("✗ Login not completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
