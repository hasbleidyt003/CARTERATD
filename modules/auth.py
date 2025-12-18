"""
AUTENTICACIÓN CON ESTILO BRILLANTE
"""

import streamlit as st
import hashlib
import time
from datetime import datetime

def hash_password(password):
    """Encripta contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    """Autentica usuario"""
    import sqlite3
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id, username, nombre, rol, password_hash FROM usuarios WHERE username = ?', (username,))
        user_data = cursor.fetchone()
        
        if not user_data:
            return False, None
        
        user_id, stored_username, nombre, rol, stored_hash = user_data
        
        if hash_password(password) != stored_hash:
            return False, None
        
        cursor.execute('UPDATE usuarios SET ultimo_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
        conn.commit()
        
        user = {
            'id': user_id,
            'username': stored_username,
            'nombre': nombre,
            'rol': rol,
            'authenticated': True,
            'login_time': datetime.now()
        }
        
        return True, user
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False, None
    finally:
        conn.close()

def show_login_screen():
    """Login estilo glass con efectos brillantes"""
    
    # CSS inline para el login
    st.markdown("""
    <style>
        .stApp {
            background: transparent !important;
        }
        
        .stApp > header {
            display: none !important;
        }
        
        #MainMenu, footer, header {
            display: none !important;
        }
        
        .block-container {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Contenedor principal del login
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-glass-card">', unsafe_allow_html=True)
    
    # Icono y título
    st.markdown('<div class="login-icon">💊</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="login-title">TODODROGAS</h1>', unsafe_allow_html=True)
    st.markdown('<p class="login-subtitle">Sistema de Gestión de Cupos</p>', unsafe_allow_html=True)
    
    # Formulario de login
    with st.form("login_form", clear_on_submit=False):
        # Campo de usuario
        st.markdown('<div style="margin-bottom: 1rem;">', unsafe_allow_html=True)
        username = st.text_input(
            "",
            placeholder="👤 Ingresa tu usuario",
            label_visibility="collapsed",
            key="username_input"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Campo de contraseña
        st.markdown('<div style="margin-bottom: 1.5rem;">', unsafe_allow_html=True)
        password = st.text_input(
            "",
            type="password",
            placeholder="🔒 Ingresa tu contraseña",
            label_visibility="collapsed",
            key="password_input"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Opciones adicionales
        col1, col2 = st.columns([1, 2])
        with col1:
            remember = st.checkbox("Recordarme", value=True)
        
        # Botón de ingreso
        submit_button = st.form_submit_button(
            "🚀 INGRESAR AL SISTEMA",
            use_container_width=True,
            type="primary"
        )
        
        if submit_button:
            if username and password:
                with st.spinner("Verificando credenciales..."):
                    time.sleep(1.5)  # Simulación de validación
                    authenticated, user = authenticate(username, password)
                    
                    if authenticated:
                        st.session_state.user = user
                        st.session_state.authenticated = True
                        st.success(f"¡Bienvenido, {user['nombre']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
            else:
                st.warning("⚠️ Por favor completa todos los campos")
    
    # Información del sistema (sin credenciales)
    st.markdown('<div style="margin-top: 2rem; text-align: center;">', unsafe_allow_html=True)
    st.markdown('<hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, rgba(0,0,0,0.1), transparent); margin: 1.5rem 0;">', unsafe_allow_html=True)
    
    # Información de ayuda
    with st.expander("🆘 ¿Necesitas ayuda?", expanded=False):
        st.info("""
        **Para acceder al sistema:**
        
        1. Contacta al administrador del sistema
        2. Solicita tus credenciales de acceso
        3. Si olvidaste tu contraseña, contacta al soporte técnico
        
        **Soporte:** soporte@tododrogas.com
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer del login
    st.markdown('<div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid rgba(0,0,0,0.05);">', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 0.9rem; margin: 0;">© 2024 Tododrogas • Versión 1.0</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def check_authentication():
    """Verifica autenticación"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        show_login_screen()
        st.stop()
    
    return st.session_state.get('user', {})

def logout():
    """Cierra sesión"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def require_admin():
    """Requiere rol admin"""
    user = check_authentication()
    
    if user.get('rol') != 'admin':
        st.error("⛔ Acceso solo para administradores")
        st.stop()
    
    return user
