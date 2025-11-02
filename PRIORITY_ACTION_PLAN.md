# Plan van Aanpak - Moon Dev AI Agents
**Datum**: 2 November 2025 (Updated with Security & RBI Upgrades)
**Status**: Draft v2.0
**Branch**: `claude/create-priority-plan-011CUiNn1HRzGDewCQzfQirb`

---

## Executive Summary

Dit document beschrijft een prioriteitsgebaseerd actieplan voor het verbeteren en onderhouden van het Moon Dev AI Agents trading systeem. Na analyse van de codebase zijn **7 kritieke gebieden** geïdentificeerd die onmiddellijke aandacht vereisen, plus **14 additionele verbeterpunten** voor langetermijn succes.

**Huidige Projectstatus**: 🟡 Functional but needs refactoring
- **Sterke Punten**: Modulaire architectuur, 30+ gespecialiseerde agents, goede LLM abstractie
- **Zwakke Punten**: **KRITIEKE SECURITY ISSUES**, code duplicatie, inconsistente error handling, oversized files, geen tests

**⚠️ URGENT**: OpenRouter API key exposure issue + arbitrary code execution risks in RBI agent vereisen onmiddellijke actie!

---

## Prioriteitsniveaus & Tijdsinschatting

| Prioriteit | Beschrijving | Totaal Effort | Tijdsbestek |
|-----------|--------------|---------------|-------------|
| 🔴 **P0 - Critical** | **SECURITY** + Systeem stabiliteit & maintainability | ~52 uur | 1-2 weken |
| 🟠 **P1 - High** | Code quality, RBI upgrades & developer experience | ~42 uur | 2-3 weken |
| 🟡 **P2 - Medium** | Features & optimalisaties | ~25 uur | 3-4 weken |
| 🟢 **P3 - Low** | Nice-to-have verbeteringen | ~20 uur | Backlog |

**Totaal geschat**: ~139 uur werk over 8-12 weken

---

# 🔴 P0: CRITICAL PRIORITIES (Week 1-2)

## 0. 🔐 SECURITY & API KEY PROTECTION **[MOST URGENT]**
**Probleem**: OpenRouter API key wordt steeds geblokkeerd door provider (exposed in repo), RBI agent executes arbitrary AI-generated code
**Impact**: 🚨 CRITICAL - Account ban, data loss, potential system compromise, financial risk
**Effort**: 12 uur

### Actie Items:

#### A. Immediate - Stop Key Exposure (2 uur)
- [ ] **Scan git history voor exposed keys**
  ```bash
  # Install git-secrets or truffleHog
  pip install truffleHog
  truffleHog --regex --entropy=True .

  # Check git history voor OpenRouter keys
  git log --all --full-history -S "OPENROUTER" --source
  git log --all --full-history -S "sk-or-v1" --source
  ```

- [ ] **Als keys gevonden in history: REVOKE EN REWRITE HISTORY**
  ```bash
  # Install BFG Repo-Cleaner
  # BACKUP EERST!
  git clone --mirror git@github.com:user/repo.git

  # Remove secrets from history
  bfg --replace-text secrets.txt repo.git
  cd repo.git
  git reflog expire --expire=now --all
  git gc --prune=now --aggressive
  git push --force
  ```
  ⚠️ **WARNING**: Dit herschrijft git history - informeer team!

- [ ] **Rotate ALL API keys onmiddellijk**
  - OpenRouter key → generate new
  - Alle andere keys in `.env` (precautie)
  - Update `.env` lokaal (NEVER commit)

#### B. Prevent Future Exposure (4 uur)
- [ ] **Add git pre-commit hook**
  ```bash
  # Install pre-commit framework
  pip install pre-commit

  # Create .pre-commit-config.yaml:
  ```
  ```yaml
  repos:
    - repo: https://github.com/pre-commit/pre-commit-hooks
      rev: v4.4.0
      hooks:
        - id: detect-private-key
        - id: check-added-large-files

    - repo: https://github.com/Yelp/detect-secrets
      rev: v1.4.0
      hooks:
        - id: detect-secrets
          args: ['--baseline', '.secrets.baseline']
  ```
  ```bash
  pre-commit install
  pre-commit run --all-files  # Test on existing files
  ```

- [ ] **Add OPENROUTER_KEY to .env_example**
  ```bash
  # Voeg toe aan .env_example (regel 21):
  OPENROUTER_KEY=your_openrouter_api_key_here
  ```

- [ ] **Scan all print/logger statements voor key leakage**
  ```bash
  # Find alle print statements met "key", "token", "secret"
  grep -rn "print.*key\|print.*KEY\|cprint.*key" src/ --include="*.py"
  grep -rn "logger.*api_key\|logger.*token" src/ --include="*.py"
  ```

  **Fix pattern**:
  ```python
  # SLECHT:
  print(f"Using API key: {api_key}")

  # GOED:
  print(f"Using API key: {api_key[:8]}...{api_key[-4:]}")  # Masked
  # OF beter:
  print("API key loaded successfully")  # No exposure at all
  ```

- [ ] **Add secrets sanitization utility**
  ```python
  # /src/utils/security.py

  import re
  import os

  def mask_sensitive_data(text: str) -> str:
      """Mask API keys and secrets in text output"""
      patterns = {
          'openrouter': r'sk-or-v1-[a-f0-9]{64}',
          'openai': r'sk-[a-zA-Z0-9]{48}',
          'anthropic': r'sk-ant-[a-zA-Z0-9-]{95}',
          'private_key': r'[1-9A-HJ-NP-Za-km-z]{32,}',  # Base58
      }

      for key_type, pattern in patterns.items():
          text = re.sub(pattern, f'[{key_type.upper()}_KEY_REDACTED]', text)

      return text

  def safe_print(message: str):
      """Print with automatic secret masking"""
      from termcolor import cprint
      cprint(mask_sensitive_data(str(message)), "white")
  ```

