"""
MÓDULO DE BASE DE DATOS - SISTEMA TODODROGAS
Base de datos SQLite con clientes reales y gestión de OCs
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

# ==================== INICIALIZACIÓN DE BASE DE DATOS ====================

def init_db():
    """Inicializa la base de datos con los clientes reales"""
    
    # Crear carpetas necesarias
    os.makedirs('data', exist_ok=True)
    os.makedirs('data/backups', exist_ok=True)
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # Tabla de clientes (estructura mejorada)
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
                THEN ROUND(((saldo_actual + cartera_vencida) * 100.0 / cupo_sugerido), 2)
                ELSE 0 
            END
        ),
        estado TEXT GENERATED ALWAYS AS (
            CASE
                WHEN (saldo_actual + cartera_vencida) > cupo_sugerido THEN 'SOBREPASADO'
                WHEN (saldo_actual + cartera_vencida) > (cupo_sugerido * 0.8) THEN 'ALERTA'
                ELSE 'NORMAL'
            END
        ),
        activo BOOLEAN DEFAULT 1,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabla de órdenes de compra (OCs)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ocs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_nit TEXT NOT NULL,
        numero_oc TEXT UNIQUE NOT NULL,
        valor_total REAL NOT NULL,
        valor_autorizado REAL DEFAULT 0,
        valor_pendiente REAL GENERATED ALWAYS AS (valor_total - valor_autorizado),
        estado TEXT DEFAULT 'PENDIENTE',  -- PENDIENTE, PARCIAL, AUTORIZADA, CANCELADA
        tipo TEXT DEFAULT 'SUELTA',       -- SUELTA, CUPO_NUEVO, RENOVACION
        cupo_referencia TEXT,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_vencimiento DATE,
        fecha_ultima_autorizacion TIMESTAMP,
        comentarios TEXT,
        creado_por TEXT DEFAULT 'Sistema',
        FOREIGN KEY (cliente_nit) REFERENCES clientes(nit)
    )
    ''')
    
    # Tabla de autorizaciones parciales
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS autorizaciones_parciales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        oc_id INTEGER NOT NULL,
        valor_autorizado REAL NOT NULL,
        fecha_autorizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        comentario TEXT,
        autorizado_por TEXT DEFAULT 'Sistema',
        FOREIGN KEY (oc_id) REFERENCES ocs(id)
    )
    ''')
    
    # Tabla de movimientos (pagos, ajustes)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movimientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_nit TEXT NOT NULL,
        tipo TEXT NOT NULL,  -- PAGO, AJUSTE, NOTA_CREDITO, NOTA_DEBITO
        valor REAL NOT NULL,
        fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        descripcion TEXT,
        referencia TEXT,
        usuario TEXT DEFAULT 'Sistema',
        FOREIGN KEY (cliente_nit) REFERENCES clientes(nit)
    )
    ''')
    
    # Tabla de historial de cambios en cupos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS historial_cupos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_nit TEXT NOT NULL,
        cupo_anterior REAL NOT NULL,
        cupo_nuevo REAL NOT NULL,
        fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        motivo TEXT,
        realizado_por TEXT DEFAULT 'Sistema',
        FOREIGN KEY (cliente_nit) REFERENCES clientes(nit)
    )
    ''')
    
    # Índices para mejor performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cliente_nit ON clientes(nit)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_oc_cliente ON ocs(cliente_nit)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_oc_estado ON ocs(estado)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_oc_numero ON ocs(numero_oc)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_mov_cliente ON movimientos(cliente_nit)')
    
    # Verificar si ya existen clientes
    cursor.execute("SELECT COUNT(*) FROM clientes")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Insertar CLIENTES REALES de Tododrogas
        clientes_reales = [
            # NIT, Nombre, Cupo Sugerido, Saldo Actual, Cartera Vencida
            ('901212102', 'AUNA COLOMBIA S.A.S', 21693849830, 19493849830, 0),
            ('890905166', 'EMPRESA SOCIAL DEL ESTADO HOSPITAL MENTAL DE ANTIOQUIA', 7500000000, 7397192942, 0),
            ('900249425', 'PHARMASAN S.A.S', 5910785209, 5710785209, 0),
            ('900748052', 'NEUROM SAS', 5500000000, 5184247623, 0),
            ('800241602', 'FUNDACION COLOMBIANA DE CANCEROLOGIA CLINICA VIDA', 3500000000, 3031469552, 0),
            ('890985122', 'COOPERATIVA DE HOSPITALES DE ANTIOQUIA', 1500000000, 1221931405, 0),
            ('811038014', 'GRUPO ONCOLOGICO INTERNACIONAL S.A.', 900000000, 806853666, 0)
        ]
        
        for nit, nombre, cupo_sugerido, saldo_actual, cartera_vencida in clientes_reales:
            cursor.execute('''
            INSERT INTO clientes (nit, nombre, cupo_sugerido, saldo_actual, cartera_vencida)
            VALUES (?, ?, ?, ?, ?)
            ''', (nit, nombre, cupo_sugerido, saldo_actual, cartera_vencida))
        
        print(f"✅ Insertados {len(clientes_reales)} clientes reales de Tododrogas")
        
        # Insertar algunas OCs de ejemplo
        ocs_ejemplo = [
            ('901212102', 'OC-2024-001', 2500000000, 'PENDIENTE', 'SUELTA', None, '2024-04-30'),
            ('890905166', 'OC-2024-002', 1200000000, 'PARCIAL', 'SUELTA', None, '2024-04-25'),
            ('900249425', 'OC-2024-003', 850000000, 'AUTORIZADA', 'SUELTA', None, '2024-04-20'),
            ('900748052', 'OC-2024-004', 600000000, 'PENDIENTE', 'CUPO_NUEVO', 'CUPO-001', '2024-05-15'),
            ('800241602', 'OC-2024-005', 450000000, 'PENDIENTE', 'SUELTA', None, '2024-04-28'),
        ]
        
        for nit, numero_oc, valor_total, estado, tipo, cupo_ref, fecha_venc in ocs_ejemplo:
            cursor.execute('''
            INSERT INTO ocs (cliente_nit, numero_oc, valor_total, estado, tipo, cupo_referencia, fecha_vencimiento)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nit, numero_oc, valor_total, estado, tipo, cupo_ref, fecha_venc))
        
        # Insertar autorizaciones de ejemplo
        autorizaciones = [
            (2, 800000000, 'Autorización parcial por aprobación de gerencia'),
            (3, 850000000, 'Autorización completa del cupo'),
        ]
        
        for oc_id, valor, comentario in autorizaciones:
            cursor.execute('''
            INSERT INTO autorizaciones_parciales (oc_id, valor_autorizado, comentario)
            VALUES (?, ?, ?)
            ''', (oc_id, valor, comentario))
            
            # Actualizar valor autorizado en la OC
            cursor.execute('''
            UPDATE ocs 
            SET valor_autorizado = valor_autorizado + ?, 
                fecha_ultima_autorizacion = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (valor, oc_id))
    
    conn.commit()
    conn.close()
    return True

# ==================== FUNCIONES PARA CLIENTES ====================

def get_clientes():
    """Obtiene todos los clientes activos"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT 
        c.*,
        COALESCE(SUM(o.valor_pendiente), 0) as pendientes_total
    FROM clientes c
    LEFT JOIN ocs o ON c.nit = o.cliente_nit AND o.estado IN ('PENDIENTE', 'PARCIAL')
    WHERE c.activo = 1
    GROUP BY c.nit
    ORDER BY c.nombre
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_cliente_por_nit(nit):
    """Obtiene un cliente específico por NIT"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT 
        c.*,
        COALESCE(SUM(o.valor_pendiente), 0) as pendientes_total
    FROM clientes c
    LEFT JOIN ocs o ON c.nit = o.cliente_nit AND o.estado IN ('PENDIENTE', 'PARCIAL')
    WHERE c.nit = ? AND c.activo = 1
    GROUP BY c.nit
    '''
    df = pd.read_sql_query(query, conn, params=(nit,))
    conn.close()
    return df.iloc[0] if not df.empty else None

def actualizar_cupo_cliente(nit, nuevo_cupo, motivo="Ajuste manual"):
    """Actualiza el cupo sugerido de un cliente y registra en historial"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        # Obtener cupo anterior
        cursor.execute("SELECT cupo_sugerido FROM clientes WHERE nit = ?", (nit,))
        cupo_anterior = cursor.fetchone()[0]
        
        # Actualizar cupo
        cursor.execute('''
        UPDATE clientes 
        SET cupo_sugerido = ?, fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE nit = ?
        ''', (nuevo_cupo, nit))
        
        # Registrar en historial
        cursor.execute('''
        INSERT INTO historial_cupos (cliente_nit, cupo_anterior, cupo_nuevo, motivo)
        VALUES (?, ?, ?, ?)
        ''', (nit, cupo_anterior, nuevo_cupo, motivo))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error al actualizar cupo: {str(e)}")
    finally:
        conn.close()

