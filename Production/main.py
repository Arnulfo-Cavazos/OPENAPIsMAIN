import os
import base64
import requests
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Manufacturing Intelligence API",
    description="""
    API diseñada para agentes de IA industriales.

    Permite:
    - Consultar órdenes de producción
    - Consultar Bill of Materials (BOM)
    - Consultar eventos de downtime
    - Consultar y agregar análisis 5 Whys
    - Filtrar dinámicamente por cualquier columna
    - Buscar por número de parte
    - Persistir análisis 5Whys en GitHub

    Ideal para integrarse con agentes tipo WatsonX Orchestrate,
    copilotos industriales o sistemas ERP.
    """
)

# =====================================================
# 🔐 CONFIGURACIÓN GITHUB
# =====================================================

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
CSV_5WHYS_PATH = os.getenv("CSV_5WHYS_PATH", "5whys.csv")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}" if GITHUB_TOKEN else "",
    "Accept": "application/vnd.github.v3+json"
}

# =====================================================
# 📁 ARCHIVOS LOCALES
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_FILES = {
    "bom": os.path.join(BASE_DIR, "BillOfMaterials.csv"),
    "downtime": os.path.join(BASE_DIR, "DownTimes.csv"),
    "production": os.path.join(BASE_DIR, "OrdenesDeProduccion.csv"),
    "5whys": os.path.join(BASE_DIR, "5whys.csv")
}

# =====================================================
# 📘 GUÍA SEMÁNTICA COMPLETA PARA AGENTE IA
# =====================================================

DATASET_GUIDE = {
    "downtime": {
        "description": "Eventos de paro en líneas de producción.",
        "columns_meaning": {
            "downtime_id": "Identificador único del evento de paro.",
            "order_id": "Orden de producción afectada.",
            "production_line": "Línea donde ocurrió el evento.",
            "machine_id": "Máquina específica afectada.",
            "station_id": "Estación dentro de la línea.",
            "start_time": "Inicio del paro.",
            "end_time": "Fin del paro.",
            "duration_minutes": "Duración total en minutos.",
            "downtime_category": "Categoría general del paro (Máquina, Material, Calidad, etc).",
            "downtime_reason_code": "Código específico del motivo.",
            "downtime_description": "Descripción textual del evento.",
            "shift": "Turno (A, B, C).",
            "operator_id": "Operador responsable.",
            "estimated_cost_per_min": "Costo estimado por minuto.",
            "total_downtime_cost": "Costo total del evento.",
            "related_scrap_id": "ID de scrap relacionado.",
            "status": "Estado del evento (Open, Closed)."
        }
    },
    "bom": {
        "description": "Bill of Materials asociado a órdenes.",
        "columns_meaning": {
            "order_id": "Orden de producción.",
            "parent_product": "Producto ensamblado.",
            "Part Number": "Número de parte del componente.",
            "component_description": "Descripción del componente.",
            "quantity_required": "Cantidad requerida.",
            "quantity_issued": "Cantidad liberada.",
            "quantity_consumed": "Cantidad consumida.",
            "unit": "Unidad de medida.",
            "status": "Estado del componente."
        }
    },
    "production": {
        "description": "Órdenes de producción planeadas y ejecutadas.",
        "columns_meaning": {
            "order_id": "Identificador de la orden.",
            "product_id": "Producto fabricado.",
            "quantity_planned": "Cantidad planeada.",
            "quantity_completed": "Cantidad terminada.",
            "start_date_planned": "Inicio planeado.",
            "end_date_planned": "Fin planeado.",
            "start_date_actual": "Inicio real.",
            "end_date_actual": "Fin real.",
            "status": "Estado actual.",
            "priority": "Prioridad numérica.",
            "production_line": "Línea asignada.",
            "shift": "Turno asignado."
        }
    },
    "5whys": {
        "description": "Análisis causa raíz estructurado bajo metodología 5 Whys.",
        "columns_meaning": {
            "analysis_id": "ID único del análisis.",
            "related_event_id": "Evento asociado (ej. downtime_id).",
            "problem_statement": "Definición del problema.",
            "why_1": "Primera causa.",
            "why_2": "Segunda causa.",
            "why_3": "Tercera causa.",
            "why_4": "Cuarta causa.",
            "why_5": "Quinta causa raíz.",
            "corrective_action": "Acción correctiva definida.",
            "status": "Estado del análisis."
        }
    }
}

