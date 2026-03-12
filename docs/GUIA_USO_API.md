# Guía de Uso - API Refacciones Grupo Picacho

## 📖 Introducción

Esta guía te ayudará a utilizar la API de Refacciones y Postventa de Grupo Picacho de manera efectiva.

## 🌐 Acceso a la API

### Desarrollo Local
```
http://localhost:8000
```

### Producción (Render)
```
https://tu-servicio.onrender.com
```

### Documentación Interactiva
- **Swagger UI:** `/docs` - Interfaz interactiva para probar endpoints
- **ReDoc:** `/redoc` - Documentación detallada
- **OpenAPI JSON:** `/openapi.json` - Especificación OpenAPI

## 🔍 Casos de Uso Comunes

### 1. Consultar si hay una refacción disponible

**Escenario:** Un técnico del taller necesita saber si hay balatas disponibles.

**Endpoint:**
```http
GET /inventario/disponibilidad/BRK-001
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

**Interpretación:**
- ✅ Hay 15 unidades disponibles
- 📍 Ubicadas en el anaquel A1-01
- 💰 Precio: $450.00

---

### 2. Buscar refacciones por modelo de vehículo

**Escenario:** Necesitas ver todas las refacciones disponibles para un Honda Civic.

**Endpoint:**
```http
GET /inventario/consultar?modelo=Civic
```

**Respuesta:**
```json
[
  {
    "numero_parte": "FLT-001",
    "descripcion": "Filtro de aceite estándar",
    "marca": "Mann",
    "modelo": "Civic/Corolla",
    "precio": 85.0,
    "stock": 25,
    "stock_minimo": 15,
    "ubicacion": "A2-01"
  },
  {
    "numero_parte": "BLT-001",
    "descripcion": "Banda de distribución",
    "marca": "Gates",
    "modelo": "Civic/Corolla",
    "precio": 850.0,
    "stock": 6,
    "stock_minimo": 8,
    "ubicacion": "B2-01"
  }
]
```

---

### 3. Verificar refacciones con stock bajo

**Escenario:** Cada mañana, el encargado de refacciones revisa qué piezas necesitan reorden.

**Endpoint:**
```http
GET /inventario/bajo-stock
```

**Respuesta:**
```json
{
  "total": 5,
  "refacciones": [
    {
      "numero_parte": "BRK-002",
      "descripcion": "Balata trasera",
      "stock": 8,
      "stock_minimo": 10,
      "ubicacion": "A1-02"
    },
    {
      "numero_parte": "SPK-002",
      "descripcion": "Bujía iridio",
      "stock": 5,
      "stock_minimo": 10,
      "ubicacion": "A3-02"
    }
  ]
}
```

**Acción recomendada:** Generar pedidos para estas refacciones.

---

### 4. Generar pedido sugerido semanal

**Escenario:** Es lunes y necesitas generar el pedido semanal basado en análisis de ventas.

**Endpoint:**
```http
GET /pedidos/sugerido
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
  },
  {
    "numero_parte": "OIL-001",
    "descripcion": "Aceite 10W-30",
    "cantidad_sugerida": 30,
    "stock_actual": 20,
    "razon": "Alta rotación de ventas"
  }
]
```

**Interpretación:**
- El sistema analiza ventas históricas
- Compara con inventario actual
- Sugiere cantidades óptimas de compra

---

### 5. Generar pedido automático diario

**Escenario:** Automatización diaria que genera pedidos para refacciones críticas.

**Endpoint:**
```http
POST /pedidos/automatico
```

**Respuesta:**
```json
{
  "mensaje": "Pedidos automáticos generados",
  "pedidos_generados": 3,
  "pedidos": [
    {
      "numero_pedido": "AUTO-20260312172800-BRK-002",
      "numero_parte": "BRK-002",
      "cantidad": 12,
      "proveedor": "Proveedor Principal",
      "fecha_pedido": "2026-03-12",
      "estatus": "Pendiente Aprobación"
    }
  ]
}
```

**Flujo:**
1. Sistema detecta stock < stock_mínimo
2. Genera pedido automáticamente
3. Calcula cantidad: `stock_minimo * 2 - stock_actual`
4. Envía para aprobación

---

### 6. Solicitar refacción para taller

**Escenario:** Un técnico necesita balatas para una orden de servicio.

**Endpoint:**
```http
POST /taller/solicitar
Content-Type: application/json

