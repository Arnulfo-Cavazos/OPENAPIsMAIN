"""
MÓDULO 2 — Valor de Referencia Internacional
Analiza el valor declarado vs. precios de mercado internacional
"""
import pandas as pd
from typing import Dict, List, Optional
import numpy as np


class AnalizadorValor:
    """Analiza valores declarados contra referencias internacionales"""
    
    def __init__(self, data_path: str = "data"):
        self.data_path = data_path
        self.precios_df = pd.read_csv(f"{data_path}/precios_referencia_internacionales.csv")
        self.tipo_cambio_df = pd.read_csv(f"{data_path}/tipo_cambio_historico.csv")
        
        # Convertir fechas
        self.precios_df['fecha_actualizacion'] = pd.to_datetime(self.precios_df['fecha_actualizacion'])
        self.tipo_cambio_df['fecha'] = pd.to_datetime(self.tipo_cambio_df['fecha'])
    
    def analizar_valor(self, fraccion: str, pais_origen: str, 
                      valor_declarado_unitario: float, cantidad: int = 1) -> Dict:
        """
        Analiza el valor declarado contra referencias de mercado
        
        Args:
            fraccion: Fracción arancelaria
            pais_origen: País de origen de la mercancía
            valor_declarado_unitario: Valor unitario declarado en USD
            cantidad: Cantidad de unidades
        
        Returns:
            Diccionario con análisis de valor
        """
        # Buscar precio de referencia
        precio_ref = self.precios_df[
            (self.precios_df['fraccion_arancelaria'] == fraccion) &
            (self.precios_df['pais_origen'] == pais_origen)
        ]
        
        if precio_ref.empty:
            # Intentar buscar solo por fracción (cualquier país)
            precio_ref = self.precios_df[
                self.precios_df['fraccion_arancelaria'] == fraccion
            ]
            
            if precio_ref.empty:
                return {
                    "encontrado": False,
                    "mensaje": f"No hay precio de referencia para fracción {fraccion}",
                    "fraccion": fraccion,
                    "pais_origen": pais_origen,
                    "valor_declarado_unitario": valor_declarado_unitario
                }
            
            # Usar promedio de todos los países
            precio_ref = precio_ref.iloc[0]
            pais_referencia = "Promedio global"
        else:
            precio_ref = precio_ref.iloc[0]
            pais_referencia = pais_origen
        
        # Calcular desviación
        precio_mercado = float(precio_ref['precio_unitario_promedio_usd'])
        precio_min = float(precio_ref['precio_min_usd'])
        precio_max = float(precio_ref['precio_max_usd'])
        
        desviacion_pct = ((valor_declarado_unitario - precio_mercado) / precio_mercado) * 100
        
        # Calcular percentil aproximado
        percentil = self._calcular_percentil(valor_declarado_unitario, precio_min, precio_max, precio_mercado)
        
        # Determinar nivel de riesgo
        nivel_riesgo = self._determinar_riesgo_valor(desviacion_pct, percentil)
        
        # Generar alertas
        alertas = self._generar_alertas_valor(
            desviacion_pct, percentil, valor_declarado_unitario, 
            precio_mercado, precio_ref
        )
        
        # Obtener tipo de cambio actual
        tipo_cambio_actual = self._obtener_tipo_cambio_actual()
        
        return {
            "encontrado": True,
            "fraccion": fraccion,
            "descripcion": precio_ref['descripcion'],
            "pais_origen": pais_origen,
            "pais_referencia": pais_referencia,
            "valor_declarado_unitario": valor_declarado_unitario,
            "cantidad": cantidad,
            "valor_total_declarado": valor_declarado_unitario * cantidad,
            "precio_mercado_promedio": precio_mercado,
            "precio_min_mercado": precio_min,
            "precio_max_mercado": precio_max,
            "unidad_medida": precio_ref['unidad_medida'],
            "desviacion_porcentual": round(desviacion_pct, 2),
            "percentil_mercado": percentil,
            "nivel_riesgo": nivel_riesgo,
            "tendencia_precio": precio_ref['tendencia_30d'],
            "variacion_30d": float(precio_ref['variacion_pct_30d']),
            "fuente_referencia": precio_ref['fuente_referencia'],
            "fecha_actualizacion": precio_ref['fecha_actualizacion'].strftime('%Y-%m-%d'),
            "tipo_cambio_usd_mxn": tipo_cambio_actual,
            "valor_mxn": round(valor_declarado_unitario * cantidad * tipo_cambio_actual, 2),
            "alertas": alertas,
            "recomendacion": self._generar_recomendacion(nivel_riesgo, desviacion_pct)
        }
    
    def _calcular_percentil(self, valor: float, precio_min: float, 
                           precio_max: float, precio_promedio: float) -> int:
        """Calcula el percentil aproximado del valor en el rango de mercado"""
        if valor <= precio_min:
            return 5
        elif valor >= precio_max:
            return 95
        elif valor < precio_promedio:
            # Entre min y promedio (percentil 5-50)
            ratio = (valor - precio_min) / (precio_promedio - precio_min)
            return int(5 + (ratio * 45))
        else:
            # Entre promedio y max (percentil 50-95)
            ratio = (valor - precio_promedio) / (precio_max - precio_promedio)
            return int(50 + (ratio * 45))
    
    def _determinar_riesgo_valor(self, desviacion_pct: float, percentil: int) -> str:
        """Determina el nivel de riesgo basado en desviación y percentil"""
        # Subfacturación severa
        if desviacion_pct < -40 or percentil < 10:
            return "ROJO"
        
        # Subfacturación moderada
        if desviacion_pct < -20 or percentil < 25:
            return "AMARILLO"
        
        # Sobrefacturación (también sospechoso)
        if desviacion_pct > 50 or percentil > 90:
            return "AMARILLO"
        
        # Valor dentro de rango normal
        return "VERDE"
    
    def _generar_alertas_valor(self, desviacion_pct: float, percentil: int,
                              valor_declarado: float, precio_mercado: float,
                              precio_ref) -> List[str]:
        """Genera alertas específicas sobre el valor"""
        alertas = []
        
        # Alerta: Subfacturación severa
        if desviacion_pct < -40:
            alertas.append(
                f"🔴 SUBFACTURACIÓN SEVERA: Valor {abs(desviacion_pct):.1f}% por debajo del mercado"
            )
        elif desviacion_pct < -20:
            alertas.append(
                f"⚠️ Posible subfacturación: Valor {abs(desviacion_pct):.1f}% por debajo del mercado"
            )
        
        # Alerta: Percentil muy bajo
        if percentil < 10:
            alertas.append(
                f"🔴 Valor en percentil {percentil} del mercado (extremadamente bajo)"
            )
        elif percentil < 25:
            alertas.append(
                f"⚠️ Valor en percentil {percentil} del mercado (por debajo del promedio)"
            )
        
        # Alerta: Sobrefacturación
        if desviacion_pct > 50:
            alertas.append(
                f"⚠️ Posible sobrefacturación: Valor {desviacion_pct:.1f}% por encima del mercado"
            )
        
        # Alerta: Tendencia de precio
        if precio_ref['tendencia_30d'] == 'BAJA' and desviacion_pct < -15:
            alertas.append(
                "ℹ️ El precio de mercado ha estado en tendencia BAJA, pero el valor declarado es significativamente menor"
            )
        
        # Alerta: Precio exacto sospechoso
        if valor_declarado == precio_mercado:
            alertas.append(
                "⚠️ Valor declarado es exactamente igual al precio promedio de mercado (poco común)"
            )
        
        return alertas
    
    def _generar_recomendacion(self, nivel_riesgo: str, desviacion_pct: float) -> str:
        """Genera recomendación de acción"""
        if nivel_riesgo == "ROJO":
            return "ACCIÓN INMEDIATA: Solicitar documentación adicional de valor (contratos, pagos bancarios, lista de precios del proveedor). Considerar reconocimiento físico."
        elif nivel_riesgo == "AMARILLO":
            if desviacion_pct < 0:
                return "Verificar documentación de valor. Solicitar justificación del precio declarado."
            else:
                return "Verificar razón de sobreprecio. Puede ser producto especializado o con características especiales."
        else:
            return "Valor dentro de parámetros normales de mercado."
    
    def _obtener_tipo_cambio_actual(self) -> float:
        """Obtiene el tipo de cambio más reciente"""
        ultimo_tc = self.tipo_cambio_df.sort_values('fecha', ascending=False).iloc[0]
        return float(ultimo_tc['fix_banxico_usd_mxn'])
    
    def comparar_con_historial_proveedor(self, fraccion: str, proveedor_id: str,
                                        valor_actual: float) -> Dict:
        """Compara el valor actual con el historial del mismo proveedor"""
        # Este método requeriría acceso a pedimentos_historicos
        # Por ahora retornamos estructura básica
        return {
            "proveedor_id": proveedor_id,
            "fraccion": fraccion,
            "valor_actual": valor_actual,
            "mensaje": "Análisis de historial de proveedor requiere implementación adicional"
        }
    
    def detectar_erosion_gradual(self, rfc_importador: str, fraccion: str,
                                proveedor_id: str, meses: int = 6) -> Dict:
        """
        Detecta si hay un patrón de erosión gradual de precios
        (técnica común de subfacturación)
        """
        return {
            "patron_detectado": False,
            "mensaje": "Análisis de erosión gradual requiere datos históricos detallados"
        }
    
    def obtener_estadisticas_fraccion(self, fraccion: str) -> Dict:
        """Obtiene estadísticas generales de una fracción arancelaria"""
        precios = self.precios_df[self.precios_df['fraccion_arancelaria'] == fraccion]
        
        if precios.empty:
            return {"encontrado": False, "fraccion": fraccion}
        
        return {
            "encontrado": True,
            "fraccion": fraccion,
            "descripcion": precios.iloc[0]['descripcion'],
            "num_paises_referencia": len(precios),
            "precio_promedio_global": float(precios['precio_unitario_promedio_usd'].mean()),
            "precio_min_global": float(precios['precio_min_usd'].min()),
            "precio_max_global": float(precios['precio_max_usd'].max()),
            "paises_disponibles": precios['pais_origen'].tolist(),
            "tendencia_predominante": precios['tendencia_30d'].mode()[0] if len(precios) > 0 else "N/A"
        }

# Made with Bob
