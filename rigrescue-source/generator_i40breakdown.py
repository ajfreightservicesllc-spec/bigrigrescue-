#!/usr/bin/env python3
"""
Big Rig Rescue Static Site Generator - FLASHY VERSION
"""

import csv
import os
import json
from pathlib import Path
from urllib.parse import quote
from collections import defaultdict
from datetime import datetime

CSV_PATH = r"C:\Users\ajfre\AppData\Roaming\Claude\local-agent-mode-sessions\1342c0de-0761-498b-9a9a-f63165993fbf\a1c8a082-dfb9-411c-ad7f-427e51f13699\local_31f6f28c-5896-4e32-b500-bed00c40eb0c\outputs\rigrescue_I40_enriched.csv"
OUTPUT_DIR = Path("C:\\Users\\ajfre\\rigrescue\\public")
BASE_URL = "https://140breakdown.com"

STATE_MAP = {
    'Arizona': 'AZ', 'California': 'CA', 'New Mexico': 'NM',
    'Texas': 'TX', 'Oklahoma': 'OK', 'Arkansas': 'AR',
    'Tennessee': 'TN', 'North Carolina': 'NC',
    'Delaware': 'DE', 'Georgia': 'GA', 'Mississippi': 'MS',
    'New Jersey': 'NJ', 'New York': 'NY', 'Pennsylvania': 'PA',
    'South Carolina': 'SC', 'Virginia': 'VA',
    'AZ': 'AZ', 'CA': 'CA', 'NM': 'NM', 'TX': 'TX', 'OK': 'OK',
    'AR': 'AR', 'TN': 'TN', 'NC': 'NC', 'DE': 'DE', 'GA': 'GA',
    'MS': 'MS', 'NJ': 'NJ', 'NY': 'NY', 'PA': 'PA', 'SC': 'SC', 'VA': 'VA'
}

STATE_NAMES = {
    'AZ': 'Arizona', 'CA': 'California', 'NM': 'New Mexico',
    'TX': 'Texas', 'OK': 'Oklahoma', 'AR': 'Arkansas',
    'TN': 'Tennessee', 'NC': 'North Carolina',
    'DE': 'Delaware', 'GA': 'Georgia', 'MS': 'Mississippi',
    'NJ': 'New Jersey', 'NY': 'New York', 'PA': 'Pennsylvania',
    'SC': 'South Carolina', 'VA': 'Virginia'
}

def load_shops():
    # I-40 states only
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

def slugify(text):
    return quote(text.lower().strip(), safe='').replace('%20', '-')

def get_state_code(state):
    return STATE_MAP.get(state, state[:2].upper() if state else '')

def get_service_list(shop):
    services = []
    service_map = {
        'svc_roadside': 'Roadside',
        'svc_24_7': '24/7',
        'svc_engine': 'Engine',
        'svc_cooling': 'Cooling',
        'svc_tire': 'Tire',
        'svc_reefer': 'Reefer',
        'svc_trailer': 'Trailer',
        'svc_rv': 'RV',
        'svc_brakes': 'Brakes',
        'svc_electrical': 'Electrical'
    }
    for key, label in service_map.items():
        if shop.get(key, '').strip().lower() == 'yes':
            services.append(label)
    return services

def format_phone(phone):
    return phone.strip() if phone else ''

