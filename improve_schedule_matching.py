#!/usr/bin/env python3
"""
Improve the schedule-based CSV by adding smarter keyword matching
Reads the initial schedule-based CSV and improves unmatched records
"""

import csv
import re
from collections import defaultdict

# Keywords that indicate specific series
SERIES_KEYWORDS = {
    'تأسيس الأحكام شرح عمدة الأحكام': [
        'تأسيس الأحكام', 'عمدة الأحكام', 'النكاح', 'الصلاة', 'الطهارة', 'الصيام',
        'اللعان', 'أحمد النجمي', 'النجمي'
    ],
    'الملخص شرح كتاب التوحيد': [
        'كتاب التوحيد', 'الملخص', 'التوحيد', 'صالح الفوزان', 'الفوزان'
    ],
    'الملخص الفقهي': [
        'الملخص الفقهي', 'الفقهي', 'صالح الفوزان'
    ],
    'الأفنان الندية': [
        'الأفنان الندية', 'الأفنان', 'الفرائض', 'البيوع', 'الربا',
        'زيد المدخلي', 'المدخلي'
    ],
    'معارج القبول شرح منظومة سلم الوصول': [
        'سلم الوصول', 'منظومة', 'معارج القبول', 'حافظ حكمي'
    ],
    'التفسير الميسر': [
        'التفسير الميسر', 'سورة', 'الطارق', 'التكوير'
    ],
    'شرح السنة للبربهاري': [
        'شرح السنة', 'البربهاري', 'السنة'
    ],
    'صحيح البخاري': [
        'صحيح البخاري', 'البخاري'
    ],
    'المورد العذب الزلال': [
        'المورد العذب', 'الزلال'
    ],
    'التحفة النجمية بشرح الأربعين النووية': [
        'التحفة النجمية', 'الأربعين النووية', 'النووية'
    ],
    'مختصر السيرة النبوية': [
        'مختصر السيرة', 'السيرة النبوية'
    ],
    'تنبيه الانام على ما في كتاب سبل السلام': [
        'تنبيه الانام', 'سبل السلام'
    ]
}

# Author to series mapping
AUTHOR_SERIES = {
    'صالح الفوزان': ['الملخص شرح كتاب التوحيد', 'الملخص الفقهي'],
    'أحمد النجمي': ['تأسيس الأحكام شرح عمدة الأحكام', 'المورد العذب الزلال'],
    'زيد المدخلي': ['الأفنان الندية'],
    'حافظ حكمي': ['معارج القبول شرح منظومة سلم الوصول'],
}

# Series metadata
SERIES_INFO = {
    'تأسيس الأحكام شرح عمدة الأحكام': {
        'author': 'أحمد بن يحيى النجمي',
        'category': 'Hadeeth'
    },
    'الملخص شرح كتاب التوحيد': {
        'author': 'صالح الفوزان',
        'category': 'Aqeedah'
    },
    'الملخص الفقهي': {
        'author': 'صالح الفوزان',
        'category': 'Fiqh'
    },
    'الأفنان الندية': {
        'author': 'زيد بن هادي المدخلي',
        'category': 'Fiqh'
    },
    'معارج القبول شرح منظومة سلم الوصول': {
        'author': 'حافظ حكمي',
        'category': 'Aqeedah'
    },
    'التفسير الميسر': {
        'author': 'نخبة من أهل العلم',
        'category': 'Other'
    },
    'شرح السنة للبربهاري': {
        'author': 'أحمد النجمي',
        'category': 'Aqeedah'
    },
    'صحيح البخاري': {
        'author': 'محمد بن إسماعيل البخاري',
        'category': 'Hadeeth'
    },
    'المورد العذب الزلال': {
        'author': 'أحمد النجمي',
        'category': 'Aqeedah'
    },
    'التحفة النجمية بشرح الأربعين النووية': {
        'author': 'أحمد النجمي',
        'category': 'Hadeeth'
    },
    'مختصر السيرة النبوية': {
        'author': 'محمد بن عبدالوهاب',
        'category': 'Seerah'
    },
    'تنبيه الانام على ما في كتاب سبل السلام من الفوائد والأحكام': {
        'author': 'أحمد النجمي',
        'category': 'Fiqh'
    }
}

