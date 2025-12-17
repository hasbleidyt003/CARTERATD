"""
Página de gestión de clientes para Streamlit
Versión corregida sin parámetro max_length
"""

import streamlit as st
import pandas as pd
import sqlite3
import sys
import os

# Configuración de ruta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def show():
    st.header("👥 Gestión de Clientes")
    
    try:
        # Intentar importar desde módulos
        from modules.database import get_clientes, actualizar_cliente, crear_cliente, agregar_movimiento
    except ImportError as e:
        st.warning(f"⚠️ Usando funciones locales: {e}")
        # Definir funciones locales como fallback
        def get_clientes():
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
        
        def actualizar_cliente(nit, cupo_sugerido=None, saldo_actual=None, nombre=None):
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            updates, params = [], []
            
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
                params.append(nit)
                query = f"UPDATE clientes SET {', '.join(updates)} WHERE nit = ?"
                cursor.execute(query, params)
                conn.commit()
            
            conn.close()
            return True
        
        def crear_cliente(nit, nombre, cupo_sugerido, saldo_actual=0):
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
                raise Exception(f"Ya existe cliente con NIT: {nit}")
            finally:
                conn.close()
        
        def agregar_movimiento(cliente_nit, tipo, valor, descripcion="", referencia="", usuario="Sistema"):
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO movimientos (cliente_nit, tipo, valor, descripcion, referencia, usuario)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (cliente_nit, tipo, valor, descripcion, referencia, usuario))
            if tipo == 'PAGO':
                cursor.execute('UPDATE clientes SET saldo_actual = saldo_actual - ? WHERE nit = ?', (valor, cliente_nit))
            conn.commit()
            conn.close()
            return True
    
    # Pestañas
    tab1, tab2 = st.tabs(["📋 Lista de Clientes", "➕ Nuevo Cliente"])
    
    with tab1:
        mostrar_clientes()
    
    with tab2:
        agregar_cliente()

