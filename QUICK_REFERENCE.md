# Lanzat - Quick Reference Card

## 🚀 Setup Commands (Copy-Paste Ready)

### Backend Setup
```bash
cd /Users/nade/Projects/hackathon/lanzat-backend
brew install gdal
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/download_data.py
python scripts/process_data.py
python app/main.py
```

### Frontend Setup
```bash
cd /Users/nade/Projects/hackathon/lanzat-frontend
npm install --legacy-peer-deps
cp .env.example .env.local
npm run dev
```

---

## 📍 URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Map interface |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Health Check | http://localhost:8000/health | Status |

---

## 🔧 Common Commands

### Backend
```bash
# Activate venv
source venv/bin/activate

# Run API
python app/main.py

# Reprocess data
python scripts/process_data.py

# Check health
curl http://localhost:8000/health
```

### Frontend
```bash
# Dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Deployment
```bash
# Backend (Railway)
railway login
railway up

# Frontend (Vercel)
vercel deploy --prod
```

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/counties` | GET | All 67 counties (GeoJSON) |
| `/api/counties/{name}` | GET | Specific county details |
| `/api/top-vulnerable?limit=10` | GET | Top N vulnerable counties |
| `/api/stats` | GET | Summary statistics |
| `/health` | GET | Health check |

---

## 🎨 Vulnerability Categories

| Score | Category | Color | Hex |
|-------|----------|-------|-----|
| 80-100% | Critical | 🔴 Dark Red | #8B0000 |
| 60-80% | High | 🟠 Red | #DC143C |
| 40-60% | Moderate | 🟡 Orange | #FF8C00 |
| 20-40% | Low | 🟢 Yellow | #FFD700 |
| 0-20% | Very Low | ⚪ Light Yellow | #FFFFE0 |

---

## 🧮 Vulnerability Formula

```
Score = (0.40 × Hurricane Risk) +
        (0.30 × Social Vulnerability) +
        (0.30 × Economic Vulnerability)
```

---

## 📁 Key Files

### Backend
- `app/main.py` - API application
- `scripts/download_data.py` - Data downloader
- `scripts/process_data.py` - Score calculator
- `data/processed/counties.geojson` - Output data

### Frontend
- `pages/index.tsx` - Main page
- `components/Map.tsx` - Leaflet map
- `components/Dashboard.tsx` - Charts & stats
- `.env.local` - Environment config

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| GDAL won't install | `brew install gdal` |
| Map not rendering | Check `NEXT_PUBLIC_API_URL` in `.env.local` |
| CORS errors | Add frontend URL to `allow_origins` in `app/main.py` |
| Data not found | Run `python scripts/process_data.py` |
| Port already in use | Kill process: `lsof -ti:8000 \| xargs kill -9` |

---

## 🎤 3-Minute Pitch Outline

**[0:00-0:30]** Hook → Problem ($12.6B Hurricane Ian losses)
**[0:30-1:00]** Gap → Nobody combines economic + vulnerability data
**[1:00-2:00]** Demo → Show map, click county, top 10, chart
**[2:00-2:45]** Impact → $2.1B budget allocation, protect communities
**[2:45-3:00]** CTA → Live at [URL], ready for pilots

---

## ✅ Pre-Demo Checklist

**1 Hour Before:**
- [ ] Backend deployed and tested
- [ ] Frontend deployed and tested
- [ ] Demo loaded in browser (don't close!)
- [ ] Backup video ready
- [ ] Pitch script memorized
- [ ] Laptop charged
- [ ] Internet connection tested

---

## 📞 Quick Help

**Full Setup:** See `SETUP.md`
**Project Overview:** See `README.md`
**Timeline:** See `HACKATHON_CHECKLIST.md`
**Data Sources:** See `RESOURCE_GUIDE.md`
**Architecture:** See `PROJECT_SUMMARY.md`

---

## 🎯 Tech Stack Summary

**Backend:** Python 3.11 + FastAPI + GeoPandas
**Frontend:** Next.js 14 + TypeScript + Leaflet + Recharts
**Deploy:** Railway (backend) + Vercel (frontend)
**Data:** NOAA + Census + BEA + CDC + FEMA

---

**Pro Tip:** Keep this file open during your hackathon for quick reference! 🚀
