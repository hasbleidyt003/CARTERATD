# pages/1_dashboard.py - VERSIÓN SIN PLOTLY
import streamlit as st
import pandas as pd
from modules.database import get_clientes, get_ocs_pendientes

def show():
    st.header("📊 Dashboard de Control - Cupos Medicamentos")
    
    # Obtener datos
    clientes = get_clientes()
    ocs_pendientes = get_ocs_pendientes()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cupo_sugerido = clientes['cupo_sugerido'].sum()
        st.metric("Cupo Sugerido Total", f"${total_cupo_sugerido:,.0f}")
    
    with col2:
        total_saldo = clientes['saldo_actual'].sum()
        st.metric("Saldo Total Clientes", f"${total_saldo:,.0f}")
    
    with col3:
        clientes_alerta = len(clientes[clientes['estado'] == 'ALERTA'])
        clientes_sobrepasado = len(clientes[clientes['estado'] == 'SOBREPASADO'])
        st.metric("Clientes Críticos", f"{clientes_alerta}/{clientes_sobrepasado}")
    
    with col4:
        total_pendientes = ocs_pendientes['valor_pendiente'].sum() if not ocs_pendientes.empty else 0
        st.metric("OCs Pendientes", f"${total_pendientes:,.0f}")
    
    st.divider()
    
    # Tabla principal de clientes
    st.subheader("🏥 Estado de Clientes")
    
    if not clientes.empty:
        # Preparar datos para mostrar
        display_df = clientes.copy()
        
        # Formatear columnas monetarias
        for col in ['cupo_sugerido', 'saldo_actual', 'cartera_vencida']:
            display_df[f'{col}_fmt'] = display_df[col].apply(lambda x: f"${x:,.0f}")
        
        # Calcular disponible
        display_df['disponible_real'] = display_df['cupo_sugerido'] - display_df['saldo_actual'] - display_df['cartera_vencida']
        display_df['disponible_fmt'] = display_df['disponible_real'].apply(
            lambda x: f"${x:,.0f}" if x >= 0 else f"(${-x:,.0f})"
        )
        
        # Crear tabla con colores
        st.dataframe(
            display_df[[
                'nit', 'nombre', 'cupo_sugerido_fmt', 'saldo_actual_fmt',
                'cartera_vencida_fmt', 'disponible_fmt', 'porcentaje_uso', 'estado'
            ]],
            column_config={
                "nit": "NIT",
                "nombre": "Cliente",
                "cupo_sugerido_fmt": "Cupo Sugerido",
                "saldo_actual_fmt": "Saldo Actual",
                "cartera_vencida_fmt": "Cartera Vencida",
                "disponible_fmt": "Disponible Real",
                "porcentaje_uso": "% Uso",
                "estado": "Estado"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("No hay clientes registrados en la base de datos")
    
    st.divider()
    
    # Gráficos simples con Streamlit nativo (sin Plotly)
    st.subheader("📊 Resumen Visual")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Distribución por Estado**")
        if not clientes.empty:
            estado_counts = clientes['estado'].value_counts()
            
            # Mostrar como métricas
            for estado, count in estado_counts.items():
                color = {
                    'NORMAL': '🟢',
                    'ALERTA': '🟡',
                    'SOBREPASADO': '🔴'
                }.get(estado, '⚫')
                
                st.metric(f"{color} {estado}", count)
    
    with col2:
        st.write("**Top 5 - Mayor Saldo**")
        if not clientes.empty:
            top_clientes = clientes.nlargest(5, 'saldo_actual')
            for _, cliente in top_clientes.iterrows():
                st.progress(
                    min(cliente['saldo_actual'] / cliente['cupo_sugerido'], 1),
                    text=f"{cliente['nombre'][:20]}...: ${cliente['saldo_actual']:,.0f}"
                )
    
    # Alertas críticas
    st.divider()
    st.subheader("🚨 Alertas Prioritarias")
    
    # Clientes sobrepasados
    sobrepasados = clientes[clientes['estado'] == 'SOBREPASADO']
    if not sobrepasados.empty:
        st.error("**Clientes con Cupo Sobrepasado:**")
        for _, cliente in sobrepasados.iterrows():
            st.write(f"• **{cliente['nombre']}** - Sobrepasa: ${(cliente['cupo_sugerido'] - cliente['saldo_actual'] - cliente['cartera_vencida'])*-1:,.0f}")
    
    # Clientes en alerta
    alertas = clientes[clientes['estado'] == 'ALERTA']
    if not alertas.empty:
        st.warning("**Clientes en Alerta (>80% uso):**")
        for _, cliente in alertas.iterrows():
            st.write(f"• **{cliente['nombre']}** - Uso: {cliente['porcentaje_uso']}%")
