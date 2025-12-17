import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

# ============================================================================
# INICIALIZACIÓN DE BASE DE DATOS
# ============================================================================

def init_db():
    """Inicializa la base de datos si no existe"""
    # Crear carpeta data si no existe
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # Tabla de clientes (CON cartera_vencida)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nit TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        cupo_sugerido REAL DEFAULT 0,
        saldo_actual REAL DEFAULT 0,
        cartera_vencida REAL DEFAULT 0,
        disponible REAL GENERATED ALWAYS AS (cupo_sugerido - saldo_actual - cartera_vencida),
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
    
    # Insertar TUS CLIENTES REALES
    cursor.execute("SELECT COUNT(*) FROM clientes")
    if cursor.fetchone()[0] == 0:
        clientes_reales = [
            # NIT, Nombre, Cupo Sugerido, Saldo Actual, Cartera Vencida
            ('890905166', 'EMPRESA SOCIAL DEL ESTADO HOSPITAL MENTAL', 
             7500000000, 7397192942, 3342688638),
            ('900746052', 'NEURUM SAS', 
             5500000000, 5184247632, 2279333768),
            ('800241602', 'FUNDACION COLOMBIANA DE CANCEROLOGIA', 
             3500000000, 3031469552, 191990541),
            ('890985122', 'COOPERATIVA DE HOSPITALES DE ANTIOQUIA', 
             1500000000, 1291931405, 321889542),
            ('900099945', 'GLOBAL SERVICE PHARMACEUTICAL S.A.S.', 
             1200000000, 1009298565, 434808971),
            ('811038014', 'GRUPO ONCOLOGICO INTERNACIONAL S.A.', 
             900000000, 806853666, 146804409),
        ]
        
        for nit, nombre, cupo, saldo, cartera in clientes_reales:
            cursor.execute('''
            INSERT INTO clientes (nit, nombre, cupo_sugerido, saldo_actual, cartera_vencida)
            VALUES (?, ?, ?, ?, ?)
            ''', (nit, nombre, cupo, saldo, cartera))
        
        # Insertar pagos registrados
        pagos = [
            ('800241602', 'PAGO', 490000000, 'Pago reportado', 'PAGO-001'),
            ('900099945', 'PAGO', 68802510, 'Pago parcial', 'PAGO-002'),
            ('811038014', 'PAGO', 583783, 'Pago mínimo', 'PAGO-003'),
        ]
        
        for nit, tipo, valor, desc, ref in pagos:
            cursor.execute('''
            INSERT INTO movimientos (cliente_nit, tipo, valor, descripcion, referencia)
            VALUES (?, ?, ?, ?, ?)
            ''', (nit, tipo, valor, desc, ref))
        
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
        c.*,
        COALESCE(SUM(o.valor_pendiente), 0) as pendientes_total,
        -- Calcular porcentaje de uso
        CASE 
            WHEN c.cupo_sugerido > 0 
            THEN ROUND(((c.saldo_actual + c.cartera_vencida) * 100.0 / c.cupo_sugerido), 2)
            ELSE 0 
        END as porcentaje_uso,
        -- Calcular estado
        CASE 
            WHEN (c.saldo_actual + c.cartera_vencida) > c.cupo_sugerido THEN 'SOBREPASADO'
            WHEN (c.saldo_actual + c.cartera_vencida) > (c.cupo_sugerido * 0.8) THEN 'ALERTA'
            ELSE 'NORMAL'
        END as estado
    FROM clientes c
    LEFT JOIN ocs o ON c.nit = o.cliente_nit AND o.estado IN ('PENDIENTE', 'PARCIAL')
    WHERE c.activo = 1
    GROUP BY c.nit
    ORDER BY 
        CASE 
            WHEN (c.saldo_actual + c.cartera_vencida) > c.cupo_sugerido THEN 1
            WHEN (c.saldo_actual + c.cartera_vencida) > (c.cupo_sugerido * 0.8) THEN 2
            ELSE 3
        END,
        c.saldo_actual DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_cliente_por_nit(nit):
    """Obtiene un cliente específico por NIT"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT c.*,
           COALESCE(SUM(o.valor_pendiente), 0) as pendientes_total,
           CASE 
                WHEN c.cupo_sugerido > 0 
                THEN ROUND(((c.saldo_actual + c.cartera_vencida) * 100.0 / c.cupo_sugerido), 2)
                ELSE 0 
           END as porcentaje_uso,
           CASE 
                WHEN (c.saldo_actual + c.cartera_vencida) > c.cupo_sugerido THEN 'SOBREPASADO'
                WHEN (c.saldo_actual + c.cartera_vencida) > (c.cupo_sugerido * 0.8) THEN 'ALERTA'
                ELSE 'NORMAL'
           END as estado
    FROM clientes c
    LEFT JOIN ocs o ON c.nit = o.cliente_nit AND o.estado IN ('PENDIENTE', 'PARCIAL')
    WHERE c.nit = ? AND c.activo = 1
    GROUP BY c.nit
    '''
    df = pd.read_sql_query(query, conn, params=(nit,))
    conn.close()
    return df.iloc[0] if not df.empty else None

def actualizar_cliente(nit, cupo_sugerido=None, saldo_actual=None, cartera_vencida=None, nombre=None):
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
    
    if cartera_vencida is not None:
        updates.append("cartera_vencida = ?")
        params.append(cartera_vencida)
    
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

def crear_cliente(nit, nombre, cupo_sugerido, saldo_actual=0, cartera_vencida=0):
    """Crea un nuevo cliente"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO clientes (nit, nombre, cupo_sugerido, saldo_actual, cartera_vencida)
        VALUES (?, ?, ?, ?, ?)
        ''', (nit, nombre, cupo_sugerido, saldo_actual, cartera_vencida))
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        raise Exception(f"Ya existe un cliente con NIT: {nit}")
    except Exception as e:
        raise Exception(f"Error al crear cliente: {str(e)}")
    finally:
        conn.close()

def eliminar_cliente_logico(nit):
    """Elimina un cliente lógicamente"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE clientes 
    SET activo = 0, fecha_actualizacion = CURRENT_TIMESTAMP
    WHERE nit = ?
    ''', (nit,))
    
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

