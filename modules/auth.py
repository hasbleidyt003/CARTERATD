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
    # CSS minimalista y elegante con glassmorphism azul purista
    st.markdown("""
    <style>
        /* Ocultar elementos de Streamlit */
        #MainMenu, footer, header {display: none !important;}
        .stApp {margin: 0; padding: 0; overflow: hidden;}

        /* Fondo azul purista con degradado sutil */
        .stApp {
            background: linear-gradient(135deg, #e0f2ff 0%, #c0e0ff 50%, #a0cfff 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* Brillo ambiental sutil */
        .stApp::before {
            content: '';
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at 30% 70%, rgba(255,255,255,0.4), transparent 50%),
                        radial-gradient(circle at 70% 30%, rgba(255,255,255,0.3), transparent 50%);
            pointer-events: none;
        }

        /* Tarjeta de vidrio */
        .glass-container {
            background: rgba(255, 255, 255, 0.22);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.4);
            box-shadow: 0 20px 40px rgba(0, 100, 200, 0.15);
            padding: 50px 60px;
            width: 100%;
            max-width: 440px;
            position: relative;
            overflow: hidden;
        }

        /* Borde luminoso sutil */
        .glass-container::before {
            content: '';
            position: absolute;
            inset: 0;
            border-radius: 24px;
            padding: 1.5px;
            background: linear-gradient(135deg, rgba(255,255,255,0.6), rgba(100,180,255,0.4), rgba(0,120,255,0.6));
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            pointer-events: none;
        }

        /* Título principal */
        .title {
            font-size: 3.2rem;
            font-weight: 900;
            background: linear-gradient(135deg, #0044aa, #0077ff, #00aaff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            margin-bottom: 8px;
            letter-spacing: -1px;
        }

        .subtitle {
            text-align: center;
            color: rgba(0, 50, 100, 0.9);
            font-size: 1.15rem;
            font-weight: 500;
            margin-bottom: 40px;
            letter-spacing: 0.3px;
        }

        /* Inputs personalizados */
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.9) !important;
            border: 2px solid rgba(255, 255, 255, 0.7) !important;
            border-radius: 16px !important;
            padding: 16px 20px !important;
            font-size: 1.05rem !important;
            color: #002244 !important;
            box-shadow: 0 4px 15px rgba(0, 100, 200, 0.1);
        }

        .stTextInput > div > div > input:focus {
            border-color: #0099ff !important;
            box-shadow: 0 0 0 4px rgba(0, 153, 255, 0.2), 0 4px 15px rgba(0, 100, 200, 0.15) !important;
            background: rgba(255, 255, 255, 0.98) !important;
        }

        /* Botón principal */
        .stButton > button {
            background: linear-gradient(135deg, #0066ff, #0088ff, #00bbff) !important;
            color: white !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 18px !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            width: 100% !important;
            margin-top: 20px;
            box-shadow: 0 10px 25px rgba(0, 102, 255, 0.3);
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 35px rgba(0, 102, 255, 0.4);
        }

        /* Mensajes */
        .alert {
            padding: 16px 20px;
            border-radius: 12px;
            text-align: center;
            font-weight: 600;
            margin: 20px 0;
            backdrop-filter: blur(10px);
        }
        .success {background: rgba(0, 220, 120, 0.25); border: 1px solid rgba(0, 220, 120, 0.5); color: #004422;}
        .error {background: rgba(255, 100, 100, 0.25); border: 1px solid rgba(255, 0, 0, 0.5); color: #440000;}
        .warning {background: rgba(255, 200, 80, 0.25); border: 1px solid rgba(255, 150, 0, 0.5); color: #443300;}

        .footer {
            text-align: center;
            margin-top: 40px;
            color: rgba(0, 50, 100, 0.8);
            font-size: 0.95rem;
            font-weight: 500;
        }
    </style>
    """, unsafe_allow_html=True)

    # Tarjeta principal
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)

    # Header
    st.markdown('<h1 class="title">TODODROGAS</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Sistema Corporativo de Gestión</p>', unsafe_allow_html=True)

    # Formulario
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            label="Usuario",
            placeholder="Ingrese su usuario",
            label_visibility="collapsed"
        )
        password = st.text_input(
            label="Contraseña",
            type="password",
            placeholder="Ingrese su contraseña",
            label_visibility="collapsed"
        )
        submit = st.form_submit_button("ACCEDER AL SISTEMA")

        if submit:
            if username and password:
                with st.spinner("Validando credenciales..."):
                    time.sleep(0.8)
                    success, user = authenticate(username, password)
                if success:
                    st.session_state.user = user
                    st.session_state.authenticated = True
                    st.markdown('<div class="alert success">✓ Acceso autorizado. Bienvenido.</div>', unsafe_allow_html=True)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.markdown('<div class="alert error">✗ Credenciales incorrectas</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert warning">⚠️ Complete todos los campos</div>', unsafe_allow_html=True)

    # Footer
    st.markdown('<div class="footer">© 2025 Tododrogas S.A.S • Versión 3.0</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Funciones de autenticación (sin cambios)
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
