"""
Módulo de mantenimiento y reportes del Sistema de Cartera TD
Incluye backup, limpieza y reportes avanzados
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import io
import os
from modules.database import (
    get_backup_data,
    exportar_a_excel,
    limpiar_ocs_antiguas,
    optimizar_base_datos,
    get_estadisticas_generales,
    get_estadisticas_por_cliente,
    get_historico_pagos
)

def show():
    """Función principal de mantenimiento"""
    st.header("🔧 Mantenimiento y Reportes")
    
    # Pestañas para organizar funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Reportes Avanzados",
        "💾 Backup y Exportación",
        "🧹 Limpieza y Optimización",
        "⚙️ Configuración"
    ])
    
    # ========== PESTAÑA 1: REPORTES AVANZADOS ==========
    with tab1:
        st.subheader("📊 Reportes Avanzados")
        
        col_report1, col_report2 = st.columns(2)
        
        with col_report1:
            st.markdown("##### Estadísticas Detalladas")
            
            try:
                stats = get_estadisticas_generales()
                
                # Mostrar estadísticas en tarjetas
                st.info(f"""
                **Resumen General:**
                - **Total Clientes:** {stats['total_clientes']}
                - **Total Cupo:** ${stats['total_cupo_sugerido']:,.0f}
                - **Saldo Actual:** ${stats['total_saldo_actual']:,.0f}
                - **Cartera Vencida:** ${stats['total_cartera_vencida']:,.0f}
                - **Disponible:** ${stats['total_disponible']:,.0f}
                - **OCs Pendientes:** ${stats['total_ocs_pendientes']:,.0f}
                """)
                
                # Botón para descargar reporte detallado
                if st.button("📥 Descargar Reporte Detallado", use_container_width=True):
                    clientes_stats = get_estadisticas_por_cliente()
                    
                    # Crear archivo en memoria
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        clientes_stats.to_excel(writer, sheet_name='Clientes', index=False)
                        
                        # Hoja de resumen
                        resumen_df = pd.DataFrame([stats])
                        resumen_df.to_excel(writer, sheet_name='Resumen', index=False)
                    
                    output.seek(0)
                    
                    st.download_button(
                        label="⬇️ Descargar Excel",
                        data=output,
                        file_name=f"reporte_cartera_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
            except Exception as e:
                st.error(f"❌ Error al generar reporte: {str(e)}")
        
        with col_report2:
            st.markdown("##### Histórico de Pagos (Últimos 30 días)")
            
            try:
                historico = get_historico_pagos(dias=30)
                
                if not historico.empty:
                    # Formatear fechas
                    historico['fecha'] = pd.to_datetime(historico['fecha']).dt.strftime('%d/%m/%Y')
                    historico['valor'] = historico['valor'].apply(lambda x: f"${x:,.0f}")
                    
                    st.dataframe(
                        historico[['fecha', 'cliente_nombre', 'valor', 'descripcion']].rename(columns={
                            'fecha': 'Fecha',
                            'cliente_nombre': 'Cliente',
                            'valor': 'Valor',
                            'descripcion': 'Descripción'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    total_pagado = historico['valor'].str.replace('$', '').str.replace(',', '').astype(float).sum()
                    st.success(f"**Total pagado en periodo:** ${total_pagado:,.0f}")
                else:
                    st.info("No hay pagos registrados en los últimos 30 días")
                    
            except Exception as e:
                st.error(f"❌ Error al cargar histórico: {str(e)}")
        
        # Reporte de clientes críticos
        st.markdown("##### 🚨 Clientes en Estado Crítico")
        
        try:
            clientes_stats = get_estadisticas_por_cliente()
            
            if not clientes_stats.empty:
                criticos = clientes_stats[
                    (clientes_stats['estado'] == 'SOBREPASADO') | 
                    (clientes_stats['estado'] == 'ALERTA')
                ].copy()
                
                if not criticos.empty:
                    # Formatear valores
                    criticos['cupo_sugerido_fmt'] = criticos['cupo_sugerido'].apply(lambda x: f"${x:,.0f}")
                    criticos['saldo_actual_fmt'] = criticos['saldo_actual'].apply(lambda x: f"${x:,.0f}")
                    criticos['ocs_pendientes_fmt'] = criticos['ocs_pendientes'].apply(lambda x: f"${x:,.0f}")
                    criticos['porcentaje_uso_fmt'] = criticos['porcentaje_uso'].apply(lambda x: f"{x:.1f}%")
                    
                    # Mostrar en tabla con colores
                    st.dataframe(
                        criticos[['nombre', 'saldo_actual_fmt', 'cupo_sugerido_fmt', 'porcentaje_uso_fmt', 'ocs_pendientes_fmt', 'estado']].rename(columns={
                            'nombre': 'Cliente',
                            'saldo_actual_fmt': 'Saldo Actual',
                            'cupo_sugerido_fmt': 'Cupo',
                            'porcentaje_uso_fmt': '% Uso',
                            'ocs_pendientes_fmt': 'OCs Pendientes',
                            'estado': 'Estado'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.success("✅ No hay clientes en estado crítico")
            else:
                st.info("No hay datos de clientes disponibles")
                
        except Exception as e:
            st.error(f"❌ Error al cargar clientes críticos: {str(e)}")
    
    # ========== PESTAÑA 2: BACKUP Y EXPORTACIÓN ==========
    with tab2:
        st.subheader("💾 Backup y Exportación de Datos")
        
        col_backup1, col_backup2 = st.columns(2)
        
        with col_backup1:
            st.markdown("##### Exportar a Excel")
            st.info("Exporta todos los datos a un archivo Excel para análisis externo.")
            
            if st.button("📥 Exportar Todo a Excel", use_container_width=True):
                try:
                    ruta = exportar_a_excel()
                    st.success(f"✅ Exportación completada: {ruta}")
                    
                    # Leer el archivo para descarga
                    with open(ruta, 'rb') as f:
                        excel_data = f.read()
                    
                    st.download_button(
                        label="⬇️ Descargar Archivo Excel",
                        data=excel_data,
                        file_name=os.path.basename(ruta),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error al exportar: {str(e)}")
            
            st.markdown("---")
            st.markdown("##### Exportación Parcial")
            
            # Opciones de exportación parcial
            export_opciones = st.multiselect(
                "Seleccionar tablas para exportar:",
                ["Clientes", "Órdenes de Compra", "Movimientos", "Autorizaciones"],
                default=["Clientes", "Órdenes de Compra"]
            )
            
            if st.button("📥 Exportar Seleccionadas", use_container_width=True):
                try:
                    datos = get_backup_data()
                    
                    # Filtrar según selección
                    datos_exportar = {}
                    if "Clientes" in export_opciones:
                        datos_exportar['Clientes'] = datos['clientes']
                    if "Órdenes de Compra" in export_opciones:
                        datos_exportar['OCs'] = datos['ocs']
                    if "Movimientos" in export_opciones:
                        datos_exportar['Movimientos'] = datos['movimientos']
                    if "Autorizaciones" in export_opciones:
                        datos_exportar['Autorizaciones'] = datos['autorizaciones']
                    
                    # Crear archivo en memoria
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        for nombre, df in datos_exportar.items():
                            df.to_excel(writer, sheet_name=nombre, index=False)
                    
                    output.seek(0)
                    
                    st.download_button(
                        label="⬇️ Descargar Excel Parcial",
                        data=output,
                        file_name=f"exportacion_parcial_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error en exportación parcial: {str(e)}")
        
        with col_backup2:
            st.markdown("##### Información del Sistema")
            
            try:
                # Verificar tamaño de la base de datos
                if os.path.exists('data/database.db'):
                    size_bytes = os.path.getsize('data/database.db')
                    size_mb = size_bytes / (1024 * 1024)
                    
                    st.metric("Tamaño Base de Datos", f"{size_mb:.2f} MB")
                
                # Estadísticas de tablas
                conn = sqlite3.connect('data/database.db')
                tablas = ['clientes', 'ocs', 'movimientos', 'autorizaciones_parciales']
                
                for tabla in tablas:
                    try:
                        count = pd.read_sql_query(f"SELECT COUNT(*) as cnt FROM {tabla}", conn).iloc[0]['cnt']
                        st.write(f"**{tabla.capitalize()}:** {count} registros")
                    except:
                        pass
                
                conn.close()
                
            except Exception as e:
                st.error(f"❌ Error al obtener información: {str(e)}")
            
            st.markdown("---")
            st.markdown("##### Backup Automático")
            
            dias_backup = st.slider(
                "Días para mantener backups automáticos:",
                min_value=7,
                max_value=90,
                value=30,
                help="Los backups más antiguos serán eliminados automáticamente"
            )
            
            if st.button("🔄 Ejecutar Backup Ahora", use_container_width=True):
                try:
                    fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
                    ruta_backup = f"data/backups/backup_{fecha}.xlsx"
                    
                    exportar_a_excel(ruta_backup)
                    st.success(f"✅ Backup creado: {ruta_backup}")
                    
                except Exception as e:
                    st.error(f"❌ Error en backup: {str(e)}")
    
    # ========== PESTAÑA 3: LIMPIEZA Y OPTIMIZACIÓN ==========
    with tab3:
        st.subheader("🧹 Limpieza y Optimización")
        
        st.warning("⚠️ **ADVERTENCIA:** Estas operaciones pueden eliminar datos permanentemente.")
        
        col_clean1, col_clean2 = st.columns(2)
        
        with col_clean1:
            st.markdown("##### Limpieza de OCs Antiguas")
            
            dias_limpieza = st.number_input(
                "Eliminar OCs autorizadas con más de (días):",
                min_value=30,
                max_value=365,
                value=90,
                step=30
            )
            
            mantener_pendientes = st.checkbox(
                "Mantener OCs pendientes y parciales",
                value=True,
                help="Solo eliminará OCs completamente autorizadas"
            )
            
            if st.button("🧹 Ejecutar Limpieza", use_container_width=True):
                try:
                    with st.spinner("Ejecutando limpieza..."):
                        eliminadas = limpiar_ocs_antiguas(
                            dias=dias_limpieza,
                            mantener_pendientes=mantener_pendientes
                        )
                    
                    if eliminadas > 0:
                        st.success(f"✅ Se eliminaron {eliminadas} OCs antiguas")
                    else:
                        st.info("ℹ️ No se encontraron OCs para eliminar")
                        
                except Exception as e:
                    st.error(f"❌ Error en limpieza: {str(e)}")
            
            st.markdown("---")
            st.markdown("##### Optimización de Base de Datos")
            
            st.info("La optimización (VACUUM) reorganiza la base de datos para mejorar el rendimiento.")
            
            if st.button("⚡ Optimizar Base de Datos", use_container_width=True):
                try:
                    with st.spinner("Optimizando..."):
                        optimizar_base_datos()
                    st.success("✅ Base de datos optimizada exitosamente")
                except Exception as e:
                    st.error(f"❌ Error en optimización: {str(e)}")
        
        with col_clean2:
            st.markdown("##### Estadísticas de Espacio")
            
            try:
                # Calcular espacio utilizado
                conn = sqlite3.connect('data/database.db')
                
                # Obtener tamaño de tablas
                query = '''
                SELECT 
                    name as tabla,
                    (pgsize / (1024.0 * 1024.0)) as size_mb
                FROM dbstat
                WHERE name NOT LIKE 'sqlite_%'
                ORDER BY pgsize DESC
                '''
                
                try:
                    sizes = pd.read_sql_query(query, conn)
                    
                    if not sizes.empty:
                        # Mostrar gráfico de pastel
                        import plotly.express as px
                        
                        fig = px.pie(
                            sizes,
                            values='size_mb',
                            names='tabla',
                            title='Espacio por Tabla (MB)',
                            hole=0.3
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No se pudo obtener información de espacio")
                        
                except:
                    # Fallback simple
                    st.info("Información de espacio no disponible")
                
                conn.close()
                
            except Exception as e:
                st.error(f"❌ Error al obtener estadísticas: {str(e)}")
            
            st.markdown("---")
            st.markdown("##### Limpieza de Movimientos")
            
            dias_movimientos = st.number_input(
                "Mantener movimientos de los últimos (días):",
                min_value=90,
                max_value=730,
                value=365,
                step=30,
                help="Los movimientos más antiguos serán eliminados"
            )
            
            if st.button("🗑️ Limpiar Movimientos Antiguos", use_container_width=True):
                try:
                    conn = sqlite3.connect('data/database.db')
                    cursor = conn.cursor()
                    
                    # Calcular fecha límite
                    fecha_limite = (datetime.now() - timedelta(days=dias_movimientos)).strftime('%Y-%m-%d')
                    
                    # Contar registros a eliminar
                    cursor.execute(f"""
                    SELECT COUNT(*) FROM movimientos 
                    WHERE DATE(fecha_movimiento) < '{fecha_limite}'
                    """)
                    count = cursor.fetchone()[0]
                    
                    if count > 0:
                        # Eliminar
                        cursor.execute(f"""
                        DELETE FROM movimientos 
                        WHERE DATE(fecha_movimiento) < '{fecha_limite}'
                        """)
                        conn.commit()
                        st.success(f"✅ Se eliminaron {count} movimientos antiguos")
                    else:
                        st.info("ℹ️ No hay movimientos para eliminar")
                    
                    conn.close()
                    
                except Exception as e:
                    st.error(f"❌ Error en limpieza: {str(e)}")
    
    # ========== PESTAÑA 4: CONFIGURACIÓN ==========
    with tab4:
        st.subheader("⚙️ Configuración del Sistema")
        
        col_config1, col_config2 = st.columns(2)
        
        with col_config1:
            st.markdown("##### Configuración General")
            
            # Configuraciones simuladas (en una app real vendrían de un archivo de configuración)
            config = {
                'notificaciones_email': st.checkbox("Enviar notificaciones por email", value=False),
                'backup_automatico': st.checkbox("Backup automático diario", value=True),
                'alertas_porcentaje': st.slider("Porcentaje para alertas:", 70, 95, 80),
                'dias_retencion': st.number_input("Días de retención de datos:", 30, 730, 365)
            }
            
            if st.button("💾 Guardar Configuración", use_container_width=True):
                st.success("✅ Configuración guardada (simulación)")
            
            st.markdown("---")
            st.markdown("##### Información de Versión")
            
            st.write(f"**Versión de la aplicación:** 2.0.0")
            st.write(f"**Última actualización:** 2024")
            st.write(f"**Base de datos:** SQLite")
            st.write(f"**Framework:** Streamlit 1.28.1")
            
        with col_config2:
            st.markdown("##### Registro de Actividad")
            
            # Mostrar archivo de log si existe
            log_file = 'data/app.log'
            
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        lineas = f.readlines()[-20:]  # Últimas 20 líneas
                    
                    if lineas:
                        st.text_area("Últimas entradas del log:", 
                                   ''.join(lineas), 
                                   height=200,
                                   disabled=True)
                    else:
                        st.info("El archivo de log está vacío")
                        
                except Exception as e:
                    st.error(f"❌ Error al leer log: {str(e)}")
            else:
                st.info("No se encontró archivo de log")
            
            # Botón para limpiar log
            if st.button("🗑️ Limpiar Log", use_container_width=True):
                try:
                    open(log_file, 'w').close()
                    st.success("✅ Log limpiado")
                    st.rerun()
                except:
                    st.error("❌ Error al limpiar log")
            
            st.markdown("---")
            st.markdown("##### Restablecer Sistema")
            
            st.error("**ADVERTENCIA CRÍTICA:** Esta acción no se puede deshacer.")
            
            if st.button("🔄 Restablecer Datos de Prueba", use_container_width=True):
                confirm = st.checkbox("Confirmo que quiero restablecer los datos de prueba")
                
                if confirm and st.button("✅ CONFIRMAR RESTABLECIMIENTO", type="primary", use_container_width=True):
                    st.error("Función no implementada en esta versión")

# Para pruebas directas
if __name__ == "__main__":
    st.set_page_config(page_title="Mantenimiento", layout="wide")
    show()
