# Data Models API

Data models represent GDELT records and results.

## Event Models

### `Event`

Bases: `BaseModel`

GDELT Event record.

Represents a single event in the GDELT Events database. Events capture who did what to whom, when, where, and how it was reported.

Source code in `src/py_gdelt/models/events.py`

```
class Event(BaseModel):
    """GDELT Event record.

    Represents a single event in the GDELT Events database. Events capture
    who did what to whom, when, where, and how it was reported.
    """

    # Identifiers
    global_event_id: int
    date: date  # Event date
    date_added: datetime | None = None  # When first recorded (UTC)
    source_url: str | None = None

    # Actors
    actor1: Actor | None = None
    actor2: Actor | None = None

    # Action
    event_code: str  # CAMEO code (string, not int, to preserve leading zeros)
    event_base_code: str
    event_root_code: str
    quad_class: int = Field(..., ge=1, le=4)  # 1-4
    goldstein_scale: float = Field(..., ge=-10, le=10)  # -10 to +10

    # Metrics
    num_mentions: int = Field(default=0, ge=0)
    num_sources: int = Field(default=0, ge=0)
    num_articles: int = Field(default=0, ge=0)
    avg_tone: float = 0.0
    is_root_event: bool = False

    # Geography (use Location from common.py)
    actor1_geo: Location | None = None
    actor2_geo: Location | None = None
    action_geo: Location | None = None

    # Metadata
    version: int = Field(default=2, ge=1, le=2)  # 1 or 2
    is_translated: bool = False
    original_record_id: str | None = None  # For translated records

    @classmethod
    def from_raw(cls, raw: _RawEvent) -> Event:
        """Convert internal _RawEvent to public Event model.

        Args:
            raw: Internal _RawEvent dataclass from TAB-delimited parsing.

        Returns:
            Event: Public Event model with proper type conversion.

        Raises:
            ValueError: If required fields are missing or invalid.
        """

        # Helper to safely parse int
        def _parse_int(value: str | None, default: int = 0) -> int:
            if not value or value == "":
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        # Helper to safely parse float
        def _parse_float(value: str | None, default: float = 0.0) -> float:
            if not value or value == "":
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        # Helper to safely parse bool
        def _parse_bool(value: str | None) -> bool:
            if not value or value == "":
                return False
            return value.strip() == "1"

        # Helper to create Location from geo fields
        def _make_location(
            geo_type: str | None,
            name: str | None,
            country_code: str | None,
            adm1_code: str | None,
            adm2_code: str | None,
            lat: str | None,
            lon: str | None,
            feature_id: str | None,
        ) -> Location | None:
            # If no geo data, return None
            if not any(
                [
                    geo_type,
                    name,
                    country_code,
                    adm1_code,
                    adm2_code,
                    lat,
                    lon,
                    feature_id,
                ],
            ):
                return None

            return Location(
                lat=_parse_float(lat) if lat else None,
                lon=_parse_float(lon) if lon else None,
                feature_id=feature_id if feature_id else None,
                name=name if name else None,
                country_code=country_code if country_code else None,
                adm1_code=adm1_code if adm1_code else None,
                adm2_code=adm2_code if adm2_code else None,
                geo_type=_parse_int(geo_type) if geo_type else None,
            )

        # Helper to create Actor
        def _make_actor(
            code: str | None,
            name: str | None,
            country_code: str | None,
            known_group_code: str | None,
            ethnic_code: str | None,
            religion1_code: str | None,
            religion2_code: str | None,
            type1_code: str | None,
            type2_code: str | None,
            type3_code: str | None,
        ) -> Actor | None:
            # If no actor data, return None
            if not any(
                [
                    code,
                    name,
                    country_code,
                    known_group_code,
                    ethnic_code,
                    religion1_code,
                    religion2_code,
                    type1_code,
                    type2_code,
                    type3_code,
                ],
            ):
                return None

            return Actor(
                code=code if code else None,
                name=name if name else None,
                country_code=country_code if country_code else None,
                known_group_code=known_group_code if known_group_code else None,
                ethnic_code=ethnic_code if ethnic_code else None,
                religion1_code=religion1_code if religion1_code else None,
                religion2_code=religion2_code if religion2_code else None,
                type1_code=type1_code if type1_code else None,
                type2_code=type2_code if type2_code else None,
                type3_code=type3_code if type3_code else None,
            )

        # Parse date from sql_date (YYYYMMDD)
        event_date = parse_gdelt_date(raw.sql_date)

        # Parse date_added (YYYYMMDDHHMMSS)
        date_added_dt: datetime | None = None
        if raw.date_added:
            with suppress(ValueError):
                date_added_dt = parse_gdelt_datetime(raw.date_added)

        # Create actors
        actor1 = _make_actor(
            raw.actor1_code,
            raw.actor1_name,
            raw.actor1_country_code,
            raw.actor1_known_group_code,
            raw.actor1_ethnic_code,
            raw.actor1_religion1_code,
            raw.actor1_religion2_code,
            raw.actor1_type1_code,
            raw.actor1_type2_code,
            raw.actor1_type3_code,
        )

        actor2 = _make_actor(
            raw.actor2_code,
            raw.actor2_name,
            raw.actor2_country_code,
            raw.actor2_known_group_code,
            raw.actor2_ethnic_code,
            raw.actor2_religion1_code,
            raw.actor2_religion2_code,
            raw.actor2_type1_code,
            raw.actor2_type2_code,
            raw.actor2_type3_code,
        )

        # Create locations
        actor1_geo = _make_location(
            raw.actor1_geo_type,
            raw.actor1_geo_fullname,
            raw.actor1_geo_country_code,
            raw.actor1_geo_adm1_code,
            raw.actor1_geo_adm2_code,
            raw.actor1_geo_lat,
            raw.actor1_geo_lon,
            raw.actor1_geo_feature_id,
        )

        actor2_geo = _make_location(
            raw.actor2_geo_type,
            raw.actor2_geo_fullname,
            raw.actor2_geo_country_code,
            raw.actor2_geo_adm1_code,
            raw.actor2_geo_adm2_code,
            raw.actor2_geo_lat,
            raw.actor2_geo_lon,
            raw.actor2_geo_feature_id,
        )

        action_geo = _make_location(
            raw.action_geo_type,
            raw.action_geo_fullname,
            raw.action_geo_country_code,
            raw.action_geo_adm1_code,
            raw.action_geo_adm2_code,
            raw.action_geo_lat,
            raw.action_geo_lon,
            raw.action_geo_feature_id,
        )

        return cls(
            global_event_id=_parse_int(raw.global_event_id),
            date=event_date,
            date_added=date_added_dt,
            source_url=raw.source_url if raw.source_url else None,
            actor1=actor1,
            actor2=actor2,
            event_code=raw.event_code,  # Keep as string to preserve leading zeros
            event_base_code=raw.event_base_code,
            event_root_code=raw.event_root_code,
            quad_class=_parse_int(raw.quad_class, default=1),
            goldstein_scale=_parse_float(raw.goldstein_scale, default=0.0),
            num_mentions=_parse_int(raw.num_mentions, default=0),
            num_sources=_parse_int(raw.num_sources, default=0),
            num_articles=_parse_int(raw.num_articles, default=0),
            avg_tone=_parse_float(raw.avg_tone, default=0.0),
            is_root_event=_parse_bool(raw.is_root_event),
            actor1_geo=actor1_geo,
            actor2_geo=actor2_geo,
            action_geo=action_geo,
            version=2,  # Default to v2, can be overridden
            is_translated=raw.is_translated,
            original_record_id=None,  # Not in raw data
        )

    @property
    def is_conflict(self) -> bool:
        """Check if event is conflict (quad_class 3 or 4).

        Returns:
            True if event is material conflict (3) or verbal conflict (4).
        """
        return self.quad_class in (3, 4)

    @property
    def is_cooperation(self) -> bool:
        """Check if event is cooperation (quad_class 1 or 2).

        Returns:
            True if event is verbal cooperation (1) or material cooperation (2).
        """
        return self.quad_class in (1, 2)
```

#### `is_conflict`

Check if event is conflict (quad_class 3 or 4).

Returns:

| Type   | Description                                                    |
| ------ | -------------------------------------------------------------- |
| `bool` | True if event is material conflict (3) or verbal conflict (4). |

#### `is_cooperation`

Check if event is cooperation (quad_class 1 or 2).

Returns:

| Type   | Description                                                          |
| ------ | -------------------------------------------------------------------- |
| `bool` | True if event is verbal cooperation (1) or material cooperation (2). |

#### `from_raw(raw)`

Convert internal \_RawEvent to public Event model.

Parameters:

| Name  | Type        | Description                                               | Default    |
| ----- | ----------- | --------------------------------------------------------- | ---------- |
| `raw` | `_RawEvent` | Internal \_RawEvent dataclass from TAB-delimited parsing. | *required* |

Returns:

| Name    | Type    | Description                                     |
| ------- | ------- | ----------------------------------------------- |
| `Event` | `Event` | Public Event model with proper type conversion. |

Raises:

| Type         | Description                                |
| ------------ | ------------------------------------------ |
| `ValueError` | If required fields are missing or invalid. |

Source code in `src/py_gdelt/models/events.py`

