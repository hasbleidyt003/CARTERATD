"""
AUTENTICACIÓN CON ESTILO FUTURISTA NEGRO/AZUL
"""

import streamlit as st
import hashlib
import time
from datetime import datetime
import random

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
    """Login estilo futurista negro/azul"""
    
    # Ocultar elementos de Streamlit
    st.markdown("""
    <style>
        .stApp {
            background: #0A0A14 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        .stApp > header {
            display: none !important;
        }
        
        #MainMenu, footer, header {
            visibility: hidden !important;
        }
        
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }
        
        .stForm {
            border: none !important;
            background: transparent !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Contenedor principal
    st.markdown('<div class="login-futurista">', unsafe_allow_html=True)
    
    # Línea de escaneo
    st.markdown('<div class="scan-line"></div>', unsafe_allow_html=True)
    
    # Panel de login
    st.markdown('<div class="login-panel">', unsafe_allow_html=True)
    
    # Header con logo animado
    st.markdown('<div class="login-header">', unsafe_allow_html=True)
    
    # Logo con anillos
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.markdown('<div class="logo-rings">', unsafe_allow_html=True)
    st.markdown('<div class="ring ring-1"></div>', unsafe_allow_html=True)
    st.markdown('<div class="ring ring-2"></div>', unsafe_allow_html=True)
    st.markdown('<div class="ring ring-3"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="futuristic-logo">💊</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Títulos
    st.markdown('<h1 class="title-main">TODODROGAS</h1>', unsafe_allow_html=True)
    st.markdown('<p class="title-sub">SYSTEM ACCESS</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Formulario de login
    with st.form("login_form", clear_on_submit=False):
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        
        # Campo de usuario
        st.markdown('<div class="input-group">', unsafe_allow_html=True)
        st.markdown('<label class="input-label">USER IDENTIFICATION</label>', unsafe_allow_html=True)
        
        username = st.text_input(
            "",
            placeholder="ENTER USERNAME",
            label_visibility="collapsed",
            key="username_input"
        )
        st.markdown('<div class="input-line"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Campo de contraseña
        st.markdown('<div class="input-group">', unsafe_allow_html=True)
        st.markdown('<label class="input-label">SECURITY CREDENTIALS</label>', unsafe_allow_html=True)
        
        password = st.text_input(
            "",
            type="password",
            placeholder="ENTER PASSWORD",
            label_visibility="collapsed",
            key="password_input"
        )
        st.markdown('<div class="input-line"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Opciones
        st.markdown('<div class="checkbox-group">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 5])
        with col1:
            remember = st.checkbox("", value=True, key="remember_checkbox")
        with col2:
            st.markdown('<label class="checkbox-label">REMEMBER SESSION</label>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botón de acceso
        submit_button = st.form_submit_button(
            "INITIATE ACCESS SEQUENCE",
            use_container_width=True,
            type="primary"
        )
        
        if submit_button:
            if username and password:
                # Efecto de carga
                with st.spinner(""):
                    # Barra de progreso animada
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(i + 1)
                    
                    # Validación
                    authenticated, user = authenticate(username, password)
                    
                    if authenticated:
                        # Efecto de éxito
                        st.markdown('''
                        <div class="neon-alert success">
                            <div style="color: #00F3FF; font-weight: 600; font-size: 1.1rem;">
                                ✓ ACCESS GRANTED
                            </div>
                            <div style="color: rgba(255, 255, 255, 0.8); margin-top: 0.5rem;">
                                WELCOME, ''' + user['nombre'] + '''
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        # Guardar sesión
                        st.session_state.user = user
                        st.session_state.authenticated = True
                        
                        # Retardo antes de redirección
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        # Efecto de error
                        st.markdown('''
                        <div class="neon-alert error">
                            <div style="color: #FF3B30; font-weight: 600; font-size: 1.1rem;">
                                ✗ ACCESS DENIED
                            </div>
                            <div style="color: rgba(255, 255, 255, 0.8); margin-top: 0.5rem;">
                                INVALID CREDENTIALS DETECTED
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
            else:
                # Advertencia
                st.markdown('''
                <div class="neon-alert">
                    <div style="color: #FF9500; font-weight: 600; font-size: 1.1rem;">
                    ⚠ SECURITY PROTOCOL
                    </div>
                    <div style="color: rgba(255, 255, 255, 0.8); margin-top: 0.5rem;">
                    ALL FIELDS REQUIRED FOR ACCESS
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="login-footer">', unsafe_allow_html=True)
    
    # Información del sistema (sin credenciales)
    with st.expander("SYSTEM INFORMATION", expanded=False):
        st.markdown('''
        <div style="color: rgba(255, 255, 255, 0.6); font-size: 0.9rem; line-height: 1.6;">
            <div style="margin-bottom: 0.5rem;">
                <strong>SYSTEM:</strong> Tododrogas Control Suite v2.0
            </div>
            <div style="margin-bottom: 0.5rem;">
                <strong>STATUS:</strong> <span style="color: #00F3FF;">OPERATIONAL</span>
            </div>
            <div style="margin-bottom: 0.5rem;">
                <strong>SECURITY:</strong> Level 3 Encryption Active
            </div>
            <div>
                <strong>LAST UPDATE:</strong> ''' + datetime.now().strftime("%Y-%m-%d %H:%M") + '''
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Copyright
    st.markdown('<p class="footer-text">© 2025 TODODROGAS SECURITY SYSTEMS</p>', unsafe_allow_html=True)
    st.markdown('<p class="footer-text">UNAUTHORIZED ACCESS PROHIBITED</p>', unsafe_allow_html=True)
    
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
    # Efecto de logout
    st.markdown('''
    <div class="neon-alert">
        <div style="color: #00F3FF; font-weight: 600; font-size: 1.1rem; text-align: center;">
            SESSION TERMINATED
        </div>
        <div style="color: rgba(255, 255, 255, 0.8); text-align: center; margin-top: 0.5rem;">
            SECURITY PROTOCOLS ENGAGED
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    time.sleep(1)
    
    # Limpiar sesión
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    st.rerun()

def require_admin():
    """Requiere rol admin"""
    user = check_authentication()
    
    if user.get('rol') != 'admin':
        # Mensaje de acceso denegado estilo futurista
        st.markdown('''
        <div class="neon-alert error" style="text-align: center;">
            <div style="color: #FF3B30; font-weight: 700; font-size: 1.3rem;">
                ⛔ ACCESS VIOLATION
            </div>
            <div style="color: rgba(255, 255, 255, 0.8); margin-top: 1rem;">
                ADMINISTRATOR PRIVILEGES REQUIRED
            </div>
            <div style="color: rgba(255, 255, 255, 0.6); margin-top: 0.5rem; font-size: 0.9rem;">
                SECURITY LOCKDOWN ENGAGED
            </div>
        </div>
        ''', unsafe_allow_html=True)
        time.sleep(2)
        st.stop()
    
    return user
