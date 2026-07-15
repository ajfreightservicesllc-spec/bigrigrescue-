#!/usr/bin/env python3
"""
Big Rig Rescue Deep Web Crawler
Crawls 664 truck repair shop websites and extracts enriched data.
Checkpoints after every batch to resume on interruption.
"""

import csv
import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

CSV_PATH = r"C:\Users\ajfre\AppData\Roaming\Claude\local-agent-mode-sessions\1342c0de-0761-498b-9a9a-f63165993fbf\a1c8a082-dfb9-411c-ad7f-427e51f13699\local_31f6f28c-5896-4e32-b500-bed00c40eb0c\outputs\rigrescue_I40_enriched.csv"
PROGRESS_FILE = Path(r'C:\Users\ajfre\rigrescue\crawl_progress.json')
RESULTS_FILE = Path(r'C:\Users\ajfre\rigrescue\crawl_results.json')

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
    return {'processed': 0, 'total': 0, 'failed': 0, 'high_confidence': 0}

def save_progress(progress):
    """Save crawl progress."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def load_results():
    """Load accumulated results."""
    if RESULTS_FILE.exists():
        with open(RESULTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_results(results):
    """Save accumulated results."""
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)

def generate_batch_tasks(shops, batch_size=3, start_index=0):
    """Generate task batches for delegation."""
    batches = []
    for i in range(start_index, len(shops), batch_size):
        batch = shops[i:i+batch_size]
        task_list = []
        for shop in batch:
            task_list.append({
                "goal": f"Crawl truck repair shop website. Shop: {shop['name']} ({shop['website']}). Fetch homepage + services/about page (15s timeout). Extract JSON with these fields only: description, services_confirmed (list), roadside_confirmed (yes/no), open_24_7_confirmed (yes/no), response_time, service_area, truck_classes, brands_certs, fleet_cards, emergency_phone, still_real_truck_shop, data_confidence. Accurate over generous—blank if site doesn't say it. Return JSON only.",
                "context": f"Shop name: {shop['name']}, Phone: {shop['phone']}, City: {shop['city']}, State: {shop['state']}, Website: {shop['website']}"
            })
        batches.append(task_list)
    return batches

def main():
    print("Loading shops...")
    shops = load_shops()
    print(f"Loaded {len(shops)} I-40 shops")
    
    progress = load_progress()
    results = load_results()
    
    processed = progress.get('processed', 0)
    total = len(shops)
    
    if processed == 0:
        print(f"Starting fresh crawl of {total} shops")
    else:
        print(f"Resuming: {processed}/{total} processed, {progress.get('high_confidence', 0)} high-confidence")
    
    # Generate batches starting from where we left off
    batches = generate_batch_tasks(shops, batch_size=3, start_index=processed)
    
    print(f"Total batches to crawl: {len(batches)}")
    print(f"\nNext batch (shops {processed}-{min(processed+3, total)}):")
    for i, shop in enumerate(shops[processed:min(processed+3, total)]):
        print(f"  {i+1}. {shop['name']} ({shop['website']})")
    
    print(f"\nTo run crawl: Use delegate_task with 3 shops at a time")
    print(f"After each batch, results are appended to {RESULTS_FILE}")
    print(f"Progress tracked in {PROGRESS_FILE}")

if __name__ == '__main__':
    main()
