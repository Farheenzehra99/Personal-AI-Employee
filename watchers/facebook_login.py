#!/usr/bin/env python3
"""
Facebook Login Helper - Opens Facebook for manual login
Usage: python watchers/facebook_login.py --session-path .facebook_session
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
    
    parser = argparse.ArgumentParser(description='Facebook Login Helper')
    parser.add_argument('--session-path', default='.facebook_session',
                        help='Path to store session')
    parser.add_argument('--timeout', type=int, default=600,
                        help='Timeout in seconds (default: 10 minutes)')
    
    args = parser.parse_args()
    
    session_path = Path(args.session_path)
    session_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("FACEBOOK LOGIN HELPER")
    print("=" * 60)
    print(f"Session will be saved to: {session_path.absolute()}")
    print(f"Browser will stay open for {args.timeout} seconds")
    print("")
    print("INSTRUCTIONS:")
    print("1. Browser will open")
    print("2. Login to Facebook with your account")
    print("3. Wait until you see your feed/home page")
    print("4. Browser will close automatically after login or timeout")
    print("=" * 60)
    print("")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,
            viewport={'width': 1280, 'height': 720}
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        print("Opening Facebook...")
        page.goto('https://www.facebook.com', timeout=60000)
        
        print(f"Waiting for login... (up to {args.timeout} seconds)")
        print("Login karo aur feed ka intezar karo...")
        print("")
        
        logged_in = False
        for i in range(args.timeout):
            current_url = page.url
            
            # Check if logged in
            if 'facebook.com' in current_url and 'login' not in current_url and 'checkpoint' not in current_url:
                # Wait a bit more to confirm
                time.sleep(3)
                if 'feed' in page.url or 'home' in page.url or 'watch' in page.url:
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
            print("  Try again with longer timeout: --timeout 600")
        
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
