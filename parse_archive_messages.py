#!/usr/bin/env python3
"""
Parse archive_messages.html to extract lessons organized by series.
These are historical lessons from previous years, well-organized with:
- Series names in hashtags
- Sequential lesson numbers
- Hijri dates
- Clip lengths
"""

from bs4 import BeautifulSoup
import json
import re
from hijri_converter import Hijri, Gregorian

# Arabic number conversion
ARABIC_TO_ENGLISH = {
    '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
    '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
}

# Hijri months mapping
HIJRI_MONTHS = {
    'محرم': 1, 'صفر': 2, 'ربيع الأول': 3, 'ربيع الآخر': 4,
    'جمادى الأولى': 5, 'جمادى الآخرة': 6, 'رجب': 7, 'شعبان': 8,
    'رمضان': 9, 'شوال': 10, 'ذو القعدة': 11, 'ذو الحجة': 12
}

def arabic_to_english_numbers(text):
    """Convert Arabic numerals to English"""
    if not text:
        return text
    result = text
    for ar, en in ARABIC_TO_ENGLISH.items():
        result = result.replace(ar, en)
    return result

def extract_hijri_date(text):
    """Extract Hijri date from text like '١ رمضان ١٤٤٣هـ'"""
    if not text:
        return None, None

    # Pattern: day month year
    # e.g., "١ رمضان ١٤٤٣هـ" or "٢٥ رمضان ١٤٤٣"
    pattern = r'([\d\u0660-\u0669]+)\s+([\u0600-\u06FF\s]+?)\s+([\d\u0660-\u0669]+)\s*هـ?'
    match = re.search(pattern, text)

    if match:
        day_ar = match.group(1).strip()
        month_name = match.group(2).strip()
        year_ar = match.group(3).strip()

        # Convert Arabic numerals to English
        day = int(arabic_to_english_numbers(day_ar))
        year = int(arabic_to_english_numbers(year_ar))

        # Find month number
        month = None
        for month_arabic, month_num in HIJRI_MONTHS.items():
            if month_arabic in month_name:
                month = month_num
                break

        if month:
            return f"{day_ar} {month_name} {year_ar}هـ", (day, month, year)

    return None, None

def hijri_to_gregorian(day, month, year):
    """Convert Hijri date to Gregorian"""
    try:
        hijri_date = Hijri(year, month, day)
        greg_date = hijri_date.to_gregorian()
        return f"{greg_date.day:02d}/{greg_date.month:02d}/{greg_date.year}"
    except:
        return "N/A"

def extract_series_name(text):
    """Extract series name from text"""
    # Look for main book titles (longer patterns first for better matching)
    series_patterns = [
        (r'تنبيه الأنام على مافي كتاب سبل السلام من الفوائد والأحكام',
         'تنبيه الأنام على ما في كتاب سبل السلام من الفوائد والأحكام'),
        (r'تنبيه الانام على ما في كتاب سبل السلام',
         'تنبيه الأنام على ما في كتاب سبل السلام من الفوائد والأحكام'),
        (r'الممتع شرح زاد المستقنع', 'الممتع شرح زاد المستقنع'),
        (r'الممتع_شرح_زاد_المستقنع', 'الممتع شرح زاد المستقنع'),
        (r'آداب المشي إلى الصلاة', 'كتاب آداب المشي إلى الصلاة'),
        (r'آداب_المشي_إلى_الصلاة', 'كتاب آداب المشي إلى الصلاة'),
        (r'الأفنان الندية شرح السبل السوية', 'الأفنان الندية شرح السبل السوية'),
        (r'الأفنان الندية', 'الأفنان الندية'),
        (r'الأفنان_الندية', 'الأفنان الندية'),
        (r'المورد العذب الزلال', 'المورد العذب الزلال'),
        (r'إرشاد الساري', 'إرشاد الساري شرح السنة للبربهاري'),
        (r'معارج القبول', 'معارج القبول شرح منظومة سلم الوصول'),
        (r'الملخص الفقهي', 'الملخص الفقهي'),
        (r'كتاب الفقه الميسر', 'شرح كتاب الفقه الميسر'),
        (r'تأسيس الأحكام', 'تأسيس الأحكام شرح عمدة الأحكام'),
        (r'صحيح البخاري', 'صحيح البخاري'),
        (r'التفسير الميسر', 'التفسير الميسر'),
        (r'الملخص شرح كتاب التوحيد', 'الملخص شرح كتاب التوحيد'),
        (r'مختصر السيرة النبوية', 'مختصر السيرة النبوية'),
        (r'التحفة النجمية', 'التحفة النجمية بشرح الأربعين النووية'),
        (r'غنية السائل', 'غنية السائل بما في لامية شيخ الإسلام من مسائل'),
    ]

    for pattern, standardized_name in series_patterns:
        if re.search(pattern, text):
            return standardized_name

    # Look for hashtags as series indicators
    hashtag_match = re.search(r'#([\u0600-\u06FF_]+)', text)
    if hashtag_match:
        hashtag = hashtag_match.group(1).replace('_', ' ')
        # Clean up and return meaningful hashtags
        if any(word in hashtag for word in ['كتاب', 'شرح', 'الأحكام', 'الفقه']):
            return hashtag

    return None

