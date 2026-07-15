#!/usr/bin/env python3
"""
WhatsApp Login Helper - Opens WhatsApp Web for manual login
"""

from playwright.sync_api import sync_playwright
import time

print("Opening WhatsApp Web for login...")
print("Scan the QR code with your WhatsApp mobile app")
print("Waiting 120 seconds...")

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        '/mnt/d/personal-ai-employee/.whatsapp_session',
        headless=False,
        viewport={'width': 1280, 'height': 720}
    )
    
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto('https://web.whatsapp.com', timeout=60000)
    
    # Wait for user to scan QR and login
    for i in range(120):
        # Check if chat list appears (indicates login)
        chat_list = page.query_selector('[data-testid="chat-list"]')
        if chat_list:
            print("\n✓ Login detected!")
            print("Session saved. You can close the browser.")
            time.sleep(5)
            break
        time.sleep(1)
    else:
        print("\nTimeout - login not completed")
    
    browser.close()

print("Done!")
