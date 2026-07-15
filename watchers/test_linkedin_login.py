#!/usr/bin/env python3
"""
Debug script to test LinkedIn session
"""

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        '/mnt/d/personal-ai-employee/.linkedin_session',
        headless=False,  # Visible browser
        viewport={'width': 1280, 'height': 720}
    )
    
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    print("Navigating to LinkedIn... Check the browser window")
    page.goto('https://www.linkedin.com', timeout=60000)
    
    print("Waiting 30 seconds for you to verify login...")
    time.sleep(30)
    
    # Take screenshot
    page.screenshot(path='linkedin_test.png')
    print("Screenshot saved as linkedin_test.png")
    
    print("Browser will close in 5 seconds...")
    time.sleep(5)
    browser.close()
