"""
AUTENTICACIÓN COMPACTA - SISTEMA TODODROGAS
Login pequeño y centrado
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
    """Login pequeño y centrado"""
    
    # Ocultar elementos de Streamlit
    st.markdown("""
    <style>
        /* Ocultar elementos no necesarios */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Fondo general */
        .stApp {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Card pequeña centrada */
        .login-small {
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
            padding: 30px; /* REDUCIDO */
            width: 100%;
            max-width: 350px; /* REDUCIDO */
            margin: 20px;
            border: 1px solid rgba(0, 0, 0, 0.05);
        }
        
        /* Header compacto */
        .login-header-small {
            text-align: center;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px; /* Píldora pegada al título */
        }
        
        .logo-small {
            font-size: 2.2rem; /* Ajustado */
            color: #0066CC;
        }
        
        .title-small {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1e40af;
        }
        
        .subtitle-small {
            color: #64748b;
            font-size: 0.9rem;
            text-align: center;
            margin-top: 5px;
        }
        
        /* Inputs con fondo azul claro */
        .input-small {
            margin-bottom: 15px;
        }
        
        .input-label-small {
            color: #475569;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 6px;
            display: block;
        }
        
        .input-field-small {
            width: 100%;
            padding: 10px 14px; /* REDUCIDO */
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 0.95rem;
            transition: all 0.2s;
            background-color: #f0f8ff; /* AZUL CLARO */
        }
        
        .input-field-small:focus {
            outline: none;
            border-color: #0066CC;
            box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
            background-color: #e6f2ff; /* AZUL MÁS INTENSO AL FOCUS */
        }
        
        /* Botón principal - EL ÚNICO BOTÓN */
        .stButton > button {
            background: #0066CC;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px;
            font-size: 1rem;
            font-weight: 600;
            width: 100%;
            margin-top: 10px;
        }
        
        .stButton > button:hover {
            background: #0052a3;
        }
        
        /* Mensajes pequeños */
        .alert-small {
            padding: 12px 16px;
            border-radius: 10px;
            margin: 15px 0;
            font-size: 0.9rem;
        }
        
        .success-small {
            background: #d1fae5;
            color: #065f46;
            border: 1px solid #a7f3d0;
        }
        
        .error-small {
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #fecaca;
        }
        
        .warning-small {
            background: #fef3c7;
            color: #92400e;
            border: 1px solid #fde68a;
        }
        
        /* Footer mínimo */
        .footer-small {
            text-align: center;
            margin-top: 20px;
            color: #94a3b8;
            font-size: 0.75rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Contenedor pequeño centrado
    st.markdown('<div class="login-small">', unsafe_allow_html=True)
    
    # Header - Píldora PEGADA al título
    st.markdown('<div class="login-header-small">', unsafe_allow_html=True)
    st.markdown('<div class="logo-small">💊</div>', unsafe_allow_html=True)
    st.markdown('<div class="title-small">TODODROGAS</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Subtítulo
    st.markdown('<div class="subtitle-small">Control de Cupos</div>', unsafe_allow_html=True)
    
    # Formulario - SOLO UN BOTÓN (ACCEDER)
    with st.form("login_form"):
        # Usuario
        st.markdown('<div class="input-small">', unsafe_allow_html=True)
        st.markdown('<label class="input-label-small">Usuario</label>', unsafe_allow_html=True)
        username = st.text_input("", placeholder="Ingresa tu usuario", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Contraseña
        st.markdown('<div class="input-small">', unsafe_allow_html=True)
        st.markdown('<label class="input-label-small">Contraseña</label>', unsafe_allow_html=True)
        password = st.text_input("", type="password", placeholder="Ingresa tu contraseña", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ⭐⭐ SOLO ESTE BOTÓN - EL BOTÓN "ACCEDER" ⭐⭐
        submit_button = st.form_submit_button("ACCEDER", use_container_width=True)
        
        if submit_button:
            if username and password:
                with st.spinner("Verificando..."):
                    time.sleep(1)
                    authenticated, user = authenticate(username, password)
                    
                    if authenticated:
                        st.session_state.user = user
                        st.session_state.authenticated = True
                        st.markdown('<div class="alert-small success-small">✓ Acceso concedido</div>', unsafe_allow_html=True)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.markdown('<div class="alert-small error-small">✗ Credenciales incorrectas</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-small warning-small">⚠️ Completa todos los campos</div>', unsafe_allow_html=True)
    
    # Footer mínimo
    st.markdown('<div class="footer-small">© 2024</div>', unsafe_allow_html=True)
    
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
        st.error("⛔ Acceso restringido a administradores")
        st.stop()
    
    return user
