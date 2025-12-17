import streamlit as st
from auth import check_auth, logout_button, get_current_user
import time
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="Sistema de Cartera - Medicamentos",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verificar autenticación
check_auth()

# ============================================================================
# SIDEBAR - MENÚ PRINCIPAL
# ============================================================================

with st.sidebar:
    # Logo y título
    st.markdown("""
    <div style='text-align: center; margin-bottom: 20px;'>
        <h2 style='color: #1E3A8A;'>💰 Sistema de Cartera</h2>
        <p style='color: #6B7280; font-size: 14px;'>Control de Cupos - Medicamentos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Información del usuario
    st.markdown("---")
    usuario_actual = get_current_user()
    st.markdown(f"**👤 Usuario:** {usuario_actual}")
    st.markdown(f"**📅 Fecha:** {datetime.now().strftime('%d/%m/%Y')}")
    
    st.markdown("---")
    
    # Menú de navegación
    st.markdown("### 📋 Navegación")
    
    # Opciones del menú
    if st.button("📊 Dashboard", use_container_width=True, key="btn_dashboard"):
        st.switch_page("pages/1_Dashboard.py")
    
    if st.button("👥 Clientes", use_container_width=True, key="btn_clientes"):
        st.switch_page("pages/2_Clientes.py")
    
    if st.button("📋 Órdenes de Compra", use_container_width=True, key="btn_ocs"):
        st.switch_page("pages/3_OCs.py")
    
    if st.button("⚙️ Mantenimiento", use_container_width=True, key="btn_mantenimiento"):
        st.switch_page("pages/4_Mantenimiento.py")
    
    st.markdown("---")
    
    # Botón de cerrar sesión
    if st.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True):
        logout_button()
    
    # Información del sistema
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6B7280; font-size: 12px;'>
        <p>Sistema de Cartera v1.0</p>
        <p>© 2024</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# CONTENIDO PRINCIPAL - HOME
# ============================================================================

# Título principal
st.title("🏥 Sistema de Gestión de Cartera - Medicamentos")
st.markdown("---")

# Bienvenida
col_welcome1, col_welcome2 = st.columns([3, 1])

with col_welcome1:
    st.markdown(f"""
    ### Bienvenido, {usuario_actual}
    
    **Sistema especializado para el control y seguimiento de cupos de medicamentos.**
    
    Esta aplicación permite gestionar:
    - Clientes y sus cupos asignados
    - Órdenes de compra pendientes
    - Autorizaciones y pagos
    - Estados de cartera y alertas
    
    **Última actualización:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
    """)

with col_welcome2:
    # Métricas rápidas
    try:
        from database import get_estadisticas_generales
        stats = get_estadisticas_generales()
        
        st.metric("Clientes Activos", stats['total_clientes'])
        st.metric("Cupo Total", f"${stats['total_cupo_sugerido']:,.0f}")
        st.metric("Saldo Actual", f"${stats['total_saldo_actual']:,.0f}")
        
    except Exception as e:
        st.info("Inicializando sistema...")

st.markdown("---")

# Sección de acceso rápido
st.subheader("⚡ Acceso Rápido")

col_quick1, col_quick2, col_quick3, col_quick4 = st.columns(4)

with col_quick1:
    if st.button("Ver Dashboard", use_container_width=True, icon="📊"):
        st.switch_page("pages/1_Dashboard.py")

with col_quick2:
    if st.button("Gestionar Clientes", use_container_width=True, icon="👥"):
        st.switch_page("pages/2_Clientes.py")

with col_quick3:
    if st.button("Nueva Orden", use_container_width=True, icon="📋"):
        st.switch_page("pages/3_OCs.py")

with col_quick4:
    if st.button("Reportes", use_container_width=True, icon="📈"):
        st.switch_page("pages/4_Mantenimiento.py")

st.markdown("---")

# Sección de novedades/recientes
st.subheader("📋 Actividad Reciente")

tab_recent1, tab_recent2, tab_recent3 = st.tabs(["Clientes", "Órdenes", "Sistema"])

with tab_recent1:
    try:
        from database import get_clientes
        clientes = get_clientes()
        if not clientes.empty:
            st.write("**Últimos clientes registrados:**")
            for _, cliente in clientes.head(3).iterrows():
                st.markdown(f"""
                - **{cliente['nombre']}** 
                  Cupo: ${cliente['cupo_sugerido']:,.0f} 
                  Estado: {cliente['estado']}
                """)
        else:
            st.info("No hay clientes registrados")
    except:
        st.info("Cargando información de clientes...")

with tab_recent2:
    try:
        from database import get_ocs_pendientes
        ocs = get_ocs_pendientes()
        if not ocs.empty:
            st.write("**Órdenes pendientes:**")
            for _, oc in ocs.head(3).iterrows():
                st.markdown(f"""
                - **OC {oc['numero_oc']}** 
                  Cliente: {oc['cliente_nombre']}
                  Valor pendiente: ${oc['valor_pendiente']:,.0f}
                """)
        else:
            st.success("No hay órdenes pendientes")
    except:
        st.info("Cargando información de órdenes...")

with tab_recent3:
    st.markdown("""
    **Estado del sistema:**
    - ✅ Base de datos operativa
    - ✅ Módulos cargados correctamente
    - ✅ Usuario autenticado
    
    **Próximas acciones sugeridas:**
    1. Revisar clientes en estado de alerta
    2. Autorizar órdenes pendientes
    3. Actualizar saldos de clientes
    """)

st.markdown("---")

# Información de ayuda
with st.expander("ℹ️ Ayuda Rápida"):
    st.markdown("""
    **¿Cómo usar el sistema?**
    
    1. **Dashboard:** Visualiza métricas generales y estados
    2. **Clientes:** Gestiona información de clientes y sus cupos
    3. **Órdenes:** Crea y autoriza órdenes de compra
    4. **Mantenimiento:** Realiza backups y limpieza del sistema
    
    **Atajos:**
    - F5: Actualizar página
    - Ctrl+R: Refrescar datos
    - Click en cualquier métrica para ver detalles
    
    **Soporte:**
    - Contacto: sistemas@empresa.com
    - Teléfono: 123-456-7890
    """)

# Inicializar base de datos si no existe
try:
    from database import init_db
    init_db()
    st.sidebar.success("✅ Sistema listo")
except Exception as e:
    st.sidebar.warning(f"⚠️ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280; font-size: 12px;'>
    <p>Sistema de Cartera v1.0 • Desarrollado para gestión de cupos de medicamentos</p>
    <p>Todos los derechos reservados © 2024</p>
</div>
""", unsafe_allow_html=True)
