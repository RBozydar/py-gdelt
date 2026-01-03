## 1. Overview & Goals

### 1.1 Project Purpose

A comprehensive Python client library for the GDELT (Global Database of Events, Language, and Tone) project, providing unified access to all GDELT data sources with a modern, type-safe API.

### 1.2 Goals

- **Unified Interface**: Single client covering all 6 REST APIs, 3 database tables, and NGrams dataset
- **Version Normalization**: Transparent handling of GDELT v1/v2 differences with normalized output
- **Resilience**: Automatic fallback to BigQuery when APIs fail or rate limit
- **Modern Python**: 3.11+, Async-first, Pydantic models, type hints throughout
- **Streaming**: Generator-based iteration for large datasets with memory efficiency
- **Developer Experience**: Clear errors, progress indicators, comprehensive lookups
