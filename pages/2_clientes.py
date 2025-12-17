import streamlit as st
import pandas as pd
from modules.database import get_clientes, actualizar_cliente, agregar_movimiento
import sqlite3

def show():
    st.header("👥 Gestión de Clientes")
    
    # Pestañas para diferentes funciones
    tab1, tab2 = st.tabs(["📋 Lista de Clientes", "➕ Nuevo Cliente"])
    
    with tab1:
        mostrar_clientes()
    
    with tab2:
        agregar_cliente()

def mostrar_clientes():
    """Muestra lista de clientes y permite editar"""
    clientes = get_clientes()
    
    if not clientes.empty:
        st.subheader(f"📊 Total de Clientes: {len(clientes)}")
        
        # Mostrar estadísticas rápidas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Cupo Total", f"${clientes['cupo_sugerido'].sum():,.0f}")
        with col2:
            st.metric("Saldo Total", f"${clientes['saldo_actual'].sum():,.0f}")
        with col3:
            sobrepasados = len(clientes[clientes['estado'] == 'SOBREPASADO'])
            st.metric("Clientes Críticos", sobrepasados)
        
        st.divider()
        
        # Formulario de edición para cada cliente
        for _, cliente in clientes.iterrows():
            with st.expander(f"{cliente['nombre']} (NIT: {cliente['nit']})", expanded=False):
                col1, col2, col3 = st.columns(3)
                
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
                    
                    if 'cartera_vencida' in cliente:
                        nueva_cartera = st.number_input(
                            "Cartera Vencida",
                            value=float(cliente['cartera_vencida']),
                            min_value=0.0,
                            step=1000000.0,
                            format="%.0f",
                            key=f"cartera_{cliente['nit']}"
                        )
                    else:
                        nueva_cartera = 0.0
                
                with col3:
                    # Mostrar estadísticas actuales
                    disponible = nuevo_cupo - nuevo_saldo - nueva_cartera
                    porcentaje_uso = (nuevo_saldo / nuevo_cupo * 100) if nuevo_cupo > 0 else 0
                    
                    st.metric("Disponible", f"${disponible:,.0f}")
                    st.metric("% Uso", f"{porcentaje_uso:.1f}%")
                    
                    # Determinar estado
                    estado = "NORMAL"
                    if disponible < 0:
                        estado = "SOBREPASADO"
                    elif porcentaje_uso > 80:
                        estado = "ALERTA"
                    
                    st.metric("Estado", estado)
                
                # Botones de acción
                col_a, col_b, col_c = st.columns([1, 1, 2])
                
                with col_a:
                    if st.button("💾 Guardar", key=f"guardar_{cliente['nit']}", use_container_width=True):
                        guardar_cambios_cliente(
                            cliente['nit'],
                            nuevo_cupo,
                            nuevo_saldo,
                            nueva_cartera,
                            nuevo_nombre
                        )
                
                with col_b:
                    if st.button("📊 Ver Detalle", key=f"detalle_{cliente['nit']}", use_container_width=True):
                        st.session_state.cliente_detalle = cliente['nit']
                        st.rerun()
                
                with col_c:
                    if st.button("➕ Nuevo Pago", key=f"pago_{cliente['nit']}", use_container_width=True):
                        with st.form(f"pago_form_{cliente['nit']}"):
                            valor_pago = st.number_input(
                                "Valor del Pago",
                                min_value=0.0,
                                step=1000000.0,
                                format="%.0f"
                            )
                            descripcion = st.text_input("Descripción")
                            
                            if st.form_submit_button("💳 Registrar Pago"):
                                agregar_movimiento(
                                    cliente_nit=cliente['nit'],
                                    tipo="PAGO",
                                    valor=valor_pago,
                                    descripcion=descripcion,
                                    referencia=f"PAGO-{cliente['nit']}"
                                )
                                st.success(f"✅ Pago de ${valor_pago:,.0f} registrado")
                                st.rerun()
    else:
        st.info("No hay clientes registrados. Agrega el primero en la pestaña 'Nuevo Cliente'.")

def guardar_cambios_cliente(nit, cupo_sugerido, saldo_actual, cartera_vencida, nombre=None):
    """Guarda los cambios de un cliente en la base de datos"""
    try:
        # Actualizar datos principales
        actualizar_cliente(nit, cupo_sugerido, saldo_actual, cartera_vencida)
        
        # Actualizar nombre si cambió
        if nombre:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clientes SET nombre = ? WHERE nit = ?",
                (nombre, nit)
            )
            conn.commit()
            conn.close()
        
        st.success("✅ Cambios guardados exitosamente")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error al guardar: {str(e)}")

