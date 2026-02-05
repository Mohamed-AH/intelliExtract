#!/usr/bin/env python3
"""
Extract data using STRICT schedule matching from WEEKLY_SCHEDULE_REFERENCE.md
This is the most accurate extraction method.
"""

import json
import csv
import re
from datetime import datetime
from collections import defaultdict

# Authoritative schedule from WEEKLY_SCHEDULE_REFERENCE.md
SCHEDULE = {
    'Saturday': [
        {
            'name': 'غنية السائل بما في لامية شيخ الإسلام من مسائل',
            'type': 'Lecture',
            'author': 'أحمد النجمي',
            'location': 'جامع الورود',
            'category': 'Aqeedah'
        },
        {
            'name': 'المورد العذب الزلال',
            'type': 'Series',
            'author': 'أحمد النجمي',
            'location': 'جامع الورود',
            'category': 'Aqeedah'
        },
        {
            'name': 'إرشاد الساري شرح السنة للبربهاري',
            'type': 'Series',
            'author': 'أحمد النجمي',
            'location': 'جامع الورود',
            'category': 'Aqeedah',
            'aliases': ['شرح السنة للبربهاري', 'شرح السنة']
        },
        {
            'name': 'التحفة النجمية بشرح الأربعين النووية',
            'type': 'Series',
            'author': 'أحمد النجمي',
            'location': 'جامع الورود',
            'category': 'Hadeeth'
        },
        {
            'name': 'مختصر السيرة النبوية',
            'type': 'Series',
            'author': 'محمد بن عبدالوهاب',
            'location': 'جامع الورود',
            'category': 'Seerah'
        },
        {
            'name': 'تنبيه الانام على ما في كتاب سبل السلام من الفوائد والأحكام',
            'type': 'Series',
            'author': 'أحمد النجمي',
            'location': 'جامع الورود',
            'category': 'Fiqh',
            'aliases': ['تنبيه الانام', 'سبل السلام']
        },
        {
            'name': 'التفسير الميسر',
            'type': 'Series',
            'author': 'نخبة من أهل العلم',
            'location': 'جامع الورود',
            'category': 'Other'
        }
    ],
    'Sunday': [
        {
            'name': 'الملخص شرح كتاب التوحيد',
            'type': 'Series',
            'author': 'صالح الفوزان',
            'location': 'جامع الورود',
            'category': 'Aqeedah',
            'aliases': ['الملخص في شرح كتاب التوحيد', 'كتاب التوحيد']
        },
        {
            'name': 'تأسيس الأحكام شرح عمدة الأحكام',
            'type': 'Series',
            'author': 'أحمد بن يحيى النجمي',
            'location': 'جامع الورود',
            'category': 'Hadeeth',
            'aliases': ['تأسيس الأحكام', 'عمدة الأحكام']
        },
        {
            'name': 'الأفنان الندية',
            'type': 'Series',
            'author': 'زيد بن هادي المدخلي',
            'location': 'Online',
            'category': 'Fiqh',
            'aliases': ['الأفنان الندية شرح السبل السوية']
        }
    ],
    'Monday': [
        {
            'name': 'الملخص الفقهي',
            'type': 'Series',
            'author': 'صالح الفوزان',
            'location': 'جامع الورود',
            'category': 'Fiqh'
        },
        {
            'name': 'تأسيس الأحكام شرح عمدة الأحكام',
            'type': 'Series',
            'author': 'أحمد بن يحيى النجمي',
            'location': 'جامع الورود',
            'category': 'Hadeeth',
            'aliases': ['تأسيس الأحكام', 'عمدة الأحكام']
        },
        {
            'name': 'الأفنان الندية',
            'type': 'Series',
            'author': 'زيد بن هادي المدخلي',
            'location': 'Online',
            'category': 'Fiqh',
            'aliases': ['الأفنان الندية شرح السبل السوية']
        }
    ],
    'Tuesday': [
        {
            'name': 'الملخص شرح كتاب التوحيد',
            'type': 'Series',
            'author': 'صالح الفوزان',
            'location': 'جامع الورود',
            'category': 'Aqeedah',
            'aliases': ['الملخص في شرح كتاب التوحيد', 'كتاب التوحيد']
        },
        {
            'name': 'معارج القبول شرح منظومة سلم الوصول',
            'type': 'Series',
            'author': 'حافظ حكمي',
            'location': 'Online',
            'category': 'Aqeedah',
            'aliases': ['منظومة سلم الوصول', 'سلم الوصول', 'معارج القبول']
        }
    ],
    'Wednesday': [
        {
            'name': 'الملخص الفقهي',
            'type': 'Series',
            'author': 'صالح الفوزان',
            'location': 'جامع الورود',
            'category': 'Fiqh'
        },
        {
            'name': 'تأسيس الأحكام شرح عمدة الأحكام',
            'type': 'Series',
            'author': 'أحمد بن يحيى النجمي',
            'location': 'Online',
            'category': 'Hadeeth',
            'aliases': ['تأسيس الأحكام', 'عمدة الأحكام']
        }
    ],
    'Thursday': [
        # No regular scheduled classes
    ],
    'Friday': [
        {
            'name': 'خطبة الجمعة',
            'type': 'Khutba',
            'author': 'Not Available',
            'location': 'جامع الورود',
            'category': 'Other'
        },
        {
            'name': 'صحيح البخاري',
            'type': 'Series',
            'author': 'محمد بن إسماعيل البخاري',
            'location': 'جامع الورود',
            'category': 'Hadeeth'
        }
    ]
}


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


