# Frontend 503 - Debugging Guide

## 🔍 Frontend Específico - Causas del 503

El frontend Next.js puede dar 503 por:
1. ✅ Server.js no arranca correctamente
2. ✅ Variables de entorno incorrectas en build time
3. ✅ Coolify no detecta el puerto 3000
4. ✅ Error de runtime en el código React

---

## 🛠️ Cambios Implementados

### 1. Eliminado Health Check del Dockerfile

**Antes:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD node -e "require('http').get('http://localhost:3000'..."
```

**Ahora:**
```dockerfile
# Sin health check - Coolify maneja la detección
CMD ["node", "server.js"]
```

**Razón:** Los health checks en el Dockerfile pueden causar conflictos con el proxy de Coolify.

### 2. Build Args para Variables de Entorno

```dockerfile
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
```

Permite que Coolify inyecte la URL correcta en build time.

---

## 🔧 Verificación en Coolify

### Paso 1: Verificar Build Completó Exitosamente

En Coolify UI:
```
Resources > frontend > Deployments > [último] > Build Logs
```

Buscar:
```
✅ Route (pages)                             Size     First Load JS
✅ ┌ ○ /                                     117 kB          198 kB
✅ Compiled successfully
```

Si hay errores de TypeScript/ESLint, ya están ignorados en next.config.mjs.

### Paso 2: Verificar Container Está Corriendo

```bash
# En Coolify UI: Resources > frontend > Containers
# O via CLI:
docker ps | grep frontend
```

Debe mostrar:
```
STATUS: Up X minutes
```

Si dice "Restarting" o "Exited", hay un problema con el servidor.

### Paso 3: Ver Logs en Tiempo Real

En Coolify UI:
```
Resources > frontend > Containers > frontend > Logs
```

Buscar:
```
✅ "ready - started server on 0.0.0.0:3000"
✅ "compiled successfully"
❌ Error: Cannot find module...
❌ ECONNREFUSED...
```

### Paso 4: Verificar Puerto 3000 Responde

```bash
# Ejecutar dentro del contenedor frontend
docker exec <frontend-container-id> sh -c "wget -qO- http://localhost:3000"

# Debe retornar HTML
<!DOCTYPE html>...
```

Si retorna HTML ✅ → El problema es con Coolify proxy
Si retorna error ❌ → El problema es con Next.js server

---

## 🐛 Errores Comunes

### Error 1: "Error: Cannot find module './server.js'"

**Causa:** Build de Next.js falló, standalone output no existe

**Solución:**
```dockerfile
# Verificar que next.config.mjs tiene:
output: 'standalone'
```

Rebuild:
```bash
# En Coolify: Force Rebuild
```

### Error 2: "ECONNREFUSED backend:8000"

**Causa:** Frontend intenta conectar al backend durante SSR y falla

**Solución:**
Verificar variable de entorno en Coolify:
```bash
NEXT_PUBLIC_API_URL=https://lanzat.api.ignacio.tech
```

**NO usar:**
```bash
❌ http://backend:8000  # Solo funciona dentro de Docker network
❌ http://localhost:8000  # Solo funciona en desarrollo
```

### Error 3: Container Sale con "Exited (1)"

**Causa:** Crash al iniciar server.js

**Logs a buscar:**
```bash
docker logs <frontend-container-id>
```

Posibles causas:
- Archivo server.js no existe (verificar build)
- Permisos incorrectos (debe ser nextjs:nodejs)
- Puerto 3000 ya en uso (poco probable en Coolify)

**Solución:**
```bash
# Verificar que los archivos existen
docker exec <frontend-container-id> ls -la /app/

