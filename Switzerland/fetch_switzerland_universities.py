import json
import os
import subprocess

def fetch_switzerland_universities():
    url = "https://yxcx.cscse.edu.cn/api/xlxwrzz/xlxwrz/getUniversityListOrPage"
    payload = {
        "country": "瑞士",
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
        
        # Save raw mapping
        raw_mapping = [
            {"chinese_name": item.get("CHINESE_NAME"), "original_name": item.get("ENGLISH_NAME")}
            for item in data
        ]
        
        json_path = os.path.join(os.path.dirname(__file__), "switzerland_universities_raw.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(raw_mapping, f, ensure_ascii=False, indent=4)
        
        print(f"Successfully saved {len(data)} universities to {json_path}")
        return len(data)
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return 0

if __name__ == "__main__":
    fetch_switzerland_universities()
