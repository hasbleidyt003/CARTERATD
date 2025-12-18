"""
PÁGINA 2 - GESTIÓN DE CLIENTES
Tabla completa de clientes con gestión de cupos
"""

import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(
    page_title="Clientes - Tododrogas",
    page_icon="👥",
    layout="wide"
)

# Importar módulos
from modules.auth import check_authentication
from modules.database import get_clientes, actualizar_cupo_cliente
from modules.utils import format_currency, format_number, get_status_badge

# Verificar autenticación
user = check_authentication()

# ==================== ESTILOS CSS ====================

st.markdown("""
<style>
    /* ESTILOS PARA TARJETAS DE CLIENTES */
    .clients-container {
        padding: 1rem;
    }
    
    .client-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E7EB;
        transition: all 0.3s ease;
    }
    
    .client-card:hover {
        box-shadow: 0 4px 20px rgba(0, 102, 204, 0.1);
        border-color: #0066CC;
    }
    
    .client-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .client-name {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1A1A1A;
    }
    
    .client-nit {
        color: #666;
        font-size: 0.9rem;
    }
    
    .client-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-item {
        padding: 0.5rem;
        background: #F8F9FA;
        border-radius: 8px;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.25rem;
    }
    
    .metric-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1A1A1A;
    }
    
    .progress-bar {
        height: 8px;
        background: #E5E7EB;
        border-radius: 4px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.6s ease;
    }
    
    .client-actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    
    .filter-section {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid #E5E7EB;
    }
    
    /* ESTILOS PARA ESTADÍSTICAS */
    .stats-summary {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #0066CC, #004499);
        color: white;
        padding: 1rem;
        border-radius: 12px;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 800;
        margin: 0.5rem 0;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Botones estilizados */
    .rappi-button {
        background: linear-gradient(135deg, #0066CC, #004499);
        color: white;
        border: none;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        width: 100%;
    }
    
    .rappi-button:hover {
        background: linear-gradient(135deg, #004499, #003377);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
    }
    
    .rappi-button:disabled {
        background: #E5E7EB;
        color: #999;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }
    
    /* Alertas y badges */
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-normal {
        background: #E6F7FF;
        color: #0066CC;
        border: 1px solid #B3E0FF;
    }
    
    .status-alerta {
        background: #FFF7E6;
        color: #FF9500;
        border: 1px solid #FFE0B3;
    }
    
    .status-sobrepasado {
        background: #FFE6E6;
        color: #FF3B30;
        border: 1px solid #FFB3B3;
    }
    
    /* Estilos para la tabla */
    .rappi-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .rappi-table th {
        background: #F8F9FA;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        color: #1A1A1A;
        border-bottom: 2px solid #E5E7EB;
    }
    
    .rappi-table td {
        padding: 1rem;
        border-bottom: 1px solid #E5E7EB;
        background: white;
    }
    
    .rappi-table tr:hover td {
        background: #F8F9FA;
    }
</style>

<script>
// Funciones JavaScript para manejar los botones
function viewClient(nit) {
    alert('Ver detalle del cliente: ' + nit);
    // En una implementación real, esto redirigiría a una página de detalle
    // window.location.href = '/detalle_cliente?nit=' + nit;
}

function editCupo(nit) {
    alert('Editar cupo del cliente: ' + nit);
    // En Streamlit, esto debería activar un modal o cambiar de página
    // st.session_state['edit_cupo_nit'] = nit;
}

function viewOCs(nit) {
    alert('Ver OCs del cliente: ' + nit);
    // window.location.href = '/ocs_cliente?nit=' + nit;
}
</script>
""", unsafe_allow_html=True)

# ==================== FUNCIONES AUXILIARES ====================

def get_color_by_percentage(percentage):
    """Obtiene color basado en porcentaje de uso"""
    if percentage >= 100:
        return "#FF3B30"
    elif percentage >= 90:
        return "#FF9500"
    elif percentage >= 80:
        return "#FFCC00"
    elif percentage >= 50:
        return "#00B8A9"
    else:
        return "#0066CC"

