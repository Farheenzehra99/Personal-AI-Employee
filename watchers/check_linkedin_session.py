#!/usr/bin/env python3
"""
Test LinkedIn session in headless mode
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        '/mnt/d/personal-ai-employee/.linkedin_session',
        headless=True,
        viewport={'width': 1280, 'height': 720}
    )
    
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    print("Navigating to LinkedIn...")
    page.goto('https://www.linkedin.com', timeout=60000)
    time.sleep(5)
    
    # Get page title
    title = page.title()
    print(f"Page title: {title}")
    
    # Get page URL
    url = page.url
    print(f"Page URL: {url}")
    
    # Check for login indicators
    try:
        # Check for feed (indicates logged in)
        feed_selector = page.query_selector('[data-control-name="feed"]')
        if feed_selector:
            print("✓ Logged in (feed detected)")
        else:
            print("✗ Feed not found")
    except:
        print("Could not check feed")
    
    try:
        # Check for login button (indicates NOT logged in)
        login_btn = page.query_selector('input[type="email"]')
        if login_btn:
            print("✗ Login page detected - NOT logged in")
        else:
            print("✓ No login form found")
    except:
        pass
    
    # Save cookies to check
    cookies = browser.context.cookies()
    print(f"\nCookies count: {len(cookies)}")
    
    # Check for LinkedIn cookies
    linkedin_cookies = [c for c in cookies if 'linkedin' in c.get('domain', '')]
    print(f"LinkedIn cookies: {len(linkedin_cookies)}")
    
    if linkedin_cookies:
        print("\nKey cookies:")
        for c in linkedin_cookies[:5]:
            print(f"  - {c.get('name')}: {c.get('value')[:50]}...")
    
    browser.close()
    print("\nTest complete!")
