"""
SISTEMA DE GESTIÓN DE CARTERA - TODODROGAS
Aplicación principal con tema empresarial moderno
"""

import streamlit as st
import os
import sys
from datetime import datetime

# ==================== CONFIGURACIÓN DEL TEMA ====================

def configure_modern_theme():
    """Configura el tema empresarial moderno de Tododrogas"""
    st.markdown("""
    <style>
        /* TEMA CORPORATIVO TODODROGAS */
        .stApp {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        }
        
        /* HEADERS ELEGANTES */
        h1, h2, h3 {
            color: #1a1a1a !important;
            font-weight: 700 !important;
            letter-spacing: -0.5px;
            margin-bottom: 1rem !important;
        }
        
        h1 {
            background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.2rem !important;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 0.5rem;
        }
        
        /* BOTONES CORPORATIVOS */
        .stButton > button {
            background: linear-gradient(135deg, #0066cc, #004499);
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.75rem 1.5rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px rgba(0, 102, 204, 0.2);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 12px rgba(0, 102, 204, 0.3) !important;
            background: linear-gradient(135deg, #004499, #003366) !important;
        }
        
        /* BOTONES SECUNDARIOS */
        div[data-testid="stButton"] button[kind="secondary"] {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef) !important;
            color: #0066cc !important;
            border: 2px solid #0066cc !important;
        }
        
        /* TARJETAS ELEGANTES */
        .card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(0, 102, 204, 0.1);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 30px rgba(0, 102, 204, 0.15);
        }
        
        /* BADGES DE ESTADO */
        .badge {
            display: inline-block;
            padding: 0.35rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin: 0.2rem;
        }
        
        .badge-pendiente {
            background: linear-gradient(135deg, #ffd166, #ffb347);
            color: #8a5700;
        }
        
        .badge-autorizada {
            background: linear-gradient(135deg, #06d6a0, #0cb48c);
            color: #00563f;
        }
        
        .badge-parcial {
            background: linear-gradient(135deg, #118ab2, #0a6c8f);
            color: white;
        }
        
        /* INPUTS MODERNOS */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div {
            border-radius: 8px !important;
            border: 2px solid #e9ecef !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #0066cc !important;
            box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1) !important;
        }
        
        /* BARRAS DE PROGRESO */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #0066cc, #00a8ff) !important;
            border-radius: 10px !important;
        }
        
        /* OCULTAR ELEMENTOS DEFAULT */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* MÉTRICAS PERSONALIZADAS */
        .stMetric {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 5px solid #0066cc;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }
        
        /* NAVBAR PERSONALIZADA */
        .navbar {
            background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
            padding: 1rem 2rem;
            margin: -1rem -1rem 2rem -1rem;
            border-radius: 0 0 12px 12px;
            box-shadow: 0 4px 20px rgba(0, 102, 204, 0.3);
        }
        
        .navbar-title {
            color: white !important;
            font-size: 1.8rem !important;
            font-weight: 800 !important;
            letter-spacing: -0.5px;
        }
        
        .navbar-subtitle {
            color: rgba(255, 255, 255, 0.9) !important;
            font-size: 1rem !important;
            margin-top: -0.5rem !important;
        }
        
        /* TABLAS ELEGANTES */
        .dataframe {
            border-radius: 8px !important;
            overflow: hidden !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
        }
        
        .dataframe th {
            background: linear-gradient(135deg, #0066cc, #004499) !important;
            color: white !important;
            font-weight: 600 !important;
        }
        
        .dataframe tr:nth-child(even) {
            background-color: #f8f9fa !important;
        }
        
        .dataframe tr:hover {
            background-color: #e9f7ff !important;
        }
        
        /* MODALES Y EXPANDERS */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef) !important;
            border-radius: 8px !important;
            border: 2px solid #e9ecef !important;
            font-weight: 600 !important;
        }
        
        /* SEPARADORES ELEGANTES */
        hr {
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, #0066cc, transparent);
            margin: 2rem 0;
        }
        
        /* SCROLLBAR PERSONALIZADA */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #0066cc, #004499);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #004499, #003366);
        }
    </style>
    """, unsafe_allow_html=True)

