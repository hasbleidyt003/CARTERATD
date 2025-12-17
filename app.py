import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import os
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

# ================= CONFIGURACIÓN =================
st.set_page_config(
    page_title="Control de Cupos - Medicamentos",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= BASE DE DATOS =================
def init_db():
    """Inicializa la base de datos SQLite"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Tabla de clientes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nit TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        cupo_sugerido REAL DEFAULT 0,
        saldo_actual REAL DEFAULT 0,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        activo BOOLEAN DEFAULT 1
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
        estado TEXT DEFAULT 'PENDIENTE',
        tipo TEXT DEFAULT 'SUELTA',
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
    
    # Índices
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cliente_nit ON clientes(nit)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_oc_cliente ON ocs(cliente_nit)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_oc_estado ON ocs(estado)')
    
    conn.commit()
    conn.close()

# ================= FUNCIONES BD =================
def get_clientes():
    conn = sqlite3.connect('database.db')
    query = '''
    SELECT 
        c.*,
        (c.cupo_sugerido - c.saldo_actual) as disponible,
        COALESCE(SUM(o.valor_total - o.valor_autorizado), 0) as pendientes_total
    FROM clientes c
    LEFT JOIN ocs o ON c.nit = o.cliente_nit AND o.estado IN ('PENDIENTE', 'PARCIAL')
    WHERE c.activo = 1
    GROUP BY c.nit
    ORDER BY c.nombre
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_ocs(cliente_nit=None):
    conn = sqlite3.connect('database.db')
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

# ================= AUTENTICACIÓN =================
USUARIOS = {
    "cartera": "admin123",
    "viewer": "view123"
}

def login_page():
    """Página de login"""
    st.markdown("""
    <div style='text-align: center; padding: 50px;'>
        <h1>💊 Control de Cupos</h1>
        <h3>Sistema de Seguimiento - Medicamentos</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("🔐 Acceso al Sistema")
            
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            
            submitted = st.form_submit_button("Ingresar", use_container_width=True)
            
            if submitted:
                if username in USUARIOS and USUARIOS[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")

# ================= DASHBOARD =================
def dashboard_page():
    """Dashboard principal"""
    st.header("📊 Dashboard de Control")
    
    clientes = get_clientes()
    ocs = get_ocs()
    pendientes = ocs[ocs['estado'].isin(['PENDIENTE', 'PARCIAL'])]
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cupo = clientes['cupo_sugerido'].sum()
        st.metric("Cupo Total", f"${total_cupo:,.0f}")
    
    with col2:
        total_pendientes = pendientes['valor_total'].sum() - pendientes['valor_autorizado'].sum()
        st.metric("Pendientes Total", f"${total_pendientes:,.0f}")
    
    with col3:
        clientes_alerta = len(clientes[clientes['cupo_sugerido'] - clientes['saldo_actual'] < 0])
        st.metric("Clientes en Alerta", clientes_alerta)
    
    with col4:
        ocs_parciales = len(pendientes[pendientes['estado'] == 'PARCIAL'])
        st.metric("OCs Parciales", ocs_parciales)
    
    st.divider()
    
    # Tabla de clientes
    st.subheader("🏥 Estado de Clientes")
    
    if not clientes.empty:
        display_df = clientes.copy()
        display_df['disponible_real'] = display_df['disponible'] - display_df['pendientes_total']
        
        for col in ['cupo_sugerido', 'saldo_actual', 'disponible', 'pendientes_total', 'disponible_real']:
            display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
        
        st.dataframe(
            display_df[['nit', 'nombre', 'cupo_sugerido', 'saldo_actual', 
                       'pendientes_total', 'disponible_real']],
            column_config={
                "nit": "NIT",
                "nombre": "Cliente",
                "cupo_sugerido": "Cupo Sugerido",
                "saldo_actual": "Saldo Actual",
                "pendientes_total": "Pendientes",
                "disponible_real": "Disponible Real"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No hay clientes registrados")

# ================= CLIENTES =================
def clientes_page():
    """Gestión de clientes"""
    st.header("👥 Gestión de Clientes")
    
    tab1, tab2 = st.tabs(["📋 Lista de Clientes", "➕ Nuevo Cliente"])
    
    with tab1:
        clientes = get_clientes()
        if not clientes.empty:
            for _, cliente in clientes.iterrows():
                with st.expander(f"{cliente['nombre']} (NIT: {cliente['nit']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        nuevo_cupo = st.number_input(
                            "Cupo Sugerido",
                            value=float(cliente['cupo_sugerido']),
                            key=f"cupo_{cliente['nit']}"
                        )
                    with col2:
                        nuevo_saldo = st.number_input(
                            "Saldo Actual",
                            value=float(cliente['saldo_actual']),
                            key=f"saldo_{cliente['nit']}"
                        )
                    
                    if st.button("💾 Guardar", key=f"guardar_{cliente['nit']}"):
                        conn = sqlite3.connect('database.db')
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE clientes 
                            SET cupo_sugerido = ?, saldo_actual = ?, fecha_actualizacion = ?
                            WHERE nit = ?
                        ''', (nuevo_cupo, nuevo_saldo, datetime.now(), cliente['nit']))
                        conn.commit()
                        conn.close()
                        st.success("✅ Datos actualizados")
                        st.rerun()
        else:
            st.info("No hay clientes registrados")
    
    with tab2:
        with st.form("nuevo_cliente"):
            col1, col2 = st.columns(2)
            with col1:
                nit = st.text_input("NIT *")
                nombre = st.text_input("Nombre del Cliente *")
            with col2:
                cupo_sugerido = st.number_input("Cupo Sugerido Inicial *", min_value=0.0, value=0.0)
                saldo_actual = st.number_input("Saldo Actual Inicial *", min_value=0.0, value=0.0)
            
            if st.form_submit_button("💾 Crear Cliente", use_container_width=True):
                if nit and nombre:
                    conn = sqlite3.connect('database.db')
                    cursor = conn.cursor()
                    try:
                        cursor.execute('''
                            INSERT INTO clientes (nit, nombre, cupo_sugerido, saldo_actual)
                            VALUES (?, ?, ?, ?)
                        ''', (nit, nombre, cupo_sugerido, saldo_actual))
                        conn.commit()
                        st.success(f"✅ Cliente '{nombre}' creado")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ Ya existe un cliente con ese NIT")
                    finally:
                        conn.close()
                else:
                    st.error("❌ Complete los campos obligatorios (*)")

# ================= OCs =================
def ocs_page():
    """Gestión de OCs"""
    st.header("📋 Gestión de Órdenes de Compra")
    
    # Filtros
    clientes = get_clientes()
    cliente_lista = ["Todos"] + clientes['nombre'].tolist()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_cliente = st.selectbox("Filtrar por Cliente", cliente_lista)
    with col2:
        filtro_estado = st.selectbox("Filtrar por Estado", ["Todos", "PENDIENTE", "PARCIAL", "AUTORIZADA"])
    with col3:
        filtro_tipo = st.selectbox("Filtrar por Tipo", ["Todos", "CUPO_NUEVO", "SUELTA"])
    
    # Obtener y filtrar OCs
    ocs = get_ocs()
    
    if filtro_cliente != "Todos":
        cliente_nit = clientes[clientes['nombre'] == filtro_cliente]['nit'].iloc[0]
        ocs = ocs[ocs['cliente_nit'] == cliente_nit]
    
    if filtro_estado != "Todos":
        ocs = ocs[ocs['estado'] == filtro_estado]
    
    if filtro_tipo != "Todos":
        ocs = ocs[ocs['tipo'] == filtro_tipo]
    
    # Mostrar OCs
    if not ocs.empty:
        for _, oc in ocs.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.subheader(f"📄 {oc['numero_oc']}")
                    st.caption(f"Cliente: {oc['cliente_nombre']}")
                    
                    if oc['estado'] == 'PARCIAL':
                        st.progress(oc['valor_autorizado'] / oc['valor_total'])
                        st.text(f"Autorizado: ${oc['valor_autorizado']:,.0f} de ${oc['valor_total']:,.0f}")
                    else:
                        st.text(f"Valor: ${oc['valor_total']:,.0f}")
                
                with col2:
                    estado_color = {'PENDIENTE': '🟡', 'PARCIAL': '🟠', 'AUTORIZADA': '🟢'}
                    st.metric("Estado", f"{estado_color.get(oc['estado'], '⚫')} {oc['estado']}")
                    st.caption(f"Tipo: {oc['tipo']}")
                
                with col3:
                    if oc['estado'] in ['PENDIENTE', 'PARCIAL']:
                        if st.button("✅ Autorizar", key=f"auth_{oc['id']}", use_container_width=True):
                            st.session_state.oc_autorizar = oc['id']
                            st.rerun()
                    else:
                        if st.button("📋 Detalle", key=f"det_{oc['id']}", use_container_width=True):
                            st.session_state.oc_detalle = oc['id']
                            st.rerun()
                
                st.divider()
    else:
        st.info("No hay OCs que coincidan con los filtros")
    
    # Modal para autorizar
    if 'oc_autorizar' in st.session_state:
        mostrar_modal_autorizar(st.session_state.oc_autorizar)
    
    # Botón para nueva OC
    st.divider()
    if st.button("➕ Agregar Nueva OC", use_container_width=True):
        st.session_state.mostrar_nueva_oc = True
    
    if 'mostrar_nueva_oc' in st.session_state and st.session_state.mostrar_nueva_oc:
        mostrar_modal_nueva_oc()

def mostrar_modal_autorizar(oc_id):
    """Modal para autorizar OC"""
    conn = sqlite3.connect('database.db')
    oc = pd.read_sql_query(f"SELECT * FROM ocs WHERE id = {oc_id}", conn)
    conn.close()
    
    if not oc.empty:
        oc = oc.iloc[0]
        with st.form(f"auth_form_{oc_id}"):
            st.subheader(f"Autorizar OC: {oc['numero_oc']}")
            
            st.info(f"**Valor total:** ${oc['valor_total']:,.0f}")
            if oc['estado'] == 'PARCIAL':
                st.info(f"**Ya autorizado:** ${oc['valor_autorizado']:,.0f}")
            
            valor_restante = oc['valor_total'] - oc['valor_autorizado']
            
            # Opciones rápidas
            col1, col2, col3, col4 = st.columns(4)
            porcentajes = {25: 0.25, 50: 0.50, 75: 0.75, 100: 1.0}
            for col, (texto, pct) in zip([col1, col2, col3, col4], porcentajes.items()):
                with col:
                    if st.button(f"{texto}%", use_container_width=True):
                        st.session_state.valor_autorizar = valor_restante * pct
            
            # Campo para valor exacto
            valor_default = st.session_state.get('valor_autorizar', valor_restante)
            valor_autorizar = st.number_input(
                "Valor a autorizar",
                min_value=0.0,
                max_value=float(valor_restante),
                value=float(valor_default),
                step=1000000.0
            )
            
            comentario = st.text_area("Comentario (opcional)")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.form_submit_button("✅ Confirmar Autorización", use_container_width=True):
                    # Actualizar OC
                    conn = sqlite3.connect('database.db')
                    cursor = conn.cursor()
                    
                    nuevo_valor_autorizado = oc['valor_autorizado'] + valor_autorizar
                    nuevo_estado = 'AUTORIZADA' if valor_autorizar == valor_restante else 'PARCIAL'
                    
                    cursor.execute('''
                        UPDATE ocs 
                        SET valor_autorizado = ?, estado = ?, fecha_ultima_autorizacion = ?
                        WHERE id = ?
                    ''', (nuevo_valor_autorizado, nuevo_estado, datetime.now(), oc_id))
                    
                    # Registrar autorización parcial
                    cursor.execute('''
                        INSERT INTO autorizaciones_parciales (oc_id, valor_autorizado, comentario, usuario)
                        VALUES (?, ?, ?, ?)
                    ''', (oc_id, valor_autorizar, comentario, st.session_state.username))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success(f"✅ Autorizado ${valor_autorizar:,.0f}")
                    del st.session_state.oc_autorizar
                    del st.session_state.valor_autorizar
                    st.rerun()
            
            with col_b:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    del st.session_state.oc_autorizar
                    del st.session_state.valor_autorizar
                    st.rerun()

def mostrar_modal_nueva_oc():
    """Modal para nueva OC"""
    clientes = get_clientes()
    with st.form("nueva_oc_form"):
        st.subheader("🆕 Nueva OC")
        
        col1, col2 = st.columns(2)
        with col1:
            cliente_nit = st.selectbox(
                "Cliente *",
                options=clientes['nit'].tolist(),
                format_func=lambda x: f"{clientes[clientes['nit']==x]['nombre'].iloc[0]} (NIT: {x})"
            )
            numero_oc = st.text_input("Número OC *")
        
        with col2:
            valor_total = st.number_input("Valor Total *", min_value=0.0, value=0.0)
            tipo = st.selectbox("Tipo", ["SUELTA", "CUPO_NUEVO"])
        
        if tipo == "CUPO_NUEVO":
            cupo_referencia = st.text_input("Referencia de Cupo")
        else:
            cupo_referencia = None
        
        comentarios = st.text_area("Comentarios (opcional)")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.form_submit_button("💾 Guardar OC", use_container_width=True):
                if cliente_nit and numero_oc and valor_total > 0:
                    conn = sqlite3.connect('database.db')
                    cursor = conn.cursor()
                    try:
                        cursor.execute('''
                            INSERT INTO ocs (cliente_nit, numero_oc, valor_total, tipo, cupo_referencia, comentarios)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (cliente_nit, numero_oc, valor_total, tipo, cupo_referencia, comentarios))
                        conn.commit()
                        st.success(f"✅ OC {numero_oc} registrada")
                        del st.session_state.mostrar_nueva_oc
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ Ya existe una OC con ese número")
                    finally:
                        conn.close()
                else:
                    st.error("❌ Complete los campos obligatorios (*)")
        
        with col_b:
            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                del st.session_state.mostrar_nueva_oc
                st.rerun()

# ================= MANTENIMIENTO =================
def mantenimiento_page():
    """Página de mantenimiento"""
    st.header("🧹 Mantenimiento del Sistema")
    
    # Estadísticas
    conn = sqlite3.connect('database.db')
    
    stats = {}
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clientes WHERE activo = 1")
    stats['clientes'] = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM ocs")
    stats['ocs_totales'] = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM ocs WHERE estado IN ('PENDIENTE', 'PARCIAL')")
    stats['ocs_pendientes'] = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM ocs WHERE estado = 'AUTORIZADA'")
    stats['ocs_autorizadas'] = cursor.fetchone()[0]
    
    # Tamaño BD
    if os.path.exists('database.db'):
        db_size = os.path.getsize('database.db') / (1024 * 1024)
    else:
        db_size = 0
    
    conn.close()
    
    # Mostrar stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Clientes Activos", stats['clientes'])
    with col2:
        st.metric("OCs Totales", stats['ocs_totales'])
    with col3:
        st.metric("OCs Pendientes", stats['ocs_pendientes'])
    with col4:
        st.metric("Tamaño BD", f"{db_size:.2f} MB")
    
    st.divider()
    
    # Limpieza manual
    st.subheader("🗑️ Limpieza de Historial")
    
    st.warning("""
    ⚠️ **ADVERTENCIA:** Esta acción eliminará permanentemente OCs antiguas.
    Se recomienda hacer un backup antes de proceder.
    """)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        dias_limpieza = st.selectbox(
            "Eliminar OCs autorizadas con más de:",
            [30, 60, 90, 180, 365],
            index=2
        )
    with col_b:
        mantener_pendientes = st.checkbox("Mantener todas las OCs pendientes", value=True)
    with col_c:
        crear_backup = st.checkbox("Crear backup automático", value=True)
    
    if st.button("📊 Previsualizar Impacto", use_container_width=True):
        previsualizar_limpieza(dias_limpieza, mantener_pendientes)
    
    st.divider()
    
    # Botones de acción
    col_exe1, col_exe2 = st.columns([1, 2])
    
    with col_exe1:
        if st.button("💾 Crear Backup", use_container_width=True):
            crear_backup_completo()
    
    with col_exe2:
        if st.button("🚨 EJECUTAR LIMPIEZA", type="primary", use_container_width=True,
                    disabled=not st.session_state.get('confirmar_limpieza', False)):
            ejecutar_limpieza(dias_limpieza, mantener_pendientes, crear_backup)

def previsualizar_limpieza(dias, mantener_pendientes):
    """Previsualiza qué se eliminaría"""
    conn = sqlite3.connect('database.db')
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    fecha_limite_str = fecha_limite.strftime('%Y-%m-%d')
    
    query = f"""
    SELECT 
        COUNT(*) as cantidad,
        SUM(valor_total) as valor_total,
        SUM(valor_autorizado) as valor_autorizado
    FROM ocs 
    WHERE estado = 'AUTORIZADA'
    AND (fecha_ultima_autorizacion < '{fecha_limite_str}' OR fecha_ultima_autorizacion IS NULL)
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df.empty and df['cantidad'].iloc[0] > 0:
        st.info(f"""
        **Se eliminarían:**
        • {df['cantidad'].iloc[0]:,} OCs autorizadas
        • Valor total: ${df['valor_total'].iloc[0]:,.0f}
        • Autorizado: ${df['valor_autorizado'].iloc[0]:,.0f}
        • Con fecha anterior a: {fecha_limite_str}
        """)
        
        confirmar = st.checkbox("✅ Confirmo que deseo proceder con la limpieza")
        if confirmar:
            st.session_state.confirmar_limpieza = True
            st.success("Listo para ejecutar. Puede usar el botón de ejecución.")
    else:
        st.success("✅ No hay OCs que cumplan los criterios de eliminación")

def crear_backup_completo():
    """Crea backup en memoria (Streamlit Cloud no permite escribir en disco)"""
    conn = sqlite3.connect('database.db')
    
    # Crear Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Tabla clientes
        df_clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
        df_clientes.to_excel(writer, sheet_name='Clientes', index=False)
        
       
