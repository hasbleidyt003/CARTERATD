import streamlit as st
import pandas as pd
from modules.database import get_clientes, actualizar_cliente, crear_cliente, agregar_movimiento
from modules.styles import apply_global_styles, format_currency, format_percentage

def show():
    apply_global_styles()
    st.title("Gestión de Clientes")
    
    tab_lista, tab_nuevo, tab_resumen = st.tabs(["Lista de Clientes", "Nuevo Cliente", "Resumen General"])
    
    with tab_lista:
        mostrar_lista_clientes()
    
    with tab_nuevo:
        agregar_cliente()
    
    with tab_resumen:
        mostrar_resumen()

def mostrar_lista_clientes():
    try:
        clientes = get_clientes()
        
        if clientes.empty:
            st.info("No hay clientes registrados")
            return
        
        # FILTROS
        st.subheader("Filtros de Búsqueda")
        
        filter_cols = st.columns([2, 1, 1])
        with filter_cols[0]:
            busqueda = st.text_input("Buscar por nombre o NIT", placeholder="Ingrese nombre o NIT...")
        
        with filter_cols[1]:
            estado_filtro = st.selectbox("Estado", ["Todos", "NORMAL", "ALERTA", "SOBREPASADO"])
        
        with filter_cols[2]:
            ordenar_por = st.selectbox("Ordenar por", ["Nombre", "Cupo", "Saldo", "% Uso"])
        
        # Aplicar filtros
        if busqueda:
            clientes = clientes[clientes.apply(
                lambda row: busqueda.lower() in str(row['nombre']).lower() or busqueda in str(row['nit']), axis=1)]
        
        if estado_filtro != "Todos":
            clientes = clientes[clientes['estado'] == estado_filtro]
        
        orden_map = {"Nombre": "nombre", "Cupo": "cupo_sugerido", "Saldo": "saldo_actual", "% Uso": "porcentaje_uso"}
        if ordenar_por in orden_map:
            clientes = clientes.sort_values(orden_map[ordenar_por], ascending=False)
        
        # ESTADÍSTICAS
        st.subheader("Estadísticas")
        
        stat_cols = st.columns(4)
        with stat_cols[0]:
            st.metric("Total Clientes", len(clientes))
        with stat_cols[1]:
            st.metric("Cupo Total", format_currency(clientes['cupo_sugerido'].sum()))
        with stat_cols[2]:
            st.metric("Saldo Total", format_currency(clientes['saldo_actual'].sum()))
        with stat_cols[3]:
            criticos = len(clientes[clientes['estado'] == 'SOBREPASADO'])
            st.metric("Críticos", criticos)
        
        st.divider()
        
        # TABLA DE CLIENTES
        st.subheader(f"Lista de Clientes ({len(clientes)})")
        
        display_df = clientes.copy()
        display_df['cupo_sugerido'] = display_df['cupo_sugerido'].apply(format_currency)
        display_df['saldo_actual'] = display_df['saldo_actual'].apply(format_currency)
        display_df['disponible'] = display_df['disponible'].apply(format_currency)
        display_df['porcentaje_uso'] = display_df['porcentaje_uso'].apply(format_percentage)
        
        display_df = display_df.rename(columns={
            'nombre': 'Cliente',
            'nit': 'NIT',
            'cupo_sugerido': 'Cupo Sugerido',
            'saldo_actual': 'Saldo Actual',
            'disponible': 'Disponible',
            'porcentaje_uso': '% Uso',
            'estado': 'Estado'
        })
        
        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Estado": st.column_config.TextColumn(width="small"),
                "Cliente": st.column_config.TextColumn(width="large"),
                "NIT": st.column_config.TextColumn(width="medium")
            }
        )
        
        # EDICIÓN INDIVIDUAL
        st.divider()
        st.subheader("Edición Individual")
        
        clientes_lista = clientes[['nit', 'nombre']].copy()
        clientes_lista['display'] = clientes_lista.apply(lambda x: f"{x['nombre']} (NIT: {x['nit']})", axis=1)
        
        cliente_seleccionado = st.selectbox("Seleccionar cliente para editar", options=clientes_lista['display'].tolist())
        
        if cliente_seleccionado:
            nit_cliente = cliente_seleccionado.split("(NIT: ")[1].replace(")", "")
            cliente_info = clientes[clientes['nit'] == nit_cliente].iloc[0]
            
            with st.form(key=f"form_editar_{nit_cliente}"):
                col_edit1, col_edit2 = st.columns(2)
                
                with col_edit1:
                    nuevo_nombre = st.text_input("Nombre del cliente", value=cliente_info['nombre'])
                    nuevo_cupo = st.number_input("Cupo Sugerido", value=float(cliente_info['cupo_sugerido']), 
                                                min_value=0.0, step=1000000.0, format="%.0f")
                
                with col_edit2:
                    nuevo_saldo = st.number_input("Saldo Actual", value=float(cliente_info['saldo_actual']), 
                                                min_value=0.0, step=1000000.0, format="%.0f")
                    nuevo_disponible = nuevo_cupo - nuevo_saldo
                    nuevo_porcentaje = (nuevo_saldo / nuevo_cupo * 100) if nuevo_cupo > 0 else 0
                    
                    st.metric("Nuevo Disponible", format_currency(nuevo_disponible))
                    st.metric("Nuevo % Uso", format_percentage(nuevo_porcentaje))
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.form_submit_button("Guardar Cambios", use_container_width=True, type="primary"):
                        try:
                            actualizar_cliente(
                                nit=nit_cliente,
                                nombre=nuevo_nombre,
                                cupo_sugerido=nuevo_cupo,
                                saldo_actual=nuevo_saldo
                            )
                            st.success("Cambios guardados exitosamente")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                
                with col_btn2:
                    if st.form_submit_button("Registrar Pago", use_container_width=True):
                        st.session_state[f'registrar_pago_{nit_cliente}'] = True
                        st.rerun()
            
            # Modal para registrar pago
            if f'registrar_pago_{nit_cliente}' in st.session_state:
                with st.form(key=f"form_pago_{nit_cliente}"):
                    st.subheader(f"Registrar Pago - {cliente_info['nombre']}")
                    
                    valor_pago = st.number_input("Valor del Pago", min_value=0.0, value=0.0, 
                                               step=1000000.0, format="%.0f")
                    descripcion = st.text_input("Descripción", placeholder="Ej: Transferencia bancaria...")
                    referencia = st.text_input("Referencia", placeholder="Ej: PAGO-001...")
                    
                    col_sub, col_can = st.columns(2)
                    with col_sub:
                        if st.form_submit_button("Confirmar Pago", use_container_width=True, type="primary"):
                            try:
                                agregar_movimiento(
                                    cliente_nit=nit_cliente,
                                    tipo="PAGO",
                                    valor=valor_pago,
                                    descripcion=descripcion,
                                    referencia=referencia,
                                    usuario=st.session_state.get('usuario', 'Admin')
                                )
                                st.success(f"Pago de {format_currency(valor_pago)} registrado")
                                del st.session_state[f'registrar_pago_{nit_cliente}']
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    
                    with col_can:
                        if st.form_submit_button("Cancelar", use_container_width=True):
                            del st.session_state[f'registrar_pago_{nit_cliente}']
                            st.rerun()
        
    except Exception as e:
        st.error(f"Error al cargar clientes: {str(e)}")