```
@classmethod
def from_raw(cls, raw: _RawEvent) -> Event:
    """Convert internal _RawEvent to public Event model.

    Args:
        raw: Internal _RawEvent dataclass from TAB-delimited parsing.

    Returns:
        Event: Public Event model with proper type conversion.

    Raises:
        ValueError: If required fields are missing or invalid.
    """

    # Helper to safely parse int
    def _parse_int(value: str | None, default: int = 0) -> int:
        if not value or value == "":
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    # Helper to safely parse float
    def _parse_float(value: str | None, default: float = 0.0) -> float:
        if not value or value == "":
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    # Helper to safely parse bool
    def _parse_bool(value: str | None) -> bool:
        if not value or value == "":
            return False
        return value.strip() == "1"

    # Helper to create Location from geo fields
    def _make_location(
        geo_type: str | None,
        name: str | None,
        country_code: str | None,
        adm1_code: str | None,
        adm2_code: str | None,
        lat: str | None,
        lon: str | None,
        feature_id: str | None,
    ) -> Location | None:
        # If no geo data, return None
        if not any(
            [
                geo_type,
                name,
                country_code,
                adm1_code,
                adm2_code,
                lat,
                lon,
                feature_id,
            ],
        ):
            return None

        return Location(
            lat=_parse_float(lat) if lat else None,
            lon=_parse_float(lon) if lon else None,
            feature_id=feature_id if feature_id else None,
            name=name if name else None,
            country_code=country_code if country_code else None,
            adm1_code=adm1_code if adm1_code else None,
            adm2_code=adm2_code if adm2_code else None,
            geo_type=_parse_int(geo_type) if geo_type else None,
        )

    # Helper to create Actor
    def _make_actor(
        code: str | None,
        name: str | None,
        country_code: str | None,
        known_group_code: str | None,
        ethnic_code: str | None,
        religion1_code: str | None,
        religion2_code: str | None,
        type1_code: str | None,
        type2_code: str | None,
        type3_code: str | None,
    ) -> Actor | None:
        # If no actor data, return None
        if not any(
            [
                code,
                name,
                country_code,
                known_group_code,
                ethnic_code,
                religion1_code,
                religion2_code,
                type1_code,
                type2_code,
                type3_code,
            ],
        ):
            return None

        return Actor(
            code=code if code else None,
            name=name if name else None,
            country_code=country_code if country_code else None,
            known_group_code=known_group_code if known_group_code else None,
            ethnic_code=ethnic_code if ethnic_code else None,
            religion1_code=religion1_code if religion1_code else None,
            religion2_code=religion2_code if religion2_code else None,
            type1_code=type1_code if type1_code else None,
            type2_code=type2_code if type2_code else None,
            type3_code=type3_code if type3_code else None,
        )

    # Parse date from sql_date (YYYYMMDD)
    event_date = parse_gdelt_date(raw.sql_date)

    # Parse date_added (YYYYMMDDHHMMSS)
    date_added_dt: datetime | None = None
    if raw.date_added:
        with suppress(ValueError):
            date_added_dt = parse_gdelt_datetime(raw.date_added)

    # Create actors
    actor1 = _make_actor(
        raw.actor1_code,
        raw.actor1_name,
        raw.actor1_country_code,
        raw.actor1_known_group_code,
        raw.actor1_ethnic_code,
        raw.actor1_religion1_code,
        raw.actor1_religion2_code,
        raw.actor1_type1_code,
        raw.actor1_type2_code,
        raw.actor1_type3_code,
    )

    actor2 = _make_actor(
        raw.actor2_code,
        raw.actor2_name,
        raw.actor2_country_code,
        raw.actor2_known_group_code,
        raw.actor2_ethnic_code,
        raw.actor2_religion1_code,
        raw.actor2_religion2_code,
        raw.actor2_type1_code,
        raw.actor2_type2_code,
        raw.actor2_type3_code,
    )

    # Create locations
    actor1_geo = _make_location(
        raw.actor1_geo_type,
        raw.actor1_geo_fullname,
        raw.actor1_geo_country_code,
        raw.actor1_geo_adm1_code,
        raw.actor1_geo_adm2_code,
        raw.actor1_geo_lat,
        raw.actor1_geo_lon,
        raw.actor1_geo_feature_id,
    )

    actor2_geo = _make_location(
        raw.actor2_geo_type,
        raw.actor2_geo_fullname,
        raw.actor2_geo_country_code,
        raw.actor2_geo_adm1_code,
        raw.actor2_geo_adm2_code,
        raw.actor2_geo_lat,
        raw.actor2_geo_lon,
        raw.actor2_geo_feature_id,
    )

    action_geo = _make_location(
        raw.action_geo_type,
        raw.action_geo_fullname,
        raw.action_geo_country_code,
        raw.action_geo_adm1_code,
        raw.action_geo_adm2_code,
        raw.action_geo_lat,
        raw.action_geo_lon,
        raw.action_geo_feature_id,
    )

    return cls(
        global_event_id=_parse_int(raw.global_event_id),
        date=event_date,
        date_added=date_added_dt,
        source_url=raw.source_url if raw.source_url else None,
        actor1=actor1,
        actor2=actor2,
        event_code=raw.event_code,  # Keep as string to preserve leading zeros
        event_base_code=raw.event_base_code,
        event_root_code=raw.event_root_code,
        quad_class=_parse_int(raw.quad_class, default=1),
        goldstein_scale=_parse_float(raw.goldstein_scale, default=0.0),
        num_mentions=_parse_int(raw.num_mentions, default=0),
        num_sources=_parse_int(raw.num_sources, default=0),
        num_articles=_parse_int(raw.num_articles, default=0),
        avg_tone=_parse_float(raw.avg_tone, default=0.0),
        is_root_event=_parse_bool(raw.is_root_event),
        actor1_geo=actor1_geo,
        actor2_geo=actor2_geo,
        action_geo=action_geo,
        version=2,  # Default to v2, can be overridden
        is_translated=raw.is_translated,
        original_record_id=None,  # Not in raw data
    )
```

### `Mention`

Bases: `BaseModel`

Mention of a GDELT event in a source.

Represents a single mention of an event in a news article. Each event can have many mentions across different sources and times.

Source code in `src/py_gdelt/models/events.py`

```
class Mention(BaseModel):
    """Mention of a GDELT event in a source.

    Represents a single mention of an event in a news article. Each event
    can have many mentions across different sources and times.
    """

    global_event_id: int
    event_time: datetime
    mention_time: datetime
    mention_type: int  # 1=WEB, 2=Citation, 3=CORE, etc.
    source_name: str
    identifier: str  # URL, DOI, or citation
    sentence_id: int
    actor1_char_offset: int | None = None
    actor2_char_offset: int | None = None
    action_char_offset: int | None = None
    in_raw_text: bool = False
    confidence: int = Field(..., ge=10, le=100)  # 10-100
    doc_length: int = Field(default=0, ge=0)
    doc_tone: float = 0.0
    translation_info: str | None = None

    @classmethod
    def from_raw(cls, raw: _RawMention) -> Mention:
        """Convert internal _RawMention to public Mention model.

        Args:
            raw: Internal _RawMention dataclass from TAB-delimited parsing.

        Returns:
            Mention: Public Mention model with proper type conversion.

        Raises:
            ValueError: If required fields are missing or invalid.
        """

        # Helper to safely parse int
        def _parse_int(value: str | None, default: int = 0) -> int:
            if not value or value == "":
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        # Helper to safely parse float
        def _parse_float(value: str | None, default: float = 0.0) -> float:
            if not value or value == "":
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        # Helper to safely parse bool
        def _parse_bool(value: str | None) -> bool:
            if not value or value == "":
                return False
            return value.strip() == "1"

        # Parse event_time (YYYYMMDDHHMMSS)
        event_time = parse_gdelt_datetime(raw.event_time_full)

        # Parse mention_time (YYYYMMDDHHMMSS)
        mention_time = parse_gdelt_datetime(raw.mention_time_full)

        # Parse char offsets (can be empty string)
        actor1_offset = (
            _parse_int(raw.actor1_char_offset)
            if raw.actor1_char_offset and raw.actor1_char_offset != ""
            else None
        )
        actor2_offset = (
            _parse_int(raw.actor2_char_offset)
            if raw.actor2_char_offset and raw.actor2_char_offset != ""
            else None
        )
        action_offset = (
            _parse_int(raw.action_char_offset)
            if raw.action_char_offset and raw.action_char_offset != ""
            else None
        )

        return cls(
            global_event_id=_parse_int(raw.global_event_id),
            event_time=event_time,
            mention_time=mention_time,
            mention_type=_parse_int(raw.mention_type, default=1),
            source_name=raw.mention_source_name,
            identifier=raw.mention_identifier,
            sentence_id=_parse_int(raw.sentence_id, default=0),
            actor1_char_offset=actor1_offset,
            actor2_char_offset=actor2_offset,
            action_char_offset=action_offset,
            in_raw_text=_parse_bool(raw.in_raw_text),
            confidence=_parse_int(raw.confidence, default=50),
            doc_length=_parse_int(raw.mention_doc_length, default=0),
            doc_tone=_parse_float(raw.mention_doc_tone, default=0.0),
            translation_info=(
                raw.mention_doc_translation_info if raw.mention_doc_translation_info else None
            ),
        )
```

#### `from_raw(raw)`

Convert internal \_RawMention to public Mention model.

Parameters:

| Name  | Type          | Description                                                 | Default    |
| ----- | ------------- | ----------------------------------------------------------- | ---------- |
| `raw` | `_RawMention` | Internal \_RawMention dataclass from TAB-delimited parsing. | *required* |

Returns:

| Name      | Type      | Description                                       |
| --------- | --------- | ------------------------------------------------- |
| `Mention` | `Mention` | Public Mention model with proper type conversion. |

Raises:

| Type         | Description                                |
| ------------ | ------------------------------------------ |
| `ValueError` | If required fields are missing or invalid. |

Source code in `src/py_gdelt/models/events.py`

```
@classmethod
def from_raw(cls, raw: _RawMention) -> Mention:
    """Convert internal _RawMention to public Mention model.

    Args:
        raw: Internal _RawMention dataclass from TAB-delimited parsing.

    Returns:
        Mention: Public Mention model with proper type conversion.

    Raises:
        ValueError: If required fields are missing or invalid.
    """

    # Helper to safely parse int
    def _parse_int(value: str | None, default: int = 0) -> int:
        if not value or value == "":
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    # Helper to safely parse float
    def _parse_float(value: str | None, default: float = 0.0) -> float:
        if not value or value == "":
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    # Helper to safely parse bool
    def _parse_bool(value: str | None) -> bool:
        if not value or value == "":
            return False
        return value.strip() == "1"

    # Parse event_time (YYYYMMDDHHMMSS)
    event_time = parse_gdelt_datetime(raw.event_time_full)

    # Parse mention_time (YYYYMMDDHHMMSS)
    mention_time = parse_gdelt_datetime(raw.mention_time_full)

    # Parse char offsets (can be empty string)
    actor1_offset = (
        _parse_int(raw.actor1_char_offset)
        if raw.actor1_char_offset and raw.actor1_char_offset != ""
        else None
    )
    actor2_offset = (
        _parse_int(raw.actor2_char_offset)
        if raw.actor2_char_offset and raw.actor2_char_offset != ""
        else None
    )
    action_offset = (
        _parse_int(raw.action_char_offset)
        if raw.action_char_offset and raw.action_char_offset != ""
        else None
    )

    return cls(
        global_event_id=_parse_int(raw.global_event_id),
        event_time=event_time,
        mention_time=mention_time,
        mention_type=_parse_int(raw.mention_type, default=1),
        source_name=raw.mention_source_name,
        identifier=raw.mention_identifier,
        sentence_id=_parse_int(raw.sentence_id, default=0),
        actor1_char_offset=actor1_offset,
        actor2_char_offset=actor2_offset,
        action_char_offset=action_offset,
        in_raw_text=_parse_bool(raw.in_raw_text),
        confidence=_parse_int(raw.confidence, default=50),
        doc_length=_parse_int(raw.mention_doc_length, default=0),
        doc_tone=_parse_float(raw.mention_doc_tone, default=0.0),
        translation_info=(
            raw.mention_doc_translation_info if raw.mention_doc_translation_info else None
        ),
    )
```

### `Actor`

Bases: `BaseModel`

Actor in a GDELT event.

Represents an entity (person, organization, country, etc.) participating in an event. Uses CAMEO actor codes for classification.

Source code in `src/py_gdelt/models/events.py`

```
class Actor(BaseModel):
    """Actor in a GDELT event.

    Represents an entity (person, organization, country, etc.) participating in an event.
    Uses CAMEO actor codes for classification.
    """

    code: str | None = None
    name: str | None = None
    country_code: str | None = None  # FIPS code
    known_group_code: str | None = None
    ethnic_code: str | None = None
    religion1_code: str | None = None
    religion2_code: str | None = None
    type1_code: str | None = None
    type2_code: str | None = None
    type3_code: str | None = None

    @property
    def is_state_actor(self) -> bool:
        """Check if actor is a state/government actor.

        Returns:
            True if actor has a country code but no known group code,
            indicating a state-level actor.
        """
        return self.country_code is not None and self.known_group_code is None
```