def get_movimientos_cliente(cliente_nit, limit=50):
    """Obtiene los movimientos de un cliente"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT * FROM movimientos 
    WHERE cliente_nit = ? 
    ORDER BY fecha_movimiento DESC
    LIMIT ?
    '''
    df = pd.read_sql_query(query, conn, params=(cliente_nit, limit))
    conn.close()
    return df

# ============================================================================
# FUNCIONES PARA OCs (COMPLETAS)
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
        params.append(cupo_referencia)
    
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
        cursor.execute('SELECT valor_autorizado, valor_total FROM ocs WHERE id = ?', (oc_id,))
        oc = cursor.fetchone()
        
        if not oc:
            raise Exception("OC no encontrada")
        
        valor_actual, valor_total = oc
        
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
# FUNCIONES DE REPORTES Y ESTADÍSTICAS
# ============================================================================

def get_estadisticas_generales():
    """Obtiene estadísticas generales del sistema"""
    conn = sqlite3.connect('data/database.db')
    
    query = '''
    SELECT 
        COUNT(*) as total_clientes,
        SUM(cupo_sugerido) as total_cupo_sugerido,
        SUM(saldo_actual) as total_saldo_actual,
        SUM(cartera_vencida) as total_cartera_vencida,
        SUM(disponible) as total_disponible,
        SUM(
            CASE 
                WHEN o.estado IN ('PENDIENTE', 'PARCIAL') 
                THEN o.valor_pendiente 
                ELSE 0 
            END
        ) as total_ocs_pendientes,
        -- Contar clientes en diferentes estados
        SUM(CASE WHEN (saldo_actual + cartera_vencida) > cupo_sugerido THEN 1 ELSE 0 END) as clientes_sobrepasados,
        SUM(CASE WHEN (saldo_actual + cartera_vencida) > (cupo_sugerido * 0.8) AND (saldo_actual + cartera_vencida) <= cupo_sugerido THEN 1 ELSE 0 END) as clientes_alerta
    FROM clientes c
    LEFT JOIN ocs o ON c.nit = o.cliente_nit
    WHERE c.activo = 1
    '''
    
    stats = pd.read_sql_query(query, conn).iloc[0]
    conn.close()
    
    return {
        'total_clientes': int(stats['total_clientes']),
        'total_cupo_sugerido': float(stats['total_cupo_sugerido']),
        'total_saldo_actual': float(stats['total_saldo_actual']),
        'total_cartera_vencida': float(stats['total_cartera_vencida']),
        'total_disponible': float(stats['total_disponible']),
        'total_ocs_pendientes': float(stats['total_ocs_pendientes']),
        'clientes_sobrepasados': int(stats['clientes_sobrepasados']),
        'clientes_alerta': int(stats['clientes_alerta'])
    }

# ============================================================================
# FUNCIONES DE MANTENIMIENTO Y BACKUP
# ============================================================================

def get_backup_data():
    """Obtiene todos los datos para backup"""
    conn = sqlite3.connect('data/database.db')
    
    datos = {
        'clientes': pd.read_sql_query("SELECT * FROM clientes", conn),
        'ocs': pd.read_sql_query("SELECT * FROM ocs", conn),
        'movimientos': pd.read_sql_query("SELECT * FROM movimientos", conn),
        'autorizaciones': pd.read_sql_query("SELECT * FROM autorizaciones_parciales", conn)
    }
    
    conn.close()
    return datos

def limpiar_ocs_antiguas(dias=90):
    """Elimina OCs autorizadas antiguas"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    fecha_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
    
    # Contar OCs a eliminar
    cursor.execute(f'''
    SELECT COUNT(*) FROM ocs 
    WHERE estado = 'AUTORIZADA'
    AND fecha_ultima_autorizacion < '{fecha_limite}'
    ''')
    count = cursor.fetchone()[0]
    
    # Eliminar autorizaciones primero
    cursor.execute(f'''
    DELETE FROM autorizaciones_parciales 
    WHERE oc_id IN (
        SELECT id FROM ocs 
        WHERE estado = 'AUTORIZADA'
        AND fecha_ultima_autorizacion < '{fecha_limite}'
    )
    ''')
    
    # Eliminar OCs
    cursor.execute(f'''
    DELETE FROM ocs 
    WHERE estado = 'AUTORIZADA'
    AND fecha_ultima_autorizacion < '{fecha_limite}'
    ''')
    
    conn.commit()
    conn.close()
    
    return count

def optimizar_base_datos():
    """Ejecuta VACUUM para optimizar la base de datos"""
    conn = sqlite3.connect('data/database.db')
    conn.execute("VACUUM")
    conn.close()
    return True

# ============================================================================
# FUNCIONES DE BÚSQUEDA
# ============================================================================

def buscar_clientes(termino):
    """Busca clientes por NIT o nombre"""
    conn = sqlite3.connect('data/database.db')
    
    query = '''
    SELECT * FROM clientes 
    WHERE (nit LIKE ? OR nombre LIKE ?) AND activo = 1
    ORDER BY nombre
    LIMIT 20
    '''
    
    termino_busqueda = f"%{termino}%"
    df = pd.read_sql_query(query, conn, params=(termino_busqueda, termino_busqueda))
    conn.close()
    return df

# ============================================================================
# INICIALIZACIÓN AUTOMÁTICA
# ============================================================================

if __name__ == "__main__":
    if not os.path.exists('data/database.db'):
        print("🔧 Inicializando base de datos...")
        init_db()
        print("✅ Base de datos lista")
