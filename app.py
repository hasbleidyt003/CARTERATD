"""
Sistema de Gestión de Cartera TD - Versión Final
"""

import streamlit as st
import os
import sys

# Configuración de rutas
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuración de página
st.set_page_config(
    page_title="Control de Cupos - Medicamentos",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Función para inicializar BD
def init_db_simple():
    """Inicializa la base de datos de forma simple"""
    try:
        import sqlite3
        
        os.makedirs('data', exist_ok=True)
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        # Tabla de clientes simplificada
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nit TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            cupo_sugerido REAL DEFAULT 0,
            saldo_actual REAL DEFAULT 0,
            cartera_vencida REAL DEFAULT 0,
            activo BOOLEAN DEFAULT 1
        )
        ''')
        
        # Verificar si hay datos
        cursor.execute("SELECT COUNT(*) FROM clientes")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Insertar datos básicos
            clientes = [
                ('890905166', 'EMPRESA SOCIAL DEL ESTADO HOSPITAL MENTAL', 7500000000, 7397192942, 3342688638),
                ('900746052', 'NEURUM SAS', 5500000000, 5184247632, 2279333768),
                ('800241602', 'FUNDACION COLOMBIANA DE CANCEROLOGIA', 3500000000, 3031469552, 191990541),
                ('890985122', 'COOPERATIVA DE HOSPITALES DE ANTIOQUIA', 1500000000, 1291931405, 321889542),
            ]
            
            for nit, nombre, cupo, saldo, cartera in clientes:
                cursor.execute('''
                INSERT INTO clientes (nit, nombre, cupo_sugerido, saldo_actual, cartera_vencida)
                VALUES (?, ?, ?, ?, ?)
                ''', (nit, nombre, cupo, saldo, cartera))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error inicializando BD: {e}")
        return False

# Página principal
def main():
    st.title("💊 Sistema de Gestión de Cartera TD")
    
    # Verificar si existe la BD
    if not os.path.exists('data/database.db'):
        st.warning("⚠️ La base de datos no está inicializada")
        if st.button("🔧 Inicializar Base de Datos", type="primary"):
            if init_db_simple():
                st.success("✅ Base de datos inicializada correctamente")
                st.rerun()
            else:
                st.error("❌ Error al inicializar la base de datos")
        return
    
    # Cargar módulos de forma segura
    try:
        from modules.database import get_estadisticas_basicas, get_clientes_basicos
    except ImportError as e:
        st.error(f"❌ Error importando módulos: {e}")
        st.info("ℹ️ Verifica que el archivo modules/database.py exista y sea correcto.")
        return
    
    # Navegación por pestañas
    tabs = st.tabs(["🏠 Dashboard", "👥 Clientes", "📋 OCs", "🔧 Configuración"])
    
    with tabs[0]:
        # Dashboard simple
        try:
            stats = get_estadisticas_basicas()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Clientes", stats['total_clientes'])
            with col2:
                st.metric("Cupo Total", f"${stats['total_cupo']:,.0f}")
            with col3:
                st.metric("Saldo Actual", f"${stats['total_saldo']:,.0f}")
            
            # Mostrar clientes
            clientes = get_clientes_basicos()
            if not clientes.empty:
                st.subheader("Clientes Registrados")
                st.dataframe(clientes, use_container_width=True)
                
        except Exception as e:
            st.error(f"❌ Error cargando datos: {e}")
    
    with tabs[1]:
        st.header("Gestión de Clientes")
        st.info("Función en desarrollo")
    
    with tabs[2]:
        st.header("Órdenes de Compra")
        st.info("Función en desarrollo")
    
    with tabs[3]:
        st.header("Configuración")
        if st.button("🔄 Reinicializar Base de Datos"):
            if os.path.exists('data/database.db'):
                os.remove('data/database.db')
                st.success("✅ Base de datos eliminada. Recarga la página.")
                st.rerun()

if __name__ == "__main__":
    main()
