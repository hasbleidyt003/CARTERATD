"""
MÓDULO DE UTILIDADES - SISTEMA TODODROGAS
Funciones auxiliares y helpers
"""

import pandas as pd
from datetime import datetime, timedelta
import json

def format_currency(value, decimals=0):
    """
    Formatea un valor monetario con separadores de miles
    
    Args:
        value: Valor numérico a formatear
        decimals: Número de decimales a mostrar
        
    Returns:
        str: Valor formateado como moneda
    """
    if pd.isna(value):
        return "$0"
    
    try:
        if value >= 1e12:  # Billones
            return f"${value/1e12:,.{decimals}f}B"
        elif value >= 1e9:  # Miles de millones
            return f"${value/1e9:,.{decimals}f}MM"
        elif value >= 1e6:  # Millones
            return f"${value/1e6:,.{decimals}f}M"
        elif value >= 1e3:  # Miles
            return f"${value/1e3:,.{decimals}f}K"
        else:
            return f"${value:,.{decimals}f}"
    except:
        return f"${value:,.0f}"

def format_number(value, decimals=0):
    """
    Formatea un número con separadores de miles
    
    Args:
        value: Valor numérico a formatear
        decimals: Número de decimales a mostrar
        
    Returns:
        str: Número formateado
    """
    if pd.isna(value):
        return "0"
    
    try:
        return f"{value:,.{decimals}f}"
    except:
        return str(value)

def calculate_percentage(part, total, decimals=1):
    """
    Calcula el porcentaje de una parte sobre un total
    
    Args:
        part: Valor de la parte
        total: Valor total
        decimals: Decimales a mostrar
        
    Returns:
        float: Porcentaje calculado
    """
    if total == 0:
        return 0.0
    return round((part / total) * 100, decimals)

def validate_nit(nit):
    """
    Valida que un NIT tenga formato correcto
    
    Args:
        nit: Número de NIT a validar
        
    Returns:
        bool: True si es válido, False si no
    """
    if not nit or not isinstance(nit, str):
        return False
    
    # Remover espacios y puntos
    nit_clean = nit.replace(" ", "").replace(".", "").replace("-", "")
    
    # Debe contener solo números
    if not nit_clean.isdigit():
        return False
    
    # Longitud típica de NIT colombiano
    if len(nit_clean) < 8 or len(nit_clean) > 12:
        return False
    
    return True

def validate_oc_number(oc_number):
    """
    Valida que un número de OC tenga formato correcto
    
    Args:
        oc_number: Número de OC a validar
        
    Returns:
        bool: True si es válido, False si no
    """
    if not oc_number or not isinstance(oc_number, str):
        return False
    
    # Formato esperado: OC-YYYY-NNN
    parts = oc_number.split('-')
    
    if len(parts) != 3:
        return False
    
    if parts[0].upper() != 'OC':
        return False
    
    if not parts[1].isdigit() or len(parts[1]) != 4:
        return False
    
    if not parts[2].isdigit():
        return False
    
    # Verificar que el año sea razonable
    year = int(parts[1])
    current_year = datetime.now().year
    
    if year < 2020 or year > current_year + 1:
        return False
    
    return True

def get_color_by_percentage(percentage):
    """
    Devuelve un color basado en el porcentaje de uso
    
    Args:
        percentage: Porcentaje de uso
        
    Returns:
        str: Color en formato hexadecimal
    """
    if percentage >= 100:
        return "#FF3B30"  # Rojo - Sobrepasado
    elif percentage >= 90:
        return "#FF9500"  # Naranja - Crítico
    elif percentage >= 80:
        return "#FFCC00"  # Amarillo - Alerta
    elif percentage >= 50:
        return "#00B8A9"  # Turquesa - Moderado
    else:
        return "#0066CC"  # Azul - Normal

def get_status_badge(percentage):
    """
    Devuelve un badge HTML basado en el porcentaje
    
    Args:
        percentage: Porcentaje de uso
        
    Returns:
        str: HTML del badge
    """
    if percentage >= 100:
        color = "#FF3B30"
        text = "SOBREPASADO"
    elif percentage >= 90:
        color = "#FF9500"
        text = "CRÍTICO"
    elif percentage >= 80:
        color = "#FFCC00"
        text = "ALERTA"
    elif percentage >= 50:
        color = "#00B8A9"
        text = "MODERADO"
    else:
        color = "#0066CC"
        text = "NORMAL"
    
    return f'''
    <span style="
        background-color: {color};
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
    ">{text}</span>
    '''

def get_oc_status_badge(estado):
    """
    Devuelve un badge HTML para el estado de una OC
    
    Args:
        estado: Estado de la OC
        
    Returns:
        str: HTML del badge
    """
    estados = {
        'PENDIENTE': {'color': '#FFCC00', 'text': 'PENDIENTE'},
        'PARCIAL': {'color': '#FF9500', 'text': 'PARCIAL'},
        'AUTORIZADA': {'color': '#00B8A9', 'text': 'AUTORIZADA'},
        'CANCELADA': {'color': '#FF3B30', 'text': 'CANCELADA'}
    }
    
    info = estados.get(estado, {'color': '#666666', 'text': estado})
    
    return f'''
    <span style="
        background-color: {info['color']};
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
    ">{info['text']}</span>
    '''

def create_data_card(title, value, change=None, icon=None):
    """
    Crea una tarjeta de datos estilo Rappi
    
    Args:
        title: Título de la tarjeta
        value: Valor principal
        change: Cambio porcentual (opcional)
        icon: Ícono a mostrar (opcional)
        
    Returns:
        str: HTML de la tarjeta
    """
    change_html = ""
    if change is not None:
        change_class = "positive" if change >= 0 else "negative"
        change_symbol = "↗" if change >= 0 else "↘"
        change_html = f'''
        <div class="metric-change {change_class}">
            {change_symbol} {abs(change):.1f}%
        </div>
        '''
    
    icon_html = f'<div class="metric-icon">{icon}</div>' if icon else ""
    
    return f'''
    <div class="rappi-card">
        <div class="metric-header">
            {icon_html}
            <div class="metric-title">{title}</div>
        </div>
        <div class="metric-value">{value}</div>
        {change_html}
    </div>
    '''

def generate_chart_config():
    """
    Genera configuración para gráficos Plotly con estilo Rappi
    
    Returns:
        dict: Configuración de gráficos
    """
    return {
        'modebar': {
            'orientation': 'h',
            'bgcolor': 'rgba(255, 255, 255, 0.8)',
        },
        'displayModeBar': True,
        'displaylogo': False,
        'responsive': True
    }

def get_date_range_options():
    """
    Devuelve opciones de rangos de fecha predefinidos
    
    Returns:
        list: Lista de opciones de fecha
    """
    today = datetime.now()
    
    return [
        {"label": "Últimos 7 días", "value": 7},
        {"label": "Últimos 30 días", "value": 30},
        {"label": "Últimos 90 días", "value": 90},
        {"label": "Este mes", "value": "month"},
        {"label": "Este año", "value": "year"}
    ]

def safe_divide(numerator, denominator):
    """
    División segura que evita división por cero
    
    Args:
        numerator: Numerador
        denominator: Denominador
        
    Returns:
        float: Resultado de la división o 0
    """
    if denominator == 0:
        return 0.0
    return numerator / denominator
