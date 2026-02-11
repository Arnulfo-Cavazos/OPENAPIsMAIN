import os
import base64
import requests
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Manufacturing AI Data API")

# =====================================================
# 🔐 CONFIGURACIÓN GITHUB (SOLO PARA 5WHYS)
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
    "bom": {
        "description": "Bill of Materials por orden de producción",
        "key_columns": ["order_id", "Part Number", "parent_product"]
    },
    "downtime": {
        "description": "Eventos de paro en producción",
        "key_columns": ["downtime_id", "order_id", "machine_id"]
    },
    "production": {
        "description": "Órdenes de producción",
        "key_columns": ["order_id", "product_id", "status"]
    },
    "5whys": {
        "description": "Análisis causa raíz",
        "key_columns": ["analysis_id", "related_event_id"]
    }
}

# =====================================================
# 📥 CARGAR CSV LOCAL (ROBUSTO)
# =====================================================

def load_csv(dataset: str) -> pd.DataFrame:
    file_path = CSV_FILES.get(dataset)

    if not file_path:
        raise HTTPException(status_code=400, detail="Dataset inválido")

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"Archivo no encontrado en producción: {file_path}"
        )

    try:
        df = pd.read_csv(file_path, encoding="utf-8")
        df.columns = df.columns.str.strip()  # eliminar espacios invisibles
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
# 🔎 CONSULTA DINÁMICA SEGURA
# =====================================================

@app.get("/data/{dataset}")
def query_data(
    dataset: str,
    column: Optional[str] = Query(None),
    value: Optional[str] = Query(None),
    exact: Optional[bool] = Query(False)
):

    df = load_csv(dataset)

    if column and value:

        # Buscar columna ignorando mayúsculas
        matched_column = None
        for col in df.columns:
            if col.lower() == column.lower():
                matched_column = col
                break

        if not matched_column:
            raise HTTPException(
                status_code=400,
                detail=f"Columna inválida. Disponibles: {list(df.columns)}"
            )

        try:
            if exact:
                df = df[df[matched_column].astype(str) == value]
            else:
                df = df[df[matched_column].astype(str).str.contains(value, case=False, na=False)]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error filtrando datos: {str(e)}")

    return {
        "dataset": dataset,
        "rows": len(df),
        "columns": list(df.columns),
        "data": df.to_dict(orient="records")
    }


# =====================================================
# 🔎 BÚSQUEDA ROBUSTA POR NÚMERO DE PARTE
# =====================================================

@app.get("/bom/part/{part_number}")
def get_part_details(part_number: str):

    df = load_csv("bom")

    # Buscar columna que contenga "part"
    target_column = None
    for col in df.columns:
        if "part" in col.lower():
            target_column = col
            break

    if not target_column:
        raise HTTPException(
            status_code=500,
            detail=f"No se encontró columna relacionada a 'Part Number'. Columnas disponibles: {list(df.columns)}"
        )

    df_filtered = df[
        df[target_column].astype(str).str.upper() == part_number.upper()
    ]

    if df_filtered.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Número de parte {part_number} no encontrado"
        )

    return {
        "part_number": part_number,
        "column_used": target_column,
        "rows": len(df_filtered),
        "data": df_filtered.to_dict(orient="records")
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
# 📤 COMMIT A GITHUB ROBUSTO
# =====================================================

def commit_5whys_to_github(df: pd.DataFrame, message: str):

    if not GITHUB_TOKEN or not GITHUB_REPO:
        raise HTTPException(status_code=500, detail="GitHub no configurado")

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CSV_5WHYS_PATH}"

    try:
        get_resp = requests.get(url, headers=HEADERS)
        if get_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="No se pudo obtener SHA del archivo")

        sha = get_resp.json()["sha"]

        csv_content = df.to_csv(index=False)
        encoded_content = base64.b64encode(csv_content.encode()).decode()

        payload = {
            "message": message,
            "content": encoded_content,
            "sha": sha,
            "branch": GITHUB_BRANCH
        }

        put_resp = requests.put(url, headers=HEADERS, json=payload)

        if put_resp.status_code not in [200, 201]:
            raise HTTPException(
                status_code=500,
                detail=f"Error haciendo commit: {put_resp.text}"
            )

        return put_resp.json()["commit"]["sha"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error GitHub: {str(e)}")


# =====================================================
# ✏️ AGREGAR 5WHYS + COMMIT
# =====================================================

@app.post("/5whys/add")
def add_5whys(record: FiveWhysModel):

    df = load_csv("5whys")
    new_row = pd.DataFrame([record.dict()])
    df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv(CSV_FILES["5whys"], index=False)

    commit_sha = commit_5whys_to_github(
        df,
        f"Add 5Whys analysis {record.analysis_id}"
    )

    return {
        "status": "success",
        "commit_sha": commit_sha
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
