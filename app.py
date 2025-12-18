"""
SISTEMA DE GESTIÓN DE CUPOS TD - VERSIÓN COMPLETA CON NAVBAR MODERNO
Todas las páginas funcionan con st.switch_page()
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import sqlite3
import sys
from pathlib import Path

# ============================================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Sistema de Cupos TD",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# NAVBAR MODERNO (Basado en tu modelo)
# ============================================================================

def modern_navbar():
    with st.sidebar:
        st.markdown("### 🧭 Navegación Rápida")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 Dashboard", use_container_width=True):
                st.switch_page("app.py")

        with col2:
            if st.button("👥 Clientes", use_container_width=True):
                st.switch_page("pages/2_clientes.py")

        col3, col4 = st.columns(2)
        with col3:
            if st.button("📋 Órdenes Compra", use_container_width=True):
                st.switch_page("pages/3_ocs.py")

        with col4:
            if st.button("📊 Reportes", use_container_width=True):
                st.switch_page("pages/4_reportes.py")

        if st.button("⚙️ Configuración", use_container_width=True):
            st.switch_page("pages/5_configuracion.py")

        st.markdown("---")
        st.markdown("### 🔐 Sesión")

        st.info("🟢 Conectado como Administrador")

        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.success("Sesión cerrada exitosamente")
            st.session_state.clear()
            st.switch_page("app.py")

    # --- NAVBAR (CSS + HTML) ---
    st.markdown("""
    <style>
        .modern-navbar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            padding: 0.8rem 0;
            margin-bottom: 0;
            border-bottom: 1px solid rgba(0, 102, 204, 0.1);
            position: relative;
            z-index: 1000;
        }
        
        .nav-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1rem;
        }
        
        .nav-title {
            color: #1a1a1a;
            font-size: 1.4rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            font-family: 'Inter', sans-serif;
        }
        
        .nav-title span {
            background: linear-gradient(135deg, #0066cc, #00a8ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .nav-user {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .user-info {
            text-align: right;
        }
        
        .user-name {
            font-weight: 600;
            color: #1a1a1a;
            font-size: 0.9rem;
        }
        
        .user-role {
            color: #666;
            font-size: 0.8rem;
        }
        
        .css-1d391kg {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border-right: 1px solid rgba(0, 102, 204, 0.1);
        }
        
        @media (max-width: 768px) {
            .nav-content {
                flex-direction: column;
                gap: 1rem;
            }
            
            .nav-user {
                width: 100%;
                justify-content: center;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="modern-navbar">
        <div class="nav-content">
            <div class="nav-title">Sistema de <span>Cupos TD</span></div>
            <div class="nav-user">
                <div class="user-info">
                    <div class="user-name">Usuario: Administrador</div>
                    <div class="user-role">Gestión de Cupos • Conectado</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# CONFIGURACIÓN DEL SISTEMA
# ============================================================================

class Config:
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / 'data'
    DATABASE_PATH = DATA_DIR / 'cupos_td.db'
    
    CLIENTES_INICIALES = [
        {
            'nit': '901212102',
            'nombre': 'AUNA COLOMBIA S.A.S',
            'total_cartera': 19493849830,
            'cupo_sugerido': 21693849830,
            'disponible': 2200000000
        },
        {
            'nit': '890905166',
            'nombre': 'EMPRESA SOCIAL DEL ESTADO HOSPITAL MENTAL DE ANTIOQ',
            'total_cartera': 7397192942,
            'cupo_sugerido': 7500000000,
            'disponible': 102807058
        },
        {
            'nit': '900249425',
            'nombre': 'PHARMASAN S.A.S',
            'total_cartera': 5710785209,
            'cupo_sugerido': 5910785209,
            'disponible': 200000000
        },
        {
            'nit': '900748052',
            'nombre': 'NEUROM SAS',
            'total_cartera': 5184247623,
            'cupo_sugerido': 5500000000,
            'disponible': 315752377
        },
        {
            'nit': '800241602',
            'nombre': 'FUNDACION COLOMBIANA DE CANCEROLOGIA CLINICA VIDA',
            'total_cartera': 3031469552,
            'cupo_sugerido': 3500000000,
            'disponible': 468530448
        },
        {
            'nit': '890985122',
            'nombre': 'COOPERATIVA DE HOSPITALES DE ANTIOQUIA',
            'total_cartera': 1221931405,
            'cupo_sugerido': 1500000000,
            'disponible': 278068595
        },
        {
            'nit': '811038014',
            'nombre': 'GRUPO ONCOLOGICO INTERNACIONAL S.A.',
            'total_cartera': 806853666,
            'cupo_sugerido': 900000000,
            'disponible': 93146334
        }
    ]

config = Config()

# ============================================================================
# FUNCIONES DE BASE DE DATOS (COMPARTIDAS)
# ============================================================================

def init_database():
    """Inicializa la base de datos"""
    try:
        os.makedirs('data', exist_ok=True)
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nit TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            total_cartera REAL DEFAULT 0,
            cupo_sugerido REAL DEFAULT 0,
            disponible REAL DEFAULT 0,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT 1
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ocs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_nit TEXT,
            numero_oc TEXT UNIQUE NOT NULL,
            valor_total REAL NOT NULL,
            valor_autorizado REAL DEFAULT 0,
            estado TEXT DEFAULT 'PENDIENTE',
            tipo TEXT DEFAULT 'NORMAL',
            prioridad TEXT DEFAULT 'MEDIA',
            descripcion TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_nit) REFERENCES clientes(nit)
        )
        ''')
        
        cursor.execute("SELECT COUNT(*) FROM clientes")
        if cursor.fetchone()[0] == 0:
            for cliente in config.CLIENTES_INICIALES:
                cursor.execute('''
                INSERT INTO clientes (nit, nombre, total_cartera, cupo_sugerido, disponible)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    cliente['nit'],
                    cliente['nombre'],
                    cliente['total_cartera'],
                    cliente['cupo_sugerido'],
                    cliente['disponible']
                ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Error inicializando BD: {e}")
        return False

def get_clientes():
    """Obtiene todos los clientes"""
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        query = '''
        SELECT 
            c.*,
            CASE 
                WHEN c.total_cartera > c.cupo_sugerido THEN 'SOBREPASADO'
                WHEN (c.total_cartera * 100.0 / c.cupo_sugerido) > 90 THEN 'ALTO'
                WHEN (c.total_cartera * 100.0 / c.cupo_sugerido) > 70 THEN 'MEDIO'
                ELSE 'NORMAL'
            END as estado_cupo,
            ROUND((c.total_cartera * 100.0 / c.cupo_sugerido), 2) as porcentaje_uso
        FROM clientes c
        WHERE c.activo = 1
        ORDER BY c.nombre
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def get_ocs():
    """Obtiene todas las OCs"""
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        query = '''
        SELECT o.*, c.nombre as cliente_nombre 
        FROM ocs o
        LEFT JOIN clientes c ON o.cliente_nit = c.nit
        ORDER BY o.fecha_registro DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def crear_oc(data):
    """Crea una nueva OC"""
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO ocs 
        (cliente_nit, numero_oc, valor_total, estado, tipo, prioridad, descripcion)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['cliente_nit'],
            data['numero_oc'],
            data['valor_total'],
            data.get('estado', 'PENDIENTE'),
            data.get('tipo', 'NORMAL'),
            data.get('prioridad', 'MEDIA'),
            data.get('descripcion', '')
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error creando OC: {e}")
        return False

def actualizar_cliente(nit, data):
    """Actualiza un cliente"""
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if 'nombre' in data:
            updates.append("nombre = ?")
            params.append(data['nombre'])
        
        if 'total_cartera' in data:
            updates.append("total_cartera = ?")
            params.append(data['total_cartera'])
        
        if 'cupo_sugerido' in data:
            updates.append("cupo_sugerido = ?")
            params.append(data['cupo_sugerido'])
        
        if updates:
            cursor.execute("SELECT total_cartera, cupo_sugerido FROM clientes WHERE nit = ?", (nit,))
            row = cursor.fetchone()
            
            nueva_cartera = data.get('total_cartera', row[0])
            nuevo_cupo = data.get('cupo_sugerido', row[1])
            nuevo_disponible = nuevo_cupo - nueva_cartera
            
            updates.append("disponible = ?")
            params.append(nuevo_disponible)
            
            updates.append("fecha_actualizacion = CURRENT_TIMESTAMP")
            params.append(nit)
            
            query = f"UPDATE clientes SET {', '.join(updates)} WHERE nit = ?"
            cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error actualizando cliente: {e}")
        return False

# ============================================================================
# FUNCIONES DE FORMATEO
# ============================================================================

def formato_monetario(valor):
    """Formatea valores monetarios"""
    if pd.isna(valor):
        return "$0"
    return f"${float(valor):,.0f}"

def formato_porcentaje(valor):
    """Formatea porcentajes"""
    if pd.isna(valor):
        return "0%"
    return f"{float(valor):.1f}%"

# ============================================================================
# PÁGINA PRINCIPAL (DASHBOARD)
# ============================================================================

def main():
    """Función principal - Dashboard"""
    
    # Mostrar navbar
    modern_navbar()
    
    # Título principal
    st.title("🏠 Dashboard Principal")
    st.markdown("---")
    
    # Verificar base de datos
    if not os.path.exists(config.DATABASE_PATH):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: white; 
                        border-radius: 16px; border: 1px solid #e0e0e0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🚀</div>
                <h2>Bienvenido al Sistema de Cupos TD</h2>
                <p style="color: #666; margin-bottom: 2rem;">
                    Sistema profesional para gestión y seguimiento de cupos de crédito
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔧 Inicializar Sistema", type="primary", use_container_width=True):
                if init_database():
                    st.success("✅ Sistema inicializado correctamente")
                    st.rerun()
        return
    
    # Obtener datos
    clientes = get_clientes()
    ocs = get_ocs()
    
    if clientes.empty:
        st.info("No hay clientes registrados")
        return
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cupo = clientes['cupo_sugerido'].sum()
        st.metric("Cupo Total", formato_monetario(total_cupo))
    
    with col2:
        total_cartera = clientes['total_cartera'].sum()
        st.metric("Cartera Total", formato_monetario(total_cartera))
    
    with col3:
        total_disponible = clientes['disponible'].sum()
        st.metric("Disponible Total", formato_monetario(total_disponible))
    
    with col4:
        porcentaje_uso = (total_cartera / total_cupo * 100) if total_cupo > 0 else 0
        st.metric("% Uso Total", formato_porcentaje(porcentaje_uso))
    
    st.divider()
    
    # Sección 1: Resumen de clientes
    st.subheader("👥 Resumen de Clientes")
    
    # Métricas de clientes
    col_c1, col_c2, col_c3 = st.columns(3)
    
    with col_c1:
        total_clientes = len(clientes)
        st.metric("Total Clientes", total_clientes)
    
    with col_c2:
        clientes_criticos = len(clientes[clientes['estado_cupo'].isin(['SOBREPASADO', 'ALTO'])])
        st.metric("Clientes Críticos", clientes_criticos)
    
    with col_c3:
        uso_promedio = clientes['porcentaje_uso'].mean()
        st.metric("% Uso Promedio", formato_porcentaje(uso_promedio))
    
    # Tabla de clientes
    df_display = clientes[['nombre', 'total_cartera', 'cupo_sugerido', 'disponible', 'porcentaje_uso', 'estado_cupo']].copy()
    df_display['total_cartera'] = df_display['total_cartera'].apply(formato_monetario)
    df_display['cupo_sugerido'] = df_display['cupo_sugerido'].apply(formato_monetario)
    df_display['disponible'] = df_display['disponible'].apply(formato_monetario)
    df_display['porcentaje_uso'] = df_display['porcentaje_uso'].apply(formato_porcentaje)
    
    # Estilo para estado
    def estilo_estado(val):
        if val == 'SOBREPASADO':
            return 'background-color: #ef4444; color: white; font-weight: bold; padding: 5px; border-radius: 4px;'
        elif val == 'ALTO':
            return 'background-color: #f59e0b; color: white; font-weight: bold; padding: 5px; border-radius: 4px;'
        elif val == 'MEDIO':
            return 'background-color: #7c3aed; color: white; font-weight: bold; padding: 5px; border-radius: 4px;'
        else:
            return 'background-color: #10b981; color: white; font-weight: bold; padding: 5px; border-radius: 4px;'
    
    styled_df = df_display.style.map(estilo_estado, subset=['estado_cupo'])
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'nombre': 'Cliente',
            'total_cartera': 'Cartera',
            'cupo_sugerido': 'Cupo',
            'disponible': 'Disponible',
            'porcentaje_uso': '% Uso',
            'estado_cupo': 'Estado'
        }
    )
    
    st.divider()
    
    # Sección 2: Gráficos
    st.subheader("📊 Visualización de Datos")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Gráfico de distribución por estado
        if 'estado_cupo' in clientes.columns:
            estado_counts = clientes['estado_cupo'].value_counts()
            
            fig1 = go.Figure(data=[go.Pie(
                labels=estado_counts.index,
                values=estado_counts.values,
                hole=.4,
                marker_colors=['#ef4444', '#f59e0b', '#7c3aed', '#10b981'],
                textinfo='label+percent'
            )])
            
            fig1.update_layout(
                title_text="Distribución por Estado",
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig1, use_container_width=True)
    
    with col_chart2:
        # Top 5 clientes por cartera
        top_clientes = clientes.nlargest(5, 'total_cartera')
        
        fig2 = px.bar(
            top_clientes,
            x='nombre',
            y='total_cartera',
            title='Top 5 Clientes por Cartera',
            labels={'nombre': 'Cliente', 'total_cartera': 'Cartera'},
            color='total_cartera',
            color_continuous_scale='Viridis'
        )
        
        fig2.update_layout(
            height=400,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    st.divider()
    
    # Sección 3: Acciones rápidas
    st.subheader("⚡ Acciones Rápidas")
    
    col_act1, col_act2, col_act3 = st.columns(3)
    
    with col_act1:
        if st.button("👥 Ver Todos los Clientes", use_container_width=True):
            st.switch_page("pages/2_clientes.py")
    
    with col_act2:
        if st.button("📋 Ver Todas las OCs", use_container_width=True):
            st.switch_page("pages/3_ocs.py")
    
    with col_act3:
        if st.button("📊 Generar Reporte", use_container_width=True):
            st.switch_page("pages/4_reportes.py")

# ============================================================================
# EJECUCIÓN
# ============================================================================

if __name__ == "__main__":
    main()
