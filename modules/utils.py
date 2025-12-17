"""
Módulo de utilidades generales para el Sistema de Cartera TD
Funciones auxiliares y helpers
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import json
import unicodedata
import hashlib

# ============================================================================
# FUNCIONES DE VALIDACIÓN
# ============================================================================

def validar_nit(nit):
    """Valida formato de NIT colombiano"""
    if not nit or not isinstance(nit, str):
        return False
    
    # Limpiar caracteres no numéricos
    nit_limpio = re.sub(r'[^0-9]', '', nit)
    
    # Validar longitud (entre 9 y 15 dígitos para NIT colombiano)
    if len(nit_limpio) < 9 or len(nit_limpio) > 15:
        return False
    
    return True

def validar_email(email):
    """Valida formato de email básico"""
    if not email:
        return True  # Email opcional
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validar_telefono(telefono):
    """Valida formato de teléfono colombiano"""
    if not telefono:
        return True  # Teléfono opcional
    
    # Limpiar caracteres no numéricos
    telefono_limpio = re.sub(r'[^0-9]', '', telefono)
    
    # Validar longitud (10 dígitos para celular colombiano)
    if len(telefono_limpio) != 10:
        return False
    
    # Validar que empiece con 3
    if not telefono_limpio.startswith('3'):
        return False
    
    return True

def validar_valor_monetario(valor):
    """Valida que sea un valor monetario válido"""
    try:
        valor_num = float(valor)
        return valor_num >= 0
    except (ValueError, TypeError):
        return False

# ============================================================================
# FUNCIONES DE FORMATEO
# ============================================================================

def formato_monetario(valor, simbolo="$", decimales=0):
    """Formatea un valor como moneda"""
    if pd.isna(valor):
        return f"{simbolo}0"
    
    try:
        valor_num = float(valor)
        if decimales > 0:
            formato = f",.{decimales}f"
        else:
            formato = ",.0f"
        
        return f"{simbolo}{valor_num:{formato}}"
    except (ValueError, TypeError):
        return f"{simbolo}0"

def formato_porcentaje(valor, decimales=1):
    """Formatea un valor como porcentaje"""
    if pd.isna(valor):
        return "0%"
    
    try:
        valor_num = float(valor)
        return f"{valor_num:.{decimales}f}%"
    except (ValueError, TypeError):
        return "0%"

def formato_fecha(fecha, formato="%d/%m/%Y"):
    """Formatea una fecha"""
    if pd.isna(fecha):
        return ""
    
    try:
        if isinstance(fecha, str):
            # Intentar parsear si es string
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M"]:
                try:
                    fecha_dt = datetime.strptime(fecha, fmt)
                    return fecha_dt.strftime(formato)
                except:
                    continue
        
        elif isinstance(fecha, datetime):
            return fecha.strftime(formato)
        
        elif isinstance(fecha, pd.Timestamp):
            return fecha.strftime(formato)
        
        return str(fecha)
    except:
        return str(fecha)

def formato_fecha_hora(fecha):
    """Formatea una fecha con hora"""
    return formato_fecha(fecha, "%d/%m/%Y %H:%M")

# ============================================================================
# FUNCIONES DE CÁLCULO
# ============================================================================

def calcular_porcentaje(parte, total):
    """Calcula porcentaje de parte sobre total"""
    if total == 0:
        return 0
    
    try:
        return (parte / total) * 100
    except:
        return 0

def calcular_dias_entre(fecha_inicio, fecha_fin):
    """Calcula días entre dos fechas"""
    try:
        if isinstance(fecha_inicio, str):
            fecha_inicio = pd.to_datetime(fecha_inicio)
        if isinstance(fecha_fin, str):
            fecha_fin = pd.to_datetime(fecha_fin)
        
        if pd.isna(fecha_inicio) or pd.isna(fecha_fin):
            return None
        
        diferencia = fecha_fin - fecha_inicio
        return diferencia.days
    except:
        return None

def calcular_edad_financiera(fecha_vencimiento):
    """Calcula la edad financiera de una factura"""
    try:
        if pd.isna(fecha_vencimiento):
            return None
        
        hoy = datetime.now()
        
        if isinstance(fecha_vencimiento, str):
            fecha_vencimiento = pd.to_datetime(fecha_vencimiento)
        
        dias = (hoy - fecha_vencimiento).days
        
        if dias < 0:
            return "Por vencer"
        elif dias <= 30:
            return f"{dias} días"
        elif dias <= 60:
            return "31-60 días"
        elif dias <= 90:
            return "61-90 días"
        else:
            return f"+90 días ({dias} días)"
            
    except:
        return None

# ============================================================================
# FUNCIONES DE DATAFRAME
# ============================================================================

def filtrar_dataframe(df, filtros):
    """Filtra un DataFrame basado en múltiples criterios"""
    if df.empty:
        return df
    
    df_filtrado = df.copy()
    
    for columna, valor in filtros.items():
        if columna in df_filtrado.columns and valor not in [None, "", "Todos"]:
            if pd.api.types.is_numeric_dtype(df_filtrado[columna]):
                # Para filtros numéricos
                try:
                    df_filtrado = df_filtrado[df_filtrado[columna] == float(valor)]
                except:
                    pass
            else:
                # Para filtros de texto
                df_filtrado = df_filtrado[df_filtrado[columna].astype(str).str.contains(str(valor), case=False, na=False)]
    
    return df_filtrado

def agrupar_por_periodo(df, columna_fecha, periodo='M'):
    """Agrupa datos por periodo temporal"""
    if df.empty or columna_fecha not in df.columns:
        return pd.DataFrame()
    
    try:
        df_copy = df.copy()
        df_copy[columna_fecha] = pd.to_datetime(df_copy[columna_fecha])
        
        if periodo == 'D':
            df_copy['periodo'] = df_copy[columna_fecha].dt.date
        elif periodo == 'W':
            df_copy['periodo'] = df_copy[columna_fecha].dt.to_period('W').dt.start_time
        elif periodo == 'M':
            df_copy['periodo'] = df_copy[columna_fecha].dt.to_period('M').dt.start_time
        elif periodo == 'Q':
            df_copy['periodo'] = df_copy[columna_fecha].dt.to_period('Q').dt.start_time
        elif periodo == 'Y':
            df_copy['periodo'] = df_copy[columna_fecha].dt.to_period('Y').dt.start_time
        else:
            df_copy['periodo'] = df_copy[columna_fecha].dt.date
        
        return df_copy.groupby('periodo')
    except:
        return pd.DataFrame()

def calcular_estadisticas_df(df, columnas_numericas=None):
    """Calcula estadísticas básicas de un DataFrame"""
    if df.empty:
        return {}
    
    stats = {
        'filas': len(df),
        'columnas': len(df.columns),
        'nulos': df.isnull().sum().sum(),
        'duplicados': df.duplicated().sum()
    }
    
    if columnas_numericas is None:
        columnas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    
    for col in columnas_numericas:
        if col in df.columns:
            stats[f'{col}_min'] = df[col].min()
            stats[f'{col}_max'] = df[col].max()
            stats[f'{col}_mean'] = df[col].mean()
            stats[f'{col}_sum'] = df[col].sum()
    
    return stats

# ============================================================================
# FUNCIONES DE STRING
# ============================================================================

def normalizar_texto(texto):
    """Normaliza texto: elimina acentos, convierte a mayúsculas"""
    if not texto:
        return ""
    
    # Convertir a string
    texto_str = str(texto)
    
    # Eliminar acentos
    texto_sin_acentos = ''.join(
        c for c in unicodedata.normalize('NFD', texto_str)
        if unicodedata.category(c) != 'Mn'
    )
    
    # Convertir a mayúsculas y eliminar espacios extra
    texto_normalizado = texto_sin_acentos.upper().strip()
    
    # Reemplazar múltiples espacios por uno solo
    texto_normalizado = re.sub(r'\s+', ' ', texto_normalizado)
    
    return texto_normalizado

def extraer_numeros(texto):
    """Extrae todos los números de un texto"""
    if not texto:
        return []
    
    return re.findall(r'\d+', str(texto))

def truncar_texto(texto, longitud=100, sufijo="..."):
    """Trunca un texto a una longitud máxima"""
    if not texto:
        return ""
    
    texto_str = str(texto)
    if len(texto_str) <= longitud:
        return texto_str
    
    return texto_str[:longitud] + sufijo

# ============================================================================
# FUNCIONES DE ARCHIVO
# ============================================================================

def calcular_hash_archivo(ruta_archivo):
    """Calcula el hash SHA-256 de un archivo"""
    try:
        hasher = hashlib.sha256()
        with open(ruta_archivo, 'rb') as f:
            for bloque in iter(lambda: f.read(4096), b''):
                hasher.update(bloque)
        return hasher.hexdigest()
    except:
        return None

def leer_json_safe(ruta_archivo, default={}):
    """Lee un archivo JSON de forma segura"""
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default

def guardar_json_safe(ruta_archivo, data):
    """Guarda datos en un archivo JSON de forma segura"""
    try:
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

# ============================================================================
# FUNCIONES DE LOGGING
# ============================================================================

class Logger:
    """Logger simple para la aplicación"""
    
    def __init__(self, archivo_log='data/app.log'):
        self.archivo_log = archivo_log
        self.crear_directorio()
    
    def crear_directorio(self):
        """Crea el directorio para logs si no existe"""
        import os
        os.makedirs(os.path.dirname(self.archivo_log), exist_ok=True)
    
    def log(self, nivel, mensaje):
        """Registra un mensaje en el log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        linea = f"[{timestamp}] [{nivel}] {mensaje}\n"
        
        try:
            with open(self.archivo_log, 'a', encoding='utf-8') as f:
                f.write(linea)
        except:
            pass
    
    def info(self, mensaje):
        """Registra un mensaje de información"""
        self.log('INFO', mensaje)
    
    def warning(self, mensaje):
        """Registra un mensaje de advertencia"""
        self.log('WARNING', mensaje)
    
    def error(self, mensaje):
        """Registra un mensaje de error"""
        self.log('ERROR', mensaje)
    
    def debug(self, mensaje):
        """Registra un mensaje de depuración"""
        self.log('DEBUG', mensaje)

