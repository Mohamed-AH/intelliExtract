#!/usr/bin/env python3
"""
Manual-style extraction: Process series one-by-one like a human would
1. Take a series from WEEKLY_SCHEDULE_REFERENCE.md
2. Search for keywords (e.g., "تأسيس")
3. Filter by location
4. Extract details with high accuracy
5. Move to next series
"""

import json
import csv
import re
from datetime import datetime
from collections import defaultdict

# Complete series list from WEEKLY_SCHEDULE_REFERENCE.md with search keywords
SERIES_DATABASE = [
    {
        'name': 'تأسيس الأحكام شرح عمدة الأحكام',
        'keywords': ['تأسيس الأحكام', 'تأسيس', 'عمدة الأحكام', 'عمدة'],
        'location_masjid': True,
        'location_online': True,  # Exists in both locations
        'author': 'أحمد بن يحيى النجمي',
        'category': 'Hadeeth',
        'days_masjid': ['Sunday', 'Monday'],
        'days_online': ['Wednesday']
    },
    {
        'name': 'الملخص شرح كتاب التوحيد',
        'keywords': ['كتاب التوحيد', 'التوحيد', 'الملخص شرح كتاب'],
        'location_masjid': True,
        'location_online': False,
        'author': 'صالح الفوزان',
        'category': 'Aqeedah',
        'days_masjid': ['Sunday', 'Tuesday']
    },
    {
        'name': 'الملخص الفقهي',
        'keywords': ['الملخص الفقهي', 'الفقهي'],
        'location_masjid': True,
        'location_online': False,
        'author': 'صالح الفوزان',
        'category': 'Fiqh',
        'days_masjid': ['Monday', 'Wednesday']
    },
    {
        'name': 'الأفنان الندية',
        'keywords': ['الأفنان الندية', 'الأفنان', 'السبل السوية'],
        'location_masjid': False,
        'location_online': True,
        'author': 'زيد بن هادي المدخلي',
        'category': 'Fiqh',
        'days_online': ['Sunday', 'Monday']
    },
    {
        'name': 'معارج القبول شرح منظومة سلم الوصول',
        'keywords': ['سلم الوصول', 'منظومة', 'معارج القبول'],
        'location_masjid': False,
        'location_online': True,
        'author': 'حافظ حكمي',
        'category': 'Aqeedah',
        'days_online': ['Tuesday']
    },
    {
        'name': 'التفسير الميسر',
        'keywords': ['التفسير الميسر', 'التفسير', 'سورة'],
        'location_masjid': True,
        'location_online': False,
        'author': 'نخبة من أهل العلم',
        'category': 'Other',
        'days_masjid': ['Saturday']
    },
    {
        'name': 'إرشاد الساري شرح السنة للبربهاري',
        'keywords': ['شرح السنة', 'البربهاري', 'إرشاد الساري'],
        'location_masjid': True,
        'location_online': False,
        'author': 'أحمد النجمي',
        'category': 'Aqeedah',
        'days_masjid': ['Saturday']
    },
    {
        'name': 'صحيح البخاري',
        'keywords': ['صحيح البخاري', 'البخاري'],
        'location_masjid': True,
        'location_online': False,
        'author': 'محمد بن إسماعيل البخاري',
        'category': 'Hadeeth',
        'days_masjid': ['Friday']
    },
    {
        'name': 'المورد العذب الزلال',
        'keywords': ['المورد العذب', 'الزلال'],
        'location_masjid': True,
        'location_online': False,
        'author': 'أحمد النجمي',
        'category': 'Aqeedah',
        'days_masjid': ['Saturday']
    },
    {
        'name': 'التحفة النجمية بشرح الأربعين النووية',
        'keywords': ['التحفة النجمية', 'الأربعين النووية', 'النووية'],
        'location_masjid': True,
        'location_online': False,
        'author': 'أحمد النجمي',
        'category': 'Hadeeth',
        'days_masjid': ['Saturday']
    },
    {
        'name': 'مختصر السيرة النبوية',
        'keywords': ['مختصر السيرة', 'السيرة النبوية'],
        'location_masjid': True,
        'location_online': False,
        'author': 'محمد بن عبدالوهاب',
        'category': 'Seerah',
        'days_masjid': ['Saturday']
    },
    {
        'name': 'تنبيه الانام على ما في كتاب سبل السلام من الفوائد والأحكام',
        'keywords': ['تنبيه الانام', 'سبل السلام'],
        'location_masjid': True,
        'location_online': False,
        'author': 'أحمد النجمي',
        'category': 'Fiqh',
        'days_masjid': ['Saturday']
    },
    {
        'name': 'غنية السائل بما في لامية شيخ الإسلام من مسائل',
        'keywords': ['غنية السائل', 'لامية شيخ الإسلام'],
        'location_masjid': True,
        'location_online': False,
        'author': 'أحمد النجمي',
        'category': 'Aqeedah',
        'days_masjid': ['Saturday']
    }
]


