import os
import glob
import re
import json
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# --- Configuration & Data ---

# Complete Country Map (English Folder Name -> Chinese Name)
COUNTRY_MAP = {
    "China": "中国", "Japan": "日本", "Poland": "波兰", "Egypt": "埃及", "USA": "美国", "UK": "英国",
    "Australia": "澳大利亚", "Malaysia": "马来西亚", "India": "印度", "Singapore": "新加坡", "Qatar": "卡塔尔",
    "Ireland": "爱尔兰", "Philippines": "菲律宾", "Ethiopia": "埃塞俄比亚", "UAE": "阿联酋", "South Korea": "韩国",
    "Bangladesh": "孟加拉国", "Moldova": "摩尔多瓦", "Russia": "俄罗斯", "France": "法国", "Germany": "德国",
    "Afghanistan": "阿富汗", "Cambodia": "柬埔寨", "Canada": "加拿大", "Kenya": "肯尼亚", "Cameroon": "喀麦隆",
    "South Africa": "南非", "Switzerland": "瑞士", "Sweden": "瑞典", "Vietnam": "越南", "Italy": "意大利",
    "Israel": "以色列", "Fiji": "斐济", "Laos": "老挝", "Mongolia": "蒙古", "Norway": "挪威", "Sri Lanka": "斯里兰卡",
    "Turkey": "土耳其", "New Zealand": "新西兰", "Georgia": "格鲁吉亚", "Netherlands": "荷兰", "Czech Republic": "捷克",
    "Portugal": "葡萄牙", "Mexico": "墨西哥", "Spain": "西班牙", "Austria": "奥地利", "Angola": "安哥拉", "Andorra": "安道尔",
    "Estonia": "爱沙尼亚", "Azerbaijan": "阿塞拜疆", "Algeria": "阿尔及利亚", "Albania": "阿尔巴尼亚", "Oman": "阿曼",
    "Argentina": "阿根廷", "Bulgaria": "保加利亚", "Iceland": "冰岛", "North Macedonia": "北马其顿", "Botswana": "博茨瓦纳",
    "Palestine": "巴勒斯坦", "Pakistan": "巴基斯坦", "Barbados": "巴巴多斯", "Panama": "巴拿马", "Brazil": "巴西",
    "Burkina Faso": "布基纳法索", "Burundi": "布隆迪", "Belgium": "比利时", "Bosnia and Herzegovina": "波斯尼亚和黑塞哥维那",
    "Bolivia": "玻利维亚", "Belarus": "白俄罗斯", "Peru": "秘鲁", "Benin": "贝宁共和国", "North Korea": "朝鲜", "Denmark": "丹麦",
    "Togo": "多哥", "Dominican Republic": "多米尼加", "Ecuador": "厄瓜多尔", "Finland": "芬兰",
    "Congo (Brazzaville)": "刚果（布）", "Congo (Kinshasa)": "刚果（金）", "Cuba": "古巴", "Colombia": "哥伦比亚",
    "Costa Rica": "哥斯达黎加", "Grenada": "格林纳达", "Kazakhstan": "哈萨克斯坦", "Montenegro": "黑山", "Guinea": "几内亚",
    "Ghana": "加纳", "Kyrgyzstan": "吉尔吉斯斯坦", "Zimbabwe": "津巴布韦", "Croatia": "克罗地亚", "Kuwait": "科威特",
    "Ivory Coast": "科特迪瓦", "Liechtenstein": "列支敦士登", "Libya": "利比亚", "Liberia": "利比里亚", "Rwanda": "卢旺达",
    "Luxembourg": "卢森堡", "Latvia": "拉脱维亚", "Lithuania": "立陶宛", "Romania": "罗马尼亚", "Lebanon": "黎巴嫩",
    "Morocco": "摩洛哥", "Monaco": "摩纳哥", "Mauritius": "毛里求斯", "Myanmar": "缅甸", "Mozambique": "莫桑比克",
    "Maldives": "马尔代夫", "Malawi": "马拉维", "Malta": "马耳他", "Madagascar": "马达加斯加", "Mali": "马里共和国",
    "Nigeria": "尼日利亚", "Niger": "尼日尔", "Nepal": "尼泊尔", "Namibia": "纳米比亚", "Serbia": "塞尔维亚",
    "Sierra Leone": "塞拉利昂", "Cyprus": "塞浦路斯", "Slovakia": "斯洛伐克", "Slovenia": "斯洛文尼亚", "Saudi Arabia": "沙特阿拉伯",
    "Sudan": "苏丹", "Turkmenistan": "土库曼斯坦", "Tanzania": "坦桑尼亚", "Tajikistan": "塔吉克斯坦", "Thailand": "泰国",
    "Trinidad and Tobago": "特立尼达和多巴哥", "Tunisia": "突尼斯", "Ukraine": "乌克兰", "Uzbekistan": "乌兹别克斯坦",
    "Uganda": "乌干达", "Uruguay": "乌拉圭", "Guatemala": "危地马拉", "Venezuela": "委内瑞拉", "Brunei": "文莱",
    "Hungary": "匈牙利", "Syria": "叙利亚", "Greece": "希腊", "Yemen": "也门", "Armenia": "亚美尼亚", "Iraq": "伊拉克",
    "Iran": "伊朗", "Indonesia": "印度尼西亚", "Jamaica": "牙买加", "Jordan": "约旦", "Chile": "智利", "Zambia": "赞比亚"
}

