#!/usr/bin/env python3
"""
Big Rig Rescue Deep Web Crawler
Crawls 664 truck repair shop websites and extracts enriched data.
Saves results progressively to CSV and checkpoints progress.
"""

import csv
import json
import requests
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from collections import defaultdict

CSV_PATH = r"C:\Users\ajfre\AppData\Roaming\Claude\local-agent-mode-sessions\1342c0de-0761-498b-9a9a-f63165993fbf\a1c8a082-dfb9-411c-ad7f-427e51f13699\local_31f6f28c-5896-4e32-b500-bed00c40eb0c\outputs\rigrescue_I40_enriched.csv"
OUTPUT_DIR = Path(r'C:\Users\ajfre\rigrescue')
RESULTS_CSV = OUTPUT_DIR / 'rigrescue_I40_deep.csv'
PROGRESS_FILE = OUTPUT_DIR / 'crawl_progress.json'

# Request timeout and headers
TIMEOUT = 15
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def load_shops():
    """Load I-40 shops from CSV."""
    i40_states = {'AZ', 'NM', 'TX', 'OK', 'AR', 'TN', 'NC',
                  'Arizona', 'New Mexico', 'Texas', 'Oklahoma', 'Arkansas', 'Tennessee', 'North Carolina'}
    
    shops = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            state = row.get('state', '').strip()
            if (row.get('is_real_truck_shop', '').strip().lower() == 'yes' and 
                row.get('phone', '').strip() and 
                state in i40_states):
                shops.append(row)
    return shops

