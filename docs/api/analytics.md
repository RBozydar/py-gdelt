# Analytics API

SQL-level analytics that push computation to BigQuery for time-series analysis,
trend detection, comparison pivots, and approximate aggregations.

!!! note "Requires BigQuery"
    All analytics methods require BigQuery credentials. See
    [Configuration](../getting-started/configuration.md) for setup.

## Domain Types

### TimeGranularity

::: py_gdelt.analytics.types.TimeGranularity
    options:
      show_root_heading: true
      heading_level: 3

### EventMetric

::: py_gdelt.analytics.types.EventMetric
    options:
      show_root_heading: true
      heading_level: 3

## Result Models

### TimeSeriesResult

::: py_gdelt.analytics.results.TimeSeriesResult
    options:
      show_root_heading: true
      heading_level: 3

### ExtremeEventsResult

::: py_gdelt.analytics.results.ExtremeEventsResult
    options:
      show_root_heading: true
      heading_level: 3

### ComparisonResult

::: py_gdelt.analytics.results.ComparisonResult
    options:
      show_root_heading: true
      heading_level: 3

### TrendResult

::: py_gdelt.analytics.results.TrendResult
    options:
      show_root_heading: true
      heading_level: 3

### DyadResult

::: py_gdelt.analytics.results.DyadResult
    options:
      show_root_heading: true
      heading_level: 3

### PartitionedTopNResult

::: py_gdelt.analytics.results.PartitionedTopNResult
    options:
      show_root_heading: true
      heading_level: 3

## Cost Tracking

### SessionCostTracker

::: py_gdelt.analytics._cost.SessionCostTracker
    options:
      show_root_heading: true
      heading_level: 3

## Events Analytics Mixin

::: py_gdelt.analytics._events_mixin.EventsAnalyticsMixin
    options:
      show_root_heading: true
      heading_level: 3

## GKG Analytics Mixin

::: py_gdelt.analytics._gkg_mixin.GKGAnalyticsMixin
    options:
      show_root_heading: true
      heading_level: 3
