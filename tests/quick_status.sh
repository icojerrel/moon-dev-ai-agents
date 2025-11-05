#!/bin/bash
echo "════════════════════════════════════════════════════════════"
echo "🌙 Moon Dev's 24-Hour Test - Live Status"
echo "════════════════════════════════════════════════════════════"
echo ""
date +"⏰ Huidige tijd: %Y-%m-%d %H:%M:%S UTC"
echo ""

# Check if test is running
if pgrep -f test_24h_trading.py > /dev/null; then
    PID=$(pgrep -f test_24h_trading.py | head -1)
    echo "✅ Test Status: RUNNING (PID: $PID)"
    
    # Get CPU and memory
    CPU=$(ps aux | grep $PID | grep -v grep | awk '{print $3}')
    MEM=$(ps aux | grep $PID | grep -v grep | awk '{print $4}')
    echo "   CPU: ${CPU}% | Memory: ${MEM}%"
else
    echo "❌ Test Status: NOT RUNNING"
fi

echo ""
echo "📊 Progress:"
CYCLES=$(grep -c "Test Cycle #" tests/test_24h_live.log 2>/dev/null || echo "0")
echo "   Completed Cycles: $CYCLES"

echo ""
echo "🔄 Latest Cycle:"
grep "Test Cycle #" tests/test_24h_live.log 2>/dev/null | tail -1 || echo "   No cycles yet"

echo ""
echo "💰 Account Status:"
grep "Account Balance:" tests/test_24h_live.log 2>/dev/null | tail -1 || echo "   No data yet"

echo ""
echo "🎯 Recent Decisions:"
grep -E "(Analyzing|optimal)" tests/test_24h_live.log 2>/dev/null | tail -5

echo ""
echo "⚠️  Recent Errors:"
ERROR_COUNT=$(grep -c "❌" tests/test_24h_live.log 2>/dev/null || echo "0")
echo "   Total Errors: $ERROR_COUNT"
if [ $ERROR_COUNT -gt 0 ]; then
    grep "❌" tests/test_24h_live.log 2>/dev/null | tail -3
fi

echo ""
echo "⏰ Next Check:"
NEXT=$(grep "Next run at" tests/test_24h_live.log 2>/dev/null | tail -1 | cut -d' ' -f5)
if [ ! -z "$NEXT" ]; then
    echo "   $NEXT UTC"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
