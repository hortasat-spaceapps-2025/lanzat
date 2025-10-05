# Lanzat Project - Comprehensive Resource Guide

**Last Updated:** October 4, 2025
**Project:** Hurricane Economic Vulnerability Platform for Florida

---

## Table of Contents
1. [Hurricane & Disaster Data](#1-hurricane--disaster-data)
2. [Economic Data (County GDP)](#2-economic-data-county-gdp)
3. [Social Vulnerability Data](#3-social-vulnerability-data)
4. [Geospatial Boundaries](#4-geospatial-boundaries)
5. [Satellite Imagery (Optional)](#5-satellite-imagery-optional)
6. [APIs & Web Services](#6-apis--web-services)
7. [Development Libraries & Tools](#7-development-libraries--tools)
8. [Research & Methodologies](#8-research--methodologies)
9. [Quick Start Download Script](#9-quick-start-download-script)
10. [Data Processing Order](#10-data-processing-order)

---

## 1. HURRICANE & DISASTER DATA

### 1.1 NOAA IBTrACS (International Best Track Archive) ⭐ CRITICAL

**Source:** NOAA National Centers for Environmental Information
**URL:** https://www.ncei.noaa.gov/products/international-best-track-archive
**Data Type:** CSV, NetCDF, Shapefile
**Coverage:** Global tropical cyclones, 1840s-present (150+ years)
**File Size:** ~50-200MB (varies by format and subset)
**Free Tier:** Unlimited, no registration required

**Access Instructions:**
1. Visit the IBTrACS data portal
2. Choose data format:
   - **CSV:** https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/
   - **Shapefile:** https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/shapefile/
   - **NetCDF:** https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/netcdf/
3. Filter for North Atlantic basin (NA) for Florida hurricanes
4. Download subsets:
   - `ibtracs.since1980.list.v04r01.csv` - Modern satellite era (~10MB)
   - `ibtracs.NA.list.v04r01.csv` - North Atlantic only (~30MB)
   - `ibtracs.ALL.list.v04r01.csv` - Complete dataset (~200MB)

**Data Quality:**
- Completeness: ✅ Excellent - All documented Atlantic hurricanes
- Timeliness: ✅ Updated regularly (within 24-48 hours)
- Format: ✅ Easy - Well-documented CSV format

**Sample Usage:**
```python
import pandas as pd
import geopandas as gpd

# Download and load IBTrACS data
ibtracs = pd.read_csv('ibtracs.NA.list.v04r01.csv', skiprows=1)

# Filter for Florida region
florida_bounds = {'min_lat': 24.5, 'max_lat': 31.0, 'min_lon': -87.6, 'max_lon': -80.0}
florida_hurricanes = ibtracs[
    (ibtracs['LAT'] >= florida_bounds['min_lat']) &
    (ibtracs['LAT'] <= florida_bounds['max_lat']) &
    (ibtracs['LON'] >= florida_bounds['min_lon']) &
    (ibtracs['LON'] <= florida_bounds['max_lon'])
]

# Filter for major hurricanes (Category 3+) since 2000
major_hurricanes = florida_hurricanes[
    (ibtracs['USA_WIND'] >= 96) &
    (pd.to_datetime(ibtracs['ISO_TIME']).dt.year >= 2000)
]
```

**Alternatives:**
- **NOAA Historical Hurricane Tracks Tool:** https://coast.noaa.gov/hurricanes/ - Interactive map with export options
- **NHC Data Archive:** https://www.nhc.noaa.gov/data/ - HURDAT2 format (more detailed)

**Notes:**
- CSV format includes: storm name, date/time, lat/lon, wind speed, pressure, category
- Use `USA_WIND` column for maximum sustained winds in knots
- Filter by `BASIN='NA'` for North Atlantic
- Major Florida hurricanes to include: Ian (2022), Michael (2018), Irma (2017), Charley (2004)

---

### 1.2 FEMA National Risk Index ⭐ CRITICAL

**Source:** Federal Emergency Management Agency
**URL:** https://hazards.fema.gov/nri/data-resources
**Data Type:** Geodatabase, Shapefile, CSV
**Coverage:** All U.S. counties and census tracts
**File Size:** ~500MB-2GB (full dataset), ~20-50MB (Florida only)
**Free Tier:** Unlimited downloads, no registration

**Access Instructions:**
1. Visit https://hazards.fema.gov/nri/data-resources
2. Select download format:
   - **National dataset** (includes Florida): All states in single file
   - **State-specific**: Florida data only (recommended for faster download)
3. Choose data level:
   - **County level** (67 Florida counties) - Recommended for MVP
   - **Census tract level** (4,200+ tracts) - More granular
4. Download formats available:
   - File Geodatabase (.gdb)
   - Shapefile (.shp)
   - CSV table

**What's Included:**
- 18 natural hazard risks (hurricanes, tornadoes, floods, etc.)
- Expected Annual Loss (EAL) values
- Social Vulnerability Index (SVI) scores
- Community Resilience scores
- Building value exposure
- Population exposure
- Risk ratings and scores

**Data Quality:**
- Completeness: ✅ Excellent - All 67 Florida counties
- Timeliness: ⚠️ Last updated March 23, 2023
- Format: ✅ Easy - Multiple formats, well-documented

**Sample Usage:**
```python
import geopandas as gpd

# Load FEMA NRI county data
fema_nri = gpd.read_file('NRI_Table_Counties.gdb', layer='NRI_Table_Counties')

# Filter for Florida (FIPS code starts with '12')
florida_nri = fema_nri[fema_nri['STCOFIPS'].str.startswith('12')]

# Extract hurricane risk metrics
hurricane_risk = florida_nri[[
    'COUNTY', 'STCOFIPS',
    'HRCN_RISKR',      # Hurricane risk rating
    'HRCN_EEAL',       # Hurricane expected annual loss
    'HRCN_AFREQ',      # Hurricane annual frequency
    'RISK_RATNG',      # Overall risk rating
    'SOVI_RATNG'       # Social vulnerability rating
]]
```

**Alternatives:**
- **FEMA Flood Map Service Center:** https://msc.fema.gov/ - Flood-specific data
- **Hazus Software:** https://www.fema.gov/flood-maps/products-tools/hazus - Advanced modeling

**Notes:**
- Download the **Data Dictionary** from the same page for variable definitions
- Hurricane metrics use prefix `HRCN_`
- Risk ratings: Very Low, Relatively Low, Relatively Moderate, Relatively High, Very High
- Expected Annual Loss (EAL) is in dollars

---

### 1.3 NOAA Storm Surge Data

**Source:** NOAA National Hurricane Center
**URL:** https://www.nhc.noaa.gov/nationalsurge/
**Data Type:** GeoTIFF, Shapefile
**Coverage:** Atlantic coast (Texas to Maine)
**File Size:** ~100-500MB per region
**Free Tier:** Unlimited

**Access Instructions:**
1. Visit https://www.nhc.noaa.gov/nationalsurge/
2. Download surge datasets for Florida regions
3. Data includes 1-foot inundation bins based on SLOSH model
4. Alternative: Florida-specific data at https://maps.floridadisaster.org/data/Storm_surge_zones_gdb.zip

**Data Quality:**
- Completeness: ✅ Good - Coastal Florida coverage
- Timeliness: ✅ Updated September 2025
- Format: ⚠️ Moderate - GeoTIFF requires spatial processing

**Sample Usage:**
```python
import rasterio
from rasterio.mask import mask

# Load storm surge GeoTIFF
with rasterio.open('florida_surge_zone.tif') as src:
    surge_data = src.read(1)

# Mask to county boundary
with fiona.open('county_boundary.shp') as shapefile:
    shapes = [feature["geometry"] for feature in shapefile]
    county_surge, transform = mask(src, shapes, crop=True)
```

**Alternatives:**
- **Florida Geographic Data Library:** https://fgdl.org/ - State-specific surge zones
- **County-level surge maps:** Individual county emergency management sites

**Notes:**
- SLOSH = Sea, Lake, and Overland Surges from Hurricanes
- Data shows potential inundation heights (1-21+ feet)
- Best used with county boundaries to calculate exposure

---

### 1.4 FEMA Flood Map Data

**Source:** FEMA Map Service Center
**URL:** https://msc.fema.gov/
**Data Type:** Shapefile, KMZ
**Coverage:** National Flood Hazard Layer (NFHL)
**File Size:** ~50-200MB per county
**Free Tier:** Unlimited

**Access Instructions:**
1. Visit https://msc.fema.gov/portal/search
2. Search for "Florida" or specific county name
3. Select "Search All Products"
4. Download NFHL data in shapefile format
5. Alternative viewer: https://www.arcgis.com/apps/webappviewer/index.html?id=8b0adb51996444d4879338b5529aa9cd

**Data Quality:**
- Completeness: ✅ Good - All coastal counties
- Timeliness: ✅ Updated regularly
- Format: ✅ Easy - Standard GIS formats

**Notes:**
- Includes 100-year and 500-year flood zones
- Useful for calculating property exposure
- Requires GIS software (QGIS, ArcGIS, or Python)

---

## 2. ECONOMIC DATA (COUNTY GDP)

### 2.1 Bureau of Economic Analysis (BEA) County GDP ⭐ CRITICAL

**Source:** U.S. Bureau of Economic Analysis
**URL:** https://www.bea.gov/data/gdp/gdp-county-metro-and-other-areas
**Data Type:** Excel (.xlsx), CSV (via API)
**Coverage:** All U.S. counties, 2001-2023
**File Size:** ~2-5MB (Excel)
**Free Tier:** Unlimited downloads, API requires free key

**Access Instructions:**

**Option 1: Direct Download (Recommended for MVP)**
1. Visit https://www.bea.gov/data/gdp/gdp-county-metro-and-other-areas
2. Download latest release:
   - Excel file: https://www.bea.gov/sites/default/files/2024-12/lagdp1224.xlsx
   - Full release PDF: https://www.bea.gov/sites/default/files/2024-12/lagdp1224.pdf
3. File includes GDP for all counties 2001-2023
4. Filter for Florida counties (FIPS codes 12001-12133)

**Option 2: Interactive Tables**
1. Visit https://apps.bea.gov/itable/?ReqID=70&step=1
2. Select "GDP by county"
3. Choose Florida as state
4. Select years and download CSV

**Option 3: BEA API** (for automated updates)
1. Register for API key: https://apps.bea.gov/api/signup/
2. Required: Name/org + email address
3. Terms of Service agreement
4. No explicit rate limits mentioned
5. Use "Regional" dataset, parameter for county-level data

**Data Quality:**
- Completeness: ✅ Excellent - All 67 Florida counties
- Timeliness: ✅ Excellent - 2023 data released Dec 2024
- Format: ✅ Easy - Excel with clear structure

**Sample Usage:**
```python
import pandas as pd

# Load BEA county GDP data
gdp_data = pd.read_excel('lagdp1224.xlsx', sheet_name='CAGDP1')

# Filter for Florida (GeoFIPS starts with '12')
florida_gdp = gdp_data[gdp_data['GeoFips'].str.startswith('12')]

# Get 2023 GDP for each county
gdp_2023 = florida_gdp[florida_gdp['Description'] == 'All industry total'][['GeoName', '2023']]

# Example API call
import requests
api_key = 'YOUR_API_KEY'
url = f'https://apps.bea.gov/api/data/?UserID={api_key}&method=GetData&datasetname=Regional&TableName=CAGDP1&LineCode=1&Year=2023&GeoFips=12*&ResultFormat=json'
response = requests.get(url)
county_gdp = response.json()
```

**Alternatives:**
- **Florida Office of Economic & Demographic Research:** https://edr.state.fl.us/Content/
- **Census Bureau County Business Patterns:** https://www.census.gov/programs-surveys/cbp.html
- **FRED Economic Data:** https://fred.stlouisfed.org/ - State-level only

**Notes:**
- Florida county GDP ranges from ~$2B (small counties) to $400B+ (Miami-Dade)
- Florida GDP grew 9.2% in 2023 (fastest growing state)
- BEA updates county GDP annually in December
- Next release: December 3, 2025 (will include 2024 data)
- Use "All industry total" line for total GDP
- GDP is in current dollars (not inflation-adjusted)

---

### 2.2 Census Bureau American Community Survey (ACS)

**Source:** U.S. Census Bureau
**URL:** https://www.census.gov/programs-surveys/acs/data.html
**Data Type:** CSV, JSON (via API)
**Coverage:** All counties, annual 5-year estimates
**File Size:** Varies by table
**Free Tier:** Unlimited, API requires free key

**Access Instructions:**
1. Main data portal: https://www.census.gov/programs-surveys/acs/data/data-via-api.html
2. API documentation: https://www.census.gov/data/developers/data-sets/acs-5year.html
3. Income tables: https://www.census.gov/topics/income-poverty/income/data/tables/acs.html
4. Poverty tables: https://www.census.gov/topics/income-poverty/poverty/data/tables/acs.html

**Key Variables for Vulnerability:**
- Median household income (Table B19013)
- Poverty rate (Table S1701)
- Unemployment rate (Table S2301)
- Educational attainment (Table S1501)
- Housing costs (Table B25070)

**Sample Usage:**
```python
import requests

# Census API call for median income
api_key = 'YOUR_CENSUS_API_KEY'
year = 2022
url = f'https://api.census.gov/data/{year}/acs/acs5?get=NAME,B19013_001E&for=county:*&in=state:12&key={api_key}'

response = requests.get(url)
income_data = response.json()
```

**Notes:**
- 5-year estimates (2018-2022) most recent
- More stable than 1-year estimates
- County-level data available

---

## 3. SOCIAL VULNERABILITY DATA

### 3.1 CDC Social Vulnerability Index (SVI) ⭐ CRITICAL

**Source:** CDC/ATSDR (Agency for Toxic Substances and Disease Registry)
**URL:** https://www.atsdr.cdc.gov/place-health/php/svi/svi-data-documentation-download.html
**Data Type:** CSV, Geodatabase, Shapefile
**Coverage:** All U.S. counties and census tracts
**File Size:** ~10-50MB (Florida county-level), ~200MB (tract-level)
**Free Tier:** Unlimited

**Access Instructions:**
1. Visit SVI data download page (URL above)
2. Select year: **2022** (most recent available)
3. Choose geography:
   - **County-level:** Easier for MVP, 67 Florida counties
   - **Census tract-level:** More granular, 4,200+ tracts
4. Download options:
   - State-specific (Florida only) - Recommended
   - National dataset (includes all states)
5. File formats: CSV, Geodatabase, Shapefile
6. Documentation: Download "SVI 2022 Documentation.pdf" for variable definitions

**What's Included:**
- **Theme 1:** Socioeconomic status (poverty, unemployment, income, education)
- **Theme 2:** Household composition (age 65+, age 17-, disability, single parent)
- **Theme 3:** Minority status & language (minority, limited English)
- **Theme 4:** Housing/transportation (multi-unit housing, mobile homes, crowding, no vehicle, group quarters)
- **Overall SVI:** Composite score (0-1, higher = more vulnerable)

**Data Quality:**
- Completeness: ✅ Excellent - All Florida counties
- Timeliness: ⚠️ 2022 data (updated Dec 2024)
- Format: ✅ Easy - CSV with clear documentation

**Sample Usage:**
```python
import pandas as pd

# Load CDC SVI data
svi = pd.read_csv('Florida_SVI_2022_County.csv')

# Key SVI columns
svi_metrics = svi[[
    'COUNTY', 'FIPS',
    'RPL_THEMES',    # Overall SVI percentile (0-1)
    'RPL_THEME1',    # Socioeconomic percentile
    'RPL_THEME2',    # Household composition percentile
    'RPL_THEME3',    # Minority/language percentile
    'RPL_THEME4',    # Housing/transport percentile
    'E_TOTPOP',      # Total population
    'EP_POV150',     # % below 150% poverty
    'EP_UNINSUR',    # % uninsured
    'EP_UNEMP'       # % unemployed
]]

# Identify high vulnerability counties (top quartile)
high_vuln = svi[svi['RPL_THEMES'] >= 0.75]
```

**Alternatives:**
- **FEMA National Risk Index:** Includes SVI as component (already covered above)
- **Census ACS data:** More current but requires manual calculation

**Notes:**
- **IMPORTANT:** Percentile scores from different years are NOT comparable
- Census tract boundaries change over time
- RPL = Percentile Ranking (0-1 scale)
- E_ prefix = Estimate count
- EP_ prefix = Estimate percentage
- F_ prefix = Flag for missing data (-999)
- Use RPL_THEMES for overall vulnerability score
- 2020 SVI updated Dec 22, 2022 (housing burden variable correction)
- Contact: svi_coordinator@cdc.gov

---

## 4. GEOSPATIAL BOUNDARIES

### 4.1 Florida County Boundaries (GeoJSON) ⭐ CRITICAL

**Source:** GitHub Community / U.S. Census Bureau
**URL:** https://github.com/danielcs88/fl_geo_json
**Data Type:** GeoJSON
**Coverage:** 67 Florida counties + state boundary
**File Size:** ~1-5MB
**Free Tier:** Unlimited (open source)

**Access Instructions:**
1. Visit https://github.com/danielcs88/fl_geo_json
2. Download files:
   - **geojson-fl-counties-fips.json** - County boundaries with FIPS codes
   - **fl-state.json** - Florida state boundary
3. Alternative: Clone repository
   ```bash
   git clone https://github.com/danielcs88/fl_geo_json.git
   ```

**Data Quality:**
- Completeness: ✅ Excellent - All 67 counties
- Timeliness: ✅ Current boundaries
- Format: ✅ Perfect - GeoJSON ready for web mapping

**Sample Usage:**
```python
import geopandas as gpd

# Load Florida county boundaries
florida_counties = gpd.read_file('geojson-fl-counties-fips.json')

# Leaflet/React usage
import json
with open('geojson-fl-counties-fips.json', 'r') as f:
    florida_geojson = json.load(f)
```

**JavaScript/React Usage:**
```javascript
// In React component
import floridaCounties from './geojson-fl-counties-fips.json';

// Use with Leaflet
<GeoJSON data={floridaCounties} />
```

**Alternatives:**
- **U.S. Census TIGER/Line:** https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
- **Census Cartographic Boundaries:** https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html (simplified)
- **Natural Earth Data:** https://www.naturalearthdata.com/ (global, lower resolution)

**Notes:**
- GeoJSON is web-ready, works directly with Leaflet
- FIPS code for Florida is `12`
- County FIPS: `12001` through `12133`
- Coordinate system: WGS84 (EPSG:4326)
- For smaller file sizes, use TopoJSON or simplify with Mapshaper

---

### 4.2 U.S. Census TIGER/Line Shapefiles

**Source:** U.S. Census Bureau
**URL:** https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
**Data Type:** Shapefile, Geodatabase, KML, Geopackage
**Coverage:** All U.S. geographic boundaries
**File Size:** ~10-50MB (Florida counties)
**Free Tier:** Unlimited

**Access Instructions:**
1. Visit TIGER/Line main page (URL above)
2. Select year: **2024** (boundaries as of January 1, 2024)
3. Choose layer: "Counties and Equivalent"
4. Select Florida from state dropdown
5. Download formats:
   - Shapefile (.shp) - Most compatible
   - Geodatabase (.gdb) - For ArcGIS
   - KML - For Google Earth
   - Geopackage - Modern format

**Cartographic Boundaries (Simplified):**
- URL: https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html
- Smaller file sizes, optimized for web mapping
- Multiple simplification levels: 1:500k, 1:5m, 1:20m

**Sample Usage:**
```python
import geopandas as gpd

# Load TIGER/Line shapefile
florida_counties = gpd.read_file('tl_2024_12_county.shp')

# Convert to GeoJSON for web
florida_counties.to_file('florida_counties.geojson', driver='GeoJSON')
```

**Notes:**
- More detailed than cartographic boundaries
- Includes water boundaries
- Can be simplified using Mapshaper or QGIS

---

### 4.3 Mapshaper (Simplification Tool)

**Source:** Open-source web tool
**URL:** https://mapshaper.org/
**Purpose:** Simplify boundaries, convert formats
**Free Tier:** Unlimited

**Usage:**
1. Upload Florida county shapefile/GeoJSON
2. Simplify to reduce file size:
   ```
   Console: simplify 10% keep-shapes
   ```
3. Export as GeoJSON, TopoJSON, or Shapefile
4. Reduces file size by 50-90% while preserving shape

**Command-line (for automation):**
```bash
npm install -g mapshaper

# Simplify and convert
mapshaper florida_counties.shp -simplify 10% keep-shapes -o florida_simple.geojson
```

---

## 5. SATELLITE IMAGERY (OPTIONAL)

### 5.1 USGS EarthExplorer (Landsat 8/9)

**Source:** U.S. Geological Survey
**URL:** https://earthexplorer.usgs.gov/
**Data Type:** GeoTIFF (multi-band satellite imagery)
**Coverage:** Global, including Florida
**File Size:** ~1-2GB per scene
**Free Tier:** Unlimited downloads, registration required

**Access Instructions:**
1. **Register account:**
   - Visit https://earthexplorer.usgs.gov/
   - Click "Login" → "Register"
   - Free account, email verification required

2. **Search for Florida imagery:**
   - Search Criteria tab:
     - Feature Name: "FLORIDA"
     - Or coordinates: 24.5°N to 31°N, -87.6°W to -80°W
   - Date Range: Select desired timeframe
     - For Hurricane Ian: September 2022
     - For current imagery: 2024

3. **Select datasets:**
   - Data Sets tab → Landsat → Landsat Collection 2 Level-2
   - **Landsat 9 OLI/TIRS** (launched Sept 2021) - Most recent
   - **Landsat 8 OLI/TIRS** (2013-present)

4. **Filter and download:**
   - Additional Criteria: Cloud cover < 10%
   - Results: Click download icon
   - Select "Level-2 Surface Reflectance" product
   - Large downloads trigger email notification

**Data Quality:**
- Completeness: ✅ Excellent - Full Florida coverage
- Timeliness: ✅ 16-day revisit time
- Format: ⚠️ Complex - Requires geospatial processing

**Sample Usage:**
```python
import rasterio
from rasterio.plot import show

# Load Landsat scene
with rasterio.open('LC09_L2SP_015041_20240915_20240917_02_T1_SR_B4.TIF') as src:
    red_band = src.read(1)
    metadata = src.meta

# Calculate NDVI (vegetation index)
red = rasterio.open('B4.TIF').read(1).astype(float)
nir = rasterio.open('B5.TIF').read(1).astype(float)
ndvi = (nir - red) / (nir + red)
```

**Alternatives:**
- **Sentinel-2 (Copernicus):** https://dataspace.copernicus.eu/ - 10m resolution, 5-day revisit
- **Google Earth Engine:** https://earthengine.google.com/ - Cloud processing, requires signup

**Notes:**
- Landsat 9: 11 spectral bands, 30m resolution (visible/NIR), 100m (thermal)
- Landsat 8: Same specifications
- Download sizes: 1-2GB per scene (7 bands)
- Florida requires ~6-8 scenes for full coverage
- "First light" Landsat 9 images: Oct 31, 2021

---

### 5.2 Copernicus Sentinel-2

**Source:** European Space Agency / Copernicus
**URL:** https://dataspace.copernicus.eu/
**Data Type:** GeoTIFF, JP2
**Coverage:** Global land surface
**File Size:** ~500MB-1GB per tile
**Free Tier:** Unlimited, registration required

**Access Instructions:**
1. **Register account:**
   - Visit https://dataspace.copernicus.eu/
   - Create free account
   - Get access token for API downloads

2. **Browse imagery:**
   - Copernicus Browser: https://browser.dataspace.copernicus.eu/
   - Select area of interest (Florida)
   - Choose date range
   - Filter: Cloud cover < 10%

3. **Download options:**
   - **Manual:** Browser download
   - **API:** OData/OpenSearch API with access token
   - **NOAA CoastWatch** (Florida coastal): MSI Sentinel-2 imagery

**Data Products:**
- **Level-1C:** Top-of-atmosphere reflectance
- **Level-2A:** Surface reflectance (atmospherically corrected) - Recommended

**Sample Usage:**
```python
from sentinelsat import SentinelAPI

# Connect to API
api = SentinelAPI('username', 'password', 'https://apihub.copernicus.eu/apihub')

# Search for Florida imagery
footprint = "POLYGON((-87.6 24.5, -80.0 24.5, -80.0 31.0, -87.6 31.0, -87.6 24.5))"
products = api.query(footprint,
                     date=('20240901', '20240930'),
                     platformname='Sentinel-2',
                     cloudcoverpercentage=(0, 10))

# Download
api.download_all(products)
```

**Alternatives:**
- **AWS Open Data:** s3://sentinel-s2-l2a/ (requires AWS CLI)
- **Google Earth Engine:** Pre-processed Sentinel-2 collection

**Notes:**
- Sentinel-2A (launched 2015), 2B (2017), 2C (Sept 2024)
- 10m resolution (visible bands), 20m (red edge/SWIR)
- 5-day revisit time (2-3 days with all satellites)
- Great for vegetation, land cover analysis

---

### 5.3 Google Earth Engine

**Source:** Google
**URL:** https://earthengine.google.com/
**Data Type:** Cloud-processed imagery
**Coverage:** 100+ petabytes satellite data
**File Size:** N/A (cloud processing)
**Free Tier:** Free for research/nonprofit, commercial pricing available

**Access Instructions:**
1. Register at https://earthengine.google.com/
2. Signup requires Google Cloud Project
3. Access via:
   - Python API: `pip install earthengine-api`
   - JavaScript: Code Editor (browser)

**Available Data (Florida):**
- Landsat 1-9 (1972-present)
- Sentinel-1 (radar), Sentinel-2 (optical)
- MODIS, VIIRS
- Climate/weather data
- Terrain/elevation

**Sample Usage:**
```python
import ee

# Initialize
ee.Initialize()

# Load Sentinel-2 for Florida
florida = ee.Geometry.Rectangle([-87.6, 24.5, -80.0, 31.0])
sentinel = ee.ImageCollection('COPERNICUS/S2_SR') \
    .filterBounds(florida) \
    .filterDate('2024-01-01', '2024-12-31') \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))

# Calculate median composite
median_image = sentinel.median()

# Export to Drive
task = ee.batch.Export.image.toDrive(
    image=median_image,
    description='florida_sentinel_2024',
    scale=10,
    region=florida
)
task.start()
```

**Notes:**
- Best for large-scale analysis
- No download limits (cloud processing)
- Requires learning curve
- Free for non-commercial use

---

## 6. APIS & WEB SERVICES

### 6.1 OpenStreetMap Tiles (Basemap) ⭐ CRITICAL

**Source:** OpenStreetMap Foundation
**URL:** https://tile.openstreetmap.org/{z}/{x}/{y}.png
**Data Type:** Map tiles (PNG images)
**Coverage:** Global
**File Size:** N/A (streamed)
**Free Tier:** Free with attribution, usage policy applies

**Access Instructions:**
1. No registration required
2. Standard tile URL: `https://tile.openstreetmap.org/{z}/{x}/{y}.png`
3. Attribution required: "© OpenStreetMap contributors"
4. Alternative tile servers:
   - **OpenStreetMap HOT:** https://tile-a.openstreetmap.fr/hot/{z}/{x}/{y}.png
   - **Stamen Terrain:** Via Stadia Maps (requires API key)

**Usage Policy:**
- Heavy use (bulk downloading): Use your own tile server
- Rate limiting applies
- Cache tiles locally when possible

**Sample Usage (React-Leaflet):**
```javascript
import { MapContainer, TileLayer } from 'react-leaflet';

<MapContainer center={[27.6648, -81.5158]} zoom={7}>
  <TileLayer
    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
  />
</MapContainer>
```

**Alternatives:**
- **Mapbox** (free tier): https://www.mapbox.com/ - 50,000 loads/month
- **Stadia Maps** (free tier): https://stadiamaps.com/ - 200,000 tiles/month
- **CartoDB Basemaps:** https://carto.com/basemaps/ - Free with attribution

**Notes:**
- For production, consider Mapbox or self-hosted tiles
- OSM tiles are not for heavy commercial use
- Cache tiles client-side to reduce requests

---

### 6.2 Nominatim Geocoding API

**Source:** OpenStreetMap Foundation
**URL:** https://nominatim.openstreetmap.org/
**Data Type:** JSON, XML, GeoJSON
**Coverage:** Global addresses and places
**File Size:** N/A (API responses)
**Free Tier:** Free, rate limit: 1 request/second

**Access Instructions:**
1. No API key required for public instance
2. Usage policy: https://operations.osmfoundation.org/policies/nominatim/
3. Endpoints:
   - **Search:** `/search?q=<query>&format=json`
   - **Reverse:** `/reverse?lat=<lat>&lon=<lon>&format=json`

**Sample Usage:**
```python
import requests

# Geocode Florida county
response = requests.get(
    'https://nominatim.openstreetmap.org/search',
    params={
        'q': 'Miami-Dade County, Florida',
        'format': 'json',
        'limit': 1
    },
    headers={'User-Agent': 'LanzatApp/1.0'}
)
result = response.json()[0]
lat, lon = result['lat'], result['lon']

# Reverse geocode
response = requests.get(
    'https://nominatim.openstreetmap.org/reverse',
    params={
        'lat': 25.7617,
        'lon': -80.1918,
        'format': 'json'
    }
)
address = response.json()['display_name']
```

**JavaScript:**
```javascript
// Geocode county name to coordinates
fetch('https://nominatim.openstreetmap.org/search?q=Broward+County+Florida&format=json')
  .then(res => res.json())
  .then(data => {
    const [lat, lon] = [data[0].lat, data[0].lon];
  });
```

**Usage Policy:**
- Rate limit: 1 request per second
- Must provide User-Agent header
- No heavy usage (>10,000 requests/day)
- For high volume, run your own Nominatim instance

**Alternatives:**
- **Mapbox Geocoding:** https://docs.mapbox.com/api/search/geocoding/ - 100,000 requests/month free
- **Google Geocoding:** https://developers.google.com/maps/documentation/geocoding - $200 credit/month
- **Geoapify:** https://www.geoapify.com/ - 3,000 requests/day free

**Notes:**
- Coordinates in WGS84 (EPSG:4326)
- Returns bounding box for counties
- Useful for converting county names to lat/lon

---

### 6.3 NOAA Weather API (Optional)

**Source:** National Oceanic and Atmospheric Administration
**URL:** https://www.weather.gov/documentation/services-web-api
**Data Type:** JSON
**Coverage:** U.S. weather forecasts and observations
**Free Tier:** Unlimited, no key required

**Access Instructions:**
1. No registration required
2. Base URL: `https://api.weather.gov`
3. User-Agent header required

**Sample Usage:**
```python
import requests

# Get weather for Miami
headers = {'User-Agent': 'LanzatApp/1.0'}
response = requests.get(
    'https://api.weather.gov/points/25.7617,-80.1918',
    headers=headers
)
forecast_url = response.json()['properties']['forecast']

# Get 7-day forecast
forecast = requests.get(forecast_url, headers=headers).json()
```

**Notes:**
- Real-time weather not critical for MVP
- Could add current hurricane alerts
- Useful for demo if active hurricane season

---

## 7. DEVELOPMENT LIBRARIES & TOOLS

### 7.1 Python Geospatial Stack

**Essential Libraries:**

```bash
# Install geospatial libraries
pip install geopandas rasterio fiona shapely pyproj
pip install pandas numpy matplotlib

# Additional
pip install contextily  # Basemap backgrounds
pip install folium      # Interactive maps
pip install earthpy     # Earth science utilities
```

**GeoPandas** - Vector data manipulation
- Documentation: https://geopandas.org/
- Tutorial: https://geopandas.org/en/stable/getting_started.html

**Rasterio** - Raster data (satellite imagery)
- Documentation: https://rasterio.readthedocs.io/
- Examples: https://rasterio.readthedocs.io/en/stable/quickstart.html

**Usage Example:**
```python
import geopandas as gpd
import pandas as pd

# Load and merge data
counties = gpd.read_file('florida_counties.geojson')
gdp_data = pd.read_csv('county_gdp.csv')
svi_data = pd.read_csv('florida_svi.csv')

# Merge on FIPS code
vulnerability_map = counties.merge(gdp_data, on='FIPS')
vulnerability_map = vulnerability_map.merge(svi_data, on='FIPS')

# Calculate vulnerability score
vulnerability_map['vuln_score'] = (
    vulnerability_map['RPL_THEMES'] * 0.4 +  # 40% social vulnerability
    vulnerability_map['HRCN_RISKR'] * 0.4 +  # 40% hurricane risk
    (1 - vulnerability_map['GDP_RANK']) * 0.2  # 20% economic (inverse)
)

# Save combined dataset
vulnerability_map.to_file('vulnerability_map.geojson', driver='GeoJSON')
```

---

### 7.2 React/JavaScript Mapping Stack

**Essential Libraries:**

```bash
# Frontend mapping
npm install leaflet react-leaflet
npm install recharts  # Charts/graphs
npm install axios     # API calls

# TypeScript types
npm install -D @types/leaflet
```

**React-Leaflet** - Interactive maps
- Documentation: https://react-leaflet.js.org/
- Examples: https://react-leaflet.js.org/docs/start-introduction

**Recharts** - Data visualization
- Documentation: https://recharts.org/
- Examples: https://recharts.org/en-US/examples

**Usage Example:**
```javascript
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import floridaData from './vulnerability_map.geojson';

function Lanzat() {
  const getColor = (score) => {
    return score > 0.8 ? '#d73027' :
           score > 0.6 ? '#fc8d59' :
           score > 0.4 ? '#fee08b' :
           score > 0.2 ? '#d9ef8b' :
                         '#91cf60';
  };

  const style = (feature) => ({
    fillColor: getColor(feature.properties.vuln_score),
    weight: 1,
    opacity: 1,
    color: 'white',
    fillOpacity: 0.7
  });

  return (
    <MapContainer center={[27.6648, -81.5158]} zoom={7}>
      <TileLayer url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <GeoJSON data={floridaData} style={style} />
    </MapContainer>
  );
}
```

---

### 7.3 Backend Framework (FastAPI/Express)

**FastAPI (Python):**
```bash
pip install fastapi uvicorn
pip install sqlalchemy  # Database
pip install python-dotenv
```

**Express (Node.js):**
```bash
npm install express cors
npm install pg  # PostgreSQL client
npm install dotenv
```

**Quick API Example (FastAPI):**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import geopandas as gpd

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Load data once at startup
vulnerability_data = gpd.read_file('vulnerability_map.geojson')

@app.get("/api/counties")
def get_counties():
    return vulnerability_data.to_json()

@app.get("/api/county/{fips}")
def get_county(fips: str):
    county = vulnerability_data[vulnerability_data['FIPS'] == fips]
    return county.to_dict(orient='records')[0]
```

---

### 7.4 Testing Frameworks

**Python (pytest):**
```bash
pip install pytest pytest-cov
pip install httpx  # For API testing
```

**JavaScript (Jest + React Testing Library):**
```bash
npm install -D jest @testing-library/react @testing-library/jest-dom
npm install -D @playwright/test  # E2E testing
```

---

## 8. RESEARCH & METHODOLOGIES

### 8.1 FEMA Hazus Methodology

**Source:** FEMA
**URL:** https://www.fema.gov/flood-maps/products-tools/hazus
**Document:** https://www.fema.gov/sites/default/files/documents/fema_hazus-hurricane-modeling-factsheet_102021.pdf

**Key Concepts:**
- **Hazard Analysis:** Wind speed, storm surge modeling
- **Inventory Data:** Building stock, essential facilities
- **Damage Functions:** Building vulnerability curves
- **Loss Estimation:** Direct economic losses, casualties

**Methodology Levels:**
- **Level 1 (Basic):** Default national databases, quick estimates
- **Level 2 (Intermediate):** Local hazard data, refined inventory
- **Level 3 (Advanced):** Detailed local data, custom damage functions

**Sample Vulnerability Calculation:**
```python
def calculate_hazus_vulnerability(county_data):
    """
    Simplified Hazus-inspired vulnerability score
    """
    # Expected Annual Loss (EAL) normalized
    eal_score = county_data['HRCN_EEAL'] / county_data['total_building_value']

    # Social vulnerability component
    svi_score = county_data['RPL_THEMES']

    # Combine components
    vulnerability = (eal_score * 0.5) + (svi_score * 0.5)

    return vulnerability
```

**Key Citations:**
- FEMA P-433: "Using HAZUS-MH for Risk Assessment"
- Hazus Hurricane Model Technical Manual
- Multi-Hazard Loss Estimation Methodology

---

### 8.2 Academic Vulnerability Assessment

**Key Research Papers:**

1. **"Assessing Socioeconomic Vulnerability after a Hurricane"** (2020)
   - Source: MDPI Sustainability
   - URL: https://www.mdpi.com/2071-1050/12/4/1452
   - Method: Index-based approach + PCA
   - Components: Susceptibility, coping capacity, adaptation

2. **"Quantifying the Role of Vulnerability in Hurricane Damage"** (2021)
   - Source: ASCE Natural Hazards Review
   - URL: https://ascelibrary.org/doi/10.1061/(ASCE)NH.1527-6996.0000460
   - Method: Machine learning (random forest)
   - Factors: Social, physical, economic drivers

3. **"Critical Review of Hurricane Risk Assessment Models"** (2025)
   - Source: ScienceDirect
   - Method: Systematic review of 94 articles
   - Focus: Hazard-vulnerability-exposure-mitigation framework

**Vulnerability Index Framework:**

```python
def calculate_composite_vulnerability(county):
    """
    Multi-dimensional vulnerability index
    Based on academic research
    """
    # 1. Hazard component (40%)
    hazard = normalize(county['hurricane_frequency'] * county['intensity'])

    # 2. Exposure component (30%)
    exposure = normalize(county['population_density'] * county['building_value'])

    # 3. Vulnerability component (30%)
    social_vuln = county['SVI_score']
    economic_vuln = 1 - normalize(county['GDP_per_capita'])
    vulnerability = (social_vuln + economic_vuln) / 2

    # Composite score
    composite = (hazard * 0.4) + (exposure * 0.3) + (vulnerability * 0.3)

    return composite
```

**Key Metrics from Literature:**
- **Susceptibility:** Population density, building quality, infrastructure age
- **Coping Capacity:** Income, education, insurance coverage, social networks
- **Adaptation:** Building codes, disaster planning, early warning systems

---

### 8.3 CDC SVI Documentation

**Source:** CDC/ATSDR
**URL:** https://www.atsdr.cdc.gov/place-health/php/svi/documentation/SVI-2022-Documentation.pdf

**Four Themes (16 Variables):**

**Theme 1 - Socioeconomic:**
- Below 150% poverty
- Unemployed
- Housing cost burden
- No high school diploma
- No health insurance

**Theme 2 - Household Characteristics:**
- Aged 65+
- Aged 17 and younger
- Civilian with disability
- Single-parent households
- English language proficiency

**Theme 3 - Racial & Ethnic Minority:**
- Hispanic/Latino
- Black/African American
- Asian
- Native American
- Pacific Islander
- Two or more races
- Other races

**Theme 4 - Housing/Transportation:**
- Multi-unit structures
- Mobile homes
- Crowding
- No vehicle
- Group quarters

**Calculation Method:**
```python
def calculate_svi_theme(county_data, theme_variables):
    """
    CDC SVI theme score calculation
    """
    percentile_ranks = []

    for var in theme_variables:
        # Calculate percentile rank for each variable
        rank = county_data[var].rank(pct=True)
        percentile_ranks.append(rank)

    # Sum percentile ranks
    theme_sum = sum(percentile_ranks)

    # Calculate percentile rank of sum
    theme_score = theme_sum.rank(pct=True)

    return theme_score
```

**Overall SVI:**
- Sum of all 16 variable percentile ranks
- Percentile rank of the sum
- Range: 0 (least vulnerable) to 1 (most vulnerable)

---

### 8.4 Economic Impact Models

**Sources:**
- Richmond Fed: "The Economic and Human Impacts of Hurricanes" (2024)
- Brookings: "Hurricanes Hit the Poor the Hardest"
- National Academies: "Integrated Approach to Hurricane Risk"

**Key Findings:**
- Hurricane damage correlates with poverty rates
- Recovery time inversely proportional to income
- Indirect losses (business interruption) = 50-200% of direct losses
- Low-income areas: 3-5x longer recovery time

**Economic Vulnerability Formula:**
```python
def economic_vulnerability(county):
    """
    Economic vulnerability to hurricanes
    """
    # GDP dependency (inverse)
    gdp_per_capita = county['GDP'] / county['population']
    gdp_vulnerability = 1 - normalize(gdp_per_capita)

    # Employment concentration risk
    industry_diversity = county['employment_herfindahl_index']
    employment_risk = normalize(industry_diversity)

    # Insurance coverage (inverse)
    uninsured_rate = county['uninsured_property_pct']
    insurance_vuln = normalize(uninsured_rate)

    # Combine
    econ_vuln = (
        gdp_vulnerability * 0.4 +
        employment_risk * 0.3 +
        insurance_vuln * 0.3
    )

    return econ_vuln
```

---

## 9. QUICK START DOWNLOAD SCRIPT

### 9.1 Automated Data Download (Python)

Save as `download_data.py`:

```python
#!/usr/bin/env python3
"""
Lanzat Data Download Script
Downloads all critical datasets for Florida vulnerability mapping
"""

import os
import requests
from pathlib import Path
import pandas as pd
import geopandas as gpd

# Create data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def download_file(url, filename):
    """Download file with progress indicator"""
    print(f"Downloading {filename}...")
    response = requests.get(url, stream=True)
    filepath = DATA_DIR / filename

    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✓ Downloaded {filename} ({filepath.stat().st_size / 1024 / 1024:.1f} MB)")
    return filepath

def download_critical_datasets():
    """Download all critical datasets for MVP"""

    print("=" * 60)
    print("Lanzat Data Download")
    print("=" * 60)

    # 1. Florida County Boundaries (GeoJSON)
    print("\n1. FLORIDA COUNTY BOUNDARIES")
    counties_url = "https://raw.githubusercontent.com/danielcs88/fl_geo_json/main/geojson-fl-counties-fips.json"
    download_file(counties_url, "florida_counties.geojson")

    # 2. IBTrACS Hurricane Data (North Atlantic)
    print("\n2. HURRICANE TRACKS (IBTrACS)")
    ibtracs_url = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.NA.list.v04r01.csv"
    download_file(ibtracs_url, "ibtracs_north_atlantic.csv")

    # 3. BEA County GDP Data
    print("\n3. COUNTY GDP DATA (BEA)")
    gdp_url = "https://www.bea.gov/sites/default/files/2024-12/lagdp1224.xlsx"
    download_file(gdp_url, "county_gdp_2023.xlsx")

    # 4. CDC Social Vulnerability Index
    print("\n4. CDC SOCIAL VULNERABILITY INDEX")
    print("Note: SVI data requires manual download from:")
    print("https://www.atsdr.cdc.gov/place-health/php/svi/svi-data-documentation-download.html")
    print("Download: Florida_SVI_2022_County.csv")
    print("Save to: data/florida_svi_2022.csv")

    # 5. FEMA National Risk Index
    print("\n5. FEMA NATIONAL RISK INDEX")
    print("Note: FEMA NRI requires manual download from:")
    print("https://hazards.fema.gov/nri/data-resources")
    print("Download: Florida County-level CSV or Shapefile")
    print("Save to: data/fema_nri_florida.csv")

    print("\n" + "=" * 60)
    print("DOWNLOAD STATUS")
    print("=" * 60)
    print("✓ Florida county boundaries")
    print("✓ Hurricane tracks (IBTrACS)")
    print("✓ County GDP data (BEA)")
    print("⚠ CDC SVI - Manual download required")
    print("⚠ FEMA NRI - Manual download required")
    print("\nEstimated total download: ~100-150 MB")
    print("Time to complete: 2-5 minutes (depending on connection)")
    print("=" * 60)

def process_hurricane_data():
    """Process hurricane data for Florida"""
    print("\nProcessing hurricane data for Florida...")

    # Load IBTrACS
    ibtracs = pd.read_csv(DATA_DIR / "ibtracs_north_atlantic.csv", skiprows=1, low_memory=False)

    # Filter for Florida region
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

    # Save processed data
    florida_hurricanes.to_csv(DATA_DIR / "florida_hurricanes.csv", index=False)
    print(f"✓ Processed {len(florida_hurricanes)} Florida hurricane data points")

def process_gdp_data():
    """Process GDP data for Florida counties"""
    print("\nProcessing GDP data for Florida counties...")

    # Load BEA GDP data
    gdp_data = pd.read_excel(DATA_DIR / "county_gdp_2023.xlsx", sheet_name='CAGDP1')

    # Filter for Florida
    florida_gdp = gdp_data[gdp_data['GeoFips'].str.startswith('12', na=False)]

    # Extract 2023 GDP (all industries)
    florida_gdp_2023 = florida_gdp[florida_gdp['Description'] == 'All industry total'][
        ['GeoFips', 'GeoName', '2023']
    ].rename(columns={'2023': 'GDP_2023'})

    # Save processed data
    florida_gdp_2023.to_csv(DATA_DIR / "florida_gdp_2023.csv", index=False)
    print(f"✓ Processed GDP for {len(florida_gdp_2023)} Florida counties")

if __name__ == "__main__":
    # Download datasets
    download_critical_datasets()

    # Process downloaded data
    print("\n" + "=" * 60)
    print("PROCESSING DATA")
    print("=" * 60)
    process_hurricane_data()
    process_gdp_data()

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("1. Manually download CDC SVI data (see instructions above)")
    print("2. Manually download FEMA NRI data (see instructions above)")
    print("3. Run data integration script: python integrate_data.py")
    print("=" * 60)
```

### 9.2 Manual Download Checklist

**CRITICAL (Hour 0-2):**
- [ ] Florida county boundaries (GeoJSON) - Automated ✓
- [ ] IBTrACS hurricane tracks - Automated ✓
- [ ] BEA county GDP data - Automated ✓
- [ ] CDC SVI Florida county data - Manual download
  - Visit: https://www.atsdr.cdc.gov/place-health/php/svi/svi-data-documentation-download.html
  - Select: 2022, Florida, County-level
  - Download: CSV format
  - Save as: `data/florida_svi_2022.csv`
- [ ] FEMA National Risk Index - Manual download
  - Visit: https://hazards.fema.gov/nri/data-resources
  - Select: County-level, CSV or Shapefile
  - Filter: Florida
  - Save as: `data/fema_nri_florida.csv`

**IMPORTANT (Hour 2-8):**
- [ ] Storm surge data (optional)
- [ ] Flood zone data (optional)
- [ ] ACS supplemental economic data (optional)

**NICE TO HAVE (Hour 8+):**
- [ ] Satellite imagery (Landsat/Sentinel)
- [ ] Real-time weather API setup

### 9.3 Download Time & Storage Estimates

| Dataset | Size | Download Time* | Priority |
|---------|------|---------------|----------|
| Florida county GeoJSON | 2 MB | < 1 min | CRITICAL |
| IBTrACS (North Atlantic) | 30 MB | 1-2 min | CRITICAL |
| BEA County GDP | 3 MB | < 1 min | CRITICAL |
| CDC SVI Florida | 5 MB | < 1 min | CRITICAL |
| FEMA NRI Florida | 20 MB | 1-2 min | CRITICAL |
| **TOTAL (MVP)** | **~60 MB** | **5-10 min** | - |
| Storm surge data | 100 MB | 5-10 min | IMPORTANT |
| Landsat scene (1) | 1-2 GB | 10-30 min | OPTIONAL |
| **TOTAL (Full)** | **~2-3 GB** | **30-60 min** | - |

*Assuming 10 Mbps connection

---

## 10. DATA PROCESSING ORDER

### Phase 1: Data Acquisition (Hour 0-2)

**Step 1: Run automated download script**
```bash
python download_data.py
```

**Step 2: Manual downloads**
1. CDC SVI Florida county CSV (5 min)
2. FEMA NRI Florida county CSV (5 min)

**Step 3: Verify data integrity**
```bash
ls -lh data/
# Should see:
# - florida_counties.geojson
# - ibtracs_north_atlantic.csv
# - county_gdp_2023.xlsx
# - florida_svi_2022.csv (manual)
# - fema_nri_florida.csv (manual)
```

---

### Phase 2: Data Integration (Hour 2-4)

**Create `integrate_data.py`:**

```python
import pandas as pd
import geopandas as gpd

# 1. Load county boundaries
counties = gpd.read_file('data/florida_counties.geojson')

# 2. Load and process GDP data
gdp = pd.read_csv('data/florida_gdp_2023.csv')
gdp['FIPS'] = gdp['GeoFips'].str.slice(2)  # Remove state code

# 3. Load SVI data
svi = pd.read_csv('data/florida_svi_2022.csv')
svi['FIPS'] = svi['FIPS'].astype(str).str.zfill(5).str.slice(2)

# 4. Load FEMA NRI
nri = pd.read_csv('data/fema_nri_florida.csv')
nri['FIPS'] = nri['STCOFIPS'].str.slice(2)

# 5. Merge all datasets
vulnerability_map = counties.merge(gdp, on='FIPS', how='left')
vulnerability_map = vulnerability_map.merge(svi[['FIPS', 'RPL_THEMES', 'RPL_THEME1', 'RPL_THEME2', 'RPL_THEME3', 'RPL_THEME4']], on='FIPS', how='left')
vulnerability_map = vulnerability_map.merge(nri[['FIPS', 'HRCN_RISKR', 'HRCN_EEAL', 'RISK_RATNG']], on='FIPS', how='left')

# 6. Calculate vulnerability score
def calculate_vulnerability(row):
    """
    Composite vulnerability score
    """
    # Normalize components to 0-1
    svi_score = row['RPL_THEMES']  # Already 0-1

    # Hurricane risk (convert rating to score)
    risk_map = {'Very Low': 0.1, 'Relatively Low': 0.3, 'Relatively Moderate': 0.5, 'Relatively High': 0.7, 'Very High': 0.9}
    hurricane_score = risk_map.get(row['HRCN_RISKR'], 0.5)

    # Economic vulnerability (inverse GDP per capita)
    gdp_per_capita = row['GDP_2023'] / row['POPULATION']  # Need to add population
    gdp_score = 1 - (gdp_per_capita / gdp_per_capita.max())

    # Weighted combination
    vulnerability = (
        svi_score * 0.4 +        # 40% social vulnerability
        hurricane_score * 0.4 +  # 40% hurricane risk
        gdp_score * 0.2          # 20% economic
    )

    return vulnerability

vulnerability_map['VULN_SCORE'] = vulnerability_map.apply(calculate_vulnerability, axis=1)

# 7. Save integrated dataset
vulnerability_map.to_file('data/vulnerability_map.geojson', driver='GeoJSON')
print("✓ Created vulnerability_map.geojson")
```

---

### Phase 3: Database Setup (Hour 4-6)

**Option A: PostgreSQL with PostGIS (Recommended for production)**

```bash
# Install PostgreSQL with PostGIS
brew install postgresql postgis

# Create database
createdb vulnerability_db
psql vulnerability_db -c "CREATE EXTENSION postgis;"

# Import data
ogr2ogr -f PostgreSQL PG:"dbname=vulnerability_db" data/vulnerability_map.geojson -nln counties
```

**Option B: SQLite (Recommended for MVP/Demo)**

```python
import sqlite3
import json

# Create SQLite database
conn = sqlite3.connect('data/vulnerability.db')

# Load GeoJSON
with open('data/vulnerability_map.geojson') as f:
    geojson = json.load(f)

# Create table
conn.execute('''
    CREATE TABLE counties (
        fips TEXT PRIMARY KEY,
        name TEXT,
        geometry TEXT,
        gdp_2023 REAL,
        svi_score REAL,
        hurricane_risk TEXT,
        vuln_score REAL
    )
''')

# Insert data
for feature in geojson['features']:
    props = feature['properties']
    conn.execute('''
        INSERT INTO counties VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        props['FIPS'],
        props['name'],
        json.dumps(feature['geometry']),
        props.get('GDP_2023'),
        props.get('RPL_THEMES'),
        props.get('HRCN_RISKR'),
        props.get('VULN_SCORE')
    ))

conn.commit()
conn.close()
```

---

### Phase 4: API Development (Hour 6-12)

**FastAPI Backend:**

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import geopandas as gpd
import json

app = FastAPI(title="Lanzat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Load data at startup
vulnerability_data = gpd.read_file('data/vulnerability_map.geojson')

@app.get("/api/counties")
def get_all_counties():
    """Get all Florida counties with vulnerability scores"""
    return json.loads(vulnerability_data.to_json())

@app.get("/api/county/{fips}")
def get_county(fips: str):
    """Get specific county by FIPS code"""
    county = vulnerability_data[vulnerability_data['FIPS'] == fips]
    if len(county) == 0:
        return {"error": "County not found"}
    return json.loads(county.to_json())['features'][0]

@app.get("/api/top-vulnerable/{n}")
def get_top_vulnerable(n: int = 10):
    """Get top N most vulnerable counties"""
    top_counties = vulnerability_data.nlargest(n, 'VULN_SCORE')
    return json.loads(top_counties.to_json())

@app.get("/api/stats")
def get_statistics():
    """Get summary statistics"""
    return {
        "total_counties": len(vulnerability_data),
        "avg_vulnerability": float(vulnerability_data['VULN_SCORE'].mean()),
        "highest_risk": vulnerability_data.nlargest(1, 'VULN_SCORE')['name'].values[0],
        "total_gdp": float(vulnerability_data['GDP_2023'].sum()),
        "avg_svi": float(vulnerability_data['RPL_THEMES'].mean())
    }
```

**Run API:**
```bash
uvicorn main:app --reload
# Access at http://localhost:8000
# Docs at http://localhost:8000/docs
```

---

### Phase 5: Frontend Development (Hour 12-20)

**React Component Structure:**

```
src/
├── components/
│   ├── Map/
│   │   ├── Lanzat.jsx
│   │   ├── CountyLayer.jsx
│   │   └── MapLegend.jsx
│   ├── Dashboard/
│   │   ├── StatsCards.jsx
│   │   ├── VulnerabilityChart.jsx
│   │   └── TopCountiesList.jsx
│   └── CountyDetails/
│       └── CountyPopup.jsx
├── services/
│   └── api.js
└── App.jsx
```

**Example Map Component:**

```javascript
// components/Map/Lanzat.jsx
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import { useEffect, useState } from 'react';
import axios from 'axios';

function Lanzat() {
  const [countyData, setCountyData] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:8000/api/counties')
      .then(res => setCountyData(res.data));
  }, []);

  const getColor = (score) => {
    return score > 0.8 ? '#b10026' :
           score > 0.6 ? '#fc4e2a' :
           score > 0.4 ? '#feb24c' :
           score > 0.2 ? '#ffeda0' :
                         '#ffffcc';
  };

  const style = (feature) => ({
    fillColor: getColor(feature.properties.VULN_SCORE),
    weight: 1,
    opacity: 1,
    color: 'white',
    fillOpacity: 0.7
  });

  const onEachCounty = (feature, layer) => {
    layer.bindPopup(`
      <strong>${feature.properties.name}</strong><br/>
      Vulnerability Score: ${(feature.properties.VULN_SCORE * 100).toFixed(1)}%<br/>
      GDP: $${(feature.properties.GDP_2023 / 1000).toFixed(1)}B<br/>
      Hurricane Risk: ${feature.properties.HRCN_RISKR}
    `);
  };

  if (!countyData) return <div>Loading...</div>;

  return (
    <MapContainer
      center={[27.6648, -81.5158]}
      zoom={7}
      style={{ height: '600px', width: '100%' }}
    >
      <TileLayer
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap contributors'
      />
      <GeoJSON
        data={countyData}
        style={style}
        onEachFeature={onEachCounty}
      />
    </MapContainer>
  );
}
```

---

### Phase 6: Testing & Deployment (Hour 20-24)

**Testing Checklist:**
- [ ] All counties load correctly
- [ ] Vulnerability scores calculated
- [ ] Map displays with proper colors
- [ ] Popups show county data
- [ ] API endpoints respond correctly
- [ ] Mobile responsive
- [ ] Cross-browser compatibility

**Deployment Options:**

**Backend:**
- Railway: https://railway.app/ (PostgreSQL included)
- Render: https://render.com/ (Free tier)
- Fly.io: https://fly.io/ (Global edge)

**Frontend:**
- Vercel: https://vercel.com/ (Next.js optimized)
- Netlify: https://netlify.com/ (SPA support)
- GitHub Pages: Free static hosting

**Quick Deploy (Vercel + Railway):**

```bash
# Backend (Railway)
railway login
railway init
railway up

# Frontend (Vercel)
vercel login
vercel --prod
```

---

## SUMMARY

### Total Resource Checklist

**CRITICAL DATASETS (Must Download):**
- [x] Florida county boundaries (GeoJSON) - 2 MB
- [x] IBTrACS hurricane tracks - 30 MB
- [x] BEA county GDP - 3 MB
- [ ] CDC SVI Florida - 5 MB (manual)
- [ ] FEMA NRI Florida - 20 MB (manual)

**TOTAL MVP:** ~60 MB, 5-10 minutes download

**IMPORTANT DATASETS (Should Download):**
- [ ] Storm surge zones - 100 MB
- [ ] Flood zones - 50 MB

**OPTIONAL (Nice to Have):**
- [ ] Satellite imagery - 1-2 GB per scene
- [ ] Real-time weather API

---

### Quick Start Command Sequence

```bash
# 1. Setup project
git clone <your-repo>
cd hackathon

# 2. Download data
python download_data.py

# 3. Manual downloads
# - CDC SVI: Visit URL and download Florida CSV
# - FEMA NRI: Visit URL and download Florida CSV

# 4. Integrate data
python integrate_data.py

# 5. Start backend
pip install -r requirements.txt
uvicorn main:app --reload

# 6. Start frontend
cd frontend
npm install
npm run dev

# 7. Open browser
# http://localhost:3000
```

---

### Contact & Support

**Dataset Issues:**
- NOAA IBTrACS: https://www.ncei.noaa.gov/support
- BEA API: developers@bea.gov
- CDC SVI: svi_coordinator@cdc.gov
- FEMA NRI: https://hazards.fema.gov/nri/

**Technical Support:**
- GeoPandas: https://gitter.im/geopandas/geopandas
- React-Leaflet: https://github.com/PaulLeCam/react-leaflet/discussions
- FastAPI: https://github.com/tiangolo/fastapi/discussions

---

**Last Updated:** October 4, 2025
**Maintainer:** Lanzat Team
**License:** Public Domain (datasets), MIT (code)
