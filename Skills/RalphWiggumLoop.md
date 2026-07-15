# Skill: RalphWiggumLoop

## Purpose
Enable autonomous multi-step task completion by keeping Claude Code working until tasks are fully complete.

## When to Use
- Complex multi-step tasks
- Tasks that require iteration
- When you want fully autonomous operation
- Processing entire queues of work

## The Problem

Claude Code by default:
1. Executes one command
2. Shows output
3. Waits for next user input

This breaks autonomous workflows because:
- Tasks often need multiple iterations
- Claude might exit prematurely
- User needs to keep prompting

## The Solution: Ralph Wiggum Pattern

A Stop hook that:
1. Intercepts Claude's exit
2. Checks if task is complete
3. If NOT complete → re-injects prompt
4. If complete → allows exit

## How It Works

```
┌─────────────────────────────────┐
│  1. Orchestrator creates task   │
│     file with prompt            │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  2. Claude works on task        │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  3. Claude tries to exit        │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  4. Stop hook checks:           │
│     Is task in /Done?           │
└────────────┬────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌────────┐      ┌────────────┐
│  NO    │      │    YES     │
│ Loop   │      │  Exit OK   │
│ Again  │      │  (Complete)│
└────────┘      └────────────┘
```

## Usage

### Basic Ralph Loop
```bash
# Start Ralph loop for a task
/ralph-loop "Process all files in Needs_Action and move to Done" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

### With File Movement Detection
```bash
# Ralph loop watches for file movement to Done/
/ralph-loop "Review and respond to all pending emails" \
  --completion-file "Needs_Action/" \
  --max-iterations 5
```

### Integration with Orchestrator
```python
# orchestrator.py creates Ralph loop automatically
def run_ralph_loop(task: str):
    subprocess.run([
        'claude',
        '--print', task,
        '--ralph-loop',
        '--max-iterations', '10'
    ])
```

## Completion Strategies

### 1. Promise-Based (Simple)
Claude outputs special marker when done:
```
<promise>TASK_COMPLETE</promise>
```

Stop hook looks for this marker.

### 2. File Movement (Advanced)
Stop hook detects when task file moves:
- From: `Needs_Action/task.md`
- To: `Done/task.md`

More reliable - completion is natural part of workflow.

## Configuration

### Max Iterations
- Default: 5
- Recommended: 5-10
- Prevents infinite loops

### Completion Promise
- Custom marker string
- Default: `TASK_COMPLETE`
- Claude outputs when done

### Timeout
- Max time per iteration
- Default: 10 minutes
- Prevents hanging

## Example Task Flow

### Task: Process Email Queue

**Initial State:**
```
Needs_Action/
├── EMAIL_Client_A.md
├── EMAIL_Client_B.md
└── EMAIL_Client_C.md
```

**Ralph Loop Prompt:**
```
Process all emails in Needs_Action/:
1. Read each email
2. Draft appropriate response
3. Move to Done/ after processing

Continue until all emails are processed.
```

**After Loop:**
```
Done/
├── EMAIL_Client_A.md
├── EMAIL_Client_B.md
└── EMAIL_Client_C.md

Needs_Action/
└── (empty)
```

## Files
- Reference: `.claude/plugins/ralph-wiggum/`
- Usage: Built into Claude Code

## Best Practices

### Good Tasks for Ralph Loop
- Processing queues of work
- Multi-step research tasks
- Batch operations
- Data transformation pipelines

### Bad Tasks for Ralph Loop
- Open-ended exploration
- Tasks without clear completion
- Creative work needing human input

### Monitoring
- Check logs after each iteration
- Set reasonable max iterations
- Review output for errors

## Error Handling

### Loop Exits Early
- Check if task actually complete
- Increase max iterations if needed
- Review error messages

### Infinite Loop
- Set max iterations limit
- Add timeout per iteration
- Check completion criteria

## Related Skills
- WeeklyBusinessAudit
- CEOBriefingGenerator
- HumanApprovalRequest
