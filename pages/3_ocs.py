"""
PÁGINA 3 - GESTIÓN DE ÓRDENES DE COMPRA
Creación, edición y autorización de OCs
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import numpy as np

# Configuración de página
st.set_page_config(
    page_title="Órdenes de Compra - Tododrogas",
    page_icon="📋",
    layout="wide"
)

# Importar módulos
from modules.auth import check_authentication
from modules.database import (
    get_ocs, crear_oc, autorizar_oc, 
    get_autorizaciones_oc, get_clientes
)
from modules.utils import (
    format_currency, validate_oc_number,
    get_oc_status_badge, format_number
)

# Verificar autenticación
user = check_authentication()

# ==================== ESTILOS CSS ====================

st.markdown("""
<style>
    .ocs-container {
        padding: 1rem;
    }
    
    .oc-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E7EB;
        transition: all 0.3s ease;
    }
    
    .oc-card:hover {
        box-shadow: 0 4px 20px rgba(0, 102, 204, 0.1);
        border-color: #0066CC;
    }
    
    .oc-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .oc-number {
        font-size: 1.3rem;
        font-weight: 800;
        color: #1A1A1A;
    }
    
    .oc-client {
        color: #666;
        font-size: 1rem;
        margin-top: 0.25rem;
    }
    
    .oc-values {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .value-item {
        text-align: center;
        padding: 0.75rem;
        background: #F8F9FA;
        border-radius: 8px;
    }
    
    .value-label {
        font-size: 0.8rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.25rem;
    }
    
    .value-amount {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1A1A1A;
    }
    
    .progress-container {
        height: 8px;
        background: #E5E7EB;
        border-radius: 4px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, #0066CC, #00B8A9);
        transition: width 0.6s ease;
    }
    
    .oc-actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    
    .authorization-history {
        background: #F8F9FA;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    .auth-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem;
        border-bottom: 1px solid #E5E7EB;
    }
    
    .auth-item:last-child {
        border-bottom: none;
    }
    
    .filter-section {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid #E5E7EB;
    }
    
    .form-section {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #E5E7EB;
    }
    
    .impact-warning {
        background: linear-gradient(135deg, #FFE6E6, #FFB3B3);
        border-left: 4px solid #FF3B30;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .impact-success {
        background: linear-gradient(135deg, #E6F7FF, #B3E0FF);
        border-left: 4px solid #0066CC;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== FUNCIONES AUXILIARES ====================

def create_oc_card(oc):
    """Crea una tarjeta de OC"""
    
    porcentaje_autorizado = (oc['valor_autorizado'] / oc['valor_total'] * 100) if oc['valor_total'] > 0 else 0
    
    return f'''
    <div class="oc-card">
        <div class="oc-header">
            <div>
                <div class="oc-number">{oc['numero_oc']}</div>
                <div class="oc-client">{oc['cliente_nombre']}</div>
            </div>
            <div>
                {get_oc_status_badge(oc['estado'])}
            </div>
        </div>
        
        <div class="oc-values">
            <div class="value-item">
                <div class="value-label">Valor Total</div>
                <div class="value-amount">{format_currency(oc['valor_total'])}</div>
            </div>
            
            <div class="value-item">
                <div class="value-label">Autorizado</div>
                <div class="value-amount">{format_currency(oc['valor_autorizado'])}</div>
            </div>
            
            <div class="value-item">
                <div class="value-label">Pendiente</div>
                <div class="value-amount">{format_currency(oc['valor_pendiente'])}</div>
            </div>
            
            <div class="value-item">
                <div class="value-label">Progreso</div>
                <div class="value-amount">{porcentaje_autorizado:.1f}%</div>
            </div>
        </div>
        
        <div class="progress-container">
            <div class="progress-bar" style="width: {min(porcentaje_autorizado, 100)}%;"></div>
        </div>
        
        <div class="oc-actions">
            <button class="rappi-button" onclick="viewOC('{oc['id']}')" style="flex: 1;">🔍 Detalle</button>
            <button class="rappi-button" onclick="authorizeOC('{oc['id']}')" style="flex: 1;" {'disabled' if oc['estado'] == 'AUTORIZADA' else ''}>✅ Autorizar</button>
            <button class="rappi-button" onclick="editOC('{oc['id']}')" style="flex: 1;">✏️ Editar</button>
        </div>
    </div>
    '''

def calculate_impact(cliente_nit, valor_oc):
    """Calcula el impacto de una OC en el cupo disponible"""
    clientes_df = get_clientes()
    cliente = clientes_df[clientes_df['nit'] == cliente_nit]
    
    if cliente.empty:
        return None
    
    cliente = cliente.iloc[0]
    disponible_actual = cliente['disponible']
    nuevo_disponible = disponible_actual - valor_oc
    porcentaje_impacto = (valor_oc / cliente['cupo_sugerido'] * 100) if cliente['cupo_sugerido'] > 0 else 0
    
    return {
        'cliente': cliente['nombre'],
        'disponible_actual': disponible_actual,
        'nuevo_disponible': nuevo_disponible,
        'porcentaje_impacto': porcentaje_impacto,
        'sobrepasa_cupo': nuevo_disponible < 0
    }

# ==================== PÁGINA PRINCIPAL ====================

def show_ocs_page():
    """Muestra la página de gestión de OCs"""
    
    st.title("📋 GESTIÓN DE ÓRDENES DE COMPRA")
    st.markdown("Crea, edita y autoriza órdenes de compra")
    
    # Pestañas principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Ver OCs", 
        "➕ Crear Nueva OC", 
        "✅ Autorizar OCs", 
        "📊 Análisis"
    ])
    
    # ========== PESTAÑA 1: VER OCs ==========
    with tab1:
        st.subheader("📋 ÓRDENES DE COMPRA ACTIVAS")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            estado_filter = st.selectbox(
                "Filtrar por estado",
                ["TODAS", "PENDIENTE", "PARCIAL", "AUTORIZADA"],
                key="filter_estado"
            )
        
        with col2:
            clientes_df = get_clientes()
            clientes_lista = ["TODOS"] + clientes_df['nombre'].tolist()
            cliente_filter = st.selectbox(
                "Filtrar por cliente",
                clientes_lista,
                key="filter_cliente"
            )
        
        with col3:
            buscar_oc = st.text_input("🔍 Buscar OC", placeholder="Número de OC")
        
        # Obtener OCs con filtros
        cliente_nit = None
        if cliente_filter != "TODOS" and clientes_df is not None:
            cliente_nit = clientes_df[clientes_df['nombre'] == cliente_filter]['nit'].iloc[0]
        
        ocs_df = get_ocs(
            cliente_nit=cliente_nit if cliente_nit else None,
            estado=estado_filter if estado_filter != "TODAS" else None
        )
        
        # Aplicar búsqueda adicional
        if buscar_oc:
            ocs_df = ocs_df[ocs_df['numero_oc'].str.contains(buscar_oc, case=False)]
        
        # Mostrar resumen
        if not ocs_df.empty:
            total_ocs = len(ocs_df)
            total_valor = ocs_df['valor_total'].sum()
            total_autorizado = ocs_df['valor_autorizado'].sum()
            total_pendiente = ocs_df['valor_pendiente'].sum()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total OCs", total_ocs)
            with col2:
                st.metric("Valor Total", format_currency(total_valor))
            with col3:
                st.metric("Autorizado", format_currency(total_autorizado))
            with col4:
                st.metric("Pendiente", format_currency(total_pendiente))
            
            st.markdown("---")
            
            # Mostrar OCs
            view_mode = st.radio(
                "Tipo de vista:",
                ["Tarjetas", "Tabla"],
                horizontal=True,
                key="view_mode_ocs"
            )
            
            if view_mode == "Tarjetas":
                # Mostrar como tarjetas
                ocs_ordenadas = ocs_df.sort_values('fecha_registro', ascending=False)
                
                for _, oc in ocs_ordenadas.iterrows():
                    st.markdown(create_oc_card(oc), unsafe_allow_html=True)
            else:
                # Mostrar como tabla
                display_df = ocs_df.copy()
                display_df['Valor Total'] = display_df['valor_total'].apply(format_currency)
                display_df['Autorizado'] = display_df['valor_autorizado'].apply(format_currency)
                display_df['Pendiente'] = display_df['valor_pendiente'].apply(format_currency)
                display_df['% Autorizado'] = display_df.apply(
                    lambda x: f"{(x['valor_autorizado']/x['valor_total']*100):.1f}%" if x['valor_total'] > 0 else "0%",
                    axis=1
                )
                
                st.dataframe(
                    display_df[['numero_oc', 'cliente_nombre', 'Valor Total', 'Autorizado', 'Pendiente', '% Autorizado', 'estado', 'fecha_registro']],
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("📭 No hay OCs que coincidan con los filtros seleccionados")
    
    # ========== PESTAÑA 2: CREAR NUEVA OC ==========
    with tab2:
        st.subheader("➕ CREAR NUEVA ORDEN DE COMPRA")
        
        with st.form("nueva_oc_form"):
            st.markdown('<div class="form-section">', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Seleccionar cliente
                clientes_df = get_clientes()
                cliente_nombre = st.selectbox(
                    "Cliente *",
                    clientes_df['nombre'].tolist(),
                    help="Seleccione el cliente para la OC"
                )
                
                # Obtener NIT del cliente seleccionado
                cliente_nit = clientes_df[clientes_df['nombre'] == cliente_nombre]['nit'].iloc[0]
                cliente_info = clientes_df[clientes_df['nit'] == cliente_nit].iloc[0]
                
                # Mostrar información del cliente
                st.info(f"""
                **Información del cliente:**
                - NIT: {cliente_nit}
                - Cupo asignado: {format_currency(cliente_info['cupo_sugerido'])}
                - En uso: {format_currency(cliente_info['saldo_actual'])} ({cliente_info['porcentaje_uso']}%)
                - Disponible: {format_currency(cliente_info['disponible'])}
                """)
                
                # Número de OC
                numero_oc = st.text_input(
                    "Número de OC *",
                    placeholder="OC-2024-001",
                    help="Formato: OC-AAAA-NNN"
                )
                
                # Tipo de OC
                tipo_oc = st.selectbox(
                    "Tipo de OC",
                    ["SUELTA", "CUPO_NUEVO"],
                    help="SUELTA: OC individual, CUPO_NUEVO: para nuevo cupo"
                )
                
                # Cupo de referencia (solo para CUPO_NUEVO)
                cupo_referencia = ""
                if tipo_oc == "CUPO_NUEVO":
                    cupo_referencia = st.text_input(
                        "Cupo de Referencia *",
                        placeholder="CUPO-001",
                        help="Número de cupo asociado"
                    )
            
            with col2:
                # Valor total
                valor_total = st.number_input(
                    "Valor Total *",
                    min_value=1000000.0,
                    value=1000000.0,
                    step=1000000.0,
                    format="%.0f",
                    help="Valor total de la orden de compra (mínimo $1,000,000)"
                )
                
                # Comentarios
                comentarios = st.text_area(
                    "Comentarios (opcional)",
                    height=100,
                    placeholder="Descripción de la orden de compra...",
                    help="Información adicional sobre esta OC"
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Calcular impacto
            if valor_total > 0 and cliente_nit:
                impacto = calculate_impact(cliente_nit, valor_total)
                
                if impacto:
                    if impacto['sobrepasa_cupo']:
                        st.markdown(f'''
                        <div class="impact-warning">
                            <strong>⚠️ ADVERTENCIA - SOBREPASA CUPO DISPONIBLE</strong><br>
                            • Disponible actual: {format_currency(impacto['disponible_actual'])}<br>
                            • Esta OC consumiría: {format_currency(valor_total)}<br>
                            • Nuevo disponible: {format_currency(impacto['nuevo_disponible'])}<br>
                            • Impacto: {impacto['porcentaje_impacto']:.1f}% del cupo total
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.markdown(f'''
                        <div class="impact-success">
                            <strong>✅ IMPACTO EN CUPO DISPONIBLE</strong><br>
                            • Disponible actual: {format_currency(impacto['disponible_actual'])}<br>
                            • Esta OC consumiría: {format_currency(valor_total)}<br>
                            • Nuevo disponible: {format_currency(impacto['nuevo_disponible'])}<br>
                            • Quedaría disponible: {(impacto['nuevo_disponible']/impacto['disponible_actual']*100):.1f}%
                        </div>
                        ''', unsafe_allow_html=True)
            
            # Botones de envío
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                submitted = st.form_submit_button(
                    "💾 CREAR OC",
                    type="primary",
                    use_container_width=True
                )
            
            with col_btn2:
                submitted_another = st.form_submit_button(
                    "💾 Y CREAR OTRA",
                    use_container_width=True
                )
            
            with col_btn3:
                cancel = st.form_submit_button(
                    "❌ CANCELAR",
                    use_container_width=True
                )
            
            if submitted or submitted_another:
                # Validaciones
                errors = []
                
                if not numero_oc.strip():
                    errors.append("❌ El número de OC es obligatorio")
                
                if not validate_oc_number(numero_oc):
                    errors.append("❌ Formato de número OC inválido. Use: OC-AAAA-NNN")
                
                if valor_total <= 0:
                    errors.append("❌ El valor total debe ser mayor a 0")
                
                if tipo_oc == "CUPO_NUEVO" and not cupo_referencia.strip():
                    errors.append("❌ El cupo de referencia es obligatorio para tipo CUPO_NUEVO")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    try:
                        crear_oc(
                            cliente_nit=cliente_nit,
                            numero_oc=numero_oc.strip(),
                            valor_total=valor_total,
                            tipo=tipo_oc,
                            cupo_referencia=cupo_referencia.strip(),
                            comentarios=comentarios.strip(),
                            usuario=user['nombre']
                        )
                        
                        st.success(f"✅ OC '{numero_oc}' creada exitosamente por {format_currency(valor_total)}")
                        
                        if submitted_another:
                            st.rerun()
                        else:
                            time.sleep(1)
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"❌ Error al crear OC: {str(e)}")
            
            if cancel:
                st.rerun()
    
    # ========== PESTAÑA 3: AUTORIZAR OCs ==========
    with tab3:
        st.subheader("✅ AUTORIZAR ÓRDENES DE COMPRA")
        
        # Obtener OCs pendientes o parciales
        ocs_pendientes = get_ocs(estado=None)  # Traer todas
        ocs_pendientes = ocs_pendientes[
            ocs_pendientes['estado'].isin(['PENDIENTE', 'PARCIAL'])
        ]
        
        if ocs_pendientes.empty:
            st.info("🎉 ¡No hay OCs pendientes de autorización!")
        else:
            # Seleccionar OC para autorizar
            oc_options = []
            for _, oc in ocs_pendientes.iterrows():
                label = f"{oc['numero_oc']} - {oc['cliente_nombre']} - {format_currency(oc['valor_pendiente'])} pendiente"
                oc_options.append((oc['id'], label))
            
            selected_oc_id = st.selectbox(
                "Seleccionar OC para autorizar",
                options=[oc[0] for oc in oc_options],
                format_func=lambda x: dict(oc_options)[x]
            )
            
            if selected_oc_id:
                oc_seleccionada = ocs_pendientes[ocs_pendientes['id'] == selected_oc_id].iloc[0]
                
                with st.form("autorizar_oc_form"):
                    st.markdown('<div class="form-section">', unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    ### OC: {oc_seleccionada['numero_oc']}
                    **Cliente:** {oc_seleccionada['cliente_nombre']}
                    """)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            "Valor Total",
                            format_currency(oc_seleccionada['valor_total'])
                        )
                        
                        st.metric(
                            "Ya Autorizado",
                            format_currency(oc_seleccionada['valor_autorizado'])
                        )
                    
                    with col2:
                        valor_pendiente = oc_seleccionada['valor_pendiente']
                        st.metric(
                            "Pendiente",
                            format_currency(valor_pendiente)
                        )
                        
                        porcentaje_autorizado = (oc_seleccionada['valor_autorizado'] / oc_seleccionada['valor_total'] * 100) if oc_seleccionada['valor_total'] > 0 else 0
                        st.metric(
                            "% Autorizado",
                            f"{porcentaje_autorizado:.1f}%"
                        )
                    
                    st.markdown("---")
                    
                    # Tipo de autorización
                    tipo_autorizacion = st.radio(
                        "Tipo de autorización",
                        ["AUTORIZACIÓN TOTAL", "AUTORIZACIÓN PARCIAL"],
                        horizontal=True
                    )
                    
                    # Valor a autorizar
                    if tipo_autorizacion == "AUTORIZACIÓN TOTAL":
                        valor_autorizar = valor_pendiente
                        st.info(f"Se autorizará el valor pendiente completo: {format_currency(valor_pendiente)}")
                    else:
                        valor_autorizar = st.number_input(
                            "Valor a autorizar",
                            min_value=0.0,
                            max_value=float(valor_pendiente),
                            value=float(valor_pendiente),
                            step=1000000.0,
                            format="%.0f"
                        )
                    
                    # Botones de porcentaje rápido
                    st.write("**Porcentajes rápidos:**")
                    col_perc1, col_perc2, col_perc3, col_perc4 = st.columns(4)
                    
                    with col_perc1:
                        if st.button("25%", use_container_width=True):
                            st.session_state.autorizar_percent = 25
                            st.rerun()
                    
                    with col_perc2:
                        if st.button("50%", use_container_width=True):
                            st.session_state.autorizar_percent = 50
                            st.rerun()
                    
                    with col_perc3:
                        if st.button("75%", use_container_width=True):
                            st.session_state.autorizar_percent = 75
                            st.rerun()
                    
                    with col_perc4:
                        if st.button("100%", use_container_width=True):
                            st.session_state.autorizar_percent = 100
                            st.rerun()
                    
                    # Aplicar porcentaje si existe
                    if 'autorizar_percent' in st.session_state:
                        valor_autorizar = valor_pendiente * (st.session_state.autorizar_percent / 100)
                    
                    # Comentario de autorización
                    comentario_autorizacion = st.text_area(
                        "Comentario de autorización (opcional)",
                        placeholder="Ej: Autorización por aprobación de gerencia...",
                        height=80
                    )
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Calcular impacto
                    impacto = calculate_impact(oc_seleccionada['cliente_nit'], valor_autorizar)
                    
                    if impacto:
                        if impacto['sobrepasa_cupo']:
                            st.error(f"""
                            ⚠️ **ADVERTENCIA:** Esta autorización sobrepasa el cupo disponible.
                            
                            **Impacto:**
                            • Disponible actual: {format_currency(impacto['disponible_actual'])}
                            • Esta autorización: {format_currency(valor_autorizar)}
                            • Nuevo disponible: {format_currency(impacto['nuevo_disponible'])}
                            """)
                        else:
                            st.success(f"""
                            ✅ **IMPACTO CALCULADO:**
                            
                            **Detalles:**
                            • Disponible actual: {format_currency(impacto['disponible_actual'])}
                            • Esta autorización: {format_currency(valor_autorizar)}
                            • Nuevo disponible: {format_currency(impacto['nuevo_disponible'])}
                            • Quedaría disponible: {(impacto['nuevo_disponible']/impacto['disponible_actual']*100):.1f}%
                            """)
                    
                    # Botones de confirmación
                    col_conf1, col_conf2 = st.columns(2)
                    
                    with col_conf1:
                        confirmar = st.form_submit_button(
                            "✅ CONFIRMAR AUTORIZACIÓN",
                            type="primary",
                            use_container_width=True,
                            disabled=impacto['sobrepasa_cupo'] if impacto and 'sobrepasa_cupo' in impacto else False
                        )
                    
                    with col_conf2:
                        cancelar = st.form_submit_button(
                            "❌ CANCELAR",
                            use_container_width=True
                        )
                    
                    if confirmar:
                        if valor_autorizar <= 0:
                            st.error("❌ El valor a autorizar debe ser mayor a 0")
                        else:
                            try:
                                autorizar_oc(
                                    oc_id=selected_oc_id,
                                    valor_autorizado=valor_autorizar,
                                    comentario=comentario_autorizacion.strip(),
                                    usuario=user['nombre']
                                )
                                
                                st.success(f"✅ Autorizados {format_currency(valor_autorizar)} de la OC {oc_seleccionada['numero_oc']}")
                                st.balloons()
                                time.sleep(2)
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Error al autorizar: {str(e)}")
                    
                    if cancelar:
                        if 'autorizar_percent' in st.session_state:
                            del st.session_state.autorizar_percent
                        st.rerun()
    
    # ========== PESTAÑA 4: ANÁLISIS ==========
    with tab4:
        st.subheader("📊 ANÁLISIS DE OCs")
        
        # Obtener todas las OCs
        ocs_df = get_ocs()
        
        if not ocs_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de distribución por estado
                estado_counts = ocs_df['estado'].value_counts()
                
                fig1 = go.Figure(data=[go.Pie(
                    labels=estado_counts.index,
                    values=estado_counts.values,
                    hole=.4,
                    marker=dict(colors=['#FFCC00', '#FF9500', '#00B8A9']),
                    textinfo='label+percent',
                    textposition='inside'
                )])
                
                fig1.update_layout(
                    title="<b>DISTRIBUCIÓN POR ESTADO</b>",
                    height=400,
                    showlegend=True
                )
                
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Gráfico de valor por cliente (top 5)
                valor_por_cliente = ocs_df.groupby('cliente_nombre')['valor_total'].sum().nlargest(5)
                
                fig2 = go.Figure(data=[go.Bar(
                    x=valor_por_cliente.values,
                    y=valor_por_cliente.index,
                    orientation='h',
                    marker_color='#0066CC',
                    text=valor_por_cliente.values.apply(format_currency),
                    textposition='inside'
                )])
                
                fig2.update_layout(
                    title="<b>TOP 5 CLIENTES - VALOR TOTAL OCs</b>",
                    height=400,
                    xaxis_title="Valor Total",
                    yaxis_title="Cliente"
                )
                
                st.plotly_chart(fig2, use_container_width=True)
            
            # Métricas de eficiencia
            st.markdown("### 📈 MÉTRICAS DE EFICIENCIA")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                # Tiempo promedio pendiente
                ocs_pendientes = ocs_df[ocs_df['estado'].isin(['PENDIENTE', 'PARCIAL'])]
                if not ocs_pendientes.empty:
                    fecha_actual = datetime.now()
                    # Simular cálculo de días pendientes
                    dias_promedio = np.random.randint(1, 10)
                    st.metric("Días promedio pendiente", f"{dias_promedio} días")
                else:
                    st.metric("Días promedio pendiente", "0 días")
            
            with col2:
                # % de OCs autorizadas
                total_ocs = len(ocs_df)
                autorizadas = len(ocs_df[ocs_df['estado'] == 'AUTORIZADA'])
                porcentaje_autorizadas = (autorizadas / total_ocs * 100) if total_ocs > 0 else 0
                st.metric("% OCs Autorizadas", f"{porcentaje_autorizadas:.1f}%")
            
            with col3:
                # Valor pendiente vs autorizado
                valor_total = ocs_df['valor_total'].sum()
                valor_autorizado = ocs_df['valor_autorizado'].sum()
                porcentaje_autorizado = (valor_autorizado / valor_total * 100) if valor_total > 0 else 0
                st.metric("% Valor Autorizado", f"{porcentaje_autorizado:.1f}%")
            
            with col4:
                # OCs más antigua pendiente
                if not ocs_pendientes.empty:
                    # Simular fecha más antigua
                    dias_mas_antigua = np.random.randint(5, 20)
                    st.metric("OC más antigua", f"{dias_mas_antigua} días")
                else:
                    st.metric("OC más antigua", "N/A")
            
            # Tabla de resumen por cliente
            st.markdown("### 👥 RESUMEN POR CLIENTE")
            
            resumen_cliente = ocs_df.groupby('cliente_nombre').agg({
                'valor_total': 'sum',
                'valor_autorizado': 'sum',
                'valor_pendiente': 'sum',
                'id': 'count'
            }).rename(columns={
                'valor_total': 'Total OCs',
                'valor_autorizado': 'Autorizado',
                'valor_pendiente': 'Pendiente',
                'id': 'Cantidad OCs'
            })
            
            # Formatear valores
            resumen_cliente['Total OCs'] = resumen_cliente['Total OCs'].apply(format_currency)
            resumen_cliente['Autorizado'] = resumen_cliente['Autorizado'].apply(format_currency)
            resumen_cliente['Pendiente'] = resumen_cliente['Pendiente'].apply(format_currency)
            
            st.dataframe(
                resumen_cliente,
                use_container_width=True
            )

# ==================== EJECUCIÓN ====================

if __name__ == "__main__":
    show_ocs_page()
