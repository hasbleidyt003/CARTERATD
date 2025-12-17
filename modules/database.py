import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

# ============================================================================
# INICIALIZACIÓN DE BASE DE DATOS CON LOS 7 CLIENTES REALES
# ============================================================================

def init_db():
    """Inicializa la base de datos con los 7 clientes reales"""
    # Crear carpeta data si no existe
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # Tabla de clientes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nit TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        cupo_sugerido REAL DEFAULT 0,
        saldo_actual REAL DEFAULT 0,
        disponible REAL GENERATED ALWAYS AS (cupo_sugerido - saldo_actual),
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        activo BOOLEAN DEFAULT 1
    )
    ''')
    
    # Tabla de movimientos/pagos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movimientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_nit TEXT,
        tipo TEXT NOT NULL,  -- PAGO, AJUSTE
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
        estado TEXT DEFAULT 'PENDIENTE',  -- PENDIENTE, PARCIAL, AUTORIZADA
        tipo TEXT DEFAULT 'SUELTA',       -- CUPO_NUEVO, SUELTA
        cupo_referencia TEXT,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_ultima_autorizacion TIMESTAMP,
        comentarios TEXT,
        FOREIGN KEY (cliente_nit) REFERENCES clientes(nit)
    )
    ''')
    
    # Tabla de autorizaciones parciales
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS autorizaciones_parciales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        oc_id INTEGER,
        valor_autorizado REAL NOT NULL,
        fecha_autorizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        comentario TEXT,
        usuario TEXT,
        FOREIGN KEY (oc_id) REFERENCES ocs(id)
    )
    ''')
    
    # Índices para mejor performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cliente_nit ON clientes(nit)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_oc_cliente ON ocs(cliente_nit)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_oc_estado ON ocs(estado)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_mov_cliente ON movimientos(cliente_nit)')
    
    # Insertar LOS 7 CLIENTES REALES
    cursor.execute("SELECT COUNT(*) FROM clientes")
    if cursor.fetchone()[0] == 0:
        clientes_reales = [
            # NIT, Nombre, Cupo Sugerido, Saldo Actual (Total Cartera)
            ('901212102', 'AUNA COLOMBIA S.A.S.', 21693849830, 19493849830),
            ('890905166', 'EMPRESA SOCIAL DEL ESTADO HOSPITAL MENTAL DE ANTIOQ', 7500000000, 7397192942),
            ('900249425', 'PHARMASAN S.A.S', 5910785209, 5710785209),
            ('900746052', 'NEURUM SAS', 5500000000, 5184247632),
            ('800241602', 'FUNDACION COLOMBIANA DE CANCEROLOGIA CLINICA VIDA', 3500000000, 3031469552),
            ('890985122', 'COOPERATIVA DE HOSPITALES DE ANTIOQUIA', 1500000000, 1291931405),
            ('811038014', 'GRUPO ONCOLOGICO INTERNACIONAL S.A.', 900000000, 806853666),
        ]
        
        for nit, nombre, cupo, saldo in clientes_reales:
            cursor.execute('''
            INSERT OR REPLACE INTO clientes (nit, nombre, cupo_sugerido, saldo_actual, activo)
            VALUES (?, ?, ?, ?, 1)
            ''', (nit, nombre, cupo, saldo))
        
        print(f"✅ Insertados {len(clientes_reales)} clientes reales")
    
    conn.commit()
    conn.close()
    return True

# ============================================================================
# FUNCIONES PARA CLIENTES
# ============================================================================

def get_clientes():
    """Obtiene todos los clientes activos"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT 
        nit,
        nombre,
        cupo_sugerido,
        saldo_actual,
        disponible,
        -- Calcular porcentaje de uso
        CASE 
            WHEN cupo_sugerido > 0 
            THEN ROUND((saldo_actual * 100.0 / cupo_sugerido), 1)
            ELSE 0 
        END as porcentaje_uso,
        -- Calcular estado
        CASE 
            WHEN saldo_actual > cupo_sugerido THEN 'SOBREPASADO'
            WHEN (saldo_actual * 100.0 / cupo_sugerido) > 80 THEN 'ALERTA'
            ELSE 'NORMAL'
        END as estado
    FROM clientes 
    WHERE activo = 1
    ORDER BY nombre
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_cliente_por_nit(nit):
    """Obtiene un cliente específico por NIT"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT 
        nit,
        nombre,
        cupo_sugerido,
        saldo_actual,
        disponible,
        CASE 
            WHEN cupo_sugerido > 0 
            THEN ROUND((saldo_actual * 100.0 / cupo_sugerido), 1)
            ELSE 0 
        END as porcentaje_uso,
        CASE 
            WHEN saldo_actual > cupo_sugerido THEN 'SOBREPASADO'
            WHEN (saldo_actual * 100.0 / cupo_sugerido) > 80 THEN 'ALERTA'
            ELSE 'NORMAL'
        END as estado
    FROM clientes 
    WHERE nit = ? AND activo = 1
    '''
    df = pd.read_sql_query(query, conn, params=(nit,))
    conn.close()
    return df.iloc[0] if not df.empty else None

