# Lanzat - Complete Setup Guide

## 🚀 Quick Start (15 Minutes)

### Prerequisites

- **macOS** with Homebrew installed
- **Python 3.11** installed
- **Node.js 18+** installed
- **Git** installed

### Backend Setup (10 minutes)

```bash
cd /Users/nade/Projects/hackathon/lanzat-backend

# 1. Install GDAL (CRITICAL - do this first!)
brew install gdal

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env

# 5. Download data (automated + manual)
python scripts/download_data.py

# 6. Manual downloads (follow printed instructions):
#    - CDC Social Vulnerability Index
#    - FEMA National Risk Index
#    Save to data/raw/ directory

# 7. Process data and calculate vulnerability scores
python scripts/process_data.py

# 8. Start the API
python app/main.py
```

Backend will run at **http://localhost:8000**

Test it: http://localhost:8000/docs

### Frontend Setup (5 minutes)

```bash
cd /Users/nade/Projects/hackathon/lanzat-frontend

# 1. Install dependencies
npm install --legacy-peer-deps

# 2. Create environment file
cp .env.example .env.local

# 3. Start development server
npm run dev
```

Frontend will run at **http://localhost:3000**

---

## 📂 Project Structure

```
hackathon/
├── lanzat-backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py                 # FastAPI application
│   ├── data/
│   │   ├── raw/                    # Downloaded datasets
│   │   └── processed/              # Generated vulnerability data
│   ├── scripts/
│   │   ├── download_data.py        # Data downloader
│   │   └── process_data.py         # Vulnerability calculator
│   ├── requirements.txt
│   └── README.md
│
└── lanzat-frontend/
    ├── components/
    │   ├── Map.tsx                 # Leaflet map
    │   ├── Dashboard.tsx           # Stats & charts
    │   ├── Header.tsx              # Top navigation
    │   └── Legend.tsx              # Map legend
    ├── pages/
    │   ├── index.tsx               # Main page
    │   └── _app.tsx                # App config
    ├── package.json
    └── FRONTEND_README.md
```

---

## 🎯 Development Workflow

### 1. Backend Development

```bash
cd lanzat-backend
source venv/bin/activate

# Run API with hot reload
uvicorn app.main:app --reload

# Or
python app/main.py
```

**API Documentation:** http://localhost:8000/docs

**Key Endpoints:**
- GET `/api/counties` - All counties (GeoJSON)
- GET `/api/counties/{name}` - Specific county
- GET `/api/top-vulnerable` - Top 10 vulnerable
- GET `/api/stats` - Summary statistics
- GET `/health` - Health check

### 2. Frontend Development

```bash
cd lanzat-frontend

# Run dev server with fast refresh
npm run dev
```

**Access:** http://localhost:3000

**Features:**
- Interactive Florida county map
- Click counties for details
- Top 10 vulnerable counties list
- GDP vs Risk scatter plot
- Vulnerability heatmap

### 3. Data Updates

If you need to update data or recalculate scores:

```bash
cd lanzat-backend
source venv/bin/activate

# Re-download data
python scripts/download_data.py

# Recalculate vulnerability scores
python scripts/process_data.py

# Restart API
python app/main.py
```

---

## 🚀 Deployment

### Backend Deployment (Railway)

```bash
cd lanzat-backend

# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Add environment variables in Railway dashboard:
#    FRONTEND_URL=https://lanzat.vercel.app
#    ALLOWED_ORIGINS=https://lanzat.vercel.app

# 5. Deploy
railway up

# 6. Upload processed data to Railway
#    Option A: Use Railway Volumes
#    Option B: Include in deployment (add to git)
git add data/processed/counties.geojson
git commit -m "Add processed data"
railway up
```

**Backend URL:** https://lanzat-backend.up.railway.app

### Frontend Deployment (Vercel)

```bash
cd lanzat-frontend

# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Deploy
vercel deploy --prod

# 4. Add environment variable in Vercel dashboard:
#    NEXT_PUBLIC_API_URL=https://lanzat-backend.up.railway.app
```

**Frontend URL:** https://lanzat.vercel.app

---

## 🔧 Troubleshooting

### GDAL Installation Issues

**Problem:** `pip install geopandas` fails with GDAL errors

**Solution:**
```bash
# macOS
brew install gdal
export GDAL_CONFIG=/opt/homebrew/bin/gdal-config
pip install geopandas --no-build-isolation

# If still failing, use conda
conda install -c conda-forge geopandas
```

### Map Not Rendering

**Problem:** Leaflet map shows blank screen

