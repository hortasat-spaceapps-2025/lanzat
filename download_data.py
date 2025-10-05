#!/usr/bin/env python3
"""
Lanzat Data Download Script
Downloads all critical datasets for Florida vulnerability mapping

Usage:
    python download_data.py

This script will:
1. Create a 'data/' directory
2. Download automated datasets (county boundaries, hurricane tracks, GDP)
3. Provide instructions for manual downloads (CDC SVI, FEMA NRI)
"""

import os
import sys
import requests
from pathlib import Path
import pandas as pd

# Create data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def download_file(url, filename, description=""):
    """Download file with progress indicator"""
    print(f"\n{'='*60}")
    print(f"Downloading: {description or filename}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        filepath = DATA_DIR / filename
        total_size = int(response.headers.get('content-length', 0))

        with open(filepath, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    downloaded += len(chunk)
                    f.write(chunk)
                    done = int(50 * downloaded / total_size)
                    sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {downloaded/1024/1024:.1f} MB")
                    sys.stdout.flush()

        file_size = filepath.stat().st_size / 1024 / 1024
        print(f"\n✓ Downloaded: {filepath}")
        print(f"  Size: {file_size:.1f} MB")
        return filepath

    except requests.exceptions.RequestException as e:
        print(f"\n✗ Error downloading {filename}: {e}")
        return None

def download_critical_datasets():
    """Download all critical datasets for MVP"""

    print("\n" + "="*60)
    print("VULNERABILITYMAP DATA DOWNLOAD")
    print("Florida Hurricane Economic Vulnerability Platform")
    print("="*60)

    downloaded_files = []

    # 1. Florida County Boundaries (GeoJSON)
    print("\n\n[1/3] FLORIDA COUNTY BOUNDARIES")
    counties_url = "https://raw.githubusercontent.com/danielcs88/fl_geo_json/main/geojson-fl-counties-fips.json"
    result = download_file(
        counties_url,
        "florida_counties.geojson",
        "Florida county boundaries with FIPS codes"
    )
    if result:
        downloaded_files.append("florida_counties.geojson")

    # 2. IBTrACS Hurricane Data (North Atlantic)
    print("\n\n[2/3] HURRICANE TRACKS (IBTrACS)")
    ibtracs_url = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.NA.list.v04r01.csv"
    result = download_file(
        ibtracs_url,
        "ibtracs_north_atlantic.csv",
        "Historical hurricane tracks - North Atlantic basin"
    )
    if result:
        downloaded_files.append("ibtracs_north_atlantic.csv")

    # 3. BEA County GDP Data
    print("\n\n[3/3] COUNTY GDP DATA (BEA)")
    gdp_url = "https://www.bea.gov/sites/default/files/2024-12/lagdp1224.xlsx"
    result = download_file(
        gdp_url,
        "county_gdp_2023.xlsx",
        "Bureau of Economic Analysis - County GDP 2023"
    )
    if result:
        downloaded_files.append("county_gdp_2023.xlsx")

    # Manual downloads notification
    print("\n\n" + "="*60)
    print("MANUAL DOWNLOADS REQUIRED")
    print("="*60)

    print("\n📋 CDC SOCIAL VULNERABILITY INDEX (SVI)")
    print("   URL: https://www.atsdr.cdc.gov/place-health/php/svi/svi-data-documentation-download.html")
    print("   Steps:")
    print("   1. Select year: 2022")
    print("   2. Select geography: Florida, County-level")
    print("   3. Download format: CSV")
    print("   4. Save as: data/florida_svi_2022.csv")

    print("\n📋 FEMA NATIONAL RISK INDEX")
    print("   URL: https://hazards.fema.gov/nri/data-resources")
    print("   Steps:")
    print("   1. Select 'Download Data'")
    print("   2. Choose County-level dataset")
    print("   3. Select Florida or download national dataset")
    print("   4. Download CSV or Shapefile")
    print("   5. Save as: data/fema_nri_florida.csv")

    # Summary
    print("\n\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)

    print("\n✓ AUTOMATED DOWNLOADS:")
    for file in downloaded_files:
        filepath = DATA_DIR / file
        if filepath.exists():
            size = filepath.stat().st_size / 1024 / 1024
            print(f"   ✓ {file} ({size:.1f} MB)")

    print("\n⚠ MANUAL DOWNLOADS PENDING:")
    print("   ⚠ florida_svi_2022.csv (CDC SVI)")
    print("   ⚠ fema_nri_florida.csv (FEMA NRI)")

    print("\n📊 STATISTICS:")
    total_size = sum((DATA_DIR / f).stat().st_size for f in downloaded_files if (DATA_DIR / f).exists())
    print(f"   Total downloaded: {total_size / 1024 / 1024:.1f} MB")
    print(f"   Files downloaded: {len(downloaded_files)}/5 critical datasets")
    print(f"   Manual downloads: 2 datasets remaining")

    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("1. Complete manual downloads (see instructions above)")
    print("2. Verify all files in data/ directory:")
    print("   ls -lh data/")
    print("3. Process hurricane data:")
    print("   python process_hurricanes.py")
    print("4. Integrate all datasets:")
    print("   python integrate_data.py")
    print("="*60 + "\n")

def process_hurricane_data():
    """Process hurricane data for Florida"""
    print("\n" + "="*60)
    print("PROCESSING HURRICANE DATA")
    print("="*60)

    ibtracs_file = DATA_DIR / "ibtracs_north_atlantic.csv"

    if not ibtracs_file.exists():
        print("✗ Error: ibtracs_north_atlantic.csv not found")
        print("  Run download_data.py first")
        return

    print("\nLoading IBTrACS data...")
    ibtracs = pd.read_csv(ibtracs_file, skiprows=1, low_memory=False)
    print(f"✓ Loaded {len(ibtracs):,} total hurricane data points")

    # Filter for Florida region
    print("\nFiltering for Florida region...")
    florida_bounds = {
        'min_lat': 24.5, 'max_lat': 31.0,
        'min_lon': -87.6, 'max_lon': -80.0
    }

    florida_hurricanes = ibtracs[
        (ibtracs['LAT'] >= florida_bounds['min_lat']) &
        (ibtracs['LAT'] <= florida_bounds['max_lat']) &
        (ibtracs['LON'] >= florida_bounds['min_lon']) &
        (ibtracs['LON'] <= florida_bounds['max_lon'])
    ]

    print(f"✓ Found {len(florida_hurricanes):,} Florida hurricane data points")

    # Statistics
    unique_storms = florida_hurricanes['NAME'].nunique()
    date_range = f"{florida_hurricanes['ISO_TIME'].min()[:4]} - {florida_hurricanes['ISO_TIME'].max()[:4]}"

    print(f"\n📊 STATISTICS:")
    print(f"   Unique storms: {unique_storms}")
    print(f"   Date range: {date_range}")
    print(f"   Data points: {len(florida_hurricanes):,}")

    # Save processed data
    output_file = DATA_DIR / "florida_hurricanes.csv"
    florida_hurricanes.to_csv(output_file, index=False)
    print(f"\n✓ Saved processed data: {output_file}")

    # Major hurricanes (Category 3+)
    major_hurricanes = florida_hurricanes[florida_hurricanes['USA_WIND'] >= 96]
    major_output = DATA_DIR / "florida_major_hurricanes.csv"
    major_hurricanes.to_csv(major_output, index=False)
    print(f"✓ Saved major hurricanes (Cat 3+): {major_output}")

    print("\n" + "="*60)

def process_gdp_data():
    """Process GDP data for Florida counties"""
    print("\n" + "="*60)
    print("PROCESSING GDP DATA")
    print("="*60)

    gdp_file = DATA_DIR / "county_gdp_2023.xlsx"

    if not gdp_file.exists():
        print("✗ Error: county_gdp_2023.xlsx not found")
        print("  Run download_data.py first")
        return

    print("\nLoading BEA GDP data...")
    gdp_data = pd.read_excel(gdp_file, sheet_name='CAGDP1')
    print(f"✓ Loaded GDP data for {len(gdp_data):,} geographic areas")

    # Filter for Florida (FIPS starts with 12)
    print("\nFiltering for Florida counties...")
    florida_gdp = gdp_data[gdp_data['GeoFips'].str.startswith('12', na=False)]

    # Extract 2023 GDP (all industries)
    florida_gdp_2023 = florida_gdp[florida_gdp['Description'] == 'All industry total'][
        ['GeoFips', 'GeoName', '2023']
    ].copy()
    florida_gdp_2023.rename(columns={'2023': 'GDP_2023', 'GeoFips': 'FIPS'}, inplace=True)

    # Remove state code from FIPS (keep only county code)
    florida_gdp_2023['COUNTY_FIPS'] = florida_gdp_2023['FIPS'].str[2:]

    print(f"✓ Processed {len(florida_gdp_2023)} Florida counties")

    # Statistics
    total_gdp = florida_gdp_2023['GDP_2023'].sum() / 1000  # Convert to billions
    avg_gdp = florida_gdp_2023['GDP_2023'].mean() / 1000
    max_county = florida_gdp_2023.loc[florida_gdp_2023['GDP_2023'].idxmax()]

    print(f"\n📊 STATISTICS:")
    print(f"   Total Florida GDP: ${total_gdp:.1f}B")
    print(f"   Average county GDP: ${avg_gdp:.1f}B")
    print(f"   Largest economy: {max_county['GeoName']} (${max_county['GDP_2023']/1000:.1f}B)")

    # Save processed data
    output_file = DATA_DIR / "florida_gdp_2023.csv"
    florida_gdp_2023.to_csv(output_file, index=False)
    print(f"\n✓ Saved processed data: {output_file}")
    print("="*60)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Download Lanzat datasets')
    parser.add_argument('--process', action='store_true', help='Process downloaded data')
    args = parser.parse_args()

    # Download datasets
    download_critical_datasets()

    # Process data if requested
    if args.process:
        process_hurricane_data()
        process_gdp_data()

    print("\n✨ Data download complete!")
    print("Run with --process flag to process downloaded data:")
    print("   python download_data.py --process\n")