def actualizar_cliente(nit, cupo_sugerido=None, saldo_actual=None, nombre=None):
    """Actualiza los datos de un cliente"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if cupo_sugerido is not None:
        updates.append("cupo_sugerido = ?")
        params.append(cupo_sugerido)
    
    if saldo_actual is not None:
        updates.append("saldo_actual = ?")
        params.append(saldo_actual)
    
    if nombre is not None:
        updates.append("nombre = ?")
        params.append(nombre)
    
    if updates:
        updates.append("fecha_actualizacion = CURRENT_TIMESTAMP")
        params.append(nit)
        
        query = f"UPDATE clientes SET {', '.join(updates)} WHERE nit = ?"
        cursor.execute(query, params)
        conn.commit()
    
    conn.close()
    return True

def crear_cliente(nit, nombre, cupo_sugerido, saldo_actual=0):
    """Crea un nuevo cliente"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO clientes (nit, nombre, cupo_sugerido, saldo_actual)
        VALUES (?, ?, ?, ?)
        ''', (nit, nombre, cupo_sugerido, saldo_actual))
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        raise Exception(f"Ya existe un cliente con NIT: {nit}")
    except Exception as e:
        raise Exception(f"Error al crear cliente: {str(e)}")
    finally:
        conn.close()

def actualizar_saldo_cliente(nit, valor):
    """Actualiza el saldo de un cliente (para autorizaciones de OCs)"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE clientes 
    SET saldo_actual = saldo_actual + ?, 
        fecha_actualizacion = CURRENT_TIMESTAMP
    WHERE nit = ?
    ''', (valor, nit))
    
    conn.commit()
    conn.close()
    return True

# ============================================================================
# FUNCIONES PARA MOVIMIENTOS
# ============================================================================

def agregar_movimiento(cliente_nit, tipo, valor, descripcion="", referencia="", usuario="Sistema"):
    """Registra un movimiento (pago, ajuste, etc.)"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        # Insertar movimiento
        cursor.execute('''
        INSERT INTO movimientos (cliente_nit, tipo, valor, descripcion, referencia, usuario)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (cliente_nit, tipo, valor, descripcion, referencia, usuario))
        
        # Si es un pago, actualizar saldo del cliente
        if tipo == 'PAGO':
            cursor.execute('''
            UPDATE clientes 
            SET saldo_actual = saldo_actual - ?, 
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE nit = ?
            ''', (valor, cliente_nit))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error al registrar movimiento: {str(e)}")
    finally:
        conn.close()

# ============================================================================
# FUNCIONES PARA OCs
# ============================================================================

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

def crear_oc(cliente_nit, numero_oc, valor_total, tipo="SUELTA", cupo_referencia="", comentarios=""):
    """Crea una nueva Orden de Compra"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO ocs (cliente_nit, numero_oc, valor_total, tipo, cupo_referencia, comentarios)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (cliente_nit, numero_oc, valor_total, tipo, cupo_referencia, comentarios))
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        raise Exception(f"Ya existe una OC con número: {numero_oc}")
    except Exception as e:
        raise Exception(f"Error al crear OC: {str(e)}")
    finally:
        conn.close()

