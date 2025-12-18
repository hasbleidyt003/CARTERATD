"""
MÓDULO DE BASE DE DATOS - SISTEMA TODODROGAS
Gestión completa de cupos y órdenes de compra
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
import json
import hashlib

# ==================== INICIALIZACIÓN ====================

def init_db():
    """Inicializa la base de datos con estructura completa"""
    
    # Crear carpetas necesarias
    os.makedirs('data', exist_ok=True)
    os.makedirs('data/backups', exist_ok=True)
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # ===== TABLA DE USUARIOS =====
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        nombre TEXT NOT NULL,
        rol TEXT DEFAULT 'usuario',  -- admin, usuario
        activo BOOLEAN DEFAULT 1,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ultimo_login TIMESTAMP
    )
    ''')
    
    # ===== TABLA DE CLIENTES =====
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nit TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        cupo_sugerido REAL DEFAULT 0,
        saldo_actual REAL DEFAULT 0,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        disponible REAL GENERATED ALWAYS AS (cupo_sugerido - saldo_actual),
        porcentaje_uso REAL GENERATED ALWAYS AS (
            CASE 
                WHEN cupo_sugerido > 0 
                THEN ROUND((saldo_actual * 100.0 / cupo_sugerido), 2)
                ELSE 0 
            END
        ),
        estado TEXT GENERATED ALWAYS AS (
            CASE
                WHEN saldo_actual > cupo_sugerido THEN 'SOBREPASADO'
                WHEN saldo_actual > (cupo_sugerido * 0.8) THEN 'ALERTA'
                ELSE 'NORMAL'
            END
        ),
        activo BOOLEAN DEFAULT 1,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # ===== TABLA DE ÓRDENES DE COMPRA =====
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ocs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_nit TEXT NOT NULL,
        numero_oc TEXT UNIQUE NOT NULL,
        valor_total REAL NOT NULL,
        valor_autorizado REAL DEFAULT 0,
        valor_pendiente REAL GENERATED ALWAYS AS (valor_total - valor_autorizado),
        estado TEXT DEFAULT 'PENDIENTE',
        tipo TEXT DEFAULT 'SUELTA',
        cupo_referencia TEXT,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_ultima_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_ultima_autorizacion TIMESTAMP,
        comentarios TEXT,
        creado_por TEXT DEFAULT 'Sistema',
        FOREIGN KEY (cliente_nit) REFERENCES clientes(nit)
    )
    ''')
    
    # ===== TABLA DE AUTORIZACIONES =====
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS autorizaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        oc_id INTEGER NOT NULL,
        valor_autorizado REAL NOT NULL,
        fecha_autorizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        comentario TEXT,
        autorizado_por TEXT DEFAULT 'Sistema',
        FOREIGN KEY (oc_id) REFERENCES ocs(id)
    )
    ''')
    
    # ===== TABLA DE HISTORIAL =====
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS historial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tabla TEXT NOT NULL,
        accion TEXT NOT NULL,
        registro_id INTEGER,
        datos_anteriores TEXT,
        datos_nuevos TEXT,
        fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        usuario TEXT DEFAULT 'Sistema'
    )
    ''')
    
    # ===== ÍNDICES =====
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cliente_nit ON clientes(nit)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_oc_cliente ON ocs(cliente_nit)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_oc_estado ON ocs(estado)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_oc_numero ON ocs(numero_oc)')
    
    # ===== DATOS INICIALES =====
    
    # Verificar si ya existen usuarios
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        # Crear usuario administrador (contraseña: admin123)
        admin_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
        INSERT INTO usuarios (username, password_hash, nombre, rol)
        VALUES (?, ?, ?, ?)
        ''', ('admin', admin_hash, 'Administrador Principal', 'admin'))
        
        # Crear usuario cartera (contraseña: cartera123)
        cartera_hash = hashlib.sha256('cartera123'.encode()).hexdigest()
        cursor.execute('''
        INSERT INTO usuarios (username, password_hash, nombre, rol)
        VALUES (?, ?, ?, ?)
        ''', ('cartera', cartera_hash, 'Gestor de Cartera', 'usuario'))
    
    # Verificar si ya existen clientes
    cursor.execute("SELECT COUNT(*) FROM clientes")
    if cursor.fetchone()[0] == 0:
        # Insertar CLIENTES REALES de Tododrogas
        clientes_reales = [
            ('901212102', 'AUNA COLOMBIA S.A.S', 21693849830, 19493849830),
            ('890905166', 'EMPRESA SOCIAL DEL ESTADO HOSPITAL MENTAL DE ANTIOQUIA', 7500000000, 7397192942),
            ('900249425', 'PHARMASAN S.A.S', 5910785209, 5710785209),
            ('900748052', 'NEUROM SAS', 5500000000, 5184247623),
            ('800241602', 'FUNDACION COLOMBIANA DE CANCEROLOGIA CLINICA VIDA', 3500000000, 3031469552),
            ('890985122', 'COOPERATIVA DE HOSPITALES DE ANTIOQUIA', 1500000000, 1221931405),
            ('811038014', 'GRUPO ONCOLOGICO INTERNACIONAL S.A.', 900000000, 806853666)
        ]
        
        for nit, nombre, cupo_sugerido, saldo_actual in clientes_reales:
            cursor.execute('''
            INSERT INTO clientes (nit, nombre, cupo_sugerido, saldo_actual)
            VALUES (?, ?, ?, ?)
            ''', (nit, nombre, cupo_sugerido, saldo_actual))
        
        print(f"✅ Insertados {len(clientes_reales)} clientes reales")
    
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada correctamente")
    return True

# ==================== FUNCIONES PARA USUARIOS ====================

def get_usuarios():
    """Obtiene todos los usuarios activos"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT id, username, nombre, rol, activo, fecha_creacion, ultimo_login
    FROM usuarios
    ORDER BY fecha_creacion DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def crear_usuario(username, password, nombre, rol='usuario'):
    """Crea un nuevo usuario"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        # Encriptar contraseña
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
        INSERT INTO usuarios (username, password_hash, nombre, rol)
        VALUES (?, ?, ?, ?)
        ''', (username, password_hash, nombre, rol))
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        raise Exception(f"El usuario '{username}' ya existe")
    except Exception as e:
        raise Exception(f"Error al crear usuario: {str(e)}")
    finally:
        conn.close()

# ==================== FUNCIONES PARA CLIENTES ====================

def get_clientes():
    """Obtiene todos los clientes activos"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT 
        c.*,
        COALESCE(SUM(o.valor_pendiente), 0) as ocs_pendientes
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
    SELECT c.*,
        COALESCE(SUM(o.valor_pendiente), 0) as ocs_pendientes
    FROM clientes c
    LEFT JOIN ocs o ON c.nit = o.cliente_nit AND o.estado IN ('PENDIENTE', 'PARCIAL')
    WHERE c.nit = ? AND c.activo = 1
    GROUP BY c.nit
    '''
    df = pd.read_sql_query(query, conn, params=(nit,))
    conn.close()
    return df.iloc[0] if not df.empty else None

def actualizar_cupo_cliente(nit, nuevo_cupo, usuario="Sistema"):
    """Actualiza el cupo sugerido de un cliente"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        # Obtener datos anteriores
        cursor.execute("SELECT cupo_sugerido, nombre FROM clientes WHERE nit = ?", (nit,))
        resultado = cursor.fetchone()
        if not resultado:
            raise Exception("Cliente no encontrado")
        
        cupo_anterior, nombre_cliente = resultado
        
        # Actualizar cupo
        cursor.execute('''
        UPDATE clientes 
        SET cupo_sugerido = ?, fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE nit = ?
        ''', (nuevo_cupo, nit))
        
        # Registrar en historial
        cursor.execute('''
        INSERT INTO historial (tabla, accion, registro_id, datos_anteriores, datos_nuevos, usuario)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ('clientes', 'ACTUALIZAR_CUPO', nit, 
              json.dumps({'cupo_sugerido': cupo_anterior}),
              json.dumps({'cupo_sugerido': nuevo_cupo}),
              usuario))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error al actualizar cupo: {str(e)}")
    finally:
        conn.close()

