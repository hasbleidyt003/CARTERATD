"""
Página de gestión de clientes para Streamlit
Compatible con modules/database.py
"""

import streamlit as st
import pandas as pd
import sqlite3
import sys
import os

# Configurar path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==================== MANEJO DE IMPORTACIONES ====================

def cargar_modulo_database():
    """
    Carga el módulo database con manejo inteligente de errores
    y caché de Streamlit
    """
    try:
        # Intentar importar normalmente
        from modules import database
        st.success("✅ Módulo database importado correctamente")
        return database
    except ImportError as e:
        st.warning(f"⚠️ No se pudo importar modules.database: {e}")
        st.info("🔄 Usando funciones locales como fallback...")
        
        # Crear clase local con funciones mínimas
        class DatabaseLocal:
            @staticmethod
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
            
            @staticmethod
            def actualizar_cliente(nit, **kwargs):
                conn = sqlite3.connect('data/database.db')
                cursor = conn.cursor()
                
                updates = []
                params = []
                
                campos_validos = ['cupo_sugerido', 'saldo_actual', 'nombre']
                for key, value in kwargs.items():
                    if value is not None and key in campos_validos:
                        updates.append(f"{key} = ?")
                        params.append(value)
                
                if updates:
                    updates.append("fecha_actualizacion = CURRENT_TIMESTAMP")
                    params.append(nit)
                    query = f"UPDATE clientes SET {', '.join(updates)} WHERE nit = ?"
                    cursor.execute(query, params)
                    conn.commit()
                
                conn.close()
                return True
            
            @staticmethod
            def agregar_movimiento(cliente_nit, tipo, valor, **kwargs):
                conn = sqlite3.connect('data/database.db')
                cursor = conn.cursor()
                
                descripcion = kwargs.get('descripcion', '')
                referencia = kwargs.get('referencia', '')
                usuario = kwargs.get('usuario', 'Sistema')
                
                cursor.execute('''
                INSERT INTO movimientos (cliente_nit, tipo, valor, descripcion, referencia, usuario)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (cliente_nit, tipo, valor, descripcion, referencia, usuario))
                
                if tipo == 'PAGO':
                    cursor.execute('''
                    UPDATE clientes 
                    SET saldo_actual = saldo_actual - ?, 
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE nit = ?
                    ''', (valor, cliente_nit))
                
                conn.commit()
                conn.close()
                return True
            
            @staticmethod
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
        
        return DatabaseLocal()

# Cargar módulo de base de datos
database = cargar_modulo_database()

# ==================== FUNCIÓN PRINCIPAL ====================

def show():
    """Función principal de la página"""
    st.header("👥 Gestión de Clientes")
    
    # Pestañas principales
    tab1, tab2 = st.tabs(["📋 Lista de Clientes", "➕ Nuevo Cliente"])
    
    with tab1:
        mostrar_clientes()
    
    with tab2:
        agregar_cliente()

# ==================== FUNCIONES DE LA PESTAÑA 1 ====================

def mostrar_clientes():
    """Muestra y permite editar la lista de clientes"""
    try:
        # Obtener clientes
        with st.spinner("Cargando clientes..."):
            clientes = database.get_clientes()
        
        if not clientes.empty:
            # Estadísticas
            st.subheader(f"📊 Total de Clientes: {len(clientes)}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Cupo Total", f"${clientes['cupo_sugerido'].sum():,.0f}")
            with col2:
                st.metric("Saldo Total", f"${clientes['saldo_actual'].sum():,.0f}")
            with col3:
                st.metric("Disponible", f"${clientes['disponible'].sum():,.0f}")
            with col4:
                if 'pendientes_total' in clientes.columns:
                    pendientes = clientes['pendientes_total'].sum()
                    st.metric("OCs Pendientes", f"${pendientes:,.0f}")
            
            st.divider()
            
            # Lista de clientes editable
            st.subheader("📝 Editar Clientes")
            
            for _, cliente in clientes.iterrows():
                with st.expander(f"{cliente['nombre']} - NIT: {cliente['nit']}", expanded=False):
                    # Formulario de edición
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        nuevo_nombre = st.text_input(
                            "Nombre",
                            value=cliente['nombre'],
                            key=f"nombre_{cliente['nit']}"
                        )
                    
                    with col2:
                        nuevo_cupo = st.number_input(
                            "Cupo Sugerido",
                            value=float(cliente['cupo_sugerido']),
                            min_value=0.0,
                            step=100000.0,
                            format="%.0f",
                            key=f"cupo_{cliente['nit']}"
                        )
                    
                    with col3:
                        nuevo_saldo = st.number_input(
                            "Saldo Actual",
                            value=float(cliente['saldo_actual']),
                            min_value=0.0,
                            step=100000.0,
                            format="%.0f",
                            key=f"saldo_{cliente['nit']}"
                        )
                    
                    # Cálculos en tiempo real
                    disponible = nuevo_cupo - nuevo_saldo
                    porcentaje_uso = (nuevo_saldo / nuevo_cupo * 100) if nuevo_cupo > 0 else 0
                    
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.metric("Disponible", f"${disponible:,.0f}")
                    with col_info2:
                        st.metric("% Uso Cupo", f"{porcentaje_uso:.1f}%")
                    
                    # Botones de acción
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    with col_btn1:
                        if st.button("💾 Guardar", key=f"guardar_{cliente['nit']}", use_container_width=True):
                            try:
                                database.actualizar_cliente(
                                    nit=cliente['nit'],
                                    nombre=nuevo_nombre,
                                    cupo_sugerido=nuevo_cupo,
                                    saldo_actual=nuevo_saldo
                                )
                                st.success("✅ Cambios guardados exitosamente")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al guardar: {str(e)}")
                    
                    with col_btn2:
                        if st.button("💰 Registrar Pago", key=f"pago_{cliente['nit']}", use_container_width=True):
                            st.session_state[f'pago_cliente_{cliente["nit"]}'] = True
                            st.rerun()
                    
                    with col_btn3:
                        if st.button("📊 Ver Detalles", key=f"detalle_{cliente['nit']}", use_container_width=True):
                            st.session_state[f'detalle_cliente_{cliente["nit"]}'] = True
                    
                    # Formulario de pago (si está activo)
                    if f'pago_cliente_{cliente["nit"]}' in st.session_state:
                        with st.form(f"form_pago_{cliente['nit']}"):
                            st.subheader(f"💳 Registrar Pago - {cliente['nombre']}")
                            
                            max_pago = float(cliente['saldo_actual'])
                            valor_pago = st.number_input(
                                "Valor del pago",
                                min_value=0.0,
                                max_value=max_pago,
                                value=min(1000000.0, max_pago),
                                step=100000.0,
                                format="%.0f"
                            )
                            
                            descripcion = st.text_input("Descripción", placeholder="Ej: Pago factura #12345")
                            
                            col_submit, col_cancel = st.columns(2)
                            with col_submit:
                                if st.form_submit_button("✅ Confirmar Pago"):
                                    try:
                                        database.agregar_movimiento(
                                            cliente_nit=cliente['nit'],
                                            tipo="PAGO",
                                            valor=valor_pago,
                                            descripcion=descripcion,
                                            referencia=f"PAGO-{cliente['nit']}-{pd.Timestamp.now().strftime('%Y%m%d')}"
                                        )
                                        st.success(f"✅ Pago de ${valor_pago:,.0f} registrado")
                                        del st.session_state[f'pago_cliente_{cliente["nit"]}']
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error: {str(e)}")
                            
                            with col_cancel:
                                if st.form_submit_button("❌ Cancelar"):
                                    del st.session_state[f'pago_cliente_{cliente["nit"]}']
                                    st.rerun()
            
            # Tabla resumen
            st.divider()
            st.subheader("📋 Resumen de Clientes")
            
            # Preparar datos para tabla
            df_resumen = clientes.copy()
            df_resumen['% Uso'] = (df_resumen['saldo_actual'] / df_resumen['cupo_sugerido'] * 100).round(1)
            df_resumen['Estado'] = df_resumen['% Uso'].apply(
                lambda x: '🟢 Normal' if x < 80 else '🟡 Alerta' if x < 100 else '🔴 Sobrepasado'
            )
            
            # Mostrar tabla
            columnas_mostrar = ['nombre', 'nit', 'cupo_sugerido', 'saldo_actual', 'disponible', '% Uso', 'Estado']
            if 'pendientes_total' in df_resumen.columns:
                columnas_mostrar.append('pendientes_total')
            
            st.dataframe(
                df_resumen[columnas_mostrar].rename(columns={
                    'nombre': 'Nombre',
                    'nit': 'NIT',
                    'cupo_sugerido': 'Cupo Sugerido',
                    'saldo_actual': 'Saldo Actual',
                    'disponible': 'Disponible',
                    'pendientes_total': 'OCs Pendientes'
                }),
                use_container_width=True,
                hide_index=True
            )
            
        else:
            st.info("📭 No hay clientes registrados. Agrega el primero en la pestaña 'Nuevo Cliente'.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar clientes: {str(e)}")
        st.code(f"Detalle del error: {e}")

# ==================== FUNCIONES DE LA PESTAÑA 2 ====================

def agregar_cliente():
    """Formulario para agregar nuevo cliente"""
    st.subheader("➕ Agregar Nuevo Cliente")
    
    with st.form("form_nuevo_cliente"):
        col1, col2 = st.columns(2)
        
        with col1:
            nit = st.text_input("NIT *", max_length=20, 
                               help="Número de identificación tributaria")
            nombre = st.text_input("Nombre del Cliente *", max_length=200,
                                  help="Nombre completo o razón social")
        
        with col2:
            cupo_sugerido = st.number_input(
                "Cupo Sugerido *", 
                min_value=0.0,
                value=1000000.0,
                step=100000.0,
                format="%.0f",
                help="Cupo de crédito sugerido para el cliente"
            )
            saldo_actual = st.number_input(
                "Saldo Actual Inicial *",
                min_value=0.0,
                value=0.0,
                step=100000.0,
                format="%.0f",
                help="Saldo inicial de cartera"
            )
        
        # Información de cálculo
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
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            # Validaciones
            if not nit.strip():
                st.error("❌ El NIT es obligatorio")
                return
            
            if not nombre.strip():
                st.error("❌ El nombre es obligatorio")
                return
            
            if cupo_sugerido <= 0:
                st.error("❌ El cupo sugerido debe ser mayor a 0")
                return
            
            try:
                # Crear cliente
                database.crear_cliente(
                    nit=nit.strip(),
                    nombre=nombre.strip(),
                    cupo_sugerido=cupo_sugerido,
                    saldo_actual=saldo_actual
                )
                
                st.success(f"✅ Cliente '{nombre}' creado exitosamente")
                st.balloons()
                
                # Mostrar resumen
                with st.expander("📋 Resumen del cliente creado", expanded=True):
                    st.write(f"**NIT:** {nit}")
                    st.write(f"**Nombre:** {nombre}")
                    st.write(f"**Cupo Sugerido:** ${cupo_sugerido:,.0f}")
                    st.write(f"**Saldo Actual:** ${saldo_actual:,.0f}")
                    st.write(f"**Disponible:** ${disponible:,.0f}")
                    st.write(f"**% Uso Inicial:** {porcentaje_uso:.1f}%")
                
                # Opción para continuar
                col_continuar, col_ver = st.columns(2)
                with col_continuar:
                    if st.button("➕ Agregar Otro Cliente"):
                        st.rerun()
                with col_ver:
                    if st.button("📋 Ver Lista de Clientes"):
                        st.session_state['active_tab'] = 0
                        st.rerun()
                        
            except Exception as e:
                st.error(f"❌ Error al crear cliente: {str(e)}")

# ==================== EJECUCIÓN DIRECTA (PARA PRUEBAS) ====================

if __name__ == "__main__":
    # Para pruebas locales
    st.set_page_config(page_title="Clientes", layout="wide")
    show()
