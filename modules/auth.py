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
        /* Ocultar elementos Streamlit */
        #MainMenu, footer, header {display: none !important;}
        .stApp {margin: 0; padding: 0; overflow: hidden;}

        /* Fondo blanco futurista ultra suave */
        .stApp {
            background: linear-gradient(135deg, #fafcff 0%, #f0f7ff 50%, #e8f2ff 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }

        /* Píldora flotante futurista (badge decorativo) */
        .pill-badge {
            position: absolute;
            top: 90px;
            left: 50%;
            transform: translateX(-50%);
            width: 320px;
            height: 100px;
            background: rgba(255, 255, 255, 0.75);
            backdrop-filter: blur(30px);
            -webkit-backdrop-filter: blur(30px);
            border-radius: 60px;
            border: 1px solid rgba(180, 230, 255, 0.7);
            box-shadow: 
                0 15px 40px rgba(100, 180, 255, 0.15),
                inset 0 2px 10px rgba(255, 255, 255, 0.8),
                0 0 30px rgba(100, 220, 255, 0.2);
            animation: float 7s ease-in-out infinite, glow 4s ease-in-out infinite alternate;
            z-index: 5;
        }

        @keyframes float {
            0%, 100% { transform: translateX(-50%) translateY(0px) rotate(0deg); }
            50% { transform: translateX(-50%) translateY(-20px) rotate(1deg); }
        }

        @keyframes glow {
            0% { box-shadow: 0 15px 40px rgba(100, 180, 255, 0.15), inset 0 2px 10px rgba(255, 255, 255, 0.8), 0 0 30px rgba(100, 220, 255, 0.2); }
            100% { box-shadow: 0 20px 50px rgba(100, 180, 255, 0.25), inset 0 2px 10px rgba(255, 255, 255, 0.9), 0 0 50px rgba(100, 220, 255, 0.4); }
        }

        /* Tarjeta principal glass ultra blanca */
        .glass-container {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(28px);
            -webkit-backdrop-filter: blur(28px);
            border-radius: 32px;
            border: 1px solid rgba(200, 235, 255, 0.6);
            box-shadow: 0 25px 60px rgba(100, 170, 255, 0.15),
                        inset 0 1px 0 rgba(255, 255, 255, 0.9);
            padding: 70px 80px;
            width: 100%;
            max-width: 480px;
            position: relative;
            z-index: 10;
        }

        /* Título principal */
        .title {
            font-size: 3.6rem;
            font-weight: 900;
            color: #0044aa;
            text-align: center;
            margin-bottom: 10px;
            letter-spacing: -1px;
            text-shadow: 0 3px 10px rgba(0, 100, 255, 0.15);
        }

        .subtitle {
            text-align: center;
            color: #446699;
            font-size: 1.2rem;
            font-weight: 500;
            margin-bottom: 50px;
        }

        /* Inputs futuristas */
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.96) !important;
            border: 1px solid rgba(180, 220, 255, 0.7) !important;
            border-radius: 20px !important;
            padding: 20px 24px !important;
            font-size: 1.1rem !important;
            color: #112233 !important;
            box-shadow: 0 6px 25px rgba(100, 170, 255, 0.1);
            transition: all 0.4s ease;
        }

        .stTextInput > div > div > input:focus {
            border-color: #66bbff !important;
            box-shadow: 0 0 0 5px rgba(100, 200, 255, 0.25), 0 10px 30px rgba(100, 170, 255, 0.2) !important;
            background: #ffffff !important;
        }

        /* Botón con glow futurista */
        .stButton > button {
            background: linear-gradient(135deg, #5599ff, #77bbff, #99ddff) !important;
            color: white !important;
            border: none !important;
            border-radius: 20px !important;
            padding: 20px !important;
            font-size: 1.15rem !important;
            font-weight: 700 !important;
            width: 100% !important;
            margin-top: 35px;
            box-shadow: 0 12px 35px rgba(100, 170, 255, 0.35),
                        inset 0 1px 0 rgba(255, 255, 255, 0.5);
            transition: all 0.4s ease;
        }

        .stButton > button:hover {
            transform: translateY(-5px);
            box-shadow: 0 25px 50px rgba(100, 170, 255, 0.45);
        }

        /* Alertas y footer */
        .alert {padding: 18px 22px; border-radius: 16px; text-align: center; font-weight: 600; margin: 25px 0; backdrop-filter: blur(12px);}
        .success {background: rgba(120, 255, 200, 0.25); border: 1px solid rgba(50, 220, 150, 0.6); color: #004444;}
        .error {background: rgba(255, 150, 150, 0.25); border: 1px solid rgba(255, 80, 80, 0.6); color: #550000;}
        .warning {background: rgba(255, 230, 150, 0.25); border: 1px solid rgba(255, 180, 80, 0.6); color: #554400;}
        .footer {text-align: center; margin-top: 60px; color: #5588aa; font-size: 0.95rem; font-weight: 500;}
    </style>
    """, unsafe_allow_html=True)

    # Píldora flotante como badge futurista
    st.markdown('<div class="pill-badge"></div>', unsafe_allow_html=True)

    # Tarjeta principal
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)

    st.markdown('<h1 class="title">TODODROGAS</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Sistema Corporativo de Gestión de Cupos</p>', unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Usuario", placeholder="Ingrese su usuario", label_visibility="collapsed")
        password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña", label_visibility="collapsed")
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

    st.markdown('<div class="footer">© 2025 Tododrogas S.A.S • Versión 3.0</div>', unsafe_allow_html=True)
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
