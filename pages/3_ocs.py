"""
Página de gestión de Órdenes de Compra (OCs) para Streamlit
Versión completa con todas las funciones
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from modules.database import (
    get_clientes, 
    get_ocs_pendientes, 
    get_todas_ocs,
    crear_oc,
    autorizar_oc,
    get_estadisticas_generales
)

# ==================== FUNCIONES AUXILIARES ====================

def mostrar_modal_agregar_oc():
    """Modal para agregar nueva OC"""
    with st.form("form_nueva_oc"):
        st.subheader("➕ Agregar Nueva Orden de Compra")
        
        # Obtener clientes para dropdown
        clientes = get_clientes()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Seleccionar cliente
            cliente_nombre = st.selectbox(
                "Cliente *",
                clientes['nombre'].tolist(),
                help="Seleccione el cliente"
            )
            
            # Obtener NIT del cliente seleccionado
            cliente_nit = clientes[clientes['nombre'] == cliente_nombre]['nit'].iloc[0]
            
            # Número de OC
            numero_oc = st.text_input(
                "Número de OC *",
                max_length=50,
                help="Ej: OC-2024-001, FACT-12345"
            )
        
        with col2:
            # Valor total
            valor_total = st.number_input(
                "Valor Total *",
                min_value=0.0,
                value=0.0,
                step=100000.0,
                format="%.0f",
                help="Valor total de la orden"
            )
            
            # Tipo de OC
            tipo_oc = st.selectbox(
                "Tipo de OC",
                ["SUELTA", "CUPO_NUEVO"],
                help="SUELTA: OC individual, CUPO_NUEVO: para cupo nuevo"
            )
        
        # Cupo de referencia (solo para tipo CUPO_NUEVO)
        cupo_referencia = ""
        if tipo_oc == "CUPO_NUEVO":
            cupo_referencia = st.text_input(
                "Cupo de Referencia",
                max_length=100,
                help="Número de cupo al que está asociada esta OC"
            )
        
        # Comentarios
        comentarios = st.text_area(
            "Comentarios (opcional)",
            height=100,
            help="Información adicional sobre esta OC"
        )
        
        # Botones de acción
        col_submit, col_cancel = st.columns(2)
        
        with col_submit:
            submitted = st.form_submit_button(
                "💾 Crear OC",
                type="primary",
                use_container_width=True
            )
        
        with col_cancel:
            cancel = st.form_submit_button(
                "❌ Cancelar",
                use_container_width=True
            )
        
        if submitted:
            # Validaciones
            if not numero_oc.strip():
                st.error("❌ El número de OC es obligatorio")
                return False
            
            if valor_total <= 0:
                st.error("❌ El valor total debe ser mayor a 0")
                return False
            
            try:
                # Crear la OC
                crear_oc(
                    cliente_nit=cliente_nit,
                    numero_oc=numero_oc.strip(),
                    valor_total=valor_total,
                    tipo=tipo_oc,
                    cupo_referencia=cupo_referencia.strip(),
                    comentarios=comentarios.strip()
                )
                
                st.success(f"✅ OC '{numero_oc}' creada exitosamente")
                st.rerun()
                return True
                
            except Exception as e:
                st.error(f"❌ Error al crear OC: {str(e)}")
                return False
        
        if cancel:
            st.rerun()
    
    return False

def mostrar_modal_autorizar(oc):
    """Modal para autorización de OC"""
    with st.form(f"auth_form_{oc['id']}"):
        st.subheader(f"✅ Autorizar OC: {oc['numero_oc']}")
        
        # Información de la OC
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.metric("Valor Total", f"${oc['valor_total']:,.0f}")
        with col_info2:
            if oc['estado'] == 'PARCIAL':
                st.metric("Ya Autorizado", f"${oc['valor_autorizado']:,.0f}")
        
        # Calcular valor restante
        valor_restante = oc['valor_total'] - oc['valor_autorizado']
        st.info(f"**Valor disponible para autorizar:** ${valor_restante:,.0f}")
        
        # Botones de porcentaje rápido
        st.write("**Autorización rápida (%):**")
        col_perc1, col_perc2, col_perc3, col_perc4 = st.columns(4)
        
        porcentaje_key = f"porcentaje_{oc['id']}"
        
        with col_perc1:
            if st.button("25%", key=f"25_{oc['id']}", use_container_width=True):
                st.session_state[porcentaje_key] = 25
        with col_perc2:
            if st.button("50%", key=f"50_{oc['id']}", use_container_width=True):
                st.session_state[porcentaje_key] = 50
        with col_perc3:
            if st.button("75%", key=f"75_{oc['id']}", use_container_width=True):
                st.session_state[porcentaje_key] = 75
        with col_perc4:
            if st.button("100%", key=f"100_{oc['id']}", use_container_width=True):
                st.session_state[porcentaje_key] = 100
        
        # Calcular valor sugerido
        valor_sugerido = valor_restante
        if porcentaje_key in st.session_state:
            valor_sugerido = valor_restante * (st.session_state[porcentaje_key] / 100)
        
        # Campo para valor de autorización
        valor_autorizar = st.number_input(
            "Valor a autorizar *",
            min_value=0.0,
            max_value=float(valor_restante),
            value=float(valor_sugerido),
            step=100000.0,
            format="%.0f"
        )
        
        # Comentario
        comentario = st.text_area(
            "Comentario (opcional)",
            placeholder="Ej: Autorización parcial por aprobación de gerencia",
            height=100
        )
        
        # Botones de acción
        col_a, col_b = st.columns(2)
        
        with col_a:
            confirmar = st.form_submit_button(
                "✅ Confirmar Autorización",
                type="primary",
                use_container_width=True
            )
        
        with col_b:
            cancelar = st.form_submit_button(
                "❌ Cancelar",
                use_container_width=True
            )
        
        if confirmar:
            if valor_autorizar <= 0:
                st.error("❌ El valor a autorizar debe ser mayor a 0")
                return False
            
            try:
                # Llamar a la función de autorización
                autorizar_oc(
                    oc_id=oc['id'],
                    valor_autorizado=valor_autorizar,
                    comentario=comentario.strip(),
                    usuario="Sistema"  # Podrías cambiar esto por usuario logueado
                )
                
                st.success(f"✅ Autorizado ${valor_autorizar:,.0f} de la OC {oc['numero_oc']}")
                st.rerun()
                return True
                
            except Exception as e:
                st.error(f"❌ Error al autorizar: {str(e)}")
                return False
        
        if cancelar:
            st.rerun()
    
    return False

def mostrar_detalle_oc(oc):
    """Muestra el detalle completo de una OC"""
    with st.expander(f"📋 Detalle completo - {oc['numero_oc']}", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Información General:**")
            st.write(f"**Número OC:** {oc['numero_oc']}")
            st.write(f"**Cliente:** {oc['cliente_nombre']}")
            st.write(f"**Tipo:** {oc['tipo']}")
            
            if oc['cupo_referencia']:
                st.write(f"**Cupo Referencia:** {oc['cupo_referencia']}")
            
            st.write(f"**Fecha Registro:** {oc['fecha_registro']}")
            
            if oc['fecha_ultima_autorizacion']:
                st.write(f"**Última Autorización:** {oc['fecha_ultima_autorizacion']}")
        
        with col2:
            st.write("**Valores:**")
            st.write(f"**Valor Total:** ${oc['valor_total']:,.0f}")
            st.write(f"**Valor Autorizado:** ${oc['valor_autorizado']:,.0f}")
            st.write(f"**Valor Pendiente:** ${oc['valor_pendiente']:,.0f}")
            
            # Barra de progreso
            if oc['valor_total'] > 0:
                progreso = (oc['valor_autorizado'] / oc['valor_total']) * 100
                st.progress(progreso / 100)
                st.write(f"**Progreso:** {progreso:.1f}%")
        
        # Comentarios
        if oc['comentarios']:
            st.write("**Comentarios:**")
            st.info(oc['comentarios'])
        
        st.divider()
        
        # Historial de autorizaciones (si existe)
        try:
            conn = sqlite3.connect('data/database.db')
            autorizaciones = pd.read_sql_query(
                "SELECT * FROM autorizaciones_parciales WHERE oc_id = ? ORDER BY fecha_autorizacion DESC",
                conn,
                params=(oc['id'],)
            )
            conn.close()
            
            if not autorizaciones.empty:
                st.write("**Historial de Autorizaciones:**")
                for _, auth in autorizaciones.iterrows():
                    col_a1, col_a2, col_a3 = st.columns([2, 2, 1])
                    with col_a1:
                        st.write(f"${auth['valor_autorizado']:,.0f}")
                    with col_a2:
                        st.write(f"{auth['fecha_autorizacion']}")
                    with col_a3:
                        if auth['comentario']:
                            st.info("📝")
            else:
                st.write("No hay historial de autorizaciones.")
                
        except Exception as e:
            st.write(f"No se pudo cargar el historial: {e}")

def mostrar_oc_tarjeta(oc):
    """Muestra una OC como tarjeta interactiva"""
    with st.container():
        # Determinar color según estado
        estado_colores = {
            'PENDIENTE': '🟡',
            'PARCIAL': '🟠', 
            'AUTORIZADA': '🟢'
        }
        color_icono = estado_colores.get(oc['estado'], '⚫')
        
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            # Número de OC y cliente
            st.subheader(f"📄 {oc['numero_oc']}")
            st.caption(f"**Cliente:** {oc['cliente_nombre']}")
            
            # Mostrar progreso si está parcial
            if oc['estado'] == 'PARCIAL':
                if oc['valor_total'] > 0:
                    progreso = (oc['valor_autorizado'] / oc['valor_total']) * 100
                    st.progress(progreso / 100)
                    st.caption(f"Autorizado: ${oc['valor_autorizado']:,.0f} de ${oc['valor_total']:,.0f} ({progreso:.1f}%)")
            else:
                st.write(f"**Valor:** ${oc['valor_total']:,.0f}")
            
            # Tipo y referencia
            st.caption(f"**Tipo:** {oc['tipo']}")
            if oc['cupo_referencia']:
                st.caption(f"**Ref:** {oc['cupo_referencia']}")
        
        with col2:
            # Estado
            st.metric("Estado", f"{color_icono} {oc['estado']}")
            
            # Fecha
            if 'fecha_registro' in oc:
                fecha = pd.to_datetime(oc['fecha_registro']).strftime('%d/%m/%Y')
                st.caption(f"Registro: {fecha}")
            
            # Valor pendiente
            if 'valor_pendiente' in oc and oc['estado'] != 'AUTORIZADA':
                st.caption(f"Pendiente: ${oc['valor_pendiente']:,.0f}")
        
        with col3:
            # Botones de acción según estado
            if oc['estado'] in ['PENDIENTE', 'PARCIAL']:
                if st.button("✅ Autorizar", 
                           key=f"auth_btn_{oc['id']}", 
                           use_container_width=True,
                           help="Autorizar total o parcialmente"):
                    st.session_state[f'autorizar_oc_{oc["id"]}'] = True
                    st.rerun()
            else:
                if st.button("📋 Detalle", 
                           key=f"det_btn_{oc['id']}", 
                           use_container_width=True,
                           help="Ver detalles completos"):
                    st.session_state[f'detalle_oc_{oc["id"]}'] = True
                    st.rerun()
        
        # Mostrar modal de autorización si está activo
        if f'autorizar_oc_{oc["id"]}' in st.session_state:
            mostrar_modal_autorizar(oc)
        
        # Mostrar detalle si está activo
        if f'detalle_oc_{oc["id"]}' in st.session_state:
            mostrar_detalle_oc(oc)
        
        st.divider()

# ==================== FUNCIÓN PRINCIPAL ====================

def show():
    """Función principal de la página de OCs"""
    st.header("📋 Gestión de Órdenes de Compra (OCs)")
    
    # Estadísticas rápidas
    try:
        stats = get_estadisticas_generales()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total OCs Pendientes", f"${stats['total_ocs_pendientes']:,.0f}")
        with col2:
            st.metric("Clientes Activos", stats['total_clientes'])
        with col3:
            st.metric("Cupo Total", f"${stats['total_cupo_sugerido']:,.0f}")
        with col4:
            st.metric("Saldo Total", f"${stats['total_saldo_actual']:,.0f}")
    except:
        pass
    
    # Botón para agregar nueva OC
    if st.button("➕ Agregar Nueva OC", 
                key="btn_nueva_oc",
                use_container_width=True,
                type="primary"):
        st.session_state['mostrar_modal_nueva_oc'] = True
    
    # Mostrar modal de nueva OC si está activo
    if 'mostrar_modal_nueva_oc' in st.session_state:
        mostrar_modal_agregar_oc()
    
    st.divider()
    
    # Obtener clientes para filtros
    try:
        clientes = get_clientes()
        cliente_lista = ["Todos"] + clientes['nombre'].tolist()
        
        # Filtros
        st.subheader("🔍 Filtros de Búsqueda")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_cliente = st.selectbox(
                "Filtrar por Cliente",
                cliente_lista,
                key="filtro_cliente"
            )
        with col2:
            filtro_estado = st.selectbox(
                "Filtrar por Estado", 
                ["Todos", "PENDIENTE", "PARCIAL", "AUTORIZADA"],
                key="filtro_estado"
            )
        with col3:
            filtro_tipo = st.selectbox(
                "Filtrar por Tipo", 
                ["Todos", "CUPO_NUEVO", "SUELTA"],
                key="filtro_tipo"
            )
        
        # Obtener todas las OCs
        with st.spinner("Cargando Órdenes de Compra..."):
            ocs = get_todas_ocs()  # Cambié a get_todas_ocs para ver todas
            
        # Aplicar filtros
        if filtro_cliente != "Todos":
            cliente_nit = clientes[clientes['nombre'] == filtro_cliente]['nit'].iloc[0]
            ocs = ocs[ocs['cliente_nit'] == cliente_nit]
        
        if filtro_estado != "Todos":
            ocs = ocs[ocs['estado'] == filtro_estado]
        
        if filtro_tipo != "Todos":
            ocs = ocs[ocs['tipo'] == filtro_tipo]
        
        # Mostrar resultados
        st.subheader(f"📊 Resultados: {len(ocs)} OCs encontradas")
        
        if not ocs.empty:
            # Opción de vista: tarjetas o tabla
            vista = st.radio(
                "Tipo de vista:",
                ["Tarjetas", "Tabla"],
                horizontal=True,
                key="vista_ocs"
            )
            
            if vista == "Tarjetas":
                # Mostrar como tarjetas
                for _, oc in ocs.iterrows():
                    mostrar_oc_tarjeta(oc)
            else:
                # Mostrar como tabla
                columnas_mostrar = [
                    'numero_oc', 'cliente_nombre', 'valor_total', 
                    'valor_autorizado', 'valor_pendiente', 'estado', 'tipo'
                ]
                
                df_tabla = ocs[columnas_mostrar].copy()
                df_tabla = df_tabla.rename(columns={
                    'numero_oc': 'Número OC',
                    'cliente_nombre': 'Cliente',
                    'valor_total': 'Valor Total',
                    'valor_autorizado': 'Autorizado',
                    'valor_pendiente': 'Pendiente',
                    'estado': 'Estado',
                    'tipo': 'Tipo'
                })
                
                st.dataframe(
                    df_tabla,
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("📭 No hay OCs que coincidan con los filtros seleccionados")
            
    except Exception as e:
        st.error(f"❌ Error al cargar OCs: {str(e)}")
        st.code(f"Detalle: {e}")

# ==================== EJECUCIÓN PARA PRUEBAS ====================

if __name__ == "__main__":
    # Para pruebas directas
    st.set_page_config(page_title="Gestión de OCs", layout="wide")
    show()
