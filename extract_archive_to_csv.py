#!/usr/bin/env python3
"""
Convert parsed archive messages to CSV format matching the standard extraction format.
"""

import json
import csv
from collections import defaultdict

def main():
    input_file = 'archive_messages_parsed.json'
    output_csv = 'archive_lectures_extracted.csv'

    print("=" * 80)
    print("CONVERTING ARCHIVE TO CSV FORMAT")
    print("=" * 80)
    print()

    # Load parsed messages
    with open(input_file, 'r', encoding='utf-8') as f:
        messages = json.load(f)

    print(f"📖 Loaded {len(messages)} messages")
    print()

    # Convert to CSV format
    csv_records = []
    for msg in messages:
        record = {
            'TelegramFileName': msg['filename'],
            'Type': 'Series',  # All archive messages are series lessons
            'SeriesName': msg['series_name'],
            'Serial': msg['lesson_number'],
            'OriginalAuthor': msg['author'],
            'Location/Online': 'جامع الورود',  # Archive lessons are from the masjid
            'Sheikh': 'حسن بن محمد منصور الدغريري',
            'DateInArabic': msg['hijri_date'],
            'DateInGreg': msg['greg_date'],
            'ClipLength': msg['clip_length'],
            'Category': msg['category']
        }
        csv_records.append(record)

    # Sort by series name, then by serial number
    def get_sort_key(record):
        series = record['SeriesName']
        serial = record['Serial']

        # Convert Arabic numerals to English for sorting
        arabic_to_eng = {
            '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
            '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
        }

        serial_eng = serial
        for ar, en in arabic_to_eng.items():
            serial_eng = serial_eng.replace(ar, en)

        try:
            serial_num = int(serial_eng)
        except:
            serial_num = 0

        return (series, serial_num)

    csv_records.sort(key=get_sort_key)

    # Write CSV
    fieldnames = [
        'TelegramFileName', 'Type', 'SeriesName', 'Serial',
        'OriginalAuthor', 'Location/Online', 'Sheikh',
        'DateInArabic', 'DateInGreg', 'ClipLength', 'Category'
    ]

    with open(output_csv, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_records)

    print(f"✅ Created {output_csv}")
    print()

    # Show statistics
    print("=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print()

    # Count by series
    series_counts = defaultdict(int)
    for record in csv_records:
        series_counts[record['SeriesName']] += 1

    print(f"📊 Series Breakdown ({len(series_counts)} unique series):")
    for series, count in sorted(series_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {series[:55]:55s} | {count:3d} lessons")

    print()

    # Count by category
    category_counts = defaultdict(int)
    for record in csv_records:
        category_counts[record['Category']] += 1

    print(f"📚 By Category:")
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {category:15s} | {count:3d} lessons")

    print()
    print("=" * 80)
    print("✨ CSV GENERATION COMPLETE!")
    print("=" * 80)
    print()
    print(f"📄 Output file: {output_csv}")
    print(f"📊 Total lessons: {len(csv_records)}")
    print(f"📚 Series count: {len(series_counts)}")
    print()

if __name__ == '__main__':
    main()
