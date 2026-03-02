"""
MÓDULO 3 — Alertas Activas de Inteligencia
Gestiona y consulta alertas de inteligencia aduanera
"""
import pandas as pd
import json
from typing import Dict, List, Optional
from datetime import datetime


class GestorAlertas:
    """Gestiona alertas de inteligencia aduanera"""
    
    def __init__(self, data_path: str = "data"):
        self.data_path = data_path
        self.alertas_df = pd.read_csv(f"{data_path}/alertas_inteligencia.csv")
        self.proveedores_df = pd.read_csv(f"{data_path}/proveedores_extranjeros.csv")
        
        # Convertir fechas
        self.alertas_df['fecha_emision'] = pd.to_datetime(self.alertas_df['fecha_emision'])
        self.alertas_df['fecha_vencimiento'] = pd.to_datetime(
            self.alertas_df['fecha_vencimiento'], 
            errors='coerce'
        )
        
        # Parsear JSON
        self.alertas_df['senales_de_alerta'] = self.alertas_df['senales_de_alerta'].apply(
            lambda x: json.loads(x) if pd.notna(x) else []
        )
    
    def obtener_alertas_vigentes(self, filtro: Optional[Dict] = None) -> List[Dict]:
        """
        Obtiene todas las alertas vigentes, opcionalmente filtradas
        
        Args:
            filtro: Diccionario con criterios de filtrado
                   - fraccion: Fracción arancelaria
                   - pais_origen: País de origen
                   - tipo: Tipo de alerta (TRI, SUB, etc.)
                   - criticidad: Nivel de criticidad
        
        Returns:
            Lista de alertas vigentes
        """
        alertas = self.alertas_df[self.alertas_df['vigente'] == True].copy()
        
        # Aplicar filtros si existen
        if filtro:
            if 'fraccion' in filtro and filtro['fraccion']:
                alertas = alertas[alertas['fraccion_arancelaria'] == filtro['fraccion']]
            
            if 'pais_origen' in filtro and filtro['pais_origen']:
                alertas = alertas[alertas['pais_origen_afectado'] == filtro['pais_origen']]
            
            if 'tipo' in filtro and filtro['tipo']:
                alertas = alertas[alertas['codigo_tipo'] == filtro['tipo']]
            
            if 'criticidad' in filtro and filtro['criticidad']:
                alertas = alertas[alertas['nivel_criticidad'] == filtro['criticidad']]
        
        # Convertir a lista de diccionarios
        resultado = []
        for _, alerta in alertas.iterrows():
            resultado.append(self._formatear_alerta(alerta))
        
        return resultado
    
    def buscar_alertas_para_operacion(self, fraccion: str, pais_origen: str,
                                     proveedor_id: Optional[str] = None) -> Dict:
        """
        Busca alertas relevantes para una operación específica
        
        Args:
            fraccion: Fracción arancelaria
            pais_origen: País de origen
            proveedor_id: ID del proveedor (opcional)
        
        Returns:
            Diccionario con alertas encontradas y análisis
        """
        alertas_encontradas = []
        
        # Buscar alertas por fracción
        alertas_fraccion = self.alertas_df[
            (self.alertas_df['vigente'] == True) &
            (self.alertas_df['fraccion_arancelaria'] == fraccion)
        ]
        
        for _, alerta in alertas_fraccion.iterrows():
            alertas_encontradas.append({
                **self._formatear_alerta(alerta),
                "tipo_match": "fraccion"
            })
        
        # Buscar alertas por país
        alertas_pais = self.alertas_df[
            (self.alertas_df['vigente'] == True) &
            (self.alertas_df['pais_origen_afectado'] == pais_origen)
        ]
        
        for _, alerta in alertas_pais.iterrows():
            if alerta['id_alerta'] not in [a['id_alerta'] for a in alertas_encontradas]:
                alertas_encontradas.append({
                    **self._formatear_alerta(alerta),
                    "tipo_match": "pais"
                })
        
        # Buscar alertas por proveedor
        if proveedor_id:
            alertas_proveedor = self.alertas_df[
                (self.alertas_df['vigente'] == True) &
                (self.alertas_df['proveedor_extranjero_afectado'] == proveedor_id)
            ]
            
            for _, alerta in alertas_proveedor.iterrows():
                if alerta['id_alerta'] not in [a['id_alerta'] for a in alertas_encontradas]:
                    alertas_encontradas.append({
                        **self._formatear_alerta(alerta),
                        "tipo_match": "proveedor"
                    })
        
        # Verificar proveedor en lista de observación
        info_proveedor = None
        if proveedor_id:
            info_proveedor = self._verificar_proveedor(proveedor_id)
        
        # Calcular nivel de riesgo global
        nivel_riesgo = self._calcular_riesgo_global(alertas_encontradas, info_proveedor)
        
        return {
            "total_alertas": len(alertas_encontradas),
            "alertas": alertas_encontradas,
            "info_proveedor": info_proveedor,
            "nivel_riesgo_global": nivel_riesgo,
            "recomendacion": self._generar_recomendacion_alertas(alertas_encontradas, nivel_riesgo)
        }
    
    def _formatear_alerta(self, alerta) -> Dict:
        """Formatea una alerta para respuesta"""
        return {
            "id_alerta": alerta['id_alerta'],
            "tipo": alerta['codigo_tipo'],
            "titulo": alerta['titulo_corto'],
            "descripcion": alerta['descripcion_detallada'],
            "nivel_criticidad": alerta['nivel_criticidad'],
            "fraccion": alerta['fraccion_arancelaria'] if pd.notna(alerta['fraccion_arancelaria']) else None,
            "pais_afectado": alerta['pais_origen_afectado'] if pd.notna(alerta['pais_origen_afectado']) else None,
            "fecha_emision": alerta['fecha_emision'].strftime('%Y-%m-%d'),
            "modus_operandi": alerta['modus_operandi'],
            "senales": alerta['senales_de_alerta'],
            "accion_recomendada": alerta['accion_recomendada'],
            "casos_detectados": int(alerta['num_casos_detectados'])
        }
    
    def _verificar_proveedor(self, proveedor_id: str) -> Optional[Dict]:
        """Verifica el estatus de un proveedor"""
        proveedor = self.proveedores_df[
            self.proveedores_df['id_proveedor'] == proveedor_id
        ]
        
        if proveedor.empty:
            return None
        
        prov = proveedor.iloc[0]
        
        return {
            "id": proveedor_id,
            "nombre": prov['nombre_empresa'],
            "pais": prov['pais'],
            "nivel_confianza": prov['nivel_confianza'],
            "anios_operacion": int(prov['anios_operacion']),
            "exportaciones_mx": int(prov['historial_exportaciones_mx']),
            "motivo_observacion": prov['motivo_observacion'] if pd.notna(prov['motivo_observacion']) else None,
            "relacionado_sancionado": bool(prov['relacionado_con_empresa_sancionada']),
            "alerta_asociada": prov['asociado_a_alerta_id'] if pd.notna(prov['asociado_a_alerta_id']) else None
        }
    
    def _calcular_riesgo_global(self, alertas: List[Dict], 
                               info_proveedor: Optional[Dict]) -> str:
        """Calcula el nivel de riesgo global basado en alertas y proveedor"""
        # Contar alertas por criticidad
        criticas = sum(1 for a in alertas if a['nivel_criticidad'] == 'CRITICO')
        altas = sum(1 for a in alertas if a['nivel_criticidad'] == 'ALTO')
        
        # Verificar proveedor
        proveedor_riesgo = False
        if info_proveedor:
            if info_proveedor['nivel_confianza'] == 'LISTA_NEGRA':
                proveedor_riesgo = True
            elif info_proveedor['relacionado_sancionado']:
                proveedor_riesgo = True
        
        # Determinar riesgo
        if criticas > 0 or proveedor_riesgo:
            return "ROJO"
        elif altas > 0 or len(alertas) >= 3:
            return "AMARILLO"
        elif len(alertas) > 0:
            return "AMARILLO"
        else:
            return "VERDE"
    
    def _generar_recomendacion_alertas(self, alertas: List[Dict], 
                                      nivel_riesgo: str) -> str:
        """Genera recomendación basada en alertas"""
        if nivel_riesgo == "ROJO":
            return "ACCIÓN CRÍTICA: Revisar exhaustivamente. Considerar canal rojo automático."
        elif nivel_riesgo == "AMARILLO":
            return "Verificación adicional requerida. Revisar documentación contra señales de alerta."
        else:
            return "Sin alertas críticas. Proceder con verificación estándar."
    
    def obtener_estadisticas_alertas(self) -> Dict:
        """Obtiene estadísticas generales de alertas"""
        alertas_vigentes = self.alertas_df[self.alertas_df['vigente'] == True]
        
        return {
            "total_alertas": len(self.alertas_df),
            "alertas_vigentes": len(alertas_vigentes),
            "alertas_vencidas": len(self.alertas_df) - len(alertas_vigentes),
            "por_tipo": alertas_vigentes['codigo_tipo'].value_counts().to_dict(),
            "por_criticidad": alertas_vigentes['nivel_criticidad'].value_counts().to_dict(),
            "casos_totales_detectados": int(alertas_vigentes['num_casos_detectados'].sum())
        }
    
    def obtener_modus_operandi_frecuentes(self, tipo_alerta: Optional[str] = None) -> List[Dict]:
        """Obtiene los modus operandi más frecuentes"""
        alertas = self.alertas_df[self.alertas_df['vigente'] == True]
        
        if tipo_alerta:
            alertas = alertas[alertas['codigo_tipo'] == tipo_alerta]
        
        resultado = []
        for _, alerta in alertas.head(10).iterrows():
            resultado.append({
                "tipo": alerta['codigo_tipo'],
                "titulo": alerta['titulo_corto'],
                "modus_operandi": alerta['modus_operandi'],
                "casos": int(alerta['num_casos_detectados'])
            })
        
        return resultado

# Made with Bob
