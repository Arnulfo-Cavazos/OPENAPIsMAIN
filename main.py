"""
API FastAPI para el Sistema de Análisis de Importaciones
Agente de Inteligencia Aduanera
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import time
from datetime import datetime

from modules import (
    AnalizadorHistorial,
    AnalizadorValor,
    GestorAlertas,
    GeneradorChecklist
)

# Inicializar FastAPI
app = FastAPI(
    title="Sistema de Análisis de Importaciones",
    description="Agente de inteligencia aduanera para análisis de operaciones de importación",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar módulos
analizador_historial = AnalizadorHistorial()
analizador_valor = AnalizadorValor()
gestor_alertas = GestorAlertas()
generador_checklist = GeneradorChecklist()


# ============================================================================
# ENDPOINTS PRINCIPALES
# ============================================================================

@app.get("/")
def root():
    """Endpoint raíz con información del sistema"""
    return {
        "sistema": "Agente de Análisis de Importaciones",
        "version": "1.0.0",
        "modulos": [
            "Módulo 1: Historial del Importador",
            "Módulo 2: Valor de Referencia Internacional",
            "Módulo 3: Alertas Activas de Inteligencia",
            "Módulo 4: Checklist Regulatorio Personalizado"
        ],
        "endpoints": {
            "analisis_completo": "/api/analisis/completo",
            "historial": "/api/importador/{rfc}",
            "valor": "/api/valor/analizar",
            "alertas": "/api/alertas/buscar",
            "checklist": "/api/checklist/generar"
        }
    }


@app.get("/api/analisis/completo")
def analisis_completo(
    rfc: str = Query(..., description="RFC del importador"),
    fraccion: str = Query(..., description="Fracción arancelaria"),
    pais_origen: str = Query(..., description="País de origen"),
    valor_unitario: float = Query(..., gt=0, description="Valor unitario en USD"),
    cantidad: int = Query(1, gt=0, description="Cantidad de unidades"),
    proveedor_id: Optional[str] = Query(None, description="ID del proveedor")
):
    """
    ANÁLISIS COMPLETO - Ejecuta los 4 módulos en secuencia
    
    Este es el endpoint principal que un oficial aduanero usaría para
    obtener un análisis completo de una operación de importación.
    """
    inicio = time.time()
    
    try:
        # MÓDULO 1: Historial del Importador
        historial = analizador_historial.analizar_importador(rfc)
        
        if not historial.get("encontrado"):
            raise HTTPException(status_code=404, detail=f"RFC {rfc} no encontrado")
        
        # MÓDULO 2: Análisis de Valor
        analisis_valor = analizador_valor.analizar_valor(
            fraccion, pais_origen, valor_unitario, cantidad
        )
        
        # MÓDULO 3: Alertas Activas
        alertas = gestor_alertas.buscar_alertas_para_operacion(
            fraccion, pais_origen, proveedor_id
        )
        
        # MÓDULO 4: Checklist Regulatorio
        tipo_importador = "nuevo" if historial.get("anios_activo", 0) < 1 else "regular"
        primera_importacion = fraccion not in [f["fraccion"] for f in historial.get("fracciones_mas_usadas", [])]
        
        checklist = generador_checklist.generar_checklist(
            fraccion, pais_origen, tipo_importador, primera_importacion
        )
        
        # Determinar nivel de riesgo global
        nivel_riesgo_global = _determinar_riesgo_global(
            historial, analisis_valor, alertas
        )
        
        # Recomendar canal
        canal_recomendado = _recomendar_canal(
            nivel_riesgo_global, historial, analisis_valor, alertas, checklist
        )
        
        # Generar acciones inmediatas
        acciones = _generar_acciones_inmediatas(
            historial, analisis_valor, alertas, checklist
        )
        
        tiempo_procesamiento = (time.time() - inicio) * 1000
        
        return {
            "timestamp": datetime.now().isoformat(),
            "tiempo_procesamiento_ms": round(tiempo_procesamiento, 2),
            "rfc_importador": rfc,
            "fraccion_arancelaria": fraccion,
            "pais_origen": pais_origen,
            
            # Resultados de los 4 módulos
            "modulo1_historial": historial,
            "modulo2_valor": analisis_valor,
            "modulo3_alertas": alertas,
            "modulo4_checklist": checklist,
            
            # Resumen ejecutivo
            "resumen_ejecutivo": {
                "nivel_riesgo_global": nivel_riesgo_global,
                "canal_recomendado": canal_recomendado,
                "perfil_importador": historial.get("perfil_riesgo"),
                "riesgo_valor": analisis_valor.get("nivel_riesgo"),
                "alertas_criticas": sum(1 for a in alertas.get("alertas", []) if a.get("nivel_criticidad") == "CRITICO"),
                "documentos_faltantes": checklist.get("documentos_faltantes", 0),
                "acciones_inmediatas": acciones
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")


# ============================================================================
# MÓDULO 1: HISTORIAL DEL IMPORTADOR
# ============================================================================

@app.get("/api/importador/{rfc}")
def consultar_importador(
    rfc: str,
    meses_historial: int = Query(24, ge=1, le=60)
):
    """Consulta el historial completo de un importador"""
    resultado = analizador_historial.analizar_importador(rfc, meses_historial)
    
    if not resultado.get("encontrado"):
        raise HTTPException(status_code=404, detail=f"RFC {rfc} no encontrado")
    
    return resultado


@app.get("/api/importador/{rfc}/operaciones")
def historial_operaciones(
    rfc: str,
    limite: int = Query(10, ge=1, le=100)
):
    """Obtiene las últimas operaciones del importador"""
    operaciones = analizador_historial.obtener_historial_operaciones(rfc, limite)
    
    if not operaciones:
        raise HTTPException(status_code=404, detail=f"No se encontraron operaciones para RFC {rfc}")
    
    return {
        "rfc": rfc,
        "total_operaciones": len(operaciones),
        "operaciones": operaciones
    }


@app.get("/api/importador/{rfc}/comparacion-sector")
def comparar_sector(rfc: str):
    """Compara las métricas del importador con su sector"""
    resultado = analizador_historial.comparar_con_promedio_sector(rfc)
    
    if "error" in resultado:
        raise HTTPException(status_code=404, detail=resultado["error"])
    
    return resultado


# ============================================================================
# MÓDULO 2: VALOR DE REFERENCIA
# ============================================================================

@app.get("/api/valor/analizar")
def analizar_valor(
    fraccion: str = Query(..., description="Fracción arancelaria"),
    pais_origen: str = Query(..., description="País de origen"),
    valor_unitario: float = Query(..., gt=0, description="Valor unitario en USD"),
    cantidad: int = Query(1, gt=0, description="Cantidad")
):
    """Analiza el valor declarado contra referencias de mercado"""
    resultado = analizador_valor.analizar_valor(fraccion, pais_origen, valor_unitario, cantidad)
    return resultado


@app.get("/api/valor/estadisticas/{fraccion}")
def estadisticas_fraccion(fraccion: str):
    """Obtiene estadísticas de precios para una fracción"""
    resultado = analizador_valor.obtener_estadisticas_fraccion(fraccion)
    
    if not resultado.get("encontrado"):
        raise HTTPException(status_code=404, detail=f"No hay datos para fracción {fraccion}")
    
    return resultado


# ============================================================================
# MÓDULO 3: ALERTAS DE INTELIGENCIA
# ============================================================================

@app.get("/api/alertas/vigentes")
def alertas_vigentes(
    tipo: Optional[str] = Query(None, description="Tipo de alerta (TRI, SUB, etc.)"),
    criticidad: Optional[str] = Query(None, description="Nivel de criticidad")
):
    """Obtiene todas las alertas vigentes"""
    filtro = {}
    if tipo:
        filtro["tipo"] = tipo
    if criticidad:
        filtro["criticidad"] = criticidad
    
    alertas = gestor_alertas.obtener_alertas_vigentes(filtro)
    
    return {
        "total": len(alertas),
        "alertas": alertas
    }


@app.get("/api/alertas/buscar")
def buscar_alertas(
    fraccion: str = Query(..., description="Fracción arancelaria"),
    pais_origen: str = Query(..., description="País de origen"),
    proveedor_id: Optional[str] = Query(None, description="ID del proveedor")
):
    """Busca alertas relevantes para una operación específica"""
    resultado = gestor_alertas.buscar_alertas_para_operacion(
        fraccion, pais_origen, proveedor_id
    )
    return resultado


@app.get("/api/alertas/estadisticas")
def estadisticas_alertas():
    """Obtiene estadísticas generales de alertas"""
    return gestor_alertas.obtener_estadisticas_alertas()


@app.get("/api/alertas/modus-operandi")
def modus_operandi(
    tipo: Optional[str] = Query(None, description="Tipo de alerta")
):
    """Obtiene los modus operandi más frecuentes"""
    return {
        "modus_operandi": gestor_alertas.obtener_modus_operandi_frecuentes(tipo)
    }


# ============================================================================
# MÓDULO 4: CHECKLIST REGULATORIO
# ============================================================================

@app.get("/api/checklist/generar")
def generar_checklist(
    fraccion: str = Query(..., description="Fracción arancelaria"),
    pais_origen: str = Query(..., description="País de origen"),
    tipo_importador: str = Query("regular", description="Tipo de importador"),
    primera_importacion: bool = Query(False, description="¿Primera importación de esta fracción?")
):
    """Genera checklist regulatorio personalizado"""
    resultado = generador_checklist.generar_checklist(
        fraccion, pais_origen, tipo_importador, primera_importacion
    )
    return resultado


@app.get("/api/checklist/noms/{fraccion}")
def verificar_noms(fraccion: str):
    """Verifica las NOMs aplicables a una fracción"""
    resultado = generador_checklist.verificar_cumplimiento_noms(fraccion)
    
    if not resultado.get("encontrado"):
        raise HTTPException(status_code=404, detail=f"No hay información para fracción {fraccion}")
    
    return resultado


@app.get("/api/checklist/tratados/{pais}")
def consultar_tratados(pais: str):
    """Consulta tratados comerciales aplicables con un país"""
    return generador_checklist.obtener_tratados_comerciales(pais)


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def _determinar_riesgo_global(historial: dict, valor: dict, alertas: dict) -> str:
    """Determina el nivel de riesgo global de la operación"""
    riesgos = []
    
    # Riesgo del importador
    if historial.get("perfil_riesgo") == "ROJO":
        riesgos.append("ROJO")
    elif historial.get("perfil_riesgo") == "AMARILLO":
        riesgos.append("AMARILLO")
    
    # Riesgo del valor
    if valor.get("nivel_riesgo") == "ROJO":
        riesgos.append("ROJO")
    elif valor.get("nivel_riesgo") == "AMARILLO":
        riesgos.append("AMARILLO")
    
    # Riesgo de alertas
    if alertas.get("nivel_riesgo_global") == "ROJO":
        riesgos.append("ROJO")
    elif alertas.get("nivel_riesgo_global") == "AMARILLO":
        riesgos.append("AMARILLO")
    
    # Determinar riesgo final
    if "ROJO" in riesgos:
        return "ROJO"
    elif "AMARILLO" in riesgos:
        return "AMARILLO"
    else:
        return "VERDE"


def _recomendar_canal(riesgo_global: str, historial: dict, valor: dict, 
                     alertas: dict, checklist: dict) -> str:
    """Recomienda el canal de desaduanamiento"""
    if riesgo_global == "ROJO":
        return "ROJO"
    
    # Verificar alertas críticas
    if alertas.get("total_alertas", 0) > 0:
        alertas_criticas = sum(1 for a in alertas.get("alertas", []) 
                              if a.get("nivel_criticidad") == "CRITICO")
        if alertas_criticas > 0:
            return "ROJO"
    
    # Verificar documentos faltantes críticos
    if checklist.get("documentos_faltantes", 0) > 2:
        return "AMARILLO"
    
    if riesgo_global == "AMARILLO":
        return "AMARILLO"
    
    # Canal verde solo si todo está en orden
    if (historial.get("perfil_riesgo") == "VERDE" and 
        valor.get("nivel_riesgo") == "VERDE" and
        alertas.get("total_alertas", 0) == 0):
        return "VERDE"
    
    return "AMARILLO"


def _generar_acciones_inmediatas(historial: dict, valor: dict, 
                                alertas: dict, checklist: dict) -> list:
    """Genera lista de acciones inmediatas requeridas"""
    acciones = []
    
    # Acciones por historial
    if historial.get("perfil_riesgo") == "ROJO":
        acciones.append("Verificar antecedentes del importador")
    
    if historial.get("opinion_sat") == "NEGATIVA":
        acciones.append("CRÍTICO: Opinión SAT negativa - Verificar situación fiscal")
    
    # Acciones por valor
    if valor.get("nivel_riesgo") == "ROJO":
        acciones.append("Solicitar documentación adicional de valor (contratos, pagos)")
    
    # Acciones por alertas
    for alerta in alertas.get("alertas", [])[:3]:  # Top 3 alertas
        if alerta.get("nivel_criticidad") in ["CRITICO", "ALTO"]:
            acciones.append(f"Alerta {alerta.get('tipo')}: {alerta.get('accion_recomendada')}")
    
    # Acciones por checklist
    if checklist.get("documentos_faltantes", 0) > 0:
        acciones.append(f"Solicitar {checklist.get('documentos_faltantes')} documentos faltantes")
    
    return acciones[:5]  # Máximo 5 acciones


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
def health_check():
    """Verifica el estado del sistema"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modulos": {
            "historial": "OK",
            "valor": "OK",
            "alertas": "OK",
            "checklist": "OK"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Made with Bob
