# Lanzat - Quick Start Guide

**Last Updated:** October 4, 2025

---

## 🚀 5-Minute Setup

### Step 1: Download Critical Data (2 minutes)

```bash
# Clone or navigate to project
cd /Users/nade/Projects/hackathon

# Install Python requirements
pip install requests pandas openpyxl geopandas

# Run automated download
python download_data.py --process
```

**This downloads:**
- ✅ Florida county boundaries (2 MB)
- ✅ Hurricane tracks (30 MB)
- ✅ County GDP data (3 MB)

### Step 2: Manual Downloads (3 minutes)

#### CDC Social Vulnerability Index
1. Visit: https://www.atsdr.cdc.gov/place-health/php/svi/svi-data-documentation-download.html
2. Select: **2022** → **Florida** → **County-level** → **CSV**
3. Save as: `data/florida_svi_2022.csv`

#### FEMA National Risk Index
1. Visit: https://hazards.fema.gov/nri/data-resources
2. Click: **Download Data** → **County-level**
3. Select: **Florida** (or download national and filter)
4. Save as: `data/fema_nri_florida.csv`

### Step 3: Verify Setup

```bash
ls -lh data/

# Should see:
# florida_counties.geojson
# ibtracs_north_atlantic.csv
# county_gdp_2023.xlsx
# florida_svi_2022.csv       ← manual
# fema_nri_florida.csv        ← manual
```

---

## 📊 Data Overview

### Critical Datasets (60 MB total)

| Dataset | Source | Size | What It Contains |
|---------|--------|------|-----------------|
| **County Boundaries** | Census/GitHub | 2 MB | GeoJSON of 67 FL counties |
| **Hurricane Tracks** | NOAA IBTrACS | 30 MB | Historical storms 1840s-2024 |
| **County GDP** | BEA | 3 MB | Economic data 2001-2023 |
| **Social Vulnerability** | CDC | 5 MB | SVI scores & demographics |
| **Hurricane Risk** | FEMA NRI | 20 MB | Risk ratings & expected losses |

---

## 🔧 Key Data Fields

### Florida Counties GeoJSON
```javascript
{
  "FIPS": "12086",           // County code
  "NAME": "Miami-Dade",      // County name
  "geometry": {...}          // Polygon coordinates
}
```

### Hurricane Tracks (IBTrACS)
```csv
NAME,ISO_TIME,LAT,LON,USA_WIND,USA_PRES,BASIN
IAN,2022-09-28,26.6,-82.3,115,940,NA
MICHAEL,2018-10-10,30.1,-85.4,140,919,NA
```

### County GDP (BEA)
```csv
FIPS,GeoName,GDP_2023
12086,Miami-Dade,372450    # $372.45 billion
12099,Palm Beach,107896
```

### Social Vulnerability Index (CDC)
```csv
FIPS,COUNTY,RPL_THEMES,RPL_THEME1,RPL_THEME2,RPL_THEME3,RPL_THEME4
12086,Miami-Dade,0.8532,0.7234,0.6421,0.9123,0.7845
```
- `RPL_THEMES`: Overall SVI (0-1, higher = more vulnerable)
- `RPL_THEME1`: Socioeconomic status
- `RPL_THEME2`: Household composition
- `RPL_THEME3`: Minority/language
- `RPL_THEME4`: Housing/transportation

### FEMA National Risk Index
```csv
STCOFIPS,COUNTY,HRCN_RISKR,HRCN_EEAL,RISK_RATNG
12086,Miami-Dade County,Very High,125000000,Relatively High
```
- `HRCN_RISKR`: Hurricane risk rating
- `HRCN_EEAL`: Expected Annual Loss (dollars)
- `RISK_RATNG`: Overall risk rating

---

## 🧮 Vulnerability Score Formula

### Recommended Algorithm

```python
def calculate_vulnerability(county_data):
    """
    Composite vulnerability score (0-1)
    Higher score = more vulnerable
    """
    # 1. Social Vulnerability (40%)
    svi_score = county_data['RPL_THEMES']  # Already 0-1

    # 2. Hurricane Risk (40%)
    risk_map = {
        'Very Low': 0.1,
        'Relatively Low': 0.3,
        'Relatively Moderate': 0.5,
        'Relatively High': 0.7,
        'Very High': 0.9
    }
    hurricane_score = risk_map.get(county_data['HRCN_RISKR'], 0.5)

    # 3. Economic Vulnerability (20%)
    # Lower GDP per capita = higher vulnerability
    gdp_per_capita = county_data['GDP_2023'] / county_data['population']
    max_gdp_per_capita = 150000  # Normalize against $150k
    economic_score = 1 - min(gdp_per_capita / max_gdp_per_capita, 1)

    # Weighted combination
    vulnerability_score = (
        svi_score * 0.4 +
        hurricane_score * 0.4 +
        economic_score * 0.2
    )

    return vulnerability_score
```

