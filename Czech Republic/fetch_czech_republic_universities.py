import requests
import json
import os
import sys

# Add parent directory to path to import ssl_adapter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ssl_adapter import get_legacy_session

def fetch_universities():
    url = "https://yxcx.cscse.edu.cn/api/xlxwrzz/xlxwrz/getUniversityListOrPage"
    payload = {
        "country": "捷克",
        "currentPage": 1,
        "pageSize": 2000,
        "universityIndex": ""
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }

    try:
        session = get_legacy_session()
        response = session.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        universities = data.get('data', [])
        
        output_file = os.path.join(os.path.dirname(__file__), 'czech_republic_universities_raw.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(universities, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully saved {len(universities)} universities to {output_file}")

    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    fetch_universities()
