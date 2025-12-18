"""
AUTENTICACIÓN - DISEÑO COMPACTO Y CENTRADO
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
    """Login compacto y centrado con píldora al lado izquierdo"""
    
    # CSS compacto y centrado
    st.markdown("""
    <style>
        /* Reset Streamlit */
        .stApp {
            background: linear-gradient(135deg, #FFFFFF 0%, #F5F9FF 100%) !important;
            min-height: 100vh;
        }
        
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
        
        /* Contenedor principal centrado */
        .login-container-compact {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1rem;
            background: linear-gradient(135deg, 
                #FFFFFF 0%, 
                #F5F9FF 30%, 
                #EDF4FF 70%, 
                #FFFFFF 100%);
            position: relative;
        }
        
        /* Fondo con líneas azules sutiles */
        .login-container-compact::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                linear-gradient(90deg, transparent 98%, rgba(0, 102, 255, 0.05) 100%),
                linear-gradient(180deg, transparent 98%, rgba(0, 102, 255, 0.05) 100%);
            background-size: 40px 40px;
            opacity: 0.3;
            pointer-events: none;
        }
        
        /* Panel glass compacto */
        .glass-panel-compact {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.4);
            box-shadow: 
                0 20px 50px rgba(0, 0, 0, 0.08),
                0 0 30px rgba(0, 102, 255, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.8);
            padding: 2.5rem;
            width: 100%;
            max-width: 450px;
            position: relative;
        }
        
        /* Borde azul sutil */
        .glass-panel-compact::after {
            content: '';
            position: absolute;
            top: -1px;
            left: -1px;
            right: -1px;
            bottom: -1px;
            border-radius: 25px;
            background: linear-gradient(135deg, 
                rgba(0, 102, 255, 0.2), 
                rgba(0, 212, 255, 0.2));
            z-index: -1;
            opacity: 0.5;
        }
        
        /* Header con píldora al lado izquierdo */
        .login-header-compact {
            display: flex;
            align-items: center;
            gap: 1.2rem;
            margin-bottom: 2.5rem;
            justify-content: center;
        }
        
        /* Píldora grande al lado izquierdo */
        .pill-left {
            font-size: 3rem;
            width: 80px;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #0066FF 0%, #00D4FF 100%);
            color: white;
            border-radius: 20px;
            box-shadow: 
                0 10px 30px rgba(0, 102, 255, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.4);
            flex-shrink: 0;
        }
        
        /* Título al lado derecho de la píldora */
        .title-compact {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #1A1A1A 0%, #0066FF 50%, #00D4FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -1px;
            line-height: 1;
        }
        
        .subtitle-compact {
            color: #4A5568;
            font-size: 1rem;
            font-weight: 400;
            margin-top: 0.3rem;
        }
        
        /* Formulario compacto */
        .form-compact {
            margin-top: 1.5rem;
        }
        
        /* Campos de entrada glass azul */
        .input-glass-azul {
            background: rgba(0, 102, 255, 0.08) !important;
            backdrop-filter: blur(10px) !important;
            border: 2px solid rgba(0, 102, 255, 0.15) !important;
            border-radius: 14px !important;
            padding: 16px 20px 16px 50px !important;
            width: 100% !important;
            font-size: 1rem !important;
            color: white !important;
            transition: all 0.3s ease !important;
            box-shadow: 
                inset 0 2px 6px rgba(0, 102, 255, 0.15),
                0 4px 15px rgba(0, 102, 255, 0.1) !important;
            font-weight: 500 !important;
            margin-bottom: 1.2rem !important;
        }
        
        .input-glass-azul:focus {
            outline: none !important;
            background: rgba(0, 102, 255, 0.12) !important;
            border-color: rgba(0, 102, 255, 0.3) !important;
            box-shadow: 
                inset 0 2px 8px rgba(0, 102, 255, 0.2),
                0 6px 20px rgba(0, 102, 255, 0.15) !important;
            transform: translateY(-1px);
        }
        
        .input-glass-azul::placeholder {
            color: rgba(255, 255, 255, 0.7) !important;
        }
        
        /* Iconos dentro de inputs */
        .input-wrapper {
            position: relative;
            width: 100%;
        }
        
        .input-icon-azul {
            position: absolute;
            left: 18px;
            top: 50%;
            transform: translateY(-50%);
            color: white;
            font-size: 1.1rem;
            z-index: 2;
            opacity: 0.8;
        }
        
        /* Botón compacto */
        .btn-compact {
            background: linear-gradient(135deg, 
                rgba(0, 102, 255, 0.9) 0%,
                rgba(0, 212, 255, 0.9) 100%) !important;
            border: none !important;
            border-radius: 14px !important;
            color: white !important;
            padding: 16px !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            width: 100% !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            position: relative !important;
            overflow: hidden !important;
            box-shadow: 
                0 8px 25px rgba(0, 102, 255, 0.25),
                inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
            margin-top: 0.5rem !important;
            letter-spacing: 0.5px !important;
        }
        
        .btn-compact:hover {
            background: linear-gradient(135deg, 
                rgba(0, 102, 255, 1) 0%,
                rgba(0, 212, 255, 1) 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 
                0 12px 35px rgba(0, 102, 255, 0.35),
                inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        }
        
        /* Efecto de destello */
        .btn-compact::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255, 255, 255, 0.2),
                transparent
            );
            transition: left 0.5s ease;
        }
        
        .btn-compact:hover::before {
            left: 100%;
        }
        
        /* Checkbox minimal */
        .checkbox-compact {
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 1.2rem 0;
            color: #4A5568;
            font-size: 0.9rem;
        }
        
        /* Footer compacto */
        .footer-compact {
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid rgba(0, 0, 0, 0.05);
            text-align: center;
            color: #718096;
            font-size: 0.85rem;
        }
        
        /* Mensajes compactos */
        .alert-compact {
            background: rgba(0, 102, 255, 0.08);
            border: 1px solid rgba(0, 102, 255, 0.15);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
            backdrop-filter: blur(10px);
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .glass-panel-compact {
                padding: 2rem 1.5rem;
                margin: 0.5rem;
            }
            
            .login-header-compact {
                flex-direction: column;
                text-align: center;
                gap: 1rem;
            }
            
            .pill-left {
                width: 70px;
                height: 70px;
                font-size: 2.5rem;
            }
            
            .title-compact {
                font-size: 2rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Contenedor principal centrado
    st.markdown('<div class="login-container-compact">', unsafe_allow_html=True)
    st.markdown('<div class="glass-panel-compact">', unsafe_allow_html=True)
    
    # Header con píldora al lado izquierdo y título al lado derecho
    st.markdown('<div class="login-header-compact">', unsafe_allow_html=True)
    
    # Píldora al lado izquierdo
    st.markdown('<div class="pill-left">💊</div>', unsafe_allow_html=True)
    
    # Título al lado derecho de la píldora
    st.markdown('''
    <div>
        <div class="title-compact">TODODROGAS</div>
        <div class="subtitle-compact">Sistema de Gestión de Cupos</div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Formulario compacto
    with st.form("login_form", clear_on_submit=False):
        st.markdown('<div class="form-compact">', unsafe_allow_html=True)
        
        # Campo de usuario
        st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="input-icon-azul">👤</div>', unsafe_allow_html=True)
        
        username = st.text_input(
            "",
            placeholder="Usuario",
            label_visibility="collapsed",
            key="username_input"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Campo de contraseña
        st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="input-icon-azul">🔒</div>', unsafe_allow_html=True)
        
        password = st.text_input(
            "",
            type="password",
            placeholder="Contraseña",
            label_visibility="collapsed",
            key="password_input"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Checkbox recordar sesión
        col1, col2 = st.columns([1, 8])
        with col1:
            remember = st.checkbox("", value=True, key="remember_checkbox")
        with col2:
            st.markdown('<div class="checkbox-compact">Recordar mi sesión</div>', unsafe_allow_html=True)
        
        # Botón de acceso
        submit_button = st.form_submit_button(
            "ACCEDER",
            use_container_width=True,
            type="primary"
        )
        
        if submit_button:
            if username and password:
                # Barra de progreso simple
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                # Validación
                authenticated, user = authenticate(username, password)
                
                # Limpiar barra
                progress_bar.empty()
                
                if authenticated:
                    # Mensaje de éxito
                    st.markdown(f'''
                    <div class="alert-compact">
                        <div style="color: #0066FF; font-weight: 600;">
                            ✓ Acceso concedido
                        </div>
                        <div style="color: #1A1A1A; margin-top: 0.5rem;">
                            Redirigiendo...
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Guardar sesión
                    st.session_state.user = user
                    st.session_state.authenticated = True
                    
                    # Redirección rápida
                    time.sleep(1)
                    st.rerun()
                else:
                    # Mensaje de error
                    st.markdown('''
                    <div class="alert-compact" style="border-color: rgba(255, 107, 107, 0.3); background: rgba(255, 107, 107, 0.08);">
                        <div style="color: #FF6B6B; font-weight: 600;">
                            ✗ Credenciales incorrectas
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
            else:
                # Mensaje de advertencia
                st.markdown('''
                <div class="alert-compact" style="border-color: rgba(255, 149, 0, 0.3); background: rgba(255, 149, 0, 0.08);">
                    <div style="color: #FF9500; font-weight: 600;">
                        ⚠ Completa todos los campos
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="footer-compact">', unsafe_allow_html=True)
    
    # Información simple
    with st.expander("ℹ️ Información", expanded=False):
        st.markdown(f'''
        **Sistema:** Tododrogas v2.0  
        **Estado:** Operativo  
        **Fecha:** {datetime.now().strftime("%d/%m/%Y")}
        ''')
    
    st.markdown('<div style="margin-top: 1rem;">© 2024 Tododrogas</div>', unsafe_allow_html=True)
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
