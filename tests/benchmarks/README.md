# Benchmark Tests

This directory contains performance benchmarks for py-gdelt components.

## Purpose

Benchmarks measure the performance of different implementation approaches to:
- Inform architectural decisions
- Track performance regressions
- Compare alternative parsing strategies

## Running Benchmarks

Run all benchmarks:
```bash
pytest tests/benchmarks/ -v -s
```

Run a specific benchmark:
```bash
pytest tests/benchmarks/test_bench_vgkg_parsing.py -v -s
```

Run as standalone script:
```bash
uv run python tests/benchmarks/test_bench_vgkg_parsing.py
```

## Current Benchmarks

### VGKG Parsing Performance

**File:** `test_bench_vgkg_parsing.py`

Compares four approaches for parsing VGKG nested structures:

1. **Pydantic nested models** - Full validation with nested BaseModel classes
2. **TypedDict approach** - Structured dicts with type hints, no runtime validation
3. **NamedTuple approach** - Immutable tuples with named fields
4. **Raw string approach** - Defer parsing, keep nested fields as strings

**Results (1000 rows):**
- Pydantic: ~15K rows/sec (baseline)
- TypedDict: ~51K rows/sec (3.4x faster)
- NamedTuple: ~34K rows/sec (2.3x faster)
- Raw: ~206K rows/sec (13.7x faster)

**Recommendation:** Use Raw or TypedDict for high-throughput scenarios with on-demand parsing. Use Pydantic when validation overhead is acceptable for the use case.

## Adding New Benchmarks

When adding new benchmarks:

1. Use the naming convention `test_bench_<component>_<aspect>.py`
2. Include realistic sample data generation
3. Measure both time and throughput
4. Provide clear recommendations based on results
5. Make runnable both via pytest and standalone
6. Follow project code quality standards (ruff, mypy, docstrings)

## Notes

- Benchmarks use `timeit` for timing measurements
- Each approach is run 5 times to calculate mean/median/stdev
- pytest-benchmark is NOT required (uses stdlib only)
- Benchmarks are excluded from coverage requirements
