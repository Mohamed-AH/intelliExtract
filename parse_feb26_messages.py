#!/usr/bin/env python3
"""
Parse 5feb26messages.html to extract audio messages with details.
Similar to the original parse_messages.py but for the new data.
"""

from bs4 import BeautifulSoup
import json
import re

def parse_messages(html_file):
    """Parse HTML export and extract audio messages"""

    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    messages = []

    # Find all message divs
    all_messages = soup.find_all('div', class_='message')

    print(f"Found {len(all_messages)} total messages")

    audio_count = 0
    for msg_div in all_messages:
        # Look for audio files
        audio_tags = msg_div.find_all('a', class_='media_audio_file')

        for audio_tag in audio_tags:
            filename = audio_tag.get('href', '')

            # Only process AUDIO-* files (actual lectures)
            if 'AUDIO-' in filename:
                audio_count += 1

                # Extract message text
                text_div = msg_div.find('div', class_='text')
                message_text = text_div.get_text(strip=True) if text_div else ''

                # Extract date
                date_div = msg_div.find('div', class_='pull_right date details')
                date_title = date_div.get('title', '') if date_div else ''

                # Extract Gregorian date from title (format: "DD.MM.YYYY HH:MM:SS UTC+03:00")
                greg_date = 'N/A'
                if date_title:
                    date_match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', date_title)
                    if date_match:
                        day, month, year = date_match.groups()
                        greg_date = f"{day}/{month}/{year}"

                # Extract clip length
                clip_length = 'N/A'
                duration_div = msg_div.find('div', class_='duration details')
                if duration_div:
                    clip_length = duration_div.get_text(strip=True)

                # If not in HTML duration div, try to extract from message text
                # Pattern: "مدة الصوتية: XX:XX دقيقة"
                if clip_length == 'N/A' and message_text:
                    duration_match = re.search(r'مدة الصوتية:\s*(\d{1,2}:\d{2})\s*دقيقة', message_text)
                    if duration_match:
                        clip_length = duration_match.group(1)

                messages.append({
                    'filename': filename.split('/')[-1],  # Just the filename
                    'message_text': message_text,
                    'clip_length': clip_length,
                    'greg_date': greg_date
                })

    print(f"Extracted {audio_count} audio messages")
    return messages

def main():
    input_file = '5feb26messages.html'
    output_json = '5feb26_messages_parsed.json'

    print("=" * 80)
    print("PARSING NEW TELEGRAM MESSAGES (Feb 2026)")
    print("=" * 80)
    print()

    messages = parse_messages(input_file)

    # Save to JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

    print()
    print(f"✅ Saved {len(messages)} messages to {output_json}")
    print()

    # Show sample
    if messages:
        print("Sample message:")
        print(json.dumps(messages[0], ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