# Debe mostrar:
# -rw-r--r-- nextjs nodejs server.js
# drwxr-xr-x nextjs nodejs .next
# drwxr-xr-x nextjs nodejs public
```

### Error 4: Build Exitoso pero 503 Persiste

**Causa:** Coolify proxy no detecta el servicio

**Verificación:**
1. En Coolify UI: Resources > frontend > Settings
2. Verificar:
   - **Port**: `3000` ✅
   - **Protocol**: `http` ✅
   - **Domain**: `lanzat.ignacio.tech` ✅

**Solución:**
```bash
# Redeploy el servicio
# En Coolify: Redeploy button
```

---

## 📊 Verificación Exitosa

### Backend Responde (Prerequisito)

```bash
curl https://lanzat.api.ignacio.tech/health

# Debe retornar:
{
  "status": "healthy",
  "app_running": true
}
```

### Frontend Container Healthy

```bash
# Desde dentro del container
docker exec <frontend-container-id> wget -qO- http://localhost:3000

# Debe retornar HTML
```

### Frontend Accesible Públicamente

```bash
curl https://lanzat.ignacio.tech/

# Debe retornar:
<!DOCTYPE html>
<html>
  <head>
    <title>Lanzat - Florida Hurricane Vulnerability Platform</title>
  </head>
  ...
</html>
```

### Frontend Carga en Navegador

1. Abrir: https://lanzat.ignacio.tech
2. Debe mostrar:
   - ✅ Título: "Lanzat - Florida Hurricane Vulnerability Platform"
   - ✅ Mapa de Florida (puede estar vacío si backend no tiene datos)
   - ✅ Dashboard con KPIs

---

## 🔄 Solución Completa: Rebuild desde Cero

Si todo lo anterior falla:

### 1. En Local: Verificar Build Funciona

```bash
cd lanzat-frontend

# Build local
docker build -t lanzat-frontend-test .

# Run local
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://lanzat.api.ignacio.tech \
  lanzat-frontend-test

# Abrir http://localhost:3000
```

Si funciona local pero no en Coolify → Problema con Coolify
Si NO funciona local → Problema con el código

### 2. En Coolify: Force Rebuild

```bash
# Coolify UI:
Resources > frontend > Advanced > Force Rebuild

# Esto:
- Elimina caché de build
- Reconstruye desde cero
- Recrea containers
```

### 3. Verificar Variables de Entorno

En Coolify UI: Resources > frontend > Environment Variables

Debe tener:
```bash
NEXT_PUBLIC_API_URL=https://lanzat.api.ignacio.tech
NODE_ENV=production
```

**IMPORTANTE:** Coolify inyecta build args automáticamente, NO necesitas definir `NEXT_PUBLIC_API_URL` en variables de entorno si está en docker-compose.yml con valor por defecto.

### 4. Verificar docker-compose.yml

```yaml
frontend:
  expose: ["3000"]  # ✅ Correcto
  environment:
    - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-https://lanzat.api.ignacio.tech}
```

**NO:**
```yaml
❌ ports: ["3000:3000"]  # Causa conflictos con Coolify
❌ healthcheck: ...  # Coolify lo maneja
```

---

## 🎯 Comandos de Diagnóstico Rápido

```bash
# 1. Ver si container está corriendo
docker ps | grep frontend

# 2. Ver logs
docker logs -f <frontend-container-id>

# 3. Probar desde dentro
docker exec <frontend-container-id> wget -qO- http://localhost:3000

# 4. Verificar archivos del build
docker exec <frontend-container-id> ls -la /app/

# 5. Verificar proceso Node
docker exec <frontend-container-id> ps aux

# 6. Verificar puerto escuchando
docker exec <frontend-container-id> netstat -tlnp 2>/dev/null || \
docker exec <frontend-container-id> ss -tlnp
```

---

## 📞 Si Nada Funciona

Compartir estos logs:

```bash
# 1. Build logs completos
# Coolify UI: Deployments > Build Logs

# 2. Runtime logs
docker logs <frontend-container-id> 2>&1

# 3. Container info
docker inspect <frontend-container-id>

# 4. Network info
docker exec <frontend-container-id> env
```

---

**El frontend DEBE arrancar correctamente después de estos cambios** 🚀