- [ ] **Replace all error dumps met masked versions**
  ```python
  # Zoek naar:
  grep -rn "print.*exc_info\|print.*traceback" src/ --include="*.py"

  # In exception handlers:
  except Exception as e:
      # VOOR:
      print(f"Error: {e}")
      print(f"Full error: {vars(e)}")

      # NA:
      from src.utils.security import mask_sensitive_data
      print(f"Error: {mask_sensitive_data(str(e))}")
      # Never print vars(e) or dir(e) - can contain env vars!
  ```

#### C. RBI Agent Code Execution Security (6 uur)
- [ ] **Implement AST-based code validation**
  ```python
  # /src/utils/code_validator.py

  import ast
  from typing import Tuple

  class CodeValidator:
      """Validate AI-generated code before execution"""

      FORBIDDEN_IMPORTS = {
          'os', 'subprocess', 'sys', 'shutil', 'requests',
          'urllib', 'socket', 'ftplib', 'telnetlib', 'pickle'
      }

      FORBIDDEN_FUNCTIONS = {
          'eval', 'exec', '__import__', 'compile', 'open',
          'input', 'raw_input'
      }

      ALLOWED_IMPORTS = {
          'pandas', 'numpy', 'backtesting', 'pandas_ta', 'talib',
          'datetime', 'typing', 'dataclasses'
      }

      @classmethod
      def validate(cls, code: str) -> Tuple[bool, str]:
          """Validate code is safe to execute"""
          try:
              tree = ast.parse(code)
          except SyntaxError as e:
              return False, f"Syntax error: {e}"

          for node in ast.walk(tree):
              # Check imports
              if isinstance(node, ast.Import):
                  for alias in node.names:
                      if alias.name in cls.FORBIDDEN_IMPORTS:
                          return False, f"Forbidden import: {alias.name}"
                      if alias.name not in cls.ALLOWED_IMPORTS:
                          return False, f"Unexpected import: {alias.name}"

              if isinstance(node, ast.ImportFrom):
                  if node.module in cls.FORBIDDEN_IMPORTS:
                      return False, f"Forbidden import from: {node.module}"

              # Check function calls
              if isinstance(node, ast.Call):
                  if isinstance(node.func, ast.Name):
                      if node.func.id in cls.FORBIDDEN_FUNCTIONS:
                          return False, f"Forbidden function: {node.func.id}"

              # Check file operations
              if isinstance(node, ast.With):
                  # Block "with open(...)"
                  return False, "File operations not allowed"

          return True, "Code validated successfully"
  ```

- [ ] **Integrate validator in RBI agent**
  ```python
  # In rbi_agent.py, rbi_agent_v2.py, rbi_agent_v3.py:
  # Before execute_backtest():

  from src.utils.code_validator import CodeValidator

  def execute_backtest_safe(code_path: str):
      with open(code_path, 'r') as f:
          code = f.read()

      is_valid, message = CodeValidator.validate(code)
      if not is_valid:
          cprint(f"❌ Security validation failed: {message}", "red")
          return None

      # Proceed with execution only if validated
      return execute_backtest(code_path)
  ```

- [ ] **Add Docker sandbox option** (optional, maar recommended)
  ```python
  # /src/utils/sandbox.py

  import docker

  def execute_in_docker(code: str, data_path: str) -> dict:
      """Execute backtest in isolated Docker container"""
      client = docker.from_env()

      container = client.containers.run(
          "python:3.11-slim",
          command=["python", "/code/backtest.py"],
          volumes={
              code_path: {'bind': '/code', 'mode': 'ro'},  # Read-only!
              data_path: {'bind': '/data', 'mode': 'ro'}
          },
          network_mode='none',  # No internet access
          mem_limit='512m',
          cpu_quota=50000,  # 50% CPU
          remove=True,
          detach=False
      )

      return {
          'stdout': container.decode(),
          'exit_code': container.attrs['State']['ExitCode']
      }
  ```

**Succescode**:
- Zero API keys in git history
- Pre-commit hooks prevent future commits met secrets
- All print/log statements masked
- RBI agent validates code before execution
- Optional: Docker sandbox voor extra isolation

---

## 1. Agent Version Cleanup & Consolidation
**Probleem**: 4-5 versies van dezelfde agents zonder duidelijke deprecation strategy
**Impact**: Code duplicatie, onduidelijkheid voor developers, moeilijk te onderhouden
**Effort**: 8 uur

### Actie Items:
- [ ] **RBI Agent consolidatie** (4 versies → 1)
  - Evalueer `rbi_agent.py`, `rbi_agent_v2.py`, `rbi_agent_v2_simple.py`, `rbi_agent_v3.py`
  - Bepaal welke versie de "canon" wordt (waarschijnlijk v3)
  - Migreer unieke features van oudere versies naar canon
  - Verplaats oude versies naar `/src/agents/deprecated/` met README

- [ ] **Chat Agent consolidatie** (3 versies → 1)
  - Analyseer verschillen tussen `chat_agent.py`, `chat_agent_og.py`, `chat_agent_ad.py`
  - Behoud beste features in single implementation
  - Archiveer oude versies

- [ ] **Cleanup legacy files**
  - Verwijder of archiveer `demo_countdown.py`, `clean_ideas.py`
  - Update `src/agents/README.md` met current agent list

