# Linting Cleanup and Configuration Audit

## Executive Summary

After comprehensive analysis of all 15 ignored linting rules, we found:

**🎉 Great News:**
- Current codebase has only **2 active violations** (TC003)
- Configuration is already excellent, just needs optimization

**📊 Key Findings:**
- **17 quick wins**: 5 rules with <10 violations each - can fix in 30 minutes
- **12 duplicate rules**: Cluttering config, easy to remove
- **50% ignore reduction possible**: 16 rules → 8 rules
- **245 total violations** across all ignored rules (detailed breakdown below)

**✅ Immediate Actions (1-2 hours):**
1. Fix 2 TC003 violations + 17 quick wins = **19 total fixes**
2. Remove 12 duplicate rules from config
3. Convert PLC0415 (177 violations) from global to per-file ignores
4. Reduce ignore list from 16 → 8 rules (50% reduction!)

**📈 Long-term (Q1 2026):**
- Fix 224 incremental debt violations (PERF401, EM101, EM102)
- Rate: 20 violations/week = done in ~11 weeks

**Final Result:** 6-rule ignore list (down from 16) - only justified permanent ignores + documented major technical debt.

---

## Overview

This plan addresses the linting configuration audit for py-gdelt, identifying duplicate rule entries, analyzing exclusions with actual violation data, and providing a systematic approach to maintain exceptional code quality standards.

## Current State Analysis

### Good News: Only 2 Active Violations! 🎉

```bash
$ uvx ruff check . --statistics
2	TC003	typing-only-standard-library-import
```

**Violations:**
- `src/py_gdelt/sources/fetcher.py:19` - `AsyncIterator` and `Iterator` should be in TYPE_CHECKING block
- **Impact:** Low - These are fixable with `--unsafe-fixes`
- **Effort:** 2 minutes to fix

### Configuration Quality Assessment

**Overall Rating:** ✅ **Excellent** - Comprehensive and well-documented

**Strengths:**
- 40+ rule categories enabled (very thorough)
- Well-justified ignores with inline comments
- Appropriate per-file overrides for tests/examples/notebooks
- Security rules enabled (S - bandit)
- Async rules (ASYNC) - critical for this async-first library
- Performance rules (PERF)
- Strict MyPy configuration

**Issues Identified:**

#### 1. **CRITICAL: Duplicate Rule Entries** (`pyproject.toml:63-116`)

The following rules are listed **twice** in the `select` array:

| Rule | Line 1 | Line 2 | Impact |
|------|--------|--------|--------|
| `"F"` (Pyflakes) | 66 | 85 | Harmless but confusing |
| `"I"` (isort) | 67 | 86 | Harmless but confusing |
| `"UP"` (pyupgrade) | 70 | 88 | Harmless but confusing |
| `"S"` (bandit) | 77 | 91 | Harmless but confusing |
| `"B"` (bugbear) | 68 | 93 | Harmless but confusing |
| `"C4"` (comprehensions) | 69 | 96 | Harmless but confusing |
| `"T20"` (print) | 78 | 104 | Harmless but confusing |
| `"SIM"` (simplify) | 72 | 110 | Harmless but confusing |
| `"TCH"` (type-checking) | 73 | 112 | Harmless but confusing |
| `"ARG"` (unused-args) | 71 | 113 | Harmless but confusing |
| `"PTH"` (pathlib) | 74 | 114 | Harmless but confusing |
| `"ERA"` (commented code) | 75 | 115 | Harmless but confusing |

**Why This Happened:** Likely from merging two configuration sources or iterative additions.

**Impact:** None functionally (Ruff deduplicates), but reduces maintainability.

## Exclusion Analysis: The Tough Eye 👁️

### 🔍 **ACTUAL VIOLATION ANALYSIS**

We ran a comprehensive audit of all 15 ignored rules to understand real violation counts:

```bash
$ uvx ruff check --select <ALL_IGNORED_RULES> . --statistics
245 total violations across all ignored rules
```

### Breakdown by Rule (src/ violations only)