def extract_lesson_number(text):
    """Extract lesson number from text like 'الدرس رقم ١' or 'الدرس الأول' or '{01}'"""
    # Pattern 1: "الدرس رقم ١"
    pattern1 = r'الدرس رقم\s*([\d\u0660-\u0669]+)'
    match1 = re.search(pattern1, text)
    if match1:
        return match1.group(1)

    # Pattern 2: "{01}" or "المجلس {02}" format
    pattern2 = r'\{(\d+)\}'
    match2 = re.search(pattern2, text)
    if match2:
        # Convert to Arabic numerals
        english_num = match2.group(1)
        arabic_num = ''.join(ARABIC_TO_ENGLISH.get(c, c) for c in str(int(english_num)))
        # Convert back to Arabic
        reverse_map = {v: k for k, v in ARABIC_TO_ENGLISH.items()}
        return ''.join(reverse_map.get(c, c) for c in english_num)

    # Pattern 3: "الدرس الأول" (ordinal)
    ordinals = {
        'الأول': '١', 'الثاني': '٢', 'الثالث': '٣', 'الرابع': '٤',
        'الخامس': '٥', 'السادس': '٦', 'السابع': '٧', 'الثامن': '٨',
        'التاسع': '٩', 'العاشر': '١٠'
    }

    for ordinal, number in ordinals.items():
        if ordinal in text:
            return number

    return None

def determine_author(series_name):
    """Determine original author based on series name"""
    if not series_name:
        return 'Not Available'

    author_map = {
        'تنبيه الأنام': 'محمد بن صالح العثيمين',
        'تأسيس الأحكام': 'أحمد بن يحيى النجمي',
        'الملخص الفقهي': 'صالح الفوزان',
        'الملخص شرح كتاب التوحيد': 'صالح الفوزان',
        'صحيح البخاري': 'محمد بن إسماعيل البخاري',
        'المورد العذب': 'أحمد النجمي',
        'الأفنان الندية': 'زيد بن هادي المدخلي',
        'الأفنان': 'زيد بن هادي المدخلي',
        'معارج القبول': 'حافظ حكمي',
        'إرشاد الساري': 'أحمد النجمي',
        'التفسير الميسر': 'نخبة من أهل العلم',
        'مختصر السيرة': 'محمد بن عبد الوهاب',
        'التحفة النجمية': 'أحمد النجمي',
        'غنية السائل': 'ابن القيم',
        'الفقه الميسر': 'مجموعة من أهل العلم',
        'الممتع': 'محمد بن صالح العثيمين',
        'آداب المشي': 'عبد العزيز بن باز',
    }

    for key, author in author_map.items():
        if key in series_name:
            return author

    return 'Not Available'

