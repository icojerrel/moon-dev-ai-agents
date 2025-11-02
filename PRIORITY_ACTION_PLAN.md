# Plan van Aanpak - Moon Dev AI Agents
**Datum**: 2 November 2025
**Status**: Draft v1.0
**Branch**: `claude/create-priority-plan-011CUiNn1HRzGDewCQzfQirb`

---

## Executive Summary

Dit document beschrijft een prioriteitsgebaseerd actieplan voor het verbeteren en onderhouden van het Moon Dev AI Agents trading systeem. Na analyse van de codebase zijn **5 kritieke gebieden** geïdentificeerd die onmiddellijke aandacht vereisen, plus **12 additionele verbeterpunten** voor langetermijn succes.

**Huidige Projectstatus**: 🟡 Functional but needs refactoring
- **Sterke Punten**: Modulaire architectuur, 30+ gespecialiseerde agents, goede LLM abstractie
- **Zwakke Punten**: Code duplicatie, inconsistente error handling, oversized files, geen tests

---

## Prioriteitsniveaus & Tijdsinschatting

| Prioriteit | Beschrijving | Totaal Effort | Tijdsbestek |
|-----------|--------------|---------------|-------------|
| 🔴 **P0 - Critical** | Systeem stabiliteit & maintainability | ~40 uur | 1-2 weken |
| 🟠 **P1 - High** | Code quality & developer experience | ~30 uur | 2-3 weken |
| 🟡 **P2 - Medium** | Features & optimalisaties | ~25 uur | 3-4 weken |
| 🟢 **P3 - Low** | Nice-to-have verbeteringen | ~20 uur | Backlog |

**Totaal geschat**: ~115 uur werk over 8-12 weken

---

# 🔴 P0: CRITICAL PRIORITIES (Week 1-2)

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

## 2. Standardisatie LLM API Calls via ModelFactory
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

## 3. Fix Error Handling Anti-patterns
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

## 4. Reduce Oversized Agent Files
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

## 5. Fix Configuration Duplication
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

## 6. Implement Testing Infrastructure
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

## 7. Resolve Gemini Integration Issue
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

## 8. Create Agent Implementation Template
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

## 9. Dependency Management Cleanup
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

## 10. Implement Strategies System
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

## 11. Data Cleanup & Management
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

## 12. Logging Framework Implementation
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

## 13. Performance Monitoring Dashboard
**Effort**: 8 uur

### Actie Items:
- [ ] Create Streamlit/Gradio dashboard
- [ ] Real-time agent status display
- [ ] Performance metrics (API latency, success rate, PnL)
- [ ] Alert system voor errors

---

## 14. Agent Communication Protocol
**Effort**: 6 uur

### Actie Items:
- [ ] Design inter-agent messaging system
- [ ] Shared memory/state management
- [ ] Event bus voor agent coordination
- [ ] Example: Risk agent broadcasts "HALT TRADING" → all agents listen

---

## 15. Documentation Improvements
**Effort**: 4 uur

### Actie Items:
- [ ] Architecture diagram (system overview)
- [ ] Data flow documentation
- [ ] Troubleshooting guide
- [ ] Video tutorials voor common tasks

---

## 16. Code Quality Tooling
**Effort**: 3 uur

### Actie Items:
- [ ] Setup pre-commit hooks
  - Black (formatting)
  - Flake8 (linting)
  - MyPy (type checking)
- [ ] Add type hints to core functions
- [ ] Enforce code style in CI

---

## 17. Database Migration
**Effort**: 12 uur (major change)

### Actie Items:
- [ ] Replace CSV/JSON storage met SQLite/PostgreSQL
- [ ] Schema design voor agent results
- [ ] Migration scripts voor existing data
- [ ] Query interface voor analysis

---

# Implementation Roadmap

## Month 1: Stabilization (P0)
**Week 1-2**: Critical fixes
- Agent consolidation
- ModelFactory migration
- Error handling fixes

**Deliverables**:
- ✅ Single version per agent
- ✅ 90%+ API calls via ModelFactory
- ✅ Zero bare except blocks
- ✅ All agents <800 lines

---

## Month 2: Quality (P1)
**Week 3-4**: Testing & infrastructure
- Test suite implementation
- Gemini fix
- Dependency cleanup

**Week 5**: Developer experience
- Agent template
- Documentation updates

**Deliverables**:
- ✅ 60%+ test coverage
- ✅ CI/CD pipeline active
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
- **1 Senior Developer**: 115 hours (3 months @ 10 hrs/week)
- **OR 2 Developers**: 60 hours (6 weeks @ 5 hrs/week each)

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

Voor immediate impact (<4 uur):

1. **Fix config duplicates** (30 min)
2. **Create .github/CODEOWNERS** (15 min)
3. **Add .editorconfig voor consistency** (15 min)
4. **Setup pre-commit hook template** (1 uur)
5. **Create agent deprecation guide** (1 uur)
6. **Add logging to top 5 agents** (2 uur)

**Total**: 5.5 uur voor 6 improvements

---

# Conclusie

Dit plan biedt een **gestructureerde aanpak** om de Moon Dev AI Agents codebase te transformeren van een functional maar fragiele systeem naar een **maintainable, testable, en scalable** platform.

**Aanbevolen Start**: Begin met P0 items in volgorde zoals gepresenteerd. Elke P0 item bouwt voort op de vorige en creëert een solide fundatie voor P1/P2 work.

**Next Steps**:
1. Review dit plan met het team
2. Prioritize items based on business needs
3. Create GitHub issues voor elk action item
4. Start met Quick Wins voor momentum
5. Begin P0 Week 1 implementation

**Vragen?** Raadpleeg de project documentation of open een GitHub discussion.

---

*Document Version*: 1.0
*Last Updated*: 2025-11-02
*Author*: Claude Code Analysis
*Status*: Ready for Review
