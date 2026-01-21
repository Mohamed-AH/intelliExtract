#!/usr/bin/env python3
"""
Analyze and organize Islamic lectures into series based on:
- Recording date from filename
- Day of week pattern
- Series name
- Location (masjid vs online)
"""

import json
import csv
import re
from datetime import datetime, timedelta
from collections import defaultdict

def extract_date_from_filename(filename):
    """Extract recording date from filename"""
    if not filename or filename == "Not Available":
        return None

    # Pattern: AUDIO-2026-01-17-21-42-37.m4a
    match = re.search(r'AUDIO-(\d{4})-(\d{2})-(\d{2})-', filename)
    if match:
        year, month, day = match.groups()
        return datetime(int(year), int(month), int(day))

    # Pattern: AUD-20260102-WA0002.m4a
    match = re.search(r'AUD-(\d{4})(\d{2})(\d{2})-', filename)
    if match:
        year, month, day = match.groups()
        return datetime(int(year), int(month), int(day))

    # Pattern: 4_5992475423785622177.mp3 (no date in filename)
    return None


def get_day_name_arabic(date):
    """Get Arabic day name"""
    days = {
        0: 'الاثنين',     # Monday
        1: 'الثلاثاء',    # Tuesday
        2: 'الأربعاء',    # Wednesday
        3: 'الخميس',      # Thursday
        4: 'الجمعة',      # Friday
        5: 'السبت',       # Saturday
        6: 'الأحد'        # Sunday
    }
    return days[date.weekday()]


def get_day_name_english(date):
    """Get English day name"""
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return days[date.weekday()]


def normalize_series_name(series_name):
    """Normalize series name for grouping"""
    if not series_name or series_name == "Not Available":
        return "Unknown"

    # Clean up common variations
    series_name = series_name.strip()
    series_name = re.sub(r'\s+', ' ', series_name)

    return series_name


