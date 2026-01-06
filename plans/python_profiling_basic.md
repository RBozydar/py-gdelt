Quick Summary
The problem: Your library hits OOM with GB-scale API data. You need to fix it and prove efficiency to users.
The solution: Memray for debugging + pytest-memray for CI + streaming patterns + user-facing profiling API.

Immediate Actions
1. Install profiling tools
bashpip install memray pytest-memray
2. Find your memory hog (development)
bash# Run with live monitoring
memray run --live your_script.py

# Generate flamegraph to see allocation hotspots
memray run -o output.bin your_script.py
memray flamegraph output.bin
The flamegraph shows where allocations happen. Look for wide bars at the bottom.
3. Fix the patterns
Stop accumulating in memory:
python# Bad: loads everything
def fetch_all():
    return [fetch_page(i) for i in range(1000)]

# Good: constant memory
def fetch_all():
    for i in range(1000):
        yield from fetch_page(i)
Reduce object overhead:
python@dataclass(slots=True)  # 35-50% smaller per instance
class Record:
    id: int
    timestamp: float
Use NumPy for numeric data:
python# ~8x smaller than Python lists
import numpy as np
data = np.array(values, dtype=np.float32)
4. Prevent regressions (CI)
python# tests/test_memory.py
import pytest

@pytest.mark.limit_memory("50 MB")  # Fails if exceeded
def test_large_fetch():
    result = api.fetch_range("2020-2024")
    assert len(result) > 100_000

@pytest.mark.limit_leaks("1 MB")  # Catches allocation growth
def test_no_leaks():
    for _ in range(100):
        api.fetch_single()
Run: pytest --memray tests/test_memory.py
5. Give users visibility
Add a .memory_usage() method:
pythonclass DataSet:
    def memory_usage(self, deep=False):
        """
        Returns memory usage in bytes.
        
        deep=True: includes referenced objects (slower, accurate)
        deep=False: quick estimate
        """
        if hasattr(self._data, 'nbytes'):
            return self._data.nbytes
        return sys.getsizeof(self)
Add a profiling context manager:
pythonfrom contextlib import contextmanager
import tracemalloc

@contextmanager
def profile_memory(label="operation"):
    tracemalloc.start()
    tracemalloc.reset_peak()
    try:
        yield
    finally:
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"{label}: {peak/1024/1024:.1f} MB peak")

# Usage
with profile_memory("fetch 2024 data"):
    data = api.fetch_year(2024)
6. Document efficiency claims
Create benchmarks/memory.py:
pythonimport tracemalloc

def benchmark(desc, func):
    tracemalloc.start()
    tracemalloc.reset_peak()
    result = func()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"{desc} → {peak/1024/1024:.1f} MB peak")
    return result

# Example
benchmark(
    "Fetch 1M records from API",
    lambda: api.fetch_all(limit=1_000_000)
)
Put results in your README:
markdown## Memory Efficiency

| Operation | Peak Memory | Dataset Size |
|-----------|-------------|--------------|
| Fetch 1M records | 45 MB | 1M rows |
| Process daily data (2020-2024) | 23 MB | 1,825 records |

Understanding Memory Issues
Check current memory in dev:
pythonimport tracemalloc
tracemalloc.start()

# Your code here
result = process_data()

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current/1024/1024:.1f} MB")
print(f"Peak: {peak/1024/1024:.1f} MB")
Compare snapshots to find leaks:
pythonsnap1 = tracemalloc.take_snapshot()
# ... run suspect code ...
snap2 = tracemalloc.take_snapshot()

for stat in snap2.compare_to(snap1, 'lineno')[:10]:
    print(stat)
Peak memory matters more than final - it determines if you OOM.

CI Integration
Add to .github/workflows/test.yml:
yaml- name: Memory tests
  run: pytest --memray tests/test_memory.py
For historical tracking, use ASV (generates graphs over commits):
python# benchmarks/benchmarks.py
def peakmem_load_dataset():
    """ASV tracks peak memory automatically."""
    return client.load_full_dataset()

Key Insight
Build profiling in from the start. Adding .memory_usage() and context managers takes 30 minutes now, saves weeks of debugging later, and gives users confidence in your library's efficiency.