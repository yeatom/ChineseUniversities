import os
import subprocess
import time

def run_fetchers():
    # List of new countries to process
    countries = [
        "Fiji", "Laos", "Mongolia", "Norway", "Sri Lanka", "Turkey", "New Zealand", # Group A
        "Georgia", "Netherlands", "Czech Republic", "Portugal", "Mexico", "Spain"   # Group B
    ]
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    for country in countries:
        dir_path = os.path.join(project_root, country)
        script_name = f"fetch_{country.lower().replace(' ', '_')}_universities.py"
        script_path = os.path.join(dir_path, script_name)
        
        if os.path.exists(script_path):
            print(f"Running fetcher for {country}...")
            try:
                subprocess.run(["python3", script_path], check=True)
                time.sleep(1) # Be nice to the API
            except subprocess.CalledProcessError as e:
                print(f"Error running {script_name}: {e}")
        else:
            print(f"Script not found: {script_path}")

if __name__ == "__main__":
    run_fetchers()