#### `is_state_actor`

Check if actor is a state/government actor.

Returns:

| Type   | Description                                               |
| ------ | --------------------------------------------------------- |
| `bool` | True if actor has a country code but no known group code, |
| `bool` | indicating a state-level actor.                           |

## Article Models

### `Article`

Bases: `BaseModel`

Article from GDELT DOC API.

Represents a news article monitored by GDELT.

Source code in `src/py_gdelt/models/articles.py`

```
class Article(BaseModel):
    """
    Article from GDELT DOC API.

    Represents a news article monitored by GDELT.
    """

    # Core fields (from API)
    url: str
    title: str | None = None
    seendate: str | None = None  # Raw GDELT date string (YYYYMMDDHHMMSS)

    # Source information
    domain: str | None = None
    source_country: str | None = Field(default=None, alias="sourcecountry")
    language: str | None = None

    # Content
    socialimage: str | None = None  # Preview image URL

    # Tone analysis (optional)
    tone: float | None = None

    # Sharing metrics (optional)
    share_count: int | None = Field(default=None, alias="sharecount")

    model_config = {"populate_by_name": True}

    @property
    def seen_datetime(self) -> datetime | None:
        """
        Parse seendate to datetime.

        Returns:
            datetime object or None if parsing fails
        """
        return try_parse_gdelt_datetime(self.seendate)

    @property
    def is_english(self) -> bool:
        """Check if article is in English."""
        if not self.language:
            return False
        return self.language.lower() in ("english", "en")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump(by_alias=True)
```

#### `seen_datetime`

Parse seendate to datetime.

Returns:

| Type       | Description |
| ---------- | ----------- |
| \`datetime | None\`      |

#### `is_english`

Check if article is in English.

#### `to_dict()`

Convert to dictionary for serialization.

Source code in `src/py_gdelt/models/articles.py`

```
def to_dict(self) -> dict[str, Any]:
    """Convert to dictionary for serialization."""
    return self.model_dump(by_alias=True)
```

### `Timeline`

Bases: `BaseModel`

Timeline data from GDELT DOC API.

Contains time series data for article volume.

Source code in `src/py_gdelt/models/articles.py`

```
class Timeline(BaseModel):
    """
    Timeline data from GDELT DOC API.

    Contains time series data for article volume.
    """

    # The timeline data
    timeline: list[TimelinePoint] = Field(default_factory=list)

    # Metadata
    query: str | None = None
    total_articles: int | None = None

    @field_validator("timeline", mode="before")
    @classmethod
    def parse_timeline(cls, v: Any) -> list[TimelinePoint]:
        """Parse timeline from various formats.

        Handles both flat format and nested series format from timelinevol API:
        - Flat: [{"date": "...", "value": ...}, ...]
        - Nested: [{"series": "...", "data": [{"date": "...", "value": ...}]}]
        """
        if v is None:
            return []
        if isinstance(v, list):
            points: list[TimelinePoint] = []
            for item in v:
                if isinstance(item, TimelinePoint):
                    points.append(item)
                elif isinstance(item, dict):
                    # Check for nested series/data structure from timelinevol API
                    if "data" in item and isinstance(item["data"], list):
                        for dp in item["data"]:
                            if isinstance(dp, dict):
                                points.append(TimelinePoint.model_validate(dp))
                            else:
                                logger.warning(
                                    "Skipping non-dict timeline data point: %s", type(dp).__name__
                                )
                    else:
                        # Flat structure with date/value directly
                        points.append(TimelinePoint.model_validate(item))
            return points
        return []

    @property
    def points(self) -> list[TimelinePoint]:
        """Alias for timeline for cleaner access."""
        return self.timeline

    @property
    def dates(self) -> list[str]:
        """Get list of dates."""
        return [p.date for p in self.timeline]

    @property
    def values(self) -> list[float]:
        """Get list of values."""
        return [p.value for p in self.timeline]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timeline": [p.model_dump() for p in self.timeline],
            "query": self.query,
            "total_articles": self.total_articles,
        }

    def to_series(self) -> dict[str, float]:
        """
        Convert to date:value mapping.

        Useful for quick lookups and plotting.
        """
        return {p.date: p.value for p in self.timeline}
```

#### `points`

Alias for timeline for cleaner access.

#### `dates`

Get list of dates.

#### `values`

Get list of values.

#### `parse_timeline(v)`

Parse timeline from various formats.

Handles both flat format and nested series format from timelinevol API:

- Flat: [{"date": "...", "value": ...}, ...]
- Nested: \[{"series": "...", "data": [{"date": "...", "value": ...}]}\]

Source code in `src/py_gdelt/models/articles.py`

```
@field_validator("timeline", mode="before")
@classmethod
def parse_timeline(cls, v: Any) -> list[TimelinePoint]:
    """Parse timeline from various formats.

    Handles both flat format and nested series format from timelinevol API:
    - Flat: [{"date": "...", "value": ...}, ...]
    - Nested: [{"series": "...", "data": [{"date": "...", "value": ...}]}]
    """
    if v is None:
        return []
    if isinstance(v, list):
        points: list[TimelinePoint] = []
        for item in v:
            if isinstance(item, TimelinePoint):
                points.append(item)
            elif isinstance(item, dict):
                # Check for nested series/data structure from timelinevol API
                if "data" in item and isinstance(item["data"], list):
                    for dp in item["data"]:
                        if isinstance(dp, dict):
                            points.append(TimelinePoint.model_validate(dp))
                        else:
                            logger.warning(
                                "Skipping non-dict timeline data point: %s", type(dp).__name__
                            )
                else:
                    # Flat structure with date/value directly
                    points.append(TimelinePoint.model_validate(item))
        return points
    return []
```

#### `to_dict()`

Convert to dictionary.

Source code in `src/py_gdelt/models/articles.py`

```
def to_dict(self) -> dict[str, Any]:
    """Convert to dictionary."""
    return {
        "timeline": [p.model_dump() for p in self.timeline],
        "query": self.query,
        "total_articles": self.total_articles,
    }
```

#### `to_series()`

Convert to date:value mapping.

Useful for quick lookups and plotting.

Source code in `src/py_gdelt/models/articles.py`

```
def to_series(self) -> dict[str, float]:
    """
    Convert to date:value mapping.

    Useful for quick lookups and plotting.
    """
    return {p.date: p.value for p in self.timeline}
```

### `TimelinePoint`

Bases: `BaseModel`

Single data point in a timeline.

Source code in `src/py_gdelt/models/articles.py`

```
class TimelinePoint(BaseModel):
    """Single data point in a timeline."""

    date: str
    value: float = Field(default=0, alias="count")

    # Optional breakdown
    tone: float | None = None

    model_config = {"populate_by_name": True}

    @property
    def parsed_date(self) -> datetime | None:
        """Parse date string to datetime."""
        return try_parse_gdelt_datetime(self.date)
```

#### `parsed_date`

Parse date string to datetime.

## GKG Models

### `GKGRecord`

Bases: `BaseModel`

GDELT Global Knowledge Graph record.

Represents enriched content analysis of a news article or document, including extracted themes, entities, locations, tone, and other metadata.

Attributes:

| Name                 | Type                  | Description                                                                         |
| -------------------- | --------------------- | ----------------------------------------------------------------------------------- |
| `record_id`          | `str`                 | Unique identifier in format "YYYYMMDDHHMMSS-seq" or with "-T" suffix for translated |
| `date`               | `datetime`            | Publication date/time                                                               |
| `source_url`         | `str`                 | URL of the source document                                                          |
| `source_name`        | `str`                 | Common name of the source                                                           |
| `source_collection`  | `int`                 | Source collection identifier (1=WEB, 2=Citation, etc.)                              |
| `themes`             | `list[EntityMention]` | Extracted themes/topics                                                             |
| `persons`            | `list[EntityMention]` | Extracted person names                                                              |
| `organizations`      | `list[EntityMention]` | Extracted organization names                                                        |
| `locations`          | `list[Location]`      | Extracted geographic locations                                                      |
| `tone`               | \`ToneScores          | None\`                                                                              |
| `gcam`               | `dict[str, float]`    | GCAM emotional dimension scores as dict                                             |
| `quotations`         | `list[Quotation]`     | Extracted quotations (v2.1+ only)                                                   |
| `amounts`            | `list[Amount]`        | Extracted numerical amounts (v2.1+ only)                                            |
| `sharing_image`      | \`str                 | None\`                                                                              |
| `all_names`          | `list[str]`           | All extracted names as flat list                                                    |
| `version`            | `int`                 | GDELT version (1 or 2)                                                              |
| `is_translated`      | `bool`                | Whether this is a translated document                                               |
| `original_record_id` | \`str                 | None\`                                                                              |
| `translation_info`   | \`str                 | None\`                                                                              |

Source code in `src/py_gdelt/models/gkg.py`

```
class GKGRecord(BaseModel):
    """GDELT Global Knowledge Graph record.

    Represents enriched content analysis of a news article or document, including
    extracted themes, entities, locations, tone, and other metadata.

    Attributes:
        record_id: Unique identifier in format "YYYYMMDDHHMMSS-seq" or with "-T" suffix for translated
        date: Publication date/time
        source_url: URL of the source document
        source_name: Common name of the source
        source_collection: Source collection identifier (1=WEB, 2=Citation, etc.)
        themes: Extracted themes/topics
        persons: Extracted person names
        organizations: Extracted organization names
        locations: Extracted geographic locations
        tone: Document tone analysis scores
        gcam: GCAM emotional dimension scores as dict
        quotations: Extracted quotations (v2.1+ only)
        amounts: Extracted numerical amounts (v2.1+ only)
        sharing_image: Primary sharing image URL if any
        all_names: All extracted names as flat list
        version: GDELT version (1 or 2)
        is_translated: Whether this is a translated document
        original_record_id: Original record ID if translated
        translation_info: Translation metadata string
    """

    # Identifiers
    record_id: str
    date: datetime
    source_url: str
    source_name: str
    source_collection: int

    # Extracted entities
    themes: list[EntityMention] = Field(default_factory=list)
    persons: list[EntityMention] = Field(default_factory=list)
    organizations: list[EntityMention] = Field(default_factory=list)
    locations: list[Location] = Field(default_factory=list)

    # Tone
    tone: ToneScores | None = None

    # GCAM emotional dimensions
    gcam: dict[str, float] = Field(default_factory=dict)

    # V2.1+ fields
    quotations: list[Quotation] = Field(default_factory=list)
    amounts: list[Amount] = Field(default_factory=list)

    # Extra fields
    sharing_image: str | None = None
    all_names: list[str] = Field(default_factory=list)

    # Metadata
    version: int = 2
    is_translated: bool = False
    original_record_id: str | None = None
    translation_info: str | None = None

    @classmethod
    def from_raw(cls, raw: _RawGKG) -> GKGRecord:
        """Convert internal _RawGKG to public GKGRecord model.

        This method handles parsing the complex delimited fields from GKG v2.1 format:
        - Themes: semicolon-delimited "theme,offset" pairs
        - GCAM: semicolon-delimited "key:value" pairs
        - Quotations: pipe-delimited records with format "offset#length#verb#quote"
        - Amounts: semicolon-delimited "amount,object,offset" triples
        - Locations: semicolon-delimited with multiple sub-fields
        - Tone: comma-separated values

        Args:
            raw: Internal _RawGKG dataclass from TSV parsing

        Returns:
            Validated GKGRecord with all fields parsed and typed
        """
        # Detect translation
        is_translated = raw.gkg_record_id.endswith("-T")
        original_record_id = None
        if is_translated:
            original_record_id = raw.gkg_record_id[:-2]

        # Parse date (format: YYYYMMDDHHMMSS)
        date = parse_gdelt_datetime(raw.date)

        # Parse themes from V2 enhanced (preferred) or V1
        themes = _parse_themes(raw.themes_v2_enhanced or raw.themes_v1)

        # Parse persons
        persons = _parse_entities(raw.persons_v2_enhanced or raw.persons_v1, entity_type="PERSON")

        # Parse organizations
        organizations = _parse_entities(
            raw.organizations_v2_enhanced or raw.organizations_v1,
            entity_type="ORG",
        )

        # Parse locations
        locations = _parse_locations(raw.locations_v2_enhanced or raw.locations_v1)

        # Parse tone
        tone = _parse_tone(raw.tone) if raw.tone else None

        # Parse GCAM
        gcam = _parse_gcam(raw.gcam) if raw.gcam else {}

        # Parse quotations (v2.1+)
        quotations = _parse_quotations(raw.quotations) if raw.quotations else []

        # Parse amounts (v2.1+)
        amounts = _parse_amounts(raw.amounts) if raw.amounts else []

        # Parse all_names
        all_names = (
            [name.strip() for name in raw.all_names.split(";") if name.strip()]
            if raw.all_names
            else []
        )

        # Determine version (if v2 enhanced fields exist, it's v2)
        version = 2 if raw.themes_v2_enhanced else 1

        return cls(
            record_id=raw.gkg_record_id,
            date=date,
            source_url=raw.document_identifier,
            source_name=raw.source_common_name,
            source_collection=int(raw.source_collection_id),
            themes=themes,
            persons=persons,
            organizations=organizations,
            locations=locations,
            tone=tone,
            gcam=gcam,
            quotations=quotations,
            amounts=amounts,
            sharing_image=raw.sharing_image,
            all_names=all_names,
            version=version,
            is_translated=is_translated,
            original_record_id=original_record_id,
            translation_info=raw.translation_info,
        )

    @property
    def primary_theme(self) -> str | None:
        """Get the first/primary theme if any.

        Returns:
            The name of the first theme, or None if no themes exist
        """
        if not self.themes:
            return None
        return self.themes[0].name

    @property
    def has_quotations(self) -> bool:
        """Check if record has extracted quotations.

        Returns:
            True if one or more quotations were extracted
        """
        return len(self.quotations) > 0