{
  "orden_servicio": "OS-20260312-0001",
  "numero_parte": "BRK-001",
  "cantidad": 2
}
```

**Respuesta (Caso 1: Disponible):**
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

**Respuesta (Caso 2: No disponible):**
```json
{
  "disponible": false,
  "mensaje": "Stock insuficiente - Pedido urgente generado",
  "orden_servicio": "OS-20260312-0001",
  "numero_parte": "BRK-001",
  "cantidad_solicitada": 2,
  "stock_disponible": 0,
  "pedido_urgente": "URG-20260312172800-BRK-001",
  "estatus": "Pendiente"
}
```

**Flujo automático:**
1. Sistema verifica disponibilidad
2. Si hay stock → Reserva y actualiza inventario
3. Si no hay stock → Genera pedido urgente automáticamente

---

### 7. Registrar entrada de refacciones

**Escenario:** Llegó un pedido del proveedor y necesitas registrar la entrada.

**Endpoint:**
```http
POST /inventario/entrada
Content-Type: application/json

{
  "numero_orden": "PED-20260312-001",
  "numero_parte": "BRK-001",
  "cantidad": 20,
  "proveedor": "Proveedor Principal"
}
```

**Respuesta:**
```json
{
  "mensaje": "Entrada registrada exitosamente",
  "numero_parte": "BRK-001",
  "cantidad": 20,
  "stock_nuevo": 35
}
```

**Acciones automáticas:**
1. Actualiza stock en inventario
2. Actualiza estatus del pedido a "Recibido"
3. Registra fecha de entrada

---

### 8. Consultar estado de pedidos

**Escenario:** Quieres ver todos los pedidos pendientes.

**Endpoint:**
```http
GET /pedidos/listar?estatus=Pendiente
```

**Respuesta:**
```json
{
  "total": 5,
  "pedidos": [
    {
      "numero_pedido": "PED-20260310-001",
      "numero_parte": "BRK-001",
      "cantidad": 20,
      "proveedor": "Proveedor Principal",
      "fecha_pedido": "2026-03-10",
      "estatus": "Pendiente"
    },
    {
      "numero_pedido": "URG-20260312-SPK-002",
      "numero_parte": "SPK-002",
      "cantidad": 10,
      "proveedor": "Proveedor Principal",
      "fecha_pedido": "2026-03-12",
      "estatus": "Urgente"
    }
  ]
}
```

**Filtros disponibles:**
- `?estatus=Pendiente` - Pedidos pendientes
- `?estatus=En Tránsito` - Pedidos en camino
- `?estatus=Recibido` - Pedidos recibidos
- `?estatus=Urgente` - Pedidos urgentes
- Sin filtro - Todos los pedidos

---

### 9. Actualizar estatus de pedido

**Escenario:** El proveedor confirmó que el pedido está en tránsito.

**Endpoint:**
```http
PUT /pedidos/PED-20260310-001/estatus?nuevo_estatus=En Tránsito
```

**Respuesta:**
```json
{
  "mensaje": "Estatus actualizado",
  "numero_pedido": "PED-20260310-001",
  "nuevo_estatus": "En Tránsito"
}
```

**Estados válidos:**
- `Pendiente` - Pedido creado, esperando confirmación
- `En Tránsito` - Pedido confirmado y en camino
- `Recibido` - Pedido recibido y registrado
- `Urgente` - Pedido prioritario
- `Cancelado` - Pedido cancelado

---

### 10. Consultas rápidas del área de servicio

**Escenario:** El área de servicio hace preguntas frecuentes.

**Endpoint:**
```http
GET /consultas/rapidas?pregunta=¿cuándo llega el pedido?
```

**Respuesta:**
```json
{
  "tipo": "pedidos_pendientes",
  "total": 5,
  "pedidos": [
    {
      "numero_pedido": "PED-20260310-001",
      "numero_parte": "BRK-001",
      "cantidad": 20,
      "proveedor": "Proveedor Principal",
      "fecha_pedido": "2026-03-10",
      "estatus": "En Tránsito"
    }
  ]
}
```

**Preguntas soportadas:**
- "¿hay esta refacción?" → Redirige a consulta de disponibilidad
- "¿cuándo llega el pedido?" → Muestra pedidos pendientes/en tránsito
- "¿qué piezas están pendientes?" → Muestra surtidos pendientes

---

### 11. Reporte resumen del sistema

**Escenario:** Dashboard ejecutivo o reporte matutino.

**Endpoint:**
```http
GET /reportes/resumen
```

**Respuesta:**
```json
{
  "fecha": "2026-03-12 17:30:00",
  "inventario": {
    "total_refacciones": 30,
    "refacciones_bajo_stock": 5,
    "valor_total_inventario": 25450.0
  },
  "pedidos": {
    "total_pedidos": 20,
    "pedidos_pendientes": 5,
    "pedidos_urgentes": 2
  },
  "ventas": {
    "total_transacciones": 100,
    "piezas_vendidas": 250
  }
}
```

**Uso:** Ideal para dashboards, reportes diarios o monitoreo general.

---

## 🔄 Flujos de Trabajo Completos

### Flujo 1: Atención de Orden de Servicio

1. **Taller solicita refacción**
   ```http
   POST /taller/solicitar
   ```

2. **Si no hay stock, se genera pedido urgente automáticamente**

3. **Cuando llega el pedido, se registra entrada**
   ```http
   POST /inventario/entrada
   ```

4. **Sistema actualiza inventario y notifica disponibilidad**

### Flujo 2: Gestión Semanal de Inventario

1. **Lunes: Revisar stock bajo**
   ```http
   GET /inventario/bajo-stock
   ```

2. **Generar pedido sugerido**
   ```http
   GET /pedidos/sugerido
   ```

3. **Revisar y aprobar pedidos**
   ```http
   GET /pedidos/listar?estatus=Pendiente
   ```

4. **Actualizar estatus cuando proveedor confirma**
   ```http
   PUT /pedidos/{numero_pedido}/estatus
   ```

5. **Registrar entrada cuando llega**
   ```http
   POST /inventario/entrada
   ```

### Flujo 3: Automatización Diaria

1. **Sistema ejecuta pedido automático (cron job)**
   ```http
   POST /pedidos/automatico
   ```

2. **Genera alertas para refacciones críticas**

3. **Envía notificaciones al encargado**

---

## 💡 Mejores Prácticas

### 1. Consultas Frecuentes
- Usa `/inventario/disponibilidad/{numero_parte}` para consultas rápidas
- Usa `/inventario/consultar` con filtros para búsquedas amplias

### 2. Gestión de Pedidos
- Revisa `/inventario/bajo-stock` diariamente
- Genera `/pedidos/sugerido` semanalmente
- Mantén actualizado el estatus de pedidos

### 3. Surtido a Taller
- Usa `/taller/solicitar` para todas las solicitudes
- El sistema maneja automáticamente la disponibilidad
- Genera pedidos urgentes cuando es necesario

### 4. Reportes
- Usa `/reportes/resumen` para dashboards
- Exporta datos para análisis más profundos

---

## 🚨 Manejo de Errores

### Error 404 - No Encontrado
```json
{
  "detail": "Refacción no encontrada"
}
```
**Solución:** Verifica el número de parte

### Error 500 - Error del Servidor
```json
{
  "detail": "Error al leer refacciones.xlsx: ..."
}
```
**Solución:** Verifica que los archivos Excel existan en `/data`

---

## 📞 Soporte

Para dudas o problemas:
1. Revisa la documentación en `/docs`
2. Consulta ejemplos en este documento
3. Contacta al equipo de desarrollo

---

**¡Listo para usar la API!** 🚀