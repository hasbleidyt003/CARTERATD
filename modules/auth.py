def show_login_screen():
    """Muestra la pantalla de login futurista estilo glass"""
    
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
        
        .login-wrapper {
            min-height: 100vh;
            background: linear-gradient(135deg, #FFFFFF 0%, #F7FAFC 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            position: relative;
            overflow: hidden;
        }
        
        .login-wrapper::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, #4D94FF, transparent);
        }
        
        .glass-login {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(30px) saturate(200%);
            -webkit-backdrop-filter: blur(30px) saturate(200%);
            border-radius: 32px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.1),
                       inset 0 1px 0 rgba(255, 255, 255, 0.5),
                       0 0 0 1px rgba(255, 255, 255, 0.1);
            padding: 3rem;
            width: 100%;
            max-width: 420px;
            position: relative;
            overflow: hidden;
        }
        
        .glass-login::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(
                circle,
                rgba(0, 102, 255, 0.15) 0%,
                transparent 70%
            );
            z-index: -1;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 2.5rem;
        }
        
        .login-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            display: block;
            background: linear-gradient(135deg, #0066FF, #00D4FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .login-title {
            font-size: 2rem;
            font-weight: 800;
            color: #1A1A1A;
            margin-bottom: 0.5rem;
            letter-spacing: -0.5px;
        }
        
        .login-subtitle {
            color: #4A5568;
            font-size: 1rem;
            font-weight: 400;
        }
        
        .login-form {
            margin-top: 2rem;
        }
        
        .input-group {
            margin-bottom: 1.5rem;
        }
        
        .input-label {
            display: block;
            color: #4A5568;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            margin-left: 0.5rem;
        }
        
        .glass-input-field {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 16px;
            padding: 16px 20px;
            width: 100%;
            font-size: 1rem;
            color: #1A1A1A;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05),
                       inset 0 1px 0 rgba(255, 255, 255, 0.6);
        }
        
        .glass-input-field:focus {
            outline: none;
            border-color: #4D94FF;
            box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.1),
                       0 4px 20px rgba(0, 102, 255, 0.15),
                       inset 0 1px 0 rgba(255, 255, 255, 0.8);
            background: white;
        }
        
        .glass-button-login {
            background: linear-gradient(135deg, rgba(0, 102, 255, 0.9), rgba(77, 148, 255, 0.9));
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.4);
            border-radius: 16px;
            color: white;
            padding: 16px 32px;
            font-size: 1rem;
            font-weight: 600;
            width: 100%;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px rgba(0, 102, 255, 0.2),
                       inset 0 1px 0 rgba(255, 255, 255, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .glass-button-login:hover {
            background: linear-gradient(135deg, rgba(0, 102, 255, 1), rgba(77, 148, 255, 1));
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0, 102, 255, 0.3),
                       inset 0 1px 0 rgba(255, 255, 255, 0.4);
        }
        
        .glass-button-login::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.6s ease;
        }
        
        .glass-button-login:hover::after {
            left: 100%;
        }
        
        .login-footer {
            text-align: center;
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid rgba(0, 0, 0, 0.05);
            color: #718096;
            font-size: 0.85rem;
        }
        
        .credential-hint {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 1rem;
            margin-top: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .pulse-animation {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Contenedor principal del login
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="glass-login">', unsafe_allow_html=True)
    
    # Header del login
    st.markdown('<div class="login-header">', unsafe_allow_html=True)
    st.markdown('<div class="login-icon">💊</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="login-title">TODODROGAS</h1>', unsafe_allow_html=True)
    st.markdown('<p class="login-subtitle">Sistema de Gestión de Cupos</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Formulario de login
    with st.form("login_form"):
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        
        # Campo usuario
        st.markdown('<div class="input-group">', unsafe_allow_html=True)
        st.markdown('<label class="input-label">👤 Usuario</label>', unsafe_allow_html=True)
        username = st.text_input("", placeholder="Ingresa tu usuario", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Campo contraseña
        st.markdown('<div class="input-group">', unsafe_allow_html=True)
        st.markdown('<label class="input-label">🔒 Contraseña</label>', unsafe_allow_html=True)
        password = st.text_input("", type="password", placeholder="Ingresa tu contraseña", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Opciones adicionales
        col1, col2 = st.columns([1, 1])
        with col1:
            remember = st.checkbox("Recordarme", value=True)
        
        # Botón de login
        if st.form_submit_button("🚀 INGRESAR AL SISTEMA", use_container_width=True):
            if username and password:
                with st.spinner("Verificando credenciales..."):
                    time.sleep(1)
                    authenticated, user = authenticate(username, password)
                    
                    if authenticated:
                        st.session_state.user = user
                        st.session_state.authenticated = True
                        st.success(f"¡Bienvenido, {user['nombre']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
            else:
                st.warning("⚠️ Por favor completa todos los campos")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Información de credenciales de prueba
    with st.expander("🔑 Credenciales de Prueba", expanded=False):
        st.markdown("""
        <div class="credential-hint">
        **Usuario Administrador:**
        - 👑 Usuario: <code>admin</code>
        - 🔑 Contraseña: <code>admin123</code>
        
        **Usuario Normal:**
        - 👤 Usuario: <code>cartera</code>
        - 🔑 Contraseña: <code>cartera123</code>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="login-footer">', unsafe_allow_html=True)
    st.markdown('© 2024 Sistema de Gestión de Cupos • Versión 1.0')
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
