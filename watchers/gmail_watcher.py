#!/usr/bin/env python3
"""
Gmail Watcher - Monitors Gmail for new important emails
Creates .md files in Needs_Action/ folder for Claude to process
"""

import os
import sys
import logging
import base64
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from typing import List, Dict, Any

# Google API imports
# try:
from google.oauth2.credentials import Credentials
# from google.oauth2 import client_secrets
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

GOOGLE_AVAILABLE = True
# except ImportError:
#     GOOGLE_AVAILABLE = False

# Base watcher pattern
class BaseWatcher:
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        self.processed_ids = set()
        
    def run_once(self):
        """Run a single check (for cron mode)"""
        try:
            items = self.check_for_updates()
            for item in items:
                self.create_action_file(item)
            return len(items)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            return 0
    
    def run(self):
        """Run continuously"""
        import time
        self.logger.info(f'Starting {self.__class__.__name__}')
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                self.logger.error(f'Error: {e}')
            time.sleep(self.check_interval)


class GmailWatcher(BaseWatcher):
    # If modifying scopes, delete token.json
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, vault_path: str, credentials_path: str = None):
        super().__init__(vault_path, check_interval=120)
        
        # Default credentials path
        if credentials_path is None:
            credentials_path = self.vault_path / 'gmail_credentials.json'
        else:
            credentials_path = Path(credentials_path)
        
        self.credentials_path = credentials_path
        self.token_path = self.vault_path / 'token.json'
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API"""
        if not GOOGLE_AVAILABLE:
            self.logger.warning("Google API libraries not installed. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            return
        
        creds = None
        
        # Load token if exists
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
                self.logger.info("Loaded existing token")
            except Exception as e:
                self.logger.warning(f"Failed to load token: {e}")
                creds = None
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.logger.info("Refreshed expired token")
                except Exception as e:
                    self.logger.warning(f"Token refresh failed: {e}")
                    creds = None
            
            if not creds:
                if not self.credentials_path.exists():
                    self.logger.error(f"Credentials file not found: {self.credentials_path}")
                    self.logger.error("Please download Gmail credentials from Google Cloud Console")
                    return
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                    
                    # Save token
                    self.token_path.write_text(creds.to_json())
                    self.logger.info(f"Saved new token to {self.token_path}")
                except Exception as e:
                    self.logger.error(f"Authentication failed: {e}")
                    return
        
        # Build service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info("Gmail service initialized")
        except Exception as e:
            self.logger.error(f"Failed to build Gmail service: {e}")
            self.service = None
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """Check for new unread important emails"""
        if not self.service:
            return []
        
        try:
            # Search for unread emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread -category:promotions -category:social',
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            new_messages = []
            
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    new_messages.append(msg)
                    self.processed_ids.add(msg['id'])
            
            return new_messages
            
        except HttpError as error:
            self.logger.error(f'Gmail API error: {error}')
            return []
        except Exception as e:
            self.logger.error(f'Error checking Gmail: {e}')
            return []
    
    def create_action_file(self, message: Dict[str, Any]) -> Path:
        """Create a .md action file for the email"""
        try:
            # Get full message
            msg = self.service.users().messages().get(
                userId='me', 
                id=message['id'],
                format='full'
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}
            
            # Extract body
            body = self._extract_body(msg['payload'])
            
            # Determine priority
            priority = 'high' if headers.get('Importance', '').lower() == 'high' else 'normal'
            
            # Create content
            content = f'''---
type: email
from: {headers.get('From', 'Unknown')}
to: {headers.get('To', '')}
subject: {headers.get('Subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
gmail_id: {message['id']}
---

## Email Content

**From:** {headers.get('From', 'Unknown')}  
**To:** {headers.get('To', '')}  
**Subject:** {headers.get('Subject', 'No Subject')}  
**Date:** {headers.get('Date', '')}

---

{body}

---

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
- [ ] Flag for follow-up

## Notes
- Check if sender is known contact (Company_Handbook.md)
- Flag if mentions payment/invoice (requires approval)
'''
            
            # Sanitize filename
            subject = headers.get('Subject', 'No Subject')[:50]
            subject = "".join(c for c in subject if c.isalnum() or c in ' -_').strip()
            from_name = headers.get('From', 'Unknown').split('<')[0].strip()[:20]
            from_name = "".join(c for c in from_name if c.isalnum() or c in ' -_').strip()
            
            filepath = self.needs_action / f'EMAIL_{from_name}_{message["id"][:8]}.md'
            filepath.write_text(content)
            
            self.logger.info(f"Created action file: {filepath.name}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        body = ""
        
        # Check for multipart
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='replace')
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='replace')
                        # Simple HTML strip
                        import re
                        body += re.sub(r'<[^>]+>', '', html)
        elif 'body' in payload:
            if 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='replace')
        
        return body.strip() if body else "(No text content)"


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument('--vault-path', default=str(Path(__file__).parent.parent.absolute()),
                        help='Path to vault directory')
    parser.add_argument('--credentials', default=None,
                        help='Path to Gmail credentials JSON')
    parser.add_argument('--once', action='store_true',
                        help='Run once and exit (for cron)')
    parser.add_argument('--interval', type=int, default=120,
                        help='Check interval in seconds')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create watcher
    watcher = GmailWatcher(
        vault_path=args.vault_path,
        credentials_path=args.credentials
    )
    
    if args.once:
        # Run once mode (for cron)
        count = watcher.run_once()
        print(f"Gmail check complete. Found {count} new emails.")
        sys.exit(0)
    else:
        # Continuous mode
        watcher.run()


if __name__ == "__main__":
    main()
