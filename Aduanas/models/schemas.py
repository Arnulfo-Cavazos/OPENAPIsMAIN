"""
Modelos Pydantic para validación de datos del sistema de análisis de importaciones
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================
class OpinionCumplimiento(str, Enum):
    POSITIVA = "POSITIVA"
    NEGATIVA = "NEGATIVA"
    NO_INSCRITO = "NO_INSCRITO"


class CanalDesaduanamiento(str, Enum):
    VERDE = "VERDE"
    AMARILLO = "AMARILLO"
    ROJO = "ROJO"


class ResultadoReconocimiento(str, Enum):
    SIN_OBSERVACIONES = "SIN_OBSERVACIONES"
    CON_OBSERVACIONES = "CON_OBSERVACIONES"
    EMBARGO = "EMBARGO"


class TipoAlerta(str, Enum):
    TRI = "TRI"  # Triangulación
    SUB = "SUB"  # Subfacturación
    FRA = "FRA"  # Fracción incorrecta
    PRO = "PRO"  # Producto prohibido
    SAN = "SAN"  # Empresa sancionada
    NOM = "NOM"  # NOM pendiente
    DUM = "DUM"  # Dumping


class NivelCriticidad(str, Enum):
    BAJO = "BAJO"
    MEDIO = "MEDIO"
    ALTO = "ALTO"
    CRITICO = "CRITICO"


class NivelConfianza(str, Enum):
    VERIFICADO = "VERIFICADO"
    EN_OBSERVACION = "EN_OBSERVACION"
    LISTA_NEGRA = "LISTA_NEGRA"


class Tendencia(str, Enum):
    ALZA = "ALZA"
    BAJA = "BAJA"
    ESTABLE = "ESTABLE"


class PerfilRiesgo(str, Enum):
    VERDE = "VERDE"  # Confiable
    AMARILLO = "AMARILLO"  # En revisión
    ROJO = "ROJO"  # Alto riesgo


# ============================================================================
# MODELOS DE DATOS
# ============================================================================
class Importador(BaseModel):
    rfc: str = Field(..., description="RFC del importador")
    razon_social: str = Field(..., description="Razón social de la empresa")
    fecha_alta_sat: date = Field(..., description="Fecha de alta en el SAT")
    giro_fiscal: str = Field(..., description="Giro fiscal de la empresa")
    estado: str = Field(..., description="Estado donde está registrada")
    agente_aduanal_asignado: str = Field(..., description="Código del agente aduanal")
    opinion_cumplimiento_sat: OpinionCumplimiento
    total_ops_24m: int = Field(..., ge=0, description="Total de operaciones en 24 meses")
    valor_total_declarado_24m: float = Field(..., ge=0, description="Valor total declarado en USD")
    tasa_irregularidades: float = Field(..., ge=0, le=100, description="Porcentaje de irregularidades")
    canal_historico_verde: float = Field(..., ge=0, le=100)
    canal_historico_amarillo: float = Field(..., ge=0, le=100)
    canal_historico_rojo: float = Field(..., ge=0, le=100)
    ultima_operacion: date
    flag_empresa_nueva: bool
    flag_volumen_anormal: bool


class Pedimento(BaseModel):
    num_pedimento: str = Field(..., description="Número de pedimento")
    rfc_importador: str
    fecha_pago: date
    aduana_entrada: str
    fraccion_arancelaria: str
    descripcion_mercancia: str
    pais_origen: str
    pais_procedencia: str
    proveedor_extranjero: str
    valor_declarado_usd: float = Field(..., ge=0)
    cantidad: int = Field(..., ge=0)
    unidad_medida: str
    peso_bruto_kg: float = Field(..., ge=0)
    tipo_cambio_dia: float = Field(..., gt=0)
    igi_pagado: float = Field(..., ge=0)
    iva_pagado: float = Field(..., ge=0)
    canal_asignado: CanalDesaduanamiento
    resultado_reconocimiento: ResultadoReconocimiento
    observaciones_text: Optional[str] = None
    agente_aduanal: str


class PrecioReferencia(BaseModel):
    fraccion_arancelaria: str
    descripcion: str
    pais_origen: str
    precio_unitario_promedio_usd: float = Field(..., gt=0)
    precio_min_usd: float = Field(..., gt=0)
    precio_max_usd: float = Field(..., gt=0)
    unidad_medida: str
    fecha_actualizacion: date
    fuente_referencia: str
    tendencia_30d: Tendencia
    variacion_pct_30d: float


class AlertaInteligencia(BaseModel):
    id_alerta: str
    codigo_tipo: TipoAlerta
    fraccion_arancelaria: Optional[str] = None
    pais_origen_afectado: Optional[str] = None
    proveedor_extranjero_afectado: Optional[str] = None
    fecha_emision: date
    fecha_vencimiento: Optional[date] = None
    vigente: bool
    nivel_criticidad: NivelCriticidad
    titulo_corto: str
    descripcion_detallada: str
    modus_operandi: str
    senales_de_alerta: List[str]
    accion_recomendada: str
    num_casos_detectados: int = Field(..., ge=0)


class ProveedorExtranjero(BaseModel):
    id_proveedor: str
    nombre_empresa: str
    pais: str
    ciudad: str
    fecha_registro_local: date
    anios_operacion: int = Field(..., ge=0)
    historial_exportaciones_mx: int = Field(..., ge=0)
    nivel_confianza: NivelConfianza
    motivo_observacion: Optional[str] = None
    asociado_a_alerta_id: Optional[str] = None
    relacionado_con_empresa_sancionada: bool


class RegulacionFraccion(BaseModel):
    fraccion_arancelaria: str
    descripcion_producto: str
    requiere_cofepris: bool
    requiere_senasica: bool
    requiere_semarnat: bool
    requiere_sedena: bool
    noms_aplicables: List[str]
    permisos_previos: List[str]
    requiere_certificado_origen: bool
    tratados_aplicables: List[str]
    notas_especiales: str
    fecha_ultima_actualizacion: date
    canal_sugerido_default: CanalDesaduanamiento


class TipoCambio(BaseModel):
    fecha: date
    fix_banxico_usd_mxn: float = Field(..., gt=0)
    euro_mxn: float = Field(..., gt=0)
    yuan_mxn: float = Field(..., gt=0)
    variacion_diaria_pct: float


# ============================================================================
# MODELOS DE RESPUESTA DEL AGENTE
# ============================================================================
class AnalisisImportador(BaseModel):
    """Resultado del análisis del Módulo 1 - Historial del Importador"""
    rfc: str
    razon_social: str
    perfil_riesgo: PerfilRiesgo
    total_operaciones: int
    valor_total_usd: float
    tasa_irregularidades: float
    anios_activo: float
    fracciones_mas_usadas: List[tuple[str, int]]
    paises_origen_frecuentes: List[tuple[str, int]]
    canal_historico: dict[str, float]
    agente_aduanal: str
    opinion_sat: str
    alertas: List[str]
    indicadores: dict[str, bool]


class AnalisisValor(BaseModel):
    """Resultado del análisis del Módulo 2 - Valor de Referencia"""
    fraccion: str
    descripcion: str
    pais_origen: str
    valor_declarado_unitario: float
    precio_mercado_promedio: float
    precio_min_mercado: float
    precio_max_mercado: float
    desviacion_porcentual: float
    percentil_mercado: int
    nivel_riesgo: PerfilRiesgo
    tendencia_precio: str
    fuente_referencia: str
    alertas: List[str]


class AlertaActiva(BaseModel):
    """Alerta activa del Módulo 3"""
    id_alerta: str
    tipo: str
    titulo: str
    descripcion: str
    nivel_criticidad: str
    senales: List[str]
    accion_recomendada: str
    casos_detectados: int


class DocumentoRequerido(BaseModel):
    """Documento en el checklist regulatorio"""
    nombre: str
    obligatorio: bool
    critico: bool
    presente: bool
    notas: Optional[str] = None


class ChecklistRegulatorio(BaseModel):
    """Resultado del Módulo 4 - Checklist Regulatorio"""
    fraccion: str
    descripcion: str
    pais_origen: str
    documentos_obligatorios: List[DocumentoRequerido]
    permisos_previos: List[DocumentoRequerido]
    regulaciones_activas: List[str]
    noms_aplicables: List[str]
    tratados_comerciales: List[str]
    canal_sugerido: CanalDesaduanamiento
    razon_canal: str


class AnalisisCompleto(BaseModel):
    """Respuesta completa del agente de análisis"""
    num_pedimento: str
    fecha_analisis: datetime
    tiempo_procesamiento_ms: float
    
    # Resultados de los 4 módulos
    modulo_importador: AnalisisImportador
    modulo_valor: AnalisisValor
    alertas_activas: List[AlertaActiva]
    checklist_regulatorio: ChecklistRegulatorio
    
    # Resumen ejecutivo
    nivel_riesgo_global: PerfilRiesgo
    recomendacion_canal: CanalDesaduanamiento
    acciones_inmediatas: List[str]
    documentos_faltantes: int
    alertas_criticas: int


# ============================================================================
# MODELOS DE REQUEST
# ============================================================================
class ConsultaPedimento(BaseModel):
    """Request para analizar un pedimento"""
    rfc_importador: str = Field(..., description="RFC del importador")
    num_pedimento: Optional[str] = Field(None, description="Número de pedimento (opcional)")
    fraccion_arancelaria: str = Field(..., description="Fracción arancelaria")
    pais_origen: str = Field(..., description="País de origen")
    valor_declarado_usd: float = Field(..., gt=0, description="Valor declarado en USD")
    cantidad: int = Field(..., gt=0, description="Cantidad de unidades")
    proveedor_extranjero: Optional[str] = Field(None, description="ID del proveedor")


class ConsultaImportador(BaseModel):
    """Request para consultar historial de importador"""
    rfc: str = Field(..., description="RFC del importador")
    meses_historial: int = Field(24, ge=1, le=60, description="Meses de historial a analizar")


class ConsultaPrecio(BaseModel):
    """Request para consultar precio de referencia"""
    fraccion_arancelaria: str
    pais_origen: str
    valor_declarado: float = Field(..., gt=0)

# Made with Bob