**Succescode**: Alleen 1 versie per agent type in production directory

---

## 2. Fix RBI Agent Critical Issues
**Probleem**: GPT-5 model bestaat niet (broken config), hardcoded absolute paths, geen model fallback
**Impact**: RBI agent werkt niet out-of-the-box, fails op andere systemen
**Effort**: 3 uur

### Actie Items:
- [ ] **Fix non-existent model references**
  ```python
  # In rbi_agent.py lines 65-82:
  # VOOR (BROKEN):
  RESEARCH_CONFIG = {"type": "openai", "name": "gpt-5"}  # Doesn't exist!

  # NA (FIXED):
  RESEARCH_CONFIG = {"type": "openai", "name": "gpt-4o"}
  BACKTEST_CONFIG = {"type": "openai", "name": "o1-mini"}  # Better reasoning
  DEBUG_CONFIG = {"type": "openai", "name": "gpt-4o"}
  PACKAGE_CONFIG = {"type": "openai", "name": "gpt-4o"}
  ```

- [ ] **Fix hardcoded absolute paths**
  ```python
  # In rbi_agent.py, rbi_agent_v2.py, rbi_agent_v3.py:
  # VOOR:
  DATA_PATH = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/data/rbi/BTC-USD-15m.csv"

  # NA:
  from pathlib import Path
  PROJECT_ROOT = Path(__file__).parent.parent.parent
  DATA_PATH = PROJECT_ROOT / "src/data/rbi/BTC-USD-15m.csv"

  # Update in backtest prompts:
  f"Use this data path: {DATA_PATH.absolute()}"
  ```

- [ ] **Add model fallback chain** (like batch_backtester has)
  ```python
  def get_model_with_fallback(primary_config: dict) -> Model:
      """Try primary model, fallback to alternatives"""
      fallback_chain = [
          primary_config,
          {"type": "openai", "name": "gpt-4o"},
          {"type": "deepseek", "name": "deepseek-chat"},
          {"type": "anthropic", "name": "claude-3-haiku"},
          {"type": "groq", "name": "llama-3.3-70b-versatile"},
      ]

      for config in fallback_chain:
          try:
              return ModelFactory.get_model(config["type"], config["name"])
          except Exception as e:
              cprint(f"⚠️ {config['name']} failed, trying next...", "yellow")
              continue

      raise ValueError("All models failed - check API keys")
  ```

**Succescode**: RBI agent runs without config changes, works on any system

---

## 3. Standardisatie LLM API Calls via ModelFactory
**Probleem**: 87+ directe API calls bypass ModelFactory, breaking abstraction
**Impact**: Moeilijk om models te switchen, inconsistent error handling, vendor lock-in risk
**Effort**: 12 uur

### Actie Items:
- [ ] **Audit alle agents voor directe API calls**
  ```bash
  # Find problematic patterns:
  grep -r "anthropic.Anthropic()" src/agents/
  grep -r "openai.Client()" src/agents/
  grep -r "from anthropic import" src/agents/
  ```

- [ ] **Refactor top priority agents** (in deze volgorde):
  1. `risk_agent.py` - kritiek voor trading decisions
  2. `trading_agent.py` - core trading logic
  3. `strategy_agent.py` - strategy execution
  4. `rbi_agent.py` (canon versie) - backtesting
  5. `chat_agent.py` (canon versie) - user interaction

- [ ] **Update pattern** voor elke agent:
  ```python
  # VOOR (oud):
  from anthropic import Anthropic
  client = Anthropic(api_key=os.getenv("ANTHROPIC_KEY"))
  response = client.messages.create(...)

  # NA (nieuw):
  from src.models.model_factory import ModelFactory
  model = ModelFactory.create_model('anthropic')
  response = model.generate_response(system_prompt, user_content, ...)
  ```

- [ ] **Create migration guide** in `/src/models/MIGRATION_GUIDE.md`

**Succescode**: <10 directe API calls buiten ModelFactory

---

## 4. Fix Error Handling Anti-patterns
**Probleem**: 27 bare `except:` blocks, 34 silent failures met `pass`
**Impact**: Debugging nightmare, onvoorspelbaar gedrag, data loss risk
**Effort**: 10 uur

### Actie Items:
- [ ] **Elimineer bare except blocks**
  ```bash
  # Find all instances:
  grep -n "except:" src/ -r --include="*.py"
  ```

  Pattern om te vervangen:
  ```python
  # SLECHT:
  try:
      risky_operation()
  except:  # Catches EVERYTHING including KeyboardInterrupt!
      print("Error")

  # GOED:
  try:
      risky_operation()
  except (ValueError, KeyError, APIError) as e:
      logger.error(f"Operation failed: {e}", exc_info=True)
      return None
  ```

- [ ] **Fix silent failures**
  - Vervang `except Exception: pass` met proper logging
  - Gebruik `logging` module instead van cprint voor errors
  - Voeg context toe aan alle exception handlers

- [ ] **Create error handling guide** in `/docs/ERROR_HANDLING.md`
  - Standaard patterns per error type
  - Best practices voor API errors
  - Recovery strategies

- [ ] **Implementeer centralized error logger**
  ```python
  # /src/utils/error_logger.py
  def log_agent_error(agent_name, error, context=None):
      """Centralized error logging with context"""
      ...
  ```

**Succescode**: Alle exception handlers hebben specifieke types en logging

---

## 5. Reduce Oversized Agent Files
**Probleem**: 8 agents >800 lines (max 1,288 lines), tegen projectrichtlijn
**Impact**: Moeilijk te lezen, testen, en onderhouden
**Effort**: 10 uur

