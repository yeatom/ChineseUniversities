import os

# Country Configuration
group_a = [
    ("Fiji", "斐济", "fiji_universities.csv"),
    ("Laos", "老挝", "laos_universities.csv"),
    ("Mongolia", "蒙古", "mongolia_universities.csv"),
    ("Norway", "挪威", "norway_universities.csv"),
    ("Sri Lanka", "斯里兰卡", "sri_lanka_universities.csv"),
    ("Turkey", "土耳其", "turkey_universities.csv"),
    ("New Zealand", "新西兰", "new_zealand_universities.csv"),
]

group_b = [
    ("Georgia", "格鲁吉亚", "georgia_universities_raw.json"),
    ("Netherlands", "荷兰", "netherlands_universities_raw.json"),
    ("Czech Republic", "捷克", "czech_republic_universities_raw.json"),
    ("Portugal", "葡萄牙", "portugal_universities_raw.json"),
    ("Mexico", "墨西哥", "mexico_universities_raw.json"),
    ("Spain", "西班牙", "spain_universities_raw.json"),
]

# Template for Group A
template_a = """import subprocess
import json
import csv
import os
import sys

def fetch_universities():
    url = "https://yxcx.cscse.edu.cn/api/xlxwrzz/xlxwrz/getUniversityListOrPage"
    
    payload_dict = {{
        "country": "{chinese_name}",
        "currentPage": 1,
        "pageSize": 2000,
        "universityIndex": ""
    }}
    payload_str = json.dumps(payload_dict, ensure_ascii=False)
    
    cmd = [
        "curl", "-k", "-s",
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", payload_str,
        url
    ]

    try:
        print(f"Fetching data for {chinese_name}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error executing curl: {{result.stderr}}")
            return

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"Error decoding JSON: {{result.stdout[:100]}}...")
            return
            
        universities = data.get('data', {{}}).get('list', []) if data.get('data') else []
        # Handle case where list might be directly in data if structure differs, but expected is data.list
        # Based on previous curl output: {"total":3,"data":[{...},{...}]} 
        # Wait, the curl output I saw was {"total":3,"data":[...],"indexList":[]}
        # So data IS the list directly?
        # "data":[{"TWOCODE":...}]
        # The previous python code used data.get('data', {}).get('list', [])
        # Let's check the curl output again carefully. 
        # {"total":3,"data":[...]} -> data is a list.
        # So structure is root -> data (list).
        # NOTE: The previous code was: universities = data.get('data', {}).get('list', [])
        # Maybe the API format depends on something or I misread.
        # Let's support both or just check data type.
        
        raw_data = data.get('data')
        if isinstance(raw_data, dict):
             universities = raw_data.get('list', [])
        elif isinstance(raw_data, list):
             universities = raw_data
        else:
             universities = []
        
        output_file = os.path.join(os.path.dirname(__file__), '{filename}')
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Chinese Name', 'English Name', 'Website', 'Province', 'City']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for uni in universities:
                # keys might be CHINESE_NAME, ENGLISH_NAME based on curl output
                # The curl output keys: "CHINESE_NAME", "ENGLISH_NAME", "gwwz" (maybe?)
                # Wait, curl output: "ENGLISH_NAME":"The University of Fiji","CHINESE_NAME":"斐济大学"
                # The python code expected: universityNameCn, universityNameEn.
                # It seems the API matches fields based on something? 
                # Let's try to handle both sets of keys.
                
                c_name = uni.get('universityNameCn') or uni.get('CHINESE_NAME', '')
                e_name = uni.get('universityNameEn') or uni.get('ENGLISH_NAME', '')
                website = uni.get('gwwz', '') # website might be missing in curl output?
                
                english_name = e_name.replace('"', '').replace(',', ' ').strip()
                writer.writerow({{
                    'Chinese Name': c_name.strip(),
                    'English Name': english_name,
                    'Website': website.strip(),
                    'Province': '',
                    'City': ''
                }})
                
        print(f"Successfully saved {{len(universities)}} universities to {{output_file}}")

    except Exception as e:
        print(f"Error fetching data: {{e}}")

if __name__ == "__main__":
    fetch_universities()
"""

# Template for Group B
template_b = """import subprocess
import json
import os
import sys

def fetch_universities():
    url = "https://yxcx.cscse.edu.cn/api/xlxwrzz/xlxwrz/getUniversityListOrPage"
    
    payload_dict = {{
        "country": "{chinese_name}",
        "currentPage": 1,
        "pageSize": 2000,
        "universityIndex": ""
    }}
    payload_str = json.dumps(payload_dict, ensure_ascii=False)
    
    cmd = [
        "curl", "-k", "-s",
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", payload_str,
        url
    ]

    try:
        print(f"Fetching data for {chinese_name}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error executing curl: {{result.stderr}}")
            return

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"Error decoding JSON: {{result.stdout[:100]}}...")
            return
            
        # raw_data = data.get('data') 
        # Check structure as above
        raw_data = data.get('data')
        if isinstance(raw_data, dict):
             universities = raw_data.get('list', [])
        elif isinstance(raw_data, list):
             universities = raw_data
        else:
             universities = []
        
        output_file = os.path.join(os.path.dirname(__file__), '{filename}')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(universities, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully saved {{len(universities)}} universities to {{output_file}}")

    except Exception as e:
        print(f"Error fetching data: {{e}}")

if __name__ == "__main__":
    fetch_universities()
"""

base_dir = os.path.dirname(os.path.abspath(__file__))

def write_script(country, content):
    country_dir = os.path.join(base_dir, country)
    if not os.path.exists(country_dir):
        os.makedirs(country_dir)
    
    script_name = f"fetch_{country.lower().replace(' ', '_')}_universities.py"
    script_path = os.path.join(country_dir, script_name)
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Generated {script_path}")

for country, cname, fname in group_a:
    content = template_a.format(chinese_name=cname, filename=fname)
    write_script(country, content)

for country, cname, fname in group_b:
    content = template_b.format(chinese_name=cname, filename=fname)
    write_script(country, content)

print("All scripts regenerated.")
