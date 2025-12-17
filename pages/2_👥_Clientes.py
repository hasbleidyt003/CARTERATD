import streamlit as st
import pandas as pd
from modules.database import get_clientes

def show():
    st.header("👥 Gestión de Clientes")
    
    # Pestañas para diferentes funciones
    tab1, tab2 = st.tabs(["📋 Lista de Clientes", "➕ Nuevo Cliente"])
    
    with tab1:
        mostrar_clientes()
    
    with tab2:
        agregar_cliente()

def mostrar_clientes():
    clientes = get_clientes()
    
    if not clientes.empty:
        # Formulario de edición en línea
        for _, cliente in clientes.iterrows():
            with st.expander(f"{cliente['nombre']} (NIT: {cliente['nit']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nuevo_cupo = st.number_input(
                        "Cupo Sugerido",
                        value=float(cliente['cupo_sugerido']),
                        key=f"cupo_{cliente['nit']}"
                    )
                
                with col2:
                    nuevo_saldo = st.number_input(
                        "Saldo Actual",
                        value=float(cliente['saldo_actual']),
                        key=f"saldo_{cliente['nit']}"
                    )
                
                if st.button("💾 Guardar Cambios", key=f"guardar_{cliente['nit']}"):
                    # Aquí iría el código para actualizar en BD
                    st.success("✅ Datos actualizados")
    else:
        st.info("No hay clientes registrados")

def agregar_cliente():
    with st.form("nuevo_cliente"):
        col1, col2 = st.columns(2)
        
        with col1:
            nit = st.text_input("NIT *")
            nombre = st.text_input("Nombre del Cliente *")
        
        with col2:
            cupo_sugerido = st.number_input("Cupo Sugerido Inicial *", 
                                          min_value=0.0, 
                                          value=0.0)
            saldo_actual = st.number_input("Saldo Actual Inicial *",
                                         min_value=0.0,
                                         value=0.0)
        
        if st.form_submit_button("💾 Crear Cliente", use_container_width=True):
            if nit and nombre:
                # Aquí iría el código para guardar en BD
                st.success(f"✅ Cliente '{nombre}' creado exitosamente")
                st.rerun()
            else:
                st.error("❌ Complete los campos obligatorios (*)")
