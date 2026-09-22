import os
import re
import json

INPUT_FOLDER = "Data"
OUTPUT_FILE = "transcripts.json"

TIMESTAMP_PATTERN = re.compile(r"^(\d{2}:\d{2})$")
SPEAKER_PATTERN = re.compile(r"^(.*?):\s*(.*)$")


def parse_transcript(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    entries = []
    current_timestamp = None

    for line in lines:
        timestamp_match = TIMESTAMP_PATTERN.match(line)

        if timestamp_match:
            current_timestamp = timestamp_match.group(1)
            continue

        speaker_match = SPEAKER_PATTERN.match(line)

        if not speaker_match or current_timestamp is None:
            continue

        speaker = speaker_match.group(1).strip()
        text = speaker_match.group(2).strip()

        entries.append({
            "timestamp": current_timestamp,
            "speaker": speaker,
            "text": text
        })

    return entries


def group_interview(entries, start_id):
    grouped_data = []
    record_id = start_id
    i = 0

    while i < len(entries):
        current = entries[i]

        if "interviewer" in current["speaker"].lower():
            interviewer_timestamp = current["timestamp"]
            interviewer_question = current["text"]

            responder = None
            responder_answer = None
            responder_timestamp = None

            if i + 1 < len(entries):
                next_entry = entries[i + 1]

                if "interviewer" not in next_entry["speaker"].lower():
                    responder = next_entry["speaker"]
                    responder_answer = next_entry["text"]
                    responder_timestamp = next_entry["timestamp"]

                    i += 1

            grouped_data.append({
                "id": record_id,
                "interviewer_timestamp": interviewer_timestamp,
                "interviewer_question": interviewer_question,
                "responder": responder,
                "responder_answer": responder_answer,
                "responder_timestamp": responder_timestamp
            })

            record_id += 1

        i += 1

    return grouped_data, record_id

def main():
    all_records = []
    next_id = 1

    for filename in sorted(os.listdir(INPUT_FOLDER)):
        if filename.endswith(".txt"):
            file_path = os.path.join(INPUT_FOLDER, filename)

            print(f"Processing: {filename}")

            entries = parse_transcript(file_path)

            grouped_records, next_id = group_interview(
                entries,
                next_id
            )

            all_records.extend(grouped_records)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(all_records, file, indent=4, ensure_ascii=False)

    print(f"\nSuccessfully created {OUTPUT_FILE}")
    print(f"Total records: {len(all_records)}")
    print(f"Next available ID: {next_id}")


if __name__ == "__main__":
    main()