# Global Universities List

A comprehensive database of universities worldwide, providing standardized **English** and **Chinese** names for each institution.

[中文版](README_CN.md)

## Project Goal
The objective of this project is to consolidate a complete list of higher education institutions globally. For every university, we provide:
- **_id**: A unique identifier for the combined list.
- **Chinese Name**: Official simplified Chinese name.
- **English Name**: Standard international name, cleaned for CSV compatibility.
- **Country Chinese**: The country name in Chinese.
- **Country English**: The country name in English.

## Data Structure
The project is organized into a modular directory structure for scalability:

- **Root Directory**:
    - `world_universities.csv`: The master consolidated database with unique `_id` fields.
    - `generate_summary.py`: The aggregator script that combines all regional data.
- **Country Folders (`CountryName/`)**:
    - `[country]_universities.csv`: Processed bilingual data for the specific country.
    - `update_[country]_universities.py`: Automation script for fetching and cleaning regional data.
- **Shared Utilities**:
    - `gemini_translator.py`: Core logic for AI-powered translations via Gemini 2.0 Flash.

## Features & Automation
- **AI-Powered Translation**: Uses **Gemini 2.0 Flash** to provide official international English names based on original language names (Polish, Japanese, etc.) or Chinese context.
- **Incremental Updates**: Scripts track existing records to avoid redundant API calls and save costs.
- **Data Cleaning**: 
    - Automatically removes wrapping double quotes around names.
    - Replaces internal double quotes with single quotes.
    - Replaces commas with spaces in English names to ensure clean CSV formatting without escaping issues.
- **Master Summary**: A central script aggregates all regional CSVs into the root database with unique IDs.

## Summary Generation
To update the global summary file:
```bash
python generate_summary.py
```

## Current Progress
- [x] 🇨🇳 **China**: 3000 records (including HK/Macau/Taiwan).
- [x] 🇺🇸 **USA**: 1539 records.
- [x] 🇯🇵 **Japan**: 959 records, Gemini-translated from Japanese.
- [x] 🇫🇷 **France**: 497 records, Gemini-translated from French.
- [x] 🇷🇺 **Russia**: 477 records, Gemini-translated from Russian.
- [x] 🇩🇪 **Germany**: 283 records, Gemini-translated from German.
- [x] 🇰🇷 **South Korea**: 261 records, Gemini-translated from Korean.
- [x] 🇮🇳 **India**: 245 records.
- [x] �🇹 **Italy**: 184 records, Gemini-translated from Italian.
- [x] 🇬🇧 **UK**: 163 records.
- [x] 🇵🇭 **Philippines**: 159 records.
- [x] 🇨🇦 **Canada**: 149 records.
- [x] 🇲🇾 **Malaysia**: 116 records.
- [x] 🇦🇺 **Australia**: 114 records.
- [x] 🇵🇱 **Poland**: 88 records, Gemini-translated from Polish.
- [x] 🇻🇳 **Vietnam**: 47 records.
- [x] 🇿🇦 **South Africa**: 38 records.
- [x] 🇸🇪 **Sweden**: 31 records, Gemini-translated from Swedish.
- [x] 🇪🇬 **Egypt**: 28 records.
- [x] 🇨🇭 **Switzerland**: 26 records, Gemini-translated.
- [x] 🇧🇩 **Bangladesh**: 24 records.
- [x] 🇦🇫 **Afghanistan**: 22 records.
- [x] 🇸🇬 **Singapore**: 15 records.
- [x] 🇮🇪 **Ireland**: 14 records.
- [x] 🇮🇱 **Israel**: 14 records.
- [x] 🇦🇪 **UAE**: 13 records.
- [x] 🇰🇪 **Kenya**: 11 records.
- [x] 🇪🇹 **Ethiopia**: 9 records.
- [x] 🇰🇭 **Cambodia**: 8 records.
- [x] 🇲🇩 **Moldova**: 8 records.
- [x] 🇨🇲 **Cameroon**: 4 records.
- [x] 🇶🇦 **Qatar**: 2 records.
- [ ] **Europe**: Planned.

## Technical Stack
- **Python 3**: Core processing.
- **Pandas**: Data manipulation and CSV management.
- **Gemini 2.0 Flash**: Academic-grade translation and entity mapping.
- **Requests / Curl**: Official API interactions.
- **python-dotenv**: Secure environment variable management.

## Setup & Usage
1. **API Key**: Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_key_here
   ```
2. **Install Dependencies**:
   ```bash
   pip install pandas google-generativeai python-dotenv requests
   ```
3. **Run Update Scripts**:
   ```bash
   python Poland/update_poland_universities.py
   python Japan/update_japan_universities.py
   ```

## Storage Format
- Encoding: `UTF-8 with BOM` for Excel compatibility.
- Normalized column names (`_id`, `chinese_name`, `english_name`, `country_chinese`, `country_english`).
