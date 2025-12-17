import streamlit as st

# Configuración de página
st.set_page_config(
    page_title="Control de Cupos - Medicamentos",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"  # IMPORTANTE: sidebar expandido
)

# ==================== AUTENTICACIÓN ====================
USUARIOS = {
    "cartera": "admin123",
    "viewer": "view123"
}

# Inicializar estado de sesión
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# ==================== PÁGINA DE LOGIN ====================
def show_login():
    """Muestra la página de login"""
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

# ==================== APLICACIÓN PRINCIPAL ====================
def main():
    # Si no está autenticado, mostrar login
    if not st.session_state.authenticated:
        show_login()
        return
    
    # Si está autenticado, Streamlit mostrará automáticamente:
    # 1. Sidebar con navegación a las páginas
    # 2. Contenido de la página seleccionada
    
    # Solo mostrar header común
    st.sidebar.markdown(f"**👤 Usuario:** {st.session_state.username}")
    
    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()
    
    # Mostrar título en página principal
    st.title("💊 Control de Cupos - Medicamentos")
    st.info("Seleccione una página en el menú lateral ⬅️")

if __name__ == "__main__":
    main()
