"""
MÓDULO DE AUTENTICACIÓN - SISTEMA TODODROGAS
Login estilo Rappi con seguridad robusta
"""

import streamlit as st
import hashlib
import time
from datetime import datetime

def hash_password(password):
    """Encripta una contraseña usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    """Autentica un usuario contra la base de datos"""
    import sqlite3
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        # Buscar usuario
        cursor.execute('''
        SELECT id, username, nombre, rol, password_hash 
        FROM usuarios 
        WHERE username = ? AND activo = 1
        ''', (username,))
        
        user_data = cursor.fetchone()
        
        if not user_data:
            return False, None
        
        user_id, stored_username, nombre, rol, stored_hash = user_data
        
        # Verificar contraseña
        if hash_password(password) != stored_hash:
            return False, None
        
        # Actualizar último login
        cursor.execute('''
        UPDATE usuarios 
        SET ultimo_login = CURRENT_TIMESTAMP 
        WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        
        # Crear objeto de usuario
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
        print(f"Error en autenticación: {str(e)}")
        return False, None
    finally:
        conn.close()

def show_login_screen():
    """Muestra la pantalla de login estilo Rappi"""
    
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 15px 50px rgba(0, 102, 204, 0.2);
        }
        
        .login-title {
            text-align: center;
            color: #0066CC;
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 10px;
        }
        
        .login-subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        
        .login-input {
            margin-bottom: 20px;
        }
        
        .login-button {
            width: 100%;
            margin-top: 20px;
        }
        
        .login-footer {
            text-align: center;
            margin-top: 30px;
            color: #999;
            font-size: 0.9rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Logo y título
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-title">💊</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-title">TODODROGAS</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Sistema de Gestión de Cupos</div>', unsafe_allow_html=True)
    
    st.markdown('---')
    
    # Formulario de login
    with st.form("login_form"):
        username = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario")
        password = st.text_input("🔒 Contraseña", type="password", placeholder="Ingresa tu contraseña")
        
        col1, col2 = st.columns(2)
        with col1:
            remember = st.checkbox("Recordarme")
        with col2:
            if st.form_submit_button("🚀 Ingresar", use_container_width=True):
                if username and password:
                    with st.spinner("Verificando credenciales..."):
                        time.sleep(1)  # Simular validación
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
    
    # Información de credenciales (solo en desarrollo)
    with st.expander("ℹ️ Credenciales de prueba"):
        st.info("""
        **Usuario Administrador:**
        - Usuario: `admin`
        - Contraseña: `admin123`
        
        **Usuario Normal:**
        - Usuario: `cartera`
        - Contraseña: `cartera123`
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="login-footer">', unsafe_allow_html=True)
    st.markdown("© 2024 Sistema de Gestión de Cupos • Versión 1.0")
    st.markdown('</div>', unsafe_allow_html=True)

def check_authentication():
    """Verifica si el usuario está autenticado"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        show_login_screen()
        st.stop()
    
    return st.session_state.get('user', {})

def logout():
    """Cierra la sesión del usuario"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def require_admin():
    """Verifica que el usuario sea administrador"""
    user = check_authentication()
    
    if user.get('rol') != 'admin':
        st.error("⛔ Acceso denegado. Se requieren privilegios de administrador.")
        st.stop()
    
    return user