def parse_date(date_str):
    """Parse date string"""
    if not date_str or date_str == "Not Available":
        return None
    formats = ['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_str.split()[0], fmt)
        except:
            continue
    return None


def get_day_name(date):
    """Get English day name"""
    if not date:
        return None
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return days[date.weekday()]


def is_online(text):
    """Detect if online"""
    return any(x in text for x in ['عن بُعد', 'عن بعد', 'بُعد', 'عبر قناة', 'عبر التليجرام'])


def extract_serial(text):
    """Extract serial/lesson number"""
    patterns = [
        r'الدرس\s+([^\n\s]+(?:\s+[^\n\s]+)?)',
        r'درس\s+([^\n\s]+)',
        r'الحلقة\s+([^\n\s]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return 'Not Available'


def extract_subtopic(text):
    """Extract subtopic/chapter"""
    patterns = [
        r'كتاب\s+([^\n]+?)(?:\n|$|\s{2})',
        r'باب\s+([^\n]+?)(?:\n|$|\s{2})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()[:100]
    return 'Not Available'


def extract_arabic_date(text):
    """Extract Hijri date"""
    patterns = [
        r'(\d{1,2}\s*[/\-]\s*\d{1,2}\s*[/\-]\s*\d{4})\s*ه',
        r'(\d{1,2}\s+\w+\s+\d{4})\s*ه',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return 'Not Available'


def main():
    print("\n" + "="*80)
    print("🎯 MANUAL-STYLE SERIES-BY-SERIES EXTRACTION")
    print("   Processing like a human: one series at a time")
    print("="*80 + "\n")

    # Load messages
    with open('5feb26_messages_parsed.json', 'r', encoding='utf-8') as f:
        messages = json.load(f)

    print(f"Loaded {len(messages)} messages\n")

    # Track which messages have been matched
    matched_messages = set()
    all_results = []

    # Process each series one by one
    for series_idx, series in enumerate(SERIES_DATABASE, 1):
        print(f"\n{'='*80}")
        print(f"[{series_idx}/{len(SERIES_DATABASE)}] Processing: {series['name']}")
        print(f"{'='*80}")

        # Determine which locations to check
        locations_to_check = []
        if series.get('location_masjid'):
            locations_to_check.append('جامع الورود')
        if series.get('location_online'):
            locations_to_check.append('Online')

        for location in locations_to_check:
            print(f"\n📍 Location: {location}")
            print(f"🔍 Searching for keywords: {', '.join(series['keywords'][:3])}...")

            series_matches = []

            # Search through all messages
            for msg_idx, msg in enumerate(messages):
                # Skip if already matched
                if msg_idx in matched_messages:
                    continue

                text = msg['message_text']
                filename = msg['filename']
                combined_text = f"{text} {filename}".lower()

                # Check location match
                msg_location = 'Online' if is_online(text) else 'جامع الورود'
                if msg_location != location:
                    continue

                # Check if any keyword matches
                keyword_match = False
                for keyword in series['keywords']:
                    if keyword.lower() in combined_text:
                        keyword_match = True
                        break

                if not keyword_match:
                    continue

                # Parse date and day
                date = parse_date(msg['greg_date'])
                day_of_week = get_day_name(date)

                # Optional: validate day of week if we have date
                expected_days = series.get(f"days_{'online' if location == 'Online' else 'masjid'}", [])
                if day_of_week and expected_days and day_of_week not in expected_days:
                    # Day doesn't match schedule, but include with doubt
                    doubt = f"Day mismatch: {day_of_week} (expected: {', '.join(expected_days)})"
                else:
                    doubt = "none"

                # Extract details
                record = {
                    'TelegramFileName': filename,
                    'Type': 'Series',
                    'Topic': 'Not Available',
                    'SeriesName': series['name'],
                    'SubTopic': extract_subtopic(text),
                    'Serial': extract_serial(text),
                    'OriginalAuthor': series['author'],
                    'Location/Online': location,
                    'Sheikh': 'حسن بن محمد منصور الدغريري',
                    'DateInArabic': extract_arabic_date(text),
                    'DateInGreg': msg['greg_date'],
                    'DayOfWeek': day_of_week or 'Unknown',
                    'ClipLength': msg['clip_length'],
                    'Category': series['category'],
                    'MatchedBy': f'Manual-style ({series_idx})',
                    'doubtsStatus': doubt
                }

                series_matches.append((msg_idx, record))
                print(f"   ✓ {filename[:50]:50s} | {day_of_week or 'N/A':9s} | {record['Serial'][:20]}")

            # Add all matches for this series/location
            for msg_idx, record in series_matches:
                matched_messages.add(msg_idx)
                all_results.append(record)

            print(f"\n   Found {len(series_matches)} lessons for {series['name']} at {location}")

    # Handle Khutbas separately
    print(f"\n{'='*80}")
    print(f"[Special] Processing Khutbas (Friday Sermons)")
    print(f"{'='*80}\n")

    khutba_count = 0
    for msg_idx, msg in enumerate(messages):
        if msg_idx in matched_messages:
            continue

        text = msg['message_text']
        date = parse_date(msg['greg_date'])
        day_of_week = get_day_name(date)

        # Check if it's a Khutba
        if ('خطبة' in text or 'الجمعة' in text) and 'صحيح البخاري' not in text:
            location = 'Online' if is_online(text) else 'جامع الورود'

            # Extract topic from Khutba
            topic = 'Not Available'
            topic_patterns = [
                r'[\[【]([^\]】]+)[\]】]',
                r'عنوان[:\s]+([^\n]+)',
            ]
            for pattern in topic_patterns:
                match = re.search(pattern, text)
                if match:
                    topic = match.group(1).strip()
                    break

            record = {
                'TelegramFileName': msg['filename'],
                'Type': 'Khutba',
                'Topic': topic,
                'SeriesName': 'Not Available',
                'SubTopic': 'Not Available',
                'Serial': 'Not Available',
                'OriginalAuthor': 'Not Available',
                'Location/Online': location,
                'Sheikh': 'حسن بن محمد منصور الدغريري',
                'DateInArabic': extract_arabic_date(text),
                'DateInGreg': msg['greg_date'],
                'DayOfWeek': day_of_week or 'Unknown',
                'ClipLength': msg['clip_length'],
                'Category': 'Other',
                'MatchedBy': 'Khutba Detection',
                'doubtsStatus': 'none' if day_of_week == 'Friday' else 'not on Friday'
            }

            matched_messages.add(msg_idx)
            all_results.append(record)
            khutba_count += 1
            print(f"   ✓ {msg['filename'][:50]:50s} | {topic[:30]}")

    print(f"\n   Found {khutba_count} Khutbas")

    # Add unmatched messages
    print(f"\n{'='*80}")
    print(f"[Remaining] Unmatched Messages")
    print(f"{'='*80}\n")

    unmatched_count = 0
    for msg_idx, msg in enumerate(messages):
        if msg_idx in matched_messages:
            continue

        text = msg['message_text']
        date = parse_date(msg['greg_date'])
        day_of_week = get_day_name(date)
        location = 'Online' if is_online(text) else 'جامع الورود'

        record = {
            'TelegramFileName': msg['filename'],
            'Type': 'Unknown',
            'Topic': 'Not Available',
            'SeriesName': 'Not Available',
            'SubTopic': extract_subtopic(text),
            'Serial': extract_serial(text),
            'OriginalAuthor': 'Not Available',
            'Location/Online': location,
            'Sheikh': 'حسن بن محمد منصور الدغريري',
            'DateInArabic': extract_arabic_date(text),
            'DateInGreg': msg['greg_date'],
            'DayOfWeek': day_of_week or 'Unknown',
            'ClipLength': msg['clip_length'],
            'Category': 'Other',
            'MatchedBy': 'Unmatched',
            'doubtsStatus': 'Could not match to any series'
        }

        all_results.append(record)
        unmatched_count += 1

    print(f"   {unmatched_count} messages could not be matched to any series")

    # Save to CSV
    output_file = '5feb26_extracted_lectures_manual_style.csv'

    fieldnames = [
        'TelegramFileName', 'Type', 'Topic', 'SeriesName', 'SubTopic',
        'Serial', 'OriginalAuthor', 'Location/Online', 'Sheikh',
        'DateInArabic', 'DateInGreg', 'DayOfWeek', 'ClipLength',
        'Category', 'MatchedBy', 'doubtsStatus'
    ]

    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    # Print summary
    print(f"\n{'='*80}")
    print("📊 EXTRACTION SUMMARY")
    print(f"{'='*80}")

    total = len(all_results)
    series_count = sum(1 for r in all_results if r['Type'] == 'Series')
    khutba_count_final = sum(1 for r in all_results if r['Type'] == 'Khutba')
    unknown = sum(1 for r in all_results if r['Type'] == 'Unknown')

    print(f"\nTotal Messages: {total}")
    print(f"✅ Matched to Series: {series_count} ({series_count/total*100:.1f}%)")
    print(f"✅ Khutbas: {khutba_count_final} ({khutba_count_final/total*100:.1f}%)")
    print(f"❓ Unmatched: {unknown} ({unknown/total*100:.1f}%)")
    print(f"\n💾 Saved to: {output_file}")

    # Series breakdown
    series_counts = defaultdict(int)
    for r in all_results:
        if r['Type'] == 'Series':
            key = f"{r['SeriesName']}|{r['Location/Online']}"
            series_counts[key] += 1

    print(f"\n📚 Series Breakdown ({len(series_counts)} unique series):")
    for series_key, count in sorted(series_counts.items(), key=lambda x: -x[1]):
        parts = series_key.split('|')
        print(f"   {parts[0][:55]:55s} | {parts[1]:15s} | {count:3d} lessons")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
