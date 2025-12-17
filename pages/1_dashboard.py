import streamlit as st
from modules.auth import authenticate
from modules.database import init_db
import importlib
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

# Sistema de autenticación
def main():
    # Mostrar login si no está autenticado
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        authenticate()
    else:
        # Mostrar aplicación principal
        show_main_app()

def show_main_app():
    # CSS personalizado
    try:
        with open('assets/styles.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except:
        pass  # Si no existe el CSS, continuar sin problemas
    
    # Barra superior
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        st.title("💊 Control de Cupos - Medicamentos")
    with col2:
        st.info(f"Usuario: {st.session_state.username}")
    with col3:
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.authenticated = False
            st.rerun()
    
    # Navegación por pestañas
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 Dashboard", 
        "👥 Clientes", 
        "📋 OCs Pendientes", 
        "🧹 Mantenimiento"
    ])
    
    # ✅ IMPORTAR CORRECTAMENTE los módulos con números
    with tab1:
        try:
            dashboard = importlib.import_module("pages/1_dashboard")
            dashboard.show()
        except Exception as e:
            st.error(f"Error cargando dashboard: {str(e)}")
            st.info("Asegúrate que existe: pages/1_dashboard.py")
    
    with tab2:
        try:
            clientes = importlib.import_module("pages/2_clientes")
            clientes.show()
        except Exception as e:
            st.error(f"Error cargando clientes: {str(e)}")
            st.info("Asegúrate que existe: pages/2_clientes.py")
    
    with tab3:
        try:
            ocs = importlib.import_module("pages/3_ocs")
            ocs.show()
        except Exception as e:
            st.error(f"Error cargando ocs: {str(e)}")
            st.info("Asegúrate que existe: pages/3_ocs.py")
    
    with tab4:
        try:
            mantenimiento = importlib.import_module("pages/4_mantenimiento")
            mantenimiento.show()
        except Exception as e:
            st.error(f"Error cargando mantenimiento: {str(e)}")
            st.info("Asegúrate que existe: pages/4_mantenimiento.py")

if __name__ == "__main__":
    main()
