# 🌙 Moon Dev's Code Review Agent

AI-powered code review agent die automatisch code analyseert, verbeteringen voorstelt en gedetailleerde rapporten genereert.

## Features

### 🎯 Review Types
- **Security**: Kwetsbaarheden, injection attacks, hardcoded secrets
- **Performance**: Algoritme efficiency, memory leaks, optimalisaties
- **Style**: PEP 8, naming conventions, code readability
- **Best Practices**: SOLID principes, design patterns, maintainability
- **All**: Comprehensive review van alle bovenstaande

### 🤖 AI Models
Ondersteunt alle models via ModelFactory:
- Claude (claude-3-5-haiku-latest) - Recommended
- GPT-4 (gpt-4o)
- DeepSeek (deepseek-reasoner) - Best for reasoning
- Groq (mixtral-8x7b-32768) - Fast
- Ollama (llama3.2) - Local
- xAI Grok (grok-4-fast-reasoning)

### 📊 Output Formats
- **Markdown**: Human-readable reports met emoji's
- **JSON**: Machine-readable voor integraties
- **CSV**: Data analysis in Excel/Pandas

### 🔧 Features
- Syntax validation voor Python files
- Git integration (review alleen gewijzigde files)
- Directory scanning met exclusion filters
- Severity levels (critical, high, medium, low)
- Code quality scores (0-100)
- Before/after code suggestions

## Installation

De agent is al geïnstalleerd als onderdeel van het Moon Dev AI Trading System. Alle dependencies zijn al aanwezig.

```bash
# Zorg dat je in de juiste conda environment zit
conda activate tflow

# Test of de agent werkt
python src/agents/code_review_agent.py --help
```

## Usage

### 1. Review een Enkel Bestand

```bash
# Basic review
python src/agents/code_review_agent.py src/agents/trading_agent.py

# Security-focused review
python src/agents/code_review_agent.py src/agents/trading_agent.py --type security

# Performance review met specifiek model
python src/agents/code_review_agent.py src/agents/trading_agent.py --type performance --model deepseek
```

### 2. Review een Hele Directory

```bash
# Review alle Python files in src/agents/
python src/agents/code_review_agent.py src/agents/

# Style review van strategieën
python src/agents/code_review_agent.py src/strategies/ --type style
```

### 3. Review Git Changes (Super Handig!)

```bash
# Review alleen files die je hebt gewijzigd
python src/agents/code_review_agent.py --git

# Security review van je changes
python src/agents/code_review_agent.py --git --type security

# Voor code review voordat je commit
git add .
python src/agents/code_review_agent.py --git
git commit -m "Your message"
```

### 4. Different Output Formats

```bash
# JSON output voor scripts
python src/agents/code_review_agent.py src/agents/ --format json

# CSV voor data analysis
python src/agents/code_review_agent.py src/agents/ --format csv
```

## Command Line Options

```
positional arguments:
  path                  File or directory to review

optional arguments:
  -h, --help            Show help message
  --type, -t            Review type: security, performance, style, best_practices, all (default: all)
  --model, -m           AI model type: claude, openai, deepseek, groq, ollama, xai (default: claude)
  --model-name          Specific model name (e.g., gpt-4o, deepseek-reasoner)
  --git, -g             Review only git-modified files
  --format, -f          Report format: markdown, json, csv (default: markdown)
```

## Python API Usage

```python
from src.agents.code_review_agent import CodeReviewAgent

# Initialize agent
agent = CodeReviewAgent(model_type="claude")

# Review single file
review = agent.analyze_file("src/agents/trading_agent.py", review_type="security")

# Review directory
reviews = agent.analyze_directory("src/agents/", review_type="all")

# Review git changes
reviews = agent.review_git_changes(review_type="all")

# Generate and save report
report_path = agent.save_report(reviews)
print(f"Report saved to: {report_path}")

# Generate custom format
markdown_report = agent.generate_report(reviews, format="markdown")
json_report = agent.generate_report(reviews, format="json")
csv_report = agent.generate_report(reviews, format="csv")
```

## Output Location

Alle rapporten worden opgeslagen in:
```
src/data/code_review/
├── reports/           # Review rapporten
│   ├── review_20250106_143022.md
│   ├── review_20250106_143022.json
│   └── review_20250106_143022.csv
└── fixes/            # Optionele auto-fixes (toekomstige feature)
```

## Example Output

### Markdown Report

