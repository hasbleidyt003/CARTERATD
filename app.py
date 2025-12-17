import streamlit as st
from modules.auth import authenticate
from modules.database import init_db
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
    with open('assets/styles.css', 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
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
    
    with tab1:
        import pages.Dashboard as dashboard
        dashboard.show()
    
    with tab2:
        import pages.Clientes as clientes
        clientes.show()
    
    with tab3:
        import pages.OCs as ocs
        ocs.show()
    
    with tab4:
        import pages.Mantenimiento as mantenimiento
        mantenimiento.show()

if __name__ == "__main__":
    main()
