# Lanzat Backend

Hurricane Economic Vulnerability Platform for Florida - FastAPI Backend

## Quick Start

### 1. Install Dependencies

```bash
# Install GDAL first (macOS)
brew install gdal

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### 2. Download Data

```bash
# Automated downloads
python scripts/download_data.py

# Manual downloads (follow printed instructions)
# - CDC Social Vulnerability Index
# - FEMA National Risk Index
```

### 3. Process Data

```bash
# Generate vulnerability scores
python scripts/process_data.py
```

### 4. Run API

```bash
# Start FastAPI server
python app/main.py

# Or use uvicorn directly
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

## API Endpoints

### GET `/api/counties`
Get all Florida counties with vulnerability scores (GeoJSON)

**Query Parameters:**
- `include_geometry` (bool): Include geometry data (default: true)

**Response:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "NAME": "Miami-Dade",
        "vulnerability_score": 0.87,
        "hurricane_risk": 0.92,
        "social_vulnerability": 0.68,
        "economic_vulnerability": 0.45,
        "gdp": 180000,
        "population": 2800000,
        "risk_category": "Critical"
      },
      "geometry": {...}
    }
  ]
}
```

### GET `/api/counties/{county_name}`
Get detailed information for a specific county

**Example:** `/api/counties/Miami-Dade`

### GET `/api/top-vulnerable`
Get top N most vulnerable counties

**Query Parameters:**
- `limit` (int): Number of counties (default: 10, max: 67)

### GET `/api/stats`
Get summary statistics

### GET `/health`
Health check endpoint

## Data Sources

- **County Boundaries:** US Census Bureau TIGER/Line Shapefiles
- **Hurricane Data:** NOAA IBTrACS Database
- **GDP Data:** Bureau of Economic Analysis (BEA)
- **Social Vulnerability:** CDC Social Vulnerability Index (SVI)
- **Risk Data:** FEMA National Risk Index

## Project Structure

```
lanzat-backend/
├── app/
│   ├── __init__.py
│   └── main.py              # FastAPI application
├── data/
│   ├── raw/                 # Downloaded datasets
│   └── processed/           # Generated GeoJSON files
├── scripts/
│   ├── download_data.py     # Data download script
│   └── process_data.py      # Data processing pipeline
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Deployment

### Railway

```bash
# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

### Render

```bash
# Create render.yaml in project root
# Push to GitHub
# Connect repository in Render dashboard
```

### Environment Variables

```bash
FRONTEND_URL=https://lanzat.vercel.app
ALLOWED_ORIGINS=https://lanzat.vercel.app
BEA_API_KEY=your_api_key_here
```

## Development

### Run Tests

```bash
pytest tests/
```

### Format Code

```bash
black app/ scripts/
```

### Lint

```bash
flake8 app/ scripts/
```

## Troubleshooting

### GDAL Installation Issues

```bash
# macOS
brew install gdal
export GDAL_CONFIG=/opt/homebrew/bin/gdal-config
pip install geopandas --no-build-isolation

# Ubuntu/Debian
sudo apt-get install gdal-bin libgdal-dev
pip install gdal==$(gdal-config --version)
```

### Data Not Found Errors

Make sure you've run the data processing pipeline:

```bash
python scripts/download_data.py
python scripts/process_data.py
```

Check that files exist in `data/processed/`:
- `counties.geojson`
- `summary_stats.json`

## License

MIT License - See LICENSE file for details
