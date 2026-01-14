import json
import csv
import os
import sys

# Add parent directory to path to import gemini_translator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gemini_translator import GeminiTranslator

def main():
    translator = GeminiTranslator()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    raw_json_path = os.path.join(current_dir, "south_korea_universities_raw.json")
    csv_path = os.path.join(current_dir, "south_korea_universities.csv")
    
    if not os.path.exists(raw_json_path):
        print(f"Error: {raw_json_path} not found.")
        return

    with open(raw_json_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # Load existing translations if file exists to resume
    existing_data = {}
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_data[row['Chinese Name']] = row['English Name']

    to_translate = []
    for item in raw_data:
        chinese_name = item.get("CHINESE_NAME")
        original_name = item.get("ENGLISH_NAME") # The API puts original language name here
        
        if chinese_name not in existing_data:
            to_translate.append({
                "chinese_name": chinese_name,
                "original_name": original_name
            })
    
    if not to_translate:
        print("Everything is already translated.")
        return

    print(f"Translating {len(to_translate)} South Korean universities...")
    
    # Batch process translations
    batch_size = 30
    results = existing_data.copy()
    
    for i in range(0, len(to_translate), batch_size):
        batch = to_translate[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1} (items {i} to {i+len(batch)})...")
        # Ensure input to translator matches its specific expected schema:
        # list of dicts with {'chinese_name': ..., 'original_name': ...}
        translated_batch = translator.translate_university_names(batch, country="South Korea", language="Korean")
        
        if not translated_batch:
            print(f"Warning: Batch {i//batch_size + 1} failed or returned no results.")
            continue

        for item in translated_batch:
            chinese_name = item.get("chinese_name")
            english_name = item.get("english_name")
            if chinese_name and english_name:
                # Clean English name
                english_name = str(english_name).replace('"', "'").replace(',', ' ')
                results[chinese_name] = english_name
        
        # Intermediate Save
        save_to_csv(csv_path, results)
        print(f"Saved progress to CSV ({len(results)} total items).")

    print(f"Translation complete. Total entries: {len(results)}")

def save_to_csv(path, data_dict):
    with open(path, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Chinese Name", "English Name"])
        for cn, en in sorted(data_dict.items()):
            writer.writerow([cn, en])

if __name__ == "__main__":
    main()