def get_day_name(date):
    """Get English day name from date"""
    if not date:
        return None
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return days[date.weekday()]


def is_online(text):
    """Detect if class is online"""
    online_indicators = ['عن بُعد', 'عن بعد', 'بُعد', 'عبر قناة', 'عبر التليجرام']
    return any(indicator in text for indicator in online_indicators)


def normalize_text(text):
    """Normalize Arabic text for matching"""
    if not text:
        return ""
    # Remove tashkeel and extra spaces
    text = re.sub(r'[\u064B-\u065F]', '', text)  # Remove diacritics
    text = re.sub(r'\s+', ' ', text)  # Normalize spaces
    return text.strip()


def match_series(message_text, day_of_week, location):
    """Match message to series using schedule"""
    if not day_of_week or day_of_week not in SCHEDULE:
        return None

    normalized_text = normalize_text(message_text)
    day_series = SCHEDULE[day_of_week]

    # Filter by location first
    candidates = [s for s in day_series if s['location'] == location]

    if not candidates:
        # If no exact location match, try all series for that day
        candidates = day_series

    # Try to match series name
    best_match = None
    best_score = 0

    for series in candidates:
        # Check main name
        series_normalized = normalize_text(series['name'])
        if series_normalized in normalized_text:
            score = len(series_normalized)
            if score > best_score:
                best_score = score
                best_match = series

        # Check aliases
        if 'aliases' in series:
            for alias in series['aliases']:
                alias_normalized = normalize_text(alias)
                if alias_normalized in normalized_text:
                    score = len(alias_normalized)
                    if score > best_score:
                        best_score = score
                        best_match = series

    return best_match


def extract_serial(text):
    """Extract serial/lesson number"""
    # Arabic patterns
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
            return match.group(1).strip()[:100]  # Limit length

    return 'Not Available'


