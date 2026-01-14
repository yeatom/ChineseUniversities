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
    return re.sub(r'[\s\(\)（）]', '', name)

def update_macau():
    url = "https://en.wikipedia.org/wiki/List_of_universities_and_colleges_in_Macau"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Output to separate file
    csv_path = os.path.join(base_dir, 'macau_universities.csv')
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Fetching {url}...")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'wikitable'})
    
    macau_universities_list = []
    
    if table:
        rows = table.find_all('tr')
        for row in rows[1:]:
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 3:
                # English, Portuguese, Chinese
                eng_name = clean_text(cols[0].get_text())
                chi_name = cc.convert(clean_text(cols[2].get_text()))
                
                if not eng_name or not chi_name: continue
                
                macau_universities_list.append({
                    "chinese_name": chi_name,
                    "english_name": eng_name
                })
                    
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['chinese_name', 'english_name']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for uni in macau_universities_list:
            writer.writerow(uni)
        
    print(f"Macau: Saved {len(macau_universities_list)} universities to {csv_path}")

if __name__ == "__main__":
    update_macau()
