# py-gdelt Jupyter Notebooks

Interactive notebooks demonstrating py-gdelt library usage.

## Overview

These notebooks provide hands-on, interactive examples of the py-gdelt library:

1. **01_getting_started.ipynb** - Comprehensive introduction to all core features
2. **02_advanced_patterns.ipynb** - Production-ready patterns and best practices
3. **03_visualization.ipynb** - Data visualization with charts and maps

## Setup

### Install Jupyter

```bash
pip install py-gdelt jupyter
```

### Optional Dependencies for Visualization

For the visualization notebook, install additional packages:

```bash
pip install pandas matplotlib folium plotly
```

### Running Notebooks

Start Jupyter Lab or Notebook:

```bash
# Jupyter Lab (recommended)
jupyter lab

# Or Jupyter Notebook
jupyter notebook
```

## Async Support

Modern Jupyter (IPython 8+) supports native async/await. The notebooks use `nest_asyncio` for compatibility with older versions:

```python
import nest_asyncio
nest_asyncio.apply()
```

For the latest Jupyter, you can use synchronous context managers without `nest_asyncio`:

```python
with GDELTClient() as client:
    events = client.events.query_sync(filter_obj)
```

## BigQuery Examples

Some notebooks include BigQuery examples that require:

1. Google Cloud credentials configured
2. BigQuery dependencies installed: `pip install py-gdelt[bigquery]`

These sections are marked and can be skipped if you don't have BigQuery access.

## Data Privacy

**Important**: Notebooks may contain API responses with real news data. Use `.gitattributes` with `nbstripout` to avoid committing outputs:

```bash
# Install nbstripout
pip install nbstripout

# Set up git filter
nbstripout --install
```

## Notebooks Overview

### 01 - Getting Started

Perfect for new users. Covers:
- Client initialization and configuration
- Querying Events, GKG, and NGrams
- Using REST APIs (DOC, GEO, Context, TV)
- Accessing lookup tables
- Basic streaming

### 02 - Advanced Patterns

For production use cases. Covers:
- Configuration via environment variables and TOML
- Error handling and retry strategies
- Deduplication strategies
- BigQuery integration and fallback
- Memory-efficient streaming
- Combining multiple data sources

### 03 - Visualization

Interactive data analysis. Covers:
- Timeline charts with matplotlib/plotly
- Geographic maps with folium
- Tone/sentiment analysis plots
- TV station comparison charts
- Network graphs of entity relationships

## Tips

- Run cells sequentially (top to bottom) for best results
- Some API calls may take time - be patient
- If you get rate limited, wait a few minutes before retrying
- Save your work frequently
- Clear outputs before committing to git

## Troubleshooting

### RuntimeError: This event loop is already running

Use `nest_asyncio`:

```python
import nest_asyncio
nest_asyncio.apply()
```

### ImportError for visualization libraries

Install optional dependencies:

```python
!pip install pandas matplotlib folium plotly
```

### Empty results from API calls

- GDELT APIs may return empty results for some queries
- Try broader time ranges (`timespan="7d"` instead of `"24h"`)
- Try more common search terms
- Check if the API is accessible from your network

## Contributing

Found an issue or have a suggestion? Please open an issue on GitHub!
