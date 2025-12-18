import streamlit as st
import hashlib
import time
from datetime import datetime
import sqlite3

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username: str, password: str):
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT id, username, nombre, rol, password_hash FROM usuarios WHERE username = ?',
            (username,)
        )
        user_data = cursor.fetchone()
        if not user_data or hash_password(password) != user_data[4]:
            return False, None
        user_id = user_data[0]
        cursor.execute('UPDATE usuarios SET ultimo_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
        conn.commit()
        user = {
            'id': user_id,
            'username': user_data[1],
            'nombre': user_data[2],
            'rol': user_data[3],
            'authenticated': True,
            'login_time': datetime.now()
        }
        return True, user
    except Exception as e:
        print(f"Error autenticación: {e}")
        return False, None
    finally:
        conn.close()

def show_login_screen():
    st.markdown("""
    <style>
        /* Ocultar elementos de Streamlit */
        #MainMenu, footer, header {display: none !important;}
        .stApp {margin: 0; padding: 0; overflow: hidden;}
        
        /* Fondo blanco futurista con toque azul muy suave */
        .stApp {
            background: linear-gradient(135deg, #f8fbff 0%, #eef5ff 50%, #e5f0ff 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        
        /* Tarjeta principal - glass muy blanco y futurista */
        .glass-container {
            background: rgba(255, 255, 255, 0.65);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border-radius: 28px;
            border: 1px solid rgba(200, 230, 255, 0.6);
            box-shadow: 0 20px 50px rgba(100, 160, 255, 0.12),
                        inset 0 1px 0 rgba(255, 255, 255, 0.8);
            padding: 60px 70px;
            width: 100%;
            max-width: 460px;
            position: relative;
            z-index: 10;
            margin: 20px;
        }
        
        /* Título futurista */
        .title {
            font-size: 3.4rem;
            font-weight: 900;
            color: #0055cc;
            text-align: center;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
            text-shadow: 0 2px 8px rgba(0, 100, 255, 0.1);
        }
        
        .subtitle {
            text-align: center;
            color: #446688;
            font-size: 1.15rem;
            font-weight: 500;
            margin-bottom: 50px;
        }
        
        /* Inputs - más blancos y suaves */
        .stTextInput > div > div {
            margin-bottom: 25px;
        }
        
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.95) !important;
            border: 1px solid rgba(180, 210, 255, 0.6) !important;
            border-radius: 18px !important;
            padding: 18px 22px !important;
            font-size: 1.05rem !important;
            color: #223344 !important;
            box-shadow: 0 4px 20px rgba(100, 160, 255, 0.08);
            width: 100% !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #66aaff !important;
            box-shadow: 0 0 0 4px rgba(100, 180, 255, 0.2), 0 8px 25px rgba(100, 160, 255, 0.15) !important;
            background: #ffffff !important;
            outline: none !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: #8899aa !important;
        }
        
        /* Botón futurista con glow */
        .stButton > button {
            background: linear-gradient(135deg, #4488ff, #66aaff, #88bbff) !important;
            color: white !important;
            border: none !important;
            border-radius: 18px !important;
            padding: 18px !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            width: 100% !important;
            margin-top: 10px;
            box-shadow: 0 10px 30px rgba(100, 160, 255, 0.3),
                        inset 0 1px 0 rgba(255, 255, 255, 0.4);
            transition: all 0.4s ease;
            cursor: pointer;
        }
        
        .stButton > button:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 40px rgba(100, 160, 255, 0.4);
        }
        
        /* Mensajes */
        .alert {
            padding: 16px 20px;
            border-radius: 14px;
            text-align: center;
            font-weight: 600;
            margin: 20px 0;
            backdrop-filter: blur(10px);
        }
        
        .success {
            background: rgba(100, 255, 180, 0.2); 
            border: 1px solid rgba(0, 220, 140, 0.5); 
            color: #004433;
        }
        
        .error {
            background: rgba(255, 140, 140, 0.2); 
            border: 1px solid rgba(255, 80, 80, 0.5); 
            color: #440000;
        }
        
        .warning {
            background: rgba(255, 220, 140, 0.2); 
            border: 1px solid rgba(255, 180, 80, 0.5); 
            color: #443300;
        }
        
        .footer {
            text-align: center;
            margin-top: 50px;
            color: #557799;
            font-size: 0.95rem;
            font-weight: 500;
        }
        

        }
        
        .glass-container {
            animation: float 6s ease-in-out infinite;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Tarjeta principal
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="title">TODODROGAS</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Sistema Corporativo de Gestión de Cupos</p>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        # Usuario - usando espacios para evitar labels automáticos
        username = st.text_input(" ", placeholder="Ingrese su usuario", label_visibility="collapsed")
        
        # Contraseña - usando espacios para evitar labels automáticos
        password = st.text_input("  ", type="password", placeholder="Ingrese su contraseña", label_visibility="collapsed")
        
        submit = st.form_submit_button("ACCEDER AL SISTEMA")
        
        if submit:
            if username and password:
                with st.spinner("Validando..."):
                    time.sleep(0.8)
                    success, user = authenticate(username, password)
                if success:
                    st.session_state.user = user
                    st.session_state.authenticated = True
                    st.markdown('<div class="alert success">✓ Acceso autorizado</div>', unsafe_allow_html=True)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.markdown('<div class="alert error">✗ Credenciales incorrectas</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert warning">⚠️ Complete todos los campos</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def check_authentication():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        show_login_screen()
        st.stop()
    return st.session_state.get('user', {})

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def require_admin():
    user = check_authentication()
    if user.get('rol') != 'admin':
        st.error("⛔ Acceso restringido a administradores")
        st.stop()
    return user