| Rule | src/ | tests/ | examples/ | Total | Status |
|------|------|--------|-----------|-------|--------|
| **PLR2004** | 398 | 1 | 1 | 400 | 🔴 Major refactor |
| **TRY003** | 374 | 1 | 1 | 376 | 🔴 Major refactor |
| **TRY400** | 220 | 1 | 53 | 274 | 🔴 Major refactor |
| **PERF401** | 181 | 336 | 1 | 518 | 🟡 Incremental fix |
| **PLC0415** | 177 | 120 | 76 | 373 | 🟢 Convert to per-file |
| **EM102** | 24 | - | - | 24 | 🟡 Medium priority |
| **EM101** | 19 | - | - | 19 | 🟡 Medium priority |
| **ARG002** | 8 | - | - | 8 | ✅ Justified (protocols) |
| **TRY300** | 6 | - | - | 6 | 🎯 **FIX NOW** |
| **SIM102** | 4 | - | - | 4 | 🎯 **FIX NOW** |
| **PLW2901** | 3 | - | - | 3 | 🎯 **FIX NOW** |
| **S608** | 3 | - | - | 3 | ✅ Justified (BigQuery) |
| **SIM105** | 2 | - | - | 2 | 🎯 **FIX NOW** |
| **TRY004** | 2 | - | - | 2 | 🎯 **FIX NOW** |
| **PLR0913** | 1 | - | - | 1 | ✅ Justified (dataclass) |

---

### Category 1: 🎯 **QUICK WINS - Fix Immediately (<10 violations)**

These have so few violations they should be fixed right now:

| Rule | Violations | Sample | Auto-fixable? | Action |
|------|-----------|---------|---------------|---------|
| **TRY300** | 6 | try-except-else pattern | ⚠️ Manual | Add else clauses to try blocks |
| **SIM102** | 4 | Collapsible if statements | ✅ Yes | `--fix` |
| **PLW2901** | 3 | Loop variable redefinition | ⚠️ Manual | Rename variables |
| **SIM105** | 2 | Use contextlib.suppress | ⚠️ Manual | Replace with suppress() |
| **TRY004** | 2 | Type-check improvements | ⚠️ Manual | Use TypeError explicitly |

**Total: 17 violations across 5 rules**

**Effort:** ~30 minutes to fix all of these manually.

**Example violations:**
```python
# TRY300 - Missing else clause
src/py_gdelt/parsers/events.py:125
# Should be: try...except...else to make success path explicit

# SIM102 - Collapsible if
src/py_gdelt/endpoints/context.py:197
# if condition1:
#     if condition2:  # Can collapse to: if condition1 and condition2:

# PLW2901 - Redefining loop variable
src/py_gdelt/parsers/gkg.py:45
# Reusing same variable name in nested loop - confusing
```

---

### Category 2: ✅ **JUSTIFIED - Keep as Global Ignores**

These violations are legitimate and should remain ignored globally:

| Rule | Violations | Why Justified | Sample |
|------|-----------|---------------|---------|
| **ARG002** | 8 | Protocol/interface compliance | `async def _build_url(self, **kwargs)` - base class defines signature |
| **S608** | 3 | BigQuery uses parameterized queries | Safe query builders, not string interpolation |
| **PLR0913** | 1 | Dataclass with many fields | Single dataclass constructor - acceptable |

**Example ARG002 violations:**
```python
# src/py_gdelt/endpoints/context.py:127
async def _build_url(self, **kwargs: Any) -> str:
    # Must accept **kwargs to match base class signature
    # Even though this endpoint doesn't use them
```

All 6 endpoints have this pattern - it's for protocol compliance.

---

### Category 3: 🟢 **CONVERT TO PER-FILE IGNORES**

| Rule | Violations | Reason | Affected Files |
|------|-----------|---------|----------------|
| **PLC0415** | 177 in src/ | Lazy imports for optional dependencies | `client.py`, `sources/fetcher.py` |

**Analysis:** This rule flags imports inside functions. In py-gdelt, these are intentional for:
1. **Optional dependencies** (BigQuery, pandas) - don't import if not installed
2. **Import cycle breaking** - avoid circular dependencies

**Current:**
```toml
ignore = ["PLC0415"]  # Global ignore
```

**Should be:**
```toml
[tool.ruff.lint.per-file-ignores]
"src/py_gdelt/client.py" = ["PLC0415"]  # BigQuery/pandas lazy imports
"src/py_gdelt/sources/fetcher.py" = ["PLC0415"]  # Optional dependency handling
"src/py_gdelt/endpoints/*.py" = ["PLC0415"]  # Some endpoints have conditional imports
```

**Benefit:** Catches accidental lazy imports in files where they shouldn't exist.

---

### Category 4: 🔴 **MAJOR REFACTORS - Document as Technical Debt**

These have 100+ violations and require significant refactoring:

| Rule | Violations | Effort | Keep Ignored? |
|------|-----------|--------|---------------|
| **PLR2004** | 398 | High | ✅ Yes - would require constants for all HTTP codes, limits, etc. |
| **TRY003** | 374 | Very High | ✅ Yes - would require exception class refactor |
| **TRY400** | 220 | Very High | ✅ Yes - architectural decision (logger vs raise) |

**PLR2004 Examples:**
```python
# src/py_gdelt/cache.py:330
if response.status_code == 200:  # Magic number
    # Would need: HTTP_OK = 200 constant

# src/py_gdelt/endpoints/base.py:172
if len(data) > 1000:  # Magic number
    # Would need: MAX_RESULTS = 1000 constant
```

**Verdict:** Keep these ignored. The refactor effort (398 violations!) outweighs the benefit. HTTP status codes like 200, 404 are self-documenting.

---

### Category 5: 🟡 **INCREMENTAL FIXES - Plan for Sprints**

| Rule | src/ Violations | Priority | Timeline |
|------|----------------|----------|----------|
| **PERF401** | 181 | Medium | Q1 2026 - 20 fixes/week |
| **EM101** | 19 | Low | Q2 2026 |
| **EM102** | 24 | Low | Q2 2026 |

**PERF401 - List comprehension opportunities:**
```python
# src/py_gdelt/endpoints/context.py:197
result = []
for item in data["themes"]:
    result.append(transform(item))

# Should be:
result = [transform(item) for item in data["themes"]]
```

**Verdict:** Worth fixing incrementally. 181 violations is manageable over time. ~10 fixes per week = done in Q1 2026.

---

### Category 6: 🎯 **Per-File Ignores - Already Well Structured**

Your existing per-file ignores are **excellent**:

#### **Tests (`tests/**/*.py`)** - 25 exceptions
✅ **APPROPRIATE** - All justified
- Note: 336 PERF401 violations in tests (list comprehension opportunities)
- Keep ignored - test clarity > performance

#### **Examples (`examples/**/*.py`)** - 7 exceptions
✅ **APPROPRIATE** - Educational code prioritizes clarity
- 76 PLC0415 violations (late imports for demo purposes)
- 53 TRY400 violations (error handling demos)

#### **Notebooks (`notebooks/**/*.ipynb`)** - 10 exceptions
✅ **APPROPRIATE** - Exploratory work

**Verdict:** No changes needed to per-file ignores.

## Problem Statement

After comprehensive violation analysis, we've identified concrete improvement opportunities:

1. **Duplicate Rule Entries**: 12 duplicate rules clutter the configuration (Lines 63-116 in pyproject.toml)
2. **Quick Wins Available**: 17 violations across 5 rules that can be fixed in ~30 minutes
3. **Inefficient Global Ignores**: PLC0415 (177 violations) should be per-file, not global
4. **Hidden Technical Debt**: 224 violations in rules we should incrementally address (PERF401, EM101, EM102)
5. **Major Technical Debt**: 992 violations we'll keep ignored (PLR2004, TRY003, TRY400) - but should document why

The current state is **much better than most projects** (only 2 active TC003 violations!), but we can eliminate unnecessary ignores and fix quick wins.

## Proposed Solution

### Phase 1: Fix Quick Wins (30-45 minutes)

**1.1 Fix Active TC003 Violations (2 violations):**
```bash
# Fix the 2 TC003 violations - move imports to TYPE_CHECKING block
uvx ruff check --select TC003 --fix --unsafe-fixes src/py_gdelt/sources/fetcher.py
```

**1.2 Fix Quick Win Rules (17 violations across 5 rules):**

These have <10 violations each and can be fixed quickly:

```bash
# SIM102 - Collapsible if (4 violations) - auto-fixable
uvx ruff check --select SIM102 --fix .

# Manually fix these (13 violations total):
# TRY300 (6) - Add else clauses to try-except blocks
# PLW2901 (3) - Rename redefined loop variables
# SIM105 (2) - Use contextlib.suppress
# TRY004 (2) - Use TypeError explicitly in type checks
```

After fixes, remove these 5 rules from ignore list.