def extract_topic_for_khutba(text):
    """Extract topic for Khutba messages"""
    # Look for patterns like: موضوع: xxx or عنوان: xxx
    patterns = [
        r'(?:موضوع|عنوان|الخطبة)\s*[:：]\s*([^\n]+)',
        r'[\[【]([^\]】]+)[\]】]',  # Text in brackets
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            topic = match.group(1).strip()
            if len(topic) > 5 and len(topic) < 100:
                return topic

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
    print("📚 SCHEDULE-BASED STRICT EXTRACTION")
    print("   Using WEEKLY_SCHEDULE_REFERENCE.md as authoritative source")
    print("="*80 + "\n")

    # Load messages
    with open('messages_parsed.json', 'r', encoding='utf-8') as f:
        messages = json.load(f)

    print(f"Loaded {len(messages)} messages\n")

    results = []
    stats = {
        'total': len(messages),
        'matched_by_schedule': 0,
        'unmatched': 0,
        'khutbas': 0,
        'by_day': defaultdict(int)
    }

    for i, msg in enumerate(messages):
        print(f"Processing {i+1}/{len(messages)}: {msg['filename'][:50]}...")

        # Parse date
        date = parse_date(msg['greg_date'])
        day_of_week = get_day_name(date) if date else None

        if day_of_week:
            stats['by_day'][day_of_week] += 1

        # Determine location
        text = msg['message_text']
        location = 'Online' if is_online(text) else 'جامع الورود'

        # Check if it's a Khutba (Friday sermon)
        is_khutba = (day_of_week == 'Friday' and
                     ('خطبة' in text or 'الجمعة' in text) and
                     'صحيح البخاري' not in text)

        if is_khutba:
            # Handle Khutba separately
            record = {
                'TelegramFileName': msg['filename'],
                'Type': 'Khutba',
                'Topic': extract_topic_for_khutba(text),
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
            stats['khutbas'] += 1
        else:
            # Try to match using schedule
            matched_series = match_series(text, day_of_week, location)

            if matched_series:
                # Matched successfully
                record = {
                    'TelegramFileName': msg['filename'],
                    'Type': matched_series['type'],
                    'Topic': 'Not Available' if matched_series['type'] == 'Series' else extract_topic_for_khutba(text),
                    'SeriesName': matched_series['name'],
                    'SubTopic': extract_subtopic(text),
                    'Serial': extract_serial(text),
                    'OriginalAuthor': matched_series['author'],
                    'Location/Online': matched_series['location'],
                    'Sheikh': 'حسن بن محمد منصور الدغريري',
                    'DateInArabic': extract_arabic_date(text),
                    'DateInGreg': msg['greg_date'],
                    'DayOfWeek': day_of_week or 'Unknown',
                    'ClipLength': msg['clip_length'],
                    'Category': matched_series['category'],
                    'MatchedBy': f'Schedule ({day_of_week})',
                    'doubtsStatus': 'none'
                }
                stats['matched_by_schedule'] += 1
            else:
                # Could not match
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
                    'MatchedBy': 'Not Matched',
                    'doubtsStatus': f'Could not match to schedule (Day: {day_of_week}, Location: {location})'
                }
                stats['unmatched'] += 1

        results.append(record)

    # Save to CSV
    output_file = 'extracted_lectures_schedule_based.csv'

    fieldnames = [
        'TelegramFileName', 'Type', 'Topic', 'SeriesName', 'SubTopic',
        'Serial', 'OriginalAuthor', 'Location/Online', 'Sheikh',
        'DateInArabic', 'DateInGreg', 'DayOfWeek', 'ClipLength',
        'Category', 'MatchedBy', 'doubtsStatus'
    ]

    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Saved to: {output_file}")

    # Print statistics
    print("\n" + "="*80)
    print("📊 EXTRACTION STATISTICS")
    print("="*80)
    print(f"\nTotal Messages: {stats['total']}")
    print(f"Matched by Schedule: {stats['matched_by_schedule']} ({stats['matched_by_schedule']/stats['total']*100:.1f}%)")
    print(f"Khutbas: {stats['khutbas']}")
    print(f"Unmatched: {stats['unmatched']} ({stats['unmatched']/stats['total']*100:.1f}%)")

    print("\nMessages by Day:")
    for day in ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        count = stats['by_day'].get(day, 0)
        if count > 0:
            print(f"  {day}: {count}")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
