"""
Quick setup script to create sample data for demo
This creates realistic sample data for all 67 Florida counties
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import json
from shapely.geometry import Polygon, Point

# Configure paths
BASE_DIR = Path(__file__).parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# All 67 Florida counties with approximate coordinates
FLORIDA_COUNTIES = {
    'Alachua': (29.6516, -82.3248), 'Baker': (30.3319, -82.2873),
    'Bay': (30.1588, -85.6602), 'Bradford': (29.9467, -82.1729),
    'Brevard': (28.2639, -80.7214), 'Broward': (26.1224, -80.1373),
    'Calhoun': (30.3802, -85.1994), 'Charlotte': (26.8937, -81.9673),
    'Citrus': (28.8894, -82.4843), 'Clay': (29.9766, -81.7290),
    'Collier': (26.1420, -81.7206), 'Columbia': (30.1910, -82.6401),
    'DeSoto': (27.1620, -81.8092), 'Dixie': (29.5966, -83.0924),
    'Duval': (30.3322, -81.6557), 'Escambia': (30.6301, -87.2169),
    'Flagler': (29.4677, -81.2528), 'Franklin': (29.8491, -84.8800),
    'Gadsden': (30.5833, -84.6199), 'Gilchrist': (29.7447, -82.8290),
    'Glades': (26.9456, -81.1023), 'Gulf': (29.9932, -85.2441),
    'Hamilton': (30.5228, -82.9646), 'Hardee': (27.4823, -81.8206),
    'Hendry': (26.5573, -81.2023), 'Hernando': (28.5369, -82.4654),
    'Highlands': (27.3167, -81.3323), 'Hillsborough': (27.9904, -82.3018),
    'Holmes': (30.8293, -85.8602), 'Indian River': (27.6648, -80.5256),
    'Jackson': (30.7802, -85.2441), 'Jefferson': (30.5461, -83.8682),
    'Lafayette': (30.0128, -83.2107), 'Lake': (28.8039, -81.6326),
    'Lee': (26.5629, -81.8495), 'Leon': (30.4583, -84.2533),
    'Levy': (29.2997, -82.7812), 'Liberty': (30.2388, -84.8824),
    'Madison': (30.4662, -83.4129), 'Manatee': (27.4989, -82.3251),
    'Marion': (29.1997, -82.0403), 'Martin': (27.1003, -80.3883),
    'Miami-Dade': (25.6206, -80.4926), 'Monroe': (24.7593, -81.2473),
    'Nassau': (30.6116, -81.7837), 'Okaloosa': (30.6302, -86.5665),
    'Okeechobee': (27.2439, -80.8295), 'Orange': (28.4742, -81.2394),
    'Osceola': (28.0984, -81.0784), 'Palm Beach': (26.6517, -80.1090),
    'Pasco': (28.2993, -82.4423), 'Pinellas': (27.8715, -82.6806),
    'Polk': (28.0002, -81.7325), 'Putnam': (29.6495, -81.6757),
    'St. Johns': (29.8986, -81.3124), 'St. Lucie': (27.3467, -80.3883),
    'Santa Rosa': (30.6802, -86.9165), 'Sarasota': (27.2440, -82.2848),
    'Seminole': (28.7011, -81.2373), 'Sumter': (28.6950, -82.0598),
    'Suwannee': (30.1910, -83.0135), 'Taylor': (30.0589, -83.5818),
    'Union': (30.0584, -82.4287), 'Volusia': (29.0280, -81.0784),
    'Wakulla': (30.1549, -84.3963), 'Walton': (30.6302, -86.1165),
    'Washington': (30.6136, -85.6485)
}

def create_county_polygon(center_lat, center_lon, size=0.5):
    """Create a simple rectangular polygon for a county"""
    half_size = size / 2
    return Polygon([
        (center_lon - half_size, center_lat - half_size),
        (center_lon + half_size, center_lat - half_size),
        (center_lon + half_size, center_lat + half_size),
        (center_lon - half_size, center_lat + half_size),
        (center_lon - half_size, center_lat - half_size)
    ])

def create_florida_counties_geojson():
    """Create a GeoDataFrame with Florida counties"""
    print("🗺️  Creating Florida county geometries...")

    # Create features
    features = []
    for county_name, (lat, lon) in FLORIDA_COUNTIES.items():
        features.append({
            'NAME': county_name,
            'STATEFP': '12',  # Florida FIPS code
            'COUNTYFP': f'{len(features):03d}',
            'GEOID': f'12{len(features):03d}',
            'geometry': create_county_polygon(lat, lon)
        })

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(features, crs="EPSG:4326")

    # Save
    output_path = RAW_DATA_DIR / "florida_counties.geojson"
    gdf.to_file(output_path, driver="GeoJSON")

    print(f"✅ Created {len(gdf)} Florida counties: {output_path}")
    return gdf

def create_sample_gdp_data():
    """Create realistic GDP data for Florida counties"""
    print("💰 Creating sample GDP data...")

    # Realistic GDP ranges (in millions)
    gdp_ranges = {
        'Miami-Dade': (170000, 190000), 'Broward': (110000, 130000),
        'Palm Beach': (85000, 95000), 'Hillsborough': (80000, 90000),
        'Orange': (90000, 100000), 'Pinellas': (50000, 60000),
        'Lee': (35000, 45000), 'Polk': (28000, 32000),
        'Duval': (75000, 85000), 'Collier': (30000, 40000),
        'Sarasota': (30000, 40000), 'Seminole': (25000, 30000),
        'Volusia': (20000, 25000), 'Brevard': (25000, 35000),
        'Pasco': (18000, 24000), 'Manatee': (18000, 22000),
        'Leon': (16000, 20000), 'St. Lucie': (12000, 16000),
        'Escambia': (20000, 28000), 'Lake': (18000, 22000),
        'Marion': (10000, 14000), 'St. Johns': (16000, 20000),
    }

    gdp_data = []
    for county_name in FLORIDA_COUNTIES.keys():
        if county_name in gdp_ranges:
            min_gdp, max_gdp = gdp_ranges[county_name]
            gdp = np.random.randint(min_gdp, max_gdp)
        else:
            # Smaller counties
            gdp = np.random.randint(300, 5000)

        gdp_data.append({'County': county_name, 'GDP_2022': gdp})

    df = pd.DataFrame(gdp_data)
    output_path = RAW_DATA_DIR / "county_gdp.csv"
    df.to_csv(output_path, index=False)

    print(f"✅ Created GDP data for {len(df)} counties: {output_path}")
    return df

def create_sample_hurricane_data():
    """Create sample hurricane track data"""
    print("🌀 Creating sample hurricane data...")

    # Coastal counties have higher risk
    coastal_counties = [
        'Miami-Dade', 'Broward', 'Palm Beach', 'Monroe', 'Collier', 'Lee',
        'Charlotte', 'Sarasota', 'Manatee', 'Pinellas', 'Hillsborough',
        'Pasco', 'Hernando', 'Citrus', 'Levy', 'Dixie', 'Taylor',
        'Wakulla', 'Franklin', 'Gulf', 'Bay', 'Walton', 'Okaloosa',
        'Santa Rosa', 'Escambia', 'Nassau', 'Duval', 'St. Johns',
        'Flagler', 'Volusia', 'Brevard', 'Indian River', 'St. Lucie', 'Martin'
    ]

    # Create simple risk scores
    risk_data = []
    for county_name, (lat, lon) in FLORIDA_COUNTIES.items():
        if county_name in coastal_counties:
            risk = np.random.uniform(0.65, 0.95)
        else:
            risk = np.random.uniform(0.25, 0.55)

        risk_data.append({
            'County': county_name,
            'LAT': lat,
            'LON': lon,
            'Risk': risk
        })

    df = pd.DataFrame(risk_data)
    output_path = RAW_DATA_DIR / "florida_hurricanes.csv"
    df.to_csv(output_path, index=False)

    print(f"✅ Created hurricane risk data: {output_path}")
    return df

def create_sample_svi_data():
    """Create sample social vulnerability data"""
    print("👥 Creating sample social vulnerability data...")

    svi_data = []
    for county_name in FLORIDA_COUNTIES.keys():
        # Urban areas tend to have higher diversity in vulnerability
        if county_name in ['Miami-Dade', 'Broward', 'Hillsborough', 'Orange']:
            svi = np.random.uniform(0.45, 0.85)
        elif county_name in ['Monroe', 'Glades', 'Union', 'Lafayette', 'Liberty']:
            # Rural/small counties higher vulnerability
            svi = np.random.uniform(0.55, 0.90)
        else:
            svi = np.random.uniform(0.30, 0.70)

        svi_data.append({'County': county_name, 'SVI': svi})

    df = pd.DataFrame(svi_data)
    output_path = RAW_DATA_DIR / "cdc_svi_florida.csv"
    df.to_csv(output_path, index=False)

    print(f"✅ Created SVI data for {len(df)} counties: {output_path}")
    return df

def main():
    """Run quick setup"""
    print("=" * 70)
    print("🚀 Lanzat Quick Setup")
    print("   Creating sample data for 67 Florida counties...")
    print("=" * 70)
    print()

    # Create all sample data
    counties_gdf = create_florida_counties_geojson()
    gdp_df = create_sample_gdp_data()
    hurricane_df = create_sample_hurricane_data()
    svi_df = create_sample_svi_data()

    print()
    print("=" * 70)
    print("✅ QUICK SETUP COMPLETE!")
    print("=" * 70)
    print(f"📁 All data saved to: {RAW_DATA_DIR}")
    print()
    print("🔜 Next step: Run 'python scripts/process_data.py'")
    print("=" * 70)

if __name__ == "__main__":
    main()
