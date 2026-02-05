#!/usr/bin/env python3
"""
Parse messages from HTML and prepare them for Claude Code extraction
This script parses the messages and outputs them in a format for analysis
"""

import re
import json
from bs4 import BeautifulSoup


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

        # Skip if message is too short or doesn't contain meaningful content
        if len(message_text) < 50:
            continue

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


def main():
    """Main execution function"""
    print("\n" + "="*70)
    print("🕌 Islamic Lecture Data Parser")
    print("="*70 + "\n")

    # Parse messages from HTML
    html_file = 'messages.html'
    messages = parse_html_messages(html_file)

    if not messages:
        print("❌ No messages found in HTML file")
        return

    # Save to JSON for processing
    output_file = 'messages_parsed.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

    print(f"💾 Saved {len(messages)} messages to {output_file}")

    # Also save first few messages as examples
    print("\n" + "="*70)
    print("📝 Sample Messages (first 3):")
    print("="*70)
    for i, msg in enumerate(messages[:3]):
        print(f"\n--- Message {i+1} ---")
        print(f"Filename: {msg['filename']}")
        print(f"Date: {msg['greg_date']}")
        print(f"Length: {msg['clip_length']}")
        print(f"Text:\n{msg['message_text'][:300]}...")

    print(f"\n✅ Ready to process {len(messages)} messages")
    print(f"📄 All messages saved to: {output_file}\n")


if __name__ == "__main__":
    main()
