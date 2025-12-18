"""
AUTENTICACIÓN COMPACTA - VERSIÓN CENTRADA
Login pequeño y bien balanceado
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
    """Login pequeño y perfectamente centrado"""
    
    # CSS optimizado para centrado perfecto
    st.markdown("""
    <style>
        /* Ocultar elementos de Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Contenedor principal centrado */
        .stApp {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        /* Card compacta y centrada */
        .login-card-center {
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
            padding: 35px 30px;
            width: 100%;
            max-width: 360px; /* Reducido para mejor ajuste */
            border: 1px solid rgba(0, 0, 0, 0.05);
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        /* Header compacto */
        .login-header-center {
            text-align: center;
            margin-bottom: 25px;
            width: 100%;
        }
        
        .logo-center {
            font-size: 2.2rem; /* Reducido */
            color: #0066CC;
            margin-bottom: 8px;
        }
        
        .title-center {
            font-size: 1.5rem; /* Reducido para caber en 360px */
            font-weight: 700;
            color: #1e40af;
            margin-bottom: 5px;
            letter-spacing: -0.5px;
        }
        
        .subtitle-center {
            color: #64748b;
            font-size: 0.85rem;
            margin-bottom: 10px;
        }
        
        /* Formulario centrado */
        .form-center {
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 16px; /* Espaciado uniforme */
        }
        
        /* Inputs centrados */
        .input-center {
            width: 100%;
        }
        
        .input-label-center {
            color: #475569;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 6px;
            display: block;
        }
        
        .input-field-center {
            width: 100%;
            padding: 12px 14px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 0.95rem;
            transition: all 0.2s;
        }
        
        .input-field-center:focus {
            outline: none;
            border-color: #0066CC;
            box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
        }
        
        /* Botón centrado y prominente */
        .btn-center {
            background: #0066CC;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 14px;
            font-size: 1rem;
            font-weight: 600;
            width: 100%;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 10px;
            margin-bottom: 5px;
        }
        
        .btn-center:hover {
            background: #0052a3;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 102, 204, 0.2);
        }
        
        /* Contenedor para mensajes (debajo del botón) */
        .messages-container {
            width: 100%;
            margin-top: 5px;
            min-height: 50px; /* Espacio reservado para mensajes */
        }
        
        /* Mensajes centrados */
        .alert-center {
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 0.85rem;
            text-align: center;
            width: 100%;
        }
        
        .success-center {
            background: #d1fae5;
            color: #065f46;
            border: 1px solid #a7f3d0;
        }
        
        .error-center {
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #fecaca;
        }
        
        .warning-center {
            background: #fef3c7;
            color: #92400e;
            border: 1px solid #fde68a;
        }
        
        /* Footer mínimo */
        .footer-center {
            text-align: center;
            margin-top: 20px;
            color: #94a3b8;
            font-size: 0.75rem;
            width: 100%;
        }
        
        /* Responsive adicional */
        @media (max-width: 400px) {
            .login-card-center {
                padding: 25px 20px;
                margin: 10px;
            }
            
            .title-center {
                font-size: 1.3rem;
            }
            
            .logo-center {
                font-size: 2rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Contenedor principal
    st.markdown('<div class="login-card-center">', unsafe_allow_html=True)
    
    # Header compacto
    st.markdown('<div class="login-header-center">', unsafe_allow_html=True)
    st.markdown('<div class="logo-center">💊</div>', unsafe_allow_html=True)
    st.markdown('<div class="title-center">TODODROGAS</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-center">Sistema de Gestión de Cupos</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Contenedor para el formulario
    form_container = st.empty()
    
    with form_container.form("login_form"):
        st.markdown('<div class="form-center">', unsafe_allow_html=True)
        
        # Usuario
        st.markdown('<div class="input-center">', unsafe_allow_html=True)
        st.markdown('<label class="input-label-center">Usuario</label>', unsafe_allow_html=True)
        username = st.text_input("", placeholder="Ingresa tu usuario", label_visibility="collapsed", key="user_input")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Contraseña
        st.markdown('<div class="input-center">', unsafe_allow_html=True)
        st.markdown('<label class="input-label-center">Contraseña</label>', unsafe_allow_html=True)
        password = st.text_input("", type="password", placeholder="Ingresa tu contraseña", label_visibility="collapsed", key="pass_input")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botón en el centro
        submit_button = st.form_submit_button("ACCEDER AL SISTEMA", use_container_width=True, type="primary")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Contenedor para mensajes (debajo del botón)
    st.markdown('<div class="messages-container">', unsafe_allow_html=True)
    
    # Manejar el submit fuera del form para mejor control
    if 'login_submitted' not in st.session_state:
        st.session_state.login_submitted = False
    
    # Si se presionó el botón
    if submit_button:
        st.session_state.login_submitted = True
        
        if username and password:
            with st.spinner("Verificando credenciales..."):
                time.sleep(1)
                authenticated, user = authenticate(username, password)
                
                if authenticated:
                    st.session_state.user = user
                    st.session_state.authenticated = True
                    st.markdown('<div class="alert-center success-center">✓ Acceso concedido. Redirigiendo...</div>', unsafe_allow_html=True)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.markdown('<div class="alert-center error-center">✗ Usuario o contraseña incorrectos</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-center warning-center">⚠️ Completa todos los campos</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Cierre de messages-container
    
    # Footer mínimo
    st.markdown('<div class="footer-center">© 2024 Tododrogas • v1.0.0</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Cierre de login-card-center

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
        st.error("⛔ Acceso restringido a administradores")
        st.stop()
    
    return user