```

#### `primary_theme`

Get the first/primary theme if any.

Returns:

| Type  | Description |
| ----- | ----------- |
| \`str | None\`      |

#### `has_quotations`

Check if record has extracted quotations.

Returns:

| Type   | Description                                   |
| ------ | --------------------------------------------- |
| `bool` | True if one or more quotations were extracted |

#### `from_raw(raw)`

Convert internal \_RawGKG to public GKGRecord model.

This method handles parsing the complex delimited fields from GKG v2.1 format:

- Themes: semicolon-delimited "theme,offset" pairs
- GCAM: semicolon-delimited "key:value" pairs
- Quotations: pipe-delimited records with format "offset#length#verb#quote"
- Amounts: semicolon-delimited "amount,object,offset" triples
- Locations: semicolon-delimited with multiple sub-fields
- Tone: comma-separated values

Parameters:

| Name  | Type      | Description                                  | Default    |
| ----- | --------- | -------------------------------------------- | ---------- |
| `raw` | `_RawGKG` | Internal \_RawGKG dataclass from TSV parsing | *required* |

Returns:

| Type        | Description                                          |
| ----------- | ---------------------------------------------------- |
| `GKGRecord` | Validated GKGRecord with all fields parsed and typed |

Source code in `src/py_gdelt/models/gkg.py`

```
@classmethod
def from_raw(cls, raw: _RawGKG) -> GKGRecord:
    """Convert internal _RawGKG to public GKGRecord model.

    This method handles parsing the complex delimited fields from GKG v2.1 format:
    - Themes: semicolon-delimited "theme,offset" pairs
    - GCAM: semicolon-delimited "key:value" pairs
    - Quotations: pipe-delimited records with format "offset#length#verb#quote"
    - Amounts: semicolon-delimited "amount,object,offset" triples
    - Locations: semicolon-delimited with multiple sub-fields
    - Tone: comma-separated values

    Args:
        raw: Internal _RawGKG dataclass from TSV parsing

    Returns:
        Validated GKGRecord with all fields parsed and typed
    """
    # Detect translation
    is_translated = raw.gkg_record_id.endswith("-T")
    original_record_id = None
    if is_translated:
        original_record_id = raw.gkg_record_id[:-2]

    # Parse date (format: YYYYMMDDHHMMSS)
    date = parse_gdelt_datetime(raw.date)

    # Parse themes from V2 enhanced (preferred) or V1
    themes = _parse_themes(raw.themes_v2_enhanced or raw.themes_v1)

    # Parse persons
    persons = _parse_entities(raw.persons_v2_enhanced or raw.persons_v1, entity_type="PERSON")

    # Parse organizations
    organizations = _parse_entities(
        raw.organizations_v2_enhanced or raw.organizations_v1,
        entity_type="ORG",
    )

    # Parse locations
    locations = _parse_locations(raw.locations_v2_enhanced or raw.locations_v1)

    # Parse tone
    tone = _parse_tone(raw.tone) if raw.tone else None

    # Parse GCAM
    gcam = _parse_gcam(raw.gcam) if raw.gcam else {}

    # Parse quotations (v2.1+)
    quotations = _parse_quotations(raw.quotations) if raw.quotations else []

    # Parse amounts (v2.1+)
    amounts = _parse_amounts(raw.amounts) if raw.amounts else []

    # Parse all_names
    all_names = (
        [name.strip() for name in raw.all_names.split(";") if name.strip()]
        if raw.all_names
        else []
    )

    # Determine version (if v2 enhanced fields exist, it's v2)
    version = 2 if raw.themes_v2_enhanced else 1

    return cls(
        record_id=raw.gkg_record_id,
        date=date,
        source_url=raw.document_identifier,
        source_name=raw.source_common_name,
        source_collection=int(raw.source_collection_id),
        themes=themes,
        persons=persons,
        organizations=organizations,
        locations=locations,
        tone=tone,
        gcam=gcam,
        quotations=quotations,
        amounts=amounts,
        sharing_image=raw.sharing_image,
        all_names=all_names,
        version=version,
        is_translated=is_translated,
        original_record_id=original_record_id,
        translation_info=raw.translation_info,
    )
```

### `Quotation`

Bases: `BaseModel`

Quote extracted from a GKG document.

Source code in `src/py_gdelt/models/gkg.py`

```
class Quotation(BaseModel):
    """Quote extracted from a GKG document."""

    offset: int
    length: int
    verb: str
    quote: str
```

### `Amount`

Bases: `BaseModel`

Numerical amount extracted from a GKG document.

Source code in `src/py_gdelt/models/gkg.py`

```
class Amount(BaseModel):
    """Numerical amount extracted from a GKG document."""

    amount: float
    object: str
    offset: int
```

### `TVGKGRecord`

Bases: `BaseModel`

TV-GKG record with timecode mapping support.

Uses composition instead of inheritance from GKGRecord. Reuses GKG parsing logic but creates independent model.

Note

The following GKG fields are always empty in TV-GKG:

- sharing_image, related_images, social_image_embeds, social_video_embeds
- quotations, all_names, dates, amounts, translation_info

Special field

- timecode_mappings: Parsed from CHARTIMECODEOFFSETTOC in extras

Attributes:

| Name                  | Type                    | Description                                   |
| --------------------- | ----------------------- | --------------------------------------------- |
| `gkg_record_id`       | `str`                   | Unique record identifier.                     |
| `date`                | `datetime`              | Timestamp of the analysis.                    |
| `source_identifier`   | `str`                   | Source collection identifier.                 |
| `document_identifier` | `str`                   | URL or identifier of the source document.     |
| `themes`              | `list[str]`             | List of detected themes.                      |
| `locations`           | `list[str]`             | List of detected locations.                   |
| `persons`             | `list[str]`             | List of detected persons.                     |
| `organizations`       | `list[str]`             | List of detected organizations.               |
| `tone`                | \`float                 | None\`                                        |
| `extras`              | `str`                   | Raw extras field content.                     |
| `timecode_mappings`   | `list[TimecodeMapping]` | Parsed character offset to timecode mappings. |

Source code in `src/py_gdelt/models/gkg.py`

```
class TVGKGRecord(BaseModel):
    """TV-GKG record with timecode mapping support.

    Uses composition instead of inheritance from GKGRecord.
    Reuses GKG parsing logic but creates independent model.

    Note:
        The following GKG fields are always empty in TV-GKG:
        - sharing_image, related_images, social_image_embeds, social_video_embeds
        - quotations, all_names, dates, amounts, translation_info

    Special field:
        - timecode_mappings: Parsed from CHARTIMECODEOFFSETTOC in extras

    Attributes:
        gkg_record_id: Unique record identifier.
        date: Timestamp of the analysis.
        source_identifier: Source collection identifier.
        document_identifier: URL or identifier of the source document.
        themes: List of detected themes.
        locations: List of detected locations.
        persons: List of detected persons.
        organizations: List of detected organizations.
        tone: Average tone score.
        extras: Raw extras field content.
        timecode_mappings: Parsed character offset to timecode mappings.
    """

    gkg_record_id: str
    date: datetime
    source_identifier: str
    document_identifier: str
    themes: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    persons: list[str] = Field(default_factory=list)
    organizations: list[str] = Field(default_factory=list)
    tone: float | None = None
    extras: str = ""
    timecode_mappings: list[TimecodeMapping] = Field(default_factory=list)

    @classmethod
    def from_raw(cls, raw: _RawGKG) -> TVGKGRecord:
        """Convert raw GKG to TV-GKG with timecode extraction.

        Args:
            raw: Internal raw GKG representation.

        Returns:
            Validated TVGKGRecord instance.

        Raises:
            ValueError: If date parsing fails.
        """
        timecodes = cls._parse_timecode_toc(raw.extras_xml)
        return cls(
            gkg_record_id=raw.gkg_record_id,
            date=parse_gdelt_datetime(raw.date),
            source_identifier=raw.source_common_name or "",
            document_identifier=raw.document_identifier or "",
            themes=_parse_semicolon_delimited(raw.themes_v1),
            locations=_parse_semicolon_delimited(raw.locations_v1),
            persons=_parse_semicolon_delimited(raw.persons_v1),
            organizations=_parse_semicolon_delimited(raw.organizations_v1),
            tone=_parse_tone_simple(raw.tone),
            extras=raw.extras_xml or "",
            timecode_mappings=timecodes,
        )

    @staticmethod
    def _parse_timecode_toc(extras: str | None) -> list[TimecodeMapping]:
        """Parse CHARTIMECODEOFFSETTOC:offset:timecode;offset:timecode;...

        Real format discovered: offset:timecode pairs separated by semicolons.

        Args:
            extras: Raw extras XML/text field from GKG record.

        Returns:
            List of TimecodeMapping instances.
        """
        if not extras:
            return []
        # Look for CHARTIMECODEOFFSETTOC block in extras
        for block in extras.split("<SPECIAL>"):
            if block.startswith("CHARTIMECODEOFFSETTOC:"):
                content = block[len("CHARTIMECODEOFFSETTOC:") :]
                mappings: list[TimecodeMapping] = []
                for raw_entry in content.split(";"):
                    entry = raw_entry.strip()
                    if ":" in entry:
                        parts = entry.split(":", 1)
                        try:
                            mappings.append(
                                TimecodeMapping(
                                    char_offset=int(parts[0]),
                                    timecode=parts[1],
                                ),
                            )
                        except (ValueError, IndexError):
                            logger.debug("Failed to parse timecode entry: %r", entry)
                            continue
                logger.debug("Parsed %d timecode mappings", len(mappings))
                return mappings
        # No CHARTIMECODEOFFSETTOC block found - this is normal for non-TV records
        if "<SPECIAL>" in extras:
            logger.debug("SPECIAL blocks present but no CHARTIMECODEOFFSETTOC found")
        return []
