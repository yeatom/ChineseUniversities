import pandas as pd
import os

def generate_summary():
    all_dfs = []
    # Project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    
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
                            
                            # Add country column using folder name
                            df['country'] = item
                            all_dfs.append(df[['chinese_name', 'english_name', 'country']])
                        else:
                            print(f"Skipping {file_path}: Missing required columns. Found: {list(df.columns)}")
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
    
    if all_dfs:
        summary_df = pd.concat(all_dfs, ignore_index=True)
        output_path = os.path.join(project_root, 'world_universities.csv')
        summary_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Successfully generated {output_path} with {len(summary_df)} entries.")
    else:
        print("No valid CSV files found in subdirectories.")

if __name__ == "__main__":
    generate_summary()
