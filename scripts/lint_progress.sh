#!/bin/bash
# Audit linting status
# Run this to verify lint ignore rules are still appropriate

echo "=== Linting Status Report ==="
echo "Date: $(date)"
echo ""

echo "=== CHECKING FOR REGRESSIONS ==="
echo ""

# Rules that SHOULD have 0 violations (we fixed them)
FIXED_RULES=("PERF401" "EM101" "EM102" "TRY400")
REGRESSION_FOUND=false

for rule in "${FIXED_RULES[@]}"; do
    COUNT=$(uvx ruff check --select "$rule" src/ 2>&1 | grep -E "^Found [0-9]+ error" | grep -oE "[0-9]+" || echo "0")
    if [ "$COUNT" != "0" ] && [ -n "$COUNT" ]; then
        echo "❌ $rule: $COUNT violations (REGRESSION!)"
        REGRESSION_FOUND=true
    else
        echo "✅ $rule: 0 violations"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$REGRESSION_FOUND" = true ]; then
    echo "⚠️  REGRESSIONS DETECTED - Fix before committing!"
    exit 1
else
    echo "✅ All previously fixed rules still clean"
fi

echo ""
echo "=== INTENTIONAL STYLE IGNORES (current counts) ==="
echo ""

# PLR2004 - Magic values (intentionally ignored)
PLR2004_COUNT=$(uvx ruff check --select PLR2004 src/ 2>&1 | grep -E "^Found [0-9]+ error" | grep -oE "[0-9]+" || echo "0")
echo "PLR2004 (magic-value-comparison): $PLR2004_COUNT violations"
echo "  Status: Intentionally ignored - HTTP codes, column counts are self-documenting"

echo ""

# TRY003 - Verbose exception messages (intentionally ignored)
TRY003_COUNT=$(uvx ruff check --select TRY003 src/ 2>&1 | grep -E "^Found [0-9]+ error" | grep -oE "[0-9]+" || echo "0")
echo "TRY003 (raise-vanilla-args): $TRY003_COUNT violations"
echo "  Status: Intentionally ignored - Descriptive messages preferred"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "For full lint check: make lint"
