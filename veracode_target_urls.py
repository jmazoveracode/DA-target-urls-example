#!/usr/bin/env python3
"""
Veracode Dynamic Analysis Target URL Extractor

This script retrieves all target URLs from Veracode Dynamic Analysis scans by:
1. Getting all analyses using GET /analyses
2. For each analysis, getting scans using GET /analyses/{analysis_id}/scans
3. Extracting target_url from each scan

Answers the questions:
1. Is there a REST/XML API to GET all Dynamic analysis URL or Target URL tied to a scan? YES
2. Can we see all Target URLs for all applications via GET API? YES (via this approach)
"""

import requests
import json
import os
import sys
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC




class VeracodeDynamicAnalysis:
    """Veracode Dynamic Analysis API client"""
    
    def __init__(self):
        self.base_url = "https://api.veracode.com"
        self.session = requests.Session()
    
    def _make_request(self, method, endpoint, data=None):
        """Make authenticated request to Veracode API"""
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Python Target URL Extractor'
        }
        
        try:
            if method == 'GET':
                response = self.session.get(url, auth=RequestsAuthPluginVeracodeHMAC(), headers=headers)
            elif method == 'POST':
                response = self.session.post(url, auth=RequestsAuthPluginVeracodeHMAC(), headers=headers, data=data)
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None
    
    def get_all_analyses(self):
        """Get all dynamic analyses"""
        print("Fetching all analyses...")
        return self._make_request('GET', '/was/configservice/v1/analyses')
    
    def get_analysis_scans(self, analysis_id):
        """Get all scans for a specific analysis"""
        print(f"Fetching scans for analysis ID: {analysis_id}")
        return self._make_request('GET', f'/was/configservice/v1/analyses/{analysis_id}/scans')
    
    def extract_target_urls(self):
        """Extract all target URLs from all analyses and their scans"""
        results = []
        
        # Step 1: Get all analyses
        analyses_response = self.get_all_analyses()
        if not analyses_response:
            print("Failed to fetch analyses")
            return results
        
        analyses = analyses_response.get('_embedded', {}).get('analyses', [])
        if not analyses:
            print("No analyses found")
            return results
        
        print(f"Found {len(analyses)} analyses")
        
        # Step 2: For each analysis, get scans and extract target URLs
        for analysis in analyses:
            analysis_id = analysis.get('analysis_id')
            analysis_name = analysis.get('name', 'Unknown')
            app_name = analysis.get('application', {}).get('name', 'Unknown')
            
            print(f"\nProcessing analysis: {analysis_name} (ID: {analysis_id}, App: {app_name})")
            
            scans_response = self.get_analysis_scans(analysis_id)
            if not scans_response:
                print(f"  No scans found for analysis {analysis_id}")
                continue
            
            scans = scans_response.get('_embedded', {}).get('scans', [])
            
            for scan in scans:
                target_url = scan.get('target_url')
                scan_id = scan.get('scan_id')
                application_name = scan.get('application_name', app_name)
                scan_config_name = scan.get('scan_config_name', 'N/A')
                latest_status = scan.get('latest_occurrence_status', {}).get('status_type', 'Unknown')
                
                if target_url:
                    result = {
                        'analysis_id': analysis_id,
                        'analysis_name': analysis_name,
                        'application_name': application_name,
                        'scan_id': scan_id,
                        'scan_config_name': scan_config_name,
                        'target_url': target_url,
                        'latest_status': latest_status,
                        'created_on': scan.get('created_on', 'Unknown'),
                        'last_modified_on': scan.get('last_modified_on', 'Unknown')
                    }
                    
                    results.append(result)
                    print(f"  Found target URL: {target_url}")
        
        return results


def main():
    """Main function to extract all target URLs"""
    # The official library will automatically read credentials from:
    # - ~/.veracode/credentials file
    # - Environment variables VERACODE_API_KEY_ID and VERACODE_API_KEY_SECRET
    
    # Initialize the client (no credentials needed - handled by library)
    client = VeracodeDynamicAnalysis()
    
    # Extract all target URLs
    print("=== Veracode Dynamic Analysis Target URL Extractor ===\n")
    target_urls = client.extract_target_urls()
    
    # Display results
    print(f"\n=== RESULTS ===")
    print(f"Total target URLs found: {len(target_urls)}")
    
    if target_urls:
        print("\nTarget URLs by Application:")
        print("-" * 80)
        
        # Group by application
        apps = {}
        for result in target_urls:
            app_name = result['application_name']
            if app_name not in apps:
                apps[app_name] = []
            apps[app_name].append(result)
        
        for app_name, app_results in apps.items():
            print(f"\nApplication: {app_name}")
            for result in app_results:
                print(f"  Analysis: {result['analysis_name']} (ID: {result['analysis_id']})")
                print(f"  Scan ID: {result['scan_id']}")
                print(f"  Scan Config: {result['scan_config_name']}")
                print(f"  Target URL: {result['target_url']}")
                print(f"  Status: {result['latest_status']}")
                print(f"  Created: {result['created_on']}")
                print(f"  Modified: {result['last_modified_on']}")
                print()
        
        # Save to JSON file
        output_file = 'veracode_target_urls.json'
        with open(output_file, 'w') as f:
            json.dump(target_urls, f, indent=2)
        print(f"Results saved to: {output_file}")
    
    else:
        print("No target URLs found.")
    
    # Answer the original questions
    print("\n=== ANSWERS TO YOUR QUESTIONS ===")
    print("1. Is there a REST/XML API to GET all Dynamic analysis URL or Target URL tied to a scan?")
    print("   YES - Use GET /analyses/{analysis_id}/scans to get scans with target_url field")
    print()
    print("2. Can we see all Target URLs for all applications via GET API?")
    print("   YES - By combining GET /analyses + GET /analyses/{analysis_id}/scans")
    print("   This script demonstrates the approach you suggested.")


if __name__ == "__main__":
    main()