# 🚀 CODE AUDIT - ACTION ITEMS
## Moon Dev AI Agents Repository

**Priority: CRITICAL → HIGH → MEDIUM → LOW**

---

## 🔴 CRITICAL - FIX IMMEDIATELY (This Week)

### 1. API Path Traversal Vulnerability
**File:** `src/agents/api.py` - Line 126  
**Severity:** MEDIUM (Security)  
**Time Estimate:** 15 minutes

```python
# CURRENT (UNSAFE)
url = f'{self.base_url}/files/{filename}'

# FIX (SAFE)
import os
if '..' in filename or '/' in filename or '\\' in filename:
    raise ValueError("Invalid filename - contains path traversal characters")
safe_filename = os.path.basename(filename)
url = f'{self.base_url}/files/{safe_filename}'
```

**Test After Fix:**
```python
# Should work:
api.get_file('data.csv')  # ✓

# Should fail:
api.get_file('../../../etc/passwd')  # ✗
api.get_file('..\\..\\windows\\system32')  # ✗
```

---

### 2. Incomplete TODO Comment
**File:** `src/agents/tiktok_agent.py` - Line 92  
**Severity:** LOW  
**Time Estimate:** 5-30 minutes

**Current:**
```python
TODO -
```

**Action:** Either:
- Complete the TODO with a meaningful comment
- Remove the TODO line entirely
- Create a GitHub issue and reference it: `# TODO: Issue #123 - Add X feature`

---

### 3. Code Execution Risk Documentation
**File:** `src/agents/code_runner_agent.py` - Entire file  
**Severity:** HIGH (Security Design)  
**Time Estimate:** 30 minutes

**Add to top of file:**
```python
"""
⚠️ SECURITY WARNING ⚠️

This agent executes dynamically generated Python code. 
NEVER run this in production without proper sandboxing:

1. Use Docker container with restricted permissions
2. Set resource limits (CPU, memory, disk)
3. Block import of dangerous modules (os, subprocess, etc.)
4. Run as unprivileged user
5. Implement timeouts for code execution

Example Docker approach:
  docker run --rm --memory="512m" --cpus="0.5" --timeout 30 agent_image

DO NOT expose this to untrusted input directly!
"""
```

---

## 🟠 HIGH PRIORITY - Complete in 1-2 Weeks

### 4. Migrate risk_agent.py to ModelFactory
**File:** `src/agents/risk_agent.py` - Line 106  
**Files Affected:** 1  
**Time Estimate:** 2-3 hours

**Current Code (Line 106):**
```python
self.client = anthropic.Anthropic(api_key=anthropic_key)
```

**Change To:**
```python
from src.models.model_factory import model_factory

# In __init__:
self.model = model_factory.create_model('anthropic')
if not self.model:
    raise ValueError("Could not initialize Anthropic model")
```

**Update Usage:**
```python
# OLD (Line 299):
message = self.client.messages.create(
    model=self.ai_model,
    max_tokens=self.ai_max_tokens,
    temperature=self.ai_temperature,
    messages=[{"role": "user", "content": prompt}]
)
response_text = str(message.content)

# NEW:
response = self.model.generate_response(
    system_prompt="You are Moon Dev's Risk Management AI",
    user_content=prompt,
    temperature=self.ai_temperature,
    max_tokens=self.ai_max_tokens
)
response_text = response if isinstance(response, str) else str(response)
```

**Related Files (18 total - update after risk_agent.py):**
- src/agents/chartanalysis_agent.py
- src/agents/clips_agent.py
- src/agents/coingecko_agent.py
- src/agents/copybot_agent.py
- src/agents/focus_agent.py
- src/agents/funding_agent.py
- src/agents/fundingarb_agent.py
- src/agents/liquidation_agent.py
- src/agents/listingarb_agent.py
- src/agents/new_or_top_agent.py
- src/agents/rbi_agent_v2.py
- src/agents/rbi_agent_v3.py
- src/agents/stream_agent.py
- src/agents/tweet_agent.py
- src/agents/whale_agent.py
- + 3 others

---

### 5. Fix Bare except Blocks
**Files Affected:** 12 files  
**Time Estimate:** 1-2 hours total

**Files to Update:**
1. src/agents/api.py - Line 198
2. src/agents/backtest_runner.py
3. src/agents/chartanalysis_agent.py
4. src/agents/chat_agent_ad.py
5. src/agents/code_runner_agent.py
6. src/agents/polymarket_agent.py
7. src/agents/rbi_agent.py
8. src/agents/rbi_batch_backtester.py
9. src/agents/sniper_agent.py
10. src/agents/stream_agent.py
11. src/agents/tiktok_agent.py
12. src/agents/tx_agent.py

