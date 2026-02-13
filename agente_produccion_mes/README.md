# Agente de Producción / Línea (MES)

API FastAPI para monitoreo de producción en tiempo real, análisis de desviaciones y recomendaciones operativas.

## Estructura de Archivos

```
agente_produccion_mes/
├── main.py                              # API FastAPI
├── requirements.txt                     # Dependencias Python
├── openapi.yaml                         # Especificación OpenAPI
├── descripcion_y_comportamiento.md      # Documentación del agente
├── generar_datos.py                     # Script para generar datos de prueba
├── datos_ordenes_produccion.xlsx        # Órdenes de producción
├── datos_estado_lineas.xlsx             # Estado actual de líneas
├── datos_downtime.xlsx                  # Eventos de downtime
├── datos_scrap.xlsx                     # Registros de scrap
├── datos_consumo_materiales.xlsx        # Consumo vs BOM
└── datos_personal.xlsx                  # Personal asignado
```

## Instalación Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Generar datos de prueba (opcional, ya están incluidos)
python generar_datos.py

# Ejecutar servidor
python main.py
```

La API estará disponible en `http://localhost:8000`

## Documentación API

Una vez ejecutando, accede a:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints Principales

- `GET /ordenes-produccion/list` - Lista todas las órdenes
- `GET /ordenes-produccion/activas` - Órdenes en proceso
- `GET /produccion-actual` - Estado actual de todas las líneas
- `POST /analisis-turno` - Analiza desviaciones de un turno
- `GET /consumo-materiales/{orden_id}` - Consumo vs BOM
- `POST /material-faltante` - Identifica materiales faltantes
- `GET /downtime/list` - Lista eventos de downtime
- `GET /scrap/list` - Lista eventos de scrap
- `GET /oee/calcular/{linea}` - Calcula OEE de una línea
- `GET /personal/asignado` - Personal por línea y turno

## Despliegue en Render

1. Crear nuevo Web Service en Render
2. Conectar repositorio de GitHub
3. Configurar:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.11

## Integración con Orchestrate

Para usar este agente en Orchestrate:

1. Despliega la API en Render
2. Obtén la URL pública (ej: `https://api-produccion-mes.onrender.com`)
3. En Orchestrate, crea un nuevo agente con tipo "API Tool"
4. Importa el archivo `openapi.yaml`
5. Configura la URL base del servidor

## Datos de Prueba

Los archivos Excel incluyen datos de muestra para demostración:
- 15 órdenes de producción en diferentes estados
- 4 líneas de producción con estado actual
- 20 eventos de downtime con diferentes causas
- 25 registros de scrap con defectos variados
- Consumo de materiales para 10 órdenes
- 20 empleados asignados a líneas

## Casos de Uso

1. **"¿Qué se está produciendo ahora?"**
   ```bash
   GET /produccion-actual
   ```

2. **"¿Por qué bajó el output en el turno?"**
   ```bash
   POST /analisis-turno
   {"linea": "Línea 1", "turno": 2}
   ```

3. **"¿Qué material falta para completar el lote?"**
   ```bash
   POST /material-faltante
   {"orden_id": "OP-2024-5678"}
   ```

## Métricas Clave

### OEE (Overall Equipment Effectiveness)
- **Disponibilidad**: Tiempo productivo / Tiempo total
- **Performance**: Tiempo ciclo ideal / Tiempo ciclo real
- **Calidad**: Unidades buenas / Unidades totales

### Análisis de Desviaciones
El agente identifica automáticamente:
- Causas de bajo rendimiento
- Impacto de downtime en producción
- Problemas de calidad (scrap elevado)
- Faltantes de material
- Desviaciones de tiempo ciclo

### Recomendaciones
Genera sugerencias accionables basadas en:
- Severidad de la desviación
- Causas raíz identificadas
- Histórico de problemas similares
- Mejores prácticas operativas

## Notas

- Los datos son generados aleatoriamente para demostración
- En producción, conectar a sistemas MES/SCADA reales
- Considerar autenticación/autorización para producción
- Los archivos Excel se pueden reemplazar con bases de datos en tiempo real
- El agente puede integrarse con sistemas de alertas (email, SMS, Slack)