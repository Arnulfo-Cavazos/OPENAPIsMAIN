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
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# =====================================================
# 📁 ARCHIVOS LOCALES
# =====================================================

CSV_FILES = {
    "bom": "BillOfMaterials.csv",
    "downtime": "DownTimes.csv",
    "production": "OrdenesDeProduccion.csv",
    "5whys": "5whys.csv"
}

# =====================================================
# 📘 GUÍA SEMÁNTICA PARA AGENTE IA
# =====================================================

DATASET_GUIDE = {
    "bom": {
        "description": "Bill of Materials por orden de producción",
        "key_columns": ["order_id", "Part Number", "parent_product"],
        "columns": {
            "order_id": "ID de la orden",
            "parent_product": "Producto ensamblado",
            "Part Number": "Número de parte del componente",
            "component_description": "Descripción del componente",
            "quantity_required": "Cantidad requerida",
            "quantity_issued": "Cantidad liberada",
            "quantity_consumed": "Cantidad consumida",
            "unit": "Unidad",
            "status": "Estado del material"
        }
    },
    "downtime": {
        "description": "Eventos de paro en producción",
        "key_columns": ["downtime_id", "order_id", "machine_id"],
        "columns": {}
    },
    "production": {
        "description": "Órdenes de producción",
        "key_columns": ["order_id", "product_id", "status"],
        "columns": {}
    },
    "5whys": {
        "description": "Análisis causa raíz",
        "key_columns": ["analysis_id", "related_event_id"],
        "columns": {}
    }
}

# =====================================================
# 📥 CARGAR CSV LOCAL
# =====================================================

def load_csv(dataset: str) -> pd.DataFrame:
    file_path = CSV_FILES.get(dataset)

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset no encontrado")

    return pd.read_csv(file_path)


# =====================================================
# 📘 ENDPOINT GUÍA
# =====================================================

@app.get("/datasets/guide")
def get_guide():
    return DATASET_GUIDE


# =====================================================
# 🔎 CONSULTA DINÁMICA
# =====================================================

@app.get("/data/{dataset}")
def query_data(
    dataset: str,
    column: Optional[str] = Query(None),
    value: Optional[str] = Query(None),
    exact: Optional[bool] = Query(False)
):

    if dataset not in CSV_FILES:
        raise HTTPException(status_code=400, detail="Dataset inválido")

    df = load_csv(dataset)

    if column and value:
        if column not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Columna inválida. Columnas disponibles: {list(df.columns)}"
            )

        if exact:
            df = df[df[column].astype(str) == value]
        else:
            df = df[df[column].astype(str).str.contains(value, case=False, na=False)]

    return {
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

    df_filtered = df[df["Part Number"].astype(str).str.upper() == part_number.upper()]

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
# 📤 COMMIT A GITHUB
# =====================================================

def commit_5whys_to_github(df: pd.DataFrame, message: str):

    if not all([GITHUB_TOKEN, GITHUB_REPO]):
        raise HTTPException(status_code=500, detail="GitHub no configurado")

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CSV_5WHYS_PATH}"

    # Obtener SHA actual
    get_resp = requests.get(url, headers=HEADERS)
    if get_resp.status_code != 200:
        raise HTTPException(status_code=500, detail="No se pudo obtener SHA")

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
        raise HTTPException(status_code=500, detail="Error haciendo commit")

    return put_resp.json()["commit"]["sha"]


# =====================================================
# ✏️ AGREGAR 5WHYS + COMMIT
# =====================================================

@app.post("/5whys/add")
def add_5whys(record: FiveWhysModel):

    df = load_csv("5whys")
    new_row = pd.DataFrame([record.dict()])
    df = pd.concat([df, new_row], ignore_index=True)

    # Guardar local
    df.to_csv("5whys.csv", index=False)

    # Commit GitHub
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
    return {"status": "Manufacturing AI API running"}
