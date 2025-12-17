"""
Dashboard principal del Sistema de Gestión de Cartera TD
Versión completa con gráficos y estadísticas
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from modules.database import (
    get_estadisticas_generales,
    get_estadisticas_por_cliente,
    get_ocs_pendientes,
    get_movimientos_recientes,
    get_historico_pagos
)

def show():
    """Función principal del dashboard"""
    st.header("📊 Dashboard - Resumen General")
    
    # Cargar datos con spinners
    with st.spinner("Cargando estadísticas..."):
        try:
            stats = get_estadisticas_generales()
            clientes_stats = get_estadisticas_por_cliente()
            ocs_pendientes = get_ocs_pendientes()
            movimientos = get_movimientos_recientes(limit=10)
            historico_pagos = get_historico_pagos(dias=30)
        except Exception as e:
            st.error(f"❌ Error al cargar datos: {str(e)}")
            return
    
    # ========== MÉTRICAS PRINCIPALES ==========
    st.subheader("📈 Métricas Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Cupo",
            value=f"${stats['total_cupo_sugerido']:,.0f}",
            delta=f"${stats['total_disponible']:,.0f} disponible"
        )
    
    with col2:
        st.metric(
            label="Saldo Actual",
            value=f"${stats['total_saldo_actual']:,.0f}",
            delta=f"${stats['total_cartera_vencida']:,.0f} vencido"
        )
    
    with col3:
        st.metric(
            label="OCs Pendientes",
            value=f"${stats['total_ocs_pendientes']:,.0f}",
            delta=f"{len(ocs_pendientes)} OCs"
        )
    
    with col4:
        porcentaje_uso = (stats['total_saldo_actual'] / stats['total_cupo_sugerido'] * 100) if stats['total_cupo_sugerido'] > 0 else 0
        st.metric(
            label="% Uso Total",
            value=f"{porcentaje_uso:.1f}%",
            delta=f"{stats['clientes_sobrepasados'] + stats['clientes_alerta']} clientes críticos"
        )
    
    st.divider()
    
    # ========== GRÁFICOS PRINCIPALES ==========
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📊 Distribución por Cliente")
        
        if not clientes_stats.empty:
            # Gráfico de barras de saldo por cliente
            fig1 = px.bar(
                clientes_stats.head(10),
                x='nombre',
                y='saldo_actual',
                color='estado',
                title='Top 10 Clientes por Saldo',
                labels={'nombre': 'Cliente', 'saldo_actual': 'Saldo Actual', 'estado': 'Estado'},
                color_discrete_map={
                    'NORMAL': '#2ecc71',
                    'ALERTA': '#f39c12',
                    'SOBREPASADO': '#e74c3c'
                }
            )
            fig1.update_layout(
                xaxis_tickangle=-45,
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No hay datos de clientes disponibles")
    
    with col_chart2:
        st.subheader("📈 Estado de Cupos")
        
        if not clientes_stats.empty:
            # Gráfico de dona para estados
            estados_counts = clientes_stats['estado'].value_counts()
            
            fig2 = go.Figure(data=[
                go.Pie(
                    labels=estados_counts.index,
                    values=estados_counts.values,
                    hole=.4,
                    marker_colors=['#e74c3c', '#f39c12', '#2ecc71'],
                    textinfo='label+percent'
                )
            ])
            fig2.update_layout(
                title_text="Clientes por Estado",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No hay datos de estados disponibles")
    
    st.divider()
    
    # ========== TABLAS DE DETALLE ==========
    col_table1, col_table2 = st.columns(2)
    
    with col_table1:
        st.subheader("📋 Clientes en Estado Crítico")
        
        if not clientes_stats.empty:
            criticos = clientes_stats[
                (clientes_stats['estado'] == 'SOBREPASADO') | 
                (clientes_stats['estado'] == 'ALERTA')
            ]
            
            if not criticos.empty:
                # Preparar datos para mostrar
                df_criticos = criticos[['nombre', 'saldo_actual', 'cupo_sugerido', 'estado', 'porcentaje_uso']].copy()
                df_criticos['uso'] = df_criticos['porcentaje_uso'].apply(lambda x: f"{x:.1f}%")
                df_criticos['saldo'] = df_criticos['saldo_actual'].apply(lambda x: f"${x:,.0f}")
                df_criticos['cupo'] = df_criticos['cupo_sugerido'].apply(lambda x: f"${x:,.0f}")
                
                st.dataframe(
                    df_criticos[['nombre', 'saldo', 'cupo', 'uso', 'estado']].rename(columns={
                        'nombre': 'Cliente',
                        'saldo': 'Saldo',
                        'cupo': 'Cupo',
                        'uso': '% Uso',
                        'estado': 'Estado'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("✅ Todos los clientes están en estado NORMAL")
        else:
            st.info("No hay datos de clientes disponibles")
    
    with col_table2:
        st.subheader("📄 Órdenes de Compra Pendientes")
        
        if not ocs_pendientes.empty:
            df_ocs = ocs_pendientes[['numero_oc', 'cliente_nombre', 'valor_total', 'valor_pendiente', 'estado']].copy()
            df_ocs['valor_total'] = df_ocs['valor_total'].apply(lambda x: f"${x:,.0f}")
            df_ocs['valor_pendiente'] = df_ocs['valor_pendiente'].apply(lambda x: f"${x:,.0f}")
            
            st.dataframe(
                df_ocs.rename(columns={
                    'numero_oc': 'N° OC',
                    'cliente_nombre': 'Cliente',
                    'valor_total': 'Valor Total',
                    'valor_pendiente': 'Pendiente',
                    'estado': 'Estado'
                }),
                use_container_width=True,
                hide_index=True,
                column_config={
                    'N° OC': st.column_config.TextColumn(width="medium"),
                    'Cliente': st.column_config.TextColumn(width="large"),
                    'Valor Total': st.column_config.TextColumn(width="small"),
                    'Pendiente': st.column_config.TextColumn(width="small"),
                    'Estado': st.column_config.TextColumn(width="small")
                }
            )
        else:
            st.success("✅ No hay OCs pendientes")
    
    st.divider()
    
    # ========== ACTIVIDAD RECIENTE ==========
    st.subheader("🔄 Actividad Reciente")
    
    col_act1, col_act2 = st.columns(2)
    
    with col_act1:
        st.markdown("##### Últimos Movimientos")
        
        if not movimientos.empty:
            for _, mov in movimientos.iterrows():
                with st.container():
                    col_m1, col_m2, col_m3 = st.columns([3, 2, 1])
                    
                    with col_m1:
                        st.write(f"**{mov['cliente_nombre']}**")
                        if mov['descripcion']:
                            st.caption(mov['descripcion'])
                    
                    with col_m2:
                        valor_color = "green" if mov['tipo'] == 'PAGO' else "orange"
                        st.markdown(f"<span style='color:{valor_color}'><strong>{mov['tipo']}: ${mov['valor']:,.0f}</strong></span>", unsafe_allow_html=True)
                    
                    with col_m3:
                        try:
                            fecha = pd.to_datetime(mov['fecha_movimiento']).strftime('%d/%m')
                            st.caption(fecha)
                        except:
                            st.caption(mov['fecha_movimiento'])
                    
                    st.divider()
        else:
            st.info("No hay movimientos recientes")
    
    with col_act2:
        st.markdown("##### Resumen por Estado")
        
        if not clientes_stats.empty:
            # Crear métricas de resumen
            col_s1, col_s2, col_s3 = st.columns(3)
            
            with col_s1:
                st.metric(
                    "Normal",
                    len(clientes_stats[clientes_stats['estado'] == 'NORMAL']),
                    delta_color="off"
                )
            
            with col_s2:
                st.metric(
                    "Alerta",
                    len(clientes_stats[clientes_stats['estado'] == 'ALERTA']),
                    delta_color="off"
                )
            
            with col_s3:
                st.metric(
                    "Sobrepasado",
                    len(clientes_stats[clientes_stats['estado'] == 'SOBREPASADO']),
                    delta_color="off"
                )
            
            # Resumen de pagos del mes
            if 'total_pagado_mes' in stats:
                st.metric(
                    "Total Pagado (Mes)",
                    f"${stats['total_pagado_mes']:,.0f}",
                    delta_color="off"
                )
            
            # OCs por estado
            if not ocs_pendientes.empty:
                estados_oc = ocs_pendientes['estado'].value_counts()
                st.markdown("##### OCs por Estado")
                
                for estado, count in estados_oc.items():
                    st.write(f"**{estado}:** {count}")
        else:
            st.info("No hay datos de resumen disponibles")
    
    # ========== BOTONES DE ACCIÓN RÁPIDA ==========
    st.divider()
    st.subheader("⚡ Acciones Rápidas")
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("👥 Ver Todos los Clientes", use_container_width=True):
            st.switch_page("pages/2_clientes.py")
    
    with col_btn2:
        if st.button("📋 Ver Todas las OCs", use_container_width=True):
            st.switch_page("pages/3_ocs.py")
    
    with col_btn3:
        if st.button("📊 Generar Reporte", use_container_width=True):
            st.switch_page("pages/4_mantenimiento.py")

# Para pruebas directas
if __name__ == "__main__":
    st.set_page_config(page_title="Dashboard", layout="wide")
    show()