**1.3 Deduplicate Configuration:**
```toml
# pyproject.toml - Cleaned select array (Lines 63-116)
[tool.ruff.lint]
select = [
    # === Core Quality (PEP 8, Pyflakes, Bugbear) ===
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "B",      # flake8-bugbear

    # === Import & Organization ===
    "I",      # isort
    "TID",    # flake8-tidy-imports
    "TCH",    # flake8-type-checking (TYPE_CHECKING blocks)

    # === Modern Python ===
    "UP",     # pyupgrade
    "YTT",    # flake8-2020 (sys.version checks)
    "FLY",    # flynt (f-string conversion)

    # === Code Quality & Simplification ===
    "C4",     # flake8-comprehensions
    "SIM",    # flake8-simplify
    "PIE",    # flake8-pie (misc best practices)
    "RET",    # flake8-return (return statement best practices)

    # === Naming & Style ===
    "N",      # pep8-naming
    "Q",      # flake8-quotes
    "COM",    # flake8-commas
    "ISC",    # flake8-implicit-str-concat

    # === Security ===
    "S",      # flake8-bandit (security)
    "BLE",    # flake8-blind-except

    # === Exception Handling ===
    "TRY",    # tryceratops (exception handling)
    "RSE",    # flake8-raise (exception raising)
    "EM",     # flake8-errmsg (exception message formatting)

    # === Type Safety ===
    "A",      # flake8-builtins (shadowing built-ins)

    # === Performance ===
    "PERF",   # Perflint (performance anti-patterns)

    # === Async/Await (CRITICAL for py-gdelt) ===
    "ASYNC",  # flake8-async (async/await best practices)

    # === Framework-Specific ===
    "PD",     # pandas-vet (optional dependency)
    "PT",     # flake8-pytest-style

    # === Debugging & Maintenance ===
    "T10",    # flake8-debugger
    "T20",    # flake8-print (no print statements in production)
    "ERA",    # eradicate (commented-out code)

    # === Logging ===
    "G",      # flake8-logging-format

    # === File Hygiene ===
    "PTH",    # flake8-use-pathlib (prefer pathlib over os.path)
    "DTZ",    # flake8-datetimez (timezone awareness)

    # === Argument Handling ===
    "ARG",    # flake8-unused-arguments

    # === Private Access ===
    "SLF",    # flake8-self (private member access)

    # === Conventions ===
    "ICN",    # flake8-import-conventions

    # === Pylint (All Categories) ===
    "PL",     # Pylint (PLC, PLE, PLR, PLW)

    # === Misc Checks ===
    "PGH",    # pygrep-hooks

    # === Ruff-Specific ===
    "RUF",    # Ruff-specific rules
]
```

**1.4 Categorize and Clean Ignores:**

**REMOVE from ignore list** (fixed in 1.2):
- TRY300, SIM102, PLW2901, SIM105, TRY004

**CONVERT to per-file ignores** (see Phase 2):
- PLC0415

**UPDATED ignore list:**
```toml
# pyproject.toml - Lines 117-134
ignore = [
    # === PERMANENT - Justified by Architecture (3 rules) ===
    "ARG002",   # unused-method-argument (8 violations - protocol compliance)
    "S608",     # hardcoded-sql-expression (3 violations - BigQuery safe builders)
    "PLR0913",  # too-many-arguments (1 violation - dataclass constructor)

    # === MAJOR TECHNICAL DEBT - Keep Ignored (3 rules, 992 violations) ===
    # These would require massive refactoring with minimal benefit
    "PLR2004",  # magic-value-comparison (398 violations - HTTP codes are self-documenting)
    "TRY003",   # raise-vanilla-args (374 violations - would require exception class refactor)
    "TRY400",   # error-instead-of-exception (220 violations - logger.error is our style)

    # === INCREMENTAL TECHNICAL DEBT - Plan to Fix (3 rules, 224 violations) ===
    # TODO(Q1-2026): Fix incrementally - 20 violations per week
    "PERF401",  # manual-list-comprehension (181 violations in src/)
    "EM101",    # raw-string-in-exception (19 violations)
    "EM102",    # f-string-in-exception (24 violations)
]
```

**Reduction:** 16 rules → 9 rules (44% reduction!)

---

### Phase 2: Convert Global to Per-File Ignores (15 minutes)

**PLC0415** (import-outside-top-level) has 177 violations in src/, but they're concentrated in specific files for legitimate reasons (lazy loading optional dependencies).

**Step 1:** Identify which files actually need this ignore:
```bash
# See where the violations are
uvx ruff check --select PLC0415 src/ --output-format grouped
```

**Step 2:** Add per-file ignores for affected files:
```toml
# pyproject.toml - Add to [tool.ruff.lint.per-file-ignores] section

"src/py_gdelt/client.py" = ["PLC0415"]  # BigQuery/pandas lazy imports
"src/py_gdelt/sources/fetcher.py" = ["PLC0415"]  # Optional dependency handling
"src/py_gdelt/endpoints/*.py" = ["PLC0415"]  # Some endpoints have conditional imports
"src/py_gdelt/parsers/*.py" = ["PLC0415"]  # Parser lazy imports
```

