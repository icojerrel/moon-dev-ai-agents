# Testing Directory

This directory contains test suites for the Moon Dev AI Agents project.

## 🧪 Available Tests

### 1. Memory Integration Tests

**File**: `test_memory_integration.py`
**Purpose**: Unit tests for MemoriSDK integration
**Tests**: 7 comprehensive tests
**Runtime**: ~30 seconds

**Run**:
```bash
python tests/test_memory_integration.py
```

**What it tests**:
- MemoriSDK installation
- Memory configuration
- Memory initialization (5 agent types)
- Database stats
- Agent integration
- Disable flag
- Custom database paths

---

### 2. Full MemoriSDK Integration Tests

**File**: `test_memorisdk_full.py`
**Purpose**: Comprehensive Phase 1+2 validation
**Tests**: 9 test categories covering all 10 agents
**Runtime**: ~5 minutes

**Run**:
```bash
python tests/test_memorisdk_full.py
```

**What it tests**:
1. **Setup & Environment** - Conda, MemoriSDK installation
2. **Unit Test Suite** - Runs test_memory_integration.py
3. **Phase 1 Agents** - chat_agent, trading_agent, risk_agent
4. **Phase 2 Shared Agents** - sentiment, whale, funding (market analysis pool)
5. **Phase 2 Individual Agents** - strategy, tweet, copybot, solana
6. **Memory Configuration** - memory_config.py module
7. **Database Creation** - Verify memory directory and databases
8. **Graceful Degradation** - Test without MemoriSDK
9. **Documentation** - Verify all docs exist

**Output**:
- Console output with colored results
- Test report saved to `tests/reports/memorisdk_test_report_TIMESTAMP.txt`
- Exit code 0 (success) or 1 (failure)

---

## 📊 Test Reports

Test reports are automatically saved to `tests/reports/` directory.

**Report includes**:
- Test summary (passed/failed/skipped)
- Pass rate percentage
- Detailed results for each test
- Recommendations for next steps
- Decision: Ready for Phase 3? Yes/No

**Example**:
```
tests/reports/
├── memorisdk_test_report_20251112_140530.txt
├── memorisdk_test_report_20251112_151245.txt
└── ...
```

---

## 🎯 Testing Workflow

### Before Running Tests

```bash
# 1. Activate conda environment
conda activate tflow

# 2. Ensure MemoriSDK is installed
pip install memorisdk

# 3. Verify environment
python -c "from memorisdk import Memori; print('✅ Ready!')"
```

### Run Tests

```bash
# Quick test (unit tests only)
python tests/test_memory_integration.py

# Full test suite (comprehensive)
python tests/test_memorisdk_full.py
```

### Interpret Results

**All tests pass** ✅:
- Ready to merge to main
- Can proceed to Phase 3
- Production-ready

**Some tests fail** ⚠️:
- Review failed tests
- Fix issues
- Re-run tests
- Do NOT proceed to Phase 3

**Setup errors** ❌:
- Check conda environment
- Install MemoriSDK
- Verify Python version
- Check file permissions

---

## 🔍 Test Categories Explained

### Unit Tests (test_memory_integration.py)

**Focus**: Internal memory system functionality

**Tests**:
1. Installation check
2. Configuration loading
3. Memory initialization
4. Database stats
5. Agent imports
6. Disable flag
7. Custom paths

**When to run**: After code changes to memory_config.py

---

### Integration Tests (test_memorisdk_full.py)

**Focus**: Full system validation

**Tests**:
1. Environment setup
2. All agent imports
3. Memory databases
4. Documentation completeness
5. Graceful degradation

**When to run**: Before merging, before Phase 3

---

## 🐛 Common Test Failures

### MemoriSDK not installed

**Error**: `ModuleNotFoundError: No module named 'memorisdk'`

**Fix**:
```bash
conda activate tflow
pip install memorisdk
```

---

### Wrong conda environment

**Error**: `Not in 'tflow' environment`

**Fix**:
```bash
conda activate tflow
# Then re-run tests
```

---

### Import errors

**Error**: `Failed to import agent module`

**Fix**:
- Check agent file exists
- Verify no syntax errors
- Check dependencies installed

---

### Database permission errors

**Error**: `Cannot write to /src/data/memory/`

**Fix**:
```bash
# Check directory exists and is writable
mkdir -p src/data/memory
chmod 755 src/data/memory
```

---

## 📝 Adding New Tests

### For new agents:

1. Add to `AGENTS_TO_TEST` dict in `test_memorisdk_full.py`
2. Specify agent file, database, and name
3. Re-run full test suite

### For new features:

1. Create new test function in `test_memorisdk_full.py`
2. Add to main test runner
3. Update expected test count
4. Document in this README

---

## 🎓 Test Best Practices

### Before Committing Code

```bash
# Always run tests before committing
python tests/test_memorisdk_full.py

# If all pass, commit
git add .
git commit -m "Your message"
git push
```

### Before Merging PR

```bash
# Full test suite must pass
python tests/test_memorisdk_full.py

# Review test report
cat tests/reports/memorisdk_test_report_*.txt | tail -1
```

### Before Starting Phase 3

```bash
# ALL tests must pass 100%
python tests/test_memorisdk_full.py

# Exit code must be 0
echo $?  # Should print: 0
```

---

## 📊 Test Coverage

### Current Coverage

**Phase 1+2**: 100%
- 10 agents tested
- 8 databases verified
- All memory configs checked
- Documentation validated

**Phase 3**: 0% (not yet implemented)

### Target Coverage

**Phase 3**: Add tests for:
- Memory analytics dashboard
- A/B testing framework
- Cross-agent queries
- Memory management tools
- PostgreSQL migration

---

## 🚀 CI/CD Integration

### GitHub Actions (Future)

```yaml
name: MemoriSDK Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup conda
        uses: conda-incubator/setup-miniconda@v2
        with:
          environment-file: environment.yml
      - name: Install MemoriSDK
        run: pip install memorisdk
      - name: Run tests
        run: python tests/test_memorisdk_full.py
```

---

## 📚 Additional Resources

- **MemoriSDK Docs**: `../MEMORISDK_QUICKSTART.md`
- **Implementation Notes**: `../MEMORISDK_IMPLEMENTATION_NOTES.md`
- **Phase 2 Summary**: `../PHASE2_COMPLETE_SUMMARY.md`
- **Phase 3 Plan**: `../PHASE3_PLAN.md`

---

## 🎯 Quick Reference

```bash
# Quick test
python tests/test_memory_integration.py

# Full test (before merge/Phase 3)
python tests/test_memorisdk_full.py

# View latest report
cat tests/reports/memorisdk_test_report_*.txt | tail -1

# Clean old reports
rm tests/reports/*.txt
```

---

**Last Updated**: 2025-11-12
**Status**: Test suite complete for Phase 1+2
**Next**: Run tests before proceeding to Phase 3
