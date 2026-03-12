# API Refacciones y Postventa - Grupo Picacho

Sistema automatizado para la gestión de refacciones, inventario y pedidos del área de postventa.

## 🎯 Características

- ✅ **Consulta de Inventario** - Búsqueda por número de parte, modelo o descripción
- ✅ **Generación de Pedidos Sugeridos** - Análisis automático basado en ventas e inventario
- ✅ **Pedidos Automáticos** - Generación diaria para refacciones con stock bajo
- ✅ **Registro de Entradas** - Control de recepción de refacciones
- ✅ **Surtido a Taller** - Gestión de solicitudes del área de servicio
- ✅ **Control de Pedidos** - Seguimiento de estatus y consultas
- ✅ **Consultas Rápidas** - Comunicación ágil entre servicio y refacciones
- ✅ **Reportes** - Resumen del sistema en tiempo real

## 🚀 Inicio Rápido

### Instalación Local

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/api-refacciones-picacho.git
cd api-refacciones-picacho
```

2. **Crear entorno virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Generar datos sintéticos** (primera vez)
```bash
cd app
python crear_datos_sinteticos.py
cd ..
```

5. **Ejecutar la aplicación**
```bash
uvicorn app.main:app --reload
```

6. **Acceder a la documentación**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## 📁 Estructura del Proyecto

```
api-refacciones-picacho/
├── app/
│   ├── main.py                    # Aplicación FastAPI principal
│   └── crear_datos_sinteticos.py  # Script para generar datos de prueba
├── data/
│   ├── refacciones.xlsx           # Inventario de refacciones
│   ├── pedidos.xlsx               # Registro de pedidos
│   ├── ventas.xlsx                # Historial de ventas
│   └── surtido_taller.xlsx        # Surtidos a taller
├── docs/
│   └── DESPLIEGUE_RENDER.md       # Guía de despliegue en Render
├── requirements.txt               # Dependencias Python
├── render.yaml                    # Configuración para Render
├── .gitignore                     # Archivos ignorados por Git
└── README.md                      # Este archivo
```

## 📊 Datos del Sistema

### Refacciones
- **Campos:** numero_parte, descripcion, marca, modelo, precio, stock, stock_minimo, ubicacion
- **Ejemplo:** BRK-001, Balata delantera, Brembo, Universal, $450.00, 15 unidades

### Pedidos
- **Campos:** numero_pedido, numero_parte, cantidad, proveedor, fecha_pedido, estatus
- **Estados:** Pendiente, En Tránsito, Recibido, Urgente, Cancelado

### Ventas
- **Campos:** numero_parte, cantidad, fecha, sucursal
- **Uso:** Análisis de rotación y generación de pedidos sugeridos

### Surtido a Taller
- **Campos:** orden_servicio, numero_parte, cantidad, estatus, fecha
- **Estados:** Surtido, Pendiente, En Proceso

## 🔌 Endpoints Principales

### Inventario

```http
GET /inventario/consultar?numero_parte=BRK-001
GET /inventario/disponibilidad/{numero_parte}
GET /inventario/bajo-stock
POST /inventario/entrada
```

### Pedidos

```http
GET /pedidos/sugerido
POST /pedidos/automatico
GET /pedidos/listar?estatus=Pendiente
GET /pedidos/{numero_pedido}
PUT /pedidos/{numero_pedido}/estatus
```

### Taller

```http
POST /taller/solicitar
```

### Consultas Rápidas

```http
GET /consultas/rapidas?pregunta=¿hay esta refacción?
```

### Reportes

```http
GET /reportes/resumen
```

## 💡 Ejemplos de Uso

### 1. Consultar Disponibilidad

```bash
curl -X GET "http://localhost:8000/inventario/disponibilidad/BRK-001"
```

**Respuesta:**
```json
{
  "numero_parte": "BRK-001",
  "disponible": true,
  "stock": 15,
  "ubicacion": "A1-01",
  "precio": 450.0,
  "descripcion": "Balata delantera"
}
```

### 2. Generar Pedido Sugerido

```bash
curl -X GET "http://localhost:8000/pedidos/sugerido"
```

**Respuesta:**
```json
[
  {
    "numero_parte": "SPK-002",
    "descripcion": "Bujía iridio",
    "cantidad_sugerida": 15,
    "stock_actual": 5,
    "razon": "Stock por debajo del mínimo"
  }
]
```

### 3. Solicitar Refacción para Taller

```bash
curl -X POST "http://localhost:8000/taller/solicitar" \
  -H "Content-Type: application/json" \
  -d '{
    "orden_servicio": "OS-20260312-0001",
    "numero_parte": "BRK-001",
    "cantidad": 2
  }'