# ==================== NAVBAR MODERNA ====================

def modern_navbar():
    """Navbar moderna y elegante para Tododrogas"""
    st.markdown("""
    <div class="navbar">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="navbar-title">💊 TODODROGAS • Automatización</div>
                <div class="navbar-subtitle">Sistema de Gestión de Cartera y Cupos</div>
            </div>
            <div style="display: flex; align-items: center; gap: 1.5rem;">
                <div style="text-align: right;">
                    <div style="color: white; font-weight: 600; font-size: 1rem;">👤 Administrador</div>
                    <div style="color: rgba(255, 255, 255, 0.8); font-size: 0.85rem;">Sistema conectado</div>
                </div>
                <div style="
                    background: rgba(255, 255, 255, 0.2);
                    padding: 0.5rem 1rem;
                    border-radius: 20px;
                    color: white;
                    font-weight: 600;
                    font-size: 0.9rem;
                ">
                    🕐 """ + datetime.now().strftime("%d/%m/%Y %H:%M") + """
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== SIDEBAR DE NAVEGACIÓN ====================

def create_sidebar():
    """Crea la barra lateral de navegación elegante"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 1.5rem; font-weight: 800; color: #0066cc;">🧭</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #1a1a1a;">Navegación</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botones de navegación
        nav_options = {
            "🏠 Dashboard Principal": "pages/1_dashboard.py",
            "👥 Gestión de Clientes": "pages/2_clientes.py",
            "📋 Órdenes de Compra": "pages/3_ocs.py",
            "📊 Reportes Avanzados": "pages/4_reportes.py",
            "⚙️ Configuración": "pages/5_configuracion.py"
        }
        
        for option, page in nav_options.items():
            if st.button(option, use_container_width=True, type="primary" if option == "📋 Órdenes de Compra" else "secondary"):
                st.switch_page(page)
        
        st.markdown("---")
        
        # Acciones rápidas
        st.markdown("### ⚡ Acciones Rápidas")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Nueva OC", use_container_width=True):
                st.switch_page("pages/3_ocs.py")
                # Aquí se activaría el modal de nueva OC
        with col2:
            if st.button("💳 Registrar Pago", use_container_width=True):
                st.switch_page("pages/2_clientes.py")
        
        st.markdown("---")
        
        # Información del sistema
        st.markdown("### 📊 Estado del Sistema")
        
        # Métricas del sistema (simuladas por ahora)
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Clientes Activos", "7", delta="+0")
        with col_b:
            st.metric("OCs Pendientes", "12", delta="+3")
        
        # Botón de cierre de sesión
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ==================== PÁGINA DE INICIO ====================

def show_homepage():
    """Muestra la página de inicio elegante"""
    
    modern_navbar()
    
    # Encabezado principal
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🎯 Panel de Control - Gestión de Cartera")
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #e9f7ff, #d1ecff);
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 5px solid #0066cc;
            margin-bottom: 2rem;
        ">
            <strong>🏆 Sistema de Gestión Empresarial</strong><br>
            Control total de cupos, cartera y órdenes de compra en tiempo real.
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🚀 Acceso Rápido", use_container_width=True):
            st.switch_page("pages/3_ocs.py")
    
    # Métricas principales
    st.subheader("📈 Métricas Clave")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Cupo Total",
            value="$71.5B",
            delta="+2.3%",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="Cartera Activa",
            value="$48.2B",
            delta="-1.2%",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="OCs Pendientes",
            value="12",
            delta="+3",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="Disponibilidad",
            value="67.4%",
            delta="+1.8%",
            delta_color="normal"
        )
    
    st.markdown("---")
    
    # Sección de acciones rápidas
    st.subheader("⚡ Acciones Inmediatas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Crear Nueva OC", use_container_width=True, type="primary"):
            # Esto abrirá el modal en la página de OCs
            st.session_state['show_new_oc_modal'] = True
            st.switch_page("pages/3_ocs.py")
    
    with col2:
        if st.button("👥 Ver Clientes", use_container_width=True):
            st.switch_page("pages/2_clientes.py")
    
    with col3:
        if st.button("📊 Generar Reporte", use_container_width=True):
            st.switch_page("pages/4_reportes.py")
    
    with col4:
        if st.button("⚙️ Configurar", use_container_width=True):
            st.switch_page("pages/5_configuracion.py")
    
    st.markdown("---")
    
    # Últimas OCs (simulado)
    st.subheader("🔄 Actividad Reciente")
    
    # Tarjetas de actividad
    activities = [
        {
            "title": "OC-2024-015",
            "cliente": "AUNA COLOMBIA S.A.S",
            "valor": "$2.500.000.000",
            "estado": "PENDIENTE",
            "fecha": "Hoy, 10:30 AM"
        },
        {
            "title": "OC-2024-014",
            "cliente": "HOSPITAL MENTAL DE ANTIOQUIA",
            "valor": "$1.200.000.000",
            "estado": "AUTORIZADA",
            "fecha": "Ayer, 15:45 PM"
        },
        {
            "title": "OC-2024-013",
            "cliente": "PHARMASAN S.A.S",
            "valor": "$850.000.000",
            "estado": "PARCIAL",
            "fecha": "15/03/2024"
        }
    ]
    
    for activity in activities:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            with col1:
                st.markdown(f"**{activity['title']}**")
                st.caption(f"👤 {activity['cliente']}")
            
            with col2:
                st.markdown(f"**Valor:** {activity['valor']}")
                st.caption(f"📅 {activity['fecha']}")
            
            with col3:
                status_color = {
                    "PENDIENTE": "#ffd166",
                    "AUTORIZADA": "#06d6a0",
                    "PARCIAL": "#118ab2"
                }[activity['estado']]
                
                st.markdown(f"""
                <div style="
                    background: {status_color};
                    color: white;
                    padding: 0.25rem 0.75rem;
                    border-radius: 20px;
                    font-size: 0.85rem;
                    font-weight: 600;
                    text-align: center;
                ">
                    {activity['estado']}
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                if st.button("📋 Detalle", key=f"det_{activity['title']}"):
                    st.session_state[f'view_oc_{activity["title"]}'] = True
                    st.switch_page("pages/3_ocs.py")
            
            st.divider()

# ==================== INICIALIZACIÓN ====================

def init_session_state():
    """Inicializa el estado de la sesión"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = True  # Simplificado para desarrollo
    if 'username' not in st.session_state:
        st.session_state.username = "Administrador"
    if 'user_role' not in st.session_state:
        st.session_state.user_role = "Sistema"

# ==================== APLICACIÓN PRINCIPAL ====================

def main():
    """Función principal de la aplicación"""
    
    # Configuración de página
    st.set_page_config(
        page_title="Tododrogas - Gestión de Cartera",
        page_icon="💊",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': """
            ## 💊 Sistema de Gestión de Cartera - Tododrogas
            
            **Versión:** 3.0.0
            **Propósito:** Control integral de cupos de crédito y cartera
            **Desarrollado por:** Equipo de Automatización
            
            Este sistema permite gestionar:
            - Clientes y sus cupos de crédito
            - Órdenes de Compra (OCs) pendientes y autorizadas
            - Movimientos y pagos
            - Reportes y estadísticas en tiempo real
            """
        }
    )
    
    # Aplicar tema personalizado
    configure_modern_theme()
    
    # Inicializar estado
    init_session_state()
    
    # Mostrar sidebar de navegación
    create_sidebar()
    
    # Mostrar página principal
    show_homepage()

# ==================== EJECUCIÓN ====================

if __name__ == "__main__":
    main()
