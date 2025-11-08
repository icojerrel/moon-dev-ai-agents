#!/bin/bash
# Moon Dev AI Trading Agents - Comprehensive Test Runner
# Run all tests in Docker sandbox environment

set -e  # Exit on error

echo "🌙 Moon Dev AI Trading System - Test Suite"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    TEST_NAME=$1
    COMMAND=$2

    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}Running: ${TEST_NAME}${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    TESTS_RUN=$((TESTS_RUN + 1))

    if $COMMAND; then
        echo -e "${GREEN}✅ PASSED: ${TEST_NAME}${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAILED: ${TEST_NAME}${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Clean up previous test runs
echo "🧹 Cleaning up previous test runs..."
docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true
rm -rf logs/test_* 2>/dev/null || true
echo ""

# Build test containers
echo "🔨 Building test containers..."
docker-compose -f docker-compose.test.yml build
echo ""

# Run tests
echo "🧪 Running Test Suite..."
echo ""

# Test 1: Mock MT5 Simulator
run_test "Mock MT5 Simulator" \
    "docker-compose -f docker-compose.test.yml run --rm test-mock-mt5"

# Test 2: Asset Detection
run_test "Asset Detection & Helpers" \
    "docker-compose -f docker-compose.test.yml run --rm test-asset-detection"

# Test 3: Sandbox Test Suite
run_test "Comprehensive Sandbox Tests" \
    "docker-compose -f docker-compose.test.yml run --rm test-sandbox"

# Test 4: Integration Tests (optional, requires API keys)
if [ "${RUN_INTEGRATION_TESTS}" = "true" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Integration tests enabled (requires API keys)${NC}"
    run_test "Integration Tests" \
        "docker-compose -f docker-compose.test.yml --profile integration run --rm test-integration"
else
    echo ""
    echo -e "${YELLOW}ℹ️  Skipping integration tests (set RUN_INTEGRATION_TESTS=true to enable)${NC}"
fi

# Clean up
echo ""
echo "🧹 Cleaning up test containers..."
docker-compose -f docker-compose.test.yml down -v
echo ""

# Print summary
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}TEST SUMMARY${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Total Tests Run: $TESTS_RUN"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    PASS_RATE=100
else
    PASS_RATE=$((TESTS_PASSED * 100 / TESTS_RUN))
fi

echo "Pass Rate: ${PASS_RATE}%"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}System is ready for deployment.${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}⚠️  ${TESTS_FAILED} test(s) failed.${NC}"
    echo -e "${RED}Please review and fix before deployment.${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi
