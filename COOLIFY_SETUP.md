# Lanzat - Coolify Deployment Setup

## 🚀 Configuración en Coolify

### Paso 1: Crear Nuevo Recurso

1. En Coolify, ir a tu proyecto
2. Click en **"+ New Resource"**
3. Seleccionar **"Docker Compose"**
4. Tipo de Source: **Git Repository**

---

### Paso 2: Configuración del Repositorio

- **Repository URL**: `https://github.com/hortasat-spaceapps-2025/lanzat`
- **Branch**: `main`
- **Compose File Location**: `docker-compose.yml`
- **Build Pack**: Docker Compose

---

### Paso 3: Configuración de Dominios

En Coolify, configura los dominios para cada servicio:

#### Backend Service
- **Service Name**: `backend`
- **Domain**: `lanzat.api.ignacio.tech`
- **Port**: `8000`

#### Frontend Service
- **Service Name**: `frontend`
- **Domain**: `lanzat.ignacio.tech`
- **Port**: `3000`

---

### Paso 4: Variables de Entorno

Coolify inyectará estas variables automáticamente, pero puedes verificar/agregar:

#### Variables Globales del Proyecto

```bash
ALLOWED_ORIGINS=https://lanzat.ignacio.tech
NEXT_PUBLIC_API_URL=https://lanzat.api.ignacio.tech
```

Coolify también agrega automáticamente variables de build como:
- `SOURCE_COMMIT`
- `COOLIFY_FQDN`
- etc.

---

### Paso 5: Deploy

1. Click en **"Deploy"**
2. Coolify hará:
   - ✅ Clone del repositorio
   - ✅ Build de las imágenes Docker
   - ✅ Crear contenedores
   - ✅ Configurar proxy reverso (Traefik)
   - ✅ Generar certificados SSL

---

## 🔍 Verificación Post-Deploy

### 1. Verificar Health Checks

En Coolify, verifica que los health checks estén pasando:

- **Backend**: `GET http://backend:8000/health`
  - Debe retornar: `{"status": "healthy", ...}`

- **Frontend**: Debe responder en el puerto 3000

### 2. Generar Datos Iniciales

Una vez desplegado, ejecutar estos comandos en el contenedor backend:

```bash
# Encontrar el ID del contenedor backend
docker ps | grep backend

# Ejecutar scripts de generación de datos
docker exec -it <backend-container-id> python scripts/download_noaa_hurricanes.py
docker exec -it <backend-container-id> python scripts/calculate_real_hurricane_risk.py
docker exec -it <backend-container-id> python scripts/enrich_with_statista.py
docker exec -it <backend-container-id> python scripts/fetch_active_hurricanes.py
```

O desde Coolify UI:
1. Ir a "Containers"
2. Seleccionar el contenedor backend
3. Abrir "Execute Command"
4. Ejecutar cada script

### 3. Configurar Cron Job (Opcional)

Para actualizar datos de huracanes en tiempo real cada 30 minutos:

1. En Coolify, ir a **Scheduled Tasks**
2. Crear nueva tarea:
   - **Container**: backend
   - **Command**: `python scripts/fetch_active_hurricanes.py`
   - **Schedule**: `*/30 * * * *` (cada 30 min)

---

## 🌐 URLs Finales

Una vez desplegado, acceder a:

- **Frontend**: https://lanzat.ignacio.tech
- **Backend API**: https://lanzat.api.ignacio.tech
- **API Docs**: https://lanzat.api.ignacio.tech/docs
- **Health Check**: https://lanzat.api.ignacio.tech/health

---

## 🐛 Troubleshooting

### "no available server"

Este error puede ocurrir si:

1. **Health checks fallan** - Verifica logs del contenedor
   ```bash
   docker logs <container-id>
   ```

2. **Puerto incorrecto** - Asegúrate que Coolify detecta:
   - Backend: puerto 8000
   - Frontend: puerto 3000

3. **Dominios no configurados** - Verifica en Coolify UI que cada servicio tiene su dominio asignado

4. **Build falla** - Revisa logs de build en Coolify

### Backend no carga datos

```bash
# Verificar que el volumen tiene datos
docker exec <backend-container-id> ls -la /app/data/processed/

# Si está vacío, ejecutar scripts de generación
docker exec <backend-container-id> python scripts/download_noaa_hurricanes.py
```

### Frontend muestra 404

Posibles causas:
- Build de Next.js falló
- Carpeta `public` no se copió correctamente
- Variable `NEXT_PUBLIC_API_URL` incorrecta

Solución:
```bash
# Verificar variables de entorno del contenedor
docker exec <frontend-container-id> env | grep NEXT_PUBLIC

# Reconstruir si es necesario
```

### CORS errors en el navegador

```bash
# Verificar ALLOWED_ORIGINS del backend
docker exec <backend-container-id> env | grep ALLOWED_ORIGINS

# Debe incluir: https://lanzat.ignacio.tech
```

---

## 🔄 Actualizaciones

### Actualizar código

```bash
git push origin main
```

Coolify detectará el push y re-desplegará automáticamente (si tienes auto-deploy activado).

O manualmente:
1. En Coolify UI
2. Click en "Redeploy"

### Actualizar solo datos

```bash
docker exec <backend-container-id> python scripts/fetch_active_hurricanes.py
```

---

## 📊 Monitoreo

Coolify provee:
- **Logs en tiempo real** por contenedor
- **Métricas de CPU/RAM**
- **Estado de health checks**
- **Historial de deploys**

Acceder a estas métricas en el dashboard de tu recurso en Coolify.

---

## 🔐 Seguridad

Coolify maneja automáticamente:
- ✅ Certificados SSL (Let's Encrypt)
- ✅ Renovación automática de certificados
- ✅ Proxy reverso seguro (Traefik)
- ✅ Aislamiento de redes Docker
- ✅ Variables de entorno seguras

---

**¡Deployment completado! 🎉**
