import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
from io import BytesIO

# Configuración de página
st.set_page_config(
    page_title="🧹 Mantenimiento",
    page_icon="🧹",
    layout="wide"
)

# ==================== CONTENIDO PÁGINA ====================
st.title("🧹 Mantenimiento del Sistema")

# Verificar autenticación
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("🔒 Por favor inicie sesión primero")
    st.stop()

# Estadísticas
conn = sqlite3.connect('database.db')

stats = {}
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM clientes WHERE activo = 1")
stats['clientes'] = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM ocs")
stats['ocs_totales'] = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM ocs WHERE estado IN ('PENDIENTE', 'PARCIAL')")
stats['ocs_pendientes'] = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM ocs WHERE estado = 'AUTORIZADA'")
stats['ocs_autorizadas'] = cursor.fetchone()[0]

# Tamaño de la BD
if os.path.exists('database.db'):
    db_size = os.path.getsize('database.db') / (1024 * 1024)
else:
    db_size = 0

conn.close()

# Mostrar estadísticas
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Clientes Activos", stats['clientes'])
with col2:
    st.metric("OCs Totales", stats['ocs_totales'])
with col3:
    st.metric("OCs Pendientes", stats['ocs_pendientes'])
with col4:
    st.metric("Tamaño BD", f"{db_size:.2f} MB")

st.divider()

# Limpieza manual
st.subheader("🗑️ Limpieza de Historial")

st.warning("""
⚠️ **ADVERTENCIA:** Esta acción eliminará permanentemente OCs antiguas.
Se recomienda hacer un backup antes de proceder.
""")

col_a, col_b, col_c = st.columns(3)
with col_a:
    dias_limpieza = st.selectbox(
        "Eliminar OCs autorizadas con más de:",
        [30, 60, 90, 180, 365],
        index=2,
        key="dias_limpieza"
    )
with col_b:
    mantener_pendientes = st.checkbox("Mantener todas las OCs pendientes", value=True, key="mantener_pendientes")
with col_c:
    crear_backup = st.checkbox("Crear backup automático", value=True, key="crear_backup")

if st.button("📊 Previsualizar Impacto", use_container_width=True, key="btn_preview"):
    # Previsualizar
    conn = sqlite3.connect('database.db')
    
    fecha_limite = datetime.now() - timedelta(days=dias_limpieza)
    fecha_limite_str = fecha_limite.strftime('%Y-%m-%d')
    
    query = f"""
    SELECT 
        COUNT(*) as cantidad,
        SUM(valor_total) as valor_total,
        SUM(valor_autorizado) as valor_autorizado
    FROM ocs 
    WHERE estado = 'AUTORIZADA'
    AND (fecha_ultima_autorizacion < '{fecha_limite_str}' OR fecha_ultima_autorizacion IS NULL)
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df.empty and df['cantidad'].iloc[0] > 0:
        st.info(f"""
        **Se eliminarían:**
        • {df['cantidad'].iloc[0]:,} OCs autorizadas
        • Valor total: ${df['valor_total'].iloc[0]:,.0f}
        • Autorizado: ${df['valor_autorizado'].iloc[0]:,.0f}
        • Con fecha anterior a: {fecha_limite_str}
        """)
        
        confirmar = st.checkbox("✅ Confirmo que deseo proceder con la limpieza", key="confirmar_limpieza")
        if confirmar:
            st.session_state.confirmar_limpieza = True
            st.success("✅ Listo para ejecutar. Puede usar el botón de ejecución.")
    else:
        st.success("✅ No hay OCs que cumplan los criterios de eliminación")

st.divider()

# Botones de acción
col_exe1, col_exe2 = st.columns([1, 2])

with col_exe1:
    if st.button("💾 Crear Backup", use_container_width=True, key="btn_backup"):
        # Crear backup
        conn = sqlite3.connect('database.db')
        
        # Crear Excel en memoria
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Exportar cada tabla
            df_clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
            df_ocs = pd.read_sql_query("SELECT * FROM ocs", conn)
            
            df_clientes.to_excel(writer, sheet_name='Clientes', index=False)
            df_ocs.to_excel(writer, sheet_name='OCs', index=False)
            
            # Si existe tabla de autorizaciones
            try:
                df_auth = pd.read_sql_query("SELECT * FROM autorizaciones_parciales", conn)
                df_auth.to_excel(writer, sheet_name='Autorizaciones', index=False)
            except:
                pass
        
        conn.close()
        
        # Ofrecer descarga
        fecha = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button(
            label="📥 Descargar Backup",
            data=output.getvalue(),
            file_name=f"backup_cupos_{fecha}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_backup"
        )
        
        st.success("✅ Backup listo para descargar")

with col_exe2:
    if st.button("🚨 EJECUTAR LIMPIEZA", type="primary", use_container_width=True,
                disabled=not st.session_state.get('confirmar_limpieza', False),
                key="btn_ejecutar_limpieza"):
        # Ejecutar limpieza
        if crear_backup:
            st.info("⚠️ Por favor descargue el backup primero antes de continuar")
            st.stop()
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        fecha_limite = datetime.now() - timedelta(days=dias_limpieza)
        fecha_limite_str = fecha_limite.strftime('%Y-%m-%d')
        
        # Eliminar OCs antiguas
        query = f"""
        DELETE FROM ocs 
        WHERE estado = 'AUTORIZADA'
        AND (fecha_ultima_autorizacion < '{fecha_limite_str}' OR fecha_ultima_autorizacion IS NULL)
        """
        
        cursor.execute(query)
        
        # Eliminar autorizaciones huérfanas
        cursor.execute("""
        DELETE FROM autorizaciones_parciales 
        WHERE oc_id NOT IN (SELECT id FROM ocs)
        """)
        
        conn.commit()
        conn.close()
        
        st.success("✅ Limpieza completada exitosamente")
        del st.session_state.confirmar_limpieza
        st.rerun()
