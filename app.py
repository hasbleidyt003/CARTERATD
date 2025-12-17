"""
Sistema de Gestión de Cartera TD - Versión Mejorada
Aplicación principal Streamlit con mejor manejo de errores y caché
"""

import streamlit as st
from modules.database import init_db
import importlib
import sys
import os
import warnings

# Ignorar warnings específicos de Streamlit
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Control de Cupos - Medicamentos",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': """
        ## Sistema de Gestión de Cartera TD
        
        **Versión:** 2.0  
        **Propósito:** Control de cupos de crédito para clientes del sector salud  
        **Desarrollado por:** Equipo de Tecnología  
        
        Este sistema permite gestionar:
        - Clientes y sus cupos de crédito
        - Órdenes de Compra (OCs) pendientes y autorizadas
        - Movimientos y pagos
        - Reportes y estadísticas
        """
    }
)

# ============================================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================================

# Agregar directorio actual al path para importaciones
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ============================================================================
# INICIALIZACIÓN DE BASE DE DATOS
# ============================================================================

@st.cache_resource
def inicializar_base_datos():
    """Inicializa la base de datos de forma segura"""
    try:
        init_db()
        return True
    except Exception as e:
        st.error(f"❌ Error crítico al inicializar base de datos: {str(e)}")
        # Intentar crear estructura mínima
        try:
            os.makedirs('data', exist_ok=True)
            return False
        except:
            return False

# Ejecutar inicialización
if not inicializar_base_datos():
    st.warning("⚠️ Problemas con la base de datos. Algunas funciones pueden no estar disponibles.")

# ============================================================================
# SISTEMA DE AUTENTICACIÓN SIMPLIFICADO
# ============================================================================

def mostrar_login():
    """Pantalla de login simplificada"""
    st.title("🔐 Sistema de Gestión de Cartera TD")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.subheader("Inicio de Sesión")
            
            # Usuario por defecto para desarrollo
            usuario = st.text_input("Usuario", value="admin")
            contrasena = st.text_input("Contraseña", type="password", value="admin123")
            
            if st.button("🚀 Ingresar", type="primary", use_container_width=True):
                # Validación simple (en producción usar módulo auth.py)
                if usuario.strip() and contrasena.strip():
                    st.session_state.authenticated = True
                    st.session_state.username = usuario
                    st.rerun()
                else:
                    st.error("Por favor complete ambos campos")
            
            st.markdown("---")
            st.caption("**Credenciales de prueba:** Usuario: admin / Contraseña: admin123")
            st.caption("Para producción, implemente el módulo completo de autenticación.")

# ============================================================================
# FUNCIONES PRINCIPALES
# ============================================================================

def cargar_modulo_pagina(nombre_modulo):
    """Carga un módulo de página de forma segura con manejo de caché"""
    try:
        module_name = f"pages.{nombre_modulo}"
        
        # Forzar recarga del módulo para evitar problemas de caché
        if module_name in sys.modules:
            del sys.modules[module_name]
        
        modulo = importlib.import_module(module_name)
        
        # Verificar que el módulo tiene la función show()
        if hasattr(modulo, 'show'):
            return modulo
        else:
            st.error(f"❌ El módulo {module_name} no tiene función 'show()'")
            return None
    except ModuleNotFoundError as e:
        st.error(f"❌ No se encontró el módulo: pages/{nombre_modulo}.py")
        st.info(f"Archivos en pages/: {os.listdir('pages') if os.path.exists('pages') else 'Directorio no existe'}")
        return None
    except ImportError as e:
        st.error(f"❌ Error de importación en {nombre_modulo}: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Error inesperado al cargar {nombre_modulo}: {str(e)}")
        return None

def mostrar_aplicacion_principal():
    """Muestra la aplicación principal con todas las funcionalidades"""
    
    # Cargar CSS personalizado
    try:
        with open('assets/styles.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # CSS por defecto si no existe el archivo
        st.markdown("""
        <style>
        .stButton > button {
            width: 100%;
            border-radius: 5px;
            font-weight: 500;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            border-radius: 4px 4px 0px 0px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Barra superior con información de usuario
    col_top1, col_top2, col_top3 = st.columns([3, 2, 1])
    
    with col_top1:
        st.title("💊 Sistema de Gestión de Cartera TD")
    
    with col_top2:
        if 'username' in st.session_state:
            st.info(f"👤 **Usuario:** {st.session_state.username}")
    
    with col_top3:
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    
    # Navegación por pestañas
    tabs = st.tabs([
        "🏠 Dashboard", 
        "👥 Gestión de Clientes", 
        "📋 Órdenes de Compra (OCs)", 
        "🔧 Mantenimiento y Reportes"
    ])
    
    # ===== PESTAÑA 1: DASHBOARD =====
    with tabs[0]:
        st.header("📊 Dashboard - Resumen General")
        
        # Cargar módulo del dashboard
        modulo_dashboard = cargar_modulo_pagina("1_dashboard")
        if modulo_dashboard:
            try:
                modulo_dashboard.show()
            except Exception as e:
                st.error(f"❌ Error al ejecutar Dashboard: {str(e)}")
                # Mostrar contenido básico como fallback
                mostrar_dashboard_basico()
        else:
            mostrar_dashboard_basico()
    
    # ===== PESTAÑA 2: CLIENTES =====
    with tabs[1]:
        st.header("👥 Gestión de Clientes")
        
        modulo_clientes = cargar_modulo_pagina("2_clientes")
        if modulo_clientes:
            try:
                modulo_clientes.show()
            except Exception as e:
                st.error(f"❌ Error al ejecutar Clientes: {str(e)}")
                mostrar_mensaje_fallback("gestión de clientes")
        else:
            mostrar_mensaje_fallback("gestión de clientes")
    
    # ===== PESTAÑA 3: OCs =====
    with tabs[2]:
        st.header("📋 Gestión de Órdenes de Compra (OCs)")
        
        modulo_ocs = cargar_modulo_pagina("3_ocs")
        if modulo_ocs:
            try:
                modulo_ocs.show()
            except Exception as e:
                st.error(f"❌ Error al ejecutar OCs: {str(e)}")
                mostrar_mensaje_fallback("gestión de OCs")
        else:
            mostrar_mensaje_fallback("gestión de OCs")
    
    # ===== PESTAÑA 4: MANTENIMIENTO =====
    with tabs[3]:
        st.header("🔧 Mantenimiento y Reportes")
        
        modulo_mantenimiento = cargar_modulo_pagina("4_mantenimiento")
        if modulo_mantenimiento:
            try:
                modulo_mantenimiento.show()
            except Exception as e:
                st.error(f"❌ Error al ejecutar Mantenimiento: {str(e)}")
                mostrar_mensaje_fallback("mantenimiento")
        else:
            mostrar_mensaje_fallback("mantenimiento")
    
    # Pie de página
    st.markdown("---")
    col_footer1, col_footer2, col_footer3 = st.columns(3)
    with col_footer2:
        st.caption("© 2024 Sistema de Gestión de Cartera TD - Versión 2.0")

def mostrar_dashboard_basico():
    """Dashboard básico como fallback"""
    try:
        from modules.database import get_estadisticas_generales
        
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
            st.metric("OCs Pendientes", f"${stats['total_ocs_pendientes']:,.0f}")
        
        st.info("ℹ️ Este es un dashboard básico. Para ver el completo, asegúrate que pages/1_dashboard.py exista y funcione correctamente.")
        
    except Exception as e:
        st.error(f"No se pudieron cargar las estadísticas: {str(e)}")

def mostrar_mensaje_fallback(modulo):
    """Muestra mensaje de fallback cuando un módulo no carga"""
    st.warning(f"⚠️ El módulo de {modulo} no está disponible temporalmente.")
    st.info(f"""
    **Solución:**
    1. Verifica que el archivo `pages/{modulo.replace(' ', '_')}.py` exista
    2. Asegúrate de que tenga una función `show()`
    3. Reinicia la aplicación Streamlit
    
    **Archivos disponibles en pages/:** 
    {os.listdir('pages') if os.path.exists('pages') else 'No se encontró la carpeta pages'}
    """)

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal de la aplicación"""
    
    # Inicializar estado de autenticación si no existe
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Mostrar login o aplicación principal
    if not st.session_state.authenticated:
        mostrar_login()
    else:
        mostrar_aplicacion_principal()

# ============================================================================
# EJECUCIÓN
# ============================================================================

if __name__ == "__main__":
    # Limpiar caché problemático de Streamlit
    try:
        import streamlit.runtime.caching as caching
        caching.clear_cache()
    except:
        pass
    
    # Ejecutar aplicación
    main()
