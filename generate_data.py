"""
Script para generar datos sintéticos para el sistema de análisis de importaciones
"""
import csv
import random
from datetime import datetime, timedelta
import json

# Configuración de semilla para reproducibilidad
random.seed(42)

# ============================================================================
# BD 1 — IMPORTADORES (500 registros)
# ============================================================================
def generate_importadores():
    """Genera 500 empresas importadoras con distribución realista"""
    
    razones_sociales = [
        "Distribuidora", "Importadora", "Comercializadora", "Grupo", "Corporativo",
        "Industrias", "Manufacturas", "Tecnología", "Alimentos", "Textiles",
        "Electrónica", "Automotriz", "Farmacéutica", "Química", "Logística"
    ]
    
    sufijos = ["SA de CV", "SAPI de CV", "SC", "SA", "SPR de RL"]
    
    estados = ["CDMX", "Nuevo León", "Jalisco", "Estado de México", "Guanajuato",
               "Querétaro", "Puebla", "Veracruz", "Baja California", "Chihuahua"]
    
    giros = [
        "Comercio al por mayor", "Manufactura", "Distribución", "Retail",
        "Tecnología", "Alimentos y bebidas", "Textil", "Automotriz",
        "Electrónica", "Farmacéutica", "Química", "Construcción"
    ]
    
    agentes = [f"AA{str(i).zfill(4)}" for i in range(1, 51)]
    
    importadores = []
    
    for i in range(1, 501):
        # Generar RFC ficticio
        rfc = f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))}{random.randint(700101, 991231):06d}{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=3))}"
        
        # Fecha de alta (últimos 10 años, con concentración en últimos 3)
        dias_atras = random.choices(
            [random.randint(1, 365), random.randint(366, 1095), random.randint(1096, 3650)],
            weights=[0.15, 0.25, 0.60]
        )[0]
        fecha_alta = datetime.now() - timedelta(days=dias_atras)
        
        # Determinar perfil (60% verde, 25% amarillo, 15% rojo)
        perfil = random.choices(['verde', 'amarillo', 'rojo'], weights=[0.60, 0.25, 0.15])[0]
        
        if perfil == 'verde':
            total_ops = random.randint(50, 500)
            tasa_irreg = round(random.uniform(0, 2), 2)
            canal_verde = round(random.uniform(70, 95), 1)
            canal_amarillo = round(random.uniform(5, 25), 1)
            canal_rojo = round(100 - canal_verde - canal_amarillo, 1)
            opinion = random.choices(['POSITIVA', 'NO_INSCRITO'], weights=[0.9, 0.1])[0]
            flag_nueva = False
            flag_volumen = False
        elif perfil == 'amarillo':
            total_ops = random.randint(10, 80)
            tasa_irreg = round(random.uniform(2, 8), 2)
            canal_verde = round(random.uniform(40, 70), 1)
            canal_amarillo = round(random.uniform(20, 45), 1)
            canal_rojo = round(100 - canal_verde - canal_amarillo, 1)
            opinion = random.choices(['POSITIVA', 'NO_INSCRITO', 'NEGATIVA'], weights=[0.5, 0.3, 0.2])[0]
            flag_nueva = dias_atras < 365
            flag_volumen = random.choice([True, False])
        else:  # rojo
            total_ops = random.randint(1, 20)
            tasa_irreg = round(random.uniform(8, 25), 2)
            canal_verde = round(random.uniform(10, 40), 1)
            canal_amarillo = round(random.uniform(30, 50), 1)
            canal_rojo = round(100 - canal_verde - canal_amarillo, 1)
            opinion = random.choices(['NEGATIVA', 'NO_INSCRITO'], weights=[0.7, 0.3])[0]
            flag_nueva = dias_atras < 180
            flag_volumen = random.choice([True, False])
        
        valor_total = round(total_ops * random.uniform(50000, 500000), 2)
        ultima_op = datetime.now() - timedelta(days=random.randint(1, 90))
        
        importador = {
            'rfc': rfc,
            'razon_social': f"{random.choice(razones_sociales)} {random.choice(['Alpha', 'Beta', 'Gamma', 'Delta', 'Omega', 'Prime', 'Global', 'Internacional', 'Nacional', 'Central'])} {random.choice(sufijos)}",
            'fecha_alta_sat': fecha_alta.strftime('%Y-%m-%d'),
            'giro_fiscal': random.choice(giros),
            'estado': random.choice(estados),
            'agente_aduanal_asignado': random.choice(agentes),
            'opinion_cumplimiento_sat': opinion,
            'total_ops_24m': total_ops,
            'valor_total_declarado_24m': valor_total,
            'tasa_irregularidades': tasa_irreg,
            'canal_historico_verde': canal_verde,
            'canal_historico_amarillo': canal_amarillo,
            'canal_historico_rojo': canal_rojo,
            'ultima_operacion': ultima_op.strftime('%Y-%m-%d'),
            'flag_empresa_nueva': flag_nueva,
            'flag_volumen_anormal': flag_volumen
        }
        
        importadores.append(importador)
    
    # Guardar CSV
    with open('data/importadores.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=importadores[0].keys())
        writer.writeheader()
        writer.writerows(importadores)
    
    print(f"[OK] Generados {len(importadores)} importadores en data/importadores.csv")
    return importadores


# ============================================================================
# BD 2 — PEDIMENTOS HISTÓRICOS (15,000 registros)
# ============================================================================
def generate_pedimentos(importadores):
    """Genera 15,000 pedimentos distribuidos entre los importadores"""
    
    aduanas = [
        "640-Veracruz", "330-Nuevo Laredo", "010-Tijuana", "820-Manzanillo",
        "470-Ciudad Juárez", "680-Lázaro Cárdenas", "410-Guadalajara",
        "060-AICM", "430-Monterrey", "710-Altamira"
    ]
    
    fracciones = [
        ("8471.30", "Computadoras portátiles", "PZA", 500, 2000),
        ("8542.31", "Circuitos integrados", "PZA", 5, 50),
        ("8517.12", "Teléfonos celulares", "PZA", 100, 500),
        ("6203.42", "Pantalones de algodón", "PZA", 10, 40),
        ("8708.29", "Partes de carrocería", "KG", 20, 100),
        ("2106.90", "Preparaciones alimenticias", "KG", 5, 30),
        ("8528.72", "Monitores LED", "PZA", 150, 600),
        ("3004.90", "Medicamentos", "KG", 50, 300),
        ("8473.30", "Partes de computadoras", "KG", 10, 80),
        ("9403.60", "Muebles de madera", "PZA", 100, 500),
        ("8544.42", "Cables eléctricos", "KG", 5, 25),
        ("3926.90", "Manufacturas de plástico", "KG", 3, 15),
        ("8536.69", "Conectores eléctricos", "PZA", 1, 10),
        ("8504.40", "Convertidores eléctricos", "PZA", 20, 150),
        ("7326.90", "Manufacturas de hierro", "KG", 5, 30)
    ]
    
    paises_origen = ["China", "Estados Unidos", "Alemania", "Japón", "Corea del Sur",
                     "Vietnam", "Taiwán", "Italia", "España", "Brasil"]
    
    canales = ["VERDE", "AMARILLO", "ROJO"]
    resultados = ["SIN_OBSERVACIONES", "CON_OBSERVACIONES", "EMBARGO"]
    
    pedimentos = []
    
    for i in range(1, 15001):
        # Seleccionar importador (con distribución realista)
        importador = random.choice(importadores)
        
        # Fecha del pedimento (últimos 24 meses)
        fecha = datetime.now() - timedelta(days=random.randint(1, 730))
        
        # Seleccionar fracción
        fraccion, descripcion, unidad, precio_min, precio_max = random.choice(fracciones)
        
        # País de origen
        pais_origen = random.choice(paises_origen)
        pais_procedencia = random.choices([pais_origen, random.choice(paises_origen)], weights=[0.8, 0.2])[0]
        
        # Cantidad y precio
        cantidad = random.randint(10, 1000)
        precio_unitario = round(random.uniform(precio_min, precio_max), 2)
        
        # Aplicar subfacturación en ~5% de casos
        if random.random() < 0.05:
            precio_unitario = round(precio_unitario * random.uniform(0.4, 0.7), 2)
        
        valor_declarado = round(cantidad * precio_unitario, 2)
        peso_bruto = round(cantidad * random.uniform(0.5, 5), 2)
        
        # Tipo de cambio simulado
        tipo_cambio = round(random.uniform(16.5, 20.5), 4)
        
        # Impuestos
        igi = round(valor_declarado * random.uniform(0, 0.15), 2)
        iva = round((valor_declarado + igi) * 0.16, 2)
        
        # Canal asignado (basado en perfil del importador)
        if importador['canal_historico_verde'] > 70:
            canal = random.choices(canales, weights=[0.75, 0.20, 0.05])[0]
        elif importador['canal_historico_amarillo'] > 40:
            canal = random.choices(canales, weights=[0.40, 0.45, 0.15])[0]
        else:
            canal = random.choices(canales, weights=[0.20, 0.40, 0.40])[0]
        
        # Resultado
        if canal == "VERDE":
            resultado = "SIN_OBSERVACIONES"
            observaciones = None
        elif canal == "AMARILLO":
            resultado = random.choices(resultados[:2], weights=[0.85, 0.15])[0]
            observaciones = "Documentación incompleta" if resultado == "CON_OBSERVACIONES" else None
        else:
            resultado = random.choices(resultados, weights=[0.50, 0.35, 0.15])[0]
            if resultado == "CON_OBSERVACIONES":
                observaciones = random.choice([
                    "Valor declarado bajo observación",
                    "Clasificación arancelaria incorrecta",
                    "Falta certificado de origen",
                    "Documentación incompleta"
                ])
            elif resultado == "EMBARGO":
                observaciones = "Mercancía embargada por subfacturación"
            else:
                observaciones = None
        
        pedimento = {
            'num_pedimento': f"{fecha.strftime('%y')}-{random.choice(aduanas).split('-')[0]}-{str(i).zfill(7)}",
            'rfc_importador': importador['rfc'],
            'fecha_pago': fecha.strftime('%Y-%m-%d'),
            'aduana_entrada': random.choice(aduanas),
            'fraccion_arancelaria': fraccion,
            'descripcion_mercancia': descripcion,
            'pais_origen': pais_origen,
            'pais_procedencia': pais_procedencia,
            'proveedor_extranjero': f"PROV-{random.randint(1, 300):03d}",
            'valor_declarado_usd': valor_declarado,
            'cantidad': cantidad,
            'unidad_medida': unidad,
            'peso_bruto_kg': peso_bruto,
            'tipo_cambio_dia': tipo_cambio,
            'igi_pagado': igi,
            'iva_pagado': iva,
            'canal_asignado': canal,
            'resultado_reconocimiento': resultado,
            'observaciones_text': observaciones,
            'agente_aduanal': importador['agente_aduanal_asignado']
        }
        
        pedimentos.append(pedimento)
    
    # Guardar CSV
    with open('data/pedimentos_historicos.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=pedimentos[0].keys())
        writer.writeheader()
        writer.writerows(pedimentos)
    
    print(f"[OK] Generados {len(pedimentos)} pedimentos en data/pedimentos_historicos.csv")
    return pedimentos


# ============================================================================
# EJECUTAR GENERACIÓN
# ============================================================================
if __name__ == "__main__":
    print("Iniciando generacion de datos sinteticos...\n")
    
    # Generar importadores
    importadores = generate_importadores()
    
    # Generar pedimentos
    pedimentos = generate_pedimentos(importadores)
    
    print("\nGeneracion completada exitosamente!")

# Made with Bob
