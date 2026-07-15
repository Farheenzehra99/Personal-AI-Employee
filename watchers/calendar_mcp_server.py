#!/usr/bin/env python3
"""
Calendar MCP Server - Google Calendar integration
Model Context Protocol server for calendar operations
"""

import os
import sys
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False
    logging.warning("Google API libraries not installed")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CalendarMCP')


class CalendarMCP:
    """Calendar MCP Server for Google Calendar"""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, credentials_path: str = None, token_path: str = None):
        """Initialize Calendar MCP"""
        self.credentials_path = credentials_path or Path(__file__).parent.parent / 'gmail_credentials.json'
        self.token_path = token_path or Path(__file__).parent.parent / 'token_calendar.json'
        self.service = None
        
        if CALENDAR_AVAILABLE:
            self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Calendar API"""
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
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("Authenticated with Google Calendar")
            
        except Exception as e:
            logger.error(f"Calendar authentication failed: {e}")

    def create_event(self, summary: str, start_time: str, end_time: str,
                    description: str = None, attendees: List[str] = None,
                    location: str = None) -> Dict:
        """Create a calendar event"""
        if not self.service:
            return {'success': False, 'error': 'Not authenticated'}
        
        try:
            event = {
                'summary': summary,
                'description': description or '',
                'location': location or '',
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                },
            }
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            logger.info(f"Event created: {created_event['id']}")
            return {
                'success': True,
                'event_id': created_event['id'],
                'html_link': created_event.get('htmlLink')
            }
            
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            return {'success': False, 'error': str(e)}

    def get_events(self, start_date: str = None, end_date: str = None, 
                   limit: int = 10) -> List[Dict]:
        """Get calendar events"""
        if not self.service:
            return []
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_date or now,
                timeMax=end_date or (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z',
                maxResults=limit,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', ''),
                    'description': event.get('description', ''),
                    'start': start,
                    'end': event['end'].get('dateTime', event['end'].get('date')),
                    'location': event.get('location', ''),
                    'attendees': event.get('attendees', [])
                })
            
            logger.info(f"Retrieved {len(formatted_events)} events")
            return formatted_events
            
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            return []

    def delete_event(self, event_id: str) -> Dict:
        """Delete a calendar event"""
        if not self.service:
            return {'success': False, 'error': 'Not authenticated'}
        
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            logger.info(f"Event deleted: {event_id}")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Failed to delete event: {e}")
            return {'success': False, 'error': str(e)}

    def update_event(self, event_id: str, **kwargs) -> Dict:
        """Update a calendar event"""
        if not self.service:
            return {'success': False, 'error': 'Not authenticated'}
        
        try:
            # Get existing event
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Update fields
            if 'summary' in kwargs:
                event['summary'] = kwargs['summary']
            if 'description' in kwargs:
                event['description'] = kwargs['description']
            if 'location' in kwargs:
                event['location'] = kwargs['location']
            if 'start_time' in kwargs:
                event['start']['dateTime'] = kwargs['start_time']
            if 'end_time' in kwargs:
                event['end']['dateTime'] = kwargs['end_time']
            
            # Save
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"Event updated: {event_id}")
            return {'success': True, 'event_id': updated_event['id']}
            
        except Exception as e:
            logger.error(f"Failed to update event: {e}")
            return {'success': False, 'error': str(e)}


# MCP Protocol Handlers

def mcp_list_tools():
    """List available MCP tools"""
    return {
        'tools': [
            {
                'name': 'calendar_create_event',
                'description': 'Create a calendar event',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'summary': {'type': 'string', 'description': 'Event title'},
                        'start_time': {'type': 'string', 'description': 'Start time (ISO 8601)'},
                        'end_time': {'type': 'string', 'description': 'End time (ISO 8601)'},
                        'description': {'type': 'string', 'description': 'Event description'},
                        'attendees': {'type': 'array', 'items': {'type': 'string'}},
                        'location': {'type': 'string', 'description': 'Event location'}
                    },
                    'required': ['summary', 'start_time', 'end_time']
                }
            },
            {
                'name': 'calendar_get_events',
                'description': 'Get calendar events',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'start_date': {'type': 'string', 'description': 'Start date (ISO 8601)'},
                        'end_date': {'type': 'string', 'description': 'End date (ISO 8601)'},
                        'limit': {'type': 'integer', 'description': 'Max events'}
                    }
                }
            },
            {
                'name': 'calendar_delete_event',
                'description': 'Delete a calendar event',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'event_id': {'type': 'string', 'description': 'Event ID'}
                    },
                    'required': ['event_id']
                }
            },
            {
                'name': 'calendar_update_event',
                'description': 'Update a calendar event',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'event_id': {'type': 'string', 'description': 'Event ID'},
                        'summary': {'type': 'string'},
                        'description': {'type': 'string'},
                        'start_time': {'type': 'string'},
                        'end_time': {'type': 'string'}
                    },
                    'required': ['event_id']
                }
            }
        ]
    }


def mcp_call_tool(name: str, args: Dict, calendar_mcp: CalendarMCP) -> Dict:
    """Call an MCP tool"""
    if name == 'calendar_create_event':
        return calendar_mcp.create_event(
            summary=args['summary'],
            start_time=args['start_time'],
            end_time=args['end_time'],
            description=args.get('description'),
            attendees=args.get('attendees'),
            location=args.get('location')
        )
    elif name == 'calendar_get_events':
        return {'events': calendar_mcp.get_events(
            start_date=args.get('start_date'),
            end_date=args.get('end_date'),
            limit=args.get('limit', 10)
        )}
    elif name == 'calendar_delete_event':
        return calendar_mcp.delete_event(args['event_id'])
    elif name == 'calendar_update_event':
        return calendar_mcp.update_event(args['event_id'], **args)
    else:
        return {'error': f'Unknown tool: {name}'}


def main():
    """Run Calendar MCP Server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Calendar MCP Server')
    parser.add_argument('--test', action='store_true', help='Test connection')
    parser.add_argument('--days', type=int, default=7, help='Days to show')
    
    args = parser.parse_args()
    
    calendar = CalendarMCP()
    
    if args.test:
        print("\n" + "="*60)
        print("CALENDAR MCP CONNECTION TEST")
        print("="*60)
        
        if calendar.service:
            print("✓ Connected to Google Calendar")
            
            # Get events
            events = calendar.get_events(limit=10)
            print(f"\n✓ Retrieved {len(events)} upcoming events")
            
            if events:
                print("\nNext 5 events:")
                for event in events[:5]:
                    print(f"  • {event['summary']}")
                    print(f"    {event['start']}")
        else:
            print("✗ Failed to connect to Google Calendar")
        
        print("="*60)


if __name__ == "__main__":
    main()
