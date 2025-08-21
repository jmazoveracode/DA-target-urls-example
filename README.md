# Veracode Dynamic Analysis Target URL Extractor

This script retrieves all target URLs from Veracode Dynamic Analysis scans by:
1. Getting all analyses using GET /analyses
2. For each analysis, getting scans using GET /analyses/{analysis_id}/scans
3. Extracting target_url from each scan

## Questions Answered

**1. Is there a REST/XML API to GET all Dynamic analysis URL or Target URL tied to a scan?**
- **YES** - Use GET /analyses/{analysis_id}/scans to get scans with target_url field

**2. Can we see all Target URLs for all applications via GET API?** 
- **YES** - By combining GET /analyses + GET /analyses/{analysis_id}/scans (this script demonstrates the approach)

## Usage

### Prerequisites
```bash
pip install -r requirements.txt
```

### Set API Credentials
```bash
export VERACODE_API_KEY_ID='your-api-id'
export VERACODE_API_KEY_SECRET='your-api-key'
```

### Run the Script
```bash
python veracode_target_urls.py
```

## Output
- Console output showing progress and results grouped by application
- JSON file: `veracode_target_urls.json` with all extracted data

## API Endpoints Used
- `GET /was/configservice/v1/analyses` - Get all dynamic analyses
- `GET /was/configservice/v1/analyses/{analysis_id}/scans` - Get scans with target URLs