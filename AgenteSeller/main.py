
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
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
GITHUB_REPO = "Arnulfo-Cavazos/OPENAPIsMAIN" # Ajusta en Render
PRODUCTS_PATH = "att_wifi_products.csv"  # Archivo local             # Archivo en GitHub
VENTAS_PATH = "AgenteSeller/Ventas.csv"


if not GITHUB_TOKEN or not GITHUB_REPO:
    raise RuntimeError("Faltan variables de entorno requeridas: GITHUB_TOKEN o GITHUB_REPO")

app = FastAPI(title="API de Productos AT&T y Ventas", version="1.0.0")

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
cache = {"ventas": None}

# ---------------------
# FUNCIONES AUXILIARES
# ---------------------
def load_csv_local(path: str):
    """Carga CSV local (productos)"""
    if not os.path.exists(path):
        raise HTTPException(status_code=500, detail=f"Archivo local {path} no encontrado.")
    return pd.read_csv(path)

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

def save_csv_to_repo(df, path: str, message="Actualización de Ventas"):
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
class VentaEntrada(BaseModel):
    nombre_completo: str
    telefono: str
    correo_electronico: EmailStr
    direccion: str
    producto: str  # Puede ser Product_ID o nombre

# ---------------------
# ENDPOINTS
# ---------------------
@app.get("/")
def home():
    return {"status": "API de Productos y Ventas operativa 🚀"}

# 1️⃣ Listar productos
@app.get("/productos/")
def listar_productos():
    df = load_csv_local(PRODUCTS_PATH)
    return df.to_dict(orient="records")

# 2️⃣ Buscar producto por ID o nombre
@app.get("/productos/{query}")
def buscar_producto(query: str):
    df = load_csv_local(PRODUCTS_PATH)
    resultado = df[(df["Product_ID"].astype(str).str.lower() == query.lower()) |
                   (df["Product_Name"].str.lower().str.contains(query.lower()))]
    if resultado.empty:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    return resultado.to_dict(orient="records")

# 3️⃣ Listar ventas
@app.get("/ventas/")
def listar_ventas():
    df = load_csv_from_repo(VENTAS_PATH, "ventas")
    return df.to_dict(orient="records")

# 4️⃣ Agregar nueva venta
@app.post("/ventas/agregar")
def agregar_venta(venta: VentaEntrada):
    # Validar producto
    df_prod = load_csv_local(PRODUCTS_PATH)
    producto_match = df_prod[(df_prod["Product_ID"].astype(str).str.lower() == venta.producto.lower()) |
                             (df_prod["Product_Name"].str.lower().str.contains(venta.producto.lower()))]
    if producto_match.empty:
        raise HTTPException(status_code=400, detail="Producto no encontrado en catálogo.")

    # Cargar ventas desde GitHub
    df_ventas = load_csv_from_repo(VENTAS_PATH, "ventas")
    nueva_fila = pd.DataFrame([{
        "Nombre completo": venta.nombre_completo,
        "Teléfono": venta.telefono,
        "Correo electrónico": venta.correo_electronico,
        "Dirección": venta.direccion,
        "Producto": producto_match.iloc[0]["Product_Name"]
    }])
    df_ventas = pd.concat([df_ventas, nueva_fila], ignore_index=True)
    save_csv_to_repo(df_ventas, VENTAS_PATH, f"Agregada venta de {venta.nombre_completo}")
    return {"mensaje": "Venta agregada y commit realizado con éxito ✅", "venta": venta.dict()}
