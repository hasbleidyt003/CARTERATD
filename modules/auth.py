import streamlit as st

# Usuarios permitidos (puedes cambiar las contraseñas)
USUARIOS = {
    "cartera": "admin123",  # Tú
    "supervisor": "view123"  # Solo lectura si quieres
}

def authenticate():
    """Muestra formulario de login"""
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
        
        # Información de usuarios demo (opcional)
        with st.expander("ℹ️ Usuarios de prueba"):
            st.code("""
            Usuario: cartera
            Contraseña: admin123
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: gray;'>© 2024 Sistema de Control de Cupos</div>", unsafe_allow_html=True)

def check_auth():
    """Verifica si el usuario está autenticado, muestra login si no"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        authenticate()
        st.stop()  # Detiene la ejecución aquí si no está autenticado
    
    return st.session_state.username

def logout_button():
    """Muestra botón para cerrar sesión"""
    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

def get_current_user():
    """Obtiene el usuario actualmente autenticado"""
    if st.session_state.get('authenticated', False):
        return st.session_state.get('username', 'Usuario')
    return 'Usuario'

# Función principal para probar
def main():
    st.set_page_config(
        page_title="Sistema de Cupos",
        page_icon="💰",
        layout="wide"
    )
    
    # Verificar autenticación
    username = check_auth()
    
    # Si llegó aquí, está autenticado
    st.title(f"Bienvenido, {username}")
    st.write("Sistema de Control de Cupos - Medicamentos")
    
    # Sidebar con menú y botón de logout
    with st.sidebar:
        st.write(f"**Usuario:** {username}")
        logout_button()

if __name__ == "__main__":
    main()
