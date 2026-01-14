import os
import glob

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the data extraction bug
    # Old faulty line: universities = data.get('data', {}).get('list', [])
    # New correct line: universities = data.get('data', [])
    
    new_content = content.replace("data.get('data', {}).get('list', [])", "data.get('data', [])")
    
    # Fix the key names
    # Old faulty keys: universityNameEn, universityNameCn
    # New correct keys: ENGLISH_NAME, CHINESE_NAME
    
    new_content = new_content.replace("'universityNameEn'", "'ENGLISH_NAME'")
    new_content = new_content.replace("'universityNameCn'", "'CHINESE_NAME'")
    
    # Just in case prompt generation differed slightly
    new_content = new_content.replace('"universityNameEn"', '"ENGLISH_NAME"')
    new_content = new_content.replace('"universityNameCn"', '"CHINESE_NAME"')

    if new_content != content:
        print(f"Patching {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
    else:
        print(f"File {filepath} matches patterns (or already patched).")

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    countries = [
        "Fiji", "Laos", "Mongolia", "Norway", "Sri Lanka", "Turkey", "New Zealand", 
        "Georgia", "Netherlands", "Czech Republic", "Portugal", "Mexico", "Spain"
    ]
    
    for country in countries:
        dir_path = os.path.join(project_root, country)
        # Using glob to find the script in the directory
        pattern = os.path.join(dir_path, "fetch_*_universities.py")
        files = glob.glob(pattern)
        for f in files:
            patch_file(f)

if __name__ == "__main__":
    main()
