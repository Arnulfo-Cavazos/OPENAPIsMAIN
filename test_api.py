"""
Script de prueba para la API de Refacciones Grupo Picacho
Ejecutar después de iniciar el servidor con: python -m uvicorn app.main:app --reload
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Imprime la respuesta de manera formateada"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)

def test_health():
    """Test 1: Verificar que el servicio está funcionando"""
    response = requests.get(f"{BASE_URL}/health")
    print_response("Test 1: Health Check", response)

def test_inventario_consultar():
    """Test 2: Consultar inventario"""
    response = requests.get(f"{BASE_URL}/inventario/consultar?modelo=Civic")
    print_response("Test 2: Consultar Inventario (Modelo: Civic)", response)

def test_disponibilidad():
    """Test 3: Verificar disponibilidad de una refacción"""
    response = requests.get(f"{BASE_URL}/inventario/disponibilidad/BRK-001")
    print_response("Test 3: Disponibilidad de BRK-001", response)

def test_bajo_stock():
    """Test 4: Refacciones con stock bajo"""
    response = requests.get(f"{BASE_URL}/inventario/bajo-stock")
    print_response("Test 4: Refacciones con Stock Bajo", response)

def test_pedido_sugerido():
    """Test 5: Generar pedido sugerido"""
    response = requests.get(f"{BASE_URL}/pedidos/sugerido")
    print_response("Test 5: Pedido Sugerido", response)

def test_listar_pedidos():
    """Test 6: Listar pedidos pendientes"""
    response = requests.get(f"{BASE_URL}/pedidos/listar?estatus=Pendiente")
    print_response("Test 6: Listar Pedidos Pendientes", response)

def test_reporte_resumen():
    """Test 7: Reporte resumen del sistema"""
    response = requests.get(f"{BASE_URL}/reportes/resumen")
    print_response("Test 7: Reporte Resumen", response)

def test_solicitar_taller():
    """Test 8: Solicitar refacción para taller"""
    data = {
        "orden_servicio": "OS-TEST-001",
        "numero_parte": "BRK-001",
        "cantidad": 2
    }
    response = requests.post(f"{BASE_URL}/taller/solicitar", json=data)
    print_response("Test 8: Solicitar Refacción para Taller", response)

def test_consulta_rapida():
    """Test 9: Consulta rápida"""
    response = requests.get(f"{BASE_URL}/consultas/rapidas?pregunta=¿cuándo llega el pedido?")
    print_response("Test 9: Consulta Rápida", response)

def run_all_tests():
    """Ejecutar todas las pruebas"""
    print("\n" + "="*60)
    print("🚀 INICIANDO PRUEBAS DE LA API")
    print("="*60)
    
    try:
        test_health()
        test_inventario_consultar()
        test_disponibilidad()
        test_bajo_stock()
        test_pedido_sugerido()
        test_listar_pedidos()
        test_reporte_resumen()
        test_solicitar_taller()
        test_consulta_rapida()
        
        print("\n" + "="*60)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se pudo conectar al servidor")
        print("Asegúrate de que el servidor está corriendo:")
        print("  python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    run_all_tests()

# Made with Bob
