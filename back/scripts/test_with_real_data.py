#!/usr/bin/env python3
"""
Test the cleaning function with actual database records.
"""

import os
import re
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.shared.database import SessionLocal
from app.shared.entities.interview import InterviewRecord


def clean_content(text: str) -> str:
    """Clean interview content by removing metadata patterns."""
    if not text:
        return text
    
    metadata_pattern = r'^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s*\n?\s*([^-]+)\s*->\s*(\d+):\s*\n?'
    cleaned_text = re.sub(metadata_pattern, '', text, flags=re.MULTILINE)
    cleaned_text = cleaned_text.lstrip()
    return cleaned_text


def main():
    """Test cleaning with real database records."""
    session = SessionLocal()
    
    try:
        # Get first 3 records
        records = session.query(InterviewRecord).limit(3).all()
        
        print("Testing cleaning function with real database records:")
        print("=" * 60)
        
        for i, record in enumerate(records, 1):
            print(f"\nRecord {i}: {record.company_name}")
            print("-" * 40)
            
            original = record.content[:200] + "..." if len(record.content) > 200 else record.content
            cleaned = clean_content(record.content)
            cleaned_preview = cleaned[:200] + "..." if len(cleaned) > 200 else cleaned
            
            print("Original content (first 200 chars):")
            try:
                print(original)
            except UnicodeEncodeError:
                print("[Content contains special characters]")
            
            print("\nCleaned content (first 200 chars):")
            try:
                print(cleaned_preview)
            except UnicodeEncodeError:
                print("[Content contains special characters]")
            
            print(f"\nLength change: {len(record.content)} -> {len(cleaned)} chars")
            print(f"Content changed: {record.content != cleaned}")
        
    finally:
        session.close()


if __name__ == "__main__":
    main()