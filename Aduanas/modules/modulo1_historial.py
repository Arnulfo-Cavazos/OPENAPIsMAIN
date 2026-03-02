"""
MÓDULO 1 — Historial del Importador
Analiza el historial de operaciones del importador en los últimos 24 meses
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import Counter


class AnalizadorHistorial:
    """Analiza el historial de un importador"""
    
    def __init__(self, data_path: str = "data"):
        self.data_path = data_path
        self.importadores_df = pd.read_csv(f"{data_path}/importadores.csv")
        self.pedimentos_df = pd.read_csv(f"{data_path}/pedimentos_historicos.csv")
        
        # Convertir fechas
        self.importadores_df['fecha_alta_sat'] = pd.to_datetime(self.importadores_df['fecha_alta_sat'])
        self.importadores_df['ultima_operacion'] = pd.to_datetime(self.importadores_df['ultima_operacion'])
        self.pedimentos_df['fecha_pago'] = pd.to_datetime(self.pedimentos_df['fecha_pago'])
    
    def analizar_importador(self, rfc: str, meses_historial: int = 24) -> Dict:
        """
        Analiza el historial completo de un importador
        
        Args:
            rfc: RFC del importador
            meses_historial: Meses de historial a analizar (default 24)
        
        Returns:
            Diccionario con análisis completo del importador
        """
        # Buscar importador
        importador = self.importadores_df[self.importadores_df['rfc'] == rfc]
        
        if importador.empty:
            return {
                "encontrado": False,
                "mensaje": f"RFC {rfc} no encontrado en la base de datos"
            }
        
        importador = importador.iloc[0]
        
        # Obtener pedimentos del importador
        fecha_limite = datetime.now() - timedelta(days=meses_historial * 30)
        pedimentos = self.pedimentos_df[
            (self.pedimentos_df['rfc_importador'] == rfc) &
            (self.pedimentos_df['fecha_pago'] >= fecha_limite)
        ]
        
        # Calcular años activo
        anios_activo = (datetime.now() - importador['fecha_alta_sat']).days / 365.25
        
        # Analizar fracciones más utilizadas
        fracciones_counter = Counter(pedimentos['fraccion_arancelaria'])
        fracciones_top = fracciones_counter.most_common(5)
        
        # Analizar países de origen más frecuentes
        paises_counter = Counter(pedimentos['pais_origen'])
        paises_top = paises_counter.most_common(5)
        
        # Determinar perfil de riesgo
        perfil_riesgo = self._determinar_perfil_riesgo(importador, anios_activo, pedimentos)
        
        # Generar alertas
        alertas = self._generar_alertas(importador, anios_activo, pedimentos, fracciones_counter)
        
        # Generar indicadores
        indicadores = self._generar_indicadores(importador, anios_activo)
        
        return {
            "encontrado": True,
            "rfc": rfc,
            "razon_social": importador['razon_social'],
            "perfil_riesgo": perfil_riesgo,
            "total_operaciones": int(importador['total_ops_24m']),
            "valor_total_usd": float(importador['valor_total_declarado_24m']),
            "tasa_irregularidades": float(importador['tasa_irregularidades']),
            "anios_activo": round(anios_activo, 1),
            "fracciones_mas_usadas": [{"fraccion": f, "cantidad": c} for f, c in fracciones_top],
            "paises_origen_frecuentes": [{"pais": p, "cantidad": c} for p, c in paises_top],
            "canal_historico": {
                "verde": float(importador['canal_historico_verde']),
                "amarillo": float(importador['canal_historico_amarillo']),
                "rojo": float(importador['canal_historico_rojo'])
            },
            "agente_aduanal": importador['agente_aduanal_asignado'],
            "opinion_sat": importador['opinion_cumplimiento_sat'],
            "ultima_operacion": importador['ultima_operacion'].strftime('%Y-%m-%d'),
            "giro_fiscal": importador['giro_fiscal'],
            "estado": importador['estado'],
            "alertas": alertas,
            "indicadores": indicadores
        }
    
    def _determinar_perfil_riesgo(self, importador, anios_activo: float, pedimentos: pd.DataFrame) -> str:
        """Determina el perfil de riesgo del importador"""
        
        # Criterios para perfil VERDE (Confiable)
        if (importador['total_ops_24m'] > 50 and 
            importador['tasa_irregularidades'] < 2 and 
            anios_activo > 3 and
            importador['opinion_cumplimiento_sat'] == 'POSITIVA'):
            return "VERDE"
        
        # Criterios para perfil ROJO (Alto riesgo)
        if (anios_activo < 0.5 or  # Menos de 6 meses
            importador['tasa_irregularidades'] > 10 or
            importador['opinion_cumplimiento_sat'] == 'NEGATIVA' or
            importador['flag_empresa_nueva']):
            return "ROJO"
        
        # Por defecto: AMARILLO (En revisión)
        return "AMARILLO"
    
    def _generar_alertas(self, importador, anios_activo: float, 
                        pedimentos: pd.DataFrame, fracciones_counter: Counter) -> List[str]:
        """Genera alertas automáticas basadas en el análisis"""
        alertas = []
        
        # Alerta: Empresa nueva
        if anios_activo < 1:
            alertas.append(f"⚠️ Empresa de reciente creación ({round(anios_activo * 12)} meses)")
        
        # Alerta: Opinión negativa SAT
        if importador['opinion_cumplimiento_sat'] == 'NEGATIVA':
            alertas.append("🔴 Opinión de cumplimiento SAT: NEGATIVA")
        
        # Alerta: Tasa alta de irregularidades
        if importador['tasa_irregularidades'] > 5:
            alertas.append(f"⚠️ Tasa de irregularidades elevada: {importador['tasa_irregularidades']}%")
        
        # Alerta: Volumen anormal
        if importador['flag_volumen_anormal']:
            alertas.append("⚠️ Cambio súbito en volumen de operaciones detectado")
        
        # Alerta: Canal rojo frecuente
        if importador['canal_historico_rojo'] > 30:
            alertas.append(f"⚠️ Alto porcentaje de canal rojo histórico: {importador['canal_historico_rojo']}%")
        
        # Alerta: Cambio reciente de agente aduanal
        # (Simulado - en producción se compararía con histórico)
        if len(pedimentos) > 0:
            agentes_unicos = pedimentos['agente_aduanal'].nunique()
            if agentes_unicos > 1:
                alertas.append(f"⚠️ Ha trabajado con {agentes_unicos} agentes aduanales diferentes")
        
        # Alerta: Primera vez importando ciertas fracciones
        if len(fracciones_counter) > 0:
            # Verificar si hay fracciones con muy pocas operaciones
            fracciones_nuevas = [f for f, c in fracciones_counter.items() if c <= 2]
            if len(fracciones_nuevas) > 0:
                alertas.append(f"ℹ️ Importando {len(fracciones_nuevas)} fracciones por primera vez o con muy pocas operaciones")
        
        return alertas
    
    def _generar_indicadores(self, importador, anios_activo: float) -> Dict[str, bool]:
        """Genera indicadores booleanos de confiabilidad"""
        return {
            "importador_confiable": (
                importador['total_ops_24m'] > 50 and 
                importador['tasa_irregularidades'] < 2 and 
                anios_activo > 3
            ),
            "importador_en_revision": (
                importador['flag_volumen_anormal'] or 
                (1 <= anios_activo <= 3)
            ),
            "importador_alto_riesgo": (
                anios_activo < 0.5 or 
                importador['tasa_irregularidades'] > 10 or
                importador['opinion_cumplimiento_sat'] == 'NEGATIVA'
            ),
            "empresa_nueva": anios_activo < 1,
            "opinion_sat_positiva": importador['opinion_cumplimiento_sat'] == 'POSITIVA',
            "volumen_estable": not importador['flag_volumen_anormal']
        }
    
    def comparar_con_promedio_sector(self, rfc: str) -> Dict:
        """Compara las métricas del importador con el promedio de su sector"""
        importador = self.importadores_df[self.importadores_df['rfc'] == rfc]
        
        if importador.empty:
            return {"error": "RFC no encontrado"}
        
        importador = importador.iloc[0]
        giro = importador['giro_fiscal']
        
        # Obtener promedio del sector
        sector = self.importadores_df[self.importadores_df['giro_fiscal'] == giro]
        
        return {
            "giro_fiscal": giro,
            "total_ops_importador": int(importador['total_ops_24m']),
            "total_ops_promedio_sector": float(sector['total_ops_24m'].mean()),
            "tasa_irreg_importador": float(importador['tasa_irregularidades']),
            "tasa_irreg_promedio_sector": float(sector['tasa_irregularidades'].mean()),
            "valor_total_importador": float(importador['valor_total_declarado_24m']),
            "valor_total_promedio_sector": float(sector['valor_total_declarado_24m'].mean()),
            "posicion_percentil": self._calcular_percentil(importador, sector)
        }
    
    def _calcular_percentil(self, importador, sector: pd.DataFrame) -> Dict:
        """Calcula en qué percentil se encuentra el importador"""
        return {
            "operaciones": float((sector['total_ops_24m'] < importador['total_ops_24m']).sum() / len(sector) * 100),
            "valor": float((sector['valor_total_declarado_24m'] < importador['valor_total_declarado_24m']).sum() / len(sector) * 100)
        }
    
    def obtener_historial_operaciones(self, rfc: str, limite: int = 10) -> List[Dict]:
        """Obtiene las últimas operaciones del importador"""
        pedimentos = self.pedimentos_df[self.pedimentos_df['rfc_importador'] == rfc]
        pedimentos = pedimentos.sort_values('fecha_pago', ascending=False).head(limite)
        
        resultado = []
        for _, ped in pedimentos.iterrows():
            resultado.append({
                "num_pedimento": ped['num_pedimento'],
                "fecha": ped['fecha_pago'].strftime('%Y-%m-%d'),
                "fraccion": ped['fraccion_arancelaria'],
                "descripcion": ped['descripcion_mercancia'],
                "pais_origen": ped['pais_origen'],
                "valor_usd": float(ped['valor_declarado_usd']),
                "canal": ped['canal_asignado'],
                "resultado": ped['resultado_reconocimiento']
            })
        
        return resultado

# Made with Bob
