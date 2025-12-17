import streamlit as st
import pandas as pd
from modules.database import get_clientes, get_ocs_pendientes
import plotly.express as px

def show():
    st.header("📊 Dashboard de Control - Cupos Medicamentos")
    
    # Obtener datos
    clientes = get_clientes()
    ocs_pendientes = get_ocs_pendientes()
    
    # Métricas principales (actualizadas)
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
        st.metric("Clientes en Alerta/Crítico", f"{clientes_alerta}/{clientes_sobrepasado}")
    
    with col4:
        total_pendientes = ocs_pendientes['valor_pendiente'].sum()
        st.metric("OCs Pendientes Total", f"${total_pendientes:,.0f}")
    
    st.divider()
    
    # Tabla de clientes con colores por estado
    st.subheader("🏥 Estado Actual de Clientes")
    
    # Formatear DataFrame para mostrar
    display_df = clientes.copy()
    
    # Calcular disponibilidad real
    display_df['disponibilidad_real'] = display_df['cupo_sugerido'] - display_df['saldo_actual'] - display_df['cartera_vencida']
    
    # Función para aplicar colores según estado
    def color_row(row):
        if row['estado'] == 'SOBREPASADO':
            return ['background-color: #ff6b6b; color: white'] * len(row)
        elif row['estado'] == 'ALERTA':
            return ['background-color: #ffeaa7'] * len(row)
        else:
            return ['background-color: #d1f7c4'] * len(row)
    
    # Columnas a mostrar
    columns_to_show = ['nit', 'nombre', 'cupo_sugerido', 'saldo_actual', 
                      'cartera_vencida', 'disponibilidad_real', 'porcentaje_uso', 'estado']
    
    # Crear DataFrame estilizado
    styled_df = display_df[columns_to_show].copy()
    
    # Formatear valores monetarios
    for col in ['cupo_sugerido', 'saldo_actual', 'cartera_vencida', 'disponibilidad_real']:
        styled_df[col] = styled_df[col].apply(lambda x: f"${x:,.0f}")
    
    styled_df['porcentaje_uso'] = styled_df['porcentaje_uso'].apply(lambda x: f"{x}%")
    
    # Aplicar estilos
    styled_df = styled_df.style.apply(color_row, axis=1)
    
    st.dataframe(
        styled_df,
        column_config={
            "nit": "NIT",
            "nombre": "Cliente",
            "cupo_sugerido": "Cupo Sugerido",
            "saldo_actual": "Saldo Actual",
            "cartera_vencida": "Cartera Vencida",
            "disponibilidad_real": "Disponible Real",
            "porcentaje_uso": "% Uso",
            "estado": "Estado"
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Gráfico de barras - Cupo vs Saldo
    st.divider()
    st.subheader("📈 Comparativa Cupo vs Saldo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.bar(
            display_df.nlargest(10, 'saldo_actual'),
            x='nombre',
            y=['cupo_sugerido', 'saldo_actual'],
            title='Top 10 - Cupo vs Saldo',
            labels={'value': 'Valor ($)', 'variable': 'Tipo'},
            barmode='group'
        )
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Gráfico de pastel - Estados
        estado_counts = display_df['estado'].value_counts().reset_index()
        estado_counts.columns = ['estado', 'cantidad']
        
        fig2 = px.pie(
            estado_counts,
            values='cantidad',
            names='estado',
            title='Distribución por Estado',
            color='estado',
            color_discrete_map={
                'NORMAL': '#2ecc71',
                'ALERTA': '#f39c12', 
                'SOBREPASADO': '#e74c3c'
            }
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Sección de resumen rápido
    st.divider()
    st.subheader("🔔 Alertas y Acciones Prioritarias")
    
    # Clientes sobrepasados
    sobrepasados = display_df[display_df['estado'] == 'SOBREPASADO']
    if not sobrepasados.empty:
        st.warning("🚨 **Clientes con Cupo Sobrepasado:**")
        for _, cliente in sobrepasados.iterrows():
            st.error(f"**{cliente['nombre']}** - Sobrepasa en: ${cliente['disponibilidad_real']*-1:,.0f}")
    
    # Clientes en alerta
    alertas = display_df[display_df['estado'] == 'ALERTA']
    if not alertas.empty:
        st.warning("⚠️ **Clientes en Estado de Alerta (80%+ uso):**")
        for _, cliente in alertas.iterrows():
            st.warning(f"**{cliente['nombre']}** - Uso: {cliente['porcentaje_uso']}")
