"""
Script to download real NOAA IBTrACS hurricane data for Florida risk calculation
"""

import requests
import pandas as pd
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point, LineString
import numpy as np

BASE_DIR = Path(__file__).parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

def download_ibtracs_data():
    """Download NOAA IBTrACS North Atlantic basin data"""
    print("🌀 Downloading NOAA IBTrACS hurricane data...")

    # IBTrACS North Atlantic basin CSV (since 1980)
    url = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/csv/ibtracs.NA.list.v04r00.csv"

    output_path = RAW_DATA_DIR / "ibtracs_north_atlantic.csv"

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(response.content)

        print(f"   ✅ Downloaded: {output_path}")
        print(f"   📦 Size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")

        # Load and preview
        df = pd.read_csv(output_path, skiprows=[1], low_memory=False)  # Skip units row
        print(f"   📊 Total track points: {len(df):,}")
        print(f"   📅 Date range: {df['ISO_TIME'].min()} to {df['ISO_TIME'].max()}")

        return df

    except Exception as e:
        print(f"   ❌ Error downloading: {e}")
        return None

def filter_florida_hurricanes(df):
    """Filter hurricanes that affected Florida"""
    print("\n🎯 Filtering Florida hurricanes...")

    # Florida bounding box (approximate)
    FL_BOUNDS = {
        'lat_min': 24.5,  # Key West area
        'lat_max': 31.0,  # Georgia border
        'lon_min': -87.6, # Pensacola area
        'lon_max': -80.0  # East coast
    }

    # Convert coordinates to numeric
    df['LAT'] = pd.to_numeric(df['LAT'], errors='coerce')
    df['LON'] = pd.to_numeric(df['LON'], errors='coerce')

    # Filter points within or near Florida
    fl_buffer = 2.0  # degrees buffer around Florida
    florida_tracks = df[
        (df['LAT'] >= FL_BOUNDS['lat_min'] - fl_buffer) &
        (df['LAT'] <= FL_BOUNDS['lat_max'] + fl_buffer) &
        (df['LON'] >= FL_BOUNDS['lon_min'] - fl_buffer) &
        (df['LON'] <= FL_BOUNDS['lon_max'] + fl_buffer)
    ].copy()

    # Get unique storms
    unique_storms = florida_tracks['SID'].nunique()

    print(f"   ✅ Found {unique_storms} storms affecting Florida region")
    print(f"   📍 Total track points: {len(florida_tracks):,}")

    # Save filtered data
    output_path = RAW_DATA_DIR / "florida_hurricanes_noaa.csv"
    florida_tracks.to_csv(output_path, index=False)
    print(f"   💾 Saved: {output_path}")

    return florida_tracks

def analyze_hurricane_stats(df):
    """Analyze hurricane statistics"""
    print("\n📈 Hurricane Statistics:")

    # Storm counts by year
    df['YEAR'] = pd.to_datetime(df['ISO_TIME']).dt.year

    storms_by_year = df.groupby('YEAR')['SID'].nunique()

    print(f"   📅 Years covered: {df['YEAR'].min()} - {df['YEAR'].max()}")
    print(f"   🌀 Average storms per year: {storms_by_year.mean():.1f}")
    print(f"   📊 Total unique storms: {df['SID'].nunique()}")

    # Wind speed stats (if available)
    if 'USA_WIND' in df.columns:
        df['USA_WIND'] = pd.to_numeric(df['USA_WIND'], errors='coerce')
        wind_data = df.dropna(subset=['USA_WIND'])
        if len(wind_data) > 0:
            print(f"   💨 Max wind speed: {wind_data['USA_WIND'].max():.0f} kt")
            print(f"   💨 Avg wind speed: {wind_data['USA_WIND'].mean():.0f} kt")

    # Category distribution (estimate from wind speed)
    df['CATEGORY'] = df.apply(lambda row: categorize_storm(row.get('USA_WIND', 0)), axis=1)
    cat_counts = df.groupby('SID')['CATEGORY'].max().value_counts().sort_index()

    print(f"\n   Storm Categories:")
    for cat, count in cat_counts.items():
        print(f"      {cat}: {count} storms")

