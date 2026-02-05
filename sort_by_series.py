#!/usr/bin/env python3
"""
Sort extracted lectures by series (SeriesName + Location) then by date
This makes it easy to see missing lessons in each series
"""

import csv
from datetime import datetime
from collections import defaultdict

def parse_date(date_str):
    """Parse date string to datetime"""
    if not date_str or date_str == "Not Available":
        return None

    formats = ['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_str.split()[0], fmt)
        except:
            continue
    return None


def main():
    print("\n" + "="*80)
    print("📚 SORTING LECTURES BY SERIES AND DATE")
    print("="*80 + "\n")

    # Read the final extraction CSV
    with open('extracted_lectures_final.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        records = list(reader)

    print(f"Loaded {len(records)} records\n")

    # Parse dates and add to records
    for record in records:
        date = parse_date(record['DateInGreg'])
        record['ParsedDate'] = date

    # Group by Series + Location
    series_groups = defaultdict(list)

    for record in records:
        series_name = record.get('SeriesName', 'Unknown')
        if not series_name or series_name == 'Not Available':
            series_name = 'Unknown'

        location = record.get('Location/Online', 'جامع الورود')

        # Create unique key: SeriesName | Location
        series_key = f"{series_name}|{location}"

        series_groups[series_key].append(record)

    print(f"Found {len(series_groups)} unique series (by name + location)\n")

    # Sort within each group by date
    for series_key in series_groups:
        series_groups[series_key].sort(key=lambda x: x['ParsedDate'] if x['ParsedDate'] else datetime.min)

    # Sort series groups by number of lessons (descending)
    sorted_series = sorted(series_groups.items(), key=lambda x: len(x[1]), reverse=True)

    # Create output with sequence numbers
    output_records = []

    for series_key, lessons in sorted_series:
        parts = series_key.split('|')
        series_name = parts[0]
        location = parts[1] if len(parts) > 1 else 'جامع الورود'

        # Add sequence number within series
        for seq_num, lesson in enumerate(lessons, 1):
            output_record = {
                'SequenceInSeries': seq_num,
                'SeriesName': series_name,
                'Location': location,
                'DayOfWeek': lesson.get('DayOfWeek', 'Unknown'),
                'RecordingDate': lesson['ParsedDate'].strftime('%Y-%m-%d') if lesson['ParsedDate'] else 'N/A',
                'TelegramFileName': lesson.get('TelegramFileName', ''),
                'Type': lesson.get('Type', ''),
                'Topic': lesson.get('Topic', ''),
                'SubTopic': lesson.get('SubTopic', ''),
                'Serial': lesson.get('Serial', ''),
                'OriginalAuthor': lesson.get('OriginalAuthor', ''),
                'Sheikh': lesson.get('Sheikh', ''),
                'DateInArabic': lesson.get('DateInArabic', ''),
                'DateInGreg': lesson.get('DateInGreg', ''),
                'ClipLength': lesson.get('ClipLength', ''),
                'Category': lesson.get('Category', ''),
                'MatchedBy': lesson.get('MatchedBy', ''),
                'doubtsStatus': lesson.get('doubtsStatus', '')
            }
            output_records.append(output_record)

    # Save to CSV
    output_file = 'lectures_sorted_by_series.csv'

    fieldnames = [
        'SequenceInSeries', 'SeriesName', 'Location', 'DayOfWeek', 'RecordingDate',
        'TelegramFileName', 'Type', 'Topic', 'SubTopic', 'Serial',
        'OriginalAuthor', 'Sheikh', 'DateInArabic', 'DateInGreg',
        'ClipLength', 'Category', 'MatchedBy', 'doubtsStatus'
    ]

    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_records)

    print(f"✅ Saved to: {output_file}")

    # Print series summary
    print("\n" + "="*80)
    print("📊 SERIES SUMMARY (Sorted by Lesson Count)")
    print("="*80 + "\n")

    for series_key, lessons in sorted_series:
        parts = series_key.split('|')
        series_name = parts[0]
        location = parts[1] if len(parts) > 1 else 'جامع الورود'

        # Get date range
        lessons_with_dates = [l for l in lessons if l['ParsedDate']]
        if lessons_with_dates:
            first_date = min(l['ParsedDate'] for l in lessons_with_dates)
            last_date = max(l['ParsedDate'] for l in lessons_with_dates)
            date_range = f"{first_date.strftime('%Y-%m-%d')} to {last_date.strftime('%Y-%m-%d')}"
            weeks = (last_date - first_date).days // 7 + 1
        else:
            date_range = "No dates"
            weeks = 0

        print(f"📖 {series_name[:60]}")
        print(f"   Location: {location}")
        print(f"   Lessons: {len(lessons)}")
        if lessons_with_dates:
            print(f"   Date Range: {date_range} ({weeks} weeks)")

            # Check for gaps
            if len(lessons_with_dates) > 1:
                gaps = []
                for i in range(len(lessons_with_dates) - 1):
                    current = lessons_with_dates[i]['ParsedDate']
                    next_lesson = lessons_with_dates[i+1]['ParsedDate']
                    days_gap = (next_lesson - current).days

                    if days_gap > 14:  # More than 2 weeks
                        weeks_gap = days_gap // 7
                        gaps.append(f"{weeks_gap} weeks between {current.strftime('%Y-%m-%d')} and {next_lesson.strftime('%Y-%m-%d')}")

                if gaps:
                    print(f"   ⚠️  Gaps: {len(gaps)} gap(s) found")
                    for gap in gaps[:3]:  # Show first 3 gaps
                        print(f"      • {gap}")
        print()

    print("="*80)
    print(f"\n💡 TIP: Open {output_file} to see lessons sorted by series and date.")
    print("   The SequenceInSeries column helps identify missing lessons.\n")


if __name__ == "__main__":
    main()
