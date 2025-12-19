import streamlit as st

def check_auth():
    """
    Verifica autenticación del usuario.
    En desarrollo, retorna siempre True.
    En producción, implementar lógica real.
    """
    # En desarrollo, siempre autenticado
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = True
    
    if not st.session_state.authenticated:
        # Mostrar formulario de login
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.title("🔐 Iniciar Sesión")
                
                with st.form("login_form"):
                    usuario = st.text_input("Usuario")
                    password = st.text_input("Contraseña", type="password")
                    
                    if st.form_submit_button("Ingresar"):
                        # Aquí iría la validación real
                        if usuario == "admin" and password == "admin":
                            st.session_state.authenticated = True
                            st.session_state.user = usuario
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas")
                return False
    return True

def get_current_user():
    """Obtiene el usuario actual"""
    return st.session_state.get('user', 'admin')

def logout():
    """Cierra sesión"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()
