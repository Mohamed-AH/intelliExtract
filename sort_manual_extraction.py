#!/usr/bin/env python3
"""
Sort the manual-style extraction by series and date,
adding sequence numbers to easily identify missing lessons.
"""

import csv
from datetime import datetime
from collections import defaultdict

def parse_date(date_str):
    """Parse date in DD/MM/YYYY format"""
    if not date_str or date_str == 'N/A':
        return None
    try:
        day, month, year = date_str.split('/')
        return datetime(int(year), int(month), int(day))
    except:
        return None

def main():
    input_file = 'extracted_lectures_manual_style.csv'
    output_file = 'lectures_manual_sorted_by_series.csv'

    print("=" * 80)
    print("SORTING MANUAL-STYLE EXTRACTION BY SERIES AND DATE")
    print("=" * 80)
    print()

    # Read the CSV
    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print(f"📖 Read {len(rows)} records from {input_file}")
    print()

    # Group by SeriesName + Location to count lessons per series
    series_counts = defaultdict(int)
    for row in rows:
        series_name = row.get('SeriesName', 'N/A')
        location = row.get('Location/Online', 'N/A')

        # Create unique series key
        if series_name != 'N/A':
            series_key = f"{series_name}|{location}"
            series_counts[series_key] += 1

    # Sort series by lesson count (descending)
    sorted_series = sorted(series_counts.items(), key=lambda x: x[1], reverse=True)

    print("📊 Series ranking by lesson count:")
    for i, (series_key, count) in enumerate(sorted_series, 1):
        series_name, location = series_key.split('|', 1)
        print(f"   {i:2d}. {series_name[:50]:50s} | {location:15s} | {count:3d} lessons")
    print()

    # Create a mapping of series_key to sort order
    series_sort_order = {}
    for i, (series_key, _) in enumerate(sorted_series):
        series_sort_order[series_key] = i

    # Add sort key to each row
    for row in rows:
        series_name = row.get('SeriesName', 'N/A')
        location = row.get('Location/Online', 'N/A')
        date_str = row.get('DateInGreg', '')

        if series_name != 'N/A':
            series_key = f"{series_name}|{location}"
            row['_series_order'] = series_sort_order.get(series_key, 9999)
        else:
            row['_series_order'] = 9999

        # Parse date for sorting
        parsed_date = parse_date(date_str)
        row['_date_parsed'] = parsed_date if parsed_date else datetime(1900, 1, 1)

    # Sort: first by series order, then by date within each series
    rows_sorted = sorted(rows, key=lambda x: (x['_series_order'], x['_date_parsed']))

    print("🔄 Sorted records by series (descending count) and date (chronological)")
    print()

    # Add sequence numbers within each series
    sequence_counter = defaultdict(int)
    for row in rows_sorted:
        series_name = row.get('SeriesName', 'N/A')
        location = row.get('Location/Online', 'N/A')

        if series_name != 'N/A':
            series_key = f"{series_name}|{location}"
            sequence_counter[series_key] += 1
            row['SequenceInSeries'] = sequence_counter[series_key]
        else:
            row['SequenceInSeries'] = 'N/A'

    print("📝 Added SequenceInSeries column (1, 2, 3...)")
    print()

    # Remove temporary sorting columns
    for row in rows_sorted:
        del row['_series_order']
        del row['_date_parsed']

    # Define output column order (add SequenceInSeries after SeriesName)
    original_columns = list(rows_sorted[0].keys())
    original_columns.remove('SequenceInSeries')

    # Insert SequenceInSeries after SeriesName
    series_name_index = original_columns.index('SeriesName')
    output_columns = original_columns[:series_name_index+1] + ['SequenceInSeries'] + original_columns[series_name_index+1:]

    # Write sorted CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=output_columns)
        writer.writeheader()
        writer.writerows(rows_sorted)

    print(f"✅ Created {output_file}")
    print()

    # Show sample of each series
    print("=" * 80)
    print("PREVIEW OF SORTED OUTPUT (First 3 lessons per series)")
    print("=" * 80)
    print()

    current_series = None
    shown_count = 0
    for row in rows_sorted:
        series_name = row.get('SeriesName', 'N/A')
        location = row.get('Location/Online', 'N/A')
        series_key = f"{series_name}|{location}"

        if series_key != current_series:
            current_series = series_key
            shown_count = 0
            print()
            print(f"📚 {series_name}")
            print(f"   Location: {location}")
            print(f"   Total: {series_counts.get(series_key, 0)} lessons")
            print()

        if shown_count < 3 and series_name != 'N/A':
            seq = row.get('SequenceInSeries', 'N/A')
            date = row.get('DateInGreg', 'N/A')
            serial = row.get('Serial', 'N/A')
            subtopic = row.get('SubTopic', 'N/A')[:50]
            print(f"   [{seq:3}] {date:12s} | Serial: {serial:5s} | {subtopic}")
            shown_count += 1

    print()
    print("=" * 80)
    print("✨ SORTING COMPLETE!")
    print("=" * 80)
    print()
    print(f"📄 Output file: {output_file}")
    print("📊 This file makes it easy to identify missing lessons by:")
    print("   • Checking sequence numbers for gaps (e.g., 1, 2, 4, 5 - missing 3)")
    print("   • Looking at date patterns to spot extended gaps")
    print("   • Seeing all lessons from the same series grouped together")
    print()

if __name__ == '__main__':
    main()
