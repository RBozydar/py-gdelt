"""Tests for py_gdelt.models.articles."""

from datetime import datetime

import pytest

from py_gdelt.models.articles import Article, Timeline, TimelinePoint


class TestArticle:
    """Tests for Article model."""

    def test_article_creation_minimal(self) -> None:
        """Test Article with minimal required fields."""
        article = Article(url="https://example.com/news")
        assert article.url == "https://example.com/news"
        assert article.title is None

    def test_article_creation_full(self) -> None:
        """Test Article with all fields."""
        article = Article(
            url="https://example.com/news",
            title="Breaking News",
            seendate="20240115120000",
            domain="example.com",
            source_country="US",
            language="English",
            tone=-2.5,
            share_count=100,
        )
        assert article.title == "Breaking News"
        assert article.source_country == "US"
        assert article.share_count == 100

    def test_article_alias_fields(self) -> None:
        """Test field aliases work."""
        article = Article(
            url="https://example.com",
            sourcecountry="UK",
            sharecount=50,
        )
        assert article.source_country == "UK"
        assert article.share_count == 50

    def test_article_seen_datetime(self) -> None:
        """Test seendate parsing."""
        article = Article(url="https://example.com", seendate="20240115123045")
        dt = article.seen_datetime
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 15
        assert dt.hour == 12

    def test_article_seen_datetime_none(self) -> None:
        """Test seendate parsing with None."""
        article = Article(url="https://example.com")
        assert article.seen_datetime is None

    def test_article_seen_datetime_invalid(self) -> None:
        """Test seendate parsing with invalid format."""
        article = Article(url="https://example.com", seendate="invalid")
        assert article.seen_datetime is None

    def test_article_is_english(self) -> None:
        """Test English language detection."""
        assert Article(url="x", language="English").is_english
        assert Article(url="x", language="en").is_english
        assert not Article(url="x", language="Spanish").is_english
        assert not Article(url="x").is_english

    def test_article_to_dict(self) -> None:
        """Test serialization."""
        article = Article(url="https://example.com", title="Test")
        d = article.to_dict()
        assert d["url"] == "https://example.com"
        assert d["title"] == "Test"

    def test_article_from_api_response(self) -> None:
        """Test parsing typical API response."""
        api_data = {
            "url": "https://news.com/story",
            "title": "News Story",
            "seendate": "20240101000000",
            "sourcecountry": "US",
            "language": "English",
            "domain": "news.com",
            "socialimage": "https://news.com/image.jpg",
        }
        article = Article.model_validate(api_data)
        assert article.url == "https://news.com/story"
        assert article.source_country == "US"


class TestTimelinePoint:
    """Tests for TimelinePoint model."""

    def test_timeline_point_creation(self) -> None:
        """Test TimelinePoint creation."""
        point = TimelinePoint(date="2024-01-15", value=100)
        assert point.date == "2024-01-15"
        assert point.value == 100

    def test_timeline_point_alias(self) -> None:
        """Test count alias for value."""
        point = TimelinePoint(date="2024-01-15", count=50)
        assert point.value == 50

    def test_timeline_point_parsed_date(self) -> None:
        """Test date parsing."""
        point = TimelinePoint(date="2024-01-15")
        dt = point.parsed_date
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 15

    def test_timeline_point_parsed_date_various_formats(self) -> None:
        """Test various date formats."""
        # ISO format
        assert TimelinePoint(date="2024-01-15").parsed_date is not None
        # Compact format
        assert TimelinePoint(date="20240115").parsed_date is not None


class TestTimeline:
    """Tests for Timeline model."""

    def test_timeline_creation_empty(self) -> None:
        """Test empty Timeline."""
        timeline = Timeline()
        assert timeline.timeline == []
        assert timeline.points == []

    def test_timeline_creation_with_points(self) -> None:
        """Test Timeline with points."""
        timeline = Timeline(
            timeline=[
                TimelinePoint(date="2024-01-01", value=10),
                TimelinePoint(date="2024-01-02", value=20),
            ]
        )
        assert len(timeline.points) == 2
        assert timeline.points[0].value == 10

    def test_timeline_from_dict_list(self) -> None:
        """Test Timeline parsing from dicts."""
        timeline = Timeline(
            timeline=[
                {"date": "2024-01-01", "count": 100},
                {"date": "2024-01-02", "count": 200},
            ]
        )
        assert len(timeline.points) == 2
        assert timeline.points[1].value == 200

    def test_timeline_dates_property(self) -> None:
        """Test dates property."""
        timeline = Timeline(
            timeline=[
                TimelinePoint(date="2024-01-01", value=10),
                TimelinePoint(date="2024-01-02", value=20),
            ]
        )
        assert timeline.dates == ["2024-01-01", "2024-01-02"]

    def test_timeline_values_property(self) -> None:
        """Test values property."""
        timeline = Timeline(
            timeline=[
                TimelinePoint(date="2024-01-01", value=10),
                TimelinePoint(date="2024-01-02", value=20),
            ]
        )
        assert timeline.values == [10, 20]

    def test_timeline_to_series(self) -> None:
        """Test to_series method."""
        timeline = Timeline(
            timeline=[
                TimelinePoint(date="2024-01-01", value=10),
                TimelinePoint(date="2024-01-02", value=20),
            ]
        )
        series = timeline.to_series()
        assert series == {"2024-01-01": 10, "2024-01-02": 20}

    def test_timeline_to_dict(self) -> None:
        """Test serialization."""
        timeline = Timeline(
            query="test",
            total_articles=100,
            timeline=[TimelinePoint(date="2024-01-01", value=50)],
        )
        d = timeline.to_dict()
        assert d["query"] == "test"
        assert d["total_articles"] == 100
        assert len(d["timeline"]) == 1

    def test_timeline_from_api_response(self) -> None:
        """Test parsing typical API timeline response."""
        api_data = {
            "timeline": [
                {"date": "2024-01-01", "count": 100},
                {"date": "2024-01-02", "count": 150},
            ]
        }
        timeline = Timeline.model_validate(api_data)
        assert len(timeline.points) == 2
