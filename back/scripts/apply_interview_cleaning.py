#!/usr/bin/env python3
"""
Script to clean interview content from metadata information.
Removes date/time stamps, author names, and ID numbers from content and full_content fields.

Usage:
    python scripts/apply_interview_cleaning.py
"""

import os
import re
import sys
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.shared.database import SessionLocal
from app.shared.entities.interview import InterviewRecord


def clean_content(text: str) -> str:
    """
    Clean interview content by removing metadata patterns.

    Patterns to remove:
    - Date/time stamps: "YYYY-MM-DD HH:MM:SS"
    - Author information: "Author Name -> ID:"
    - Leading whitespace and newlines

    Args:
        text: Original text content

    Returns:
        Cleaned text content
    """
    if not text:
        return text

    # Pattern to match the metadata line:
    # Date/time + optional whitespace + author name + " -> " + ID + ":"
    metadata_pattern = (
        r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s*\n?\s*([^-]+)\s*->\s*(\d+):\s*\n?"
    )

    # Remove the metadata line from the beginning
    cleaned_text = re.sub(metadata_pattern, "", text, flags=re.MULTILINE)

    # Remove any leading whitespace and newlines
    cleaned_text = cleaned_text.lstrip()

    return cleaned_text


def main():
    """Apply cleaning to all interview records."""
    print("Starting interview content cleaning...")
    print("This will remove metadata from content and full_content fields.")

    response = input("Are you sure you want to proceed? (yes/no): ")
    if response.lower() not in ["yes", "y"]:
        print("Aborted by user")
        return

    session = SessionLocal()

    try:
        # Get all interview records
        records = session.query(InterviewRecord).all()
        total_records = len(records)
        cleaned_records = 0

        print(f"Processing {total_records} interview records...")

        for i, record in enumerate(records):
            if i % 100 == 0:
                print(
                    f"Processed {i}/{total_records} records... (cleaned: {cleaned_records})"
                )

            original_content = record.content
            original_full_content = record.full_content

            # Clean both content fields
            cleaned_content = clean_content(original_content)
            cleaned_full_content = clean_content(original_full_content)

            # Check if cleaning made any changes
            content_changed = cleaned_content != original_content
            full_content_changed = cleaned_full_content != original_full_content

            if content_changed or full_content_changed:
                # Update the record
                record.content = cleaned_content
                record.full_content = cleaned_full_content
                record.updatedAt = datetime.utcnow()
                cleaned_records += 1

        # Commit changes
        print("Committing changes to database...")
        session.commit()

        print("\nCleaning completed successfully!")
        print(f"Total records: {total_records}")
        print(f"Records cleaned: {cleaned_records}")
        print(f"Records unchanged: {total_records - cleaned_records}")

    except Exception as e:
        session.rollback()
        print(f"Error during cleaning: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
