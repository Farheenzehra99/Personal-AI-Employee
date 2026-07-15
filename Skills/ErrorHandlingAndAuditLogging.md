# Skill: ErrorHandlingAndAuditLogging

## Purpose
Implement comprehensive error handling, graceful degradation, and audit logging for all AI Employee operations.

## When to Use
- Any automated operation
- Critical business processes
- Compliance requirements
- Debugging issues
- Performance monitoring

## Error Handling Principles

### 1. Graceful Degradation
When a component fails:
- Log the error
- Continue with reduced functionality
- Notify user if critical
- Retry if appropriate

### 2. Retry Logic
For transient errors:
- Retry up to 3 times
- Exponential backoff (1s, 5s, 30s)
- Circuit breaker after 5 failures

### 3. Error Categories

| Category | Action | Example |
|----------|--------|---------|
| Critical | Stop, notify | Database corruption |
| Major | Retry, then notify | API timeout |
| Minor | Log, continue | Non-essential feature fail |
| Info | Log only | Debug information |

## Audit Logging

### What to Log

**Every Action:**
- Timestamp
- User/Agent ID
- Action type
- Input parameters
- Result (success/failure)
- Duration
- Error details (if any)

**Format:**
```json
{
  "timestamp": "2026-03-12T10:30:00Z",
  "agent": "AI_Employee_v1.0",
  "action": "linkedin_post",
  "input": {"content": "Post text..."},
  "result": "success",
  "duration_ms": 5432,
  "metadata": {"post_id": "12345"}
}
```

### Log Levels

| Level | Use Case |
|-------|----------|
| ERROR | Operation failed, needs attention |
| WARN | Operation succeeded with issues |
| INFO | Normal operation |
| DEBUG | Detailed diagnostic info |

## Implementation

### Error Handler Class

```python
class ErrorHandler:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.logger = AuditLogger()
    
    def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with retry logic"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                self.logger.log('INFO', f'{func.__name__} succeeded')
                return result
            except Exception as e:
                last_error = e
                self.logger.log('ERROR', f'{func.__name__} failed: {e}', 
                               attempt=attempt+1)
                time.sleep(2 ** attempt)  # Exponential backoff
        
        # All retries failed
        self.logger.log('CRITICAL', f'{func.__name__} failed after {self.max_retries} attempts')
        raise last_error
```

### Audit Logger Class

```python
class AuditLogger:
    def __init__(self, log_path='Logs/audit.log'):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, level, message, **metadata):
        """Write audit log entry"""
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            **metadata
        }
        
        # Append to log file
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        # Also print to console
        print(f"[{level}] {message}")
    
    def get_logs(self, level=None, start_date=None, end_date=None):
        """Read audit logs with filters"""
        logs = []
        
        with open(self.log_path, 'r') as f:
            for line in f:
                entry = json.loads(line)
                
                # Apply filters
                if level and entry['level'] != level:
                    continue
                
                logs.append(entry)
        
        return logs
```

## Usage Examples

### Watcher with Error Handling

```python
class WhatsAppWatcher:
    def __init__(self):
        self.error_handler = ErrorHandler(max_retries=3)
        self.audit_logger = AuditLogger()
    
    def check_for_updates(self):
        """Check WhatsApp with error handling"""
        try:
            self.audit_logger.log('INFO', 'Starting WhatsApp check')
            
            items = self.error_handler.execute_with_retry(
                self._whatsapp_check
            )
            
            self.audit_logger.log('INFO', f'Found {len(items)} items')
            return items
            
        except Exception as e:
            self.audit_logger.log('ERROR', f'WhatsApp check failed: {e}')
            return []  # Graceful degradation
```

### Poster with Audit Trail

```python
class LinkedInPoster:
    def __init__(self):
        self.audit_logger = AuditLogger()
    
    def post_content(self, content):
        """Post with full audit trail"""
        start_time = datetime.utcnow()
        
        try:
            self.audit_logger.log('INFO', 'Starting LinkedIn post',
                                 content_length=len(content))
            
            result = self._post_to_linkedin(content)
            
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            self.audit_logger.log('INFO', 'LinkedIn post completed',
                                 result=result,
                                 duration_ms=duration)
            
            return result
            
        except Exception as e:
            self.audit_logger.log('ERROR', 'LinkedIn post failed',
                                 error=str(e))
            raise
```

## Monitoring Dashboard

### Log Analysis

```bash
# Count errors by type
grep '"level":"ERROR"' Logs/audit.log | \
  jq -r '.message' | sort | uniq -c | sort -rn

# Find slow operations
grep '"duration_ms"' Logs/audit.log | \
  jq -r 'select(.duration_ms > 5000) | .message'

# Today's activity summary
grep "$(date +%Y-%m-%d)" Logs/audit.log | \
  jq -r '.level' | sort | uniq -c
```

### Alerts

Set up alerts for:
- More than 10 errors in 1 hour
- Any CRITICAL level errors
- Operations taking >30 seconds
- Failed authentication attempts

## Files

### Scripts
- `watchers/error_handler.py` - Error handling utilities
- `watchers/audit_logger.py` - Audit logging utilities

### Logs
- `Logs/audit.log` - Main audit log
- `Logs/error.log` - Error-specific log
- `Logs/performance.log` - Performance metrics

## Best Practices

### Do's
✅ Log all external API calls
✅ Include correlation IDs for tracing
✅ Set up log rotation (keep 30 days)
✅ Monitor error rates
✅ Document error codes

### Don'ts
❌ Log sensitive data (passwords, tokens)
❌ Log excessively (performance impact)
❌ Ignore errors silently
❌ Retry indefinitely
❌ Mix log levels inconsistently

## Related Skills
- WeeklyBusinessAudit
- CEOBriefingGenerator
- RalphWiggumLoop
