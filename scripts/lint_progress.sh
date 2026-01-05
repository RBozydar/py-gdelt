#!/bin/bash
# Audit linting technical debt progress
# Run this weekly during active development to track improvements

echo "=== Linting Technical Debt Progress ==="
echo "Date: $(date)"
echo ""

echo "=== INCREMENTAL TECHNICAL DEBT (Goal: Fix 20/week) ==="
echo ""

# PERF401 - List comprehensions
PERF401_COUNT=$(uvx ruff check --select PERF401 src/ 2>/dev/null | grep -c "^src/" || echo "0")
echo "PERF401 (manual-list-comprehension): $PERF401_COUNT violations"
if [ "$PERF401_COUNT" -eq 0 ]; then
    echo "  ✅ COMPLETE - Remove from ignore list!"
elif [ "$PERF401_COUNT" -lt 20 ]; then
    echo "  🎯 Almost done - fix remaining violations this week"
else
    echo "  📋 In progress - target: 20 fixes this week"
fi
echo ""

# EM101 - Raw strings in exceptions
EM101_COUNT=$(uvx ruff check --select EM101 src/ 2>/dev/null | grep -c "^src/" || echo "0")
echo "EM101 (raw-string-in-exception): $EM101_COUNT violations"
if [ "$EM101_COUNT" -eq 0 ]; then
    echo "  ✅ COMPLETE - Remove from ignore list!"
elif [ "$EM101_COUNT" -lt 20 ]; then
    echo "  🎯 Fix all remaining violations"
else
    echo "  📋 In progress"
fi
echo ""

# EM102 - F-strings in exceptions
EM102_COUNT=$(uvx ruff check --select EM102 src/ 2>/dev/null | grep -c "^src/" || echo "0")
echo "EM102 (f-string-in-exception): $EM102_COUNT violations"
if [ "$EM102_COUNT" -eq 0 ]; then
    echo "  ✅ COMPLETE - Remove from ignore list!"
elif [ "$EM102_COUNT" -lt 20 ]; then
    echo "  🎯 Fix all remaining violations"
else
    echo "  📋 In progress"
fi
echo ""

# Calculate total
TOTAL=$((PERF401_COUNT + EM101_COUNT + EM102_COUNT))
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TOTAL INCREMENTAL DEBT: $TOTAL violations"
echo ""

if [ "$TOTAL" -eq 0 ]; then
    echo "🎉 ALL INCREMENTAL DEBT RESOLVED!"
    echo "Next steps:"
    echo "  1. Remove PERF401, EM101, EM102 from pyproject.toml ignore list"
    echo "  2. Run 'make ci' to verify"
    echo "  3. Commit changes"
else
    WEEKS_REMAINING=$((TOTAL / 20 + 1))
    echo "Target completion: ~$WEEKS_REMAINING weeks at 20 fixes/week"
    echo ""
    echo "To fix violations this week:"
    echo "  1. Run: uvx ruff check --select PERF401,EM101,EM102 src/"
    echo "  2. Fix 20 violations (start with auto-fixable PERF401)"
    echo "  3. Run: make ci"
    echo "  4. Commit with message: 'refactor: reduce linting debt (20 violations fixed)'"
fi