def categorize_storm(wind_kt):
    """Categorize storm by Saffir-Simpson scale"""
    try:
        wind_kt = float(wind_kt)
    except:
        return "Unknown"

    if wind_kt >= 137:
        return "Category 5"
    elif wind_kt >= 113:
        return "Category 4"
    elif wind_kt >= 96:
        return "Category 3"
    elif wind_kt >= 83:
        return "Category 2"
    elif wind_kt >= 64:
        return "Category 1"
    elif wind_kt >= 34:
        return "Tropical Storm"
    else:
        return "Tropical Depression"

def create_hurricane_frequency_map():
    """Create county-level hurricane frequency data"""
    print("\n🗺️ Creating county-level hurricane frequency map...")

    # Load Florida counties
    counties_path = RAW_DATA_DIR / "florida_counties.geojson"
    if not counties_path.exists():
        print(f"   ⚠️ Counties file not found: {counties_path}")
        return None

    # Read GeoJSON directly to avoid Fiona path issues
    import json
    with open(counties_path, 'r') as f:
        geojson_data = json.load(f)

    counties_gdf = gpd.GeoDataFrame.from_features(geojson_data['features'], crs="EPSG:4326")

    # Load hurricane tracks
    hurricanes_path = RAW_DATA_DIR / "florida_hurricanes_noaa.csv"
    if not hurricanes_path.exists():
        print(f"   ⚠️ Hurricane data not found")
        return None

    df = pd.read_csv(hurricanes_path)

    # Convert to GeoDataFrame
    df['LAT'] = pd.to_numeric(df['LAT'], errors='coerce')
    df['LON'] = pd.to_numeric(df['LON'], errors='coerce')
    df = df.dropna(subset=['LAT', 'LON'])

    geometry = [Point(lon, lat) for lon, lat in zip(df['LON'], df['LAT'])]
    hurricanes_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

    # Spatial join to count hurricanes per county
    print("   🔄 Performing spatial join...")
    joined = gpd.sjoin(hurricanes_gdf, counties_gdf, how='inner', predicate='within')

    # Determine column name (varies based on GeoPandas version)
    name_col = 'NAME_right' if 'NAME_right' in joined.columns else 'NAME'

    # Count unique storms per county
    county_storm_counts = joined.groupby(name_col)['SID'].nunique().reset_index()
    county_storm_counts.columns = ['County', 'storm_count']

    # Calculate intensity metrics
    if 'USA_WIND' in joined.columns:
        joined['USA_WIND'] = pd.to_numeric(joined['USA_WIND'], errors='coerce')
        intensity_stats = joined.groupby(name_col)['USA_WIND'].agg(['mean', 'max']).reset_index()
        intensity_stats.columns = ['County', 'avg_wind_speed', 'max_wind_speed']

        county_storm_counts = county_storm_counts.merge(intensity_stats, on='County', how='left')

    # Save
    output_path = RAW_DATA_DIR / "county_hurricane_frequency.csv"
    county_storm_counts.to_csv(output_path, index=False)
    print(f"   ✅ Saved county frequency data: {output_path}")

    print(f"\n   Top 5 most affected counties:")
    top_5 = county_storm_counts.nlargest(5, 'storm_count')
    for _, row in top_5.iterrows():
        print(f"      {row['County']}: {row['storm_count']} storms")

    return county_storm_counts

def main():
    print("=" * 70)
    print("🌀 NOAA IBTrACS Hurricane Data Download & Processing")
    print("=" * 70)
    print()

    # Step 1: Download IBTrACS data
    df = download_ibtracs_data()

    if df is not None:
        # Step 2: Filter Florida hurricanes
        florida_df = filter_florida_hurricanes(df)

        # Step 3: Analyze statistics
        analyze_hurricane_stats(florida_df)

        # Step 4: Create county frequency map
        create_hurricane_frequency_map()

        print("\n" + "=" * 70)
        print("✅ HURRICANE DATA PROCESSING COMPLETE")
        print("=" * 70)
        print("\nNext: Run 'python scripts/calculate_real_hurricane_risk.py'")
        print("      to update vulnerability scores with real NOAA data")
        print("=" * 70)
    else:
        print("\n❌ Failed to download hurricane data")

if __name__ == "__main__":
    main()