def agregar_cliente():
    """Formulario para agregar nuevo cliente"""
    st.subheader("➕ Agregar Nuevo Cliente")
    
    with st.form("nuevo_cliente_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nit = st.text_input("NIT *", max_length=20)
            nombre = st.text_input("Nombre del Cliente *", max_length=200)
        
        with col2:
            cupo_sugerido = st.number_input(
                "Cupo Sugerido Inicial *", 
                min_value=0.0,
                value=0.0,
                step=1000000.0,
                format="%.0f"
            )
            saldo_actual = st.number_input(
                "Saldo Actual Inicial *",
                min_value=0.0,
                value=0.0,
                step=1000000.0,
                format="%.0f"
            )
        
        cartera_vencida = st.number_input(
            "Cartera Vencida Inicial",
            min_value=0.0,
            value=0.0,
            step=1000000.0,
            format="%.0f",
            help="Deje en 0 si no hay cartera vencida"
        )
        
        notas = st.text_area("Notas adicionales (opcional)")
        
        # Validación y botón de envío
        col_submit1, col_submit2 = st.columns([3, 1])
        
        with col_submit1:
            submitted = st.form_submit_button(
                "💾 Crear Cliente", 
                use_container_width=True,
                type="primary"
            )
        
        with col_submit2:
            if st.form_submit_button("🔄 Limpiar", use_container_width=True):
                st.rerun()
        
        if submitted:
            # Validar campos obligatorios
            if not nit or not nombre:
                st.error("❌ Los campos marcados con * son obligatorios")
                return
            
            if cupo_sugerido <= 0:
                st.error("❌ El cupo sugerido debe ser mayor a 0")
                return
            
            try:
                # Insertar en base de datos
                conn = sqlite3.connect('data/database.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                INSERT INTO clientes 
                (nit, nombre, cupo_sugerido, saldo_actual, cartera_vencida, fecha_actualizacion)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (nit, nombre, cupo_sugerido, saldo_actual, cartera_vencida))
                
                conn.commit()
                conn.close()
                
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
                - Disponible: ${cupo_sugerido - saldo_actual - cartera_vencida:,.0f}
                """)
                
                # Opción para agregar otro
                if st.button("➕ Agregar Otro Cliente"):
                    st.rerun()
                
            except sqlite3.IntegrityError:
                st.error(f"❌ Ya existe un cliente con NIT: {nit}")
            except Exception as e:
                st.error(f"❌ Error al crear cliente: {str(e)}")

# Función adicional para mostrar detalle de cliente
def mostrar_detalle_cliente():
    """Muestra detalle completo de un cliente"""
    if 'cliente_detalle' in st.session_state:
        nit = st.session_state.cliente_detalle
        
        st.subheader(f"📋 Detalle Completo - NIT: {nit}")
        
        # Obtener datos del cliente
        conn = sqlite3.connect('data/database.db')
        
        # Datos del cliente
        query_cliente = '''
        SELECT * FROM clientes WHERE nit = ?
        '''
        cliente = pd.read_sql_query(query_cliente, conn, params=(nit,))
        
        if not cliente.empty:
            cliente = cliente.iloc[0]
            
            # Mostrar información
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Información Básica**")
                st.write(f"- NIT: {cliente['nit']}")
                st.write(f"- Nombre: {cliente['nombre']}")
                st.write(f"- Estado: {cliente.get('estado', 'N/A')}")
                st.write(f"- Última actualización: {cliente.get('fecha_actualizacion', 'N/A')}")
            
            with col2:
                st.write("**Información Financiera**")
                st.write(f"- Cupo Sugerido: ${cliente['cupo_sugerido']:,.0f}")
                st.write(f"- Saldo Actual: ${cliente['saldo_actual']:,.0f}")
                st.write(f"- Cartera Vencida: ${cliente.get('cartera_vencida', 0):,.0f}")
                st.write(f"- Disponible: ${cliente.get('disponible', 0):,.0f}")
                st.write(f"- % Uso: {cliente.get('porcentaje_uso', 0)}%")
            
            # Movimientos del cliente
            st.divider()
            st.write("**📝 Historial de Movimientos**")
            
            query_movimientos = '''
            SELECT * FROM movimientos 
            WHERE cliente_nit = ? 
            ORDER BY fecha_movimiento DESC
            LIMIT 10
            '''
            movimientos = pd.read_sql_query(query_movimientos, conn, params=(nit,))
            
            if not movimientos.empty:
                st.dataframe(
                    movimientos[['fecha_movimiento', 'tipo', 'valor', 'descripcion', 'referencia']],
                    hide_index=True
                )
            else:
                st.info("No hay movimientos registrados")
            
            # OCs del cliente
            st.write("**📋 Órdenes de Compra**")
            
            query_ocs = '''
            SELECT * FROM ocs 
            WHERE cliente_nit = ? 
            ORDER BY fecha_registro DESC
            '''
            ocs = pd.read_sql_query(query_ocs, conn, params=(nit,))
            
            if not ocs.empty:
                st.dataframe(
                    ocs[['numero_oc', 'valor_total', 'valor_autorizado', 'estado', 'fecha_registro']],
                    hide_index=True
                )
            else:
                st.info("No hay OCs registradas")
        
        conn.close()
        
        # Botón para volver
        if st.button("← Volver a la lista"):
            del st.session_state.cliente_detalle
            st.rerun()