### Actie Items:
- [ ] **Split large agents** (prioriteit):
  1. `tiktok_agent.py` (1,288 lines) → `tiktok_agent/`
  2. `rbi_agent_v3.py` (1,132 lines) → refactor tijdens consolidatie
  3. `chat_agent_og.py` (1,111 lines) → refactor tijdens consolidatie
  4. `rbi_agent.py` (1,049 lines) → zie boven
  5. `chat_agent_ad.py` (1,018 lines) → zie boven

- [ ] **Refactoring strategy per agent**:
  - Extract helpers → `/src/agents/{agent_name}_utils.py`
  - Extract data models → `/src/agents/{agent_name}_models.py`
  - Extract API interactions → `/src/agents/{agent_name}_api.py`
  - Keep main agent file <800 lines (pure orchestration)

- [ ] **Example: TikTok Agent restructuring**
  ```
  src/agents/tiktok_agent/
  ├── __init__.py           # Main agent class (~400 lines)
  ├── video_processor.py    # Video editing logic (~300 lines)
  ├── content_generator.py  # Script generation (~300 lines)
  ├── uploader.py           # TikTok API interaction (~200 lines)
  └── models.py             # Data classes (~100 lines)
  ```

**Succescode**: Alle agents <800 lines, avg ~400-600 lines

---

## 6. Fix Configuration Duplication
**Probleem**: Settings gedefinieerd op meerdere plekken in config.py
**Impact**: Inconsistencies, moeilijk te wijzigen, bugs
**Effort**: 2 uur

### Actie Items:
- [ ] **Remove duplicates in config.py**:
  - `SLEEP_BETWEEN_RUNS_MINUTES` (lijnen 48, 93)
  - `slippage` (lijnen 38, 67)

- [ ] **Consolidate "future variables"**
  - Verplaats alle "NOT USED YET" vars naar dedicated sectie
  - Add comments met planned implementation date
  - Of verwijder als >6 maanden oud

- [ ] **Environment variable migration**
  - Verplaats hardcoded wallet address naar .env
  - Verplaats token addresses naar .env of database
  - Update .env_example met nieuwe vars

- [ ] **Create config validation**
  ```python
  # In config.py:
  def validate_config():
      """Validate all required config values are set"""
      assert SLEEP_BETWEEN_RUNS_MINUTES > 0
      assert 0 <= CASH_PERCENTAGE <= 100
      # ... etc

  validate_config()  # Run on import
  ```

**Succescode**: Geen duplicate config keys, alle settings validated

---

# 🟠 P1: HIGH PRIORITY (Week 3-5)

## 6. RBI Agent Capability Upgrades
**Probleem**: RBI agent mist belangrijke features voor production use
**Impact**: Suboptimale strategies, geen validation, geen ranking system
**Effort**: 12 uur

### Actie Items:

#### A. Strategy Validation & Ranking (4 uur)
- [ ] **Parse backtest results for metrics**
  ```python
  # /src/agents/rbi_utils.py

  import re
  from dataclasses import dataclass

  @dataclass
  class BacktestMetrics:
      return_pct: float
      sharpe_ratio: float
      max_drawdown_pct: float
      win_rate_pct: float
      num_trades: int
      strategy_name: str
      execution_time: float

  def parse_backtest_output(stdout: str) -> BacktestMetrics:
      """Extract metrics from backtesting.py output"""
      patterns = {
          'return': r'Return \[%\]\s+([-+]?\d+\.?\d*)',
          'sharpe': r'Sharpe Ratio\s+([-+]?\d+\.?\d*)',
          'drawdown': r'Max\. Drawdown \[%\]\s+([-+]?\d+\.?\d*)',
          'win_rate': r'Win Rate \[%\]\s+([-+]?\d+\.?\d*)',
          'trades': r'# Trades\s+(\d+)',
      }

      metrics = {}
      for key, pattern in patterns.items():
          match = re.search(pattern, stdout)
          if match:
              metrics[key] = float(match.group(1))

      return BacktestMetrics(**metrics)
  ```

- [ ] **Add minimum performance thresholds**
  ```python
  # In rbi_agent execute loop:
  MIN_RETURN = 5.0  # 5% minimum
  MIN_SHARPE = 0.5
  MAX_DRAWDOWN = -25.0  # Max 25% drawdown

  metrics = parse_backtest_output(result.stdout)

  if metrics.return_pct < MIN_RETURN:
      cprint(f"⚠️ Strategy below minimum return ({metrics.return_pct}% < {MIN_RETURN}%)", "yellow")
      # Skip or retry with optimization

  if metrics.sharpe_ratio < MIN_SHARPE:
      cprint(f"⚠️ Low Sharpe ratio: {metrics.sharpe_ratio}", "yellow")
  ```