def create_client_card(cliente):
    """Crea una tarjeta de cliente"""
    
    color = get_color_by_percentage(cliente['porcentaje_uso'])
    
    # Determinar el estado para el badge
    estado = ""
    if cliente['porcentaje_uso'] >= 100:
        estado = '<span class="status-badge status-sobrepasado">ALERTA CRÍTICA</span>'
    elif cliente['porcentaje_uso'] >= 90:
        estado = '<span class="status-badge status-alerta">ALERTA</span>'
    else:
        estado = '<span class="status-badge status-normal">NORMAL</span>'
    
    return f'''
    <div class="client-card">
        <div class="client-header">
            <div>
                <div class="client-name">{cliente['nombre']}</div>
                <div class="client-nit">NIT: {cliente['nit']}</div>
            </div>
            <div>
                {estado}
            </div>
        </div>
        
        <div class="client-metrics">
            <div class="metric-item">
                <div class="metric-label">Cupo Asignado</div>
                <div class="metric-value">{format_currency(cliente['cupo_sugerido'])}</div>
            </div>
            
            <div class="metric-item">
                <div class="metric-label">En Uso</div>
                <div class="metric-value">{format_currency(cliente['saldo_actual'])}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {min(cliente['porcentaje_uso'], 100)}%; background: {color};"></div>
                </div>
            </div>
            
            <div class="metric-item">
                <div class="metric-label">Disponible</div>
                <div class="metric-value">{format_currency(cliente['disponible'])}</div>
            </div>
            
            <div class="metric-item">
                <div class="metric-label">% Uso</div>
                <div class="metric-value">{cliente['porcentaje_uso']}%</div>
            </div>
        </div>
        
        <div class="client-actions">
            <button class="rappi-button" onclick="viewClient('{cliente['nit']}')" style="flex: 1;">📋 Ver Detalle</button>
            <button class="rappi-button" onclick="editCupo('{cliente['nit']}')" style="flex: 1;">✏️ Editar Cupo</button>
            <button class="rappi-button" onclick="viewOCs('{cliente['nit']}')" style="flex: 1;">📄 Ver OCs</button>
        </div>
    </div>
    '''

def create_stats_summary(clientes_df):
    """Crea resumen estadístico"""
    
    total_cupo = clientes_df['cupo_sugerido'].sum()
    total_en_uso = clientes_df['saldo_actual'].sum()
    total_disponible = clientes_df['disponible'].sum()
    porcentaje_promedio = clientes_df['porcentaje_uso'].mean()
    
    return f'''
    <div class="stats-summary">
        <div class="stat-card">
            <div class="stat-label">CUPO TOTAL</div>
            <div class="stat-value">{format_currency(total_cupo)}</div>
        </div>
        
        <div class="stat-card" style="background: linear-gradient(135deg, #00B8A9, #0088AA);">
            <div class="stat-label">EN USO</div>
            <div class="stat-value">{format_currency(total_en_uso)}</div>
        </div>
        
        <div class="stat-card" style="background: linear-gradient(135deg, #06D6A0, #0CB48C);">
            <div class="stat-label">DISPONIBLE</div>
            <div class="stat-value">{format_currency(total_disponible)}</div>
        </div>
        
        <div class="stat-card" style="background: linear-gradient(135deg, #FF9500, #FF7B00);">
            <div class="stat-label">USO PROMEDIO</div>
            <div class="stat-value">{porcentaje_promedio:.1f}%</div>
        </div>
    </div>
    '''

# ==================== PÁGINA PRINCIPAL ====================

