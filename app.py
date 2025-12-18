"""
APLICACIÓN PRINCIPAL - SISTEMA DE GESTIÓN DE CUPOS TODODROGAS
Diseño futurista estilo glass
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
        **Propósito:** Control integral de cupos de crédito
        **Estilo:** Futurista Glass
        """
    }
)

# ==================== CSS PERSONALIZADO ====================

def load_custom_css():
    """Carga estilos CSS personalizados"""
    try:
        with open('assets/styles.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # CSS mínimo de emergencia
        st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(135deg, #FFFFFF 0%, #F7FAFC 100%);
            }
            .main .block-container {
                padding-top: 1rem;
            }
        </style>
        """, unsafe_allow_html=True)

# ==================== NAVBAR GLASS ====================

def create_glass_navbar():
    """Crea navbar estilo glass futurista"""
    
    current_time = datetime.now().strftime("%d/%m/%Y • %H:%M")
    user = st.session_state.get('user', {})
    
    navbar_html = f"""
    <div style="
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.08);
        padding: 1rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="
                    background: linear-gradient(135deg, #0066FF, #00D4FF);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    font-size: 1.8rem;
                    font-weight: 800;
                ">💊</div>
                <div>
                    <div style="font-size: 1.4rem; font-weight: 800; color: #1A1A1A;">
                        TODODROGAS
                    </div>
                    <div style="font-size: 0.9rem; color: #4A5568; margin-top: -2px;">
                        Control de Cupos - Glass Edition
                    </div>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="
                    background: rgba(255, 255, 255, 0.7);
                    backdrop-filter: blur(10px);
                    border-radius: 16px;
                    padding: 8px 16px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                ">
                    <div style="color: #1A1A1A; font-weight: 600; font-size: 0.9rem;">
                        ⏰ {current_time}
                    </div>
                </div>
                
                <div style="text-align: right;">
                    <div style="color: #1A1A1A; font-weight: 600;">
                        👤 {user.get('nombre', 'Usuario')}
                    </div>
                    <div style="color: #4A5568; font-size: 0.85rem;">
                        {user.get('rol', 'Usuario').upper()}
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    return navbar_html

# ==================== SIDEBAR MODERNA ====================

def create_sidebar():
    """Crea barra lateral moderna"""
    
    with st.sidebar:
        # Logo y título
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="
                background: linear-gradient(135deg, #0066FF, #00D4FF);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 2.5rem;
                margin-bottom: 10px;
            ">💊</div>
            <div style="font-size: 1.2rem; font-weight: 800; color: #1A1A1A;">
                MENÚ
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Menú de navegación
        st.markdown("### 🧭 Navegación")
        
        if st.button("🏠 Dashboard", use_container_width=True, type="primary"):
            st.switch_page("pages/1_dashboard.py")
        
        if st.button("👥 Clientes", use_container_width=True):
            st.switch_page("pages/2_clientes.py")
        
        if st.button("📋 Órdenes Compra", use_container_width=True):
            st.switch_page("pages/3_ocs.py")
        
        if st.button("📊 Reportes", use_container_width=True):
            st.switch_page("pages/4_reportes.py")
        
        if st.button("⚙️ Configuración", use_container_width=True):
            st.switch_page("pages/5_configuracion.py")
        
        st.markdown("---")
        
        # Acciones rápidas
        st.markdown("### ⚡ Acciones")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Nueva OC", use_container_width=True):
                st.switch_page("pages/3_ocs.py")
        with col2:
            if st.button("📈 Análisis", use_container_width=True):
                st.switch_page("pages/4_reportes.py")
        
        st.markdown("---")
        
        # Usuario actual
        user = st.session_state.get('user', {})
        st.markdown(f"""
        <div style="
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
        ">
            <div style="font-weight: 600; color: #1A1A1A;">
                👤 {user.get('nombre', 'Usuario')}
            </div>
            <div style="color: #4A5568; font-size: 0.85rem;">
                {user.get('rol', 'Rol')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón de cerrar sesión
        if st.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
            logout()

# ==================== PÁGINA PRINCIPAL ====================

def show_homepage():
    """Muestra página principal"""
    
    # Cargar CSS
    load_custom_css()
    
    # Crear navbar
    st.markdown(create_glass_navbar(), unsafe_allow_html=True)
    
    # Crear sidebar
    create_sidebar()
    
    # Redirigir al dashboard
    st.switch_page("pages/1_dashboard.py")

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal"""
    
    # Verificar autenticación
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        show_login_screen()
    else:
        show_homepage()

if __name__ == "__main__":
    main()
