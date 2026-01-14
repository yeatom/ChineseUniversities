import json
import csv
import os
import sys

# Add parent directory to path to import gemini_translator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gemini_translator import GeminiTranslator

def process_country(country_name, folder_name, language):
    translator = GeminiTranslator()
    # Corrected path calculation
    project_root = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.path.join(project_root, folder_name)
    # Handle spaces in folder name for file construction (Czech Republic -> czech_republic)
    file_base = folder_name.lower().replace(' ', '_')
    raw_json_path = os.path.join(current_dir, f"{file_base}_universities_raw.json")
    csv_path = os.path.join(current_dir, f"{file_base}_universities.csv")
    
    if not os.path.exists(raw_json_path):
        print(f"Error: {raw_json_path} not found.")
        return

    with open(raw_json_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    existing_data = {}
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_data[row['Chinese Name']] = row['English Name']

    to_translate = []
    for item in raw_data:
        chinese_name = item.get("CHINESE_NAME")
        original_name = item.get("ENGLISH_NAME")
        if chinese_name not in existing_data:
            to_translate.append({"chinese_name": chinese_name, "original_name": original_name})
    
    if not to_translate:
        print(f"Everything for {country_name} is already translated.")
        return

    print(f"Translating {len(to_translate)} universities for {country_name} ({language})...")
    batch_size = 40
    results = existing_data.copy()
    
    for i in range(0, len(to_translate), batch_size):
        batch = to_translate[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{ (len(to_translate)-1)//batch_size + 1 }...")
        translated_batch = translator.translate_university_names(batch, country=country_name, language=language)
        
        if not translated_batch:
            continue

        for item in translated_batch:
            cn = item.get("chinese_name")
            en = item.get("english_name")
            if cn and en:
                results[cn] = str(en).replace('"', "'").replace(',', ' ')
        
        save_to_csv(csv_path, results)
        print(f"Saved progress for {country_name}.")

def save_to_csv(path, data_dict):
    with open(path, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Chinese Name", "English Name"])
        for cn, en in sorted(data_dict.items()):
            writer.writerow([cn, en])

def main():
    countries = [
        ("Russia", "Russia", "Russian"),
        ("France", "France", "French"),
        ("Germany", "Germany", "German"),
        ("Switzerland", "Switzerland", "German/French/Italian"),
        ("Sweden", "Sweden", "Swedish"),
        ("Italy", "Italy", "Italian"),
        ("Georgia", "Georgia", "Georgian"),
        ("Netherlands", "Netherlands", "Dutch"),
        ("Czech Republic", "Czech Republic", "Czech"),
        ("Portugal", "Portugal", "Portuguese"),
        ("Mexico", "Mexico", "Spanish"),
        ("Spain", "Spain", "Spanish")
    ]
    for name, folder, lang in countries:
        try:
            process_country(name, folder, lang)
        except Exception as e:
            print(f"Error processing {name}: {e}")

if __name__ == "__main__":
    main()