def load_progress():
    """Load crawl progress."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'processed': 0, 'failed': 0, 'high_confidence': 0, 'medium_confidence': 0, 'low_confidence': 0}

def save_progress(progress):
    """Save crawl progress."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def fetch_page(url):
    """Fetch a webpage with timeout."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return None

def extract_text(html):
    """Extract clean text from HTML."""
    if not html:
        return ""
    soup = BeautifulSoup(html, 'html.parser')
    # Remove script and style
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text()
    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    return text[:3000]  # Limit to 3000 chars

def find_services_page(base_url, homepage_text):
    """Try to find a services or about page."""
    candidates = [
        '/services',
        '/service',
        '/about',
        '/about-us',
        '/services.html',
        '/services/',
        '/repair-services',
        '/service-offerings',
    ]
    
    for path in candidates:
        try:
            url = urljoin(base_url, path)
            html = fetch_page(url)
            if html:
                return html
        except:
            pass
    
    return None

def extract_services(text):
    """Extract service keywords from text."""
    text_lower = text.lower()
    services = []
    
    service_keywords = {
        'roadside': ['roadside', 'emergency repair', 'roadside service', 'towing'],
        'engine': ['engine', 'diesel', 'motor repair', 'cylinder head'],
        'cooling': ['cooling', 'radiator', 'coolant', 'temperature'],
        'tire': ['tire', 'tires', 'wheel', 'puncture'],
        'reefer': ['reefer', 'refrigerated', 'reefer unit', 'temperature control'],
        'trailer': ['trailer', 'semi trailer', 'tandem'],
        'rv': ['rv', 'motorhome', 'camper', 'rv service'],
        'brakes': ['brake', 'braking', 'air brake', 'brake system'],
        'electrical': ['electrical', 'battery', 'alternator', 'starter', 'wiring']
    }
    
    for service, keywords in service_keywords.items():
        if any(kw in text_lower for kw in keywords):
            services.append(service)
    
    return services

def check_24_7(text):
    """Check if shop claims 24/7 service."""
    text_lower = text.lower()
    indicators_24_7 = ['24/7', '24 hours', '24-hour', 'open 24', 'around the clock', 'day and night']
    return any(ind in text_lower for ind in indicators_24_7)

def check_roadside(text):
    """Check if shop has roadside service."""
    text_lower = text.lower()
    indicators = ['roadside', 'come to you', 'mobile', 'on-site', 'towing', 'we come to']
    return any(ind in text_lower for ind in indicators)

def extract_phone(text):
    """Try to extract a different phone number."""
    import re
    # Look for phone patterns
    phone_pattern = r'\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})'
    matches = re.findall(phone_pattern, text)
    if matches:
        # Return first match that looks different
        for match in matches:
            phone = f"({match[0]}) {match[1]}-{match[2]}"
            return phone
    return ""

def crawl_shop(shop):
    """Crawl a single shop and extract enriched data."""
    result = {
        'name': shop['name'],
        'phone': shop['phone'],
        'website': shop['website'],
        'city': shop['city'],
        'state': shop['state'],
        'description': '',
        'services_confirmed': '',
        'roadside_confirmed': 'no',
        'open_24_7_confirmed': 'no',
        'response_time': '',
        'service_area': '',
        'truck_classes': '',
        'brands_certs': '',
        'fleet_cards': '',
        'emergency_phone': '',
        'still_real_truck_shop': 'yes',
        'data_confidence': 'low',
    }
    
    # Fetch homepage
    homepage_html = fetch_page(shop['website'])
    if not homepage_html:
        return result  # Can't reach site
    
    homepage_text = extract_text(homepage_html)
    
    # Try to fetch services page
    services_html = find_services_page(shop['website'], homepage_text)
    if services_html:
        services_text = extract_text(services_html)
        combined_text = homepage_text + " " + services_text
    else:
        combined_text = homepage_text
    
    # Extract services
    services = extract_services(combined_text)
    if services:
        result['services_confirmed'] = ','.join(services)
        result['data_confidence'] = 'medium'
    
    # Check 24/7
    if check_24_7(combined_text):
        result['open_24_7_confirmed'] = 'yes'
        result['data_confidence'] = 'medium'
    
    # Check roadside
    if check_roadside(combined_text):
        result['roadside_confirmed'] = 'yes'
        result['data_confidence'] = 'medium'
    
    # Try to extract emergency phone
    emergency_phone = extract_phone(combined_text)
    if emergency_phone and emergency_phone != shop['phone']:
        result['emergency_phone'] = emergency_phone
    
    # Build description from first 150 words
    desc_text = combined_text[:500].split('.')[:2]
    if desc_text:
        result['description'] = '.'.join(desc_text).strip() + '.'
        if len(result['description']) > 150:
            result['description'] = result['description'][:150] + '...'
    
    # If we got meaningful data, boost confidence
    if services and (result['roadside_confirmed'] == 'yes' or result['open_24_7_confirmed'] == 'yes'):
        result['data_confidence'] = 'high'
    
    return result

def init_results_csv(shops):
    """Initialize results CSV with all columns."""
    if RESULTS_CSV.exists():
        return  # Already exists
    
    # Get all columns from first shop
    result = crawl_shop(shops[0])
    
    with open(RESULTS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=result.keys())
        writer.writeheader()

def append_result(result):
    """Append a result to the CSV."""
    file_exists = RESULTS_CSV.exists()
    with open(RESULTS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=result.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(result)

def main():
    print("=" * 60)
    print("BIG RIG RESCUE DEEP WEB CRAWLER")
    print("=" * 60)
    
    shops = load_shops()
    progress = load_progress()
    
    total = len(shops)
    start_idx = progress['processed']
    
    print(f"\nLoaded {total} I-40 shops")
    print(f"Resuming from shop {start_idx + 1}")
    print(f"Progress: {start_idx}/{total} processed")
    print(f"  High confidence: {progress['high_confidence']}")
    print(f"  Medium confidence: {progress['medium_confidence']}")
    print(f"  Low confidence: {progress['low_confidence']}")
    print(f"  Failed: {progress['failed']}")
    
    if start_idx == 0:
        init_results_csv(shops)
        print(f"\nCreated {RESULTS_CSV}")
    
    print(f"\nCrawling shops {start_idx + 1}-{min(start_idx + 50, total)}...")
    print("(First 50 shops will take ~2-3 minutes)\n")
    
    # Process next 50 shops
    batch_end = min(start_idx + 50, total)
    
    for i in range(start_idx, batch_end):
        shop = shops[i]
        print(f"[{i+1}/{total}] {shop['name'][:40]:40s} ({shop['city']}, {shop['state']}) ", end='', flush=True)
        
        try:
            result = crawl_shop(shop)
            append_result(result)
            
            # Update progress
            progress['processed'] += 1
            
            if result['data_confidence'] == 'high':
                progress['high_confidence'] += 1
                print("✓ HIGH")
            elif result['data_confidence'] == 'medium':
                progress['medium_confidence'] += 1
                print("◐ MEDIUM")
            else:
                progress['low_confidence'] += 1
                print("○ LOW")
            
            # Save progress every 5 shops
            if (i - start_idx + 1) % 5 == 0:
                save_progress(progress)
        
        except Exception as e:
            progress['failed'] += 1
            print(f"✗ ERROR: {str(e)[:30]}")
        
        # Small delay to be respectful
        time.sleep(0.5)
    
    # Final save
    save_progress(progress)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"BATCH COMPLETE")
    print("=" * 60)
    print(f"Processed this run: {batch_end - start_idx}")
    print(f"Total processed: {progress['processed']}/{total}")
    print(f"\nConfidence distribution:")
    print(f"  High: {progress['high_confidence']} ({100*progress['high_confidence']//progress['processed'] if progress['processed'] else 0}%)")
    print(f"  Medium: {progress['medium_confidence']} ({100*progress['medium_confidence']//progress['processed'] if progress['processed'] else 0}%)")
    print(f"  Low: {progress['low_confidence']} ({100*progress['low_confidence']//progress['processed'] if progress['processed'] else 0}%)")
    print(f"  Failed: {progress['failed']}")
    
    remaining = total - progress['processed']
    if remaining > 0:
        print(f"\nRemaining: {remaining} shops")
        est_time = remaining * 0.5 / 60  # 0.5s per shop
        print(f"Est. time for full crawl: {est_time:.1f} hours (running 24/7)")
        print(f"\nTo continue crawling, run this script again.")
    else:
        print(f"\n✓ CRAWL COMPLETE! All shops processed.")
        print(f"Results saved to: {RESULTS_CSV}")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