# =====================================================
# 📥 CARGA SEGURA CSV
# =====================================================

def load_csv(dataset: str) -> pd.DataFrame:

    dataset = dataset.lower()

    if dataset not in CSV_FILES:
        raise HTTPException(status_code=400, detail="Dataset inválido")

    path = CSV_FILES[dataset]

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {path}")

    try:
        df = pd.read_csv(path, encoding="utf-8")
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error leyendo CSV: {str(e)}")

# =====================================================
# 📘 ENDPOINT GUÍA
# =====================================================

@app.get("/datasets/guide")
def get_guide():
    return DATASET_GUIDE

# =====================================================
# 🔎 CONSULTA DINÁMICA UNIVERSAL
# =====================================================

@app.get("/data/{dataset}")
def query_data(
    dataset: str,
    column: Optional[str] = Query(None),
    value: Optional[str] = Query(None),
    exact: bool = False
):

    df = load_csv(dataset)

    if column and value:
        real_column = next(
            (c for c in df.columns if c.lower() == column.lower()),
            None
        )

        if not real_column:
            raise HTTPException(
                status_code=400,
                detail=f"Columna inválida. Disponibles: {list(df.columns)}"
            )

        if exact:
            df = df[df[real_column].astype(str) == value]
        else:
            df = df[df[real_column].astype(str).str.contains(value, case=False, na=False)]

    return {
        "dataset": dataset,
        "rows": len(df),
        "data": df.to_dict(orient="records")
    }

# =====================================================
# 🔎 BÚSQUEDA POR NÚMERO DE PARTE
# =====================================================

@app.get("/bom/part/{part_number}")
def get_part_details(part_number: str):

    df = load_csv("bom")

    part_column = next(
        (c for c in df.columns if "part" in c.lower()),
        None
    )

    if not part_column:
        raise HTTPException(status_code=500, detail="Columna Part Number no encontrada")

    result = df[df[part_column].astype(str).str.upper() == part_number.upper()]

    if result.empty:
        raise HTTPException(status_code=404, detail="Parte no encontrada")

    return result.to_dict(orient="records")

# =====================================================
# ✏️ MODELO 5WHYS
# =====================================================

class FiveWhysModel(BaseModel):
    analysis_id: str
    related_event_id: str
    problem_statement: str
    why_1: str
    why_2: str
    why_3: str
    why_4: str
    why_5: str
    corrective_action: str
    status: str

# =====================================================
# 📤 COMMIT A GITHUB (OPCIONAL)
# =====================================================

def commit_5whys(df: pd.DataFrame, message: str):

    if not GITHUB_TOKEN or not GITHUB_REPO:
        return "GitHub not configured — local save only"

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CSV_5WHYS_PATH}"

    get_resp = requests.get(url, headers=HEADERS)

    if get_resp.status_code != 200:
        return "Could not retrieve file SHA"

    sha = get_resp.json()["sha"]

    encoded = base64.b64encode(df.to_csv(index=False).encode()).decode()

    payload = {
        "message": message,
        "content": encoded,
        "sha": sha,
        "branch": GITHUB_BRANCH
    }

    put_resp = requests.put(url, headers=HEADERS, json=payload)

    if put_resp.status_code not in [200, 201]:
        return f"GitHub error: {put_resp.text}"

    return put_resp.json()["commit"]["sha"]

# =====================================================
# ➕ AGREGAR 5WHYS
# =====================================================

@app.post("/5whys/add")
def add_5whys(record: FiveWhysModel):

    df = load_csv("5whys")

    new_row = pd.DataFrame([record.dict()])
    df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv(CSV_FILES["5whys"], index=False)

    commit_result = commit_5whys(
        df,
        f"Add 5Whys analysis {record.analysis_id}"
    )

    return {
        "status": "5Whys added successfully",
        "commit_result": commit_result
    }

# =====================================================
# ❤️ HEALTHCHECK
# =====================================================

@app.get("/")
def root():
    return {
        "status": "Manufacturing AI API running",
        "datasets_available": list(CSV_FILES.keys())
    }
