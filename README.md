# WorldUniTranslation

A comprehensive database of universities worldwide, providing both **English** and **Chinese** names for each institution.

## Project Goal
The objective of this project is to crawl and consolidate a complete list of higher education institutions globally. For every university, we aim to provide:
- **English Name**: Standard international name.
- **Chinese Name**: Simplified Chinese name (translated or localized).

## Data Structure
The project is organized by region/country:

- `world_universities.csv`: A consolidated list of all universities worldwide.
- `China/`: Contains data for Mainland China, Hong Kong, Macau, and Taiwan.
  - Data stored in `china_universities.csv`.
  - Includes conversion from Traditional to Simplified Chinese for HK/Macau/Taiwan entries.
- `Japan/`: (In Progress) Planned structure for Japanese institutions.

## Summary Generation
To update the global summary file, run:
```bash
python3 generate_summary.py
```
This script traverses all regional folders and aggregates individual CSVs into the root `world_universities.csv`, adding a `country` column based on the folder name.

## Current Progress
- [x] **Mainland China**: Extracted from official lists.
- [x] **Hong Kong**: Scraped from Wikipedia, names mapped and simplified.
- [x] **Macau**: Scraped from Wikipedia, names mapped and simplified.
- [x] **Taiwan**: Scraped from Wikipedia, names mapped and simplified.
- [ ] **Japan**: Researching data sources.
- [ ] **USA**: Planned.
- [ ] **Europe**: Planned.

## Storage Format
All finalized regional data is stored in **CSV** format for easy access in Excel and data processing.
- Encoding: `UTF-8 with BOM` (compatible with Excel).
- Columns: `chinese_name`, `english_name`.

## Technical Stack
- **Python 3**: Core processing language.
- **Pandas**: Initial data extraction from Excel.
- **BeautifulSoup4 & Requests**: Web scraping from Wikipedia.
- **OpenCC**: Traditional to Simplified Chinese conversion.
- **CSV**: Standard storage format.

## Setup & Usage
1. Install dependencies:
   ```bash
   pip install pandas requests beautifulsoup4 opencc-python-reimplemented
   ```
2. Run regional scripts to update data:
   ```bash
   python3 China/update_hk_universities.py
   ```

## Contribution
This project is under active development. The goal is to build the most accurate bilingual university directory available.