```

**Respuesta (disponible):**
```json
{
  "disponible": true,
  "mensaje": "Refacción reservada para taller",
  "orden_servicio": "OS-20260312-0001",
  "numero_parte": "BRK-001",
  "cantidad": 2,
  "estatus": "Surtido"
}
```

### 4. Registrar Entrada de Refacciones

```bash
curl -X POST "http://localhost:8000/inventario/entrada" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_orden": "PED-20260312-001",
    "numero_parte": "BRK-001",
    "cantidad": 20,
    "proveedor": "Proveedor Principal"
  }'
```

## 🔄 Automatizaciones

### Pedido Automático Diario

El sistema puede generar automáticamente pedidos para refacciones con stock bajo:

```bash
curl -X POST "http://localhost:8000/pedidos/automatico"
```

**Lógica:**
- Si `stock < stock_minimo` → Genera pedido
- Cantidad sugerida: `stock_minimo * 2 - stock_actual`
- Estatus inicial: "Pendiente Aprobación"

### Pedido Sugerido Semanal

Análisis inteligente basado en:
- Ventas históricas (últimas 4 semanas)
- Inventario actual vs stock mínimo
- Rotación de piezas
- Temporalidad

## 🌐 Despliegue en Render

Para desplegar en producción, consulta la guía completa:

📖 [Guía de Despliegue en Render](docs/DESPLIEGUE_RENDER.md)

**Resumen rápido:**

1. Sube el código a GitHub
2. Conecta tu repositorio en Render.com
3. Configura el servicio con:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. ¡Despliega!

Tu API estará disponible en: `https://tu-servicio.onrender.com`

## 🛠️ Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **Pandas** - Manipulación de datos Excel
- **Pydantic** - Validación de datos
- **Uvicorn** - Servidor ASGI
- **OpenAPI** - Documentación automática

## 📝 Notas Importantes

### Datos Sintéticos

Los archivos Excel incluyen datos de prueba generados automáticamente:
- 30 refacciones diferentes
- 20 pedidos históricos
- 100 transacciones de ventas
- 30 surtidos a taller

Para regenerar los datos:
```bash
cd app
python crear_datos_sinteticos.py
```

### Persistencia de Datos

Actualmente, los datos se almacenan en archivos Excel. Para producción, considera:
- Migrar a PostgreSQL o MySQL
- Implementar respaldos automáticos
- Usar Redis para caché

### Limitaciones del Plan Free de Render

- El servicio se duerme después de 15 minutos de inactividad
- Primera petición puede tardar 30-60 segundos en despertar
- 750 horas/mes de uso
- 512 MB RAM

## 🔐 Seguridad

Para producción, implementa:
- Autenticación JWT
- API Keys
- Rate limiting
- CORS configurado
- Variables de entorno para credenciales

## 📈 Próximas Mejoras

- [ ] Autenticación y autorización
- [ ] Integración con DMS Autoflex
- [ ] Notificaciones por email/SMS
- [ ] Dashboard web
- [ ] Reportes avanzados en PDF
- [ ] Integración con proveedores
- [ ] App móvil

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es propiedad de **Grupo Picacho**.

## 📞 Contacto

**Grupo Picacho - Área de Refacciones y Postventa**

---

Desarrollado con ❤️ para Grupo Picacho