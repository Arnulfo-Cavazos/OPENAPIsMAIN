"""
Script de prueba para el Sistema de Análisis de Importaciones
Ejecuta ejemplos de consultas a la API
"""
import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Imprime un separador de sección"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_health():
    """Prueba el endpoint de health check"""
    print_section("1. HEALTH CHECK")
    response = requests.get(f"{BASE_URL}/health")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_analisis_completo():
    """Prueba el análisis completo de una operación"""
    print_section("2. ANALISIS COMPLETO - Operación de Ejemplo")
    
    # Obtener un RFC de ejemplo de los datos generados
    params = {
        "rfc": "ABC700101ABC",  # RFC de ejemplo
        "fraccion": "8471.30",
        "pais_origen": "China",
        "valor_unitario": 450,
        "cantidad": 100
    }
    
    print(f"Consultando operación:")
    print(f"  RFC: {params['rfc']}")
    print(f"  Fracción: {params['fraccion']}")
    print(f"  País: {params['pais_origen']}")
    print(f"  Valor unitario: ${params['valor_unitario']} USD")
    print(f"  Cantidad: {params['cantidad']} unidades\n")
    
    response = requests.get(f"{BASE_URL}/api/analisis/completo", params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"Tiempo de procesamiento: {data['tiempo_procesamiento_ms']:.2f} ms\n")
        
        # Resumen ejecutivo
        resumen = data['resumen_ejecutivo']
        print("RESUMEN EJECUTIVO:")
        print(f"  Nivel de riesgo global: {resumen['nivel_riesgo_global']}")
        print(f"  Canal recomendado: {resumen['canal_recomendado']}")
        print(f"  Perfil importador: {resumen['perfil_importador']}")
        print(f"  Riesgo valor: {resumen['riesgo_valor']}")
        print(f"  Alertas críticas: {resumen['alertas_criticas']}")
        print(f"  Documentos faltantes: {resumen['documentos_faltantes']}")
        
        if resumen['acciones_inmediatas']:
            print("\nACCIONES INMEDIATAS:")
            for i, accion in enumerate(resumen['acciones_inmediatas'], 1):
                print(f"  {i}. {accion}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def test_importador():
    """Prueba la consulta de historial de importador"""
    print_section("3. HISTORIAL DEL IMPORTADOR")
    
    rfc = "ABC700101ABC"
    response = requests.get(f"{BASE_URL}/api/importador/{rfc}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"RFC: {data['rfc']}")
        print(f"Razón Social: {data['razon_social']}")
        print(f"Perfil de Riesgo: {data['perfil_riesgo']}")
        print(f"Total Operaciones (24m): {data['total_operaciones']}")
        print(f"Valor Total: ${data['valor_total_usd']:,.2f} USD")
        print(f"Tasa Irregularidades: {data['tasa_irregularidades']}%")
        print(f"Años Activo: {data['anios_activo']}")
        
        if data['alertas']:
            print("\nALERTAS:")
            for alerta in data['alertas']:
                print(f"  - {alerta}")
    else:
        print(f"Error: {response.status_code}")

def test_valor():
    """Prueba el análisis de valor"""
    print_section("4. ANALISIS DE VALOR")
    
    params = {
        "fraccion": "8542.31",
        "pais_origen": "China",
        "valor_unitario": 4.20,
        "cantidad": 1000
    }
    
    response = requests.get(f"{BASE_URL}/api/valor/analizar", params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Fracción: {data['fraccion']}")
        print(f"Descripción: {data['descripcion']}")
        print(f"Valor declarado: ${data['valor_declarado_unitario']:.2f} USD")
        print(f"Precio mercado: ${data['precio_mercado_promedio']:.2f} USD")
        print(f"Desviación: {data['desviacion_porcentual']:.1f}%")
        print(f"Percentil: {data['percentil_mercado']}")
        print(f"Nivel de riesgo: {data['nivel_riesgo']}")
        
        if data['alertas']:
            print("\nALERTAS DE VALOR:")
            for alerta in data['alertas']:
                print(f"  {alerta}")
    else:
        print(f"Error: {response.status_code}")

def test_alertas():
    """Prueba la búsqueda de alertas"""
    print_section("5. ALERTAS DE INTELIGENCIA")
    
    params = {
        "fraccion": "8471.30",
        "pais_origen": "China"
    }
    
    response = requests.get(f"{BASE_URL}/api/alertas/buscar", params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total alertas encontradas: {data['total_alertas']}")
        print(f"Nivel de riesgo global: {data['nivel_riesgo_global']}")
        
        if data['alertas']:
            print("\nALERTAS ACTIVAS:")
            for alerta in data['alertas'][:3]:  # Mostrar solo las primeras 3
                print(f"\n  ID: {alerta['id_alerta']}")
                print(f"  Tipo: {alerta['tipo']}")
                print(f"  Título: {alerta['titulo']}")
                print(f"  Criticidad: {alerta['nivel_criticidad']}")
                print(f"  Casos detectados: {alerta['casos_detectados']}")
    else:
        print(f"Error: {response.status_code}")

def test_checklist():
    """Prueba la generación de checklist"""
    print_section("6. CHECKLIST REGULATORIO")
    
    params = {
        "fraccion": "2106.90",
        "pais_origen": "Estados Unidos",
        "tipo_importador": "regular",
        "primera_importacion": False
    }
    
    response = requests.get(f"{BASE_URL}/api/checklist/generar", params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Fracción: {data['fraccion']}")
        print(f"Descripción: {data['descripcion']}")
        print(f"Canal sugerido: {data['canal_sugerido']}")
        print(f"Razón: {data['razon_canal']}")
        print(f"Cumplimiento: {data['cumplimiento_pct']}%")
        
        print(f"\nDOCUMENTOS OBLIGATORIOS ({len(data['documentos_obligatorios'])}):")
        for doc in data['documentos_obligatorios'][:5]:
            estado = "[X]" if doc['presente'] else "[ ]"
            critico = " (CRITICO)" if doc['critico'] else ""
            print(f"  {estado} {doc['nombre']}{critico}")
        
        if data['noms_aplicables']:
            print(f"\nNOMs APLICABLES:")
            for nom in data['noms_aplicables']:
                print(f"  - {nom}")
    else:
        print(f"Error: {response.status_code}")

def test_estadisticas():
    """Prueba endpoints de estadísticas"""
    print_section("7. ESTADISTICAS DEL SISTEMA")
    
    # Estadísticas de alertas
    response = requests.get(f"{BASE_URL}/api/alertas/estadisticas")
    if response.status_code == 200:
        data = response.json()
        print("ALERTAS:")
        print(f"  Total: {data['total_alertas']}")
        print(f"  Vigentes: {data['alertas_vigentes']}")
        print(f"  Vencidas: {data['alertas_vencidas']}")
        print(f"  Casos detectados: {data['casos_totales_detectados']}")

def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*80)
    print("  SISTEMA DE ANALISIS DE IMPORTACIONES - PRUEBAS")
    print("="*80)
    print("\nAsegurate de que el servidor este corriendo en http://localhost:8000")
    print("Presiona Ctrl+C para cancelar\n")
    
    try:
        input("Presiona Enter para continuar...")
    except KeyboardInterrupt:
        print("\n\nPruebas canceladas.")
        return
    
    try:
        # Ejecutar pruebas
        test_health()
        sleep(1)
        
        test_analisis_completo()
        sleep(1)
        
        test_importador()
        sleep(1)
        
        test_valor()
        sleep(1)
        
        test_alertas()
        sleep(1)
        
        test_checklist()
        sleep(1)
        
        test_estadisticas()
        
        print("\n" + "="*80)
        print("  PRUEBAS COMPLETADAS")
        print("="*80 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] No se pudo conectar al servidor.")
        print("Asegurate de que el servidor este corriendo:")
        print("  python main.py")
        print("\nO:")
        print("  uvicorn main:app --reload")
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")

if __name__ == "__main__":
    main()

# Made with Bob
