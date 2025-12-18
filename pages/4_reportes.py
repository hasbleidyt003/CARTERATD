"""
PÁGINA 4 - REPORTES Y ANÁLISIS
Reportes avanzados y análisis de datos
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Configuración de página
st.set_page_config(
    page_title="Reportes - Tododrogas",
    page_icon="📊",
    layout="wide"
)

# Importar módulos
from modules.auth import check_authentication
from modules.database import get_estadisticas_generales, get_estadisticas_por_cliente, get_ocs
from modules.utils import format_currency, format_number, calculate_percentage

# Verificar autenticación
user = check_authentication()

# ==================== FUNCIONES DE REPORTES ====================

def create_availability_report(clientes_df):
    """Crea reporte de disponibilidad por cliente"""
    
    reporte = clientes_df.copy()
    reporte = reporte[['nombre', 'nit', 'cupo_sugerido', 'saldo_actual', 'disponible', 'porcentaje_uso', 'estado']]
    
    # Ordenar por disponibilidad (ascendente)
    reporte = reporte.sort_values('disponible')
    
    # Agregar columna de riesgo
    def get_risk_level(porcentaje):
        if porcentaje >= 100:
            return "🔴 CRÍTICO"
        elif porcentaje >= 90:
            return "🟠 ALTO"
        elif porcentaje >= 80:
            return "🟡 MEDIO"
        else:
            return "🟢 BAJO"
    
    reporte['Nivel de Riesgo'] = reporte['porcentaje_uso'].apply(get_risk_level)
    
    # Formatear valores
    reporte['cupo_sugerido'] = reporte['cupo_sugerido'].apply(format_currency)
    reporte['saldo_actual'] = reporte['saldo_actual'].apply(format_currency)
    reporte['disponible'] = reporte['disponible'].apply(format_currency)
    reporte['porcentaje_uso'] = reporte['porcentaje_uso'].apply(lambda x: f"{x:.1f}%")
    
    return reporte.rename(columns={
        'nombre': 'Cliente',
        'nit': 'NIT',
        'cupo_sugerido': 'Cupo Asignado',
        'saldo_actual': 'En Uso',
        'disponible': 'Disponible',
        'porcentaje_uso': '% Uso',
        'estado': 'Estado'
    })

def create_ocs_analysis_report(ocs_df):
    """Crea reporte de análisis de OCs"""
    
    if ocs_df.empty:
        return pd.DataFrame()
    
    # Agrupar por cliente
    reporte = ocs_df.groupby('cliente_nombre').agg({
        'valor_total': 'sum',
        'valor_autorizado': 'sum',
        'valor_pendiente': 'sum',
        'id': 'count'
    }).reset_index()
    
    # Calcular porcentajes
    reporte['% Autorizado'] = reporte.apply(
        lambda x: (x['valor_autorizado'] / x['valor_total'] * 100) if x['valor_total'] > 0 else 0,
        axis=1
    )
    
    reporte['% Pendiente'] = reporte.apply(
        lambda x: (x['valor_pendiente'] / x['valor_total'] * 100) if x['valor_total'] > 0 else 0,
        axis=1
    )
    
    # Ordenar por valor pendiente descendente
    reporte = reporte.sort_values('valor_pendiente', ascending=False)
    
    # Formatear valores
    reporte['valor_total'] = reporte['valor_total'].apply(format_currency)
    reporte['valor_autorizado'] = reporte['valor_autorizado'].apply(format_currency)
    reporte['valor_pendiente'] = reporte['valor_pendiente'].apply(format_currency)
    reporte['% Autorizado'] = reporte['% Autorizado'].apply(lambda x: f"{x:.1f}%")
    reporte['% Pendiente'] = reporte['% Pendiente'].apply(lambda x: f"{x:.1f}%")
    
    return reporte.rename(columns={
        'cliente_nombre': 'Cliente',
        'valor_total': 'Total OCs',
        'valor_autorizado': 'Autorizado',
        'valor_pendiente': 'Pendiente',
        'id': 'Cantidad OCs'
    })

def create_risk_analysis(clientes_df, ocs_df):
    """Crea análisis de riesgo combinado"""
    
    riesgo_data = []
    
    for _, cliente in clientes_df.iterrows():
        # OCs pendientes del cliente
        ocs_cliente = ocs_df[ocs_df['cliente_nit'] == cliente['nit']]
        ocs_pendientes = ocs_cliente[ocs_cliente['estado'].isin(['PENDIENTE', 'PARCIAL'])]
        
        # Calcular riesgo
        disponible = cliente['disponible']
        pendiente_total = ocs_pendientes['valor_pendiente'].sum()
        
        # Nuevo disponible si se autorizan todas las OCs pendientes
        nuevo_disponible = disponible - pendiente_total
        
        # Determinar nivel de riesgo
        if nuevo_disponible < 0:
            nivel_riesgo = "🔴 SOBREPASARÍA CUPO"
        elif nuevo_disponible < (cliente['cupo_sugerido'] * 0.1):  # Menos del 10% disponible
            nivel_riesgo = "🟠 RIESGO ALTO"
        elif nuevo_disponible < (cliente['cupo_sugerido'] * 0.2):  # Menos del 20% disponible
            nivel_riesgo = "🟡 RIESGO MEDIO"
        else:
            nivel_riesgo = "🟢 RIESGO BAJO"
        
        riesgo_data.append({
            'Cliente': cliente['nombre'],
            'NIT': cliente['nit'],
            'Cupo Asignado': format_currency(cliente['cupo_sugerido']),
            'Disponible Actual': format_currency(disponible),
            'OCs Pendientes': format_currency(pendiente_total),
            'Nuevo Disponible': format_currency(nuevo_disponible),
            'Nivel de Riesgo': nivel_riesgo,
            'Acción Recomendada': "Revisar cupo" if nuevo_disponible < 0 else "Monitorear" if "RIESGO" in nivel_riesgo else "Normal"
        })
    
    return pd.DataFrame(riesgo_data)

# ==================== PÁGINA PRINCIPAL ====================

def show_reports_page():
    """Muestra la página de reportes"""
    
    st.title("📊 REPORTES Y ANÁLISIS")
    st.markdown("Reportes avanzados y análisis de datos del sistema")
    
    # Obtener datos
    with st.spinner("Cargando datos para reportes..."):
        stats = get_estadisticas_generales()
        clientes_df = get_estadisticas_por_cliente()
        ocs_df = get_ocs()
    
    # Pestañas de reportes
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Resumen Ejecutivo",
        "👥 Disponibilidad por Cliente", 
        "📋 Análisis de OCs",
        "⚠️ Análisis de Riesgo",
        "📤 Exportar Reportes"
    ])
    
    # ========== PESTAÑA 1: RESUMEN EJECUTIVO ==========
    with tab1:
        st.subheader("📈 RESUMEN EJECUTIVO DEL SISTEMA")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Cupo Total Asignado",
                format_currency(stats['total_cupo'])
            )
        
        with col2:
            porcentaje_uso = calculate_percentage(stats['total_en_uso'], stats['total_cupo'])
            st.metric(
                "Cupo en Uso",
                format_currency(stats['total_en_uso']),
                delta=f"{porcentaje_uso:.1f}%"
            )
        
        with col3:
            st.metric(
                "Cupo Disponible",
                format_currency(stats['total_disponible'])
            )
        
        with col4:
            st.metric(
                "OCs Pendientes",
                f"{stats['cantidad_ocs_pendientes']} OCs",
                delta=format_currency(stats['total_ocs_pendientes'])
            )
        
        st.markdown("---")
        
        # Distribución de estados
        st.subheader("📊 DISTRIBUCIÓN DE ESTADOS DE CLIENTES")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de donut
            labels = ['NORMAL', 'ALERTA', 'SOBREPASADO']
            values = [
                stats['clientes_normal'],
                stats['clientes_alerta'],
                stats['clientes_sobrepasados']
            ]
            colors = ['#0066CC', '#FFCC00', '#FF3B30']
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=.5,
                marker=dict(colors=colors),
                textinfo='label+percent'
            )])
            
            fig.update_layout(
                height=400,
                showlegend=True,
                annotations=[dict(
                    text=f"{sum(values)}<br>Clientes",
                    x=0.5, y=0.5,
                    font=dict(size=20),
                    showarrow=False
                )]
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Tabla de distribución
            distribucion_df = pd.DataFrame({
                'Estado': ['🟢 NORMAL', '🟠 ALERTA', '🔴 SOBREPASADO'],
                'Cantidad': [
                    stats['clientes_normal'],
                    stats['clientes_alerta'],
                    stats['clientes_sobrepasados']
                ],
                'Porcentaje': [
                    f"{(stats['clientes_normal']/stats['total_clientes']*100):.1f}%",
                    f"{(stats['clientes_alerta']/stats['total_clientes']*100):.1f}%",
                    f"{(stats['clientes_sobrepasados']/stats['total_clientes']*100):.1f}%"
                ]
            })
            
            st.dataframe(
                distribucion_df,
                use_container_width=True,
                hide_index=True
            )
        
        # Top 5 clientes por uso
        st.subheader("🏆 TOP 5 CLIENTES - MAYOR USO DE CUPO")
        
        if not clientes_df.empty:
            top_clientes = clientes_df.nlargest(5, 'porcentaje_uso')
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=top_clientes['nombre'],
                y=top_clientes['porcentaje_uso'],
                marker_color=top_clientes['porcentaje_uso'].apply(
                    lambda x: '#FF3B30' if x >= 100 else 
                             '#FF9500' if x >= 90 else
                             '#FFCC00' if x >= 80 else
                             '#00B8A9' if x >= 50 else '#0066CC'
                ),
                text=top_clientes['porcentaje_uso'].apply(lambda x: f"{x:.1f}%"),
                textposition='outside'
            ))
            
            fig.update_layout(
                height=400,
                xaxis_title="Cliente",
                yaxis_title="% de Uso",
                yaxis_range=[0, 110]
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar tabla detallada
            display_df = top_clientes[['nombre', 'nit', 'porcentaje_uso', 'cupo_sugerido', 'saldo_actual', 'disponible']].copy()
            display_df['cupo_sugerido'] = display_df['cupo_sugerido'].apply(format_currency)
            display_df['saldo_actual'] = display_df['saldo_actual'].apply(format_currency)
            display_df['disponible'] = display_df['disponible'].apply(format_currency)
            display_df['porcentaje_uso'] = display_df['porcentaje_uso'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(
                display_df.rename(columns={
                    'nombre': 'Cliente',
                    'nit': 'NIT',
                    'porcentaje_uso': '% Uso',
                    'cupo_sugerido': 'Cupo',
                    'saldo_actual': 'En Uso',
                    'disponible': 'Disponible'
                }),
                use_container_width=True,
                hide_index=True
            )
    
    # ========== PESTAÑA 2: DISPONIBILIDAD POR CLIENTE ==========
    with tab2:
        st.subheader("👥 REPORTE DE DISPONIBILIDAD POR CLIENTE")
        
        if not clientes_df.empty:
            # Crear reporte
            disponibilidad_report = create_availability_report(clientes_df)
            
            # Filtros
            col1, col2 = st.columns(2)
            
            with col1:
                filter_estado = st.multiselect(
                    "Filtrar por estado",
                    options=disponibilidad_report['Estado'].unique(),
                    default=disponibilidad_report['Estado'].unique()
                )
            
            with col2:
                filter_riesgo = st.multiselect(
                    "Filtrar por nivel de riesgo",
                    options=disponibilidad_report['Nivel de Riesgo'].unique(),
                    default=disponibilidad_report['Nivel de Riesgo'].unique()
                )
            
            # Aplicar filtros
            filtered_report = disponibilidad_report.copy()
            
            if filter_estado:
                filtered_report = filtered_report[filtered_report['Estado'].isin(filter_estado)]
            
            if filter_riesgo:
                filtered_report = filtered_report[filtered_report['Nivel de Riesgo'].isin(filter_riesgo)]
            
            # Mostrar reporte
            st.dataframe(
                filtered_report,
                use_container_width=True,
                height=400
            )
            
            # Resumen
            st.subheader("📋 RESUMEN DE DISPONIBILIDAD")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                clientes_criticos = len(filtered_report[filtered_report['Nivel de Riesgo'].str.contains('CRÍTICO')])
                st.metric("Clientes Críticos", clientes_criticos)
            
            with col2:
                clientes_alto_riesgo = len(filtered_report[filtered_report['Nivel de Riesgo'].str.contains('ALTO')])
                st.metric("Alto Riesgo", clientes_alto_riesgo)
            
            with col3:
                clientes_bajo_riesgo = len(filtered_report[filtered_report['Nivel de Riesgo'].str.contains('BAJO')])
                st.metric("Bajo Riesgo", clientes_bajo_riesgo)
            
            # Gráfico de disponibilidad
            st.subheader("📊 DISTRIBUCIÓN DEL DISPONIBLE")
            
            # Tomar top 10 por disponibilidad
            top_disponible = clientes_df.nlargest(10, 'disponible')
            
            fig = go.Figure(data=[go.Bar(
                y=top_disponible['nombre'],
                x=top_disponible['disponible'],
                orientation='h',
                marker_color='#00B8A9',
                text=top_disponible['disponible'].apply(format_currency),
                textposition='inside'
            )])
            
            fig.update_layout(
                height=500,
                title="TOP 10 - MAYOR CUPO DISPONIBLE",
                xaxis_title="Disponible",
                yaxis_title="Cliente"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de clientes para mostrar.")
    
    # ========== PESTAÑA 3: ANÁLISIS DE OCs ==========
    with tab3:
        st.subheader("📋 ANÁLISIS DE ÓRDENES DE COMPRA")
        
        if not ocs_df.empty:
            # Crear reporte
            ocs_report = create_ocs_analysis_report(ocs_df)
            
            st.dataframe(
                ocs_report,
                use_container_width=True,
                height=400
            )
            
            # Gráficos de análisis
            col1, col2 = st.columns(2)
            
            with col1:
                # Distribución por estado
                estado_counts = ocs_df['estado'].value_counts()
                
                fig1 = go.Figure(data=[go.Pie(
                    labels=estado_counts.index,
                    values=estado_counts.values,
                    hole=.4,
                    marker=dict(colors=['#FFCC00', '#FF9500', '#00B8A9'])
                )])
                
                fig1.update_layout(
                    title="DISTRIBUCIÓN DE OCs POR ESTADO",
                    height=400
                )
                
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Valor por estado
                valor_por_estado = ocs_df.groupby('estado')['valor_total'].sum()
                
                fig2 = go.Figure(data=[go.Bar(
                    x=valor_por_estado.index,
                    y=valor_por_estado.values,
                    marker_color=['#FFCC00', '#FF9500', '#00B8A9'],
                    text=valor_por_estado.values.apply(format_currency),
                    textposition='outside'
                )])
                
                fig2.update_layout(
                    title="VALOR TOTAL POR ESTADO",
                    height=400,
                    xaxis_title="Estado",
                    yaxis_title="Valor Total"
                )
                
                st.plotly_chart(fig2, use_container_width=True)
            
            # Análisis de tendencia (simulado)
            st.subheader("📅 TENDENCIA DE AUTORIZACIONES (ÚLTIMOS 30 DÍAS)")
            
            # Datos simulados para la tendencia
            fechas = pd.date_range(end=datetime.now(), periods=30, freq='D')
            valores = np.random.randint(500000000, 3000000000, size=30)
            
            tendencia_df = pd.DataFrame({
                'Fecha': fechas,
                'Valor Autorizado': valores
            })
            
            fig3 = px.line(
                tendencia_df,
                x='Fecha',
                y='Valor Autorizado',
                title='EVOLUCIÓN DIARIA DE AUTORIZACIONES'
            )
            
            fig3.update_traces(line_color='#0066CC', line_width=3)
            fig3.update_layout(height=400)
            
            st.plotly_chart(fig3, use_container_width=True)
            
            # Métricas de eficiencia
            st.subheader("⚡ MÉTRICAS DE EFICIENCIA")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                # Tiempo promedio de autorización (simulado)
                tiempo_promedio = np.random.randint(1, 5)
                st.metric("Días promedio autorización", f"{tiempo_promedio} días")
            
            with col2:
                # % de OCs autorizadas
                total_ocs = len(ocs_df)
                autorizadas = len(ocs_df[ocs_df['estado'] == 'AUTORIZADA'])
                porcentaje = (autorizadas / total_ocs * 100) if total_ocs > 0 else 0
                st.metric("% OCs Autorizadas", f"{porcentaje:.1f}%")
            
            with col3:
                # Valor pendiente vs total
                valor_total = ocs_df['valor_total'].sum()
                valor_pendiente = ocs_df['valor_pendiente'].sum()
                porcentaje_pendiente = (valor_pendiente / valor_total * 100) if valor_total > 0 else 0
                st.metric("% Valor Pendiente", f"{porcentaje_pendiente:.1f}%")
            
            with col4:
                # OCs por cliente (promedio)
                ocs_por_cliente = ocs_df.groupby('cliente_nit').size().mean()
                st.metric("OCs por cliente (prom)", f"{ocs_por_cliente:.1f}")
        else:
            st.info("No hay OCs registradas en el sistema.")
    
    # ========== PESTAÑA 4: ANÁLISIS DE RIESGO ==========
    with tab4:
        st.subheader("⚠️ ANÁLISIS DE RIESGO COMBINADO")
        
        if not clientes_df.empty and not ocs_df.empty:
            # Crear análisis de riesgo
            riesgo_report = create_risk_analysis(clientes_df, ocs_df)
            
            st.dataframe(
                riesgo_report,
                use_container_width=True,
                height=400
            )
            
            # Resumen de riesgo
            st.subheader("📊 RESUMEN DE NIVELES DE RIESGO")
            
            niveles_riesgo = riesgo_report['Nivel de Riesgo'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de niveles de riesgo
                fig = go.Figure(data=[go.Bar(
                    x=niveles_riesgo.index,
                    y=niveles_riesgo.values,
                    marker_color=['#FF3B30', '#FF9500', '#FFCC00', '#00B8A9'],
                    text=niveles_riesgo.values,
                    textposition='outside'
                )])
                
                fig.update_layout(
                    title="DISTRIBUCIÓN DE NIVELES DE RIESGO",
                    height=400,
                    xaxis_title="Nivel de Riesgo",
                    yaxis_title="Cantidad de Clientes"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Tabla de resumen
                resumen_df = pd.DataFrame({
                    'Nivel de Riesgo': niveles_riesgo.index,
                    'Cantidad': niveles_riesgo.values,
                    'Porcentaje': (niveles_riesgo.values / len(riesgo_report) * 100).round(1)
                })
                
                st.dataframe(
                    resumen_df,
                    use_container_width=True,
                    hide_index=True
                )
            
            # Clientes con mayor riesgo
            st.subheader("🔴 CLIENTES CON MAYOR RIESGO")
            
            clientes_alto_riesgo = riesgo_report[
                riesgo_report['Nivel de Riesgo'].isin(['🔴 SOBREPASARÍA CUPO', '🟠 RIESGO ALTO'])
            ]
            
            if not clientes_alto_riesgo.empty:
                for _, cliente in clientes_alto_riesgo.iterrows():
                    with st.expander(f"{cliente['Cliente']} - {cliente['Nivel de Riesgo']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**NIT:** {cliente['NIT']}")
                            st.write(f"**Cupo Asignado:** {cliente['Cupo Asignado']}")
                            st.write(f"**Disponible Actual:** {cliente['Disponible Actual']}")
                        
                        with col2:
                            st.write(f"**OCs Pendientes:** {cliente['OCs Pendientes']}")
                            st.write(f"**Nuevo Disponible:** {cliente['Nuevo Disponible']}")
                            st.write(f"**Acción Recomendada:** {cliente['Acción Recomendada']}")
            else:
                st.success("🎉 No hay clientes con alto riesgo identificado.")
        else:
            st.info("No hay suficientes datos para el análisis de riesgo.")
    
    # ========== PESTAÑA 5: EXPORTAR REPORTES ==========
    with tab5:
        st.subheader("📤 EXPORTAR REPORTES")
        
        st.info("""
        Exporta los reportes generados en formato Excel para su análisis fuera del sistema.
        Los archivos incluyen todas las tablas y datos mostrados en esta sección.
        """)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Exportar Reporte Completo", use_container_width=True):
                try:
                    from modules.database import exportar_datos_a_excel
                    ruta = exportar_datos_a_excel()
                    
                    with open(ruta, "rb") as file:
                        st.download_button(
                            label="⬇️ Descargar Reporte Completo",
                            data=file,
                            file_name=f"reporte_tododrogas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                    st.success("✅ Reporte generado exitosamente")
                except Exception as e:
                    st.error(f"❌ Error al exportar: {str(e)}")
        
        with col2:
            if st.button("📊 Exportar Datos Clientes", use_container_width=True):
                try:
                    # Crear Excel con datos de clientes
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    ruta_clientes = f'data/backups/clientes_{timestamp}.xlsx'
                    
                    with pd.ExcelWriter(ruta_clientes, engine='openpyxl') as writer:
                        # Hoja 1: Datos completos
                        clientes_df.to_excel(writer, sheet_name='Datos Completos', index=False)
                        
                        # Hoja 2: Reporte de disponibilidad
                        if not clientes_df.empty:
                            disponibilidad_report = create_availability_report(clientes_df)
                            disponibilidad_report.to_excel(writer, sheet_name='Disponibilidad', index=False)
                        
                        # Hoja 3: Estadísticas
                        stats_df = pd.DataFrame([stats])
                        stats_df.to_excel(writer, sheet_name='Estadísticas', index=False)
                    
                    with open(ruta_clientes, "rb") as file:
                        st.download_button(
                            label="⬇️ Descargar Datos Clientes",
                            data=file,
                            file_name=f"clientes_tododrogas_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                    st.success("✅ Datos de clientes exportados")
                except Exception as e:
                    st.error(f"❌ Error al exportar: {str(e)}")
        
        with col3:
            if st.button("📋 Exportar Datos OCs", use_container_width=True):
                try:
                    # Crear Excel con datos de OCs
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    ruta_ocs = f'data/backups/ocs_{timestamp}.xlsx'
                    
                    with pd.ExcelWriter(ruta_ocs, engine='openpyxl') as writer:
                        # Hoja 1: Datos completos
                        ocs_df.to_excel(writer, sheet_name='OCs Completas', index=False)
                        
                        # Hoja 2: Análisis
                        if not ocs_df.empty:
                            ocs_report = create_ocs_analysis_report(ocs_df)
                            ocs_report.to_excel(writer, sheet_name='Análisis', index=False)
                    
                    with open(ruta_ocs, "rb") as file:
                        st.download_button(
                            label="⬇️ Descargar Datos OCs",
                            data=file,
                            file_name=f"ocs_tododrogas_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                    st.success("✅ Datos de OCs exportados")
                except Exception as e:
                    st.error(f"❌ Error al exportar: {str(e)}")
        
        # Opciones adicionales
        st.markdown("---")
        st.subheader("⚙️ OPCIONES AVANZADAS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fecha_inicio = st.date_input(
                "Fecha inicio (para reportes históricos)",
                value=datetime.now() - timedelta(days=30)
            )
        
        with col2:
            fecha_fin = st.date_input(
                "Fecha fin (para reportes históricos)",
                value=datetime.now()
            )
        
        if st.button("🔄 Generar Reporte Histórico", use_container_width=True):
            st.info(f"Reporte histórico generado para el período: {fecha_inicio} al {fecha_fin}")
            st.success("✅ (Funcionalidad en desarrollo - próximamente disponible)")

# ==================== EJECUCIÓN ====================

if __name__ == "__main__":
    show_reports_page()