# ==================== FUNCIONES PARA OCs ====================

def crear_oc(cliente_nit, numero_oc, valor_total, tipo="SUELTA", 
             cupo_referencia="", comentarios="", usuario="Sistema"):
    """Crea una nueva Orden de Compra"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        # Verificar que el cliente existe
        cursor.execute("SELECT nombre FROM clientes WHERE nit = ? AND activo = 1", (cliente_nit,))
        if not cursor.fetchone():
            raise Exception("Cliente no encontrado o inactivo")
        
        # Crear la OC
        cursor.execute('''
        INSERT INTO ocs 
        (cliente_nit, numero_oc, valor_total, tipo, cupo_referencia, comentarios, creado_por)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (cliente_nit, numero_oc, valor_total, tipo, cupo_referencia, comentarios, usuario))
        
        # Registrar en historial
        cursor.execute('''
        INSERT INTO historial (tabla, accion, registro_id, datos_nuevos, usuario)
        VALUES (?, ?, ?, ?, ?)
        ''', ('ocs', 'CREAR', numero_oc,
              json.dumps({
                  'cliente_nit': cliente_nit,
                  'valor_total': valor_total,
                  'tipo': tipo,
                  'comentarios': comentarios
              }),
              usuario))
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        raise Exception(f"Ya existe una OC con número: {numero_oc}")
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error al crear OC: {str(e)}")
    finally:
        conn.close()

def get_ocs(cliente_nit=None, estado=None):
    """Obtiene OCs con filtros opcionales"""
    conn = sqlite3.connect('data/database.db')
    
    where_clauses = []
    params = []
    
    if cliente_nit:
        where_clauses.append("o.cliente_nit = ?")
        params.append(cliente_nit)
    
    if estado and estado != 'TODAS':
        where_clauses.append("o.estado = ?")
        params.append(estado)
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    query = f'''
    SELECT 
        o.*,
        c.nombre as cliente_nombre,
        c.cupo_sugerido as cliente_cupo,
        c.saldo_actual as cliente_saldo
    FROM ocs o
    JOIN clientes c ON o.cliente_nit = c.nit
    WHERE {where_sql}
    ORDER BY o.fecha_registro DESC
    '''
    
    df = pd.read_sql_query(query, conn, params=params if params else ())
    conn.close()
    return df

def autorizar_oc(oc_id, valor_autorizado, comentario="", usuario="Sistema"):
    """Autoriza total o parcialmente una OC"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        # Obtener datos actuales de la OC
        cursor.execute('''
        SELECT o.valor_autorizado, o.valor_total, o.cliente_nit, c.saldo_actual
        FROM ocs o
        JOIN clientes c ON o.cliente_nit = c.nit
        WHERE o.id = ?
        ''', (oc_id,))
        
        resultado = cursor.fetchone()
        if not resultado:
            raise Exception("OC no encontrada")
        
        valor_actual, valor_total, cliente_nit, saldo_cliente = resultado
        
        # Validar que no exceda el valor total
        nuevo_valor_autorizado = valor_actual + valor_autorizado
        if nuevo_valor_autorizado > valor_total:
            raise Exception(f"Valor a autorizar ({valor_autorizado:,.0f}) excede el pendiente ({valor_total - valor_actual:,.0f})")
        
        # Determinar nuevo estado
        if nuevo_valor_autorizado >= valor_total:
            estado = 'AUTORIZADA'
        elif nuevo_valor_autorizado > 0:
            estado = 'PARCIAL'
        else:
            estado = 'PENDIENTE'
        
        # Actualizar OC
        cursor.execute('''
        UPDATE ocs 
        SET valor_autorizado = ?, 
            estado = ?,
            fecha_ultima_autorizacion = CURRENT_TIMESTAMP,
            fecha_ultima_modificacion = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (nuevo_valor_autorizado, estado, oc_id))
        
        # Actualizar saldo del cliente
        cursor.execute('''
        UPDATE clientes 
        SET saldo_actual = saldo_actual + ?,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE nit = ?
        ''', (valor_autorizado, cliente_nit))
        
        # Registrar autorización
        cursor.execute('''
        INSERT INTO autorizaciones (oc_id, valor_autorizado, comentario, autorizado_por)
        VALUES (?, ?, ?, ?)
        ''', (oc_id, valor_autorizado, comentario, usuario))
        
        # Registrar en historial
        cursor.execute('''
        INSERT INTO historial (tabla, accion, registro_id, datos_anteriores, datos_nuevos, usuario)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ('ocs', 'AUTORIZAR', oc_id,
              json.dumps({
                  'valor_autorizado_anterior': valor_actual,
                  'estado_anterior': 'PENDIENTE' if valor_actual == 0 else 'PARCIAL'
              }),
              json.dumps({
                  'valor_autorizado_nuevo': nuevo_valor_autorizado,
                  'estado_nuevo': estado,
                  'valor_autorizado': valor_autorizado
              }),
              usuario))
        
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
    SELECT * FROM autorizaciones
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
        COUNT(DISTINCT c.nit) as total_clientes,
        SUM(c.cupo_sugerido) as total_cupo,
        SUM(c.saldo_actual) as total_en_uso,
        SUM(c.disponible) as total_disponible,
        COUNT(CASE WHEN c.estado = 'SOBREPASADO' THEN 1 END) as clientes_sobrepasados,
        COUNT(CASE WHEN c.estado = 'ALERTA' THEN 1 END) as clientes_alerta,
        COUNT(CASE WHEN c.estado = 'NORMAL' THEN 1 END) as clientes_normal,
        SUM(CASE WHEN o.estado IN ('PENDIENTE', 'PARCIAL') THEN o.valor_pendiente ELSE 0 END) as total_ocs_pendientes,
        COUNT(DISTINCT CASE WHEN o.estado IN ('PENDIENTE', 'PARCIAL') THEN o.id END) as cantidad_ocs_pendientes
    FROM clientes c
    LEFT JOIN ocs o ON c.nit = o.cliente_nit
    WHERE c.activo = 1
    '''
    
    stats = pd.read_sql_query(query, conn).iloc[0]
    conn.close()
    
    return {
        'total_clientes': int(stats['total_clientes']),
        'total_cupo': float(stats['total_cupo']),
        'total_en_uso': float(stats['total_en_uso']),
        'total_disponible': float(stats['total_disponible']),
        'clientes_sobrepasados': int(stats['clientes_sobrepasados']),
        'clientes_alerta': int(stats['clientes_alerta']),
        'clientes_normal': int(stats['clientes_normal']),
        'total_ocs_pendientes': float(stats['total_ocs_pendientes']),
        'cantidad_ocs_pendientes': int(stats['cantidad_ocs_pendientes'])
    }

def get_estadisticas_por_cliente():
    """Obtiene estadísticas detalladas por cliente"""
    conn = sqlite3.connect('data/database.db')
    
    query = '''
    SELECT
        c.nit,
        c.nombre,
        c.cupo_sugerido,
        c.saldo_actual,
        c.disponible,
        c.porcentaje_uso,
        c.estado,
        COALESCE(SUM(CASE WHEN o.estado IN ('PENDIENTE', 'PARCIAL') THEN o.valor_pendiente ELSE 0 END), 0) as ocs_pendientes,
        COUNT(o.id) as total_ocs,
        COUNT(CASE WHEN o.estado = 'AUTORIZADA' THEN 1 END) as ocs_autorizadas
    FROM clientes c
    LEFT JOIN ocs o ON c.nit = o.cliente_nit
    WHERE c.activo = 1
    GROUP BY c.nit
    ORDER BY c.saldo_actual DESC
    '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ==================== FUNCIONES DE EXPORTACIÓN ====================

def exportar_datos_a_excel():
    """Exporta todos los datos a un archivo Excel"""
    conn = sqlite3.connect('data/database.db')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta_archivo = f'data/backups/exportacion_{timestamp}.xlsx'
    
    with pd.ExcelWriter(ruta_archivo, engine='openpyxl') as writer:
        # Exportar clientes
        clientes_df = get_clientes()
        clientes_df.to_excel(writer, sheet_name='Clientes', index=False)
        
        # Exportar OCs
        ocs_df = get_ocs()
        ocs_df.to_excel(writer, sheet_name='OCs', index=False)
        
        # Exportar usuarios
        usuarios_df = get_usuarios()
        usuarios_df.to_excel(writer, sheet_name='Usuarios', index=False)
    
    conn.close()
    return ruta_archivo

# ==================== INICIALIZACIÓN AUTOMÁTICA ====================

# Inicializar base de datos si no existe
if not os.path.exists('data/database.db'):
    print("🔧 Inicializando base de datos...")
    init_db()
else:
    print("✅ Base de datos ya existe")