```

#### `from_raw(raw)`

Convert raw GKG to TV-GKG with timecode extraction.

Parameters:

| Name  | Type      | Description                      | Default    |
| ----- | --------- | -------------------------------- | ---------- |
| `raw` | `_RawGKG` | Internal raw GKG representation. | *required* |

Returns:

| Type          | Description                     |
| ------------- | ------------------------------- |
| `TVGKGRecord` | Validated TVGKGRecord instance. |

Raises:

| Type         | Description            |
| ------------ | ---------------------- |
| `ValueError` | If date parsing fails. |

Source code in `src/py_gdelt/models/gkg.py`

```
@classmethod
def from_raw(cls, raw: _RawGKG) -> TVGKGRecord:
    """Convert raw GKG to TV-GKG with timecode extraction.

    Args:
        raw: Internal raw GKG representation.

    Returns:
        Validated TVGKGRecord instance.

    Raises:
        ValueError: If date parsing fails.
    """
    timecodes = cls._parse_timecode_toc(raw.extras_xml)
    return cls(
        gkg_record_id=raw.gkg_record_id,
        date=parse_gdelt_datetime(raw.date),
        source_identifier=raw.source_common_name or "",
        document_identifier=raw.document_identifier or "",
        themes=_parse_semicolon_delimited(raw.themes_v1),
        locations=_parse_semicolon_delimited(raw.locations_v1),
        persons=_parse_semicolon_delimited(raw.persons_v1),
        organizations=_parse_semicolon_delimited(raw.organizations_v1),
        tone=_parse_tone_simple(raw.tone),
        extras=raw.extras_xml or "",
        timecode_mappings=timecodes,
    )
```

### `TimecodeMapping`

Bases: `NamedTuple`

Character offset to video timecode mapping (lightweight).

Used in TV-GKG to map text positions to video timestamps.

Attributes:

| Name          | Type  | Description                         |
| ------------- | ----- | ----------------------------------- |
| `char_offset` | `int` | Character offset in the transcript. |
| `timecode`    | `str` | Video timecode (e.g., "00:01:23").  |

Source code in `src/py_gdelt/models/gkg.py`

```
class TimecodeMapping(NamedTuple):
    """Character offset to video timecode mapping (lightweight).

    Used in TV-GKG to map text positions to video timestamps.

    Attributes:
        char_offset: Character offset in the transcript.
        timecode: Video timecode (e.g., "00:01:23").
    """

    char_offset: int
    timecode: str
```

## NGrams Models

### `NGramRecord`

Bases: `BaseModel`

GDELT NGram 3.0 record.

Represents an n-gram (word or phrase) occurrence in web content, including context and source information.

Source code in `src/py_gdelt/models/ngrams.py`

```
class NGramRecord(BaseModel):
    """GDELT NGram 3.0 record.

    Represents an n-gram (word or phrase) occurrence in web content,
    including context and source information.
    """

    date: datetime
    ngram: str  # Word or character
    language: str  # ISO 639-1/2
    segment_type: int  # 1=space-delimited, 2=scriptio continua
    position: int  # Article decile (0-90, where 0 = first 10% of article)
    pre_context: str  # ~7 words before
    post_context: str  # ~7 words after
    url: str

    @classmethod
    def from_raw(cls, raw: _RawNGram) -> NGramRecord:
        """Convert internal _RawNGram to public NGramRecord model.

        Args:
            raw: Internal raw ngram representation with string fields

        Returns:
            Validated NGramRecord instance

        Raises:
            ValueError: If date parsing or type conversion fails
        """
        return cls(
            date=parse_gdelt_datetime(raw.date),
            ngram=raw.ngram,
            language=raw.language,
            segment_type=int(raw.segment_type),
            position=int(raw.position),
            pre_context=raw.pre_context,
            post_context=raw.post_context,
            url=raw.url,
        )

    @property
    def context(self) -> str:
        """Get full context (pre + ngram + post).

        Returns:
            Full context string with ngram surrounded by pre and post context
        """
        return f"{self.pre_context} {self.ngram} {self.post_context}"

    @property
    def is_early_in_article(self) -> bool:
        """Check if ngram appears in first 30% of article.

        Returns:
            True if position <= 20 (first 30% of article)
        """
        return self.position <= 20

    @property
    def is_late_in_article(self) -> bool:
        """Check if ngram appears in last 30% of article.

        Returns:
            True if position >= 70 (last 30% of article)
        """
        return self.position >= 70
```

#### `context`

Get full context (pre + ngram + post).

Returns:

| Type  | Description                                                       |
| ----- | ----------------------------------------------------------------- |
| `str` | Full context string with ngram surrounded by pre and post context |

#### `is_early_in_article`

Check if ngram appears in first 30% of article.

Returns:

| Type   | Description                                    |
| ------ | ---------------------------------------------- |
| `bool` | True if position \<= 20 (first 30% of article) |

#### `is_late_in_article`

Check if ngram appears in last 30% of article.

Returns:

| Type   | Description                                  |
| ------ | -------------------------------------------- |
| `bool` | True if position >= 70 (last 30% of article) |

#### `from_raw(raw)`

Convert internal \_RawNGram to public NGramRecord model.

Parameters:

| Name  | Type        | Description                                          | Default    |
| ----- | ----------- | ---------------------------------------------------- | ---------- |
| `raw` | `_RawNGram` | Internal raw ngram representation with string fields | *required* |

Returns:

| Type          | Description                    |
| ------------- | ------------------------------ |
| `NGramRecord` | Validated NGramRecord instance |

Raises:

| Type         | Description                              |
| ------------ | ---------------------------------------- |
| `ValueError` | If date parsing or type conversion fails |

Source code in `src/py_gdelt/models/ngrams.py`

```
@classmethod
def from_raw(cls, raw: _RawNGram) -> NGramRecord:
    """Convert internal _RawNGram to public NGramRecord model.

    Args:
        raw: Internal raw ngram representation with string fields

    Returns:
        Validated NGramRecord instance

    Raises:
        ValueError: If date parsing or type conversion fails
    """
    return cls(
        date=parse_gdelt_datetime(raw.date),
        ngram=raw.ngram,
        language=raw.language,
        segment_type=int(raw.segment_type),
        position=int(raw.position),
        pre_context=raw.pre_context,
        post_context=raw.post_context,
        url=raw.url,
    )
```

### `BroadcastNGramRecord`

Bases: `BaseModel`

Broadcast NGram frequency record (TV or Radio).

Unified model for both TV and Radio NGrams since schemas are compatible. TV NGrams: 5 columns (DATE, STATION, HOUR, WORD, COUNT) Radio NGrams: 6 columns (DATE, STATION, HOUR, NGRAM, COUNT, SHOW)

Attributes:

| Name      | Type              | Description                           |
| --------- | ----------------- | ------------------------------------- |
| `date`    | `date`            | Date of the broadcast.                |
| `station` | `str`             | Station identifier (e.g., CNN, KQED). |
| `hour`    | `int`             | Hour of broadcast (0-23).             |
| `ngram`   | `str`             | Word or phrase.                       |
| `count`   | `int`             | Frequency count.                      |
| `show`    | \`str             | None\`                                |
| `source`  | `BroadcastSource` | Indicates origin (tv or radio).       |

Source code in `src/py_gdelt/models/ngrams.py`

```
class BroadcastNGramRecord(BaseModel):
    """Broadcast NGram frequency record (TV or Radio).

    Unified model for both TV and Radio NGrams since schemas are compatible.
    TV NGrams: 5 columns (DATE, STATION, HOUR, WORD, COUNT)
    Radio NGrams: 6 columns (DATE, STATION, HOUR, NGRAM, COUNT, SHOW)

    Attributes:
        date: Date of the broadcast.
        station: Station identifier (e.g., CNN, KQED).
        hour: Hour of broadcast (0-23).
        ngram: Word or phrase.
        count: Frequency count.
        show: Show name (Radio only, None for TV).
        source: Indicates origin (tv or radio).
    """

    date: date_type
    station: str
    hour: int = Field(ge=0, le=23)
    ngram: str
    count: int = Field(ge=0)
    show: str | None = None
    source: BroadcastSource

    @classmethod
    def from_raw(cls, raw: _RawBroadcastNGram, source: BroadcastSource) -> BroadcastNGramRecord:
        """Convert internal _RawBroadcastNGram to public model.

        Args:
            raw: Internal raw broadcast ngram representation.
            source: Source type (TV or Radio).

        Returns:
            Validated BroadcastNGramRecord instance.

        Raises:
            ValueError: If date parsing or type conversion fails.
        """
        return cls(
            date=parse_gdelt_date(raw.date),
            station=raw.station,
            hour=int(raw.hour),
            ngram=raw.ngram,
            count=int(raw.count),
            show=raw.show if raw.show else None,
            source=source,
        )
