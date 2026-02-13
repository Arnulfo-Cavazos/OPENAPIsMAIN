from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from datetime import datetime, timedelta
import os

app = FastAPI(
    title="Agente de Producción MES API",
    description="API para monitoreo de producción en tiempo real, análisis de desviaciones y recomendaciones operativas",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class OrdenProduccionQuery(BaseModel):
    orden_id: Optional[str] = None
    linea: Optional[str] = None
    estado: Optional[str] = None

class AnalisisTurnoQuery(BaseModel):
    linea: str
    turno: int
    fecha: Optional[str] = None

class MaterialFaltanteQuery(BaseModel):
    orden_id: str

# Funciones auxiliares
def load_excel_data(filename: str) -> pd.DataFrame:
    """Carga datos desde archivo Excel"""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    return pd.read_excel(filepath)

def calculate_oee(disponibilidad: float, performance: float, calidad: float) -> float:
    """Calcula OEE (Overall Equipment Effectiveness)"""
    return round(disponibilidad * performance * calidad, 2)

def calculate_desviacion_output(real: int, objetivo: int) -> dict:
    """Calcula desviación de output"""
    desviacion = real - objetivo
    porcentaje = round((desviacion / objetivo * 100), 1) if objetivo > 0 else 0
    return {
        "real": real,
        "objetivo": objetivo,
        "desviacion": desviacion,
        "porcentaje": porcentaje
    }

def analizar_causas_raiz(df_downtime, df_scrap, tiempo_ciclo_real, tiempo_ciclo_std):
    """Analiza causas raíz de desviaciones"""
    causas = []
    
    # Analizar downtime
    if not df_downtime.empty:
        total_downtime = df_downtime['Duracion_Minutos'].sum()
        if total_downtime > 30:
            for _, row in df_downtime.iterrows():
                impacto = (row['Duracion_Minutos'] / total_downtime) * 100
                causas.append({
                    "categoria": "DOWNTIME",
                    "descripcion": row['Causa'],
                    "duracion_minutos": row['Duracion_Minutos'],
                    "impacto_porcentaje": round(impacto, 1),
                    "unidades_perdidas": row['Unidades_Perdidas']
                })
    
    # Analizar tiempo ciclo
    if tiempo_ciclo_real > tiempo_ciclo_std * 1.1:
        incremento = ((tiempo_ciclo_real - tiempo_ciclo_std) / tiempo_ciclo_std) * 100
        causas.append({
            "categoria": "TIEMPO_CICLO_ELEVADO",
            "descripcion": f"Tiempo ciclo {round(incremento, 1)}% sobre estándar",
            "tiempo_real": tiempo_ciclo_real,
            "tiempo_estandar": tiempo_ciclo_std,
            "impacto_porcentaje": 20
        })
    
    # Analizar scrap
    if not df_scrap.empty:
        total_scrap = df_scrap['Cantidad'].sum()
        if total_scrap > 0:
            causas.append({
                "categoria": "SCRAP_ELEVADO",
                "descripcion": "Scrap por encima del estándar",
                "unidades_rechazadas": int(total_scrap),
                "impacto_porcentaje": 10
            })
    
    return causas

# Endpoints
@app.get("/")
def read_root():
    return {
        "message": "API Agente de Producción MES",
        "version": "1.0.0",
        "endpoints": [
            "/ordenes-produccion/list",
            "/ordenes-produccion/activas",
            "/produccion-actual",
            "/analisis-turno",
            "/consumo-materiales",
            "/downtime/list",
            "/scrap/list",
            "/oee/calcular",
            "/material-faltante"
        ]
    }

@app.get("/ordenes-produccion/list")
def list_ordenes_produccion():
    """Lista todas las órdenes de producción"""
    try:
        df = load_excel_data("datos_ordenes_produccion.xlsx")
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar órdenes: {str(e)}")

@app.get("/ordenes-produccion/activas")
def get_ordenes_activas():
    """Obtiene órdenes de producción activas"""
    try:
        df = load_excel_data("datos_ordenes_produccion.xlsx")
        df_activas = df[df['Estado'].isin(['En Proceso', 'Iniciada'])]
        return df_activas.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/produccion-actual")
def get_produccion_actual():
    """Obtiene estado actual de producción en todas las líneas"""
    try:
        df_ordenes = load_excel_data("datos_ordenes_produccion.xlsx")
        df_lineas = load_excel_data("datos_estado_lineas.xlsx")
        
        # Combinar información
        resultado = []
        for _, linea in df_lineas.iterrows():
            orden_actual = df_ordenes[
                (df_ordenes['Linea'] == linea['Linea']) & 
                (df_ordenes['Estado'] == 'En Proceso')
            ]
            
            if not orden_actual.empty:
                orden = orden_actual.iloc[0]
                resultado.append({
                    "linea": linea['Linea'],
                    "estado": linea['Estado'],
                    "orden_id": orden['Orden_ID'],
                    "producto": orden['Producto'],
                    "cantidad_objetivo": orden['Cantidad_Objetivo'],
                    "cantidad_producida": orden['Cantidad_Producida'],
                    "porcentaje_completado": round((orden['Cantidad_Producida'] / orden['Cantidad_Objetivo']) * 100, 1),
                    "turno_actual": linea['Turno_Actual'],
                    "operadores": linea['Operadores_Asignados'],
                    "tiempo_ciclo_actual": linea['Tiempo_Ciclo_Actual'],
                    "oee_actual": linea['OEE_Actual']
                })
            else:
                resultado.append({
                    "linea": linea['Linea'],
                    "estado": linea['Estado'],
                    "orden_id": None,
                    "mensaje": "Sin orden activa"
                })
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/analisis-turno")
def analizar_turno(query: AnalisisTurnoQuery):
    """Analiza desviaciones y causas raíz de un turno específico"""
    try:
        df_ordenes = load_excel_data("datos_ordenes_produccion.xlsx")
        df_downtime = load_excel_data("datos_downtime.xlsx")
        df_scrap = load_excel_data("datos_scrap.xlsx")
        df_lineas = load_excel_data("datos_estado_lineas.xlsx")
        
        # Filtrar por línea y turno
        linea_info = df_lineas[df_lineas['Linea'] == query.linea]
        if linea_info.empty:
            raise HTTPException(status_code=404, detail="Línea no encontrada")
        
        linea_info = linea_info.iloc[0]
        
        # Obtener orden activa
        orden = df_ordenes[
            (df_ordenes['Linea'] == query.linea) & 
            (df_ordenes['Estado'] == 'En Proceso')
        ]
        
        if orden.empty:
            return {"mensaje": "No hay orden activa en esta línea"}
        
        orden = orden.iloc[0]
        
        # Calcular desviación
        desviacion = calculate_desviacion_output(
            orden['Cantidad_Producida'],
            orden['Cantidad_Objetivo']
        )
        
        # Filtrar downtime y scrap de la línea
        downtime_linea = df_downtime[df_downtime['Linea'] == query.linea]
        scrap_linea = df_scrap[df_scrap['Linea'] == query.linea]
        
        # Analizar causas raíz
        causas = analizar_causas_raiz(
            downtime_linea,
            scrap_linea,
            linea_info['Tiempo_Ciclo_Actual'],
            linea_info['Tiempo_Ciclo_Estandar']
        )
        
        # Generar recomendaciones
        recomendaciones = []
        if desviacion['porcentaje'] < -10:
            recomendaciones.append("URGENTE: Investigar causas de bajo rendimiento")
        if not downtime_linea.empty and downtime_linea['Duracion_Minutos'].sum() > 30:
            recomendaciones.append("Revisar disponibilidad de materiales para próximo turno")
        if linea_info['Tiempo_Ciclo_Actual'] > linea_info['Tiempo_Ciclo_Estandar'] * 1.15:
            recomendaciones.append("Considerar entrenamiento adicional para operadores")
        
        return {
            "linea": query.linea,
            "turno": query.turno,
            "orden_id": orden['Orden_ID'],
            "producto": orden['Producto'],
            "desviacion_output": desviacion,
            "oee_turno": linea_info['OEE_Actual'],
            "causas_raiz": causas,
            "recomendaciones": recomendaciones,
            "downtime_total_minutos": downtime_linea['Duracion_Minutos'].sum() if not downtime_linea.empty else 0,
            "scrap_total_unidades": scrap_linea['Cantidad'].sum() if not scrap_linea.empty else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")

@app.get("/consumo-materiales/{orden_id}")
def get_consumo_materiales(orden_id: str):
    """Obtiene consumo de materiales vs BOM para una orden"""
    try:
        df = load_excel_data("datos_consumo_materiales.xlsx")
        consumo = df[df['Orden_ID'] == orden_id]
        
        if consumo.empty:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        
        return consumo.to_dict(orient="records")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/material-faltante")
def get_material_faltante(query: MaterialFaltanteQuery):
    """Identifica materiales faltantes para completar una orden"""
    try:
        df_consumo = load_excel_data("datos_consumo_materiales.xlsx")
        df_ordenes = load_excel_data("datos_ordenes_produccion.xlsx")
        
        # Obtener orden
        orden = df_ordenes[df_ordenes['Orden_ID'] == query.orden_id]
        if orden.empty:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        
        orden = orden.iloc[0]
        
        # Obtener consumo
        consumo = df_consumo[df_consumo['Orden_ID'] == query.orden_id]
        
        # Calcular faltantes
        faltantes = []
        for _, row in consumo.iterrows():
            cantidad_restante = orden['Cantidad_Objetivo'] - orden['Cantidad_Producida']
            material_necesario = (row['Cantidad_BOM'] * cantidad_restante)
            material_disponible = row['Inventario_Disponible']
            
            if material_disponible < material_necesario:
                faltante = material_necesario - material_disponible
                horas_disponibles = (material_disponible / row['Cantidad_BOM']) / (orden['Cantidad_Objetivo'] / 8)  # Asumiendo 8 horas
                
                faltantes.append({
                    "material": row['Material'],
                    "necesario": round(material_necesario, 2),
                    "disponible": material_disponible,
                    "faltante": round(faltante, 2),
                    "unidad": row['Unidad'],
                    "horas_disponibles": round(horas_disponibles, 1),
                    "criticidad": "CRÍTICO" if horas_disponibles < 2 else "ALTO" if horas_disponibles < 4 else "MEDIO"
                })
        
        return {
            "orden_id": query.orden_id,
            "producto": orden['Producto'],
            "cantidad_pendiente": orden['Cantidad_Objetivo'] - orden['Cantidad_Producida'],
            "materiales_faltantes": faltantes,
            "total_faltantes": len(faltantes)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/downtime/list")
def list_downtime():
    """Lista todos los eventos de downtime"""
    try:
        df = load_excel_data("datos_downtime.xlsx")
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/scrap/list")
def list_scrap():
    """Lista todos los eventos de scrap"""
    try:
        df = load_excel_data("datos_scrap.xlsx")
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/oee/calcular/{linea}")
def calcular_oee(linea: str):
    """Calcula OEE para una línea específica"""
    try:
        df_lineas = load_excel_data("datos_estado_lineas.xlsx")
        df_downtime = load_excel_data("datos_downtime.xlsx")
        df_scrap = load_excel_data("datos_scrap.xlsx")
        df_ordenes = load_excel_data("datos_ordenes_produccion.xlsx")
        
        linea_info = df_lineas[df_lineas['Linea'] == linea]
        if linea_info.empty:
            raise HTTPException(status_code=404, detail="Línea no encontrada")
        
        linea_info = linea_info.iloc[0]
        
        # Calcular disponibilidad
        tiempo_total = 480  # 8 horas en minutos
        downtime_total = df_downtime[df_downtime['Linea'] == linea]['Duracion_Minutos'].sum()
        disponibilidad = (tiempo_total - downtime_total) / tiempo_total
        
        # Calcular performance
        tiempo_ciclo_ideal = linea_info['Tiempo_Ciclo_Estandar']
        tiempo_ciclo_real = linea_info['Tiempo_Ciclo_Actual']
        performance = tiempo_ciclo_ideal / tiempo_ciclo_real if tiempo_ciclo_real > 0 else 0
        
        # Calcular calidad
        orden = df_ordenes[(df_ordenes['Linea'] == linea) & (df_ordenes['Estado'] == 'En Proceso')]
        if not orden.empty:
            orden = orden.iloc[0]
            scrap_total = df_scrap[df_scrap['Linea'] == linea]['Cantidad'].sum()
            total_producido = orden['Cantidad_Producida'] + scrap_total
            calidad = (total_producido - scrap_total) / total_producido if total_producido > 0 else 1
        else:
            calidad = 1
        
        oee = calculate_oee(disponibilidad, performance, calidad)
        
        return {
            "linea": linea,
            "oee": oee,
            "disponibilidad": round(disponibilidad, 3),
            "performance": round(performance, 3),
            "calidad": round(calidad, 3),
            "downtime_minutos": downtime_total,
            "tiempo_ciclo_real": tiempo_ciclo_real,
            "tiempo_ciclo_estandar": tiempo_ciclo_ideal
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/personal/asignado")
def get_personal_asignado():
    """Obtiene personal asignado por línea y turno"""
    try:
        df = load_excel_data("datos_personal.xlsx")
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Made with Bob
