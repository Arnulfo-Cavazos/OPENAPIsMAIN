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

    Diseñada para integración con:
    - WatsonX Orchestrate
    - Agentes IA industriales
    - ERP
    - Sistemas MES
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
# 📘 GUÍA SEMÁNTICA PARA AGENTE IA
# =====================================================

DATASET_GUIDE = {
    "downtime": {
        "description": "Eventos de paro en líneas de producción.",
    },
    "bom": {
        "description": "Bill of Materials asociado a órdenes."
    },
    "production": {
        "description": "Órdenes de producción planeadas y ejecutadas."
    },
    "5whys": {
        "description": "Análisis causa raíz estructurado bajo metodología 5 Whys."
    }
}

# =====================================================
# 📥 CARGA ROBUSTA CSV (ENCODING SAFE)
# =====================================================

def load_csv(dataset: str) -> pd.DataFrame:

    dataset = dataset.lower()

    if dataset not in CSV_FILES:
        raise HTTPException(status_code=400, detail="Dataset inválido")

    path = CSV_FILES[dataset]

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {path}")

    encodings_to_try = ["utf-8", "utf-8-sig", "latin1", "cp1252"]

    for enc in encodings_to_try:
        try:
            df = pd.read_csv(path, encoding=enc)

            # Limpieza avanzada de columnas
            df.columns = (
                df.columns
                .str.strip()
                .str.replace("\ufeff", "", regex=False)
            )

            return df

        except Exception:
            continue

    raise HTTPException(
        status_code=500,
        detail="No se pudo leer el CSV con ningún encoding soportado"
    )

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

        try:
            if exact:
                df = df[df[real_column].astype(str) == value]
            else:
                df = df[df[real_column].astype(str).str.contains(value, case=False, na=False)]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error aplicando filtro: {str(e)}"
            )

    return {
        "dataset": dataset,
        "rows": len(df),
        "columns": list(df.columns),
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
        raise HTTPException(
            status_code=500,
            detail=f"No se encontró columna de Part Number. Columnas disponibles: {list(df.columns)}"
        )

    result = df[df[part_column].astype(str).str.upper() == part_number.upper()]

    if result.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Número de parte {part_number} no encontrado"
        )

    return {
        "part_number": part_number,
        "rows_found": len(result),
        "data": result.to_dict(orient="records")
    }

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
# 📤 COMMIT A GITHUB
# =====================================================

def commit_5whys(df: pd.DataFrame, message: str):

    if not GITHUB_TOKEN or not GITHUB_REPO:
        return "GitHub not configured — local save only"

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CSV_5WHYS_PATH}"

    get_resp = requests.get(url, headers=HEADERS)

    if get_resp.status_code != 200:
        return f"Could not retrieve file SHA: {get_resp.text}"

    sha = get_resp.json()["sha"]

    encoded = base64.b64encode(df.to_csv(index=False).encode("utf-8")).decode()

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

    df.to_csv(CSV_FILES["5whys"], index=False, encoding="utf-8")

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