def show_clients_page():
    """Muestra la página de gestión de clientes"""
    
    st.title("👥 GESTIÓN DE CLIENTES")
    st.markdown("Tabla completa de clientes con control de cupos")
    
    # Obtener datos
    with st.spinner("Cargando clientes..."):
        clientes_df = get_clientes()
    
    if clientes_df.empty:
        st.warning("No hay clientes registrados en el sistema.")
        return
    
    # ========== FILTROS Y BÚSQUEDA ==========
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search_term = st.text_input("🔍 Buscar cliente", placeholder="Nombre o NIT")
    
    with col2:
        estado_filter = st.selectbox(
            "Filtrar por estado",
            ["TODOS", "NORMAL", "ALERTA", "SOBREPASADO"]
        )
    
    with col3:
        sort_by = st.selectbox(
            "Ordenar por",
            ["Nombre (A-Z)", "Nombre (Z-A)", "% Uso (↑)", "% Uso (↓)", "Cupo (↑)", "Cupo (↓)"]
        )
    
    with col4:
        items_per_page = st.selectbox(
            "Clientes por página",
            [10, 25, 50, 100],
            index=0
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== RESUMEN ESTADÍSTICO ==========
    st.markdown(create_stats_summary(clientes_df), unsafe_allow_html=True)
    
    # ========== APLICAR FILTROS ==========
    filtered_df = clientes_df.copy()
    
    # Búsqueda por término
    if search_term:
        filtered_df = filtered_df[
            filtered_df['nombre'].str.contains(search_term, case=False) |
            filtered_df['nit'].str.contains(search_term, case=False)
        ]
    
    # Filtro por estado
    if estado_filter != "TODOS":
        if estado_filter == "NORMAL":
            filtered_df = filtered_df[filtered_df['porcentaje_uso'] < 90]
        elif estado_filter == "ALERTA":
            filtered_df = filtered_df[(filtered_df['porcentaje_uso'] >= 90) & (filtered_df['porcentaje_uso'] < 100)]
        elif estado_filter == "SOBREPASADO":
            filtered_df = filtered_df[filtered_df['porcentaje_uso'] >= 100]
    
    # Ordenar
    if sort_by == "Nombre (A-Z)":
        filtered_df = filtered_df.sort_values('nombre')
    elif sort_by == "Nombre (Z-A)":
        filtered_df = filtered_df.sort_values('nombre', ascending=False)
    elif sort_by == "% Uso (↑)":
        filtered_df = filtered_df.sort_values('porcentaje_uso')
    elif sort_by == "% Uso (↓)":
        filtered_df = filtered_df.sort_values('porcentaje_uso', ascending=False)
    elif sort_by == "Cupo (↑)":
        filtered_df = filtered_df.sort_values('cupo_sugerido')
    elif sort_by == "Cupo (↓)":
        filtered_df = filtered_df.sort_values('cupo_sugerido', ascending=False)
    
    # ========== PAGINACIÓN ==========
    total_clientes = len(filtered_df)
    total_pages = (total_clientes // items_per_page) + (1 if total_clientes % items_per_page > 0 else 0)
    
    if total_pages > 1:
        page_number = st.number_input(
            "Página",
            min_value=1,
            max_value=total_pages,
            value=1,
            step=1
        )
        
        start_idx = (page_number - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_df = filtered_df.iloc[start_idx:end_idx]
        
        st.caption(f"Mostrando clientes {start_idx + 1}-{min(end_idx, total_clientes)} de {total_clientes}")
    else:
        page_df = filtered_df
    
    # ========== TABLA DE CLIENTES ==========
    st.markdown(f"### 📋 CLIENTES ({len(filtered_df)})")
    
    # Opción de vista: Tarjetas o Tabla
    view_mode = st.radio(
        "Tipo de vista:",
        ["Tarjetas", "Tabla"],
        horizontal=True,
        key="view_mode_clients"
    )
    
    if view_mode == "Tarjetas":
        # Mostrar como tarjetas
        for _, cliente in page_df.iterrows():
            st.markdown(create_client_card(cliente), unsafe_allow_html=True)
    else:
        # Mostrar como tabla usando st.dataframe (mejor para Streamlit)
        display_df = page_df.copy()
        display_df['Cupo Asignado'] = display_df['cupo_sugerido'].apply(format_currency)
        display_df['En Uso'] = display_df['saldo_actual'].apply(format_currency)
        display_df['Disponible'] = display_df['disponible'].apply(format_currency)
        display_df['% Uso'] = display_df['porcentaje_uso'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(
            display_df[['nombre', 'nit', 'Cupo Asignado', 'En Uso', 'Disponible', '% Uso']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "nombre": st.column_config.TextColumn("Cliente", width="large"),
                "nit": st.column_config.TextColumn("NIT", width="medium"),
                "Cupo Asignado": st.column_config.TextColumn("Cupo", width="medium"),
                "En Uso": st.column_config.TextColumn("En Uso", width="medium"),
                "Disponible": st.column_config.TextColumn("Disponible", width="medium"),
                "% Uso": st.column_config.TextColumn("% Uso", width="small")
            }
        )
    
    # ========== ACCIONES MASIVAS ==========
    st.markdown("---")
    st.markdown("### 🚀 ACCIONES MASIVAS")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Exportar a Excel", use_container_width=True):
            try:
                # Crear archivo Excel
                output = pd.ExcelWriter('clientes_export.xlsx', engine='xlsxwriter')
                filtered_df.to_excel(output, index=False, sheet_name='Clientes')
                output.close()
                
                with open('clientes_export.xlsx', 'rb') as f:
                    st.download_button(
                        label="⬇️ Descargar Excel",
                        data=f,
                        file_name="clientes_tododrogas.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"❌ Error al exportar: {str(e)}")
    
    with col2:
        if st.button("🔄 Actualizar todos", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("📊 Ver análisis", use_container_width=True):
            st.switch_page("pages/4_reportes.py")

# ==================== EJECUCIÓN ====================

if __name__ == "__main__":
    show_clients_page()