**Pattern to Fix:**
```python
# BEFORE (BAD):
try:
    # code
except:
    pass

# AFTER (GOOD):
try:
    # code
except (KeyError, ValueError, TypeError) as e:
    cprint(f"❌ Error processing data: {e}", "red")
except Exception as e:
    cprint(f"❌ Unexpected error: {e}", "red")
    traceback.print_exc()
```

---

### 6. Start Refactoring Oversized Agents
**Primary Target:** `rbi_agent.py` (1,049 lines)  
**Time Estimate:** 4-6 hours

**Split rbi_agent.py into:**

1. **rbi_agent.py** (Keep core, ~400 lines)
   - Main RBIAgent class
   - Main processing loop
   - Configuration handling

2. **rbi_research.py** (New, ~300 lines)
   - research_strategy()
   - get_idea_content()
   - get_youtube_transcript()
   - get_pdf_text()
   - clean_model_output()

3. **rbi_backtest.py** (New, ~250 lines)
   - create_backtest()
   - debug_backtest()
   - package_check()
   - BACKTEST_PROMPT, DEBUG_PROMPT, PACKAGE_PROMPT

4. **rbi_utils.py** (New, ~150 lines)
   - Utility functions
   - animate_progress()
   - run_with_animation()
   - chat_with_model()
   - get_model_id()

**Update imports in rbi_agent.py:**
```python
from src.agents.rbi_research import research_strategy, get_idea_content
from src.agents.rbi_backtest import create_backtest, debug_backtest, package_check
from src.agents.rbi_utils import chat_with_model, run_with_animation
```

---

## 🟡 MEDIUM PRIORITY - Complete in 1 Month

### 7. Consolidate RBI Agent Variants
**Files to Consolidate:** 6 files  
**Action:**
- [ ] Keep `rbi_agent.py` (base)
- [ ] Keep `rbi_agent_v3.py` (enhanced version)
- [ ] DELETE: `rbi_agent_v2.py` (older version)
- [ ] MERGE: `rbi_agent_pp.py` → consolidate into v3
- [ ] MERGE: `rbi_agent_pp_multi.py` → consolidate into v3
- [ ] DEPRECATE: `rbi_batch_backtester.py` (functionality move to v3)

**Time Estimate:** 4-6 hours

---

### 8. Expand BaseAgent Functionality
**File:** `src/agents/base_agent.py` (57 lines)  
**Time Estimate:** 2-3 hours

**Current:**
```python
class BaseAgent:
    def __init__(self, agent_type, use_exchange_manager=False):
        self.type = agent_type
        self.start_time = datetime.now()
        self.em = None
    
    def run(self):
        raise NotImplementedError()
```

**Expand To:**
```python
class BaseAgent:
    def __init__(self, agent_type, use_exchange_manager=False):
        self.type = agent_type
        self.start_time = datetime.now()
        self.em = None
        self.config = self._load_config()
        self.logger = self._setup_logging()
    
    def _load_config(self):
        """Load configuration from config.py"""
        from src.config import (
            MONITORED_TOKENS, EXCLUDED_TOKENS, AI_MODEL,
            SLEEP_BETWEEN_RUNS_MINUTES, usd_size, max_usd_order_size
        )
        return {
            'tokens': MONITORED_TOKENS,
            'excluded': EXCLUDED_TOKENS,
            'ai_model': AI_MODEL,
            'sleep_minutes': SLEEP_BETWEEN_RUNS_MINUTES,
            'position_size': usd_size,
            'max_order': max_usd_order_size,
        }
    
    def _setup_logging(self):
        """Setup logging for the agent"""
        import logging
        logger = logging.getLogger(self.type)
        return logger
    
    def safe_run(self):
        """Wrapper around run() with error handling"""
        try:
            return self.run()
        except Exception as e:
            self.logger.error(f"Error in {self.type}: {e}", exc_info=True)
            cprint(f"❌ {self.type} error: {e}", "red")
            raise
    
    def run(self):
        raise NotImplementedError("Each agent must implement its own run method")
```

---

### 9. Input Validation Improvements
**Files to Update:**
- [ ] rbi_agent.py - Add protocol validation for URLs (Line 816)
- [ ] api.py - Filename validation (already listed above as CRITICAL)
- [ ] trading_agent.py - Already good, no changes needed

**Time Estimate:** 1 hour

**rbi_agent.py fix (Line 816):**
```python
# BEFORE:
if "youtube.com" in idea_url or "youtu.be" in idea_url:

# AFTER:
from urllib.parse import urlparse
try:
    parsed = urlparse(idea_url)
    if not parsed.scheme in ('http', 'https'):
        raise ValueError("URL must use http or https")
    if "youtube.com" in parsed.netloc or "youtu.be" in parsed.netloc:
        # Process as YouTube
except Exception as e:
    raise ValueError(f"Invalid URL: {e}")
```

---

## 🟢 LOW PRIORITY - Nice to Have

