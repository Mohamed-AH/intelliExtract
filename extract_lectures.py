#!/usr/bin/env python3
"""
Islamic Lecture Data Extraction Tool
Extracts structured data from Telegram messages using Claude API
"""

import os
import re
import json
import csv
import time
from bs4 import BeautifulSoup
from datetime import datetime
from anthropic import Anthropic

# Initialize Claude API client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def parse_html_messages(html_file):
    """Parse messages from the exported Telegram HTML file"""
    print(f"📖 Reading {html_file}...")

    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    messages = []
    message_divs = soup.find_all('div', class_='message')

    for msg_div in message_divs:
        # Skip service messages (date separators)
        if 'service' in msg_div.get('class', []):
            continue

        # Extract message text
        text_div = msg_div.find('div', class_='text')
        if not text_div:
            continue

        message_text = text_div.get_text(separator='\n', strip=True)

        # Extract audio file info
        audio_file = "Not Available"
        clip_length = "Not Available"

        media_div = msg_div.find('div', class_='media_audio_file')
        if media_div:
            title_div = media_div.find('div', class_='title')
            if title_div:
                audio_file = title_div.get_text(strip=True)

            status_div = media_div.find('div', class_='status')
            if status_div:
                status_text = status_div.get_text(strip=True)
                # Extract duration (format: "14:56, 7.0 MB")
                duration_match = re.match(r'(\d+:\d+)', status_text)
                if duration_match:
                    clip_length = duration_match.group(1)

        # Extract date
        date_div = msg_div.find('div', class_='date')
        greg_date = "Not Available"
        if date_div and 'title' in date_div.attrs:
            date_str = date_div['title']
            # Format: "03.10.2025 12:25:20 UTC+03:00"
            greg_date = date_str.split()[0]  # Get just the date part

        messages.append({
            'filename': audio_file,
            'message_text': message_text,
            'clip_length': clip_length,
            'greg_date': greg_date
        })

    print(f"✅ Found {len(messages)} messages to process")
    return messages


def create_extraction_prompt(message):
    """Create the detailed extraction prompt for Claude API"""

    # Read the extraction prompt template
    with open('EXTRACTION_PROMPT.md', 'r', encoding='utf-8') as f:
        extraction_rules = f.read()

    prompt = f"""You are analyzing a Telegram message from Sheikh Hassan Al-Daghriri's Islamic education channel in Saudi Arabia.

**MESSAGE DETAILS:**
Filename: {message['filename']}
Clip Length: {message['clip_length']}
Gregorian Date: {message['greg_date']}

**MESSAGE TEXT:**
{message['message_text']}

**YOUR TASK:**
Follow the extraction rules provided below to extract structured data with maximum accuracy.

{extraction_rules}

**CRITICAL REMINDER:**
- Return ONLY valid JSON, no markdown formatting, no explanation
- For Series: Topic field MUST be "Not Available"
- Location defaults to "جامع الورود" unless explicitly marked as online (عن بُعد)
- Keep serial numbers in Arabic format
- Be transparent in the "doubts" field if uncertain about anything

Respond with ONLY the JSON object:"""

    return prompt


def extract_with_claude(message, index, total):
    """Use Claude API to extract structured data from a message"""

    print(f"🤖 Processing message {index + 1}/{total}: {message['filename'][:50]}...")

    try:
        prompt = create_extraction_prompt(message)

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            temperature=0,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract JSON from response
        response_text = response.content[0].text.strip()

        # Remove markdown code blocks if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        response_text = response_text.strip()

        # Parse JSON
        analysis = json.loads(response_text)

        return analysis

    except json.JSONDecodeError as e:
        print(f"   ⚠️  JSON parse error: {e}")
        print(f"   Response was: {response_text[:200]}...")
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def process_all_messages(messages):
    """Process all messages and extract data"""

    results = []
    no_doubts_count = 0

    print(f"\n🚀 Starting extraction of {len(messages)} messages...\n")

    for i, msg in enumerate(messages):
        analysis = extract_with_claude(msg, i, len(messages))

        if analysis:
            # Create CSV record
            record = {
                'TelegramFileName': msg['filename'],
                'Type': analysis.get('Type', 'Not Available'),
                'Topic': analysis.get('Topic', 'Not Available'),
                'SeriesName': analysis.get('SeriesName', 'Not Available'),
                'SubTopic': analysis.get('SubTopic', 'Not Available'),
                'Serial': analysis.get('Serial', 'Not Available'),
                'OriginalAuthor': analysis.get('OriginalAuthor', 'Not Available'),
                'Location/Online': analysis.get('Location', 'جامع الورود'),
                'Sheikh': 'حسن بن محمد منصور الدغريري',
                'DateInArabic': analysis.get('DateInArabic', 'Not Available'),
                'DateInGreg': msg['greg_date'],
                'ClipLength': msg['clip_length'],
                'Category': analysis.get('Category', 'Not Available'),
                'doubtsStatus': analysis.get('doubts', 'unknown')
            }

            results.append(record)

            if analysis.get('doubts') == 'none':
                no_doubts_count += 1
                print(f"   ✅ No doubts - High confidence")
            else:
                print(f"   ⚠️  Doubts: {analysis.get('doubts')}")
        else:
            print(f"   ❌ Failed to extract data")

        # Small delay to respect rate limits
        time.sleep(0.5)

        # Progress update every 10 messages
        if (i + 1) % 10 == 0:
            accuracy = (no_doubts_count / len(results)) * 100 if results else 0
            print(f"\n📊 Progress: {i + 1}/{len(messages)} | Accuracy: {accuracy:.1f}%\n")

    return results, no_doubts_count


def save_to_csv(results, output_file):
    """Save extracted data to CSV file"""

    if not results:
        print("❌ No results to save")
        return

    print(f"\n💾 Saving {len(results)} records to {output_file}...")

    fieldnames = [
        'TelegramFileName', 'Type', 'Topic', 'SeriesName', 'SubTopic',
        'Serial', 'OriginalAuthor', 'Location/Online', 'Sheikh',
        'DateInArabic', 'DateInGreg', 'ClipLength', 'Category', 'doubtsStatus'
    ]

    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ CSV file saved successfully!")


def main():
    """Main execution function"""

    print("\n" + "="*70)
    print("🕌 Islamic Lecture Data Extraction Tool")
    print("   Using Claude API for intelligent pattern recognition")
    print("="*70 + "\n")

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("   Please set it with: export ANTHROPIC_API_KEY='your-api-key'")
        return

    # Parse messages from HTML
    html_file = 'messages.html'
    if not os.path.exists(html_file):
        print(f"❌ Error: {html_file} not found")
        return

    messages = parse_html_messages(html_file)

    if not messages:
        print("❌ No messages found in HTML file")
        return

    # Process all messages
    results, no_doubts_count = process_all_messages(messages)

    # Save to CSV
    output_file = 'extracted_lectures_data.csv'
    save_to_csv(results, output_file)

    # Print summary
    print("\n" + "="*70)
    print("📊 EXTRACTION SUMMARY")
    print("="*70)
    print(f"   Total Messages: {len(messages)}")
    print(f"   Successfully Processed: {len(results)}")
    print(f"   High Confidence (No Doubts): {no_doubts_count}")
    if results:
        accuracy = (no_doubts_count / len(results)) * 100
        print(f"   Accuracy Rate: {accuracy:.1f}%")
    print(f"   Output File: {output_file}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