def agregar_cliente():
    st.subheader("Agregar Nuevo Cliente")
    
    with st.form(key="form_nuevo_cliente"):
        col_input1, col_input2 = st.columns(2)
        
        with col_input1:
            nit = st.text_input("NIT *", placeholder="Ej: 901212102")
            nombre = st.text_input("Nombre del Cliente *", placeholder="Ej: AUNA COLOMBIA S.A.S.")
        
        with col_input2:
            cupo_sugerido = st.number_input("Cupo Sugerido *", min_value=0.0, value=1000000000.0, 
                                          step=1000000.0, format="%.0f")
            saldo_actual = st.number_input("Saldo Actual Inicial", min_value=0.0, value=0.0, 
                                         step=1000000.0, format="%.0f")
        
        disponible = cupo_sugerido - saldo_actual
        porcentaje_uso = (saldo_actual / cupo_sugerido * 100) if cupo_sugerido > 0 else 0
        
        st.subheader("Resumen del Nuevo Cliente")
        
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric("Cupo Sugerido", format_currency(cupo_sugerido))
        with col_res2:
            st.metric("Saldo Inicial", format_currency(saldo_actual))
        with col_res3:
            st.metric("Disponible", format_currency(disponible))
        
        st.info(f"% de Uso Inicial: {format_percentage(porcentaje_uso)}")
        
        if st.form_submit_button("Crear Cliente", type="primary", use_container_width=True):
            if not nit or not nombre:
                st.error("NIT y Nombre son campos obligatorios")
                return
            
            if not nit.isdigit():
                st.error("El NIT debe contener solo números")
                return
            
            try:
                crear_cliente(nit, nombre, cupo_sugerido, saldo_actual)
                st.success(f"Cliente '{nombre}' creado exitosamente")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

