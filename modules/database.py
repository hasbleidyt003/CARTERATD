"""
Módulo de base de datos para Sistema de Cartera TD - CORREGIDO
Versión con columnas no ambiguas
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

# ============================================================================
# INICIALIZACIÓN DE BASE DE DATOS
# ============================================================================

def init_db():
    """Inicializa la base de datos si no existe"""
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # Tabla de clientes (ACTUALIZADA SIN columna estado)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nit TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        cupo_sugerido REAL DEFAULT 0,
        saldo_actual REAL DEFAULT 0,
        cartera_vencida REAL DEFAULT 0,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        disponible REAL GENERATED ALWAYS AS (cupo_sugerido - saldo_actual - cartera_vencida),
        porcentaje_uso REAL GENERATED ALWAYS AS (
            CASE 
                WHEN cupo_sugerido > 0 
                THEN ROUND((saldo_actual * 100.0 / cupo_sugerido), 2)
                ELSE 0 
            END
        ),
        activo BOOLEAN DEFAULT 1
    )
    ''')
    
    # Tabla de movimientos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movimientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_nit TEXT,
        tipo TEXT NOT NULL,
        valor REAL NOT NULL,
        fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        descripcion TEXT,
        referencia TEXT,
        usuario TEXT DEFAULT 'Sistema',
        FOREIGN KEY (cliente_nit) REFERENCES clientes(nit)
    )
    ''')
    
    # Tabla de OCs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ocs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_nit TEXT,
        numero_oc TEXT UNIQUE NOT NULL,
        valor_total REAL NOT NULL,
        valor_autorizado REAL DEFAULT 0,
        valor_pendiente REAL GENERATED ALWAYS AS (valor_total - valor_autorizado),
        estado TEXT DEFAULT 'PENDIENTE',
        tipo TEXT DEFAULT 'SUELTA',
        cupo_referencia TEXT,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_ultima_autorizacion TIMESTAMP,
        comentarios TEXT,
        FOREIGN KEY (cliente_nit) REFERENCES clientes(nit)
    )
    ''')
    
    # Insertar datos de ejemplo
    cursor.execute("SELECT COUNT(*) FROM clientes")
    if cursor.fetchone()[0] == 0:
        clientes_reales = [
            ('890905166', 'EMPRESA SOCIAL DEL ESTADO HOSPITAL MENTAL', 7500000000, 7397192942, 3342688638),
            ('900746052', 'NEURUM SAS', 5500000000, 5184247632, 2279333768),
            ('800241602', 'FUNDACION COLOMBIANA DE CANCEROLOGIA', 3500000000, 3031469552, 191990541),
            ('890985122', 'COOPERATIVA DE HOSPITALES DE ANTIOQUIA', 1500000000, 1291931405, 321889542),
            ('900099945', 'GLOBAL SERVICE PHARMACEUTICAL S.A.S.', 1200000000, 1009298565, 434808971),
            ('811038014', 'GRUPO ONCOLOGICO INTERNACIONAL S.A.', 900000000, 806853666, 146804409),
        ]
        
        for nit, nombre, cupo, saldo, cartera in clientes_reales:
            cursor.execute('''
            INSERT INTO clientes (nit, nombre, cupo_sugerido, saldo_actual, cartera_vencida)
            VALUES (?, ?, ?, ?, ?)
            ''', (nit, nombre, cupo, saldo, cartera))
    
    conn.commit()
    conn.close()
    return True

# ============================================================================
# FUNCIONES CORREGIDAS
# ============================================================================

def get_clientes():
    """Obtiene todos los clientes activos - CORREGIDO"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT 
        c.*,
        COALESCE(SUM(o.valor_pendiente), 0) as pendientes_total,
        -- Calcular estado dinámicamente SIN ambigüedad
        CASE 
            WHEN c.saldo_actual + c.cartera_vencida > c.cupo_sugerido THEN 'SOBREPASADO'
            WHEN c.saldo_actual + c.cartera_vencida > (c.cupo_sugerido * 0.8) THEN 'ALERTA'
            ELSE 'NORMAL'
        END as estado_cliente
    FROM clientes c
    LEFT JOIN ocs o ON c.nit = o.cliente_nit AND o.estado IN ('PENDIENTE', 'PARCIAL')
    WHERE c.activo = 1
    GROUP BY c.nit
    ORDER BY c.saldo_actual DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_estadisticas_generales():
    """Obtiene estadísticas generales - CORREGIDO"""
    conn = sqlite3.connect('data/database.db')
    
    query = '''
    SELECT 
        COUNT(*) as total_clientes,
        SUM(c.cupo_sugerido) as total_cupo_sugerido,
        SUM(c.saldo_actual) as total_saldo_actual,
        SUM(c.cartera_vencida) as total_cartera_vencida,
        SUM(c.disponible) as total_disponible,
        -- Calcular estados SIN ambigüedad
        COUNT(CASE 
            WHEN c.saldo_actual + c.cartera_vencida > c.cupo_sugerido 
            THEN 1 
        END) as clientes_sobrepasados,
        COUNT(CASE 
            WHEN c.saldo_actual + c.cartera_vencida > (c.cupo_sugerido * 0.8)
            AND c.saldo_actual + c.cartera_vencida <= c.cupo_sugerido
            THEN 1 
        END) as clientes_alerta,
        SUM(
            CASE 
                WHEN o.estado IN ('PENDIENTE', 'PARCIAL') 
                THEN o.valor_pendiente 
                ELSE 0 
            END
        ) as total_ocs_pendientes,
        SUM(
            CASE 
                WHEN m.tipo = 'PAGO' 
                THEN m.valor 
                ELSE 0 
            END
        ) as total_pagado_mes
    FROM clientes c
    LEFT JOIN ocs o ON c.nit = o.cliente_nit
    LEFT JOIN movimientos m ON c.nit = m.cliente_nit 
        AND strftime('%Y-%m', m.fecha_movimiento) = strftime('%Y-%m', 'now')
    WHERE c.activo = 1
    '''
    
    stats = pd.read_sql_query(query, conn).iloc[0]
    conn.close()
    
    return {
        'total_clientes': int(stats['total_clientes']),
        'total_cupo_sugerido': float(stats['total_cupo_sugerido'] or 0),
        'total_saldo_actual': float(stats['total_saldo_actual'] or 0),
        'total_cartera_vencida': float(stats['total_cartera_vencida'] or 0),
        'total_disponible': float(stats['total_disponible'] or 0),
        'clientes_sobrepasados': int(stats['clientes_sobrepasados'] or 0),
        'clientes_alerta': int(stats['clientes_alerta'] or 0),
        'total_ocs_pendientes': float(stats['total_ocs_pendientes'] or 0),
        'total_pagado_mes': float(stats['total_pagado_mes'] or 0)
    }

