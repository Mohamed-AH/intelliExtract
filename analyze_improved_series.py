#!/usr/bin/env python3
"""
Analyze the improved extraction and organize into series
Shows what lessons we have and what's missing
"""

import csv
from datetime import datetime, timedelta
from collections import defaultdict

def parse_date(date_str):
    """Parse various date formats"""
    if not date_str or date_str == "Not Available":
        return None

    # Try different formats
    formats = [
        '%d.%m.%Y',  # 03.10.2025
        '%d/%m/%Y',  # 03/10/2025
        '%Y-%m-%d',  # 2025-10-03
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.split()[0], fmt)
        except:
            continue

    return None


def main():
    print("\n" + "="*80)
    print("📚 SERIES ORGANIZATION REPORT - IMPROVED EXTRACTION")
    print("="*80 + "\n")

    # Load improved data
    with open('extracted_lectures_improved.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        records = list(reader)

    print(f"Loaded {len(records)} records\n")

    # Group by series (SeriesName + Location + DayOfWeek)
    series_groups = defaultdict(list)

    for record in records:
        series_name = record['SeriesName']
        if series_name == "Not Available":
            series_name = "Unknown"

        location = record['Location/Online']
        day_of_week = record.get('DayOfWeek', 'Unknown')

        # Parse date
        date = parse_date(record['DateInGreg'])
        if date:
            record['ParsedDate'] = date
        else:
            record['ParsedDate'] = None

        # Create unique series key
        series_key = f"{series_name}|{location}|{day_of_week}"

        series_groups[series_key].append(record)

    # Sort each series by date
    for key in series_groups:
        series_groups[key].sort(key=lambda x: x['ParsedDate'] if x['ParsedDate'] else datetime.min)

    print(f"📊 Found {len(series_groups)} unique series\n")
    print("="*80)

    # Analyze each series
    series_stats = []

    for series_key in sorted(series_groups.keys()):
        parts = series_key.split('|')
        series_name = parts[0]
        location = parts[1]
        day_of_week = parts[2]

        lessons = series_groups[series_key]

        # Filter lessons with dates
        lessons_with_dates = [l for l in lessons if l['ParsedDate']]

        if len(lessons) < 2:  # Skip single-lesson items
            continue

        # Stats
        total_lessons = len(lessons)
        category = lessons[0].get('Category', 'Unknown')
        author = lessons[0].get('OriginalAuthor', 'Unknown')

        stats = {
            'name': series_name,
            'location': location,
            'day': day_of_week,
            'category': category,
            'author': author,
            'count': total_lessons,
            'lessons': lessons
        }

        if lessons_with_dates:
            stats['first_date'] = min(l['ParsedDate'] for l in lessons_with_dates)
            stats['last_date'] = max(l['ParsedDate'] for l in lessons_with_dates)
            stats['weeks_span'] = (stats['last_date'] - stats['first_date']).days // 7 + 1
            stats['expected'] = stats['weeks_span']
            stats['missing'] = stats['expected'] - len(lessons_with_dates)
            stats['completeness'] = (len(lessons_with_dates) / stats['expected']) * 100 if stats['expected'] > 0 else 0
        else:
            stats['first_date'] = None
            stats['last_date'] = None
            stats['weeks_span'] = 0
            stats['expected'] = total_lessons
            stats['missing'] = 0
            stats['completeness'] = 100

        series_stats.append(stats)

    # Sort by number of lessons (descending)
    series_stats.sort(key=lambda x: x['count'], reverse=True)

    # Print detailed series breakdown
    for i, stats in enumerate(series_stats, 1):
        print(f"\n{i}. 📖 {stats['name']}")
        print(f"   {'─' * 70}")
        print(f"   📍 Location: {stats['location']}")
        print(f"   📅 Day: {stats['day']}")
        print(f"   📚 Category: {stats['category']}")
        print(f"   ✍️  Author: {stats['author']}")
        print(f"   📊 Lessons Found: {stats['count']}")

        if stats['first_date'] and stats['last_date']:
            print(f"   📆 Date Range: {stats['first_date'].strftime('%Y-%m-%d')} to {stats['last_date'].strftime('%Y-%m-%d')}")
            print(f"   🗓️  Weeks Span: {stats['weeks_span']} weeks")
            print(f"   ✅ Expected: {stats['expected']} | Missing: {stats['missing']} | Completeness: {stats['completeness']:.1f}%")

            # Show lesson dates
            lessons_with_dates = [l for l in stats['lessons'] if l['ParsedDate']]
            if lessons_with_dates:
                print(f"\n   📋 Lesson Dates:")
                for j, lesson in enumerate(lessons_with_dates, 1):
                    serial = lesson.get('Serial', 'N/A')
                    date_str = lesson['ParsedDate'].strftime('%Y-%m-%d')
                    filename = lesson['TelegramFileName'][:40]
                    subtopic = lesson.get('SubTopic', 'N/A')
                    print(f"      {j:2d}. {date_str} | Serial: {serial[:20]:20s} | {subtopic[:30]:30s}")

            # Check for gaps
            if len(lessons_with_dates) > 1:
                gaps = []
                for j in range(len(lessons_with_dates) - 1):
                    current = lessons_with_dates[j]['ParsedDate']
                    next_lesson = lessons_with_dates[j+1]['ParsedDate']
                    days_gap = (next_lesson - current).days

                    if days_gap > 14:  # More than 2 weeks
                        weeks_gap = days_gap // 7
                        gaps.append((current, next_lesson, weeks_gap))

                if gaps:
                    print(f"\n   ⚠️  Gaps Detected:")
                    for gap_start, gap_end, weeks in gaps:
                        print(f"      • {weeks} weeks between {gap_start.strftime('%Y-%m-%d')} and {gap_end.strftime('%Y-%m-%d')}")

    # Save organized CSV
    print("\n\n" + "="*80)
    print("💾 SAVING ORGANIZED CSV")
    print("="*80 + "\n")

    output_file = 'lectures_by_series_organized.csv'

    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = [
            'SeriesName', 'Location', 'DayOfWeek', 'Category', 'OriginalAuthor',
            'LessonSeq', 'RecordingDate', 'Serial', 'SubTopic',
            'TelegramFileName', 'Type', 'Topic',
            'DateInArabic', 'ClipLength', 'doubtsStatus'
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for stats in series_stats:
            for i, lesson in enumerate(stats['lessons'], 1):
                row = {
                    'SeriesName': stats['name'],
                    'Location': stats['location'],
                    'DayOfWeek': stats['day'],
                    'Category': stats['category'],
                    'OriginalAuthor': stats['author'],
                    'LessonSeq': i,
                    'RecordingDate': lesson['ParsedDate'].strftime('%Y-%m-%d') if lesson['ParsedDate'] else 'N/A',
                    'Serial': lesson.get('Serial', 'N/A'),
                    'SubTopic': lesson.get('SubTopic', 'N/A'),
                    'TelegramFileName': lesson['TelegramFileName'],
                    'Type': lesson['Type'],
                    'Topic': lesson.get('Topic', 'N/A'),
                    'DateInArabic': lesson.get('DateInArabic', 'N/A'),
                    'ClipLength': lesson.get('ClipLength', 'N/A'),
                    'doubtsStatus': lesson.get('doubtsStatus', 'N/A')
                }
                writer.writerow(row)

    print(f"✅ Organized CSV saved to: {output_file}")

    # Summary statistics
    print("\n" + "="*80)
    print("📈 SUMMARY STATISTICS")
    print("="*80)

    total_series = len(series_stats)
    total_lessons = sum(s['count'] for s in series_stats)

    series_with_dates = [s for s in series_stats if s['first_date']]
    total_expected = sum(s['expected'] for s in series_with_dates)
    total_missing = sum(s['missing'] for s in series_with_dates)

    print(f"\n📚 Total Series: {total_series}")
    print(f"📖 Total Lessons: {total_lessons}")
    if series_with_dates:
        print(f"📊 Expected Lessons (series with dates): {total_expected}")
        print(f"⚠️  Estimated Missing: {total_missing}")
        print(f"📈 Overall Completeness: {((total_expected - total_missing) / total_expected * 100):.1f}%")

    # By category
    print("\n📊 By Category:")
    cat_count = defaultdict(int)
    for s in series_stats:
        cat_count[s['category']] += s['count']

    for cat, count in sorted(cat_count.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count} lessons")

    # By location
    print("\n📍 By Location:")
    loc_count = defaultdict(int)
    for s in series_stats:
        loc_count[s['location']] += s['count']

    for loc, count in sorted(loc_count.items(), key=lambda x: -x[1]):
        print(f"   {loc}: {count} lessons")

    # Top 10 series
    print("\n🏆 Top 10 Series by Lesson Count:")
    for i, s in enumerate(series_stats[:10], 1):
        print(f"   {i:2d}. {s['name'][:50]:50s} | {s['count']:3d} lessons | {s['location']:15s} | {s['day']}")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
