#!/bin/bash

echo "=== DETAILED VIOLATION ANALYSIS ==="
echo ""

# Top 5 rules by violation count
echo "Top violations by rule:"
echo ""
for rule in PERF401 PLR2004 PLC0415 TRY003 TRY400; do
  total=$(uvx ruff check --select $rule . 2>/dev/null | wc -l)
  src_count=$(uvx ruff check --select $rule src/ 2>/dev/null | wc -l)
  test_count=$(uvx ruff check --select $rule tests/ 2>/dev/null | wc -l)
  ex_count=$(uvx ruff check --select $rule examples/ 2>/dev/null | wc -l)

  echo "$rule: $total total (src=$src_count, tests=$test_count, examples=$ex_count)"
done

echo ""
echo "=== Sample violations from src/ ==="
echo ""

echo "--- PERF401 (manual list comprehension) ---"
uvx ruff check --select PERF401 src/ 2>/dev/null | head -5
echo ""

echo "--- PLR2004 (magic values) ---"
uvx ruff check --select PLR2004 src/ 2>/dev/null | head -5
echo ""

echo "--- PLC0415 (import outside top-level) ---"
uvx ruff check --select PLC0415 src/ 2>/dev/null | head -5
echo ""

echo "--- TRY003 (raise vanilla args) ---"
uvx ruff check --select TRY003 src/ 2>/dev/null | head -5
echo ""

echo "--- ARG002 (unused method argument) ---"
uvx ruff check --select ARG002 src/ 2>/dev/null
