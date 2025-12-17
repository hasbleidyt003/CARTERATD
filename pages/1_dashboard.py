import streamlit as st
import pandas as pd
from modules.database import get_clientes, get_ocs_pendientes

def show():
    st.header("📊 Dashboard de Control - Cupos Medicamentos")
    
    # Obtener datos
    clientes = get_clientes()
    ocs_pendientes = get_ocs_pendientes()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cupo_sugerido = clientes['cupo_sugerido'].sum() if not clientes.empty else 0
        st.metric("Cupo Sugerido Total", f"${total_cupo_sugerido:,.0f}")
    
    with col2:
        total_saldo = clientes['saldo_actual'].sum() if not clientes.empty else 0
        st.metric("Saldo Total Clientes", f"${total_saldo:,.0f}")
    
    with col3:
        if not clientes.empty:
            clientes_alerta = len(clientes[clientes['estado'] == 'ALERTA']) if 'estado' in clientes.columns else 0
            clientes_sobrepasado = len(clientes[clientes['estado'] == 'SOBREPASADO']) if 'estado' in clientes.columns else 0
            st.metric("Clientes Críticos", f"{clientes_alerta}/{clientes_sobrepasado}")
        else:
            st.metric("Clientes Críticos", "0/0")
    
    with col4:
        total_pendientes = ocs_pendientes['valor_pendiente'].sum() if not ocs_pendientes.empty else 0
        st.metric("OCs Pendientes", f"${total_pendientes:,.0f}")
    
    st.divider()
    
    # Tabla principal de clientes
    st.subheader("🏥 Estado de Clientes")
    
    if not clientes.empty:
        # Asegurar que tenemos las columnas necesarias
        required_cols = ['nit', 'nombre', 'cupo_sugerido', 'saldo_actual']
        if all(col in clientes.columns for col in required_cols):
            # Preparar datos para mostrar
            display_df = clientes.copy()
            
            # Calcular disponible
            if 'cartera_vencida' in display_df.columns:
                display_df['disponible_real'] = display_df['cupo_sugerido'] - display_df['saldo_actual'] - display_df['cartera_vencida']
            else:
                display_df['disponible_real'] = display_df['cupo_sugerido'] - display_df['saldo_actual']
            
            # Formatear columnas monetarias
            monetary_cols = ['cupo_sugerido', 'saldo_actual', 'disponible_real']
            if 'cartera_vencida' in display_df.columns:
                monetary_cols.append('cartera_vencida')
            
            for col in monetary_cols:
                if col in display_df.columns:
                    display_df[f'{col}_fmt'] = display_df[col].apply(lambda x: f"${x:,.0f}")
            
            # Columnas a mostrar
            columns_to_show = ['nit', 'nombre']
            
            # Agregar columnas formateadas
            column_mapping = {
                'cupo_sugerido_fmt': 'Cupo Sugerido',
                'saldo_actual_fmt': 'Saldo Actual',
                'disponible_real_fmt': 'Disponible Real'
            }
            
            if 'cartera_vencida_fmt' in display_df.columns:
                column_mapping['cartera_vencida_fmt'] = 'Cartera Vencida'
            
            if 'porcentaje_uso' in display_df.columns:
                column_mapping['porcentaje_uso'] = '% Uso'
            
            if 'estado' in display_df.columns:
                column_mapping['estado'] = 'Estado'
            
            # Crear DataFrame final
            final_columns = ['nit', 'nombre']
            for col in column_mapping.keys():
                if col in display_df.columns:
                    final_columns.append(col)
            
            # Mostrar tabla
            st.dataframe(
                display_df[final_columns],
                column_config={
                    "nit": "NIT",
                    "nombre": "Cliente",
                    **column_mapping
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.error("Faltan columnas necesarias en los datos de clientes")
            st.write("Columnas disponibles:", list(clientes.columns))
    else:
        st.info("No hay clientes registrados en la base de datos")
    
    st.divider()
    
    # Sección de resumen
    st.subheader("📈 Resumen Visual")
    
    if not clientes.empty and len(clientes) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Distribución por Estado**")
            if 'estado' in clientes.columns:
                estado_counts = clientes['estado'].value_counts()
                
                for estado, count in estado_counts.items():
                    color = {
                        'NORMAL': '🟢',
                        'ALERTA': '🟡',
                        'SOBREPASADO': '🔴'
                    }.get(estado, '⚫')
                    
                    st.metric(f"{color} {estado}", count)
            else:
                st.info("No hay información de estados")
        
        with col2:
            st.write("**Top 5 - Mayor Saldo**")
            top_clientes = clientes.nlargest(5, 'saldo_actual')
            
            for _, cliente in top_clientes.iterrows():
                cupo = cliente.get('cupo_sugerido', 1)
                saldo = cliente.get('saldo_actual', 0)
                
                if cupo > 0:
                    porcentaje = min(saldo / cupo, 1.0)
                    st.progress(
                        porcentaje,
                        text=f"{cliente.get('nombre', 'Sin nombre')[:20]}...: ${saldo:,.0f}"
                    )
    
    # Alertas críticas
    st.divider()
    st.subheader("🚨 Alertas Prioritarias")
    
    if not clientes.empty and 'estado' in clientes.columns:
        # Clientes sobrepasados
        sobrepasados = clientes[clientes['estado'] == 'SOBREPASADO']
        if not sobrepasados.empty:
            st.error("**Clientes con Cupo Sobrepasado:**")
            for _, cliente in sobrepasados.iterrows():
                cupo = cliente.get('cupo_sugerido', 0)
                saldo = cliente.get('saldo_actual', 0)
                cartera = cliente.get('cartera_vencida', 0)
                sobrepaso = (cupo - saldo - cartera) * -1
                st.write(f"• **{cliente.get('nombre', 'Sin nombre')}** - Sobrepasa: ${sobrepaso:,.0f}")
        
        # Clientes en alerta
        alertas = clientes[clientes['estado'] == 'ALERTA']
        if not alertas.empty:
            st.warning("**Clientes en Alerta (>80% uso):**")
            for _, cliente in alertas.iterrows():
                st.write(f"• **{cliente.get('nombre', 'Sin nombre')}** - Uso: {cliente.get('porcentaje_uso', 'N/A')}%")
    else:
        st.info("No hay información de alertas disponible")
    
    # Información de OCs pendientes
    st.divider()
    st.subheader("📋 Órdenes de Compra Pendientes")
    
    if not ocs_pendientes.empty:
        st.write(f"Total de OCs pendientes: {len(ocs_pendientes)}")
        
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
                column_config={
                    "Valor Pendiente": st.column_config.NumberColumn(
                        format="$ %d"
                    )
                }
            )
    else:
        st.success("✅ No hay OCs pendientes")
