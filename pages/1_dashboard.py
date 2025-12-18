"""
PÁGINA 1 - DASHBOARD PRINCIPAL
Dashboard ejecutivo con estilo Rappi/Oracle Mining
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Configuración de página
st.set_page_config(
    page_title="Dashboard - Tododrogas",
    page_icon="📊",
    layout="wide"
)

# Importar módulos
from modules.auth import check_authentication
from modules.database import get_estadisticas_generales, get_estadisticas_por_cliente
from modules.utils import format_currency, calculate_percentage

# Verificar autenticación
user = check_authentication()

# ==================== ESTILOS CSS ESPECÍFICOS ====================

st.markdown("""
<style>
    /* Dashboard Styles */
    .dashboard-header {
        margin-bottom: 2rem;
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .charts-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .quick-actions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .client-list {
        max-height: 400px;
        overflow-y: auto;
    }
    
    /* Oracle Mining Effects */
    .oracle-header {
        background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .oracle-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #0066CC, #00B8A9);
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    /* Rappi Cards */
    .rappi-metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #E5E7EB;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .rappi-metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0, 102, 204, 0.15);
    }
    
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        display: inline-block;
    }
    
    .metric-title {
        color: #666;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .metric-value {
        color: #1A1A1A;
        font-size: 2rem;
        font-weight: 800;
        line-height: 1;
        margin: 0.5rem 0;
    }
    
    .metric-change {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .metric-change.positive {
        background: rgba(0, 184, 169, 0.1);
        color: #00B8A9;
    }
    
    .metric-change.negative {
        background: rgba(255, 59, 48, 0.1);
        color: #FF3B30;
    }
    
    /* Quick Actions */
    .quick-action-button {
        background: white;
        border: 2px solid #E5E7EB;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .quick-action-button:hover {
        border-color: #0066CC;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 102, 204, 0.1);
    }
    
    .quick-action-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .quick-action-text {
        font-size: 0.9rem;
        font-weight: 600;
        color: #1A1A1A;
    }
</style>
""", unsafe_allow_html=True)

# ==================== FUNCIONES AUXILIARES ====================

def create_oracle_header():
    """Crea el header estilo Oracle Mining"""
    current_time = datetime.now().strftime("%d/%m/%Y • %H:%M")
    
    return f'''
    <div class="oracle-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 1.8rem; font-weight: 800; margin-bottom: 0.5rem;">
                    📊 DASHBOARD EJECUTIVO
                </div>
                <div style="color: rgba(255, 255, 255, 0.8); font-size: 1rem;">
                    Visión en tiempo real de cupos y disponibilidad
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.7);">
                    Actualizado
                </div>
                <div style="font-size: 1.1rem; font-weight: 600;">
                    {current_time}
                </div>
            </div>
        </div>
    </div>
    '''

def create_metric_card(title, value, icon=None, change=None, subtitle=None):
    """Crea una tarjeta de métrica estilo Rappi"""
    
    change_html = ""
    if change is not None:
        change_class = "positive" if change >= 0 else "negative"
        change_symbol = "↗" if change >= 0 else "↘"
        change_html = f'''
        <div class="metric-change {change_class}">
            {change_symbol} {abs(change):.1f}%
        </div>
        '''
    
    subtitle_html = f'<div style="color: #666; font-size: 0.85rem; margin-top: 0.5rem;">{subtitle}</div>' if subtitle else ""
    
    icon_html = f'<div class="metric-icon">{icon}</div>' if icon else ""
    
    return f'''
    <div class="rappi-metric-card">
        {icon_html}
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {subtitle_html}
        {change_html}
    </div>
    '''

def create_quick_action(icon, text, action_key):
    """Crea un botón de acción rápida"""
    return f'''
    <div class="quick-action-button" onclick="handleQuickAction('{action_key}')">
        <div class="quick-action-icon">{icon}</div>
        <div class="quick-action-text">{text}</div>
    </div>
    '''

def create_client_usage_chart(clientes_df):
    """Crea gráfico de uso por cliente"""
    
    # Ordenar por porcentaje de uso descendente
    clientes_df = clientes_df.sort_values('porcentaje_uso', ascending=False)
    
    fig = go.Figure()
    
    # Añadir barras
    fig.add_trace(go.Bar(
        y=clientes_df['nombre'],
        x=clientes_df['porcentaje_uso'],
        orientation='h',
        marker=dict(
            color=clientes_df['porcentaje_uso'].apply(lambda x: '#FF3B30' if x >= 100 else 
                                                     '#FF9500' if x >= 90 else
                                                     '#FFCC00' if x >= 80 else
                                                     '#00B8A9' if x >= 50 else '#0066CC'),
            line=dict(color='white', width=1)
        ),
        text=clientes_df['porcentaje_uso'].apply(lambda x: f'{x:.1f}%'),
        textposition='inside',
        textfont=dict(color='white', size=12, weight='bold')
    ))
    
    fig.update_layout(
        title=dict(
            text='<b>USO DE CUPO POR CLIENTE</b>',
            font=dict(size=16, color='#1A1A1A')
        ),
        height=max(400, len(clientes_df) * 40),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        xaxis=dict(
            title='PORCENTAJE DE USO',
            title_font=dict(size=12, color='#666'),
            range=[0, 110],
            gridcolor='#F0F0F0',
            zerolinecolor='#E5E7EB'
        ),
        yaxis=dict(
            title='CLIENTE',
            title_font=dict(size=12, color='#666'),
            tickfont=dict(size=11),
            gridcolor='#F0F0F0'
        ),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig

def create_status_distribution_chart(stats):
    """Crea gráfico de distribución de estados"""
    
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
        textinfo='label+percent',
        textposition='inside',
        textfont=dict(color='white', size=12, weight='bold')
    )])
    
    fig.update_layout(
        title=dict(
            text='<b>DISTRIBUCIÓN DE ESTADOS</b>',
            font=dict(size=16, color='#1A1A1A')
        ),
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        annotations=[dict(
            text=f"{sum(values)}<br>Clientes",
            x=0.5, y=0.5,
            font=dict(size=20, color='#1A1A1A'),
            showarrow=False
        )]
    )
    
    return fig

def create_availability_chart(clientes_df):
    """Crea gráfico de disponibilidad por cliente"""
    
    # Tomar top 5 por disponibilidad
    top_clientes = clientes_df.nlargest(5, 'disponible')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=top_clientes['nombre'],
        y=top_clientes['disponible'],
        marker_color='#00B8A9',
        text=top_clientes['disponible'].apply(lambda x: format_currency(x)),
        textposition='auto',
        textfont=dict(color='white', size=11, weight='bold')
    ))
    
    fig.update_layout(
        title=dict(
            text='<b>TOP 5 - CUPO DISPONIBLE</b>',
            font=dict(size=16, color='#1A1A1A')
        ),
        height=350,
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        xaxis=dict(
            title='CLIENTE',
            title_font=dict(size=12, color='#666'),
            tickangle=45,
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            title='DISPONIBLE',
            title_font=dict(size=12, color='#666'),
            gridcolor='#F0F0F0'
        )
    )
    
    return fig

# ==================== DASHBOARD PRINCIPAL ====================

def show_dashboard():
    """Muestra el dashboard principal"""
    
    # Obtener datos
    with st.spinner("Cargando datos..."):
        stats = get_estadisticas_generales()
        clientes_df = get_estadisticas_por_cliente()
    
    # Header estilo Oracle Mining
    st.markdown(create_oracle_header(), unsafe_allow_html=True)
    
    # ========== SECCIÓN 1: MÉTRICAS PRINCIPALES ==========
    st.markdown("### 📈 MÉTRICAS CLAVE")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card(
            "CUPO TOTAL",
            format_currency(stats['total_cupo']),
            icon="💰",
            subtitle=f"{stats['total_clientes']} clientes"
        ), unsafe_allow_html=True)
    
    with col2:
        porcentaje_uso = calculate_percentage(stats['total_en_uso'], stats['total_cupo'])
        st.markdown(create_metric_card(
            "EN USO",
            format_currency(stats['total_en_uso']),
            icon="📊",
            change=2.3,  # Simulado
            subtitle=f"{porcentaje_uso:.1f}% del total"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "DISPONIBLE",
            format_currency(stats['total_disponible']),
            icon="✅",
            change=1.8,  # Simulado
            subtitle=f"{(100-porcentaje_uso):.1f}% del total"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "OCs PENDIENTES",
            f"{stats['cantidad_ocs_pendientes']} OCs",
            icon="📋",
            change=25.0,  # Simulado
            subtitle=format_currency(stats['total_ocs_pendientes'])
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== SECCIÓN 2: ACCIONES RÁPIDAS ==========
    st.markdown("### ⚡ ACCIONES RÁPIDAS")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("➕ Nueva OC", use_container_width=True, type="primary"):
            st.switch_page("pages/3_ocs.py")
    
    with col2:
        if st.button("👥 Ver Clientes", use_container_width=True):
            st.switch_page("pages/2_clientes.py")
    
    with col3:
        if st.button("📋 Gestionar OCs", use_container_width=True):
            st.switch_page("pages/3_ocs.py")
    
    with col4:
        if st.button("📊 Ver Reportes", use_container_width=True):
            st.switch_page("pages/4_reportes.py")
    
    with col5:
        if st.button("🔄 Actualizar", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # ========== SECCIÓN 3: GRÁFICOS ==========
    st.markdown("### 📊 VISUALIZACIONES")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de uso por cliente
        if not clientes_df.empty:
            fig_uso = create_client_usage_chart(clientes_df)
            st.plotly_chart(fig_uso, use_container_width=True)
    
    with col2:
        # Gráfico de distribución de estados
        fig_estados = create_status_distribution_chart(stats)
        st.plotly_chart(fig_estados, use_container_width=True)
    
    # Gráfico de disponibilidad
    if not clientes_df.empty:
        fig_disponible = create_availability_chart(clientes_df)
        st.plotly_chart(fig_disponible, use_container_width=True)
    
    st.markdown("---")
    
    # ========== SECCIÓN 4: CLIENTES DESTACADOS ==========
    st.markdown("### 👥 CLIENTES DESTACADOS")
    
    if not clientes_df.empty:
        # Clientes en alerta
        clientes_alerta = clientes_df[clientes_df['estado'] == 'ALERTA']
        if not clientes_alerta.empty:
            st.warning("### ⚠️ CLIENTES EN ALERTA")
            cols = st.columns(min(3, len(clientes_alerta)))
            for idx, (_, cliente) in enumerate(clientes_alerta.iterrows()):
                with cols[idx % 3]:
                    st.metric(
                        label=cliente['nombre'][:20] + ("..." if len(cliente['nombre']) > 20 else ""),
                        value=f"{cliente['porcentaje_uso']:.1f}%",
                        delta=f"Disp: {format_currency(cliente['disponible'])}"
                    )
        
        # Clientes normales
        clientes_normales = clientes_df[clientes_df['estado'] == 'NORMAL'].head(3)
        if not clientes_normales.empty:
            st.info("### 🟢 CLIENTES EN ESTADO NORMAL")
            cols = st.columns(min(3, len(clientes_normales)))
            for idx, (_, cliente) in enumerate(clientes_normales.iterrows()):
                with cols[idx % 3]:
                    st.metric(
                        label=cliente['nombre'][:20] + ("..." if len(cliente['nombre']) > 20 else ""),
                        value=f"{cliente['porcentaje_uso']:.1f}%",
                        delta=f"Disp: {format_currency(cliente['disponible'])}"
                    )
    
    # ========== PIE DE PÁGINA ==========
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.caption(f"👤 Usuario: {user.get('nombre', 'Invitado')}")
    
    with col2:
        st.caption(f"🏢 Sistema: Tododrogas Gestión de Cupos")
    
    with col3:
        st.caption(f"🕐 Última actualización: {datetime.now().strftime('%H:%M')}")

# ==================== EJECUCIÓN ====================

if __name__ == "__main__":
    show_dashboard()
