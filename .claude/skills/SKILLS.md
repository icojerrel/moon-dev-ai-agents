# Claude Code Skills for Moon Dev AI Trading System

This directory contains specialized skills for Claude Code that streamline common development and analysis workflows for the Moon Dev AI trading system.

## What are Skills?

Skills are specialized prompts that give Claude Code expert capabilities in specific domains. When you invoke a skill, Claude Code loads detailed instructions and becomes an expert in that area, performing comprehensive workflows with consistency and best practices.

**Benefits**:
- ⚡ Faster than typing detailed prompts every time
- 🎯 Consistent methodology across sessions
- 📋 Comprehensive checklists ensure nothing is missed
- 🔄 Reusable across different projects
- 🚀 No runtime overhead (pure prompt engineering)

## Available Skills

### 1. 📊 analyze-performance
**What it does**: Performs deep performance analysis of the trading system

**When to use**:
- After making significant code changes
- When the system feels slow
- Before optimization efforts
- Monthly performance reviews

**Usage**:
```bash
/skill analyze-performance
```

**What it analyzes**:
- Agent execution times
- API call patterns and costs
- Caching opportunities
- Sequential vs. parallel execution bottlenecks
- Memory and resource usage
- Configuration issues

**Output**: Detailed performance report with prioritized action items

---

### 2. 🧪 run-backtest
**What it does**: Executes complete backtesting workflow with validation and reporting

**When to use**:
- Testing new trading strategies
- Validating strategy modifications
- Comparing strategy performance
- Before deploying strategies to live trading

**Usage**:
```bash
/skill run-backtest
```

**What it does**:
1. Validates strategy file and data
2. Loads OHLCV data
3. Executes backtest with proper settings
4. Generates comprehensive performance report
5. Compares vs. buy-and-hold benchmark
6. Provides improvement recommendations

**Requirements**:
- Strategy file in `src/strategies/`
- OHLCV data (default: `src/data/rbi/BTC-USD-15m.csv`)
- Dependencies: `backtesting`, `pandas_ta` or `talib`

**Output**: Complete backtest report with metrics, trade statistics, and recommendations

---

### 3. ✅ validate-system
**What it does**: Performs comprehensive system validation before trading

**When to use**:
- Before running trading system for first time
- After configuration changes
- After dependency updates
- Before deployment to production
- Daily pre-flight checks

**Usage**:
```bash
/skill validate-system
```

**What it validates**:
1. File structure completeness
2. Python syntax for all agents (48+)
3. Dependencies installation
4. Environment variables (API keys)
5. Configuration reasonableness
6. API connectivity
7. ModelFactory setup
8. Agent integrity
9. Performance infrastructure
10. Trading functions availability

**Output**: Comprehensive validation report with status (READY/NEEDS ATTENTION/NOT READY)

---

### 4. 💰 optimize-costs
**What it does**: Analyzes API costs and provides specific optimization recommendations

**When to use**:
- Monthly cost reviews
- After cost spikes
- Before scaling up operations
- When optimizing for profitability

**Usage**:
```bash
/skill optimize-costs
```

**What it analyzes**:
- AI API costs by agent and model
- Trading API costs (BirdEye, CoinGecko, RPC)
- Caching opportunities
- Model right-sizing opportunities
- Redundant API calls
- OpenRouter migration potential
- Execution frequency optimization

**Output**: Detailed cost analysis with specific implementation code and ROI calculations

**Expected results**:
- Current daily/monthly cost breakdown
- Optimization opportunities prioritized by ROI
- Concrete implementation code for each optimization
- Phase-based implementation roadmap
- Expected savings ($/day, $/month, $/year)

---

## Quick Start

### First Time Setup Workflow

```bash
# Step 1: Validate system
/skill validate-system

# Step 2: Fix any critical issues found

# Step 3: Analyze performance
/skill analyze-performance

# Step 4: Review costs
/skill optimize-costs
```

### Regular Maintenance Workflow

```bash
# Weekly: Validate system health
/skill validate-system

# Weekly: Check performance
/skill analyze-performance

# Monthly: Review and optimize costs
/skill optimize-costs
```

### Strategy Development Workflow

```bash
# Step 1: Develop strategy in src/strategies/

# Step 2: Run backtest
/skill run-backtest

# Step 3: Review results and iterate

# Step 4: Validate system before deployment
/skill validate-system
```

## How Skills Work

When you invoke a skill (e.g., `/skill analyze-performance`), Claude Code:

1. Loads the skill prompt from `.claude/skills/analyze-performance.md`
2. Becomes an expert in that domain with specific instructions
3. Executes a comprehensive workflow
4. Generates a detailed report

