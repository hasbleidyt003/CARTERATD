import streamlit as st
import pandas as pd
from modules.database import get_clientes, get_todas_ocs, get_estadisticas_generales
from modules.styles import apply_global_styles, format_currency

def show():
    apply_global_styles()
    
    st.title("Dashboard de Control - Cupos Medicamentos")
    
    try:
        clientes = get_clientes()
        todas_ocs = get_todas_ocs()
        ocs_pendientes = todas_ocs[todas_ocs['estado'].isin(['PENDIENTE', 'PARCIAL'])] if not todas_ocs.empty else pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        clientes = pd.DataFrame()
        ocs_pendientes = pd.DataFrame()
    
    # MÉTRICAS PRINCIPALES
    st.subheader("Métricas Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cupo = clientes['cupo_sugerido'].sum() if not clientes.empty else 0
        st.metric("Cupo Total", format_currency(total_cupo))
    
    with col2:
        total_saldo = clientes['saldo_actual'].sum() if not clientes.empty else 0
        st.metric("Saldo Total", format_currency(total_saldo))
    
    with col3:
        if not clientes.empty and 'estado' in clientes.columns:
            alertas = len(clientes[clientes['estado'] == 'ALERTA'])
            sobrepasados = len(clientes[clientes['estado'] == 'SOBREPASADO'])
            st.metric("Clientes Críticos", f"{sobrepasados + alertas}")
        else:
            st.metric("Clientes", len(clientes) if not clientes.empty else 0)
    
    with col4:
        total_pendientes = ocs_pendientes['valor_pendiente'].sum() if not ocs_pendientes.empty else 0
        st.metric("OCs Pendientes", format_currency(total_pendientes))
    
    st.divider()
    
    # TABLA PRINCIPAL DE CLIENTES
    st.subheader("Estado de Clientes")
    
    if not clientes.empty:
        display_df = clientes.copy()
        columnas_a_mostrar = ['nombre', 'nit', 'cupo_sugerido', 'saldo_actual', 'disponible', 'porcentaje_uso', 'estado']
        columnas_existentes = [col for col in columnas_a_mostrar if col in display_df.columns]
        display_df = display_df[columnas_existentes]
        
        rename_map = {
            'nombre': 'Cliente',
            'nit': 'NIT',
            'cupo_sugerido': 'Cupo',
            'saldo_actual': 'Saldo',
            'disponible': 'Disponible',
            'porcentaje_uso': '% Uso',
            'estado': 'Estado'
        }
        display_df = display_df.rename(columns=rename_map)
        
        for col in ['Cupo', 'Saldo', 'Disponible']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(format_currency)
        
        if '% Uso' in display_df.columns:
            display_df['% Uso'] = display_df['% Uso'].apply(lambda x: f"{x}%")
        
        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Estado": st.column_config.Column(width="small"),
                "Cliente": st.column_config.Column(width="large"),
                "NIT": st.column_config.Column(width="small"),
                "% Uso": st.column_config.ProgressColumn(format="%f%%", min_value=0, max_value=100)
            }
        )
    else:
        st.info("No hay clientes registrados")
    
    st.divider()
    
    # ALERTAS CRÍTICAS
    st.subheader("Alertas Prioritarias")
    
    if not clientes.empty and 'estado' in clientes.columns:
        alert_columns = st.columns(2)
        
        with alert_columns[0]:
            sobrepasados = clientes[clientes['estado'] == 'SOBREPASADO']
            if not sobrepasados.empty:
                st.error("Clientes con Cupo Sobrepasado")
                for _, cliente in sobrepasados.iterrows():
                    excedido = abs(cliente['disponible'])
                    st.markdown(f"""
                    **{cliente['nombre']}**  
                    NIT: {cliente['nit']}  
                    Excedido por: {format_currency(excedido)}  
                    % Uso: {cliente['porcentaje_uso']}%
                    """)
            else:
                st.success("No hay clientes sobrepasados")
        
        with alert_columns[1]:
            alertas = clientes[clientes['estado'] == 'ALERTA']
            if not alertas.empty:
                st.warning("Clientes en Alerta (>80% uso)")
                for _, cliente in alertas.iterrows():
                    st.markdown(f"""
                    **{cliente['nombre']}**  
                    NIT: {cliente['nit']}  
                    Cupo usado: {cliente['porcentaje_uso']}%  
                    Disponible: {format_currency(cliente['disponible'])}
                    """)
            else:
                st.success("No hay clientes en alerta")
    else:
        st.info("No hay información de alertas")
    
    st.divider()
    
    # RESUMEN DE OCs
    st.subheader("Resumen de Órdenes de Compra")
    
    if not ocs_pendientes.empty:
        cols_summary = st.columns(3)
        
        with cols_summary[0]:
            st.metric("OCs Pendientes", len(ocs_pendientes))
        
        with cols_summary[1]:
            valor_total_pend = ocs_pendientes['valor_pendiente'].sum()
            st.metric("Valor Pendiente", format_currency(valor_total_pend))
        
        with cols_summary[2]:
            if not ocs_pendientes.empty:
                cliente_mas_ocs = ocs_pendientes['cliente_nombre'].mode()[0] if 'cliente_nombre' in ocs_pendientes.columns else "N/A"
                st.metric("Cliente con más OCs", cliente_mas_ocs)
        
        if 'cliente_nombre' in ocs_pendientes.columns and 'valor_pendiente' in ocs_pendientes.columns:
            resumen_ocs = ocs_pendientes.groupby('cliente_nombre').agg({
                'numero_oc': 'count',
                'valor_pendiente': 'sum'
            }).reset_index()
            
            resumen_ocs = resumen_ocs.rename(columns={
                'cliente_nombre': 'Cliente',
                'numero_oc': 'Cantidad OCs',
                'valor_pendiente': 'Valor Pendiente'
            })
            
            resumen_ocs['Valor Pendiente'] = resumen_ocs['Valor Pendiente'].apply(format_currency)
            resumen_ocs = resumen_ocs.sort_values('Cantidad OCs', ascending=False)
            
            st.dataframe(
                resumen_ocs,
                hide_index=True,
                use_container_width=True
            )
    else:
        st.success("No hay OCs pendientes")
    
    st.divider()
    
    # ACCIONES RÁPIDAS
    st.subheader("Acciones Rápidas")
    
    col_actions1, col_actions2, col_actions3 = st.columns(3)
    
    with col_actions1:
        if st.button("Ver Todos los Clientes", use_container_width=True):
            st.switch_page("pages/2_Clientes.py")
    
    with col_actions2:
        if st.button("Ver Todas las OCs", use_container_width=True):
            st.switch_page("pages/3_OCs.py")
    
    with col_actions3:
        if st.button("Actualizar Dashboard", use_container_width=True):
            st.rerun()
