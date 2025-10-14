# main.py

from fastapi import FastAPI, HTTPException
from typing import List, Optional, Dict, Any
import pandas as pd
import os

# ----------------------------------------------------
# 1. Configuración y Carga de Datos
# ----------------------------------------------------

# Nombre del archivo de datos (basado en la imagen)
DATA_FILE = "users_data_2_test.csv"

# Inicializar el DataFrame
df: Optional[pd.DataFrame] = None

# Función para cargar los datos de forma segura
def load_data():
    global df
    data_path = os.path.join("data", DATA_FILE)
    if not os.path.exists(data_path):
        # Asumiendo que el archivo está en la carpeta 'data'
        raise FileNotFoundError(f"El archivo de datos no se encontró en: {data_path}")
    
    try:
        df = pd.read_csv(data_path)
        # Convertir el DataFrame a formato Python estándar para evitar errores de tipo
        df = df.astype(str)
        print(f"Datos cargados exitosamente desde {DATA_FILE}. Total de filas: {len(df)}")
    except Exception as e:
        print(f"Error al cargar el archivo CSV: {e}")
        df = None

# Cargar los datos al inicio de la aplicación
load_data()

# ----------------------------------------------------
# 2. Inicialización de FastAPI
# ----------------------------------------------------

app = FastAPI(
    title="Agente de Consulta de Datos de Usuarios",
    description="API que permite consultar información de usuarios del archivo users_data_2_test.csv."
)

# ----------------------------------------------------
# 3. Endpoints (Rutas de la API)
# ----------------------------------------------------

@app.get("/")
def read_root():
    """Endpoint de bienvenida."""
    return {"message": "Agente de Datos Operativo", "status": "Ready"}

# Endpoint para obtener todos los datos
@app.get("/users", response_model=List[Dict[str, Any]])
def get_all_users():
    """Retorna la lista completa de todos los usuarios."""
    if df is None:
        raise HTTPException(status_code=503, detail="Datos no disponibles. El archivo CSV no se pudo cargar.")
    
    # Retornar la lista de diccionarios (registros)
    return df.to_dict('records')


# Endpoint para buscar por nombre
@app.get("/users/search", response_model=List[Dict[str, Any]])
def search_users_by_name(name: str):
    """
    Busca usuarios cuyo nombre contenga el texto proporcionado (búsqueda parcial e insensible a mayúsculas/minúsculas).
    """
    if df is None:
        raise HTTPException(status_code=503, detail="Datos no disponibles. El archivo CSV no se pudo cargar.")

    # Asegurarse de que la columna 'Name' es una cadena y realizar la búsqueda
    # Usando .str.contains para búsqueda parcial, y case=False para ser insensible a mayúsculas/minúsculas
    results = df[df['Name'].astype(str).str.contains(name, case=False, na=False)]
    
    if results.empty:
        raise HTTPException(status_code=404, detail=f"No se encontraron usuarios con el nombre que contenga: '{name}'")
        
    return results.to_dict('records')


# Endpoint para obtener un registro específico por número 'num'
@app.get("/users/{num}", response_model=Dict[str, Any])
def get_user_by_num(num: int):
    """
    Retorna la información de un usuario específico usando su número de índice ('num').
    """
    if df is None:
        raise HTTPException(status_code=503, detail="Datos no disponibles. El archivo CSV no se pudo cargar.")

    # Buscar el registro donde la columna 'num' coincida con el valor.
    # Es necesario convertir la columna 'num' a entero o string para la comparación.
    try:
        user_record = df[df['num'].astype(int) == num].to_dict('records')
    except ValueError:
        # En caso de que la conversión falle, tratar la columna como string
        user_record = df[df['num'].astype(str) == str(num)].to_dict('records')

    if not user_record:
        raise HTTPException(status_code=404, detail=f"Usuario con número '{num}' no encontrado.")
        
    # Retornar el primer (y único) resultado
    return user_record[0]
