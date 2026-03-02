# 🚀 Inicio Rápido - Sistema de Análisis de Importaciones

## Instalación en 5 Pasos

### 1️⃣ Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2️⃣ Generar Datos (si no existen)

```bash
python generate_data.py
python generate_data_part2.py
python generate_data_part3.py
```

Esto creará la carpeta `data/` con 7 archivos CSV.

### 3️⃣ Iniciar el Servidor

```bash
python main.py
```

O con uvicorn:

```bash
uvicorn main:app --reload
```

### 4️⃣ Abrir Documentación Interactiva

Abre tu navegador en: **http://localhost:8000/docs**

### 5️⃣ Probar el Sistema

```bash
python test_api.py
```

---

## 🎯 Demo en 60 Segundos

### Opción A: Usando el Navegador

1. Abre: http://localhost:8000/docs
2. Expande el endpoint `/api/analisis/completo`
3. Click en "Try it out"
4. Ingresa los parámetros:
   - **rfc**: `ABC700101ABC`
   - **fraccion**: `8471.30`
   - **pais_origen**: `China`
   - **valor_unitario**: `450`
   - **cantidad**: `100`
5. Click en "Execute"

### Opción B: Usando cURL

```bash
curl "http://localhost:8000/api/analisis/completo?rfc=ABC700101ABC&fraccion=8471.30&pais_origen=China&valor_unitario=450&cantidad=100"
```

### Opción C: Usando Python

```python
import requests

response = requests.get(
    "http://localhost:8000/api/analisis/completo",
    params={
        "rfc": "ABC700101ABC",
        "fraccion": "8471.30",
        "pais_origen": "China",
        "valor_unitario": 450,
        "cantidad": 100
    }
)

data = response.json()
print(f"Nivel de riesgo: {data['resumen_ejecutivo']['nivel_riesgo_global']}")
print(f"Canal recomendado: {data['resumen_ejecutivo']['canal_recomendado']}")
```

---

## 📊 Ejemplos de Consultas

### Consultar Importador

```bash
curl "http://localhost:8000/api/importador/ABC700101ABC"
```

### Analizar Valor

```bash
curl "http://localhost:8000/api/valor/analizar?fraccion=8542.31&pais_origen=China&valor_unitario=4.20&cantidad=1000"
```

### Buscar Alertas

```bash
curl "http://localhost:8000/api/alertas/buscar?fraccion=8471.30&pais_origen=China"
```

### Generar Checklist

```bash
curl "http://localhost:8000/api/checklist/generar?fraccion=2106.90&pais_origen=Estados%20Unidos"
```

---

## 🔍 RFCs de Ejemplo para Probar

Los datos sintéticos incluyen 500 empresas. Algunos RFCs de ejemplo:

- **Perfil Verde (Confiable)**: Busca empresas con >50 operaciones
- **Perfil Amarillo (Revisión)**: Empresas con 10-50 operaciones
- **Perfil Rojo (Alto Riesgo)**: Empresas con <10 operaciones

Para ver todos los RFCs disponibles, consulta: `data/importadores.csv`

---

## 🛠️ Solución de Problemas

### Error: "Module not found"

```bash
pip install -r requirements.txt
```

### Error: "No such file or directory: 'data/importadores.csv'"

```bash
python generate_data.py
python generate_data_part2.py
python generate_data_part3.py
```

### Error: "Address already in use"

El puerto 8000 está ocupado. Usa otro puerto:

```bash
uvicorn main:app --reload --port 8001
```

### Error de conexión en test_api.py

Asegúrate de que el servidor esté corriendo:

```bash
python main.py
```

En otra terminal:

```bash
python test_api.py
```

---

## 📚 Documentación Completa

Para más información, consulta: **README.md**

---

## 🎓 Conceptos Clave

### Perfiles de Riesgo

- 🟢 **VERDE**: Importador confiable (>50 ops, <2% irregularidades, >3 años)
- 🟡 **AMARILLO**: En revisión (cambios recientes, volumen anormal)
- 🔴 **ROJO**: Alto riesgo (<6 meses, >10% irregularidades, SAT negativo)

### Canales de Desaduanamiento

- **VERDE**: Despacho libre
- **AMARILLO**: Reconocimiento documental
- **ROJO**: Reconocimiento físico

### Tipos de Alertas

- **TRI**: Triangulación de origen
- **SUB**: Subfacturación sistémica
- **FRA**: Clasificación incorrecta
- **PRO**: Producto prohibido/restringido
- **SAN**: Empresa sancionada
- **NOM**: NOM pendiente
- **DUM**: Dumping activo

---

## 💡 Tips

1. **Explora la documentación interactiva**: http://localhost:8000/docs
2. **Usa el script de pruebas**: `python test_api.py`
3. **Revisa los datos CSV** para entender la estructura
4. **Experimenta con diferentes parámetros** en los endpoints

---

**¡Listo para analizar importaciones! 🎉**