**Step 3:** Remove PLC0415 from global ignore list

**Step 4:** Verify we didn't break anything:
```bash
make ci  # Should still pass
```

**Benefit:** Now if someone accidentally adds a lazy import in a file that shouldn't have them (like models or utils), Ruff will catch it.

---

### Phase 3: Documentation & Process (15 minutes)

**Update CLAUDE.md with linting philosophy:**
```markdown
## Linting Philosophy

### Rule Categories

All ignored rules fall into three categories:

1. **PERMANENT** (3 rules) - Justified by project architecture
   - ARG002, S608, PLR0913

2. **MAJOR TECHNICAL DEBT** (3 rules, 992 violations) - Keep ignored
   - PLR2004, TRY003, TRY400
   - Would require massive refactoring with minimal benefit

3. **INCREMENTAL DEBT** (3 rules, 224 violations) - Fix over time
   - PERF401 (181), EM101 (19), EM102 (24)
   - Target: 20 fixes per week during active development

### Adding New Ignores

Before adding any rule to ignore list:
1. Run `uvx ruff check --select <RULE> .` to see violations
2. Try auto-fix: `uvx ruff check --select <RULE> --fix .`
3. If genuinely needed, categorize and document why
4. Get team approval in PR review

### Quarterly Review

Every Q1/Q2/Q3/Q4: Review ignore list, check if incremental debt is decreasing
```

**Create monitoring script:**
```bash
# scripts/lint_progress.sh
#!/bin/bash
echo "=== Incremental Technical Debt Progress ==="
echo ""
echo "PERF401 (list comprehensions): $(uvx ruff check --select PERF401 src/ 2>/dev/null | wc -l) violations"
echo "EM101 (exception messages): $(uvx ruff check --select EM101 src/ 2>/dev/null | wc -l) violations"
echo "EM102 (exception messages): $(uvx ruff check --select EM102 src/ 2>/dev/null | wc -l) violations"
echo ""
echo "Target: Reduce by 20/week during active development"
```

---

### Phase 4: Incremental Improvements (Ongoing - Q1 2026)

**Target:** Fix 20 violations per week during active development

**Incremental Debt Remaining:** 224 violations across 3 rules

| Rule | Violations | Weeks to Fix (@ 20/week) |
|------|-----------|--------------------------|
| PERF401 | 181 | ~9 weeks |
| EM101 | 19 | ~1 week |
| EM102 | 24 | ~1.2 weeks |

**Weekly Workflow:**

1. **Monday:** Check progress
   ```bash
   ./scripts/lint_progress.sh
   ```

2. **Pick target:** Focus on one rule (start with PERF401)
   ```bash
   # Get next 20 violations for PERF401
   uvx ruff check --select PERF401 src/ 2>/dev/null | head -20 > /tmp/targets.txt
   ```

3. **Fix violations:**
   ```bash
   # Try auto-fix first
   uvx ruff check --select PERF401 --fix src/

   # Review changes
   git diff

   # Manual fixes for ones that can't auto-fix
   ```

4. **Test:**
   ```bash
   make ci  # Ensure nothing broke
   ```

5. **Commit:**
   ```bash
   git commit -m "refactor: convert 20 loops to list comprehensions (PERF401)"
   ```

**Completion Timeline:**
- **End of Q1 2026:** All 3 incremental debt rules resolved
- **Can then remove** PERF401, EM101, EM102 from ignore list

---

## Acceptance Criteria

### Phase 1 (Quick Wins - Complete in 1 session):
- [ ] 2 TC003 violations fixed in `src/py_gdelt/sources/fetcher.py:19`
- [ ] 17 quick win violations fixed (TRY300, SIM102, PLW2901, SIM105, TRY004)
- [ ] 5 rules removed from ignore list (quick wins)
- [ ] Duplicate rules removed from `pyproject.toml` select array (12 duplicates)
- [ ] Ignore list reduced from 16 rules → 9 rules (44% reduction)
- [ ] All ignores categorized with comments (PERMANENT / MAJOR DEBT / INCREMENTAL DEBT)
- [ ] `make ci` passes with 0 active violations

### Phase 2 (Per-File Ignores - 15 minutes):
- [ ] PLC0415 converted from global ignore to per-file ignores
- [ ] Ignore list reduced from 9 rules → 8 rules
- [ ] Per-file ignores added for: `client.py`, `sources/fetcher.py`, `endpoints/*.py`, `parsers/*.py`
- [ ] `make ci` still passes

