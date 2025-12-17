import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="🏠 Dashboard",
    page_icon="📊",
    layout="wide"
)

# ==================== FUNCIONES BD ====================
def get_clientes():
    conn = sqlite3.connect('database.db')
    query = '''
    SELECT 
        c.*,
        (c.cupo_sugerido - c.saldo_actual) as disponible,
        COALESCE(SUM(o.valor_total - o.valor_autorizado), 0) as pendientes_total
    FROM clientes c
    LEFT JOIN ocs o ON c.nit = o.cliente_nit AND o.estado IN ('PENDIENTE', 'PARCIAL')
    WHERE c.activo = 1
    GROUP BY c.nit
    ORDER BY c.nombre
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_ocs():
    conn = sqlite3.connect('database.db')
    query = '''
    SELECT o.*, c.nombre as cliente_nombre 
    FROM ocs o
    JOIN clientes c ON o.cliente_nit = c.nit
    ORDER BY o.fecha_registro DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ==================== CONTENIDO PÁGINA ====================
st.title("🏠 Dashboard")

# Verificar autenticación
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("🔒 Por favor inicie sesión primero")
    st.stop()

# Obtener datos
clientes = get_clientes()
ocs = get_ocs()
pendientes = ocs[ocs['estado'].isin(['PENDIENTE', 'PARCIAL'])]

# Métricas
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_cupo = clientes['cupo_sugerido'].sum()
    st.metric("Cupo Total", f"${total_cupo:,.0f}")

with col2:
    total_pendientes = pendientes['valor_total'].sum() - pendientes['valor_autorizado'].sum()
    st.metric("Pendientes Total", f"${total_pendientes:,.0f}")

with col3:
    clientes_alerta = len(clientes[clientes['disponible'] < 0])
    st.metric("Clientes en Alerta", clientes_alerta)

with col4:
    ocs_parciales = len(pendientes[pendientes['estado'] == 'PARCIAL'])
    st.metric("OCs Parciales", ocs_parciales)

st.divider()

# Tabla de clientes
st.subheader("🏥 Estado de Clientes")

if not clientes.empty:
    display_df = clientes.copy()
    display_df['disponible_real'] = display_df['disponible'] - display_df['pendientes_total']
    
    # Formatear valores
    for col in ['cupo_sugerido', 'saldo_actual', 'disponible', 'pendientes_total', 'disponible_real']:
        display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "$0")
    
    st.dataframe(
        display_df[['nit', 'nombre', 'cupo_sugerido', 'saldo_actual', 
                   'pendientes_total', 'disponible_real']],
        column_config={
            "nit": "NIT",
            "nombre": "Cliente",
            "cupo_sugerido": "Cupo Sugerido",
            "saldo_actual": "Saldo Actual",
            "pendientes_total": "Pendientes",
            "disponible_real": "Disponible Real"
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("No hay clientes registrados")
