# Agent Registry & Coordination System

This file tracks all Claude Code agent instances working on the moon-dev-ai-agents project. Each agent registers here to enable coordination, task distribution, and collaborative development.

## System Overview

This is a **multi-agent coordination system** where multiple Claude Code instances work together on the trading AI platform. Agents communicate via the agent mail system and coordinate through shared task planning documents.

## Active Agents

### Agent-1: Coordinator-Prime
- **Session ID**: `011CUgefbZrQTRbhNVZov8nn`
- **Branch**: `claude/agent-coordination-setup-011CUgefbZrQTRbhNVZov8nn`
- **Role**: Coordination Setup & System Architecture
- **Specialization**: Multi-agent orchestration, system design, coordination infrastructure
- **Status**: Active
- **Registered**: 2025-11-01
- **Last Active**: 2025-11-01
- **Current Tasks**:
  - Setting up agent coordination system
  - Creating agent registry and mail system
  - Defining task distribution framework
- **Capabilities**:
  - Agent coordination and orchestration
  - System architecture design
  - Multi-agent workflow planning
  - Infrastructure setup
- **Contact**: Via agent_mail/coordinator-prime/

---

## Agent Registration Process

To register a new agent, add your information following this template:

```markdown
### Agent-N: [Your-Agent-Name]
- **Session ID**: `[your-session-id]`
- **Branch**: `claude/[your-branch-name]`
- **Role**: [Primary Role]
- **Specialization**: [Your specialized focus areas]
- **Status**: Active | Idle | Offline
- **Registered**: YYYY-MM-DD
- **Last Active**: YYYY-MM-DD
- **Current Tasks**:
  - [Task 1]
  - [Task 2]
- **Capabilities**:
  - [Capability 1]
  - [Capability 2]
- **Contact**: Via agent_mail/[your-agent-name]/
```

## Agent Mail System

Agents communicate asynchronously through the `agent_mail/` directory structure:

```
agent_mail/
├── inbox/              # Broadcast messages to all agents
├── coordinator-prime/  # Messages for Coordinator-Prime
│   ├── inbox/         # Incoming messages
│   └── sent/          # Sent messages
├── [agent-name]/      # Per-agent mailboxes
│   ├── inbox/
│   └── sent/
└── README.md          # Mail system usage guide
```

### Sending a Message

Create a JSON file in the target agent's inbox:

```json
{
  "from": "agent-name",
  "to": "target-agent-name",
  "timestamp": "2025-11-01T05:00:00Z",
  "subject": "Message subject",
  "priority": "high|medium|low",
  "message": "Message content",
  "thread_id": "optional-thread-id",
  "requires_response": true,
  "metadata": {
    "task_reference": "task-id",
    "related_files": ["file1", "file2"]
  }
}
```

### Broadcast Messages

Place messages in `agent_mail/inbox/` to notify all agents.

## Coordination Principles

### 1. Task Distribution
- Agents claim tasks from `PLAN_TO_DO_XYZ.md` by marking them with their name
- Update task status when starting and completing work
- Communicate blockers immediately via agent mail

### 2. Code Review Protocol
- All major changes require review by at least one other agent
- Request reviews via agent mail
- Use `REVIEWS_NEEDED/` directory for pending reviews

### 3. Conflict Resolution
- Git conflicts should be resolved collaboratively
- Communicate about files you're actively editing
- Use feature branches for experimental work

### 4. Synchronization Points
- Agents should sync with main coordination doc at start of each session
- Update AGENTS.md with current status and tasks
- Check agent mail inbox before starting new work

## Specialized Agent Roles

As the project scales, agents may specialize in:

### Trading System Agents
- **Trading Logic Specialist**: Focus on trading algorithms, strategies, risk management
- **Data Pipeline Engineer**: Market data ingestion, processing, storage
- **Backtesting Specialist**: Strategy validation, performance optimization

### Infrastructure Agents
- **DevOps Engineer**: Deployment, monitoring, infrastructure
- **API Integration Specialist**: External API integrations (BirdEye, CoinGecko, etc.)
- **LLM Integration Engineer**: Model factory, prompt engineering

### AI Agent Development
- **Agent Developer**: Creating and refining the 48+ trading agents
- **Orchestration Engineer**: Main loop coordination, agent scheduling
- **Memory & State Manager**: Agent memory systems, state persistence

### Quality & Documentation
- **Test Engineer**: Unit tests, integration tests, backtests
- **Documentation Specialist**: README files, API docs, user guides
- **Code Reviewer**: Quality assurance, code review, best practices

## Communication Channels

### Synchronous Communication
- **Active Coordination**: Through shared task documents
- **Real-time Updates**: Via AGENTS.md status updates

### Asynchronous Communication
- **Agent Mail**: For detailed discussions, reviews, handoffs
- **Task Comments**: In PLAN_TO_DO_XYZ.md for task-specific notes
- **Code Comments**: For implementation-level coordination

## Best Practices

1. **Check inbox first**: Always review agent mail before starting work
2. **Update your status**: Keep AGENTS.md current with your work
3. **Claim tasks explicitly**: Mark tasks with your agent name
4. **Communicate early**: Report blockers immediately
5. **Document decisions**: Record important technical decisions
6. **Review code**: Participate in peer reviews
7. **Test thoroughly**: Ensure your changes don't break existing functionality
8. **Sync frequently**: Pull latest changes, push completed work

## Emergency Protocols

### Critical Bugs
1. Post to `agent_mail/inbox/` with CRITICAL priority
2. All agents should pause and assess impact
3. Coordinate immediate fix

### Merge Conflicts
1. Agent who discovers conflict posts to agent mail
2. Involved agents coordinate resolution
3. Document resolution approach

### System Downtime
1. Update status to "Offline" in AGENTS.md
2. Document current work state
3. Hand off urgent tasks to other agents

## Getting Started

For new agents joining the project:

1. **Read all documentation**:
   - CLAUDE.md (project overview)
   - README.md (system architecture)
   - This file (coordination system)
   - PLAN_TO_DO_XYZ.md (current tasks)

2. **Register yourself**:
   - Add your entry to Active Agents section
   - Create your agent mail directory
   - Send introduction to agent_mail/inbox/

3. **Review current state**:
   - Check what other agents are working on
   - Review recent agent mail messages
   - Understand current priorities

4. **Claim initial task**:
   - Find unclaimed task in PLAN_TO_DO_XYZ.md
   - Update task with your agent name
   - Send notification of task claim

5. **Start contributing**:
   - Begin work on claimed task
   - Update status regularly
   - Communicate progress and blockers

---

**Last Updated**: 2025-11-01 by Coordinator-Prime
**System Version**: 1.0.0
**Total Active Agents**: 1
