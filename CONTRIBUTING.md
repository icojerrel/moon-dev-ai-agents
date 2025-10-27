# 🌙 Contributing to Moon Dev AI Agents

Thank you for your interest in contributing! This document provides guidelines and best practices for contributing to this project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Agent Development](#agent-development)
- [Testing](#testing)
- [Documentation](#documentation)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive experience for everyone. We expect all contributors to:

- Be respectful and considerate
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

### What's Not Acceptable

- Harassment, trolling, or discriminatory language
- Publishing others' private information
- Any conduct that could be considered unprofessional

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.10.9 installed
- Git installed and configured
- Read the [README.md](README.md), [SETUP.md](SETUP.md), and [CLAUDE.md](CLAUDE.md)
- Joined the [Moon Dev Discord](http://moondev.com)

### First Time Contributors

1. **Star the repository** ⭐ (shows your support!)
2. **Fork the repository** 🍴
3. **Read the documentation** 📚
4. **Look for "good first issue" labels** 🏷️
5. **Ask questions in Discord** 💬

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repo on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/moon-dev-ai-agents.git
cd moon-dev-ai-agents

# Add upstream remote
git remote add upstream https://github.com/icojerrel/moon-dev-ai-agents.git
```

### 2. Create Environment

```bash
# Create conda environment
conda create -n tflow python=3.10.9
conda activate tflow

# Install dependencies
pip install -r requirements.txt
```

### 3. Install Development Tools

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Install linting tools
pip install flake8 black isort
```

### 4. Validate Setup

```bash
# Run validation
python scripts/validate_config.py
```

---

## Making Changes

### Branch Naming

Create descriptive branch names:

```bash
# Feature branches
git checkout -b feature/add-sentiment-analysis

# Bug fixes
git checkout -b fix/risk-agent-calculation

# Documentation
git checkout -b docs/improve-setup-guide

# Refactoring
git checkout -b refactor/model-factory-cleanup
```

### Before You Start

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Create your branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Keep changes focused**: One feature/fix per PR

### Making Commits

#### Commit Message Format

```
<type>: <subject>

<body>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

**Examples:**

```bash
# Good commit messages
git commit -m "feat: Add DeepSeek R1 support to model factory"
git commit -m "fix: Correct PnL calculation in risk agent"
git commit -m "docs: Update SETUP.md with TA-Lib installation"

# Bad commit messages
git commit -m "updates"
git commit -m "fix bug"
git commit -m "WIP"
```

---

## Submitting Changes

### Pull Request Process

1. **Update your branch**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**:
   - Go to GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template

### PR Template

```markdown
## Summary
Brief description of changes

## Changes Made
- Change 1
- Change 2
- Change 3

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Tested locally
- [ ] Added tests
- [ ] Updated documentation

## Screenshots (if applicable)
...
```

### PR Review Process

- PRs require at least one approval
- Address review comments
- Keep PR updated with main branch
- Be patient and respectful

---

## Coding Standards

### Python Style Guide

Follow PEP 8 with these modifications:

```python
# Line length: 127 characters max
max_line_length = 127

# Use double quotes for strings
good = "This is a string"
bad = 'This is a string'

# Use f-strings for formatting
good = f"Token price: ${price}"
bad = "Token price: ${}".format(price)
```

### File Organization

```python
"""
🌙 Moon Dev's Agent Name
Brief description
"""

# Standard library imports
import os
import sys
from datetime import datetime

# Third-party imports
import pandas as pd
from termcolor import cprint

# Local imports
from config import *
from nice_funcs import token_overview
from models.model_factory import ModelFactory

# Constants
CONSTANT_NAME = "value"

# Classes
class AgentName:
    pass

# Functions
def helper_function():
    pass

# Main execution
if __name__ == "__main__":
    main()
```

### Naming Conventions

```python
# Files
agent_name.py           # Snake case for files
StrategyClass.py        # PascalCase for classes

# Variables
token_address           # Snake case
USD_BALANCE            # CAPS for constants

# Functions
def get_token_price():  # Snake case
    pass

# Classes
class TradingAgent:     # PascalCase
    pass
```

---

## Agent Development

### Creating a New Agent

1. **Use the agent template**:

```python
"""
🌙 Moon Dev's [Agent Name]
[Brief description of what this agent does]
"""

import os
from termcolor import cprint
from models.model_factory import ModelFactory
from config import *

class AgentName:
    """[Agent purpose]"""

    def __init__(self):
        """Initialize agent"""
        self.model = ModelFactory.create_model('anthropic')
        cprint("🤖 Agent Name initialized", "cyan")

    def run(self):
        """Main agent logic"""
        try:
            # Your logic here
            cprint("✅ Agent completed successfully", "green")
        except Exception as e:
            cprint(f"❌ Error: {str(e)}", "red")

    def analyze(self, data):
        """Analyze data with AI"""
        system_prompt = "You are an expert..."
        user_content = f"Analyze this: {data}"

        response = self.model.generate_response(
            system_prompt,
            user_content,
            temperature=0.7,
            max_tokens=1024
        )

        return response.content

if __name__ == "__main__":
    agent = AgentName()
    agent.run()
```

2. **Agent Requirements**:
   - Must be < 800 lines
   - Must work standalone (runnable independently)
   - Must use ModelFactory for AI
   - Must handle errors gracefully
   - Must output to `src/data/[agent_name]/`

3. **Add to documentation**:
   - Update `README.md` agent list
   - Add usage example
   - Document configuration options

### Agent Best Practices

```python
# ✅ Good: Clear, focused agents
class SentimentAgent:
    """Analyzes Twitter sentiment for tokens"""
    # Single responsibility

# ❌ Bad: Do-everything agents
class SuperAgent:
    """Does sentiment, trading, risk, and portfolio"""
    # Too many responsibilities
```

---

## Testing

### Manual Testing

Before submitting:

```bash
# 1. Validate configuration
python scripts/validate_config.py

# 2. Test your changes
python src/agents/your_agent.py

# 3. Check syntax
python -m py_compile src/agents/your_agent.py

# 4. Run main orchestrator (if applicable)
python src/main.py
```

### Test Checklist

- [ ] Agent runs without errors
- [ ] Configuration validation passes
- [ ] Documentation updated
- [ ] No API keys exposed
- [ ] Code follows style guide
- [ ] Pre-commit hooks pass

### Integration Testing

```bash
# Test with minimal config
# Test error handling
# Test with missing API keys
# Test with invalid inputs
```

---

## Documentation

### When to Update Documentation

Update docs when you:
- Add a new agent
- Change configuration options
- Add dependencies
- Modify setup process
- Fix bugs affecting setup

### Documentation Files

| File | When to Update |
|------|----------------|
| `README.md` | New agents, major features |
| `SETUP.md` | Setup process changes |
| `TROUBLESHOOTING.md` | Common issues |
| `CLAUDE.md` | Development patterns |
| `src/agents/README.md` | Agent documentation |

### Documentation Style

```markdown
## Clear Headings

Use descriptive headings with emojis where appropriate.

### Code Examples

Provide working code examples:

\`\`\`python
# Example code
agent = TradingAgent()
agent.run()
\`\`\`

### Lists

- Use bullet points for lists
- Keep items concise
- Maintain parallel structure
```

---

## Specific Contribution Areas

### 🤖 Adding AI Model Support

1. Create new model file in `src/models/`
2. Inherit from `BaseModel`
3. Implement required methods
4. Add to ModelFactory
5. Update `src/models/README.md`
6. Add API key to `.env_example`

### 📊 Adding Trading Strategies

1. Create strategy in `src/strategies/`
2. Implement `generate_signals()` method
3. Add docstring with description
4. Test with backtest
5. Document usage

### 🔧 Adding Utility Scripts

1. Create script in `scripts/`
2. Add docstring and usage
3. Make executable (`chmod +x`)
4. Update `scripts/README.md`
5. Add to CI/CD if applicable

### 📚 Improving Documentation

1. Identify gaps or unclear sections
2. Make improvements
3. Test instructions
4. Submit PR with `docs:` prefix

---

## Common Issues

### Pre-commit Hooks Failing

```bash
# Update hooks
pre-commit autoupdate

# Run manually
pre-commit run --all-files

# Skip if necessary (not recommended)
git commit --no-verify -m "message"
```

### Merge Conflicts

```bash
# Update from upstream
git fetch upstream
git rebase upstream/main

# Resolve conflicts
# Edit conflicting files
git add .
git rebase --continue
```

### Failed CI/CD

- Check GitHub Actions logs
- Fix issues locally
- Push updates
- CI will re-run automatically

---

## Getting Help

### Resources

- **Documentation**: Read all `.md` files in root
- **Discord**: http://moondev.com
- **YouTube**: [@moondevonyt](https://www.youtube.com/@moondevonyt)
- **GitHub Issues**: For bugs and features

### Asking Good Questions

Include:
- What you're trying to do
- What you expected
- What actually happened
- Steps to reproduce
- Your environment (OS, Python version)
- Relevant code snippets

**Good Question:**
> I'm adding a new agent for whale tracking. It runs standalone but crashes in main.py with "ModuleNotFoundError: No module named 'whale_agent'". I've added it to src/agents/ and it imports in Python shell. Running Python 3.10.9 on Ubuntu.

**Bad Question:**
> My code doesn't work. Help?

---

## Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes
- Community shoutouts in Discord

Significant contributors may be featured in:
- YouTube videos
- Project documentation
- Special Discord roles

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

## Questions?

Join the [Moon Dev Discord](http://moondev.com) and ask in #contributors channel.

---

🌙 **Thank you for contributing to democratizing AI agent development!**

*Built with love by the Moon Dev community*
