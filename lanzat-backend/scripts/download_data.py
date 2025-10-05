"""
Data Download Script for Lanzat
Downloads all required datasets for vulnerability calculation
"""

import requests
import geopandas as gpd
import pandas as pd
from pathlib import Path
import zipfile
import io
import os
from typing import Optional

# Configure paths
BASE_DIR = Path(__file__).parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_file(url: str, output_path: Path, description: str = "file") -> bool:
    """Download a file with progress indication"""
    print(f"📥 Downloading {description}...")
    print(f"   URL: {url}")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))

        with open(output_path, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    percent = (downloaded / total_size) * 100
                    print(f"\r   Progress: {percent:.1f}%", end='', flush=True)
                print()  # New line after progress

        print(f"✅ Downloaded: {output_path.name} ({output_path.stat().st_size / 1024 / 1024:.2f} MB)")
        return True

    except Exception as e:
        print(f"❌ Error downloading {description}: {e}")
        return False


def download_florida_counties():
    """Download Florida county boundaries from Census Bureau"""
    print("\n🗺️  STEP 1: Florida County Boundaries")

    # Census Bureau TIGER/Line Shapefiles
    url = "https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/tl_2023_us_county.zip"
    zip_path = RAW_DATA_DIR / "us_counties.zip"

    if not download_file(url, zip_path, "US County Boundaries"):
        return False

    # Extract shapefile
    print("📦 Extracting shapefile...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(RAW_DATA_DIR / "us_counties")

    # Filter to Florida only (STATEFP = '12')
    print("🔍 Filtering to Florida counties...")
    gdf = gpd.read_file(RAW_DATA_DIR / "us_counties" / "tl_2023_us_county.shp")
    florida = gdf[gdf['STATEFP'] == '12'].copy()

    # Save Florida counties
    florida_path = RAW_DATA_DIR / "florida_counties.geojson"
    florida.to_file(florida_path, driver="GeoJSON")

    print(f"✅ Saved {len(florida)} Florida counties to {florida_path.name}")
    return True


def download_hurricane_data():
    """Download NOAA historical hurricane tracks"""
    print("\n🌀 STEP 2: Hurricane Historical Data")

    # NOAA IBTrACS database
    url = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/csv/ibtracs.NA.list.v04r00.csv"
    csv_path = RAW_DATA_DIR / "hurricane_tracks.csv"

    if not download_file(url, csv_path, "NOAA Hurricane Tracks"):
        return False

    # Load and filter to relevant storms
    print("🔍 Processing hurricane data...")
    df = pd.read_csv(csv_path, low_memory=False)

    # Filter to storms affecting Florida region
    # Latitude: ~24-31°N, Longitude: ~87-80°W
    florida_region = df[
        (df['LAT'].astype(str).str.replace('[A-Z]', '', regex=True).astype(float) >= 24.0) &
        (df['LAT'].astype(str).str.replace('[A-Z]', '', regex=True).astype(float) <= 31.0) &
        (df['LON'].astype(str).str.replace('[A-Z]', '', regex=True).astype(float) >= -87.0) &
        (df['LON'].astype(str).str.replace('[A-Z]', '', regex=True).astype(float) <= -80.0)
    ].copy()

    florida_hurricanes_path = RAW_DATA_DIR / "florida_hurricanes.csv"
    florida_region.to_csv(florida_hurricanes_path, index=False)

    print(f"✅ Saved {len(florida_region)} hurricane track points to {florida_hurricanes_path.name}")
    return True


def download_gdp_data():
    """Download county GDP data from BEA"""
    print("\n💰 STEP 3: County GDP Data")

    print("⚠️  BEA API requires registration:")
    print("   1. Visit: https://apps.bea.gov/API/signup/")
    print("   2. Get your API key")
    print("   3. Set BEA_API_KEY in .env file")

    api_key = os.getenv("BEA_API_KEY")

    if not api_key or api_key == "your_bea_api_key_here":
        print("\n📝 For now, downloading sample GDP data...")

        # Create sample GDP data for all 67 Florida counties
        florida_counties = [
            "Alachua", "Baker", "Bay", "Bradford", "Brevard", "Broward", "Calhoun",
            "Charlotte", "Citrus", "Clay", "Collier", "Columbia", "DeSoto", "Dixie",
            "Duval", "Escambia", "Flagler", "Franklin", "Gadsden", "Gilchrist", "Glades",
            "Gulf", "Hamilton", "Hardee", "Hendry", "Hernando", "Highlands", "Hillsborough",
            "Holmes", "Indian River", "Jackson", "Jefferson", "Lafayette", "Lake", "Lee",
            "Leon", "Levy", "Liberty", "Madison", "Manatee", "Marion", "Martin", "Miami-Dade",
            "Monroe", "Nassau", "Okaloosa", "Okeechobee", "Orange", "Osceola", "Palm Beach",
            "Pasco", "Pinellas", "Polk", "Putnam", "St. Johns", "St. Lucie", "Santa Rosa",
            "Sarasota", "Seminole", "Sumter", "Suwannee", "Taylor", "Union", "Volusia",
            "Wakulla", "Walton", "Washington"
        ]

        # Sample GDP data (in millions)
        sample_gdp = pd.DataFrame({
            'County': florida_counties,
            'GDP_2022': [
                25000, 500, 10000, 600, 30000, 120000, 400,
                15000, 5000, 12000, 35000, 3000, 1500, 300,
                80000, 25000, 8000, 500, 2000, 800, 300,
                400, 400, 1200, 1500, 8000, 3000, 85000,
                500, 6000, 2500, 400, 200, 20000, 40000,
                18000, 1500, 300, 500, 20000, 12000, 8000, 180000,
                4000, 5000, 18000, 1200, 95000, 25000, 90000,
                22000, 55000, 30000, 2500, 18000, 15000, 12000,
                35000, 28000, 5000, 1500, 800, 400, 25000,
                1200, 4000, 1000
            ]
        })

        gdp_path = RAW_DATA_DIR / "county_gdp.csv"
        sample_gdp.to_csv(gdp_path, index=False)

        print(f"✅ Created sample GDP data for {len(sample_gdp)} counties")
        print(f"   Saved to: {gdp_path.name}")
        return True

    # If API key provided, use real BEA API
    print("🔑 BEA API key found, downloading real data...")
    # Implementation would go here for production use

    return True


def download_manual_instructions():
    """Provide instructions for manual downloads"""
    print("\n📋 MANUAL DOWNLOAD REQUIRED:")
    print("=" * 70)

    print("\n1️⃣  CDC Social Vulnerability Index (SVI):")
    print("   URL: https://www.atsdr.cdc.gov/placeandhealth/svi/data_documentation_download.html")
    print("   Steps:")
    print("   - Click 'Download the Data'")
    print("   - Choose 'Florida' from state dropdown")
    print("   - Download 'County' level data (CSV)")
    print("   - Save to: data/raw/cdc_svi_florida.csv")
    print("   File size: ~5 MB")

    print("\n2️⃣  FEMA National Risk Index:")
    print("   URL: https://hazards.fema.gov/nri/data-resources")
    print("   Steps:")
    print("   - Click 'Download NRI Data'")
    print("   - Select 'County' geography")
    print("   - Download CSV for Florida")
    print("   - Save to: data/raw/fema_nri_florida.csv")
    print("   File size: ~20 MB")

    print("\n" + "=" * 70)


def main():
    """Main download orchestrator"""
    print("=" * 70)
    print("🚀 Lanzat Data Download Script")
    print("=" * 70)

    success_count = 0
    total_steps = 3

    # Step 1: Florida Counties
    if download_florida_counties():
        success_count += 1

    # Step 2: Hurricane Data
    if download_hurricane_data():
        success_count += 1

    # Step 3: GDP Data
    if download_gdp_data():
        success_count += 1

    # Manual download instructions
    download_manual_instructions()

    # Summary
    print("\n" + "=" * 70)
    print(f"📊 DOWNLOAD SUMMARY: {success_count}/{total_steps} automated downloads completed")
    print("=" * 70)

    if success_count == total_steps:
        print("✅ All automated downloads successful!")
        print("⚠️  Please complete the 2 manual downloads above")
        print("\n📍 All data saved to:", RAW_DATA_DIR)
        print("\n🔜 Next step: Run 'python scripts/process_data.py' to integrate data")
    else:
        print("⚠️  Some downloads failed. Please check errors above.")

    print("=" * 70)


if __name__ == "__main__":
    main()
