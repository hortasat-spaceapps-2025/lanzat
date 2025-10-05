# Lanzat - Hurricane Economic Vulnerability Platform

![Platform](https://img.shields.io/badge/Platform-Florida%20Counties-blue)
![Data](https://img.shields.io/badge/Data-NOAA%20IBTrACS-green)
![Real--time](https://img.shields.io/badge/Real--time-Hurricane%20Tracking-red)

**Sistema completo para analizar riesgo de huracanes, vulnerabilidad económica e impacto social en 67 condados de Florida usando datos históricos de NOAA (1851-2023) y seguimiento en tiempo real.**

---

## 🌐 Demo

- **Frontend**: https://lanzat.ignacio.tech
- **Backend API**: https://lanzat.api.ignacio.tech
- **API Docs**: https://lanzat.api.ignacio.tech/docs

---

## 🌊 Características

### Análisis Histórico
- **Datos NOAA IBTrACS**: 704 tormentas históricas desde 1851-2023
- **Cálculo de Riesgo**: Basado en frecuencia (50%), intensidad promedio (30%), intensidad máxima (20%)
- **Modelo de Vulnerabilidad**: 25% Riesgo + 20% Social + 20% Económico + 20% Propiedades + 15% Rural

### Capacidades en Tiempo Real
- **Seguimiento de Tormentas Activas**: Integración con API NOAA NHC
- **Evaluación de Amenazas por Condado**: Niveles de amenaza basados en distancia
- **Alertas Críticas**: Análisis combinado de amenaza actual + vulnerabilidad histórica

---

## 🚀 Quick Start

### Desarrollo Local

```bash
# Clonar repositorio
git clone https://github.com/hortasat-spaceapps-2025/lanzat.git
cd lanzat

# Iniciar con Docker (desarrollo local)
docker-compose -f docker-compose.local.yml up -d

# Acceder
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Producción (Coolify)

```bash
# Usar docker-compose.yml (Coolify maneja el proxy)
docker-compose up -d
```

---

## 📊 API Endpoints

### Datos Históricos
- `GET /api/counties` - Todos los condados con scores de vulnerabilidad
- `GET /api/counties/{name}` - Detalles de condado específico
- `GET /api/top-vulnerable?limit=10` - Top condados vulnerables
- `GET /api/stats` - Estadísticas generales
- `GET /api/enhanced/critical-rural` - Zonas rurales críticas
- `GET /api/enhanced/correlations` - Análisis de correlación

### Datos en Tiempo Real
- `GET /api/realtime/active-storms` - Huracanes activos (NOAA NHC)
- `GET /api/realtime/county-threats` - Amenazas por condado
- `GET /api/realtime/critical-threats` - Condados en alerta crítica
- `POST /api/realtime/refresh` - Refrescar datos en tiempo real

### Sistema
- `GET /health` - Health check del servicio
- `GET /` - Información de la API y endpoints disponibles

---

## 🛠️ Tech Stack

**Backend**:
- Python 3.11
- FastAPI (API REST)
- GeoPandas (análisis geoespacial)
- GDAL (procesamiento de datos satelitales)
- Shapely (geometrías)

**Frontend**:
- Next.js 14 (React framework)
- TypeScript
- Leaflet (mapas interactivos)
- Tailwind CSS (estilos)

**Infrastructure**:
- Docker + Docker Compose
- Coolify (deployment)
- Traefik (proxy reverso)

---

## 📁 Estructura del Proyecto

```
lanzat/
├── docker-compose.yml              # Producción (Coolify)
├── docker-compose.local.yml        # Desarrollo local
├── lanzat-backend/
│   ├── Dockerfile
│   ├── app/
│   │   └── main.py                 # FastAPI application
│   ├── scripts/
│   │   ├── download_noaa_hurricanes.py     # Descarga datos históricos
│   │   ├── calculate_real_hurricane_risk.py # Calcula riesgos
│   │   ├── enrich_with_statista.py         # Enriquece con datos económicos
│   │   └── fetch_active_hurricanes.py      # Datos en tiempo real
│   ├── data/
│   │   ├── raw/                    # Datos sin procesar
│   │   └── processed/              # GeoJSON procesados
│   └── requirements.txt
└── lanzat-frontend/
    ├── Dockerfile
    ├── pages/
    │   └── index.tsx               # Página principal
    ├── components/
    │   ├── Map.tsx                 # Mapa interactivo de Florida
    │   └── Dashboard.tsx           # Dashboard con KPIs
    ├── next.config.mjs
    └── package.json
```

---

## 🔧 Configuración

### Variables de Entorno

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

## 🎯 Deployment en Coolify

### Paso 1: Configuración en Coolify UI

1. **Crear nuevo recurso** → Docker Compose
2. **Repository**: `https://github.com/hortasat-spaceapps-2025/lanzat`
3. **Branch**: `main`
4. **Compose File**: `docker-compose.yml`

### Paso 2: Configurar Dominios

**Backend:**
- Service: `backend`
- Domain: `lanzat.api.ignacio.tech`
- Port: `8000`

**Frontend:**
- Service: `frontend`
- Domain: `lanzat.ignacio.tech`
- Port: `3000`

### Paso 3: Variables de Entorno (Coolify)

```bash
ALLOWED_ORIGINS=https://lanzat.ignacio.tech
NEXT_PUBLIC_API_URL=https://lanzat.api.ignacio.tech
```

### Paso 4: Deploy

Click **Deploy** - Coolify construirá y desplegará automáticamente.

### Paso 5: Generar Datos Iniciales

```bash
# Encontrar container ID del backend
docker ps | grep backend

# Ejecutar scripts de generación
docker exec <backend-container-id> python scripts/download_noaa_hurricanes.py
docker exec <backend-container-id> python scripts/calculate_real_hurricane_risk.py
docker exec <backend-container-id> python scripts/enrich_with_statista.py
docker exec <backend-container-id> python scripts/fetch_active_hurricanes.py
```

### Paso 6 (Opcional): Cron Job para Actualizaciones

Configurar en Coolify para actualizar huracanes activos cada 30 minutos:
```bash
*/30 * * * * python scripts/fetch_active_hurricanes.py
```

---

## 🧮 Algoritmo de Vulnerabilidad

### Fórmula del Score

```python
vulnerability_score = (
    svi_score * 0.4 +          # 40% Social Vulnerability Index
    hurricane_score * 0.4 +     # 40% Riesgo de huracanes
    economic_score * 0.2        # 20% Vulnerabilidad económica
)
```

**Componentes:**

1. **Social Vulnerability (SVI)** - CDC Social Vulnerability Index
   - Nivel socioeconómico
   - Composición del hogar
   - Minorías/lenguaje
   - Vivienda/transporte

2. **Hurricane Risk** - FEMA National Risk Index
   - Frecuencia histórica de huracanes
   - Intensidad promedio
   - Expected Annual Loss (EAL)

3. **Economic Vulnerability**
   - GDP per capita del condado
   - Valor de propiedades
   - Densidad poblacional

### Categorías de Riesgo

| Score | Categoría | Color |
|-------|-----------|-------|
| 80-100% | Critical | 🔴 #8B0000 |
| 60-80% | High | 🟠 #DC143C |
| 40-60% | Moderate | 🟡 #FF8C00 |
| 20-40% | Low | 🟢 #FFD700 |
| 0-20% | Very Low | ⚪ #FFFFE0 |

---

## 📡 Fuentes de Datos

### Históricas
- **NOAA IBTrACS**: Hurricane tracks (1851-2023)
- **BEA**: County GDP data
- **CDC SVI**: Social Vulnerability Index
- **FEMA NRI**: National Risk Index
- **Census**: Florida county boundaries

### Tiempo Real
- **NOAA NHC**: Current Storms API
- **NASA**: Satellite imagery (Landsat, MODIS)

---

## 🐛 Troubleshooting

### Backend no inicia

```bash
# Ver logs
docker logs <backend-container-id>

# Verificar health
curl http://localhost:8000/health
```

### Frontend da 503

```bash
# Verificar que el contenedor está corriendo
docker ps | grep frontend

# Ver logs
docker logs <frontend-container-id>

# Debe mostrar: "ready - started server on 0.0.0.0:3000"
```

### CORS errors

Verificar que `ALLOWED_ORIGINS` en backend incluye el dominio del frontend:
```bash
docker exec <backend-container-id> env | grep ALLOWED_ORIGINS
```

### Datos no cargan

```bash
# Verificar que existen los archivos procesados
docker exec <backend-container-id> ls -la /app/data/processed/

# Si están vacíos, ejecutar scripts de generación
docker exec <backend-container-id> python scripts/download_noaa_hurricanes.py
```

---

## 🏆 Créditos

**Team**: HortaSat
**Event**: NASA Space Apps Challenge 2025
**Data Sources**: NOAA, NASA, CDC, BEA, FEMA

---

## 📄 Licencia

MIT License - Ver archivo LICENSE para detalles

---

**Made with 🌊 for Florida hurricane resilience**
