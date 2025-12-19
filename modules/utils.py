import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

def format_currency(value):
    """Formatea un valor numérico como moneda"""
    if pd.isna(value) or value is None:
        return "$0"
    
    try:
        value = float(value)
        if value >= 1_000_000_000:
            return f"${value/1_000_000_000:,.1f}B".replace(',', '.')
        elif value >= 1_000_000:
            return f"${value/1_000_000:,.1f}M".replace(',', '.')
        else:
            return f"${value:,.0f}".replace(',', '.')
    except:
        return f"${value}"

def format_number(value, decimals=0):
    """Formatea un número con separadores de miles"""
    try:
        return f"{float(value):,.{decimals}f}".replace(',', '.')
    except:
        return str(value)

def get_risk_level(usage_percentage):
    """Determina el nivel de riesgo basado en porcentaje de uso"""
    if usage_percentage >= 95:
        return {"level": "CRÍTICO", "color": "#EF4444", "icon": "🔴"}
    elif usage_percentage >= 85:
        return {"level": "ALERTA", "color": "#F59E0B", "icon": "🟡"}
    else:
        return {"level": "NORMAL", "color": "#10B981", "icon": "🟢"}

def calculate_indicators(cliente_data):
    """Calcula indicadores para un cliente"""
    if cliente_data['cupo_sugerido'] == 0:
        return {
            'disponible': 0,
            'porcentaje_uso': 0,
            'risk_level': get_risk_level(0)
        }
    
    disponible = cliente_data['cupo_sugerido'] - cliente_data['total_cartera']
    porcentaje_uso = (cliente_data['total_cartera'] / cliente_data['cupo_sugerido']) * 100
    
    return {
        'disponible': disponible,
        'porcentaje_uso': porcentaje_uso,
        'risk_level': get_risk_level(porcentaje_uso)
    }

def validate_nit(nit):
    """Valida formato de NIT colombiano"""
    if not nit or not isinstance(nit, str):
        return False
    
    # Limpiar caracteres no numéricos
    clean_nit = ''.join(filter(str.isdigit, nit))
    
    # Validar longitud
    if len(clean_nit) < 8 or len(clean_nit) > 15:
        return False
    
    return True

def generate_oc_number():
    """Genera número de OC automático"""
    from modules.database import get_db_connection
    
    conn = get_db_connection()
    year = datetime.now().year
    
    # Obtener el último número de OC del año actual
    query = f"SELECT MAX(numero) FROM ocs WHERE numero LIKE 'OC-{year}-%'"
    result = pd.read_sql(query, conn)
    conn.close()
    
    last_number = result.iloc[0, 0]
    
    if last_number:
        try:
            # Extraer el número secuencial
            seq = int(last_number.split('-')[-1])
            new_seq = seq + 1
        except:
            new_seq = 1
    else:
        new_seq = 1
    
    return f"OC-{year}-{new_seq:03d}"

def get_date_range(days=30):
    """Obtiene rango de fechas"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def export_to_excel(dataframes, sheet_names, filename):
    """Exporta múltiples DataFrames a un archivo Excel"""
    import io
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for df, sheet_name in zip(dataframes, sheet_names):
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    output.seek(0)
    return output

def show_success_message(message):
    """Muestra mensaje de éxito"""
    st.success(f"✅ {message}")

def show_error_message(message):
    """Muestra mensaje de error"""
    st.error(f"❌ {message}")

def show_warning_message(message):
    """Muestra mensaje de advertencia"""
    st.warning(f"⚠️ {message}")

def show_info_message(message):
    """Muestra mensaje informativo"""
    st.info(f"ℹ️ {message}")

def create_download_button(data, filename, label="📥 Descargar"):
    """Crea botón de descarga para datos"""
    import base64
    
    if isinstance(data, pd.DataFrame):
        csv = data.to_csv(index=False).encode('utf-8')
    elif isinstance(data, bytes):
        csv = data
    else:
        csv = str(data).encode('utf-8')
    
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" style="text-decoration: none;">{label}</a>'
    st.markdown(href, unsafe_allow_html=True)
