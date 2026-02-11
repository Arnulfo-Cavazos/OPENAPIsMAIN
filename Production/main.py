import os
import base64
import requests
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Manufacturing AI Data API")

# =====================================================
# 🔐 CONFIGURACIÓN GITHUB (PARA 5WHYS)
# =====================================================

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
CSV_5WHYS_PATH = os.getenv("CSV_5WHYS_PATH", "5whys.csv")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# =====================================================
# 📁 PATH BASE SEGURO (IMPORTANTE PARA RENDER)
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_FILES = {
    "bom": os.path.join(BASE_DIR, "BillOfMaterials.csv"),
    "downtime": os.path.join(BASE_DIR, "DownTimes.csv"),
    "production": os.path.join(BASE_DIR, "OrdenesDeProduccion.csv"),
    "5whys": os.path.join(BASE_DIR, "5whys.csv")
}

# =====================================================
# 📘 DESCRIPCIÓN SEMÁNTICA BASE
# =====================================================

DATASET_DESCRIPTIONS = {
    "bom": "Bill of Materials por orden de producción",
    "downtime": "Eventos de paro en producción",
    "production": "Órdenes de producción",
    "5whys": "Análisis causa raíz tipo 5 Why"
}

# =====================================================
# 📥 CARGAR CSV SEGURO
# =====================================================

def load_csv(dataset: str) -> pd.DataFrame:
    file_path = CSV_FILES.get(dataset)

    if not file_path:
        raise HTTPException(status_code=400, detail="Dataset inválido")

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"Archivo no encontrado: {file_path}"
        )

    try:
        return pd.read_csv(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# 📘 GUÍA DINÁMICA PARA AGENTE IA
# =====================================================

@app.get("/datasets/guide")
def get_guide():

    response = {}

    for key in CSV_FILES:
        try:
            df = load_csv(key)
            response[key] = {
                "description": DATASET_DESCRIPTIONS.get(key, ""),
                "rows": len(df),
                "columns": list(df.columns),
                "filter_example": f"/data/{key}?column=order_id&value=PO-1001"
            }
        except Exception as e:
            response[key] = {"error": str(e)}

    return response


# =====================================================
# 🔎 CONSULTA DINÁMICA UNIVERSAL
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

        if column not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Columna inválida. Disponibles: {list(df.columns)}"
            )

        try:
            if exact:
                df = df[df[column].astype(str) == value]
            else:
                df = df[df[column].astype(str).str.contains(value, case=False, na=False)]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {
        "dataset": dataset,
        "rows": len(df),
        "columns": list(df.columns),
        "data": df.to_dict(orient="records")
    }


# =====================================================
# 🔎 BÚSQUEDA ESPECIAL POR NÚMERO DE PARTE
# =====================================================

@app.get("/bom/part/{part_number}")
def get_part_details(part_number: str):

    df = load_csv("bom")

    if "Part Number" not in df.columns:
        raise HTTPException(
            status_code=500,
            detail=f"Columna 'Part Number' no encontrada. Columnas: {list(df.columns)}"
        )

    df_filtered = df[
        df["Part Number"].astype(str).str.upper() == part_number.upper()
    ]

    if df_filtered.empty:
        raise HTTPException(status_code=404, detail="Número de parte no encontrado")

    return {
        "part_number": part_number,
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
# 📤 COMMIT ROBUSTO A GITHUB
# =====================================================

def commit_5whys_to_github(df: pd.DataFrame, message: str):

    if not GITHUB_TOKEN or not GITHUB_REPO:
        raise HTTPException(
            status_code=500,
            detail="GitHub no configurado en variables de entorno"
        )

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CSV_5WHYS_PATH}"

    csv_content = df.to_csv(index=False)
    encoded_content = base64.b64encode(csv_content.encode()).decode()

    get_resp = requests.get(url, headers=HEADERS)

    if get_resp.status_code == 200:
        sha = get_resp.json()["sha"]
        payload = {
            "message": message,
            "content": encoded_content,
            "sha": sha,
            "branch": GITHUB_BRANCH
        }

    elif get_resp.status_code == 404:
        payload = {
            "message": message,
            "content": encoded_content,
            "branch": GITHUB_BRANCH
        }

    else:
        raise HTTPException(status_code=500, detail=get_resp.text)

    put_resp = requests.put(url, headers=HEADERS, json=payload)

    if put_resp.status_code not in [200, 201]:
        raise HTTPException(status_code=500, detail=put_resp.text)

    return put_resp.json()["commit"]["sha"]


# =====================================================
# ✏️ AGREGAR 5WHYS + COMMIT
# =====================================================

@app.post("/5whys/add")
def add_5whys(record: FiveWhysModel):

    df = load_csv("5whys")

    new_row = pd.DataFrame([record.dict()])
    df_updated = pd.concat([df, new_row], ignore_index=True)

    # Guardar local (solo temporal en Render)
    df_updated.to_csv(CSV_FILES["5whys"], index=False)

    commit_sha = commit_5whys_to_github(
        df_updated,
        f"Add 5Whys analysis {record.analysis_id}"
    )

    return {
        "status": "success",
        "analysis_id": record.analysis_id,
        "commit_sha": commit_sha
    }


# =====================================================
# ❤️ HEALTHCHECK
# =====================================================

@app.get("/")
def root():
    return {
        "status": "Manufacturing AI API running",
        "environment": "Render Ready",
        "datasets_available": list(CSV_FILES.keys())
    }