def render_header(title="140 Breakdown"):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="24/7 Emergency Truck Repair Along Interstate 40. Roadside Towing, Diesel Engine Repair, Reefer Service, Mobile Mechanics - Fast Response.">
    <meta name="theme-color" content="#ff2020">
    <link rel="canonical" href="{BASE_URL}">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ scroll-behavior: smooth; }}
        body {{ 
            font-family: 'Arial', 'Helvetica Neue', sans-serif; 
            line-height: 1.6; 
            color: #222; 
            background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
        }}
        a {{ color: #ff2020; text-decoration: none; transition: all 0.3s; }}
        a:hover {{ text-decoration: underline; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        
        /* ANIMATIONS */
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
        @keyframes glow {{
            0%, 100% {{ box-shadow: 0 0 20px rgba(255, 32, 32, 0.6); }}
            50% {{ box-shadow: 0 0 40px rgba(255, 32, 32, 0.9); }}
        }}
        @keyframes slideDown {{
            from {{ opacity: 0; transform: translateY(-20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes bounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-10px); }}
        }}
        @keyframes flash {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        
        /* HEADER */
        header {{ 
            background: linear-gradient(135deg, #ff2020 0%, #cc0000 50%, #990000 100%);
            color: white; 
            padding: 25px 0;
            box-shadow: 0 8px 30px rgba(0,0,0,0.4);
            position: relative;
            overflow: hidden;
            animation: slideDown 0.8s ease;
        }}
        header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -10%;
            width: 600px;
            height: 600px;
            background: radial-gradient(circle, rgba(255,255,255,0.2), transparent);
            border-radius: 50%;
            animation: pulse 4s infinite;
        }}
        header::after {{
            content: '⚙️';
            position: absolute;
            font-size: 200px;
            right: -50px;
            top: -50px;
            opacity: 0.08;
            animation: pulse 3s infinite;
        }}
        header .container {{ position: relative; z-index: 1; }}
        header h1 {{ 
            font-size: 52px; 
            margin-bottom: 8px; 
            font-weight: 900;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
            letter-spacing: -1px;
        }}
        header .tagline {{
            font-size: 14px;
            color: #ffff00;
            font-weight: 900;
            margin-bottom: 8px;
            letter-spacing: 1px;
        }}
        header p {{ 
            font-size: 18px; 
            opacity: 0.95; 
            font-weight: 600;
            max-width: 600px;
        }}
        
        /* HERO SECTION */
        .hero {{
            background: linear-gradient(135deg, #ff2020 0%, #ff4040 50%, #ffaa00 100%);
            color: white;
            padding: 80px 20px;
            text-align: center;
            margin-bottom: 50px;
            position: relative;
            overflow: hidden;
        }}
        .hero::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(255,255,255,0.1) 0%, transparent 50%);
            pointer-events: none;
        }}
        .hero .container {{ position: relative; z-index: 1; }}
        .hero h2 {{
            font-size: 56px;
            margin-bottom: 15px;
            font-weight: 900;
            text-shadow: 4px 4px 8px rgba(0,0,0,0.3);
            animation: pulse 2s infinite;
            letter-spacing: -2px;
        }}
        .hero .highlight {{
            color: #ffff00;
            font-weight: 900;
            display: block;
            font-size: 64px;
            text-shadow: 4px 4px 8px rgba(0,0,0,0.4);
        }}
        .hero p {{
            font-size: 22px;
            margin: 20px 0;
            opacity: 0.95;
            font-weight: 700;
        }}
        .hero .emergency-badge {{
            display: inline-block;
            background: rgba(0,0,0,0.3);
            border: 3px solid #ffff00;
            color: #ffff00;
            padding: 12px 24px;
            border-radius: 50px;
            font-weight: 900;
            font-size: 16px;
            margin-top: 15px;
            animation: glow 2s infinite;
        }}
        
        .stat-boxes {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 15px;
            margin-top: 40px;
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }}
        .stat-box {{
            background: rgba(0,0,0,0.25);
            padding: 25px;
            border-radius: 12px;
            border: 3px solid rgba(255,255,255,0.3);
            transition: all 0.3s;
            animation: slideDown 0.8s ease-out backwards;
        }}
        .stat-box:nth-child(1) {{ animation-delay: 0.1s; }}
        .stat-box:nth-child(2) {{ animation-delay: 0.2s; }}
        .stat-box:nth-child(3) {{ animation-delay: 0.3s; }}
        .stat-box:nth-child(4) {{ animation-delay: 0.4s; }}
        .stat-box:hover {{
            background: rgba(0,0,0,0.4);
            transform: scale(1.08);
        }}
        .stat-box .number {{
            font-size: 36px;
            font-weight: 900;
            color: #ffff00;
        }}
        .stat-box .label {{
            font-size: 13px;
            opacity: 0.9;
            margin-top: 8px;
            font-weight: 700;
        }}
        
        h2 {{ font-size: 38px; margin: 50px 0 30px 0; color: #333; font-weight: 900; text-transform: uppercase; letter-spacing: 1px; }}
        h3 {{ font-size: 22px; margin: 20px 0 15px 0; font-weight: bold; }}
        
        /* BREADCRUMB */
        .breadcrumb {{ font-size: 13px; margin: 15px 0; color: #666; }}
        .breadcrumb a {{ color: #ff2020; font-weight: 700; }}
        
        /* SEARCH FILTER */
        .search-filter {{ 
            background: white; 
            padding: 35px; 
            margin-bottom: 50px; 
            border-radius: 15px; 
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            border-left: 6px solid #ff2020;
        }}
        .search-filter h2 {{ margin-top: 0; }}
        .search-filter label {{ 
            display: block; 
            margin: 15px 0 8px 0; 
            font-weight: bold; 
            font-size: 15px;
            color: #333;
        }}
        .search-filter select, .search-filter input {{ 
            width: 100%; 
            padding: 12px; 
            margin-bottom: 15px; 
            border: 2px solid #ddd; 
            border-radius: 8px; 
            font-size: 14px;
        }}
        .search-filter select:focus, .search-filter input:focus {{
            outline: none;
            border-color: #ff2020;
            box-shadow: 0 0 8px rgba(255,32,32,0.4);
        }}
        
        /* BUTTONS */
        .button {{ 
            display: inline-block; 
            background: linear-gradient(135deg, #ff2020, #cc0000);
            color: white; 
            padding: 14px 32px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 16px; 
            text-decoration: none;
            font-weight: 900;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(255,32,32,0.4);
        }}
        .button:hover {{ 
            background: linear-gradient(135deg, #ff4040, #dd0000);
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(255,32,32,0.6);
            text-decoration: none;
        }}
        
        /* SHOP CARDS */
        .shop-card {{ 
            border: none;
            padding: 28px; 
            margin-bottom: 20px; 
            border-radius: 12px; 
            background: white;
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
            transition: all 0.3s;
            border-left: 5px solid #ff2020;
        }}
        .shop-card:hover {{
            box-shadow: 0 12px 35px rgba(0,0,0,0.2);
            transform: translateY(-5px);
        }}
        .shop-card h3 {{ 
            margin: 0 0 10px 0; 
            color: #333;
        }}
        .shop-card h3 a {{
            color: #ff2020;
            font-weight: 900;
        }}
        .shop-card h3 a:hover {{
            color: #cc0000;
            text-decoration: underline;
        }}
        .shop-card p {{ margin: 8px 0; color: #666; }}
        
        .shop-card a.phone-link {{ 
            display: inline-block; 
            background: linear-gradient(135deg, #ff2020, #cc0000);
            color: white; 
            padding: 16px 28px; 
            border-radius: 8px; 
            font-size: 18px; 
            font-weight: 900; 
            margin: 15px 0; 
            text-decoration: none;
            box-shadow: 0 4px 15px rgba(255,32,32,0.4);
            transition: all 0.3s;
        }}
        .shop-card a.phone-link:hover {{ 
            background: linear-gradient(135deg, #ff4040, #dd0000);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255,32,32,0.6);
            text-decoration: none;
        }}
        
        /* BADGES */
        .badges {{ margin: 15px 0; }}
        .badge {{ 
            display: inline-block; 
            background: #f0f0f0; 
            color: #333; 
            padding: 8px 16px; 
            margin: 6px 8px 6px 0; 
            border-radius: 25px; 
            font-size: 13px; 
            font-weight: 800;
            border: 2px solid #ddd;
            transition: all 0.3s;
        }}
        .badge:hover {{
            transform: scale(1.1);
        }}
        .badge.highlight {{ 
            background: linear-gradient(135deg, #ff2020, #ff4040);
            color: white; 
            border: none;
            font-weight: 900;
            animation: glow 2s infinite;
        }}
        
        /* RATING */
        .rating {{ 
            color: #ff9800; 
            margin: 10px 0;
            font-weight: 900;
            font-size: 15px;
        }}
        
        /* GRID */
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        /* SERVICE LINKS */
        .service-link {{ 
            display: inline-block; 
            padding: 16px 20px; 
            background: white; 
            border: 3px solid #ff2020;
            border-radius: 10px; 
            margin: 10px 10px 10px 0; 
            text-decoration: none; 
            color: #ff2020; 
            font-weight: 900;
            font-size: 15px;
            transition: all 0.3s;
        }}
        .service-link:hover {{ 
            background: #ff2020;
            color: white;
            text-decoration: none;
            transform: scale(1.08);
        }}
        .service-link small {{
            display: block;
            font-size: 12px;
            opacity: 0.8;
            margin-top: 4px;
            font-weight: bold;
        }}
        
        /* FOOTER */
        footer {{ 
            background: #1a1a1a; 
            color: white;
            padding: 40px; 
            margin-top: 80px; 
            text-align: center; 
            font-size: 13px;
            border-top: 5px solid #ff2020;
        }}
        footer a {{ color: #ff2020; font-weight: 900; }}
        
        /* BIG CALL BUTTON */
        .big-call-button {{
            display: block;
            width: 100%;
            background: linear-gradient(135deg, #ff2020, #cc0000);
            color: white;
            padding: 35px 20px;
            border: none;
            border-radius: 12px;
            font-size: 32px;
            font-weight: 900;
            margin: 30px 0;
            text-decoration: none;
            text-align: center;
            box-shadow: 0 8px 30px rgba(255,32,32,0.5);
            transition: all 0.3s;
            cursor: pointer;
            animation: glow 2s infinite;
        }}
        .big-call-button:hover {{
            background: linear-gradient(135deg, #ff4040, #dd0000);
            transform: scale(1.05);
            box-shadow: 0 12px 40px rgba(255,32,32,0.7);
            text-decoration: none;
        }}
        
        /* RESPONSIVE */
        @media (max-width: 768px) {{
            header h1 {{ font-size: 40px; }}
            .hero h2 {{ font-size: 42px; }}
            .hero .highlight {{ font-size: 48px; }}
            .grid {{ grid-template-columns: 1fr; }}
            .stat-boxes {{ grid-template-columns: repeat(2, 1fr); }}
            h2 {{ font-size: 28px; }}
        }}
        @media (max-width: 600px) {{
            header h1 {{ font-size: 32px; }}
            header p {{ font-size: 14px; }}
            .hero h2 {{ font-size: 32px; }}
            .hero .highlight {{ font-size: 38px; }}
            .hero p {{ font-size: 16px; }}
            .container {{ padding: 15px; }}
            .grid {{ grid-template-columns: 1fr; }}
            .big-call-button {{ font-size: 26px; padding: 25px 15px; }}
            h2 {{ font-size: 22px; }}
            .stat-boxes {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="tagline">🚛 TRUCK & RV EMERGENCY REPAIR 🚐</div>
            <h1>⚙️ 140 BREAKDOWN</h1>
            <p>24/7 EMERGENCY TRUCK REPAIR ALONG I-40</p>
        </div>
    </header>
"""

def render_footer():
    return """    </div>
    <footer>
        <p>&copy; 2024 140 Breakdown. 24/7 Emergency Truck Repair & Roadside Service.
        <br><a href="/sitemap.xml">Sitemap</a> | <a href="/">Home</a></p>
    </footer>
</body>
</html>
"""

def render_service_badges(shop):
    services = get_service_list(shop)
    if not services:
        return ""
    badges = []
    for service in services:
        highlight = "highlight" if service in ['Roadside', '24/7'] else ""
        badges.append(f'<span class="badge {highlight}">{service}</span>')
    return '<div class="badges">' + ''.join(badges) + '</div>'

def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)

def generate_homepage(shops, states, cities_dict):
    ensure_dir(OUTPUT_DIR)
    
    service_counts = defaultdict(int)
    for shop in shops:
        if shop.get('svc_roadside', '').lower() == 'yes':
            service_counts['roadside'] += 1
        if shop.get('svc_24_7', '').lower() == 'yes':
            service_counts['24-7'] += 1
        if shop.get('svc_reefer', '').lower() == 'yes':
            service_counts['reefer'] += 1
        if shop.get('svc_tire', '').lower() == 'yes':
            service_counts['tire'] += 1
        if shop.get('svc_cooling', '').lower() == 'yes':
            service_counts['cooling'] += 1
        if shop.get('svc_engine', '').lower() == 'yes':
            service_counts['engine'] += 1
        if shop.get('svc_trailer', '').lower() == 'yes':
            service_counts['trailer'] += 1
        if shop.get('svc_rv', '').lower() == 'yes':
            service_counts['rv'] += 1
    
    html = render_header("140 Breakdown - 24/7 Emergency Truck Repair on I-40")
    
    html += f"""
    <div class="hero">
        <div class="container">
            <h2>STRANDED ON THE ROAD?</h2>
            <span class="highlight">WE'VE GOT YOU</span>
            <div class="emergency-badge">🚨 FAST RESPONSE • 24/7 • 684 SHOPS 🚨</div>
            <p>Expert Diesel Mechanics • Roadside Service • All I-40 States</p>
            
            <div class="stat-boxes">
                <div class="stat-box">
                    <div class="number">{len(shops)}</div>
                    <div class="label">REPAIR SHOPS</div>
                </div>
                <div class="stat-box">
                    <div class="number">{len(states)}</div>
                    <div class="label">STATES</div>
                </div>
                <div class="stat-box">
                    <div class="number">24/7</div>
                    <div class="label">ALWAYS READY</div>
                </div>
                <div class="stat-box">
                    <div class="number">{len(cities_dict)}</div>
                    <div class="label">CITIES</div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="container">
        <h2>⚡ FIND HELP BY SERVICE TYPE</h2>
        <div class="grid">
"""
    
    services = [
        ('roadside', '🚨 ROADSIDE REPAIR'),
        ('24-7', '🌙 24/7 AVAILABLE'),
        ('reefer', '❄️ REEFER REPAIR'),
        ('tire', '🛞 TIRE SERVICE'),
        ('cooling', '🌡️ COOLING SYSTEMS'),
        ('engine', '⚙️ ENGINE REPAIR'),
        ('trailer', '🔗 TRAILER SERVICE'),
        ('rv', '🚐 RV SERVICE')
    ]
    
    for service_key, service_label in services:
        count = service_counts.get(service_key, 0)
        html += f'            <a href="/service/{service_key}/" class="service-link">{service_label}<small>({count} SHOPS)</small></a>\n'
    
    html += """        </div>
        
        <h2>🗺️ FIND HELP BY STATE</h2>
        <div class="grid">
"""
    
    for state_code in sorted(states):
        state_name = STATE_NAMES.get(state_code, state_code)
        state_shops = [s for s in shops if get_state_code(s.get('state', '')) == state_code]
        html += f'            <a href="/state/{state_code}/" class="service-link">{state_name.upper()}<small>({len(state_shops)} SHOPS)</small></a>\n'
    
    html += """        </div>
"""
    
    html += render_footer()
    
    with open(OUTPUT_DIR / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html)

def generate_shop_page(shop, state_code, city):
    shop_slug = slugify(shop['name'])
    shop_dir = OUTPUT_DIR / 'shop' / state_code / city / shop_slug
    ensure_dir(shop_dir)
    
    phone = format_phone(shop['phone'])
    address = shop.get('full address', '').strip()
    rating = shop.get('google rating', '')
    review_count = shop.get('review count', '')
    hours = shop.get('hours', '')
    website = shop.get('website', '').strip()
    
    title = f"{shop['name']} - {city}, {state_code} | Big Rig Rescue"
    
    schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": shop['name'],
        "telephone": phone,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": address.split(',')[0] if ',' in address else address,
            "addressLocality": city,
            "addressRegion": state_code,
            "postalCode": shop.get('zip', ''),
            "addressCountry": "US"
        }
    }
    
    if shop.get('latitude') and shop.get('longitude'):
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": float(shop['latitude']),
            "longitude": float(shop['longitude'])
        }
    
    if rating:
        try:
            review_int = int(float(review_count)) if review_count else 0
        except (ValueError, TypeError):
            review_int = 0
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": rating,
            "reviewCount": review_int
        }
    
    html = render_header(title)
    html += f"""
        <div class="breadcrumb">
            <a href="/">Home</a> / <a href="/state/{state_code}/">{STATE_NAMES.get(state_code, state_code)}</a> / <a href="/city/{state_code}/{slugify(city)}/">{city}</a> / {shop['name']}
        </div>
        
        <h2>{shop['name']}</h2>
        
        <a href="tel:{phone}" class="big-call-button">
            📞 CALL NOW: {phone}
        </a>
        
        {render_service_badges(shop)}
        
        <div class="shop-card" style="margin-top: 20px;">
            <h3>📍 ADDRESS</h3>
            <p><strong>{address}</strong></p>
            <a href="https://www.google.com/maps/search/{quote(address)}" target="_blank" class="button">📍 OPEN IN GOOGLE MAPS</a>
            
            <h3 style="margin-top: 20px;">🕐 HOURS</h3>
            <p>{hours if hours else 'Hours not available'}</p>
            
            <h3 style="margin-top: 20px;">⭐ RATING</h3>
            <p class="rating">⭐ {rating} / 5.0 ({review_count} reviews)</p>
            
            <h3 style="margin-top: 20px;">🔧 SERVICES</h3>
            {render_service_badges(shop)}
            
            {f'<h3 style="margin-top: 20px;">🌐 WEBSITE</h3><p><a href="{website}" target="_blank">{website}</a></p>' if website else ''}
        </div>
        
        <script type="application/ld+json">
{json.dumps(schema, indent=2)}
        </script>
"""
    
    html += render_footer()
    
    with open(shop_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html)

def generate_state_page(state_code, shops):
    state_dir = OUTPUT_DIR / 'state' / state_code
    ensure_dir(state_dir)
    
    state_name = STATE_NAMES.get(state_code, state_code)
    title = f"Truck Repair in {state_name} | Big Rig Rescue"
    
    html = render_header(title)
    html += f"""
        <div class="breadcrumb">
            <a href="/">Home</a> / {state_name}
        </div>
        
        <h2>🚨 EMERGENCY TRUCK REPAIR IN {state_name.upper()}</h2>
        <p>Found <strong>{len(shops)} shops</strong> across <strong>{len(set(s.get('city', '') for s in shops))} cities</strong>.</p>
"""
    
    for shop in shops:
        city = shop.get('city', '').strip()
        phone = format_phone(shop['phone'])
        shop_slug = slugify(shop['name'])
        
        html += f"""
        <div class="shop-card">
            <h3><a href="/shop/{state_code}/{slugify(city)}/{shop_slug}/">{shop['name']}</a></h3>
            <p><strong>{city}, {state_code}</strong></p>
            <a href="tel:{phone}" class="phone-link">📞 {phone}</a>
            {render_service_badges(shop)}
            <p style="font-size: 12px; color: #666; margin-top: 10px;">
                ⭐ {shop.get('google rating', 'N/A')} ({shop.get('review count', '0')} reviews)
            </p>
        </div>
"""
    
    html += render_footer()
    
    with open(state_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html)

def generate_city_page(state_code, city, shops):
    city_dir = OUTPUT_DIR / 'city' / state_code / slugify(city)
    ensure_dir(city_dir)
    
    title = f"Truck Repair in {city}, {state_code} | Big Rig Rescue"
    
    html = render_header(title)
    html += f"""
        <div class="breadcrumb">
            <a href="/">Home</a> / <a href="/state/{state_code}/">{STATE_NAMES.get(state_code, state_code)}</a> / {city}
        </div>
        
        <h2>🚨 EMERGENCY TRUCK REPAIR IN {city.upper()}, {state_code}</h2>
        <p>Found <strong>{len(shops)} shops</strong> in {city}.</p>
"""
    
    for shop in shops:
        phone = format_phone(shop['phone'])
        shop_slug = slugify(shop['name'])
        
        html += f"""
        <div class="shop-card">
            <h3><a href="/shop/{state_code}/{slugify(city)}/{shop_slug}/">{shop['name']}</a></h3>
            <p>{shop.get('full address', '').strip()}</p>
            <a href="tel:{phone}" class="phone-link">📞 {phone}</a>
            {render_service_badges(shop)}
            <p style="font-size: 12px; color: #666; margin-top: 10px;">
                ⭐ {shop.get('google rating', 'N/A')} ({shop.get('review count', '0')} reviews)
            </p>
        </div>
"""
    
    html += render_footer()
    
    with open(city_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html)

def generate_service_page(service_key, service_label, shops):
    service_dir = OUTPUT_DIR / 'service' / service_key
    ensure_dir(service_dir)
    
    service_map_csv = {
        'roadside': 'svc_roadside',
        '24-7': 'svc_24_7',
        'reefer': 'svc_reefer',
        'tire': 'svc_tire',
        'cooling': 'svc_cooling',
        'engine': 'svc_engine',
        'trailer': 'svc_trailer',
        'rv': 'svc_rv',
        'brakes': 'svc_brakes',
        'electrical': 'svc_electrical'
    }
    
    csv_key = service_map_csv.get(service_key, '')
    filtered = [s for s in shops if csv_key and s.get(csv_key, '').lower() == 'yes']
    
    title = f"{service_label} - Emergency Truck Repair | Big Rig Rescue"
    
    html = render_header(title)
    html += f"""
        <div class="breadcrumb">
            <a href="/">Home</a> / {service_label}
        </div>
        
        <h2>{service_label}</h2>
        <p>Found <strong>{len(filtered)} shops</strong> offering {service_label.lower()}.</p>
"""
    
    for shop in sorted(filtered, key=lambda x: (x.get('city', ''), x['name']))[:100]:
        city = shop.get('city', '').strip()
        state = get_state_code(shop.get('state', ''))
        phone = format_phone(shop['phone'])
        shop_slug = slugify(shop['name'])
        
        html += f"""
        <div class="shop-card">
            <h3><a href="/shop/{state}/{slugify(city)}/{shop_slug}/">{shop['name']}</a></h3>
            <p>{city}, {state}</p>
            <a href="tel:{phone}" class="phone-link">📞 {phone}</a>
            {render_service_badges(shop)}
        </div>
"""
    
    if len(filtered) > 100:
        html += f"<p style='font-size: 12px; color: #999; text-align: center; margin-top: 20px;'>Showing first 100 of {len(filtered)} shops</p>"
    
    html += render_footer()
    
    with open(service_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html)

def generate_sitemap(shops, states, cities_dict):
    sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>""" + BASE_URL + """/</loc>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
"""
    
    for state_code in sorted(states):
        sitemap += f"""    <url>
        <loc>{BASE_URL}/state/{state_code}/</loc>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
    </url>
"""
    
    for city_state in sorted(cities_dict.keys())[:100]:
        state_code = city_state.split(', ')[1]
        sitemap += f"""    <url>
        <loc>{BASE_URL}/city/{state_code}/{slugify(city_state.split(", ")[0])}/</loc>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
"""
    
    for service_key in ['roadside', '24-7', 'reefer', 'tire', 'cooling', 'engine', 'trailer', 'rv']:
        sitemap += f"""    <url>
        <loc>{BASE_URL}/service/{service_key}/</loc>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
"""
    
    sitemap += """</urlset>
"""
    
    with open(OUTPUT_DIR / 'sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)

def generate_robots_txt():
    robots = f"""User-agent: *
Allow: /
Sitemap: {BASE_URL}/sitemap.xml
"""
    with open(OUTPUT_DIR / 'robots.txt', 'w', encoding='utf-8') as f:
        f.write(robots)

def main():
    print("Loading shops...")
    shops = load_shops()
    print(f"Loaded {len(shops)} valid shops")
    
    states_dict = defaultdict(list)
    for shop in shops:
        state = get_state_code(shop.get('state', ''))
        states_dict[state].append(shop)
    
    cities_dict = defaultdict(list)
    for shop in shops:
        city = shop.get('city', '').strip()
        state = get_state_code(shop.get('state', ''))
        city_state = f"{city}, {state}"
        cities_dict[city_state].append(shop)
    
    print(f"Grouped into {len(states_dict)} states, {len(cities_dict)} cities")
    
    print("Generating homepage...")
    generate_homepage(shops, states_dict.keys(), cities_dict)
    
    print("Generating state pages...")
    for state_code, state_shops in states_dict.items():
        generate_state_page(state_code, state_shops)
    
    print("Generating city pages...")
    for city_state, city_shops in cities_dict.items():
        city, state_code = city_state.rsplit(', ', 1)
        generate_city_page(state_code, city, city_shops)
    
    print("Generating service pages...")
    services = ['roadside', '24-7', 'reefer', 'tire', 'cooling', 'engine', 'trailer', 'rv', 'brakes', 'electrical']
    service_labels = {
        'roadside': '🚨 ROADSIDE REPAIR',
        '24-7': '🌙 24/7 AVAILABLE',
        'reefer': '❄️ REEFER REPAIR',
        'tire': '🛞 TIRE SERVICE',
        'cooling': '🌡️ COOLING SYSTEMS',
        'engine': '⚙️ ENGINE REPAIR',
        'trailer': '🔗 TRAILER SERVICE',
        'rv': '🚐 RV SERVICE',
        'brakes': '🛑 BRAKE SERVICE',
        'electrical': '⚡ ELECTRICAL SERVICE'
    }
    for service_key in services:
        generate_service_page(service_key, service_labels[service_key], shops)
    
    print("Generating shop pages...")
    for i, shop in enumerate(shops, 1):
        if i % 100 == 0:
            print(f"  {i}/{len(shops)}")
        city = shop.get('city', '').strip()
        state = get_state_code(shop.get('state', ''))
        generate_shop_page(shop, state, city)
    
    print("Generating sitemap and robots.txt...")
    generate_sitemap(shops, states_dict.keys(), cities_dict)
    generate_robots_txt()
    
    print(f"\n✓ Generated {len(shops)} shop pages, {len(states_dict)} state pages, {len(cities_dict)} city pages")
    print(f"✓ Output: {OUTPUT_DIR}")

if __name__ == '__main__':
    main()
