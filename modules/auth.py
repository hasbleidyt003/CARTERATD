"""
AUTENTICACIÓN - GLASSMORPHISM CON AZUL PURISTA
Efecto cristal con tonos azules brillantes - Placeholders integrados
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
    """Login con efecto Glassmorphism - SOLO PLACEHOLDERS"""
    
    # CSS con Glassmorphism y azul purista - SIN LABELS
    st.markdown("""
    <style>
        /* RESET COMPLETO - SIN LABELS */
        #MainMenu, footer, header {
            display: none !important;
        }
        
        /* OCULTAR CUALQUIER LABEL DE STREAMLIT */
        label, .stTextInput label, .stTextInput p, 
        div[data-testid="stForm"] > div > div > div:first-child {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            opacity: 0 !important;
        }
        
        .stApp {
            overflow: hidden;
        }
        
        /* 1) FONDO CON GRADIENTE AZUL PURISTA */
        .stApp {
            background: linear-gradient(
                135deg,
                #e8f4ff 0%,
                #d4e7ff 25%,
                #b8d4ff 50%,
                #9cc2ff 75%,
                #7fb0ff 100%
            );
            min-height: 100vh;
            margin: 0;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        
        /* Efecto de brillo */
        .stApp::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.4) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.3) 0%, transparent 50%);
            pointer-events: none;
        }
        
        /* 2) GLASS CARD */
        .glass-card {
            backdrop-filter: blur(20px) saturate(200%);
            background: rgba(255, 255, 255, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.4);
            border-radius: 28px;
            box-shadow: 
                0 25px 60px rgba(0, 102, 255, 0.25),
                0 8px 25px rgba(0, 102, 255, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.6);
            padding: 60px 50px;
            width: 100%;
            max-width: 480px;
            margin: 20px;
            position: relative;
            overflow: hidden;
            z-index: 10;
        }
        
        /* Borde brillante */
        .glass-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 28px;
            padding: 2px;
            background: linear-gradient(
                135deg,
                rgba(255, 255, 255, 0.8) 0%,
                rgba(255, 255, 255, 0.4) 25%,
                rgba(100, 180, 255, 0.6) 50%,
                rgba(0, 120, 255, 0.8) 75%,
                rgba(0, 80, 255, 0.9) 100%
            );
            -webkit-mask: 
                linear-gradient(#fff 0 0) content-box, 
                linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            pointer-events: none;
        }
        
        /* 3) HEADER */
        .glass-header {
            text-align: center;
            margin-bottom: 50px;
            position: relative;
            z-index: 2;
        }
        
        .glass-logo {
            font-size: 4.5rem;
            margin-bottom: 25px;
            display: inline-block;
            background: linear-gradient(
                135deg,
                #0066ff 0%,
                #0099ff 25%,
                #00ccff 50%,
                #33ccff 75%,
                #66ccff 100%
            );
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            filter: drop-shadow(0 4px 12px rgba(0, 102, 255, 0.4));
        }
        
        .glass-title {
            font-size: 3rem;
            font-weight: 900;
            background: linear-gradient(
                135deg,
                #003366 0%,
                #0066cc 50%,
                #0099ff 100%
            );
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 12px;
            letter-spacing: -0.5px;
        }
        
        .glass-subtitle {
            color: rgba(0, 51, 102, 0.9);
            font-size: 1.1rem;
            font-weight: 500;
            opacity: 0.9;
        }
        
        /* 4) INPUTS - PLACEHOLDERS VISIBLES, SIN LABELS */
        .login-input-container {
            margin-bottom: 25px;
        }
        
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.9) !important;
            backdrop-filter: blur(10px) !important;
            border: 2px solid rgba(255, 255, 255, 0.6) !important;
            border-radius: 16px !important;
            padding: 20px 24px !important;
            font-size: 1.1rem !important;
            color: #003366 !important;
            transition: all 0.3s ease !important;
            box-shadow: 
                inset 0 2px 6px rgba(0, 0, 0, 0.05),
                0 4px 12px rgba(0, 102, 255, 0.15) !important;
            width: 100% !important;
            height: 60px !important;
        }
        
        /* PLACEHOLDER ESTILIZADO */
        .stTextInput > div > div > input::placeholder {
            color: rgba(0, 51, 102, 0.6) !important;
            font-weight: 500;
            font-size: 1.05rem;
        }
        
        .stTextInput > div > div > input:focus {
            background: rgba(255, 255, 255, 0.95) !important;
            border-color: rgba(0, 153, 255, 0.8) !important;
            box-shadow: 
                0 0 0 4px rgba(0, 153, 255, 0.25),
                inset 0 2px 6px rgba(0, 0, 0, 0.05) !important;
            outline: none !important;
        }
        
        /* 5) BOTÓN PRINCIPAL */
        .stButton > button {
            background: linear-gradient(
                135deg,
                #0066ff 0%,
                #0088ff 25%,
                #00aaff 50%,
                #00ccff 75%,
                #33ddff 100%
            ) !important;
            color: white !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 22px 36px !important;
            font-size: 1.15rem !important;
            font-weight: 800 !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            box-shadow: 
                0 12px 30px rgba(0, 102, 255, 0.4),
                0 4px 15px rgba(0, 102, 255, 0.2) !important;
            letter-spacing: 0.5px !important;
            margin-top: 10px !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 
                0 16px 40px rgba(0, 102, 255, 0.5),
                0 6px 20px rgba(0, 102, 255, 0.3) !important;
        }
        
        /* 6) MENSAJES */
        .glass-alert {
            padding: 18px 22px;
            border-radius: 16px;
            margin: 25px 0;
            font-size: 1rem;
            border: 2px solid;
            backdrop-filter: blur(15px);
            text-align: center;
            font-weight: 600;
        }
        
        .glass-success {
            color: #003311;
            border-color: rgba(0, 204, 102, 0.4);
            background: rgba(0, 255, 128, 0.2);
        }
        
        .glass-error {
            color: #330000;
            border-color: rgba(255, 0, 51, 0.4);
            background: rgba(255, 102, 102, 0.2);
        }
        
        .glass-warning {
            color: #332200;
            border-color: rgba(255, 153, 0, 0.4);
            background: rgba(255, 204, 102, 0.2);
        }
        
        /* 7) FOOTER */
        .glass-footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 30px;
            border-top: 2px solid rgba(255, 255, 255, 0.3);
            color: rgba(0, 51, 102, 0.8);
            font-size: 0.95rem;
            font-weight: 500;
        }
        
        /* 8) SPACING MEJORADO */
        .glass-form-container {
            position: relative;
            z-index: 2;
        }
        
        .login-spacing {
            margin-bottom: 30px;
        }
        
        /* 9) OCULTAR SCROLLBAR */
        ::-webkit-scrollbar {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Contenedor principal
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="glass-header">', unsafe_allow_html=True)
    st.markdown('<div class="glass-logo">🔷</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-title">TODODROGAS</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-subtitle">Sistema Corporativo de Gestión</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Formulario SOLO con placeholders
    with st.form("login_form"):
        st.markdown('<div class="glass-form-container">', unsafe_allow_html=True)
        
        # Usuario - SOLO PLACEHOLDER
        st.markdown('<div class="login-spacing"></div>', unsafe_allow_html=True)
        username = st.text_input(
            " ",
            placeholder="Ingrese su usuario", 
            label_visibility="collapsed",
            key="username_login"
        )
        
        # Contraseña - SOLO PLACEHOLDER  
        st.markdown('<div class="login-spacing"></div>', unsafe_allow_html=True)
        password = st.text_input(
            "  ",
            type="password", 
            placeholder="Ingrese su contraseña", 
            label_visibility="collapsed",
            key="password_login"
        )
        
        # Botón principal
        submit_button = st.form_submit_button("🔐 ACCEDER AL SISTEMA", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if submit_button:
            if username and password:
                with st.spinner("Validando credenciales..."):
                    time.sleep(1.2)
                    authenticated, user = authenticate(username, password)
                    
                    if authenticated:
                        st.session_state.user = user
                        st.session_state.authenticated = True
                        st.markdown('<div class="glass-alert glass-success">✓ Acceso autorizado. Redirigiendo...</div>', unsafe_allow_html=True)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.markdown('<div class="glass-alert glass-error">✗ Credenciales incorrectas</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="glass-alert glass-warning">⚠️ Complete todos los campos</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="glass-footer">© 2024 Tododrogas S.A.S • v3.0</div>', unsafe_allow_html=True)
    
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
