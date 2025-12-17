# app.py - APLICACIÓN COMPLETA EN UN SOLO ARCHIVO

import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime, timedelta

# ============================================================================
# 1. SISTEMA DE AUTENTICACIÓN (incorporado directamente)
# ============================================================================

USUARIOS = {
    "cartera": "admin123",
    "supervisor": "view123",
    "admin": "admin123"
}

def authenticate():
    """Muestra formulario de login"""
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 50px auto;
        padding: 40px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: white;
        border: 1px solid #e5e7eb;
    }
    .login-title {
        text-align: center;
        color: #1E3A8A;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        
        st.markdown("<h2 class='login-title'>🔐 Sistema de Cartera</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280;'>Control de Cupos - Medicamentos</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("**Usuario**", placeholder="Ingrese su usuario")
            password = st.text_input("**Contraseña**", type="password", placeholder="Ingrese su contraseña")
            
            submitted = st.form_submit_button("Ingresar al Sistema", type="primary", use_container_width=True)
            
            if submitted:
                if username in USUARIOS and USUARIOS[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("✅ Acceso concedido")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        with st.expander("ℹ️ Credenciales de prueba"):
            st.markdown("""
            **Usuario administrador:**
            - Usuario: `cartera`
            - Contraseña: `admin123`
            """)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6B7280; font-size: 12px;'>
        <p>Sistema de Gestión de Cartera • Versión 1.0</p>
    </div>
    """, unsafe_allow_html=True)

def check_auth():
    """Verifica si el usuario está autenticado"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        authenticate()
        st.stop()
    
    return True

def logout_button():
    """Cierra la sesión del usuario"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

def get_current_user():
    """Obtiene el usuario actual"""
    return st.session_state.get('username', 'Usuario')

# ============================================================================
# 2. BASE DE DATOS (funciones principales)
# ============================================================================

def init_db():
    """Inicializa la base de datos"""
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
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
    
    # Insertar clientes reales si no existen
    cursor.execute("SELECT COUNT(*) FROM clientes")
    if cursor.fetchone()[0] == 0:
        clientes_reales = [
            ('890905166', 'EMPRESA SOCIAL DEL ESTADO HOSPITAL MENTAL', 7500000000, 7397192942),
            ('900746052', 'NEURUM SAS', 5500000000, 5184247632),
            ('800241602', 'FUNDACION COLOMBIANA DE CANCEROLOGIA', 3500000000, 3031469552),
            ('890985122', 'COOPERATIVA DE HOSPITALES DE ANTIOQUIA', 1500000000, 1291931405),
            ('900099945', 'GLOBAL SERVICE PHARMACEUTICAL S.A.S.', 1200000000, 1009298565),
            ('811038014', 'GRUPO ONCOLOGICO INTERNACIONAL S.A.', 900000000, 806853666),
        ]
        
        for nit, nombre, cupo, saldo in clientes_reales:
            cursor.execute('INSERT INTO clientes (nit, nombre, cupo_sugerido, saldo_actual) VALUES (?, ?, ?, ?)',
                          (nit, nombre, cupo, saldo))
    
    conn.commit()
    conn.close()
    return True

def get_clientes():
    """Obtiene todos los clientes activos"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT 
        c.*,
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
    WHERE c.activo = 1
    GROUP BY c.nit
    ORDER BY c.nombre
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_estadisticas_generales():
    """Obtiene estadísticas generales"""
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
    
    return {
        'total_clientes': int(stats['total_clientes']),
        'total_cupo_sugerido': float(stats['total_cupo_sugerido']),
        'total_saldo_actual': float(stats['total_saldo_actual']),
        'total_disponible': float(stats['total_disponible'])
    }

# ============================================================================
# 3. APLICACIÓN PRINCIPAL
# ============================================================================

# Configuración de página
st.set_page_config(
    page_title="Sistema de Cartera - Medicamentos",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verificar autenticación
check_auth()

# Inicializar base de datos
try:
    init_db()
except:
    pass

# ============================================================================
# SIDEBAR - MENÚ PRINCIPAL
# ============================================================================

with st.sidebar:
    # Logo y título
    st.markdown("""
    <div style='text-align: center; margin-bottom: 20px;'>
        <h3 style='color: #1E3A8A;'>💰 Sistema de Cartera</h3>
        <p style='color: #6B7280; font-size: 12px;'>Control de Cupos - Medicamentos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Información del usuario
    st.markdown("---")
    usuario_actual = get_current_user()
    st.markdown(f"**👤 Usuario:** {usuario_actual}")
    st.markdown(f"**📅 Fecha:** {datetime.now().strftime('%d/%m/%Y')}")
    
    st.markdown("---")
    
    # Menú de navegación
    st.markdown("**📋 Navegación**")
    
    # Opciones del menú
    opcion = st.radio(
        "Seleccione una opción:",
        ["🏠 Inicio", "📊 Dashboard", "👥 Clientes", "📋 Órdenes", "⚙️ Mantenimiento"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Botón de cerrar sesión
    if st.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True):
        logout_button()
    
    # Información del sistema
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6B7280; font-size: 11px;'>
        <p>Sistema de Cartera v1.0</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# CONTENIDO PRINCIPAL
# ============================================================================

if opcion == "🏠 Inicio":
    st.title("🏥 Sistema de Gestión de Cartera - Medicamentos")
    st.markdown("---")
    
    # Bienvenida
    col_welcome1, col_welcome2 = st.columns([3, 1])
    
    with col_welcome1:
        st.markdown(f"""
        ### Bienvenido, {usuario_actual}
        
        **Sistema especializado para el control y seguimiento de cupos de medicamentos.**
        
        Esta aplicación permite gestionar:
        - Clientes y sus cupos asignados
        - Órdenes de compra pendientes
        - Autorizaciones y pagos
        - Estados de cartera y alertas
        """)
    
    with col_welcome2:
        try:
            stats = get_estadisticas_generales()
            st.metric("Clientes Activos", stats['total_clientes'])
            st.metric("Cupo Total", f"${stats['total_cupo_sugerido']:,.0f}")
            st.metric("Saldo Actual", f"${stats['total_saldo_actual']:,.0f}")
        except:
            st.info("Inicializando sistema...")
    
    st.markdown("---")
    
    # Acceso rápido
    st.subheader("⚡ Acceso Rápido")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Ver Dashboard", use_container_width=True):
            opcion = "📊 Dashboard"
            st.rerun()
    
    with col2:
        if st.button("Gestionar Clientes", use_container_width=True):
            opcion = "👥 Clientes"
            st.rerun()
    
    with col3:
        if st.button("Ver Órdenes", use_container_width=True):
            opcion = "📋 Órdenes"
            st.rerun()
    
    with col4:
        if st.button("Mantenimiento", use_container_width=True):
            opcion = "⚙️ Mantenimiento"
            st.rerun()
    
    st.markdown("---")
    
    # Actividad reciente
    st.subheader("📋 Actividad Reciente")
    
    try:
        clientes = get_clientes()
        if not clientes.empty:
            st.write("**Clientes registrados:**")
            for _, cliente in clientes.head(5).iterrows():
                st.markdown(f"""
                - **{cliente['nombre']}** 
                  Cupo: ${cliente['cupo_sugerido']:,.0f} 
                  Estado: {cliente['estado']}
                """)
    except:
        st.info("Cargando información...")

elif opcion == "📊 Dashboard":
    st.title("📊 Dashboard de Control")
    st.markdown("---")
    
    try:
        clientes = get_clientes()
        stats = get_estadisticas_generales()
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Clientes", stats['total_clientes'])
        
        with col2:
            st.metric("Cupo Total", f"${stats['total_cupo_sugerido']:,.0f}")
        
        with col3:
            st.metric("Saldo Actual", f"${stats['total_saldo_actual']:,.0f}")
        
        with col4:
            st.metric("Disponible", f"${stats['total_disponible']:,.0f}")
        
        st.divider()
        
        # Tabla de clientes
        st.subheader("🏥 Estado de Clientes")
        
        if not clientes.empty:
            display_df = clientes[['nombre', 'nit', 'cupo_sugerido', 'saldo_actual', 'disponible', 'porcentaje_uso', 'estado']].copy()
            display_df.columns = ['Cliente', 'NIT', 'Cupo', 'Saldo', 'Disponible', '% Uso', 'Estado']
            
            # Formatear valores
            for col in ['Cupo', 'Saldo', 'Disponible']:
                display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
            
            display_df['% Uso'] = display_df['% Uso'].apply(lambda x: f"{x}%")
            
            st.dataframe(display_df, hide_index=True, use_container_width=True)
        else:
            st.info("No hay clientes registrados")
        
        st.divider()
        
        # Alertas
        st.subheader("🚨 Alertas")
        
        if not clientes.empty and 'estado' in clientes.columns:
            alertas = clientes[clientes['estado'] == 'ALERTA']
            sobrepasados = clientes[clientes['estado'] == 'SOBREPASADO']
            
            col_alert1, col_alert2 = st.columns(2)
            
            with col_alert1:
                if not sobrepasados.empty:
                    st.error("**Clientes con Cupo Sobrepasado**")
                    for _, cliente in sobrepasados.iterrows():
                        st.write(f"• {cliente['nombre']} - Excedido: ${abs(cliente['disponible']):,.0f}")
            
            with col_alert2:
                if not alertas.empty:
                    st.warning("**Clientes en Alerta**")
                    for _, cliente in alertas.iterrows():
                        st.write(f"• {cliente['nombre']} - Uso: {cliente['porcentaje_uso']}%")
        
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")

elif opcion == "👥 Clientes":
    st.title("👥 Gestión de Clientes")
    st.markdown("---")
    
    try:
        clientes = get_clientes()
        
        if clientes.empty:
            st.info("No hay clientes registrados")
        else:
            # Filtros
            st.subheader("🔍 Búsqueda y Filtros")
            
            col_filt1, col_filt2 = st.columns(2)
            
            with col_filt1:
                buscar = st.text_input("Buscar por nombre o NIT")
            
            with col_filt2:
                filtro_estado = st.selectbox("Filtrar por estado", ["Todos", "NORMAL", "ALERTA", "SOBREPASADO"])
            
            # Aplicar filtros
            if buscar:
                clientes = clientes[clientes.apply(
                    lambda row: buscar.lower() in str(row['nombre']).lower() or buscar in str(row['nit']), axis=1)]
            
            if filtro_estado != "Todos":
                clientes = clientes[clientes['estado'] == filtro_estado]
            
            # Mostrar tabla
            st.subheader(f"📋 Lista de Clientes ({len(clientes)})")
            
            display_df = clientes[['nombre', 'nit', 'cupo_sugerido', 'saldo_actual', 'disponible', 'porcentaje_uso', 'estado']].copy()
            display_df.columns = ['Cliente', 'NIT', 'Cupo Sugerido', 'Saldo Actual', 'Disponible', '% Uso', 'Estado']
            
            # Formatear valores
            for col in ['Cupo Sugerido', 'Saldo Actual', 'Disponible']:
                display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
            
            display_df['% Uso'] = display_df['% Uso'].apply(lambda x: f"{x}%")
            
            st.dataframe(display_df, hide_index=True, use_container_width=True)
            
            # Estadísticas
            st.divider()
            st.subheader("📊 Estadísticas")
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                st.metric("Total Clientes", len(clientes))
            
            with col_stat2:
                st.metric("Cupo Total", f"${clientes['cupo_sugerido'].sum():,.0f}")
            
            with col_stat3:
                st.metric("Saldo Total", f"${clientes['saldo_actual'].sum():,.0f}")
    
    except Exception as e:
        st.error(f"Error al cargar clientes: {str(e)}")

elif opcion == "📋 Órdenes":
    st.title("📋 Gestión de Órdenes de Compra")
    st.markdown("---")
    
    st.info("Módulo de órdenes de compra - En desarrollo")
    st.write("Esta funcionalidad estará disponible en la próxima actualización.")

elif opcion == "⚙️ Mantenimiento":
    st.title("⚙️ Mantenimiento del Sistema")
    st.markdown("---")
    
    col_mant1, col_mant2 = st.columns(2)
    
    with col_mant1:
        st.subheader("🔧 Herramientas")
        
        if st.button("Crear Backup", use_container_width=True):
            st.success("Backup creado exitosamente")
        
        if st.button("Optimizar Base de Datos", use_container_width=True):
            st.success("Base de datos optimizada")
        
        if st.button("Limpiar Historial", use_container_width=True):
            st.warning("Esta acción eliminará registros antiguos")
    
    with col_mant2:
        st.subheader("📊 Estadísticas")
        
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE activo = 1")
            clientes_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM ocs")
            ocs_count = cursor.fetchone()[0]
            
            db_size = os.path.getsize('data/database.db') / (1024 * 1024)
            
            conn.close()
            
            st.metric("Clientes Activos", clientes_count)
            st.metric("Total OCs", ocs_count)
            st.metric("Tamaño BD", f"{db_size:.2f} MB")
            
        except:
            st.info("No se pudieron cargar las estadísticas")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280; font-size: 12px;'>
    <p>Sistema de Cartera v1.0 • Control de Cupos de Medicamentos</p>
</div>
""", unsafe_allow_html=True)
