import json
import csv
import os
import subprocess
import sys

# Add root to path to import gemini_translator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gemini_translator import GeminiTranslator

def fetch_poland_raw():
    url = "https://yxcx.cscse.edu.cn/api/xlxwrzz/xlxwrz/getUniversityListOrPage"
    payload = {
        "country": "波兰",
        "currentPage": 1,
        "pageSize": 200,
        "universityIndex": ""
    }
    
    curl_command = [
        "curl", "-s", "-X", "POST", url,
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]
    
    try:
        process = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        result = json.loads(process.stdout)
        data = result.get("data", [])
        
        # Save raw mapping
        raw_mapping = [
            {"chinese_name": item.get("CHINESE_NAME"), "original_name": item.get("ENGLISH_NAME")}
            for item in data
        ]
        mapping_path = os.path.join(os.path.dirname(__file__), "poland_universities_raw.json")
        with open(mapping_path, 'w', encoding='utf-8') as f:
            json.dump(raw_mapping, f, ensure_ascii=False, indent=4)
        print(f"Saved raw mapping to {mapping_path}")
        return raw_mapping
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def load_existing_data(csv_path):
    existing = {}
    if os.path.exists(csv_path):
        try:
            with open(csv_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("Chinese Name") and row.get("English Name"):
                        existing[row["Chinese Name"]] = row["English Name"]
        except Exception as e:
            print(f"Error loading existing CSV: {e}")
    return existing

def save_to_csv(csv_path, data_dict):
    with open(csv_path, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Chinese Name", "English Name"])
        for cname, ename in data_dict.items():
            # Clean wrapping quotes and internal quotes
            ename = str(ename).strip()
            if ename.startswith('"') and ename.endswith('"'):
                ename = ename[1:-1].strip()
            ename = ename.replace('"', "'").replace(',', ' ')
            writer.writerow([cname, ename])

def main():
    mapping_path = os.path.join(os.path.dirname(__file__), "poland_universities_raw.json")
    csv_path = os.path.join(os.path.dirname(__file__), "poland_universities.csv")
    
    if os.path.exists(mapping_path):
        print(f"Loading raw data from {mapping_path}...")
        with open(mapping_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    else:
        print("Fetching raw data from API...")
        raw_data = fetch_poland_raw()

    if not raw_data:
        print("No data to process.")
        return

    existing_translated = load_existing_data(csv_path)
    print(f"Found {len(raw_data)} universities total, {len(existing_translated)} already translated.")

    translator = GeminiTranslator()
    batch_size = 20
    
    # Filter to only get untranslated ones
    to_translate = [item for item in raw_data if item['chinese_name'] not in existing_translated]
    
    if not to_translate:
        print("All universities already translated.")
        return

    for i in range(0, len(to_translate), batch_size):
        batch = to_translate[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(to_translate)-1)//batch_size + 1}...")
        translated_batch = translator.translate_university_names(batch, country="Poland", language="Polish")
        
        # Merge new translations
        for item in translated_batch:
            existing_translated[item['chinese_name']] = item['english_name']
        
        # Save after each batch
        save_to_csv(csv_path, existing_translated)
        print(f"Batch saved. Total translated: {len(existing_translated)}")

    print(f"Successfully finished. Results in {csv_path}")

    print(f"Successfully saved {len(all_translated)} universities to {csv_path}")

if __name__ == "__main__":
    main()