# --- Classes ---

class GeminiTranslator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # Try to check if we can run without API key (e.g. for normalization only)
            # But the translator needs it.
            print("Warning: GEMINI_API_KEY not found. Translation will fail.")
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')

    def translate_university_names(self, universities, country="Poland", language=None):
        """
        universities: list of dicts with {'chinese_name': ..., 'original_name': ...}
        returns: list of dicts with {'chinese_name': ..., 'english_name': ...}
        """
        if not hasattr(self, 'model'):
             print("Gemini model not initialized.")
             return []

        lang_context = f"(in {language})" if language else "(likely in the local language)"
        
        prompt = (
            f"You are an expert academic translator. I will provide a list of universities in {country}. "
            f"Each entry contains a 'chinese_name' and an 'original_name' {lang_context}. "
            f"Please provide the official, most commonly used international English name for each university "
            f"based primarily on the 'original_name', using the 'chinese_name' only as secondary context. "
            "IMPORTANT: Output MUST be in English. Translate terms like 'Universidad' to 'University', 'Ecole'/ 'École' to 'School', 'Institut' to 'Institute', 'Hochschule' to 'University of Applied Sciences', 'Facultad' to 'Faculty'. "
            "FORCE TRANSLATION: Even if the university is known by its native name (e.g. 'Université libre de Bruxelles'), translate it to English (e.g. 'Free University of Brussels'). "
            "Do NOT return the input name if it contains non-English academic terms (Universita, Hochschule, Ecole, etc.). "
            "Respond strictly in JSON format as a list of objects, each containing the original 'chinese_name' and the new 'english_name'.\n\n"
            f"Data: {json.dumps(universities, ensure_ascii=False)}"
        )
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            data = json.loads(response.text)
            
            if not isinstance(data, list):
                print(f"Warning: Gemini returned non-list data.")
                return []
            
            validated_data = []
            for item in data:
                if isinstance(item, dict) and 'chinese_name' in item and 'english_name' in item:
                    ename = str(item['english_name']).lower()
                    if any(err in ename for err in ["error", "unknown", "n/a", "cannot translate"]):
                        continue
                    validated_data.append(item)
            
            return validated_data
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return []