# Day-based schedule
DAY_SCHEDULE = {
    'Saturday': ['غنية السائل', 'المورد العذب الزلال', 'شرح السنة للبربهاري',
                 'التحفة النجمية', 'مختصر السيرة النبوية', 'تنبيه الانام',
                 'التفسير الميسر'],
    'Sunday': ['الملخص شرح كتاب التوحيد', 'تأسيس الأحكام شرح عمدة الأحكام', 'الأفنان الندية'],
    'Monday': ['الملخص الفقهي', 'تأسيس الأحكام شرح عمدة الأحكام', 'الأفنان الندية'],
    'Tuesday': ['الملخص شرح كتاب التوحيد', 'معارج القبول شرح منظومة سلم الوصول'],
    'Wednesday': ['الملخص الفقهي', 'تأسيس الأحكام شرح عمدة الأحكام'],
    'Friday': ['خطبة الجمعة', 'صحيح البخاري']
}


def find_series_by_keywords(text, subtopic, day_of_week, location):
    """Find series using keyword matching"""

    # Normalize text
    text_combined = f"{text} {subtopic}".lower()

    # Score each series
    scores = defaultdict(int)

    for series, keywords in SERIES_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_combined:
                scores[series] += len(keyword)  # Longer keyword = higher score

    # Filter by day schedule if available
    if day_of_week and day_of_week in DAY_SCHEDULE:
        day_series = DAY_SCHEDULE[day_of_week]
        # Boost scores for series on this day
        for series in scores:
            if any(day_s in series for day_s in day_series):
                scores[series] += 20

    # Return best match
    if scores:
        best_series = max(scores, key=scores.get)
        if scores[best_series] >= 3:  # Minimum threshold
            return best_series

    return None


def main():
    print("\n" + "="*80)
    print("🔧 IMPROVING SCHEDULE-BASED EXTRACTION")
    print("="*80 + "\n")

    # Read the schedule-based CSV
    with open('extracted_lectures_schedule_based.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        records = list(reader)

    print(f"Loaded {len(records)} records")
    print(f"Processing unmatched records...\n")

    improved = 0
    for i, record in enumerate(records):
        if record['Type'] == 'Unknown' or record['SeriesName'] == 'Not Available':
            # Try to find series using keywords
            filename = record['TelegramFileName']
            subtopic = record['SubTopic']
            day = record['DayOfWeek']
            location = record['Location/Online']

            # Read the original message for more context
            # For now, use what we have
            series = find_series_by_keywords(filename + " " + subtopic, subtopic, day, location)

            if series and series in SERIES_INFO:
                record['Type'] = 'Series'
                record['SeriesName'] = series
                record['OriginalAuthor'] = SERIES_INFO[series]['author']
                record['Category'] = SERIES_INFO[series]['category']
                record['MatchedBy'] = f'Keyword Match ({day})'
                record['doubtsStatus'] = 'matched by keywords'
                improved += 1
                print(f"  ✓ Matched: {filename[:50]} → {series[:40]}")

    # Save improved CSV
    output_file = 'extracted_lectures_final.csv'

    fieldnames = list(records[0].keys())

    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    # Count results
    matched = sum(1 for r in records if r['Type'] != 'Unknown')
    khutbas = sum(1 for r in records if r['Type'] == 'Khutba')
    series = sum(1 for r in records if r['Type'] == 'Series')
    unmatched = sum(1 for r in records if r['Type'] == 'Unknown')

    print(f"\n✅ Saved to: {output_file}")
    print("\n" + "="*80)
    print("📊 FINAL STATISTICS")
    print("="*80)
    print(f"\nTotal Records: {len(records)}")
    print(f"Matched (Series + Khutba): {matched} ({matched/len(records)*100:.1f}%)")
    print(f"  - Series: {series}")
    print(f"  - Khutbas: {khutbas}")
    print(f"Still Unmatched: {unmatched} ({unmatched/len(records)*100:.1f}%)")
    print(f"\nImproved in this pass: {improved}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
