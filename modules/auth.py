import streamlit as st

# Usuarios permitidos
USUARIOS = {
    "cartera": "admin123",      # Usuario administrador
    "supervisor": "view123",    # Usuario de solo lectura
    "admin": "admin123"         # Usuario técnico
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
    
    # Centrar el formulario
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
        
        # Información de usuarios demo
        with st.expander("ℹ️ Credenciales de prueba"):
            st.markdown("""
            **Usuario administrador:**
            - Usuario: `cartera`
            - Contraseña: `admin123`
            
            **Usuario supervisor:**
            - Usuario: `supervisor`
            - Contraseña: `view123`
            """)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer del login
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6B7280; font-size: 12px;'>
        <p>Sistema de Gestión de Cartera • Versión 1.0</p>
        <p>© 2024 - Todos los derechos reservados</p>
    </div>
    """, unsafe_allow_html=True)

def check_auth():
    """Verifica si el usuario está autenticado"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        authenticate()
        st.stop()  # Detiene la ejecución aquí
    
    return True

def logout_button():
    """Cierra la sesión del usuario"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

def get_current_user():
    """Obtiene el usuario actual"""
    return st.session_state.get('username', 'Usuario')
