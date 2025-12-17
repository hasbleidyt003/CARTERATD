import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="📋 OCs",
    page_icon="📋",
    layout="wide"
)

# ==================== FUNCIONES BD ====================
def get_clientes():
    conn = sqlite3.connect('database.db')
    query = '''
    SELECT * FROM clientes WHERE activo = 1 ORDER BY nombre
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_ocs(cliente_nit=None):
    conn = sqlite3.connect('database.db')
    if cliente_nit:
        query = '''
        SELECT o.*, c.nombre as cliente_nombre 
        FROM ocs o
        JOIN clientes c ON o.cliente_nit = c.nit
        WHERE o.cliente_nit = ?
        ORDER BY o.fecha_registro DESC
        '''
        df = pd.read_sql_query(query, conn, params=(cliente_nit,))
    else:
        query = '''
        SELECT o.*, c.nombre as cliente_nombre 
        FROM ocs o
        JOIN clientes c ON o.cliente_nit = c.nit
        ORDER BY o.fecha_registro DESC
        '''
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ==================== CONTENIDO PÁGINA ====================
st.title("📋 Gestión de Órdenes de Compra")

# Verificar autenticación
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("🔒 Por favor inicie sesión primero")
    st.stop()

# Filtros
clientes = get_clientes()
cliente_lista = ["Todos"] + clientes['nombre'].tolist()

col1, col2, col3 = st.columns(3)
with col1:
    filtro_cliente = st.selectbox("Filtrar por Cliente", cliente_lista, key="filtro_cliente")
with col2:
    filtro_estado = st.selectbox("Filtrar por Estado", 
                               ["Todos", "PENDIENTE", "PARCIAL", "AUTORIZADA"],
                               key="filtro_estado")
with col3:
    filtro_tipo = st.selectbox("Filtrar por Tipo", 
                             ["Todos", "CUPO_NUEVO", "SUELTA"],
                             key="filtro_tipo")

# Obtener y filtrar OCs
ocs = get_ocs()

if filtro_cliente != "Todos":
    cliente_nit = clientes[clientes['nombre'] == filtro_cliente]['nit'].iloc[0]
    ocs = ocs[ocs['cliente_nit'] == cliente_nit]

if filtro_estado != "Todos":
    ocs = ocs[ocs['estado'] == filtro_estado]

if filtro_tipo != "Todos":
    ocs = ocs[ocs['tipo'] == filtro_tipo]

# Mostrar OCs
if not ocs.empty:
    for _, oc in ocs.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.subheader(f"📄 {oc['numero_oc']}")
                st.caption(f"Cliente: {oc['cliente_nombre']}")
                
                if oc['estado'] == 'PARCIAL':
                    porcentaje = (oc['valor_autorizado'] / oc['valor_total']) * 100
                    st.progress(porcentaje / 100)
                    st.text(f"Autorizado: ${oc['valor_autorizado']:,.0f} de ${oc['valor_total']:,.0f} ({porcentaje:.1f}%)")
                else:
                    st.text(f"Valor: ${oc['valor_total']:,.0f}")
            
            with col2:
                estado_color = {'PENDIENTE': '🟡', 'PARCIAL': '🟠', 'AUTORIZADA': '🟢'}
                st.metric("Estado", f"{estado_color.get(oc['estado'], '⚫')} {oc['estado']}")
                st.caption(f"Tipo: {oc['tipo']}")
                if oc['cupo_referencia']:
                    st.caption(f"Ref: {oc['cupo_referencia']}")
            
            with col3:
                if oc['estado'] in ['PENDIENTE', 'PARCIAL']:
                    if st.button("✅ Autorizar", key=f"auth_{oc['id']}", use_container_width=True):
                        st.session_state[f"oc_autorizar_{oc['id']}"] = True
                        st.rerun()
                else:
                    if st.button("📋 Detalle", key=f"det_{oc['id']}", use_container_width=True):
                        st.session_state[f"oc_detalle_{oc['id']}"] = True
                        st.rerun()
            
            # Modal para autorizar
            if st.session_state.get(f"oc_autorizar_{oc['id']}", False):
                with st.form(f"auth_form_{oc['id']}"):
                    st.subheader(f"Autorizar OC: {oc['numero_oc']}")
                    
                    st.info(f"**Valor total:** ${oc['valor_total']:,.0f}")
                    if oc['estado'] == 'PARCIAL':
                        st.info(f"**Ya autorizado:** ${oc['valor_autorizado']:,.0f}")
                    
                    valor_restante = oc['valor_total'] - oc['valor_autorizado']
                    
                    # Opciones rápidas
                    col_btns1, col_btns2, col_btns3, col_btns4 = st.columns(4)
                    with col_btns1:
                        if st.button("25%", key=f"25_{oc['id']}", use_container_width=True):
                            st.session_state[f"valor_{oc['id']}"] = valor_restante * 0.25
                    with col_btns2:
                        if st.button("50%", key=f"50_{oc['id']}", use_container_width=True):
                            st.session_state[f"valor_{oc['id']}"] = valor_restante * 0.50
                    with col_btns3:
                        if st.button("75%", key=f"75_{oc['id']}", use_container_width=True):
                            st.session_state[f"valor_{oc['id']}"] = valor_restante * 0.75
                    with col_btns4:
                        if st.button("100%", key=f"100_{oc['id']}", use_container_width=True):
                            st.session_state[f"valor_{oc['id']}"] = valor_restante
                    
                    # Campo para valor exacto
                    valor_default = st.session_state.get(f"valor_{oc['id']}", valor_restante)
                    valor_autorizar = st.number_input(
                        "Valor a autorizar",
                        min_value=0.0,
                        max_value=float(valor_restante),
                        value=float(valor_default),
                        step=1000000.0,
                        key=f"input_valor_{oc['id']}"
                    )
                    
                    comentario = st.text_area("Comentario (opcional)", key=f"coment_{oc['id']}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.form_submit_button("✅ Confirmar Autorización", use_container_width=True):
                            # Actualizar OC
                            conn = sqlite3.connect('database.db')
                            cursor = conn.cursor()
                            
                            nuevo_valor_autorizado = oc['valor_autorizado'] + valor_autorizar
                            nuevo_estado = 'AUTORIZADA' if valor_autorizar == valor_restante else 'PARCIAL'
                            
                            cursor.execute('''
                                UPDATE ocs 
                                SET valor_autorizado = ?, estado = ?, fecha_ultima_autorizacion = ?
                                WHERE id = ?
                            ''', (nuevo_valor_autorizado, nuevo_estado, datetime.now(), oc['id']))
                            
                            # Registrar autorización parcial
                            cursor.execute('''
                                INSERT INTO autorizaciones_parciales (oc_id, valor_autorizado, comentario, usuario)
                                VALUES (?, ?, ?, ?)
                            ''', (oc['id'], valor_autorizar, comentario, st.session_state.get('username', 'admin')))
                            
                            conn.commit()
                            conn.close()
                            
                            st.success(f"✅ Autorizado ${valor_autorizar:,.0f}")
                            del st.session_state[f"oc_autorizar_{oc['id']}"]
                            del st.session_state[f"valor_{oc['id']}"]
                            st.rerun()
                    
                    with col_b:
                        if st.form_submit_button("❌ Cancelar", use_container_width=True):
                            del st.session_state[f"oc_autorizar_{oc['id']}"]
                            del st.session_state[f"valor_{oc['id']}"]
                            st.rerun()
            
            st.divider()
else:
    st.info("No hay OCs que coincidan con los filtros")

# Botón para nueva OC
st.divider()
if st.button("➕ Agregar Nueva OC", use_container_width=True, key="btn_nueva_oc"):
    st.session_state.mostrar_nueva_oc = True

# Modal para nueva OC
if st.session_state.get('mostrar_nueva_oc', False):
    with st.form("nueva_oc_form"):
        st.subheader("🆕 Nueva OC")
        
        col1, col2 = st.columns(2)
        with col1:
            cliente_nit = st.selectbox(
                "Cliente *",
                options=clientes['nit'].tolist(),
                format_func=lambda x: f"{clientes[clientes['nit']==x]['nombre'].iloc[0]} (NIT: {x})",
                key="nueva_oc_cliente"
            )
            numero_oc = st.text_input("Número OC *", key="nueva_oc_numero")
        
        with col2:
            valor_total = st.number_input("Valor Total *", min_value=0.0, value=0.0, step=1000000.0, key="nueva_oc_valor")
            tipo = st.selectbox("Tipo", ["SUELTA", "CUPO_NUEVO"], key="nueva_oc_tipo")
        
        if tipo == "CUPO_NUEVO":
            cupo_referencia = st.text_input("Referencia de Cupo", key="nueva_oc_ref")
        else:
            cupo_referencia = None
        
        comentarios = st.text_area("Comentarios (opcional)", key="nueva_oc_coment")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.form_submit_button("💾 Guardar OC", use_container_width=True):
                if cliente_nit and numero_oc and valor_total > 0:
                    conn = sqlite3.connect('database.db')
                    cursor = conn.cursor()
                    try:
                        cursor.execute('''
                            INSERT INTO ocs (cliente_nit, numero_oc, valor_total, tipo, cupo_referencia, comentarios)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (cliente_nit, numero_oc, valor_total, tipo, cupo_referencia, comentarios))
                        conn.commit()
                        st.success(f"✅ OC {numero_oc} registrada")
                        del st.session_state.mostrar_nueva_oc
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ Ya existe una OC con ese número")
                    finally:
                        conn.close()
                else:
                    st.error("❌ Complete los campos obligatorios (*)")
        
        with col_b:
            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                del st.session_state.mostrar_nueva_oc
                st.rerun()