def determine_category(series_name):
    """Determine category based on series name"""
    if not series_name:
        return 'Other'

    fiqh_keywords = ['فقه', 'أحكام', 'سبل السلام', 'الملخص الفقهي', 'الأفنان', 'الممتع', 'زاد المستقنع', 'آداب المشي', 'صلاة']
    aqeedah_keywords = ['توحيد', 'معارج القبول', 'المورد العذب', 'إرشاد الساري', 'التحفة']
    hadeeth_keywords = ['بخاري', 'تأسيس الأحكام']
    seerah_keywords = ['سيرة']
    tafseer_keywords = ['تفسير']

    series_lower = series_name.lower()

    if any(kw in series_lower for kw in fiqh_keywords):
        return 'Fiqh'
    elif any(kw in series_lower for kw in aqeedah_keywords):
        return 'Aqeedah'
    elif any(kw in series_lower for kw in hadeeth_keywords):
        return 'Hadeeth'
    elif any(kw in series_lower for kw in seerah_keywords):
        return 'Seerah'
    elif any(kw in series_lower for kw in tafseer_keywords):
        return 'Tafseer'

    return 'Other'

def parse_archive_messages(html_file):
    """Parse archive HTML export and extract structured data"""

    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    messages = []
    all_message_divs = soup.find_all('div', class_='message')

    print(f"Found {len(all_message_divs)} total message divs")

    audio_count = 0
    for msg_div in all_message_divs:
        # Look for audio files
        audio_tags = msg_div.find_all('a', class_='media_audio_file')

        for audio_tag in audio_tags:
            filename = audio_tag.get('href', '')

            # Only process actual audio files (not links)
            if filename and ('files/' in filename or '.m4a' in filename or '.mp3' in filename):
                audio_count += 1

                # Extract filename
                audio_filename = filename.split('/')[-1] if '/' in filename else filename

                # Extract clip length (duration)
                clip_length = 'N/A'
                status_div = audio_tag.find('div', class_='status details')
                if status_div:
                    clip_length = status_div.get_text(strip=True)

                # Extract message text
                text_div = msg_div.find('div', class_='text')
                message_text = text_div.get_text(strip=True) if text_div else ''

                # Extract series name
                series_name = extract_series_name(message_text)

                # Extract lesson number
                lesson_number = extract_lesson_number(message_text)

                # Extract Hijri date
                hijri_date_text, hijri_tuple = extract_hijri_date(message_text)

                # Convert to Gregorian
                greg_date = 'N/A'
                if hijri_tuple:
                    day, month, year = hijri_tuple
                    greg_date = hijri_to_gregorian(day, month, year)

                # Determine author and category
                author = determine_author(series_name) if series_name else 'Not Available'
                category = determine_category(series_name) if series_name else 'Other'

                messages.append({
                    'filename': audio_filename,
                    'series_name': series_name or 'Not Available',
                    'lesson_number': lesson_number or 'Not Available',
                    'hijri_date': hijri_date_text or 'Not Available',
                    'greg_date': greg_date,
                    'clip_length': clip_length,
                    'author': author,
                    'category': category,
                    'message_text': message_text
                })

    print(f"Extracted {audio_count} audio messages")
    return messages

def main():
    input_file = 'archive_messages.html'
    output_json = 'archive_messages_parsed.json'

    print("=" * 80)
    print("PARSING ARCHIVE MESSAGES")
    print("=" * 80)
    print()

    messages = parse_archive_messages(input_file)

    # Save to JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

    print()
    print(f"✅ Saved {len(messages)} messages to {output_json}")
    print()

    # Show sample
    if messages:
        print("Sample messages:")
        for i, msg in enumerate(messages[:3], 1):
            print(f"\n{i}. {msg['filename']}")
            print(f"   Series: {msg['series_name']}")
            print(f"   Lesson: {msg['lesson_number']}")
            print(f"   Hijri: {msg['hijri_date']}")
            print(f"   Greg: {msg['greg_date']}")
            print(f"   Duration: {msg['clip_length']}")

    # Show series summary
    print("\n" + "=" * 80)
    print("SERIES SUMMARY")
    print("=" * 80)

    from collections import defaultdict
    series_count = defaultdict(int)
    for msg in messages:
        series_count[msg['series_name']] += 1

    for series, count in sorted(series_count.items(), key=lambda x: x[1], reverse=True):
        print(f"   {series[:50]:50s} | {count:3d} lessons")

if __name__ == '__main__':
    main()
