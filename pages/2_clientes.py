"""
Página de gestión de clientes
"""

import streamlit as st
import pandas as pd
from modules.database import (
    get_clientes, 
    actualizar_cliente, 
    crear_cliente,
    agregar_movimiento,
    get_cliente_por_nit
)

def show():
    st.title("👥 Gestión de Clientes")
    
    # Pestañas
    tab1, tab2, tab3 = st.tabs(["📋 Clientes", "➕ Nuevo", "📊 Resumen"])
    
    with tab1:
        mostrar_clientes()
    
    with tab2:
        agregar_cliente()
    
    with tab3:
        mostrar_resumen()

def mostrar_clientes():
    """Muestra la lista de clientes con opciones de edición"""
    try:
        clientes = get_clientes()
        
        if clientes.empty:
            st.info("No hay clientes registrados")
            return
        
        # Estadísticas rápidas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Clientes", len(clientes))
        with col2:
            st.metric("Cupo Total", f"${clientes['cupo_sugerido'].sum():,.0f}")
        with col3:
            st.metric("Saldo Total", f"${clientes['saldo_actual'].sum():,.0f}")
        with col4:
            criticos = len(clientes[clientes['estado'] == 'SOBREPASADO'])
            st.metric("Críticos", criticos)
        
        st.divider()
        
        # Filtros
        estado_filtro = st.selectbox(
            "Filtrar por estado:",
            ["Todos", "NORMAL", "ALERTA", "SOBREPASADO"],
            key="filtro_estado_clientes"
        )
        
        if estado_filtro != "Todos":
            clientes = clientes[clientes['estado'] == estado_filtro]
        
        # Mostrar clientes
        for idx, cliente in clientes.iterrows():
            with st.expander(f"{cliente['nombre']} (NIT: {cliente['nit']})", expanded=False):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    # Formulario de edición
                    with st.form(key=f"form_{cliente['nit']}"):
                        nuevo_nombre = st.text_input(
                            "Nombre",
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
                        
                        nuevo_saldo = st.number_input(
                            "Saldo Actual",
                            value=float(cliente['saldo_actual']),
                            min_value=0.0,
                            step=1000000.0,
                            format="%.0f",
                            key=f"saldo_{cliente['nit']}"
                        )
                        
                        # Botones
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("💾 Guardar", use_container_width=True):
                                actualizar_cliente(
                                    nit=cliente['nit'],
                                    nombre=nuevo_nombre,
                                    cupo_sugerido=nuevo_cupo,
                                    saldo_actual=nuevo_saldo
                                )
                                st.success("✅ Cambios guardados")
                                st.rerun()
                        
                        with col_btn2:
                            if st.form_submit_button("💳 Registrar Pago", use_container_width=True):
                                st.session_state[f"pago_{cliente['nit']}"] = True
                                st.rerun()
                
                with col_b:
                    # Información actual
                    st.info("**Estado Actual:**")
                    
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        st.metric("Cupo", f"${cliente['cupo_sugerido']:,.0f}")
                        st.metric("Disponible", f"${cliente['disponible']:,.0f}")
                    with col_m2:
                        st.metric("Saldo", f"${cliente['saldo_actual']:,.0f}")
                        st.metric("% Uso", f"{cliente['porcentaje_uso']}%")
                    
                    # Estado con color
                    estado_color = {
                        'NORMAL': '🟢',
                        'ALERTA': '🟡',
                        'SOBREPASADO': '🔴'
                    }
                    st.write(f"**Estado:** {estado_color.get(cliente['estado'], '⚪')} {cliente['estado']}")
                    
                    # Barra de progreso
                    st.progress(min(float(cliente['porcentaje_uso']), 100) / 100)
                
                # Modal para registrar pago
                if f"pago_{cliente['nit']}" in st.session_state:
                    with st.form(key=f"pago_form_{cliente['nit']}"):
                        st.subheader(f"💳 Registrar Pago - {cliente['nombre']}")
                        
                        valor_pago = st.number_input(
                            "Valor del Pago",
                            min_value=0.0,
                            value=0.0,
                            step=1000000.0,
                            format="%.0f"
                        )
                        
                        descripcion = st.text_input("Descripción", placeholder="Ej: Transferencia bancaria")
                        referencia = st.text_input("Referencia", placeholder="Ej: PAGO-001")
                        
                        col_sub, col_can = st.columns(2)
                        with col_sub:
                            if st.form_submit_button("✅ Confirmar Pago", use_container_width=True):
                                try:
                                    agregar_movimiento(
                                        cliente_nit=cliente['nit'],
                                        tipo="PAGO",
                                        valor=valor_pago,
                                        descripcion=descripcion,
                                        referencia=referencia,
                                        usuario=st.session_state.get('username', 'Admin')
                                    )
                                    st.success(f"✅ Pago de ${valor_pago:,.0f} registrado")
                                    del st.session_state[f"pago_{cliente['nit']}"]
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                        
                        with col_can:
                            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                del st.session_state[f"pago_{cliente['nit']}"]
                                st.rerun()
        
        # Mostrar también en tabla
        st.divider()
        st.subheader("📋 Vista en Tabla")
        
        df_tabla = clientes.copy()
        df_tabla = df_tabla[['nombre', 'nit', 'cupo_sugerido', 'saldo_actual', 'disponible', 'porcentaje_uso', 'estado']]
        df_tabla.columns = ['Cliente', 'NIT', 'Cupo Sugerido', 'Saldo Actual', 'Disponible', '% Uso', 'Estado']
        
        # Formatear valores
        for col in ['Cupo Sugerido', 'Saldo Actual', 'Disponible']:
            df_tabla[col] = df_tabla[col].apply(lambda x: f"${x:,.0f}")
        
        st.dataframe(df_tabla, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Error al cargar clientes: {str(e)}")

def agregar_cliente():
    """Formulario para agregar nuevo cliente"""
    st.subheader("➕ Agregar Nuevo Cliente")
    
    with st.form("nuevo_cliente_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nit = st.text_input("NIT *")
            nombre = st.text_input("Nombre del Cliente *")
        
        with col2:
            cupo_sugerido = st.number_input(
                "Cupo Sugerido *",
                min_value=0.0,
                value=1000000000.0,
                step=1000000.0,
                format="%.0f"
            )
            
            saldo_actual = st.number_input(
                "Saldo Actual Inicial",
                min_value=0.0,
                value=0.0,
                step=1000000.0,
                format="%.0f"
            )
        
        # Cálculos
        disponible = cupo_sugerido - saldo_actual
        porcentaje_uso = (saldo_actual / cupo_sugerido * 100) if cupo_sugerido > 0 else 0
        
        # Mostrar resumen
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.metric("Disponible", f"${disponible:,.0f}")
        with col_info2:
            st.metric("% Uso", f"{porcentaje_uso:.1f}%")
        
        # Botón de envío
        if st.form_submit_button("💾 Crear Cliente", use_container_width=True, type="primary"):
            if not nit or not nombre:
                st.error("NIT y Nombre son obligatorios")
                return
            
            try:
                crear_cliente(nit, nombre, cupo_sugerido, saldo_actual)
                st.success(f"✅ Cliente '{nombre}' creado exitosamente")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

def mostrar_resumen():
    """Muestra resumen general de clientes"""
    try:
        clientes = get_clientes()
        
        if clientes.empty:
            st.info("No hay clientes para mostrar")
            return
        
        st.subheader("📊 Resumen General")
        
        # KPIs principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Clientes", len(clientes))
        with col2:
            st.metric("Cupo Total", f"${clientes['cupo_sugerido'].sum():,.0f}")
        with col3:
            st.metric("Saldo Total", f"${clientes['saldo_actual'].sum():,.0f}")
        with col4:
            st.metric("Disponible Total", f"${clientes['disponible'].sum():,.0f}")
        
        st.divider()
        
        # Distribución por estado
        st.subheader("📈 Distribución por Estado")
        
        estados = clientes['estado'].value_counts()
        col_est1, col_est2, col_est3 = st.columns(3)
        
        normales = estados.get('NORMAL', 0)
        alertas = estados.get('ALERTA', 0)
        sobrepasados = estados.get('SOBREPASADO', 0)
        
        with col_est1:
            st.metric("🟢 NORMAL", normales)
        with col_est2:
            st.metric("🟡 ALERTA", alertas)
        with col_est3:
            st.metric("🔴 SOBREPASADO", sobrepasados)
        
        st.divider()
        
        # Top 5 mayor uso
        st.subheader("🏆 Top 5 - Mayor % de Uso")
        
        top5 = clientes.nlargest(5, 'porcentaje_uso')
        for i, (_, cliente) in enumerate(top5.iterrows(), 1):
            with st.container():
                col_num, col_info = st.columns([1, 4])
                with col_num:
                    st.subheader(f"#{i}")
                with col_info:
                    st.write(f"**{cliente['nombre']}**")
                    st.progress(min(float(cliente['porcentaje_uso']), 100) / 100)
                    st.caption(f"{cliente['porcentaje_uso']}%")
        
        st.divider()
        
        # Clientes críticos
        st.subheader("⚠️ Clientes Críticos")
        
        criticos = clientes[clientes['estado'] == 'SOBREPASADO']
        if not criticos.empty:
            for _, critico in criticos.iterrows():
                with st.container():
                    st.error(f"**{critico['nombre']}**")
                    st.write(f"Excedido por: ${abs(critico['disponible']):,.0f}")
        else:
            st.success("✅ No hay clientes sobrepasados")
            
    except Exception as e:
        st.error(f"Error en resumen: {str(e)}")
