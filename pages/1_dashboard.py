"""
Dashboard principal - Versión Corregida
"""

import streamlit as st
import pandas as pd
from modules.database import (
    get_estadisticas_basicas,
    get_clientes_basicos,
    get_ocs_pendientes
)

def show():
    """Función principal del dashboard"""
    st.header("📊 Dashboard - Resumen General")
    
    try:
        # Cargar estadísticas básicas
        stats = get_estadisticas_basicas()
        
        # ========== MÉTRICAS PRINCIPALES ==========
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Clientes",
                value=stats['total_clientes'],
                delta=f"${stats['total_disponible']:,.0f} disponible"
            )
        
        with col2:
            st.metric(
                label="Cupo Total",
                value=f"${stats['total_cupo']:,.0f}",
                delta=f"${stats['total_saldo']:,.0f} saldo"
            )
        
        with col3:
            st.metric(
                label="Saldo Actual",
                value=f"${stats['total_saldo']:,.0f}",
                delta=f"${stats['total_vencido']:,.0f} vencido"
            )
        
        with col4:
            porcentaje_uso = (stats['total_saldo'] / stats['total_cupo'] * 100) if stats['total_cupo'] > 0 else 0
            st.metric(
                label="% Uso Total",
                value=f"{porcentaje_uso:.1f}%"
            )
        
        st.divider()
        
        # ========== TABLA DE CLIENTES ==========
        st.subheader("👥 Lista de Clientes")
        
        clientes = get_clientes_basicos()
        
        if not clientes.empty:
            # Formatear para mostrar
            df_display = clientes.copy()
            df_display['cupo_sugerido'] = df_display['cupo_sugerido'].apply(lambda x: f"${x:,.0f}")
            df_display['saldo_actual'] = df_display['saldo_actual'].apply(lambda x: f"${x:,.0f}")
            df_display['disponible'] = df_display['disponible'].apply(lambda x: f"${x:,.0f}")
            df_display['porcentaje_uso'] = df_display['porcentaje_uso'].apply(lambda x: f"{x}%")
            
            st.dataframe(
                df_display.rename(columns={
                    'nit': 'NIT',
                    'nombre': 'Cliente',
                    'cupo_sugerido': 'Cupo',
                    'saldo_actual': 'Saldo',
                    'disponible': 'Disponible',
                    'porcentaje_uso': '% Uso'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay clientes registrados")
        
        st.divider()
        
        # ========== OCs PENDIENTES ==========
        st.subheader("📄 Órdenes de Compra Pendientes")
        
        ocs_pendientes = get_ocs_pendientes()
        
        if not ocs_pendientes.empty:
            df_ocs = ocs_pendientes[['numero_oc', 'cliente_nombre', 'valor_total', 'valor_pendiente', 'estado']].copy()
            df_ocs['valor_total'] = df_ocs['valor_total'].apply(lambda x: f"${x:,.0f}")
            df_ocs['valor_pendiente'] = df_ocs['valor_pendiente'].apply(lambda x: f"${x:,.0f}")
            
            st.dataframe(
                df_ocs.rename(columns={
                    'numero_oc': 'N° OC',
                    'cliente_nombre': 'Cliente',
                    'valor_total': 'Valor Total',
                    'valor_pendiente': 'Pendiente',
                    'estado': 'Estado'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ No hay OCs pendientes")
            
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
        st.info("ℹ️ Asegúrate de que la base de datos esté inicializada correctamente.")

if __name__ == "__main__":
    st.set_page_config(page_title="Dashboard", layout="wide")
    show()
