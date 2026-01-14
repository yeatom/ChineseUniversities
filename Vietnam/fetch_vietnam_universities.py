import json
import csv
import os
import subprocess

def fetch_vietnam_universities():
    url = "https://yxcx.cscse.edu.cn/api/xlxwrzz/xlxwrz/getUniversityListOrPage"
    payload = {
        "country": "越南",
        "currentPage": 1,
        "pageSize": 1000,
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
        
        csv_path = os.path.join(os.path.dirname(__file__), "vietnam_universities.csv")
        
        with open(csv_path, mode='w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Chinese Name", "English Name"])
            for item in data:
                chinese_name = item.get("CHINESE_NAME")
                english_name = str(item.get("ENGLISH_NAME", "")).strip()
                
                # Cleaning English name
                if english_name.startswith('"') and english_name.endswith('"'):
                    english_name = english_name[1:-1].strip()
                english_name = english_name.replace('"', "'")
                
                writer.writerow([chinese_name, english_name])
        
        print(f"Successfully saved {len(data)} universities to {csv_path}")
        return len(data)
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return 0

if __name__ == "__main__":
    fetch_vietnam_universities()
