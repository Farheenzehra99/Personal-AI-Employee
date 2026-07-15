#!/usr/bin/env python3
"""
LinkedIn API Poster - Posts directly using LinkedIn API v2
Uses credentials from .env file
"""

import os
import sys
import json
import logging
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class LinkedInAPIPoster:
    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path) if vault_path else Path(__file__).parent.parent
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Load credentials from .env
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.company_urn = os.getenv('COMPANY_URN')
        
        # Validate credentials
        if not self.access_token:
            raise ValueError("LINKEDIN_ACCESS_TOKEN not found in .env file")
        
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        # Determine author (person or company)
        self.author = self._get_person_urn()
        
        if not self.author:
            raise ValueError("Could not determine author - check LINKEDIN_ACCESS_TOKEN permissions")
        
        if self.author.startswith('urn:li:member'):
            self.logger.info(f"Will post to person profile: {self.author}")
        elif self.author.startswith('urn:li:organization'):
            self.logger.info(f"Will post to company page: {self.author}")
        
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved_folder = self.vault_path / 'Approved'
        self.done_folder = self.vault_path / 'Done'
        
        for folder in [self.pending_approval, self.approved_folder, self.done_folder]:
            folder.mkdir(parents=True, exist_ok=True)

    def _get_person_urn(self) -> str:
        """Get the person URN from LinkedIn API"""
        try:
            response = requests.get(
                f"{self.base_url}/me",
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                return f"urn:li:member:{data['id']}"
            else:
                self.logger.warning(f"Could not fetch person URN: {response.status_code}")
                # Fallback to company URN if available
                if self.company_urn:
                    return self.company_urn
                return None
        except Exception as e:
            self.logger.warning(f"Error fetching person URN: {e}")
            # Fallback to company URN if available
            if self.company_urn:
                return self.company_urn
            return None

    def post(self, content: str, title: str = None) -> dict:
        """
        Post to LinkedIn using API v2
        Returns dict with success status and post URL
        """
        if not title:
            title = "AI Employee Update"
        
        # Create the post payload for LinkedIn API v2
        payload = {
            "author": self.author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        self.logger.info(f"Posting to LinkedIn as: {self.author}")
        self.logger.info(f"Content length: {len(content)} chars")
        
        try:
            # Make API request
            response = requests.post(
                f"{self.base_url}/ugcPosts",
                headers=self.headers,
                json=payload
            )
            
            self.logger.info(f"API Response Status: {response.status_code}")
            
            if response.status_code == 201:
                # Success! Get the post ID from response
                post_data = response.json()
                post_id = post_data.get('id', 'unknown')
                post_url = f"https://www.linkedin.com/feed/update/{post_id}"
                
                self.logger.info(f"✓ Post created successfully!")
                self.logger.info(f"Post ID: {post_id}")
                self.logger.info(f"Post URL: {post_url}")
                
                return {
                    'success': True,
                    'post_id': post_id,
                    'post_url': post_url,
                    'message': 'Post published successfully'
                }
            else:
                # Error - log details
                error_msg = f"API Error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data}"
                    self.logger.error(f"Error details: {error_data}")
                except:
                    error_msg += f" - {response.text}"
                
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_approval_file(self, content: str) -> Path:
        """Create approval file for manual review"""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
        filepath = self.pending_approval / f'LINKEDIN_POST_{timestamp}.md'
        
        content_text = f'''---
type: linkedin_post_approval
created: {datetime.now().isoformat()}
status: pending
action: linkedin_post
---

## Drafted Post

{content}

---

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder.
'''
        filepath.write_text(content_text)
        self.logger.info(f"Approval file created: {filepath}")
        return filepath

    def process_queue(self) -> int:
        """Process all approved posts"""
        count = 0
        
        for filepath in sorted(self.approved_folder.glob('LINKEDIN_POST_*.md')):
            self.logger.info(f"Processing: {filepath.name}")
            content = filepath.read_text()
            
            # Extract post content
            post_content = self._extract_post_content(content)
            
            if not post_content:
                self.logger.warning(f"No content found in {filepath.name}")
                continue
            
            # Post to LinkedIn
            result = self.post(post_content)
            
            if result['success']:
                # Update the approval file with post URL
                original_content = filepath.read_text()
                updated_content = original_content + f"\n\n## Posted\n- URL: {result['post_url']}\n- Time: {datetime.now().isoformat()}\n"
                filepath.write_text(updated_content)
                
                # Move to Done
                filepath.rename(self.done_folder / filepath.name)
                self.logger.info(f"✓ Posted successfully: {result['post_url']}")
                count += 1
            else:
                self.logger.error(f"✗ Failed: {result.get('error', 'Unknown error')}")
                # Move to Needs_Action for review
                error_file = self.vault_path / 'Needs_Action' / f'FAILED_{filepath.name}'
                error_content = f'''---
type: linkedin_post_error
original_file: {filepath.name}
failed_at: {datetime.now().isoformat()}
---

## Error Details
{result.get('error', 'Unknown error')}

## Original Content
{post_content}

## Action Required
Fix the issue and move back to Approved folder.
'''
                error_file.write_text(error_content)
                filepath.unlink()  # Remove from Approved
        
        return count

    def _extract_post_content(self, content: str) -> str:
        """Extract post content from approval file"""
        lines = content.split('\n')
        in_content = False
        post_lines = []
        
        for line in lines:
            if '## Drafted Post' in line or '## Post Content' in line:
                in_content = True
                continue
            elif in_content and line.startswith('##'):
                break
            elif in_content:
                post_lines.append(line)
        
        return '\n'.join(post_lines).strip()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn API Poster')
    parser.add_argument('--vault-path', default=str(Path(__file__).parent.parent.absolute()))
    parser.add_argument('--content', type=str, help='Content to post')
    parser.add_argument('--process-queue', action='store_true', help='Process approved queue')
    parser.add_argument('--test', action='store_true', help='Test API connection')
    parser.add_argument('--verbose', '-v', action='store_true')
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        poster = LinkedInAPIPoster(vault_path=args.vault_path)
    except ValueError as e:
        print(f"Error: {e}")
        print("\nMake sure .env file contains:")
        print("  LINKEDIN_ACCESS_TOKEN=your_token_here")
        sys.exit(1)
    
    if args.test:
        # Test API connection
        print("Testing LinkedIn API connection...")
        result = poster.post("Test post from AI Employee - API Test (will be deleted)")
        if result['success']:
            print(f"✓ API Test Successful!")
            print(f"Post URL: {result['post_url']}")
        else:
            print(f"✗ API Test Failed: {result.get('error', 'Unknown error')}")
    
    elif args.content:
        # Create approval file
        poster.create_approval_file(args.content)
        print(f"✓ Approval file created in Pending_Approval/")
        print(f"Move to Approved/ folder to post")
    
    elif args.process_queue:
        # Process approved posts
        count = poster.process_queue()
        print(f"Posted {count} update(s)")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
