"""
Módulo de autenticación simplificado para Streamlit
Versión básica para desarrollo - En producción usar autenticación robusta
"""

import streamlit as st
import hashlib
import sqlite3
import os
from datetime import datetime, timedelta

# ============================================================================
# INICIALIZACIÓN DE TABLA DE USUARIOS
# ============================================================================

def init_auth_db():
    """Inicializa la tabla de usuarios si no existe"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        nombre TEXT NOT NULL,
        email TEXT,
        rol TEXT DEFAULT 'usuario',  -- admin, usuario, auditor
        activo BOOLEAN DEFAULT 1,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ultimo_login TIMESTAMP
    )
    ''')
    
    # Insertar usuario admin por defecto si no existe
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        # Contraseña: admin123 (hash)
        password_hash = hash_password('admin123')
        cursor.execute('''
        INSERT INTO usuarios (username, password_hash, nombre, rol)
        VALUES (?, ?, ?, ?)
        ''', ('admin', password_hash, 'Administrador', 'admin'))
        print("✅ Usuario admin creado (contraseña: admin123)")
    
    conn.commit()
    conn.close()
    return True

# ============================================================================
# FUNCIONES DE AUTENTICACIÓN
# ============================================================================

def hash_password(password):
    """Hashea una contraseña usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    """Autentica un usuario"""
    try:
        password_hash = hash_password(password)
        
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, username, nombre, rol 
        FROM usuarios 
        WHERE username = ? AND password_hash = ? AND activo = 1
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        
        if user:
            # Actualizar último login
            cursor.execute('''
            UPDATE usuarios 
            SET ultimo_login = CURRENT_TIMESTAMP 
            WHERE id = ?
            ''', (user[0],))
            conn.commit()
            
            conn.close()
            return {
                'id': user[0],
                'username': user[1],
                'nombre': user[2],
                'rol': user[3],
                'autenticado': True
            }
        else:
            conn.close()
            return {'autenticado': False, 'error': 'Credenciales inválidas'}
            
    except Exception as e:
        print(f"Error en autenticación: {e}")
        return {'autenticado': False, 'error': str(e)}

def create_user(username, password, nombre, email="", rol="usuario"):
    """Crea un nuevo usuario"""
    try:
        password_hash = hash_password(password)
        
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO usuarios (username, password_hash, nombre, email, rol)
        VALUES (?, ?, ?, ?, ?)
        ''', (username, password_hash, nombre, email, rol))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        raise Exception(f"El usuario '{username}' ya existe")
    except Exception as e:
        raise Exception(f"Error al crear usuario: {str(e)}")

def change_password(username, old_password, new_password):
    """Cambia la contraseña de un usuario"""
    # Primero autenticar
    auth = authenticate(username, old_password)
    
    if not auth['autenticado']:
        return {'success': False, 'error': 'Contraseña actual incorrecta'}
    
    try:
        new_password_hash = hash_password(new_password)
        
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE usuarios 
        SET password_hash = ? 
        WHERE username = ?
        ''', (new_password_hash, username))
        
        conn.commit()
        conn.close()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_all_users():
    """Obtiene todos los usuarios (solo para admin)"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT id, username, nombre, email, rol, activo, 
           fecha_creacion, ultimo_login
    FROM usuarios
    ORDER BY fecha_creacion DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ============================================================================
# DECORADORES Y FUNCIONES DE CONTROL DE ACCESO
# ============================================================================

def require_login(func):
    """Decorador para requerir autenticación"""
    def wrapper(*args, **kwargs):
        if 'user' not in st.session_state or not st.session_state.user.get('autenticado', False):
            st.warning("⚠️ Debes iniciar sesión para acceder a esta página")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def require_role(roles):
    """Decorador para requerir roles específicos"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Primero verificar login
            if 'user' not in st.session_state or not st.session_state.user.get('autenticado', False):
                st.warning("⚠️ Debes iniciar sesión para acceder a esta página")
                st.stop()
            
            # Verificar rol
            user_role = st.session_state.user.get('rol', '')
            if user_role not in roles:
                st.error("🚫 No tienes permisos para acceder a esta función")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ============================================================================
# FUNCIONES PARA STREAMLIT
# ============================================================================

def show_login_page():
    """Muestra la página de login en Streamlit"""
    st.title("🔐 Sistema de Gestión de Cartera TD")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.subheader("Inicio de Sesión")
            
            username = st.text_input("Usuario", key="login_username")
            password = st.text_input("Contraseña", type="password", key="login_password")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("🚀 Ingresar", type="primary", use_container_width=True):
                    if not username or not password:
                        st.error("Por favor complete ambos campos")
                    else:
                        user = authenticate(username, password)
                        
                        if user['autenticado']:
                            st.session_state.user = user
                            st.success(f"✅ Bienvenido, {user['nombre']}!")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {user.get('error', 'Credenciales inválidas')}")
            
            with col_btn2:
                if st.button("🔄 Restablecer", use_container_width=True):
                    st.session_state.login_username = ""
                    st.session_state.login_password = ""
                    st.rerun()
            
            st.markdown("---")
            
            # Información de ayuda
            with st.expander("ℹ️ Información de acceso"):
                st.write("""
                **Para desarrollo:**
                - Usuario: `admin`
                - Contraseña: `admin123`
                
                **Roles disponibles:**
                - **admin:** Acceso completo
                - **usuario:** Acceso básico
                - **auditor:** Solo lectura
                
                **Nota:** En producción, implementar autenticación robusta.
                """)

def show_user_management():
    """Muestra la gestión de usuarios (solo para admin)"""
    st.header("👥 Gestión de Usuarios")
    
    if st.session_state.user.get('rol') != 'admin':
        st.error("🚫 Solo los administradores pueden acceder a esta sección")
        return
    
    tab1, tab2 = st.tabs(["📋 Usuarios Existentes", "➕ Nuevo Usuario"])
    
    with tab1:
        try:
            users = get_all_users()
            
            if not users.empty:
                st.dataframe(
                    users[['username', 'nombre', 'email', 'rol', 'activo', 'ultimo_login']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No hay usuarios registrados")
                
        except Exception as e:
            st.error(f"Error al cargar usuarios: {str(e)}")
    
    with tab2:
        with st.form("nuevo_usuario_form"):
            st.subheader("➕ Crear Nuevo Usuario")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Nombre de usuario *")
                new_nombre = st.text_input("Nombre completo *")
            
            with col2:
                new_password = st.text_input("Contraseña *", type="password")
                new_email = st.text_input("Correo electrónico")
                new_rol = st.selectbox("Rol", ["usuario", "admin", "auditor"])
            
            submitted = st.form_submit_button("💾 Crear Usuario", type="primary")
            
            if submitted:
                if not all([new_username, new_nombre, new_password]):
                    st.error("Los campos marcados con * son obligatorios")
                else:
                    try:
                        create_user(new_username, new_password, new_nombre, new_email, new_rol)
                        st.success(f"✅ Usuario '{new_username}' creado exitosamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# ============================================================================
# INICIALIZACIÓN
# ============================================================================

# Inicializar tabla de usuarios si no existe
if __name__ == "__main__":
    init_auth_db()
    print("✅ Módulo de autenticación listo")