# ==================== FUNCIONES PARA OCs ====================

def crear_oc(cliente_nit, numero_oc, valor_total, tipo="SUELTA", 
             cupo_referencia="", fecha_vencimiento=None, comentarios="", usuario="Sistema"):
    """Crea una nueva Orden de Compra"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO ocs 
        (cliente_nit, numero_oc, valor_total, tipo, cupo_referencia, 
         fecha_vencimiento, comentarios, creado_por)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cliente_nit, numero_oc, valor_total, tipo, cupo_referencia, 
              fecha_vencimiento, comentarios, usuario))
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        raise Exception(f"Ya existe una OC con número: {numero_oc}")
    except Exception as e:
        raise Exception(f"Error al crear OC: {str(e)}")
    finally:
        conn.close()

def get_oc_por_numero(numero_oc):
    """Obtiene una OC por su número"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT o.*, c.nombre as cliente_nombre
    FROM ocs o
    JOIN clientes c ON o.cliente_nit = c.nit
    WHERE o.numero_oc = ?
    '''
    df = pd.read_sql_query(query, conn, params=(numero_oc,))
    conn.close()
    return df.iloc[0] if not df.empty else None

def get_ocs_pendientes(cliente_nit=None):
    """Obtiene OCs pendientes o parciales"""
    conn = sqlite3.connect('data/database.db')
    
    if cliente_nit:
        query = '''
        SELECT o.*, c.nombre as cliente_nombre
        FROM ocs o
        JOIN clientes c ON o.cliente_nit = c.nit
        WHERE o.estado IN ('PENDIENTE', 'PARCIAL')
        AND o.cliente_nit = ?
        ORDER BY o.fecha_registro DESC
        '''
        df = pd.read_sql_query(query, conn, params=(cliente_nit,))
    else:
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

def get_todas_ocs(cliente_nit=None):
    """Obtiene todas las OCs"""
    conn = sqlite3.connect('data/database.db')
    
    if cliente_nit:
        query = '''
        SELECT o.*, c.nombre as cliente_nombre
        FROM ocs o
        JOIN clientes c ON o.cliente_nit = c.nit
        WHERE o.cliente_nit = ?
        ORDER BY o.fecha_registro DESC
        '''
        df = pd.read_sql_query(query, conn, params=(cliente_nit,))
    else:
        query = '''
        SELECT o.*, c.nombre as cliente_nombre
        FROM ocs o
        JOIN clientes c ON o.cliente_nit = c.nit
        ORDER BY o.fecha_registro DESC
        '''
        df = pd.read_sql_query(query, conn)
    
    conn.close()
    return df

def actualizar_oc(oc_id, datos):
    """Actualiza una OC existente"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if 'valor_total' in datos:
            updates.append("valor_total = ?")
            params.append(datos['valor_total'])
        
        if 'tipo' in datos:
            updates.append("tipo = ?")
            params.append(datos['tipo'])
        
        if 'cupo_referencia' in datos:
            updates.append("cupo_referencia = ?")
            params.append(datos['cupo_referencia'])
        
        if 'fecha_vencimiento' in datos:
            updates.append("fecha_vencimiento = ?")
            params.append(datos['fecha_vencimiento'])
        
        if 'comentarios' in datos:
            updates.append("comentarios = ?")
            params.append(datos['comentarios'])
        
        if 'estado' in datos:
            updates.append("estado = ?")
            params.append(datos['estado'])
        
        if updates:
            params.append(oc_id)
            query = f"UPDATE ocs SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error al actualizar OC: {str(e)}")
    finally:
        conn.close()

def autorizar_oc_parcial(oc_id, valor_autorizado, comentario="", usuario="Sistema"):
    """Autoriza parcialmente una OC"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        # Obtener datos actuales
        cursor.execute('SELECT valor_autorizado, valor_total FROM ocs WHERE id = ?', (oc_id,))
        oc = cursor.fetchone()
        
        if not oc:
            raise Exception("OC no encontrada")
        
        valor_actual, valor_total = oc
        
        # Verificar que no exceda el valor total
        nuevo_valor = valor_actual + valor_autorizado
        if nuevo_valor > valor_total:
            raise Exception(f"El valor autorizado ({nuevo_valor:,.0f}) excede el valor total ({valor_total:,.0f})")
        
        # Determinar nuevo estado
        if nuevo_valor >= valor_total:
            estado = 'AUTORIZADA'
        elif nuevo_valor > 0:
            estado = 'PARCIAL'
        else:
            estado = 'PENDIENTE'
        
        # Actualizar OC
        cursor.execute('''
        UPDATE ocs 
        SET valor_autorizado = ?, 
            estado = ?,
            fecha_ultima_autorizacion = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (nuevo_valor, estado, oc_id))
        
        # Registrar autorización parcial
        cursor.execute('''
        INSERT INTO autorizaciones_parciales (oc_id, valor_autorizado, comentario, autorizado_por)
        VALUES (?, ?, ?, ?)
        ''', (oc_id, valor_autorizado, comentario, usuario))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error al autorizar OC: {str(e)}")
    finally:
        conn.close()

