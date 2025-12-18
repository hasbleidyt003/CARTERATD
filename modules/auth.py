"""
MÓDULO DE AUTENTICACIÓN - SISTEMA TODODROGAS
Login minimalista glass azul
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
    """Login minimalista glass azul centrado"""
    
    # CSS minimalista
    st.markdown("""
    <style>
        /* Reset básico */
        .stApp {
            background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
            min-height: 100vh;
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
        
        /* Contenedor centrado */
        .login-center {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        /* Card glass */
        .login-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 
                0 15px 35px rgba(0, 0, 0, 0.1),
                0 0 25px rgba(0, 102, 255, 0.1);
            padding: 40px;
            width: 100%;
            max-width: 400px;
        }
        
        /* Header con píldora al lado */
        .login-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 30px;
            justify-content: center;
        }
        
        /* Píldora */
        .pill {
            font-size: 2.5rem;
            width: 60px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #0066FF 0%, #00D4FF 100%);
            color: white;
            border-radius: 15px;
            box-shadow: 0 8px 20px rgba(0, 102, 255, 0.3);
        }
        
        /* Título */
        .title {
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #1A1A1A 0%, #0066FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            color: #666;
            font-size: 0.9rem;
            margin-top: 5px;
        }
        
        /* Inputs glass azules */
        .input-group {
            margin-bottom: 20px;
        }
        
        .input-label {
            color: #333;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 8px;
            display: block;
        }
        
        .input-field {
            background: rgba(0, 102, 255, 0.1);
            border: 2px solid rgba(0, 102, 255, 0.2);
            border-radius: 12px;
            padding: 14px 16px;
            width: 100%;
            font-size: 1rem;
            color: #333;
            transition: all 0.3s;
        }
        
        .input-field:focus {
            outline: none;
            border-color: #0066FF;
            box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.1);
            background: rgba(0, 102, 255, 0.15);
        }
        
        /* Botón */
        .login-btn {
            background: linear-gradient(135deg, #0066FF 0%, #00D4FF 100%);
            border: none;
            border-radius: 12px;
            color: white;
            padding: 16px;
            font-size: 1rem;
            font-weight: 600;
            width: 100%;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 102, 255, 0.3);
        }
        
        /* Footer */
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            text-align: center;
            color: #888;
            font-size: 0.85rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Contenedor principal
    st.markdown('<div class="login-center">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    # Header con píldora y título
    st.markdown('<div class="login-header">', unsafe_allow_html=True)
    st.markdown('<div class="pill">💊</div>', unsafe_allow_html=True)
    st.markdown('<div><div class="title">TODODROGAS</div><div class="subtitle">Sistema de Gestión</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Formulario simple
    with st.form("login_form"):
        # Usuario
        st.markdown('<div class="input-group">', unsafe_allow_html=True)
        st.markdown('<label class="input-label">Usuario</label>', unsafe_allow_html=True)
        username = st.text_input("", placeholder="Ingresa tu usuario", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Contraseña
        st.markdown('<div class="input-group">', unsafe_allow_html=True)
        st.markdown('<label class="input-label">Contraseña</label>', unsafe_allow_html=True)
        password = st.text_input("", type="password", placeholder="Ingresa tu contraseña", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botón
        submit_button = st.form_submit_button("ACCEDER", use_container_width=True, type="primary")
        
        if submit_button:
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
    
    # Footer
    st.markdown('<div class="footer">© 2024 Tododrogas</div>', unsafe_allow_html=True)
    
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
