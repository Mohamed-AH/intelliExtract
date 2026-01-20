#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Islamic Lecture Data Extraction Script
Extracts structured data from 268 Telegram messages according to detailed extraction rules
"""

import json
import csv
import re
from typing import Dict, List, Tuple

class LectureExtractor:
    def __init__(self):
        # Schedule knowledge for online detection and series identification
        self.online_series = {
            "الأفنان الندية",
            "منظومة سلم الوصول",
            "معارج القبول"
        }

        # Series to author mapping
        self.series_authors = {
            "تأسيس الأحكام": "أحمد بن يحيى النجمي",
            "الملخص الفقهي": "صالح الفوزان",
            "الملخص شرح كتاب التوحيد": "صالح الفوزان",
            "الأفنان الندية": "زيد بن هادي المدخلي",
            "منظومة سلم الوصول": "حافظ حكمي",
            "معارج القبول": "حافظ حكمي",
            "شرح السنة": "البربهاري",
            "التفسير الميسر": "نخبة من أهل العلم"
        }

        # Series to category mapping
        self.series_categories = {
            "تأسيس الأحكام": "Hadeeth",
            "الملخص الفقهي": "Fiqh",
            "الملخص شرح كتاب التوحيد": "Aqeedah",
            "الأفنان الندية": "Fiqh",
            "منظومة سلم الوصول": "Aqeedah",
            "معارج القبول": "Aqeedah",
            "شرح السنة": "Aqeedah",
            "التفسير الميسر": "Other"
        }

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

    def extract_series_name(self, text: str, msg_type: str) -> Tuple[str, List[str]]:
        """Extract full series name with context"""
        doubts = []

        if msg_type != "Series":
            return "Not Available", doubts

        # Look for series names
        series_patterns = {
            "تأسيس الأحكام شرح عمدة الأحكام": [r"تأسيس الأحكام"],
            "الملخص شرح كتاب التوحيد": [r"الملخص شرح كتاب التوحيد", r"الملخّص في شرح كتاب التوحيد"],
            "الملخص الفقهي": [r"الملخص الفقهي", r"الملخّص الفقهي"],
            "الأفنان الندية": [r"الأفنان الندية"],
            "منظومة سلم الوصول": [r"منظومة سلم الوصول", r"سلم الوصول"],
            "معارج القبول": [r"معارج القبول"],
            "شرح السنة": [r'شرح "السنة"', r"شرح السنة"],
            "التفسير الميسر": [r"التفسير الميسر", r"التفسير الميسّر"]
        }

        for full_name, patterns in series_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return full_name, doubts

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

    def extract_location(self, text: str, series_name: str) -> Tuple[str, List[str]]:
        """Determine if Online or جامع الورود"""
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
                # Remove trailing ه‍ marker if present (it's a special character)
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

        # Extract each field
        msg_type, type_doubts = self.extract_type(text)
        all_doubts.extend(type_doubts)

        topic, topic_doubts = self.extract_topic(text, msg_type)
        all_doubts.extend(topic_doubts)

        series_name, series_doubts = self.extract_series_name(text, msg_type)
        all_doubts.extend(series_doubts)

        subtopic, subtopic_doubts = self.extract_subtopic(text, msg_type)
        all_doubts.extend(subtopic_doubts)

        serial, serial_doubts = self.extract_serial(text, msg_type)
        all_doubts.extend(serial_doubts)

        author, author_doubts = self.extract_original_author(text, series_name, msg_type)
        all_doubts.extend(author_doubts)

        location, location_doubts = self.extract_location(text, series_name)
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
            "ClipLength": clip_length,
            "Category": category,
            "doubtsStatus": doubts_status
        }

def main():
    print("Starting extraction of 268 Islamic lecture messages...")

    # Load messages
    with open('/home/user/intelliExtract/messages_parsed.json', 'r', encoding='utf-8') as f:
        messages = json.load(f)

    print(f"Loaded {len(messages)} messages")

    # Initialize extractor
    extractor = LectureExtractor()

    # Extract data from all messages
    extracted_data = []
    for i, message in enumerate(messages, 1):
        if i % 50 == 0:
            print(f"Processed {i}/{len(messages)} messages...")

        extracted = extractor.extract_message(message)
        extracted_data.append(extracted)

    print(f"Extraction complete. Processed {len(extracted_data)} messages")

    # Calculate statistics
    high_confidence = sum(1 for item in extracted_data if item["doubtsStatus"] == "none")
    accuracy_pct = (high_confidence / len(extracted_data)) * 100

    print(f"\nStatistics:")
    print(f"Total messages processed: {len(extracted_data)}")
    print(f"High confidence (no doubts): {high_confidence}")
    print(f"Accuracy: {accuracy_pct:.1f}%")

    # Write to CSV with UTF-8 BOM for Excel compatibility
    csv_file = '/home/user/intelliExtract/extracted_lectures_data.csv'
    fieldnames = [
        "TelegramFileName", "Type", "Topic", "SeriesName", "SubTopic",
        "Serial", "OriginalAuthor", "Location/Online", "Sheikh",
        "DateInArabic", "DateInGreg", "ClipLength", "Category", "doubtsStatus"
    ]

    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(extracted_data)

    print(f"\nCSV file created: {csv_file}")
    print(f"Encoding: UTF-8 with BOM (Excel compatible)")

    # Show sample of data
    print("\n" + "="*80)
    print("SAMPLE RECORDS (first 5):")
    print("="*80)
    for i, record in enumerate(extracted_data[:5], 1):
        print(f"\nRecord {i}:")
        print(f"  Type: {record['Type']}")
        print(f"  Topic: {record['Topic']}")
        print(f"  SeriesName: {record['SeriesName']}")
        print(f"  SubTopic: {record['SubTopic']}")
        print(f"  Serial: {record['Serial']}")
        print(f"  Author: {record['OriginalAuthor']}")
        print(f"  Location: {record['Location/Online']}")
        print(f"  Date: {record['DateInArabic']}")
        print(f"  Category: {record['Category']}")
        print(f"  Doubts: {record['doubtsStatus']}")

    # Show breakdown by type
    print("\n" + "="*80)
    print("BREAKDOWN BY TYPE:")
    print("="*80)
    type_counts = {}
    for record in extracted_data:
        msg_type = record['Type']
        type_counts[msg_type] = type_counts.get(msg_type, 0) + 1

    for msg_type, count in sorted(type_counts.items()):
        pct = (count / len(extracted_data)) * 100
        print(f"  {msg_type}: {count} ({pct:.1f}%)")

    # Show breakdown by category
    print("\n" + "="*80)
    print("BREAKDOWN BY CATEGORY:")
    print("="*80)
    category_counts = {}
    for record in extracted_data:
        category = record['Category']
        category_counts[category] = category_counts.get(category, 0) + 1

    for category, count in sorted(category_counts.items()):
        pct = (count / len(extracted_data)) * 100
        print(f"  {category}: {count} ({pct:.1f}%)")

    print("\n" + "="*80)
    print("Extraction completed successfully!")
    print("="*80)

if __name__ == "__main__":
    main()
