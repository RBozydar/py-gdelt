#!/usr/bin/env python
"""Quick validation script for MentionsParser.

This script provides a simple way to test the MentionsParser with sample data
without running the full test suite.
"""

from py_gdelt.parsers.mentions import MentionsParser


def main() -> None:
    """Run basic validation tests."""
    parser = MentionsParser()

    # Sample mentions data (16 columns, TAB-delimited)
    sample_data = (
        # Valid mention with all fields
        b"123456789\t"
        b"20240104120000\t"
        b"20240104121500\t"
        b"1\t"
        b"CNN\t"
        b"https://cnn.com/article/123\t"
        b"5\t"
        b"45\t"
        b"78\t"
        b"100\t"
        b"1\t"
        b"95\t"
        b"5000\t"
        b"-2.5\t"
        b"eng;spa\t"
        b"\n"
        # Another mention
        b"987654321\t"
        b"20240104130000\t"
        b"20240104130500\t"
        b"2\t"
        b"BBC\t"
        b"https://bbc.com/news/456\t"
        b"1\t"
        b"0\t"
        b"0\t"
        b"0\t"
        b"0\t"
        b"80\t"
        b"3000\t"
        b"1.2\t"
        b"\t"
        b"\n"
        # Malformed line (wrong column count) - should be skipped
        b"bad\tline\n"
    )

    mentions = list(parser.parse(sample_data))

    print(f"Parsed {len(mentions)} mentions")
    print()

    for i, mention in enumerate(mentions, start=1):
        print(f"Mention {i}:")
        print(f"  GlobalEventID: {mention.global_event_id}")
        print(f"  Event Time: {mention.event_time_full} (date: {mention.event_time_date})")
        print(f"  Mention Time: {mention.mention_time_full} (date: {mention.mention_time_date})")
        print(f"  Type: {mention.mention_type}")
        print(f"  Source: {mention.mention_source_name}")
        print(f"  URL: {mention.mention_identifier}")
        print(f"  Confidence: {mention.confidence}")
        print(f"  Tone: {mention.mention_doc_tone}")
        print(f"  Translation Info: {mention.mention_doc_translation_info}")
        print()

    print("Validation complete!")


if __name__ == "__main__":
    main()
