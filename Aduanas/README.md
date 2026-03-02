# Sistema de Análisis de Importaciones - Agente de Inteligencia Aduanera

Sistema completo de análisis de operaciones de importación con 4 módulos de inteligencia aduanera y bases de datos sintéticas.

## 🎯 Características Principales

### MÓDULO 1 — Historial del Importador (24 meses)
- Análisis completo de operaciones históricas
- Perfil de riesgo automático (🟢 Verde / 🟡 Amarillo / 🔴 Rojo)
- Detección de patrones anormales
- Comparación con promedio del sector
- Alertas automáticas sobre cambios súbitos

### MÓDULO 2 — Valor de Referencia Internacional
- Comparación con precios de mercado internacional
- Detección de subfacturación/sobrefacturación
- Cálculo de percentiles de mercado
- Análisis de tendencias de precios
- Alertas de desviación significativa

### MÓDULO 3 — Alertas Activas de Inteligencia
- 120 alertas de inteligencia (40 vigentes)
- 7 tipos de alertas (Triangulación, Subfacturación, etc.)
- Verificación de proveedores en listas de observación
- Modus operandi documentados
- Acciones recomendadas específicas

### MÓDULO 4 — Checklist Regulatorio Personalizado
- Checklist dinámico por fracción arancelaria
- Verificación de NOMs aplicables
- Permisos previos requeridos
- Tratados comerciales disponibles
- Recomendación de canal de desaduanamiento

## 📊 Bases de Datos Sintéticas

El sistema incluye 7 bases de datos CSV con datos realistas:

1. **importadores.csv** - 500 empresas importadoras
2. **pedimentos_historicos.csv** - 15,000 operaciones de importación
3. **precios_referencia_internacionales.csv** - ~800 precios de referencia
4. **alertas_inteligencia.csv** - 120 alertas de inteligencia
5. **proveedores_extranjeros.csv** - 300 proveedores internacionales
6. **regulaciones_por_fraccion.csv** - 300 regulaciones por fracción
7. **tipo_cambio_historico.csv** - 730 días de tipo de cambio

## 🚀 Instalación y Configuración

### 1. Clonar o descargar el proyecto

```bash
cd bob1
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Generar datos sintéticos

```bash
python generate_data.py
python generate_data_part2.py
python generate_data_part3.py
```

Esto creará la carpeta `data/` con todos los archivos CSV.

### 5. Iniciar el servidor FastAPI

```bash
python main.py
```

O usando uvicorn directamente:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: **http://localhost:8000**

## 📖 Documentación de la API

### Documentación Interactiva

Una vez iniciado el servidor, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Principales

#### 🎯 Análisis Completo (Demo en 60 segundos)

```http
GET /api/analisis/completo?rfc=ABC123456789&fraccion=8471.30&pais_origen=China&valor_unitario=450&cantidad=100
```

**Respuesta incluye:**
- Análisis del historial del importador
- Comparación de valor con mercado
- Alertas activas relevantes
- Checklist regulatorio personalizado
- Recomendación de canal
- Acciones inmediatas

#### 📋 Módulo 1: Historial del Importador

```http
GET /api/importador/{rfc}
GET /api/importador/{rfc}/operaciones
GET /api/importador/{rfc}/comparacion-sector
```

#### 💰 Módulo 2: Valor de Referencia

```http
GET /api/valor/analizar?fraccion=8471.30&pais_origen=China&valor_unitario=450&cantidad=100
GET /api/valor/estadisticas/{fraccion}
```

#### ⚠️ Módulo 3: Alertas de Inteligencia

```http
GET /api/alertas/vigentes
GET /api/alertas/buscar?fraccion=8471.30&pais_origen=China
GET /api/alertas/estadisticas
GET /api/alertas/modus-operandi
```

#### ✅ Módulo 4: Checklist Regulatorio

```http
GET /api/checklist/generar?fraccion=8471.30&pais_origen=China
GET /api/checklist/noms/{fraccion}
GET /api/checklist/tratados/{pais}
```

## 🎬 Demo Rápida (60 segundos)

### Ejemplo 1: Operación de Bajo Riesgo

```bash
curl "http://localhost:8000/api/analisis/completo?rfc=ABC700101ABC&fraccion=8471.30&pais_origen=Estados%20Unidos&valor_unitario=800&cantidad=50"
```

**Resultado esperado:**
- 🟢 Importador confiable
- 🟢 Valor dentro de parámetros normales
- Sin alertas críticas
- Canal recomendado: VERDE

### Ejemplo 2: Operación de Alto Riesgo

```bash
curl "http://localhost:8000/api/analisis/completo?rfc=XYZ991231XYZ&fraccion=8542.31&pais_origen=China&valor_unitario=4.20&cantidad=1000"
```

**Resultado esperado:**
- 🔴 Importador nuevo o con irregularidades
- 🔴 Subfacturación detectada (46% por debajo del mercado)
- ⚠️ Alertas activas de triangulación
- 📋 Documentos faltantes
- Canal recomendado: ROJO

## 📁 Estructura del Proyecto

```
bob1/
├── data/                          # Bases de datos CSV
│   ├── importadores.csv
│   ├── pedimentos_historicos.csv
│   ├── precios_referencia_internacionales.csv
│   ├── alertas_inteligencia.csv
│   ├── proveedores_extranjeros.csv
│   ├── regulaciones_por_fraccion.csv
│   └── tipo_cambio_historico.csv
├── models/                        # Modelos Pydantic
│   ├── __init__.py
│   └── schemas.py
├── modules/                       # Módulos de análisis
│   ├── __init__.py
│   ├── modulo1_historial.py      # Historial del importador
│   ├── modulo2_valor.py          # Análisis de valor
│   ├── modulo3_alertas.py        # Alertas de inteligencia
│   └── modulo4_checklist.py      # Checklist regulatorio
├── generate_data.py               # Generador de datos parte 1
├── generate_data_part2.py         # Generador de datos parte 2
├── generate_data_part3.py         # Generador de datos parte 3
├── main.py                        # Aplicación FastAPI
├── requirements.txt               # Dependencias
└── README.md                      # Este archivo
```

## 🔍 Casos de Uso

### Caso 1: Verificación Rápida de Importador

```python
import requests

