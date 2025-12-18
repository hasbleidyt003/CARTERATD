"""
AUTENTICACIÓN - ESTILO MINIMALISTA GLASS AZUL
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
    """Login minimalista glass azul con píldora grande"""
    
    # CSS inline para el login minimalista
    st.markdown("""
    <style>
        /* Ocultar elementos de Streamlit */
        .stApp > header {
            display: none !important;
        }
        
        #MainMenu, footer, header {
            visibility: hidden !important;
        }
        
        .block-container {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            max-width: 100% !important;
        }
        
        /* Contenedor principal */
        .login-minimalista {
            min-height: 100vh;
            background: linear-gradient(135deg, 
                #FFFFFF 0%, 
                #F5F9FF 25%, 
                #EDF4FF 50%, 
                #F5F9FF 75%, 
                #FFFFFF 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            position: relative;
            overflow: hidden;
        }
        
        /* Efecto de visos azules en fondo */
        .login-minimalista::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                linear-gradient(45deg, transparent 48%, rgba(0, 102, 255, 0.03) 50%, transparent 52%),
                linear-gradient(-45deg, transparent 48%, rgba(0, 212, 255, 0.02) 50%, transparent 52%);
            background-size: 60px 60px;
            opacity: 0.4;
            animation: subtle-move 20s infinite linear;
        }
        
        @keyframes subtle-move {
            0% { background-position: 0 0; }
            100% { background-position: 60px 60px; }
        }
        
        /* Contenedor glass */
        .login-glass-minimal {
            background: rgba(255, 255, 255, 0.92);
            backdrop-filter: blur(30px) saturate(180%);
            -webkit-backdrop-filter: blur(30px) saturate(180%);
            border-radius: 28px;
            border: 1px solid rgba(255, 255, 255, 0.4);
            box-shadow: 
                0 25px 60px rgba(0, 0, 0, 0.08),
                0 0 40px rgba(0, 102, 255, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.7);
            padding: 4rem;
            width: 100%;
            max-width: 500px;
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        /* Encabezado con píldora y título al lado */
        .login-header-minimal {
            display: flex;
            align-items: center;
            gap: 1.5rem;
            margin-bottom: 3rem;
            width: 100%;
            justify-content: flex-start;
        }
        
        /* Píldora grande igual que el título */
        .pill-large {
            font-size: 3.5rem;
            width: 100px;
            height: 100px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #0066FF 0%, #00D4FF 100%);
            color: white;
            border-radius: 24px;
            box-shadow: 
                0 15px 35px rgba(0, 102, 255, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.4);
            animation: pill-float 3s ease-in-out infinite;
        }
        
        @keyframes pill-float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        /* Título al lado de la píldora */
        .title-minimal {
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #1A1A1A 0%, #0066FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -1.5px;
            line-height: 1;
        }
        
        .subtitle-minimal {
            color: #4A5568;
            font-size: 1.1rem;
            font-weight: 400;
            margin-top: 0.5rem;
            letter-spacing: 0.5px;
        }
        
        /* Campos de entrada minimalistas glass azules */
        .input-group-minimal {
            width: 100%;
            margin-bottom: 1.8rem;
            position: relative;
        }
        
        .glass-input-minimal {
            background: rgba(0, 102, 255, 0.1) !important;
            backdrop-filter: blur(15px) !important;
            border: 2px solid rgba(0, 102, 255, 0.2) !important;
            border-radius: 16px !important;
            padding: 18px 22px !important;
            width: 100% !important;
            font-size: 1.1rem !important;
            color: white !important;
            transition: all 0.3s ease !important;
            box-shadow: 
                inset 0 2px 8px rgba(0, 102, 255, 0.2),
                0 4px 20px rgba(0, 102, 255, 0.15) !important;
            font-weight: 500 !important;
        }
        
        .glass-input-minimal:focus {
            outline: none !important;
            background: rgba(0, 102, 255, 0.2) !important;
            border-color: rgba(0, 102, 255, 0.4) !important;
            box-shadow: 
                inset 0 2px 12px rgba(0, 102, 255, 0.3),
                0 6px 30px rgba(0, 102, 255, 0.25),
                0 0 0 3px rgba(0, 102, 255, 0.1) !important;
            transform: translateY(-2px);
        }
        
        .glass-input-minimal::placeholder {
            color: rgba(255, 255, 255, 0.7) !important;
        }
        
        /* Iconos dentro de los inputs */
        .input-with-icon {
            position: relative;
        }
        
        .input-icon {
            position: absolute;
            left: 18px;
            top: 50%;
            transform: translateY(-50%);
            color: white;
            font-size: 1.2rem;
            z-index: 2;
            opacity: 0.8;
        }
        
        .glass-input-minimal {
            padding-left: 55px !important;
        }
        
        /* Botón glass azul */
        .glass-button-minimal {
            background: linear-gradient(135deg, 
                rgba(0, 102, 255, 0.9) 0%,
                rgba(0, 212, 255, 0.9) 100%) !important;
            backdrop-filter: blur(15px) !important;
            border: 2px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 18px !important;
            color: white !important;
            padding: 20px 40px !important;
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            width: 100% !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            position: relative !important;
            overflow: hidden !important;
            box-shadow: 
                0 10px 40px rgba(0, 102, 255, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.3),
                0 0 30px rgba(0, 102, 255, 0.2) !important;
            margin-top: 1rem !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
        }
        
        .glass-button-minimal:hover {
            background: linear-gradient(135deg, 
                rgba(0, 102, 255, 1) 0%,
                rgba(0, 212, 255, 1) 100%) !important;
            transform: translateY(-3px) !important;
            box-shadow: 
                0 15px 50px rgba(0, 102, 255, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.4),
                0 0 40px rgba(0, 102, 255, 0.3) !important;
            border-color: rgba(255, 255, 255, 0.4) !important;
        }
        
        /* Efecto de destello */
        .glass-button-minimal::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255, 255, 255, 0.3),
                transparent
            );
            transition: left 0.6s ease;
        }
        
        .glass-button-minimal:hover::before {
            left: 100%;
        }
        
        /* Checkbox minimalista */
        .checkbox-minimal {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 1.5rem 0;
            width: 100%;
        }
        
        /* Footer */
        .login-footer-minimal {
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid rgba(0, 0, 0, 0.05);
            text-align: center;
            width: 100%;
        }
        
        .footer-text-minimal {
            color: #4A5568;
            font-size: 0.9rem;
            opacity: 0.7;
        }
        
        /* Mensajes de estado */
        .status-message {
            background: rgba(0, 102, 255, 0.1);
            border: 1px solid rgba(0, 102, 255, 0.2);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            backdrop-filter: blur(10px);
            text-align: center;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .login-glass-minimal {
                padding: 3rem 2rem;
                margin: 1rem;
            }
            
            .login-header-minimal {
                flex-direction: column;
                text-align: center;
                gap: 1rem;
            }
            
            .pill-large {
                width: 80px;
                height: 80px;
                font-size: 2.8rem;
            }
            
            .title-minimal {
                font-size: 2.8rem;
            }
            
            .glass-button-minimal {
                padding: 18px 30px;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Contenedor principal
    st.markdown('<div class="login-minimalista">', unsafe_allow_html=True)
    st.markdown('<div class="login-glass-minimal">', unsafe_allow_html=True)
    
    # Encabezado con píldora grande y título al lado
    st.markdown('<div class="login-header-minimal">', unsafe_allow_html=True)
    
    # Píldora grande
    st.markdown('<div class="pill-large">💊</div>', unsafe_allow_html=True)
    
    # Título al lado
    col_title = st.columns([1])
    with col_title[0]:
        st.markdown('<h1 class="title-minimal">TODODROGAS</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle-minimal">Sistema de Gestión de Cupos</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Formulario de login
    with st.form("login_form", clear_on_submit=False):
        # Campo de usuario con icono
        st.markdown('<div class="input-group-minimal input-with-icon">', unsafe_allow_html=True)
        st.markdown('<div class="input-icon">👤</div>', unsafe_allow_html=True)
        
        username = st.text_input(
            "",
            placeholder="Usuario",
            label_visibility="collapsed",
            key="username_input"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Campo de contraseña con icono
        st.markdown('<div class="input-group-minimal input-with-icon">', unsafe_allow_html=True)
        st.markdown('<div class="input-icon">🔒</div>', unsafe_allow_html=True)
        
        password = st.text_input(
            "",
            type="password",
            placeholder="Contraseña",
            label_visibility="collapsed",
            key="password_input"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Opción recordar sesión
        st.markdown('<div class="checkbox-minimal">', unsafe_allow_html=True)
        col_check = st.columns([1, 5])
        with col_check[0]:
            remember = st.checkbox("", value=True, key="remember_checkbox")
        with col_check[1]:
            st.markdown('<label style="color: #4A5568; font-weight: 500;">Recordar mi sesión</label>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botón de acceso
        submit_button = st.form_submit_button(
            "ACCEDER AL SISTEMA",
            use_container_width=True,
            type="primary"
        )
        
        if submit_button:
            if username and password:
                # Efecto de carga
                with st.spinner(""):
                    # Barra de progreso animada
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.015)
                        progress_bar.progress(i + 1)
                    
                    # Validación
                    authenticated, user = authenticate(username, password)
                    
                    # Limpiar barra
                    progress_bar.empty()
                    
                    if authenticated:
                        # Mensaje de éxito
                        st.markdown(f'''
                        <div class="status-message">
                            <div style="color: #0066FF; font-weight: 600; font-size: 1.2rem;">
                                ✓ Acceso concedido
                            </div>
                            <div style="color: #1A1A1A; margin-top: 0.8rem;">
                                ¡Bienvenido, {user['nombre']}!
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        # Guardar sesión
                        st.session_state.user = user
                        st.session_state.authenticated = True
                        
                        # Retardo antes de redirección
                        time.sleep(1.2)
                        st.rerun()
                    else:
                        # Mensaje de error
                        st.markdown('''
                        <div class="status-message">
                            <div style="color: #FF6B6B; font-weight: 600; font-size: 1.2rem;">
                                ✗ Credenciales incorrectas
                            </div>
                            <div style="color: #1A1A1A; margin-top: 0.8rem;">
                                Verifica tus datos e intenta nuevamente
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
            else:
                # Mensaje de advertencia
                st.markdown('''
                <div class="status-message">
                    <div style="color: #FF9500; font-weight: 600; font-size: 1.2rem;">
                        ⚠ Campos requeridos
                    </div>
                    <div style="color: #1A1A1A; margin-top: 0.8rem;">
                        Completa todos los campos para continuar
                    </div>
                </div>
                ''', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="login-footer-minimal">', unsafe_allow_html=True)
    
    # Información del sistema
    with st.expander("ℹ️ Información del sistema", expanded=False):
        st.markdown(f'''
        <div style="color: #4A5568; font-size: 0.95rem; line-height: 1.6;">
            <div style="margin-bottom: 0.8rem;">
                <strong>Sistema:</strong> Tododrogas Gestión de Cupos v2.0
            </div>
            <div style="margin-bottom: 0.8rem;">
                <strong>Estado:</strong> <span style="color: #0066FF; font-weight: 600;">Operativo</span>
            </div>
            <div style="margin-bottom: 0.8rem;">
                <strong>Último acceso:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M")}
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Copyright
    st.markdown('<p class="footer-text-minimal">© 2024 Tododrogas • Sistema de gestión empresarial</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
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
    # Limpiar sesión
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    st.rerun()

def require_admin():
    """Requiere rol admin"""
    user = check_authentication()
    
    if user.get('rol') != 'admin':
        st.error("⛔ Acceso solo para administradores")
        st.stop()
    
    return user
