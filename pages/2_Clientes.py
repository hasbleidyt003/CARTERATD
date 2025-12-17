import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="👥 Clientes",
    page_icon="👥",
    layout="wide"
)

# ==================== FUNCIONES BD ====================
def get_clientes():
    conn = sqlite3.connect('database.db')
    query = '''
    SELECT * FROM clientes WHERE activo = 1 ORDER BY nombre
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_ocs_por_cliente(nit):
    conn = sqlite3.connect('database.db')
    query = '''
    SELECT COUNT(*) as total_ocs, 
           SUM(CASE WHEN estado IN ('PENDIENTE', 'PARCIAL') THEN valor_total - valor_autorizado ELSE 0 END) as pendientes
    FROM ocs WHERE cliente_nit = ?
    '''
    df = pd.read_sql_query(query, conn, params=(nit,))
    conn.close()
    return df

# ==================== CONTENIDO PÁGINA ====================
st.title("👥 Gestión de Clientes")

# Verificar autenticación
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("🔒 Por favor inicie sesión primero")
    st.stop()

# Pestañas
tab1, tab2 = st.tabs(["📋 Lista de Clientes", "➕ Nuevo Cliente"])

with tab1:
    clientes = get_clientes()
    
    if not clientes.empty:
        for _, cliente in clientes.iterrows():
            with st.expander(f"{cliente['nombre']} (NIT: {cliente['nit']})", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    nuevo_cupo = st.number_input(
                        "Cupo Sugerido",
                        value=float(cliente['cupo_sugerido']),
                        key=f"cupo_{cliente['nit']}",
                        step=1000000.0
                    )
                
                with col2:
                    nuevo_saldo = st.number_input(
                        "Saldo Actual",
                        value=float(cliente['saldo_actual']),
                        key=f"saldo_{cliente['nit']}",
                        step=1000000.0
                    )
                
                # Mostrar estadísticas del cliente
                stats = get_ocs_por_cliente(cliente['nit'])
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.metric("OCs Totales", int(stats['total_ocs'].iloc[0]) if pd.notnull(stats['total_ocs'].iloc[0]) else 0)
                with col_info2:
                    pendientes_val = stats['pendientes'].iloc[0] if pd.notnull(stats['pendientes'].iloc[0]) else 0
                    st.metric("Pendientes", f"${pendientes_val:,.0f}")
                
                if st.button("💾 Guardar Cambios", key=f"guardar_{cliente['nit']}"):
                    conn = sqlite3.connect('database.db')
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE clientes 
                        SET cupo_sugerido = ?, saldo_actual = ?, fecha_actualizacion = ?
                        WHERE nit = ?
                    ''', (nuevo_cupo, nuevo_saldo, datetime.now(), cliente['nit']))
                    conn.commit()
                    conn.close()
                    st.success("✅ Datos actualizados")
                    st.rerun()
    else:
        st.info("No hay clientes registrados")

with tab2:
    with st.form("nuevo_cliente"):
        col1, col2 = st.columns(2)
        
        with col1:
            nit = st.text_input("NIT *", help="Número de identificación tributaria")
            nombre = st.text_input("Nombre del Cliente *")
        
        with col2:
            cupo_sugerido = st.number_input("Cupo Sugerido Inicial *", 
                                          min_value=0.0, 
                                          value=0.0,
                                          step=1000000.0)
            saldo_actual = st.number_input("Saldo Actual Inicial *",
                                         min_value=0.0,
                                         value=0.0,
                                         step=1000000.0)
        
        if st.form_submit_button("💾 Crear Cliente", use_container_width=True):
            if nit and nombre:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                try:
                    cursor.execute('''
                        INSERT INTO clientes (nit, nombre, cupo_sugerido, saldo_actual)
                        VALUES (?, ?, ?, ?)
                    ''', (nit, nombre, cupo_sugerido, saldo_actual))
                    conn.commit()
                    st.success(f"✅ Cliente '{nombre}' creado exitosamente")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("❌ Ya existe un cliente con ese NIT")
                finally:
                    conn.close()
            else:
                st.error("❌ Complete los campos obligatorios (*)")
