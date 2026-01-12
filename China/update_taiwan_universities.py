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
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\[[a-z]{2}\]', '', text)
    return text.strip()

def normalize(name):
    # Remove all whitespace and common variations
    return re.sub(r'[\s\(\)（）]', '', name)

def update_taiwan():
    url = "https://en.wikipedia.org/wiki/List_of_universities_and_colleges_in_Taiwan"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'china_universities.csv')
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found")
        return

    universities = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            universities.append(row)
                
    uni_map = {normalize(u['chinese_name']): i for i, u in enumerate(universities)}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Fetching {url}...")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    tables = soup.find_all('table', {'class': 'wikitable'})
    
    matched_count = 0
    added_count = 0
    
    for table in tables:
        # Identify name indices
        header_row = table.find('tr')
        if not header_row: continue
        
        headers_text = [h.get_text().strip().lower() for h in header_row.find_all(['th', 'td'])]
        
        eng_idx = -1
        chi_idx = -1
        
        for i, h in enumerate(headers_text):
            if 'chinese' in h:
                chi_idx = i
            elif 'name' in h or h == 'school' or h == 'institution':
                eng_idx = i
        
        if eng_idx == -1 or chi_idx == -1:
            continue
            
        rows = table.find_all('tr')
        for row in rows[1:]:
            cols = row.find_all(['td', 'th'])
            if len(cols) > max(eng_idx, chi_idx):
                eng_name = clean_text(cols[eng_idx].get_text())
                chi_name = cc.convert(clean_text(cols[chi_idx].get_text()))
                
                if not eng_name or not chi_name: continue
                
                norm_chi = normalize(chi_name)
                if norm_chi in uni_map:
                    idx = uni_map[norm_chi]
                    if not universities[idx].get('english_name'):
                        universities[idx]['english_name'] = eng_name
                        matched_count += 1
                else:
                    universities.append({
                        "chinese_name": chi_name,
                        "english_name": eng_name
                    })
                    uni_map[norm_chi] = len(universities) - 1
                    added_count += 1
                    
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['chinese_name', 'english_name']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for uni in universities:
            writer.writerow(uni)
        
    print(f"Matched {matched_count} Taiwan universities.")
    print(f"Added {added_count} new Taiwan universities to JSON.")

if __name__ == "__main__":
    update_taiwan()
