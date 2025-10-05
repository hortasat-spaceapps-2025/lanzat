#!/usr/bin/env python3
"""
Fetch current active hurricanes from NOAA National Hurricane Center API
Updates Florida counties with real-time storm threat levels
"""

import requests
import json
from pathlib import Path
from datetime import datetime
from shapely.geometry import Point, shape
from shapely.ops import nearest_points
import numpy as np

# Directories
BASE_DIR = Path(__file__).parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

# Output files
ACTIVE_STORMS_FILE = PROCESSED_DATA_DIR / "active_hurricanes.json"
COUNTIES_WITH_THREATS_FILE = PROCESSED_DATA_DIR / "counties_current_threats.json"

# NOAA NHC APIs
NHC_ACTIVE_STORMS_URL = "https://www.nhc.noaa.gov/CurrentStorms.json"
NHC_GIS_URL = "https://www.nhc.noaa.gov/gis-at.xml"

# Threat distance thresholds (in km)
THREAT_THRESHOLDS = {
    'extreme': 100,    # Within 100km
    'high': 250,       # Within 250km
    'moderate': 500,   # Within 500km
    'low': 1000        # Within 1000km
}

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points on Earth (in km)"""
    R = 6371  # Earth's radius in km

    # Convert to float and handle None values
    try:
        lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
    except (TypeError, ValueError):
        return float('inf')

    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))

    return R * c

def fetch_active_storms():
    """Fetch current active storms from NOAA NHC"""
    print(f"Fetching active hurricanes from NOAA NHC...")

    try:
        response = requests.get(NHC_ACTIVE_STORMS_URL, timeout=30)
        response.raise_for_status()
        data = response.json()

        active_storms = []

        # Process each active cyclone
        if 'activeStorms' in data and data['activeStorms']:
            for storm in data['activeStorms']:
                storm_info = {
                    'id': storm.get('id', 'unknown'),
                    'name': storm.get('name', 'Unnamed'),
                    'classification': storm.get('classification', 'Unknown'),
                    'intensity': storm.get('intensity', 0),
                    'pressure': storm.get('pressure', 0),
                    'latitude': storm.get('latitude', 0),
                    'longitude': storm.get('longitude', 0),
                    'movement': storm.get('movement', ''),
                    'last_update': storm.get('lastUpdate', ''),
                    'wind_speed_kt': storm.get('windSpeed', 0),
                    'category': categorize_storm(storm.get('windSpeed', 0))
                }
                active_storms.append(storm_info)
                print(f"  - {storm_info['name']}: {storm_info['classification']}, {storm_info['wind_speed_kt']}kt")
        else:
            print("  No active storms currently tracked by NHC")

        return active_storms

    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not fetch active storms: {e}")
        return []

def categorize_storm(wind_speed_kt):
    """Categorize storm based on wind speed (Saffir-Simpson scale)"""
    if wind_speed_kt < 34:
        return "Tropical Depression"
    elif wind_speed_kt < 64:
        return "Tropical Storm"
    elif wind_speed_kt < 83:
        return "Category 1 Hurricane"
    elif wind_speed_kt < 96:
        return "Category 2 Hurricane"
    elif wind_speed_kt < 113:
        return "Category 3 Hurricane"
    elif wind_speed_kt < 137:
        return "Category 4 Hurricane"
    else:
        return "Category 5 Hurricane"

def calculate_county_threats(active_storms):
    """Calculate threat level for each Florida county based on active storms"""

    # Load county geometries
    counties_file = PROCESSED_DATA_DIR / "counties_enhanced.csv"

    if not counties_file.exists():
        print("Warning: Enhanced counties file not found, using base counties")
        counties_file = PROCESSED_DATA_DIR / "counties_noaa.csv"

    import pandas as pd
    counties_df = pd.read_csv(counties_file)

    # Load GeoJSON for geometries
    geojson_file = PROCESSED_DATA_DIR / "counties.geojson"
    with open(geojson_file, 'r') as f:
        geojson_data = json.load(f)

    # Build county centroids dict
    county_centroids = {}
    for feature in geojson_data['features']:
        county_name = feature['properties']['NAME']
        geom = shape(feature['geometry'])
        centroid = geom.centroid
        county_centroids[county_name] = (centroid.y, centroid.x)  # (lat, lon)

    county_threats = []

    for _, county in counties_df.iterrows():
        county_name = county['NAME']

        if county_name not in county_centroids:
            continue

        county_lat, county_lon = county_centroids[county_name]

        # Calculate minimum distance to any active storm
        min_distance = float('inf')
        nearest_storm = None

        for storm in active_storms:
            storm_lat = storm['latitude']
            storm_lon = storm['longitude']

            distance = haversine_distance(county_lat, county_lon, storm_lat, storm_lon)

            if distance < min_distance:
                min_distance = distance
                nearest_storm = storm

        # Determine threat level
        threat_level = 'none'
        if nearest_storm:
            if min_distance <= THREAT_THRESHOLDS['extreme']:
                threat_level = 'extreme'
            elif min_distance <= THREAT_THRESHOLDS['high']:
                threat_level = 'high'
            elif min_distance <= THREAT_THRESHOLDS['moderate']:
                threat_level = 'moderate'
            elif min_distance <= THREAT_THRESHOLDS['low']:
                threat_level = 'low'

        county_threat = {
            'NAME': county_name,
            'current_threat_level': threat_level,
            'nearest_storm_distance_km': round(min_distance, 1) if min_distance != float('inf') else None,
            'nearest_storm_name': nearest_storm['name'] if nearest_storm else None,
            'nearest_storm_category': nearest_storm['category'] if nearest_storm else None,
            'nearest_storm_wind_speed': nearest_storm['wind_speed_kt'] if nearest_storm else None,
            'has_active_threat': threat_level != 'none',
            'enhanced_vulnerability': float(county.get('enhanced_vulnerability', county.get('vulnerability_score', 0)))
        }

        county_threats.append(county_threat)

    return county_threats

def generate_summary_stats(active_storms, county_threats):
    """Generate summary statistics for active threats"""

    threat_counts = {
        'extreme': sum(1 for c in county_threats if c['current_threat_level'] == 'extreme'),
        'high': sum(1 for c in county_threats if c['current_threat_level'] == 'high'),
        'moderate': sum(1 for c in county_threats if c['current_threat_level'] == 'moderate'),
        'low': sum(1 for c in county_threats if c['current_threat_level'] == 'low'),
        'none': sum(1 for c in county_threats if c['current_threat_level'] == 'none')
    }

    # Find counties with extreme/high threats and high vulnerability
    critical_counties = [
        c for c in county_threats
        if c['current_threat_level'] in ['extreme', 'high'] and c['enhanced_vulnerability'] >= 0.6
    ]
    critical_counties.sort(key=lambda x: x['enhanced_vulnerability'], reverse=True)

    return {
        'generated_at': datetime.now().isoformat(),
        'active_storms_count': len(active_storms),
        'active_storms': active_storms,
        'threat_distribution': threat_counts,
        'counties_under_threat': threat_counts['extreme'] + threat_counts['high'] + threat_counts['moderate'] + threat_counts['low'],
        'critical_counties': critical_counties[:10],  # Top 10 critical
        'total_counties_analyzed': len(county_threats)
    }

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("NOAA Real-Time Hurricane Tracking System")
    print("="*60 + "\n")

    # Create output directory
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Fetch active storms
    active_storms = fetch_active_storms()

    # Calculate county-level threats
    print("\nCalculating county-level threat assessments...")
    county_threats = calculate_county_threats(active_storms)

    # Generate summary
    summary = generate_summary_stats(active_storms, county_threats)

    # Save active storms data
    with open(ACTIVE_STORMS_FILE, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\n✓ Saved active storms data to {ACTIVE_STORMS_FILE}")

    # Save county threats data
    with open(COUNTIES_WITH_THREATS_FILE, 'w') as f:
        json.dump(county_threats, f, indent=2)
    print(f"✓ Saved county threat assessments to {COUNTIES_WITH_THREATS_FILE}")

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Active Storms: {summary['active_storms_count']}")
    print(f"Counties Under Threat: {summary['counties_under_threat']}")
    print(f"\nThreat Distribution:")
    print(f"  Extreme: {summary['threat_distribution']['extreme']} counties")
    print(f"  High: {summary['threat_distribution']['high']} counties")
    print(f"  Moderate: {summary['threat_distribution']['moderate']} counties")
    print(f"  Low: {summary['threat_distribution']['low']} counties")
    print(f"  None: {summary['threat_distribution']['none']} counties")

    if summary['critical_counties']:
        print(f"\n⚠️  Critical Counties (High Threat + High Vulnerability):")
        for county in summary['critical_counties'][:5]:
            print(f"  - {county['NAME']}: {county['current_threat_level'].upper()} threat, "
                  f"{county['enhanced_vulnerability']*100:.1f}% vulnerability, "
                  f"{county['nearest_storm_distance_km']}km from {county['nearest_storm_name']}")

    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
