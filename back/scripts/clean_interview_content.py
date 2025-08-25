#!/usr/bin/env python3
"""
Script to clean interview content from metadata information.
Removes date/time stamps, author names, and ID numbers from content and full_content fields.

Usage:
    python scripts/clean_interview_content.py [--dry-run]

Options:
    --dry-run    Show what would be cleaned without making changes
"""

import argparse
import os
import re
import sys
from datetime import datetime
from typing import Tuple

# Add the parent directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


# Import database components
from app.shared.database import SessionLocal
from app.shared.models.interview_models import InterviewRecord


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
    # Examples:
    # "2025-07-18 10:25:52\n Daniil Daniil -> 2071074234:"
    # "2025-07-17 20:49:57\n Даниил -> 2071074234:"
    # "2025-07-14 13:42:11\n Ivan Kulyaev -> 2071074234:"

    metadata_pattern = (
        r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s*\n?\s*([^-]+)\s*->\s*(\d+):\s*\n?"
    )

    # Remove the metadata line from the beginning
    cleaned_text = re.sub(metadata_pattern, "", text, flags=re.MULTILINE)

    # Remove any leading whitespace and newlines
    cleaned_text = cleaned_text.lstrip()

    return cleaned_text


def preview_cleaning(
    original: str, cleaned: str, max_preview_length: int = 200
) -> None:
    """Show a preview of what will be cleaned."""
    try:
        print(f"Original (first {max_preview_length} chars):")
        print(repr(original[:max_preview_length]))
        print(f"\nCleaned (first {max_preview_length} chars):")
        print(repr(cleaned[:max_preview_length]))
        print("-" * 50)
    except UnicodeEncodeError:
        # Fallback for problematic characters
        print("Original (contains non-printable characters)")
        print("Cleaned (contains non-printable characters)")
        print("-" * 50)


def clean_interview_records(dry_run: bool = False) -> Tuple[int, int]:
    """
    Clean all interview records in the database.

    Args:
        dry_run: If True, show what would be cleaned without making changes

    Returns:
        Tuple of (total_records, cleaned_records)
    """
    session = SessionLocal()

    try:
        # Get all interview records
        records = session.query(InterviewRecord).all()
        total_records = len(records)
        cleaned_records = 0

        print(f"Found {total_records} interview records to process")

        for record in records:
            original_content = record.content
            original_full_content = record.full_content

            # Clean both content fields
            cleaned_content = clean_content(original_content)
            cleaned_full_content = clean_content(original_full_content)

            # Check if cleaning made any changes
            content_changed = cleaned_content != original_content
            full_content_changed = cleaned_full_content != original_full_content

            if content_changed or full_content_changed:
                cleaned_records += 1

                if dry_run:
                    print(f"\nRecord ID: {record.id} ({record.company_name})")
                    if content_changed:
                        print("Content would be cleaned:")
                        preview_cleaning(original_content, cleaned_content, 150)
                    if full_content_changed:
                        print("Full content would be cleaned:")
                        preview_cleaning(
                            original_full_content, cleaned_full_content, 150
                        )
                else:
                    # Update the record
                    record.content = cleaned_content
                    record.full_content = cleaned_full_content
                    record.updatedAt = datetime.utcnow()

                    print(f"Cleaned record {record.id} ({record.company_name})")

        if not dry_run:
            # Commit changes
            session.commit()
            print(
                f"\nSuccessfully cleaned {cleaned_records} out of {total_records} records"
            )
        else:
            print(
                f"\nDry run complete: {cleaned_records} out of {total_records} records would be cleaned"
            )

        return total_records, cleaned_records

    except Exception as e:
        session.rollback()
        print(f"Error during cleaning: {e}")
        raise
    finally:
        session.close()


def main():
    """Main function to run the cleaning script."""
    parser = argparse.ArgumentParser(
        description="Clean interview content from metadata"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be cleaned without making changes",
    )

    args = parser.parse_args()

    print("Interview Content Cleaning Script")
    print("=" * 40)

    if args.dry_run:
        print("Running in DRY RUN mode - no changes will be made")
    else:
        print("Running in LIVE mode - changes will be committed to database")
        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() not in ["yes", "y"]:
            print("Aborted by user")
            sys.exit(0)

    try:
        total, cleaned = clean_interview_records(dry_run=args.dry_run)

        print("\nSummary:")
        print(f"Total records: {total}")
        print(f"Records {'that would be ' if args.dry_run else ''}cleaned: {cleaned}")
        print(f"Records unchanged: {total - cleaned}")

        if args.dry_run:
            print("\nTo apply these changes, run without --dry-run flag")

    except Exception as e:
        print(f"Script failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
