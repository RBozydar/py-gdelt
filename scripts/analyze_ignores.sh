#!/bin/bash
# Analyze each ignored rule to understand violations

RULES="TRY003 EM101 EM102 TRY400 PLC0415 PLR2004 PERF401 TRY300 SIM102 SIM105 TRY004 PLW2901 ARG002 S608 PLR0913"

for rule in $RULES; do
  echo "============================================"
  echo "Rule: $rule"
  echo "============================================"

  violations=$(uvx ruff check --select $rule . 2>/dev/null)
  count=$(echo "$violations" | grep -c "^src/")

  echo "Total violations in src/: $count"
  echo ""

  if [ $count -eq 0 ]; then
    echo "✅ No violations found - can remove from ignore list!"
  elif [ $count -lt 30 ]; then
    echo "All violations:"
    echo "$violations"
  else
    echo "Sample violations (first 20):"
    echo "$violations" | head -20
    echo ""
    echo "... (showing 20 of $count violations)"
  fi

  echo ""
  echo ""
done