### Phase 3 (Documentation - 15 minutes):
- [ ] Linting philosophy section added to CLAUDE.md
- [ ] `scripts/lint_progress.sh` created and executable
- [ ] Process documented for adding new ignores
- [ ] Quarterly review schedule documented

### Phase 4 (Incremental Improvements - Ongoing Q1 2026):
- [ ] Track progress weekly with `./scripts/lint_progress.sh`
- [ ] Fix 20 violations per week during active development
- [ ] End of Q1: PERF401, EM101, EM102 resolved
- [ ] End of Q1: Remove all 3 incremental debt rules from ignore list
- [ ] Final ignore list: 5 rules (3 permanent + 3 major debt)

## Technical Approach

### File Structure

```
py-gdelt/
├── pyproject.toml                    # MODIFY: Clean up duplicates, categorize ignores
├── scripts/
│   └── audit_ignores.sh             # CREATE: Audit script
├── CLAUDE.md                         # UPDATE: Add linting philosophy section
├── Makefile                          # UPDATE: Add lint-audit target
└── docs/
    └── linting-audit-report.txt     # GENERATE: Initial audit report
```

### Implementation Details

#### 1. Fix TC003 Violations

**File:** `src/py_gdelt/sources/fetcher.py`

**Current Code (Line 19):**
```python
from collections.abc import AsyncIterator, Iterator
```