def get_estadisticas_por_cliente():
    """Obtiene estadísticas por cliente - CORREGIDO"""
    conn = sqlite3.connect('data/database.db')
    
    query = '''
    SELECT 
        c.nit,
        c.nombre,
        c.cupo_sugerido,
        c.saldo_actual,
        c.cartera_vencida,
        c.disponible,
        c.porcentaje_uso,
        -- Estado calculado dinámicamente
        CASE 
            WHEN c.saldo_actual + c.cartera_vencida > c.cupo_sugerido THEN 'SOBREPASADO'
            WHEN c.saldo_actual + c.cartera_vencida > (c.cupo_sugerido * 0.8) THEN 'ALERTA'
            ELSE 'NORMAL'
        END as estado,
        COALESCE(SUM(o.valor_pendiente), 0) as ocs_pendientes,
        COALESCE(COUNT(o.id), 0) as total_ocs
    FROM clientes c
    LEFT JOIN ocs o ON c.nit = o.cliente_nit
    WHERE c.activo = 1
    GROUP BY c.nit
    ORDER BY c.saldo_actual DESC
    '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ============================================================================
# FUNCIONES SIMPLIFICADAS PARA EL DASHBOARD
# ============================================================================

def get_estadisticas_basicas():
    """Obtiene estadísticas básicas sin joins complejos"""
    conn = sqlite3.connect('data/database.db')
    
    query = '''
    SELECT 
        COUNT(*) as total_clientes,
        SUM(cupo_sugerido) as total_cupo,
        SUM(saldo_actual) as total_saldo,
        SUM(cartera_vencida) as total_vencido,
        SUM(cupo_sugerido - saldo_actual - cartera_vencida) as total_disponible
    FROM clientes
    WHERE activo = 1
    '''
    
    stats = pd.read_sql_query(query, conn).iloc[0]
    conn.close()
    
    return {
        'total_clientes': int(stats['total_clientes'] or 0),
        'total_cupo': float(stats['total_cupo'] or 0),
        'total_saldo': float(stats['total_saldo'] or 0),
        'total_vencido': float(stats['total_vencido'] or 0),
        'total_disponible': float(stats['total_disponible'] or 0)
    }

def get_clientes_basicos():
    """Obtiene clientes básicos sin cálculos complejos"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT 
        nit,
        nombre,
        cupo_sugerido,
        saldo_actual,
        cartera_vencida,
        (cupo_sugerido - saldo_actual - cartera_vencida) as disponible,
        ROUND((saldo_actual * 100.0 / cupo_sugerido), 2) as porcentaje_uso
    FROM clientes
    WHERE activo = 1
    ORDER BY nombre
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ============================================================================
# FUNCIONES PARA OCs
# ============================================================================

def get_ocs_pendientes():
    """Obtiene OCs pendientes"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT o.*, c.nombre as cliente_nombre 
    FROM ocs o
    JOIN clientes c ON o.cliente_nit = c.nit
    WHERE o.estado IN ('PENDIENTE', 'PARCIAL')
    ORDER BY o.fecha_registro DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_todas_ocs():
    """Obtiene todas las OCs"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT o.*, c.nombre as cliente_nombre 
    FROM ocs o
    JOIN clientes c ON o.cliente_nit = c.nit
    ORDER BY o.fecha_registro DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ============================================================================
# INICIALIZACIÓN
# ============================================================================

if __name__ == "__main__":
    if not os.path.exists('data/database.db'):
        print("🔧 Inicializando base de datos...")
        init_db()
        print("✅ Base de datos lista")
