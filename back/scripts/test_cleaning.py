#!/usr/bin/env python3
"""
Test script to verify the cleaning function works correctly.
"""

import re


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


# Test samples
test_samples = [
    "2025-07-18 10:25:52\n Daniil Daniil -> 2071074234:\nКомпания: Яндекс Финтех 1 этап\nЗадача 1:\nУсловий не сохранилось, но задачка была на то, что будет в консоле при обработке Promise",
    "2025-07-17 20:49:57\n Даниил -> 2071074234:\nЯндекс 1 этап технички\nЗП: говорил 250-300+\n\nЗадача 1\n\nНеобходимо написать функцию",
    "2025-07-14 13:42:11\n Ivan Kulyaev -> 2071074234:\n1. Яндекс 1 этап\n2. Написала HR\n3. ЗП просил от 250к\n\nВопросы:",
    "Some content without metadata should remain unchanged",
]

print("Testing cleaning function:")
print("=" * 50)

for i, sample in enumerate(test_samples, 1):
    print(f"\nTest {i}:")
    print("Original:")
    print(repr(sample))

    cleaned = clean_content(sample)
    print("Cleaned:")
    print(repr(cleaned))

    print("Readable cleaned:")
    print(cleaned[:100] + "..." if len(cleaned) > 100 else cleaned)
    print("-" * 30)
