# Lanzat - Production Deployment Guide

## 🌐 Production URLs

- **Frontend**: https://lanzat.ignacio.tech
- **Backend API**: https://lanzat.api.ignacio.tech
- **API Docs**: https://lanzat.api.ignacio.tech/docs

---

## 🚀 Coolify Deployment

### Backend Configuration

**Service**: lanzat-backend

**Environment Variables:**
```bash
ALLOWED_ORIGINS=https://lanzat.ignacio.tech
PYTHONUNBUFFERED=1
```

**Port**: 8000

**Health Check**:
```bash
curl -f http://localhost:8000/health
```

**Domain**: lanzat.api.ignacio.tech

---

### Frontend Configuration

**Service**: lanzat-frontend

**Environment Variables:**
```bash
NEXT_PUBLIC_API_URL=https://lanzat.api.ignacio.tech
NODE_ENV=production
```

**Port**: 3000

**Domain**: lanzat.ignacio.tech

---

## 🔧 Post-Deployment Setup

### 1. Generate Initial Data

SSH into the backend container and run:

```bash
# Download historical hurricane data
docker exec lanzat-backend python scripts/download_noaa_hurricanes.py

# Calculate hurricane risk metrics
docker exec lanzat-backend python scripts/calculate_real_hurricane_risk.py

# Enrich with economic data
docker exec lanzat-backend python scripts/enrich_with_statista.py

# Fetch active hurricanes (real-time)
docker exec lanzat-backend python scripts/fetch_active_hurricanes.py
```

### 2. Setup Cron Job for Real-time Updates

Add to Coolify cron or server crontab:

```bash
# Update active hurricanes every 30 minutes
*/30 * * * * docker exec lanzat-backend python scripts/fetch_active_hurricanes.py
```

### 3. Verify Deployment

```bash
# Test backend health
curl https://lanzat.api.ignacio.tech/health

# Test API endpoints
curl https://lanzat.api.ignacio.tech/api/counties
curl https://lanzat.api.ignacio.tech/api/realtime/active-storms

# Test frontend
curl https://lanzat.ignacio.tech
```

---

## 📊 Monitoring

### Health Checks

**Backend**:
```bash
curl https://lanzat.api.ignacio.tech/health
```

Expected response:
```json
{
  "status": "healthy",
  "data_loaded": true,
  "enhanced_data_loaded": true,
  "counties_file": "/app/data/processed/counties.geojson",
  "summary_file": "/app/data/processed/summary_stats.json",
  "enhanced_counties_file": "/app/data/processed/counties_enhanced.geojson"
}
```

**Frontend**: Should return HTML with title "Lanzat - Florida Hurricane Vulnerability Platform"

### Log Monitoring

```bash
# Backend logs
docker logs -f lanzat-backend

# Frontend logs
docker logs -f lanzat-frontend
```

---

## 🔄 Updates and Redeployment

### Update Code

```bash
# Coolify auto-deploys on git push to main
git push origin main
```

### Manual Rebuild

In Coolify dashboard:
1. Go to your Lanzat project
2. Click "Redeploy"

Or via command line:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### Update Real-time Data Only

```bash
docker exec lanzat-backend python scripts/fetch_active_hurricanes.py
```

---

## 🐛 Troubleshooting

### Frontend Can't Connect to Backend

**Issue**: CORS errors in browser console

**Solution**: Verify backend ALLOWED_ORIGINS includes frontend domain
```bash
docker exec lanzat-backend env | grep ALLOWED_ORIGINS
# Should show: ALLOWED_ORIGINS=https://lanzat.ignacio.tech
```

### Backend Not Loading Data

**Issue**: Health check shows `data_loaded: false`

**Solution**: Run data generation scripts
```bash
docker exec lanzat-backend python scripts/download_noaa_hurricanes.py
docker exec lanzat-backend python scripts/calculate_real_hurricane_risk.py
```

### SSL/HTTPS Issues

**Issue**: Mixed content warnings

**Solution**:
1. Verify frontend uses HTTPS API URL
2. Check Coolify SSL certificate is active
3. Ensure both domains have valid SSL certs

### Container Won't Start

**Issue**: Backend container exits immediately

**Solution**: Check logs for GDAL or Python errors
```bash
docker logs lanzat-backend
```

Common fix: Rebuild with no cache
```bash
docker-compose -f docker-compose.prod.yml build --no-cache backend
docker-compose -f docker-compose.prod.yml up -d backend
```

---

## 📈 Performance Optimization

### Enable Caching

Backend already includes in-memory caching for:
- County GeoJSON data
- Vulnerability calculations
- Real-time storm data (5min cache)

### CDN for Frontend

Serve static assets through Cloudflare or similar CDN.

### Database Connection Pooling

If using PostgreSQL in future, configure connection pooling in backend.

---

## 🔐 Security Checklist

- ✅ HTTPS enabled for both domains
- ✅ CORS restricted to frontend domain only
- ✅ Environment variables not committed to git
- ✅ No API keys in code
- ✅ Health check doesn't expose sensitive data
- ✅ Docker containers run as non-root users

---

## 📞 Support

- **Repository**: https://github.com/hortasat-spaceapps-2025/lanzat
- **Issues**: https://github.com/hortasat-spaceapps-2025/lanzat/issues

---

**Deployed with 🌊 on Coolify**
