# Claude Code Configuration

This directory contains Claude Code configuration and extensions for the Moon Dev AI Trading System.

## Directory Structure

```
.claude/
├── README.md           # This file
└── skills/             # Claude Code Skills
    ├── SKILLS.md       # Skills documentation
    ├── analyze-performance.md
    ├── run-backtest.md
    ├── validate-system.md
    └── optimize-costs.md
```

## What's in This Directory

### Skills
Specialized expert prompts that give Claude Code domain-specific capabilities.

**Available skills**:
- `analyze-performance` - Deep performance analysis
- `run-backtest` - Complete backtesting workflow
- `validate-system` - Comprehensive system validation
- `optimize-costs` - API cost optimization analysis

**See [skills/SKILLS.md](skills/SKILLS.md)** for complete documentation.

## Quick Start

```bash
# Validate system before first run
/skill validate-system

# Analyze performance
/skill analyze-performance

# Run a backtest
/skill run-backtest

# Optimize costs
/skill optimize-costs
```

## Why Use .claude Directory?

The `.claude/` directory is the standard location for Claude Code configuration and extensions:

- **skills/** - Reusable expert workflows
- **agents/** - Multi-agent configurations (future)
- **commands/** - Custom slash commands (future)
- **hooks/** - Event hooks (future)

## Architecture Decision

This project uses a **hybrid approach**:

1. **Claude Code Skills** (.claude/skills/) - For development workflows
   - Performance analysis
   - System validation
   - Cost optimization
   - Backtest execution

2. **Python AI Agents** (src/agents/) - For trading logic
   - 48+ specialized trading agents
   - Risk management
   - Market analysis
   - Strategy execution

3. **MCP Servers** (not yet implemented) - For external systems
   - Database integration
   - Real-time data feeds
   - External API wrappers

**Why this architecture?**
- Skills = Fast, no overhead, perfect for dev workflows
- Python Agents = Stateful, complex logic, perfect for trading
- MCP = External integration when needed

## Future Extensions

Planned additions to `.claude/`:

### Agents (Future)
Multi-agent configurations for complex workflows:
```
.claude/agents/
├── code-review-swarm.md
├── performance-optimizer.md
└── security-auditor.md
```

### Commands (Future)
Custom slash commands:
```
.claude/commands/
├── quick-test.md      # /quick-test
├── deploy.md          # /deploy
└── health-check.md    # /health-check
```

### Hooks (Future)
Event-based automation:
```
.claude/hooks/
├── pre-commit.md      # Run before commits
├── post-test.md       # Run after tests
└── on-error.md        # Run on errors
```

## Documentation

- **Skills Documentation**: [skills/SKILLS.md](skills/SKILLS.md)
- **Project Documentation**: [../DOCUMENTATION_INDEX.md](../DOCUMENTATION_INDEX.md)
- **Performance Analysis**: [../PERFORMANCE_ANALYSIS.md](../PERFORMANCE_ANALYSIS.md)

## Contributing

To add new skills or extensions:

1. Create the file in appropriate directory
2. Follow existing patterns and structure
3. Document in relevant README
4. Test thoroughly
5. Submit PR

## Notes

- This `.claude/` directory is separate from the old `.claude/` structure in `src/data/rbi/.claude/`
- The old structure was exploratory and is not actively used
- This new structure follows Claude Code best practices

## Support

- **GitHub Issues**: Report problems or request features
- **Discord**: Join community for help and discussion
- **Documentation**: See [DOCUMENTATION_INDEX.md](../DOCUMENTATION_INDEX.md)

---

Made with ❤️ for the Moon Dev community