def mostrar_clientes():
    """Muestra lista de clientes y permite editar"""
    try:
        from modules.database import get_clientes, actualizar_cliente, agregar_movimiento
        
        clientes = get_clientes()
        
        if not clientes.empty:
            st.subheader(f"📊 Total de Clientes: {len(clientes)}")
            
            # Mostrar estadísticas rápidas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Cupo Total", f"${clientes['cupo_sugerido'].sum():,.0f}")
            with col2:
                st.metric("Saldo Total", f"${clientes['saldo_actual'].sum():,.0f}")
            with col3:
                if 'estado' in clientes.columns:
                    sobrepasados = len(clientes[clientes['estado'] == 'SOBREPASADO'])
                    st.metric("Clientes Críticos", sobrepasados)
                else:
                    st.metric("Clientes", len(clientes))
            
            st.divider()
            
            # Formulario de edición para cada cliente
            for _, cliente in clientes.iterrows():
                with st.expander(f"{cliente['nombre']} (NIT: {cliente['nit']})", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        nuevo_nombre = st.text_input(
                            "Nombre",
                            value=cliente['nombre'],
                            key=f"nombre_{cliente['nit']}"
                        )
                        
                        nuevo_cupo = st.number_input(
                            "Cupo Sugerido",
                            value=float(cliente['cupo_sugerido']),
                            min_value=0.0,
                            step=1000000.0,
                            format="%.0f",
                            key=f"cupo_{cliente['nit']}"
                        )
                    
                    with col2:
                        nuevo_saldo = st.number_input(
                            "Saldo Actual",
                            value=float(cliente['saldo_actual']),
                            min_value=0.0,
                            step=1000000.0,
                            format="%.0f",
                            key=f"saldo_{cliente['nit']}"
                        )
                    
                    with col3:
                        # Mostrar estadísticas actuales
                        disponible = nuevo_cupo - nuevo_saldo
                        porcentaje_uso = (nuevo_saldo / nuevo_cupo * 100) if nuevo_cupo > 0 else 0
                        
                        st.metric("Disponible", f"${disponible:,.0f}")
                        st.metric("% Uso", f"{porcentaje_uso:.1f}%")
                        
                        # Determinar estado
                        estado = "NORMAL"
                        if disponible < 0:
                            estado = "SOBREPASADO"
                        elif porcentaje_uso > 80:
                            estado = "ALERTA"
                        
                        st.metric("Estado", estado)
                    
                    # Botones de acción
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        if st.button("💾 Guardar", key=f"guardar_{cliente['nit']}", use_container_width=True):
                            try:
                                actualizar_cliente(
                                    nit=cliente['nit'],
                                    cupo_sugerido=nuevo_cupo,
                                    saldo_actual=nuevo_saldo,
                                    nombre=nuevo_nombre
                                )
                                st.success("✅ Cambios guardados exitosamente")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al guardar: {str(e)}")
                    
                    with col_b:
                        if st.button("➕ Nuevo Pago", key=f"pago_{cliente['nit']}", use_container_width=True):
                            st.session_state.registrar_pago = cliente['nit']
                            st.rerun()
            
            # Formulario para registrar pago (si está activo)
            if 'registrar_pago' in st.session_state:
                with st.form(f"pago_form_{st.session_state.registrar_pago}"):
                    st.subheader(f"💳 Registrar Pago - NIT: {st.session_state.registrar_pago}")
                    
                    cliente_actual = clientes[clientes['nit'] == st.session_state.registrar_pago].iloc[0]
                    st.info(f"Saldo actual: ${cliente_actual['saldo_actual']:,.0f}")
                    
                    valor_pago = st.number_input(
                        "Valor del Pago",
                        min_value=0.0,
                        max_value=float(cliente_actual['saldo_actual']),
                        step=1000000.0,
                        format="%.0f"
                    )
                    descripcion = st.text_input("Descripción")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.form_submit_button("✅ Confirmar Pago"):
                            agregar_movimiento(
                                cliente_nit=st.session_state.registrar_pago,
                                tipo="PAGO",
                                valor=valor_pago,
                                descripcion=descripcion,
                                referencia=f"PAGO-{st.session_state.registrar_pago}"
                            )
                            st.success(f"✅ Pago de ${valor_pago:,.0f} registrado")
                            del st.session_state.registrar_pago
                            st.rerun()
                    
                    with col_btn2:
                        if st.form_submit_button("❌ Cancelar"):
                            del st.session_state.registrar_pago
                            st.rerun()
                            
        else:
            st.info("No hay clientes registrados. Agrega el primero en la pestaña 'Nuevo Cliente'.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar clientes: {str(e)}")
        st.code(f"Detalles: {e.__class__.__name__}")

def agregar_cliente():
    """Formulario para agregar nuevo cliente - CORREGIDO sin max_length"""
    st.subheader("➕ Agregar Nuevo Cliente")
    
    with st.form("nuevo_cliente_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nit = st.text_input("NIT *", help="Número de Identificación Tributaria")
            nombre = st.text_input("Nombre del Cliente *", help="Nombre completo o razón social")
        
        with col2:
            cupo_sugerido = st.number_input(
                "Cupo Sugerido Inicial *", 
                min_value=0.0,
                value=0.0,
                step=1000000.0,
                format="%.0f",
                help="Cupo de crédito sugerido"
            )
            saldo_actual = st.number_input(
                "Saldo Actual Inicial *",
                min_value=0.0,
                value=0.0,
                step=1000000.0,
                format="%.0f",
                help="Saldo inicial de cartera"
            )
        
        # Cálculos en tiempo real
        disponible = cupo_sugerido - saldo_actual
        porcentaje_uso = (saldo_actual / cupo_sugerido * 100) if cupo_sugerido > 0 else 0
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.metric("Disponible Inicial", f"${disponible:,.0f}")
        with col_info2:
            st.metric("% Uso Inicial", f"{porcentaje_uso:.1f}%")
        
        # Botón de envío
        submitted = st.form_submit_button(
            "💾 Crear Cliente", 
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            # Validar campos obligatorios
            if not nit or not nombre:
                st.error("❌ Los campos marcados con * son obligatorios")
                return
            
            if cupo_sugerido <= 0:
                st.error("❌ El cupo sugerido debe ser mayor a 0")
                return
            
            try:
                from modules.database import crear_cliente
                
                crear_cliente(
                    nit=nit,
                    nombre=nombre,
                    cupo_sugerido=cupo_sugerido,
                    saldo_actual=saldo_actual
                )
                
                st.success(f"✅ Cliente '{nombre}' creado exitosamente")
                st.balloons()
                
                # Mostrar resumen
                st.info(f"""
                **Resumen del cliente creado:**
                - NIT: {nit}
                - Nombre: {nombre}
                - Cupo Sugerido: ${cupo_sugerido:,.0f}
                - Saldo Actual: ${saldo_actual:,.0f}
                - Disponible: ${disponible:,.0f}
                - % Uso Inicial: {porcentaje_uso:.1f}%
                """)
                
                # Opción para agregar otro
                if st.button("➕ Agregar Otro Cliente"):
                    st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error al crear cliente: {str(e)}")

# Solo para pruebas locales
if __name__ == "__main__":
    show()


"""
Módulo de base de datos para Sistema de Cartera TD
Versión compatible con Streamlit - CORREGIDO
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
    # Crear carpeta data si no existe
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # Tabla de clientes (SIN columna estado)
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
    
    # Insertar datos de ejemplo si no existen
    cursor.execute("SELECT COUNT(*) FROM clientes")
    if cursor.fetchone()[0] == 0:
        clientes_ejemplo = [
            ('890905166', 'EMPRESA SOCIAL DEL ESTADO HOSPITAL MENTAL', 7500000000, 7397192942),
            ('900746052', 'NEURUM SAS', 5500000000, 5184247632),
            ('800241602', 'FUNDACION COLOMBIANA DE CANCEROLOGIA', 3500000000, 3031469552),
            ('890985122', 'COOPERATIVA DE HOSPITALES DE ANTIOQUIA', 1500000000, 1291931405),
            ('900099945', 'GLOBAL SERVICE PHARMACEUTICAL S.A.S.', 1200000000, 1009298565),
            ('811038014', 'GRUPO ONCOLOGICO INTERNACIONAL S.A.', 900000000, 806853666),
        ]
        
        for nit, nombre, cupo, saldo in clientes_ejemplo:
            cursor.execute('''
            INSERT INTO clientes (nit, nombre, cupo_sugerido, saldo_actual)
            VALUES (?, ?, ?, ?)
            ''', (nit, nombre, cupo, saldo))
        
        # Insertar OCs de ejemplo
        ocs_ejemplo = [
            ('890905166', 'OC-2024-001', 500000000, 'SUELTA'),
            ('900746052', 'OC-2024-002', 300000000, 'SUELTA'),
            ('800241602', 'OC-2024-003', 150000000, 'CUPO_NUEVO', 'CUPO-001'),
        ]
        
        for oc in ocs_ejemplo:
            if len(oc) == 4:
                nit, num_oc, valor, tipo = oc
                cupo_ref = ""
            else:
                nit, num_oc, valor, tipo, cupo_ref = oc
            
            cursor.execute('''
            INSERT INTO ocs (cliente_nit, numero_oc, valor_total, tipo, cupo_referencia)
            VALUES (?, ?, ?, ?, ?)
            ''', (nit, num_oc, valor, tipo, cupo_ref))
        
        print(f"✅ Insertados {len(clientes_ejemplo)} clientes de ejemplo")
    
    conn.commit()
    conn.close()
    return True

# ============================================================================
# FUNCIONES PARA CLIENTES (CORREGIDAS)
# ============================================================================

def get_clientes():
    """Obtiene todos los clientes activos - CORREGIDO SIN columna estado"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT 
        c.*,
        COALESCE(SUM(o.valor_pendiente), 0) as pendientes_total,
        -- Calcular porcentaje de uso dinámicamente
        CASE 
            WHEN c.cupo_sugerido > 0 
            THEN ROUND((c.saldo_actual * 100.0 / c.cupo_sugerido), 2)
            ELSE 0 
        END as porcentaje_uso,
        -- Calcular estado dinámicamente
        CASE 
            WHEN c.saldo_actual > c.cupo_sugerido THEN 'SOBREPASADO'
            WHEN c.saldo_actual > (c.cupo_sugerido * 0.8) THEN 'ALERTA'
            ELSE 'NORMAL'
        END as estado
    FROM clientes c
    LEFT JOIN ocs o ON c.nit = o.cliente_nit AND o.estado IN ('PENDIENTE', 'PARCIAL')
    WHERE c.activo = 1
    GROUP BY c.nit
    -- Ordenar por estado calculado y saldo
    ORDER BY 
        CASE 
            WHEN c.saldo_actual > c.cupo_sugerido THEN 1
            WHEN c.saldo_actual > (c.cupo_sugerido * 0.8) THEN 2
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
                THEN ROUND((c.saldo_actual * 100.0 / c.cupo_sugerido), 2)
                ELSE 0 
           END as porcentaje_uso,
           CASE 
                WHEN c.saldo_actual > c.cupo_sugerido THEN 'SOBREPASADO'
                WHEN c.saldo_actual > (c.cupo_sugerido * 0.8) THEN 'ALERTA'
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

def get_movimientos_recientes(limit=20):
    """Obtiene los movimientos más recientes de todos los clientes"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT m.*, c.nombre as cliente_nombre 
    FROM movimientos m
    JOIN clientes c ON m.cliente_nit = c.nit
    ORDER BY m.fecha_movimiento DESC
    LIMIT ?
    '''
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df

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
        SUM(disponible) as total_disponible,
        SUM(
            CASE 
                WHEN o.estado IN ('PENDIENTE', 'PARCIAL') 
                THEN o.valor_pendiente 
                ELSE 0 
            END
        ) as total_ocs_pendientes,
        -- Contar clientes en diferentes estados
        SUM(CASE WHEN saldo_actual > cupo_sugerido THEN 1 ELSE 0 END) as clientes_sobrepasados,
        SUM(CASE WHEN saldo_actual > (cupo_sugerido * 0.8) AND saldo_actual <= cupo_sugerido THEN 1 ELSE 0 END) as clientes_alerta
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
        'total_disponible': float(stats['total_disponible']),
        'total_ocs_pendientes': float(stats['total_ocs_pendientes']),
        'clientes_sobrepasados': int(stats['clientes_sobrepasados']),
        'clientes_alerta': int(stats['clientes_alerta'])
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
        ROUND((c.saldo_actual * 100.0 / c.cupo_sugerido), 2) as porcentaje_uso,
        CASE 
            WHEN c.saldo_actual > c.cupo_sugerido THEN 'SOBREPASADO'
            WHEN c.saldo_actual > (c.cupo_sugerido * 0.8) THEN 'ALERTA'
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

def get_resumen_cliente(nit):
    """Obtiene resumen completo de un cliente"""
    cliente = get_cliente_por_nit(nit)
    if not cliente:
        return None
    
    conn = sqlite3.connect('data/database.db')
    
    # Obtener OCs pendientes
    ocs_pendientes = pd.read_sql_query('''
    SELECT * FROM ocs 
    WHERE cliente_nit = ? AND estado IN ('PENDIENTE', 'PARCIAL')
    ORDER BY fecha_registro DESC
    ''', conn, params=(nit,))
    
    # Obtener últimos movimientos
    movimientos = pd.read_sql_query('''
    SELECT * FROM movimientos 
    WHERE cliente_nit = ? 
    ORDER BY fecha_movimiento DESC 
    LIMIT 10
    ''', conn, params=(nit,))
    
    conn.close()
    
    return {
        'cliente': cliente,
        'ocs_pendientes': ocs_pendientes,
        'movimientos': movimientos,
        'total_ocs_pendientes': ocs_pendientes['valor_pendiente'].sum() if not ocs_pendientes.empty else 0
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

def exportar_a_excel(ruta_archivo='data/backups/exportacion.xlsx'):
    """Exporta todos los datos a un archivo Excel"""
    datos = get_backup_data()
    
    with pd.ExcelWriter(ruta_archivo, engine='openpyxl') as writer:
        datos['clientes'].to_excel(writer, sheet_name='Clientes', index=False)
        datos['ocs'].to_excel(writer, sheet_name='OCs', index=False)
        datos['movimientos'].to_excel(writer, sheet_name='Movimientos', index=False)
        if not datos['autorizaciones'].empty:
            datos['autorizaciones'].to_excel(writer, sheet_name='Autorizaciones', index=False)
    
    return ruta_archivo

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

def buscar_ocs(termino, cliente_nit=None):
    """Busca OCs por número, referencia o comentarios"""
    conn = sqlite3.connect('data/database.db')
    
    if cliente_nit:
        query = '''
        SELECT o.*, c.nombre as cliente_nombre 
        FROM ocs o
        JOIN clientes c ON o.cliente_nit = c.nit
        WHERE (o.numero_oc LIKE ? OR o.cupo_referencia LIKE ? OR o.comentarios LIKE ?)
        AND o.cliente_nit = ?
        ORDER BY o.fecha_registro DESC
        LIMIT 20
        '''
        termino_busqueda = f"%{termino}%"
        df = pd.read_sql_query(query, conn, params=(termino_busqueda, termino_busqueda, termino_busqueda, cliente_nit))
    else:
        query = '''
        SELECT o.*, c.nombre as cliente_nombre 
        FROM ocs o
        JOIN clientes c ON o.cliente_nit = c.nit
        WHERE (o.numero_oc LIKE ? OR o.cupo_referencia LIKE ? OR o.comentarios LIKE ?)
        ORDER BY o.fecha_registro DESC
        LIMIT 20
        '''
        termino_busqueda = f"%{termino}%"
        df = pd.read_sql_query(query, conn, params=(termino_busqueda, termino_busqueda, termino_busqueda))
    
    conn.close()
    return df

# ============================================================================
# INICIALIZACIÓN AUTOMÁTICA
# ============================================================================

# Verificar si la base de datos existe e inicializar si es necesario
if __name__ == "__main__":
    # Ejecutar solo si se llama directamente
    if not os.path.exists('data/database.db'):
        print("🔧 Inicializando base de datos por primera vez...")
        init_db()
        print("✅ Base de datos lista para usar")
    else:
        print("✅ Base de datos ya existe")
