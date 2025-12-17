"""
Página de gestión de clientes
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

def show():
    st.title("👥 Gestión de Clientes")
    
    # Inicializar base de datos si no existe
    init_database()
    
    # Pestañas
    tab1, tab2, tab3 = st.tabs(["📋 Clientes", "➕ Nuevo", "📊 Resumen"])
    
    with tab1:
        mostrar_clientes()
    
    with tab2:
        agregar_cliente()
    
    with tab3:
        mostrar_resumen()

def init_database():
    """Inicializa la base de datos con clientes predeterminados"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # Crear tabla de clientes si no existe
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        nit TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        cupo_total REAL DEFAULT 0,
        saldo_actual REAL DEFAULT 0,
        disponible REAL GENERATED ALWAYS AS (cupo_total - saldo_actual) VIRTUAL,
        activo INTEGER DEFAULT 1,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Insertar clientes predeterminados si no existen
    clientes_predeterminados = [
        ('901212102', 'AUNA COLOMBIA S.A.S.', 21693849830, 19493849830),
        ('890905166', 'EMPRESA SOCIAL DEL ESTADO HOSPITAL MENTAL DE ANTIOQ', 7500000000, 7397192942),
        ('900249425', 'PHARMASAN S.A.S', 5910785209, 5710785209),
        ('900746052', 'NEURUM SAS', 5500000000, 5184247632),
        ('800241602', 'FUNDACION COLOMBIANA DE CANCEROLOGIA CLINICA VIDA', 3500000000, 3031469552),
        ('890985122', 'COOPERATIVA DE HOSPITALES DE ANTIOQUIA', 1500000000, 1291931405),
        ('811038014', 'GRUPO ONCOLOGICO INTERNACIONAL S.A.', 900000000, 806853666)
    ]
    
    for nit, nombre, cupo_total, saldo_actual in clientes_predeterminados:
        cursor.execute('''
        INSERT OR IGNORE INTO clientes (nit, nombre, cupo_total, saldo_actual, activo)
        VALUES (?, ?, ?, ?, 1)
        ''', (nit, nombre, cupo_total, saldo_actual))
    
    conn.commit()
    conn.close()

def get_clientes():
    """Obtiene todos los clientes activos"""
    conn = sqlite3.connect('data/database.db')
    query = '''
    SELECT 
        nit,
        nombre,
        cupo_total,
        saldo_actual,
        (cupo_total - saldo_actual) as disponible,
        CASE 
            WHEN saldo_actual > cupo_total THEN 'SOBREPASADO'
            WHEN (saldo_actual * 100.0 / cupo_total) > 80 THEN 'ALERTA'
            ELSE 'NORMAL'
        END as estado,
        (saldo_actual * 100.0 / cupo_total) as porcentaje_uso
    FROM clientes 
    WHERE activo = 1
    ORDER BY nombre
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def actualizar_cliente(nit, nombre=None, cupo_total=None, saldo_actual=None):
    """Actualiza los datos de un cliente"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if nombre:
        updates.append("nombre = ?")
        params.append(nombre)
    if cupo_total is not None:
        updates.append("cupo_total = ?")
        params.append(cupo_total)
    if saldo_actual is not None:
        updates.append("saldo_actual = ?")
        params.append(saldo_actual)
    
    if updates:
        updates.append("fecha_actualizacion = ?")
        params.append(datetime.now())
        params.append(nit)
        
        query = f"UPDATE clientes SET {', '.join(updates)} WHERE nit = ?"
        cursor.execute(query, params)
    
    conn.commit()
    conn.close()
    return True

def crear_cliente(nit, nombre, cupo_total, saldo_actual=0):
    """Crea un nuevo cliente"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO clientes (nit, nombre, cupo_total, saldo_actual, activo)
        VALUES (?, ?, ?, ?, 1)
        ''', (nit, nombre, cupo_total, saldo_actual))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        raise Exception(f"Ya existe un cliente con NIT: {nit}")
    finally:
        conn.close()

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
            st.metric("Cupo Total", f"${clientes['cupo_total'].sum():,.0f}")
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
                            "Cupo Total",
                            value=float(cliente['cupo_total']),
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
                                    cupo_total=nuevo_cupo,
                                    saldo_actual=nuevo_saldo
                                )
                                st.success("✅ Cambios guardados")
                                st.rerun()
                        
                        with col_btn2:
                            if st.form_submit_button("📝 Ver Detalles", use_container_width=True):
                                st.session_state[f"detalle_{cliente['nit']}"] = True
                                st.rerun()
                
                with col_b:
                    # Información actual
                    st.info("**Estado Actual:**")
                    
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        st.metric("Cupo", f"${cliente['cupo_total']:,.0f}")
                        st.metric("Disponible", f"${cliente['disponible']:,.0f}")
                    with col_m2:
                        st.metric("Saldo", f"${cliente['saldo_actual']:,.0f}")
                        st.metric("% Uso", f"{cliente['porcentaje_uso']:.1f}%")
                    
                    # Estado con color
                    estado_color = {
                        'NORMAL': '🟢',
                        'ALERTA': '🟡',
                        'SOBREPASADO': '🔴'
                    }
                    st.write(f"**Estado:** {estado_color.get(cliente['estado'], '⚪')} {cliente['estado']}")
                    
                    # Barra de progreso
                    st.progress(min(cliente['porcentaje_uso'] / 100, 1))
        
        # Mostrar también en tabla
        st.divider()
        st.subheader("📋 Vista en Tabla")
        
        df_tabla = clientes.copy()
        df_tabla = df_tabla[['nombre', 'nit', 'cupo_total', 'saldo_actual', 'disponible', 'porcentaje_uso', 'estado']]
        df_tabla.columns = ['Cliente', 'NIT', 'Cupo Total', 'Saldo Actual', 'Disponible', '% Uso', 'Estado']
        
        # Formatear valores
        for col in ['Cupo Total', 'Saldo Actual', 'Disponible']:
            df_tabla[col] = df_tabla[col].apply(lambda x: f"${x:,.0f}")
        df_tabla['% Uso'] = df_tabla['% Uso'].apply(lambda x: f"{x:.1f}%")
        
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
            cupo_total = st.number_input(
                "Cupo Total *",
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
        disponible = cupo_total - saldo_actual
        porcentaje_uso = (saldo_actual / cupo_total * 100) if cupo_total > 0 else 0
        
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
                crear_cliente(nit, nombre, cupo_total, saldo_actual)
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
            st.metric("Cupo Total", f"${clientes['cupo_total'].sum():,.0f}")
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
                    st.progress(min(cliente['porcentaje_uso'] / 100, 1))
                    st.caption(f"{cliente['porcentaje_uso']:.1f}%")
        
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