def mostrar_resumen():
    try:
        clientes = get_clientes()
        
        if clientes.empty:
            st.info("No hay clientes para mostrar")
            return
        
        st.subheader("Resumen General")
        
        kpi_cols = st.columns(4)
        with kpi_cols[0]:
            st.metric("Total Clientes", len(clientes))
        with kpi_cols[1]:
            st.metric("Cupo Total", format_currency(clientes['cupo_sugerido'].sum()))
        with kpi_cols[2]:
            st.metric("Saldo Total", format_currency(clientes['saldo_actual'].sum()))
        with kpi_cols[3]:
            st.metric("Disponible Total", format_currency(clientes['disponible'].sum()))
        
        st.divider()
        
        # Distribución por estado
        st.subheader("Distribución por Estado")
        
        if 'estado' in clientes.columns:
            estado_cols = st.columns(3)
            
            estados = clientes['estado'].value_counts()
            normal = estados.get('NORMAL', 0)
            alerta = estados.get('ALERTA', 0)
            sobrepasado = estados.get('SOBREPASADO', 0)
            
            with estado_cols[0]:
                st.metric("NORMAL", normal)
            with estado_cols[1]:
                st.metric("ALERTA", alerta)
            with estado_cols[2]:
                st.metric("SOBREPASADO", sobrepasado)
        else:
            st.info("No hay información de estados disponible")
        
        st.divider()
        
        # Top clientes
        st.subheader("Ranking de Clientes")
        
        top_tabs = st.tabs(["Mayor % Uso", "Mayor Saldo", "Menor Disponible"])
        
        with top_tabs[0]:
            if 'porcentaje_uso' in clientes.columns:
                top_uso = clientes.nlargest(5, 'porcentaje_uso')
                for i, (_, cliente) in enumerate(top_uso.iterrows(), 1):
                    with st.container():
                        cols = st.columns([1, 4])
                        with cols[0]:
                            st.markdown(f"#{i}")
                        with cols[1]:
                            st.write(f"**{cliente['nombre']}**")
                            st.progress(min(cliente['porcentaje_uso'] / 100, 1))
                            st.caption(f"{format_percentage(cliente['porcentaje_uso'])}")
        
        with top_tabs[1]:
            if 'saldo_actual' in clientes.columns:
                top_saldo = clientes.nlargest(5, 'saldo_actual')
                for i, (_, cliente) in enumerate(top_saldo.iterrows(), 1):
                    with st.container():
                        cols = st.columns([1, 4])
                        with cols[0]:
                            st.markdown(f"#{i}")
                        with cols[1]:
                            st.write(f"**{cliente['nombre']}**")
                            st.metric("Saldo", format_currency(cliente['saldo_actual']))
        
        with top_tabs[2]:
            if 'disponible' in clientes.columns:
                top_disponible = clientes.nsmallest(5, 'disponible')
                for i, (_, cliente) in enumerate(top_disponible.iterrows(), 1):
                    with st.container():
                        cols = st.columns([1, 4])
                        with cols[0]:
                            st.markdown(f"#{i}")
                        with cols[1]:
                            st.write(f"**{cliente['nombre']}**")
                            disponible_val = cliente['disponible']
                            if disponible_val < 0:
                                st.error(f"Excedido: {format_currency(abs(disponible_val))}")
                            else:
                                st.info(f"Disponible: {format_currency(disponible_val)}")
        
    except Exception as e:
        st.error(f"Error en resumen: {str(e)}")
