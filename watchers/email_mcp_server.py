#!/usr/bin/env python3
"""
Email MCP Server - Send/Receive emails via Gmail API
Model Context Protocol server for email operations
"""

import os
import sys
import logging
import json
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    logging.warning("Google API libraries not installed")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EmailMCP')


class EmailMCP:
    """Email MCP Server for Gmail"""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    
    def __init__(self, credentials_path: str = None, token_path: str = None):
        """Initialize Email MCP"""
        self.credentials_path = credentials_path or Path(__file__).parent.parent / 'gmail_credentials.json'
        self.token_path = token_path or Path(__file__).parent.parent / 'token.json'
        self.service = None
        
        if GMAIL_AVAILABLE:
            self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API"""
        try:
            creds = None
            
            # Load existing token
            if self.token_path.exists():
                creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save token
                self.token_path.write_text(creds.to_json())
            
            # Build service
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Authenticated with Gmail API")
            
        except Exception as e:
            logger.error(f"Gmail authentication failed: {e}")

    def send_email(self, to: str, subject: str, body: str, 
                   cc: str = None, attachments: List[str] = None) -> Dict:
        """Send an email"""
        if not self.service:
            return {'success': False, 'error': 'Not authenticated'}
        
        try:
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.base import MIMEBase
            from email import encoders
            
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            message['from'] = 'me'
            
            if cc:
                message['cc'] = cc
            
            # Add body
            message.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for filepath in attachments:
                    if Path(filepath).exists():
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(Path(filepath).read_bytes())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename={Path(filepath).name}'
                        )
                        message.attach(part)
            
            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"Email sent to {to}: {subject}")
            return {
                'success': True,
                'message_id': sent_message['id'],
                'thread_id': sent_message['threadId']
            }
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {'success': False, 'error': str(e)}

    def read_emails(self, query: str = 'is:unread', limit: int = 10) -> List[Dict]:
        """Read emails matching query"""
        if not self.service:
            return []
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=limit
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                email = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Extract headers
                headers = {h['name']: h['value'] for h in email['payload']['headers']}
                
                # Get body
                body = ''
                if 'parts' in email['payload']:
                    for part in email['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            body = base64.urlsafe_b64decode(part['body']['data']).decode()
                            break
                
                emails.append({
                    'id': email['id'],
                    'thread_id': email['threadId'],
                    'from': headers.get('From', ''),
                    'to': headers.get('To', ''),
                    'subject': headers.get('Subject', ''),
                    'date': headers.get('Date', ''),
                    'snippet': email.get('snippet', ''),
                    'body': body,
                    'unread': 'UNREAD' in email.get('labelIds', [])
                })
            
            logger.info(f"Read {len(emails)} emails")
            return emails
            
        except Exception as e:
            logger.error(f"Failed to read emails: {e}")
            return []

    def mark_as_read(self, message_ids: List[str]) -> Dict:
        """Mark emails as read"""
        if not self.service:
            return {'success': False, 'error': 'Not authenticated'}
        
        try:
            for msg_id in message_ids:
                self.service.users().messages().modify(
                    userId='me',
                    id=msg_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
            
            logger.info(f"Marked {len(message_ids)} emails as read")
            return {'success': True, 'marked': len(message_ids)}
            
        except Exception as e:
            logger.error(f"Failed to mark as read: {e}")
            return {'success': False, 'error': str(e)}

    def draft_email(self, to: str, subject: str, body: str) -> Dict:
        """Create a draft email"""
        if not self.service:
            return {'success': False, 'error': 'Not authenticated'}
        
        try:
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            message['from'] = 'me'
            message.attach(MIMEText(body, 'plain'))
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw_message}}
            ).execute()
            
            logger.info(f"Draft created: {draft['id']}")
            return {'success': True, 'draft_id': draft['id']}
            
        except Exception as e:
            logger.error(f"Failed to create draft: {e}")
            return {'success': False, 'error': str(e)}


# MCP Protocol Handlers

def mcp_list_tools():
    """List available MCP tools"""
    return {
        'tools': [
            {
                'name': 'email_send',
                'description': 'Send an email via Gmail',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'to': {'type': 'string', 'description': 'Recipient email'},
                        'subject': {'type': 'string', 'description': 'Email subject'},
                        'body': {'type': 'string', 'description': 'Email body'},
                        'cc': {'type': 'string', 'description': 'CC recipients'},
                        'attachments': {'type': 'array', 'items': {'type': 'string'}}
                    },
                    'required': ['to', 'subject', 'body']
                }
            },
            {
                'name': 'email_read',
                'description': 'Read emails from Gmail',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'query': {'type': 'string', 'description': 'Gmail search query'},
                        'limit': {'type': 'integer', 'description': 'Max emails to return'}
                    }
                }
            },
            {
                'name': 'email_mark_read',
                'description': 'Mark emails as read',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'message_ids': {'type': 'array', 'items': {'type': 'string'}}
                    },
                    'required': ['message_ids']
                }
            },
            {
                'name': 'email_draft',
                'description': 'Create a draft email',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'to': {'type': 'string', 'description': 'Recipient email'},
                        'subject': {'type': 'string', 'description': 'Email subject'},
                        'body': {'type': 'string', 'description': 'Email body'}
                    },
                    'required': ['to', 'subject', 'body']
                }
            }
        ]
    }


def mcp_call_tool(name: str, args: Dict, email_mcp: EmailMCP) -> Dict:
    """Call an MCP tool"""
    if name == 'email_send':
        return email_mcp.send_email(
            to=args['to'],
            subject=args['subject'],
            body=args['body'],
            cc=args.get('cc'),
            attachments=args.get('attachments')
        )
    elif name == 'email_read':
        return {'emails': email_mcp.read_emails(
            query=args.get('query', 'is:unread'),
            limit=args.get('limit', 10)
        )}
    elif name == 'email_mark_read':
        return email_mcp.mark_as_read(args['message_ids'])
    elif name == 'email_draft':
        return email_mcp.draft_email(
            to=args['to'],
            subject=args['subject'],
            body=args['body']
        )
    else:
        return {'error': f'Unknown tool: {name}'}


def main():
    """Run Email MCP Server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Email MCP Server')
    parser.add_argument('--test', action='store_true', help='Test connection')
    parser.add_argument('--send', action='store_true', help='Send test email')
    parser.add_argument('--to', type=str, help='Recipient email')
    
    args = parser.parse_args()
    
    email = EmailMCP()
    
    if args.test:
        print("\n" + "="*60)
        print("EMAIL MCP CONNECTION TEST")
        print("="*60)
        
        if email.service:
            print("✓ Connected to Gmail API")
            
            # Test read emails
            emails = email.read_emails(limit=5)
            print(f"✓ Retrieved {len(emails)} emails")
            
            if emails:
                print(f"\nLatest email:")
                print(f"  From: {emails[0]['from']}")
                print(f"  Subject: {emails[0]['subject']}")
        else:
            print("✗ Failed to connect to Gmail API")
            print("  Run: python watchers/gmail_watcher.py --auth first")
        
        print("="*60)
    
    if args.send and args.to:
        result = email.send_email(
            to=args.to,
            subject="Test from AI Employee",
            body="This is a test email from the AI Employee Email MCP Server."
        )
        
        if result['success']:
            print(f"✓ Email sent! Message ID: {result['message_id']}")
        else:
            print(f"✗ Failed: {result['error']}")


if __name__ == "__main__":
    main()