```markdown
# Code Review Report

Generated: 2025-01-06 14:30:22

## Summary

- Files reviewed: 5
- Files with issues: 3
- Total issues: 12

### Issues by Severity

- 🔴 Critical: 1
- 🟠 High: 3
- 🟡 Medium: 6
- 🟢 Low: 2

## Detailed Results

### src/agents/trading_agent.py

**Review Type:** security
**Score:** 75/100

**Issues Found:** 4

#### 1. 🔴 Hardcoded API Key (Line 45)

**Description:** API key is hardcoded in source code, which is a security risk.

**Before:**
```python
api_key = "sk-1234567890abcdef"
```

**Suggestion:** Use environment variables to store API keys.

**After:**
```python
api_key = os.getenv("API_KEY")
```
```

### JSON Output

```json
[
  {
    "file": "src/agents/trading_agent.py",
    "review_type": "security",
    "model": "claude-3-5-haiku-latest",
    "timestamp": "2025-01-06T14:30:22.123456",
    "severity": "high",
    "score": 75,
    "issues": [
      {
        "line": 45,
        "type": "Hardcoded Secret",
        "severity": "critical",
        "description": "API key is hardcoded in source code",
        "suggestion": "Use environment variables",
        "code_before": "api_key = \"sk-1234567890abcdef\"",
        "code_after": "api_key = os.getenv(\"API_KEY\")"
      }
    ],
    "summary": "Found 4 security issues requiring attention"
  }
]
```

## Integration in CI/CD

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
echo "🔍 Running code review on changed files..."
python src/agents/code_review_agent.py --git --type security

if [ $? -ne 0 ]; then
    echo "❌ Code review found critical issues. Fix them before committing."
    exit 1
fi
```

### GitHub Actions

```yaml
name: AI Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run Code Review
        env:
          ANTHROPIC_KEY: ${{ secrets.ANTHROPIC_KEY }}
        run: |
          python src/agents/code_review_agent.py --git --format json > review.json
          cat review.json
```

## Tips & Tricks

### 1. Snelle Review Tijdens Development

```bash
# Alias in je .bashrc/.zshrc
alias review="python src/agents/code_review_agent.py --git --model groq"

# Nu gewoon:
review
```

### 2. Focused Reviews

```bash
# Alleen security voor kritieke files
python src/agents/code_review_agent.py src/nice_funcs.py --type security

# Style check voor nieuwe features
python src/agents/code_review_agent.py src/agents/new_agent.py --type style
```

### 3. Batch Reviews

```bash
# Review alle agents
for file in src/agents/*.py; do
    python src/agents/code_review_agent.py "$file" --type all
done
```

### 4. Compare Models

```bash
# Test verschillende models op dezelfde file
python src/agents/code_review_agent.py src/agents/trading_agent.py --model claude
python src/agents/code_review_agent.py src/agents/trading_agent.py --model deepseek
python src/agents/code_review_agent.py src/agents/trading_agent.py --model openai
```

## Best Practices

1. **Run security reviews** op kritieke files met trading logic
2. **Use --git flag** voor snelle reviews tijdens development
3. **DeepSeek model** is excellent voor reasoning over complex code
4. **Claude** is sneller voor routine reviews
5. **Save reports** voor later reference en trending analysis
6. **Review before committing** om problemen vroeg te vangen

## Troubleshooting

### "Failed to initialize model"
```bash
# Check je .env file
cat .env | grep ANTHROPIC_KEY

# Test model availability
python -c "from src.models import model_factory; print(model_factory.available_models)"
```

### "No files to review"
```bash
# Check of je in de juiste directory bent
pwd

# Check of er Python files zijn
ls -la src/agents/*.py
```

### Syntax Errors
```bash
# De agent detecteert syntax errors automatisch
# Fix ze eerst voordat je een review doet
python -m py_compile src/agents/your_file.py
```

## Future Features (Coming Soon)

- 🔧 **Auto-fix mode**: Automatisch fixes toepassen
- 📈 **Trending analysis**: Track code quality over time
- 🔄 **PR integration**: Automatische reviews op pull requests
- 🎯 **Custom rules**: Definieer je eigen review rules
- 📊 **Dashboard**: Web interface voor review history
- 🤝 **Team reports**: Aggregated metrics per developer

## Support

Voor vragen of issues:
- GitHub Issues: https://github.com/yourusername/moon-dev-ai-agents/issues
- Discord: [Your Discord Link]
- Documentation: See CLAUDE.md

## License

Part of Moon Dev AI Trading Agents - Open Source 🌙

---

Made with ❤️ by Moon Dev
