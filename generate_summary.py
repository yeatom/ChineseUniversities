import pandas as pd
import os

def generate_summary():
    all_dfs = []
    # Project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Country mapping (Folder Name -> Chinese Name)
    country_map = {
        "China": "中国",
        "Japan": "日本",
        "Poland": "波兰",
        "Egypt": "埃及",
        "USA": "美国",
        "UK": "英国",
        "Australia": "澳大利亚",
        "Malaysia": "马来西亚",
        "India": "印度",
        "Singapore": "新加坡",
        "Qatar": "卡塔尔",
        "Ireland": "爱尔兰",
        "Philippines": "菲律宾",
        "Ethiopia": "埃塞俄比亚",
        "UAE": "阿联酋",
        "South Korea": "韩国",
        "Bangladesh": "孟加拉国",
        "Moldova": "摩尔多瓦",
        "Russia": "俄罗斯",
        "France": "法国",
        "Germany": "德国",
        "Afghanistan": "阿富汗",
        "Cambodia": "柬埔寨",
        "Canada": "加拿大",
        "Kenya": "肯尼亚",
        "Cameroon": "喀麦隆",
        "South Africa": "南非",
        "Switzerland": "瑞士",
        "Sweden": "瑞典",
        "Vietnam": "越南",
        "Italy": "意大利",
        "Israel": "以色列"
    }
    
    # Search for all csv files in subdirectories
    for item in os.listdir(project_root):
        item_path = os.path.join(project_root, item)
        if os.path.isdir(item_path) and not item.startswith('.'):
            for file in os.listdir(item_path):
                if file.endswith('.csv'):
                    file_path = os.path.join(item_path, file)
                    print(f"Processing {file_path}...")
                    try:
                        # Read with utf-8-sig to handle BOM if present
                        df = pd.read_csv(file_path, encoding='utf-8-sig')
                        
                        # Normalize column names to lowercase/no space for internal checking
                        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

                        # Ensure expected columns exist
                        if 'chinese_name' in df.columns and 'english_name' in df.columns:
                            # Clean english_name: 
                            # 1. Replace commas with spaces
                            df['english_name'] = df['english_name'].astype(str).str.replace(',', ' ', regex=False)
                            # 2. Handle quotes
                            def clean_quotes(s):
                                s = s.strip()
                                # Remove wrapping quotes
                                if len(s) >= 2 and s.startswith('"') and s.endswith('"'):
                                    s = s[1:-1].strip()
                                # Replace internal double quotes with single quotes to avoid CSV wrapping
                                return s.replace('"', "'")
                            
                            df['english_name'] = df['english_name'].apply(clean_quotes)
                            
                            # Add country columns
                            df['country_english'] = item
                            df['country_chinese'] = country_map.get(item, item) # Fallback to folder name if not mapped
                            
                            all_dfs.append(df[['chinese_name', 'english_name', 'country_chinese', 'country_english']])
                        else:
                            print(f"Skipping {file_path}: Missing required columns. Found: {list(df.columns)}")
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
    
    if all_dfs:
        summary_df = pd.concat(all_dfs, ignore_index=True)
        
        # Add _id column at the beginning
        # Use a simple range-based unique ID, or you could use a hash if preferred.
        # Here we use index + 1 for a human-readable unique integer ID.
        summary_df.insert(0, '_id', range(1, len(summary_df) + 1))
        
        output_path = os.path.join(project_root, 'world_universities.csv')
        summary_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Successfully generated {output_path} with {len(summary_df)} entries.")
    else:
        print("No valid CSV files found in subdirectories.")

if __name__ == "__main__":
    generate_summary()
