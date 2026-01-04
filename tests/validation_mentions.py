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
        "123456789\t"
        "20240104120000\t"
        "20240104121500\t"
        "1\t"
        "CNN\t"
        "https://cnn.com/article/123\t"
        "5\t"
        "45\t"
        "78\t"
        "100\t"
        "1\t"
        "95\t"
        "5000\t"
        "-2.5\t"
        "eng;spa\t"
        "\n"
        # Another mention
        "987654321\t"
        "20240104130000\t"
        "20240104130500\t"
        "2\t"
        "BBC\t"
        "https://bbc.com/news/456\t"
        "1\t"
        "0\t"
        "0\t"
        "0\t"
        "0\t"
        "80\t"
        "3000\t"
        "1.2\t"
        "\t"
        "\n"
        # Malformed line (wrong column count) - should be skipped
        "bad\tline\n"
    ).encode("utf-8")

    mentions = list(parser.parse(sample_data))

    print(f"Parsed {len(mentions)} mentions")
    print()

    for i, mention in enumerate(mentions, start=1):
        print(f"Mention {i}:")
        print(f"  GlobalEventID: {mention.global_event_id}")
        print(f"  Event Time: {mention.event_time_full} (date: {mention.event_time_date})")
        print(
            f"  Mention Time: {mention.mention_time_full} (date: {mention.mention_time_date})"
        )
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
