"""
AUTENTICACIÓN - ESTILO CORPORATIVO MINIMALISTA
Fondo 90% blanco, azul muy sutil
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
    """Login estilo corporativo minimalista"""
    
    # CSS corporativo minimalista
    st.markdown("""
    <style>
        /* Reset completo */
        #MainMenu, footer, header {
            visibility: hidden;
        }
        
        /* Fondo 90% blanco, 10% azul sutil */
        .stApp {
            background: linear-gradient(
                135deg,
                #ffffff 0%,
                #ffffff 60%,
                #f9fbff 85%,
                #f5f9ff 100%
            );
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Card vidrio suave */
        .login-card-corp {
            background: rgba(255, 255, 255, 0.92);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(0, 0, 0, 0.05);
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.04),
                0 1px 2px rgba(0, 0, 0, 0.02);
            padding: 40px;
            width: 100%;
            max-width: 420px;
            margin: 20px;
        }
        
        /* Header minimalista */
        .login-header-corp {
            text-align: center;
            margin-bottom: 35px;
        }
        
        .logo-corp {
            font-size: 2.5rem;
            color: #2c5282;
            margin-bottom: 12px;
            opacity: 0.9;
        }
        
        .title-corp {
            font-size: 2rem;
            font-weight: 700;
            color: #1a365d;
            margin-bottom: 6px;
            letter-spacing: -0.5px;
        }
        
        .subtitle-corp {
            color: #718096;
            font-size: 0.95rem;
            font-weight: 400;
        }
        
        /* Formulario minimalista */
        .form-corp {
            width: 100%;
        }
        
        /* Labels sutiles */
        .label-corp {
            color: #4a5568;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 8px;
            display: block;
        }
        
        /* Inputs con borde sutil */
        .input-corp {
            width: 100%;
            padding: 14px 16px;
            border: 1.5px solid #e2e8f0;
            border-radius: 12px;
            font-size: 1rem;
            color: #2d3748;
            background: #ffffff;
            transition: all 0.2s ease;
            margin-bottom: 20px;
        }
        
        .input-corp:focus {
            outline: none;
            border-color: #90cdf4;
            box-shadow: 0 0 0 3px rgba(144, 205, 244, 0.1);
        }
        
        /* Botón azul sutil pero visible */
        .stButton > button {
            background: linear-gradient(135deg, #4299e1, #3182ce);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 16px 32px;
            font-size: 1rem;
            font-weight: 600;
            width: 100%;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px rgba(66, 153, 225, 0.15);
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #3182ce, #2c5282);
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(66, 153, 225, 0.2);
        }
        
        /* Mensajes sutiles */
        .alert-corp {
            padding: 14px 18px;
            border-radius: 12px;
            margin: 20px 0;
            font-size: 0.95rem;
            border: 1px solid transparent;
        }
        
        .success-corp {
            background: #f0fff4;
            color: #276749;
            border-color: #c6f6d5;
        }
        
        .error-corp {
            background: #fff5f5;
            color: #c53030;
            border-color: #fed7d7;
        }
        
        .warning-corp {
            background: #fffaf0;
            color: #c05621;
            border-color: #feebc8;
        }
        
        /* Footer minimalista */
        .footer-corp {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #f1f5f9;
            color: #94a3b8;
            font-size: 0.85rem;
        }
        
        /* Loading spinner sutil */
        .stSpinner > div {
            border-color: #4299e1 transparent transparent transparent;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Contenedor principal
    st.markdown('<div class="login-card-corp">', unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="login-header-corp">', unsafe_allow_html=True)
    st.markdown('<div class="logo-corp">💊</div>', unsafe_allow_html=True)
    st.markdown('<div class="title-corp">TODODROGAS</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-corp">Gestión de Cupos Corporativa</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Formulario
    with st.form("login_form"):
        # Usuario
        st.markdown('<label class="label-corp">Usuario</label>', unsafe_allow_html=True)
        username = st.text_input("", placeholder="usuario@tododrogas.com", label_visibility="collapsed")
        
        # Contraseña
        st.markdown('<label class="label-corp">Contraseña</label>', unsafe_allow_html=True)
        password = st.text_input("", type="password", placeholder="············", label_visibility="collapsed")
        
        # Solo este botón - ACCEDER
        submit_button = st.form_submit_button("ACCEDER AL SISTEMA", use_container_width=True)
        
        if submit_button:
            if username and password:
                with st.spinner("Verificando credenciales..."):
                    time.sleep(1.2)
                    authenticated, user = authenticate(username, password)
                    
                    if authenticated:
                        st.session_state.user = user
                        st.session_state.authenticated = True
                        st.markdown('<div class="alert-corp success-corp">✓ Acceso autorizado</div>', unsafe_allow_html=True)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.markdown('<div class="alert-corp error-corp">✗ Credenciales no válidas</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-corp warning-corp">⚠️ Complete todos los campos</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="footer-corp">© 2025 Tododrogas • Sistema Corporativo</div>', unsafe_allow_html=True)
    
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
        st.error("⛔ Acceso restringido")
        st.stop()
    
    return user
