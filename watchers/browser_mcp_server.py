#!/usr/bin/env python3
"""
Browser MCP Server - Web automation via Playwright
Model Context Protocol server for browser operations
"""

import os
import sys
import logging
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not installed")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BrowserMCP')


class BrowserMCP:
    """Browser MCP Server for web automation"""
    
    def __init__(self, headless: bool = True):
        """Initialize Browser MCP"""
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

    def launch(self):
        """Launch browser"""
        if not PLAYWRIGHT_AVAILABLE:
            return {'success': False, 'error': 'Playwright not installed'}
        
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            self.context = self.browser.new_context(
                viewport={'width': 1280, 'height': 720}
            )
            self.page = self.context.new_page()
            
            # Hide automation flags
            self.page.add_init_script('''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            ''')
            
            logger.info("Browser launched")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
            return {'success': False, 'error': str(e)}

    def navigate(self, url: str, timeout: int = 30000) -> Dict:
        """Navigate to URL"""
        if not self.page:
            self.launch()
        
        try:
            self.page.goto(url, timeout=timeout)
            logger.info(f"Navigated to: {url}")
            
            return {
                'success': True,
                'url': self.page.url,
                'title': self.page.title()
            }
            
        except Exception as e:
            logger.error(f"Failed to navigate: {e}")
            return {'success': False, 'error': str(e)}

    def click(self, selector: str) -> Dict:
        """Click an element"""
        if not self.page:
            return {'success': False, 'error': 'Browser not launched'}
        
        try:
            self.page.click(selector)
            logger.info(f"Clicked: {selector}")
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Failed to click: {e}")
            return {'success': False, 'error': str(e)}

    def fill(self, selector: str, value: str) -> Dict:
        """Fill an input field"""
        if not self.page:
            return {'success': False, 'error': 'Browser not launched'}
        
        try:
            self.page.fill(selector, value)
            logger.info(f"Filled {selector} with: {value}")
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Failed to fill: {e}")
            return {'success': False, 'error': str(e)}

    def screenshot(self, path: str = None) -> Dict:
        """Take screenshot"""
        if not self.page:
            return {'success': False, 'error': 'Browser not launched'}
        
        try:
            if not path:
                path = f'/tmp/browser_screenshot_{int(time.time())}.png'
            
            self.page.screenshot(path=path)
            logger.info(f"Screenshot saved: {path}")
            
            return {
                'success': True,
                'path': path
            }
            
        except Exception as e:
            logger.error(f"Failed to screenshot: {e}")
            return {'success': False, 'error': str(e)}

    def evaluate(self, script: str) -> Dict:
        """Execute JavaScript"""
        if not self.page:
            return {'success': False, 'error': 'Browser not launched'}
        
        try:
            result = self.page.evaluate(script)
            
            return {
                'success': True,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Failed to evaluate: {e}")
            return {'success': False, 'error': str(e)}

    def content(self) -> Dict:
        """Get page content"""
        if not self.page:
            return {'success': False, 'error': 'Browser not launched'}
        
        try:
            html = self.page.content()
            text = self.page.inner_text('body')
            
            return {
                'success': True,
                'html': html[:10000],  # Limit size
                'text': text[:5000]
            }
            
        except Exception as e:
            logger.error(f"Failed to get content: {e}")
            return {'success': False, 'error': str(e)}

    def query_selector(self, selector: str) -> Dict:
        """Find element"""
        if not self.page:
            return {'success': False, 'error': 'Browser not launched'}
        
        try:
            element = self.page.query_selector(selector)
            
            if element:
                return {
                    'success': True,
                    'found': True,
                    'text': element.inner_text()[:500]
                }
            else:
                return {
                    'success': True,
                    'found': False
                }
            
        except Exception as e:
            logger.error(f"Failed to query: {e}")
            return {'success': False, 'error': str(e)}

    def close(self):
        """Close browser"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            
            logger.info("Browser closed")
            
        except Exception as e:
            logger.error(f"Failed to close: {e}")


# MCP Protocol Handlers

def mcp_list_tools():
    """List available MCP tools"""
    return {
        'tools': [
            {
                'name': 'browser_navigate',
                'description': 'Navigate to a URL',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'url': {'type': 'string', 'description': 'URL to navigate to'},
                        'timeout': {'type': 'integer', 'description': 'Timeout in ms'}
                    },
                    'required': ['url']
                }
            },
            {
                'name': 'browser_click',
                'description': 'Click an element',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'selector': {'type': 'string', 'description': 'CSS selector'}
                    },
                    'required': ['selector']
                }
            },
            {
                'name': 'browser_fill',
                'description': 'Fill an input field',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'selector': {'type': 'string', 'description': 'CSS selector'},
                        'value': {'type': 'string', 'description': 'Value to fill'}
                    },
                    'required': ['selector', 'value']
                }
            },
            {
                'name': 'browser_screenshot',
                'description': 'Take a screenshot',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'path': {'type': 'string', 'description': 'Save path'}
                    }
                }
            },
            {
                'name': 'browser_evaluate',
                'description': 'Execute JavaScript',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'script': {'type': 'string', 'description': 'JavaScript code'}
                    },
                    'required': ['script']
                }
            },
            {
                'name': 'browser_content',
                'description': 'Get page content',
                'inputSchema': {
                    'type': 'object',
                    'properties': {}
                }
            }
        ]
    }


def mcp_call_tool(name: str, args: Dict, browser_mcp: BrowserMCP) -> Dict:
    """Call an MCP tool"""
    if name == 'browser_navigate':
        return browser_mcp.navigate(args['url'], args.get('timeout', 30000))
    elif name == 'browser_click':
        return browser_mcp.click(args['selector'])
    elif name == 'browser_fill':
        return browser_mcp.fill(args['selector'], args['value'])
    elif name == 'browser_screenshot':
        return browser_mcp.screenshot(args.get('path'))
    elif name == 'browser_evaluate':
        return browser_mcp.evaluate(args['script'])
    elif name == 'browser_content':
        return browser_mcp.content()
    else:
        return {'error': f'Unknown tool: {name}'}


def main():
    """Run Browser MCP Server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Browser MCP Server')
    parser.add_argument('--test', action='store_true', help='Test browser')
    parser.add_argument('--url', type=str, help='Test URL')
    
    args = parser.parse_args()
    
    browser = BrowserMCP(headless=False)
    
    if args.test:
        print("\n" + "="*60)
        print("BROWSER MCP CONNECTION TEST")
        print("="*60)
        
        result = browser.launch()
        if result['success']:
            print("✓ Browser launched successfully")
            
            # Test navigate
            if args.url:
                nav_result = browser.navigate(args.url)
                if nav_result['success']:
                    print(f"✓ Navigated to: {args.url}")
                    print(f"  Title: {nav_result['title']}")
            
            # Test screenshot
            screenshot_result = browser.screenshot()
            if screenshot_result['success']:
                print(f"✓ Screenshot saved: {screenshot_result['path']}")
            
            browser.close()
        else:
            print(f"✗ Failed: {result['error']}")
        
        print("="*60)


if __name__ == "__main__":
    main()