### 10. Clean Up Legacy Files
**Files to Remove/Deprecate:**
- [ ] `src/agents/chat_agent_og.py` (1,111 lines)
  - First verify it's not used elsewhere
  - Check if functionality is in `chat_agent.py` (653 lines)
  - Remove if confirmed redundant

- [ ] `src/agents/rbi_agent_v2.py` (873 lines)
  - Will be consolidated in High Priority #7
  - Safe to delete after v3 consolidation

**Time Estimate:** 30 minutes verification + deletion

---

### 11. Add Unit Tests
**Start With:** 5 critical functions
- [ ] test_trading_agent.py
- [ ] test_risk_agent.py
- [ ] test_strategy_agent.py
- [ ] test_api.py
- [ ] test_swarm_agent.py

**Time Estimate:** 4-6 hours

**Example test structure:**
```python
# tests/test_trading_agent.py
import pytest
from src.agents.trading_agent import TradingAgent

def test_trading_agent_init():
    """Test agent initialization"""
    agent = TradingAgent()
    assert agent.model is not None
    assert isinstance(agent.recommendations_df, pd.DataFrame)

def test_exclude_tokens():
    """Test that excluded tokens are skipped"""
    agent = TradingAgent()
    # Test excluded token handling
```

---

### 12. Replace Wildcard Imports
**Files to Update:** 30+ files  
**Priority:** Low (works but not ideal)

**Example Fix:**
```python
# BEFORE:
from src.config import *

# AFTER:
from src.config import (
    MONITORED_TOKENS,
    EXCLUDED_TOKENS,
    AI_MODEL,
    SLEEP_BETWEEN_RUNS_MINUTES,
    usd_size,
    max_usd_order_size,
    slippage,
    USDC_ADDRESS,
)
```

**Time Estimate:** 2-3 hours (distribute across multiple PRs)

---

## 📊 Priority Summary Table

| Priority | Task | Files | Hours | Deadline |
|----------|------|-------|-------|----------|
| 🔴 CRITICAL | Fix path traversal | 1 | 0.25 | This week |
| 🔴 CRITICAL | Fix TODO | 1 | 0.5 | This week |
| 🔴 CRITICAL | Code execution warning | 1 | 0.5 | This week |
| 🟠 HIGH | Migrate to ModelFactory | 1+18 | 3 | 2 weeks |
| 🟠 HIGH | Fix bare excepts | 12 | 2 | 2 weeks |
| 🟠 HIGH | Start refactoring | 1 | 5 | 2 weeks |
| 🟡 MEDIUM | Consolidate RBI | 6 | 5 | 1 month |
| 🟡 MEDIUM | Expand BaseAgent | 1 | 2.5 | 1 month |
| 🟡 MEDIUM | Input validation | 2 | 1 | 1 month |
| 🟢 LOW | Clean up legacy | 2 | 0.5 | 2 months |
| 🟢 LOW | Add unit tests | 5 | 5 | 2 months |
| 🟢 LOW | Replace wildcards | 30+ | 3 | 3 months |

**Total Estimated Effort: 40-60 developer hours**

---

## 📋 Verification Checklist

After completing each item, verify with:

### Code Quality
- [ ] Run `pylint` on modified files
- [ ] Run `black` for formatting
- [ ] Check for new TODO/FIXME comments

### Security
- [ ] No new hardcoded credentials
- [ ] Input validation working
- [ ] Error messages don't expose sensitive data

### Testing
- [ ] Modified code tested locally
- [ ] Related agents still work
- [ ] No new warnings/errors in logs

### Documentation
- [ ] Updated CLAUDE.md if needed
- [ ] Added comments for complex changes
- [ ] Updated README if behavior changed

---

## 🎯 Success Metrics

After completing all items:

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Files under 800 lines | 41/54 (76%) | 54/54 (100%) | ❌ |
| ModelFactory adoption | 23/54 (43%) | 54/54 (100%) | ❌ |
| Bare except blocks | 12 files | 0 files | ❌ |
| Security issues | 3 critical | 0 critical | ❌ |
| Code duplication | High (6 RBI) | Low (2-3 RBI) | ❌ |
| Unit test coverage | ~5% | >60% | ❌ |
| Code quality grade | B+ (82/100) | A (90+/100) | ❌ |

---

## 👤 Suggested Assignment

**If multiple developers:**

- **Dev 1:** Critical fixes + ModelFactory migration
- **Dev 2:** Refactoring oversized agents  
- **Dev 3:** Input validation + error handling
- **Dev 4:** Unit tests + documentation

**If single developer:**
- Complete in priority order
- Aim for 2-3 hours per day
- Complete in 2-3 weeks

---

## 📞 Questions?

For clarification on any action item, check:
1. Full audit report: `CODE_AUDIT_REPORT.md`
2. Code examples above
3. Related files mentioned

---

**Generated:** November 13, 2025  
**By:** Code Audit System  
**Status:** Ready for Implementation

