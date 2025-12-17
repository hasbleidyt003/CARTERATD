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
    """Modal para agregar nueva OC con opción de autorizar inmediatamente"""
    with st.form("form_nueva_oc"):
        st.subheader("➕ Agregar Nueva Orden de Compra")
        
        # Obtener clientes
        clientes_data = {
            '901212102': ['AUNA COLOMBIA S.A.S.', 21693849830, -2200000000],
            '890905166': ['EMPRESA SOCIAL DEL ESTADO HOSPITAL MENTAL DE ANTIOQ', 7500000000, -102807058],
            '900249425': ['PHARMASAN S.A.S', 5910785209, -200000000],
            '900746052': ['NEURUM SAS', 5500000000, -315752368],
            '800241602': ['FUNDACION COLOMBIANA DE CANCEROLOGIA CLINICA VIDA', 3500000000, -468530448],
            '890985122': ['COOPERATIVA DE HOSPITALES DE ANTIOQUIA', 1500000000, -208068595],
            '811038014': ['GRUPO ONCOLOGICO INTERNACIONAL S.A.', 900000000, -93146334]
        }
        
        if not clientes_data:
            st.warning("No hay clientes disponibles")
            return False
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Crear lista de clientes con información de cupo disponible
            opciones_clientes = []
            for nit, data in clientes_data.items():
                nombre, cupo_sugerido, disponible = data
                # Mostrar cupo disponible (negativo significa excedido)
                if disponible < 0:
                    estado_cupo = f"❌ Excedido: ${abs(disponible):,.0f}"
                else:
                    estado_cupo = f"✅ Disponible: ${disponible:,.0f}"
                
                texto_cliente = f"{nombre} - Cupo: ${cupo_sugerido:,.0f} ({estado_cupo})"
                opciones_clientes.append((texto_cliente, nit, nombre, disponible))
            
            # Selectbox para clientes
            cliente_opcion = st.selectbox(
                "Cliente *",
                options=[op[0] for op in opciones_clientes],
                help="Seleccione un cliente. Se muestra cupo total y disponibilidad"
            )
            
            # Obtener datos del cliente seleccionado
            cliente_info = None
            for op in opciones_clientes:
                if op[0] == cliente_opcion:
                    cliente_info = op
                    break
            
            # Número de OC
            numero_oc = st.text_input(
                "Número de OC *",
                placeholder="Ej: OC-2024-001, FACT-12345"
            )
        
        with col2:
            if cliente_info:
                nit_cliente, nombre_cliente, disponible_cliente = cliente_info[1], cliente_info[2], cliente_info[3]
                
                # Mostrar información del cupo
                st.info(f"**Cupo disponible:** ${disponible_cliente:,.0f}")
                
                # Valor total de la OC
                valor_total = st.number_input(
                    "Valor Total de la OC *",
                    min_value=0.0,
                    value=0.0,
                    step=100000.0,
                    format="%.0f"
                )
                
                # Validar si el valor excede el cupo disponible
                if valor_total > 0 and disponible_cliente < 0:
                    st.warning(f"⚠️ El cliente tiene excedido de cupo por ${abs(disponible_cliente):,.0f}")
                
                if valor_total > 0 and disponible_cliente >= 0 and valor_total > disponible_cliente:
                    st.error(f"❌ El valor excede el cupo disponible por ${valor_total - disponible_cliente:,.0f}")
                
                # Opción: ¿Autorizar inmediatamente o dejar pendiente?
                tipo_autorizacion = st.radio(
                    "Estado de la OC:",
                    ["📝 Dejar como PENDIENTE", "✅ Autorizar INMEDIATAMENTE"],
                    help="PENDIENTE: Solo registra la OC. AUTORIZAR: Descarga el cupo automáticamente"
                )
                
                autorizar_inmediato = tipo_autorizacion == "✅ Autorizar INMEDIATAMENTE"
                
                if autorizar_inmediato:
                    # Si autoriza inmediatamente, preguntar cuánto autorizar
                    if disponible_cliente >= 0:
                        max_valor = min(valor_total, disponible_cliente)
                        valor_autorizar = st.number_input(
                            "Valor a autorizar ahora *",
                            min_value=0.0,
                            max_value=float(max_valor),
                            value=float(valor_total) if valor_total <= disponible_cliente else float(disponible_cliente),
                            step=100000.0,
                            format="%.0f",
                            help=f"Máximo autorizable: ${max_valor:,.0f}"
                        )
                        
                        if valor_autorizar < valor_total:
                            st.warning(f"📝 Quedarán pendientes: ${valor_total - valor_autorizar:,.0f}")
                    else:
                        st.error("❌ No se puede autorizar: Cupo excedido")
                        valor_autorizar = 0
            else:
                valor_total = 0
                autorizar_inmediato = False
                valor_autorizar = 0
        
        # Comentarios
        comentarios = st.text_area(
            "Comentarios (opcional)",
            height=100,
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
        
        if submitted and cliente_info:
            # Validaciones
            if not numero_oc.strip():
                st.error("❌ El número de OC es obligatorio")
                return False
            
            if valor_total <= 0:
                st.error("❌ El valor total debe ser mayor a 0")
                return False
            
            nit_cliente, nombre_cliente, disponible_cliente = cliente_info[1], cliente_info[2], cliente_info[3]
            
            try:
                # Crear la OC
                oc_id = crear_oc(
                    cliente_nit=nit_cliente,
                    cliente_nombre=nombre_cliente,
                    numero_oc=numero_oc.strip(),
                    valor_total=valor_total,
                    tipo="SUELTA",
                    comentarios=comentarios.strip()
                )
                
                # Si se debe autorizar inmediatamente
                if autorizar_inmediato and valor_autorizar > 0:
                    if valor_autorizar <= disponible_cliente or disponible_cliente < 0:
                        # Autorizar la OC
                        autorizar_oc(
                            oc_id=oc_id,
                            valor_autorizado=valor_autorizar,
                            comentario="Autorización automática al crear OC",
                            usuario=st.session_state.get('username', 'Sistema')
                        )
                        
                        # Actualizar cupo disponible en los datos del cliente
                        # NOTA: Aquí deberías actualizar tu base de datos
                        nuevo_disponible = disponible_cliente - valor_autorizar
                        st.success(f"✅ OC '{numero_oc}' creada y autorizada por ${valor_autorizar:,.0f}")
                        st.info(f"📊 Cupo actualizado: ${nuevo_disponible:,.0f}")
                    else:
                        st.warning(f"⚠️ OC creada como PENDIENTE. No se pudo autorizar por exceso de cupo")
                else:
                    st.success(f"✅ OC '{numero_oc}' creada como PENDIENTE")
                
                st.rerun()
                return True
                
            except Exception as e:
                st.error(f"❌ Error al crear OC: {str(e)}")
                return False
        
        if cancel:
            st.rerun()
    
    return False

def mostrar_modal_autorizar(oc):
    """Modal para autorizar una OC pendiente"""
    with st.form(f"auth_form_{oc['id']}"):
        st.subheader(f"✅ Autorizar OC: {oc['numero_oc']}")
        
        # Obtener datos actuales del cliente
        clientes_data = {
            '901212102': ['AUNA COLOMBIA S.A.S.', 21693849830, -2200000000],
            '890905166': ['EMPRESA SOCIAL DEL ESTADO HOSPITAL MENTAL DE ANTIOQ', 7500000000, -102807058],
            '900249425': ['PHARMASAN S.A.S', 5910785209, -200000000],
            '900746052': ['NEURUM SAS', 5500000000, -315752368],
            '800241602': ['FUNDACION COLOMBIANA DE CANCEROLOGIA CLINICA VIDA', 3500000000, -468530448],
            '890985122': ['COOPERATIVA DE HOSPITALES DE ANTIOQUIA', 1500000000, -208068595],
            '811038014': ['GRUPO ONCOLOGICO INTERNACIONAL S.A.', 900000000, -93146334]
        }
        
        # Buscar cliente
        cliente_info = clientes_data.get(str(oc['cliente_nit']))
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.metric("Valor Total OC", f"${oc['valor_total']:,.0f}")
            st.metric("Ya Autorizado", f"${oc['valor_autorizado']:,.0f}")
        
        with col_info2:
            if cliente_info:
                nombre_cliente, cupo_sugerido, disponible = cliente_info
                st.metric("Cliente", nombre_cliente)
                st.metric("Cupo Disponible", f"${disponible:,.0f}")
        
        # Calcular valor restante de la OC
        valor_restante_oc = oc['valor_total'] - oc['valor_autorizado']
        
        if cliente_info:
            disponible_cliente = cliente_info[2]
            # El máximo que se puede autorizar es el mínimo entre lo que falta de la OC y el cupo disponible
            max_autorizable = min(valor_restante_oc, disponible_cliente) if disponible_cliente >= 0 else 0
            
            st.info(f"**Por autorizar de esta OC:** ${valor_restante_oc:,.0f}")
            
            if disponible_cliente < 0:
                st.error(f"❌ Cliente con cupo excedido por ${abs(disponible_cliente):,.0f}")
                max_autorizable = 0
            elif max_autorizable < valor_restante_oc:
                st.warning(f"⚠️ Solo se puede autorizar ${max_autorizable:,.0f} (cupo insuficiente)")
        else:
            max_autorizable = valor_restante_oc
            st.warning("Cliente no encontrado en base de datos")
        
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
        valor_sugerido = max_autorizable
        if porcentaje_key in st.session_state and max_autorizable > 0:
            porcentaje = st.session_state[porcentaje_key]
            valor_sugerido = min(valor_restante_oc * (porcentaje / 100), max_autorizable)
        
        # Campo para valor de autorización
        valor_autorizar = st.number_input(
            "Valor a autorizar *",
            min_value=0.0,
            max_value=float(max_autorizable),
            value=float(valor_sugerido),
            step=100000.0,
            format="%.0f"
        )
        
        # Mostrar lo que quedará pendiente
        if valor_autorizar > 0:
            nuevo_pendiente = valor_restante_oc - valor_autorizar
            nuevo_disponible = disponible_cliente - valor_autorizar if cliente_info else 0
            
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.metric("Quedará pendiente OC", f"${nuevo_pendiente:,.0f}")
            with col_res2:
                if cliente_info:
                    st.metric("Nuevo cupo disponible", f"${nuevo_disponible:,.0f}")
        
        # Comentario
        comentario = st.text_area(
            "Comentario (opcional)",
            placeholder="Motivo de la autorización...",
            height=100
        )
        
        # Botones de acción
        col_a, col_b = st.columns(2)
        
        confirmado = False
        with col_a:
            confirmado = st.form_submit_button(
                "✅ Confirmar Autorización",
                type="primary",
                use_container_width=True,
                disabled=(max_autorizable <= 0)
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
                # Autorizar la OC
                autorizar_oc(
                    oc_id=oc['id'],
                    valor_autorizado=valor_autorizar,
                    comentario=comentario.strip(),
                    usuario=st.session_state.get('username', 'Sistema')
                )
                
                # ACTUALIZAR EL CUPO DISPONIBLE EN LA BASE DE DATOS
                # Aquí deberías llamar a una función que actualice el disponible del cliente
                # Ejemplo: actualizar_cupo_cliente(oc['cliente_nit'], -valor_autorizar)
                
                st.success(f"✅ Autorizado ${valor_autorizar:,.0f} de la OC {oc['numero_oc']}")
                st.info(f"📊 Cupo del cliente reducido en ${valor_autorizar:,.0f}")
                
                st.rerun()
                return True
                
            except Exception as e:
                st.error(f"❌ Error al autorizar: {str(e)}")
                return False
        
        if cancelado:
            st.rerun()
    
    return False

def mostrar_oc_tarjeta(oc):
    """Muestra una OC como tarjeta interactiva"""
    with st.container():
        estado_colores = {
            'PENDIENTE': '🟡',
            'PARCIAL': '🟠', 
            'AUTORIZADA': '🟢'
        }
        color_icono = estado_colores.get(oc['estado'], '⚫')
        
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.subheader(f"📄 {oc['numero_oc']}")
            st.caption(f"**Cliente:** {oc['cliente_nombre']}")
            
            if oc['estado'] == 'PARCIAL':
                if oc['valor_total'] > 0:
                    progreso = (oc['valor_autorizado'] / oc['valor_total']) * 100
                    st.progress(progreso / 100)
                    st.caption(f"Autorizado: ${oc['valor_autorizado']:,.0f} de ${oc['valor_total']:,.0f} ({progreso:.1f}%)")
            else:
                st.write(f"**Valor:** ${oc['valor_total']:,.0f}")
            
            if 'tipo' in oc:
                st.caption(f"**Tipo:** {oc['tipo']}")
        
        with col2:
            st.metric("Estado", f"{color_icono} {oc['estado']}")
            
            if 'fecha_registro' in oc:
                try:
                    fecha = pd.to_datetime(oc['fecha_registro']).strftime('%d/%m/%Y')
                    st.caption(f"Registro: {fecha}")
                except:
                    st.caption(f"Registro: {oc['fecha_registro']}")
            
            valor_pendiente = oc['valor_total'] - oc.get('valor_autorizado', 0)
            if valor_pendiente > 0 and oc['estado'] != 'AUTORIZADA':
                st.caption(f"**Pendiente:** ${valor_pendiente:,.0f}")
        
        with col3:
            if oc['estado'] in ['PENDIENTE', 'PARCIAL']:
                # Botón autorizar
                if st.button("✅ Autorizar", 
                           key=f"auth_btn_{oc['id']}", 
                           use_container_width=True,
                           help="Usar cupo disponible para autorizar"):
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
        
        st.divider()

# ==================== FUNCIÓN PRINCIPAL ====================

def show():
    """Función principal de la página de OCs"""
    st.header("📋 Gestión de Órdenes de Compra (OCs)")
    
    # Mostrar resumen de cupos de clientes
    st.subheader("🏦 Cupos de Clientes")
    
    clientes_data = [
        ['901212102', 'AUNA COLOMBIA S.A.S.', 21693849830, -2200000000],
        ['890905166', 'EMPRESA SOCIAL DEL ESTADO HOSPITAL MENTAL DE ANTIOQ', 7500000000, -102807058],
        ['900249425', 'PHARMASAN S.A.S', 5910785209, -200000000],
        ['900746052', 'NEURUM SAS', 5500000000, -315752368],
        ['800241602', 'FUNDACION COLOMBIANA DE CANCEROLOGIA CLINICA VIDA', 3500000000, -468530448],
        ['890985122', 'COOPERATIVA DE HOSPITALES DE ANTIOQUIA', 1500000000, -208068595],
        ['811038014', 'GRUPO ONCOLOGICO INTERNACIONAL S.A.', 900000000, -93146334]
    ]
    
    # Crear dataframe para mostrar
    df_clientes = pd.DataFrame(clientes_data, 
                              columns=['NIT', 'Cliente', 'Cupo Total', 'Disponible'])
    
    # Formatear valores
    df_clientes['Cupo Total'] = df_clientes['Cupo Total'].apply(lambda x: f"${x:,.0f}")
    df_clientes['Disponible'] = df_clientes['Disponible'].apply(lambda x: f"${x:,.0f}")
    
    # Mostrar tabla de clientes
    st.dataframe(df_clientes, use_container_width=True, hide_index=True)
    
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
    
    # Mostrar OCs existentes
    st.subheader("📄 Órdenes de Compra Existentes")
    
    try:
        with st.spinner("Cargando Órdenes de Compra..."):
            ocs = get_todas_ocs()
        
        if not ocs.empty:
            # Filtrar por estado si se desea
            estado_filtro = st.selectbox(
                "Filtrar por estado:",
                ["Todas", "PENDIENTE", "PARCIAL", "AUTORIZADA"],
                key="filtro_estado_ocs"
            )
            
            if estado_filtro != "Todas":
                ocs = ocs[ocs['estado'] == estado_filtro]
            
            st.write(f"**Mostrando {len(ocs)} OCs**")
            
            # Mostrar como tarjetas
            for _, oc in ocs.iterrows():
                mostrar_oc_tarjeta(oc)
        else:
            st.info("📭 No hay OCs registradas aún")
            
    except Exception as e:
        st.error(f"❌ Error al cargar OCs: {str(e)}")
        st.code(f"Detalle: {e}")

# ==================== EJECUCIÓN PARA PRUEBAS ====================

if __name__ == "__main__":
    # Para pruebas directas
    st.set_page_config(page_title="Gestión de OCs", layout="wide")
    
    # Simular usuario logueado
    if 'username' not in st.session_state:
        st.session_state['username'] = "admin"
    
    show()
