import streamlit as st
import pandas as pd
from modules.database import get_clientes, get_ocs_pendientes

def show():
    st.header("📊 Dashboard de Control")
    
    # Obtener datos
    clientes = get_clientes()
    ocs_pendientes = get_ocs_pendientes()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cupo = clientes['cupo_sugerido'].sum()
        st.metric("Cupo Total", f"${total_cupo:,.0f}")
    
    with col2:
        total_pendientes = ocs_pendientes['valor_pendiente'].sum()
        st.metric("Pendientes Total", f"${total_pendientes:,.0f}")
    
    with col3:
        clientes_alerta = len(clientes[clientes['disponible'] < 0])
        st.metric("Clientes en Alerta", clientes_alerta)
    
    with col4:
        ocs_parciales = len(ocs_pendientes[ocs_pendientes['estado'] == 'PARCIAL'])
        st.metric("OCs Parciales", ocs_parciales)
    
    st.divider()
    
    # Tabla de clientes con alertas
    st.subheader("🏥 Estado de Clientes")
    
    # Crear DataFrame para mostrar
    display_df = clientes.copy()
    display_df['disponible_real'] = display_df['disponible'] - display_df['pendientes_total']
    
    # Formatear valores
    for col in ['cupo_sugerido', 'saldo_actual', 'disponible', 'pendientes_total', 'disponible_real']:
        display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
    
    # Añadir colores según estado
    def color_disponible(val):
        try:
            num = float(val.replace('$', '').replace(',', ''))
            if num < 0:
                return 'color: #ff6b6b; font-weight: bold'
            elif num < 100000000:  # Menos de 100M
                return 'color: #feca57; font-weight: bold'
            else:
                return 'color: #1dd1a1'
        except:
            return ''
    
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
        hide_index=True
    )
