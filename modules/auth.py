# modules/auth.py
import streamlit as st
import hashlib
import time
from datetime import datetime, timedelta
import jwt
from .databases import DatabaseManager

class AuthSystem:
    """Sistema de autenticación robusto"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.secret_key = "clave-secreta-para-jwt-2024"
        self.token_expiry = timedelta(hours=8)
        
        # Crear tabla de usuarios si no existe
        self._create_users_table()
    
    def _create_users_table(self):
        """Crear tabla de usuarios"""
        self.db.conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            nombre_completo VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            rol VARCHAR(20) DEFAULT 'autorizador',
            activo BOOLEAN DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ultimo_acceso TIMESTAMP,
            intentos_fallidos INTEGER DEFAULT 0,
            bloqueado_hasta TIMESTAMP
        )
        ''')
        
        # Insertar usuario admin por defecto si no existe
        cursor = self.db.conn.execute("SELECT COUNT(*) as count FROM usuarios")
        if cursor.fetchone()['count'] == 0:
            self._create_default_users()
        
        self.db.conn.commit()
    
    def _create_default_users(self):
        """Crear usuarios por defecto"""
        default_users = [
            {
                'username': 'admin',
                'password': 'Admin123!',
                'nombre': 'Administrador Sistema',
                'email': 'admin@sistema.com',
                'rol': 'admin'
            },
            {
                'username': 'autorizador',
                'password': 'Autoriza123!',
                'nombre': 'Usuario Autorizador',
                'email': 'autorizador@sistema.com',
                'rol': 'autorizador'
            },
            {
                'username': 'consulta',
                'password': 'Consulta123!',
                'nombre': 'Usuario Consulta',
                'email': 'consulta@sistema.com',
                'rol': 'consulta'
            }
        ]
        
        for user in default_users:
            password_hash = self._hash_password(user['password'])
            self.db.conn.execute('''
            INSERT INTO usuarios (username, password_hash, nombre_completo, email, rol)
            VALUES (?, ?, ?, ?, ?)
            ''', (user['username'], password_hash, user['nombre'], user['email'], user['rol']))
        
        print("✅ Usuarios por defecto creados")
    
    def _hash_password(self, password):
        """Hashear contraseña"""
        salt = "sistema_autorizaciones_2024"
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def _generate_token(self, user_id, username, rol):
        """Generar token JWT"""
        payload = {
            'user_id': user_id,
            'username': username,
            'rol': rol,
            'exp': datetime.utcnow() + self.token_expiry,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def _verify_token(self, token):
        """Verificar token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def login(self, username, password):
        """Autenticar usuario"""
        # Verificar si el usuario está bloqueado
        user = self.db.execute_query(
            "SELECT * FROM usuarios WHERE username = ? AND activo = 1",
            (username,),
            fetchone=True
        )
        
        if not user:
            return False, "Usuario no encontrado o inactivo"
        
        # Verificar bloqueo temporal
        if user['bloqueado_hasta']:
            bloqueo_hasta = datetime.fromisoformat(user['bloqueado_hasta'])
            if datetime.now() < bloqueo_hasta:
                minutos_restantes = (bloqueo_hasta - datetime.now()).seconds // 60
                return False, f"Cuenta bloqueada. Intente en {minutos_restantes} minutos"
        
        # Verificar contraseña
        password_hash = self._hash_password(password)
        if user['password_hash'] != password_hash:
            # Incrementar intentos fallidos
            nuevos_intentos = user['intentos_fallidos'] + 1
            self.db.conn.execute(
                "UPDATE usuarios SET intentos_fallidos = ? WHERE id = ?",
                (nuevos_intentos, user['id'])
            )
            
            # Bloquear después de 3 intentos fallidos
            if nuevos_intentos >= 3:
                bloqueo_hasta = datetime.now() + timedelta(minutes=15)
                self.db.conn.execute(
                    "UPDATE usuarios SET bloqueado_hasta = ? WHERE id = ?",
                    (bloqueo_hasta.isoformat(), user['id'])
                )
                self.db.conn.commit()
                return False, "Demasiados intentos fallidos. Cuenta bloqueada por 15 minutos"
            
            self.db.conn.commit()
            return False, f"Contraseña incorrecta. Intentos restantes: {3 - nuevos_intentos}"
        
        # Login exitoso - resetear intentos fallidos
        self.db.conn.execute('''
        UPDATE usuarios SET 
            intentos_fallidos = 0,
            bloqueado_hasta = NULL,
            ultimo_acceso = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (user['id'],))
        
        # Generar token
        token = self._generate_token(user['id'], user['username'], user['rol'])
        
        self.db.conn.commit()
        return True, {
            'token': token,
            'user_id': user['id'],
            'username': user['username'],
            'nombre': user['nombre_completo'],
            'email': user['email'],
            'rol': user['rol']
        }
    
    def verify_session(self):
        """Verificar sesión actual"""
        if 'auth_token' not in st.session_state:
            return False
        
        payload = self._verify_token(st.session_state.auth_token)
        if not payload:
            return False
        
        # Actualizar datos de sesión
        st.session_state.user_id = payload['user_id']
        st.session_state.username = payload['username']
        st.session_state.role = payload['rol']
        st.session_state.authenticated = True
        
        return True
    
    def logout(self):
        """Cerrar sesión"""
        keys_to_remove = ['auth_token', 'user_id', 'username', 'role', 'authenticated']
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
    
    def has_permission(self, required_role):
        """Verificar permisos de usuario"""
        if not self.verify_session():
            return False
        
        user_role = st.session_state.get('role')
        
        # Jerarquía de roles
        role_hierarchy = {
            'admin': ['admin', 'autorizador', 'consulta'],
            'autorizador': ['autorizador', 'consulta'],
            'consulta': ['consulta']
        }
        
        return user_role in role_hierarchy.get(required_role, [])

# Instancia global del sistema de autenticación
auth_system = AuthSystem()

# Decorador para proteger páginas
def require_auth(required_role='consulta'):
    """Decorador para requerir autenticación"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not auth_system.verify_session():
                st.error("🔒 Debes iniciar sesión para acceder a esta página")
                st.stop()
            
            if not auth_system.has_permission(required_role):
                st.error("🚫 No tienes permisos para acceder a esta página")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Función para mostrar login
def show_login():
    """Mostrar formulario de login"""
    st.markdown("""
    <div class='main-container'>
        <div style='text-align: center; padding: 3rem 0;'>
            <h1 class='text-gradient' style='font-size: 3rem; margin-bottom: 1rem;'>🎯</h1>
            <h1 class='text-gradient' style='font-size: 2.5rem; margin-bottom: 0.5rem;'>
                SISTEMA DE AUTORIZACIONES
            </h1>
            <p style='color: #666; font-size: 1.2rem; margin-bottom: 3rem;'>
                Gestión Inteligente de Órdenes de Compra
            </p>
    """, unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                st.subheader("🔐 INICIAR SESIÓN")
                
                username = st.text_input(
                    "👤 Usuario",
                    placeholder="Ingrese su usuario"
                )
                
                password = st.text_input(
                    "🔒 Contraseña",
                    type="password",
                    placeholder="Ingrese su contraseña"
                )
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submit = st.form_submit_button(
                        "🚀 INGRESAR",
                        type="primary",
                        use_container_width=True
                    )
                with col_btn2:
                    if st.form_submit_button("🔄 LIMPIAR", use_container_width=True):
                        st.rerun()
                
                if submit:
                    if not username or not password:
                        st.error("⚠️ Por favor complete todos los campos")
                    else:
                        with st.spinner("🔐 Verificando credenciales..."):
                            success, result = auth_system.login(username, password)
                            
                            if success:
                                st.session_state.auth_token = result['token']
                                st.session_state.user_id = result['user_id']
                                st.session_state.username = result['username']
                                st.session_state.user_fullname = result['nombre']
                                st.session_state.user_email = result['email']
                                st.session_state.role = result['rol']
                                st.session_state.authenticated = True
                                
                                st.success(f"✅ ¡Bienvenido {result['nombre']}!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ {result}")
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Información de usuarios demo
    with st.expander("📋 USUARIOS DE DEMOSTRACIÓN", expanded=False):
        st.info("""
        **Usuarios disponibles para prueba:**
        
        | Usuario | Contraseña | Rol |
        |---------|------------|-----|
        | admin | Admin123! | Administrador |
        | autorizador | Autoriza123! | Autorizador |
        | consulta | Consulta123! | Solo consulta |
        
        **Nota:** Estos usuarios son solo para desarrollo.
        """)

# Función para registrar nuevo usuario (solo admin)
def register_user(username, password, nombre, email, rol='consulta'):
    """Registrar nuevo usuario"""
    if not auth_system.has_permission('admin'):
        return False, "No tienes permisos para registrar usuarios"
    
    # Validaciones
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not any(c.isupper() for c in password):
        return False, "La contraseña debe tener al menos una mayúscula"
    
    if not any(c.isdigit() for c in password):
        return False, "La contraseña debe tener al menos un número"
    
    try:
        password_hash = auth_system._hash_password(password)
        auth_system.db.conn.execute('''
        INSERT INTO usuarios (username, password_hash, nombre_completo, email, rol)
        VALUES (?, ?, ?, ?, ?)
        ''', (username, password_hash, nombre, email, rol))
        
        auth_system.db.conn.commit()
        return True, "Usuario registrado exitosamente"
    except Exception as e:
        return False, f"Error al registrar usuario: {str(e)}"
