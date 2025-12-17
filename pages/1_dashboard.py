import streamlit as st
import pandas as pd
from modules.database import get_clientes, get_todas_ocs

def show():
    st.title("📊 Dashboard de Control - Cupos Medicamentos")
    
    try:
        # Obtener datos
        clientes = get_clientes()
        todas_ocs = get_todas_ocs()
        
        # Filtrar OCs pendientes o parciales
        if not todas_ocs.empty and 'estado' in todas_ocs.columns:
            ocs_pendientes = todas_ocs[todas_ocs['estado'].isin(['PENDIENTE', 'PARCIAL'])]
        else:
            ocs_pendientes = pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        clientes = pd.DataFrame()
        ocs_pendientes = pd.DataFrame()
    
    # ============ MÉTRICAS PRINCIPALES ============
    st.subheader("📈 Métricas Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not clientes.empty and 'cupo_sugerido' in clientes.columns:
            total_cupo = clientes['cupo_sugerido'].sum()
            st.metric("Cupo Total", f"${total_cupo:,.0f}")
        else:
            st.metric("Cupo Total", "$0")
    
    with col2:
        if not clientes.empty and 'saldo_actual' in clientes.columns:
            total_saldo = clientes['saldo_actual'].sum()
            st.metric("Saldo Total", f"${total_saldo:,.0f}")
        else:
            st.metric("Saldo Total", "$0")
    
    with col3:
        if not clientes.empty:
            if 'estado' in clientes.columns:
                alertas = len(clientes[clientes['estado'] == 'ALERTA'])
                sobrepasados = len(clientes[clientes['estado'] == 'SOBREPASADO'])
                st.metric("Clientes Críticos", f"{alertas}/{sobrepasados}")
            else:
                st.metric("Clientes", len(clientes))
        else:
            st.metric("Clientes", "0")
    
    with col4:
        if not ocs_pendientes.empty and 'valor_pendiente' in ocs_pendientes.columns:
            total_pendientes = ocs_pendientes['valor_pendiente'].sum()
            st.metric("OCs Pendientes", f"${total_pendientes:,.0f}")
        else:
            st.metric("OCs Pendientes", "$0")
    
    st.divider()
    
    # ============ TABLA PRINCIPAL DE CLIENTES ============
    st.subheader("🏥 Estado de Clientes")
    
    if not clientes.empty:
        # Preparar datos para mostrar
        display_df = clientes.copy()
        
        # Seleccionar y ordenar columnas
        columnas_a_mostrar = ['nombre', 'nit', 'cupo_sugerido', 'saldo_actual', 
                             'disponible', 'porcentaje_uso', 'estado']
        
        # Filtrar columnas existentes
        columnas_existentes = [col for col in columnas_a_mostrar if col in display_df.columns]
        display_df = display_df[columnas_existentes]
        
        # Renombrar columnas
        display_df = display_df.rename(columns={
            'nombre': 'Cliente',
            'nit': 'NIT',
            'cupo_sugerido': 'Cupo Sugerido',
            'saldo_actual': 'Saldo Actual',
            'disponible': 'Disponible',
            'porcentaje_uso': '% Uso',
            'estado': 'Estado'
        })
        
        # Formatear valores monetarios
        for col in ['Cupo Sugerido', 'Saldo Actual', 'Disponible']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
        
        # Formatear porcentaje
        if '% Uso' in display_df.columns:
            display_df['% Uso'] = display_df['% Uso'].apply(lambda x: f"{x}%")
        
        # Mostrar tabla
        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Estado": st.column_config.TextColumn(
                    help="🟢 NORMAL, 🟡 ALERTA, 🔴 SOBREPASADO"
                )
            }
        )
    else:
        st.info("No hay clientes registrados en la base de datos")
    
    st.divider()
    
    # ============ RESUMEN VISUAL ============
    st.subheader("📈 Resumen Visual")
    
    if not clientes.empty and len(clientes) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Distribución por Estado**")
            if 'estado' in clientes.columns:
                estados = ['NORMAL', 'ALERTA', 'SOBREPASADO']
                for estado in estados:
                    if estado in clientes['estado'].values:
                        count = len(clientes[clientes['estado'] == estado])
                        color = {'NORMAL': '🟢', 'ALERTA': '🟡', 'SOBREPASADO': '🔴'}[estado]
                        st.metric(f"{color} {estado}", count)
            else:
                st.info("No hay información de estados")
        
        with col2:
            st.write("**Top 3 - Mayor Saldo**")
            if 'saldo_actual' in clientes.columns and 'nombre' in clientes.columns:
                top_clientes = clientes.nlargest(3, 'saldo_actual')
                
                for _, cliente in top_clientes.iterrows():
                    nombre = cliente['nombre'][:25] + "..." if len(cliente['nombre']) > 25 else cliente['nombre']
                    saldo = cliente['saldo_actual']
                    st.write(f"• **{nombre}**: ${saldo:,.0f}")
            else:
                st.info("No hay datos para mostrar")
    
    st.divider()
    
    # ============ ALERTAS CRÍTICAS ============
    st.subheader("🚨 Alertas Prioritarias")
    
    if not clientes.empty and 'estado' in clientes.columns:
        # Clientes sobrepasados
        sobrepasados = clientes[clientes['estado'] == 'SOBREPASADO']
        if not sobrepasados.empty:
            st.error("**🔴 Clientes con Cupo Sobrepasado:**")
            for _, cliente in sobrepasados.iterrows():
                sobrepaso = abs(cliente['disponible'])
                st.write(f"• **{cliente['nombre']}** - Sobrepasa: ${sobrepaso:,.0f}")
        else:
            st.success("✅ No hay clientes sobrepasados")
        
        # Clientes en alerta
        alertas = clientes[clientes['estado'] == 'ALERTA']
        if not alertas.empty:
            st.warning("**🟡 Clientes en Alerta (>80% uso):**")
            for _, cliente in alertas.iterrows():
                st.write(f"• **{cliente['nombre']}** - Uso: {cliente['porcentaje_uso']}%")
        else:
            st.success("✅ No hay clientes en alerta")
    else:
        st.info("No hay información de alertas disponible")
    
    st.divider()
    
    # ============ OCs PENDIENTES ============
    st.subheader("📋 Órdenes de Compra Pendientes")
    
    if not ocs_pendientes.empty:
        st.write(f"**Total de OCs pendientes:** {len(ocs_pendientes)}")
        
        # Mostrar resumen de OCs por cliente
        if 'cliente_nombre' in ocs_pendientes.columns:
            ocs_por_cliente = ocs_pendientes.groupby('cliente_nombre')['valor_pendiente'].sum().reset_index()
            ocs_por_cliente = ocs_por_cliente.sort_values('valor_pendiente', ascending=False)
            
            st.dataframe(
                ocs_por_cliente.rename(columns={
                    'cliente_nombre': 'Cliente',
                    'valor_pendiente': 'Valor Pendiente'
                }),
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Valor Pendiente": st.column_config.NumberColumn(
                        format="$ %d"
                    )
                }
            )
    else:
        st.success("✅ No hay OCs pendientes")
    
    st.divider()
    
    # ============ ACCIONES RÁPIDAS ============
    st.subheader("⚡ Acciones Rápidas")
    
    col_a1, col_a2, col_a3 = st.columns(3)
    
    with col_a1:
        if st.button("👥 Ver Todos los Clientes", use_container_width=True):
            st.session_state['tab'] = "clientes"
            st.rerun()
    
    with col_a2:
        if st.button("📋 Ver Todas las OCs", use_container_width=True):
            st.session_state['tab'] = "ocs"
            st.rerun()
    
    with col_a3:
        if st.button("🔄 Actualizar Datos", use_container_width=True):
            st.rerun()
