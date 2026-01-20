#!/usr/bin/env python3
"""
Process all messages and create CSV output
This script reads the parsed messages and creates a template for data extraction
"""

import json
import csv


def classify_message(msg):
    """
    Classify message and extract basic information
    This is a simplified extraction - for full accuracy, use Claude API
    """
    text = msg['message_text']

    # Initialize record
    record = {
        'TelegramFileName': msg['filename'],
        'Type': 'Not Available',
        'Topic': 'Not Available',
        'SeriesName': 'Not Available',
        'SubTopic': 'Not Available',
        'Serial': 'Not Available',
        'OriginalAuthor': 'Not Available',
        'Location/Online': 'جامع الورود',
        'Sheikh': 'حسن بن محمد منصور الدغريري',
        'DateInArabic': 'Not Available',
        'DateInGreg': msg['greg_date'],
        'ClipLength': msg['clip_length'],
        'Category': 'Not Available',
        'doubtsStatus': 'needs_review'
    }

    # Type detection
    if '#خطبة_الجمعة' in text or 'خطبة' in text:
        record['Type'] = 'Khutba'
    elif 'محاضرة' in text:
        record['Type'] = 'Lecture'
    elif 'الدرس' in text or 'شرح' in text:
        record['Type'] = 'Series'

    # Detect if online
    if 'عن بُعد' in text or 'عبر قناة' in text or 'بُعد' in text:
        record['Location/Online'] = 'Online'

    # Series detection
    if 'تأسيس الأحكام' in text:
        record['SeriesName'] = 'تأسيس الأحكام شرح عمدة الأحكام'
        record['OriginalAuthor'] = 'أحمد بن يحيى النجمي'
        record['Category'] = 'Hadeeth'
    elif 'الملخص الفقهي' in text:
        record['SeriesName'] = 'الملخص الفقهي'
        record['OriginalAuthor'] = 'صالح الفوزان'
        record['Category'] = 'Fiqh'
    elif 'كتاب التوحيد' in text or 'الملخص شرح كتاب التوحيد' in text:
        record['SeriesName'] = 'الملخص شرح كتاب التوحيد'
        record['OriginalAuthor'] = 'صالح الفوزان'
        record['Category'] = 'Aqeedah'
    elif 'الأفنان الندية' in text:
        record['SeriesName'] = 'الأفنان الندية'
        record['OriginalAuthor'] = 'زيد بن هادي المدخلي'
        record['Category'] = 'Fiqh'
    elif 'السنة' in text and 'البربهاري' in text:
        record['SeriesName'] = 'شرح السنة للبربهاري'
        record['OriginalAuthor'] = 'البربهاري'
        record['Category'] = 'Aqeedah'
    elif 'سلم الوصول' in text or 'معارج القبول' in text:
        record['SeriesName'] = 'منظومة سلم الوصول'
        record['OriginalAuthor'] = 'حافظ حكمي'
        record['Category'] = 'Aqeedah'
    elif 'التفسير الميسر' in text:
        record['SeriesName'] = 'التفسير الميسر'
        record['Category'] = 'Other'

    return record


def main():
    """Process all messages"""
    print("\n" + "="*70)
    print("🕌 Processing All Messages")
    print("="*70 + "\n")

    # Load messages
    with open('messages_parsed.json', 'r', encoding='utf-8') as f:
        messages = json.load(f)

    print(f"📚 Processing {len(messages)} messages...\n")

    # Process each message
    results = []
    for i, msg in enumerate(messages):
        record = classify_message(msg)
        results.append(record)

        if (i + 1) % 50 == 0:
            print(f"   Processed {i + 1}/{len(messages)} messages...")

    # Save to CSV
    output_file = 'extracted_lectures_data.csv'
    fieldnames = [
        'TelegramFileName', 'Type', 'Topic', 'SeriesName', 'SubTopic',
        'Serial', 'OriginalAuthor', 'Location/Online', 'Sheikh',
        'DateInArabic', 'DateInGreg', 'ClipLength', 'Category', 'doubtsStatus'
    ]

    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Processed all {len(results)} messages")
    print(f"💾 CSV saved to: {output_file}")
    print("\nℹ️  Note: This is a basic extraction.")
    print("   For full accuracy with all fields, manual review or Claude API is recommended.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