```

#### `from_raw(raw, source)`

Convert internal \_RawBroadcastNGram to public model.

Parameters:

| Name     | Type                 | Description                                  | Default    |
| -------- | -------------------- | -------------------------------------------- | ---------- |
| `raw`    | `_RawBroadcastNGram` | Internal raw broadcast ngram representation. | *required* |
| `source` | `BroadcastSource`    | Source type (TV or Radio).                   | *required* |

Returns:

| Type                   | Description                              |
| ---------------------- | ---------------------------------------- |
| `BroadcastNGramRecord` | Validated BroadcastNGramRecord instance. |

Raises:

| Type         | Description                               |
| ------------ | ----------------------------------------- |
| `ValueError` | If date parsing or type conversion fails. |

Source code in `src/py_gdelt/models/ngrams.py`

```
@classmethod
def from_raw(cls, raw: _RawBroadcastNGram, source: BroadcastSource) -> BroadcastNGramRecord:
    """Convert internal _RawBroadcastNGram to public model.

    Args:
        raw: Internal raw broadcast ngram representation.
        source: Source type (TV or Radio).

    Returns:
        Validated BroadcastNGramRecord instance.

    Raises:
        ValueError: If date parsing or type conversion fails.
    """
    return cls(
        date=parse_gdelt_date(raw.date),
        station=raw.station,
        hour=int(raw.hour),
        ngram=raw.ngram,
        count=int(raw.count),
        show=raw.show if raw.show else None,
        source=source,
    )
```

### `BroadcastSource`

Bases: `str`, `Enum`

Source type for broadcast NGrams.

Source code in `src/py_gdelt/models/ngrams.py`

```
class BroadcastSource(str, Enum):
    """Source type for broadcast NGrams."""

    TV = "tv"
    RADIO = "radio"
```

### `TVNGramRecord = BroadcastNGramRecord`

### `RadioNGramRecord = BroadcastNGramRecord`

## VGKG Models

### `VGKGRecord`

Bases: `BaseModel`

Visual GKG record with Cloud Vision annotations.

Nested structures (labels, faces, etc.) use TypedDict for performance. See tests/benchmarks/test_bench_vgkg_parsing.py for rationale.

Attributes:

| Name                   | Type                       | Description                                     |
| ---------------------- | -------------------------- | ----------------------------------------------- |
| `date`                 | `datetime`                 | Timestamp of the analysis.                      |
| `document_identifier`  | `str`                      | Source article URL.                             |
| `image_url`            | `str`                      | URL of the analyzed image.                      |
| `labels`               | `list[VisionLabelDict]`    | List of detected labels with confidence scores. |
| `logos`                | `list[VisionLabelDict]`    | List of detected logos.                         |
| `web_entities`         | `list[VisionLabelDict]`    | List of web entities matched to the image.      |
| `safe_search`          | \`SafeSearchDict           | None\`                                          |
| `faces`                | `list[FaceAnnotationDict]` | List of detected faces with pose information.   |
| `ocr_text`             | `str`                      | Text extracted via OCR.                         |
| `landmark_annotations` | `list[VisionLabelDict]`    | List of detected landmarks.                     |
| `domain`               | `str`                      | Domain of the source article.                   |
| `raw_json`             | `str`                      | Full Cloud Vision API JSON response.            |

Source code in `src/py_gdelt/models/vgkg.py`

```
class VGKGRecord(BaseModel):
    """Visual GKG record with Cloud Vision annotations.

    Nested structures (labels, faces, etc.) use TypedDict for performance.
    See tests/benchmarks/test_bench_vgkg_parsing.py for rationale.

    Attributes:
        date: Timestamp of the analysis.
        document_identifier: Source article URL.
        image_url: URL of the analyzed image.
        labels: List of detected labels with confidence scores.
        logos: List of detected logos.
        web_entities: List of web entities matched to the image.
        safe_search: SafeSearch annotation scores.
        faces: List of detected faces with pose information.
        ocr_text: Text extracted via OCR.
        landmark_annotations: List of detected landmarks.
        domain: Domain of the source article.
        raw_json: Full Cloud Vision API JSON response.
    """

    date: datetime
    document_identifier: str
    image_url: str
    labels: list[VisionLabelDict] = Field(default_factory=list)
    logos: list[VisionLabelDict] = Field(default_factory=list)
    web_entities: list[VisionLabelDict] = Field(default_factory=list)
    safe_search: SafeSearchDict | None = None
    faces: list[FaceAnnotationDict] = Field(default_factory=list)
    ocr_text: str = ""
    landmark_annotations: list[VisionLabelDict] = Field(default_factory=list)
    domain: str = ""
    raw_json: str = ""  # Keep as string - users can parse with json.loads() if needed

    @classmethod
    def from_raw(cls, raw: _RawVGKG) -> VGKGRecord:
        """Convert internal _RawVGKG to validated VGKGRecord model.

        Args:
            raw: Internal raw VGKG representation with string fields.

        Returns:
            Validated VGKGRecord instance.

        Raises:
            ValueError: If date parsing or type conversion fails.
        """
        return cls(
            date=parse_gdelt_datetime(raw.date),
            document_identifier=raw.document_identifier,
            image_url=raw.image_url,
            labels=cls._parse_labels(raw.labels),
            logos=cls._parse_labels(raw.logos),
            web_entities=cls._parse_labels(raw.web_entities),
            safe_search=cls._parse_safe_search(raw.safe_search),
            faces=cls._parse_faces(raw.faces),
            ocr_text=raw.ocr_text or "",
            landmark_annotations=cls._parse_labels(raw.landmark_annotations),
            domain=raw.domain or "",
            raw_json=raw.raw_json or "",
        )

    @classmethod
    def _parse_labels(cls, raw: str) -> list[VisionLabelDict]:
        """Parse Label<FIELD>Confidence<FIELD>MID<RECORD>... format.

        Args:
            raw: Delimited string with label records.

        Returns:
            List of VisionLabelDict objects.
        """
        if not raw:
            return []
        labels: list[VisionLabelDict] = []
        for record in raw.split(_RECORD_DELIM):
            if not record.strip():
                continue
            fields = record.split(_FIELD_DELIM)
            if len(fields) >= 2:
                try:
                    labels.append(
                        {
                            "description": fields[0],
                            "confidence": float(fields[1]) if fields[1] else 0.0,
                            "mid": fields[2] if len(fields) > 2 and fields[2] else None,
                        }
                    )
                except (ValueError, IndexError):
                    continue
        return labels

    @classmethod
    def _parse_safe_search(cls, raw: str) -> SafeSearchDict | None:
        """Parse safe_search field (4 integers).

        Args:
            raw: Delimited string with 4 safe search scores.

        Returns:
            SafeSearchDict or None if parsing fails.
        """
        if not raw:
            return None
        fields = raw.split(_FIELD_DELIM)
        if len(fields) < 4:
            return None
        try:
            return {
                "adult": int(fields[0]) if fields[0] else -1,
                "spoof": int(fields[1]) if fields[1] else -1,
                "medical": int(fields[2]) if fields[2] else -1,
                "violence": int(fields[3]) if fields[3] else -1,
            }
        except (ValueError, IndexError):
            return None

    @classmethod
    def _parse_faces(cls, raw: str) -> list[FaceAnnotationDict]:
        """Parse faces field (roll/pan/tilt angles, NOT emotions).

        Args:
            raw: Delimited string with face records.

        Returns:
            List of FaceAnnotationDict objects.
        """
        if not raw:
            return []
        faces: list[FaceAnnotationDict] = []
        for record in raw.split(_RECORD_DELIM):
            if not record.strip():
                continue
            fields = record.split(_FIELD_DELIM)
            if len(fields) >= 5:
                try:
                    faces.append(
                        {
                            "confidence": float(fields[0]) if fields[0] else 0.0,
                            "roll": float(fields[1]) if fields[1] else 0.0,
                            "pan": float(fields[2]) if fields[2] else 0.0,
                            "tilt": float(fields[3]) if fields[3] else 0.0,
                            "detection_confidence": float(fields[4]) if fields[4] else 0.0,
                            "bounding_box": fields[5] if len(fields) > 5 and fields[5] else None,
                        }
                    )
                except (ValueError, IndexError):
                    continue
        return faces
```

#### `from_raw(raw)`

Convert internal \_RawVGKG to validated VGKGRecord model.

Parameters:

| Name  | Type       | Description                                          | Default    |
| ----- | ---------- | ---------------------------------------------------- | ---------- |
| `raw` | `_RawVGKG` | Internal raw VGKG representation with string fields. | *required* |

Returns:

| Type         | Description                    |
| ------------ | ------------------------------ |
| `VGKGRecord` | Validated VGKGRecord instance. |

Raises:

| Type         | Description                               |
| ------------ | ----------------------------------------- |
| `ValueError` | If date parsing or type conversion fails. |

Source code in `src/py_gdelt/models/vgkg.py`

```
@classmethod
def from_raw(cls, raw: _RawVGKG) -> VGKGRecord:
    """Convert internal _RawVGKG to validated VGKGRecord model.

    Args:
        raw: Internal raw VGKG representation with string fields.

    Returns:
        Validated VGKGRecord instance.

    Raises:
        ValueError: If date parsing or type conversion fails.
    """
    return cls(
        date=parse_gdelt_datetime(raw.date),
        document_identifier=raw.document_identifier,
        image_url=raw.image_url,
        labels=cls._parse_labels(raw.labels),
        logos=cls._parse_labels(raw.logos),
        web_entities=cls._parse_labels(raw.web_entities),
        safe_search=cls._parse_safe_search(raw.safe_search),
        faces=cls._parse_faces(raw.faces),
        ocr_text=raw.ocr_text or "",
        landmark_annotations=cls._parse_labels(raw.landmark_annotations),
        domain=raw.domain or "",
        raw_json=raw.raw_json or "",
    )
```

### `VisionLabelDict`

Bases: `TypedDict`

Google Cloud Vision label annotation (lightweight).

Used for labels, logos, web_entities, and landmark_annotations fields. TypedDict avoids Pydantic validation overhead for nested structures.

Source code in `src/py_gdelt/models/vgkg.py`

```
class VisionLabelDict(TypedDict):
    """Google Cloud Vision label annotation (lightweight).

    Used for labels, logos, web_entities, and landmark_annotations fields.
    TypedDict avoids Pydantic validation overhead for nested structures.
    """

    description: str
    confidence: float
    mid: str | None  # Knowledge Graph MID - useful for entity linking
```

### `SafeSearchDict`

Bases: `TypedDict`

SafeSearch detection results.

Values are integers from Cloud Vision API:

- UNKNOWN = -1
- VERY_UNLIKELY = 0
- UNLIKELY = 1
- POSSIBLE = 2
- LIKELY = 3
- VERY_LIKELY = 4

Source code in `src/py_gdelt/models/vgkg.py`

```
class SafeSearchDict(TypedDict):
    """SafeSearch detection results.

    Values are integers from Cloud Vision API:
    - UNKNOWN = -1
    - VERY_UNLIKELY = 0
    - UNLIKELY = 1
    - POSSIBLE = 2
    - LIKELY = 3
    - VERY_LIKELY = 4
    """

    adult: int
    spoof: int
    medical: int
    violence: int
