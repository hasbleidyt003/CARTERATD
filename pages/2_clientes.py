"""
Página de gestión de clientes - CORREGIDA
"""

import streamlit as st
import pandas as pd
import sqlite3
import os

def get_clientes():
    """Obtiene todos los clientes activos"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT 
        c.*,
        -- Calcular estado dinámicamente
        CASE 
            WHEN c.saldo_actual + c.cartera_vencida > c.cupo_sugerido THEN 'SOBREPASADO'
            WHEN c.saldo_actual + c.cartera_vencida > (c.cupo_sugerido * 0.8) THEN 'ALERTA'
            ELSE 'NORMAL'
        END as estado,
        ROUND(((c.saldo_actual + c.cartera_vencida) * 100.0 / c.cupo_sugerido), 2) as porcentaje_uso_total
    FROM clientes c
    WHERE c.activo = 1
    ORDER BY c.nombre
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def actualizar_cliente(nit, cupo_sugerido=None, saldo_actual=None, cartera_vencida=None, nombre=None):
    """Actualiza los datos de un cliente"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if cupo_sugerido is not None:
        updates.append("cupo_sugerido = ?")
        params.append(cupo_sugerido)
    
    if saldo_actual is not None:
        updates.append("saldo_actual = ?")
        params.append(saldo_actual)
    
    if cartera_vencida is not None:
        updates.append("cartera_vencida = ?")
        params.append(cartera_vencida)
    
    if nombre is not None:
        updates.append("nombre = ?")
        params.append(nombre)
    
    if updates:
        updates.append("fecha_actualizacion = CURRENT_TIMESTAMP")
        params.append(nit)
        
        query = f"UPDATE clientes SET {', '.join(updates)} WHERE nit = ?"
        cursor.execute(query, params)
        conn.commit()
    
    conn.close()
    return True

