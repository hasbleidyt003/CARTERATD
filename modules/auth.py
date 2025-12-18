"""
AUTENTICACIÓN - GLASSMORPHISM CORPORATIVO
Balance 70% blanco / 30% azul sutil con efecto cristal real
Píldora con color original preservado
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
    """Login con verdadero efecto Glassmorphism - Píldora con color original"""
    
    # CSS con Glassmorphism real - COLOR ORIGINAL DE PÍLDORA PRESERVADO
    st.markdown("""
    <style>
        /* RESET COMPLETO */
        #MainMenu, footer, header {
            display: none;
        }
        .stApp {
            overflow: hidden;
        }
        
        /* 1) FONDO CON GRADIENTE SUAVE - 70% BLANCO / 30% AZUL SUTIL */
        .stApp {
            background: linear-gradient(
                140deg,
                #ffffff 0%,          /* 70% - Blanco puro */
                #f9fbff 30%,         /* Blanco con toque azul */
                #f0f5ff 60%,         /* 20% - Azul muy claro */
                #e8f0ff 100%         /* 10% - Azul ligero */
            );
            min-height: 100vh;
            margin: 0;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* 2) GLASS CARD - EFECTO CRISTAL REAL */
        .glass-card {
            backdrop-filter: blur(16px) saturate(180%);
            background: rgba(255, 255, 255, 0.38);
            border: 1px solid rgba(255, 255, 255, 0.62);
            border-radius: 24px;
            box-shadow: 
                0 12px 40px rgba(66, 153, 225, 0.12),
                0 4px 15px rgba(0, 0, 0, 0.06),
                inset 0 0 0 1px rgba(255, 255, 255, 0.8);
            padding: 50px 45px;
            width: 100%;
            max-width: 440px;
            margin: 20px;
            position: relative;
            overflow: hidden;
        }
        
        /* Efecto de vidrio esmerilado */
        .glass-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(
                135deg,
                rgba(255, 255, 255, 0.15) 0%,
                rgba(255, 255, 255, 0.05) 50%,
                rgba(255, 255, 255, 0.1) 100%
            );
            pointer-events: none;
            border-radius: 24px;
            z-index: 0;
        }
        
        /* 3) HEADER GLASS - PÍLDORA CON COLOR ORIGINAL */
        .glass-header {
            text-align: center;
            margin-bottom: 45px;
            position: relative;
            z-index: 1;
        }
        
        /* COLOR ORIGINAL DE PÍLDORA PRESERVADO - NO CAMBIAR */
        .glass-logo {
            font-size: 3.2rem;
            background: linear-gradient(135deg, #4299e1 0%, #63b3ed 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 18px;
            filter: drop-shadow(0 4px 8px rgba(66, 153, 225, 0.2));
        }
        
        .glass-title {
            font-size: 2.4rem;
            font-weight: 800;
            color: #1a365d;
            margin-bottom: 10px;
            letter-spacing: -0.5px;
            text-shadow: 0 2px 4px rgba(255, 255, 255, 0.8);
        }
        
        .glass-subtitle {
            color: #4a5568;
            font-size: 1.05rem;
            font-weight: 400;
            opacity: 0.85;
        }
        
        /* 4) INPUTS GLASS - TRANSLÚCIDOS */
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.7) !important;
            backdrop-filter: blur(8px) !important;
            border: 1.5px solid rgba(200, 200, 200, 0.35) !important;
            border-radius: 14px !important;
            padding: 16px 20px !important;
            font-size: 1.08rem !important;
            color: #2d3748 !important;
            transition: all 0.3s ease !important;
            box-shadow: 
                inset 0 1px 3px rgba(0, 0, 0, 0.05),
                0 2px 4px rgba(0, 0, 0, 0.04) !important;
        }
        
        .stTextInput > div > div > input:focus {
            background: rgba(255, 255, 255, 0.85) !important;
            border-color: #63b3ed !important;
            box-shadow: 
                0 0 0 3px rgba(99, 179, 237, 0.18),
                inset 0 1px 3px rgba(0, 0, 0, 0.05) !important;
            outline: none !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: #a0aec0 !important;
            opacity: 0.7 !important;
        }
        
        /* 5) BOTÓN PRINCIPAL - 30% AZUL INTENSO */
        .stButton > button {
            background: linear-gradient(135deg, #3182ce 0%, #2b6cb0 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 14px !important;
            padding: 18px 32px !important;
            font-size: 1.12rem !important;
            font-weight: 700 !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            box-shadow: 
                0 8px 25px rgba(49, 130, 206, 0.3),
                0 3px 10px rgba(43, 108, 176, 0.2) !important;
            letter-spacing: 0.3px !important;
            margin-top: 15px !important;
            backdrop-filter: blur(4px) !important;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #2b6cb0 0%, #2c5282 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 
                0 12px 30px rgba(43, 108, 176, 0.35),
                0 4px 12px rgba(43, 108, 176, 0.25) !important;
        }
        
        /* 6) LABELS GLASS */
        .glass-label {
            color: #2d3748;
            font-size: 0.95rem;
            font-weight: 600;
            margin-bottom: 12px;
            display: block;
            padding-left: 5px;
            text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
        }
        
        /* 7) MENSAJES GLASS */
        .glass-alert {
            padding: 18px 22px;
            border-radius: 14px;
            margin: 28px 0;
            font-size: 1rem;
            border: 1px solid;
            backdrop-filter: blur(12px);
            position: relative;
            z-index: 1;
        }
        
        .glass-success {
            color: #22543d;
            border-color: rgba(154, 230, 180, 0.5);
            background: rgba(240, 255, 244, 0.6);
        }
        
        .glass-error {
            color: #742a2a;
            border-color: rgba(252, 129, 129, 0.5);
            background: rgba(255, 245, 245, 0.6);
        }
        
        .glass-warning {
            color: #744210;
            border-color: rgba(251, 211, 141, 0.5);
            background: rgba(255, 250, 240, 0.6);
        }
        
        /* 8) FOOTER GLASS */
        .glass-footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 28px;
            border-top: 1px solid rgba(226, 232, 240, 0.5);
            color: #4a5568;
            font-size: 0.92rem;
            opacity: 0.8;
            position: relative;
            z-index: 1;
            text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
        }
        
        /* 9) CONTENEDOR DE FORMULARIO */
        .glass-form-container {
            position: relative;
            z-index: 1;
        }
        
        /* 10) EFECTO DE LUZ EN BORDE - COLOR ORIGINAL */
        .glass-card::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: linear-gradient(90deg, 
                rgba(66, 153, 225, 0.3) 0%,
                rgba(99, 179, 237, 0.5) 50%,
                rgba(66, 153, 225, 0.3) 100%);
            border-radius: 24px 24px 0 0;
            opacity: 0.6;
        }
        
        /* 11) MEJORA PARA STREAMLIT NATIVO */
        .stTextInput {
            margin-bottom: 22px;
        }
        
        /* 12) ANIMACIÓN SUTIL */
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0px); }
        }
        
        .glass-card {
            animation: float 6s ease-in-out infinite;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Contenedor principal con efecto glass
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # Header con efecto glass - PÍLDORA CON COLOR ORIGINAL
    st.markdown('<div class="glass-header">', unsafe_allow_html=True)
    st.markdown('<div class="glass-logo">💊</div>', unsafe_allow_html=True)  # COLOR ORIGINAL PRESERVADO
    st.markdown('<div class="glass-title">TODODROGAS</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-subtitle">Sistema Corporativo de Gestión</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Formulario
    with st.form("login_form"):
        st.markdown('<div class="glass-form-container">', unsafe_allow_html=True)
        
        # Usuario
        st.markdown('<label class="glass-label">Usuario</label>', unsafe_allow_html=True)
        username = st.text_input("", placeholder="Ingrese su usuario", label_visibility="collapsed", key="username_input")
        
        # Contraseña
        st.markdown('<label class="glass-label">Contraseña</label>', unsafe_allow_html=True)
        password = st.text_input("", type="password", placeholder="Ingrese su contraseña", label_visibility="collapsed", key="password_input")
        
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
                        st.markdown('<div class="glass-alert glass-error">✗ Credenciales incorrectas. Intente nuevamente.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="glass-alert glass-warning">⚠️ Complete todos los campos</div>', unsafe_allow_html=True)
    
    # Footer
 
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