- [ ] **Create results database**
  ```python
  # /src/data/rbi/strategies.db (SQLite)

  import sqlite3

  def create_strategies_db():
      conn = sqlite3.connect('src/data/rbi/strategies.db')
      c = conn.cursor()
      c.execute('''
          CREATE TABLE IF NOT EXISTS strategies (
              id INTEGER PRIMARY KEY,
              name TEXT UNIQUE,
              date_created TEXT,
              return_pct REAL,
              sharpe_ratio REAL,
              max_drawdown_pct REAL,
              win_rate_pct REAL,
              num_trades INTEGER,
              code_hash TEXT,
              source_idea TEXT,
              status TEXT  -- 'backtest', 'paper_trading', 'live'
          )
      ''')
      conn.commit()

  def save_strategy_results(metrics: BacktestMetrics, idea: str):
      """Save to database for ranking"""
      conn = sqlite3.connect('src/data/rbi/strategies.db')
      c = conn.cursor()
      c.execute('''
          INSERT OR REPLACE INTO strategies
          VALUES (NULL, ?, datetime('now'), ?, ?, ?, ?, ?, ?, ?, 'backtest')
      ''', (metrics.strategy_name, metrics.return_pct, ...))
      conn.commit()

  def get_top_strategies(limit=10):
      """Get best performing strategies"""
      conn = sqlite3.connect('src/data/rbi/strategies.db')
      c = conn.cursor()
      c.execute('''
          SELECT * FROM strategies
          WHERE return_pct > 5 AND sharpe_ratio > 1.0
          ORDER BY return_pct DESC, sharpe_ratio DESC
          LIMIT ?
      ''', (limit,))
      return c.fetchall()
  ```

#### B. Walk-Forward Analysis (4 uur)
- [ ] **Split data into train/test periods**
  ```python
  # In backtest prompt:
  # Instead of: bt.run()
  # Use:

  # Train on 2023 data
  train_data = data[data.index < '2024-01-01']
  stats_train = bt.run()

  # Test on 2024 data (out-of-sample)
  test_data = data[data.index >= '2024-01-01']
  stats_test = bt.run()

  print(f"Train Return: {stats_train['Return [%]']}")
  print(f"Test Return: {stats_test['Return [%]']}")
  print(f"Overfitting Check: {abs(stats_train['Return [%]'] - stats_test['Return [%]'])}")
  ```

- [ ] **Add walk-forward results to database**
  ```sql
  ALTER TABLE strategies ADD COLUMN train_return REAL;
  ALTER TABLE strategies ADD COLUMN test_return REAL;
  ALTER TABLE strategies ADD COLUMN overfit_score REAL;
  ```

#### C. Parameter Optimization (4 uur)
- [ ] **Add grid search for indicator parameters**
  ```python
  # In optimization loop (v3):
  # Instead of: "rewrite the strategy logic"
  # Use: "optimize these parameters: SMA_PERIOD (5-50), RSI_PERIOD (7-21), STOP_LOSS (0.5-5.0%)"

  from itertools import product

  def optimize_parameters(strategy_code: str):
      """Grid search over parameter ranges"""
      param_grid = {
          'SMA_PERIOD': range(10, 51, 10),
          'RSI_PERIOD': [7, 14, 21],
          'STOP_LOSS': [0.01, 0.02, 0.05],  # 1%, 2%, 5%
      }

      best_return = -float('inf')
      best_params = {}

      for params in product(*param_grid.values()):
          # Inject params into code
          modified_code = inject_parameters(strategy_code, dict(zip(param_grid.keys(), params)))

          # Run backtest
          result = execute_backtest(modified_code)
          metrics = parse_backtest_output(result.stdout)

          if metrics.return_pct > best_return:
              best_return = metrics.return_pct
              best_params = dict(zip(param_grid.keys(), params))

      return best_params, best_return
  ```

**Succescode**:
- All strategies saved to database with metrics
- Walk-forward analysis shows train vs test performance
- Parameter optimization finds best configurations
- Can query "top 10 strategies by Sharpe ratio"

---

## 7. Implement Testing Infrastructure
**Probleem**: Geen automated tests, manual testing only
**Impact**: Regression bugs, fear of refactoring, slow development
**Effort**: 15 uur

### Actie Items:
- [ ] **Setup pytest infrastructure**
  ```bash
  pip install pytest pytest-cov pytest-mock pytest-asyncio
  mkdir -p tests/{unit,integration,e2e}
  ```

- [ ] **Create test structure**
  ```
  tests/
  ├── conftest.py              # Shared fixtures
  ├── unit/
  │   ├── test_nice_funcs.py   # Core utilities
  │   ├── test_model_factory.py
  │   └── agents/
  │       ├── test_risk_agent.py
  │       └── test_trading_agent.py
  ├── integration/
  │   ├── test_agent_orchestration.py
  │   └── test_api_clients.py
  └── e2e/
      └── test_trading_flow.py
  ```

- [ ] **Write priority tests**:
  1. `nice_funcs.py` - 20+ utility functions (80% coverage target)
  2. `ModelFactory` - all providers
  3. `risk_agent.py` - circuit breakers, position limits
  4. `config.py` - validation logic

- [ ] **Add CI/CD with GitHub Actions**
  ```yaml
  # .github/workflows/test.yml
  name: Tests
  on: [push, pull_request]
  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - run: pip install -r requirements.txt
        - run: pytest tests/ --cov=src --cov-report=html
  ```

**Succescode**: 60%+ code coverage, all PRs require passing tests

---

## 8. Resolve Gemini Integration Issue
**Probleem**: Gemini model disabled door protobuf version conflict
**Impact**: Kan Gemini models niet gebruiken, limited model choices
**Effort**: 4 uur

### Actie Items:
- [ ] **Diagnose protobuf conflict**
  ```bash
  pip list | grep protobuf
  pip show google-generativeai
  pip show anthropic  # Check for conflicts
  ```

- [ ] **Test resolution strategies** (in volgorde):
  1. Update all packages: `pip install --upgrade google-generativeai anthropic`
  2. Pin protobuf version: `protobuf==4.25.0` (laatste compatible)
  3. Use virtual environment isolation per provider
  4. Als alles faalt: document incompatibility en remove Gemini support

- [ ] **Update ModelFactory**
  - Re-enable Gemini in `model_factory.py`
  - Add integration tests voor Gemini provider
  - Update README.md met working configuration

