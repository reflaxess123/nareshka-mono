#!/usr/bin/env python3
"""
Quick check to see how many records need cleaning without detailed output.
"""

import os
import re
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.shared.database import SessionLocal
from app.shared.entities.interview import InterviewRecord


def clean_content(text: str) -> str:
    """Clean interview content by removing metadata patterns."""
    if not text:
        return text

    metadata_pattern = (
        r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s*\n?\s*([^-]+)\s*->\s*(\d+):\s*\n?"
    )
    cleaned_text = re.sub(metadata_pattern, "", text, flags=re.MULTILINE)
    cleaned_text = cleaned_text.lstrip()
    return cleaned_text


def main():
    """Quick check of how many records need cleaning."""
    session = SessionLocal()

    try:
        records = session.query(InterviewRecord).all()
        total_records = len(records)
        needs_cleaning = 0

        print(f"Checking {total_records} records...")

        for i, record in enumerate(records):
            if i % 100 == 0:
                print(f"Processed {i}/{total_records} records...")

            # Check if cleaning would make changes
            content_changed = clean_content(record.content) != record.content
            full_content_changed = (
                clean_content(record.full_content) != record.full_content
            )

            if content_changed or full_content_changed:
                needs_cleaning += 1

        print("\nResults:")
        print(f"Total records: {total_records}")
        print(f"Records needing cleaning: {needs_cleaning}")
        print(f"Records already clean: {total_records - needs_cleaning}")
        print(f"Percentage needing cleaning: {(needs_cleaning/total_records)*100:.1f}%")

    finally:
        session.close()


if __name__ == "__main__":
    main()