### Alternative: Risk × Impact Approach

```python
def calculate_risk_impact_vulnerability(county_data):
    """
    Risk × Impact methodology
    """
    # Risk: Likelihood of hurricane
    risk = county_data['HRCN_AFREQ']  # Annual frequency

    # Impact: Potential damage
    exposure = county_data['HRCN_EEAL'] / county_data['GDP_2023']  # EAL as % of GDP
    sensitivity = county_data['RPL_THEMES']  # Social vulnerability

    # Vulnerability = Risk × (Exposure + Sensitivity)
    vulnerability = risk * (exposure * 0.5 + sensitivity * 0.5)

    return min(vulnerability, 1.0)  # Cap at 1.0
```

---

## 🗺️ Map Color Scheme

### Recommended Choropleth Colors

```javascript
function getColor(vulnerabilityScore) {
  return vulnerabilityScore > 0.8 ? '#b10026' :  // Very High - Dark Red
         vulnerabilityScore > 0.6 ? '#fc4e2a' :  // High - Red
         vulnerabilityScore > 0.4 ? '#feb24c' :  // Moderate - Orange
         vulnerabilityScore > 0.2 ? '#ffeda0' :  // Low - Yellow
                                     '#ffffcc';  // Very Low - Light Yellow
}
```

### Accessibility-Friendly (Color-blind safe)

```javascript
function getColorAccessible(score) {
  return score > 0.8 ? '#d73027' :  // Dark orange-red
         score > 0.6 ? '#fc8d59' :  // Orange
         score > 0.4 ? '#fee08b' :  // Light orange
         score > 0.2 ? '#d9ef8b' :  // Light green
                       '#91cf60';   // Green
}
```

---

## 📈 Dashboard Metrics

### Key Performance Indicators (KPIs)

```javascript
// Calculate from integrated dataset
const kpis = {
  totalCounties: 67,
  avgVulnerability: mean(vulnerabilityScores),
  highRiskCounties: counties.filter(c => c.vuln_score > 0.7).length,
  totalGDP: sum(counties.map(c => c.GDP_2023)),
  totalPopulationAtRisk: sum(counties.filter(c => c.HRCN_RISKR === 'Very High').map(c => c.population))
};
```

### Top Vulnerable Counties Table

```javascript
const topVulnerable = counties
  .sort((a, b) => b.vuln_score - a.vuln_score)
  .slice(0, 10)
  .map(county => ({
    name: county.NAME,
    score: (county.vuln_score * 100).toFixed(1) + '%',
    gdp: `$${(county.GDP_2023 / 1000).toFixed(1)}B`,
    risk: county.HRCN_RISKR,
    svi: (county.RPL_THEMES * 100).toFixed(1) + '%'
  }));
```

### Scatter Plot: GDP vs Vulnerability

```javascript
// Recharts scatter plot data
const scatterData = counties.map(c => ({
  x: c.GDP_2023 / 1000,        // GDP in billions
  y: c.vuln_score * 100,       // Vulnerability %
  name: c.NAME,
  size: c.population / 100000  // Bubble size
}));

// React component
<ScatterChart>
  <XAxis dataKey="x" name="GDP" unit="B" />
  <YAxis dataKey="y" name="Vulnerability" unit="%" />
  <Scatter data={scatterData} fill="#8884d8" />
</ScatterChart>
```

---

## 🚦 MVP Feature Checklist (24-hour hackathon)

### Hour 0-4: Data Setup ✅
- [ ] Download all datasets
- [ ] Process and clean data
- [ ] Calculate vulnerability scores
- [ ] Create integrated GeoJSON

### Hour 4-8: Backend API
- [ ] FastAPI setup
- [ ] `/api/counties` - Get all counties
- [ ] `/api/county/{fips}` - Get single county
- [ ] `/api/top-vulnerable` - Top 10 list
- [ ] `/api/stats` - Summary statistics
- [ ] CORS configuration

### Hour 8-16: Frontend
- [ ] React + Leaflet map setup
- [ ] County choropleth layer
- [ ] Color-coded by vulnerability
- [ ] County popups with details
- [ ] Legend component
- [ ] Dashboard with KPI cards
- [ ] Top 10 vulnerable counties list
- [ ] Scatter plot (GDP vs Vulnerability)

### Hour 16-20: Polish
- [ ] Mobile responsive
- [ ] Loading states
- [ ] Error handling
- [ ] Filters (by risk level, GDP range)
- [ ] Search county by name
- [ ] Export data functionality

### Hour 20-24: Deployment & Pitch
- [ ] Deploy backend (Railway/Render)
- [ ] Deploy frontend (Vercel/Netlify)
- [ ] Test live demo
- [ ] Create pitch deck
- [ ] Record demo video

