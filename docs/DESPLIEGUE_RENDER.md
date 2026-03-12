# Guía de Despliegue en Render - API Refacciones Grupo Picacho

## 📋 Requisitos Previos

1. Cuenta en [Render.com](https://render.com) (gratuita)
2. Cuenta en GitHub/GitLab/Bitbucket
3. Repositorio Git con el código del proyecto

## 🚀 Pasos para Desplegar

### 1. Preparar el Repositorio

Asegúrate de que tu repositorio contenga:
- ✅ `requirements.txt` - Dependencias de Python
- ✅ `app/main.py` - Aplicación FastAPI
- ✅ `data/*.xlsx` - Archivos Excel con datos
- ✅ `render.yaml` - Configuración de Render (opcional pero recomendado)

### 2. Subir el Código a GitHub

```bash
# Inicializar repositorio Git
git init

# Agregar archivos
git add .

# Hacer commit
git commit -m "Initial commit - API Refacciones Grupo Picacho"

# Conectar con GitHub (reemplaza con tu URL)
git remote add origin https://github.com/tu-usuario/api-refacciones-picacho.git

# Subir código
git push -u origin main
```

### 3. Crear Web Service en Render

1. **Ir a Render Dashboard**
   - Visita https://dashboard.render.com
   - Haz clic en "New +" → "Web Service"

2. **Conectar Repositorio**
   - Selecciona "Connect a repository"
   - Autoriza a Render para acceder a tu GitHub
   - Selecciona el repositorio `api-refacciones-picacho`

3. **Configurar el Servicio**
   
   **Configuración Básica:**
   - **Name:** `api-refacciones-picacho`
   - **Region:** Oregon (US West) o el más cercano
   - **Branch:** `main`
   - **Root Directory:** (dejar vacío)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Seleccionar Plan**
   - Elige el plan **Free** (suficiente para desarrollo/pruebas)
   - Nota: El plan gratuito tiene limitaciones:
     - Se duerme después de 15 minutos de inactividad
     - 750 horas/mes de uso
     - Reinicio automático cada mes

5. **Variables de Entorno (Opcional)**
   - No son necesarias para esta configuración básica
   - Si necesitas agregar alguna, hazlo en la sección "Environment"

6. **Desplegar**
   - Haz clic en "Create Web Service"
   - Render comenzará a construir y desplegar tu aplicación
   - El proceso toma aproximadamente 2-5 minutos

### 4. Verificar el Despliegue

Una vez completado el despliegue:

1. **URL del Servicio**
   - Render te proporcionará una URL como: `https://api-refacciones-picacho.onrender.com`

2. **Probar la API**
   ```bash
   # Verificar que está funcionando
   curl https://api-refacciones-picacho.onrender.com/health
   
   # Ver documentación interactiva
   # Abre en navegador: https://api-refacciones-picacho.onrender.com/docs
   ```

3. **Endpoints Disponibles**
   - Documentación Swagger: `/docs`
   - Documentación ReDoc: `/redoc`
   - OpenAPI JSON: `/openapi.json`

## 📊 Estructura de la API Desplegada

### Endpoints Principales

#### General
- `GET /` - Información del API
- `GET /health` - Estado del servicio

#### Inventario
- `GET /inventario/consultar` - Consultar inventario
- `GET /inventario/disponibilidad/{numero_parte}` - Verificar disponibilidad
- `GET /inventario/bajo-stock` - Refacciones con stock bajo
- `POST /inventario/entrada` - Registrar entrada de refacciones

#### Pedidos
- `GET /pedidos/sugerido` - Generar pedido sugerido
- `POST /pedidos/automatico` - Generar pedido automático
- `GET /pedidos/listar` - Listar pedidos
- `GET /pedidos/{numero_pedido}` - Consultar pedido específico
- `PUT /pedidos/{numero_pedido}/estatus` - Actualizar estatus

#### Taller
- `POST /taller/solicitar` - Solicitar refacción para taller

#### Consultas Rápidas
- `GET /consultas/rapidas` - Consultas rápidas de servicio

#### Reportes
- `GET /reportes/resumen` - Reporte resumen del sistema

## 🔄 Actualizaciones Automáticas

Render se actualiza automáticamente cuando haces push a tu repositorio:

```bash
# Hacer cambios en el código
git add .
git commit -m "Actualización de funcionalidad"
git push origin main

# Render detectará el cambio y redesplegará automáticamente
```

## ⚙️ Configuración Avanzada

### Usar render.yaml (Recomendado)

El archivo `render.yaml` en la raíz del proyecto permite configuración como código:

```yaml
services:
  - type: web
    name: api-refacciones-picacho
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

### Monitoreo y Logs

1. **Ver Logs en Tiempo Real**
   - En el dashboard de Render, ve a tu servicio
   - Haz clic en la pestaña "Logs"
   - Verás los logs de la aplicación en tiempo real

2. **Métricas**
   - Pestaña "Metrics" muestra:
     - CPU usage
     - Memory usage
     - Request count
     - Response times

### Dominios Personalizados

Para usar un dominio propio:

1. Ve a la pestaña "Settings" de tu servicio
2. Scroll hasta "Custom Domains"
3. Haz clic en "Add Custom Domain"
4. Sigue las instrucciones para configurar DNS

## 🔒 Seguridad

### Recomendaciones:

1. **Variables de Entorno**
   - Nunca subas credenciales al repositorio
   - Usa variables de entorno en Render para datos sensibles

2. **HTTPS**
   - Render proporciona HTTPS automáticamente
   - Todos los endpoints están protegidos con SSL

3. **Rate Limiting**
   - Considera implementar rate limiting para producción
   - Usa librerías como `slowapi`

## 🐛 Solución de Problemas

### El servicio no inicia

1. **Revisar logs:**
   ```
   Dashboard → Tu Servicio → Logs
   ```

2. **Verificar dependencias:**
   - Asegúrate de que `requirements.txt` esté completo
   - Verifica versiones compatibles

3. **Comando de inicio:**
   - Debe ser: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Nota el uso de `$PORT` (variable de Render)

### Archivos Excel no se encuentran

- Los archivos en `data/` deben estar en el repositorio
- Verifica que no estén en `.gitignore`
- Render copia todo el repositorio al desplegar

### El servicio se duerme (Plan Free)

- Es normal en el plan gratuito
- Primera petición después de 15 min puede tardar 30-60 segundos
- Considera upgrade a plan pagado para producción

## 💰 Costos

### Plan Free (Actual)
- ✅ 750 horas/mes
- ✅ SSL automático
- ✅ Despliegues ilimitados
- ⚠️ Se duerme después de 15 min de inactividad
- ⚠️ 512 MB RAM

### Plan Starter ($7/mes)
- ✅ Siempre activo
- ✅ 512 MB RAM
- ✅ Sin límite de horas

### Plan Standard ($25/mes)
- ✅ 2 GB RAM
- ✅ Mejor rendimiento
- ✅ Soporte prioritario

## 📞 Soporte

- **Documentación Render:** https://render.com/docs
- **Community Forum:** https://community.render.com
- **Status Page:** https://status.render.com

## ✅ Checklist de Despliegue

- [ ] Código subido a GitHub
- [ ] Archivos Excel en carpeta `data/`
- [ ] `requirements.txt` actualizado
- [ ] Servicio creado en Render
- [ ] Build exitoso
- [ ] Endpoint `/health` responde
- [ ] Documentación `/docs` accesible
- [ ] Pruebas de endpoints principales
- [ ] Logs sin errores

## 🎯 Próximos Pasos

1. **Configurar CI/CD**
   - GitHub Actions para tests automáticos
   - Deploy automático en merge a main

2. **Agregar Autenticación**
   - JWT tokens
   - API Keys

3. **Base de Datos**
   - Migrar de Excel a PostgreSQL
   - Render ofrece PostgreSQL gratuito

4. **Monitoreo**
   - Integrar con Sentry para error tracking
   - Configurar alertas

---

**¡Tu API está lista para usar!** 🚀

Accede a la documentación interactiva en:
`https://tu-servicio.onrender.com/docs`