class UniversityProjectManager:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.translator = GeminiTranslator()
        
    def normalize_csv_files(self):
        """
        Walks through all CSV files (excluding world_universities.csv),
        normalizes headers to 'chinese_name', 'english_name',
        and removes duplicates.
        """
        print("Starting Normalization...")
        csv_files = glob.glob(os.path.join(self.project_root, '*', '*_universities.csv'))
        
        for file_path in csv_files:
            if 'world_universities.csv' in file_path:
                continue
                
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                original_columns = list(df.columns)
                # Normalize headers: lower, strip, replace space with underscore
                df.columns = [str(c).strip().lower().replace(' ', '_') for c in df.columns]
                
                header_changed = list(df.columns) != original_columns

                # Check if we have the required columns
                if 'chinese_name' not in df.columns:
                    print(f"Skipping {file_path}: Missing 'chinese_name'. Found: {df.columns}")
                    continue
                
                # Create 'english_name' if missing
                if 'english_name' not in df.columns:
                    if 'original_name' in df.columns:
                        df.rename(columns={'original_name': 'english_name'}, inplace=True)
                        header_changed = True
                    else:
                        df['english_name'] = ""
                        header_changed = True
                
                # Deduplicate rows based on Chinese Name
                initial_count = len(df)
                df.drop_duplicates(subset=['chinese_name'], inplace=True, keep='first')
                
                # Clean header names (remove duplicates columns with .1 suffix)
                cols_to_drop = [c for c in df.columns if re.search(r'\.\d+$', c)]
                if cols_to_drop:
                    df.drop(columns=cols_to_drop, inplace=True)
                
                # Save back if changes occurred
                if len(df) < initial_count or cols_to_drop or header_changed:
                    df.to_csv(file_path, index=False, encoding='utf-8-sig')
                    print(f"cleaned {os.path.basename(file_path)}: {initial_count} -> {len(df)} rows. Headers updated: {header_changed}")
                    
            except Exception as e:
                print(f"Error normalizing {file_path}: {e}")

    def is_valid_english(self, text):
        if pd.isna(text) or str(text).strip() == "" or str(text).lower() == "nan":
            return False
        text_str = str(text)

        # 1. Start with a strict ASCII check. 
        # Most "International English" names should be ASCII. 
        # If it contains accents (é, à, etc.) or non-latin scripts, assume it needs translation/normalization.
        try:
            text_str.encode('ascii')
        except UnicodeEncodeError:
            # Contains non-ASCII characters (Chinese, Cyrillic, or Latin accents like é, ü)
            return False
            
        # 2. Keyword Checks for ASCII-based non-English terms
        # Even if it is pure ASCII (e.g. "Universidad"), it might not be English.
        text_lower = text_str.lower()
        
        # Terms that clearly indicate the name is NOT fully English
        # We look for whole words to avoid false positives in substrings
        bad_keywords = [
            # Spanish / Portuguese / Italian
            'universidad', 'facultad', 'escuela', 'politécnica', 'autónoma', 
            'universidade', 'instituto', 'superior', 'nacional', 'católica', 'pontificia',
            'degli', 'studi', 'accademia', 'politecnico',
            # French (unaccented versions as ASCII check handled accented ones)
            'universite', 'ecole', 'superieur', 'superieure', 'francais', 
            'academie', 'conservatoire', 'royale',
            # German / Dutch / Northern Europe
            'universitat', 'hochschule', 'fachhochschule', 'akademie', 'hogeschool', 
            'vrije', 'uniwersytet', 'politechnika', 'univerzita', 'vysoka', 'skola', 'egyetem'
        ]
        
        # Simple word boundary check
        # e.g. "ecole" should match "Ecole de..." but not "Molecule" (bad example but you get the idea)
        # We'll just check valid separators or start/end of string
        
        for kw in bad_keywords:
            # Check if keyword exists as a distinct word
            pattern = r'(^|\s|[^a-z0-9])' + re.escape(kw) + r'($|\s|[^a-z0-9])'
            if re.search(pattern, text_lower):
                return False

        return True

    def translate_missing_or_bad_names(self):
        """
        Scans all CSVs. If english_name is missing or invalid, translates it.
        """
        print("\nStarting Translation Tasks...")
        csv_files = glob.glob(os.path.join(self.project_root, '*', '*_universities.csv'))
        
        for file_path in csv_files:
            if 'China' in file_path: continue 
            
            relative_path = os.path.relpath(file_path, self.project_root)
            country_name = os.path.dirname(relative_path) 
            
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                
                to_translate = []
                indices = []
                
                for idx, row in df.iterrows():
                    cname = row['chinese_name']
                    ename = row.get('english_name', '')
                    
                    if not self.is_valid_english(ename):
                        to_translate.append({
                            "chinese_name": cname,
                            "original_name": ename 
                        })
                        indices.append(idx)
                
                if not to_translate:
                    continue
                    
                print(f"translating {len(to_translate)} names for {country_name}...")
                
                # Batch translation
                batch_size = 20
                translation_map = {}
                
                for i in range(0, len(to_translate), batch_size):
                    batch = to_translate[i:i+batch_size]
                    results = self.translator.translate_university_names(batch, country=country_name, language=None)
                    for res in results:
                        translation_map[res['chinese_name']] = res['english_name']
                
                # Apply updates
                updated_count = 0
                for idx in indices:
                    cname = df.at[idx, 'chinese_name']
                    if cname in translation_map:
                        df.at[idx, 'english_name'] = translation_map[cname]
                        updated_count += 1
                
                if updated_count > 0:
                    df.to_csv(file_path, index=False, encoding='utf-8-sig')
                    print(f"Updated {updated_count} names in {relative_path}")
                    
            except Exception as e:
                print(f"Error translating {relative_path}: {e}")

    def generate_global_summary(self):
        print("\nGenerating World Summary...")
        all_dfs = []
        
        # Search for all csv files in subdirectories
        for item in os.listdir(self.project_root):
            item_path = os.path.join(self.project_root, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                for file in os.listdir(item_path):
                    if file.endswith('.csv'):
                        file_path = os.path.join(item_path, file)
                        try:
                            df = pd.read_csv(file_path, encoding='utf-8-sig')
                            # Normalize internal columns just in case
                            df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

                            if 'chinese_name' in df.columns and 'english_name' in df.columns:
                                # Clean English Name
                                df['english_name'] = df['english_name'].astype(str).str.replace(',', ' ', regex=False)
                                
                                def clean_quotes(s):
                                    s = s.strip()
                                    if len(s) >= 2 and s.startswith('"') and s.endswith('"'):
                                        s = s[1:-1].strip()
                                    return s.replace('"', "'")
                                
                                df['english_name'] = df['english_name'].apply(clean_quotes)
                                
                                # Add country columns
                                df['country_english'] = item
                                df['country_chinese'] = COUNTRY_MAP.get(item, item) 
                                
                                # Special handling for China regions
                                if item == 'China':
                                    if 'hk_universities.csv' in file or 'hong_kong' in file.lower():
                                        df['country_english'] = 'Hong Kong'
                                        df['country_chinese'] = '中国香港'
                                    elif 'macau_universities.csv' in file or 'macao' in file.lower():
                                        df['country_english'] = 'Macau'
                                        df['country_chinese'] = '中国澳门'
                                    elif 'taiwan_universities.csv' in file or 'taiwan' in file.lower():
                                        df['country_english'] = 'Taiwan'
                                        df['country_chinese'] = '中国台湾'
                                
                                all_dfs.append(df[['chinese_name', 'english_name', 'country_chinese', 'country_english']])
                            else:
                                pass # Skipping verbose invalid files
                        except Exception as e:
                            print(f"Error reading {file_path}: {e}")
        
        if all_dfs:
            summary_df = pd.concat(all_dfs, ignore_index=True)
            summary_df.sort_values(by='country_english', inplace=True)
            
            output_file = os.path.join(self.project_root, 'world_universities.csv')
            summary_df.insert(0, '_id', range(1, len(summary_df) + 1))
            
            summary_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"Successfully generated {output_file} with {len(summary_df)} entries.")
        else:
            print("No valid CSV files found.")

if __name__ == "__main__":
    manager = UniversityProjectManager()
    
    # Step 1: Normalize all CSVs
    manager.normalize_csv_files()
    
    # Step 2: Translate missing or non-English names
    manager.translate_missing_or_bad_names()
    
    # Step 3: Global Summary
    manager.generate_global_summary()