"""
Script para enriquecer datos de vulnerabilidad con datos de Statista
Incluye: valores de propiedades, zonas rurales, correlación FEMA-PIB
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import json

# Configurar rutas
BASE_DIR = Path(__file__).parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

def load_enriched_data():
    """Cargar datos enriquecidos de Statista"""
    print("📊 Cargando datos enriquecidos de Statista...")

    statista_path = RAW_DATA_DIR / "statista_enriched_data.csv"
    if not statista_path.exists():
        raise FileNotFoundError(f"No se encontró: {statista_path}")

    df = pd.read_csv(statista_path)
    print(f"   ✅ Cargados {len(df)} condados con datos enriquecidos")
    return df

def load_existing_vulnerability_data():
    """Cargar datos de vulnerabilidad existentes"""
    print("📍 Cargando datos de vulnerabilidad existentes...")

    counties_path = PROCESSED_DATA_DIR / "counties.geojson"

    with open(counties_path, 'r') as f:
        geojson_data = json.load(f)

    gdf = gpd.GeoDataFrame.from_features(geojson_data['features'], crs="EPSG:4326")
    print(f"   ✅ Cargados {len(gdf)} condados")
    return gdf

def calculate_enhanced_vulnerability(counties_gdf, statista_df):
    """
    Calcular vulnerabilidad mejorada con datos de Statista

    Nueva fórmula:
    Vulnerabilidad Mejorada =
        0.25 * Riesgo Huracán +
        0.20 * Vulnerabilidad Social +
        0.20 * Vulnerabilidad Económica (GDP) +
        0.20 * Exposición de Propiedades (valor casas) +
        0.15 * Factor Rural/Urbano
    """
    print("🧮 Calculando vulnerabilidad mejorada...")

    result = counties_gdf.copy()

    # Merge con datos de Statista
    statista_lookup = statista_df.set_index('County').to_dict('index')

    # Agregar nuevos campos
    new_fields = []
    for idx, row in result.iterrows():
        county_name = row['NAME']

        if county_name in statista_lookup:
            data = statista_lookup[county_name]
            new_fields.append({
                'median_home_value': data['median_home_value'],
                'property_growth_rate': data['annual_growth_percent'],
                'rural_status': data['rural_status'],
                'fema_risk_zone': data['fema_risk_zone'],
                'population_density': data['population_density']
            })
        else:
            # Valores por defecto si no hay datos
            new_fields.append({
                'median_home_value': 300000,
                'property_growth_rate': 3.5,
                'rural_status': 'suburban',
                'fema_risk_zone': 'moderate',
                'population_density': 200
            })

    new_df = pd.DataFrame(new_fields)
    result = pd.concat([result.reset_index(drop=True), new_df], axis=1)

    # Normalizar valores de propiedades (0-1)
    result['property_exposure'] = (result['median_home_value'] - result['median_home_value'].min()) / \
                                   (result['median_home_value'].max() - result['median_home_value'].min())

    # Factor rural (más vulnerable = 1, urbano = 0)
    rural_map = {
        'rural': 1.0,
        'rural_coastal': 0.9,
        'suburban': 0.4,
        'urban': 0.2
    }
    result['rural_factor'] = result['rural_status'].map(rural_map)

    # Factor FEMA (correlación con zona de riesgo)
    fema_map = {
        'very_high': 1.0,
        'high': 0.75,
        'moderate': 0.5,
        'low': 0.25
    }
    result['fema_risk_factor'] = result['fema_risk_zone'].map(fema_map)

    # Calcular vulnerabilidad mejorada
    result['enhanced_vulnerability'] = (
        0.25 * result['hurricane_risk'] +
        0.20 * result['social_vulnerability'] +
        0.20 * result['economic_vulnerability'] +
        0.20 * result['property_exposure'] +
        0.15 * result['rural_factor']
    )

    # Asegurar rango 0-1
    result['enhanced_vulnerability'] = result['enhanced_vulnerability'].clip(0, 1)

    # Categorizar riesgo mejorado
    def categorize_enhanced_risk(score):
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

    result['enhanced_risk_category'] = result['enhanced_vulnerability'].apply(categorize_enhanced_risk)

    # Calcular índice de correlación PIB-FEMA
    result['gdp_fema_correlation'] = result['gdp'] / 1000 * result['fema_risk_factor']

    # Identificar zonas críticas rurales (alta vulnerabilidad + rural)
    result['critical_rural'] = (
        (result['enhanced_vulnerability'] >= 0.7) &
        (result['rural_status'].isin(['rural', 'rural_coastal']))
    )

    print(f"   ✅ Vulnerabilidad mejorada calculada")
    print(f"      Media: {result['enhanced_vulnerability'].mean():.3f}")
    print(f"      Rango: {result['enhanced_vulnerability'].min():.3f} - {result['enhanced_vulnerability'].max():.3f}")
    print(f"      Zonas críticas rurales: {result['critical_rural'].sum()} condados")

    return result

def generate_enhanced_stats(gdf):
    """Generar estadísticas mejoradas"""
    print("📈 Generando estadísticas mejoradas...")

    # Top 10 por diferentes criterios
    top_vulnerability = gdf.nlargest(10, 'enhanced_vulnerability')[
        ['NAME', 'enhanced_vulnerability', 'rural_status', 'median_home_value']
    ].to_dict('records')

    top_property_exposure = gdf.nlargest(10, 'property_exposure')[
        ['NAME', 'median_home_value', 'property_growth_rate', 'fema_risk_zone']
    ].to_dict('records')

    critical_rural_zones = gdf[gdf['critical_rural']][
        ['NAME', 'enhanced_vulnerability', 'gdp', 'population_density']
    ].to_dict('records')

    stats = {
        'generated_at': pd.Timestamp.now().isoformat(),
        'total_counties': len(gdf),
        'enhanced_vulnerability_stats': {
            'mean': float(gdf['enhanced_vulnerability'].mean()),
            'median': float(gdf['enhanced_vulnerability'].median()),
            'std': float(gdf['enhanced_vulnerability'].std()),
            'min': float(gdf['enhanced_vulnerability'].min()),
            'max': float(gdf['enhanced_vulnerability'].max())
        },
        'property_value_stats': {
            'mean': float(gdf['median_home_value'].mean()),
            'median': float(gdf['median_home_value'].median()),
            'min': float(gdf['median_home_value'].min()),
            'max': float(gdf['median_home_value'].max())
        },
        'rural_distribution': gdf['rural_status'].value_counts().to_dict(),
        'fema_risk_distribution': gdf['fema_risk_zone'].value_counts().to_dict(),
        'enhanced_risk_category_counts': gdf['enhanced_risk_category'].value_counts().to_dict(),
        'critical_rural_zones_count': int(gdf['critical_rural'].sum()),
        'top_10_vulnerable_enhanced': top_vulnerability,
        'top_10_property_exposure': top_property_exposure,
        'critical_rural_zones': critical_rural_zones,
        'correlations': {
            'gdp_vulnerability': float(gdf['gdp'].corr(gdf['enhanced_vulnerability'])),
            'property_vulnerability': float(gdf['median_home_value'].corr(gdf['enhanced_vulnerability'])),
            'density_vulnerability': float(gdf['population_density'].corr(gdf['enhanced_vulnerability']))
        }
    }

    print("   ✅ Estadísticas mejoradas generadas")
    return stats

def save_enhanced_data(gdf, stats):
    """Guardar datos mejorados"""
    print("💾 Guardando datos mejorados...")

    # Guardar GeoJSON mejorado
    output_geojson = PROCESSED_DATA_DIR / "counties_enhanced.geojson"
    gdf_output = gdf.copy()
    gdf_output.to_file(output_geojson, driver="GeoJSON")
    print(f"   ✅ GeoJSON mejorado: {output_geojson}")

    # Guardar estadísticas mejoradas
    stats_path = PROCESSED_DATA_DIR / "enhanced_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"   ✅ Estadísticas mejoradas: {stats_path}")

    # Guardar CSV para análisis
    csv_path = PROCESSED_DATA_DIR / "counties_enhanced.csv"
    csv_df = gdf.copy()
    csv_df['geometry'] = csv_df['geometry'].apply(lambda x: str(x))
    csv_df.to_csv(csv_path, index=False)
    print(f"   ✅ CSV mejorado: {csv_path}")

def main():
    """Pipeline principal"""
    print("=" * 70)
    print("🚀 Enriquecimiento de Datos con Statista")
    print("=" * 70)
    print()

    try:
        # 1. Cargar datos
        statista_df = load_enriched_data()
        counties_gdf = load_existing_vulnerability_data()

        # 2. Calcular vulnerabilidad mejorada
        enhanced_gdf = calculate_enhanced_vulnerability(counties_gdf, statista_df)

        # 3. Generar estadísticas
        enhanced_stats = generate_enhanced_stats(enhanced_gdf)

        # 4. Guardar resultados
        save_enhanced_data(enhanced_gdf, enhanced_stats)

        print()
        print("=" * 70)
        print("✅ ENRIQUECIMIENTO COMPLETADO!")
        print("=" * 70)
        print(f"📊 {len(enhanced_gdf)} condados procesados")
        print(f"🔴 {enhanced_stats['critical_rural_zones_count']} zonas críticas rurales identificadas")
        print(f"📈 Correlación GDP-Vulnerabilidad: {enhanced_stats['correlations']['gdp_vulnerability']:.3f}")
        print(f"🏠 Correlación Propiedades-Vulnerabilidad: {enhanced_stats['correlations']['property_vulnerability']:.3f}")
        print()
        print("Archivos generados:")
        print("  - counties_enhanced.geojson")
        print("  - enhanced_stats.json")
        print("  - counties_enhanced.csv")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise

if __name__ == "__main__":
    main()