def get_autorizaciones_oc(oc_id):
    """Obtiene el historial de autorizaciones de una OC"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT * FROM autorizaciones_parciales
    WHERE oc_id = ?
    ORDER BY fecha_autorizacion DESC
    '''
    df = pd.read_sql_query(query, conn, params=(oc_id,))
    conn.close()
    return df

# ==================== FUNCIONES DE ESTADÍSTICAS ====================

def get_estadisticas_generales():
    """Obtiene estadísticas generales del sistema"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT
        COUNT(*) as total_clientes,
        SUM(cupo_sugerido) as total_cupo,
        SUM(saldo_actual) as total_cartera,
        SUM(disponible) as total_disponible,
        COUNT(CASE WHEN estado = 'SOBREPASADO' THEN 1 END) as clientes_sobrepasados,
        COUNT(CASE WHEN estado = 'ALERTA' THEN 1 END) as clientes_alerta,
        SUM(CASE WHEN o.estado IN ('PENDIENTE', 'PARCIAL') THEN o.valor_pendiente ELSE 0 END) as total_ocs_pendientes
    FROM clientes c
    LEFT JOIN ocs o ON c.nit = o.cliente_nit
    WHERE c.activo = 1
    '''
    
    stats = pd.read_sql_query(query, conn).iloc[0]
    conn.close()
    
    return {
        'total_clientes': int(stats['total_clientes']),
        'total_cupo': float(stats['total_cupo']),
        'total_cartera': float(stats['total_cartera']),
        'total_disponible': float(stats['total_disponible']),
        'clientes_sobrepasados': int(stats['clientes_sobrepasados']),
        'clientes_alerta': int(stats['clientes_alerta']),
        'total_ocs_pendientes': float(stats['total_ocs_pendientes'])
    }

# ==================== INICIALIZACIÓN AUTOMÁTICA ====================

# Inicializar base de datos si no existe
if not os.path.exists('data/database.db'):
    print("🔧 Inicializando base de datos de Tododrogas...")
    init_db()
    print("✅ Base de datos lista con clientes reales")