def crear_cliente(nit, nombre, cupo_sugerido, saldo_actual=0, cartera_vencida=0):
    """Crea un nuevo cliente"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO clientes (nit, nombre, cupo_sugerido, saldo_actual, cartera_vencida)
        VALUES (?, ?, ?, ?, ?)
        ''', (nit, nombre, cupo_sugerido, saldo_actual, cartera_vencida))
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        raise Exception(f"Ya existe un cliente con NIT: {nit}")
    except Exception as e:
        raise Exception(f"Error al crear cliente: {str(e)}")
    finally:
        conn.close()

def agregar_movimiento(cliente_nit, tipo, valor, descripcion="", referencia="", usuario="Sistema"):
    """Registra un movimiento"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        # Insertar movimiento
        cursor.execute('''
        INSERT INTO movimientos (cliente_nit, tipo, valor, descripcion, referencia, usuario)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (cliente_nit, tipo, valor, descripcion, referencia, usuario))
        
        # Actualizar saldo si es pago
        if tipo == 'PAGO':
            cursor.execute('''
            UPDATE clientes 
            SET saldo_actual = saldo_actual - ?,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE nit = ?
            ''', (valor, cliente_nit))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error al registrar movimiento: {str(e)}")
    finally:
        conn.close()

def get_movimientos_cliente(cliente_nit, limit=20):
    """Obtiene los movimientos de un cliente"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT * FROM movimientos 
    WHERE cliente_nit = ? 
    ORDER BY fecha_movimiento DESC
    LIMIT ?
    '''
    df = pd.read_sql_query(query, conn, params=(cliente_nit, limit))
    conn.close()
    return df

def show():
    st.header("👥 Gestión de Clientes")
    
    # Verificar que la base de datos exista
    if not os.path.exists('data/database.db'):
        st.error("❌ La base de datos no está inicializada. Ve al Dashboard primero.")
        return
    
    # Pestañas
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Clientes", "➕ Nuevo Cliente", "💳 Movimientos"])
    
    with tab1:
        mostrar_lista_clientes()
    
    with tab2:
        mostrar_form_nuevo_cliente()
    
    with tab3:
        mostrar_movimientos()

def mostrar_lista_clientes():
    """Muestra la lista de clientes con opción de editar"""
    try:
        clientes = get_clientes()
        
        if not clientes.empty:
            st.subheader(f"📊 Total de Clientes: {len(clientes)}")
            
            # Estadísticas rápidas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Cupo Total", f"${clientes['cupo_sugerido'].sum():,.0f}")
            with col2:
                st.metric("Saldo Total", f"${clientes['saldo_actual'].sum():,.0f}")
            with col3:
                if 'estado' in clientes.columns:
                    criticos = len(clientes[clientes['estado'].isin(['SOBREPASADO', 'ALERTA'])])
                    st.metric("Clientes Críticos", criticos)
            
            st.divider()
            
            # Formulario de edición para cada cliente
            for _, cliente in clientes.iterrows():
                with st.expander(f"{cliente['nombre']} (NIT: {cliente['nit']})", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
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
                    
                    with col2:
                        nuevo_saldo = st.number_input(
                            "Saldo Actual",
                            value=float(cliente['saldo_actual']),
                            min_value=0.0,
                            step=1000000.0,
                            format="%.0f",
                            key=f"saldo_{cliente['nit']}"
                        )
                        
                        nueva_cartera = st.number_input(
                            "Cartera Vencida",
                            value=float(cliente['cartera_vencida']),
                            min_value=0.0,
                            step=1000000.0,
                            format="%.0f",
                            key=f"cartera_{cliente['nit']}"
                        )
                    
                    # Calcular métricas en tiempo real
                    disponible = nuevo_cupo - nuevo_saldo - nueva_cartera
                    porcentaje_uso = ((nuevo_saldo + nueva_cartera) / nuevo_cupo * 100) if nuevo_cupo > 0 else 0
                    
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.metric("Disponible", f"${disponible:,.0f}")
                    with col_info2:
                        st.metric("% Uso Total", f"{porcentaje_uso:.1f}%")
                    
                    # Determinar estado
                    estado_color = ""
                    if nuevo_saldo + nueva_cartera > nuevo_cupo:
                        estado_color = "🔴 SOBREPASADO"
                    elif porcentaje_uso > 80:
                        estado_color = "🟡 ALERTA"
                    else:
                        estado_color = "🟢 NORMAL"
                    
                    st.info(f"**Estado:** {estado_color}")
                    
                    # Botones de acción
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button("💾 Guardar", key=f"guardar_{cliente['nit']}", use_container_width=True):
                            try:
                                actualizar_cliente(
                                    nit=cliente['nit'],
                                    cupo_sugerido=nuevo_cupo,
                                    saldo_actual=nuevo_saldo,
                                    cartera_vencida=nueva_cartera,
                                    nombre=nuevo_nombre
                                )
                                st.success("✅ Cambios guardados exitosamente")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al guardar: {str(e)}")
                    
                    with col_btn2:
                        if st.button("💳 Registrar Pago", key=f"pago_{cliente['nit']}", use_container_width=True):
                            st.session_state.registrar_pago = cliente['nit']
                            st.rerun()
        else:
            st.info("📭 No hay clientes registrados. Agrega el primero en la pestaña 'Nuevo Cliente'.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar clientes: {str(e)}")

def mostrar_form_nuevo_cliente():
    """Formulario para agregar nuevo cliente"""
    with st.form("nuevo_cliente_form"):
        st.subheader("➕ Agregar Nuevo Cliente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nit = st.text_input("NIT *", help="Número de Identificación Tributaria")
            nombre = st.text_input("Nombre del Cliente *", help="Nombre completo o razón social")
        
        with col2:
            cupo_sugerido = st.number_input(
                "Cupo Sugerido *", 
                min_value=0.0,
                value=10000000.0,
                step=1000000.0,
                format="%.0f",
                help="Cupo de crédito sugerido"
            )
            saldo_actual = st.number_input(
                "Saldo Actual",
                min_value=0.0,
                value=0.0,
                step=1000000.0,
                format="%.0f",
                help="Saldo inicial de cartera"
            )
            cartera_vencida = st.number_input(
                "Cartera Vencida",
                min_value=0.0,
                value=0.0,
                step=1000000.0,
                format="%.0f",
                help="Cartera vencida inicial"
            )
        
        # Cálculos en tiempo real
        disponible = cupo_sugerido - saldo_actual - cartera_vencida
        porcentaje_uso = ((saldo_actual + cartera_vencida) / cupo_sugerido * 100) if cupo_sugerido > 0 else 0
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.metric("Disponible Inicial", f"${disponible:,.0f}")
        with col_info2:
            st.metric("% Uso Inicial", f"{porcentaje_uso:.1f}%")
        
        # Botón de envío
        submitted = st.form_submit_button(
            "💾 Crear Cliente", 
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            # Validar campos obligatorios
            if not nit or not nombre:
                st.error("❌ Los campos marcados con * son obligatorios")
                return
            
            if cupo_sugerido <= 0:
                st.error("❌ El cupo sugerido debe ser mayor a 0")
                return
            
            try:
                crear_cliente(
                    nit=nit,
                    nombre=nombre,
                    cupo_sugerido=cupo_sugerido,
                    saldo_actual=saldo_actual,
                    cartera_vencida=cartera_vencida
                )
                
                st.success(f"✅ Cliente '{nombre}' creado exitosamente")
                st.balloons()
                
                # Mostrar resumen
                st.info(f"""
                **Resumen del cliente creado:**
                - NIT: {nit}
                - Nombre: {nombre}
                - Cupo Sugerido: ${cupo_sugerido:,.0f}
                - Saldo Actual: ${saldo_actual:,.0f}
                - Cartera Vencida: ${cartera_vencida:,.0f}
                - Disponible: ${disponible:,.0f}
                - % Uso Inicial: {porcentaje_uso:.1f}%
                """)
                
                # Opción para agregar otro
                if st.button("➕ Agregar Otro Cliente"):
                    st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error al crear cliente: {str(e)}")

def mostrar_movimientos():
    """Muestra y gestiona movimientos de clientes"""
    st.subheader("💳 Gestión de Movimientos")
    
    try:
        # Obtener lista de clientes para seleccionar
        clientes = get_clientes()
        
        if clientes.empty:
            st.info("Primero agrega clientes para registrar movimientos")
            return
        
        col_sel1, col_sel2 = st.columns(2)
        
        with col_sel1:
            cliente_seleccionado = st.selectbox(
                "Seleccionar Cliente:",
                options=clientes['nombre'].tolist(),
                key="cliente_movimientos"
            )
        
        # Obtener NIT del cliente seleccionado
        cliente_nit = clientes[clientes['nombre'] == cliente_seleccionado]['nit'].iloc[0]
        cliente_info = clientes[clientes['nit'] == cliente_nit].iloc[0]
        
        with col_sel2:
            st.metric("Saldo Actual", f"${cliente_info['saldo_actual']:,.0f}")
        
        # Formulario para nuevo movimiento
        with st.form("nuevo_movimiento_form"):
            st.subheader(f"📝 Nuevo Movimiento - {cliente_seleccionado}")
            
            col_mov1, col_mov2 = st.columns(2)
            
            with col_mov1:
                tipo_movimiento = st.selectbox(
                    "Tipo de Movimiento *",
                    ["PAGO", "AJUSTE", "NOTA_CREDITO", "NOTA_DEBITO"],
                    help="Tipo de movimiento a registrar"
                )
                
                valor_movimiento = st.number_input(
                    "Valor *",
                    min_value=0.0,
                    value=0.0,
                    step=100000.0,
                    format="%.0f",
                    help="Valor del movimiento"
                )
            
            with col_mov2:
                descripcion = st.text_input(
                    "Descripción",
                    help="Descripción del movimiento"
                )
                
                referencia = st.text_input(
                    "Referencia",
                    help="Número de referencia (ej: PAGO-001)"
                )
            
            # Validaciones para pagos
            if tipo_movimiento == 'PAGO' and valor_movimiento > cliente_info['saldo_actual']:
                st.warning(f"⚠️ El valor del pago (${valor_movimiento:,.0f}) excede el saldo actual (${cliente_info['saldo_actual']:,.0f})")
            
            submitted = st.form_submit_button(
                "💾 Registrar Movimiento",
                type="primary",
                use_container_width=True
            )
            
            if submitted:
                if valor_movimiento <= 0:
                    st.error("❌ El valor debe ser mayor a 0")
                else:
                    try:
                        agregar_movimiento(
                            cliente_nit=cliente_nit,
                            tipo=tipo_movimiento,
                            valor=valor_movimiento,
                            descripcion=descripcion,
                            referencia=referencia
                        )
                        
                        st.success(f"✅ {tipo_movimiento} de ${valor_movimiento:,.0f} registrado exitosamente")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error al registrar movimiento: {str(e)}")
        
        st.divider()
        
        # Mostrar historial de movimientos
        st.subheader("📋 Historial de Movimientos")
        
        movimientos = get_movimientos_cliente(cliente_nit, limit=20)
        
        if not movimientos.empty:
            # Formatear para mostrar
            movimientos_display = movimientos.copy()
            movimientos_display['valor'] = movimientos_display['valor'].apply(lambda x: f"${x:,.0f}")
            movimientos_display['fecha_movimiento'] = pd.to_datetime(movimientos_display['fecha_movimiento']).dt.strftime('%d/%m/%Y %H:%M')
            
            st.dataframe(
                movimientos_display[['fecha_movimiento', 'tipo', 'valor', 'descripcion', 'referencia']].rename(columns={
                    'fecha_movimiento': 'Fecha',
                    'tipo': 'Tipo',
                    'valor': 'Valor',
                    'descripcion': 'Descripción',
                    'referencia': 'Referencia'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay movimientos registrados para este cliente")
            
    except Exception as e:
        st.error(f"❌ Error al cargar movimientos: {str(e)}")

if __name__ == "__main__":
    show()
