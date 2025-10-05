"""
Calculate real hurricane risk using NOAA IBTrACS data
Updates vulnerability scores with real historical hurricane data
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

def load_hurricane_frequency():
    """Load county-level hurricane frequency data"""
    print("🌀 Loading NOAA hurricane frequency data...")

    freq_path = RAW_DATA_DIR / "county_hurricane_frequency.csv"
    if not freq_path.exists():
        raise FileNotFoundError(
            f"Hurricane frequency data not found: {freq_path}\n"
            "Please run 'python scripts/download_noaa_hurricanes.py' first"
        )

    df = pd.read_csv(freq_path)
    print(f"   ✅ Loaded hurricane data for {len(df)} counties")
    print(f"   📊 Storm count range: {df['storm_count'].min()} - {df['storm_count'].max()}")
    print(f"   💨 Avg wind range: {df['avg_wind_speed'].min():.1f} - {df['avg_wind_speed'].max():.1f} kt")

    return df

def calculate_hurricane_risk(frequency_df):
    """
    Calculate normalized hurricane risk score (0-1) based on:
    - Frequency: Number of historical storms
    - Intensity: Average and max wind speeds

    Formula:
    Risk = 0.5 * frequency_score + 0.3 * avg_intensity_score + 0.2 * max_intensity_score
    """
    print("\n🎯 Calculating real hurricane risk scores...")

    df = frequency_df.copy()

    # Normalize frequency (0-1)
    df['frequency_score'] = (df['storm_count'] - df['storm_count'].min()) / \
                             (df['storm_count'].max() - df['storm_count'].min())

    # Normalize average wind speed (0-1)
    # Tropical storm starts at 34 kt, Category 5 is 137+ kt
    df['avg_intensity_score'] = (df['avg_wind_speed'] - 34) / (137 - 34)
    df['avg_intensity_score'] = df['avg_intensity_score'].clip(0, 1)

    # Normalize max wind speed (0-1)
    df['max_intensity_score'] = (df['max_wind_speed'] - 34) / (160 - 34)  # 160 kt is extreme
    df['max_intensity_score'] = df['max_intensity_score'].clip(0, 1)

    # Calculate composite hurricane risk
    df['hurricane_risk_noaa'] = (
        0.50 * df['frequency_score'] +
        0.30 * df['avg_intensity_score'] +
        0.20 * df['max_intensity_score']
    )

    # Ensure 0-1 range
    df['hurricane_risk_noaa'] = df['hurricane_risk_noaa'].clip(0, 1)

    print(f"   ✅ Calculated hurricane risk scores")
    print(f"      Mean risk: {df['hurricane_risk_noaa'].mean():.3f}")
    print(f"      Range: {df['hurricane_risk_noaa'].min():.3f} - {df['hurricane_risk_noaa'].max():.3f}")

    # Show top 10 highest risk
    top_10 = df.nlargest(10, 'hurricane_risk_noaa')[['County', 'hurricane_risk_noaa', 'storm_count', 'max_wind_speed']]
    print(f"\n   Top 10 highest hurricane risk counties:")
    for _, row in top_10.iterrows():
        print(f"      {row['County']}: {row['hurricane_risk_noaa']:.3f} ({row['storm_count']} storms, max {row['max_wind_speed']:.0f}kt)")

    return df[['County', 'hurricane_risk_noaa', 'storm_count', 'avg_wind_speed', 'max_wind_speed']]

def update_vulnerability_with_noaa_risk(risk_df):
    """Update existing vulnerability calculations with real NOAA hurricane risk"""
    print("\n🔄 Updating vulnerability scores with NOAA data...")

    # Load existing counties data
    counties_path = PROCESSED_DATA_DIR / "counties.geojson"

    if not counties_path.exists():
        raise FileNotFoundError(
            f"Counties data not found: {counties_path}\n"
            "Please run 'python scripts/process_data.py' first"
        )

    # Read GeoJSON
    with open(counties_path, 'r') as f:
        geojson_data = json.load(f)

    gdf = gpd.GeoDataFrame.from_features(geojson_data['features'], crs="EPSG:4326")

    # Merge with NOAA risk data
    risk_lookup = dict(zip(risk_df['County'], risk_df['hurricane_risk_noaa']))

    # Update hurricane_risk with NOAA data
    gdf['hurricane_risk_old'] = gdf['hurricane_risk']  # Keep old for comparison
    gdf['hurricane_risk'] = gdf['NAME'].map(risk_lookup)

    # Handle counties without NOAA data (use old risk)
    gdf['hurricane_risk'] = gdf['hurricane_risk'].fillna(gdf['hurricane_risk_old'])

    # Recalculate vulnerability score with new hurricane risk
    # Original formula: 0.4 * hurricane_risk + 0.3 * social_vuln + 0.3 * economic_vuln
    gdf['vulnerability_score'] = (
        0.40 * gdf['hurricane_risk'] +
        0.30 * gdf['social_vulnerability'] +
        0.30 * gdf['economic_vulnerability']
    ).clip(0, 1)

    # Update risk categories
    def categorize_risk(score):
        if score >= 0.8:
            return "Critical"
        elif score >= 0.6:
            return "High"
        elif score >= 0.4:
            return "Moderate"
        elif score >= 0.2:
            return "Low"
        else:
            return "Very Low"

    gdf['risk_category'] = gdf['vulnerability_score'].apply(categorize_risk)

    # Add NOAA metadata
    for col in ['storm_count', 'avg_wind_speed', 'max_wind_speed']:
        if col in risk_df.columns:
            lookup = dict(zip(risk_df['County'], risk_df[col]))
            gdf[col] = gdf['NAME'].map(lookup)

    print(f"   ✅ Updated vulnerability scores")
    print(f"      New mean vulnerability: {gdf['vulnerability_score'].mean():.3f}")
    print(f"      Mean hurricane risk change: {(gdf['hurricane_risk'] - gdf['hurricane_risk_old']).mean():.3f}")

    # Compare changes
    biggest_changes = (gdf['hurricane_risk'] - gdf['hurricane_risk_old']).abs().nlargest(5)
    print(f"\n   Counties with biggest risk changes:")
    for idx in biggest_changes.index:
        name = gdf.loc[idx, 'NAME']
        old_risk = gdf.loc[idx, 'hurricane_risk_old']
        new_risk = gdf.loc[idx, 'hurricane_risk']
        print(f"      {name}: {old_risk:.3f} → {new_risk:.3f} (Δ{new_risk-old_risk:+.3f})")

    return gdf

def save_updated_data(gdf):
    """Save updated vulnerability data"""
    print("\n💾 Saving updated data...")

    # Remove old risk column
    if 'hurricane_risk_old' in gdf.columns:
        gdf = gdf.drop(columns=['hurricane_risk_old'])

    # Save GeoJSON with NOAA data
    output_path = PROCESSED_DATA_DIR / "counties_noaa.geojson"
    gdf.to_file(output_path, driver="GeoJSON")
    print(f"   ✅ Saved NOAA-enhanced GeoJSON: {output_path}")

    # Also update main counties file
    main_path = PROCESSED_DATA_DIR / "counties.geojson"
    gdf.to_file(main_path, driver="GeoJSON")
    print(f"   ✅ Updated main counties file: {main_path}")

    # Save CSV
    csv_gdf = gdf.copy()
    csv_gdf['geometry'] = csv_gdf['geometry'].apply(lambda x: str(x))
    csv_path = PROCESSED_DATA_DIR / "counties_noaa.csv"
    csv_gdf.to_csv(csv_path, index=False)
    print(f"   ✅ Saved CSV: {csv_path}")

    # Update summary stats
    stats = {
        'generated_at': datetime.now().isoformat(),
        'data_source': 'NOAA IBTrACS',
        'total_counties': len(gdf),
        'hurricane_risk_stats': {
            'mean': float(gdf['hurricane_risk'].mean()),
            'median': float(gdf['hurricane_risk'].median()),
            'std': float(gdf['hurricane_risk'].std()),
            'min': float(gdf['hurricane_risk'].min()),
            'max': float(gdf['hurricane_risk'].max())
        },
        'vulnerability_stats': {
            'mean': float(gdf['vulnerability_score'].mean()),
            'median': float(gdf['vulnerability_score'].median()),
            'std': float(gdf['vulnerability_score'].std()),
            'min': float(gdf['vulnerability_score'].min()),
            'max': float(gdf['vulnerability_score'].max())
        },
        'risk_category_counts': gdf['risk_category'].value_counts().to_dict(),
        'top_10_vulnerable': gdf.nlargest(10, 'vulnerability_score')[
            ['NAME', 'vulnerability_score', 'hurricane_risk', 'storm_count']
        ].to_dict('records'),
        'noaa_data': {
            'total_historical_storms': 704,
            'date_range': '1851-2023',
            'categories_included': ['Category 1-5', 'Tropical Storms', 'Tropical Depressions']
        }
    }

    stats_path = PROCESSED_DATA_DIR / "summary_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"   ✅ Updated summary stats: {stats_path}")

def main():
    print("=" * 70)
    print("🌀 Real Hurricane Risk Calculation (NOAA IBTrACS)")
    print("=" * 70)
    print()

    try:
        # Step 1: Load hurricane frequency data
        frequency_df = load_hurricane_frequency()

        # Step 2: Calculate real hurricane risk
        risk_df = calculate_hurricane_risk(frequency_df)

        # Step 3: Update vulnerability scores
        updated_gdf = update_vulnerability_with_noaa_risk(risk_df)

        # Step 4: Save updated data
        save_updated_data(updated_gdf)

        print("\n" + "=" * 70)
        print("✅ REAL HURRICANE RISK CALCULATION COMPLETE!")
        print("=" * 70)
        print(f"📊 Updated {len(updated_gdf)} counties with real NOAA data")
        print(f"🌀 Based on 704 historical storms (1851-2023)")
        print()
        print("Next steps:")
        print("1. Restart backend to load new data")
        print("2. View updated vulnerability map")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise

if __name__ == "__main__":
    main()
