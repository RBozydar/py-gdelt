"""Example: Using BigQuerySource to query GDELT events.

This example demonstrates how to use the BigQuerySource class to query
GDELT events from BigQuery with proper credential configuration.

Prerequisites:
1. Google Cloud account with BigQuery enabled
2. Credentials configured (either ADC or service account JSON file)
3. Optional: Set environment variables:
   - GDELT_BIGQUERY_PROJECT="your-project-id"
   - GDELT_BIGQUERY_CREDENTIALS="/path/to/credentials.json"
"""

import asyncio
from datetime import date

from py_gdelt.filters import DateRange, EventFilter
from py_gdelt.sources import BigQuerySource


async def query_events_example() -> None:
    """Query GDELT events for US-China interactions."""
    # Create filter for events between USA and China in January 2024
    filter_obj = EventFilter(
        date_range=DateRange(
            start=date(2024, 1, 1),
            end=date(2024, 1, 7),
        ),
        actor1_country="USA",
        actor2_country="CHN",
        min_tone=-10.0,  # Only negative tone events
        max_tone=0.0,
    )

    # Query events using BigQuery
    async with BigQuerySource() as source:
        print("Querying GDELT events from BigQuery...")
        print(f"Date range: {filter_obj.date_range.start} to {filter_obj.date_range.end}")
        print(f"Filter: Actor1={filter_obj.actor1_country}, Actor2={filter_obj.actor2_country}")
        print(f"Tone range: {filter_obj.min_tone} to {filter_obj.max_tone}")
        print()

        # Stream results (limited to 10 for demo)
        count = 0
        async for event in source.query_events(filter_obj, limit=10):
            count += 1
            print(f"Event #{count}:")
            print(f"  ID: {event['GLOBALEVENTID']}")
            print(f"  Date: {event['SQLDATE']}")
            print(f"  Event Code: {event['EventCode']}")
            print(f"  Actor1: {event['Actor1Name']} ({event['Actor1CountryCode']})")
            print(f"  Actor2: {event['Actor2Name']} ({event['Actor2CountryCode']})")
            print(f"  Tone: {event['AvgTone']}")
            print(f"  Goldstein Scale: {event['GoldsteinScale']}")
            print()

        print(f"Total events retrieved: {count}")


async def query_gkg_example() -> None:
    """Query GDELT GKG for climate change themes."""
    from py_gdelt.filters import GKGFilter

    # Create filter for climate change themes
    filter_obj = GKGFilter(
        date_range=DateRange(start=date(2024, 1, 1)),
        themes=["ENV_CLIMATECHANGE"],
        country="USA",
    )

    async with BigQuerySource() as source:
        print("Querying GDELT GKG for climate change mentions...")
        print()

        # Stream results (limited to 5 for demo)
        count = 0
        async for record in source.query_gkg(filter_obj, limit=5):
            count += 1
            print(f"GKG Record #{count}:")
            print(f"  ID: {record['GKGRECORDID']}")
            print(f"  Date: {record['DATE']}")
            print(f"  Source: {record['SourceCommonName']}")
            print(f"  Themes: {record['V2Themes'][:100]}...")  # Truncate long themes
            print()

        print(f"Total GKG records retrieved: {count}")


async def query_mentions_example() -> None:
    """Query event mentions for a specific event."""
    # First, get an event ID
    filter_obj = EventFilter(
        date_range=DateRange(start=date(2024, 1, 1)),
        actor1_country="USA",
    )

    async with BigQuerySource() as source:
        # Get first event
        event_id = None
        async for event in source.query_events(filter_obj, limit=1):
            event_id = event["GLOBALEVENTID"]
            print(f"Found event: {event_id}")
            print(f"  Event Code: {event['EventCode']}")
            print(f"  Actors: {event['Actor1Name']} -> {event['Actor2Name']}")
            print()
            break

        if event_id:
            # Query mentions for this event
            print(f"Querying mentions for event {event_id}...")
            print()

            count = 0
            async for mention in source.query_mentions(
                global_event_id=event_id,
                date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 1, 7)),
            ):
                count += 1
                print(f"Mention #{count}:")
                print(f"  Source: {mention['MentionSourceName']}")
                print(f"  Mention Time: {mention['MentionTimeDate']}")
                print(f"  Confidence: {mention['Confidence']}")
                print()

            print(f"Total mentions retrieved: {count}")


async def main() -> None:
    """Run all examples."""
    print("=" * 80)
    print("GDELT BigQuery Examples")
    print("=" * 80)
    print()

    try:
        # Example 1: Query events
        await query_events_example()
        print("\n" + "=" * 80 + "\n")

        # Example 2: Query GKG
        await query_gkg_example()
        print("\n" + "=" * 80 + "\n")

        # Example 3: Query mentions
        await query_mentions_example()

    except Exception as e:
        print(f"Error: {e}")
        print()
        print("Note: This example requires BigQuery credentials to be configured.")
        print("Set environment variables:")
        print("  export GDELT_BIGQUERY_PROJECT='your-project-id'")
        print("  export GDELT_BIGQUERY_CREDENTIALS='/path/to/credentials.json'")
        print()
        print("Or use Application Default Credentials:")
        print("  gcloud auth application-default login")
        print("  export GDELT_BIGQUERY_PROJECT='your-project-id'")


if __name__ == "__main__":
    asyncio.run(main())