**After Fix:**
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator
```

**Why this works:** These types are only used in type hints, not at runtime, so they can be safely moved to a TYPE_CHECKING block to reduce import overhead.

#### 2. Deduplicate Select Array

**Current:** 53 entries (12 duplicates)
**After:** 41 unique entries (organized by category)

**Benefits:**
- Easier to scan and understand
- Clear grouping by purpose
- Commented categories explain why each group is enabled

#### 3. Categorization System

Use three-tier categorization:

```toml
ignore = [
    # === PERMANENT IGNORES (Well-Justified) ===
    # Rules that don't apply to our architecture

    # === STYLISTIC PREFERENCES (Team Decision) ===
    # Debatable rules where we've chosen a side

    # === TECHNICAL DEBT (Scheduled for Review) ===
    # Rules we should probably enable but need time to fix violations
    # TODO(YYYY-QQ): Review date
]
```

## Success Metrics

### Quantitative - Immediate (Phase 1-3):
- **Active violations**: 2 TC003 → 0 ✓
- **Quick win violations**: 17 → 0 ✓
- **Configuration size**: 53 select entries → 41 unique (22% reduction) ✓
- **Ignore list size**: 16 rules → 8 rules (50% reduction!) ✓
- **Rules fixed**: 5 rules removed from ignore list ✓
- **Global to per-file**: PLC0415 converted (177 violations scoped) ✓

### Quantitative - Long-term (Phase 4, Q1 2026):
- **Incremental debt progress**: 224 violations → 0
  - PERF401: 181 → 0
  - EM101: 19 → 0
  - EM102: 24 → 0
- **Final ignore list**: 8 rules → 6 rules (only permanent + major debt)
- **Weekly fix rate**: Target 20 violations/week

### Qualitative:
- **Transparency**: Every ignored rule has a documented category and reason
- **Maintainability**: Clear distinction between permanent ignores vs technical debt
- **Process**: Documented workflow for quarterly reviews and adding new ignores
- **Trend**: Technical debt decreases over time (tracked with `lint_progress.sh`)

## Dependencies & Risks

### Dependencies:
- ✅ Ruff 0.8+ (already installed)
- ✅ Make (already in use)
- ✅ Git (already in use)

### Risks & Mitigation:

| Risk | Probability | Impact | Mitigation |
|------|-------------|---------|------------|
| Fixing violations introduces bugs | Low | High | Run `make ci` (includes tests) after every fix |
| Team disagrees on categorization | Low | Low | Document rationale; this plan is based on research |
| Audit reveals hundreds of violations for some rules | Medium | Medium | Use incremental approach; some rules stay ignored longer |
| Auto-fixes change behavior | Low | High | Review all `--fix` changes with `git diff` before commit |

## Alternative Approaches Considered

### ❌ Option 1: "Nuclear Option" - Start Fresh with `select = ["ALL"]`

**Pros:**
- Catches absolutely everything
- No hidden issues

**Cons:**
- Overwhelming number of violations
- Many rules are legitimately not applicable
- Constant churn as Ruff adds new rules

**Why Rejected:** Too disruptive for an already high-quality codebase.

---

### ❌ Option 2: Keep Status Quo

**Pros:**
- Zero effort
- Already passing CI

**Cons:**
- Duplicate rules clutter config
- No systematic review of technical debt
- Ignores may be hiding fixable issues

**Why Rejected:** Misses opportunity for incremental improvement.

---

### ✅ Option 3: Surgical Cleanup (Selected Approach)

**Pros:**
- Low risk, high value
- Preserves existing quality
- Creates process for continuous improvement
- Fixes only what needs fixing

**Cons:**
- Requires ongoing discipline

**Why Selected:** Best balance of improvement vs. disruption.

## Future Considerations

### Enable Preview Rules

Ruff has a `preview` mode for experimental rules:

```toml
[tool.ruff]
preview = true
```

**Recommendation:** Enable in Q2 2026 after technical debt is reduced.

### Enable Docstring Rules

Currently, docstrings are checked by `interrogate` but not Ruff's `D` rules:

```toml
extend-select = ["D"]  # pydocstyle
```

**Recommendation:** Evaluate in Q2 2026. May conflict with existing `interrogate` setup.

### Consider Even Stricter Rules

Once technical debt is cleared:
- `ANN` - flake8-annotations (require type hints everywhere)
- `RUF100` - unused-noqa (remove unnecessary suppressions)

## References & Research

### Internal References

**Configuration:**
- `pyproject.toml:58-221` - Current Ruff configuration
- `pyproject.toml:223-257` - MyPy strict configuration
- `CLAUDE.md:45-48` - "NEVER bypass linting rules" directive
- `Makefile:11-19` - Current linting commands

**Violations:**
- `src/py_gdelt/sources/fetcher.py:19` - TC003 violations (AsyncIterator, Iterator)

**Current Suppressions:**
- `src/py_gdelt/client.py:212` - BLE001 (BigQuery error boundary)
- `src/py_gdelt/filters.py:10` - TC003 (Pydantic runtime access)
- `src/py_gdelt/config.py:215-216` - ARG003 (Pydantic protocol)

### External References

**Official Documentation:**
- [Ruff Official Docs](https://docs.astral.sh/ruff/)
- [Ruff Rules Reference](https://docs.astral.sh/ruff/rules/)
- [Ruff Configuration Guide](https://docs.astral.sh/ruff/configuration/)

**Best Practices:**
- [How to Configure Recommended Ruff Defaults](https://pydevtools.com/handbook/how-to/how-to-configure-recommended-ruff-defaults/)
- [Linting with Ruff - Better Stack](https://betterstack.com/community/guides/scaling-python/ruff-explained/)
- [Ruff: Modern Python Linter - Real Python](https://realpython.com/ruff-python/)
- [Airbus Cyber: Python Code Quality with Ruff](https://cyber.airbus.com/en/newsroom/stories/2025-10-python-code-quality-with-ruff-one-step-at-a-time-part-1)
- [Mastering Python Linting - Medium](https://wbarillon.medium.com/mastering-python-linting-keep-control-over-your-code-7aa371d31c36)

**Migration Guides:**
- [Ruff and Ready: Migration Guide](https://www.thenegation.com/posts/migrate-to-ruff/)
- [Python Code Quality Best Practices - Real Python](https://realpython.com/python-code-quality/)

**Standards:**
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [Python Code Review Checklist - Redwerk](https://redwerk.com/blog/python-code-review-checklist/)

### Related Issues/PRs

**Recent Commits:**
- `ab703e3` - "chore - formatting" (reformatted mypy config)
- `d4597f0` - "feat: enforce conventional commits with full automation"
- `02e6c05` - "feat: setup CI/CD with PyPI publishing and documentation coverage"

**Pattern:** Project recently underwent major CI/CD improvements (Dec 2024), now is perfect time to refine linting.

---

## MVP Implementation Files

### `pyproject.toml` (Cleaned Configuration)

```toml
[tool.ruff.lint]
select = [
    # === Core Quality ===
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "B",      # flake8-bugbear

    # === Imports ===
    "I",      # isort
    "TID",    # flake8-tidy-imports
    "TCH",    # flake8-type-checking

    # === Modern Python ===
    "UP",     # pyupgrade
    "YTT",    # flake8-2020
    "FLY",    # flynt

    # === Code Quality ===
    "C4",     # flake8-comprehensions
    "SIM",    # flake8-simplify
    "PIE",    # flake8-pie
    "RET",    # flake8-return

    # === Style ===
    "N",      # pep8-naming
    "Q",      # flake8-quotes
    "COM",    # flake8-commas
    "ISC",    # flake8-implicit-str-concat

    # === Security ===
    "S",      # flake8-bandit
    "BLE",    # flake8-blind-except

    # === Exceptions ===
    "TRY",    # tryceratops
    "RSE",    # flake8-raise
    "EM",     # flake8-errmsg

    # === Types ===
    "A",      # flake8-builtins

    # === Performance ===
    "PERF",   # Perflint

    # === Async (CRITICAL) ===
    "ASYNC",  # flake8-async

    # === Frameworks ===
    "PD",     # pandas-vet
    "PT",     # flake8-pytest-style

    # === Debug ===
    "T10",    # flake8-debugger
    "T20",    # flake8-print
    "ERA",    # eradicate

    # === Logging ===
    "G",      # flake8-logging-format

    # === Files ===
    "PTH",    # flake8-use-pathlib
    "DTZ",    # flake8-datetimez

    # === Arguments ===
    "ARG",    # flake8-unused-arguments

    # === Access ===
    "SLF",    # flake8-self

    # === Conventions ===
    "ICN",    # flake8-import-conventions

    # === Pylint ===
    "PL",     # Pylint (all)

    # === Misc ===
    "PGH",    # pygrep-hooks
    "RUF",    # Ruff-specific
]