```

### `FaceAnnotationDict`

Bases: `TypedDict`

Detected face with pose angles.

Contains pose information (roll/pan/tilt angles), NOT emotion scores. Angles are in degrees relative to the camera.

Source code in `src/py_gdelt/models/vgkg.py`

```
class FaceAnnotationDict(TypedDict):
    """Detected face with pose angles.

    Contains pose information (roll/pan/tilt angles), NOT emotion scores.
    Angles are in degrees relative to the camera.
    """

    confidence: float
    roll: float  # Head roll angle in degrees
    pan: float  # Head pan angle in degrees
    tilt: float  # Head tilt angle in degrees
    detection_confidence: float
    bounding_box: str | None  # Format: "x1,y1,x2,y2"
```

## Graph Models

### `Entity`

Bases: `SchemaEvolutionMixin`, `BaseModel`

Entity extracted from GEG (Global Entity Graph).

Represents a named entity with metadata and knowledge graph links.

Attributes:

| Name                  | Type    | Description |
| --------------------- | ------- | ----------- |
| `name`                | `str`   | Entity name |
| `entity_type`         | `str`   | Entity type |
| `salience`            | \`float | None\`      |
| `wikipedia_url`       | \`str   | None\`      |
| `knowledge_graph_mid` | \`str   | None\`      |

Source code in `src/py_gdelt/models/graphs.py`

```
class Entity(SchemaEvolutionMixin, BaseModel):
    """Entity extracted from GEG (Global Entity Graph).

    Represents a named entity with metadata and knowledge graph links.

    Attributes:
        name: Entity name
        entity_type: Entity type
        salience: Salience score
        wikipedia_url: Wikipedia URL if available
        knowledge_graph_mid: Google Knowledge Graph MID if available
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    name: str
    entity_type: str = Field(alias="type")
    salience: float | None = None
    wikipedia_url: str | None = None
    knowledge_graph_mid: str | None = Field(default=None, alias="mid")
```

### `GALRecord`

Bases: `SchemaEvolutionMixin`, `BaseModel`

Article List record.

Represents a news article with basic metadata.

Attributes:

| Name          | Type       | Description           |
| ------------- | ---------- | --------------------- |
| `date`        | `datetime` | Publication date/time |
| `url`         | `str`      | Article URL           |
| `title`       | \`str      | None\`                |
| `image`       | \`str      | None\`                |
| `description` | \`str      | None\`                |
| `author`      | \`str      | None\`                |
| `lang`        | `str`      | Language code         |

Source code in `src/py_gdelt/models/graphs.py`

```
class GALRecord(SchemaEvolutionMixin, BaseModel):
    """Article List record.

    Represents a news article with basic metadata.

    Attributes:
        date: Publication date/time
        url: Article URL
        title: Article title if available
        image: Primary image URL if available
        description: Article description if available
        author: Article author if available
        lang: Language code
    """

    date: datetime
    url: str
    title: str | None = None
    image: str | None = None
    description: str | None = None
    author: str | None = None
    lang: str

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> datetime:
        """Parse date from ISO or GDELT format."""
        return parse_gdelt_datetime(v)
```

#### `parse_date(v)`

Parse date from ISO or GDELT format.

Source code in `src/py_gdelt/models/graphs.py`

```
@field_validator("date", mode="before")
@classmethod
def parse_date(cls, v: Any) -> datetime:
    """Parse date from ISO or GDELT format."""
    return parse_gdelt_datetime(v)
```

### `GEGRecord`

Bases: `SchemaEvolutionMixin`, `BaseModel`

Global Entity Graph record.

Represents a document with extracted entities and their metadata.

Attributes:

| Name       | Type           | Description                |
| ---------- | -------------- | -------------------------- |
| `date`     | `datetime`     | Publication date/time      |
| `url`      | `str`          | Source document URL        |
| `lang`     | `str`          | Language code              |
| `entities` | `list[Entity]` | List of extracted entities |

Source code in `src/py_gdelt/models/graphs.py`

```
class GEGRecord(SchemaEvolutionMixin, BaseModel):
    """Global Entity Graph record.

    Represents a document with extracted entities and their metadata.

    Attributes:
        date: Publication date/time
        url: Source document URL
        lang: Language code
        entities: List of extracted entities
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    date: datetime
    url: str
    lang: str
    entities: list[Entity] = Field(default_factory=list)

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> datetime:
        """Parse date from ISO or GDELT format."""
        return parse_gdelt_datetime(v)
```

#### `parse_date(v)`

Parse date from ISO or GDELT format.

Source code in `src/py_gdelt/models/graphs.py`

```
@field_validator("date", mode="before")
@classmethod
def parse_date(cls, v: Any) -> datetime:
    """Parse date from ISO or GDELT format."""
    return parse_gdelt_datetime(v)
```

### `GEMGRecord`

Bases: `SchemaEvolutionMixin`, `BaseModel`

Global Embedded Metadata Graph record.

Represents a document with extracted metadata tags and JSON-LD.

Attributes:

| Name       | Type            | Description                     |
| ---------- | --------------- | ------------------------------- |
| `date`     | `datetime`      | Publication date/time           |
| `url`      | `str`           | Source document URL             |
| `title`    | \`str           | None\`                          |
| `lang`     | `str`           | Language code                   |
| `metatags` | `list[MetaTag]` | List of extracted metadata tags |
| `jsonld`   | `list[str]`     | List of JSON-LD strings         |

Source code in `src/py_gdelt/models/graphs.py`

```
class GEMGRecord(SchemaEvolutionMixin, BaseModel):
    """Global Embedded Metadata Graph record.

    Represents a document with extracted metadata tags and JSON-LD.

    Attributes:
        date: Publication date/time
        url: Source document URL
        title: Document title if available
        lang: Language code
        metatags: List of extracted metadata tags
        jsonld: List of JSON-LD strings
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    date: datetime
    url: str
    title: str | None = None
    lang: str
    metatags: list[MetaTag] = Field(default_factory=list)
    jsonld: list[str] = Field(default_factory=list)

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> datetime:
        """Parse date from ISO or GDELT format."""
        return parse_gdelt_datetime(v)
```

#### `parse_date(v)`

Parse date from ISO or GDELT format.

Source code in `src/py_gdelt/models/graphs.py`

```
@field_validator("date", mode="before")
@classmethod
def parse_date(cls, v: Any) -> datetime:
    """Parse date from ISO or GDELT format."""
    return parse_gdelt_datetime(v)
```

### `GFGRecord`

Bases: `SchemaEvolutionMixin`, `BaseModel`

Global Frontpage Graph record (TSV format).

Represents a hyperlink from a frontpage to another URL.

Attributes:

| Name                 | Type       | Description              |
| -------------------- | ---------- | ------------------------ |
| `date`               | `datetime` | Publication date/time    |
| `from_frontpage_url` | `str`      | Source frontpage URL     |
| `link_url`           | `str`      | Destination link URL     |
| `link_text`          | `str`      | Anchor text of the link  |
| `page_position`      | `int`      | Position of link on page |
| `lang`               | `str`      | Language code            |

Source code in `src/py_gdelt/models/graphs.py`

```
class GFGRecord(SchemaEvolutionMixin, BaseModel):
    """Global Frontpage Graph record (TSV format).

    Represents a hyperlink from a frontpage to another URL.

    Attributes:
        date: Publication date/time
        from_frontpage_url: Source frontpage URL
        link_url: Destination link URL
        link_text: Anchor text of the link
        page_position: Position of link on page
        lang: Language code
    """

    date: datetime
    from_frontpage_url: str
    link_url: str
    link_text: str
    page_position: int
    lang: str

    @classmethod
    def from_raw(cls, raw: _RawGFGRecord) -> Self:
        """Convert internal _RawGFGRecord to public GFGRecord model.

        Args:
            raw: Internal _RawGFGRecord dataclass from TSV parsing.

        Returns:
            Validated GFGRecord with all fields parsed and typed.
        """
        date = parse_gdelt_datetime(raw.date)

        # Parse page_position (default to 0 if empty)
        page_position = 0
        if raw.page_position:
            try:
                page_position = int(raw.page_position)
            except ValueError:
                logger.warning("Invalid page_position '%s', defaulting to 0", raw.page_position)

        return cls(
            date=date,
            from_frontpage_url=raw.from_frontpage_url,
            link_url=raw.link_url,
            link_text=raw.link_text,
            page_position=page_position,
            lang=raw.lang,
        )
```

#### `from_raw(raw)`

Convert internal \_RawGFGRecord to public GFGRecord model.

Parameters:

| Name  | Type            | Description                                         | Default    |
| ----- | --------------- | --------------------------------------------------- | ---------- |
| `raw` | `_RawGFGRecord` | Internal \_RawGFGRecord dataclass from TSV parsing. | *required* |

Returns:

| Type   | Description                                           |
| ------ | ----------------------------------------------------- |
| `Self` | Validated GFGRecord with all fields parsed and typed. |

Source code in `src/py_gdelt/models/graphs.py`

```
@classmethod
def from_raw(cls, raw: _RawGFGRecord) -> Self:
    """Convert internal _RawGFGRecord to public GFGRecord model.

    Args:
        raw: Internal _RawGFGRecord dataclass from TSV parsing.

    Returns:
        Validated GFGRecord with all fields parsed and typed.
    """
    date = parse_gdelt_datetime(raw.date)

    # Parse page_position (default to 0 if empty)
    page_position = 0
    if raw.page_position:
        try:
            page_position = int(raw.page_position)
        except ValueError:
            logger.warning("Invalid page_position '%s', defaulting to 0", raw.page_position)

    return cls(
        date=date,
        from_frontpage_url=raw.from_frontpage_url,
        link_url=raw.link_url,
        link_text=raw.link_text,
        page_position=page_position,
        lang=raw.lang,
    )
```

### `GGGRecord`

Bases: `SchemaEvolutionMixin`, `BaseModel`

Global Geographic Graph record.

Represents a document with an extracted geographic location.

Attributes:

| Name            | Type       | Description              |
| --------------- | ---------- | ------------------------ |
| `date`          | `datetime` | Publication date/time    |
| `url`           | `str`      | Source document URL      |
| `location_name` | `str`      | Name of the location     |
| `lat`           | `float`    | Latitude (-90 to 90)     |
| `lon`           | `float`    | Longitude (-180 to 180)  |
| `context`       | `str`      | Surrounding text context |

Source code in `src/py_gdelt/models/graphs.py`

```
class GGGRecord(SchemaEvolutionMixin, BaseModel):
    """Global Geographic Graph record.

    Represents a document with an extracted geographic location.

    Attributes:
        date: Publication date/time
        url: Source document URL
        location_name: Name of the location
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        context: Surrounding text context
    """

    date: datetime
    url: str
    location_name: str
    lat: float
    lon: float
    context: str

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> datetime:
        """Parse date from ISO or GDELT format."""
        return parse_gdelt_datetime(v)

    @field_validator("lat")
    @classmethod
    def validate_lat(cls, v: float) -> float:
        """Validate latitude is within valid range.

        Args:
            v: Latitude value.

        Returns:
            Validated latitude.

        Raises:
            ValueError: If latitude is outside -90 to 90 range.
        """
        if not -90 <= v <= 90:
            msg = f"Latitude must be between -90 and 90, got {v}"
            raise ValueError(msg)
        return v

    @field_validator("lon")
    @classmethod
    def validate_lon(cls, v: float) -> float:
        """Validate longitude is within valid range.

        Args:
            v: Longitude value.

        Returns:
            Validated longitude.

        Raises:
            ValueError: If longitude is outside -180 to 180 range.
        """
        if not -180 <= v <= 180:
            msg = f"Longitude must be between -180 and 180, got {v}"
            raise ValueError(msg)
        return v
```

#### `parse_date(v)`

Parse date from ISO or GDELT format.

Source code in `src/py_gdelt/models/graphs.py`

```
@field_validator("date", mode="before")
@classmethod
def parse_date(cls, v: Any) -> datetime:
    """Parse date from ISO or GDELT format."""
    return parse_gdelt_datetime(v)
```

#### `validate_lat(v)`

Validate latitude is within valid range.

Parameters:

| Name | Type    | Description     | Default    |
| ---- | ------- | --------------- | ---------- |
| `v`  | `float` | Latitude value. | *required* |

Returns:

| Type    | Description         |
| ------- | ------------------- |
| `float` | Validated latitude. |

Raises:

| Type         | Description                             |
| ------------ | --------------------------------------- |
| `ValueError` | If latitude is outside -90 to 90 range. |

Source code in `src/py_gdelt/models/graphs.py`

```
@field_validator("lat")
@classmethod
def validate_lat(cls, v: float) -> float:
    """Validate latitude is within valid range.

    Args:
        v: Latitude value.

    Returns:
        Validated latitude.

    Raises:
        ValueError: If latitude is outside -90 to 90 range.
    """
    if not -90 <= v <= 90:
        msg = f"Latitude must be between -90 and 90, got {v}"
        raise ValueError(msg)
    return v
```

#### `validate_lon(v)`

Validate longitude is within valid range.

Parameters:

| Name | Type    | Description      | Default    |
| ---- | ------- | ---------------- | ---------- |
| `v`  | `float` | Longitude value. | *required* |

Returns:

| Type    | Description          |
| ------- | -------------------- |
| `float` | Validated longitude. |

Raises:

| Type         | Description                                |
| ------------ | ------------------------------------------ |
| `ValueError` | If longitude is outside -180 to 180 range. |

Source code in `src/py_gdelt/models/graphs.py`

```
@field_validator("lon")
@classmethod
def validate_lon(cls, v: float) -> float:
    """Validate longitude is within valid range.

    Args:
        v: Longitude value.

    Returns:
        Validated longitude.

    Raises:
        ValueError: If longitude is outside -180 to 180 range.
    """
    if not -180 <= v <= 180:
        msg = f"Longitude must be between -180 and 180, got {v}"
        raise ValueError(msg)
    return v
```

### `GQGRecord`

Bases: `SchemaEvolutionMixin`, `BaseModel`

Global Quotation Graph record.

Represents a document with extracted quotations and their context.

Attributes:

| Name     | Type          | Description                               |
| -------- | ------------- | ----------------------------------------- |
| `date`   | `datetime`    | Publication date/time                     |
| `url`    | `str`         | Source document URL                       |
| `lang`   | `str`         | Language code                             |
| `quotes` | `list[Quote]` | List of extracted quotations with context |

Source code in `src/py_gdelt/models/graphs.py`

```
class GQGRecord(SchemaEvolutionMixin, BaseModel):
    """Global Quotation Graph record.

    Represents a document with extracted quotations and their context.

    Attributes:
        date: Publication date/time
        url: Source document URL
        lang: Language code
        quotes: List of extracted quotations with context
    """

    date: datetime
    url: str
    lang: str
    quotes: list[Quote] = Field(default_factory=list)

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> datetime:
        """Parse date from ISO or GDELT format."""
        return parse_gdelt_datetime(v)
```

#### `parse_date(v)`

Parse date from ISO or GDELT format.

Source code in `src/py_gdelt/models/graphs.py`

```
@field_validator("date", mode="before")
@classmethod
def parse_date(cls, v: Any) -> datetime:
    """Parse date from ISO or GDELT format."""
    return parse_gdelt_datetime(v)
```

### `MetaTag`

Bases: `SchemaEvolutionMixin`, `BaseModel`

Metadata tag extracted from GEMG (Global Embedded Metadata Graph).

Represents a single metadata tag from HTML meta tags or JSON-LD.

Attributes:

| Name       | Type  | Description  |
| ---------- | ----- | ------------ |
| `key`      | `str` | Tag key/name |
| `tag_type` | `str` | Tag type     |
| `value`    | `str` | Tag value    |

Source code in `src/py_gdelt/models/graphs.py`

```
class MetaTag(SchemaEvolutionMixin, BaseModel):
    """Metadata tag extracted from GEMG (Global Embedded Metadata Graph).

    Represents a single metadata tag from HTML meta tags or JSON-LD.

    Attributes:
        key: Tag key/name
        tag_type: Tag type
        value: Tag value
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    key: str
    tag_type: str = Field(alias="type")
    value: str
