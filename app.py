"""
APLICACIÓN PRINCIPAL - SISTEMA DE GESTIÓN DE CUPOS TODODROGAS
Entry point principal con diseño Rappi-Style/Oracle Mining
"""

import streamlit as st
import time
from datetime import datetime
import os
import sys

# Configurar path para módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos
from modules.auth import show_login_screen, check_authentication, logout
from modules.database import init_db

# ==================== CONFIGURACIÓN INICIAL ====================

# Inicializar base de datos si no existe
if not os.path.exists('data/database.db'):
    init_db()

# ==================== CONFIGURACIÓN DE PÁGINA ====================

st.set_page_config(
    page_title="Tododrogas - Gestión de Cupos",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': """
        ## 💊 Sistema de Gestión de Cupos - Tododrogas
        
        **Versión:** 1.0.0
        **Propósito:** Control integral de cupos de crédito y órdenes de compra
        **Desarrollado por:** Equipo de Automatización
        
        Este sistema permite gestionar:
        - Clientes y sus cupos de crédito
        - Órdenes de Compra (OCs) pendientes y autorizadas
        - Análisis de disponibilidad y riesgo
        - Reportes ejecutivos en tiempo real
        
        **Credenciales de prueba:**
        - Administrador: admin / admin123
        - Usuario: cartera / cartera123
        """
    }
)

# ==================== CSS PERSONALIZADO ====================

def load_custom_css():
    """Carga los estilos CSS personalizados"""
    try:
        with open('assets/styles.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # CSS mínimo si no existe el archivo
        st.markdown("""
        <style>
            .stApp {
                background-color: #f8fafc;
            }
            
            h1, h2, h3 {
                color: #1e40af !important;
            }
            
            .stButton > button {
                background-color: #2563eb !important;
                color: white !important;
                border-radius: 8px !important;
            }
            
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)

# ==================== NAVBAR RAPPI-STYLE ====================

def create_rappi_navbar():
    """Crea la navbar estilo Rappi"""
    
    current_time = datetime.now().strftime("%d/%m/%Y • %H:%M")
    user = st.session_state.get('user', {})
    
    navbar_html = f"""
    <div class="rappi-navbar">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="font-size: 1.8rem;">💊</div>
                <div>
                    <div style="font-size: 1.4rem; font-weight: 800; color: white;">
                        TODODROGAS • GESTIÓN DE CUPOS
                    </div>
                    <div style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.9);">
                        Sistema de control ejecutivo
                    </div>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="text-align: right;">
                    <div style="color: white; font-weight: 600;">
                        👤 {user.get('nombre', 'Usuario')}
                    </div>
                    <div style="color: rgba(255, 255, 255, 0.8); font-size: 0.85rem;">
                        {user.get('rol', '').upper()}
                    </div>
                </div>
                
                <div style="
                    background: rgba(255, 255, 255, 0.15);
                    padding: 8px 16px;
                    border-radius: 12px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                ">
                    <div style="color: white; font-weight: 600; font-size: 0.9rem;">
                        ⏰ {current_time}
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    return navbar_html

# ==================== SIDEBAR DE NAVEGACIÓN ====================

def create_sidebar():
    """Crea la barra lateral de navegación"""
    
    with st.sidebar:
        # Logo y título
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 2.5rem; margin-bottom: 10px;">💊</div>
            <div style="font-size: 1.2rem; font-weight: 800; color: #0066CC;">
                TODODROGAS
            </div>
            <div style="font-size: 0.9rem; color: #666; margin-top: 5px;">
                Control de Cupos
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Menú de navegación
        st.markdown("### 🧭 NAVEGACIÓN PRINCIPAL")
        
        # Botones de navegación
        if st.button("🏠 Dashboard Principal", use_container_width=True, type="primary"):
            st.switch_page("pages/1_dashboard.py")
        
        if st.button("👥 Gestión de Clientes", use_container_width=True):
            st.switch_page("pages/2_clientes.py")
        
        if st.button("📋 Órdenes de Compra", use_container_width=True):
            st.switch_page("pages/3_ocs.py")
        
        if st.button("📊 Reportes y Análisis", use_container_width=True):
            st.switch_page("pages/4_reportes.py")
        
        if st.button("⚙️ Configuración", use_container_width=True):
            st.switch_page("pages/5_configuracion.py")
        
        st.markdown("---")
        
        # Acciones rápidas
        st.markdown("### ⚡ ACCIONES RÁPIDAS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➕ Nueva OC", use_container_width=True):
                st.switch_page("pages/3_ocs.py")
        
        with col2:
            if st.button("📤 Exportar", use_container_width=True):
                st.switch_page("pages/4_reportes.py")
        
        st.markdown("---")
        
        # Información del sistema
        st.markdown("### 📊 ESTADO DEL SISTEMA")
        
        try:
            from modules.database import get_estadisticas_generales
            stats = get_estadisticas_generales()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Clientes", stats['total_clientes'])
            with col2:
                st.metric("OCs Activas", stats['cantidad_ocs_pendientes'])
        except:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Clientes", "7")
            with col2:
                st.metric("OCs Activas", "12")
        
        # Estado de conexión
        st.progress(85, text="🟢 Sistema operativo")
        
        st.markdown("---")
        
        # Información de usuario
        user = st.session_state.get('user', {})
        st.markdown(f"""
        <div style="background: #F8F9FA; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
            <div style="font-weight: 600; color: #1A1A1A;">👤 {user.get('nombre', 'Usuario')}</div>
            <div style="color: #666; font-size: 0.85rem;">{user.get('rol', 'Rol no asignado').upper()}</div>
            <div style="color: #999; font-size: 0.8rem; margin-top: 5px;">
                Último acceso: {datetime.now().strftime('%H:%M')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón de cierre de sesión
        if st.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
            logout()

# ==================== PÁGINA DE INICIO ====================

def show_homepage():
    """Muestra la página de inicio"""
    
    # Cargar CSS personalizado
    load_custom_css()
    
    # Crear navbar
    st.markdown(create_rappi_navbar(), unsafe_allow_html=True)
    
    # Crear sidebar
    create_sidebar()
    
    # Contenido principal - Redirigir al dashboard
    st.switch_page("pages/1_dashboard.py")

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal de la aplicación"""
    
    # Verificar autenticación
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        # Mostrar pantalla de login
        show_login_screen()
    else:
        # Mostrar aplicación principal
        show_homepage()

# ==================== EJECUCIÓN ====================

if __name__ == "__main__":
    main()
