# Archive Messages Extraction Summary

## Overview

This extraction processes historical lessons from the Sheikh's archive, exported as `archive_messages.html`. These are well-organized lessons from previous years (2022-2023), arranged by series with clear structure.

## Results

### Extraction Statistics

- **Total Messages**: 66 audio lessons
- **✅ All Matched**: 100% (66/66)
- **Series Identified**: 7 distinct series
- **Category**: All Fiqh (Islamic Jurisprudence)
- **Period Covered**: 2020-2023 (Hijri: 1441-1444)

### Format Characteristics

Unlike the recent Telegram messages, archive messages have:
- **Well-structured format**: Each lesson clearly labeled with series name
- **Sequential numbering**: Lessons numbered 1, 2, 3... within each series
- **Complete metadata**: Hijri dates, clip lengths, lesson numbers all present
- **Hashtag organization**: Series indicated with hashtags (#كتاب_الصيام, #الأفنان_الندية, etc.)
- **Consistent authors**: Original book authors clearly mentioned

## Series Breakdown

### 1. الممتع شرح زاد المستقنع (15 lessons)
- **Author**: محمد بن صالح العثيمين
- **Category**: Fiqh
- **Location**: جامع الورود
- **Period**: Ramadan 1444 (March-April 2023)
- **Most lessons**: كتاب الصيام (Fasting chapter)

### 2. تأسيس الأحكام شرح عمدة الأحكام (12 lessons)
- **Author**: أحمد بن يحيى النجمي
- **Category**: Hadeeth/Fiqh
- **Location**: جامع الورود
- **Lessons**: Various chapters including Salah, Fasting

### 3. تنبيه الأنام على ما في كتاب سبل السلام من الفوائد والأحكام (12 lessons)
- **Author**: محمد بن صالح العثيمين
- **Category**: Fiqh
- **Location**: جامع الورود
- **Period**: Ramadan 1443 (April 2022)
- **Chapter**: كتاب الصيام (Lessons 1-12)

### 4. الأفنان الندية شرح السبل السوية (10 lessons)
- **Author**: زيد بن هادي المدخلي
- **Category**: Fiqh
- **Location**: جامع الورود
- **Period**: Sha'ban 1444 (February-March 2023)
- **Chapter**: كتاب الصيام (Fasting)

### 5. شرح كتاب الفقه الميسر (6 lessons)
- **Author**: مجموعة من أهل العلم
- **Category**: Fiqh
- **Location**: جامع الورود
- **Complete series**: Lessons 1-6

### 6. كتاب آداب المشي إلى الصلاة (6 lessons)
- **Author**: عبد العزيز بن باز
- **Category**: Fiqh
- **Location**: جامع الورود
- **Period**: Sha'ban-Ramadan 1441 (April-May 2020)
- **Complete series**: Lessons 1-6 (including final lesson)

### 7. الملخص الفقهي (5 lessons)
- **Author**: صالح الفوزان
- **Category**: Fiqh
- **Location**: جامع الورود
- **Lessons**: 5 lessons from various chapters

## Key Observations

1. **Ramadan Focus**: Many series are specifically taught during Ramadan (كتاب الصيام - Book of Fasting)

2. **Complete Mini-Series**: Several complete short series included:
   - كتاب آداب المشي إلى الصلاة: 6 lessons (complete)
   - شرح كتاب الفقه الميسر: 6 lessons (complete)
   - تنبيه الأنام (Fasting chapter): 12 lessons (complete)

3. **Predominantly Fiqh**: All 66 lessons are Fiqh-related, covering:
   - Fasting (الصيام) - majority
   - Prayer (الصلاة)
   - Various jurisprudence topics

4. **Date Range**: Covers 3-4 years (1441-1444 Hijri / 2020-2023 Gregorian)

5. **Perfect Extraction**: 100% match rate due to well-structured original formatting

## Files Generated

1. **parse_archive_messages.py** - HTML parser extracting structured data
2. **archive_messages_parsed.json** - 66 parsed messages with all metadata
3. **extract_archive_to_csv.py** - Converter to standard CSV format
4. **archive_lectures_extracted.csv** - Final CSV output in standard format

## CSV Format

Standard extraction format with columns:
- TelegramFileName
- Type (all "Series")
- SeriesName
- Serial (lesson number in Arabic)
- OriginalAuthor
- Location/Online (all جامع الورود)
- Sheikh (حسن بن محمد منصور الدغريري)
- DateInArabic (Hijri)
- DateInGreg (Gregorian)
- ClipLength
- Category (all Fiqh)

## Technical Notes

- **Hijri Date Conversion**: Used hijri-converter library for accurate Hijri-to-Gregorian conversion
- **Arabic Numeral Handling**: Properly extracted and preserved Arabic numerals (٠-٩)
- **Series Detection**: Pattern matching on hashtags and full book titles
- **Author Mapping**: Automatic author assignment based on known book-author pairs
- **Category Classification**: Keyword-based categorization (all Fiqh in this archive)

## Comparison with Recent Extractions

| Aspect | Archive Messages | Recent Messages (Oct 2025 - Feb 2026) |
|--------|------------------|--------------------------------------|
| Match Rate | 100% (66/66) | 84-86% |
| Structure | Highly organized by series | Mixed daily uploads |
| Metadata | Complete & explicit | Requires parsing from text |
| Period | 2020-2023 | Current ongoing |
| Series Count | 7 complete/partial series | 15 active series |

The archive represents historical teaching material that has been organized retroactively, while recent messages are ongoing daily uploads with more varied content including announcements and special events.
