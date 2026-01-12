import requests
from bs4 import BeautifulSoup
import csv
import os
import re
from opencc import OpenCC

cc = OpenCC('t2s')

def clean_text(text):
    if not text:
        return ""
    # Remove footnotes like [1], [2]
    text = re.sub(r'\[\d+\]', '', text)
    # Remove [zh] or other markers
    text = re.sub(r'\[[a-z]{2}\]', '', text)
    return text.strip()

def normalize(name):
    return re.sub(r'[\s\(\)（）]', '', name)

def get_hk_universities():
    url = "https://en.wikipedia.org/wiki/List_of_higher_education_institutions_in_Hong_Kong"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Fetching {url}...")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table', {'class': 'wikitable'})
    
    hk_list = []
    
    for table in tables:
        rows = table.find_all('tr')
        if not rows:
            continue
            
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if not cols:
                continue
            
            # Usually the name is in the first column
            name_cell = cols[0].get_text().strip()
            if not name_cell or name_cell.lower() == 'name':
                continue
                
            # Split English and Chinese
            # Pattern: English part followed by Chinese part
            # Many HK wiki tables have "University of Hong Kong 香港大學"
            # We can find the character where Chinese starts
            match = re.search(r'([\u4e00-\u9fff])', name_cell)
            if match:
                start = match.start()
                eng_name = clean_text(name_cell[:start])
                chi_name = clean_text(name_cell[start:])
                # Clean up Chinese name (take only the characters)
                chi_name = re.sub(r'[^\u4e00-\u9fff]', '', chi_name)
                # Convert to Simplified Chinese
                chi_name = cc.convert(chi_name)
                
                if eng_name and chi_name:
                    hk_list.append({
                        'english': eng_name,
                        'chinese': chi_name
                    })
            else:
                # Some might be only English or only Chinese
                if any('\u4e00' <= char <= '\u9fff' for char in name_cell):
                    chi_name = cc.convert(clean_text(name_cell))
                    hk_list.append({'english': '', 'chinese': chi_name})
                else:
                    hk_list.append({'english': clean_text(name_cell), 'chinese': ''})

    return hk_list

def update_json():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'china_universities.csv')
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    universities = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            universities.append(row)

    hk_universities = get_hk_universities()
    print(f"Found {len(hk_universities)} universities in Hong Kong page.")

    # Mapping
    uni_map = {normalize(u['chinese_name']): i for i, u in enumerate(universities)}
    
    matched_count = 0
    added_count = 0
    for hk_uni in hk_universities:
        if not hk_uni['chinese'] or not hk_uni['english']:
            continue
            
        norm_chi = normalize(hk_uni['chinese'])
        if norm_chi in uni_map:
            idx = uni_map[norm_chi]
            if not universities[idx].get('english_name'):
                universities[idx]['english_name'] = hk_uni['english']
                matched_count += 1
        else:
            # Add new university to the list
            universities.append({
                "chinese_name": hk_uni['chinese'],
                "english_name": hk_uni['english']
            })
            # Update map to prevent duplicates if multiple tables have same school
            uni_map[norm_chi] = len(universities) - 1
            added_count += 1

    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['chinese_name', 'english_name']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for uni in universities:
            writer.writerow(uni)
        
    print(f"Successfully matched and updated {matched_count} Hong Kong universities.")
    print(f"Added {added_count} new Hong Kong universities to CSV.")

if __name__ == "__main__":
    update_json()
