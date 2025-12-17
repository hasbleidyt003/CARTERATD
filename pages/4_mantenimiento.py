import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import os

def show():
    st.title("Mantenimiento del Sistema")
    
    # Estadísticas actuales
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM clientes WHERE activo = 1")
    clientes_activos = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ocs")
    ocs_totales = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ocs WHERE estado IN ('PENDIENTE', 'PARCIAL')")
    ocs_pendientes = cursor.fetchone()[0]
    
    db_size = os.path.getsize('data/database.db') / (1024 * 1024)
    
    conn.close()
    
    # Mostrar estadísticas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Clientes Activos", clientes_activos)
    
    with col2:
        st.metric("OCs Totales", ocs_totales)
    
    with col3:
        st.metric("OCs Pendientes", ocs_pendientes)
    
    with col4:
        st.metric("Tamaño BD", f"{db_size:.2f} MB")
    
    st.divider()
    
    # Sección de limpieza
    st.subheader("Limpieza de Historial")
    
    st.warning("ADVERTENCIA: Esta acción eliminará permanentemente OCs antiguas. Se recomienda hacer backup antes.")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        dias_limpieza = st.selectbox("Eliminar OCs autorizadas con más de:", [30, 60, 90, 180, 365], index=2)
    
    with col_b:
        mantener_pendientes = st.checkbox("Mantener todas las OCs pendientes", value=True)
    
    with col_c:
        crear_backup = st.checkbox("Crear backup automático", value=True)
    
    if st.button("Previsualizar Impacto", use_container_width=True):
        previsualizar_limpieza(dias_limpieza, mantener_pendientes)
    
    st.divider()
    
    # Botón de ejecución
    col_exe1, col_exe2 = st.columns([1, 2])
    
    with col_exe1:
        if st.button("Crear Backup Completo", use_container_width=True):
            crear_backup_completo()
    
    with col_exe2:
        if st.button("EJECUTAR LIMPIEZA", type="primary", use_container_width=True,
                    disabled=not st.session_state.get('confirmar_limpieza', False)):
            ejecutar_limpieza(dias_limpieza, mantener_pendientes, crear_backup)

def previsualizar_limpieza(dias, mantener_pendientes):
    conn = sqlite3.connect('data/database.db')
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    fecha_limite_str = fecha_limite.strftime('%Y-%m-%d')
    
    query = f"""
    SELECT 
        COUNT(*) as cantidad,
        SUM(valor_total) as valor_total,
        SUM(valor_autorizado) as valor_autorizado
    FROM ocs 
    WHERE estado = 'AUTORIZADA'
    AND fecha_ultima_autorizacion < '{fecha_limite_str}'
    """
    
    if mantener_pendientes:
        query += " AND estado = 'AUTORIZADA'"
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df.empty and df['cantidad'].iloc[0] > 0:
        st.info(f"""
        Se eliminarían:
        • {df['cantidad'].iloc[0]:,} OCs autorizadas
        • Valor total: ${df['valor_total'].iloc[0]:,.0f}
        • Autorizado: ${df['valor_autorizado'].iloc[0]:,.0f}
        • Con fecha anterior a: {fecha_limite_str}
        """)
        
        confirmar = st.checkbox("Confirmo que deseo proceder con la limpieza")
        if confirmar:
            st.session_state.confirmar_limpieza = True
            st.success("Listo para ejecutar. Puede usar el botón de ejecución.")
    else:
        st.success("No hay OCs que cumplan los criterios de eliminación")

def crear_backup_completo():
    conn = sqlite3.connect('data/database.db')
    
    fecha = datetime.now().strftime("%Y%m%d_%H%M")
    backup_path = f"data/backups/backup_{fecha}.xlsx"
    
    os.makedirs("data/backups", exist_ok=True)
    
    with pd.ExcelWriter(backup_path, engine='openpyxl') as writer:
        df_clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
        df_clientes.to_excel(writer, sheet_name='Clientes', index=False)
        
        df_ocs = pd.read_sql_query("SELECT * FROM ocs", conn)
        df_ocs.to_excel(writer, sheet_name='OCs', index=False)
        
        df_auth = pd.read_sql_query("SELECT * FROM autorizaciones_parciales", conn)
        df_auth.to_excel(writer, sheet_name='Autorizaciones', index=False)
    
    conn.close()
    
    with open(backup_path, 'rb') as f:
        st.download_button(
            label="Descargar Backup",
            data=f,
            file_name=f"backup_cupos_{fecha}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    st.success(f"Backup creado: {backup_path}")

def ejecutar_limpieza(dias, mantener_pendientes, crear_backup):
    if crear_backup:
        crear_backup_completo()
    
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    fecha_limite_str = fecha_limite.strftime('%Y-%m-%d')
    
    query = f"""
    DELETE FROM ocs 
    WHERE estado = 'AUTORIZADA'
    AND fecha_ultima_autorizacion < '{fecha_limite_str}'
    """
    
    cursor.execute(query)
    conn.commit()
    
    cursor.execute("""
    DELETE FROM autorizaciones_parciales 
    WHERE oc_id NOT IN (SELECT id FROM ocs)
    """)
    
    conn.commit()
    conn.close()
    
    st.success("Limpieza completada exitosamente")    st.success("✅ Limpieza completada exitosamente")
    st.rerun()
