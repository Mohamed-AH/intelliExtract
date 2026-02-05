# IntelliExtract - Islamic Lecture Data Extraction Tool

🕌 Intelligent data extraction from Sheikh Hassan Al-Daghriri's Telegram channel using Claude API

## Overview

This tool automatically extracts structured data from Telegram messages containing Islamic lectures, series lessons, and Friday sermons (Khutbas). It uses Claude AI to intelligently parse Arabic text and classify content according to detailed extraction rules.

### Key Findings

**From 268 Telegram messages, we identified:**
- ✅ **15 unique series** (including Friday Khutba as separate series)
- 📚 **231 lessons matched to series** (86.2% accuracy!) + 10 Khutbas
- 🎓 **ALL series are taught 2-7 times per week** (intensive schedule!)
- 📍 **216 masjid lessons** (81.5%) + 49 online (18.5%)
- ❓ **27 messages unmatched** (mostly Thursday sessions and announcements)

**Top Series (Manual-Style Extraction):**
1. تأسيس الأحكام شرح عمدة الأحكام (55 lessons, masjid)
2. الملخص شرح كتاب التوحيد (31 lessons, masjid)
3. الملخص الفقهي (31 lessons, masjid)
4. الأفنان الندية (29 lessons, online)

See `lectures_manual_sorted_by_series.csv` for the complete organized dataset.

## Features

- ✅ Parses HTML exports from Telegram
- 🤖 Uses Claude API for intelligent pattern recognition
- 📊 Extracts 14 data points per message
- 📝 Outputs clean CSV format
- 🎯 Tracks confidence levels with "doubts" field
- 🌐 Handles Arabic text and Hijri dates

## Setup

### Prerequisites

- Python 3.8 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Or on Windows:
```cmd
set ANTHROPIC_API_KEY=your-api-key-here
```

## Usage

### Quick Start - View Organized Results

The repository includes pre-processed data organized by series:

```bash
# 🏆 BEST: Manual-style extraction sorted by series (86.2% accuracy!)
open lectures_manual_sorted_by_series.csv

# 📊 View statistics and methodology
cat manual_extraction_log.txt

# 📚 All extraction results with details
open extracted_lectures_manual_style.csv
```

**TIP:** `lectures_manual_sorted_by_series.csv` is sorted by series (descending lesson count), then chronologically within each series. The `SequenceInSeries` column makes it trivial to identify missing lessons (e.g., if you see 1, 2, 4, 5, then lesson 3 is missing).

**METHODOLOGY:** This extraction mimics manual human analysis - processing each series from `WEEKLY_SCHEDULE_REFERENCE.md` one by one, searching for series-specific keywords, matching locations, and extracting details with high accuracy.

### Run Extraction (Optional)

If you want to re-extract from source:

```bash
python extract_lectures.py
```

The script will:
1. Parse all messages from `messages.html`
2. Process each message through Claude API
3. Generate `extracted_lectures_data.csv`

### Analyze Series Organization

To analyze lessons into series accounting for multi-day classes:

```bash
python analyze_series_corrected.py
```

This generates:
- `lectures_by_series_corrected.csv` - Lessons grouped by series
- Series statistics showing multi-day teaching patterns

## Output Format

The CSV file contains these columns:

| Column | Description |
|--------|-------------|
| TelegramFileName | Audio file name |
| Type | Khutba, Lecture, or Series |
| Topic | Topic for Khutba/Lecture (N/A for Series) |
| SeriesName | Full book series name |
| SubTopic | Chapter/section within series |
| Serial | Lesson number (in Arabic) |
| OriginalAuthor | Author of the book being studied |
| Location/Online | جامع الورود or Online |
| Sheikh | حسن بن محمد منصور الدغريري |
| DateInArabic | Hijri date |
| DateInGreg | Gregorian date |
| ClipLength | Audio duration |
| Category | Fiqh, Aqeedah, Hadeeth, or Other |
| doubtsStatus | Extraction confidence level |

## Extraction Rules

The tool follows detailed rules defined in `EXTRACTION_PROMPT.md`:

- **Type Classification**: Khutba, Lecture, or Series
- **Series Detection**: Identifies ongoing book studies
- **Location**: Defaults to mosque unless marked online (عن بُعد)
- **Serial Numbers**: Preserves Arabic format
- **Categories**: Classifies into Fiqh, Aqeedah, Hadeeth, or Other
- **Transparency**: Reports doubts when uncertain

## Files

### Source Data
- `messages.html` - Telegram export (source data, 268 messages)
- `csvCleanSample.xlsx` - Weekly schedule reference (Excel)
- **`WEEKLY_SCHEDULE_REFERENCE.md`** ⭐ - **Authoritative teaching schedule** extracted from Excel
- `EXTRACTION_PROMPT.md` - Detailed extraction rules

### Extraction Scripts
- **`extract_manual_style.py`** ⭐⭐⭐ - **Latest**: Manual-style series-by-series extraction (86.2% accuracy)
- `sort_manual_extraction.py` - Sorts manual extraction by series and adds sequence numbers
- `extract_with_schedule_strict.py` - Enhanced extraction using weekly schedule (47% accuracy)
- `analyze_series_corrected.py` - Series analysis accounting for multi-day classes
- `extract_lectures.py` - Original extraction script (requires API key)
- `ai_extraction_app.jsx` - React web app version

### Output Files (Pre-Generated)

**🏆 Latest Manual-Style Extraction (BEST):**
- **`lectures_manual_sorted_by_series.csv`** ⭐⭐⭐⭐ - **HIGHEST ACCURACY**: 86.2% matched (231/268), sorted by series then date, with sequence numbers
- **`extracted_lectures_manual_style.csv`** ⭐⭐⭐ - All 268 messages with manual-style extraction
- **`manual_extraction_log.txt`** ⭐⭐ - Detailed log showing series-by-series processing

**Previous Extractions (For Reference):**
- `lectures_sorted_by_series.csv` - Earlier sorted version (47% accuracy)
- `extracted_lectures_final.csv` - Schedule-based extraction (47% accuracy)
- `lectures_by_series_corrected.csv` - Lessons with multi-day analysis
- `extracted_lectures_improved.csv` - All 268 messages with earlier extraction

**Reference Documents:**
- **`WEEKLY_SCHEDULE_REFERENCE.md`** ⭐⭐⭐ - **Authoritative teaching schedule** from Excel
- `SERIES_ANALYSIS_SUMMARY.md` - Complete series analysis and findings (based on earlier extraction)
- `EXTRACTION_REPORT.md` - Detailed extraction methodology and stats

## Example Output

```csv
TelegramFileName,Type,Topic,SeriesName,SubTopic,Serial,OriginalAuthor,...
مفاسد المظاهرات.m4a,Khutba,مفاسد المظاهرات,Not Available,Not Available,Not Available,Not Available,...
```

## Performance

- **Target Accuracy**: 95%+ with no doubts
- **Processing Speed**: ~2 seconds per message
- **API Model**: Claude Sonnet 4.5

## Notes

- The script includes a 0.5 second delay between API calls to respect rate limits
- All Arabic text is preserved in original format
- CSV uses UTF-8 BOM encoding for Excel compatibility

## License

This tool is designed for educational and archival purposes for Islamic content.
