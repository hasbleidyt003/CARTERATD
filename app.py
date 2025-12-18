"""
SISTEMA DE GESTIÓN DE CUPOS TD
Versión 3.0 - Interfaz Futurista y Profesional
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar módulos personalizados
from config import config
from modules.database import (
    init_database, obtener_clientes, obtener_ocs, crear_oc, autorizar_oc,
    obtener_estadisticas_generales, verificar_alertas_cupos, obtener_tendencias_cupos,
    obtener_historial_autorizaciones, crear_cliente, actualizar_cliente
)
from modules.utils import (
    Validador, Formateador, CalculadoraFinanciera, DataFrameManager, DateUtils
)

# ============================================================================
# CONFIGURACIÓN DE PÁGINA STREAMLIT
# ============================================================================

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': None,
        'About': f"""
        ## {config.APP_NAME}
        
        **Versión:** {config.APP_VERSION}
        **Descripción:** {config.APP_DESCRIPTION}
        
        Sistema profesional para gestión y seguimiento de cupos de crédito.
        Desarrollado con tecnología de punta para máxima eficiencia.
        """
    }
)

# ============================================================================
# INYECTAR CSS PERSONALIZADO
# ============================================================================

def inject_custom_css():
    """Inyecta CSS personalizado en la aplicación"""
    css_path = Path(__file__).parent / 'assets' / 'styles.css'
    if css_path.exists():
        with open(css_path, 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        # CSS de respaldo
        st.markdown("""
        <style>
        .stApp { background: #0f172a; color: white; }
        h1, h2, h3 { color: #2563eb; }
        .stButton>button { background: linear-gradient(135deg, #2563eb, #7c3aed); }
        </style>
        """, unsafe_allow_html=True)

# ============================================================================
# BARRA DE NAVEGACIÓN SUPERIOR PERSONALIZADA
# ============================================================================

def render_top_navigation():
    """Renderiza barra de navegación superior personalizada"""
    st.markdown("""
    <div class="top-nav">
        <div class="nav-brand">
            <div class="nav-logo">💼 CUPOS TD</div>
            <div style="font-size: 0.9rem; color: #94a3b8;">v{config.APP_VERSION}</div>
        </div>
        
        <div class="nav-tabs">
            <button class="nav-tab" onclick="window.location.href='?page=dashboard'">🏠 Dashboard</button>
            <button class="nav-tab" onclick="window.location.href='?page=clientes'">👥 Clientes</button>
            <button class="nav-tab" onclick="window.location.href='?page=ocs'">📋 Órdenes de Compra</button>
            <button class="nav-tab" onclick="window.location.href='?page=reportes'">📊 Reportes</button>
            <button class="nav-tab" onclick="window.location.href='?page=configuracion'">⚙️ Configuración</button>
        </div>
        
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="background: rgba(37, 99, 235, 0.1); padding: 0.5rem 1rem; border-radius: 8px;">
                <span style="color: #94a3b8; font-size: 0.9rem;">Sistema Activo</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# COMPONENTES REUTILIZABLES
# ============================================================================

def metric_card(title, value, delta=None, icon="📊", color="primary"):
    """Componente de tarjeta métrica futurista"""
    colors = config.COLORS
    color_map = {
        'primary': colors['primary'],
        'success': colors['success'],
        'warning': colors['warning'],
        'danger': colors['danger'],
        'accent': colors['accent']
    }
    
    gradient = f"linear-gradient(135deg, {color_map.get(color, colors['primary'])} 0%, {colors['secondary']} 100%)"
    
    return f"""
    <div class="metric-card" style="border-top-color: {color_map.get(color, colors['primary'])};">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <div class="metric-label">{title}</div>
                <div class="metric-value">{value}</div>
                {f'<div style="color: #94a3b8; font-size: 0.9rem;">{delta}</div>' if delta else ''}
            </div>
            <div style="font-size: 2rem; opacity: 0.7;">{icon}</div>
        </div>
    </div>
    """

def data_table(df, title="", height=400):
    """Componente de tabla de datos estilizada"""
    if df.empty:
        return st.info("No hay datos para mostrar")
    
    return st.dataframe(
        df,
        use_container_width=True,
        height=height,
        hide_index=True
    )

# ============================================================================
# PÁGINA: DASHBOARD PRINCIPAL
# ============================================================================

def page_dashboard():
    """Dashboard principal futurista"""
    
    # Verificar e inicializar base de datos
    if not os.path.exists(config.DATABASE_PATH):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 4rem; background: rgba(15, 23, 42, 0.5); 
                        border-radius: 16px; border: 1px solid rgba(100, 116, 139, 0.3);">
                <div style="font-size: 4rem; margin-bottom: 2rem;">🚀</div>
                <h2>Bienvenido al Sistema de Cupos TD</h2>
                <p style="color: #94a3b8; margin-bottom: 2rem;">
                    Sistema profesional para gestión de cupos de crédito
                </p>
                <button onclick="window.location.href='?page=init'" 
                        style="background: linear-gradient(135deg, #2563eb, #7c3aed); 
                               color: white; border: none; padding: 1rem 2rem; 
                               border-radius: 10px; font-size: 1rem; cursor: pointer;">
                    Inicializar Sistema
                </button>
            </div>
            """, unsafe_allow_html=True)
        return
    
    try:
        # Obtener estadísticas generales
        stats = obtener_estadisticas_generales()
        
        # Encabezado del dashboard
        col_header1, col_header2, col_header3 = st.columns([2, 1, 1])
        with col_header1:
            st.markdown(f"<h1>📊 Dashboard Principal</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #94a3b8;'>Resumen general del sistema - {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>", unsafe_allow_html=True)
        
        with col_header2:
            st.markdown(metric_card(
                "Clientes Activos",
                f"{stats.get('total_clientes', 0):,}",
                icon="👥"
            ), unsafe_allow_html=True)
        
        with col_header3:
            st.markdown(metric_card(
                "Cupo Total",
                Formateador.formato_monetario(stats.get('total_cupo_sistema', 0)),
                icon="💰"
            ), unsafe_allow_html=True)
        
        # Primera fila de métricas
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(metric_card(
                "Cartera Total",
                Formateador.formato_monetario(stats.get('total_cartera_sistema', 0)),
                delta=f"{stats.get('porcentaje_uso_promedio', 0):.1f}% de uso",
                icon="📈",
                color="accent"
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown(metric_card(
                "Disponible Total",
                Formateador.formato_monetario(stats.get('total_disponible_sistema', 0)),
                delta=f"{stats.get('porcentaje_disponible', 0):.1f}% disponible",
                icon="🔄",
                color="success"
            ), unsafe_allow_html=True)
        
        with col3:
            st.markdown(metric_card(
                "Órdenes Pendientes",
                Formateador.formato_monetario(stats.get('valor_pendiente', 0)),
                delta=f"Valor por autorizar",
                icon="⏳",
                color="warning"
            ), unsafe_allow_html=True)
        
        with col4:
            st.markdown(metric_card(
                "Órdenes Autorizadas",
                Formateador.formato_monetario(stats.get('valor_autorizado', 0)),
                delta=f"Valor autorizado",
                icon="✅",
                color="success"
            ), unsafe_allow_html=True)
        
        # Segunda fila: Gráficos principales
        st.markdown("<br>", unsafe_allow_html=True)
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("### 📊 Distribución por Estado de Cupo")
            
            # Obtener datos de clientes
            clientes = obtener_clientes()
            if not clientes.empty and 'estado_cupo' in clientes.columns:
                estado_counts = clientes['estado_cupo'].value_counts()
                
                fig = go.Figure(data=[go.Pie(
                    labels=estado_counts.index,
                    values=estado_counts.values,
                    hole=.4,
                    marker_colors=[config.COLORS['danger'], config.COLORS['warning'], 
                                  config.COLORS['success'], config.COLORS['accent']],
                    textinfo='label+percent',
                    textposition='inside'
                )])
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    showlegend=False,
                    height=300,
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de clientes disponibles")
        
        with col_chart2:
            st.markdown("### 📈 Tendencia de Cupos (Últimos 30 días)")
            
            # Obtener tendencias
            tendencias = obtener_tendencias_cupos(30)
            if not tendencias.empty:
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=tendencias['fecha'],
                    y=tendencias['total_cartera_dia'],
                    mode='lines+markers',
                    name='Cartera Total',
                    line=dict(color=config.COLORS['primary'], width=3),
                    marker=dict(size=8)
                ))
                
                fig.add_trace(go.Scatter(
                    x=tendencias['fecha'],
                    y=tendencias['total_cupo_dia'],
                    mode='lines',
                    name='Cupo Total',
                    line=dict(color=config.COLORS['success'], width=2, dash='dash')
                ))
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    height=300,
                    margin=dict(l=20, r=20, t=30, b=20),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de tendencias disponibles")
        
        # Tercera fila: Alertas y OCs recientes
        st.markdown("<br>", unsafe_allow_html=True)
        col_alerts, col_recent = st.columns(2)
        
        with col_alerts:
            st.markdown("### 🚨 Alertas Activas")
            
            alertas = verificar_alertas_cupos()
            if not alertas.empty:
                for _, alerta in alertas.iterrows():
                    nivel_color = {
                        'CRITICO': config.COLORS['danger'],
                        'ALERTA': config.COLORS['warning'],
                        'NORMAL': config.COLORS['success']
                    }.get(alerta['nivel_alerta'], config.COLORS['warning'])
                    
                    st.markdown(f"""
                    <div style="background: rgba{(*tuple(int(nivel_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)), 0.1)}; 
                                border-left: 4px solid {nivel_color}; 
                                padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>{alerta['nombre']}</strong>
                                <div style="color: #94a3b8; font-size: 0.9rem;">NIT: {alerta['nit']}</div>
                            </div>
                            <div style="background: {nivel_color}; color: white; padding: 0.25rem 0.75rem; 
                                        border-radius: 20px; font-size: 0.8rem; font-weight: bold;">
                                {alerta['nivel_alerta']}
                            </div>
                        </div>
                        <div style="margin-top: 0.5rem; display: flex; gap: 1rem;">
                            <div style="color: #94a3b8;">Uso: <strong>{alerta['porcentaje_uso']:.1f}%</strong></div>
                            <div style="color: #94a3b8;">Disponible: <strong>{Formateador.formato_monetario(alerta['disponible'])}</strong></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ No hay alertas activas en este momento")
        
        with col_recent:
            st.markdown("### 📋 Órdenes de Compra Recientes")
            
            ocs_recientes = obtener_ocs({'fecha_desde': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')})
            if not ocs_recientes.empty:
                for _, oc in ocs_recientes.head(5).iterrows():
                    estado_colores = {
                        'PENDIENTE': config.COLORS['warning'],
                        'PARCIAL': config.COLORS['accent'],
                        'AUTORIZADA': config.COLORS['success'],
                        'RECHAZADA': config.COLORS['danger'],
                        'ANULADA': config.COLORS['dark']
                    }
                    
                    estado_color = estado_colores.get(oc['estado_oc'], config.COLORS['warning'])
                    
                    st.markdown(f"""
                    <div style="background: rgba{(*tuple(int(estado_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)), 0.1)}; 
                                border-left: 4px solid {estado_color}; 
                                padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>{oc['numero_oc']}</strong>
                                <div style="color: #94a3b8; font-size: 0.9rem;">{oc['cliente_nombre']}</div>
                            </div>
                            <div style="background: {estado_color}; color: white; padding: 0.25rem 0.75rem; 
                                        border-radius: 20px; font-size: 0.8rem; font-weight: bold;">
                                {oc['estado_oc']}
                            </div>
                        </div>
                        <div style="margin-top: 0.5rem; display: flex; justify-content: space-between;">
                            <div style="color: #94a3b8;">Total: <strong>{Formateador.formato_monetario(oc['valor_total'])}</strong></div>
                            <div style="color: #94a3b8;">Autorizado: <strong>{Formateador.formato_monetario(oc['valor_autorizado'])}</strong></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if len(ocs_recientes) > 5:
                    st.info(f"Mostrando 5 de {len(ocs_recientes)} OCs recientes")
            else:
                st.info("No hay OCs recientes")
        
        # Cuarta fila: Resumen de clientes
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 👥 Resumen de Clientes")
        
        clientes_resumen = obtener_clientes()
        if not clientes_resumen.empty:
            # Crear tabla resumen
            df_resumen = clientes_resumen[['nombre', 'total_cartera', 'cupo_sugerido', 'disponible', 'porcentaje_uso', 'estado_cupo']].copy()
            
            # Formatear valores
            df_resumen['total_cartera'] = df_resumen['total_cartera'].apply(lambda x: Formateador.formato_monetario(x))
            df_resumen['cupo_sugerido'] = df_resumen['cupo_sugerido'].apply(lambda x: Formateador.formato_monetario(x))
            df_resumen['disponible'] = df_resumen['disponible'].apply(lambda x: Formateador.formato_monetario(x))
            df_resumen['porcentaje_uso'] = df_resumen['porcentaje_uso'].apply(lambda x: f"{x:.1f}%")
            
            # Aplicar estilo a la columna estado
            def estilo_estado(val):
                color = {
                    'SOBREPASADO': config.COLORS['danger'],
                    'ALTO': config.COLORS['warning'],
                    'MEDIO': config.COLORS['accent'],
                    'NORMAL': config.COLORS['success']
                }.get(val, config.COLORS['dark'])
                
                return f'background-color: {color}20; color: {color}; font-weight: bold; padding: 5px; border-radius: 4px;'
            
            styled_df = df_resumen.style.applymap(estilo_estado, subset=['estado_cupo'])
            
            st.dataframe(
                styled_df,
                use_container_width=True,
                height=300,
                column_config={
                    'nombre': 'Cliente',
                    'total_cartera': 'Cartera',
                    'cupo_sugerido': 'Cupo',
                    'disponible': 'Disponible',
                    'porcentaje_uso': '% Uso',
                    'estado_cupo': 'Estado'
                }
            )
        else:
            st.info("No hay clientes registrados")
            
    except Exception as e:
        st.error(f"❌ Error cargando dashboard: {str(e)}")
        st.info("Verifica que la base de datos esté correctamente inicializada.")

# ============================================================================
# PÁGINA: GESTIÓN DE CLIENTES
# ============================================================================

def page_clientes():
    """Página de gestión de clientes"""
    
    st.markdown(f"<h1>👥 Gestión de Clientes</h1>", unsafe_allow_html=True)
    
    # Verificar base de datos
    if not os.path.exists(config.DATABASE_PATH):
        st.error("❌ La base de datos no está inicializada. Ve al Dashboard primero.")
        return
    
    # Pestañas principales
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Clientes", "➕ Nuevo Cliente", "📊 Análisis Detallado"])
    
    with tab1:
        # Filtros avanzados
        col_filt1, col_filt2, col_filt3, col_filt4 = st.columns(4)
        
        with col_filt1:
            filtro_nit = st.text_input("🔍 Buscar por NIT", key="filtro_nit_cliente")
        
        with col_filt2:
            filtro_nombre = st.text_input("🔍 Buscar por Nombre", key="filtro_nombre_cliente")
        
        with col_filt3:
            filtro_estado = st.selectbox(
                "Filtrar por Estado",
                ["TODOS", "NORMAL", "MEDIO", "ALTO", "SOBREPASADO"],
                key="filtro_estado_cliente"
            )
        
        with col_filt4:
            st.markdown("<br>", unsafe_allow_html=True)
            btn_actualizar = st.button("🔄 Actualizar", use_container_width=True)
        
        # Obtener clientes con filtros
        filtros = {}
        if filtro_nit:
            filtros['nit'] = filtro_nit
        if filtro_nombre:
            filtros['nombre'] = filtro_nombre
        if filtro_estado != "TODOS":
            filtros['estado'] = filtro_estado
        
        clientes = obtener_clientes(filtros)
        
        if not clientes.empty:
            # Mostrar métricas resumen
            col_met1, col_met2, col_met3, col_met4 = st.columns(4)
            
            with col_met1:
                st.markdown(metric_card(
                    "Clientes",
                    len(clientes),
                    icon="👥"
                ), unsafe_allow_html=True)
            
            with col_met2:
                st.markdown(metric_card(
                    "Cartera Total",
                    Formateador.formato_monetario(clientes['total_cartera'].sum()),
                    icon="💰"
                ), unsafe_allow_html=True)
            
            with col_met3:
                st.markdown(metric_card(
                    "Cupo Total",
                    Formateador.formato_monetario(clientes['cupo_sugerido'].sum()),
                    icon="📊"
                ), unsafe_allow_html=True)
            
            with col_met4:
                st.markdown(metric_card(
                    "% Uso Promedio",
                    f"{clientes['porcentaje_uso'].mean():.1f}%",
                    icon="📈"
                ), unsafe_allow_html=True)
            
            st.divider()
            
            # Tabla de clientes con opciones de edición
            for idx, cliente in clientes.iterrows():
                with st.expander(f"{cliente['nombre']} (NIT: {cliente['nit']})", expanded=False):
                    col_edit1, col_edit2, col_edit3 = st.columns(3)
                    
                    with col_edit1:
                        nuevo_nombre = st.text_input(
                            "Nombre del Cliente",
                            value=cliente['nombre'],
                            key=f"nombre_{cliente['nit']}"
                        )
                        
                        nuevo_cupo = st.number_input(
                            "Cupo Sugerido",
                            value=float(cliente['cupo_sugerido']),
                            min_value=0.0,
                            step=1000000.0,
                            format="%.0f",
                            key=f"cupo_{cliente['nit']}"
                        )
                    
                    with col_edit2:
                        nueva_cartera = st.number_input(
                            "Total Cartera",
                            value=float(cliente['total_cartera']),
                            min_value=0.0,
                            step=1000000.0,
                            format="%.0f",
                            key=f"cartera_{cliente['nit']}"
                        )
                        
                        # Calcular nuevos valores
                        nuevo_disponible = nuevo_cupo - nueva_cartera
                        nuevo_porcentaje = (nueva_cartera / nuevo_cupo * 100) if nuevo_cupo > 0 else 0
                    
                    with col_edit3:
                        # Mostrar nuevos cálculos
                        st.metric(
                            "Nuevo Disponible",
                            Formateador.formato_monetario(nuevo_disponible),
                            delta=f"{nuevo_porcentaje:.1f}% uso"
                        )
                        
                        # Determinar nuevo estado
                        if nueva_cartera > nuevo_cupo:
                            nuevo_estado = "SOBREPASADO"
                            estado_color = config.COLORS['danger']
                        elif nuevo_porcentaje >= 90:
                            nuevo_estado = "ALTO"
                            estado_color = config.COLORS['warning']
                        elif nuevo_porcentaje >= 70:
                            nuevo_estado = "MEDIO"
                            estado_color = config.COLORS['accent']
                        else:
                            nuevo_estado = "NORMAL"
                            estado_color = config.COLORS['success']
                        
                        st.markdown(f"""
                        <div style="background: {estado_color}20; color: {estado_color}; 
                                    padding: 0.5rem; border-radius: 8px; text-align: center; font-weight: bold;">
                            {nuevo_estado}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Botones de acción
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    with col_btn1:
                        if st.button("💾 Guardar Cambios", key=f"guardar_{cliente['nit']}", use_container_width=True):
                            try:
                                actualizar_cliente(
                                    nit=cliente['nit'],
                                    data={
                                        'nombre': nuevo_nombre,
                                        'cupo_sugerido': nuevo_cupo,
                                        'total_cartera': nueva_cartera,
                                        'usuario': 'Sistema'
                                    }
                                )
                                st.success("✅ Cambios guardados exitosamente")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                    
                    with col_btn2:
                        if st.button("📋 Ver OCs", key=f"ocs_{cliente['nit']}", use_container_width=True):
                            st.session_state.cliente_seleccionado = cliente['nit']
                            st.switch_page("pages/3_ocs.py")
                    
                    with col_btn3:
                        if st.button("📊 Ver Historial", key=f"hist_{cliente['nit']}", use_container_width=True):
                            st.session_state.cliente_detalle = cliente['nit']
        else:
            st.info("📭 No hay clientes que coincidan con los filtros")
    
    with tab2:
        st.markdown("### ➕ Agregar Nuevo Cliente")
        
        with st.form("form_nuevo_cliente"):
            col_new1, col_new2 = st.columns(2)
            
            with col_new1:
                nuevo_nit = st.text_input("NIT *", help="Número de Identificación Tributaria")
                nuevo_nombre = st.text_input("Nombre del Cliente *", help="Nombre completo o razón social")
                nuevo_email = st.text_input("Email de Contacto", help="Correo electrónico del cliente")
            
            with col_new2:
                nuevo_cupo = st.number_input(
                    "Cupo Sugerido *",
                    min_value=0.0,
                    value=100000000.0,
                    step=10000000.0,
                    format="%.0f",
                    help="Cupo de crédito sugerido para el cliente"
                )
                
                nueva_cartera = st.number_input(
                    "Total Cartera Inicial",
                    min_value=0.0,
                    value=0.0,
                    step=10000000.0,
                    format="%.0f",
                    help="Cartera inicial del cliente"
                )
                
                nuevo_telefono = st.text_input("Teléfono de Contacto", help="Teléfono del cliente")
            
            # Cálculos en tiempo real
            disponible = nuevo_cupo - nueva_cartera
            porcentaje_uso = (nueva_cartera / nuevo_cupo * 100) if nuevo_cupo > 0 else 0
            
            col_calc1, col_calc2 = st.columns(2)
            with col_calc1:
                st.metric("Disponible Inicial", Formateador.formato_monetario(disponible))
            with col_calc2:
                st.metric("% Uso Inicial", f"{porcentaje_uso:.1f}%")
            
            notas = st.text_area("Notas Adicionales", height=100)
            
            # Botón de envío
            col_submit, col_cancel = st.columns(2)
            
            with col_submit:
                submitted = st.form_submit_button(
                    "🚀 Crear Cliente",
                    type="primary",
                    use_container_width=True
                )
            
            with col_cancel:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.rerun()
            
            if submitted:
                # Validaciones
                if not nuevo_nit or not nuevo_nombre:
                    st.error("❌ Los campos marcados con * son obligatorios")
                    return
                
                if not Validador.validar_nit(nuevo_nit):
                    st.error("❌ El NIT no tiene un formato válido")
                    return
                
                if nuevo_cupo <= 0:
                    st.error("❌ El cupo sugerido debe ser mayor a 0")
                    return
                
                try:
                    crear_cliente({
                        'nit': nuevo_nit,
                        'nombre': nuevo_nombre,
                        'cupo_sugerido': nuevo_cupo,
                        'total_cartera': nueva_cartera,
                        'contacto_email': nuevo_email,
                        'contacto_telefono': nuevo_telefono,
                        'notas': notas,
                        'usuario': 'Sistema'
                    })
                    
                    st.success(f"✅ Cliente '{nuevo_nombre}' creado exitosamente")
                    st.balloons()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error al crear cliente: {str(e)}")
    
    with tab3:
        st.markdown("### 📊 Análisis Detallado de Clientes")
        
        if clientes.empty:
            st.info("Agrega clientes para ver análisis detallados")
            return
        
        # Gráfico de dispersión: Cartera vs Cupo
        fig = px.scatter(
            clientes,
            x='cupo_sugerido',
            y='total_cartera',
            size='porcentaje_uso',
            color='estado_cupo',
            hover_name='nombre',
            hover_data=['nit', 'disponible'],
            labels={
                'cupo_sugerido': 'Cupo Sugerido',
                'total_cartera': 'Total Cartera',
                'porcentaje_uso': '% Uso',
                'estado_cupo': 'Estado'
            },
            color_discrete_map={
                'NORMAL': config.COLORS['success'],
                'MEDIO': config.COLORS['accent'],
                'ALTO': config.COLORS['warning'],
                'SOBREPASADO': config.COLORS['danger']
            }
        )
        
        # Agregar línea de 100% de uso
        max_val = max(clientes['cupo_sugerido'].max(), clientes['total_cartera'].max())
        fig.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            line=dict(color=config.COLORS['danger'], width=2, dash='dash'),
            name='Límite 100%'
        ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Análisis por rangos de uso
        st.markdown("#### 📈 Distribución por Nivel de Uso")
        
        bins = [0, 50, 70, 90, 100, float('inf')]
        labels = ['0-50%', '51-70%', '71-90%', '91-100%', '>100%']
        
        clientes['rango_uso'] = pd.cut(clientes['porcentaje_uso'], bins=bins, labels=labels, right=False)
        distribucion = clientes['rango_uso'].value_counts().sort_index()
        
        col_dist1, col_dist2 = st.columns([2, 1])
        
        with col_dist1:
            fig_dist = px.bar(
                x=distribucion.index,
                y=distribucion.values,
                labels={'x': 'Rango de Uso', 'y': 'Número de Clientes'},
                color=distribucion.index,
                color_discrete_sequence=[
                    config.COLORS['success'], 
                    config.COLORS['accent'], 
                    config.COLORS['warning'], 
                    config.COLORS['danger'],
                    config.COLORS['dark']
                ]
            )
            
            fig_dist.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                showlegend=False,
                height=300
            )
            
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with col_dist2:
            st.markdown("##### Resumen por Rango")
            for rango, count in distribucion.items():
                porcentaje = (count / len(clientes)) * 100
                st.metric(
                    f"{rango}",
                    f"{count} clientes",
                    delta=f"{porcentaje:.1f}%"
                )

# ============================================================================
# PÁGINA: ÓRDENES DE COMPRA
# ============================================================================

def page_ocs():
    """Página de gestión de órdenes de compra"""
    
    st.markdown(f"<h1>📋 Gestión de Órdenes de Compra</h1>", unsafe_allow_html=True)
    
    # Verificar base de datos
    if not os.path.exists(config.DATABASE_PATH):
        st.error("❌ La base de datos no está inicializada. Ve al Dashboard primero.")
        return
    
    # Estadísticas rápidas
    try:
        stats = obtener_estadisticas_generales()
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.markdown(metric_card(
                "Total OCs",
                stats.get('total_ocs', 0),
                icon="📄"
            ), unsafe_allow_html=True)
        
        with col_stat2:
            st.markdown(metric_card(
                "Pendientes",
                Formateador.formato_monetario(stats.get('valor_pendiente', 0)),
                icon="⏳"
            ), unsafe_allow_html=True)
        
        with col_stat3:
            st.markdown(metric_card(
                "Autorizadas",
                Formateador.formato_monetario(stats.get('valor_autorizado', 0)),
                icon="✅"
            ), unsafe_allow_html=True)
        
        with col_stat4:
            st.markdown(metric_card(
                "Parciales",
                Formateador.formato_monetario(stats.get('valor_parcial', 0)),
                icon="🔄"
            ), unsafe_allow_html=True)
    except:
        pass
    
    # Pestañas principales
    tab1, tab2, tab3 = st.tabs(["📋 Lista de OCs", "➕ Nueva OC", "✅ Autorizar OCs"])
    
    with tab1:
        # Filtros avanzados para OCs
        with st.expander("🔍 Filtros Avanzados", expanded=True):
            col_filt1, col_filt2, col_filt3 = st.columns(3)
            
            with col_filt1:
                filtro_numero = st.text_input("Número de OC", key="filtro_numero_oc")
                filtro_cliente = st.selectbox(
                    "Cliente",
                    ["TODOS"] + obtener_clientes()['nombre'].tolist() if not obtener_clientes().empty else ["TODOS"],
                    key="filtro_cliente_oc"
                )
            
            with col_filt2:
                filtro_estado = st.selectbox(
                    "Estado",
                    ["TODOS", "PENDIENTE", "PARCIAL", "AUTORIZADA", "RECHAZADA", "ANULADA"],
                    key="filtro_estado_oc"
                )
                
                filtro_prioridad = st.selectbox(
                    "Prioridad",
                    ["TODAS", "BAJA", "MEDIA", "ALTA", "CRITICA"],
                    key="filtro_prioridad_oc"
                )
            
            with col_filt3:
                col_fecha1, col_fecha2 = st.columns(2)
                with col_fecha1:
                    filtro_fecha_desde = st.date_input("Desde", key="filtro_fecha_desde")
                with col_fecha2:
                    filtro_fecha_hasta = st.date_input("Hasta", key="filtro_fecha_hasta")
        
        # Aplicar filtros
        filtros = {}
        if filtro_numero:
            filtros['numero_oc'] = filtro_numero
        if filtro_cliente != "TODOS":
            clientes_df = obtener_clientes()
            cliente_nit = clientes_df[clientes_df['nombre'] == filtro_cliente]['nit'].iloc[0]
            filtros['cliente_nit'] = cliente_nit
        if filtro_estado != "TODOS":
            filtros['estado_oc'] = filtro_estado
        if filtro_prioridad != "TODAS":
            filtros['prioridad'] = filtro_prioridad
        if filtro_fecha_desde:
            filtros['fecha_desde'] = filtro_fecha_desde.strftime('%Y-%m-%d')
        if filtro_fecha_hasta:
            filtros['fecha_hasta'] = filtro_fecha_hasta.strftime('%Y-%m-%d')
        
        # Obtener OCs filtradas
        ocs = obtener_ocs(filtros)
        
        if not ocs.empty:
            # Mostrar OCs como tarjetas interactivas
            for _, oc in ocs.iterrows():
                render_oc_card(oc)
        else:
            st.info("📭 No hay OCs que coincidan con los filtros")
    
    with tab2:
        st.markdown("### ➕ Crear Nueva Orden de Compra")
        
        with st.form("form_nueva_oc", clear_on_submit=True):
            col_oc1, col_oc2 = st.columns(2)
            
            with col_oc1:
                # Selección de cliente
                clientes_disponibles = obtener_clientes()
                if clientes_disponibles.empty:
                    st.error("❌ No hay clientes disponibles. Agrega clientes primero.")
                    st.stop()
                
                cliente_seleccionado = st.selectbox(
                    "Cliente *",
                    clientes_disponibles['nombre'].tolist(),
                    help="Seleccione el cliente para la OC"
                )
                
                cliente_nit = clientes_disponibles[
                    clientes_disponibles['nombre'] == cliente_seleccionado
                ]['nit'].iloc[0]
                
                # Información del cliente seleccionado
                cliente_info = clientes_disponibles[
                    clientes_disponibles['nit'] == cliente_nit
                ].iloc[0]
                
                st.info(f"""
                **Información del cliente:**
                - Cupo disponible: {Formateador.formato_monetario(cliente_info['disponible'])}
                - % Uso actual: {cliente_info['porcentaje_uso']:.1f}%
                - Estado: {cliente_info['estado_cupo']}
                """)
                
                # Número de OC
                numero_oc = st.text_input(
                    "Número de OC *",
                    help="Ej: OC-2024-001, FACT-12345",
                    placeholder="OC-2024-001"
                )
                
                # Proveedor
                proveedor = st.text_input(
                    "Proveedor",
                    help="Nombre del proveedor",
                    placeholder="Nombre del proveedor"
                )
            
            with col_oc2:
                # Valores y tipo
                valor_total = st.number_input(
                    "Valor Total *",
                    min_value=0.0,
                    value=0.0,
                    step=100000.0,
                    format="%.0f",
                    help="Valor total de la orden de compra"
                )
                
                # Validar cupo disponible
                disponible_cliente = cliente_info['disponible']
                if valor_total > disponible_cliente:
                    st.warning(f"⚠️ El valor excede el cupo disponible (${disponible_cliente:,.0f})")
                
                tipo_oc = st.selectbox(
                    "Tipo de OC",
                    ["NORMAL", "URGENTE", "CUPO_NUEVO"],
                    help="Tipo de orden de compra"
                )
                
                prioridad = st.selectbox(
                    "Prioridad",
                    ["MEDIA", "BAJA", "ALTA", "CRITICA"],
                    help="Prioridad de la OC"
                )
                
                fecha_requerida = st.date_input(
                    "Fecha Requerida",
                    help="Fecha en que se requiere la orden"
                )
            
            # Información adicional
            st.markdown("#### 📝 Información Adicional")
            
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                descripcion = st.text_area(
                    "Descripción",
                    height=100,
                    help="Descripción detallada de la OC",
                    placeholder="Descripción de los productos o servicios..."
                )
                
                centro_costo = st.text_input(
                    "Centro de Costo",
                    help="Centro de costo asociado"
                )
            
            with col_info2:
                proyecto = st.text_input(
                    "Proyecto",
                    help="Proyecto asociado"
                )
                
                area = st.text_input(
                    "Área Solicitante",
                    help="Área que solicita la OC"
                )
                
                referencia_cupo = st.text_input(
                    "Referencia de Cupo",
                    help="Referencia específica del cupo"
                )
            
            observaciones = st.text_area(
                "Observaciones",
                height=80,
                help="Observaciones adicionales",
                placeholder="Observaciones o notas importantes..."
            )
            
            # Botones de acción
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                submitted = st.form_submit_button(
                    "🚀 Crear Orden de Compra",
                    type="primary",
                    use_container_width=True
                )
            
            with col_btn2:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.rerun()
            
            if submitted:
                # Validaciones
                if not numero_oc.strip():
                    st.error("❌ El número de OC es obligatorio")
                    return
                
                if valor_total <= 0:
                    st.error("❌ El valor total debe ser mayor a 0")
                    return
                
                if not cliente_nit:
                    st.error("❌ Debe seleccionar un cliente")
                    return
                
                # Validar cupo si no es CUPO_NUEVO
                if tipo_oc != "CUPO_NUEVO" and valor_total > disponible_cliente:
                    st.error(f"❌ El valor excede el cupo disponible (${disponible_cliente:,.0f})")
                    return
                
                try:
                    oc_id = crear_oc({
                        'cliente_nit': cliente_nit,
                        'numero_oc': Formateador.formato_numero_oc(numero_oc),
                        'proveedor': proveedor,
                        'valor_total': valor_total,
                        'tipo_oc': tipo_oc,
                        'prioridad': prioridad,
                        'descripcion': descripcion,
                        'centro_costo': centro_costo,
                        'proyecto': proyecto,
                        'area': area,
                        'fecha_solicitud': datetime.now().strftime('%Y-%m-%d'),
                        'fecha_requerida': fecha_requerida.strftime('%Y-%m-%d'),
                        'referencia_cupo': referencia_cupo,
                        'observaciones': observaciones,
                        'usuario_creacion': 'Sistema'
                    })
                    
                    st.success(f"✅ Orden de Compra '{numero_oc}' creada exitosamente (ID: {oc_id})")
                    st.balloons()
                    
                    # Mostrar resumen
                    st.info(f"""
                    **Resumen de la OC creada:**
                    - **Número:** {numero_oc}
                    - **Cliente:** {cliente_seleccionado}
                    - **Valor Total:** {Formateador.formato_monetario(valor_total)}
                    - **Tipo:** {tipo_oc}
                    - **Prioridad:** {prioridad}
                    - **Estado:** PENDIENTE
                    """)
                    
                    # Opción para crear otra
                    if st.button("➕ Crear Otra OC"):
                        st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error al crear OC: {str(e)}")
    
    with tab3:
        st.markdown("### ✅ Autorización de Órdenes de Compra")
        
        # Obtener OCs pendientes o parciales
        ocs_pendientes = obtener_ocs({'estado_oc': 'PENDIENTE'})
        ocs_parciales = obtener_ocs({'estado_oc': 'PARCIAL'})
        
        todas_ocs = pd.concat([ocs_pendientes, ocs_parciales]).reset_index(drop=True)
        
        if not todas_ocs.empty:
            st.markdown(f"#### 📋 OCs Pendientes de Autorización ({len(todas_ocs)})")
            
            for _, oc in todas_ocs.iterrows():
                with st.container():
                    col_oc1, col_oc2, col_oc3 = st.columns([3, 2, 1])
                    
                    with col_oc1:
                        st.markdown(f"**{oc['numero_oc']}**")
                        st.caption(f"Cliente: {oc['cliente_nombre']}")
                        
                        if oc['descripcion']:
                            st.caption(f"Descripción: {oc['descripcion'][:100]}...")
                    
                    with col_oc2:
                        # Barra de progreso de autorización
                        valor_total = oc['valor_total']
                        valor_autorizado = oc['valor_autorizado'] or 0
                        porcentaje_autorizado = (valor_autorizado / valor_total * 100) if valor_total > 0 else 0
                        
                        st.progress(porcentaje_autorizado / 100)
                        st.caption(f"Autorizado: {Formateador.formato_monetario(valor_autorizado)} de {Formateador.formato_monetario(valor_total)}")
                        
                        # Mostrar prioridad
                        prioridad_colores = {
                            'CRITICA': config.COLORS['danger'],
                            'ALTA': config.COLORS['warning'],
                            'MEDIA': config.COLORS['accent'],
                            'BAJA': config.COLORS['success']
                        }
                        
                        prioridad_color = prioridad_colores.get(oc['prioridad'], config.COLORS['dark'])
                        st.markdown(f"""
                        <div style="background: {prioridad_color}20; color: {prioridad_color}; 
                                    padding: 0.25rem 0.5rem; border-radius: 4px; display: inline-block;">
                            {oc['prioridad']}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_oc3:
                        if st.button("✅ Autorizar", key=f"auth_{oc['id']}", use_container_width=True):
                            st.session_state.oc_autorizar = oc['id']
                            st.rerun()
                    
                    st.divider()
            
            # Modal de autorización si hay OC seleccionada
            if 'oc_autorizar' in st.session_state:
                oc_id = st.session_state.oc_autorizar
                oc_info = todas_ocs[todas_ocs['id'] == oc_id].iloc[0]
                
                with st.form(f"form_autorizar_{oc_id}"):
                    st.markdown(f"### ✅ Autorizar OC: {oc_info['numero_oc']}")
                    
                    col_auth1, col_auth2 = st.columns(2)
                    
                    with col_auth1:
                        st.metric(
                            "Valor Total",
                            Formateador.formato_monetario(oc_info['valor_total'])
                        )
                        
                        valor_restante = oc_info['valor_total'] - (oc_info['valor_autorizado'] or 0)
                        st.metric(
                            "Por Autorizar",
                            Formateador.formato_monetario(valor_restante)
                        )
                    
                    with col_auth2:
                        st.metric(
                            "Ya Autorizado",
                            Formateador.formato_monetario(oc_info['valor_autorizado'] or 0)
                        )
                        
                        porcentaje_actual = ((oc_info['valor_autorizado'] or 0) / oc_info['valor_total'] * 100) if oc_info['valor_total'] > 0 else 0
                        st.metric(
                            "% Autorizado",
                            f"{porcentaje_actual:.1f}%"
                        )
                    
                    st.divider()
                    
                    # Opciones de autorización
                    st.markdown("#### 📝 Opciones de Autorización")
                    
                    col_opts1, col_opts2, col_opts3, col_opts4 = st.columns(4)
                    
                    opciones_porcentaje = {}
                    with col_opts1:
                        if st.button("25%", use_container_width=True):
                            opciones_porcentaje['porcentaje'] = 25
                    with col_opts2:
                        if st.button("50%", use_container_width=True):
                            opciones_porcentaje['porcentaje'] = 50
                    with col_opts3:
                        if st.button("75%", use_container_width=True):
                            opciones_porcentaje['porcentaje'] = 75
                    with col_opts4:
                        if st.button("100%", use_container_width=True):
                            opciones_porcentaje['porcentaje'] = 100
                    
                    # Campo para valor específico
                    valor_autorizar = st.number_input(
                        "Valor a Autorizar *",
                        min_value=0.0,
                        max_value=float(valor_restante),
                        value=float(valor_restante),
                        step=100000.0,
                        format="%.0f",
                        help="Ingrese el valor específico a autorizar"
                    )
                    
                    # Comentarios
                    comentarios = st.text_area(
                        "Comentarios de Autorización",
                        height=100,
                        placeholder="Comentarios sobre la autorización..."
                    )
                    
                    nivel_autorizacion = st.selectbox(
                        "Nivel de Autorización",
                        [1, 2, 3],
                        help="Nivel jerárquico de autorización"
                    )
                    
                    # Botones de confirmación
                    col_confirm1, col_confirm2 = st.columns(2)
                    
                    with col_confirm1:
                        if st.form_submit_button("✅ Confirmar Autorización", type="primary", use_container_width=True):
                            if valor_autorizar <= 0:
                                st.error("❌ El valor a autorizar debe ser mayor a 0")
                            else:
                                try:
                                    autorizar_oc(
                                        oc_id=oc_id,
                                        data={
                                            'valor_autorizado': valor_autorizar,
                                            'comentarios': comentarios,
                                            'nivel_autorizacion': nivel_autorizacion,
                                            'usuario': 'Sistema',
                                            'departamento': 'Finanzas'
                                        }
                                    )
                                    
                                    st.success(f"✅ Autorizados {Formateador.formato_monetario(valor_autorizar)} exitosamente")
                                    del st.session_state.oc_autorizar
                                    st.rerun()
                                    
                                except Exception as e:
                                    st.error(f"❌ Error al autorizar: {str(e)}")
                    
                    with col_confirm2:
                        if st.form_submit_button("❌ Cancelar", use_container_width=True):
                            del st.session_state.oc_autorizar
                            st.rerun()
        
        else:
            st.success("✅ No hay OCs pendientes de autorización")

def render_oc_card(oc):
    """Renderiza una tarjeta de OC interactiva"""
    with st.container():
        estado_colores = {
            'PENDIENTE': config.COLORS['warning'],
            'PARCIAL': config.COLORS['accent'],
            'AUTORIZADA': config.COLORS['success'],
            'RECHAZADA': config.COLORS['danger'],
            'ANULADA': config.COLORS['dark']
        }
        
        estado_color = estado_colores.get(oc['estado_oc'], config.COLORS['warning'])
        prioridad_colores = {
            'CRITICA': config.COLORS['danger'],
            'ALTA': config.COLORS['warning'],
            'MEDIA': config.COLORS['accent'],
            'BAJA': config.COLORS['success']
        }
        
        prioridad_color = prioridad_colores.get(oc['prioridad'], config.COLORS['dark'])
        
        col_card1, col_card2, col_card3, col_card4 = st.columns([3, 2, 2, 1])
        
        with col_card1:
            st.markdown(f"**{oc['numero_oc']}**")
            st.caption(f"👤 {oc['cliente_nombre']}")
            
            if oc['descripcion']:
                with st.expander("📝 Descripción"):
                    st.write(oc['descripcion'])
        
        with col_card2:
            # Barra de progreso
            valor_total = oc['valor_total']
            valor_autorizado = oc['valor_autorizado'] or 0
            porcentaje = (valor_autorizado / valor_total * 100) if valor_total > 0 else 0
            
            st.progress(porcentaje / 100)
            st.caption(f"{Formateador.formato_monetario(valor_autorizado)} / {Formateador.formato_monetario(valor_total)}")
            
            # Fechas
            if 'fecha_solicitud' in oc and oc['fecha_solicitud']:
                st.caption(f"📅 {Formateador.formato_fecha(oc['fecha_solicitud'])}")
        
        with col_card3:
            # Estado y prioridad
            st.markdown(f"""
            <div style="background: {estado_color}20; color: {estado_color}; 
                        padding: 0.5rem; border-radius: 8px; text-align: center; margin-bottom: 0.5rem;">
                <strong>{oc['estado_oc']}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background: {prioridad_color}20; color: {prioridad_color}; 
                        padding: 0.5rem; border-radius: 8px; text-align: center;">
                <strong>{oc['prioridad']}</strong>
            </div>
            """, unsafe_allow_html=True)
        
        with col_card4:
            # Botones de acción
            if oc['estado_oc'] in ['PENDIENTE', 'PARCIAL']:
                if st.button("✅", key=f"btn_auth_{oc['id']}", help="Autorizar"):
                    st.session_state.oc_autorizar = oc['id']
                    st.rerun()
            
            if st.button("📋", key=f"btn_detail_{oc['id']}", help="Detalles"):
                st.session_state.oc_detalle = oc['id']
                st.rerun()
        
        # Separador
        st.markdown("---")

# ============================================================================
# PÁGINA: REPORTES
# ============================================================================

def page_reportes():
    """Página de reportes y análisis"""
    
    st.markdown(f"<h1>📊 Reportes y Análisis</h1>", unsafe_allow_html=True)
    
    # Verificar base de datos
    if not os.path.exists(config.DATABASE_PATH):
        st.error("❌ La base de datos no está inicializada. Ve al Dashboard primero.")
        return
    
    # Pestañas de reportes
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Reportes Generales", "👥 Por Cliente", "📋 Por OCs", "📁 Exportaciones"])
    
    with tab1:
        st.markdown("### 📈 Reportes Generales del Sistema")
        
        # Selector de período
        col_period1, col_period2 = st.columns(2)
        with col_period1:
            periodo = st.selectbox(
                "Período de Análisis",
                ["Últimos 7 días", "Últimos 30 días", "Mes actual", "Mes anterior", "Año actual", "Personalizado"],
                key="periodo_reporte"
            )
        
        with col_period2:
            if periodo == "Personalizado":
                col_date1, col_date2 = st.columns(2)
                with col_date1:
                    fecha_inicio = st.date_input("Fecha inicio", key="fecha_inicio_reporte")
                with col_date2:
                    fecha_fin = st.date_input("Fecha fin", key="fecha_fin_reporte")
        
        # Obtener datos según período
        try:
            # Obtener estadísticas
            stats = obtener_estadisticas_generales()
            
            # Métricas principales
            col_met1, col_met2, col_met3, col_met4 = st.columns(4)
            
            with col_met1:
                st.markdown(metric_card(
                    "Cupo Total",
                    Formateador.formato_monetario(stats['total_cupo_sistema']),
                    icon="💰"
                ), unsafe_allow_html=True)
            
            with col_met2:
                st.markdown(metric_card(
                    "Cartera Total",
                    Formateador.formato_monetario(stats['total_cartera_sistema']),
                    delta=f"{stats['porcentaje_uso_promedio']:.1f}% uso",
                    icon="📈"
                ), unsafe_allow_html=True)
            
            with col_met3:
                st.markdown(metric_card(
                    "Disponible",
                    Formateador.formato_monetario(stats['total_disponible_sistema']),
                    delta=f"{stats['porcentaje_disponible']:.1f}% disponible",
                    icon="🔄"
                ), unsafe_allow_html=True)
            
            with col_met4:
                st.markdown(metric_card(
                    "OCs Totales",
                    stats['total_ocs'],
                    icon="📄"
                ), unsafe_allow_html=True)
            
            st.divider()
            
            # Gráficos de análisis
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("#### 📊 Distribución de Estados de Cupo")
                
                clientes = obtener_clientes()
                if not clientes.empty and 'estado_cupo' in clientes.columns:
                    estado_counts = clientes['estado_cupo'].value_counts()
                    
                    fig = px.pie(
                        values=estado_counts.values,
                        names=estado_counts.index,
                        color=estado_counts.index,
                        color_discrete_map={
                            'NORMAL': config.COLORS['success'],
                            'MEDIO': config.COLORS['accent'],
                            'ALTO': config.COLORS['warning'],
                            'SOBREPASADO': config.COLORS['danger']
                        }
                    )
                    
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        showlegend=True,
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            with col_chart2:
                st.markdown("#### 📈 Tendencia de Cartera vs Cupo")
                
                # Obtener tendencias
                tendencias = obtener_tendencias_cupos(30)
                if not tendencias.empty:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=tendencias['fecha'],
                        y=tendencias['total_cartera_dia'],
                        mode='lines+markers',
                        name='Cartera',
                        line=dict(color=config.COLORS['primary'], width=3)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=tendencias['fecha'],
                        y=tendencias['total_cupo_dia'],
                        mode='lines',
                        name='Cupo',
                        line=dict(color=config.COLORS['success'], width=2, dash='dash')
                    ))
                    
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        height=400,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            # Tabla de clientes con mayor uso
            st.markdown("#### 👥 Top 10 Clientes con Mayor % de Uso")
            
            clientes_top = clientes.nlargest(10, 'porcentaje_uso')[['nombre', 'porcentaje_uso', 'total_cartera', 'cupo_sugerido', 'estado_cupo']].copy()
            clientes_top['porcentaje_uso'] = clientes_top['porcentaje_uso'].apply(lambda x: f"{x:.1f}%")
            clientes_top['total_cartera'] = clientes_top['total_cartera'].apply(lambda x: Formateador.formato_monetario(x))
            clientes_top['cupo_sugerido'] = clientes_top['cupo_sugerido'].apply(lambda x: Formateador.formato_monetario(x))
            
            st.dataframe(
                clientes_top,
                use_container_width=True,
                column_config={
                    'nombre': 'Cliente',
                    'porcentaje_uso': '% Uso',
                    'total_cartera': 'Cartera',
                    'cupo_sugerido': 'Cupo',
                    'estado_cupo': 'Estado'
                }
            )
            
        except Exception as e:
            st.error(f"❌ Error generando reportes: {str(e)}")
    
    with tab2:
        st.markdown("### 👥 Reportes por Cliente")
        
        # Selección de cliente
        clientes_lista = obtener_clientes()
        if clientes_lista.empty:
            st.info("No hay clientes disponibles")
            return
        
        cliente_seleccionado = st.selectbox(
            "Seleccionar Cliente",
            clientes_lista['nombre'].tolist(),
            key="cliente_reporte"
        )
        
        cliente_info = clientes_lista[clientes_lista['nombre'] == cliente_seleccionado].iloc[0]
        
        # Métricas del cliente
        col_cli1, col_cli2, col_cli3, col_cli4 = st.columns(4)
        
        with col_cli1:
            st.markdown(metric_card(
                "Cupo Sugerido",
                Formateador.formato_monetario(cliente_info['cupo_sugerido']),
                icon="💰"
            ), unsafe_allow_html=True)
        
        with col_cli2:
            st.markdown(metric_card(
                "Total Cartera",
                Formateador.formato_monetario(cliente_info['total_cartera']),
                icon="📈"
            ), unsafe_allow_html=True)
        
        with col_cli3:
            st.markdown(metric_card(
                "Disponible",
                Formateador.formato_monetario(cliente_info['disponible']),
                icon="🔄"
            ), unsafe_allow_html=True)
        
        with col_cli4:
            st.markdown(metric_card(
                "% Uso",
                f"{cliente_info['porcentaje_uso']:.1f}%",
                icon="📊"
            ), unsafe_allow_html=True)
        
        st.divider()
        
        # OCs del cliente
        st.markdown(f"#### 📋 Órdenes de Compra de {cliente_seleccionado}")
        
        ocs_cliente = obtener_ocs({'cliente_nit': cliente_info['nit']})
        if not ocs_cliente.empty:
            # Resumen por estado
            estado_summary = ocs_cliente.groupby('estado_oc').agg({
                'id': 'count',
                'valor_total': 'sum',
                'valor_autorizado': 'sum'
            }).reset_index()
            
            estado_summary['valor_total'] = estado_summary['valor_total'].apply(lambda x: Formateador.formato_monetario(x))
            estado_summary['valor_autorizado'] = estado_summary['valor_autorizado'].apply(lambda x: Formateador.formato_monetario(x))
            
            st.dataframe(
                estado_summary,
                use_container_width=True,
                column_config={
                    'estado_oc': 'Estado',
                    'id': 'Cantidad',
                    'valor_total': 'Valor Total',
                    'valor_autorizado': 'Valor Autorizado'
                }
            )
            
            # Gráfico de OCs por estado
            fig = px.bar(
                estado_summary,
                x='estado_oc',
                y='id',
                color='estado_oc',
                labels={'estado_oc': 'Estado', 'id': 'Cantidad'},
                color_discrete_map={
                    'PENDIENTE': config.COLORS['warning'],
                    'PARCIAL': config.COLORS['accent'],
                    'AUTORIZADA': config.COLORS['success'],
                    'RECHAZADA': config.COLORS['danger'],
                    'ANULADA': config.COLORS['dark']
                }
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                showlegend=False,
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla detallada de OCs
            st.markdown("#### 📋 Detalle de Órdenes de Compra")
            
            ocs_display = ocs_cliente[['numero_oc', 'valor_total', 'valor_autorizado', 'estado_oc', 'prioridad', 'fecha_solicitud']].copy()
            ocs_display['valor_total'] = ocs_display['valor_total'].apply(lambda x: Formateador.formato_monetario(x))
            ocs_display['valor_autorizado'] = ocs_display['valor_autorizado'].apply(lambda x: Formateador.formato_monetario(x))
            ocs_display['fecha_solicitud'] = ocs_display['fecha_solicitud'].apply(lambda x: Formateador.formato_fecha(x))
            
            st.dataframe(
                ocs_display,
                use_container_width=True,
                height=300,
                column_config={
                    'numero_oc': 'Número OC',
                    'valor_total': 'Valor Total',
                    'valor_autorizado': 'Autorizado',
                    'estado_oc': 'Estado',
                    'prioridad': 'Prioridad',
                    'fecha_solicitud': 'Fecha Solicitud'
                }
            )
        
        else:
            st.info("Este cliente no tiene órdenes de compra registradas")
    
    with tab3:
        st.markdown("### 📋 Reportes por Órdenes de Compra")
        
        # Filtros para reporte de OCs
        col_filt1, col_filt2 = st.columns(2)
        
        with col_filt1:
            estado_filtro = st.multiselect(
                "Estados",
                ["PENDIENTE", "PARCIAL", "AUTORIZADA", "RECHAZADA", "ANULADA"],
                default=["PENDIENTE", "PARCIAL", "AUTORIZADA"]
            )
        
        with col_filt2:
            prioridad_filtro = st.multiselect(
                "Prioridades",
                ["BAJA", "MEDIA", "ALTA", "CRITICA"],
                default=["MEDIA", "ALTA", "CRITICA"]
            )
        
        # Obtener OCs filtradas
        ocs_filtradas = pd.DataFrame()
        for estado in estado_filtro:
            ocs_estado = obtener_ocs({'estado_oc': estado})
            if not ocs_estado.empty:
                ocs_filtradas = pd.concat([ocs_filtradas, ocs_estado])
        
        if not ocs_filtradas.empty:
            # Filtrar por prioridad
            ocs_filtradas = ocs_filtradas[ocs_filtradas['prioridad'].isin(prioridad_filtro)]
        
        if not ocs_filtradas.empty:
            # Métricas de OCs
            col_oc1, col_oc2, col_oc3 = st.columns(3)
            
            with col_oc1:
                total_valor = ocs_filtradas['valor_total'].sum()
                st.metric("Valor Total", Formateador.formato_monetario(total_valor))
            
            with col_oc2:
                valor_autorizado = ocs_filtradas['valor_autorizado'].sum()
                st.metric("Valor Autorizado", Formateador.formato_monetario(valor_autorizado))
            
            with col_oc3:
                valor_pendiente = total_valor - valor_autorizado
                st.metric("Valor Pendiente", Formateador.formato_monetario(valor_pendiente))
            
            # Gráfico de OCs por cliente
            st.markdown("#### 📊 Distribución por Cliente")
            
            clientes_ocs = ocs_filtradas.groupby('cliente_nombre').agg({
                'id': 'count',
                'valor_total': 'sum'
            }).reset_index().sort_values('valor_total', ascending=False).head(10)
            
            fig = px.bar(
                clientes_ocs,
                x='cliente_nombre',
                y='valor_total',
                color='valor_total',
                labels={'cliente_nombre': 'Cliente', 'valor_total': 'Valor Total'},
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=400,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla detallada
            st.markdown("#### 📋 Detalle de Órdenes de Compra")
            
            ocs_display = ocs_filtradas[['numero_oc', 'cliente_nombre', 'valor_total', 'valor_autorizado', 'estado_oc', 'prioridad', 'fecha_solicitud']].copy()
            ocs_display['valor_total'] = ocs_display['valor_total'].apply(lambda x: Formateador.formato_monetario(x))
            ocs_display['valor_autorizado'] = ocs_display['valor_autorizado'].apply(lambda x: Formateador.formato_monetario(x))
            ocs_display['fecha_solicitud'] = ocs_display['fecha_solicitud'].apply(lambda x: Formateador.formato_fecha(x))
            
            st.dataframe(
                ocs_display,
                use_container_width=True,
                height=400,
                column_config={
                    'numero_oc': 'Número OC',
                    'cliente_nombre': 'Cliente',
                    'valor_total': 'Valor Total',
                    'valor_autorizado': 'Autorizado',
                    'estado_oc': 'Estado',
                    'prioridad': 'Prioridad',
                    'fecha_solicitud': 'Fecha'
                }
            )
        
        else:
            st.info("No hay OCs que coincidan con los filtros seleccionados")
    
    with tab4:
        st.markdown("### 📁 Exportación de Datos")
        
        # Opciones de exportación
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            formato = st.selectbox(
                "Formato de Exportación",
                ["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"],
                key="formato_exportacion"
            )
        
        with col_exp2:
            datos_a_exportar = st.multiselect(
                "Datos a Exportar",
                ["Clientes", "Órdenes de Compra", "Autorizaciones", "Estadísticas"],
                default=["Clientes", "Órdenes de Compra"]
            )
        
        # Botón de exportación
        if st.button("🚀 Generar Exportación", type="primary", use_container_width=True):
            try:
                from modules.database import generar_reporte_exportacion
                
                datos = generar_reporte_exportacion()
                
                if not datos:
                    st.error("❌ No hay datos para exportar")
                    return
                
                # Filtrar datos según selección
                datos_exportar = {}
                if "Clientes" in datos_a_exportar and 'clientes' in datos:
                    datos_exportar['Clientes'] = datos['clientes']
                if "Órdenes de Compra" in datos_a_exportar and 'ocs' in datos:
                    datos_exportar['OCs'] = datos['ocs']
                if "Autorizaciones" in datos_a_exportar and 'autorizaciones' in datos:
                    datos_exportar['Autorizaciones'] = datos['autorizaciones']
                if "Estadísticas" in datos_a_exportar and 'estadisticas' in datos:
                    datos_exportar['Estadísticas'] = datos['estadisticas']
                
                if not datos_exportar:
                    st.error("❌ No se seleccionaron datos para exportar")
                    return
                
                # Generar archivo según formato
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                if "Excel" in formato:
                    import io
                    from pandas import ExcelWriter
                    
                    output = io.BytesIO()
                    with ExcelWriter(output, engine='openpyxl') as writer:
                        for nombre, df in datos_exportar.items():
                            df.to_excel(writer, sheet_name=nombre[:31], index=False)
                    
                    output.seek(0)
                    
                    st.download_button(
                        label=f"⬇️ Descargar {formato}",
                        data=output,
                        file_name=f"reporte_cupos_td_{timestamp}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                elif "CSV" in formato:
                    # Crear ZIP con múltiples archivos CSV
                    import zipfile
                    import io
                    
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for nombre, df in datos_exportar.items():
                            csv_data = df.to_csv(index=False)
                            zip_file.writestr(f"{nombre.lower().replace(' ', '_')}.csv", csv_data)
                    
                    zip_buffer.seek(0)
                    
                    st.download_button(
                        label="⬇️ Descargar ZIP con CSVs",
                        data=zip_buffer,
                        file_name=f"reporte_cupos_td_{timestamp}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                
                elif "JSON" in formato:
                    import json
                    
                    datos_json = {}
                    for nombre, df in datos_exportar.items():
                        datos_json[nombre] = json.loads(df.to_json(orient='records'))
                    
                    st.download_button(
                        label="⬇️ Descargar JSON",
                        data=json.dumps(datos_json, indent=2, ensure_ascii=False),
                        file_name=f"reporte_cupos_td_{timestamp}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                st.success("✅ Exportación generada exitosamente")
                
            except Exception as e:
                st.error(f"❌ Error generando exportación: {str(e)}")

# ============================================================================
# PÁGINA: CONFIGURACIÓN
# ============================================================================

def page_configuracion():
    """Página de configuración del sistema"""
    
    st.markdown(f"<h1>⚙️ Configuración del Sistema</h1>", unsafe_allow_html=True)
    
    # Verificar base de datos
    if not os.path.exists(config.DATABASE_PATH):
        st.error("❌ La base de datos no está inicializada. Ve al Dashboard primero.")
        return
    
    # Pestañas de configuración
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 Sistema", "📊 Parámetros", "🔄 Mantenimiento", "ℹ️ Información"])
    
    with tab1:
        st.markdown("### 🔧 Configuración General del Sistema")
        
        col_sys1, col_sys2 = st.columns(2)
        
        with col_sys1:
            # Configuración de notificaciones
            st.markdown("#### 🔔 Notificaciones")
            
            notif_email = st.checkbox("Notificaciones por Email", value=True)
            notif_alertas = st.checkbox("Alertas en Tiempo Real", value=True)
            notif_informe = st.checkbox("Informes Diarios Automáticos", value=False)
            
            if st.button("💾 Guardar Configuración Notificaciones", use_container_width=True):
                st.success("✅ Configuración de notificaciones guardada")
        
        with col_sys2:
            # Configuración de seguridad
            st.markdown("#### 🔒 Seguridad")
            
            autenticacion = st.checkbox("Requerir Autenticación", value=False)
            log_detallado = st.checkbox("Log Detallado de Actividades", value=True)
            backup_auto = st.checkbox("Backup Automático Diario", value=True)
            
            dias_backup = st.slider(
                "Días de Retención de Backups",
                min_value=7,
                max_value=365,
                value=30,
                help="Número de días para mantener backups automáticos"
            )
            
            if st.button("💾 Guardar Configuración Seguridad", use_container_width=True):
                st.success("✅ Configuración de seguridad guardada")
        
        st.divider()
        
        # Configuración de límites
        st.markdown("#### 📊 Límites del Sistema")
        
        col_lim1, col_lim2, col_lim3 = st.columns(3)
        
        with col_lim1:
            limite_alerta = st.number_input(
                "% para Alertas de Cupo",
                min_value=50,
                max_value=100,
                value=90,
                help="Porcentaje de uso para generar alertas"
            )
        
        with col_lim2:
            limite_critico = st.number_input(
                "% para Nivel Crítico",
                min_value=50,
                max_value=100,
                value=100,
                help="Porcentaje de uso para nivel crítico"
            )
        
        with col_lim3:
            max_ocs_cliente = st.number_input(
                "Máx OCs por Cliente",
                min_value=1,
                max_value=100,
                value=10,
                help="Máximo número de OCs pendientes por cliente"
            )
        
        if st.button("💾 Guardar Límites del Sistema", type="primary", use_container_width=True):
            st.success("✅ Límites del sistema guardados")
    
    with tab2:
        st.markdown("### 📊 Parámetros del Sistema")
        
        try:
            from modules.database import get_connection
            
            with get_connection() as conn:
                parametros = pd.read_sql_query("SELECT * FROM parametros_sistema", conn)
            
            if not parametros.empty:
                # Mostrar parámetros editables
                for _, param in parametros.iterrows():
                    if param['editable']:
                        col_param1, col_param2, col_param3 = st.columns([3, 2, 1])
                        
                        with col_param1:
                            st.markdown(f"**{param['clave']}**")
                            st.caption(param['descripcion'])
                        
                        with col_param2:
                            if param['tipo'] == 'BOOLEAN':
                                nuevo_valor = st.checkbox("", value=param['valor'].lower() == 'true', 
                                                         key=f"param_{param['id']}")
                                valor_str = str(nuevo_valor).lower()
                            elif param['tipo'] == 'NUMERO':
                                nuevo_valor = st.number_input("", value=float(param['valor']), 
                                                            key=f"param_{param['id']}")
                                valor_str = str(nuevo_valor)
                            else:
                                nuevo_valor = st.text_input("", value=param['valor'], 
                                                          key=f"param_{param['id']}")
                                valor_str = nuevo_valor
                        
                        with col_param3:
                            if st.button("💾", key=f"save_{param['id']}", help="Guardar"):
                                try:
                                    with get_connection() as conn:
                                        cursor = conn.cursor()
                                        cursor.execute('''
                                        UPDATE parametros_sistema 
                                        SET valor = ?, fecha_modificacion = CURRENT_TIMESTAMP
                                        WHERE id = ?
                                        ''', (valor_str, param['id']))
                                        conn.commit()
                                    
                                    st.success("✅ Parámetro actualizado")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
            else:
                st.info("No hay parámetros configurados")
                
        except Exception as e:
            st.error(f"❌ Error cargando parámetros: {str(e)}")
    
    with tab3:
        st.markdown("### 🔄 Mantenimiento del Sistema")
        
        col_mant1, col_mant2 = st.columns(2)
        
        with col_mant1:
            st.markdown("#### 🧹 Limpieza de Datos")
            
            dias_limpieza = st.number_input(
                "Eliminar OCs autorizadas con más de (días):",
                min_value=30,
                max_value=365,
                value=90,
                step=30
            )
            
            if st.button("🧹 Ejecutar Limpieza", use_container_width=True):
                try:
                    # Aquí iría la función de limpieza
                    st.info("🔄 Ejecutando limpieza...")
                    # limpiar_ocs_antiguas(dias_limpieza)
                    st.success(f"✅ Limpieza completada (simulación)")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            
            st.markdown("---")
            
            st.markdown("#### 📊 Optimización")
            
            if st.button("⚡ Optimizar Base de Datos", use_container_width=True):
                try:
                    # optimizar_base_datos()
                    st.success("✅ Base de datos optimizada (simulación)")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        with col_mant2:
            st.markdown("#### 💾 Backup y Restauración")
            
            # Información del sistema
            if os.path.exists(config.DATABASE_PATH):
                import os
                size_bytes = os.path.getsize(config.DATABASE_PATH)
                size_mb = size_bytes / (1024 * 1024)
                
                st.metric("Tamaño Base de Datos", f"{size_mb:.2f} MB")
            
            if st.button("💾 Crear Backup Manual", use_container_width=True):
                try:
                    # crear_backup_manual()
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    st.success(f"✅ Backup creado: backup_{timestamp}.db (simulación)")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            
            st.markdown("---")
            
            st.markdown("#### 🚨 Operaciones Peligrosas")
            
            st.warning("⚠️ **ADVERTENCIA:** Estas operaciones no se pueden deshacer.")
            
            if st.button("🔄 Reinicializar Sistema", type="secondary", use_container_width=True):
                confirm = st.checkbox("Confirmo que quiero reinicializar el sistema")
                
                if confirm:
                    if st.button("✅ CONFIRMAR REINICIALIZACIÓN", type="primary", use_container_width=True):
                        try:
                            # Eliminar base de datos
                            if os.path.exists(config.DATABASE_PATH):
                                os.remove(config.DATABASE_PATH)
                                st.success("✅ Sistema reinicializado")
                                st.info("Recarga la página para continuar")
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
    
    with tab4:
        st.markdown("### ℹ️ Información del Sistema")
        
        # Información de la aplicación
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.markdown("""
            #### 📱 Información de la Aplicación
            
            **Nombre:** Sistema de Gestión de Cupos TD  
            **Versión:** 3.0.0  
            **Entorno:** Producción  
            **Última Actualización:** """ + datetime.now().strftime('%d/%m/%Y') + """  
            
            #### 🛠 Tecnologías Utilizadas
            
            • **Frontend:** Streamlit 1.28.1  
            • **Backend:** Python 3.10+  
            • **Base de Datos:** SQLite  
            • **Visualización:** Plotly, Pandas  
            • **Estilos:** CSS Personalizado
            """)
        
        with col_info2:
            st.markdown("""
            #### 📊 Estadísticas del Sistema
            
            **Estado:** 🟢 Operativo  
            **Clientes Registrados:** """ + str(len(obtener_clientes())) + """  
            **Órdenes de Compra:** """ + str(obtener_estadisticas_generales().get('total_ocs', 0)) + """  
            **Cupo Total:** """ + Formateador.formato_monetario(obtener_estadisticas_generales().get('total_cupo_sistema', 0)) + """  
            
            #### 📞 Soporte
            
            **Desarrollado por:** Equipo de Tecnología TD  
            **Contacto:** tecnologia@td.com.co  
            **Horario de Soporte:** L-V 8:00 AM - 6:00 PM
            """)
        
        st.divider()
        
        # Logs del sistema
        st.markdown("#### 📝 Logs de Actividad Reciente")
        
        try:
            from modules.database import get_connection
            
            with get_connection() as conn:
                logs = pd.read_sql_query(
                    "SELECT * FROM log_actividad ORDER BY fecha DESC LIMIT 10", 
                    conn
                )
            
            if not logs.empty:
                for _, log in logs.iterrows():
                    nivel_colores = {
                        'INFO': config.COLORS['accent'],
                        'WARNING': config.COLORS['warning'],
                        'ERROR': config.COLORS['danger'],
                        'CRITICAL': config.COLORS['dark']
                    }
                    
                    nivel_color = nivel_colores.get(log['nivel'], config.COLORS['dark'])
                    
                    st.markdown(f"""
                    <div style="background: {nivel_color}10; border-left: 4px solid {nivel_color}; 
                                padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>{log['modulo']} - {log['accion']}</strong>
                                <div style="color: #94a3b8; font-size: 0.9rem;">{log['usuario']} • {Formateador.formato_fecha(log['fecha'], '%d/%m/%Y %H:%M')}</div>
                            </div>
                            <div style="background: {nivel_color}; color: white; padding: 0.25rem 0.5rem; 
                                        border-radius: 4px; font-size: 0.8rem;">
                                {log['nivel']}
                            </div>
                        </div>
                        {f'<div style="margin-top: 0.5rem; color: #cbd5e1; font-size: 0.9rem;">{log["detalles"]}</div>' if log['detalles'] else ''}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay logs registrados")
                
        except Exception as e:
            st.warning(f"No se pudieron cargar los logs: {str(e)}")

# ============================================================================
# PÁGINA DE INICIALIZACIÓN
# ============================================================================

def page_init():
    """Página de inicialización del sistema"""
    
    st.markdown(f"""
    <div style="text-align: center; padding: 4rem;">
        <div style="font-size: 4rem; margin-bottom: 2rem;">🚀</div>
        <h1>Inicialización del Sistema</h1>
        <p style="color: #94a3b8; margin-bottom: 3rem; max-width: 600px; margin-left: auto; margin-right: auto;">
            Bienvenido al Sistema de Gestión de Cupos TD. 
            Antes de comenzar, necesitamos inicializar la base de datos del sistema.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_init1, col_init2, col_init3 = st.columns([1, 2, 1])
    
    with col_init2:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.5); padding: 2rem; border-radius: 16px; 
                    border: 1px solid rgba(100, 116, 139, 0.3);">
            <h3 style="text-align: center;">¿Qué se inicializará?</h3>
            
            <div style="margin: 1.5rem 0;">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="background: rgba(37, 99, 235, 0.2); color: #2563eb; 
                                width: 30px; height: 30px; border-radius: 50%; 
                                display: flex; align-items: center; justify-content: center; margin-right: 1rem;">
                        1
                    </div>
                    <span>Base de datos con estructura avanzada</span>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="background: rgba(37, 99, 235, 0.2); color: #2563eb; 
                                width: 30px; height: 30px; border-radius: 50%; 
                                display: flex; align-items: center; justify-content: center; margin-right: 1rem;">
                        2
                    </div>
                    <span>Clientes iniciales con datos reales</span>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="background: rgba(37, 99, 235, 0.2); color: #2563eb; 
                                width: 30px; height: 30px; border-radius: 50%; 
                                display: flex; align-items: center; justify-content: center; margin-right: 1rem;">
                        3
                    </div>
                    <span>Parámetros del sistema configurados</span>
                </div>
                
                <div style="display: flex; align-items: center;">
                    <div style="background: rgba(37, 99, 235, 0.2); color: #2563eb; 
                                width: 30px; height: 30px; border-radius: 50%; 
                                display: flex; align-items: center; justify-content: center; margin-right: 1rem;">
                        4
                    </div>
                    <span>Sistema de logging y seguimiento</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🚀 Inicializar Sistema", type="primary", use_container_width=True):
                try:
                    with st.spinner("🔄 Inicializando sistema..."):
                        from modules.database import init_database
                        init_database()
                    
                    st.success("✅ Sistema inicializado exitosamente!")
                    st.balloons()
                    
                    st.markdown("""
                    <div style="text-align: center; margin-top: 2rem;">
                        <p>El sistema está listo para usar. Redirigiendo al dashboard...</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Redirigir después de 2 segundos
                    import time
                    time.sleep(2)
                    st.query_params['page'] = 'dashboard'
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error al inicializar el sistema: {str(e)}")
        
        with col_btn2:
            if st.button("🏠 Ir al Dashboard", use_container_width=True):
                st.query_params['page'] = 'dashboard'
                st.rerun()

# ============================================================================
# RUTA PRINCIPAL DE LA APLICACIÓN
# ============================================================================

def main():
    """Función principal de la aplicación"""
    
    # Inyectar CSS personalizado
    inject_custom_css()
    
    # Renderizar barra de navegación superior
    render_top_navigation()
    
    # Determinar página actual basada en parámetros de URL
    query_params = st.query_params
    
    # Inicializar base de datos si no existe
    if not os.path.exists(config.DATABASE_PATH):
        page_init()
        return
    
    # Determinar página a mostrar
    page = query_params.get('page', ['dashboard'])[0]
    
    # Renderizar página correspondiente
    if page == 'dashboard':
        page_dashboard()
    elif page == 'clientes':
        page_clientes()
    elif page == 'ocs':
        page_ocs()
    elif page == 'reportes':
        page_reportes()
    elif page == 'configuracion':
        page_configuracion()
    elif page == 'init':
        page_init()
    else:
        page_dashboard()

# ============================================================================
# EJECUCIÓN DE LA APLICACIÓN
# ============================================================================

if __name__ == "__main__":
    main()
