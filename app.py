import streamlit as st
from modules.auth import authenticate
from modules.database import init_db
import importlib
import warnings
warnings.filterwarnings('ignore')

# Configuración de página
st.set_page_config(
    page_title="Control de Cupos - Medicamentos",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicializar base de datos
init_db()

# Sistema de autenticación
def main():
    # Mostrar login si no está autenticado
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        authenticate()
    else:
        # Mostrar aplicación principal
        show_main_app()

def show_main_app():
    # CSS personalizado
    try:
        with open('assets/styles.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except:
        pass  # Si no existe el CSS, continuar sin problemas
    
    # Barra superior
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        st.title("💊 Control de Cupos - Medicamentos")
    with col2:
        st.info(f"Usuario: {st.session_state.username}")
    with col3:
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.authenticated = False
            st.rerun()
    
    # Navegación por pestañas
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 Dashboard", 
        "👥 Clientes", 
        "📋 OCs Pendientes", 
        "🧹 Mantenimiento"
    ])
    
    # ✅ IMPORTAR CORRECTAMENTE los módulos
    with tab1:
        try:
            # Primero intentar con el nombre con emoji
            try:
                dashboard = importlib.import_module("pages.1_🏠_Dashboard")
                dashboard.show()
            except:
                # Si falla, intentar sin emoji
                try:
                    dashboard = importlib.import_module("pages.1_dashboard")
                    dashboard.show()
                except:
                    # Último intento con ruta directa
                    import sys
                    sys.path.append('.')
                    from pages.dashboard import show
                    show()
        except Exception as e:
            st.error(f"Error cargando Dashboard: {str(e)}")
            st.info("Asegúrate que existe: pages/1_🏠_Dashboard.py o pages/1_dashboard.py")
            # Mostrar un dashboard básico en caso de error
            st.subheader("📊 Dashboard")
            from modules.database import get_estadisticas_generales
            try:
                stats = get_estadisticas_generales()
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Clientes Activos", stats['total_clientes'])
                with col2:
                    st.metric("Total Cupo", f"${stats['total_cupo_sugerido']:,.0f}")
                with col3:
                    st.metric("Total Saldo", f"${stats['total_saldo_actual']:,.0f}")
                with col4:
                    st.metric("Total Disponible", f"${stats['total_disponible']:,.0f}")
            except:
                st.info("No se pudieron cargar las estadísticas. La base de datos puede estar vacía.")
    
    with tab2:
        try:
            # Intentar con el nombre con emoji
            try:
                clientes = importlib.import_module("pages.2_👥_Clientes")
                clientes.show()
            except:
                # Si falla, intentar sin emoji
                try:
                    clientes = importlib.import_module("pages.2_clientes")
                    clientes.show()
                except:
                    # Último intento
                    import sys
                    sys.path.append('.')
                    from pages.clientes import show
                    show()
        except Exception as e:
            st.error(f"Error cargando Clientes: {str(e)}")
            st.info("Asegúrate que existe: pages/2_👥_Clientes.py o pages/2_clientes.py")
            # Mostrar clientes básicos
            st.subheader("👥 Clientes")
            from modules.database import get_clientes
            try:
                clientes_df = get_clientes()
                if not clientes_df.empty:
                    st.dataframe(clientes_df[['nit', 'nombre', 'cupo_sugerido', 'saldo_actual', 'disponible']])
                else:
                    st.info("No hay clientes registrados.")
            except:
                st.info("No se pudieron cargar los clientes.")
    
    with tab3:
        try:
            # Intentar con el nombre con emoji
            try:
                ocs = importlib.import_module("pages.3_📋_OCs")
                ocs.show()
            except:
                # Si falla, intentar sin emoji
                try:
                    ocs = importlib.import_module("pages.3_ocs")
                    ocs.show()
                except:
                    # Último intento
                    import sys
                    sys.path.append('.')
                    from pages.ocs import show
                    show()
        except Exception as e:
            st.error(f"Error cargando OCs: {str(e)}")
            st.info("Asegúrate que existe: pages/3_📋_OCs.py o pages/3_ocs.py")
            st.info("**Nota:** Ya tienes este archivo modificado con las funciones de edición.")
    
    with tab4:
        try:
            # Intentar con el nombre con emoji
            try:
                mantenimiento = importlib.import_module("pages.4_🧹_Mantenimiento")
                mantenimiento.show()
            except:
                # Si falla, intentar sin emoji
                try:
                    mantenimiento = importlib.import_module("pages.4_mantenimiento")
                    mantenimiento.show()
                except:
                    # Último intento
                    import sys
                    sys.path.append('.')
                    from pages.mantenimiento import show
                    show()
        except Exception as e:
            st.error(f"Error cargando Mantenimiento: {str(e)}")
            st.info("Asegúrate que existe: pages/4_🧹_Mantenimiento.py o pages/4_mantenimiento.py")
            # Mostrar funciones básicas de mantenimiento
            st.subheader("🧹 Mantenimiento")
            from modules.database import exportar_a_excel, optimizar_base_datos
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📤 Exportar a Excel"):
                    try:
                        ruta = exportar_a_excel()
                        st.success(f"✅ Exportado a: {ruta}")
                        with open(ruta, "rb") as file:
                            st.download_button(
                                label="📥 Descargar Excel",
                                data=file,
                                file_name="backup_cartera.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    except Exception as e:
                        st.error(f"Error al exportar: {str(e)}")
            with col2:
                if st.button("⚡ Optimizar Base de Datos"):
                    try:
                        optimizar_base_datos()
                        st.success("✅ Base de datos optimizada")
                    except Exception as e:
                        st.error(f"Error al optimizar: {str(e)}")

if __name__ == "__main__":
    main()