# Instancia global del logger
logger = Logger()

# ============================================================================
# FUNCIONES DE FECHAS ESPECIALES
# ============================================================================

def es_fin_de_semana(fecha):
    """Determina si una fecha es fin de semana"""
    try:
        if isinstance(fecha, str):
            fecha = pd.to_datetime(fecha)
        
        return fecha.weekday() >= 5  # 5=Sábado, 6=Domingo
    except:
        return False

def es_dia_habil(fecha):
    """Determina si una fecha es día hábil (lunes a viernes)"""
    return not es_fin_de_semana(fecha)

def sumar_dias_habiles(fecha, dias):
    """Suma días hábiles a una fecha"""
    try:
        if isinstance(fecha, str):
            fecha = pd.to_datetime(fecha)
        
        fecha_resultado = fecha
        dias_sumados = 0
        
        while dias_sumados < dias:
            fecha_resultado += timedelta(days=1)
            if es_dia_habil(fecha_resultado):
                dias_sumados += 1
        
        return fecha_resultado
    except:
        return fecha

# ============================================================================
# FUNCIONES DE VALIDACIÓN DE DATOS
# ============================================================================

def detectar_outliers_serie(serie, umbral=3):
    """Detecta outliers en una serie numérica"""
    if serie.empty:
        return pd.Series([False] * len(serie))
    
    # Calcular z-score
    z_score = np.abs((serie - serie.mean()) / serie.std())
    
    # Identificar outliers
    outliers = z_score > umbral
    
    return outliers

