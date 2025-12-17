"""
Página de gestión de clientes para Streamlit
Con base de datos inicial de los 7 clientes principales
"""

import streamlit as st
import pandas as pd
import sqlite3
import sys
import os
from datetime import datetime

# Configuración de ruta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def show():
    st.header("👥 Gestión de Clientes")
    
    try:
        from modules.database import get_clientes, actualizar_cliente, crear_cliente, agregar_movimiento
    except ImportError as e:
        st.warning(f"⚠️ Usando funciones locales: {e}")
        # Definir funciones locales
        def get_clientes():
            conn = sqlite3.connect('data/database.db')
            try:
                # Verificar si la tabla existe
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clientes'")
                if not cursor.fetchone():
                    # Crear tabla con datos iniciales
                    crear_tabla_clientes(conn)
                
                query = '''
                SELECT 
                    c.*,
                    (c.cupo_sugerido - c.saldo_actual) as disponible,
                    (c.saldo_actual * 100.0 / c.cupo_sugerido) as porcentaje_uso,
                    CASE 
                        WHEN c.saldo_actual > c.cupo_sugerido THEN 'SOBREPASADO'
                        WHEN (c.saldo_actual * 100.0 / c.cupo_sugerido) > 80 THEN 'ALERTA'
                        ELSE 'NORMAL'
                    END as estado
                FROM clientes c
                WHERE c.activo = 1
                ORDER BY c.nombre
                '''
                df = pd.read_sql_query(query, conn)
                return df
            finally:
                conn.close()
        
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
                INSERT INTO clientes (nit, nombre, cupo_sugerido, saldo_actual, activo)
                VALUES (?, ?, ?, ?, 1)
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
            
            # Registrar movimiento
            cursor.execute('''
            INSERT INTO movimientos (cliente_nit, tipo, valor, descripcion, referencia, usuario, fecha)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (cliente_nit, tipo, valor, descripcion, referencia, usuario, datetime.now()))
            
            # Actualizar saldo del cliente
            if tipo == 'PAGO':
                cursor.execute('UPDATE clientes SET saldo_actual = saldo_actual - ? WHERE nit = ?', (valor, cliente_nit))
            elif tipo == 'OC_AUTORIZADA':
                cursor.execute('UPDATE clientes SET saldo_actual = saldo_actual + ? WHERE nit = ?', (valor, cliente_nit))
            
            conn.commit()
            conn.close()
            return True
    
    # Inicializar base de datos con los 7 clientes si no existen
    inicializar_clientes()
    
    # Pestañas
    tab1, tab2, tab3 = st.tabs(["📋 Clientes Existentes", "➕ Nuevo Cliente", "📊 Resumen General"])
    
    with tab1:
        mostrar_clientes()
    
    with tab2:
        agregar_cliente()
    
    with tab3:
        mostrar_resumen()

def crear_tabla_clientes(conn):
    """Crea la tabla de clientes si no existe"""
    cursor = conn.cursor()
    
    # Tabla clientes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        nit TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        cupo_sugerido REAL DEFAULT 0,
        saldo_actual REAL DEFAULT 0,
        activo INTEGER DEFAULT 1,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabla movimientos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movimientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_nit TEXT NOT NULL,
        tipo TEXT NOT NULL, -- PAGO, OC_AUTORIZADA, AJUSTE
        valor REAL NOT NULL,
        descripcion TEXT,
        referencia TEXT,
        usuario TEXT DEFAULT 'Sistema',
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cliente_nit) REFERENCES clientes (nit)
    )
    ''')
    
    conn.commit()

