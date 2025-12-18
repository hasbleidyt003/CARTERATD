"""
Página de Gestión de Clientes
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
from pathlib import Path

# Configuración de página
st.set_page_config(
    page_title="Clientes - Cupos TD",
    page_icon="👥",
    layout="wide"
)

# Importar funciones compartidas
sys.path.append(str(Path(__file__).parent.parent))
from app import modern_navbar, Config, get_clientes, actualizar_cliente, formato_monetario, formato_porcentaje

# Mostrar navbar
modern_navbar()

# Título
st.title("👥 Gestión de Clientes")
st.markdown("---")

# Verificar base de datos
config = Config()
if not os.path.exists(config.DATABASE_PATH):
    st.error("❌ La base de datos no está inicializada. Ve al Dashboard primero.")
    st.stop()

# Pestañas
tab1, tab2 = st.tabs(["📋 Lista de Clientes", "➕ Nuevo Cliente"])

with tab1:
    # Filtros
    col_filt1, col_filt2 = st.columns(2)
    
    with col_filt1:
        filtro_nombre = st.text_input("🔍 Buscar por nombre")
    
    with col_filt2:
        filtro_estado = st.selectbox(
            "Filtrar por estado",
            ["TODOS", "NORMAL", "MEDIO", "ALTO", "SOBREPASADO"]
        )
    
    # Obtener clientes
    clientes = get_clientes()
    
    if not clientes.empty:
        # Aplicar filtros
        if filtro_nombre:
            clientes = clientes[clientes['nombre'].str.contains(filtro_nombre, case=False, na=False)]
        
        if filtro_estado != "TODOS":
            clientes = clientes[clientes['estado_cupo'] == filtro_estado]
        
        # Mostrar métricas
        col_met1, col_met2, col_met3 = st.columns(3)
        
        with col_met1:
            st.metric("Total Clientes", len(clientes))
        
        with col_met2:
            st.metric("Cupo Total", formato_monetario(clientes['cupo_sugerido'].sum()))
        
        with col_met3:
            st.metric("Cartera Total", formato_monetario(clientes['total_cartera'].sum()))
        
        st.divider()
        
        # Formulario de edición para cada cliente
        for _, cliente in clientes.iterrows():
            with st.expander(f"{cliente['nombre']} (NIT: {cliente['nit']})", expanded=False):
                col_edit1, col_edit2 = st.columns(2)
                
                with col_edit1:
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
                
                with col_edit2:
                    nueva_cartera = st.number_input(
                        "Total Cartera",
                        value=float(cliente['total_cartera']),
                        min_value=0.0,
                        step=1000000.0,
                        format="%.0f",
                        key=f"cartera_{cliente['nit']}"
                    )
                    
                    # Calcular en tiempo real
                    nuevo_disponible = nuevo_cupo - nueva_cartera
                    nuevo_porcentaje = (nueva_cartera / nuevo_cupo * 100) if nuevo_cupo > 0 else 0
                
                # Mostrar cálculos
                col_calc1, col_calc2 = st.columns(2)
                with col_calc1:
                    st.metric("Nuevo Disponible", formato_monetario(nuevo_disponible))
                with col_calc2:
                    st.metric("% Uso", formato_porcentaje(nuevo_porcentaje))
                
                # Botón de guardar
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("💾 Guardar Cambios", key=f"guardar_{cliente['nit']}", use_container_width=True):
                        try:
                            actualizar_cliente(
                                nit=cliente['nit'],
                                data={
                                    'nombre': nuevo_nombre,
                                    'cupo_sugerido': nuevo_cupo,
                                    'total_cartera': nueva_cartera
                                }
                            )
                            st.success("✅ Cambios guardados exitosamente")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                
                with col_btn2:
                    if st.button("📋 Ver OCs del Cliente", key=f"ocs_{cliente['nit']}", use_container_width=True):
                        st.session_state.cliente_seleccionado = cliente['nit']
                        st.switch_page("pages/3_ocs.py")
    else:
        st.info("📭 No hay clientes que coincidan con los filtros")

with tab2:
    st.subheader("➕ Agregar Nuevo Cliente")
    
    with st.form("nuevo_cliente"):
        col1, col2 = st.columns(2)
        
        with col1:
            nit = st.text_input("NIT *")
            nombre = st.text_input("Nombre del Cliente *")
        
        with col2:
            cupo = st.number_input(
                "Cupo Sugerido *",
                min_value=0.0,
                value=10000000.0,
                step=1000000.0,
                format="%.0f"
            )
            cartera = st.number_input(
                "Total Cartera",
                min_value=0.0,
                value=0.0,
                step=1000000.0,
                format="%.0f"
            )
        
        # Cálculos en tiempo real
        disponible = cupo - cartera
        porcentaje_uso = (cartera / cupo * 100) if cupo > 0 else 0
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.metric("Disponible Inicial", formato_monetario(disponible))
        with col_info2:
            st.metric("% Uso Inicial", formato_porcentaje(porcentaje_uso))
        
        # Botón de envío
        submitted = st.form_submit_button(
            "🚀 Crear Cliente",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not nit or not nombre:
                st.error("❌ Los campos marcados con * son obligatorios")
            elif cupo <= 0:
                st.error("❌ El cupo sugerido debe ser mayor a 0")
            else:
                try:
                    conn = sqlite3.connect(config.DATABASE_PATH)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                    INSERT INTO clientes (nit, nombre, cupo_sugerido, total_cartera, disponible)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (nit, nombre, cupo, cartera, disponible))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success(f"✅ Cliente '{nombre}' creado exitosamente")
                    st.balloons()
                    st.rerun()
                    
                except sqlite3.IntegrityError:
                    st.error(f"❌ Ya existe un cliente con NIT: {nit}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
