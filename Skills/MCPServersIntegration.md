# Skill: MCPServersIntegration

## Purpose
Integrate Model Context Protocol (MCP) servers for external system interactions including Email, Browser, and Calendar.

## When to Use
- Send emails via Gmail API
- Automate web interactions via browser
- Schedule meetings via Google Calendar
- Multi-step workflows requiring external actions

## MCP Servers Available

### 1. Email MCP Server
**Purpose:** Send/receive emails via Gmail

**Capabilities:**
- Send emails with attachments
- Read emails with filters
- Create drafts
- Mark as read/unread
- Search emails

**Usage:**
```bash
# Test connection
python watchers/email_mcp_server.py --test

# Send email
python watchers/email_mcp_server.py --send --to someone@example.com
```

**Example - Send Email:**
```
Use EmailMCP to send an email:
- To: client@example.com
- Subject: Meeting Confirmation
- Body: "Hi, confirming our meeting tomorrow at 2 PM."
```

---

### 2. Browser MCP Server
**Purpose:** Web automation via Playwright

**Capabilities:**
- Navigate to URLs
- Click elements
- Fill forms
- Take screenshots
- Execute JavaScript
- Scrape content

**Usage:**
```bash
# Test browser
python watchers/browser_mcp_server.py --test --url https://example.com
```

**Example - Web Automation:**
```
Use BrowserMCP to:
1. Navigate to https://linkedin.com
2. Fill login form
3. Click submit
4. Take screenshot
```

---

### 3. Calendar MCP Server
**Purpose:** Schedule events via Google Calendar

**Capabilities:**
- Create events
- Get upcoming events
- Update events
- Delete events
- Add attendees

**Usage:**
```bash
# Test calendar
python watchers/calendar_mcp_server.py --test
```

**Example - Schedule Meeting:**
```
Use CalendarMCP to create event:
- Summary: "Client Meeting"
- Start: 2026-03-15T14:00:00Z
- End: 2026-03-15T15:00:00Z
- Attendees: ["client@example.com"]
- Location: "Zoom"
```

---

## Installation

### Prerequisites
```bash
# Install dependencies
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install playwright
playwright install chromium
```

### Authentication

#### Gmail/Calendar
```bash
# First time setup
python watchers/gmail_watcher.py --auth

# Follow browser prompts to authorize
# Token saved to token.json
```

#### Browser
No authentication needed - uses saved sessions

---

## MCP Protocol

### Tool Definition Format
```json
{
  "name": "email_send",
  "description": "Send an email",
  "inputSchema": {
    "type": "object",
    "properties": {
      "to": {"type": "string"},
      "subject": {"type": "string"},
      "body": {"type": "string"}
    },
    "required": ["to", "subject", "body"]
  }
}
```

### Tool Call Format
```json
{
  "tool": "email_send",
  "arguments": {
    "to": "user@example.com",
    "subject": "Hello",
    "body": "Test email"
  }
}
```

### Response Format
```json
{
  "success": true,
  "message_id": "abc123",
  "thread_id": "xyz789"
}
```

---

## Claude Code Integration

### Configure MCP Servers

Create `~/.config/claude-code/mcp.json`:

```json
{
  "mcpServers": {
    "email": {
      "command": "python",
      "args": ["/mnt/d/personal-ai-employee/watchers/email_mcp_server.py"],
      "env": {}
    },
    "browser": {
      "command": "python",
      "args": ["/mnt/d/personal-ai-employee/watchers/browser_mcp_server.py"],
      "env": {"HEADLESS": "true"}
    },
    "calendar": {
      "command": "python",
      "args": ["/mnt/d/personal-ai-employee/watchers/calendar_mcp_server.py"],
      "env": {}
    }
  }
}
```

### Usage in Claude

```
# Send email via MCP
claude "Use email MCP to send a meeting reminder to team@example.com"

# Schedule meeting
claude "Use calendar MCP to schedule a 1-hour meeting tomorrow at 3 PM"

# Web automation
claude "Use browser MCP to check our website status"
```

---

## Example Workflows

### Workflow 1: Meeting Scheduler

1. **Read email for meeting request**
   ```
   Use EmailMCP to read emails with query "meeting request"
   ```

2. **Extract details**
   - From email body
   - Parse date/time

3. **Create calendar event**
   ```
   Use CalendarMCP to create event with extracted details
   ```

4. **Send confirmation**
   ```
   Use EmailMCP to send confirmation email
   ```

---

### Workflow 2: Web Form Automation

1. **Navigate to form**
   ```
   Use BrowserMCP to navigate to https://example.com/form
   ```

2. **Fill fields**
   ```
   Use BrowserMCP to fill #name with "John Doe"
   Use BrowserMCP to fill #email with "john@example.com"
   ```

3. **Submit**
   ```
   Use BrowserMCP to click button[type="submit"]
   ```

4. **Screenshot confirmation**
   ```
   Use BrowserMCP to take screenshot
   ```

---

### Workflow 3: Invoice Email with Calendar Follow-up

1. **Create invoice in Odoo**
   ```
   Use OdooAccounting to create invoice
   ```

2. **Email invoice**
   ```
   Use EmailMCP to send email with invoice PDF
   ```

3. **Schedule follow-up**
   ```
   Use CalendarMCP to create follow-up event in 7 days
   ```

---

## Error Handling

### Authentication Errors
```
Error: "Not authenticated"
Solution: Run authentication script first
```

### Browser Errors
```
Error: "Browser not launched"
Solution: Call browser.launch() first
```

### API Quota Errors
```
Error: "Quota exceeded"
Solution: Wait and retry, or increase quota
```

---

## Best Practices

### Security
- Never commit credentials/tokens
- Use environment variables
- Rotate tokens periodically

### Performance
- Reuse browser instances
- Batch email operations
- Cache calendar data

### Reliability
- Add retry logic
- Handle timeouts gracefully
- Log all operations

---

## Files

### Scripts
- `watchers/email_mcp_server.py` - Email MCP
- `watchers/browser_mcp_server.py` - Browser MCP
- `watchers/calendar_mcp_server.py` - Calendar MCP

### Config
- `gmail_credentials.json` - Google API credentials
- `token.json` - Gmail auth token
- `token_calendar.json` - Calendar auth token

### MCP Config
- `~/.config/claude-code/mcp.json` - Claude MCP configuration

---

## Troubleshooting

### Email MCP Issues

**Problem:** Authentication failed
```bash
# Re-authenticate
rm token.json
python watchers/gmail_watcher.py --auth
```

**Problem:** Quota exceeded
- Wait 24 hours
- Or create new Google Cloud project

### Browser MCP Issues

**Problem:** Browser won't launch
```bash
# Reinstall Playwright
pip uninstall playwright
pip install playwright
playwright install chromium
```

**Problem:** Elements not found
- Check selector syntax
- Wait for page load
- Use waitForSelector

### Calendar MCP Issues

**Problem:** Can't create events
- Check calendar permissions
- Verify authentication
- Ensure valid date format

---

## Related Skills
- OdooAccounting
- EmailResponder
- HumanApprovalRequest
