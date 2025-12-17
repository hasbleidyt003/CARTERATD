"""
Página de gestión de Órdenes de Compra (OCs) para Streamlit
Versión MEJORADA con edición y eliminación de OCs
"""

import streamlit as st
import pandas as pd
from modules.database import (
    get_clientes, 
    get_ocs_pendientes, 
    get_todas_ocs,
    crear_oc,
    editar_oc,
    eliminar_oc,
    autorizar_oc,
    get_estadisticas_generales,
    get_autorizaciones_oc,
    get_oc_por_id
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
            if not clientes.empty:
                cliente_nombre = st.selectbox(
                    "Cliente *",
                    clientes['nombre'].tolist(),
                    help="Seleccione el cliente"
                )
                
                # Obtener NIT del cliente seleccionado
                cliente_nit = clientes[clientes['nombre'] == cliente_nombre]['nit'].iloc[0]
            else:
                st.warning("No hay clientes disponibles")
                cliente_nit = None
            
            # Número de OC
            numero_oc = st.text_input(
                "Número de OC *",
                help="Ej: OC-2024-001, FACT-12345",
                placeholder="OC-2024-001"
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
                help="Número de cupo al que está asociada esta OC",
                placeholder="CUPO-001"
            )
        
        # Comentarios
        comentarios = st.text_area(
            "Comentarios (opcional)",
            height=100,
            help="Información adicional sobre esta OC",
            placeholder="Descripción o notas adicionales..."
        )
        
        # Botón de envío
        col_submit, col_cancel = st.columns(2)
        
        submitted = False
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
            
            if not cliente_nit:
                st.error("❌ Debe seleccionar un cliente")
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

def mostrar_modal_editar_oc(oc):
    """Modal para editar una OC existente"""
    with st.form(f"edit_form_{oc['id']}"):
        st.subheader(f"✏️ Editar OC: {oc['numero_oc']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Número de OC (puede cambiar)
            nuevo_numero_oc = st.text_input(
                "Número de OC *",
                value=oc['numero_oc'],
                help="Nuevo número de OC"
            )
            
            # Valor total
            nuevo_valor_total = st.number_input(
                "Valor Total *",
                min_value=0.0,
                value=float(oc['valor_total']),
                step=100000.0,
                format="%.0f",
                help="Nuevo valor total"
            )
        
        with col2:
            # Tipo de OC
            nuevo_tipo = st.selectbox(
                "Tipo de OC",
                ["SUELTA", "CUPO_NUEVO"],
                index=0 if oc['tipo'] == 'SUELTA' else 1,
                help="Tipo de orden"
            )
            
            # Cupo de referencia
            nuevo_cupo_ref = st.text_input(
                "Cupo de Referencia",
                value=oc['cupo_referencia'] if oc['cupo_referencia'] else "",
                help="Referencia del cupo (solo para tipo CUPO_NUEVO)",
                placeholder="CUPO-001",
                disabled=(nuevo_tipo != 'CUPO_NUEVO')
            )
        
        # Comentarios
        nuevos_comentarios = st.text_area(
            "Comentarios",
            value=oc['comentarios'] if oc['comentarios'] else "",
            height=100,
            placeholder="Actualice los comentarios..."
        )
        
        # Botones de acción
        col_save, col_cancel = st.columns(2)
        
        guardado = False
        with col_save:
            guardado = st.form_submit_button(
                "💾 Guardar Cambios",
                type="primary",
                use_container_width=True
            )
        
        with col_cancel:
            cancelado = st.form_submit_button(
                "❌ Cancelar",
                use_container_width=True
            )
        
        if guardado:
            # Validaciones
            if not nuevo_numero_oc.strip():
                st.error("❌ El número de OC es obligatorio")
                return False
            
            if nuevo_valor_total <= 0:
                st.error("❌ El valor total debe ser mayor a 0")
                return False
            
            try:
                # Actualizar la OC
                editar_oc(
                    oc_id=oc['id'],
                    numero_oc=nuevo_numero_oc.strip(),
                    valor_total=nuevo_valor_total,
                    tipo=nuevo_tipo,
                    cupo_referencia=nuevo_cupo_ref.strip(),
                    comentarios=nuevos_comentarios.strip()
                )
                
                st.success(f"✅ OC '{nuevo_numero_oc}' actualizada exitosamente")
                st.rerun()
                return True
                
            except Exception as e:
                st.error(f"❌ Error al editar OC: {str(e)}")
                return False
        
        if cancelado:
            st.rerun()
    
    return False

def mostrar_modal_eliminar_oc(oc):
    """Modal para confirmar eliminación de OC"""
    with st.form(f"delete_form_{oc['id']}"):
        st.subheader(f"🗑️ Eliminar OC: {oc['numero_oc']}")
        
        st.warning(f"⚠️ **¡ADVERTENCIA!** Estás a punto de eliminar la OC:")
        st.info(f"**Cliente:** {oc['cliente_nombre']}")
        st.info(f"**Número OC:** {oc['numero_oc']}")
        st.info(f"**Valor:** ${oc['valor_total']:,.0f}")
        st.info(f"**Estado:** {oc['estado']}")
        
        st.error("**Esta acción NO se puede deshacer.**")
        
        # Confirmación
        confirmacion = st.text_input(
            "Escribe 'ELIMINAR' para confirmar:",
            placeholder="ELIMINAR",
            help="Debes escribir exactamente 'ELIMINAR' para proceder"
        )
        
        # Botones
        col_del, col_can = st.columns(2)
        
        eliminado = False
        with col_del:
            eliminado = st.form_submit_button(
                "🔥 Confirmar Eliminación",
                type="secondary",
                use_container_width=True,
                disabled=(confirmacion != "ELIMINAR")
            )
        
        with col_can:
            cancelado = st.form_submit_button(
                "❌ Cancelar",
                use_container_width=True
            )
        
        if eliminado and confirmacion == "ELIMINAR":
            try:
                eliminar_oc(oc['id'])
                st.success(f"✅ OC '{oc['numero_oc']}' eliminada exitosamente")
                st.rerun()
                return True
            except Exception as e:
                st.error(f"❌ Error al eliminar OC: {str(e)}")
                return False
        
        if cancelado:
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
            if st.form_submit_button("25%", use_container_width=True):
                st.session_state[porcentaje_key] = 25
                st.rerun()
        with col_perc2:
            if st.form_submit_button("50%", use_container_width=True):
                st.session_state[porcentaje_key] = 50
                st.rerun()
        with col_perc3:
            if st.form_submit_button("75%", use_container_width=True):
                st.session_state[porcentaje_key] = 75
                st.rerun()
        with col_perc4:
            if st.form_submit_button("100%", use_container_width=True):
                st.session_state[porcentaje_key] = 100
                st.rerun()
        
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
        
        confirmado = False
        with col_a:
            confirmado = st.form_submit_button(
                "✅ Confirmar Autorización",
                type="primary",
                use_container_width=True
            )
        
        with col_b:
            cancelado = st.form_submit_button(
                "❌ Cancelar",
                use_container_width=True
            )
        
        if confirmado:
            if valor_autorizar <= 0:
                st.error("❌ El valor a autorizar debe ser mayor a 0")
                return False
            
            try:
                # Llamar a la función de autorización
                autorizar_oc(
                    oc_id=oc['id'],
                    valor_autorizado=valor_autorizar,
                    comentario=comentario.strip(),
                    usuario="Sistema"
                )
                
                st.success(f"✅ Autorizado ${valor_autorizar:,.0f} de la OC {oc['numero_oc']}")
                st.rerun()
                return True
                
            except Exception as e:
                st.error(f"❌ Error al autorizar: {str(e)}")
                return False
        
        if cancelado:
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
            autorizaciones = get_autorizaciones_oc(oc['id'])
            
            if not autorizaciones.empty:
                st.write("**Historial de Autorizaciones:**")
                
                for _, auth in autorizaciones.iterrows():
                    col_a1, col_a2, col_a3 = st.columns([2, 2, 1])
                    with col_a1:
                        st.write(f"**Valor:** ${auth['valor_autorizado']:,.0f}")
                    with col_a2:
                        # Formatear fecha
                        try:
                            fecha = pd.to_datetime(auth['fecha_autorizacion']).strftime('%d/%m/%Y %H:%M')
                            st.write(f"**Fecha:** {fecha}")
                        except:
                            st.write(f"**Fecha:** {auth['fecha_autorizacion']}")
                    with col_a3:
                        if auth['comentario']:
                            with st.expander("📝 Comentario"):
                                st.write(auth['comentario'])
                st.divider()
            else:
                st.write("No hay historial de autorizaciones.")
                
        except Exception as e:
            st.write(f"No se pudo cargar el historial: {e}")

def mostrar_oc_tarjeta(oc):
    """Muestra una OC como tarjeta interactiva con botones de edición/eliminación"""
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
                try:
                    fecha = pd.to_datetime(oc['fecha_registro']).strftime('%d/%m/%Y')
                    st.caption(f"Registro: {fecha}")
                except:
                    st.caption(f"Registro: {oc['fecha_registro']}")
            
            # Valor pendiente
            if 'valor_pendiente' in oc and oc['estado'] != 'AUTORIZADA':
                st.caption(f"Pendiente: ${oc['valor_pendiente']:,.0f}")
        
        with col3:
            # Botones de acción según estado
            if oc['estado'] in ['PENDIENTE', 'PARCIAL']:
                # Botón autorizar
                if st.button("✅ Autorizar", 
                           key=f"auth_btn_{oc['id']}", 
                           use_container_width=True,
                           help="Autorizar total o parcialmente"):
                    st.session_state[f'autorizar_oc_{oc["id"]}'] = True
                    st.rerun()
                
                # Botón editar
                if st.button("✏️ Editar", 
                           key=f"edit_btn_{oc['id']}", 
                           use_container_width=True,
                           help="Editar esta OC"):
                    st.session_state[f'editar_oc_{oc["id"]}'] = True
                    st.rerun()
                
                # Botón eliminar
                if st.button("🗑️ Eliminar", 
                           key=f"del_btn_{oc['id']}", 
                           use_container_width=True,
                           help="Eliminar esta OC"):
                    st.session_state[f'eliminar_oc_{oc["id"]}'] = True
                    st.rerun()
            else:
                # Para OCs autorizadas, solo mostrar detalle
                if st.button("📋 Detalle", 
                           key=f"det_btn_{oc['id']}", 
                           use_container_width=True,
                           help="Ver detalles completos"):
                    st.session_state[f'detalle_oc_{oc["id"]}'] = True
                    st.rerun()
        
        # Mostrar modal de autorización si está activo
        if f'autorizar_oc_{oc["id"]}' in st.session_state:
            mostrar_modal_autorizar(oc)
            # Limpiar estado después de mostrar
            if f'autorizar_oc_{oc["id"]}' in st.session_state:
                del st.session_state[f'autorizar_oc_{oc["id"]}']
        
        # Mostrar modal de edición si está activo
        if f'editar_oc_{oc["id"]}' in st.session_state:
            mostrar_modal_editar_oc(oc)
            # Limpiar estado después de mostrar
            if f'editar_oc_{oc["id"]}' in st.session_state:
                del st.session_state[f'editar_oc_{oc["id"]}']
        
        # Mostrar modal de eliminación si está activo
        if f'eliminar_oc_{oc["id"]}' in st.session_state:
            mostrar_modal_eliminar_oc(oc)
            # Limpiar estado después de mostrar
            if f'eliminar_oc_{oc["id"]}' in st.session_state:
                del st.session_state[f'eliminar_oc_{oc["id"]}']
        
        # Mostrar detalle si está activo
        if f'detalle_oc_{oc["id"]}' in st.session_state:
            mostrar_detalle_oc(oc)
            # Limpiar estado después de mostrar
            if f'detalle_oc_{oc["id"]}' in st.session_state:
                del st.session_state[f'detalle_oc_{oc["id"]}']
        
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
    except Exception as e:
        st.warning(f"No se pudieron cargar todas las estadísticas: {e}")
    
    # Botón para agregar nueva OC
    if st.button("➕ Agregar Nueva OC", 
                key="btn_nueva_oc",
                use_container_width=True,
                type="primary"):
        st.session_state['mostrar_modal_nueva_oc'] = True
    
    # Mostrar modal de nueva OC si está activo
    if 'mostrar_modal_nueva_oc' in st.session_state:
        mostrar_modal_agregar_oc()
        # Limpiar estado
        if 'mostrar_modal_nueva_oc' in st.session_state:
            del st.session_state['mostrar_modal_nueva_oc']
    
    st.divider()
    
    # Obtener clientes para filtros
    try:
        clientes = get_clientes()
        
        if not clientes.empty:
            cliente_lista = ["Todos"] + clientes['nombre'].tolist()
        else:
            cliente_lista = ["Todos"]
            st.warning("No hay clientes registrados. Agrega clientes primero.")
        
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
            ocs = get_todas_ocs()
        
        # Aplicar filtros
        if not ocs.empty:
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
                # Mostrar como tabla con acciones
                columnas_mostrar = [
                    'numero_oc', 'cliente_nombre', 'valor_total', 
                    'valor_autorizado', 'valor_pendiente', 'estado', 'tipo'
                ]
                
                # Filtrar columnas que existen
                columnas_existentes = [col for col in columnas_mostrar if col in ocs.columns]
                
                df_tabla = ocs[columnas_existentes].copy()
                df_tabla = df_tabla.rename(columns={
                    'numero_oc': 'Número OC',
                    'cliente_nombre': 'Cliente',
                    'valor_total': 'Valor Total',
                    'valor_autorizado': 'Autorizado',
                    'valor_pendiente': 'Pendiente',
                    'estado': 'Estado',
                    'tipo': 'Tipo'
                })
                
                # Formatear valores monetarios
                for col in ['Valor Total', 'Autorizado', 'Pendiente']:
                    if col in df_tabla.columns:
                        df_tabla[col] = df_tabla[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "")
                
                st.dataframe(
                    df_tabla,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Número OC": st.column_config.Column(width="medium"),
                        "Cliente": st.column_config.Column(width="large"),
                        "Valor Total": st.column_config.Column(width="small"),
                        "Autorizado": st.column_config.Column(width="small"),
                        "Pendiente": st.column_config.Column(width="small"),
                        "Estado": st.column_config.Column(width="small"),
                        "Tipo": st.column_config.Column(width="small")
                    }
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
