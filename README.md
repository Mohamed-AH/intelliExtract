# IntelliExtract - Islamic Lecture Data Extraction Tool

🕌 Intelligent data extraction from Sheikh Hassan Al-Daghriri's Telegram channel using Claude API

## Overview

This tool automatically extracts structured data from Telegram messages containing Islamic lectures, series lessons, and Friday sermons (Khutbas). It uses Claude AI to intelligently parse Arabic text and classify content according to detailed extraction rules.

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

Run the extraction script:

```bash
python extract_lectures.py
```

The script will:
1. Parse all messages from `messages.html`
2. Process each message through Claude API
3. Generate `extracted_lectures_data.csv`

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

- `extract_lectures.py` - Main extraction script
- `messages.html` - Telegram export (source data)
- `EXTRACTION_PROMPT.md` - Detailed extraction rules
- `ai_extraction_app.jsx` - React web app version
- `extracted_lectures_data.csv` - Output file (generated)

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
