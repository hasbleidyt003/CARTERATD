import streamlit as st
from modules.auth import authenticate
from modules.database import init_db
import importlib.util
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Configuración de página
st.set_page_config(
    page_title="Control de Cupos - Medicamentos",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicializar base de datos
init_db()

# Función robusta para importar páginas
def import_page(module_name):
    """Importa páginas que comienzan con números"""
    module_path = f"pages/{module_name}.py"
    
    if not os.path.exists(module_path):
        raise FileNotFoundError(f"Archivo no encontrado: {module_path}")
    
    # Crear un nombre de módulo válido (sin números al inicio)
    valid_name = f"page_{module_name.replace('1_', '').replace('2_', '').replace('3_', '').replace('4_', '')}"
    
    spec = importlib.util.spec_from_file_location(valid_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[valid_name] = module
    spec.loader.exec_module(module)
    return module

# Sistema de autenticación
def main():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        authenticate()
    else:
        show_main_app()

def show_main_app():
    # CSS personalizado
    try:
        with open('assets/styles.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except:
        pass
    
    # Barra superior
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        st.title("💊 Control de Cupos - Medicamentos")
    with col2:
        st.info(f"Usuario: {st.session_state.username}")
    with col3:
        if st.button("🚪 Cerrar Sesión"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Navegación por pestañas
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 Dashboard", 
        "👥 Clientes", 
        "📋 OCs Pendientes", 
        "🧹 Mantenimiento"
    ])
    
    # Importar páginas de forma robusta
    with tab1:
        try:
            dashboard = import_page("1_dashboard")
            if hasattr(dashboard, 'show'):
                dashboard.show()
            else:
                st.error("El módulo dashboard no tiene función 'show()'")
        except Exception as e:
            st.error(f"Error dashboard: {e}")
            # Mostrar contenido del archivo para debug
            if os.path.exists('pages/1_dashboard.py'):
                st.text("Contenido de 1_dashboard.py:")
                st.code(open('pages/1_dashboard.py', 'r').read())
    
    with tab2:
        try:
            clientes = import_page("2_clientes")
            clientes.show()
        except Exception as e:
            st.error(f"Error clientes: {e}")
    
    with tab3:
        try:
            ocs = import_page("3_ocs")
            ocs.show()
        except Exception as e:
            st.error(f"Error OCs: {e}")
    
    with tab4:
        try:
            mantenimiento = import_page("4_mantenimiento")
            mantenimiento.show()
        except Exception as e:
            st.error(f"Error mantenimiento: {e}")

if __name__ == "__main__":
    main()
