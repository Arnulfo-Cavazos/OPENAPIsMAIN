# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import random

# Datos Órdenes de Producción
ordenes_data = {
    'Orden_ID': [f'OP-2024-{5600+i}' for i in range(15)],
    'Linea': random.choices(['Línea 1', 'Línea 2', 'Línea 3', 'Línea 4'], k=15),
    'Producto': random.choices(['Producto A', 'Producto B', 'Producto C', 'Producto D', 'Producto E'], k=15),
    'Cantidad_Objetivo': [random.randint(800, 1200) for _ in range(15)],
    'Cantidad_Producida': [random.randint(400, 1100) for _ in range(15)],
    'Estado': random.choices(['En Proceso', 'Completada', 'Iniciada', 'Pendiente'], weights=[6, 4, 3, 2], k=15),
    'Fecha_Inicio': [(datetime.now() - timedelta(days=random.randint(0, 5))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(15)],
    'Fecha_Fin_Estimada': [(datetime.now() + timedelta(hours=random.randint(2, 24))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(15)],
    'Turno': random.choices([1, 2, 3], k=15),
    'Prioridad': random.choices(['Alta', 'Media', 'Baja'], weights=[3, 5, 2], k=15)
}
df_ordenes = pd.DataFrame(ordenes_data)
df_ordenes.to_excel('datos_ordenes_produccion.xlsx', index=False)
print('OK datos_ordenes_produccion.xlsx creado')

# Datos Estado de Líneas
lineas_data = {
    'Linea': ['Línea 1', 'Línea 2', 'Línea 3', 'Línea 4'],
    'Estado': ['Produciendo', 'Produciendo', 'Paro', 'Produciendo'],
    'Turno_Actual': [2, 2, 2, 2],
    'Operadores_Asignados': [4, 3, 4, 3],
    'Tiempo_Ciclo_Actual': [32.5, 28.3, 0, 35.2],
    'Tiempo_Ciclo_Estandar': [30.0, 28.0, 30.0, 32.0],
    'OEE_Actual': [0.78, 0.85, 0.0, 0.72],
    'Unidades_Hora_Actual': [110, 128, 0, 102],
    'Unidades_Hora_Objetivo': [120, 128, 120, 112]
}
df_lineas = pd.DataFrame(lineas_data)
df_lineas.to_excel('datos_estado_lineas.xlsx', index=False)
print('OK datos_estado_lineas.xlsx creado')

# Datos Downtime
downtime_data = {
    'Downtime_ID': [f'DT-{2400+i}' for i in range(20)],
    'Linea': random.choices(['Línea 1', 'Línea 2', 'Línea 3', 'Línea 4'], k=20),
    'Fecha_Hora': [(datetime.now() - timedelta(hours=random.randint(1, 8))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(20)],
    'Causa': random.choices([
        'Falta de material',
        'Cambio de modelo',
        'Falla mecánica',
        'Ajuste de calidad',
        'Falta de personal',
        'Mantenimiento preventivo',
        'Problema eléctrico'
    ], k=20),
    'Duracion_Minutos': [random.randint(5, 60) for _ in range(20)],
    'Turno': random.choices([1, 2, 3], k=20),
    'Unidades_Perdidas': [random.randint(10, 120) for _ in range(20)],
    'Categoria': random.choices(['Material', 'Equipo', 'Método', 'Personal'], k=20)
}
df_downtime = pd.DataFrame(downtime_data)
df_downtime.to_excel('datos_downtime.xlsx', index=False)
print('OK datos_downtime.xlsx creado')

# Datos Scrap
scrap_data = {
    'Scrap_ID': [f'SCR-{3200+i}' for i in range(25)],
    'Linea': random.choices(['Línea 1', 'Línea 2', 'Línea 3', 'Línea 4'], k=25),
    'Orden_ID': random.choices([f'OP-2024-{5600+i}' for i in range(15)], k=25),
    'Fecha_Hora': [(datetime.now() - timedelta(hours=random.randint(1, 8))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(25)],
    'Cantidad': [random.randint(1, 15) for _ in range(25)],
    'Defecto': random.choices([
        'Soldadura defectuosa',
        'Dimensión fuera de spec',
        'Rayado superficial',
        'Ensamble incorrecto',
        'Material dañado',
        'Falta de componente'
    ], k=25),
    'Estacion': random.choices(['Estación 1', 'Estación 2', 'Estación 3', 'Estación 4', 'Inspección Final'], k=25),
    'Turno': random.choices([1, 2, 3], k=25),
    'Operador': random.choices(['Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez', 'Pedro Sánchez'], k=25)
}
df_scrap = pd.DataFrame(scrap_data)
df_scrap.to_excel('datos_scrap.xlsx', index=False)
print('OK datos_scrap.xlsx creado')

# Datos Consumo de Materiales
consumo_data = {
    'Orden_ID': [],
    'Material': [],
    'Cantidad_BOM': [],
    'Cantidad_Consumida': [],
    'Inventario_Disponible': [],
    'Unidad': []
}

materiales = ['Lámina acero', 'Tornillos M6', 'Conectores', 'Cable 14AWG', 'Resina plástica', 'Empaque']
for orden_id in [f'OP-2024-{5600+i}' for i in range(10)]:
    num_materiales = random.randint(3, 5)
    for material in random.sample(materiales, num_materiales):
        consumo_data['Orden_ID'].append(orden_id)
        consumo_data['Material'].append(material)
        cantidad_bom = round(random.uniform(0.5, 5.0), 2)
        consumo_data['Cantidad_BOM'].append(cantidad_bom)
        consumo_data['Cantidad_Consumida'].append(round(cantidad_bom * random.randint(400, 900), 2))
        consumo_data['Inventario_Disponible'].append(round(random.uniform(100, 5000), 2))
        consumo_data['Unidad'].append(random.choice(['KG', 'PZA', 'MTS', 'LTS']))

df_consumo = pd.DataFrame(consumo_data)
df_consumo.to_excel('datos_consumo_materiales.xlsx', index=False)
print('OK datos_consumo_materiales.xlsx creado')

# Datos Personal
personal_data = {
    'Empleado_ID': [f'EMP-{1000+i}' for i in range(20)],
    'Nombre': [
        'Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez', 'Pedro Sánchez',
        'Laura Rodríguez', 'Miguel Torres', 'Carmen Flores', 'José Ramírez', 'Isabel Morales',
        'Francisco Jiménez', 'Rosa Hernández', 'Antonio Ruiz', 'Patricia Díaz', 'Luis Castro',
        'Elena Vargas', 'Roberto Ortiz', 'Sofía Mendoza', 'Diego Romero', 'Gabriela Silva'
    ],
    'Linea_Asignada': random.choices(['Línea 1', 'Línea 2', 'Línea 3', 'Línea 4'], k=20),
    'Turno': random.choices([1, 2, 3], k=20),
    'Puesto': random.choices(['Operador', 'Líder de línea', 'Inspector de calidad', 'Técnico'], weights=[12, 4, 3, 1], k=20),
    'Experiencia_Meses': [random.randint(3, 120) for _ in range(20)],
    'Certificaciones': random.choices(['Básico', 'Intermedio', 'Avanzado', 'Experto'], weights=[5, 8, 5, 2], k=20),
    'Productividad_Promedio': [round(random.uniform(0.85, 1.15), 2) for _ in range(20)]
}
df_personal = pd.DataFrame(personal_data)
df_personal.to_excel('datos_personal.xlsx', index=False)
print('OK datos_personal.xlsx creado')

print('\nTodos los archivos Excel han sido generados exitosamente')

# Made with Bob