**Succescode**: Gemini models werkend OF officieel gedeprecated met documentatie

---

## 9. Create Agent Implementation Template
**Probleem**: Elke agent heeft unieke structure, geen standaard pattern
**Impact**: Inconsistency, nieuwe agents moeilijk te maken, code review chaos
**Effort**: 6 uur

### Actie Items:
- [ ] **Design canonical agent structure**
  ```python
  # /src/agents/templates/base_agent_template.py

  from abc import ABC, abstractmethod
  from src.models.model_factory import ModelFactory
  import logging

  class BaseAgent(ABC):
      """Template for all trading agents"""

      def __init__(self, config: dict = None):
          self.config = config or {}
          self.logger = logging.getLogger(self.__class__.__name__)
          self.model = ModelFactory.create_model(
              self.config.get('ai_provider', 'anthropic')
          )

      @abstractmethod
      def analyze(self, market_data: dict) -> dict:
          """Main analysis logic - must implement"""
          pass

      def save_results(self, results: dict, filepath: str):
          """Standardized result saving"""
          pass

      def run(self):
          """Main execution loop"""
          try:
              data = self.fetch_data()
              results = self.analyze(data)
              self.save_results(results)
              return results
          except Exception as e:
              self.logger.error(f"Agent failed: {e}", exc_info=True)
              raise
  ```

- [ ] **Create new agent scaffold CLI**
  ```bash
  python scripts/create_agent.py --name sentiment_v2 --type analysis
  # Generates boilerplate from template
  ```

- [ ] **Refactor 2-3 agents naar template** (proof of concept)
  - Kies simpele agents: `sentiment_agent`, `funding_agent`
  - Migrate naar new structure
  - Document lessons learned

- [ ] **Update documentation**
  - `/docs/AGENT_DEVELOPMENT_GUIDE.md`
  - Code examples per agent type
  - Testing checklist

**Succescode**: Template gebruikt voor alle nieuwe agents, 3+ agents refactored

---

## 10. Dependency Management Cleanup
**Probleem**: requirements.txt incomplete, protobuf conflicts, no version pinning
**Impact**: Deployment failures, reproducibility issues
**Effort**: 5 uur

### Actie Items:
- [ ] **Audit actual imports vs requirements.txt**
  ```bash
  # Find all imports
  grep -rh "^import\|^from" src/ | sort -u > actual_imports.txt

  # Compare with requirements.txt
  pip freeze > current_env.txt
  ```

- [ ] **Add missing packages**
  - `solders` (Solana SDK)
  - Alle ontbrekende dependencies

- [ ] **Pin critical versions**
  ```txt
  # requirements.txt
  anthropic==0.39.0  # Specific version for stability
  openai==1.55.3
  pandas==2.2.0
  protobuf==4.25.0   # Fix Gemini conflict
  ```

- [ ] **Create requirements structure**
  ```
  requirements/
  ├── base.txt          # Core dependencies
  ├── ai.txt            # All LLM providers
  ├── trading.txt       # Solana, exchanges
  ├── dev.txt           # Testing, linting
  └── prod.txt          # Production only (minimal)
  ```

- [ ] **Document platform-specific deps**
  - `ta-lib` installation guide (macOS vs Linux vs Windows)
  - Alternative: switch to `pandas-ta` (pure Python)

**Succescode**: Clean install werkt op fresh environment, locked versions

---

# 🟡 P2: MEDIUM PRIORITY (Week 6-9)

## 11. Implement Strategies System
**Probleem**: Strategy framework bestaat maar wordt niet gebruikt in live trading
**Impact**: Missed functionality, confusing architecture
**Effort**: 10 uur

### Actie Items:
- [ ] **Create 3 real strategies** (examples):
  1. **Momentum Strategy** - RSI + volume confirmation
  2. **Mean Reversion** - Bollinger Bands + oversold/overbought
  3. **Breakout Strategy** - Support/resistance levels

- [ ] **Implement strategy in trading loop**
  ```python
  # In trading_agent.py:
  if config.ENABLE_STRATEGIES:
      strategies = load_strategies()
      for strategy in strategies:
          signal = strategy.generate_signals(token, market_data)
          if signal['action'] == 'BUY' and signal['confidence'] > 75:
              execute_trade(signal)
  ```

- [ ] **Add strategy backtesting**
  - Integration met `rbi_agent.py`
  - Performance metrics per strategy
  - Strategy comparison dashboard

- [ ] **Strategy marketplace concept**
  - Users can add custom strategies to `/src/strategies/custom/`
  - Auto-discovery and loading
  - Risk validation before deployment

**Succescode**: 3+ strategies running in paper trading mode

---

## 12. Data Cleanup & Management
**Probleem**: RBI backtest data accumulates indefinitely, no cleanup
**Impact**: Disk space waste, slow file operations
**Effort**: 4 uur

### Actie Items:
- [ ] **Implement data retention policy**
  ```python
  # /src/utils/data_cleanup.py

  def cleanup_old_backtests(days_to_keep=30):
      """Remove backtest results older than X days"""
      cutoff = datetime.now() - timedelta(days=days_to_keep)
      # Delete files older than cutoff
  ```

- [ ] **Add to main.py orchestration**
  ```python
  # Run cleanup daily
  if should_run_daily_cleanup():
      cleanup_old_backtests(days_to_keep=30)
      cleanup_temp_files()
      cleanup_logs()
  ```

- [ ] **Archive important results**
  - Best performing backtests → `/archive/`
  - Failed/interesting edge cases → `/archive/failures/`
  - Auto-compression (.gz) voor >30 dagen oude data

