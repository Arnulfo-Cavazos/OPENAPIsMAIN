"""
Script para generar datos sintéticos - Parte 3
Bases de datos: regulaciones_por_fraccion, tipo_cambio_historico
"""
import csv
import random
from datetime import datetime, timedelta
import json

# Configuración de semilla para reproducibilidad
random.seed(42)

# ============================================================================
# BD 6 — REGULACIONES POR FRACCIÓN (300 registros)
# ============================================================================
def generate_regulaciones():
    """Genera 300 registros de regulaciones por fracción arancelaria"""
    
    fracciones_reguladas = [
        # Electrónica
        ("8471.30", "Computadoras portátiles", False, False, False, False, ["NOM-019-SCFI"], [], True, ["T-MEC", "TLCUE"], "VERDE"),
        ("8542.31", "Procesadores y controladores", False, False, False, False, ["NOM-019-SCFI"], [], True, ["T-MEC"], "VERDE"),
        ("8517.12", "Teléfonos celulares", False, False, False, False, ["NOM-208-SCFI", "IFT"], ["Homologación IFT"], True, ["T-MEC"], "AMARILLO"),
        ("8528.72", "Monitores LED", False, False, False, False, ["NOM-019-SCFI", "NOM-024-SCFI"], [], True, ["T-MEC"], "VERDE"),
        ("8473.30", "Partes de computadoras", False, False, False, False, ["NOM-019-SCFI"], [], True, ["T-MEC"], "VERDE"),
        
        # Textiles
        ("6203.42", "Pantalones de algodón hombre", False, False, False, False, ["NOM-004-SE"], [], True, ["T-MEC"], "VERDE"),
        ("6204.62", "Pantalones de algodón mujer", False, False, False, False, ["NOM-004-SE"], [], True, ["T-MEC"], "VERDE"),
        ("6110.20", "Suéteres de algodón", False, False, False, False, ["NOM-004-SE"], [], True, ["T-MEC"], "VERDE"),
        
        # Automotriz
        ("8708.29", "Partes de carrocería", False, False, False, False, ["NOM-050-SCFI"], [], True, ["T-MEC"], "VERDE"),
        ("8708.99", "Otras partes de vehículos", False, False, False, False, ["NOM-050-SCFI"], [], True, ["T-MEC"], "VERDE"),
        
        # Alimentos
        ("2106.90", "Preparaciones alimenticias", True, True, False, False, ["NOM-051-SCFI", "NOM-002-SCFI"], ["Registro COFEPRIS"], False, [], "AMARILLO"),
        ("1901.90", "Extractos de malta", True, True, False, False, ["NOM-051-SCFI", "NOM-002-SCFI"], ["Registro COFEPRIS"], False, [], "AMARILLO"),
        ("0201.10", "Carne de bovino fresca", True, True, False, False, ["NOM-194-SSA1"], ["Certificado zoosanitario SENASICA"], False, [], "ROJO"),
        ("0203.12", "Carne de porcino fresca", True, True, False, False, ["NOM-194-SSA1"], ["Certificado zoosanitario SENASICA"], False, [], "ROJO"),
        
        # Medicamentos
        ("3004.90", "Medicamentos en dosis", True, False, False, False, ["NOM-072-SSA1", "NOM-073-SSA1"], ["Registro sanitario COFEPRIS"], False, [], "ROJO"),
        ("3003.90", "Medicamentos sin dosificar", True, False, False, False, ["NOM-072-SSA1"], ["Registro sanitario COFEPRIS"], False, [], "ROJO"),
        
        # Químicos
        ("2804.10", "Hidrógeno", False, False, True, False, ["NOM-018-STPS"], ["Permiso SEMARNAT"], False, [], "ROJO"),
        ("2811.21", "Dióxido de carbono", False, False, True, False, ["NOM-018-STPS"], ["Permiso SEMARNAT"], False, [], "AMARILLO"),
        
        # Juguetes
        ("9503.00", "Juguetes diversos", False, False, False, False, ["NOM-015-SCFI"], [], False, [], "AMARILLO"),
        
        # Muebles
        ("9403.60", "Muebles de madera", False, False, True, False, ["NOM-008-SCFI"], ["Certificado SEMARNAT si es madera tropical"], False, [], "VERDE"),
        ("9403.70", "Muebles de plástico", False, False, False, False, ["NOM-008-SCFI"], [], False, [], "VERDE"),
        
        # Eléctricos
        ("8544.42", "Cables eléctricos", False, False, False, False, ["NOM-001-SEDE"], [], False, [], "VERDE"),
        ("8536.69", "Conectores eléctricos", False, False, False, False, ["NOM-003-SCFI"], [], False, [], "VERDE"),
        ("8504.40", "Convertidores estáticos", False, False, False, False, ["NOM-019-SCFI"], [], True, ["T-MEC"], "VERDE"),
        
        # Plásticos
        ("3926.90", "Manufacturas de plástico", False, False, False, False, [], [], False, [], "VERDE"),
        ("3923.30", "Bombonas de plástico", False, False, False, False, ["NOM-002-SCFI"], [], False, [], "VERDE"),
        
        # Metales
        ("7326.90", "Manufacturas de hierro", False, False, False, False, [], [], False, [], "VERDE"),
        ("7308.90", "Construcciones de hierro", False, False, False, False, ["NOM-008-SCFI"], [], False, [], "VERDE"),
        
        # Equipos médicos
        ("9018.90", "Instrumentos médicos", True, False, False, False, ["NOM-241-SSA1"], ["Registro COFEPRIS"], False, [], "ROJO"),
        ("9018.19", "Aparatos de electrodiagnóstico", True, False, False, False, ["NOM-241-SSA1"], ["Registro COFEPRIS"], False, [], "ROJO"),
        
        # Válvulas
        ("8481.80", "Válvulas diversas", False, False, False, False, [], [], False, [], "VERDE"),
        ("8481.10", "Válvulas reductoras", False, False, False, False, ["NOM-020-STPS"], [], False, [], "VERDE"),
        
        # Motores
        ("8501.10", "Motores pequeños", False, False, False, False, ["NOM-016-ENER"], [], False, [], "VERDE"),
        ("8501.40", "Motores AC", False, False, False, False, ["NOM-016-ENER"], [], False, [], "VERDE"),
        
        # Baterías
        ("8507.60", "Baterías de litio", False, False, True, False, ["NOM-001-SEDE"], ["Certificado UN38.3"], False, [], "AMARILLO"),
        ("8507.80", "Otros acumuladores", False, False, True, False, ["NOM-001-SEDE"], [], False, [], "VERDE"),
        
        # Refrigeración
        ("8418.69", "Grupos frigoríficos", False, False, True, False, ["NOM-023-ENER"], ["Certificado gases refrigerantes"], False, [], "AMARILLO"),
        ("8418.99", "Partes de refrigeradores", False, False, False, False, [], [], False, [], "VERDE"),
        
        # Filtros
        ("8421.23", "Filtros de lubricantes", False, False, False, False, [], [], False, [], "VERDE"),
        ("8421.39", "Filtros de gases", False, False, False, False, [], [], False, [], "VERDE"),
        
        # Iluminación
        ("9405.40", "Lámparas portátiles", False, False, False, False, ["NOM-058-SCFI"], [], False, [], "VERDE"),
        ("9405.10", "Lámparas de techo", False, False, False, False, ["NOM-058-SCFI"], [], False, [], "VERDE"),
        
        # Herramientas
        ("8467.21", "Taladros eléctricos", False, False, False, False, ["NOM-003-SCFI"], [], False, [], "VERDE"),
        ("8467.29", "Otras herramientas eléctricas", False, False, False, False, ["NOM-003-SCFI"], [], False, [], "VERDE"),
        
        # Calzado
        ("6403.99", "Calzado de cuero", False, False, False, False, ["NOM-020-SCFI"], [], False, [], "VERDE"),
        ("6404.19", "Calzado deportivo", False, False, False, False, ["NOM-020-SCFI"], [], False, [], "VERDE"),
        
        # Cosméticos
        ("3304.99", "Productos de belleza", True, False, False, False, ["NOM-141-SSA1"], ["Aviso sanitario COFEPRIS"], False, [], "AMARILLO"),
        ("3305.90", "Preparaciones capilares", True, False, False, False, ["NOM-141-SSA1"], ["Aviso sanitario COFEPRIS"], False, [], "AMARILLO"),
        
        # Bebidas
        ("2202.99", "Bebidas no alcohólicas", True, False, False, False, ["NOM-051-SCFI", "NOM-218-SSA1"], ["Registro COFEPRIS"], False, [], "AMARILLO"),
        ("2203.00", "Cerveza", True, False, False, False, ["NOM-199-SCFI"], ["Marbete IEPS"], False, [], "ROJO"),
        
        # Armas y municiones
        ("9303.30", "Armas de fuego deportivas", False, False, False, True, [], ["Permiso SEDENA"], False, [], "ROJO"),
        ("9306.30", "Cartuchos", False, False, False, True, [], ["Permiso SEDENA"], False, [], "ROJO")
    ]
    
    regulaciones = []
    
    for fraccion, descripcion, cofepris, senasica, semarnat, sedena, noms, permisos, cert_origen, tratados, canal in fracciones_reguladas:
        fecha_act = datetime.now() - timedelta(days=random.randint(0, 180))
        
        # Generar notas especiales
        notas = []
        if cofepris:
            notas.append("Requiere registro sanitario vigente (máximo 5 años)")
        if senasica:
            notas.append("Certificado zoosanitario debe ser emitido en país de origen")
        if semarnat:
            notas.append("Verificar que el producto no esté en lista CITES")
        if sedena:
            notas.append("CRÍTICO: Requiere autorización previa SEDENA")
        if cert_origen:
            notas.append("Certificado de origen puede ser declaración en factura si valor <1000 USD")
        
        regulacion = {
            'fraccion_arancelaria': fraccion,
            'descripcion_producto': descripcion,
            'requiere_cofepris': cofepris,
            'requiere_senasica': senasica,
            'requiere_semarnat': semarnat,
            'requiere_sedena': sedena,
            'noms_aplicables': json.dumps(noms),
            'permisos_previos': json.dumps(permisos),
            'requiere_certificado_origen': cert_origen,
            'tratados_aplicables': json.dumps(tratados),
            'notas_especiales': " | ".join(notas) if notas else "Sin notas especiales",
            'fecha_ultima_actualizacion': fecha_act.strftime('%Y-%m-%d'),
            'canal_sugerido_default': canal
        }
        
        regulaciones.append(regulacion)
    
    # Agregar más fracciones genéricas para llegar a 300
    fracciones_genericas = [
        "8471.60", "8471.70", "8525.80", "8525.89", "8483.40", "8483.50",
        "8419.89", "8419.90", "7318.15", "7318.16", "3920.10", "3920.20",
        "4011.10", "4011.20", "8302.10", "8302.42", "7616.99", "7616.10",
        "8414.80", "8414.90", "8415.10", "8415.90", "8450.11", "8450.19",
        "8516.10", "8516.60", "8509.40", "8509.80", "9506.91", "9506.99"
    ]
    
    for i, fraccion in enumerate(fracciones_genericas * 10):  # Repetir para llegar a 300
        if len(regulaciones) >= 300:
            break
        
        regulacion = {
            'fraccion_arancelaria': fraccion,
            'descripcion_producto': f"Producto clasificado en {fraccion}",
            'requiere_cofepris': False,
            'requiere_senasica': False,
            'requiere_semarnat': False,
            'requiere_sedena': False,
            'noms_aplicables': json.dumps([]),
            'permisos_previos': json.dumps([]),
            'requiere_certificado_origen': random.choice([True, False]),
            'tratados_aplicables': json.dumps(["T-MEC"] if random.random() > 0.5 else []),
            'notas_especiales': "Sin regulaciones especiales",
            'fecha_ultima_actualizacion': datetime.now().strftime('%Y-%m-%d'),
            'canal_sugerido_default': "VERDE"
        }
        
        regulaciones.append(regulacion)
    
    # Guardar CSV
    with open('data/regulaciones_por_fraccion.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=regulaciones[0].keys())
        writer.writeheader()
        writer.writerows(regulaciones)
    
    print(f"[OK] Generadas {len(regulaciones)} regulaciones en data/regulaciones_por_fraccion.csv")
    return regulaciones


# ============================================================================
# BD 7 — TIPO DE CAMBIO HISTÓRICO (730 registros - 2 años)
# ============================================================================
def generate_tipo_cambio():
    """Genera 730 días de tipo de cambio histórico"""
    
    tipos_cambio = []
    
    # Valores base
    usd_base = 18.50
    eur_base = 20.50
    yuan_base = 2.85
    
    fecha_actual = datetime.now()
    usd_anterior = usd_base
    
    for i in range(730, 0, -1):
        fecha = fecha_actual - timedelta(days=i)
        
        # Simular volatilidad realista con tendencias
        # Agregar ciclos y eventos
        dias_transcurridos = 730 - i
        
        # Tendencia general (depreciación gradual)
        tendencia = dias_transcurridos * 0.002
        
        # Volatilidad diaria
        volatilidad_usd = random.uniform(-0.15, 0.15)
        volatilidad_eur = random.uniform(-0.20, 0.20)
        volatilidad_yuan = random.uniform(-0.05, 0.05)
        
        # Eventos especiales (crisis, elecciones, etc.)
        if dias_transcurridos in [100, 200, 400, 600]:  # Eventos simulados
            volatilidad_usd += random.uniform(-0.50, 0.80)
        
        # Calcular tipos de cambio
        usd_mxn = round(usd_base + tendencia + volatilidad_usd, 4)
        eur_mxn = round(eur_base + tendencia * 1.1 + volatilidad_eur, 4)
        yuan_mxn = round(yuan_base + tendencia * 0.15 + volatilidad_yuan, 4)
        
        # Calcular variación diaria
        if i < 730:
            variacion = round(((usd_mxn - usd_anterior) / usd_anterior) * 100, 2)
        else:
            variacion = 0.0
        
        tipo_cambio = {
            'fecha': fecha.strftime('%Y-%m-%d'),
            'fix_banxico_usd_mxn': usd_mxn,
            'euro_mxn': eur_mxn,
            'yuan_mxn': yuan_mxn,
            'variacion_diaria_pct': variacion
        }
        
        tipos_cambio.append(tipo_cambio)
        
        # Guardar valor anterior para siguiente iteración
        usd_anterior = usd_mxn
        usd_base = usd_mxn  # Actualizar base para siguiente día
        eur_base = eur_mxn
        yuan_base = yuan_mxn
    
    # Guardar CSV
    with open('data/tipo_cambio_historico.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=tipos_cambio[0].keys())
        writer.writeheader()
        writer.writerows(tipos_cambio)
    
    print(f"[OK] Generados {len(tipos_cambio)} registros de tipo de cambio en data/tipo_cambio_historico.csv")
    return tipos_cambio


# ============================================================================
# EJECUTAR GENERACIÓN
# ============================================================================
if __name__ == "__main__":
    print("Iniciando generacion de datos sinteticos - Parte 3...\n")
    
    # Generar regulaciones
    regulaciones = generate_regulaciones()
    
    # Generar tipo de cambio
    tipo_cambio = generate_tipo_cambio()
    
    print("\nGeneracion Parte 3 completada exitosamente!")
    print("\n" + "="*60)
    print("RESUMEN DE BASES DE DATOS GENERADAS:")
    print("="*60)
    print("1. importadores.csv                          - 500 registros")
    print("2. pedimentos_historicos.csv                 - 15,000 registros")
    print("3. precios_referencia_internacionales.csv    - ~800 registros")
    print("4. alertas_inteligencia.csv                  - 120 registros")
    print("5. proveedores_extranjeros.csv               - 300 registros")
    print("6. regulaciones_por_fraccion.csv             - 300 registros")
    print("7. tipo_cambio_historico.csv                 - 730 registros")
    print("="*60)

# Made with Bob
