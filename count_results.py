import os
import json
import pandas as pd

def count_csv(filepath):
    if not os.path.exists(filepath):
        return 0
    try:
        df = pd.read_csv(filepath)
        return len(df)
    except Exception:
        return 0

def count_json(filepath):
    if not os.path.exists(filepath):
        return 0
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return len(data)
    except Exception:
        return 0

countries = [
    # Group A
    ("Fiji", "Fiji/fiji_universities.csv", "csv"),
    ("Laos", "Laos/laos_universities.csv", "csv"),
    ("Mongolia", "Mongolia/mongolia_universities.csv", "csv"),
    ("Norway", "Norway/norway_universities.csv", "csv"),
    ("Sri Lanka", "Sri Lanka/sri_lanka_universities.csv", "csv"),
    ("Turkey", "Turkey/turkey_universities.csv", "csv"),
    ("New Zealand", "New Zealand/new_zealand_universities.csv", "csv"),
    # Group B
    ("Georgia", "Georgia/georgia_universities_raw.json", "json"),
    ("Netherlands", "Netherlands/netherlands_universities_raw.json", "json"),
    ("Czech Republic", "Czech Republic/czech_republic_universities_raw.json", "json"),
    ("Portugal", "Portugal/portugal_universities_raw.json", "json"),
    ("Mexico", "Mexico/mexico_universities_raw.json", "json"),
    ("Spain", "Spain/spain_universities_raw.json", "json"),
]

print("| Country | Type | Count | File Path |")
print("|---|---|---|---|")

for name, rel_path, ftype in countries:
    full_path = os.path.join(os.getcwd(), rel_path)
    if ftype == 'csv':
        count = count_csv(full_path)
    else:
        count = count_json(full_path)
    
    print(f"| {name} | {ftype.upper()} | {count} | {rel_path} |")