---

## 🔗 Essential Links

### Data Sources
- **NOAA Hurricane Tracks:** https://www.ncei.noaa.gov/products/international-best-track-archive
- **BEA County GDP:** https://www.bea.gov/data/gdp/gdp-county-metro-and-other-areas
- **CDC SVI:** https://www.atsdr.cdc.gov/place-health/php/svi/svi-data-documentation-download.html
- **FEMA NRI:** https://hazards.fema.gov/nri/data-resources
- **Census Boundaries:** https://github.com/danielcs88/fl_geo_json

### Documentation
- **GeoPandas:** https://geopandas.org/en/stable/
- **React-Leaflet:** https://react-leaflet.js.org/
- **Recharts:** https://recharts.org/
- **FastAPI:** https://fastapi.tiangolo.com/

### Deployment
- **Backend:** https://railway.app/ | https://render.com/
- **Frontend:** https://vercel.com/ | https://netlify.com/
- **Database:** PostgreSQL on Railway/Render

---

## 🎯 Sample Use Cases

### 1. Emergency Management
"Which counties need priority evacuation resources?"
→ Filter counties with `vuln_score > 0.7` and `HRCN_RISKR = 'Very High'`

### 2. Infrastructure Investment
"Where should we prioritize hurricane-resistant infrastructure?"
→ High vulnerability + high GDP counties = max ROI

### 3. Insurance Planning
"Which areas have highest expected annual losses?"
→ Sort by `HRCN_EEAL` (Expected Annual Loss)

### 4. Social Services
"Where are the most socially vulnerable populations?"
→ Filter by `RPL_THEMES > 0.75` (top quartile SVI)

---

## 🐛 Troubleshooting

### Data Download Issues

**Problem:** IBTrACS download fails
```bash
# Alternative: Download manually
curl -o data/ibtracs_north_atlantic.csv https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.NA.list.v04r01.csv
```

**Problem:** BEA Excel file corrupted
```bash
# Try different format
# Download from interactive tables instead:
# https://apps.bea.gov/itable/?ReqID=70&step=1
```

### Integration Issues

**Problem:** FIPS codes don't match
```python
# Standardize FIPS codes (5 digits, zero-padded)
df['FIPS'] = df['FIPS'].astype(str).str.zfill(5)

# Remove state code if needed (keep last 3 digits)
df['COUNTY_FIPS'] = df['FIPS'].str[-3:]
```

**Problem:** Missing data for some counties
```python
# Check for missing values
print(df.isnull().sum())

# Fill missing values with median
df['vuln_score'].fillna(df['vuln_score'].median(), inplace=True)
```

### Map Display Issues

**Problem:** Map doesn't render
```javascript
// Ensure Leaflet CSS is imported
import 'leaflet/dist/leaflet.css';

// Set map height explicitly
<MapContainer style={{ height: '600px', width: '100%' }}>
```

**Problem:** GeoJSON not showing
```javascript
// Verify GeoJSON structure
console.log(geoJsonData.type);  // Should be 'FeatureCollection'
console.log(geoJsonData.features.length);  // Should be 67
```

---

## 📞 Support & Resources

### Dataset Issues
- **NOAA:** https://www.ncei.noaa.gov/support
- **BEA:** developers@bea.gov
- **CDC:** svi_coordinator@cdc.gov
- **FEMA:** https://hazards.fema.gov/nri/

### Technical Help
- **GeoPandas:** https://gitter.im/geopandas/geopandas
- **React-Leaflet:** https://github.com/PaulLeCam/react-leaflet/discussions
- **FastAPI:** https://github.com/tiangolo/fastapi/discussions

---

## 🏆 Hackathon Tips

### Time Management
- **Hours 0-4:** Data acquisition (use download script!)
- **Hours 4-12:** Core functionality (API + basic map)
- **Hours 12-20:** Features & polish
- **Hours 20-24:** Deployment & pitch prep

### Must-Have Features
1. Interactive map with county popups ✅
2. Color-coded vulnerability scores ✅
3. Top 10 vulnerable counties list ✅
4. Summary statistics dashboard ✅

### Nice-to-Have Features
- Search county by name
- Filter by risk level
- Compare multiple counties
- Time-series hurricane animation
- Export data to CSV

### Presentation Tips
1. **Start with impact:** "X million Floridians live in high-risk areas"
2. **Show the map first:** Visual impact
3. **Walk through a use case:** Emergency manager perspective
4. **Highlight unique insights:** GDP × Vulnerability findings
5. **Demo live filtering:** Interactive > static
6. **End with scalability:** "Expandable to all coastal states"

---

**Good luck! 🚀**

For detailed documentation, see: `/Users/nade/Projects/hackathon/RESOURCE_GUIDE.md`
