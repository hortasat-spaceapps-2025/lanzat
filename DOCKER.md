# Docker Deployment Guide

## Requisitos

- Docker Desktop instalado
- Docker Compose v2+

## Quick Start

### 1. Desarrollo Local (con mapeo de puertos)

```bash
# Usar docker-compose.local.yml para desarrollo
docker-compose -f docker-compose.local.yml up --build

# O en segundo plano
docker-compose -f docker-compose.local.yml up -d
```

Esto iniciará:
- **Backend** (FastAPI): http://localhost:8000
- **Frontend** (Next.js): http://localhost:3000

### 2. Producción / Coolify (solo EXPOSE)

```bash
# Usar docker-compose.yml para Coolify
docker-compose up --build

# O en segundo plano
docker-compose up -d
```

Los puertos se exponen pero NO se mapean directamente. Coolify usa su proxy reverso para el routing.

### 3. Ver logs

```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo frontend
docker-compose logs -f frontend
```

### 4. Detener servicios

```bash
docker-compose down
```

### 5. Detener y eliminar volúmenes

```bash
docker-compose down -v
```

## Comandos Útiles

### Reconstruir imágenes

```bash
docker-compose build --no-cache
```

### Ejecutar comandos dentro del contenedor

```bash
# Backend - Actualizar datos de huracanes en tiempo real
docker-compose exec backend python scripts/fetch_active_hurricanes.py

# Backend - Shell interactivo
docker-compose exec backend bash

# Frontend - Shell interactivo
docker-compose exec frontend sh
```

### Ver estado de servicios

```bash
docker-compose ps
```

### Reiniciar un servicio específico

```bash
docker-compose restart backend
# o
docker-compose restart frontend
```

## Estructura de Servicios

### Backend (FastAPI + GeoPandas)
- Puerto: 8000
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs
- Volúmenes: `./lanzat-backend/data` montado en `/app/data`

### Frontend (Next.js)
- Puerto: 3000
- URL: http://localhost:3000
- Depende de: backend (espera health check)

## Variables de Entorno

Copia `.env.example` a `.env` y personaliza:

```bash
cp .env.example .env
```

## Actualizar Datos en Producción

```bash
# Actualizar datos de huracanes activos
docker-compose exec backend python scripts/fetch_active_hurricanes.py

# Recalcular riesgos con NOAA
docker-compose exec backend python scripts/calculate_real_hurricane_risk.py

# Enriquecer con datos Statista
docker-compose exec backend python scripts/enrich_with_statista.py
```

## Troubleshooting

### Backend no inicia
```bash
# Ver logs detallados
docker-compose logs backend

# Verificar health check
docker-compose ps
```

### Frontend no conecta con backend
- Verificar NEXT_PUBLIC_API_URL en docker-compose.yml
- Verificar ALLOWED_ORIGINS en backend
- Verificar que backend esté healthy: `docker-compose ps`

### Rebuild completo
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Limpieza completa de Docker
```bash
# Detener todo
docker-compose down -v

# Eliminar imágenes
docker rmi lanzat-backend lanzat-frontend

# Limpiar sistema Docker
docker system prune -a
```

## Production Notes

Para producción, considera:

1. Usar variables de entorno seguras
2. Configurar HTTPS con nginx reverse proxy
3. Usar volúmenes Docker para persistencia de datos
4. Implementar logging centralizado
5. Configurar auto-restart policies
6. Monitorear health checks

## Desarrollo vs Producción

### Desarrollo Local (sin Docker - hot-reload)
```bash
cd lanzat-backend && source venv/bin/activate && uvicorn app.main:app --reload
cd lanzat-frontend && npm run dev
```

### Desarrollo Local (con Docker)
```bash
# Usa docker-compose.local.yml con mapeo de puertos
docker-compose -f docker-compose.local.yml up -d

# Acceder en:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Producción en Coolify
```bash
# Usa docker-compose.yml (EXPOSE sin mapeo de puertos)
docker-compose up -d

# Coolify maneja el proxy reverso
# URLs de producción:
# Frontend: https://lanzat.ignacio.tech
# Backend: https://lanzat.api.ignacio.tech
# API Docs: https://lanzat.api.ignacio.tech/docs
```

## Archivos de Configuración

- **docker-compose.yml** - Para Coolify (usa EXPOSE, sin mapeo de puertos)
- **docker-compose.local.yml** - Para desarrollo local (mapea puertos 3000 y 8000)
- **docker-compose.prod.yml** - Producción con URLs específicas
