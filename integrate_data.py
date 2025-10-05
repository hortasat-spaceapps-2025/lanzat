#!/usr/bin/env python3
"""
Lanzat Data Integration Script
Merges all datasets into a single vulnerability map GeoJSON

Usage:
    python integrate_data.py

Prerequisites:
    - All datasets downloaded (run download_data.py first)
    - Manual downloads completed (CDC SVI, FEMA NRI)
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
import json
import sys

DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def check_prerequisites():
    """Check if all required files exist"""
    required_files = {
        'florida_counties.geojson': 'Florida county boundaries',
        'florida_hurricanes.csv': 'Hurricane tracks (run download_data.py --process)',
        'florida_gdp_2023.csv': 'County GDP data (run download_data.py --process)',
        'florida_svi_2022.csv': 'CDC Social Vulnerability Index (manual download)',
        'fema_nri_florida.csv': 'FEMA National Risk Index (manual download)'
    }

    missing_files = []
    for filename, description in required_files.items():
        filepath = DATA_DIR / filename
        if not filepath.exists():
            missing_files.append(f"✗ {filename} - {description}")
        else:
            size = filepath.stat().st_size / 1024 / 1024
            print(f"✓ {filename} ({size:.1f} MB)")

    if missing_files:
        print("\n❌ Missing required files:")
        for missing in missing_files:
            print(f"   {missing}")
        print("\nPlease download missing files and try again.")
        return False

    return True

def calculate_hurricane_frequency(hurricane_data, county_geom, years=20):
    """Calculate hurricane frequency for a county"""
    try:
        # Create points from hurricane tracks
        hurricane_points = gpd.GeoDataFrame(
            hurricane_data,
            geometry=gpd.points_from_xy(hurricane_data.LON, hurricane_data.LAT),
            crs='EPSG:4326'
        )

        # Filter for recent years
        hurricane_points = hurricane_points[
            pd.to_datetime(hurricane_points['ISO_TIME']).dt.year >= (2024 - years)
        ]

        # Count hurricanes within county
        within_county = hurricane_points[hurricane_points.within(county_geom)]
        frequency = len(within_county) / years

        # Count major hurricanes (Cat 3+)
        major_hurricanes = within_county[within_county['USA_WIND'] >= 96]
        major_freq = len(major_hurricanes) / years

        return frequency, major_freq

    except Exception as e:
        print(f"Warning: Error calculating hurricane frequency: {e}")
        return 0, 0

def calculate_vulnerability_score(row):
    """
    Calculate composite vulnerability score (0-1)
    Based on research methodologies from FEMA Hazus and academic literature
    """
    # 1. Social Vulnerability (40% weight)
    svi_score = row.get('RPL_THEMES', 0.5)  # Overall SVI percentile

    # 2. Hurricane Risk (40% weight)
    risk_map = {
        'Very Low': 0.1,
        'Relatively Low': 0.3,
        'Relatively Moderate': 0.5,
        'Relatively High': 0.7,
        'Very High': 0.9,
        'Not Applicable': 0.0
    }
    hurricane_score = risk_map.get(row.get('HRCN_RISKR', 'Relatively Moderate'), 0.5)

    # 3. Economic Vulnerability (20% weight)
    # Lower GDP per capita = higher vulnerability
    gdp_per_capita = row.get('GDP_PER_CAPITA', 50000)
    max_gdp_per_capita = 150000  # Normalize against $150k
    economic_score = 1 - min(gdp_per_capita / max_gdp_per_capita, 1)

    # Weighted combination
    vulnerability_score = (
        svi_score * 0.4 +
        hurricane_score * 0.4 +
        economic_score * 0.2
    )

    return round(vulnerability_score, 4)

def calculate_risk_category(score):
    """Categorize vulnerability score"""
    if score >= 0.8:
        return 'Critical'
    elif score >= 0.6:
        return 'High'
    elif score >= 0.4:
        return 'Moderate'
    elif score >= 0.2:
        return 'Low'
    else:
        return 'Very Low'

def integrate_datasets():
    """Main integration function"""

    print("\n" + "="*60)
    print("LANZAT DATA INTEGRATION")
    print("="*60)

    # Check prerequisites
    print("\nChecking for required files...")
    if not check_prerequisites():
        sys.exit(1)

    print("\n" + "="*60)
    print("LOADING DATASETS")
    print("="*60)

    # 1. Load county boundaries (base layer)
    print("\n1. Loading Florida county boundaries...")
    counties = gpd.read_file(DATA_DIR / 'florida_counties.geojson')
    print(f"   ✓ Loaded {len(counties)} counties")

    # Ensure FIPS is string and properly formatted
    if 'FIPS' in counties.columns:
        counties['FIPS'] = counties['FIPS'].astype(str).str.zfill(5)
    else:
        print("   ⚠ Warning: FIPS column not found, trying to extract from properties")
        # Try to extract FIPS from properties or create from state/county codes

    # 2. Load GDP data
    print("\n2. Loading GDP data...")
    gdp = pd.read_csv(DATA_DIR / 'florida_gdp_2023.csv')
    print(f"   ✓ Loaded GDP for {len(gdp)} counties")

    # Standardize FIPS
    if 'COUNTY_FIPS' in gdp.columns:
        gdp['FIPS'] = '12' + gdp['COUNTY_FIPS'].astype(str).str.zfill(3)
    elif 'FIPS' in gdp.columns:
        gdp['FIPS'] = gdp['FIPS'].astype(str).str.zfill(5)

    # 3. Load CDC SVI data
    print("\n3. Loading CDC Social Vulnerability Index...")
    svi = pd.read_csv(DATA_DIR / 'florida_svi_2022.csv')
    print(f"   ✓ Loaded SVI for {len(svi)} areas")

    # Standardize FIPS
    if 'FIPS' in svi.columns:
        svi['FIPS'] = svi['FIPS'].astype(str).str.zfill(5)

    # Select key SVI columns
    svi_columns = ['FIPS', 'COUNTY', 'RPL_THEMES', 'RPL_THEME1', 'RPL_THEME2', 'RPL_THEME3', 'RPL_THEME4',
                   'E_TOTPOP', 'EP_POV150', 'EP_UNINSUR', 'EP_UNEMP']
    svi_subset = svi[[col for col in svi_columns if col in svi.columns]]

    # 4. Load FEMA NRI data
    print("\n4. Loading FEMA National Risk Index...")
    nri = pd.read_csv(DATA_DIR / 'fema_nri_florida.csv')
    print(f"   ✓ Loaded NRI for {len(nri)} areas")

    # Standardize FIPS
    if 'STCOFIPS' in nri.columns:
        nri['FIPS'] = nri['STCOFIPS'].astype(str).str.zfill(5)
    elif 'FIPS' in nri.columns:
        nri['FIPS'] = nri['FIPS'].astype(str).str.zfill(5)

    # Select key NRI columns
    nri_columns = ['FIPS', 'HRCN_RISKR', 'HRCN_EEAL', 'HRCN_AFREQ', 'RISK_RATNG', 'SOVI_RATNG']
    nri_subset = nri[[col for col in nri_columns if col in nri.columns]]

    # 5. Load hurricane data
    print("\n5. Loading hurricane track data...")
    hurricanes = pd.read_csv(DATA_DIR / 'florida_hurricanes.csv')
    print(f"   ✓ Loaded {len(hurricanes)} hurricane data points")

    print("\n" + "="*60)
    print("MERGING DATASETS")
    print("="*60)

    # Merge all datasets
    print("\nMerging datasets by FIPS code...")
    vulnerability_map = counties.copy()

    # Merge GDP
    vulnerability_map = vulnerability_map.merge(
        gdp[['FIPS', 'GeoName', 'GDP_2023']],
        on='FIPS',
        how='left',
        suffixes=('', '_gdp')
    )
    print(f"   ✓ Merged GDP data: {vulnerability_map['GDP_2023'].notna().sum()} matches")

    # Merge SVI
    vulnerability_map = vulnerability_map.merge(
        svi_subset,
        on='FIPS',
        how='left',
        suffixes=('', '_svi')
    )
    print(f"   ✓ Merged SVI data: {vulnerability_map['RPL_THEMES'].notna().sum()} matches")

    # Merge NRI
    vulnerability_map = vulnerability_map.merge(
        nri_subset,
        on='FIPS',
        how='left',
        suffixes=('', '_nri')
    )
    print(f"   ✓ Merged NRI data: {vulnerability_map['HRCN_RISKR'].notna().sum()} matches")

    print("\n" + "="*60)
    print("CALCULATING METRICS")
    print("="*60)

    # Calculate derived metrics
    print("\nCalculating vulnerability scores...")

    # GDP per capita (assuming population from SVI)
    if 'E_TOTPOP' in vulnerability_map.columns:
        vulnerability_map['GDP_PER_CAPITA'] = (
            vulnerability_map['GDP_2023'] * 1000000 / vulnerability_map['E_TOTPOP']
        ).fillna(50000)  # Default if missing
    else:
        vulnerability_map['GDP_PER_CAPITA'] = 50000  # Default estimate

    # Calculate vulnerability score for each county
    vulnerability_map['VULNERABILITY_SCORE'] = vulnerability_map.apply(
        calculate_vulnerability_score,
        axis=1
    )

    # Risk category
    vulnerability_map['RISK_CATEGORY'] = vulnerability_map['VULNERABILITY_SCORE'].apply(
        calculate_risk_category
    )

    # Calculate rankings
    vulnerability_map['VULNERABILITY_RANK'] = vulnerability_map['VULNERABILITY_SCORE'].rank(
        ascending=False,
        method='min'
    ).astype(int)

    print(f"   ✓ Calculated vulnerability scores for {len(vulnerability_map)} counties")

    print("\n" + "="*60)
    print("STATISTICS")
    print("="*60)

    # Summary statistics
    stats = {
        'total_counties': len(vulnerability_map),
        'avg_vulnerability': vulnerability_map['VULNERABILITY_SCORE'].mean(),
        'critical_counties': len(vulnerability_map[vulnerability_map['RISK_CATEGORY'] == 'Critical']),
        'high_risk_counties': len(vulnerability_map[vulnerability_map['RISK_CATEGORY'] == 'High']),
        'total_gdp': vulnerability_map['GDP_2023'].sum(),
        'avg_svi': vulnerability_map['RPL_THEMES'].mean(),
        'total_population': vulnerability_map.get('E_TOTPOP', pd.Series([0])).sum()
    }

    print(f"\n📊 SUMMARY STATISTICS:")
    print(f"   Total counties: {stats['total_counties']}")
    print(f"   Average vulnerability: {stats['avg_vulnerability']:.3f}")
    print(f"   Critical risk: {stats['critical_counties']} counties")
    print(f"   High risk: {stats['high_risk_counties']} counties")
    print(f"   Total GDP: ${stats['total_gdp']:.1f}B")
    print(f"   Average SVI: {stats['avg_svi']:.3f}")
    if stats['total_population'] > 0:
        print(f"   Total population: {stats['total_population']:,.0f}")

    # Top vulnerable counties
    print(f"\n🔴 TOP 10 MOST VULNERABLE COUNTIES:")
    top_10 = vulnerability_map.nlargest(10, 'VULNERABILITY_SCORE')[
        ['GeoName', 'VULNERABILITY_SCORE', 'RISK_CATEGORY', 'HRCN_RISKR', 'RPL_THEMES']
    ]
    for idx, row in top_10.iterrows():
        print(f"   {row['VULNERABILITY_RANK']:.0f}. {row.get('GeoName', 'Unknown')}: {row['VULNERABILITY_SCORE']:.3f} ({row['RISK_CATEGORY']})")

    print("\n" + "="*60)
    print("SAVING OUTPUT")
    print("="*60)

    # Save integrated GeoJSON
    output_geojson = OUTPUT_DIR / 'vulnerability_map.geojson'
    vulnerability_map.to_file(output_geojson, driver='GeoJSON')
    size = output_geojson.stat().st_size / 1024 / 1024
    print(f"\n✓ Saved: {output_geojson} ({size:.1f} MB)")

    # Save CSV (without geometry)
    output_csv = OUTPUT_DIR / 'vulnerability_data.csv'
    vulnerability_map.drop(columns=['geometry']).to_csv(output_csv, index=False)
    size = output_csv.stat().st_size / 1024 / 1024
    print(f"✓ Saved: {output_csv} ({size:.1f} MB)")

    # Save summary statistics
    stats_file = OUTPUT_DIR / 'summary_stats.json'
    # Convert non-serializable values
    stats_json = {k: float(v) if isinstance(v, (int, float)) else v for k, v in stats.items()}
    with open(stats_file, 'w') as f:
        json.dump(stats_json, f, indent=2)
    print(f"✓ Saved: {stats_file}")

    # Save top vulnerable counties list
    top_vulnerable_file = OUTPUT_DIR / 'top_vulnerable_counties.json'
    top_vulnerable_json = top_10.to_dict(orient='records')
    with open(top_vulnerable_file, 'w') as f:
        json.dump(top_vulnerable_json, f, indent=2)
    print(f"✓ Saved: {top_vulnerable_file}")

    print("\n" + "="*60)
    print("INTEGRATION COMPLETE ✨")
    print("="*60)

    print("\n📁 Output files created:")
    print(f"   • vulnerability_map.geojson - Full dataset with geometry")
    print(f"   • vulnerability_data.csv - Tabular data without geometry")
    print(f"   • summary_stats.json - Summary statistics")
    print(f"   • top_vulnerable_counties.json - Top 10 list")

    print("\n🚀 Next steps:")
    print("   1. Load vulnerability_map.geojson in your frontend")
    print("   2. Use summary_stats.json for dashboard KPIs")
    print("   3. Start your API server and serve the data")
    print("   4. Build the interactive map!")

    return vulnerability_map

if __name__ == "__main__":
    try:
        vulnerability_map = integrate_datasets()
        print("\n✨ Success! Data integration complete.\n")
    except Exception as e:
        print(f"\n❌ Error during integration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
