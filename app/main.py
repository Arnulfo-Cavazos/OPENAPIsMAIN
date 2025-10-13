# Archivo: app/main.py

import os
import json
from typing import Optional, Tuple, Any, List

# Dependencias de GSpread y Pandas
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# Dependencias de FastAPI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# --- CONFIGURACIÓN GLOBAL ---
NOMBRE_DEL_SHEET = 'Datos_Usuarios_IA'
# La conexión se intentará una vez al iniciar el servidor
gspread_client: Optional[gspread.Client] = None

# --- DEFINICIÓN DE MODELOS (Basado en la especificación OpenAPI) ---

class User(BaseModel):
    """Esquema de un registro de usuario."""
    num: int = Field(..., description="ID único del registro.")
    Name: str = Field(..., description="Nombre completo del empleado.")
    Job: str = Field(..., description="Puesto de trabajo.")
    Address: str = Field(..., description="Dirección física.")
    RequestedTimeOff: int = Field(..., description="Cantidad de días libres solicitados.")
    
class UserUpdate(BaseModel):
    """Esquema para la actualización de un solo campo."""
    column_name: str = Field(..., description="Nombre de la columna a modificar (ej. 'RequestedTimeOff').")
    new_value: str = Field(..., description="El nuevo valor a asignar. Se usa string por la flexibilidad de gspread.")


# --- INICIALIZACIÓN DE LA APLICACIÓN ASGI ---
# ESTA LÍNEA ES LA CLAVE PARA RESOLVER SU ERROR
app = FastAPI(
    title="Google Sheets Data API para Agente IA",
    description="API para leer y actualizar los datos de recursos humanos.",
    version="1.0.0"
)

# --- FUNCIONES DE ACCESO A GOOGLE SHEETS (Migradas de su código original) ---

def conectar_sheets() -> Optional[gspread.Client]:
    """Establece la conexión con Google Sheets usando GitHub Secrets."""
    global gspread_client
    creds_json_str = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
    
    if not creds_json_str:
        print("ERROR: La variable de entorno 'GCP_SERVICE_ACCOUNT_JSON' no está configurada.")
        return None
        
    try:
        creds_info = json.loads(creds_json_str)
        SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPE)
        gspread_client = gspread.authorize(creds)
        print("Conexión a Google Sheets exitosa.")
        return gspread_client
    except Exception as e:
        print(f"Error al conectar con Google Sheets: {e}")
        return None

def obtener_datos(client: gspread.Client, nombre_hoja: str) -> Tuple[Optional[gspread.Worksheet], Optional[pd.DataFrame]]:
    """Abre la hoja de cálculo y retorna el objeto Worksheet y un DataFrame."""
    try:
        spreadsheet = client.open(nombre_hoja)
        worksheet = spreadsheet.sheet1 
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        return worksheet, df
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return None, None

def actualizar_dato(worksheet: gspread.Worksheet, num_registro: int, nombre_columna: str, nuevo_valor: Any) -> bool:
    """Actualiza una celda específica en la hoja de cálculo."""
    try:
        headers = worksheet.row_values(1)
        
        # 1. Encontrar la columna
        if nombre_columna not in headers:
            print(f"ERROR: Columna '{nombre_columna}' no encontrada.")
            return False
        col_index = headers.index(nombre_columna) + 1
        
        # 2. Encontrar la fila (buscando por 'num')
        col_num_values = worksheet.col_values(1)
        try:
            target_row_index = col_num_values.index(str(num_registro))
            sheet_row_number = target_row_index + 1
        except ValueError:
            print(f"ERROR: Registro con 'num'={num_registro} no encontrado.")
            return False

        # 3. Actualizar la celda
        worksheet.update_cell(sheet_row_number, col_index, nuevo_valor)
        print(f"Actualización exitosa: ID={num_registro}, Columna='{nombre_columna}' actualizada a: {nuevo_valor}")
        return True
        
    except Exception as e:
        print(f"Error al actualizar la celda: {e}")
        return False

# --- EVENTO DE INICIO DEL SERVIDOR ---

@app.on_event("startup")
async def startup_event():
    """Intenta conectar con Google Sheets al iniciar la aplicación."""
    global gspread_client
    if gspread_client is None:
        conectar_sheets()
        if gspread_client is None:
            # Si falla la conexión, la API no podrá operar con los datos
            print("ADVERTENCIA: La aplicación está iniciada, pero no pudo conectar con Google Sheets.")

# --- ENDPOINTS DE LA API (Implementación de la especificación OpenAPI) ---

@app.get("/users", response_model=List[User], summary="Obtener todos los registros de usuarios.")
async def read_users():
    """Implementa el GET /users para que la IA visualice los datos."""
    if gspread_client is None:
        raise HTTPException(status_code=500, detail="Error de conexión con Google Sheets. Revise credenciales.")
    
    worksheet, datos_df = obtener_datos(gspread_client, NOMBRE_DEL_SHEET)
    
    if datos_df is None:
        raise HTTPException(status_code=500, detail="Error al leer los datos de la hoja.")

    # Convertir el DataFrame a una lista de diccionarios, luego a los modelos Pydantic
    return datos_df.to_dict('records')


@app.patch("/users/{user_id}", summary="Actualizar un campo específico de un usuario.")
async def update_user_field(user_id: int, update_data: UserUpdate):
    """Implementa el PATCH /users/{user_id} para que la IA modifique un campo."""
    if gspread_client is None:
        raise HTTPException(status_code=500, detail="Error de conexión con Google Sheets.")
    
    # Necesitamos el Worksheet para la actualización
    worksheet, _ = obtener_datos(gspread_client, NOMBRE_DEL_SHEET)
    
    if worksheet is None:
        raise HTTPException(status_code=500, detail="No se pudo obtener la hoja de trabajo.")
        
    # Llamar a la función de actualización
    success = actualizar_dato(
        worksheet=worksheet,
        num_registro=user_id,
        nombre_columna=update_data.column_name,
        nuevo_valor=update_data.new_value
    )
    
    if success:
        return {"message": f"Actualización exitosa: ID={user_id}, Columna='{update_data.column_name}' actualizada a: {update_data.new_value}"}
    else:
        # La función actualizar_dato ya imprime el error específico
        raise HTTPException(status_code=404, detail=f"No se pudo actualizar el registro {user_id}. Verifique si el ID o el nombre de la columna son correctos.")