def limpiar_nulos_df(df, estrategia='drop', valor=0):
    """Limpia valores nulos de un DataFrame"""
    if df.empty:
        return df
    
    df_limpio = df.copy()
    
    if estrategia == 'drop':
        df_limpio = df_limpio.dropna()
    elif estrategia == 'fill':
        df_limpio = df_limpio.fillna(valor)
    elif estrategia == 'ffill':
        df_limpio = df_limpio.ffill()
    elif estrategia == 'bfill':
        df_limpio = df_limpio.bfill()
    elif estrategia == 'mean':
        for col in df_limpio.select_dtypes(include=[np.number]).columns:
            df_limpio[col] = df_limpio[col].fillna(df_limpio[col].mean())
    
    return df_limpio

# ============================================================================
# FUNCIONES DE CONVERSIÓN
# ============================================================================

def dict_a_dataframe(datos_dict):
    """Convierte un diccionario anidado a DataFrame"""
    try:
        # Aplanar diccionario
        datos_aplanados = []
        
        for clave, valor in datos_dict.items():
            if isinstance(valor, dict):
                valor['id'] = clave
                datos_aplanados.append(valor)
            else:
                datos_aplanados.append({'id': clave, 'valor': valor})
        
        return pd.DataFrame(datos_aplanados)
    except:
        return pd.DataFrame()

def dataframe_a_dict(df, clave='id'):
    """Convierte un DataFrame a diccionario"""
    if df.empty or clave not in df.columns:
        return {}
    
    try:
        return df.set_index(clave).to_dict('index')
    except:
        return {}