def inicializar_clientes():
    """Inicializa la base de datos con los 7 clientes principales"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # Crear tablas si no existen
    crear_tabla_clientes(conn)
    
    # Lista de los 7 clientes principales
    clientes_iniciales = [
        ('901212102', 'AUNA COLOMBIA S.A.S.', 21693849830, 19493849830),
        ('890905166', 'EMPRESA SOCIAL DEL ESTADO HOSPITAL MENTAL DE ANTIOQ', 7500000000, 7397192942),
        ('900249425', 'PHARMASAN S.A.S', 5910785209, 5710785209),
        ('900746052', 'NEURUM SAS', 5500000000, 5184247632),
        ('800241602', 'FUNDACION COLOMBIANA DE CANCEROLOGIA CLINICA VIDA', 3500000000, 3031469552),
        ('890985122', 'COOPERATIVA DE HOSPITALES DE ANTIOQUIA', 1500000000, 1291931405),
        ('811038014', 'GRUPO ONCOLOGICO INTERNACIONAL S.A.', 900000000, 806853666)
    ]
    
    # Insertar clientes si no existen
    for nit, nombre, cupo_sugerido, saldo_actual in clientes_iniciales:
        cursor.execute('''
        INSERT OR IGNORE INTO clientes (nit, nombre, cupo_sugerido, saldo_actual, activo)
        VALUES (?, ?, ?, ?, 1)
        ''', (nit, nombre, cupo_sugerido, saldo_actual))
    
    conn.commit()
    conn.close()

def mostrar_clientes():
    """Muestra lista de clientes y permite editar"""
    try:
        from modules.database import get_clientes, actualizar_cliente, agregar_movimiento
        
        clientes = get_clientes()
        
        if not clientes.empty:
            st.subheader(f"📊 Total de Clientes: {len(clientes)}")
            
            # Estadísticas rápidas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                cupo_total = clientes['cupo_sugerido'].sum()
                st.metric("Cupo Total", f"${cupo_total:,.0f}")
            with col2:
                saldo_total = clientes['saldo_actual'].sum()
                st.metric("Saldo Total", f"${saldo_total:,.0f}")
            with col3:
                disponible_total = clientes['disponible'].sum()
                st.metric("Disponible Total", f"${disponible_total:,.0f}")
            with col4:
                clientes_sobrepasados = len(clientes[clientes['estado'] == 'SOBREPASADO'])
                st.metric("Críticos", clientes_sobrepasados)
            
            st.divider()
            
            # Filtros
            st.write("🔍 **Filtrar por estado:**")
            col_filtros = st.columns(4)
            with col_filtros[0]:
                if st.button("Todos", use_container_width=True):
                    st.session_state.filtro_estado = "TODOS"
            with col_filtros[1]:
                if st.button("🟢 NORMAL", use_container_width=True):
                    st.session_state.filtro_estado = "NORMAL"
            with col_filtros[2]:
                if st.button("🟡 ALERTA", use_container_width=True):
                    st.session_state.filtro_estado = "ALERTA"
            with col_filtros[3]:
                if st.button("🔴 SOBREPASADO", use_container_width=True):
                    st.session_state.filtro_estado = "SOBREPASADO"
            
            # Aplicar filtro
            if 'filtro_estado' in st.session_state and st.session_state.filtro_estado != "TODOS":
                clientes = clientes[clientes['estado'] == st.session_state.filtro_estado]
            
            # Mostrar cada cliente en un expander
            for _, cliente in clientes.iterrows():
                # Determinar color según estado
                colores_estado = {
                    'NORMAL': '🟢',
                    'ALERTA': '🟡',
                    'SOBREPASADO': '🔴'
                }
                color = colores_estado.get(cliente['estado'], '⚪')
                
                with st.expander(f"{color} {cliente['nombre']} (NIT: {cliente['nit']})", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Formulario de edición
                        with st.form(key=f"form_{cliente['nit']}"):
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                nuevo_nombre = st.text_input(
                                    "Nombre del Cliente",
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
                            
                            with col_b:
                                nuevo_saldo = st.number_input(
                                    "Saldo Actual",
                                    value=float(cliente['saldo_actual']),
                                    min_value=0.0,
                                    step=1000000.0,
                                    format="%.0f",
                                    key=f"saldo_{cliente['nit']}"
                                )
                                
                                # Cálculos automáticos
                                nuevo_disponible = nuevo_cupo - nuevo_saldo
                                nuevo_porcentaje = (nuevo_saldo / nuevo_cupo * 100) if nuevo_cupo > 0 else 0
                                
                                st.metric("Disponible", f"${nuevo_disponible:,.0f}")
                                st.metric("% Uso", f"{nuevo_porcentaje:.1f}%")
                            
                            # Botones
                            col_btn1, col_btn2, col_btn3 = st.columns(3)
                            with col_btn1:
                                if st.form_submit_button("💾 Guardar Cambios", use_container_width=True):
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
                            
                            with col_btn2:
                                if st.form_submit_button("💳 Registrar Pago", use_container_width=True):
                                    st.session_state[f'pago_{cliente["nit"]}'] = True
                                    st.rerun()
                            
                            with col_btn3:
                                if st.form_submit_button("📝 Registrar OC", use_container_width=True):
                                    st.session_state[f'oc_{cliente["nit"]}'] = True
                                    st.rerun()
                    
                    with col2:
                        # Tarjeta de estado actual
                        st.info("**Estado Actual:**")
                        st.metric("Cupo", f"${cliente['cupo_sugerido']:,.0f}")
                        st.metric("Saldo", f"${cliente['saldo_actual']:,.0f}")
                        st.metric("Disponible", f"${cliente['disponible']:,.0f}")
                        st.metric("% Uso", f"{cliente['porcentaje_uso']:.1f}%")
                        
                        # Barra de progreso
                        porcentaje = min(cliente['porcentaje_uso'], 100)
                        st.progress(porcentaje / 100)
                        
                        # Estado
                        st.write(f"**Estado:** {cliente['estado']}")
                    
                    # Modal para registrar pago
                    if f'pago_{cliente["nit"]}' in st.session_state:
                        with st.form(key=f"pago_form_{cliente['nit']}"):
                            st.subheader(f"💳 Registrar Pago - {cliente['nombre']}")
                            
                            max_pago = cliente['saldo_actual']
                            valor_pago = st.number_input(
                                "Valor del Pago",
                                min_value=0.0,
                                max_value=float(max_pago),
                                value=float(max_pago),
                                step=1000000.0,
                                format="%.0f",
                                help=f"Máximo: ${max_pago:,.0f}"
                            )
                            
                            descripcion = st.text_input("Descripción del pago", placeholder="Ej: Pago factura 001, Transferencia bancaria")
                            referencia = st.text_input("Referencia", placeholder="Ej: PAGO-001, TRANS-123")
                            
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
                                            usuario=st.session_state.get('username', 'Sistema')
                                        )
                                        st.success(f"✅ Pago de ${valor_pago:,.0f} registrado")
                                        del st.session_state[f'pago_{cliente["nit"]}']
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error al registrar pago: {str(e)}")
                            
                            with col_can:
                                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                    del st.session_state[f'pago_{cliente["nit"]}']
                                    st.rerun()
                    
                    # Modal para registrar OC autorizada
                    if f'oc_{cliente["nit"]}' in st.session_state:
                        with st.form(key=f"oc_form_{cliente['nit']}"):
                            st.subheader(f"📋 Registrar OC Autorizada - {cliente['nombre']}")
                            
                            max_oc = cliente['disponible']
                            valor_oc = st.number_input(
                                "Valor de la OC",
                                min_value=0.0,
                                max_value=float(max_oc),
                                value=float(max_oc),
                                step=1000000.0,
                                format="%.0f",
                                help=f"Máximo basado en disponible: ${max_oc:,.0f}"
                            )
                            
                            num_oc = st.text_input("Número de OC", placeholder="Ej: OC-2024-001")
                            descripcion = st.text_input("Descripción", placeholder="Ej: Compra de medicamentos")
                            
                            col_sub, col_can = st.columns(2)
                            with col_sub:
                                if st.form_submit_button("✅ Registrar OC", use_container_width=True):
                                    try:
                                        agregar_movimiento(
                                            cliente_nit=cliente['nit'],
                                            tipo="OC_AUTORIZADA",
                                            valor=valor_oc,
                                            descripcion=descripcion,
                                            referencia=num_oc,
                                            usuario=st.session_state.get('username', 'Sistema')
                                        )
                                        st.success(f"✅ OC {num_oc} por ${valor_oc:,.0f} registrada")
                                        del st.session_state[f'oc_{cliente["nit"]}']
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error al registrar OC: {str(e)}")
                            
                            with col_can:
                                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                    del st.session_state[f'oc_{cliente["nit"]}']
                                    st.rerun()
            
            # Mostrar tabla resumen
            st.divider()
            st.subheader("📋 Resumen en Tabla")
            
            # Preparar datos para tabla
            df_resumen = clientes.copy()
            df_resumen = df_resumen[['nit', 'nombre', 'cupo_sugerido', 'saldo_actual', 'disponible', 'porcentaje_uso', 'estado']]
            df_resumen.columns = ['NIT', 'Cliente', 'Cupo Total', 'Saldo Actual', 'Disponible', '% Uso', 'Estado']
            
            # Formatear valores
            df_resumen['Cupo Total'] = df_resumen['Cupo Total'].apply(lambda x: f"${x:,.0f}")
            df_resumen['Saldo Actual'] = df_resumen['Saldo Actual'].apply(lambda x: f"${x:,.0f}")
            df_resumen['Disponible'] = df_resumen['Disponible'].apply(lambda x: f"${x:,.0f}")
            df_resumen['% Uso'] = df_resumen['% Uso'].apply(lambda x: f"{x:.1f}%")
            
            # Aplicar color según estado
            def color_estado(val):
                if 'SOBREPASADO' in val:
                    return 'color: red; font-weight: bold'
                elif 'ALERTA' in val:
                    return 'color: orange'
                else:
                    return 'color: green'
            
            st.dataframe(
                df_resumen.style.applymap(color_estado, subset=['Estado']),
                use_container_width=True,
                hide_index=True
            )
            
        else:
            st.info("📭 No hay clientes registrados. Agrega el primero en la pestaña 'Nuevo Cliente'.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar clientes: {str(e)}")
        st.exception(e)

def agregar_cliente():
    """Formulario para agregar nuevo cliente"""
    st.subheader("➕ Agregar Nuevo Cliente")
    
    with st.form("nuevo_cliente_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nit = st.text_input("NIT *", help="Número de Identificación Tributaria (10-11 dígitos)")
            nombre = st.text_input("Nombre del Cliente *", help="Nombre completo o razón social")
        
        with col2:
            cupo_sugerido = st.number_input(
                "Cupo Sugerido *", 
                min_value=0.0,
                value=1000000000.0,  # Valor por defecto 1,000 millones
                step=1000000.0,
                format="%.0f",
                help="Cupo de crédito sugerido para el cliente"
            )
            
            saldo_actual = st.number_input(
                "Saldo Actual Inicial",
                min_value=0.0,
                value=0.0,
                step=1000000.0,
                format="%.0f",
                help="Saldo inicial de cartera (dejar en 0 para nuevo cliente)"
            )
        
        # Cálculos en tiempo real
        disponible = cupo_sugerido - saldo_actual
        porcentaje_uso = (saldo_actual / cupo_sugerido * 100) if cupo_sugerido > 0 else 0
        
        # Mostrar resumen
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.metric("Disponible Inicial", f"${disponible:,.0f}")
        with col_info2:
            st.metric("% Uso Inicial", f"{porcentaje_uso:.1f}%")
        
        # Validar estado
        estado = "NORMAL"
        if disponible < 0:
            estado = "SOBREPASADO"
        elif porcentaje_uso > 80:
            estado = "ALERTA"
        
        st.info(f"**Estado inicial:** {estado}")
        
        # Botón de envío
        submitted = st.form_submit_button(
            "💾 Crear Cliente", 
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            # Validar campos obligatorios
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
                from modules.database import crear_cliente
                
                crear_cliente(
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
                    st.write(f"**Estado:** {estado}")
                
                # Opción para agregar otro
                if st.button("➕ Agregar Otro Cliente", use_container_width=True):
                    st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error al crear cliente: {str(e)}")

def mostrar_resumen():
    """Muestra un resumen general de todos los clientes"""
    try:
        from modules.database import get_clientes
        
        clientes = get_clientes()
        
        if clientes.empty:
            st.info("No hay clientes registrados")
            return
        
        st.subheader("📊 Resumen General de Clientes")
        
        # Estadísticas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_clientes = len(clientes)
            st.metric("Total Clientes", total_clientes)
        
        with col2:
            cupo_total = clientes['cupo_sugerido'].sum()
            st.metric("Cupo Total", f"${cupo_total:,.0f}")
        
        with col3:
            saldo_total = clientes['saldo_actual'].sum()
            st.metric("Saldo Total", f"${saldo_total:,.0f}")
        
        with col4:
            disponible_total = clientes['disponible'].sum()
            st.metric("Disponible Total", f"${disponible_total:,.0f}")
        
        # Distribución por estado
        st.divider()
        st.subheader("📈 Distribución por Estado")
        
        col_est1, col_est2, col_est3 = st.columns(3)
        
        with col_est1:
            normales = len(clientes[clientes['estado'] == 'NORMAL'])
            st.metric("🟢 NORMAL", normales)
        
        with col_est2:
            alertas = len(clientes[clientes['estado'] == 'ALERTA'])
            st.metric("🟡 ALERTA", alertas)
        
        with col_est3:
            sobrepasados = len(clientes[clientes['estado'] == 'SOBREPASADO'])
            st.metric("🔴 SOBREPASADO", sobrepasados)
        
        # Gráfico de uso por cliente
        st.divider()
        st.subheader("📊 Uso de Cupo por Cliente")
        
        # Crear gráfico simple con barras
        df_grafico = clientes.copy()
        df_grafico = df_grafico[['nombre', 'porcentaje_uso']].sort_values('porcentaje_uso', ascending=False)
        df_grafico.columns = ['Cliente', '% Uso']
        
        # Mostrar como tabla con barras
        for _, row in df_grafico.iterrows():
            cliente_nombre = row['Cliente'][:30] + "..." if len(row['Cliente']) > 30 else row['Cliente']
            porcentaje = min(row['% Uso'], 100)
            
            # Determinar color
            if porcentaje > 100:
                color = "red"
            elif porcentaje > 80:
                color = "orange"
            else:
                color = "green"
            
            # Mostrar barra
            st.write(f"**{cliente_nombre}**")
            st.progress(porcentaje / 100)
            st.caption(f"{porcentaje:.1f}%")
            st.write("---")
        
        # Top 5 clientes con mayor uso
        st.divider()
        st.subheader("🏆 Top 5 - Mayor % de Uso")
        
        top5 = df_grafico.head(5)
        for i, (_, row) in enumerate(top5.iterrows(), 1):
            with st.container():
                col_rank, col_data = st.columns([1, 4])
                with col_rank:
                    st.subheader(f"#{i}")
                with col_data:
                    st.write(f"**{row['Cliente']}**")
                    st.progress(min(row['% Uso'], 100) / 100)
                    st.caption(f"{row['% Uso']:.1f}%")
        
        # Clientes críticos (sobrepasados)
        st.divider()
        st.subheader("⚠️ Clientes Críticos (Sobrepasados)")
        
        criticos = clientes[clientes['estado'] == 'SOBREPASADO']
        if not criticos.empty:
            for _, critico in criticos.iterrows():
                excedido = abs(critico['disponible'])
                with st.container():
                    st.error(f"**{critico['nombre']}**")
                    st.write(f"NIT: {critico['nit']}")
                    st.write(f"Cupo: ${critico['cupo_sugerido']:,.0f}")
                    st.write(f"Saldo: ${critico['saldo_actual']:,.0f}")
                    st.write(f"📉 **Excedido por:** ${excedido:,.0f}")
                    st.write("---")
        else:
            st.success("✅ No hay clientes sobrepasados")
        
    except Exception as e:
        st.error(f"❌ Error al generar resumen: {str(e)}")

# Solo para pruebas locales
if __name__ == "__main__":
    st.set_page_config(page_title="Gestión de Clientes", layout="wide")
    show()
