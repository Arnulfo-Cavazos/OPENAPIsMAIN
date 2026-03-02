"""
MÓDULO 4 — Checklist Regulatorio Personalizado
Genera checklist dinámico de documentos y regulaciones
"""
import pandas as pd
import json
from typing import Dict, List, Optional


class GeneradorChecklist:
    """Genera checklist regulatorio personalizado"""
    
    def __init__(self, data_path: str = "data"):
        self.data_path = data_path
        self.regulaciones_df = pd.read_csv(f"{data_path}/regulaciones_por_fraccion.csv")
        
        # Convertir fechas
        self.regulaciones_df['fecha_ultima_actualizacion'] = pd.to_datetime(
            self.regulaciones_df['fecha_ultima_actualizacion']
        )
        
        # Parsear JSON
        self.regulaciones_df['noms_aplicables'] = self.regulaciones_df['noms_aplicables'].apply(
            lambda x: json.loads(x) if pd.notna(x) else []
        )
        self.regulaciones_df['permisos_previos'] = self.regulaciones_df['permisos_previos'].apply(
            lambda x: json.loads(x) if pd.notna(x) else []
        )
        self.regulaciones_df['tratados_aplicables'] = self.regulaciones_df['tratados_aplicables'].apply(
            lambda x: json.loads(x) if pd.notna(x) else []
        )
    
    def generar_checklist(self, fraccion: str, pais_origen: str,
                         tipo_importador: str = "regular",
                         primera_importacion: bool = False) -> Dict:
        """
        Genera checklist personalizado para una operación
        
        Args:
            fraccion: Fracción arancelaria
            pais_origen: País de origen
            tipo_importador: Tipo de importador (regular, nuevo, certificado)
            primera_importacion: Si es primera vez que importa esta fracción
        
        Returns:
            Diccionario con checklist completo
        """
        # Buscar regulación
        regulacion = self.regulaciones_df[
            self.regulaciones_df['fraccion_arancelaria'] == fraccion
        ]
        
        if regulacion.empty:
            return {
                "encontrado": False,
                "mensaje": f"No se encontró regulación para fracción {fraccion}",
                "fraccion": fraccion,
                "documentos_basicos": self._documentos_basicos()
            }
        
        reg = regulacion.iloc[0]
        
        # Generar documentos obligatorios
        documentos = self._generar_documentos_obligatorios(reg, pais_origen)
        
        # Generar permisos previos
        permisos = self._generar_permisos_previos(reg)
        
        # Generar regulaciones activas
        regulaciones_activas = self._generar_regulaciones_activas(reg)
        
        # Determinar canal sugerido
        canal_sugerido = self._determinar_canal_sugerido(
            reg, tipo_importador, primera_importacion
        )
        
        # Contar documentos faltantes (simulado)
        docs_faltantes = sum(1 for d in documentos if not d['presente'])
        permisos_faltantes = sum(1 for p in permisos if not p['presente'])
        
        return {
            "encontrado": True,
            "fraccion": fraccion,
            "descripcion": reg['descripcion_producto'],
            "pais_origen": pais_origen,
            "documentos_obligatorios": documentos,
            "permisos_previos": permisos,
            "regulaciones_activas": regulaciones_activas,
            "noms_aplicables": reg['noms_aplicables'],
            "tratados_comerciales": reg['tratados_aplicables'],
            "requiere_certificado_origen": bool(reg['requiere_certificado_origen']),
            "notas_especiales": reg['notas_especiales'],
            "fecha_actualizacion": reg['fecha_ultima_actualizacion'].strftime('%Y-%m-%d'),
            "canal_sugerido": canal_sugerido['canal'],
            "razon_canal": canal_sugerido['razon'],
            "documentos_faltantes": docs_faltantes,
            "permisos_faltantes": permisos_faltantes,
            "total_requisitos": len(documentos) + len(permisos),
            "cumplimiento_pct": round(
                ((len(documentos) + len(permisos) - docs_faltantes - permisos_faltantes) / 
                 (len(documentos) + len(permisos)) * 100) if (len(documentos) + len(permisos)) > 0 else 100,
                1
            )
        }
    
    def _documentos_basicos(self) -> List[Dict]:
        """Retorna documentos básicos siempre requeridos"""
        return [
            {
                "nombre": "Factura comercial",
                "obligatorio": True,
                "critico": True,
                "presente": True,
                "notas": "Debe incluir valor unitario desglosado"
            },
            {
                "nombre": "Lista de empaque (packing list)",
                "obligatorio": True,
                "critico": False,
                "presente": True,
                "notas": None
            },
            {
                "nombre": "Conocimiento de embarque",
                "obligatorio": True,
                "critico": True,
                "presente": True,
                "notas": "Bill of lading o guía aérea"
            }
        ]
    
    def _generar_documentos_obligatorios(self, reg, pais_origen: str) -> List[Dict]:
        """Genera lista de documentos obligatorios"""
        documentos = self._documentos_basicos()
        
        # Certificado de origen
        if reg['requiere_certificado_origen']:
            tratados = reg['tratados_aplicables']
            if tratados and len(tratados) > 0:
                notas = f"Certificado de origen {tratados[0]} o declaración en factura"
            else:
                notas = "Certificado de origen requerido"
            
            documentos.append({
                "nombre": "Certificado de origen",
                "obligatorio": True,
                "critico": True,
                "presente": False,  # Simulado como faltante
                "notas": notas
            })
        
        # Documentos específicos por regulación
        if reg['requiere_cofepris']:
            documentos.append({
                "nombre": "Registro sanitario COFEPRIS vigente",
                "obligatorio": True,
                "critico": True,
                "presente": False,
                "notas": "Debe tener menos de 5 años de antigüedad"
            })
            
            documentos.append({
                "nombre": "Certificado de análisis del lote",
                "obligatorio": True,
                "critico": False,
                "presente": False,
                "notas": "Análisis microbiológico y fisicoquímico"
            })
        
        if reg['requiere_senasica']:
            documentos.append({
                "nombre": "Certificado zoosanitario/fitosanitario",
                "obligatorio": True,
                "critico": True,
                "presente": False,
                "notas": "Emitido por autoridad del país de origen"
            })
        
        if reg['requiere_semarnat']:
            documentos.append({
                "nombre": "Certificado CITES (si aplica)",
                "obligatorio": False,
                "critico": True,
                "presente": False,
                "notas": "Solo si el producto está en lista CITES"
            })
        
        if reg['requiere_sedena']:
            documentos.append({
                "nombre": "Permiso SEDENA",
                "obligatorio": True,
                "critico": True,
                "presente": False,
                "notas": "CRÍTICO: Autorización previa obligatoria"
            })
        
        # Etiquetado
        if reg['requiere_cofepris'] or 'NOM-051' in str(reg['noms_aplicables']):
            documentos.append({
                "nombre": "Etiquetado en español verificado",
                "obligatorio": True,
                "critico": False,
                "presente": False,
                "notas": "Debe cumplir NOM vigente"
            })
        
        return documentos
    
    def _generar_permisos_previos(self, reg) -> List[Dict]:
        """Genera lista de permisos previos requeridos"""
        permisos = []
        
        for permiso in reg['permisos_previos']:
            permisos.append({
                "nombre": permiso,
                "obligatorio": True,
                "critico": True,
                "presente": False,
                "notas": "Debe obtenerse ANTES de la importación"
            })
        
        return permisos
    
    def _generar_regulaciones_activas(self, reg) -> List[str]:
        """Genera lista de regulaciones activas"""
        regulaciones = []
        
        # NOMs
        for nom in reg['noms_aplicables']:
            regulaciones.append(f"NOM aplicable: {nom}")
        
        # Permisos
        if reg['requiere_cofepris']:
            regulaciones.append("Regulación COFEPRIS activa")
        
        if reg['requiere_senasica']:
            regulaciones.append("Regulación SENASICA activa")
        
        if reg['requiere_semarnat']:
            regulaciones.append("Regulación SEMARNAT activa")
        
        if reg['requiere_sedena']:
            regulaciones.append("Regulación SEDENA activa - CRÍTICO")
        
        # Notas especiales
        if reg['notas_especiales'] and reg['notas_especiales'] != "Sin notas especiales":
            regulaciones.append(f"Nota especial: {reg['notas_especiales']}")
        
        return regulaciones
    
    def _determinar_canal_sugerido(self, reg, tipo_importador: str,
                                   primera_importacion: bool) -> Dict:
        """Determina el canal de desaduanamiento sugerido"""
        # Canal por defecto de la regulación
        canal_base = reg['canal_sugerido_default']
        
        # Ajustar según contexto
        razones = []
        
        if reg['requiere_sedena']:
            return {
                "canal": "ROJO",
                "razon": "Producto requiere permiso SEDENA - Reconocimiento obligatorio"
            }
        
        if primera_importacion:
            razones.append("Primera importación de esta fracción")
            if canal_base == "VERDE":
                canal_base = "AMARILLO"
        
        if tipo_importador == "nuevo":
            razones.append("Importador nuevo en el sistema")
            if canal_base == "VERDE":
                canal_base = "AMARILLO"
        
        if reg['requiere_cofepris'] or reg['requiere_senasica']:
            razones.append("Producto regulado sanitariamente")
        
        if len(reg['noms_aplicables']) > 2:
            razones.append(f"Múltiples NOMs aplicables ({len(reg['noms_aplicables'])})")
        
        if not razones:
            if canal_base == "VERDE":
                razones.append("Producto sin regulaciones especiales, importador confiable")
            elif canal_base == "AMARILLO":
                razones.append("Verificación documental recomendada")
            else:
                razones.append("Producto de alto riesgo o regulación estricta")
        
        return {
            "canal": canal_base,
            "razon": " | ".join(razones)
        }
    
    def verificar_cumplimiento_noms(self, fraccion: str) -> Dict:
        """Verifica las NOMs aplicables a una fracción"""
        regulacion = self.regulaciones_df[
            self.regulaciones_df['fraccion_arancelaria'] == fraccion
        ]
        
        if regulacion.empty:
            return {"encontrado": False, "fraccion": fraccion}
        
        reg = regulacion.iloc[0]
        
        return {
            "encontrado": True,
            "fraccion": fraccion,
            "descripcion": reg['descripcion_producto'],
            "noms_aplicables": reg['noms_aplicables'],
            "total_noms": len(reg['noms_aplicables']),
            "fecha_actualizacion": reg['fecha_ultima_actualizacion'].strftime('%Y-%m-%d'),
            "requiere_certificacion": len(reg['noms_aplicables']) > 0
        }
    
    def obtener_tratados_comerciales(self, pais_origen: str) -> Dict:
        """Obtiene información sobre tratados comerciales aplicables"""
        # Mapeo simplificado de países a tratados
        tratados_por_pais = {
            "Estados Unidos": ["T-MEC"],
            "Canadá": ["T-MEC"],
            "Alemania": ["TLCUE"],
            "España": ["TLCUE"],
            "Italia": ["TLCUE"],
            "Francia": ["TLCUE"],
            "Japón": ["AAE México-Japón"],
            "Corea del Sur": ["TLC México-Corea"],
            "Chile": ["TLC México-Chile"],
            "Colombia": ["Alianza del Pacífico"],
            "Perú": ["Alianza del Pacífico"]
        }
        
        tratados = tratados_por_pais.get(pais_origen, [])
        
        return {
            "pais": pais_origen,
            "tratados_aplicables": tratados,
            "tiene_tratado": len(tratados) > 0,
            "beneficios": "Arancel preferencial disponible" if len(tratados) > 0 else "Sin tratado comercial"
        }

# Made with Bob