**Solution:**
1. Check browser console for errors
2. Verify backend is running: http://localhost:8000/health
3. Check CORS settings in `app/main.py`
4. Verify `NEXT_PUBLIC_API_URL` in `.env.local`

### CORS Errors

**Problem:** Frontend can't access backend API

**Solution:**

Backend (`app/main.py`):
```python
allow_origins=[
    "http://localhost:3000",
    "https://lanzat.vercel.app"
]
```

### Data Not Found

**Problem:** API returns 404 for `/api/counties`

**Solution:**
```bash
cd lanzat-backend
source venv/bin/activate

# Check if processed data exists
ls data/processed/counties.geojson

# If missing, run processing
python scripts/process_data.py
```

### Deployment Issues

**Railway Backend:**
- Make sure `requirements.txt` is up to date
- Check Railway logs: `railway logs`
- Verify environment variables are set
- Ensure processed data is included in deployment

**Vercel Frontend:**
- Check build logs in Vercel dashboard
- Verify `NEXT_PUBLIC_API_URL` environment variable
- Make sure backend allows Vercel domain in CORS

---

## 📊 Data Sources

1. **Florida County Boundaries**
   - Source: US Census Bureau TIGER/Line Shapefiles
   - URL: https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/
   - Format: Shapefile → GeoJSON

2. **Hurricane Historical Data**
   - Source: NOAA IBTrACS Database
   - URL: https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/
   - Format: CSV

3. **County GDP Data**
   - Source: Bureau of Economic Analysis (BEA)
   - URL: https://apps.bea.gov/API/signup/
   - Format: JSON/CSV

4. **Social Vulnerability Index**
   - Source: CDC/ATSDR SVI
   - URL: https://www.atsdr.cdc.gov/placeandhealth/svi/
   - Format: CSV

5. **FEMA Risk Data**
   - Source: FEMA National Risk Index
   - URL: https://hazards.fema.gov/nri/data-resources
   - Format: CSV

---

## 🧮 Vulnerability Score Formula

```python
vulnerability_score = (
    0.40 * hurricane_risk +           # Historical hurricane exposure
    0.30 * social_vulnerability +     # CDC SVI metrics
    0.30 * economic_vulnerability     # GDP per capita (inverse)
)
```

**Risk Categories:**
- **Critical:** 80-100% (Dark Red)
- **High:** 60-80% (Red)
- **Moderate:** 40-60% (Orange)
- **Low:** 20-40% (Yellow)
- **Very Low:** 0-20% (Light Yellow)

---

## 🎤 Demo Script (3 Minutes)

### Opening (30 seconds)
"Hurricane Ian caused $12.6 billion in losses to Florida. State and local governments spend billions on disaster preparedness every year. But which communities need it most?"

### Problem (30 seconds)
"FEMA shows where hurricanes might hit. CDC shows who is socially vulnerable. But nobody combines economic impact, social vulnerability, and disaster risk to help governors prioritize preparedness funding."

### Demo (90 seconds)
1. **Show Map:** "Lanzat scores all 67 Florida counties"
2. **Click County:** "Here's Miami-Dade: 87/100 vulnerability score"
3. **Show Breakdown:** "High hurricane risk + large population + economic exposure"
4. **Show Dashboard:** "Top 10 counties need urgent investment"
5. **Show Chart:** "GDP vs Risk: find high-value, high-risk areas"

### Impact (30 seconds)
"This helps governors allocate Florida's $2.1 billion preparedness budget more effectively. Protect vulnerable communities before disasters strike. We're ready to expand to Texas, Louisiana, and all hurricane-prone states."

---

## ✅ Pre-Demo Checklist

**24 Hours Before:**
- [ ] Backend deployed to Railway (test all endpoints)
- [ ] Frontend deployed to Vercel (test on mobile)
- [ ] Data processed and uploaded
- [ ] CORS configured for production domains
- [ ] Demo scenario tested (Miami-Dade → Top 10 → Chart)

**1 Hour Before:**
- [ ] Demo site loaded in browser (don't close tab!)
- [ ] Backup video/screenshots ready
- [ ] Pitch script memorized
- [ ] Laptop charged and plugged in
- [ ] Internet connection tested

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🆘 Support

If you encounter issues:

1. Check troubleshooting section above
2. Review error messages in console/logs
3. Verify all dependencies are installed
4. Check that data processing completed successfully

**Backend Health Check:** http://localhost:8000/health
**Frontend Dev Server:** http://localhost:3000

Good luck with your hackathon! 🚀🌊