ignore = [
    # === PERMANENT IGNORES ===
    "E501",     # line-too-long (formatter handles)
    "TRY003",   # raise-vanilla-args (too strict)
    "ARG002",   # unused-method-argument (protocols)
    "S608",     # hardcoded-sql (safe builders)
    "PLR0913",  # too-many-arguments (dataclasses)
    "TRY400",   # error-vs-exception (logger style)
    "PLC0415",  # import-outside-top-level (lazy)

    # === STYLISTIC ===
    "SIM105",   # suppressible-exception
    "TRY004",   # type-check-without-type-error

    # === TECHNICAL DEBT (TODO: Q1-2026) ===
    "PERF401",  # manual-list-comprehension
    "TRY300",   # try-consider-else
    "PLR2004",  # magic-value-comparison
    "SIM102",   # collapsible-if
    "PLW2901",  # redefined-loop-name
    "EM101",    # raw-string-in-exception
    "EM102",    # f-string-in-exception
]

# ... rest of config unchanged
```

### `scripts/audit_ignores.sh`

```bash
#!/bin/bash
# Audit linting technical debt

echo "=== Linting Technical Debt Audit ==="
echo "Date: $(date)"
echo

DEBT_RULES="PERF401 TRY300 SIM102 PLW2901 EM101 EM102 PLR2004"

for rule in $DEBT_RULES; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Rule: $rule"

    count=$(uvx ruff check --select $rule . 2>/dev/null | grep -c "^src/")
    echo "Violations: $count"

    if [ $count -eq 0 ]; then
        echo "✅ Remove from ignore list"
    elif [ $count -lt 5 ]; then
        echo "🎯 Fix now (<5 violations)"
    elif [ $count -lt 20 ]; then
        echo "⚠️  Fix next sprint (<20 violations)"
    else
        echo "📋 Fix incrementally (many violations)"
    fi

    if [ $count -gt 0 ]; then
        echo
        echo "Samples:"
        uvx ruff check --select $rule . 2>/dev/null | grep "^src/" | head -3
    fi
    echo
done
```

### `CLAUDE.md` Addition

```markdown
## Linting Philosophy

### Never bypass rules without justification

All ignore rules are categorized:
- **PERMANENT**: Justified by architecture
- **STYLISTIC**: Team preference
- **TECHNICAL DEBT**: Scheduled for review (see TODO dates)

### Process

1. **Adding ignores**: Requires PR approval + category + comment
2. **Weekly fixes**: 1 technical debt rule during active dev
3. **Quarterly review**: All ignores re-evaluated Q1/Q2/Q3/Q4
```

---

## Summary

This plan transforms an **already excellent** linting setup into a **perfect** one:

- **Immediate win**: Fix 2 violations, clean 12 duplicates
- **Systematic approach**: Categorize and track technical debt
- **Sustainable process**: Weekly improvements, quarterly reviews
- **Zero regression risk**: CI enforces quality at every step

The py-gdelt project already follows 2025 best practices. This plan adds the final polish and ensures continuous improvement.