def main():
    print("\n" + "="*80)
    print("📚 ISLAMIC LECTURES SERIES ANALYZER")
    print("="*80 + "\n")

    # Load extracted data
    with open('extracted_lectures_data.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        records = list(reader)

    print(f"Loaded {len(records)} records\n")

    # Parse dates and enrich records
    records_with_dates = []
    no_date_count = 0

    for record in records:
        filename = record['TelegramFileName']
        date = extract_date_from_filename(filename)

        if date:
            record['RecordingDate'] = date
            record['DayOfWeek'] = get_day_name_english(date)
            record['DayOfWeekArabic'] = get_day_name_arabic(date)
            records_with_dates.append(record)
        else:
            no_date_count += 1

    print(f"✅ Extracted dates from {len(records_with_dates)} filenames")
    print(f"⚠️  Could not extract dates from {no_date_count} filenames\n")

    # Group by series
    series_groups = defaultdict(list)

    for record in records_with_dates:
        series_name = normalize_series_name(record['SeriesName'])
        location = record['Location/Online']
        day_of_week = record['DayOfWeek']

        # Create unique key: SeriesName + Location + DayOfWeek
        # This ensures same series name on different days or locations are separate
        series_key = f"{series_name} | {location} | {day_of_week}"

        series_groups[series_key].append(record)

    # Sort each series by date
    for key in series_groups:
        series_groups[key].sort(key=lambda x: x['RecordingDate'])

    print(f"📊 Identified {len(series_groups)} unique series (by name + location + day)\n")

    # Analyze each series
    print("="*80)
    print("SERIES ANALYSIS")
    print("="*80 + "\n")

    series_analysis = []

    for series_key, lessons in sorted(series_groups.items(), key=lambda x: len(x[1]), reverse=True):
        parts = series_key.split(" | ")
        series_name = parts[0]
        location = parts[1]
        day_of_week = parts[2]

        if len(lessons) < 2:  # Skip single-lesson series for now
            continue

        first_date = lessons[0]['RecordingDate']
        last_date = lessons[-1]['RecordingDate']
        total_weeks = (last_date - first_date).days // 7 + 1

        # Calculate expected lessons (one per week)
        expected_lessons = total_weeks
        actual_lessons = len(lessons)
        missing_lessons = expected_lessons - actual_lessons

        # Get category
        category = lessons[0].get('Category', 'Unknown')
        author = lessons[0].get('OriginalAuthor', 'Unknown')

        analysis = {
            'SeriesName': series_name,
            'Location': location,
            'DayOfWeek': day_of_week,
            'Category': category,
            'Author': author,
            'TotalLessons': actual_lessons,
            'FirstDate': first_date.strftime('%Y-%m-%d'),
            'LastDate': last_date.strftime('%Y-%m-%d'),
            'WeeksSpan': total_weeks,
            'ExpectedLessons': expected_lessons,
            'MissingLessons': missing_lessons,
            'Completeness': f"{(actual_lessons/expected_lessons)*100:.1f}%" if expected_lessons > 0 else "N/A",
            'Lessons': lessons
        }

        series_analysis.append(analysis)

        # Print series summary
        print(f"📖 {series_name}")
        print(f"   📍 Location: {location}")
        print(f"   📅 Day: {day_of_week}")
        print(f"   📚 Category: {category}")
        print(f"   ✍️  Author: {author}")
        print(f"   📊 Lessons: {actual_lessons} (Expected: {expected_lessons}, Missing: {missing_lessons})")
        print(f"   📈 Completeness: {(actual_lessons/expected_lessons)*100:.1f}%")
        print(f"   📆 Date Range: {first_date.strftime('%Y-%m-%d')} to {last_date.strftime('%Y-%m-%d')}")

        # Show gaps if any
        if missing_lessons > 0:
            print(f"   ⚠️  Potential gaps:")
            for i in range(len(lessons) - 1):
                current_date = lessons[i]['RecordingDate']
                next_date = lessons[i+1]['RecordingDate']
                days_diff = (next_date - current_date).days

                if days_diff > 14:  # More than 2 weeks gap
                    weeks_gap = days_diff // 7
                    print(f"      • Gap of {weeks_gap} weeks between {current_date.strftime('%Y-%m-%d')} and {next_date.strftime('%Y-%m-%d')}")

        print()

    # Save organized CSV grouped by series
    print("\n" + "="*80)
    print("GENERATING ORGANIZED CSV")
    print("="*80 + "\n")

    output_file = 'lectures_organized_by_series.csv'

    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = [
            'SeriesName', 'Location', 'DayOfWeek', 'Category', 'Author',
            'LessonNumber', 'RecordingDate', 'TelegramFileName',
            'Type', 'Topic', 'SubTopic', 'Serial',
            'DateInArabic', 'DateInGreg', 'ClipLength', 'doubtsStatus'
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for analysis in sorted(series_analysis, key=lambda x: (-x['TotalLessons'], x['SeriesName'])):
            for i, lesson in enumerate(analysis['Lessons'], 1):
                row = {
                    'SeriesName': analysis['SeriesName'],
                    'Location': analysis['Location'],
                    'DayOfWeek': analysis['DayOfWeek'],
                    'Category': analysis['Category'],
                    'Author': analysis['Author'],
                    'LessonNumber': i,
                    'RecordingDate': lesson['RecordingDate'].strftime('%Y-%m-%d'),
                    'TelegramFileName': lesson['TelegramFileName'],
                    'Type': lesson['Type'],
                    'Topic': lesson['Topic'],
                    'SubTopic': lesson['SubTopic'],
                    'Serial': lesson['Serial'],
                    'DateInArabic': lesson['DateInArabic'],
                    'DateInGreg': lesson['DateInGreg'],
                    'ClipLength': lesson['ClipLength'],
                    'doubtsStatus': lesson['doubtsStatus']
                }
                writer.writerow(row)

    print(f"✅ Saved organized CSV to: {output_file}")

    # Print summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)

    total_series = len(series_analysis)
    total_lessons_all = sum(s['TotalLessons'] for s in series_analysis)
    total_expected = sum(s['ExpectedLessons'] for s in series_analysis)
    total_missing = sum(s['MissingLessons'] for s in series_analysis)

    print(f"📚 Total Series: {total_series}")
    print(f"📖 Total Lessons: {total_lessons_all}")
    print(f"📊 Expected Lessons: {total_expected}")
    print(f"⚠️  Missing Lessons: {total_missing}")
    print(f"📈 Overall Completeness: {(total_lessons_all/total_expected)*100:.1f}%")

    # Category breakdown
    print("\n📊 By Category:")
    category_count = defaultdict(int)
    for analysis in series_analysis:
        category_count[analysis['Category']] += analysis['TotalLessons']

    for category, count in sorted(category_count.items(), key=lambda x: -x[1]):
        print(f"   {category}: {count} lessons")

    # Location breakdown
    print("\n📍 By Location:")
    location_count = defaultdict(int)
    for analysis in series_analysis:
        location_count[analysis['Location']] += analysis['TotalLessons']

    for location, count in sorted(location_count.items(), key=lambda x: -x[1]):
        print(f"   {location}: {count} lessons")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
