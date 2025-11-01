# Agent Mail System

Asynchronous communication system for coordinating multiple Claude Code agent instances working on the moon-dev-ai-agents project.

## Directory Structure

```
agent_mail/
├── inbox/                      # Broadcast messages (all agents)
├── coordinator-prime/          # Coordinator-Prime's mailbox
│   ├── inbox/                 # Incoming messages
│   └── sent/                  # Sent messages
└── [other-agents]/            # Additional agent mailboxes
    ├── inbox/
    └── sent/
```

## Message Format

All messages are JSON files with the following structure:

```json
{
  "from": "sender-agent-name",
  "to": "recipient-agent-name",
  "timestamp": "2025-11-01T05:00:00Z",
  "subject": "Brief message subject",
  "priority": "critical|high|medium|low",
  "message": "Detailed message content. Can be multi-line.",
  "thread_id": "optional-thread-identifier",
  "requires_response": true,
  "metadata": {
    "task_reference": "task-id-from-plan",
    "related_files": ["path/to/file1.py", "path/to/file2.py"],
    "branch": "branch-name",
    "commit": "commit-hash",
    "tags": ["bug", "feature", "review"]
  }
}
```

## Usage Examples

### Sending a Direct Message

```bash
# Create message file
cat > agent_mail/[recipient]/inbox/msg-$(date +%s).json << 'EOF'
{
  "from": "my-agent-name",
  "to": "recipient-agent-name",
  "timestamp": "2025-11-01T05:30:00Z",
  "subject": "Code review request for trading_agent.py",
  "priority": "high",
  "message": "I've completed refactoring the trading_agent.py file. Could you review the risk calculation logic in lines 245-312? I'm concerned about edge cases when volatility spikes.",
  "thread_id": "review-trading-agent-refactor",
  "requires_response": true,
  "metadata": {
    "related_files": ["src/agents/trading_agent.py"],
    "branch": "claude/refactor-trading-logic",
    "tags": ["review", "trading", "risk-management"]
  }
}
EOF
```

### Broadcasting to All Agents

```bash
# Create broadcast message
cat > agent_mail/inbox/broadcast-$(date +%s).json << 'EOF'
{
  "from": "coordinator-prime",
  "to": "all-agents",
  "timestamp": "2025-11-01T06:00:00Z",
  "subject": "CRITICAL: API key rotation required",
  "priority": "critical",
  "message": "BirdEye API keys are being rotated. All agents must update their .env files. New keys available in 1Password under 'BirdEye-Production-Nov2025'. Please acknowledge receipt.",
  "requires_response": true,
  "metadata": {
    "tags": ["critical", "security", "api"]
  }
}
EOF
```

### Responding to a Message

```bash
# Reply to existing thread
cat > agent_mail/[original-sender]/inbox/reply-$(date +%s).json << 'EOF'
{
  "from": "my-agent-name",
  "to": "original-sender",
  "timestamp": "2025-11-01T06:15:00Z",
  "subject": "Re: Code review request for trading_agent.py",
  "priority": "medium",
  "message": "Review complete. The risk calculation logic looks solid. I added comments on lines 267-270 suggesting we add a circuit breaker for extreme volatility (>100% change). Otherwise LGTM.",
  "thread_id": "review-trading-agent-refactor",
  "requires_response": false,
  "metadata": {
    "related_files": ["src/agents/trading_agent.py"],
    "tags": ["review-complete", "approved"]
  }
}
EOF
```

## Message Priority Levels

- **critical**: System-wide issues, security concerns, immediate action required
- **high**: Important updates, blocking issues, urgent reviews
- **medium**: Regular coordination, non-blocking questions, standard reviews
- **low**: FYI updates, nice-to-have improvements, general discussion

## Best Practices

### 1. Check Inbox Regularly
```bash
# Check for new messages at start of session
ls -lt agent_mail/[your-agent-name]/inbox/

# Check broadcast messages
ls -lt agent_mail/inbox/
```

### 2. Archive Read Messages
```bash
# Move processed messages to archive
mkdir -p agent_mail/[your-agent-name]/archive/
mv agent_mail/[your-agent-name]/inbox/msg-*.json agent_mail/[your-agent-name]/archive/
```

