from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from github import Github
import os
from dotenv import load_dotenv
import logging
from io import StringIO

# ---------------------
# CONFIGURACIÓN
# ---------------------
logging.basicConfig(level=logging.INFO)
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "Arnulfo-Cavazos/OPENAPIsMAIN"
PATH_INVENTARIO = "SupplyChain/INVENTARIODB.csv"
PATH_TRANSITO = "SupplyChain/Inventario_transit.csv"
PATH_ORDENES = "SupplyChain/OrdenDeSurtido.csv"


if not GITHUB_TOKEN or not GITHUB_REPO:
    raise RuntimeError("Faltan variables de entorno requeridas: GITHUB_TOKEN o GITHUB_REPO")

app = FastAPI(title="API de Inventario y Órdenes", version="1.0.0")

# ---------------------
# CONEXIÓN GITHUB
# ---------------------
try:
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPO)
except Exception as e:
    logging.error(f"Error inicializando conexión con GitHub: {e}")
    raise RuntimeError("No se pudo inicializar GitHub")

# ---------------------
# CACHE LOCAL
# ---------------------
cache = {"inventario": None, "transito": None, "ordenes": None}

# ---------------------
# FUNCIONES AUXILIARES
# ---------------------
def load_csv_from_repo(path: str, cache_key: str):
    """Carga CSV desde GitHub y lo guarda temporalmente en cache"""
    if cache[cache_key] is not None:
        return cache[cache_key].copy()
    try:
        logging.info(f"Cargando {path} desde GitHub...")
        contents = repo.get_contents(path, ref="main")
        csv_data = contents.decoded_content.decode("utf-8")
        df = pd.read_csv(StringIO(csv_data))
        cache[cache_key] = df.copy()
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar {path}: {e}")

def save_csv_to_repo(df, path: str, message="Actualización de CSV"):
    """Guarda el CSV actualizado en el repositorio con commit"""
    try:
        csv_buffer = df.to_csv(index=False)
        contents = repo.get_contents(path, ref="main")
        repo.update_file(path, message, csv_buffer, contents.sha, branch="main")
        cache[path] = df.copy()
        logging.info(f"Archivo {path} actualizado y enviado a GitHub.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo guardar {path}: {e}")

# ---------------------
# MODELOS DE DATOS
# ---------------------
class OrdenEntrada(BaseModel):
    Numero_de_Parte: str
    Descripcion: str
    Cantidad: int
    Tipo_Envio: str

# ---------------------
# ENDPOINTS
# ---------------------
@app.get("/")
def home():
    return {"status": "API de Inventario operativa 🚀"}

# 1️⃣ Inventario (solo lectura)
@app.get("/inventario/{numero_parte}")
def obtener_inventario(numero_parte: str):
    df = load_csv_from_repo(PATH_INVENTARIO, "inventario")
    resultado = df[df["Número de Parte"].astype(str) == numero_parte]
    if resultado.empty:
        raise HTTPException(status_code=404, detail="Número de parte no encontrado en inventario.")
    return resultado.to_dict(orient="records")

# 2️⃣ Tránsito (solo lectura)
@app.get("/transito/{numero_parte}")
def obtener_transito(numero_parte: str):
    df = load_csv_from_repo(PATH_TRANSITO, "transito")
    resultado = df[df["Número de Parte"].astype(str) == numero_parte]
    if resultado.empty:
        raise HTTPException(status_code=404, detail="Número de parte no encontrado en tránsito.")
    return resultado.to_dict(orient="records")

# 3️⃣ Órdenes - listar todas
@app.get("/ordenes/")
def listar_ordenes():
    df = load_csv_from_repo(PATH_ORDENES, "ordenes")
    return df.to_dict(orient="records")

# 4️⃣ Agregar nueva orden (escritura)
@app.post("/ordenes/agregar")
def agregar_orden(orden: OrdenEntrada):
    df = load_csv_from_repo(PATH_ORDENES, "ordenes")
    nueva_fila = pd.DataFrame([orden.dict()])
    df = pd.concat([df, nueva_fila], ignore_index=True)
    save_csv_to_repo(df, PATH_ORDENES, f"Agregada orden {orden.Numero_de_Parte}")
    return {"mensaje": "Orden agregada y commit realizado con éxito ✅", "orden": orden.dict()}

# 5️⃣ Crear orden automática (a partir de tránsito)
@app.post("/crear_orden_automatica/{numero_parte}")
def crear_orden_automatica(numero_parte: str):
    df_inv = load_csv_from_repo(PATH_INVENTARIO, "inventario")
    df_trans = load_csv_from_repo(PATH_TRANSITO, "transito")
    df_ordenes = load_csv_from_repo(PATH_ORDENES, "ordenes")

    inv_f = df_inv[df_inv["Número de Parte"].astype(str) == numero_parte]
    trans_f = df_trans[df_trans["Número de Parte"].astype(str) == numero_parte]

    if inv_f.empty or trans_f.empty:
        raise HTTPException(status_code=404, detail="El número de parte no se encontró en ambas bases.")

    total_transito = trans_f["Cantidad Enviada"].sum()
    descripcion = inv_f.iloc[0]["Descripción"]

    orden_auto = {
        "Numero_de_Parte": numero_parte,
        "Descripcion": descripcion,
        "Cantidad": int(total_transito),
        "Tipo_Envio": "Automático"
    }

    df_ordenes = pd.concat([df_ordenes, pd.DataFrame([orden_auto])], ignore_index=True)
    save_csv_to_repo(df_ordenes, PATH_ORDENES, f"Orden automática creada para {numero_parte}")

    return {"mensaje": f"Orden automática creada y enviada al repo GitHub para {numero_parte}", "orden": orden_auto}
