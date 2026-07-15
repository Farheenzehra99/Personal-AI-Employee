#!/usr/bin/env python3
"""
LinkedIn Post with Image - Create and post with colorful AI images
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def create_post_with_image(content: str, image_path: str, session_path: str = None) -> bool:
    """Post to LinkedIn with an image"""
    
    if not PLAYWRIGHT_AVAILABLE:
        print("Playwright not installed")
        return False
    
    if session_path is None:
        session_path = Path(__file__).parent.parent / '.linkedin_session'
    else:
        session_path = Path(session_path)
    
    print(f"Using session: {session_path}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                session_path,
                headless=False,
                viewport={'width': 1280, 'height': 800}
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # Go to LinkedIn
            print("Opening LinkedIn...")
            page.goto('https://www.linkedin.com', timeout=60000)
            time.sleep(5)
            
            # Check if logged in
            current_url = page.url
            if 'login' in current_url:
                print("⚠ Not logged in. Waiting 60 seconds for login...")
                for i in range(60):
                    if 'feed' in page.url:
                        print("✓ Login detected!")
                        break
                    time.sleep(1)
            
            time.sleep(3)
            
            # Click "Start a post"
            print("Opening post creator...")
            post_btn = page.query_selector('button:has-text("Start a post")')
            if post_btn:
                post_btn.click()
                time.sleep(3)
            else:
                print("⚠ Post button not found, trying direct URL")
                page.goto('https://www.linkedin.com/feed/update/urn:li:share:create/', timeout=30000)
                time.sleep(3)
            
            # Upload image - LinkedIn uses media upload button
            print(f"Uploading image: {image_path}")
            
            # First click on media/photo button
            media_btn = page.query_selector('button[aria-label*="photo"], button[aria-label*="media"], button[aria-label*="image"]')
            if media_btn:
                media_btn.click()
                print("Clicked media button")
                time.sleep(2)
                
                # Now find the file input
                file_input = page.query_selector('input[type="file"]')
                if file_input:
                    file_input.set_input_files(str(image_path))
                    print("✓ Image uploaded")
                    time.sleep(3)
                else:
                    print("⚠ Could not find file input")
            else:
                print("⚠ Could not find media button, trying direct file input")
                # Try finding hidden file input
                file_inputs = page.query_selector_all('input[type="file"]')
                if file_inputs:
                    file_inputs[0].set_input_files(str(image_path))
                    print("✓ Image uploaded via direct input")
                    time.sleep(3)
                else:
                    print("⚠ No file input found - you may need to upload image manually")
            
            # Enter text
            print("Entering content...")
            text_field = page.query_selector('.ql-editor')
            if text_field:
                text_field.fill(content)
                print("✓ Content added")
            
            time.sleep(2)
            
            # Ready to post
            print("\n" + "="*60)
            print("POST READY!")
            print("="*60)
            print("Image and content are loaded in LinkedIn")
            print("Please click the 'Post' button manually to publish")
            print("="*60)
            
            # Wait for user to click Post
            for i in range(90):
                modal = page.query_selector('.ql-editor')
                if not modal:
                    print("✓ Post submitted!")
                    break
                time.sleep(1)
            
            time.sleep(3)
            browser.close()
            return True
            
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    import argparse
    import time
    
    parser = argparse.ArgumentParser(description='LinkedIn Post with Image')
    parser.add_argument('--content', type=str, required=True, help='Post content (or path to file)')
    parser.add_argument('--image', type=str, help='Path to image file')
    parser.add_argument('--session-path', type=str, help='LinkedIn session path')
    
    args = parser.parse_args()
    
    # If content is a file path, read it
    if Path(args.content).exists():
        args.content = Path(args.content).read_text()
    
    # Default image
    if not args.image:
        args.image = '/mnt/d/personal-ai-employee/linkedin_images/ai_agents.png'
    
    print("="*60)
    print("LINKEDIN POST WITH IMAGE")
    print("="*60)
    print(f"Content: {args.content[:100]}...")
    print(f"Image: {args.image}")
    print("="*60)
    
    success = create_post_with_image(args.content, args.image, args.session_path)
    
    if success:
        print("\n✓ Post process completed!")
    else:
        print("\n✗ Post failed")
        sys.exit(1)
