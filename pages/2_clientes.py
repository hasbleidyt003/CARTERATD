"""
Página de gestión de clientes para Streamlit
Versión corregida sin parámetro max_length
"""

import streamlit as st
import pandas as pd
import sqlite3
import sys
import os

# Configuración de ruta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def show():
    st.header("👥 Gestión de Clientes")
    
    try:
        # Intentar importar desde módulos
        from modules.database import get_clientes, actualizar_cliente, crear_cliente, agregar_movimiento
    except ImportError as e:
        st.warning(f"⚠️ Usando funciones locales: {e}")
        # Definir funciones locales como fallback
        def get_clientes():
            conn = sqlite3.connect('data/database.db')
            query = '''
            SELECT 
                c.*,
                COALESCE(SUM(o.valor_pendiente), 0) as pendientes_total
            FROM clientes c
            LEFT JOIN ocs o ON c.nit = o.cliente_nit AND o.estado IN ('PENDIENTE', 'PARCIAL')
            WHERE c.activo = 1
            GROUP BY c.nit
            ORDER BY c.nombre
            '''
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        
        def actualizar_cliente(nit, cupo_sugerido=None, saldo_actual=None, nombre=None):
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            updates, params = [], []
            
            if cupo_sugerido is not None:
                updates.append("cupo_sugerido = ?")
                params.append(cupo_sugerido)
            if saldo_actual is not None:
                updates.append("saldo_actual = ?")
                params.append(saldo_actual)
            if nombre is not None:
                updates.append("nombre = ?")
                params.append(nombre)
            
            if updates:
                params.append(nit)
                query = f"UPDATE clientes SET {', '.join(updates)} WHERE nit = ?"
                cursor.execute(query, params)
                conn.commit()
            
            conn.close()
            return True
        
        def crear_cliente(nit, nombre, cupo_sugerido, saldo_actual=0):
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            try:
                cursor.execute('''
                INSERT INTO clientes (nit, nombre, cupo_sugerido, saldo_actual)
                VALUES (?, ?, ?, ?)
                ''', (nit, nombre, cupo_sugerido, saldo_actual))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                raise Exception(f"Ya existe cliente con NIT: {nit}")
            finally:
                conn.close()
        
        def agregar_movimiento(cliente_nit, tipo, valor, descripcion="", referencia="", usuario="Sistema"):
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO movimientos (cliente_nit, tipo, valor, descripcion, referencia, usuario)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (cliente_nit, tipo, valor, descripcion, referencia, usuario))
            if tipo == 'PAGO':
                cursor.execute('UPDATE clientes SET saldo_actual = saldo_actual - ? WHERE nit = ?', (valor, cliente_nit))
            conn.commit()
            conn.close()
            return True
    
    # Pestañas
    tab1, tab2 = st.tabs(["📋 Lista de Clientes", "➕ Nuevo Cliente"])
    
    with tab1:
        mostrar_clientes()
    
    with tab2:
        agregar_cliente()

def mostrar_clientes():
    """Muestra lista de clientes y permite editar"""
    try:
        from modules.database import get_clientes, actualizar_cliente, agregar_movimiento
        
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
                if 'estado' in clientes.columns:
                    sobrepasados = len(clientes[clientes['estado'] == 'SOBREPASADO'])
                    st.metric("Clientes Críticos", sobrepasados)
                else:
                    st.metric("Clientes", len(clientes))
            
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
                    
                    with col3:
                        # Mostrar estadísticas actuales
                        disponible = nuevo_cupo - nuevo_saldo
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
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        if st.button("💾 Guardar", key=f"guardar_{cliente['nit']}", use_container_width=True):
                            try:
                                actualizar_cliente(
                                    nit=cliente['nit'],
                                    cupo_sugerido=nuevo_cupo,
                                    saldo_actual=nuevo_saldo,
                                    nombre=nuevo_nombre
                                )
                                st.success("✅ Cambios guardados exitosamente")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al guardar: {str(e)}")
                    
                    with col_b:
                        if st.button("➕ Nuevo Pago", key=f"pago_{cliente['nit']}", use_container_width=True):
                            st.session_state.registrar_pago = cliente['nit']
                            st.rerun()
            
            # Formulario para registrar pago (si está activo)
            if 'registrar_pago' in st.session_state:
                with st.form(f"pago_form_{st.session_state.registrar_pago}"):
                    st.subheader(f"💳 Registrar Pago - NIT: {st.session_state.registrar_pago}")
                    
                    cliente_actual = clientes[clientes['nit'] == st.session_state.registrar_pago].iloc[0]
                    st.info(f"Saldo actual: ${cliente_actual['saldo_actual']:,.0f}")
                    
                    valor_pago = st.number_input(
                        "Valor del Pago",
                        min_value=0.0,
                        max_value=float(cliente_actual['saldo_actual']),
                        step=1000000.0,
                        format="%.0f"
                    )
                    descripcion = st.text_input("Descripción")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.form_submit_button("✅ Confirmar Pago"):
                            agregar_movimiento(
                                cliente_nit=st.session_state.registrar_pago,
                                tipo="PAGO",
                                valor=valor_pago,
                                descripcion=descripcion,
                                referencia=f"PAGO-{st.session_state.registrar_pago}"
                            )
                            st.success(f"✅ Pago de ${valor_pago:,.0f} registrado")
                            del st.session_state.registrar_pago
                            st.rerun()
                    
                    with col_btn2:
                        if st.form_submit_button("❌ Cancelar"):
                            del st.session_state.registrar_pago
                            st.rerun()
                            
        else:
            st.info("No hay clientes registrados. Agrega el primero en la pestaña 'Nuevo Cliente'.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar clientes: {str(e)}")
        st.code(f"Detalles: {e.__class__.__name__}")

def agregar_cliente():
    """Formulario para agregar nuevo cliente - CORREGIDO sin max_length"""
    st.subheader("➕ Agregar Nuevo Cliente")
    
    with st.form("nuevo_cliente_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nit = st.text_input("NIT *", help="Número de Identificación Tributaria")
            nombre = st.text_input("Nombre del Cliente *", help="Nombre completo o razón social")
        
        with col2:
            cupo_sugerido = st.number_input(
                "Cupo Sugerido Inicial *", 
                min_value=0.0,
                value=0.0,
                step=1000000.0,
                format="%.0f",
                help="Cupo de crédito sugerido"
            )
            saldo_actual = st.number_input(
                "Saldo Actual Inicial *",
                min_value=0.0,
                value=0.0,
                step=1000000.0,
                format="%.0f",
                help="Saldo inicial de cartera"
            )
        
        # Cálculos en tiempo real
        disponible = cupo_sugerido - saldo_actual
        porcentaje_uso = (saldo_actual / cupo_sugerido * 100) if cupo_sugerido > 0 else 0
        
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
                from modules.database import crear_cliente
                
                crear_cliente(
                    nit=nit,
                    nombre=nombre,
                    cupo_sugerido=cupo_sugerido,
                    saldo_actual=saldo_actual
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
                - Disponible: ${disponible:,.0f}
                - % Uso Inicial: {porcentaje_uso:.1f}%
                """)
                
                # Opción para agregar otro
                if st.button("➕ Agregar Otro Cliente"):
                    st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error al crear cliente: {str(e)}")

# Solo para pruebas locales
if __name__ == "__main__":
    show()
