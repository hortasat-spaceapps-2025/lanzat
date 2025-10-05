# Lanzat - Hurricane Economic Vulnerability Platform

![Platform](https://img.shields.io/badge/Platform-Florida%20Counties-blue)
![Data](https://img.shields.io/badge/Data-NOAA%20IBTrACS-green)
![Real--time](https://img.shields.io/badge/Real--time-Hurricane%20Tracking-red)

**Hurricane Economic Vulnerability Platform for Florida** - Sistema completo para analizar riesgo de huracanes, vulnerabilidad económica e impacto social en 67 condados de Florida usando datos históricos de NOAA (1851-2023) y seguimiento en tiempo real.

## 🌊 Características

### Análisis Histórico
- **Datos NOAA IBTrACS**: 704 tormentas históricas desde 1851-2023
- **Cálculo de Riesgo**: Basado en frecuencia (50%), intensidad promedio (30%), intensidad máxima (20%)
- **Modelo de Vulnerabilidad Mejorado**: 25% Riesgo + 20% Social + 20% Económico + 20% Propiedades + 15% Rural

### Capacidades en Tiempo Real
- **Seguimiento de Tormentas Activas**: Integración con API NOAA NHC
- **Evaluación de Amenazas por Condado**: Niveles de amenaza basados en distancia
- **Alertas Críticas**: Análisis combinado de amenaza actual + vulnerabilidad histórica

## 🚀 Quick Start con Docker

### Desarrollo Local

\`\`\`bash
# Clonar repositorio
git clone https://github.com/hortasat-spaceapps-2025/lanzat.git
cd lanzat

# Iniciar servicios (con mapeo de puertos)
docker-compose -f docker-compose.local.yml up -d

# Acceder
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
\`\`\`

### Producción (Coolify)

\`\`\`bash
# Usar docker-compose.yml (sin mapeo de puertos, usa EXPOSE)
docker-compose up -d

# Coolify manejará el proxy reverso automáticamente
\`\`\`

## 🌐 Demo en Vivo

- **Frontend**: https://lanzat.ignacio.tech
- **Backend API**: https://lanzat.api.ignacio.tech
- **API Docs**: https://lanzat.api.ignacio.tech/docs

## 🎯 Deployment en Coolify

### Paso 1: Crear Proyecto
1. Ir a tu instancia de Coolify
2. Crear nuevo proyecto: **Lanzat**
3. Agregar recurso → **Docker Compose**

### Paso 2: Configurar Repositorio Git
- **Repository**: \`https://github.com/hortasat-spaceapps-2025/lanzat\`
- **Branch**: \`main\`
- **Docker Compose Path**: \`docker-compose.yml\`

### Paso 3: Variables de Entorno

**Backend:**
\`\`\`bash
ALLOWED_ORIGINS=https://lanzat.ignacio.tech
PYTHONUNBUFFERED=1
\`\`\`

**Frontend:**
\`\`\`bash
NEXT_PUBLIC_API_URL=https://lanzat.api.ignacio.tech
NODE_ENV=production
\`\`\`

### Paso 4: Deploy
Click **Deploy** - Coolify construirá y desplegará automáticamente ambos servicios.

### Paso 5: Generar Datos Iniciales
\`\`\`bash
# En el contenedor backend
docker exec lanzat-backend python scripts/download_noaa_hurricanes.py
docker exec lanzat-backend python scripts/calculate_real_hurricane_risk.py
docker exec lanzat-backend python scripts/enrich_with_statista.py
docker exec lanzat-backend python scripts/fetch_active_hurricanes.py
\`\`\`

## 📊 API Endpoints

### Datos Históricos
- \`GET /api/counties\` - Todos los condados
- \`GET /api/top-vulnerable\` - Top condados vulnerables
- \`GET /api/enhanced/critical-rural\` - Zonas rurales críticas
- \`GET /api/enhanced/correlations\` - Análisis de correlación

### Datos en Tiempo Real
- \`GET /api/realtime/active-storms\` - Huracanes activos (NOAA NHC)
- \`GET /api/realtime/county-threats\` - Amenazas por condado
- \`GET /api/realtime/critical-threats\` - Condados en alerta crítica
- \`POST /api/realtime/refresh\` - Refrescar datos

## 🛠️ Tech Stack

**Backend**: FastAPI + GeoPandas + GDAL + Shapely  
**Frontend**: Next.js 14 + TypeScript + Leaflet + Tailwind CSS  
**Infrastructure**: Docker + Docker Compose + Coolify

## 📁 Estructura del Proyecto

\`\`\`
lanzat/
├── docker-compose.yml
├── lanzat-backend/
│   ├── Dockerfile
│   ├── app/main.py
│   ├── scripts/
│   └── data/
└── lanzat-frontend/
    ├── Dockerfile
    ├── pages/
    ├── components/
    └── next.config.mjs
\`\`\`

## 🏆 Credits

**Team**: HortaSat  
**Event**: NASA Space Apps Challenge 2025  
**Data**: NOAA, NASA, CDC, BEA, Statista

---

**Made with 🌊 for Florida hurricane resilience**
