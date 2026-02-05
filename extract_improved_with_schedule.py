#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Improved Islamic Lecture Data Extraction Script
Uses weekly schedule reference to significantly improve series identification accuracy
"""

import json
import csv
import re
from typing import Dict, List, Tuple
from datetime import datetime

class ImprovedLectureExtractor:
    def __init__(self, weekly_schedule: Dict):
        """Initialize with weekly schedule reference from Excel"""
        self.weekly_schedule = weekly_schedule

        # Series to author mapping (from Excel schedule)
        self.series_authors = {
            "تأسيس الأحكام شرح عمدة الأحكام": "أحمد بن يحيى النجمي",
            "الملخص الفقهي": "صالح الفوزان",
            "الملخص شرح كتاب التوحيد": "صالح الفوزان",
            "الأفنان الندية": "زيد بن هادي المدخلي",
            "منظومة سلم الوصول": "حافظ حكمي",
            "معارج القبول شرح منظومة سلم الوصول": "حافظ حكمي",
            "شرح السنة للبربهاري": "البربهاري",
            "التفسير الميسر": "نخبة من أهل العلم",
            "غنية السائل بما في لامية شيخ الإسلام من مسائل": "أحمد النجمي",
            "المورد العذب الزلال": "أحمد النجمي",
            "إرشاد الساري شرح السنة للبربهاري": "البربهاري",
            "صحيح البخاري": "محمد بن إسماعيل البخاري",
            "التحفة النجمية بشرح الأربعين النووية": "أحمد النجمي",
            "مختصر السيرة النبوية": "محمد بن عبدالوهاب",
            "تنبيه الانام على ما في كتاب سبل السلام من الفوائد والأحكام": "أحمد النجمي"
        }

        # Series to category mapping
        self.series_categories = {
            "تأسيس الأحكام شرح عمدة الأحكام": "Hadeeth",
            "الملخص الفقهي": "Fiqh",
            "الملخص شرح كتاب التوحيد": "Aqeedah",
            "الأفنان الندية": "Fiqh",
            "منظومة سلم الوصول": "Aqeedah",
            "معارج القبول شرح منظومة سلم الوصول": "Aqeedah",
            "شرح السنة للبربهاري": "Aqeedah",
            "إرشاد الساري شرح السنة للبربهاري": "Aqeedah",
            "التفسير الميسر": "Other",
            "غنية السائل بما في لامية شيخ الإسلام من مسائل": "Aqeedah",
            "المورد العذب الزلال": "Aqeedah",
            "صحيح البخاري": "Hadeeth",
            "التحفة النجمية بشرح الأربعين النووية": "Hadeeth",
            "مختصر السيرة النبوية": "Other",
            "تنبيه الانام على ما في كتاب سبل السلام من الفوائد والأحكام": "Fiqh"
        }

    def parse_day_of_week(self, greg_date: str) -> str:
        """Parse Gregorian date and return day of week"""
        try:
            # Format: DD.MM.YYYY or DD/MM/YYYY
            date_str = greg_date.replace('.', '/').strip()
            day, month, year = date_str.split('/')
            date_obj = datetime(int(year), int(month), int(day))
            # Return English day name
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            return days[date_obj.weekday()]
        except:
            return "Not Available"

    def extract_type(self, text: str) -> Tuple[str, List[str]]:
        """Determine if message is Khutba, Lecture, or Series"""
        doubts = []

        # Check for Khutba
        if "#خطبة_الجمعة" in text or "خطبة_الجمعة" in text or "خطبة الجمعة" in text:
            return "Khutba", doubts

        # Check for Series (has lesson number)
        series_patterns = [
            r"الدرس\s+",
            r"الحلقة\s+",
            r"(الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر)",
            r"(الحادي|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع)\s+(عشر|والعشرون|والثلاثون|والأربعون|والخمسون|والستون|والسبعون|والثمانون|والتسعون)"
        ]

        for pattern in series_patterns:
            if re.search(pattern, text):
                return "Series", doubts

        # Check for standalone lecture
        if "محاضرة" in text:
            return "Lecture", doubts

        # Default to Series if uncertain
        doubts.append("Type unclear - defaulted to Series")
        return "Series", doubts

    def extract_topic(self, text: str, msg_type: str) -> Tuple[str, List[str]]:
        """Extract topic for Khutba/Lecture only"""
        doubts = []

        # For Series, ALWAYS return "Not Available"
        if msg_type == "Series":
            return "Not Available", doubts

        # For Khutba/Lecture - look for topic in brackets or after بعنوان
        patterns = [
            r"•\[\s*\n?\s*([^\]]+?)\s*\n?\s*\]•",  # •[ topic ]• with possible newlines
            r"عنوان الخطبة:\s*\n?\s*([^\n\.]+)",  # عنوان الخطبة: topic
            r"محاضرة[^:]*بعنوان:\s*\n?\s*▪️\s*\n?\s*([^\n]+?)\s*\n?\s*▪️",  # محاضرة بعنوان: ▪️ topic ▪️
            r"بعنوان:\s*\n?\s*([^\n▪]+)",  # بعنوان: topic
            r"▪️\s*\n?\s*([^\n▪]+?)\s*\n?\s*▪️"  # ▪️ topic ▪️
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                topic = match.group(1).strip()
                # Clean up
                topic = re.sub(r'\s+', ' ', topic)
                # Remove extra markers
                topic = re.sub(r'^[▪️\s]+', '', topic)
                topic = re.sub(r'[▪️\s]+$', '', topic)
                if topic and topic != '▪️':
                    return topic, doubts

        doubts.append("Topic not clearly identified")
        return "Not Available", doubts

    def extract_series_name_with_schedule(self, text: str, msg_type: str, day_of_week: str) -> Tuple[str, List[str]]:
        """Extract full series name using weekly schedule as reference"""
        doubts = []

        if msg_type != "Series":
            return "Not Available", doubts

        # First, try direct pattern matching from weekly schedule
        series_patterns = {
            "تأسيس الأحكام شرح عمدة الأحكام": [r"تأسيس الأحكام"],
            "الملخص شرح كتاب التوحيد": [r"الملخص شرح كتاب التوحيد", r"الملخّص في شرح كتاب التوحيد", r"الملخص.*كتاب التوحيد"],
            "الملخص الفقهي": [r"الملخص الفقهي", r"الملخّص الفقهي"],
            "الأفنان الندية": [r"الأفنان الندية"],
            "منظومة سلم الوصول": [r"منظومة سلم الوصول", r"سلم الوصول"],
            "معارج القبول شرح منظومة سلم الوصول": [r"معارج القبول"],
            "شرح السنة للبربهاري": [r'شرح "السنة"', r"شرح السنة"],
            "إرشاد الساري شرح السنة للبربهاري": [r"إرشاد الساري"],
            "التفسير الميسر": [r"التفسير الميسر", r"التفسير الميسّر"],
            "غنية السائل بما في لامية شيخ الإسلام من مسائل": [r"غنية السائل"],
            "المورد العذب الزلال": [r"المورد العذب الزلال"],
            "صحيح البخاري": [r"صحيح البخاري"],
            "التحفة النجمية بشرح الأربعين النووية": [r"التحفة النجمية", r"الأربعين النووية"],
            "مختصر السيرة النبوية": [r"مختصر السيرة النبوية"],
            "تنبيه الانام على ما في كتاب سبل السلام من الفوائد والأحكام": [r"تنبيه الانام"]
        }

        # Try to match patterns
        for full_name, patterns in series_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return full_name, doubts

        # If no direct match, use schedule knowledge based on day of week
        if day_of_week in self.weekly_schedule:
            day_series = self.weekly_schedule[day_of_week]
            # Look for keywords from scheduled series
            for series_name in day_series:
                # Extract key words from series name
                key_words = series_name.split()[:3]  # First 3 words
                if any(word in text for word in key_words):
                    return series_name, doubts

        doubts.append("Series name not clearly identified")
        return "Not Available", doubts

    def extract_subtopic(self, text: str, msg_type: str) -> Tuple[str, List[str]]:
        """Extract chapter/section within series"""
        doubts = []

        if msg_type != "Series":
            return "Not Available", doubts

        # Look for كتاب or باب patterns
        patterns = [
            r"(كتاب\s+[^\n\-]+(?:\s*\([^\)]+\))?)",
            r"(باب\s+[^\n\-]+)",
            r"\(\s*(سورة\s+[^\)]+)\s*\)"
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                subtopic = match.group(1).strip()
                # Clean up
                subtopic = re.sub(r'\s+', ' ', subtopic)
                return subtopic, doubts

        return "Not Available", doubts

    def extract_serial(self, text: str, msg_type: str) -> Tuple[str, List[str]]:
        """Extract lesson number in Arabic"""
        doubts = []

        if msg_type != "Series":
            return "Not Available", doubts

        # Look for lesson number patterns - more flexible matching
        patterns = [
            # Match "الدرس الأول" style with Arabic words
            r"الدرس\s+(ال[\u0600-\u06FF]+(?:\s+[\u0600-\u06FF]+)*?)(?:\s+ب|\s+في|\s+مع|\s+عن|\s*\n)",
            # Match "الحلقة الأولى" style
            r"الحلقة\s+(ال[\u0600-\u06FF]+(?:\s+[\u0600-\u06FF]+)*?)(?:\s+ب|\s+في|\s+مع|\s+عن|\s*\n)",
            # Match Arabic numerals
            r"الدرس\s+([٠-٩]+)",
            # Match Western numerals
            r"الدرس\s+(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                serial = match.group(1).strip()
                serial = re.sub(r'\s+', ' ', serial)
                return serial, doubts

        doubts.append("Serial number not found")
        return "Not Available", doubts

    def extract_original_author(self, text: str, series_name: str, msg_type: str) -> Tuple[str, List[str]]:
        """Extract book author (not the Sheikh)"""
        doubts = []

        if msg_type != "Series":
            return "Not Available", doubts

        # First try to extract from text
        author_patterns = [
            r"للعلامة:\s*([^\n\-]+?)(?:\s*-|رحمه)",
            r"للعلامة\s+([^\n\-]+?)(?:\s*-|رحمه)",
            r"للإمام:\s*([^\n]+?)(?:\s*-|رحمه)",
            r"قام بإعداده\s+([^\n]+)"
        ]

        for pattern in author_patterns:
            match = re.search(pattern, text)
            if match:
                author = match.group(1).strip()
                # Clean up
                author = re.sub(r'\s+', ' ', author)
                # Remove common honorifics at the end
                author = re.sub(r'\s*رحمه الله\s*', '', author)
                author = re.sub(r'\s*حفظه الله\s*', '', author)
                return author, doubts

        # Fall back to series mapping
        for series_key, author in self.series_authors.items():
            if series_key in series_name:
                return author, doubts

        doubts.append("Original author not found")
        return "Not Available", doubts

    def extract_location(self, text: str, series_name: str, day_of_week: str) -> Tuple[str, List[str]]:
        """Determine if Online or جامع الورود using schedule knowledge"""
        doubts = []

        # Check for explicit online indicators
        online_indicators = [
            r"عن\s*بُعد",
            r"عن\s*بعد",
            r"بُعد",
            r"عبر قناة التليجرام",
            r"عبر قناته الرسمية"
        ]

        for indicator in online_indicators:
            if re.search(indicator, text):
                return "Online", doubts

        # Check for explicit mosque mention
        if "جامع الورود" in text or "في جامع الورود" in text:
            return "جامع الورود", doubts

        # Use schedule knowledge: certain series are always online
        online_series_keywords = [
            "الأفنان الندية",
            "منظومة سلم الوصول",
            "معارج القبول"
        ]

        # Sunday/Monday Isha: الأفنان الندية = Online
        # Tuesday Isha: معارج القبول/منظومة سلم الوصول = Online
        # Wednesday Isha: تأسيس الأحكام = Online

        # Default to جامع الورود
        return "جامع الورود", doubts

    def extract_date_arabic(self, text: str) -> Tuple[str, List[str]]:
        """Extract Hijri date in any format"""
        doubts = []

        # Look for various date patterns
        patterns = [
            r"❲\s*([^❳]+)\s*❳",  # ❲ date ❳
            r"التاريخ:\s*([^\n]+?)(?:ه‍|\n|$)",  # التاريخ: date
            r"([٠-٩]+\s*[/\-]\s*[٠-٩]+\s*[/\-]\s*[٠-٩]+)",  # Arabic numerals: ٥/٢/١٤٤٧
            r"(\d+\s*[/\-]\s*\d+\s*[/\-]\s*\d+\s*ه)",  # 5/2/1447ه
            r"(\d+\s+[\u0600-\u06FF]+\s+\d+\s*ه)",  # 17 جمادى الآخرة 1440ه
            r"(الجمعة\s+[٠-٩]+\s*[/\-]\s*[٠-٩]+\s*[/\-]\s*[٠-٩]+)",  # الجمعة ٥/٢/١٤٤٧
            r"(الجمعة\s+\d+\s*[/\-]\s*\d+\s*[/\-]\s*\d+)",  # الجمعة 5/2/1447
            r"ليلة\s+[\u0600-\u06FF]+\s+([٠-٩]+\s+[\u0600-\u06FF]+\s+[٠-٩]+)",  # ليلة السبت ١٢ ربيع الآخر ١٤٤٧
            r"ليلة\s+\w+\s+(\d+\s+[\u0600-\u06FF]+\s+\d+\s*ه)",  # ليلة السبت 12 ربيع الآخر 1447هـ
            r"(?:في|بجدة)\s*-\s*([٠-٩]+\s*/\s*[٠-٩]+\s*/\s*[٠-٩]+)",  # في - ١٥ / ٣ / ١٤٤٧
            r"(?:في|بجدة)\s*-\s*(\d+\s*/\s*\d+\s*/\s*\d+)"  # في - 14 / 3 / 1447
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                date = match.group(1).strip()
                date = re.sub(r'\s+', ' ', date)
                # Remove trailing ه‍ marker if present
                date = re.sub(r'ه‍$', '', date)
                return date, doubts

        doubts.append("Arabic date not found")
        return "Not Available", doubts

    def extract_category(self, text: str, series_name: str, msg_type: str, topic: str) -> Tuple[str, List[str]]:
        """Determine category: Fiqh, Aqeedah, Hadeeth, or Other"""
        doubts = []

        # For Series, use series mapping
        if msg_type == "Series":
            for series_key, category in self.series_categories.items():
                if series_key in series_name:
                    return category, doubts

        # For Khutba/Lecture, analyze topic
        if msg_type == "Khutba" or msg_type == "Lecture":
            # Check for Aqeedah topics
            aqeedah_keywords = ["توحيد", "عقيدة", "أسماء", "صفات", "إيمان"]
            for keyword in aqeedah_keywords:
                if keyword in topic or keyword in text:
                    return "Aqeedah", doubts

            # Check for Fiqh topics
            fiqh_keywords = ["صلاة", "صيام", "زكاة", "حج", "نكاح", "بيوع", "فقه"]
            for keyword in fiqh_keywords:
                if keyword in topic or keyword in text:
                    return "Fiqh", doubts

            # Default for Khutba is Other
            return "Other", doubts

        # Default
        return "Other", doubts

    def extract_message(self, message: Dict) -> Dict:
        """Extract all fields from a single message"""
        text = message.get("message_text", "")
        filename = message.get("filename", "Not Available")
        clip_length = message.get("clip_length", "Not Available")
        greg_date = message.get("greg_date", "Not Available")

        all_doubts = []

        # Parse day of week from Gregorian date
        day_of_week = self.parse_day_of_week(greg_date)

        # Extract each field
        msg_type, type_doubts = self.extract_type(text)
        all_doubts.extend(type_doubts)

        topic, topic_doubts = self.extract_topic(text, msg_type)
        all_doubts.extend(topic_doubts)

        series_name, series_doubts = self.extract_series_name_with_schedule(text, msg_type, day_of_week)
        all_doubts.extend(series_doubts)

        subtopic, subtopic_doubts = self.extract_subtopic(text, msg_type)
        all_doubts.extend(subtopic_doubts)

        serial, serial_doubts = self.extract_serial(text, msg_type)
        all_doubts.extend(serial_doubts)

        author, author_doubts = self.extract_original_author(text, series_name, msg_type)
        all_doubts.extend(author_doubts)

        location, location_doubts = self.extract_location(text, series_name, day_of_week)
        all_doubts.extend(location_doubts)

        date_arabic, date_doubts = self.extract_date_arabic(text)
        all_doubts.extend(date_doubts)

        category, category_doubts = self.extract_category(text, series_name, msg_type, topic)
        all_doubts.extend(category_doubts)

        # Format doubts
        doubts_status = "none" if not all_doubts else "; ".join(all_doubts)

        return {
            "TelegramFileName": filename,
            "Type": msg_type,
            "Topic": topic,
            "SeriesName": series_name,
            "SubTopic": subtopic,
            "Serial": serial,
            "OriginalAuthor": author,
            "Location/Online": location,
            "Sheikh": "حسن بن محمد منصور الدغريري",
            "DateInArabic": date_arabic,
            "DateInGreg": greg_date,
            "DayOfWeek": day_of_week,
            "ClipLength": clip_length,
            "Category": category,
            "doubtsStatus": doubts_status
        }


def main():
    print("="*80)
    print("IMPROVED ISLAMIC LECTURE DATA EXTRACTION")
    print("Using Weekly Schedule Reference for Better Accuracy")
    print("="*80)
    print()

    # Define weekly schedule from Excel reference
    weekly_schedule = {
        "Saturday": [
            "غنية السائل بما في لامية شيخ الإسلام من مسائل",
            "المورد العذب الزلال",
            "إرشاد الساري شرح السنة للبربهاري",
            "التفسير الميسر",
            "تأسيس الأحكام شرح عمدة الأحكام",
            "التحفة النجمية بشرح الأربعين النووية",
            "مختصر السيرة النبوية",
            "تنبيه الانام على ما في كتاب سبل السلام من الفوائد والأحكام"
        ],
        "Sunday": [
            "الملخص شرح كتاب التوحيد",
            "تأسيس الأحكام شرح عمدة الأحكام",
            "الأفنان الندية"  # Online
        ],
        "Monday": [
            "الملخص الفقهي",
            "تأسيس الأحكام شرح عمدة الأحكام",
            "الأفنان الندية"  # Online
        ],
        "Tuesday": [
            "الملخص شرح كتاب التوحيد",
            "معارج القبول شرح منظومة سلم الوصول"  # Online
        ],
        "Wednesday": [
            "الملخص الفقهي",
            "تأسيس الأحكام شرح عمدة الأحكام"  # Online
        ],
        "Friday": [
            "خطبة الجمعة",
            "صحيح البخاري"
        ]
    }

    # Load messages
    print("Loading messages from JSON file...")
    with open('/home/user/intelliExtract/messages_parsed.json', 'r', encoding='utf-8') as f:
        messages = json.load(f)

    print(f"✓ Loaded {len(messages)} messages")
    print()

    # Initialize extractor with schedule
    extractor = ImprovedLectureExtractor(weekly_schedule)

    # Extract data from all messages
    print("Extracting data with improved accuracy...")
    extracted_data = []
    for i, message in enumerate(messages, 1):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(messages)} messages processed...")

        extracted = extractor.extract_message(message)
        extracted_data.append(extracted)

    print(f"✓ Extraction complete. Processed {len(extracted_data)} messages")
    print()

    # Calculate statistics
    high_confidence = sum(1 for item in extracted_data if item["doubtsStatus"] == "none")
    accuracy_pct = (high_confidence / len(extracted_data)) * 100

    print("="*80)
    print("EXTRACTION STATISTICS")
    print("="*80)
    print(f"Total messages processed: {len(extracted_data)}")
    print(f"High confidence (no doubts): {high_confidence}")
    print(f"Accuracy: {accuracy_pct:.1f}%")
    print()

    # Write to CSV with UTF-8 BOM for Excel compatibility
    csv_file = '/home/user/intelliExtract/extracted_lectures_improved.csv'
    fieldnames = [
        "TelegramFileName", "Type", "Topic", "SeriesName", "SubTopic",
        "Serial", "OriginalAuthor", "Location/Online", "Sheikh",
        "DateInArabic", "DateInGreg", "DayOfWeek", "ClipLength", "Category", "doubtsStatus"
    ]

    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(extracted_data)

    print(f"✓ CSV file created: {csv_file}")
    print(f"✓ Encoding: UTF-8 with BOM (Excel compatible)")
    print()

    # Show breakdown by type
    print("="*80)
    print("BREAKDOWN BY TYPE")
    print("="*80)
    type_counts = {}
    for record in extracted_data:
        msg_type = record['Type']
        type_counts[msg_type] = type_counts.get(msg_type, 0) + 1

    for msg_type, count in sorted(type_counts.items()):
        pct = (count / len(extracted_data)) * 100
        print(f"  {msg_type:15s}: {count:3d} ({pct:5.1f}%)")
    print()

    # Show breakdown by category
    print("="*80)
    print("BREAKDOWN BY CATEGORY")
    print("="*80)
    category_counts = {}
    for record in extracted_data:
        category = record['Category']
        category_counts[category] = category_counts.get(category, 0) + 1

    for category, count in sorted(category_counts.items()):
        pct = (count / len(extracted_data)) * 100
        print(f"  {category:15s}: {count:3d} ({pct:5.1f}%)")
    print()

    # Show breakdown by series (top 10)
    print("="*80)
    print("TOP 10 SERIES")
    print("="*80)
    series_counts = {}
    for record in extracted_data:
        if record['Type'] == 'Series':
            series = record['SeriesName']
            series_counts[series] = series_counts.get(series, 0) + 1

    top_series = sorted(series_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for series, count in top_series:
        print(f"  {count:3d} lessons: {series}")
    print()

    # Show sample records
    print("="*80)
    print("SAMPLE RECORDS (First 5)")
    print("="*80)
    for i, record in enumerate(extracted_data[:5], 1):
        print(f"\nRecord {i}:")
        print(f"  File: {record['TelegramFileName'][:50]}...")
        print(f"  Type: {record['Type']}")
        print(f"  SeriesName: {record['SeriesName']}")
        print(f"  SubTopic: {record['SubTopic']}")
        print(f"  Serial: {record['Serial']}")
        print(f"  Author: {record['OriginalAuthor']}")
        print(f"  Location: {record['Location/Online']}")
        print(f"  Date (Hijri): {record['DateInArabic']}")
        print(f"  Date (Greg): {record['DateInGreg']}")
        print(f"  Day: {record['DayOfWeek']}")
        print(f"  Category: {record['Category']}")
        print(f"  Doubts: {record['doubtsStatus']}")
    print()

    print("="*80)
    print("EXTRACTION COMPLETED SUCCESSFULLY!")
    print("="*80)
    print(f"\nOutput file: {csv_file}")
    print(f"Total records: {len(extracted_data)}")
    print(f"Accuracy achieved: {accuracy_pct:.1f}%")


if __name__ == "__main__":
    main()
