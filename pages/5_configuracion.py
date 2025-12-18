"""
PÁGINA 5 - CONFIGURACIÓN DEL SISTEMA
Configuración de usuarios y parámetros del sistema
"""

import streamlit as st
import hashlib
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="Configuración - Tododrogas",
    page_icon="⚙️",
    layout="wide"
)

# Importar módulos
from modules.auth import require_admin
from modules.database import get_usuarios, crear_usuario

# Verificar que sea administrador
user = require_admin()

# ==================== FUNCIONES AUXILIARES ====================

def hash_password(password):
    """Encripta una contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

# ==================== PÁGINA PRINCIPAL ====================

def show_config_page():
    """Muestra la página de configuración"""
    
    st.title("⚙️ CONFIGURACIÓN DEL SISTEMA")
    st.markdown("Gestión de usuarios y configuración del sistema")
    
    # Pestañas de configuración
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Usuarios",
        "🏢 Empresa", 
        "📊 Sistema",
        "🔐 Seguridad"
    ])
    
    # ========== PESTAÑA 1: USUARIOS ==========
    with tab1:
        st.subheader("👥 GESTIÓN DE USUARIOS")
        
        # Obtener usuarios
        with st.spinner("Cargando usuarios..."):
            usuarios_df = get_usuarios()
        
        # Mostrar usuarios existentes
        if not usuarios_df.empty:
            st.markdown("### 📋 USUARIOS REGISTRADOS")
            
            # Filtrar columnas para mostrar
            display_df = usuarios_df.copy()
            display_df['activo'] = display_df['activo'].apply(lambda x: '✅ Activo' if x else '❌ Inactivo')
            
            if 'password_hash' in display_df.columns:
                display_df = display_df.drop(columns=['password_hash'])
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
        
        # Formulario para crear nuevo usuario
        st.markdown("### ➕ CREAR NUEVO USUARIO")
        
        with st.form("nuevo_usuario_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nuevo_username = st.text_input(
                    "Nombre de usuario *",
                    placeholder="usuario123",
                    help="Nombre único para iniciar sesión"
                )
                
                nuevo_nombre = st.text_input(
                    "Nombre completo *",
                    placeholder="Juan Pérez",
                    help="Nombre real del usuario"
                )
            
            with col2:
                nuevo_password = st.text_input(
                    "Contraseña *",
                    type="password",
                    placeholder="Mínimo 8 caracteres",
                    help="Contraseña segura para el usuario"
                )
                
                confirm_password = st.text_input(
                    "Confirmar contraseña *",
                    type="password",
                    placeholder="Repite la contraseña"
                )
                
                nuevo_rol = st.selectbox(
                    "Rol *",
                    ["usuario", "admin"],
                    help="Usuario: acceso normal, Admin: acceso completo"
                )
            
            # Validación de contraseña
            if nuevo_password:
                if len(nuevo_password) < 8:
                    st.warning("⚠️ La contraseña debe tener al menos 8 caracteres")
                
                if nuevo_password != confirm_password:
                    st.error("❌ Las contraseñas no coinciden")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                crear = st.form_submit_button(
                    "👤 CREAR USUARIO",
                    type="primary",
                    use_container_width=True
                )
            
            with col_btn2:
                cancelar = st.form_submit_button(
                    "❌ CANCELAR",
                    use_container_width=True
                )
            
            if crear:
                if not all([nuevo_username, nuevo_nombre, nuevo_password, confirm_password]):
                    st.error("❌ Por favor complete todos los campos obligatorios (*)")
                elif nuevo_password != confirm_password:
                    st.error("❌ Las contraseñas no coinciden")
                elif len(nuevo_password) < 8:
                    st.error("❌ La contraseña debe tener al menos 8 caracteres")
                else:
                    try:
                        crear_usuario(
                            username=nuevo_username,
                            password=nuevo_password,
                            nombre=nuevo_nombre,
                            rol=nuevo_rol
                        )
                        
                        st.success(f"✅ Usuario '{nuevo_username}' creado exitosamente")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error al crear usuario: {str(e)}")
        
        # Cambiar contraseña de usuario existente
        st.markdown("### 🔐 CAMBIAR CONTRASEÑA")
        
        if not usuarios_df.empty:
            usuario_cambiar = st.selectbox(
                "Seleccionar usuario",
                usuarios_df['username'].tolist()
            )
            
            nueva_password = st.text_input(
                "Nueva contraseña",
                type="password",
                key="cambiar_password"
            )
            
            confirmar_nueva = st.text_input(
                "Confirmar nueva contraseña",
                type="password",
                key="confirmar_cambiar"
            )
            
            if st.button("🔄 ACTUALIZAR CONTRASEÑA", use_container_width=True):
                if not nueva_password or not confirmar_nueva:
                    st.error("❌ Por favor complete ambos campos")
                elif nueva_password != confirmar_nueva:
                    st.error("❌ Las contraseñas no coinciden")
                elif len(nueva_password) < 8:
                    st.error("❌ La contraseña debe tener al menos 8 caracteres")
                else:
                    try:
                        # En una implementación real, aquí se actualizaría en la BD
                        st.success(f"✅ Contraseña de '{usuario_cambiar}' actualizada (simulación)")
                    except Exception as e:
                        st.error(f"❌ Error al actualizar: {str(e)}")
    
    # ========== PESTAÑA 2: EMPRESA ==========
    with tab2:
        st.subheader("🏢 CONFIGURACIÓN EMPRESARIAL")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ℹ️ INFORMACIÓN DE LA EMPRESA")
            
            # Datos de la empresa (simulados)
            empresa_nombre = st.text_input(
                "Nombre de la empresa",
                value="TODODROGAS S.A.S"
            )
            
            empresa_nit = st.text_input(
                "NIT de la empresa",
                value="900.000.000-1"
            )
            
            empresa_direccion = st.text_input(
                "Dirección",
                value="Calle 123 #45-67, Medellín, Colombia"
            )
            
            empresa_telefono = st.text_input(
                "Teléfono",
                value="+57 (4) 123 4567"
            )
        
        with col2:
            st.markdown("### ⚙️ PARÁMETROS DEL SISTEMA")
            
            # Umbrales de alerta
            st.markdown("#### 🚨 UMBRALES DE ALERTA")
            
            umbral_alerta = st.slider(
                "Umbral de alerta (%)",
                min_value=50,
                max_value=95,
                value=80,
                help="Porcentaje de uso que activa estado ALERTA"
            )
            
            umbral_critico = st.slider(
                "Umbral crítico (%)",
                min_value=umbral_alerta + 1,
                max_value=100,
                value=90,
                help="Porcentaje de uso que activa estado CRÍTICO"
            )
            
            # Políticas de autorización
            st.markdown("#### ✅ POLÍTICAS DE AUTORIZACIÓN")
            
            requiere_aprobacion = st.number_input(
                "Valor mínimo que requiere aprobación adicional",
                min_value=0.0,
                value=1000000000.0,  # 1,000 millones
                step=100000000.0,
                format="%.0f"
            )
            
            limite_autorizacion = st.number_input(
                "Límite máximo de autorización por OC",
                min_value=0.0,
                value=5000000000.0,  # 5,000 millones
                step=1000000000.0,
                format="%.0f"
            )
        
        # Botón de guardar
        if st.button("💾 GUARDAR CONFIGURACIÓN EMPRESA", use_container_width=True):
            st.success("✅ Configuración empresarial guardada")
            
            # Mostrar resumen
            st.info(f"""
            **Resumen de configuración:**
            
            **Empresa:**
            - Nombre: {empresa_nombre}
            - NIT: {empresa_nit}
            - Dirección: {empresa_direccion}
            - Teléfono: {empresa_telefono}
            
            **Parámetros:**
            - Umbral alerta: {umbral_alerta}%
            - Umbral crítico: {umbral_critico}%
            - Requiere aprobación: {format(requiere_aprobacion, ',.0f')}
            - Límite autorización: {format(limite_autorizacion, ',.0f')}
            """)
    
    # ========== PESTAÑA 3: SISTEMA ==========
    with tab3:
        st.subheader("📊 CONFIGURACIÓN DEL SISTEMA")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👁️ PREFERENCIAS DE VISUALIZACIÓN")
            
            # Formato de números
            formato_moneda = st.selectbox(
                "Formato de moneda",
                ["$1,000,000", "$1.000.000", "USD 1,000,000"]
            )
            
            separador_miles = st.selectbox(
                "Separador de miles",
                [", (coma)", ". (punto)", " (espacio)"]
            )
            
            decimales = st.slider(
                "Decimales a mostrar",
                min_value=0,
                max_value=4,
                value=0
            )
            
            # Unidades
            usar_millones = st.checkbox(
                "Usar millones como unidad",
                value=True,
                help="Mostrar 1.5M en lugar de 1,500,000"
            )
            
            # Idioma
            idioma = st.selectbox(
                "Idioma del sistema",
                ["Español", "English"]
            )
        
        with col2:
            st.markdown("### 📁 CONFIGURACIÓN DE DATOS")
            
            # Backup automático
            backup_auto = st.checkbox(
                "Backup automático diario",
                value=True
            )
            
            if backup_auto:
                hora_backup = st.time_input(
                    "Hora del backup",
                    value=datetime.strptime("02:00", "%H:%M").time()
                )
            
            # Retención de datos
            retencion_ocs = st.selectbox(
                "Retención de OCs antiguas",
                ["30 días", "60 días", "90 días", "1 año", "Indefinido"]
            )
            
            # Limpieza automática
            limpieza_auto = st.checkbox(
                "Limpieza automática de registros",
                value=False
            )
            
            # Logs del sistema
            nivel_log = st.selectbox(
                "Nivel de logging",
                ["Error", "Warning", "Info", "Debug"]
            )
        
        # Acciones del sistema
        st.markdown("### 🛠️ ACCIONES DEL SISTEMA")
        
        col_acc1, col_acc2, col_acc3 = st.columns(3)
        
        with col_acc1:
            if st.button("🔄 OPTIMIZAR BASE DE DATOS", use_container_width=True):
                st.info("🔧 Optimizando base de datos...")
                st.success("✅ Base de datos optimizada correctamente")
        
        with col_acc2:
            if st.button("🧹 LIMPIAR CACHÉ", use_container_width=True):
                st.info("🧽 Limpiando caché del sistema...")
                st.success("✅ Caché limpiado correctamente")
        
        with col_acc3:
            if st.button("📊 REINDEXAR DATOS", use_container_width=True):
                st.info("📈 Reindexando datos...")
                st.success("✅ Datos reindexados correctamente")
        
        # Botón de guardar
        if st.button("💾 GUARDAR CONFIGURACIÓN SISTEMA", use_container_width=True, type="primary"):
            st.success("✅ Configuración del sistema guardada")
    
    # ========== PESTAÑA 4: SEGURIDAD ==========
    with tab4:
        st.subheader("🔐 CONFIGURACIÓN DE SEGURIDAD")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔒 SEGURIDAD DE ACCESO")
            
            # Autenticación de dos factores
            usar_2fa = st.checkbox(
                "Habilitar autenticación de dos factores",
                value=False
            )
            
            # Límite de intentos
            max_intentos = st.number_input(
                "Máximo intentos de login",
                min_value=1,
                max_value=10,
                value=3
            )
            
            # Bloqueo por inactividad
            timeout_sesion = st.selectbox(
                "Timeout de sesión",
                ["15 minutos", "30 minutos", "1 hora", "4 horas", "8 horas"]
            )
            
            # IP restrictions
            restringir_ip = st.checkbox(
                "Restringir acceso por IP",
                value=False
            )
            
            if restringir_ip:
                ips_permitidas = st.text_area(
                    "IPs permitidas (una por línea)",
                    placeholder="192.168.1.1\n10.0.0.1",
                    height=100
                )
        
        with col2:
            st.markdown("### 📝 REGISTRO DE AUDITORÍA")
            
            # Log de auditoría
            log_auditoria = st.checkbox(
                "Habilitar registro de auditoría completo",
                value=True
            )
            
            if log_auditoria:
                eventos_log = st.multiselect(
                    "Eventos a registrar",
                    [
                        "Login/Logout",
                        "Creación/Modificación OCs",
                        "Autorizaciones",
                        "Cambios en cupos",
                        "Creación/Modificación usuarios",
                        "Exportación de datos"
                    ],
                    default=[
                        "Login/Logout",
                        "Creación/Modificación OCs",
                        "Autorizaciones",
                        "Cambios en cupos"
                    ]
                )
            
            # Retención de logs
            retencion_logs = st.selectbox(
                "Retención de logs de auditoría",
                ["7 días", "30 días", "90 días", "1 año", "Indefinido"]
            )
            
            # Notificaciones de seguridad
            notificar_intentos = st.checkbox(
                "Notificar intentos fallidos de login",
                value=True
            )
            
            if notificar_intentos:
                email_notificacion = st.text_input(
                    "Email para notificaciones",
                    placeholder="seguridad@tododrogas.com"
                )
        
        # Cambiar contraseña del administrador
        st.markdown("### 👑 CAMBIAR CONTRASEÑA ADMINISTRADOR")
        
        with st.form("cambiar_password_admin"):
            st.warning("⚠️ Esta acción cambiará la contraseña del administrador actual")
            
            password_actual = st.text_input(
                "Contraseña actual *",
                type="password"
            )
            
            nueva_password_admin = st.text_input(
                "Nueva contraseña *",
                type="password"
            )
            
            confirmar_password_admin = st.text_input(
                "Confirmar nueva contraseña *",
                type="password"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                cambiar = st.form_submit_button(
                    "🔐 CAMBIAR CONTRASEÑA",
                    type="primary",
                    use_container_width=True
                )
            
            with col_btn2:
                cancelar_cambio = st.form_submit_button(
                    "❌ CANCELAR",
                    use_container_width=True
                )
            
            if cambiar:
                if not all([password_actual, nueva_password_admin, confirmar_password_admin]):
                    st.error("❌ Por favor complete todos los campos")
                elif nueva_password_admin != confirmar_password_admin:
                    st.error("❌ Las contraseñas no coinciden")
                elif len(nueva_password_admin) < 8:
                    st.error("❌ La contraseña debe tener al menos 8 caracteres")
                else:
                    # En una implementación real, aquí se validaría la contraseña actual
                    st.success("✅ Contraseña de administrador actualizada (simulación)")
        
        # Botón de guardar seguridad
        if st.button("💾 GUARDAR CONFIGURACIÓN SEGURIDAD", use_container_width=True):
            st.success("✅ Configuración de seguridad guardada")

# ==================== EJECUCIÓN ====================

if __name__ == "__main__":
    show_config_page()
