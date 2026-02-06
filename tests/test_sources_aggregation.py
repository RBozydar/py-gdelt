"""Tests for aggregation models, enums, and exports.

This module tests:
- AggFunc enum values
- Aggregation Pydantic model validation
- GKGUnnestField enum and GKG_UNNEST_CONFIG consistency
- AggregationResult construction
- Top-level and sources-level exports
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from py_gdelt.sources.aggregation import (
    GKG_UNNEST_CONFIG,
    AggFunc,
    Aggregation,
    AggregationResult,
    GKGUnnestField,
)


class TestAggFuncEnum:
    """Tests for the AggFunc enum."""

    def test_agg_func_enum_values(self) -> None:
        assert AggFunc.COUNT == "COUNT"
        assert AggFunc.SUM == "SUM"
        assert AggFunc.AVG == "AVG"
        assert AggFunc.MIN == "MIN"
        assert AggFunc.MAX == "MAX"
        assert AggFunc.COUNT_DISTINCT == "COUNT_DISTINCT"
        # Verify exhaustive membership
        assert len(AggFunc) == 6


class TestAggregationModel:
    """Tests for the Aggregation Pydantic model."""

    def test_aggregation_count_star(self) -> None:
        agg = Aggregation(func=AggFunc.COUNT)
        assert agg.func == AggFunc.COUNT
        assert agg.column == "*"
        assert agg.alias is None

    def test_aggregation_star_only_with_count(self) -> None:
        with pytest.raises(ValidationError, match=r"column='\*' is only valid with AggFunc\.COUNT"):
            Aggregation(func=AggFunc.AVG, column="*")

    def test_aggregation_star_rejected_for_sum(self) -> None:
        with pytest.raises(ValidationError):
            Aggregation(func=AggFunc.SUM, column="*")

    def test_aggregation_star_rejected_for_min(self) -> None:
        with pytest.raises(ValidationError):
            Aggregation(func=AggFunc.MIN, column="*")

    def test_aggregation_star_rejected_for_max(self) -> None:
        with pytest.raises(ValidationError):
            Aggregation(func=AggFunc.MAX, column="*")

    def test_aggregation_star_rejected_for_count_distinct(self) -> None:
        with pytest.raises(ValidationError):
            Aggregation(func=AggFunc.COUNT_DISTINCT, column="*")

    def test_aggregation_with_alias(self) -> None:
        agg = Aggregation(func=AggFunc.AVG, column="AvgTone", alias="mean_tone")
        assert agg.alias == "mean_tone"
        assert agg.func == AggFunc.AVG
        assert agg.column == "AvgTone"

    def test_aggregation_without_alias(self) -> None:
        agg = Aggregation(func=AggFunc.SUM, column="NumMentions")
        assert agg.alias is None

    def test_aggregation_with_named_column(self) -> None:
        agg = Aggregation(func=AggFunc.COUNT_DISTINCT, column="Actor1CountryCode")
        assert agg.column == "Actor1CountryCode"
        assert agg.func == AggFunc.COUNT_DISTINCT


class TestGKGUnnestField:
    """Tests for the GKGUnnestField enum and GKG_UNNEST_CONFIG."""

    def test_gkg_unnest_field_enum(self) -> None:
        assert GKGUnnestField.THEMES == "themes"
        assert GKGUnnestField.PERSONS == "persons"
        assert GKGUnnestField.ORGANIZATIONS == "organizations"
        assert len(GKGUnnestField) == 3

    def test_gkg_unnest_config_keys(self) -> None:
        config_keys = set(GKG_UNNEST_CONFIG.keys())
        enum_members = set(GKGUnnestField)
        assert config_keys == enum_members

    def test_gkg_unnest_config_themes_value(self) -> None:
        bq_column, split_expr = GKG_UNNEST_CONFIG[GKGUnnestField.THEMES]
        assert bq_column == "V2Themes"
        assert "SPLIT" in split_expr
        assert "item" in split_expr

    def test_gkg_unnest_config_persons_value(self) -> None:
        bq_column, split_expr = GKG_UNNEST_CONFIG[GKGUnnestField.PERSONS]
        assert bq_column == "V2Persons"
        assert "SPLIT" in split_expr

    def test_gkg_unnest_config_organizations_value(self) -> None:
        bq_column, split_expr = GKG_UNNEST_CONFIG[GKGUnnestField.ORGANIZATIONS]
        assert bq_column == "V2Organizations"
        assert "SPLIT" in split_expr


class TestAggregationResult:
    """Tests for the AggregationResult Pydantic model."""

    def test_aggregation_result_basic(self) -> None:
        result = AggregationResult(
            rows=[{"EventRootCode": "14", "cnt": 100}],
            group_by=["EventRootCode"],
            total_rows=1,
            bytes_processed=5000,
        )
        assert result.total_rows == 1
        assert result.rows[0]["EventRootCode"] == "14"
        assert result.rows[0]["cnt"] == 100
        assert result.group_by == ["EventRootCode"]
        assert result.bytes_processed == 5000

    def test_aggregation_result_bytes_processed_optional(self) -> None:
        result = AggregationResult(
            rows=[],
            group_by=["EventCode"],
            total_rows=0,
        )
        assert result.bytes_processed is None

    def test_aggregation_result_multiple_rows(self) -> None:
        rows = [
            {"EventRootCode": "14", "cnt": 100},
            {"EventRootCode": "01", "cnt": 50},
            {"EventRootCode": "02", "cnt": 30},
        ]
        result = AggregationResult(
            rows=rows,
            group_by=["EventRootCode"],
            total_rows=3,
            bytes_processed=12000,
        )
        assert result.total_rows == 3
        assert len(result.rows) == 3


class TestTopLevelExports:
    """Tests for top-level and sources-level exports."""

    def test_top_level_exports(self) -> None:
        import py_gdelt

        # Aggregation types
        assert hasattr(py_gdelt, "AggFunc")
        assert hasattr(py_gdelt, "Aggregation")
        assert hasattr(py_gdelt, "AggregationResult")
        assert hasattr(py_gdelt, "GKGUnnestField")

        # Column profiles
        assert hasattr(py_gdelt, "EventColumns")
        assert hasattr(py_gdelt, "GKGColumns")
        assert hasattr(py_gdelt, "MentionColumns")

        # Verify they are the correct types
        assert py_gdelt.AggFunc is AggFunc
        assert py_gdelt.Aggregation is Aggregation
        assert py_gdelt.AggregationResult is AggregationResult
        assert py_gdelt.GKGUnnestField is GKGUnnestField

    def test_sources_exports(self) -> None:
        from py_gdelt.sources import (
            AggFunc as SourcesAggFunc,
        )
        from py_gdelt.sources import (
            Aggregation as SourcesAggregation,
        )
        from py_gdelt.sources import (
            AggregationResult as SourcesAggregationResult,
        )
        from py_gdelt.sources import (
            BigQuerySource,
        )
        from py_gdelt.sources import (
            EventColumns as SourcesEventColumns,
        )
        from py_gdelt.sources import (
            GKGColumns as SourcesGKGColumns,
        )
        from py_gdelt.sources import (
            GKGUnnestField as SourcesGKGUnnestField,
        )
        from py_gdelt.sources import (
            MentionColumns as SourcesMentionColumns,
        )
        from py_gdelt.sources.columns import EventColumns, GKGColumns, MentionColumns

        assert SourcesAggFunc is AggFunc
        assert SourcesAggregation is Aggregation
        assert SourcesAggregationResult is AggregationResult
        assert SourcesGKGUnnestField is GKGUnnestField
        assert SourcesEventColumns is EventColumns
        assert SourcesGKGColumns is GKGColumns
        assert SourcesMentionColumns is MentionColumns
        assert BigQuerySource is not None

    def test_top_level_all_contains_aggregation_types(self) -> None:
        import py_gdelt

        all_exports = py_gdelt.__all__
        assert "AggFunc" in all_exports
        assert "Aggregation" in all_exports
        assert "AggregationResult" in all_exports
        assert "GKGUnnestField" in all_exports
        assert "EventColumns" in all_exports
        assert "GKGColumns" in all_exports
        assert "MentionColumns" in all_exports