### 3. Use Descriptive Filenames
```bash
# Good filename patterns:
msg-[timestamp]-[subject-slug].json
reply-[timestamp]-[thread-id].json
broadcast-[timestamp]-[topic].json

# Examples:
msg-1730435000-code-review-request.json
reply-1730435500-trading-refactor.json
broadcast-1730436000-api-key-rotation.json
```

### 4. Thread Conversations
Use consistent `thread_id` for related messages:
```json
{
  "thread_id": "feature-sentiment-analysis",
  ...
}
```

### 5. Reference Tasks and Files
Always link messages to tasks and relevant files:
```json
{
  "metadata": {
    "task_reference": "PLAN-TASK-15",
    "related_files": ["src/agents/sentiment_agent.py"],
    "branch": "claude/sentiment-feature"
  }
}
```

## Message Lifecycle

1. **Creation**: Sender creates message in recipient's inbox
2. **Reading**: Recipient checks inbox and reads message
3. **Processing**: Recipient takes action based on message
4. **Response**: Recipient sends reply if `requires_response: true`
5. **Archival**: Both parties archive processed messages

## Advanced Usage

### Task Handoff
```json
{
  "subject": "Task handoff: Complete sentiment_agent.py testing",
  "message": "I've implemented the sentiment analysis features but need to hand off to focus on risk_agent. Current state:\n- Implementation: Complete\n- Unit tests: 80% coverage\n- Integration tests: TODO\n- Documentation: TODO\n\nNext steps in PLAN_TO_DO_XYZ.md under TASK-42.",
  "metadata": {
    "task_reference": "TASK-42",
    "related_files": ["src/agents/sentiment_agent.py", "tests/test_sentiment.py"]
  }
}
```

### Code Review Request
```json
{
  "subject": "Review request: New backtesting framework",
  "message": "Implemented new backtesting framework using backtesting.py library with pandas_ta indicators. Please review:\n\n1. Architecture (src/strategies/backtest_framework.py)\n2. Sample strategy (src/strategies/macd_crossover.py)\n3. Results analysis (src/data/backtest_results.csv)\n\nKey concerns: Performance with large datasets, indicator calculation accuracy.",
  "metadata": {
    "task_reference": "TASK-28",
    "related_files": [
      "src/strategies/backtest_framework.py",
      "src/strategies/macd_crossover.py"
    ],
    "tags": ["review", "backtesting", "performance"]
  }
}
```

### Blocker Notification
```json
{
  "subject": "BLOCKED: Need BirdEye API access",
  "priority": "high",
  "message": "Blocked on TASK-35 (whale_agent enhancement). Need elevated BirdEye API access for historical whale transaction data. Current key has rate limits that prevent fetching last 30 days of data. ETA: Unknown",
  "metadata": {
    "task_reference": "TASK-35",
    "tags": ["blocked", "api", "external-dependency"]
  }
}
```

## Integration with Other Systems

### AGENTS.md Integration
Update your status in AGENTS.md when sending important messages:
```markdown
- **Current Tasks**:
  - Implementing sentiment_agent features (90% complete)
  - Waiting for review on PR #123 (sent review request via agent mail)
```

### PLAN_TO_DO_XYZ.md Integration
Reference task IDs from the plan:
```json
{
  "metadata": {
    "task_reference": "TASK-15",
    ...
  }
}
```

### Git Integration
Include commit hashes and branches:
```json
{
  "metadata": {
    "branch": "claude/sentiment-feature",
    "commit": "a3bcd27",
    ...
  }
}
```

## Troubleshooting

### Message Not Received
- Check recipient name spelling
- Verify inbox directory exists
- Check file permissions

### Too Many Messages
- Archive old messages regularly
- Use priority levels to filter
- Create subdirectories for different topics

### Lost Thread Context
- Always use consistent thread_ids
- Reference previous message filenames
- Include conversation history in important messages

## Security Considerations

- **No sensitive data**: Never include API keys, private keys, or credentials in messages
- **Reference securely**: Point to secure storage (1Password, .env files) instead
- **Public repository**: Remember this is a public repo - all messages are visible

---

**System Version**: 1.0.0
**Created**: 2025-11-01 by Coordinator-Prime
**Last Updated**: 2025-11-01
