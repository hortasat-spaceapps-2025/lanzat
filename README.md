# Lanzat - Hurricane Economic Vulnerability Platform

![Platform](https://img.shields.io/badge/Platform-Florida%20Counties-blue)
![Data](https://img.shields.io/badge/Data-NOAA%20IBTrACS-green)
![Real--time](https://img.shields.io/badge/Real--time-Hurricane%20Tracking-red)

**Complete system for analyzing hurricane risk, economic vulnerability, and social impact across 67 Florida counties using NOAA historical data (1851-2023) and real-time tracking.**

---

## 🌐 Demo

- **Frontend**: https://lanzat.ignacio.tech
- **Backend API**: https://lanzat.api.ignacio.tech
- **API Docs**: https://lanzat.api.ignacio.tech/docs

---

## 🌊 Features

### Historical Analysis
- **NOAA IBTrACS Data**: 704 historical storms from 1851-2023
- **Risk Calculation**: Based on frequency (50%), average intensity (30%), maximum intensity (20%)
- **Vulnerability Model**: 25% Risk + 20% Social + 20% Economic + 20% Property + 15% Rural

### Real-time Capabilities
- **Active Storm Tracking**: Integration with NOAA NHC API
- **County Threat Assessment**: Distance-based threat levels
- **Critical Alerts**: Combined analysis of current threat + historical vulnerability

---

## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/hortasat-spaceapps-2025/lanzat.git
cd lanzat

# Start with Docker (local development)
docker-compose -f docker-compose.local.yml up -d

# Access
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Production (Coolify)

```bash
# Use docker-compose.yml (Coolify handles proxy)
docker-compose up -d
```

---

## 📊 API Endpoints

### Historical Data
- `GET /api/counties` - All counties with vulnerability scores
- `GET /api/counties/{name}` - Specific county details
- `GET /api/top-vulnerable?limit=10` - Top vulnerable counties
- `GET /api/stats` - General statistics
- `GET /api/enhanced/critical-rural` - Critical rural zones
- `GET /api/enhanced/correlations` - Correlation analysis

### Real-time Data
- `GET /api/realtime/active-storms` - Active hurricanes (NOAA NHC)
- `GET /api/realtime/county-threats` - County-level threats
- `GET /api/realtime/critical-threats` - Counties under critical alert
- `POST /api/realtime/refresh` - Refresh real-time data

### System
- `GET /health` - Service health check
- `GET /` - API information and available endpoints

---

## 🛠️ Tech Stack

**Backend**:
- Python 3.11
- FastAPI (REST API)
- GeoPandas (geospatial analysis)
- GDAL (satellite data processing)
- Shapely (geometries)

**Frontend**:
- Next.js 14 (React framework)
- TypeScript
- Leaflet (interactive maps)
- Tailwind CSS (styling)

**Infrastructure**:
- Docker + Docker Compose
- Coolify (deployment)
- Traefik (reverse proxy)

---

## 📁 Project Structure

```
lanzat/
├── docker-compose.yml              # Production (Coolify)
├── docker-compose.local.yml        # Local development
├── lanzat-backend/
│   ├── Dockerfile
│   ├── app/
│   │   └── main.py                 # FastAPI application
│   ├── scripts/
│   │   ├── download_noaa_hurricanes.py     # Download historical data
│   │   ├── calculate_real_hurricane_risk.py # Calculate risks
│   │   ├── enrich_with_statista.py         # Enrich with economic data
│   │   └── fetch_active_hurricanes.py      # Real-time data
│   ├── data/
│   │   ├── raw/                    # Raw data
│   │   └── processed/              # Processed GeoJSON
│   └── requirements.txt
└── lanzat-frontend/
    ├── Dockerfile
    ├── pages/
    │   └── index.tsx               # Main page
    ├── components/
    │   ├── Map.tsx                 # Interactive Florida map
    │   └── Dashboard.tsx           # Dashboard with KPIs
    ├── next.config.mjs
    └── package.json
```

---

## 🔧 Configuration

### Environment Variables

**Backend (`lanzat-backend/.env`):**
```bash
ALLOWED_ORIGINS=https://lanzat.ignacio.tech
PYTHONUNBUFFERED=1
```

**Frontend (`lanzat-frontend/.env.local`):**
```bash
NEXT_PUBLIC_API_URL=https://lanzat.api.ignacio.tech
NODE_ENV=production
```

---

## 🎯 Deployment on Coolify

### Step 1: Coolify UI Configuration

1. **Create new resource** → Docker Compose
2. **Repository**: `https://github.com/hortasat-spaceapps-2025/lanzat`
3. **Branch**: `main`
4. **Compose File**: `docker-compose.yml`

### Step 2: Configure Domains

**Backend:**
- Service: `backend`
- Domain: `lanzat.api.ignacio.tech`
- Port: `8000`

**Frontend:**
- Service: `frontend`
- Domain: `lanzat.ignacio.tech`
- Port: `3000`

### Step 3: Environment Variables (Coolify)

```bash
ALLOWED_ORIGINS=https://lanzat.ignacio.tech
NEXT_PUBLIC_API_URL=https://lanzat.api.ignacio.tech
```

### Step 4: Deploy

Click **Deploy** - Coolify will automatically build and deploy.

### Step 5: Generate Initial Data

```bash
# Find backend container ID
docker ps | grep backend

# Execute generation scripts
docker exec <backend-container-id> python scripts/download_noaa_hurricanes.py
docker exec <backend-container-id> python scripts/calculate_real_hurricane_risk.py
docker exec <backend-container-id> python scripts/enrich_with_statista.py
docker exec <backend-container-id> python scripts/fetch_active_hurricanes.py
```

### Step 6 (Optional): Cron Job for Updates

Configure in Coolify to update active hurricanes every 30 minutes:
```bash
*/30 * * * * python scripts/fetch_active_hurricanes.py
```

---

## 🧮 Vulnerability Algorithm

### Score Formula

```python
vulnerability_score = (
    svi_score * 0.4 +          # 40% Social Vulnerability Index
    hurricane_score * 0.4 +     # 40% Hurricane risk
    economic_score * 0.2        # 20% Economic vulnerability
)
```

**Components:**

1. **Social Vulnerability (SVI)** - CDC Social Vulnerability Index
   - Socioeconomic status
   - Household composition
   - Minority status/language
   - Housing/transportation

2. **Hurricane Risk** - FEMA National Risk Index
   - Historical hurricane frequency
   - Average intensity
   - Expected Annual Loss (EAL)

3. **Economic Vulnerability**
   - County GDP per capita
   - Property values
   - Population density

### Risk Categories

| Score | Category | Color |
|-------|-----------|-------|
| 80-100% | Critical | 🔴 #8B0000 |
| 60-80% | High | 🟠 #DC143C |
| 40-60% | Moderate | 🟡 #FF8C00 |
| 20-40% | Low | 🟢 #FFD700 |
| 0-20% | Very Low | ⚪ #FFFFE0 |

---

## 📡 Data Sources

### Historical
- **NOAA IBTrACS**: Hurricane tracks (1851-2023)
- **BEA**: County GDP data
- **CDC SVI**: Social Vulnerability Index
- **FEMA NRI**: National Risk Index
- **Census**: Florida county boundaries

### Real-time
- **NOAA NHC**: Current Storms API
- **NASA**: Satellite imagery (Landsat, MODIS)

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# View logs
docker logs <backend-container-id>

# Check health
curl http://localhost:8000/health
```

### Frontend returns 503

```bash
# Verify container is running
docker ps | grep frontend

# View logs
docker logs <frontend-container-id>

# Should show: "ready - started server on 0.0.0.0:3000"
```

### CORS errors

Verify that `ALLOWED_ORIGINS` in backend includes frontend domain:
```bash
docker exec <backend-container-id> env | grep ALLOWED_ORIGINS
```

### Data not loading

```bash
# Verify processed files exist
docker exec <backend-container-id> ls -la /app/data/processed/

# If empty, run generation scripts
docker exec <backend-container-id> python scripts/download_noaa_hurricanes.py
```

---

## 🏆 Credits

**Team**: HortaSat
**Event**: NASA Space Apps Challenge 2025
**Data Sources**: NOAA, NASA, CDC, BEA, FEMA

---

## 📄 License

MIT License - See LICENSE file for details

---

**Made with 🌊 for Florida hurricane resilience**
