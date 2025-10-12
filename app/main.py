# main.py

import os
import json
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from typing import Optional, Tuple, Any

# Nombre de la hoja de cálculo en Google Sheets (¡Asegúrate de que este nombre sea correcto!)
NOMBRE_DEL_SHEET = 'Datos_Usuarios_IA'

# -----------------------------------------------------------
# PASO 1: AUTENTICACIÓN SEGURA (Código proporcionado por el usuario)
# -----------------------------------------------------------

def conectar_sheets():
    """Establece la conexión con Google Sheets usando GitHub Secrets."""
    creds_json_str = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
    
    if not creds_json_str:
        print("ERROR: La variable de entorno 'GCP_SERVICE_ACCOUNT_JSON' no está configurada.")
        return None
        
    try:
        creds_info = json.loads(creds_json_str)
        SCOPE = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPE)
        client = gspread.authorize(creds)
        
        print("Conexión a Google Sheets exitosa y segura.")
        return client
        
    except Exception as e:
        print(f"Error al conectar con Google Sheets: {e}")
        return None

# -----------------------------------------------------------
# PASO 2: LECTURA DE DATOS (Simula la operación GET)
# -----------------------------------------------------------

def obtener_datos(client: gspread.Client, nombre_hoja: str) -> Tuple[Optional[gspread.Worksheet], Optional[pd.DataFrame]]:
    """
    Abre la hoja de cálculo y retorna el objeto Worksheet y un DataFrame de Pandas.
    Simula una operación GET para obtener todos los registros.
    """
    try:
        # Abre la hoja de cálculo por su nombre
        spreadsheet = client.open(nombre_hoja)
        # Selecciona la primera pestaña (Worksheet). Si tienes varias, usa spreadsheet.worksheet("NombreDeLaPestaña")
        worksheet = spreadsheet.sheet1 
        
        # Obtiene todos los registros como una lista de diccionarios (usa la cabecera como claves)
        data = worksheet.get_all_records()
        
        # Opcional: convertir a DataFrame de Pandas para manipulación y filtrado por la IA
        df = pd.DataFrame(data)
        
        print(f"Datos leídos. Total de registros (filas de datos): {len(df)}")
        return worksheet, df
        
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"ERROR: Hoja de cálculo '{nombre_hoja}' no encontrada o no compartida.")
        return None, None
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return None, None

# -----------------------------------------------------------
# PASO 3: ACTUALIZACIÓN DE DATOS (Simula la operación PUT/PATCH)
# -----------------------------------------------------------

def actualizar_dato(worksheet: gspread.Worksheet, num_registro: int, nombre_columna: str, nuevo_valor: Any) -> bool:
    """
    Actualiza una celda específica en la hoja de cálculo.
    Simula una operación PUT/PATCH para modificar un recurso (registro).
    
    :param worksheet: Objeto de la pestaña de Google Sheets.
    :param num_registro: El 'num' (ID del registro, empezando en 451).
    :param nombre_columna: El nombre de la columna a actualizar (ej. 'RequestedTimeOff').
    :param nuevo_valor: El nuevo valor a colocar.
    :return: True si la actualización fue exitosa, False en caso contrario.
    """
    try:
        # Obtener los encabezados (fila 1 de la hoja) para encontrar la columna
        headers = worksheet.row_values(1)
        
        # 1. Encontrar el índice (columna)
        if nombre_columna not in headers:
            print(f"ERROR: Columna '{nombre_columna}' no encontrada en la hoja.")
            return False
        # gspread usa índice 1 basado (Columna A es 1, B es 2, etc.)
        col_index = headers.index(nombre_columna) + 1
        
        # 2. Encontrar la fila (buscando por 'num')
        # Buscamos el valor del 'num' en la primera columna (Columna 'num')
        col_num_values = worksheet.col_values(1)
        
        # La Fila 1 es el encabezado, por eso buscamos desde el índice 1 (fila 2 de Sheets)
        # La fila en Sheets es (índice_en_lista + 1)
        try:
            # Convertimos el ID a string, porque col_values devuelve strings
            target_row_index = col_num_values.index(str(num_registro))
            # gspread es índice 1-basado. Si el ID se encuentra en el índice 1 de Python, es la Fila 2 de Sheets.
            sheet_row_number = target_row_index + 1
        except ValueError:
            print(f"ERROR: Registro con 'num'={num_registro} no encontrado en la base de datos.")
            return False

        # 3. Actualizar la celda
        worksheet.update_cell(sheet_row_number, col_index, nuevo_valor)
        print(f"Actualización exitosa: ID={num_registro}, Columna='{nombre_columna}' actualizada a: {nuevo_valor}")
        return True
        
    except Exception as e:
        print(f"Error al actualizar la celda: {e}")
        return False

# -----------------------------------------------------------
# LÓGICA PRINCIPAL DE INTERACCIÓN CON EL AGENTE DE IA
# -----------------------------------------------------------

if __name__ == "__main__":
    
    # 1. Conectar de forma segura
    gspread_client = conectar_sheets()
    
    if gspread_client:
        # 2. Obtener datos y el objeto Worksheet
        hoja_trabajo, datos_df = obtener_datos(gspread_client, NOMBRE_DEL_SHEET)
        
        if hoja_trabajo is not None and datos_df is not None:
            print("\n--- Simulación de Agente de IA (OPEN API) ---")
            
            # =================================================================
            # PASO 4: INTERACCIÓN CON EL AGENTE DE IA
            # =================================================================
            
            # A. Lógica para VISUALIZAR DATOS (Simulando un GET)
            # El agente consulta los datos para tomar una decisión.
            
            # Ejemplo: Buscar datos del usuario con 'num'=451 (Daniel Anderson)
            user_id_to_check = 451
            user_data = datos_df[datos_df['num'] == user_id_to_check].to_dict('records')
            
            if user_data:
                print(f"\n[GET - Consulta de la IA]: Datos de usuario {user_id_to_check}:")
                print(user_data[0])
                
                # B. Lógica de DECISIÓN de la IA (Ejemplo)
                # La IA determina que 'RequestedTimeOff' debe cambiar de 10 a 18 días.
                nuevo_valor_ia = 18 
                
                # C. Lógica para MODIFICAR DATOS (Simulando un PUT/PATCH)
                # El agente usa la función para escribir el cambio en la hoja.
                print(f"\n[PUT - Acción de la IA]: Solicitando cambio de RequestedTimeOff para ID {user_id_to_check} a {nuevo_valor_ia}.")
                
                actualizacion_exitosa = actualizar_dato(
                    worksheet=hoja_trabajo,
                    num_registro=user_id_to_check,
                    nombre_columna='RequestedTimeOff',
                    nuevo_valor=nuevo_valor_ia
                )
                
                if actualizacion_exitosa:
                    print("La actualización fue registrada en Google Sheets.")
                
            else:
                print(f"Usuario con ID {user_id_to_check} no encontrado para la simulación.")
            
            print("\n--- Proceso Completado ---")