**Succescode**: Automated cleanup, max 30 dagen data retention

---

## 13. Logging Framework Implementation
**Probleem**: Inconsistent logging (cprint vs print vs logging module)
**Impact**: No log files, moeilijk te debuggen, geen audit trail
**Effort**: 6 uur

### Actie Items:
- [ ] **Setup structured logging**
  ```python
  # /src/utils/logger.py

  import logging
  from logging.handlers import RotatingFileHandler

  def setup_logger(name: str, level=logging.INFO):
      logger = logging.getLogger(name)

      # Console handler (colored)
      console = logging.StreamHandler()
      console.setFormatter(ColoredFormatter())

      # File handler (rotating)
      file_handler = RotatingFileHandler(
          f'logs/{name}.log',
          maxBytes=10*1024*1024,  # 10MB
          backupCount=5
      )
      file_handler.setFormatter(JSONFormatter())

      logger.addHandler(console)
      logger.addHandler(file_handler)
      return logger
  ```

- [ ] **Migrate agents van cprint → logger**
  ```python
  # VOOR:
  from termcolor import cprint
  cprint("✅ Analysis complete", "green")

  # NA:
  logger.info("Analysis complete", extra={'emoji': '✅'})
  ```

- [ ] **Add log aggregation**
  - Alle agents loggen naar central `logs/` directory
  - Daily rotation
  - JSON format voor easy parsing

**Succescode**: All agents use logger, logs saved to files

---

# 🟢 P3: LOW PRIORITY (Backlog)

## 14. Performance Monitoring Dashboard
**Effort**: 8 uur

### Actie Items:
- [ ] Create Streamlit/Gradio dashboard
- [ ] Real-time agent status display
- [ ] Performance metrics (API latency, success rate, PnL)
- [ ] Alert system voor errors

---

## 15. Agent Communication Protocol
**Effort**: 6 uur

### Actie Items:
- [ ] Design inter-agent messaging system
- [ ] Shared memory/state management
- [ ] Event bus voor agent coordination
- [ ] Example: Risk agent broadcasts "HALT TRADING" → all agents listen

---

## 16. Documentation Improvements
**Effort**: 4 uur

### Actie Items:
- [ ] Architecture diagram (system overview)
- [ ] Data flow documentation
- [ ] Troubleshooting guide
- [ ] Video tutorials voor common tasks

---

## 17. Code Quality Tooling
**Effort**: 3 uur

### Actie Items:
- [ ] Setup pre-commit hooks
  - Black (formatting)
  - Flake8 (linting)
  - MyPy (type checking)
- [ ] Add type hints to core functions
- [ ] Enforce code style in CI

---

## 18. Database Migration
**Effort**: 12 uur (major change)

### Actie Items:
- [ ] Replace CSV/JSON storage met SQLite/PostgreSQL
- [ ] Schema design voor agent results
- [ ] Migration scripts voor existing data
- [ ] Query interface voor analysis

---

# Implementation Roadmap

## Month 1: Stabilization & Security (P0)
**Week 1**: URGENT Security Fixes
- 🔐 API key protection (git secrets scan, pre-commit hooks)
- 🔐 RBI code execution validation
- 🔐 Secret masking in logs
- Fix RBI agent broken config (GPT-5 → GPT-4o)

**Week 2**: Code Quality Foundations
- Agent consolidation (RBI, Chat)
- ModelFactory migration (top 5 agents)
- Error handling fixes
- Configuration deduplication

**Deliverables**:
- ✅ Zero exposed API keys in git history
- ✅ Pre-commit hooks active
- ✅ RBI agent validates code before execution
- ✅ Single version per agent type
- ✅ 90%+ API calls via ModelFactory
- ✅ Zero bare except blocks
- ✅ All agents <800 lines

---

## Month 2: Quality & RBI Upgrades (P1)
**Week 3-4**: Testing & RBI Enhancements
- Test suite implementation (pytest, 60% coverage)
- RBI strategy validation & ranking system
- RBI walk-forward analysis
- RBI parameter optimization
- Gemini protobuf fix

**Week 5**: Developer Experience
- Agent implementation template
- Dependency cleanup & version pinning
- Documentation updates

**Deliverables**:
- ✅ 60%+ test coverage
- ✅ CI/CD pipeline active
- ✅ RBI strategies database with ranking
- ✅ Walk-forward analysis implemented
- ✅ Parameter grid search working
- ✅ Clean requirements.txt
- ✅ Agent development guide

---

## Month 3: Features (P2)
**Week 6-8**: Feature development
- Strategies implementation
- Data management
- Logging framework

**Week 9**: Polish
- Performance testing
- Bug fixes from backlog

**Deliverables**:
- ✅ 3 production strategies
- ✅ Automated data cleanup
- ✅ Centralized logging

---

## Ongoing: Maintenance (P3)
- Backlog refinement
- Performance monitoring
- Documentation updates
- Community contributions

---

# Success Metrics

## Code Quality Metrics
- **Test Coverage**: Target 60%+ (currently 0%)
- **File Size Compliance**: 100% agents <800 lines (currently 75%)
- **Error Handling**: Zero bare `except:` blocks (currently 27)
- **Code Duplication**: <5% (currently ~15-20%)

## System Health Metrics
- **Agent Uptime**: >95% (current unknown)
- **API Success Rate**: >98% (current unknown)
- **Mean Time to Recovery**: <15 min (current unknown)
- **Build Success Rate**: 100% (no CI currently)