```

### `Quote`

Bases: `SchemaEvolutionMixin`, `BaseModel`

Quote extracted from GQG (Global Quotation Graph).

Represents a single quotation with surrounding context.

Attributes:

| Name    | Type  | Description           |
| ------- | ----- | --------------------- |
| `pre`   | `str` | Text before the quote |
| `quote` | `str` | The quotation text    |
| `post`  | `str` | Text after the quote  |

Source code in `src/py_gdelt/models/graphs.py`

```
class Quote(SchemaEvolutionMixin, BaseModel):
    """Quote extracted from GQG (Global Quotation Graph).

    Represents a single quotation with surrounding context.

    Attributes:
        pre: Text before the quote
        quote: The quotation text
        post: Text after the quote
    """

    pre: str
    quote: str
    post: str
```

## Common Models

### `Location`

Bases: `BaseModel`

Geographic location from GDELT data.

Source code in `src/py_gdelt/models/common.py`

```
class Location(BaseModel):
    """Geographic location from GDELT data."""

    lat: float | None = None
    lon: float | None = None
    feature_id: str | None = None  # GNIS/ADM1 code
    name: str | None = None
    country_code: str | None = None  # FIPS code
    adm1_code: str | None = None
    adm2_code: str | None = None
    geo_type: int | None = None  # 1=Country, 2=State, 3=City, 4=Coordinates

    def as_tuple(self) -> tuple[float, float]:
        """Return (lat, lon) tuple. Raises ValueError if either is None."""
        if self.lat is None or self.lon is None:
            msg = "Cannot create tuple: lat or lon is None"
            raise ValueError(msg)
        return (self.lat, self.lon)

    def as_wkt(self) -> str:
        """Return WKT POINT string for geopandas compatibility.

        Returns:
            WKT POINT string in format "POINT(lon lat)".

        Raises:
            ValueError: If lat or lon is None.
        """
        if self.lat is None or self.lon is None:
            msg = "Cannot create WKT: lat or lon is None"
            raise ValueError(msg)
        return f"POINT({self.lon} {self.lat})"

    @property
    def has_coordinates(self) -> bool:
        """Check if location has valid coordinates."""
        return self.lat is not None and self.lon is not None
```

#### `has_coordinates`

Check if location has valid coordinates.

#### `as_tuple()`

Return (lat, lon) tuple. Raises ValueError if either is None.

Source code in `src/py_gdelt/models/common.py`

```
def as_tuple(self) -> tuple[float, float]:
    """Return (lat, lon) tuple. Raises ValueError if either is None."""
    if self.lat is None or self.lon is None:
        msg = "Cannot create tuple: lat or lon is None"
        raise ValueError(msg)
    return (self.lat, self.lon)
```

#### `as_wkt()`

Return WKT POINT string for geopandas compatibility.

Returns:

| Type  | Description                                  |
| ----- | -------------------------------------------- |
| `str` | WKT POINT string in format "POINT(lon lat)". |

Raises:

| Type         | Description            |
| ------------ | ---------------------- |
| `ValueError` | If lat or lon is None. |

Source code in `src/py_gdelt/models/common.py`

```
def as_wkt(self) -> str:
    """Return WKT POINT string for geopandas compatibility.

    Returns:
        WKT POINT string in format "POINT(lon lat)".

    Raises:
        ValueError: If lat or lon is None.
    """
    if self.lat is None or self.lon is None:
        msg = "Cannot create WKT: lat or lon is None"
        raise ValueError(msg)
    return f"POINT({self.lon} {self.lat})"
```

### `ToneScores`

Bases: `BaseModel`

Tone analysis scores from GDELT.

Source code in `src/py_gdelt/models/common.py`

```
class ToneScores(BaseModel):
    """Tone analysis scores from GDELT."""

    tone: float = Field(..., ge=-100, le=100)  # Overall tone (-100 to +100)
    positive_score: float
    negative_score: float
    polarity: float  # Emotional extremity
    activity_reference_density: float
    self_group_reference_density: float
    word_count: int | None = None
```

### `EntityMention`

Bases: `BaseModel`

Entity mention from GKG records.

Source code in `src/py_gdelt/models/common.py`

```
class EntityMention(BaseModel):
    """Entity mention from GKG records."""

    entity_type: str  # PERSON, ORG, LOCATION, etc.
    name: str
    offset: int | None = None  # Character offset in source
    confidence: float | None = None
```

## Result Models

### `FetchResult`

Bases: `Generic[T]`

Result container with partial failure tracking.

Source code in `src/py_gdelt/models/common.py`

```
@dataclass
class FetchResult(Generic[T]):
    """Result container with partial failure tracking."""

    data: list[T]
    failed: list[FailedRequest] = field(default_factory=list)

    @property
    def complete(self) -> bool:
        """True if no requests failed."""
        return len(self.failed) == 0

    @property
    def partial(self) -> bool:
        """True if some but not all requests failed."""
        return len(self.failed) > 0 and len(self.data) > 0

    @property
    def total_failed(self) -> int:
        """Number of failed requests."""
        return len(self.failed)

    def __iter__(self) -> Iterator[T]:
        """Allow direct iteration over data."""
        return iter(self.data)

    def __len__(self) -> int:
        """Return count of successful items."""
        return len(self.data)
```

#### `complete`

True if no requests failed.

#### `partial`

True if some but not all requests failed.

#### `total_failed`

Number of failed requests.

#### `__iter__()`

Allow direct iteration over data.

Source code in `src/py_gdelt/models/common.py`

```
def __iter__(self) -> Iterator[T]:
    """Allow direct iteration over data."""
    return iter(self.data)
```

#### `__len__()`

Return count of successful items.

Source code in `src/py_gdelt/models/common.py`

```
def __len__(self) -> int:
    """Return count of successful items."""
    return len(self.data)
```

### `FailedRequest`

Represents a failed request in a partial result.

Source code in `src/py_gdelt/models/common.py`

```
@dataclass(slots=True)
class FailedRequest:
    """Represents a failed request in a partial result."""

    url: str
    error: str
    status_code: int | None = None
    retry_after: int | None = None  # For rate limit errors
```
