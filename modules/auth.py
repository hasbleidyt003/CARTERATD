"""
AUTENTICACIÓN - ESTILO 30% AZUL CORPORATIVO
Balance 70% blanco / 30% azul sutil
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
    """Login con 30% presencia azul"""
    
    # CSS 70% blanco / 30% azul
    st.markdown("""
    <style>
        /* Reset */
        #MainMenu, footer, header {
            visibility: hidden;
        }
        
        /* Fondo 70% blanco, 30% azul sutil */
        .stApp {
            background: linear-gradient(
                145deg,
                #ffffff 0%,
                #f8fafc 30%,
                #edf4ff 50%,
                #e6f0ff 70%,
                #dbe8ff 100%
            );
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Card con 30% influencia azul */
        .login-card-30blue {
            background: linear-gradient(145deg, #ffffff, #f5f9ff);
            border-radius: 22px;
            border: 1px solid rgba(66, 153, 225, 0.15);
            box-shadow: 
                0 10px 40px rgba(66, 153, 225, 0.08),
                0 2px 8px rgba(66, 153, 225, 0.04),
                inset 0 1px 0 rgba(255, 255, 255, 0.8);
            padding: 45px 40px;
            width: 100%;
            max-width: 420px;
            margin: 20px;
            position: relative;
            overflow: hidden;
        }
        
        /* Borde azul sutil */
        .login-card-30blue::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #4299e1, #63b3ed, #4299e1);
            opacity: 0.4;
        }
        
        /* Header con 30% azul */
        .login-header-30blue {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .logo-30blue {
            font-size: 2.8rem;
            background: linear-gradient(135deg, #2b6cb0, #4299e1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 15px;
            filter: drop-shadow(0 2px 4px rgba(66, 153, 225, 0.2));
        }
        
        .title-30blue {
            font-size: 2.2rem;
            font-weight: 800;
            color: #1a365d;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }
        
        .subtitle-30blue {
            color: #4a5568;
            font-size: 1rem;
            font-weight: 400;
            opacity: 0.8;
        }
        
        /* Formulario con 30% elementos azules */
        .form-30blue {
            width: 100%;
        }
        
        /* Labels con tono azul */
        .label-30blue {
            color: #2d3748;
            font-size: 0.92rem;
            font-weight: 600;
            margin-bottom: 10px;
            display: block;
            padding-left: 4px;
        }
        
        /* Inputs con borde azul sutil */
        .input-30blue {
            width: 100%;
            padding: 15px 18px;
            border: 1.8px solid #cbd5e0;
            border-radius: 14px;
            font-size: 1.05rem;
            color: #2d3748;
            background: rgba(255, 255, 255, 0.9);
            transition: all 0.25s ease;
            margin-bottom: 22px;
            box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.04);
        }
        
        .input-30blue:focus {
            outline: none;
            border-color: #63b3ed;
            background: rgba(255, 255, 255, 1);
            box-shadow: 
                0 0 0 3px rgba(99, 179, 237, 0.15),
                inset 0 1px 3px rgba(0, 0, 0, 0.04);
        }
        
        /* Botón - 30% de presencia azul (más intenso) */
        .stButton > button {
            background: linear-gradient(135deg, #3182ce, #2b6cb0);
            color: white;
            border: none;
            border-radius: 14px;
            padding: 18px 32px;
            font-size: 1.1rem;
            font-weight: 700;
            width: 100%;
            transition: all 0.25s ease;
            box-shadow: 
                0 6px 20px rgba(49, 130, 206, 0.25),
                0 2px 8px rgba(49, 130, 206, 0.15);
            letter-spacing: 0.3px;
            margin-top: 10px;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #2b6cb0, #2c5282);
            transform: translateY(-2px);
            box-shadow: 
                0 8px 25px rgba(43, 108, 176, 0.3),
                0 3px 10px rgba(43, 108, 176, 0.2);
        }
        
        /* Mensajes con 30% tono azul */
        .alert-30blue {
            padding: 16px 20px;
            border-radius: 14px;
            margin: 25px 0;
            font-size: 0.98rem;
            border: 1px solid;
            background: rgba(255, 255, 255, 0.95);
        }
        
        .success-30blue {
            color: #22543d;
            border-color: #9ae6b4;
            background: linear-gradient(135deg, #f0fff4, #e6fffa);
        }
        
        .error-30blue {
            color: #742a2a;
            border-color: #fc8181;
            background: linear-gradient(135deg, #fff5f5, #fed7d7);
        }
        
        .warning-30blue {
            color: #744210;
            border-color: #fbd38d;
            background: linear-gradient(135deg, #fffaf0, #feebc8);
        }
        
        /* Footer con 30% tono azul */
        .footer-30blue {
            text-align: center;
            margin-top: 35px;
            padding-top: 25px;
            border-top: 1px solid #e2e8f0;
            color: #4a5568;
            font-size: 0.9rem;
            opacity: 0.7;
        }
        
        /* Placeholders azul muy sutil */
        .input-30blue::placeholder {
            color: #a0aec0;
            opacity: 0.7;
        }
        
        /* Efecto de profundidad */
        .login-card-30blue::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(145deg, transparent, rgba(66, 153, 225, 0.02));
            pointer-events: none;
            border-radius: 22px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Contenedor principal
    st.markdown('<div class="login-card-30blue">', unsafe_allow_html=True)
    
    # Header con 30% presencia azul
    st.markdown('<div class="login-header-30blue">', unsafe_allow_html=True)
    st.markdown('<div class="logo-30blue">💊</div>', unsafe_allow_html=True)
    st.markdown('<div class="title-30blue">TODODROGAS</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-30blue">Sistema Corporativo de Gestión</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Formulario
    with st.form("login_form"):
        # Usuario
        st.markdown('<label class="label-30blue">Usuario Corporativo</label>', unsafe_allow_html=True)
        username = st.text_input("", placeholder="usuario.corporativo@tododrogas.co", label_visibility="collapsed")
        
        # Contraseña
        st.markdown('<label class="label-30blue">Credencial de Acceso</label>', unsafe_allow_html=True)
        password = st.text_input("", type="password", placeholder="··················", label_visibility="collapsed")
        
        # Botón principal
        submit_button = st.form_submit_button("🔐 ACCEDER AL SISTEMA", use_container_width=True)
        
        if submit_button:
            if username and password:
                with st.spinner("Validando credenciales..."):
                    time.sleep(1.3)
                    authenticated, user = authenticate(username, password)
                    
                    if authenticated:
                        st.session_state.user = user
                        st.session_state.authenticated = True
                        st.markdown('<div class="alert-30blue success-30blue">✓ Acceso autorizado al sistema corporativo</div>', unsafe_allow_html=True)
                        time.sleep(1.2)
                        st.rerun()
                    else:
                        st.markdown('<div class="alert-30blue error-30blue">✗ Credenciales no válidas. Verifique sus datos.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-30blue warning-30blue">⚠️ Complete todos los campos requeridos</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="footer-30blue">© 2024 Tododrogas S.A.S • Sistema v3.0</div>', unsafe_allow_html=True)
    
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
