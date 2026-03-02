"""
Script para generar datos sintéticos - Parte 2
Bases de datos: precios_referencia, alertas, proveedores, regulaciones, tipo_cambio
"""
import csv
import random
from datetime import datetime, timedelta
import json

# Configuración de semilla para reproducibilidad
random.seed(42)

# ============================================================================
# BD 3 — PRECIOS REFERENCIA INTERNACIONALES (800 registros)
# ============================================================================
def generate_precios_referencia():
    """Genera 800 registros de precios de referencia internacional"""
    
    fracciones_detalladas = [
        ("8471.30", "Computadoras portátiles y notebooks", "PZA", 400, 1500),
        ("8542.31", "Procesadores y controladores", "PZA", 8, 80),
        ("8542.32", "Memorias RAM", "PZA", 15, 120),
        ("8517.12", "Teléfonos celulares smartphones", "PZA", 150, 800),
        ("8517.62", "Módems y routers", "PZA", 20, 150),
        ("6203.42", "Pantalones de algodón para hombre", "PZA", 8, 35),
        ("6204.62", "Pantalones de algodón para mujer", "PZA", 10, 40),
        ("6110.20", "Suéteres de algodón", "PZA", 12, 45),
        ("8708.29", "Partes de carrocería automotriz", "KG", 15, 85),
        ("8708.99", "Otras partes de vehículos", "KG", 10, 60),
        ("2106.90", "Preparaciones alimenticias diversas", "KG", 4, 25),
        ("1901.90", "Extractos de malta y preparaciones", "KG", 3, 18),
        ("8528.72", "Monitores y proyectores LED", "PZA", 120, 550),
        ("8528.59", "Otros monitores", "PZA", 80, 400),
        ("3004.90", "Medicamentos en dosis", "KG", 40, 280),
        ("3003.90", "Medicamentos sin dosificar", "KG", 30, 200),
        ("8473.30", "Partes de máquinas de procesamiento", "KG", 8, 70),
        ("8473.50", "Partes de otras máquinas", "KG", 5, 45),
        ("9403.60", "Muebles de madera", "PZA", 80, 450),
        ("9403.70", "Muebles de plástico", "PZA", 30, 180),
        ("8544.42", "Cables eléctricos con conectores", "KG", 4, 22),
        ("8544.49", "Otros conductores eléctricos", "KG", 3, 18),
        ("3926.90", "Manufacturas de plástico diversas", "KG", 2, 12),
        ("3923.30", "Bombonas y botellas de plástico", "KG", 1.5, 8),
        ("8536.69", "Conectores para tensión <= 1000V", "PZA", 0.8, 9),
        ("8536.90", "Otros aparatos eléctricos", "PZA", 1.2, 15),
        ("8504.40", "Convertidores estáticos", "PZA", 18, 140),
        ("8504.90", "Partes de transformadores", "KG", 8, 55),
        ("7326.90", "Manufacturas de hierro o acero", "KG", 4, 28),
        ("7308.90", "Construcciones de hierro o acero", "KG", 6, 35),
        ("8471.60", "Unidades de entrada o salida", "PZA", 15, 120),
        ("8471.70", "Unidades de memoria", "PZA", 25, 200),
        ("8525.80", "Cámaras de video", "PZA", 80, 600),
        ("8525.89", "Otras cámaras", "PZA", 50, 400),
        ("9018.90", "Instrumentos médicos diversos", "PZA", 30, 250),
        ("9018.19", "Otros aparatos de electro diagnóstico", "PZA", 100, 800),
        ("8481.80", "Válvulas diversas", "PZA", 5, 45),
        ("8481.10", "Válvulas reductoras de presión", "PZA", 8, 65),
        ("8483.40", "Engranajes y ruedas de fricción", "KG", 10, 75),
        ("8483.50", "Volantes y poleas", "KG", 8, 55),
        ("8501.10", "Motores de potencia <= 37.5 W", "PZA", 5, 40),
        ("8501.40", "Motores de corriente alterna", "PZA", 20, 180),
        ("8507.60", "Acumuladores de iones de litio", "PZA", 15, 120),
        ("8507.80", "Otros acumuladores", "PZA", 10, 85),
        ("8418.69", "Grupos frigoríficos", "PZA", 150, 900),
        ("8418.99", "Partes de refrigeradores", "KG", 8, 60),
        ("8419.89", "Aparatos para tratamiento de materias", "PZA", 200, 1500),
        ("8419.90", "Partes de aparatos", "KG", 12, 90),
        ("8421.23", "Aparatos para filtrar lubricantes", "PZA", 8, 65),
        ("8421.39", "Aparatos para filtrar gases", "PZA", 25, 200),
        ("9405.40", "Lámparas eléctricas portátiles", "PZA", 5, 35)
    ]
    
    paises = ["China", "Estados Unidos", "Alemania", "Japón", "Corea del Sur",
              "Vietnam", "Taiwán", "Italia", "España", "Brasil", "México",
              "Canadá", "Francia", "Reino Unido", "India", "Tailandia"]
    
    fuentes = ["COMTRADE", "BLOOMBERG", "INEGI", "ESTIMADO"]
    tendencias = ["ALZA", "BAJA", "ESTABLE"]
    
    precios = []
    
    for fraccion, descripcion, unidad, precio_base_min, precio_base_max in fracciones_detalladas:
        # Para cada fracción, generar precios para múltiples países
        paises_seleccionados = random.sample(paises, min(random.randint(4, 8), len(paises)))
        
        for pais in paises_seleccionados:
            # Ajustar precio base según país
            if pais == "China":
                factor = random.uniform(0.6, 0.9)
            elif pais in ["Estados Unidos", "Alemania", "Japón"]:
                factor = random.uniform(1.0, 1.3)
            elif pais in ["Vietnam", "India", "Tailandia"]:
                factor = random.uniform(0.5, 0.8)
            else:
                factor = random.uniform(0.8, 1.1)
            
            precio_promedio = round((precio_base_min + precio_base_max) / 2 * factor, 2)
            precio_min = round(precio_promedio * random.uniform(0.6, 0.8), 2)
            precio_max = round(precio_promedio * random.uniform(1.2, 1.5), 2)
            
            # Tendencia y variación
            tendencia = random.choice(tendencias)
            if tendencia == "ALZA":
                variacion = round(random.uniform(2, 15), 2)
            elif tendencia == "BAJA":
                variacion = round(random.uniform(-15, -2), 2)
            else:
                variacion = round(random.uniform(-2, 2), 2)
            
            fecha_act = datetime.now() - timedelta(days=random.randint(0, 30))
            
            precio = {
                'fraccion_arancelaria': fraccion,
                'descripcion': descripcion,
                'pais_origen': pais,
                'precio_unitario_promedio_usd': precio_promedio,
                'precio_min_usd': precio_min,
                'precio_max_usd': precio_max,
                'unidad_medida': unidad,
                'fecha_actualizacion': fecha_act.strftime('%Y-%m-%d'),
                'fuente_referencia': random.choice(fuentes),
                'tendencia_30d': tendencia,
                'variacion_pct_30d': variacion
            }
            
            precios.append(precio)
    
    # Guardar CSV
    with open('data/precios_referencia_internacionales.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=precios[0].keys())
        writer.writeheader()
        writer.writerows(precios)
    
    print(f"[OK] Generados {len(precios)} precios de referencia en data/precios_referencia_internacionales.csv")
    return precios


# ============================================================================
# BD 4 — ALERTAS DE INTELIGENCIA (120 registros)
# ============================================================================
def generate_alertas():
    """Genera 120 alertas de inteligencia"""
    
    tipos_alerta = [
        ("TRI", "Triangulación de origen", "ALTO"),
        ("SUB", "Subfacturación sistémica", "CRITICO"),
        ("FRA", "Clasificación arancelaria incorrecta", "MEDIO"),
        ("PRO", "Producto prohibido/restringido", "CRITICO"),
        ("SAN", "Empresa sancionada o relacionada", "CRITICO"),
        ("NOM", "NOM pendiente de verificación", "MEDIO"),
        ("DUM", "Posible dumping activo", "ALTO")
    ]
    
    fracciones_riesgo = [
        "8471.30", "8542.31", "8517.12", "6203.42", "8708.29",
        "2106.90", "8528.72", "3004.90", "8473.30", "9403.60",
        "8544.42", "3926.90", "8536.69", "8504.40", "7326.90"
    ]
    
    paises_riesgo = ["China", "Vietnam", "Panamá", "Hong Kong", "Malasia", "Tailandia"]
    
    alertas = []
    
    for i in range(1, 121):
        tipo_codigo, tipo_nombre, criticidad = random.choice(tipos_alerta)
        
        # Determinar si está vigente (40 activas, 80 históricas)
        vigente = i <= 40
        
        if vigente:
            fecha_emision = datetime.now() - timedelta(days=random.randint(1, 180))
            fecha_venc = None if random.random() < 0.7 else (datetime.now() + timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d')
        else:
            fecha_emision = datetime.now() - timedelta(days=random.randint(181, 730))
            fecha_venc = (fecha_emision + timedelta(days=random.randint(90, 365))).strftime('%Y-%m-%d')
        
        # Generar contenido según tipo
        if tipo_codigo == "TRI":
            fraccion = random.choice(fracciones_riesgo)
            pais = random.choice(paises_riesgo)
            titulo = f"Triangulación detectada: {pais} como origen falso"
            descripcion = f"Se detecta triangulación desde China vía {pais} para aprovechar aranceles preferenciales inexistentes."
            modus = f"Productos manufacturados en China son re-etiquetados en {pais} con certificados de origen apócrifos."
            senales = json.dumps([
                f"Proveedor registrado hace <12 meses en {pais}",
                f"No hay historial de manufactura en {pais}",
                "Precio 35-50% por debajo del mercado",
                "Certificado de origen con irregularidades"
            ])
            accion = f"Solicitar certificado de origen y verificar número de registro del exportador con autoridades de {pais}"
        
        elif tipo_codigo == "SUB":
            fraccion = random.choice(fracciones_riesgo)
            pais = random.choice(paises_riesgo)
            titulo = f"Subfacturación sistemática en {fraccion}"
            descripcion = f"Patrón de subfacturación detectado en importaciones de esta fracción desde {pais}."
            modus = "Declaración de valores 40-60% por debajo del mercado de forma consistente."
            senales = json.dumps([
                "Precio declarado en percentil <5 del mercado",
                "Mismo importador con patrón de erosión gradual de precios",
                "Múltiples importadores con precio idéntico del mismo proveedor"
            ])
            accion = "Solicitar documentación adicional de valor: contratos, pagos bancarios, lista de precios del proveedor"
        
        elif tipo_codigo == "FRA":
            fraccion = random.choice(fracciones_riesgo)
            pais = None
            titulo = f"Clasificación incorrecta frecuente en {fraccion}"
            descripcion = "Se detecta uso incorrecto de esta fracción para productos de mayor arancel."
            modus = "Productos clasificados como 'partes' cuando son equipos completos."
            senales = json.dumps([
                "Descripción de mercancía no coincide con fracción",
                "Precio unitario inconsistente con la clasificación",
                "Historial de reclasificaciones en reconocimiento"
            ])
            accion = "Verificar descripción detallada y solicitar ficha técnica del producto"
        
        elif tipo_codigo == "PRO":
            fraccion = random.choice(fracciones_riesgo)
            pais = None
            titulo = f"Producto con restricciones especiales"
            descripcion = "Producto sujeto a regulaciones especiales o permisos previos."
            modus = "Intento de importación sin permisos requeridos."
            senales = json.dumps([
                "Falta permiso COFEPRIS/SENASICA/SEMARNAT",
                "Producto en lista de sustancias controladas",
                "Requiere certificación especial"
            ])
            accion = "Verificar permisos previos y certificaciones requeridas"
        
        elif tipo_codigo == "SAN":
            fraccion = None
            pais = random.choice(paises_riesgo)
            titulo = f"Proveedor en lista de observación"
            descripcion = f"Proveedor extranjero con antecedentes de irregularidades."
            modus = "Empresa relacionada con casos previos de fraude aduanero."
            senales = json.dumps([
                "Proveedor en lista OFAC o similar",
                "Relacionado con empresa sancionada",
                "Múltiples casos de subfacturación"
            ])
            accion = "Verificar identidad del proveedor y solicitar documentación corporativa"
        
        elif tipo_codigo == "NOM":
            fraccion = random.choice(fracciones_riesgo)
            pais = None
            titulo = f"NOM actualizada requiere verificación"
            descripcion = "Norma oficial mexicana actualizada recientemente para esta fracción."
            modus = "Productos importados bajo norma anterior ya no vigente."
            senales = json.dumps([
                "Certificado de cumplimiento con fecha anterior a actualización",
                "Etiquetado no cumple nueva NOM",
                "Falta certificación de laboratorio acreditado"
            ])
            accion = "Verificar cumplimiento con versión vigente de la NOM"
        
        else:  # DUM
            fraccion = random.choice(fracciones_riesgo)
            pais = random.choice(paises_riesgo)
            titulo = f"Posible dumping desde {pais}"
            descripcion = f"Precios consistentemente por debajo del costo de producción."
            modus = "Venta a precios predatorios para ganar participación de mercado."
            senales = json.dumps([
                "Precio por debajo del costo de materias primas",
                "Volumen de importaciones aumentó 200%+",
                "Industria nacional presenta quejas formales"
            ])
            accion = "Documentar para posible investigación de prácticas desleales"
        
        alerta = {
            'id_alerta': f"A-2024-{str(i).zfill(4)}",
            'codigo_tipo': tipo_codigo,
            'fraccion_arancelaria': fraccion,
            'pais_origen_afectado': pais,
            'proveedor_extranjero_afectado': f"PROV-{random.randint(1, 300):03d}" if random.random() < 0.3 else None,
            'fecha_emision': fecha_emision.strftime('%Y-%m-%d'),
            'fecha_vencimiento': fecha_venc,
            'vigente': vigente,
            'nivel_criticidad': criticidad,
            'titulo_corto': titulo,
            'descripcion_detallada': descripcion,
            'modus_operandi': modus,
            'senales_de_alerta': senales,
            'accion_recomendada': accion,
            'num_casos_detectados': random.randint(3, 50)
        }
        
        alertas.append(alerta)
    
    # Guardar CSV
    with open('data/alertas_inteligencia.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=alertas[0].keys())
        writer.writeheader()
        writer.writerows(alertas)
    
    print(f"[OK] Generadas {len(alertas)} alertas en data/alertas_inteligencia.csv")
    return alertas


# ============================================================================
# BD 5 — PROVEEDORES EXTRANJEROS (300 registros)
# ============================================================================
def generate_proveedores():
    """Genera 300 proveedores extranjeros"""
    
    nombres_base = [
        "Global", "International", "Trading", "Export", "Import", "Manufacturing",
        "Industries", "Technology", "Electronics", "Textiles", "Foods", "Chemicals",
        "Automotive", "Machinery", "Components", "Systems", "Solutions", "Group"
    ]
    
    sufijos = ["Co Ltd", "Inc", "Corp", "GmbH", "SA", "Pte Ltd", "BV", "SpA"]
    
    paises = {
        "China": ["Shenzhen", "Shanghai", "Guangzhou", "Beijing", "Ningbo"],
        "Estados Unidos": ["Los Angeles", "New York", "Houston", "Miami", "Chicago"],
        "Alemania": ["Munich", "Berlin", "Hamburg", "Frankfurt", "Stuttgart"],
        "Japón": ["Tokyo", "Osaka", "Nagoya", "Yokohama", "Kobe"],
        "Corea del Sur": ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon"],
        "Vietnam": ["Ho Chi Minh", "Hanoi", "Da Nang", "Hai Phong", "Can Tho"],
        "Taiwán": ["Taipei", "Kaohsiung", "Taichung", "Tainan", "Hsinchu"],
        "Italia": ["Milan", "Rome", "Turin", "Florence", "Venice"],
        "España": ["Barcelona", "Madrid", "Valencia", "Seville", "Bilbao"],
        "Brasil": ["Sao Paulo", "Rio de Janeiro", "Brasilia", "Salvador", "Fortaleza"]
    }
    
    niveles = ["VERIFICADO", "EN_OBSERVACION", "LISTA_NEGRA"]
    
    proveedores = []
    
    for i in range(1, 301):
        pais = random.choice(list(paises.keys()))
        ciudad = random.choice(paises[pais])
        
        # Distribución: 200 verificados, 70 en observación, 30 lista negra
        if i <= 200:
            nivel = "VERIFICADO"
            motivo = None
            relacionado = False
            historial = random.randint(20, 500)
            anios = random.randint(5, 30)
        elif i <= 270:
            nivel = "EN_OBSERVACION"
            motivo = random.choice([
                "Precios inconsistentes con mercado",
                "Documentación incompleta en operaciones previas",
                "Cambio reciente de razón social",
                "Dirección no verificada",
                "Certificados de origen con irregularidades"
            ])
            relacionado = False
            historial = random.randint(5, 50)
            anios = random.randint(1, 8)
        else:
            nivel = "LISTA_NEGRA"
            motivo = random.choice([
                "Subfacturación comprobada",
                "Certificados de origen apócrifos",
                "Empresa fantasma",
                "Relacionado con fraude aduanero",
                "Sancionado por autoridades locales"
            ])
            relacionado = random.choice([True, False])
            historial = random.randint(0, 10)
            anios = random.randint(0, 3)
        
        fecha_registro = datetime.now() - timedelta(days=anios * 365 + random.randint(0, 365))
        
        proveedor = {
            'id_proveedor': f"PROV-{str(i).zfill(3)}",
            'nombre_empresa': f"{random.choice(nombres_base)} {random.choice(nombres_base)} {random.choice(sufijos)}",
            'pais': pais,
            'ciudad': ciudad,
            'fecha_registro_local': fecha_registro.strftime('%Y-%m-%d'),
            'anios_operacion': anios,
            'historial_exportaciones_mx': historial,
            'nivel_confianza': nivel,
            'motivo_observacion': motivo,
            'asociado_a_alerta_id': f"A-2024-{random.randint(1, 120):04d}" if nivel != "VERIFICADO" and random.random() < 0.4 else None,
            'relacionado_con_empresa_sancionada': relacionado
        }
        
        proveedores.append(proveedor)
    
    # Guardar CSV
    with open('data/proveedores_extranjeros.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=proveedores[0].keys())
        writer.writeheader()
        writer.writerows(proveedores)
    
    print(f"[OK] Generados {len(proveedores)} proveedores en data/proveedores_extranjeros.csv")
    return proveedores


# ============================================================================
# EJECUTAR GENERACIÓN
# ============================================================================
if __name__ == "__main__":
    print("Iniciando generacion de datos sinteticos - Parte 2...\n")
    
    # Generar precios de referencia
    precios = generate_precios_referencia()
    
    # Generar alertas
    alertas = generate_alertas()
    
    # Generar proveedores
    proveedores = generate_proveedores()
    
    print("\nGeneracion Parte 2 completada exitosamente!")

# Made with Bob
