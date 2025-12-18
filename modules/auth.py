"""
MÓDULO DE AUTENTICACIÓN - ESTILO FUTURISTA
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
    """Login estilo glass futurista"""
    
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 0 !important;
        }
        
        .login-wrapper {
            min-height: 100vh;
            background: linear-gradient(135deg, #FFFFFF 0%, #F7FAFC 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
        
        .glass-login {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(30px);
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            padding: 3rem;
            width: 100%;
            max-width: 400px;
        }
        
        .login-title {
            text-align: center;
            font-size: 2rem;
            font-weight: 800;
            color: #1A1A1A;
            margin-bottom: 0.5rem;
        }
        
        .login-subtitle {
            text-align: center;
            color: #4A5568;
            margin-bottom: 2rem;
        }
        
        .glass-input {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 12px;
            padding: 14px 16px;
            width: 100%;
            margin-bottom: 1rem;
        }
        
        .glass-btn {
            background: linear-gradient(135deg, #0066FF, #4D94FF);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 14px;
            width: 100%;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .glass-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 102, 255, 0.3);
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="glass-login">', unsafe_allow_html=True)
    
    # Título
    st.markdown('<div class="login-title">💊</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-title">TODODROGAS</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Sistema de Gestión de Cupos</div>', unsafe_allow_html=True)
    
    # Formulario
    with st.form("login_form"):
        username = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario")
        password = st.text_input("🔒 Contraseña", type="password", placeholder="Ingresa tu contraseña")
        
        if st.form_submit_button("🚀 Ingresar", use_container_width=True):
            if username and password:
                with st.spinner("Verificando..."):
                    time.sleep(1)
                    authenticated, user = authenticate(username, password)
                    
                    if authenticated:
                        st.session_state.user = user
                        st.session_state.authenticated = True
                        st.success(f"¡Bienvenido, {user['nombre']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas")
            else:
                st.warning("⚠️ Completa todos los campos")
    
    # Credenciales de prueba
    with st.expander("🔑 Credenciales de prueba"):
        st.info("""
        **Admin:** admin / admin123  
        **Usuario:** cartera / cartera123
        """)
    
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
