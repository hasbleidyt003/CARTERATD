import streamlit as st
import pandas as pd
from modules.database import get_clientes, get_ocs_pendientes

def show():
    st.header("📋 Gestión de Órdenes de Compra")
    
    # Obtener clientes para filtros
    clientes = get_clientes()
    cliente_lista = ["Todos"] + clientes['nombre'].tolist()
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_cliente = st.selectbox("Filtrar por Cliente", cliente_lista)
    with col2:
        filtro_estado = st.selectbox("Filtrar por Estado", 
                                   ["Todos", "PENDIENTE", "PARCIAL", "AUTORIZADA"])
    with col3:
        filtro_tipo = st.selectbox("Filtrar por Tipo", 
                                 ["Todos", "CUPO_NUEVO", "SUELTA"])
    
    # Obtener OCs filtradas
    ocs = get_ocs_pendientes()
    
    # Aplicar filtros
    if filtro_cliente != "Todos":
        cliente_nit = clientes[clientes['nombre'] == filtro_cliente]['nit'].iloc[0]
        ocs = ocs[ocs['cliente_nit'] == cliente_nit]
    
    if filtro_estado != "Todos":
        ocs = ocs[ocs['estado'] == filtro_estado]
    
    if filtro_tipo != "Todos":
        ocs = ocs[ocs['tipo'] == filtro_tipo]
    
    # Mostrar tabla
    if not ocs.empty:
        for _, oc in ocs.iterrows():
            mostrar_oc_tarjeta(oc)
    else:
        st.info("No hay OCs que coincidan con los filtros")
    
    # Botón para agregar nueva OC
    st.divider()
    if st.button("➕ Agregar Nueva OC", use_container_width=True):
        mostrar_modal_agregar_oc()

def mostrar_oc_tarjeta(oc):
    """Muestra una OC como tarjeta interactiva"""
    with st.container():
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.subheader(f"📄 {oc['numero_oc']}")
            st.caption(f"Cliente: {oc['cliente_nombre']}")
            
            if oc['estado'] == 'PARCIAL':
                st.progress(oc['valor_autorizado'] / oc['valor_total'])
                st.text(f"Autorizado: ${oc['valor_autorizado']:,.0f} de ${oc['valor_total']:,.0f}")
            else:
                st.text(f"Valor: ${oc['valor_total']:,.0f}")
        
        with col2:
            estado_color = {
                'PENDIENTE': '🟡',
                'PARCIAL': '🟠', 
                'AUTORIZADA': '🟢'
            }
            st.metric("Estado", f"{estado_color.get(oc['estado'], '⚫')} {oc['estado']}")
            st.caption(f"Tipo: {oc['tipo']}")
        
        with col3:
            if oc['estado'] in ['PENDIENTE', 'PARCIAL']:
                if st.button("✅ Autorizar", key=f"auth_{oc['id']}", use_container_width=True):
                    mostrar_modal_autorizar(oc)
            else:
                if st.button("📋 Detalle", key=f"det_{oc['id']}", use_container_width=True):
                    mostrar_detalle_oc(oc)
        
        st.divider()

def mostrar_modal_autorizar(oc):
    """Modal para autorización total/parcial"""
    with st.form(f"auth_form_{oc['id']}"):
        st.subheader(f"Autorizar OC: {oc['numero_oc']}")
        
        st.info(f"**Valor total:** ${oc['valor_total']:,.0f}")
        if oc['estado'] == 'PARCIAL':
            st.info(f"**Ya autorizado:** ${oc['valor_autorizado']:,.0f}")
        
        valor_restante = oc['valor_total'] - oc['valor_autorizado']
        
        # Opción rápida de porcentajes
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("25%", use_container_width=True):
                st.session_state.porcentaje = 25
        with col2:
            if st.button("50%", use_container_width=True):
                st.session_state.porcentaje = 50
        with col3:
            if st.button("75%", use_container_width=True):
                st.session_state.porcentaje = 75
        with col4:
            if st.button("100%", use_container_width=True):
                st.session_state.porcentaje = 100
        
        # Campo para valor exacto
        valor_default = valor_restante if 'porcentaje' not in st.session_state else \
                       valor_restante * (st.session_state.porcentaje / 100)
        
        valor_autorizar = st.number_input(
            "Valor a autorizar",
            min_value=0.0,
            max_value=float(valor_restante),
            value=float(valor_default),
            step=1000000.0
        )
        
        comentario = st.text_area("Comentario (opcional)")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.form_submit_button("✅ Confirmar Autorización", use_container_width=True):
                # Código para guardar autorización
                st.success(f"✅ Autorizado ${valor_autorizar:,.0f}")
                st.rerun()
        with col_b:
            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                pass
