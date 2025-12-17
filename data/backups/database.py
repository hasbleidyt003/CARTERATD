import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

def init_db():
    """Inicializa la base de datos si no existe"""
    
    # Crear carpetas necesarias
    os.makedirs('data', exist_ok=True)
    os.makedirs('data/backups', exist_ok=True)
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # Tabla de clientes (ACTUALIZADA con nuevos campos)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nit TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        cupo_actual REAL DEFAULT 0,
        saldo_actual REAL DEFAULT 0,
        cupo_sugerido REAL DEFAULT 0,
        cartera_vencida REAL DEFAULT 0,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        disponible REAL GENERATED ALWAYS AS (cupo_sugerido - saldo_actual - cartera_vencida),
        porcentaje_uso REAL GENERATED ALWAYS AS (ROUND((saldo_actual * 100.0 / cupo_sugerido), 2)),
        estado TEXT GENERATED ALWAYS AS (
            CASE 
                WHEN (saldo_actual + cartera_vencida) > cupo_sugerido THEN 'SOBREPASADO'
                WHEN (saldo_actual + cartera_vencida) > (cupo_sugerido * 0.8) THEN 'ALERTA'
                ELSE 'NORMAL'
            END
        ),
        activo BOOLEAN DEFAULT 1
    )
    ''')
    
    # Tabla de OCs (actualizada)
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
    
    # Tabla de movimientos/pagos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movimientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_nit TEXT,
        tipo TEXT NOT NULL,  -- PAGO, AJUSTE, NOTA_CREDITO, NOTA_DEBITO
        valor REAL NOT NULL,
        fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        descripcion TEXT,
        referencia TEXT,
        usuario TEXT,
        FOREIGN KEY (cliente_nit) REFERENCES clientes(nit)
    )
    ''')
    
    # Insertar TUS CLIENTES REALES (valores en pesos colombianos)
    cursor.execute("SELECT COUNT(*) FROM clientes")
    if cursor.fetchone()[0] == 0:
        clientes_reales = [
            # NIT, Nombre, Cupo Actual, Saldo Actual, Cupo Sugerido, Cartera Vencida
            ('890905166', 'EMPRESA SOCIAL DEL ESTADO HOSPITAL MENTAL', 
             4000000000, 7397192942, 7500000000, 3342688638),
            ('900746052', 'NEURUM SAS', 
             3500000000, 5184247632, 5500000000, 2279333768),
            ('800241602', 'FUNDACION COLOMBIANA DE CANCEROLOGIA', 
             2500000000, 3031469552, 3500000000, 191990541),
            ('890985122', 'COOPERATIVA DE HOSPITALES DE ANTIOQUIA', 
             800000000, 1291931405, 1500000000, 321889542),
            ('900099945', 'GLOBAL SERVICE PHARMACEUTICAL S.A.S.', 
             1000000000, 1009298565, 1200000000, 434808971),
            ('811038014', 'GRUPO ONCOLOGICO INTERNACIONAL S.A.', 
             800000000, 806853666, 900000000, 146804409),
        ]
        
        for nit, nombre, cupo_actual, saldo_actual, cupo_sugerido, cartera_vencida in clientes_reales:
            cursor.execute('''
            INSERT INTO clientes 
            (nit, nombre, cupo_actual, saldo_actual, cupo_sugerido, cartera_vencida, fecha_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (nit, nombre, cupo_actual, saldo_actual, cupo_sugerido, cartera_vencida))
        
        print(f"✅ Insertados {len(clientes_reales)} clientes reales")
        
        # Insertar algunas OCs de ejemplo para pruebas
        ocs_ejemplo = [
            ('890905166', 'OC-2024-001', 500000000, 'PENDIENTE', 'SUELTA'),
            ('900746052', 'OC-2024-002', 300000000, 'PARCIAL', 'SUELTA'),
            ('800241602', 'OC-2024-003', 150000000, 'PENDIENTE', 'SUELTA'),
            ('890985122', 'OC-2024-004', 80000000, 'AUTORIZADA', 'SUELTA'),
        ]
        
        for nit, num_oc, valor, estado, tipo in ocs_ejemplo:
            cursor.execute('''
            INSERT INTO ocs (cliente_nit, numero_oc, valor_total, estado, tipo)
            VALUES (?, ?, ?, ?, ?)
            ''', (nit, num_oc, valor, estado, tipo))
        
        # Insertar pagos registrados
        pagos = [
            ('800241602', 'PAGO', 490000000, 'Pago reportado en tabla', 'PAGO-001'),
            ('900099945', 'PAGO', 68802510, 'Pago parcial', 'PAGO-002'),
            ('811038014', 'PAGO', 583783, 'Pago mínimo', 'PAGO-003'),
        ]
        
        for nit, tipo, valor, desc, ref in pagos:
            cursor.execute('''
            INSERT INTO movimientos (cliente_nit, tipo, valor, descripcion, referencia)
            VALUES (?, ?, ?, ?, ?)
            ''', (nit, tipo, valor, desc, ref))
    
    # Crear índices para mejor performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cliente_nit ON clientes(nit)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_oc_cliente ON ocs(cliente_nit)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_oc_estado ON ocs(estado)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_mov_cliente ON movimientos(cliente_nit)')
    
    conn.commit()
    conn.close()
    
    print("✅ Base de datos inicializada con clientes reales")

# Funciones CRUD actualizadas
def get_clientes():
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT 
        c.*,
        COALESCE(SUM(o.valor_pendiente), 0) as pendientes_total,
        COALESCE(SUM(CASE WHEN o.estado IN ('PENDIENTE', 'PARCIAL') THEN o.valor_pendiente ELSE 0 END), 0) as pendientes_activos
    FROM clientes c
    LEFT JOIN ocs o ON c.nit = o.cliente_nit
    WHERE c.activo = 1
    GROUP BY c.nit
    ORDER BY c.estado DESC, c.saldo_actual DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_cliente_por_nit(nit):
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT c.*,
           COALESCE(SUM(o.valor_pendiente), 0) as pendientes_total
    FROM clientes c
    LEFT JOIN ocs o ON c.nit = o.cliente_nit AND o.estado IN ('PENDIENTE', 'PARCIAL')
    WHERE c.nit = ?
    GROUP BY c.nit
    '''
    df = pd.read_sql_query(query, conn, params=(nit,))
    conn.close()
    return df.iloc[0] if not df.empty else None

def actualizar_cliente(nit, cupo_sugerido=None, saldo_actual=None, cartera_vencida=None):
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
    
    if updates:
        updates.append("fecha_actualizacion = CURRENT_TIMESTAMP")
        params.append(nit)
        
        query = f"UPDATE clientes SET {', '.join(updates)} WHERE nit = ?"
        cursor.execute(query, params)
        conn.commit()
    
    conn.close()

def agregar_movimiento(cliente_nit, tipo, valor, descripcion="", referencia="", usuario="Sistema"):
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
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
    conn.close()

# Resto de funciones permanecen similares...