def editar_oc(oc_id, numero_oc=None, valor_total=None, tipo=None, cupo_referencia=None, comentarios=None):
    """Edita una OC existente"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if numero_oc is not None:
        updates.append("numero_oc = ?")
        params.append(numero_oc)
    
    if valor_total is not None:
        updates.append("valor_total = ?")
        params.append(valor_total)
    
    if tipo is not None:
        updates.append("tipo = ?")
        params.append(tipo)
    
    if cupo_referencia is not None:
        updates.append("cupo_referencia = ?")
        params.append(cupo_reference)
    
    if comentarios is not None:
        updates.append("comentarios = ?")
        params.append(comentarios)
    
    if updates:
        params.append(oc_id)
        
        query = f"UPDATE ocs SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
    
    conn.close()
    return True

def eliminar_oc(oc_id):
    """Elimina una OC y sus autorizaciones asociadas"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        # Primero eliminar autorizaciones asociadas
        cursor.execute('DELETE FROM autorizaciones_parciales WHERE oc_id = ?', (oc_id,))
        
        # Luego eliminar la OC
        cursor.execute('DELETE FROM ocs WHERE id = ?', (oc_id,))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error al eliminar OC: {str(e)}")
    finally:
        conn.close()

def autorizar_oc(oc_id, valor_autorizado, comentario="", usuario="Sistema"):
    """Autoriza total o parcialmente una OC"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        # Obtener datos actuales de la OC
        cursor.execute('SELECT valor_autorizado, valor_total, cliente_nit FROM ocs WHERE id = ?', (oc_id,))
        oc = cursor.fetchone()
        
        if not oc:
            raise Exception("OC no encontrada")
        
        valor_actual, valor_total, cliente_nit = oc
        
        # Calcular nuevo valor autorizado
        nuevo_valor = valor_actual + valor_autorizado
        
        # Determinar estado
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
        INSERT INTO autorizaciones_parciales (oc_id, valor_autorizado, comentario, usuario)
        VALUES (?, ?, ?, ?)
        ''', (oc_id, valor_autorizado, comentario, usuario))
        
        # Actualizar saldo del cliente (aumenta porque es deuda)
        cursor.execute('''
        UPDATE clientes 
        SET saldo_actual = saldo_actual + ?, 
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE nit = ?
        ''', (valor_autorizado, cliente_nit))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error al autorizar OC: {str(e)}")
    finally:
        conn.close()

def get_oc_por_id(oc_id):
    """Obtiene una OC específica por su ID"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT o.*, c.nombre as cliente_nombre 
    FROM ocs o
    JOIN clientes c ON o.cliente_nit = c.nit
    WHERE o.id = ?
    '''
    df = pd.read_sql_query(query, conn, params=(oc_id,))
    conn.close()
    return df.iloc[0] if not df.empty else None

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

# ============================================================================
# FUNCIONES DE ESTADÍSTICAS
# ============================================================================

def get_estadisticas_generales():
    """Obtiene estadísticas generales del sistema"""
    conn = sqlite3.connect('data/database.db')
    
    query = '''
    SELECT 
        COUNT(*) as total_clientes,
        SUM(cupo_sugerido) as total_cupo_sugerido,
        SUM(saldo_actual) as total_saldo_actual,
        SUM(disponible) as total_disponible
    FROM clientes 
    WHERE activo = 1
    '''
    
    stats = pd.read_sql_query(query, conn).iloc[0]
    conn.close()
    
    # Calcular OCs pendientes
    ocs_pendientes = get_ocs_pendientes()
    total_pendientes = ocs_pendientes['valor_pendiente'].sum() if not ocs_pendientes.empty else 0
    
    return {
        'total_clientes': int(stats['total_clientes']),
        'total_cupo_sugerido': float(stats['total_cupo_sugerido']),
        'total_saldo_actual': float(stats['total_saldo_actual']),
        'total_disponible': float(stats['total_disponible']),
        'total_ocs_pendientes': float(total_pendientes)
    }

# ============================================================================
# INICIALIZACIÓN AUTOMÁTICA
# ============================================================================

if __name__ == "__main__":
    if not os.path.exists('data/database.db'):
        print("🔧 Inicializando base de datos...")
        init_db()
        print("✅ Base de datos lista")
