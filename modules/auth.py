"""
Sistema de autenticación mejorado manteniendo estilo simple
"""
import streamlit as st
import hashlib
from datetime import datetime
import json
import os

# ==============================================
# CONFIGURACIÓN
# ==============================================

USERS_FILE = "data/users.json"

# Usuarios por defecto (se guardarán en archivo encriptado)
DEFAULT_USERS = {
    "cartera": {
        "password": "admin123",
        "role": "admin",
        "name": "Gestor de Cartera",
        "email": "cartera@empresa.com",
        "active": True,
        "created": datetime.now().strftime("%Y-%m-%d")
    },
    "supervisor": {
        "password": "view123", 
        "role": "viewer",
        "name": "Supervisor",
        "email": "supervisor@empresa.com",
        "active": True,
        "created": datetime.now().strftime("%Y-%m-%d")
    }
}

# ==============================================
# FUNCIONES DE SEGURIDAD
# ==============================================

def hash_password(password):
    """Encripta la contraseña usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_users():
    """Inicializa el archivo de usuarios con contraseñas encriptadas"""
    if not os.path.exists("data"):
        os.makedirs("data")
    
    if not os.path.exists(USERS_FILE):
        encrypted_users = {}
        for username, user_data in DEFAULT_USERS.items():
            encrypted_users[username] = {
                "hashed_password": hash_password(user_data["password"]),
                "role": user_data["role"],
                "name": user_data["name"],
                "email": user_data["email"],
                "active": user_data["active"],
                "created": user_data["created"],
                "last_login": None
            }
        
        with open(USERS_FILE, 'w') as f:
            json.dump(encrypted_users, f, indent=2)

def load_users():
    """Carga los usuarios desde el archivo"""
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        init_users()
        return load_users()

def save_users(users):
    """Guarda los usuarios en el archivo"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def authenticate_user(username, password):
    """Autentica un usuario"""
    users = load_users()
    
    if username not in users:
        return False, "❌ Usuario no encontrado"
    
    user = users[username]
    
    if not user.get("active", True):
        return False, "❌ Usuario inactivo"
    
    # Verificar contraseña encriptada
    if user["hashed_password"] != hash_password(password):
        return False, "❌ Contraseña incorrecta"
    
    # Actualizar último login
    user["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_users(users)
    
    return True, "✅ Inicio de sesión exitoso"

def get_user_role(username):
    """Obtiene el rol del usuario"""
    users = load_users()
    return users.get(username, {}).get("role", "viewer")

# ==============================================
# INTERFAZ DE LOGIN (Mismo Estilo Mejorado)
# ==============================================

def authenticate():
    """Muestra formulario de login con mejoras"""
    
    # Estilo mejorado manteniendo simplicidad
    st.markdown("""
    <style>
    /* Estilo para el login */
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    
    .login-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-header h1 {
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .login-header h3 {
        color: #666;
        font-weight: 400;
        margin-top: 0;
    }
    
    /* Estilo para inputs */
    .stTextInput > div > div > input {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 0.75rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #764ba2;
        box-shadow: 0 0 0 2px rgba(118, 75, 162, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Contenedor principal centrado
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Contenedor del login
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Encabezado
        st.markdown("""
        <div class="login-header">
            <h1>💊 Control de Cupos</h1>
            <h3>Sistema de Seguimiento - Medicamentos</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Formulario de login
        with st.form("login_form", clear_on_submit=False):
            col_a, col_b = st.columns([1, 1])
            
            with col_a:
                st.subheader("🔐 Acceso")
            with col_b:
                # Mostrar hora actual
                now = datetime.now()
                st.caption(f"📅 {now.strftime('%d/%m/%Y %H:%M')}")
            
            # Campos de entrada
            username = st.text_input(
                "**Usuario**",
                placeholder="Ingrese su usuario",
                key="login_username"
            )
            
            password = st.text_input(
                "**Contraseña**",
                type="password",
                placeholder="Ingrese su contraseña",
                key="login_password"
            )
            
            # Botón de ingreso
            submitted = st.form_submit_button(
                "🚀 **Ingresar al Sistema**",
                use_container_width=True,
                type="primary"
            )
            
            if submitted:
                if not username or not password:
                    st.error("⚠️ Por favor complete todos los campos")
                else:
                    # Mostrar spinner mientras verifica
                    with st.spinner("🔐 Verificando credenciales..."):
                        success, message = authenticate_user(username, password)
                        
                        if success:
                            # Guardar en sesión
                            st.session_state.authenticated = True
                            st.session_state.username = username
                            st.session_state.user_role = get_user_role(username)
                            st.session_state.login_time = datetime.now()
                            
                            # Mensaje de éxito
                            st.success(message)
                            
                            # Pequeña animación
                            st.balloons()
                            
                            # Redirigir después de 1 segundo
                            st.rerun()
                        else:
                            st.error(message)
            
            # Información de ayuda
            with st.expander("📋 Información de acceso", expanded=False):
                st.info("""
                **Usuarios disponibles:**
                
                👤 **Gestor de Cartera**
                - Usuario: `cartera`
                - Contraseña: `admin123`
                - Permisos: Administración completa
                
                👤 **Supervisor**
                - Usuario: `supervisor`
                - Contraseña: `view123`
                - Permisos: Solo lectura
                
                🔒 **Recomendaciones de seguridad:**
                1. Cambie las contraseñas después del primer acceso
                2. No comparta sus credenciales
                3. Cierre sesión al finalizar
                """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer
        st.markdown("---")
        st.caption("© 2024 Sistema de Control de Cupos - Versión 1.0")

# ==============================================
# FUNCIONES ADICIONALES
# ==============================================

def require_auth():
    """Decorador para requerir autenticación en funciones"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not st.session_state.get('authenticated'):
                st.warning("🔒 Acceso no autorizado. Por favor inicie sesión.")
                authenticate()
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_permission(required_role):
    """Verifica si el usuario tiene el rol requerido"""
    if not st.session_state.get('authenticated'):
        return False
    
    user_role = st.session_state.get('user_role', 'viewer')
    
    # Jerarquía de roles
    role_hierarchy = {
        'admin': 3,      # Máximo nivel
        'cartera': 2,    # Nivel intermedio
        'viewer': 1      # Solo lectura
    }
    
    user_level = role_hierarchy.get(user_role, 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    return user_level >= required_level

def show_user_info():
    """Muestra información del usuario en la barra superior"""
    if st.session_state.get('authenticated'):
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col2:
            role_display = {
                'admin': '👑 Administrador',
                'cartera': '💼 Gestor de Cartera',
                'viewer': '👁️ Supervisor'
            }
            
            role = st.session_state.get('user_role', 'viewer')
            st.info(f"👤 **{st.session_state.username}** | {role_display.get(role, 'Usuario')}")
        
        with col3:
            if st.button("🚪 Cerrar Sesión", key="logout_btn", use_container_width=True):
                # Limpiar sesión
                for key in ['authenticated', 'username', 'user_role', 'login_time']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

def show_change_password():
    """Muestra formulario para cambiar contraseña"""
    st.subheader("🔐 Cambiar Contraseña")
    
    with st.form("change_password_form"):
        current_password = st.text_input(
            "Contraseña Actual",
            type="password",
            placeholder="Ingrese su contraseña actual"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            new_password = st.text_input(
                "Nueva Contraseña",
                type="password",
                placeholder="Mínimo 8 caracteres"
            )
        
        with col2:
            confirm_password = st.text_input(
                "Confirmar Contraseña",
                type="password",
                placeholder="Repita la nueva contraseña"
            )
        
        submitted = st.form_submit_button("🔄 Cambiar Contraseña", use_container_width=True)
        
        if submitted:
            # Validaciones
            if not all([current_password, new_password, confirm_password]):
                st.error("⚠️ Complete todos los campos")
            elif new_password != confirm_password:
                st.error("⚠️ Las contraseñas no coinciden")
            elif len(new_password) < 8:
                st.error("⚠️ La contraseña debe tener al menos 8 caracteres")
            else:
                # Verificar contraseña actual
                users = load_users()
                username = st.session_state.username
                
                if users[username]["hashed_password"] == hash_password(current_password):
                    # Actualizar contraseña
                    users[username]["hashed_password"] = hash_password(new_password)
                    save_users(users)
                    
                    st.success("✅ Contraseña cambiada exitosamente")
                    st.info("🔐 Por favor inicie sesión nuevamente")
                    
                    # Cerrar sesión
                    st.session_state.authenticated = False
                    st.rerun()
                else:
                    st.error("❌ Contraseña actual incorrecta")

# ==============================================
# FUNCIÓN PRINCIPAL PARA TEST
# ==============================================

if __name__ == "__main__":
    # Inicializar usuarios si no existen
    init_users()
    
    # Mostrar login
    authenticate()
    
    # Si está autenticado, mostrar información
    if st.session_state.get('authenticated'):
        st.title("✅ Autenticación Exitosa")
        st.write(f"Bienvenido, **{st.session_state.username}**")
        st.write(f"Rol: {st.session_state.get('user_role', 'No asignado')}")
        
        if st.button("Cerrar Sesión"):
            st.session_state.authenticated = False
            st.rerun()
