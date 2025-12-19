import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st

# Configuración de la base de datos
DB_PATH = "data/finanzas.db"

def get_db_connection():
    """Establece conexión con la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=()):
    """Ejecuta una consulta SQL"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Inicializa la base de datos con tablas y datos iniciales"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabla de clientes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nit TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        total_cartera REAL DEFAULT 0,
        cupo_sugerido REAL DEFAULT 0,
        excluir_calculo INTEGER DEFAULT 0,
        observaciones TEXT,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabla de órdenes de compra
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ocs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero TEXT UNIQUE NOT NULL,
        cliente_nit TEXT NOT NULL,
        valor_total REAL NOT NULL,
        fecha DATE NOT NULL,
        descripcion TEXT,
        estado TEXT DEFAULT 'PENDIENTE',
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cliente_nit) REFERENCES clientes (nit)
    )
    ''')
    
    # Tabla de autorizaciones parciales
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS autorizaciones_parciales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        oc_numero TEXT NOT NULL,
        valor_autorizado REAL NOT NULL,
        valor_pendiente REAL NOT NULL,
        comentario TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (oc_numero) REFERENCES ocs (numero)
    )
    ''')
    
    # Insertar datos iniciales si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM clientes")
    if cursor.fetchone()[0] == 0:
        # Datos iniciales de clientes
        initial_clients = [
            ('901212102', 'AUNA COLOMBIA S.A.S', 19493849830, 21693849830, 1, 'pendientes 2.000 y nuevo cupo 200 - andres confirma'),
            ('890905166', 'HOSPITAL MENTAL DE ANTIOQUIA', 7397192942, 7500000000, 0, 'cupo sugerido'),
            ('900249425', 'PHARMASAN S.A.S', 5710785209, 5910785209, 1, 'se autoriza cupo de 200m'),
            ('900748052', 'NEUROM SAS', 5184247623, 5500000000, 0, ''),
            ('800241602', 'FUNDACIÓN CLÍNICA VIDA', 3031469552, 3500000000, 0, ''),
            ('890985122', 'COOPERATIVA HOSPITALES ANTIOQUIA', 1221931405, 1500000000, 0, 'cupo sugerido'),
            ('811038014', 'GRUPO ONCOLOGICO INTERNACIONAL', 806853666, 900000000, 0, 'cupo sugerido')
        ]
        
        cursor.executemany('''
        INSERT INTO clientes (nit, nombre, total_cartera, cupo_sugerido, excluir_calculo, observaciones)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', initial_clients)
        
        # Insertar algunas OCs de ejemplo
        sample_ocs = [
            ('OC-2024-001', '890905166', 200000000, '2024-01-15', 'Medicamentos varios', 'PENDIENTE'),
            ('OC-2024-002', '900748052', 150000000, '2024-01-10', 'Equipos médicos', 'PENDIENTE'),
            ('OC-2024-003', '800241602', 80000000, '2024-01-05', 'Insumos hospitalarios', 'AUTORIZADA'),
        ]
        
        cursor.executemany('''
        INSERT INTO ocs (numero, cliente_nit, valor_total, fecha, descripcion, estado)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_ocs)
    
    conn.commit()
    conn.close()
    
    # Crear carpeta de respaldo si no existe
    import os
    os.makedirs("backup", exist_ok=True)

def backup_database():
    """Crea un respaldo de la base de datos"""
    import shutil
    from datetime import datetime
    
    backup_file = f"backup/finanzas_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(DB_PATH, backup_file)
    return backup_file

def restore_database(backup_file):
    """Restaura la base de datos desde un respaldo"""
    import shutil
    shutil.copy2(backup_file, DB_PATH)
    return True

def get_client_summary():
    """Obtiene resumen de clientes para dashboard"""
    conn = get_db_connection()
    
    query = """
    SELECT 
        COUNT(*) as total_clientes,
        SUM(CASE WHEN excluir_calculo = 0 THEN 1 ELSE 0 END) as clientes_incluidos,
        SUM(CASE WHEN excluir_calculo = 1 THEN 1 ELSE 0 END) as clientes_excluidos,
        SUM(cupo_sugerido) as cupo_total,
        SUM(total_cartera) as cartera_total,
        SUM(CASE WHEN excluir_calculo = 0 THEN cupo_sugerido - total_cartera ELSE 0 END) as disponible_total
    FROM clientes
    """
    
    result = pd.read_sql(query, conn)
    conn.close()
    return result.iloc[0].to_dict()

def get_ocs_summary():
    """Obtiene resumen de OCs para dashboard"""
    conn = get_db_connection()
    
    query = """
    SELECT 
        COUNT(*) as total_ocs,
        SUM(CASE WHEN estado = 'PENDIENTE' THEN 1 ELSE 0 END) as ocs_pendientes,
        SUM(CASE WHEN estado = 'PARCIAL' THEN 1 ELSE 0 END) as ocs_parciales,
        SUM(CASE WHEN estado = 'AUTORIZADA' THEN 1 ELSE 0 END) as ocs_autorizadas,
        SUM(valor_total) as valor_total_ocs,
        SUM(CASE WHEN estado = 'PENDIENTE' THEN valor_total ELSE 0 END) as valor_pendiente
    FROM ocs
    """
    
    result = pd.read_sql(query, conn)
    conn.close()
    return result.iloc[0].to_dict()
