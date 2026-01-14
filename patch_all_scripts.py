import os

countries = [
    "Fiji", "Laos", "Mongolia", "Norway", "Sri Lanka", "Turkey", "New Zealand",
    "Georgia", "Netherlands", "Czech Republic", "Portugal", "Mexico", "Spain"
]

injection = """import requests
import csv
import os
import sys
import json

# Add parent directory to path to import ssl_adapter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ssl_adapter import get_legacy_session
"""

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if "get_legacy_session" in content:
        print(f"Skipping {filepath}, already patched.")
        return

    # Replace imports
    # We look for "import requests\nimport csv\nimport os" or similar variations.
    # To be safe, we just replace the first few lines if they match standard pattern,
    # or better, just replace "import requests" which is common.
    
    if "import requests" in content:
        content = content.replace("import requests", injection, 1)
        # Clean up duplicate imports if any
        content = content.replace("import csv\nimport os", "") 
        content = content.replace("import json\nimport os", "")
        # Remove any other leftover imports that we might have doubled up on
    
    # Replace the request call
    old_call = "response = requests.post(url, json=payload, headers=headers)"
    new_call = "session = get_legacy_session()\n        response = session.post(url, json=payload, headers=headers)"
    
    content = content.replace(old_call, new_call)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {filepath}")

base_dir = os.path.dirname(os.path.abspath(__file__))

for country in countries:
    # Find the fetch script
    country_dir = os.path.join(base_dir, country)
    if not os.path.exists(country_dir):
        print(f"Directory not found: {country_dir}")
        continue
        
    files = os.listdir(country_dir)
    fetch_script = next((f for f in files if f.startswith("fetch_") and f.endswith(".py")), None)
    
    if fetch_script:
        patch_file(os.path.join(country_dir, fetch_script))
    else:
        print(f"No fetch script found in {country}")
