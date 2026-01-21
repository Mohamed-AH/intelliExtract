# IntelliExtract - Islamic Lecture Data Extraction Tool

🕌 Intelligent data extraction from Sheikh Hassan Al-Daghriri's Telegram channel using Claude API

## Overview

This tool automatically extracts structured data from Telegram messages containing Islamic lectures, series lessons, and Friday sermons (Khutbas). It uses Claude AI to intelligently parse Arabic text and classify content according to detailed extraction rules.

### Key Findings

**From 268 Telegram messages, we identified:**
- ✅ **14 unique series** (after correcting for multi-day classes)
- 📚 **265 lessons** extracted and organized
- 🎓 **ALL series are taught 2-7 times per week** (intensive schedule!)
- 📊 **29.7% overall completeness** (~628 lessons missing)
- 📍 **216 masjid lessons** (81.5%) + 49 online (18.5%)

**Top Series:**
1. تأسيس الأحكام شرح عمدة الأحكام (47 lessons, 7x/week)
2. الملخص شرح كتاب التوحيد (34 lessons, 6x/week)
3. الملخص الفقهي (31 lessons, 6x/week)

See `SERIES_ANALYSIS_SUMMARY.md` for complete details.

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
# BEST: View lessons sorted by series and date (easiest to spot gaps)
open lectures_sorted_by_series.csv

# Read the analysis summary
cat SERIES_ANALYSIS_SUMMARY.md

# Or view series with multi-day analysis
open lectures_by_series_corrected.csv
```

**TIP:** `lectures_sorted_by_series.csv` is sorted by series, then chronologically within each series. The `SequenceInSeries` column makes it trivial to identify missing lessons (e.g., if you see 1, 2, 4, 5, then lesson 3 is missing).

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
- `extract_lectures.py` - Main extraction script (requires API key)
- `extract_improved_with_schedule.py` - Enhanced extraction using weekly schedule
- `analyze_series_corrected.py` - Series analysis accounting for multi-day classes
- `ai_extraction_app.jsx` - React web app version

### Output Files (Pre-Generated)
- **`lectures_sorted_by_series.csv`** ⭐⭐⭐ - **BEST FOR GAPS**: Sorted by series, then date - easy to spot missing lessons (90KB)
- **`extracted_lectures_final.csv`** ⭐⭐ - Schedule-based extraction with 47% accuracy (85KB)
- **`lectures_by_series_corrected.csv`** ⭐ - Lessons organized by series with multi-day analysis (86KB)
- `extracted_lectures_improved.csv` - All 268 messages with improved extraction (83KB)
- `extracted_lectures_data.csv` - Initial extraction output
- **`WEEKLY_SCHEDULE_REFERENCE.md`** ⭐⭐ - **Authoritative teaching schedule** from Excel
- **`SERIES_ANALYSIS_SUMMARY.md`** ⭐ - Complete series analysis and findings
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
