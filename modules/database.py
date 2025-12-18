"""
SISTEMA EJECUTIVO DE GESTIÓN DE CARTERA - TODODROGAS
Panel de Control Corporativo con Visualización de Datos Avanzada
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# Configurar ruta para módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==================== CONFIGURACIÓN DEL TEMA EJECUTIVO ====================

def configure_executive_theme():
    """Configura el tema ejecutivo corporativo"""
    st.markdown("""
    <style>
        /* TEMA EJECUTIVO - AZUL CORPORATIVO */
        .stApp {
            background: linear-gradient(135deg, #ffffff 0%, #f5f9ff 100%);
            font-family: 'Inter', 'Segoe UI', 'Roboto', system-ui, sans-serif;
        }
        
        /* HEADERS CORPORATIVOS */
        .corporate-header {
            color: #003366 !important;
            font-weight: 800 !important;
            letter-spacing: -0.5px;
            border-bottom: 4px solid #0066cc;
            padding-bottom: 10px;
            margin-bottom: 25px !important;
            font-size: 2.5rem !important;
            text-transform: uppercase;
        }
        
        .section-header {
            color: #004080 !important;
            font-weight: 700 !important;
            font-size: 1.6rem !important;
            margin: 30px 0 15px 0 !important;
            border-left: 5px solid #0066cc;
            padding-left: 15px;
        }
        
        /* MÉTRICAS EJECUTIVAS */
        .metric-card {
            background: white;
            border-radius: 15px;
            padding: 25px 20px;
            margin: 10px 0;
            box-shadow: 0 8px 25px rgba(0, 51, 102, 0.08);
            border: 1px solid rgba(0, 102, 204, 0.1);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 35px rgba(0, 102, 204, 0.15);
            border-color: rgba(0, 102, 204, 0.3);
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 5px;
            height: 100%;
            background: linear-gradient(to bottom, #0066cc, #004499);
        }
        
        .metric-label {
            color: #666666;
            font-size: 0.95rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        
        .metric-value {
            color: #003366;
            font-size: 2.2rem;
            font-weight: 800;
            line-height: 1;
            margin: 5px 0;
        }
        
        .metric-change {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-top: 8px;
        }
        
        .metric-positive {
            background: linear-gradient(135deg, #e6f7ff, #b3e0ff);
            color: #0066cc;
        }
        
        .metric-negative {
            background: linear-gradient(135deg, #ffe6e6, #ffb3b3);
            color: #cc0000;
        }
        
        /* NAVBAR EJECUTIVA */
        .executive-navbar {
            background: linear-gradient(135deg, #003366 0%, #002244 100%);
            padding: 1.5rem 2.5rem;
            margin: -1rem -1rem 2rem -1rem;
            border-radius: 0 0 25px 25px;
            box-shadow: 0 10px 30px rgba(0, 51, 102, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        .executive-navbar::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(0, 102, 204, 0.3) 0%, transparent 70%);
        }
        
        .navbar-logo {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .logo-icon {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #00a8ff, #0066cc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 4px 6px rgba(0, 102, 204, 0.3));
        }
        
        .logo-text {
            color: white;
            font-size: 1.8rem;
            font-weight: 800;
            letter-spacing: -0.5px;
        }
        
        .logo-subtitle {
            color: rgba(255, 255, 255, 0.85);
            font-size: 1.1rem;
            font-weight: 500;
        }
        
        .navbar-info {
            display: flex;
            align-items: center;
            gap: 25px;
        }
        
        .user-badge {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            padding: 10px 20px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .user-name {
            color: white;
            font-weight: 700;
            font-size: 1.1rem;
        }
        
        .user-role {
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
        }
        
        /* BOTONES EJECUTIVOS */
        .stButton > button {
            background: linear-gradient(135deg, #0066cc, #004499);
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            padding: 12px 25px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 6px 15px rgba(0, 102, 204, 0.2) !important;
            letter-spacing: 0.3px;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 10px 25px rgba(0, 102, 204, 0.3) !important;
            background: linear-gradient(135deg, #0052a3, #003366) !important;
        }
        
        /* TARJETAS DE ACCIÓN */
        .action-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin: 15px 0;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.05);
            border: 2px solid #e6f0ff;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .action-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 102, 204, 0.15);
            border-color: #0066cc;
        }
        
        .action-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
            display: block;
        }
        
        .action-title {
            color: #003366;
            font-weight: 700;
            font-size: 1.2rem;
            margin-bottom: 10px;
        }
        
        .action-desc {
            color: #666666;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        
        /* TABLAS EJECUTIVAS */
        .dataframe {
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.05) !important;
            border: 1px solid #e6f0ff !important;
        }
        
        .dataframe th {
            background: linear-gradient(135deg, #003366, #0066cc) !important;
            color: white !important;
            font-weight: 700 !important;
            padding: 15px !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.9rem !important;
        }
        
        .dataframe td {
            padding: 12px 15px !important;
            border-bottom: 1px solid #f0f7ff !important;
        }
        
        .dataframe tr:hover {
            background-color: #f0f7ff !important;
        }
        
        /* PROGRESS BARS */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #0066cc, #00a8ff) !important;
            border-radius: 10px !important;
        }
        
        /* CARD DE DATOS */
        .data-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.04);
            border-left: 5px solid #0066cc;
        }
        
        .data-card-title {
            color: #003366;
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .data-card-value {
            color: #0066cc;
            font-size: 1.8rem;
            font-weight: 700;
            line-height: 1;
        }
        
        /* GRID EJECUTIVO */
        .executive-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin: 25px 0;
        }
        
        /* BADGES DE ESTADO */
        .status-badge {
            display: inline-block;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-pending {
            background: linear-gradient(135deg, #ffd166, #ffb347);
            color: #8a5700;
        }
        
        .status-approved {
            background: linear-gradient(135deg, #06d6a0, #0cb48c);
            color: #00563f;
        }
        
        .status-partial {
            background: linear-gradient(135deg, #118ab2, #0a6c8f);
            color: white;
        }
        
        /* OCULTAR ELEMENTOS DEFAULT */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display:none;}
        
        /* SCROLLBAR */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f7ff;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #0066cc, #004499);
            border-radius: 10px;
        }
        
        /* RESPONSIVE */
        @media (max-width: 768px) {
            .executive-grid {
                grid-template-columns: 1fr;
            }
            
            .navbar-info {
                flex-direction: column;
                gap: 10px;
            }
            
            .metric-value {
                font-size: 1.8rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# ==================== NAVBAR EJECUTIVA ====================

def create_executive_navbar():
    """Crea la navbar ejecutiva corporativa"""
    current_time = datetime.now().strftime("%d/%m/%Y • %H:%M")
    
    st.markdown(f"""
    <div class="executive-navbar">
        <div style="display: flex; justify-content: space-between; align-items: center; position: relative; z-index: 10;">
            <div class="navbar-logo">
                <div class="logo-icon">💊</div>
                <div>
                    <div class="logo-text">TODODROGAS • EXECUTIVE DASHBOARD</div>
                    <div class="logo-subtitle">Control Integral de Cartera y Cupos • V 3.0</div>
                </div>
            </div>
            
            <div class="navbar-info">
                <div class="user-badge">
                    <div class="user-name">👤 ADMINISTRADOR DEL SISTEMA</div>
                    <div class="user-role">Rol: Superusuario • Acceso Total</div>
                </div>
                <div style="
                    background: rgba(255, 255, 255, 0.1);
                    padding: 10px 20px;
                    border-radius: 15px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                ">
                    <div style="color: white; font-weight: 600; font-size: 0.9rem;">⏰ HORA ACTUAL</div>
                    <div style="color: #00a8ff; font-weight: 700; font-size: 1.1rem;">{current_time}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== SIDEBAR EJECUTIVO ====================

def create_executive_sidebar():
    """Crea la sidebar ejecutiva"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem; padding: 1.5rem; background: linear-gradient(135deg, #0066cc, #004499); border-radius: 15px;">
            <div style="font-size: 2rem; margin-bottom: 10px;">🧭</div>
            <div style="color: white; font-size: 1.2rem; font-weight: 700;">NAVEGACIÓN PRINCIPAL</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botones principales de navegación
        nav_items = [
            ("📊 PANEL DE CONTROL", "🏠", "#f0f7ff"),
            ("👥 GESTIÓN DE CLIENTES", "👤", "#e6f2ff"),
            ("📋 ÓRDENES DE COMPRA", "📄", "#d9e8ff"),
            ("💰 CARTERA ACTIVA", "💳", "#cce0ff"),
            ("📈 REPORTES AVANZADOS", "📊", "#bfd9ff"),
            ("⚙️ CONFIGURACIÓN", "🔧", "#b3d1ff")
        ]
        
        for item, icon, color in nav_items:
            if st.button(f"{icon} {item}", use_container_width=True, 
                        type="primary" if item == "📊 PANEL DE CONTROL" else "secondary"):
                if item == "📋 ÓRDENES DE COMPRA":
                    st.switch_page("pages/3_ocs.py")
        
        st.markdown("---")
        
        # Acciones rápidas
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #003366, #002244);
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
        ">
            <div style="color: white; font-weight: 700; margin-bottom: 15px;">⚡ ACCIONES INMEDIATAS</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ NUEVA OC", use_container_width=True):
                st.session_state['crear_oc_modal'] = True
                st.switch_page("pages/3_ocs.py")
        
        with col2:
            if st.button("📤 EXPORTAR", use_container_width=True):
                st.info("Exportando datos...")
        
        st.markdown("---")
        
        # Resumen ejecutivo
        st.markdown("### 🎯 RESUMEN EJECUTIVO")
        
        metrics_data = [
            ("Clientes Activos", "7", "+0%"),
            ("Cupo Total", "$71.5B", "+2.3%"),
            ("Cartera Activa", "$48.2B", "-1.2%"),
            ("OCs Pendientes", "12", "+3")
        ]
        
        for label, value, change in metrics_data:
            st.metric(label=label, value=value, delta=change)
        
        st.markdown("---")
        
        # Estado del sistema
        st.markdown("### 🟢 ESTADO DEL SISTEMA")
        st.progress(85, text="Operativo al 85%")
        
        # Botón de cierre
        if st.button("🚪 CERRAR SESIÓN", use_container_width=True, type="secondary"):
            st.success("Sesión cerrada exitosamente")
            st.rerun()

# ==================== FUNCIONES DE DATOS EJECUTIVOS ====================

def get_executive_metrics():
    """Obtiene métricas ejecutivas para el dashboard"""
    return {
        'cupo_total': 71500000000,  # 71.5B
        'cartera_activa': 48200000000,  # 48.2B
        'ocs_pendientes': 12,
        'disponibilidad': 67.4,
        'clientes_activos': 7,
        'clientes_alerta': 1,
        'clientes_sobrepasados': 0,
        'cartera_vencida': 3250000000  # 3.25B
    }

def get_client_data():
    """Obtiene datos de clientes para visualización"""
    clientes = [
        {
            'nit': '901212102',
            'nombre': 'AUNA COLOMBIA S.A.S',
            'cupo': 21693849830,
            'cartera': 19493849830,
            'uso': 89.8,
            'estado': 'ALERTA'
        },
        {
            'nit': '890905166',
            'nombre': 'HOSPITAL MENTAL DE ANTIOQUIA',
            'cupo': 7500000000,
            'cartera': 7397192942,
            'uso': 98.6,
            'estado': 'ALERTA'
        },
        {
            'nit': '900249425',
            'nombre': 'PHARMASAN S.A.S',
            'cupo': 5910785209,
            'cartera': 5710785209,
            'uso': 96.6,
            'estado': 'ALERTA'
        },
        {
            'nit': '900748052',
            'nombre': 'NEUROM SAS',
            'cupo': 5500000000,
            'cartera': 5184247623,
            'uso': 94.3,
            'estado': 'ALERTA'
        },
        {
            'nit': '800241602',
            'nombre': 'FUNDACIÓN COLOMBIANA DE CANCEROLOGÍA',
            'cupo': 3500000000,
            'cartera': 3031469552,
            'uso': 86.6,
            'estado': 'NORMAL'
        }
    ]
    return pd.DataFrame(clientes)

def get_recent_ocs():
    """Obtiene OCs recientes"""
    ocs = [
        {
            'numero': 'OC-2024-015',
            'cliente': 'AUNA COLOMBIA S.A.S',
            'valor': 2500000000,
            'estado': 'PENDIENTE',
            'fecha': 'Hoy, 10:30 AM',
            'vencimiento': '30/04/2024'
        },
        {
            'numero': 'OC-2024-014',
            'cliente': 'HOSPITAL MENTAL DE ANTIOQUIA',
            'valor': 1200000000,
            'estado': 'AUTORIZADA',
            'fecha': 'Ayer, 15:45 PM',
            'vencimiento': '25/04/2024'
        },
        {
            'numero': 'OC-2024-013',
            'cliente': 'PHARMASAN S.A.S',
            'valor': 850000000,
            'estado': 'PARCIAL',
            'fecha': '15/03/2024',
            'vencimiento': '20/04/2024'
        },
        {
            'numero': 'OC-2024-012',
            'cliente': 'NEUROM SAS',
            'valor': 600000000,
            'estado': 'PENDIENTE',
            'fecha': '14/03/2024',
            'vencimiento': '15/05/2024'
        }
    ]
    return pd.DataFrame(ocs)

# ==================== COMPONENTES DE VISUALIZACIÓN ====================

def create_metric_card(label, value, change=None, change_type="positive"):
    """Crea una tarjeta de métrica ejecutiva"""
    change_html = ""
    if change:
        change_class = "metric-positive" if change_type == "positive" else "metric-negative"
        change_html = f'<div class="metric-change {change_class}">{change}</div>'
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {change_html}
    </div>
    """

def create_action_card(icon, title, description, action_key):
    """Crea una tarjeta de acción"""
    return f"""
    <div class="action-card" onclick="handleAction('{action_key}')">
        <div class="action-icon">{icon}</div>
        <div class="action-title">{title}</div>
        <div class="action-desc">{description}</div>
    </div>
    """

def format_currency(value):
    """Formatea valores monetarios"""
    if value >= 1e9:
        return f"${value/1e9:,.1f}B"
    elif value >= 1e6:
        return f"${value/1e6:,.1f}M"
    else:
        return f"${value:,.0f}"

# ==================== DASHBOARD EJECUTIVO ====================

def show_executive_dashboard():
    """Muestra el dashboard ejecutivo"""
    
    # Obtener datos
    metrics = get_executive_metrics()
    clientes_df = get_client_data()
    ocs_df = get_recent_ocs()
    
    # Header ejecutivo
    create_executive_navbar()
    
    # Título principal
    st.markdown('<h1 class="corporate-header">📊 PANEL DE CONTROL EJECUTIVO</h1>', unsafe_allow_html=True)
    
    # Indicador ejecutivo
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #e6f2ff, #d1e6ff);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 30px;
        border-left: 6px solid #0066cc;
    ">
        <div style="display: flex; align-items: center; gap: 20px;">
            <div style="font-size: 3rem;">🎯</div>
            <div style="flex: 1;">
                <div style="color: #003366; font-weight: 800; font-size: 1.3rem; margin-bottom: 8px;">
                    SISTEMA DE GESTIÓN INTEGRAL - TODODROGAS
                </div>
                <div style="color: #666; font-size: 1.1rem; line-height: 1.5;">
                    Monitoreo en tiempo real de cartera, cupos y órdenes de compra con análisis predictivo y control ejecutivo.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ========== SECCIÓN 1: MÉTRICAS CLAVE ==========
    st.markdown('<h2 class="section-header">📈 MÉTRICAS CLAVE DEL SISTEMA</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card(
            "CUPO TOTAL ASIGNADO",
            format_currency(metrics['cupo_total']),
            "↑ +2.3%",
            "positive"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "CARTERA ACTIVA",
            format_currency(metrics['cartera_activa']),
            "↓ -1.2%",
            "negative"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "OCs PENDIENTES",
            str(metrics['ocs_pendientes']),
            "↑ +3",
            "positive"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "DISPONIBILIDAD",
            f"{metrics['disponibilidad']}%",
            "↑ +1.8%",
            "positive"
        ), unsafe_allow_html=True)
    
    # ========== SECCIÓN 2: ACCIONES INMEDIATAS ==========
    st.markdown('<h2 class="section-header">⚡ ACCIONES INMEDIATAS</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ CREAR NUEVA OC", use_container_width=True, type="primary"):
            st.session_state['show_oc_creator'] = True
            st.switch_page("pages/3_ocs.py")
    
    with col2:
        if st.button("👥 GESTIONAR CLIENTES", use_container_width=True):
            st.switch_page("pages/2_clientes.py")
    
    with col3:
        if st.button("📊 VER REPORTES", use_container_width=True):
            st.switch_page("pages/4_reportes.py")
    
    with col4:
        if st.button("🔄 ACTUALIZAR DATOS", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # ========== SECCIÓN 3: VISIÓN GENERAL DE CLIENTES ==========
    st.markdown('<h2 class="section-header">👥 VISIÓN GENERAL DE CLIENTES</h2>', unsafe_allow_html=True)
    
    # Gráfico de uso de cupos
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Crear gráfico de barras
            fig = go.Figure()
            
            for _, row in clientes_df.head(5).iterrows():
                fig.add_trace(go.Bar(
                    name=row['nombre'][:20] + "...",
                    x=[row['uso']],
                    y=[''],
                    orientation='h',
                    marker=dict(
                        color='#0066cc' if row['uso'] < 90 else ('#ff9900' if row['uso'] < 100 else '#cc0000'),
                        line=dict(color='white', width=2)
                    ),
                    text=[f"{row['uso']}%"],
                    textposition='inside',
                    textfont=dict(color='white', size=12, weight='bold')
                ))
            
            fig.update_layout(
                title="<b>USO DE CUPO POR CLIENTE (TOP 5)</b>",
                title_font=dict(size=16, color='#003366'),
                height=300,
                plot_bgcolor='white',
                paper_bgcolor='white',
                showlegend=False,
                xaxis=dict(
                    title="PORCENTAJE DE USO",
                    title_font=dict(size=12, color='#666'),
                    range=[0, 110],
                    gridcolor='#f0f7ff',
                    zerolinecolor='#e6f0ff'
                ),
                yaxis=dict(
                    showticklabels=False,
                    gridcolor='#f0f7ff'
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Resumen de estados
            st.markdown("""
            <div class="data-card">
                <div class="data-card-title">ESTADO DE CLIENTES</div>
                <div style="margin: 15px 0;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin: 10px 0;">
                        <span>🟢 NORMAL</span>
                        <span style="font-weight: 700; color: #06d6a0;">4</span>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: space-between; margin: 10px 0;">
                        <span>🟠 ALERTA</span>
                        <span style="font-weight: 700; color: #ff9900;">3</span>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: space-between; margin: 10px 0;">
                        <span>🔴 SOBREPASADO</span>
                        <span style="font-weight: 700; color: #cc0000;">0</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Cartera vencida
            st.markdown(f"""
            <div class="data-card">
                <div class="data-card-title">CARTERA VENCIDA</div>
                <div class="data-card-value">{format_currency(metrics['cartera_vencida'])}</div>
                <div style="margin-top: 10px;">
                    <div style="background: #ffe6e6; height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="background: #cc0000; width: 15%; height: 100%;"></div>
                    </div>
                    <div style="color: #cc0000; font-size: 0.9rem; margin-top: 5px;">15% del total</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ========== SECCIÓN 4: ACTIVIDAD RECIENTE ==========
    st.markdown('<h2 class="section-header">🔄 ACTIVIDAD RECIENTE DEL SISTEMA</h2>', unsafe_allow_html=True)
    
    # Tabla de OCs recientes
    if not ocs_df.empty:
        # Formatear datos para la tabla
        display_df = ocs_df.copy()
        display_df['valor'] = display_df['valor'].apply(lambda x: f"${x/1e9:,.1f}B" if x >= 1e9 else f"${x/1e6:,.1f}M")
        display_df['estado'] = display_df['estado'].apply(
            lambda x: f'<span class="status-badge status-{x.lower()}">{x}</span>'
        )
        
        # Mostrar tabla
        st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== SECCIÓN 5: INDICADORES DE PERFORMANCE ==========
    st.markdown('<h2 class="section-header">📊 INDICADORES DE PERFORMANCE</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="data-card">
            <div class="data-card-title">ROTACIÓN DE CARTERA</div>
            <div class="data-card-value">45 DÍAS</div>
            <div style="color: #06d6a0; font-weight: 600; margin-top: 10px;">↓ -5 días</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="data-card">
            <div class="data-card-title">TIEMPO RESPUESTA OC</div>
            <div class="data-card-value">2.3 DÍAS</div>
            <div style="color: #06d6a0; font-weight: 600; margin-top: 10px;">↓ -0.7 días</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="data-card">
            <div class="data-card-title">EFICIENCIA COBRANZA</div>
            <div class="data-card-value">94.2%</div>
            <div style="color: #0066cc; font-weight: 600; margin-top: 10px;">↑ +2.1%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ========== PIE DE PÁGINA ==========
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("""
        <div style="color: #666; font-size: 0.9rem; line-height: 1.5;">
            <strong>📋 Sistema de Gestión de Cartera - Tododrogas</strong><br>
            Versión 3.0 • Última actualización: """ + datetime.now().strftime("%d/%m/%Y %H:%M") + """<br>
            © 2024 Departamento de Automatización • Todos los derechos reservados
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <div style="color: #0066cc; font-weight: 700; font-size: 0.9rem;">🟢 SISTEMA ACTIVO</div>
            <div style="color: #666; font-size: 0.8rem;">Operativo 24/7</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center;">
            <div style="color: #0066cc; font-weight: 700; font-size: 0.9rem;">📞 SOPORTE</div>
            <div style="color: #666; font-size: 0.8rem;">Ext. 5021</div>
        </div>
        """, unsafe_allow_html=True)

# ==================== INICIALIZACIÓN ====================

def init_session_state():
    """Inicializa el estado de la sesión"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = True
    if 'username' not in st.session_state:
        st.session_state.username = "Administrador Ejecutivo"
    if 'user_role' not in st.session_state:
        st.session_state.user_role = "Superusuario"

# ==================== APLICACIÓN PRINCIPAL ====================

def main():
    """Función principal de la aplicación ejecutiva"""
    
    # Configuración de página
    st.set_page_config(
        page_title="Tododrogas Executive Dashboard",
        page_icon="💊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Aplicar tema ejecutivo
    configure_executive_theme()
    
    # Inicializar estado
    init_session_state()
    
    # Crear sidebar ejecutivo
    create_executive_sidebar()
    
    # Mostrar dashboard ejecutivo
    show_executive_dashboard()

# ==================== EJECUCIÓN ====================

if __name__ == "__main__":
    main()