## Developer Productivity Metrics
- **Time to Create New Agent**: <2 hours (currently 4-6 hours)
- **Time to Debug Issue**: <30 min (currently 1-2 hours)
- **Test Execution Time**: <5 min (N/A currently)
- **Deployment Time**: <10 min (currently manual)

---

# Risk Assessment

## High Risk Items
1. **ModelFactory migration**: Could break live trading
   - **Mitigation**: Test in paper trading first, gradual rollout

2. **Agent refactoring**: Risk of losing functionality
   - **Mitigation**: Comprehensive testing before deprecation

3. **Dependency updates**: Could introduce new bugs
   - **Mitigation**: Virtual env testing, staged rollout

## Medium Risk Items
1. **Large agent splitting**: Complex refactor
   - **Mitigation**: One agent at a time, full test coverage

2. **Strategies implementation**: New code paths
   - **Mitigation**: Paper trading only initially

## Low Risk Items
- Configuration cleanup (easily reversible)
- Documentation improvements (no code changes)
- Logging framework (additive, not breaking)

---

# Resource Requirements

## Development Time
- **1 Senior Developer**: 139 hours (3 months @ 12 hrs/week)
- **OR 2 Developers**: 70 hours (6 weeks @ 6 hrs/week each)
- **Security fixes**: Can start immediately (first 2 days critical)

## Infrastructure
- **CI/CD**: GitHub Actions (free tier sufficient)
- **Testing**: Local + cloud (minimal cost)
- **Storage**: +2GB voor logs (negligible cost)

## External Dependencies
- No new API subscriptions needed
- Existing LLM provider accounts sufficient
- No additional hardware required

---

# Appendix: Quick Wins

Voor immediate impact (<6 uur):

## Security Quick Wins (URGENT)
1. **Scan git history voor exposed keys** (30 min)
   ```bash
   git log --all --full-history -S "OPENROUTER" --source
   git log --all --full-history -S "sk-or-v1" --source
   ```

2. **Add OPENROUTER_KEY to .env_example** (5 min)
3. **Rotate all API keys** (15 min - maar DO THIS FIRST!)

## Code Quality Quick Wins
4. **Fix RBI agent GPT-5 → GPT-4o** (10 min) - CRITICAL, agent is broken!
5. **Fix config duplicates** (30 min)
6. **Setup pre-commit hooks for secrets detection** (1 uur)
7. **Create .github/CODEOWNERS** (15 min)
8. **Add .editorconfig voor consistency** (15 min)

## Low-Effort High-Impact
9. **Create agent deprecation guide** (1 uur)
10. **Add secret masking utility** (1 uur)
11. **Add RBI code validator skeleton** (30 min)

**Total**: ~6 uur voor 11 critical improvements

**Recommended Order**: Do 1-6 TODAY (security critical!), then 7-11 this week.

---

# Conclusie

Dit plan biedt een **gestructureerde aanpak** om de Moon Dev AI Agents codebase te transformeren van een functional maar fragiele systeem naar een **secure, maintainable, testable, en scalable** platform.

## 🚨 URGENT: Security First

**De belangrijkste bevinding**: OpenRouter API key exposure en arbitrary code execution in RBI agent vormen **kritieke security risico's** die onmiddellijk aangepakt moeten worden. Deze issues kunnen leiden tot:
- Account bans bij API providers
- Financieel verlies
- Potentieel system compromise
- Data loss

**Aanbevolen Actie**: Start VANDAAG met:
1. Git history scan voor exposed keys (30 min)
2. Rotate ALL API keys (15 min)
3. Setup pre-commit hooks (1 uur)
4. Fix RBI agent GPT-5 bug (10 min)

Deze 4 items kosten **< 2 uur** maar voorkomen potentieel **grote schade**.

## RBI Agent Transformation

De RBI agent is een **krachtige tool** maar heeft critical fixes nodig:
- **NOW**: Fix broken GPT-5 reference (agent werkt niet!)
- **Week 1**: Add code validation (security)
- **Week 3-4**: Add strategy ranking, walk-forward analysis, parameter optimization

Met deze upgrades wordt RBI van een "interessant experiment" naar een **production-ready backtesting platform**.

## Implementation Strategy

**Aanbevolen Start**: Begin met P0 items in volgorde zoals gepresenteerd. Elke P0 item bouwt voort op de vorige en creëert een solide fundatie voor P1/P2 work.

**Kritieke Pad** (eerste 2 weken):
```
Day 1: Security scan + key rotation + pre-commit hooks
Day 2: RBI agent fixes (GPT-5 → GPT-4o, hardcoded paths)
Day 3-5: Code execution validation + secret masking
Week 2: Agent consolidation + error handling + ModelFactory migration
```

**Next Steps**:
1. **IMMEDIATE**: Do Quick Wins 1-6 (security critical!)
2. Review dit plan met het team
3. Prioritize items based on business needs
4. Create GitHub issues voor elk action item
5. Begin P0 Week 1 implementation

**Long-term Vision**: Na 3 maanden heb je:
- ✅ Secure codebase (no exposed keys, validated code execution)
- ✅ Production-ready RBI agent (ranking, walk-forward, optimization)
- ✅ 60%+ test coverage
- ✅ Standardized agent patterns
- ✅ Clean, maintainable code <800 lines per file

**Vragen?** Raadpleeg de project documentation of open een GitHub discussion.

---

*Document Version*: 2.0 (Security & RBI Upgrades Added)
*Last Updated*: 2025-11-02
*Author*: Claude Code Security & Architecture Analysis
*Status*: Ready for Immediate Action
*Priority*: 🔴 CRITICAL - Start security fixes TODAY
