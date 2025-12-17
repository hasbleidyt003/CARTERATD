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
