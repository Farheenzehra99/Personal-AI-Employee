#!/usr/bin/env python3
"""
LinkedIn Login Helper - Opens LinkedIn for manual login
Usage: python watchers/linkedin_login.py --session-path .linkedin_session_account2
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
    
    parser = argparse.ArgumentParser(description='LinkedIn Login Helper')
    parser.add_argument('--session-path', default='.linkedin_session',
                        help='Path to store session')
    parser.add_argument('--timeout', type=int, default=300,
                        help='Timeout in seconds (default: 5 minutes)')
    
    args = parser.parse_args()
    
    session_path = Path(args.session_path)
    session_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("LINKEDIN LOGIN HELPER")
    print("=" * 60)
    print(f"Session will be saved to: {session_path.absolute()}")
    print(f"Browser will stay open for {args.timeout} seconds")
    print("")
    print("INSTRUCTIONS:")
    print("1. Browser will open")
    print("2. Login to LinkedIn with your account")
    print("3. Wait until you see your feed")
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
        
        print("Opening LinkedIn...")
        page.goto('https://www.linkedin.com', timeout=60000)
        
        print(f"Waiting {args.timeout} seconds for login...")
        print("(Scan QR code or enter credentials)")
        
        logged_in = False
        for i in range(args.timeout):
            current_url = page.url
            
            # Check if logged in
            if 'feed' in current_url or 'mynetwork' in current_url:
                print("")
                print("✓ Login successful!")
                print(f"  Logged in at: {current_url}")
                logged_in = True
                # Wait a bit more to ensure session is saved
                time.sleep(5)
                break
            
            # Show progress every 10 seconds
            if (i + 1) % 10 == 0:
                print(f"  Waiting... {i + 1}/{args.timeout} seconds")
            
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