rfc = "ABC123456789"
response = requests.get(f"http://localhost:8000/api/importador/{rfc}")
data = response.json()

print(f"Perfil de riesgo: {data['perfil_riesgo']}")
print(f"Total operaciones: {data['total_operaciones']}")
print(f"Tasa irregularidades: {data['tasa_irregularidades']}%")
```

### Caso 2: Análisis de Valor Declarado

```python
import requests

params = {
    "fraccion": "8471.30",
    "pais_origen": "China",
    "valor_unitario": 450,
    "cantidad": 100
}

response = requests.get("http://localhost:8000/api/valor/analizar", params=params)
data = response.json()

print(f"Desviación: {data['desviacion_porcentual']}%")
print(f"Nivel de riesgo: {data['nivel_riesgo']}")
```

### Caso 3: Búsqueda de Alertas Activas

```python
import requests

params = {
    "fraccion": "8542.31",
    "pais_origen": "China"
}

response = requests.get("http://localhost:8000/api/alertas/buscar", params=params)
data = response.json()

print(f"Alertas encontradas: {data['total_alertas']}")
for alerta in data['alertas']:
    print(f"- {alerta['titulo']} ({alerta['nivel_criticidad']})")
```

## 🎨 Interpretación de Resultados

### Perfiles de Riesgo

- **🟢 VERDE (Confiable)**
  - >50 operaciones en 24 meses
  - <2% de irregularidades
  - >3 años activo
  - Opinión SAT positiva

- **🟡 AMARILLO (En Revisión)**
  - Cambios súbitos de volumen
  - Nuevo agente aduanal
  - 1-3 años de antigüedad
  - Irregularidades moderadas (2-10%)

- **🔴 ROJO (Alto Riesgo)**
  - <6 meses activo
  - >10% irregularidades
  - Opinión SAT negativa
  - Primera importación de fracción

### Canales de Desaduanamiento

- **VERDE**: Despacho libre sin reconocimiento
- **AMARILLO**: Reconocimiento documental
- **ROJO**: Reconocimiento físico de mercancía

## 🛠️ Desarrollo y Extensión

### Agregar Nuevas Fracciones Arancelarias

Edita `generate_data_part2.py` y agrega a la lista `fracciones_detalladas`:

```python
("9999.99", "Nueva descripción", "PZA", precio_min, precio_max)
```

### Agregar Nuevas Alertas

Edita `generate_data_part2.py` en la función `generate_alertas()`.

### Personalizar Regulaciones

Edita `generate_data_part3.py` en la función `generate_regulaciones()`.

## 📊 Estadísticas del Sistema

- **500** empresas importadoras
- **15,000** operaciones históricas
- **~800** precios de referencia internacional
- **120** alertas de inteligencia (40 vigentes)
- **300** proveedores extranjeros
- **300** regulaciones por fracción
- **730** días de tipo de cambio

## 🔐 Seguridad y Privacidad

⚠️ **IMPORTANTE**: Este sistema utiliza datos sintéticos generados aleatoriamente. No contiene información real de empresas, personas o operaciones comerciales.

## 📝 Notas Técnicas

- Los datos son generados con semilla aleatoria fija (seed=42) para reproducibilidad
- Los RFCs son ficticios y no corresponden a empresas reales
- Los precios de referencia son simulados basados en rangos realistas
- Las alertas son ejemplos educativos de patrones de fraude conocidos

## 🤝 Contribuciones

Este es un proyecto de demostración. Para mejoras o sugerencias, considera:

1. Agregar más fracciones arancelarias
2. Implementar machine learning para detección de patrones
3. Integrar con APIs reales de tipo de cambio
4. Agregar visualizaciones con gráficas
5. Implementar autenticación y autorización

## 📄 Licencia

Este proyecto es de código abierto para fines educativos y de demostración.

## 📞 Soporte

Para preguntas o problemas:
1. Revisa la documentación en `/docs`
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de que los datos CSV se hayan generado correctamente

---

**Desarrollado con FastAPI, Pandas y Python** 🐍