Skills use these tools automatically:
- `Read` - To examine files
- `Glob` - To find files by pattern
- `Grep` - To search code
- `Bash` - To run validation commands
- Direct analysis (no Task tool spawning for efficiency)

## Skill Structure

Each skill is a markdown file containing:

```markdown
# [Skill Name]

You are a [domain] expert for Moon Dev...

## Your Task
[What the skill does]

## Workflow Steps
[Detailed checklist of steps]

## Expected Output Format
[Structured output template]

## Tools You Should Use
[Specific tools for this skill]

## Success Criteria
[How to know the task is complete]

Begin [task] now!
```

## Creating Custom Skills

You can create your own skills:

1. Create `.claude/skills/my-skill.md`
2. Follow the structure above
3. Be specific about the task, tools, and output format
4. Test with `/skill my-skill`

**Example custom skills**:
- `debug-agent.md` - Debug specific agent issues
- `deploy-strategy.md` - Deploy strategy to production
- `generate-report.md` - Generate trading performance report
- `monitor-health.md` - Real-time system health monitoring

## Best Practices

### When to Use Skills
✅ Use skills for:
- Repetitive analysis workflows
- Complex multi-step processes
- Comprehensive validations
- Consistent reporting

❌ Don't use skills for:
- Simple one-off questions
- Quick file reads
- Basic debugging
- Conversational interactions

### Skill Invocation
```bash
# Correct - use /skill prefix
/skill analyze-performance

# Incorrect - skills are not Python scripts
python analyze-performance.md
```

### Combining Skills
You can run multiple skills in sequence:

```bash
# Morning routine
/skill validate-system
# [wait for completion]
/skill analyze-performance
# [wait for completion]
/skill optimize-costs
```

## Tips

1. **Read the output carefully** - Skills generate comprehensive reports with specific action items

2. **Act on recommendations** - Skills provide concrete code changes, not just analysis

3. **Rerun after changes** - After implementing recommendations, rerun skills to verify improvements

4. **Customize for your needs** - Fork and modify skills to match your workflow

5. **Share improvements** - If you create useful skills, share them with the community

## Skill vs. Agent vs. MCP

Understanding the differences:

| Feature | Skill | Python Agent | MCP Server |
|---------|-------|--------------|------------|
| **Purpose** | Dev workflows | Trading logic | External systems |
| **Runtime** | No overhead | Continuous | Server process |
| **Complexity** | Simple (MD) | Complex (Python) | Medium (Server) |
| **State** | Stateless | Stateful | Stateful |
| **Examples** | Validation, Analysis | Trading, Risk | Database, API |
| **When to use** | Development | Core trading | Integration |

**In this project**:
- **Skills**: Development workflows (this directory)
- **Python Agents**: 48+ trading agents in `src/agents/`
- **MCP**: Not used yet (could integrate for external APIs)

## Troubleshooting

### Skill not found
```bash
Error: Skill 'analyze-performance' not found
```
**Fix**: Check file exists at `.claude/skills/analyze-performance.md`

### Skill runs but output is incomplete
**Fix**: Skill is working but may need more time. Check the output for specific errors.

### Skill doesn't follow instructions
**Fix**: The skill prompt may need refinement. Edit the `.md` file to be more specific.

## Advanced Usage

### Skill Chaining
Create a master skill that calls other skills:

```markdown
# meta-analysis.md

1. First, invoke analyze-performance skill
2. Wait for results
3. Then invoke optimize-costs skill
4. Combine insights into meta-analysis
```

### Parameterized Skills
While skills can't take direct parameters, you can create variants:

```
.claude/skills/
├── run-backtest-btc.md     # BTC-specific
├── run-backtest-eth.md     # ETH-specific
└── run-backtest-sol.md     # SOL-specific
```

### Context-Aware Skills
Skills can read configuration and adapt:

```markdown
# In the skill prompt:
First, read src/config.py to determine:
- Which AI model is configured
- Which tokens are monitored
- Current risk settings

Then adapt analysis based on configuration.
```

## Contributing

To contribute a new skill:

1. Create the skill in `.claude/skills/`
2. Test thoroughly
3. Document in this SKILLS.md
4. Submit PR with:
   - Skill file
   - Documentation
   - Example output

## Support

- **Documentation**: See [DOCUMENTATION_INDEX.md](../../../DOCUMENTATION_INDEX.md)
- **Issues**: Report at GitHub issues
- **Community**: Join Discord for skill sharing

## Next Steps

1. ✅ Read this documentation
2. 🧪 Try each skill once
3. 📊 Review generated reports
4. 🔧 Implement recommendations
5. 🎯 Create custom skills for your workflow

---

**Remember**: Skills are here to make your development faster and more consistent. Use them liberally!
