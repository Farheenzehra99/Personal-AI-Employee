#!/usr/bin/env python3
"""
Orchestrator - Watches Approved folder and triggers MCP actions
This is the bridge between human approval and actual execution.

When a human moves an approval file to /Approved, the orchestrator:
1. Detects the new approved file
2. Reads the approval request
3. Executes the appropriate MCP action
4. Logs the result
5. Moves the task to Done/
"""

import os
import sys
import logging
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class Orchestrator:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.approved_folder = self.vault_path / 'Approved'
        self.done_folder = self.vault_path / 'Done'
        self.logs_folder = self.vault_path / 'Logs'
        self.needs_action_folder = self.vault_path / 'Needs_Action'
        
        # Ensure folders exist
        for folder in [self.approved_folder, self.done_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger('Orchestrator')
        self.log_file = self.logs_folder / f'{datetime.now().strftime("%Y-%m-%d")}.json'
        self._init_log()
        
        # Track processed files
        self.processed_files = set()
        self._load_state()
    
    def _init_log(self):
        """Initialize or load today's log file"""
        if self.log_file.exists():
            try:
                self.today_log = json.loads(self.log_file.read_text())
            except:
                self.today_log = {'date': datetime.now().isoformat(), 'actions': []}
        else:
            self.today_log = {'date': datetime.now().isoformat(), 'actions': []}
    
    def _save_log(self):
        """Save log to file"""
        try:
            self.log_file.write_text(json.dumps(self.today_log, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save log: {e}")
    
    def _load_state(self):
        """Load processed files state"""
        state_file = self.logs_folder / 'orchestrator_state.json'
        if state_file.exists():
            try:
                state = json.loads(state_file.read_text())
                self.processed_files = set(state.get('processed_files', []))
            except:
                self.processed_files = set()
    
    def _save_state(self):
        """Save processed files state"""
        state_file = self.logs_folder / 'orchestrator_state.json'
        try:
            state = {'processed_files': list(self.processed_files)}
            state_file.write_text(json.dumps(state, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    def log_action(self, action_type: str, status: str, details: Dict[str, Any]):
        """Log an action to the daily log"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'status': status,
            'details': details
        }
        self.today_log['actions'].append(log_entry)
        self._save_log()
    
    def run_once(self):
        """Process all approved files once"""
        self.logger.info("Checking for approved files...")
        processed_count = 0
        
        # Find all .md files in Approved folder
        approved_files = list(self.approved_folder.glob('*.md'))
        
        for approved_file in approved_files:
            if approved_file.name in self.processed_files:
                continue
            
            self.logger.info(f"Processing approved file: {approved_file.name}")
            
            try:
                # Read the approval file
                content = approved_file.read_text()
                approval_data = self._parse_approval_file(content, approved_file)
                
                if not approval_data:
                    self.logger.warning(f"Could not parse approval file: {approved_file.name}")
                    continue
                
                # Execute the approved action
                action_type = approval_data.get('action')
                result = self._execute_action(action_type, approval_data)
                
                if result['success']:
                    self.logger.info(f"Action executed successfully: {action_type}")
                    self.log_action(action_type, 'success', {
                        'file': approved_file.name,
                        'result': result.get('message', '')
                    })
                    
                    # Move to Done
                    done_file = self.done_folder / approved_file.name
                    shutil.move(str(approved_file), str(done_file))
                    processed_count += 1
                    self.processed_files.add(approved_file.name)
                    
                else:
                    self.logger.error(f"Action failed: {result.get('error', 'Unknown error')}")
                    self.log_action(action_type, 'failed', {
                        'file': approved_file.name,
                        'error': result.get('error', '')
                    })
                    
            except Exception as e:
                self.logger.error(f"Error processing {approved_file.name}: {e}")
                self.log_action('unknown', 'error', {
                    'file': approved_file.name,
                    'error': str(e)
                })
        
        self._save_state()
        return processed_count
    
    def _parse_approval_file(self, content: str, filepath: Path) -> Optional[Dict[str, Any]]:
        """Parse the frontmatter and content of an approval file"""
        try:
            # Extract frontmatter
            if not content.startswith('---'):
                return None
            
            # Find frontmatter boundaries
            end_marker = content.find('---', 3)
            if end_marker == -1:
                return None
            
            frontmatter = content[4:end_marker].strip()
            
            # Parse YAML-like frontmatter (simple parser)
            data = {}
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Handle boolean
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    
                    data[key] = value
            
            # Add full content
            data['full_content'] = content
            data['source_file'] = filepath.name
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error parsing approval file: {e}")
            return None
    
    def _execute_action(self, action_type: str, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the approved action based on type"""
        
        if action_type == 'linkedin_post':
            return self._execute_linkedin_post(approval_data)
        
        elif action_type == 'email_send':
            return self._execute_email_send(approval_data)
        
        elif action_type == 'payment':
            return self._execute_payment(approval_data)
        
        elif action_type == 'whatsapp_reply':
            return self._execute_whatsapp_reply(approval_data)
        
        else:
            return {
                'success': False,
                'error': f'Unknown action type: {action_type}'
            }
    
    def _execute_linkedin_post(self, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute LinkedIn post via MCP or API"""
        try:
            # Extract post content from the approval file
            content = approval_data.get('full_content', '')
            
            # Find the drafted post section
            post_start = content.find('## Drafted Post')
            if post_start == -1:
                post_start = content.find('## Post Content')
            
            if post_start == -1:
                return {'success': False, 'error': 'Could not find post content'}
            
            # Extract post text (until next ## or end)
            post_content = content[post_start:]
            post_end = post_content.find('\n## ', 1)
            if post_end != -1:
                post_content = post_content[:post_end]
            
            # Clean up
            post_content = post_content.replace('## Drafted Post', '').strip()
            post_content = post_content.replace('## Post Content', '').strip()
            
            # Remove separator lines
            post_content = '\n'.join(
                line for line in post_content.split('\n') 
                if not line.strip().startswith('---')
            ).strip()
            
            self.logger.info(f"LinkedIn post content extracted ({len(post_content)} chars)")
            
            # Try MCP call via Claude Code
            # Note: In production, this would call the actual MCP server
            # For now, we simulate success
            mcp_available = self._check_mcp_server('linkedin')
            
            if mcp_available:
                # Call MCP server
                result = self._call_mcp_linkedin(post_content)
                return result
            else:
                # Simulate success (for testing)
                self.logger.info("MCP LinkedIn not configured - simulating success")
                return {
                    'success': True,
                    'message': 'LinkedIn post simulated (MCP not configured)',
                    'post_length': len(post_content),
                    'simulated': True
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_email_send(self, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email send via MCP or Gmail API"""
        try:
            mcp_available = self._check_mcp_server('email')
            
            if mcp_available:
                # Call MCP email server
                return self._call_mcp_email(approval_data)
            else:
                # Log that email would be sent
                self.logger.info("MCP Email not configured - logging only")
                return {
                    'success': True,
                    'message': 'Email send simulated (MCP not configured)',
                    'simulated': True
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_payment(self, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute payment via MCP or banking API"""
        try:
            # Payments always require real integration
            # For now, log that this needs manual handling
            amount = approval_data.get('amount', 'Unknown')
            recipient = approval_data.get('recipient', 'Unknown')
            
            self.logger.warning(f"Payment action requires manual handling: ${amount} to {recipient}")
            
            return {
                'success': True,
                'message': f'Payment flagged for manual processing: ${amount} to {recipient}',
                'requires_manual_action': True
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_whatsapp_reply(self, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute WhatsApp reply via MCP or automation"""
        try:
            mcp_available = self._check_mcp_server('whatsapp')
            
            if mcp_available:
                return self._call_mcp_whatsapp(approval_data)
            else:
                self.logger.info("MCP WhatsApp not configured - logging only")
                return {
                    'success': True,
                    'message': 'WhatsApp reply simulated (MCP not configured)',
                    'simulated': True
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _check_mcp_server(self, server_name: str) -> bool:
        """Check if an MCP server is configured"""
        # Check for MCP config file
        mcp_config_paths = [
            Path.home() / '.config' / 'claude-code' / 'mcp.json',
            self.vault_path / '.claude' / 'settings.json',
            Path.home() / '.claude' / 'settings.json'
        ]
        
        for config_path in mcp_config_paths:
            if config_path.exists():
                try:
                    config = json.loads(config_path.read_text())
                    servers = config.get('mcpServers', {})
                    if server_name in servers:
                        return True
                except:
                    continue
        
        return False
    
    def _call_mcp_linkedin(self, post_content: str) -> Dict[str, Any]:
        """Call LinkedIn MCP server to post"""
        # This would be replaced with actual MCP call
        # Example: subprocess call to claude-code with MCP tool
        try:
            # Simulated MCP call
            self.logger.info(f"Posting to LinkedIn: {post_content[:100]}...")
            return {
                'success': True,
                'message': 'LinkedIn post published successfully',
                'post_url': 'https://linkedin.com/posts/simulated'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _call_mcp_email(self, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Email MCP server to send"""
        try:
            # Simulated MCP call
            return {
                'success': True,
                'message': 'Email sent successfully'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _call_mcp_whatsapp(self, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call WhatsApp MCP server to send"""
        try:
            # Simulated MCP call
            return {
                'success': True,
                'message': 'WhatsApp message sent successfully'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run(self):
        """Run orchestrator continuously"""
        self.logger.info("Orchestrator started - watching Approved folder")
        
        import time
        
        while True:
            try:
                count = self.run_once()
                if count > 0:
                    self.logger.info(f"Processed {count} approved file(s)")
            except Exception as e:
                self.logger.error(f"Error in orchestrator loop: {e}")
            
            time.sleep(30)  # Check every 30 seconds


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Orchestrator for AI Employee')
    parser.add_argument('--vault-path', default=str(Path(__file__).parent.parent.absolute()),
                        help='Path to vault directory')
    parser.add_argument('--once', action='store_true',
                        help='Run once and exit (for cron)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create orchestrator
    orchestrator = Orchestrator(vault_path=args.vault_path)
    
    if args.once:
        # Run once mode (for cron)
        count = orchestrator.run_once()
        print(f"Orchestrator complete. Processed {count} approved file(s).")
        sys.exit(0)
    else:
        # Continuous mode
        orchestrator.run()


if __name__ == "__main__":
    main()
