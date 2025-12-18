"""
Utilidades Avanzadas para Sistema de Cupos TD
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import json
import hashlib
import uuid
from typing import Dict, List, Optional, Any

# ============================================================================
# VALIDACIONES AVANZADAS
# ============================================================================

class Validador:
    """Clase para validaciones avanzadas del sistema"""
    
    @staticmethod
    def validar_nit(nit: str) -> bool:
        """Valida formato de NIT colombiano con algoritmo de verificación"""
        if not nit or not isinstance(nit, str):
            return False
        
        # Limpiar caracteres no numéricos
        nit_limpio = re.sub(r'[^0-9]', '', nit)
        
        # Validar longitud
        if len(nit_limpio) < 9 or len(nit_limpio) > 15:
            return False
        
        # Algoritmo de verificación de dígito de control (simplificado)
        try:
            nit_sin_dv = nit_limpio[:-1]
            digito_verificacion = int(nit_limpio[-1])
            
            # Calcular dígito de verificación
            factores = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
            suma = 0
            
            for i, digito in enumerate(reversed(nit_sin_dv)):
                suma += int(digito) * factores[i]
            
            residuo = suma % 11
            if residuo < 2:
                dv_calculado = residuo
            else:
                dv_calculado = 11 - residuo
            
            return dv_calculado == digito_verificacion
            
        except:
            return True  # Si falla el cálculo, al menos validar formato básico
    
    @staticmethod
    def validar_valor_monetario(valor: Any) -> bool:
        """Valida que sea un valor monetario válido y razonable"""
        try:
            valor_num = float(valor)
            return valor_num >= 0 and valor_num <= 1000000000000  # Hasta 1 billón
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validar_fecha(fecha_str: str, formato: str = '%Y-%m-%d') -> bool:
        """Valida formato de fecha"""
        try:
            datetime.strptime(fecha_str, formato)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida formato de email"""
        if not email:
            return True
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

# ============================================================================
# FORMATEADORES PROFESIONALES
# ============================================================================

class Formateador:
    """Clase para formateo profesional de datos"""
    
    @staticmethod
    def formato_monetario(valor: float, moneda: str = '$', decimales: int = 0) -> str:
        """Formatea valores monetarios de forma profesional"""
        if pd.isna(valor) or valor is None:
            return f"{moneda}0"
        
        try:
            valor_num = float(valor)
            if decimales > 0:
                formato = f",.{decimales}f"
            else:
                formato = ",.0f"
            
            return f"{moneda}{valor_num:{formato}}"
        except:
            return f"{moneda}0"
    
    @staticmethod
    def formato_porcentaje(valor: float, decimales: int = 2) -> str:
        """Formatea porcentajes"""
        if pd.isna(valor) or valor is None:
            return "0.00%"
        
        try:
            return f"{valor:.{decimales}f}%"
        except:
            return "0.00%"
    
    @staticmethod
    def formato_fecha(fecha: Any, formato_salida: str = '%d/%m/%Y') -> str:
        """Formatea fechas de manera flexible"""
        if pd.isna(fecha) or fecha is None:
            return ""
        
        try:
            if isinstance(fecha, str):
                # Intentar parsear diferentes formatos
                formatos_entrada = [
                    '%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S',
                    '%d/%m/%Y %H:%M', '%Y%m%d', '%d%m%Y'
                ]
                
                for fmt in formatos_entrada:
                    try:
                        fecha_dt = datetime.strptime(fecha, fmt)
                        return fecha_dt.strftime(formato_salida)
                    except:
                        continue
            
            elif isinstance(fecha, datetime):
                return fecha.strftime(formato_salida)
            
            elif isinstance(fecha, pd.Timestamp):
                return fecha.strftime(formato_salida)
            
            return str(fecha)
            
        except:
            return str(fecha)
    
    @staticmethod
    def formato_numero_oc(numero: str) -> str:
        """Formatea número de OC para mejor visualización"""
        if not numero:
            return ""
        
        # Eliminar espacios y convertir a mayúsculas
        numero_limpio = str(numero).strip().upper()
        
        # Agregar prefijo OC- si no lo tiene
        if not numero_limpio.startswith('OC-'):
            numero_limpio = f"OC-{numero_limpio}"
        
        return numero_limpio

# ============================================================================
# CALCULADORAS AVANZADAS
# ============================================================================

class CalculadoraFinanciera:
    """Clase para cálculos financieros avanzados"""
    
    @staticmethod
    def calcular_indicadores_cupo(total_cartera: float, cupo_sugerido: float) -> Dict:
        """Calcula indicadores financieros para un cupo"""
        if cupo_sugerido <= 0:
            return {
                'disponible': 0,
                'porcentaje_uso': 0,
                'estado': 'SIN_CUPO',
                'margen_seguridad': 0
            }
        
        disponible = cupo_sugerido - total_cartera
        porcentaje_uso = (total_cartera / cupo_sugerido) * 100
        margen_seguridad = (disponible / cupo_sugerido) * 100 if cupo_sugerido > 0 else 0
        
        # Determinar estado
        if total_cartera > cupo_sugerido:
            estado = 'SOBREPASADO'
        elif porcentaje_uso >= 90:
            estado = 'ALTO'
        elif porcentaje_uso >= 70:
            estado = 'MEDIO'
        else:
            estado = 'NORMAL'
        
        return {
            'disponible': disponible,
            'porcentaje_uso': round(porcentaje_uso, 2),
            'estado': estado,
            'margen_seguridad': round(margen_seguridad, 2),
            'capacidad_endeudamiento': round(disponible * 0.8, 2)  # 80% del disponible como recomendación
        }
    
    @staticmethod
    def proyectar_cupo_30_dias(total_cartera: float, tendencia_diaria: float) -> Dict:
        """Proyecta el comportamiento del cupo para los próximos 30 días"""
        proyecciones = []
        fecha_actual = datetime.now()
        
        for i in range(30):
            fecha = fecha_actual + timedelta(days=i)
            cartera_proyectada = total_cartera + (tendencia_diaria * i)
            
            proyecciones.append({
                'fecha': fecha.strftime('%Y-%m-%d'),
                'cartera_proyectada': cartera_proyectada,
                'dias_hasta_90': max(0, 90 - ((cartera_proyectada / total_cartera) * 100) if total_cartera > 0 else 0)
            })
        
        return {
            'proyecciones': proyecciones,
            'cartera_final_30d': total_cartera + (tendencia_diaria * 30),
            'tasa_crecimiento_diaria': tendencia_diaria
        }
    
    @staticmethod
    def calcular_rotacion_cartera(movimientos: List[Dict], periodo_dias: int = 30) -> float:
        """Calcula la rotación de cartera"""
        if not movimientos or periodo_dias <= 0:
            return 0
        
        # Filtrar movimientos del período
        fecha_limite = datetime.now() - timedelta(days=periodo_dias)
        movimientos_periodo = [
            m for m in movimientos 
            if datetime.strptime(m.get('fecha', ''), '%Y-%m-%d') >= fecha_limite
            if m.get('tipo') in ['PAGO', 'ABONO']
        ]
        
        total_movimientos = sum(m.get('valor', 0) for m in movimientos_periodo)
        
        # Suponer cartera promedio (simplificado)
        cartera_promedio = sum(m.get('valor', 0) for m in movimientos) / len(movimientos) if movimientos else 0
        
        if cartera_promedio > 0:
            rotacion = total_movimientos / cartera_promedio
            return round(rotacion, 2)
        
        return 0

# ============================================================================
# GENERADORES DE CÓDIGOS Y IDENTIFICADORES
# ============================================================================

class Generador:
    """Clase para generar códigos e identificadores únicos"""
    
    @staticmethod
    def generar_numero_oc(prefix: str = 'OC') -> str:
        """Genera número de OC único"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_part = str(uuid.uuid4().int)[:6]
        return f"{prefix}-{timestamp}-{random_part}"
    
    @staticmethod
    def generar_referencia_pago(cliente_nit: str) -> str:
        """Genera referencia de pago única"""
        fecha = datetime.now().strftime('%Y%m%d')
        hash_obj = hashlib.md5(f"{cliente_nit}{fecha}".encode())
        hash_hex = hash_obj.hexdigest()[:8].upper()
        return f"PAGO-{fecha}-{hash_hex}"
    
    @staticmethod
    def generar_codigo_seguimiento() -> str:
        """Genera código de seguimiento único"""
        return f"SEG-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

# ============================================================================
# MANIPULACIÓN DE DATAFRAMES AVANZADA
# ============================================================================

class DataFrameManager:
    """Clase para manipulación avanzada de DataFrames"""
    
    @staticmethod
    def aplicar_filtros_avanzados(df: pd.DataFrame, filtros: Dict) -> pd.DataFrame:
        """Aplica filtros avanzados a un DataFrame"""
        if df.empty:
            return df
        
        df_filtrado = df.copy()
        
        for columna, valor in filtros.items():
            if columna in df_filtrado.columns and valor not in [None, "", "Todos", "TODOS"]:
                # Filtros especiales
                if columna.endswith('_min'):
                    col_base = columna.replace('_min', '')
                    if col_base in df_filtrado.columns:
                        df_filtrado = df_filtrado[df_filtrado[col_base] >= float(valor)]
                
                elif columna.endswith('_max'):
                    col_base = columna.replace('_max', '')
                    if col_base in df_filtrado.columns:
                        df_filtrado = df_filtrado[df_filtrado[col_base] <= float(valor)]
                
                elif columna.endswith('_range'):
                    col_base = columna.replace('_range', '')
                    if col_base in df_filtrado.columns and isinstance(valor, (list, tuple)) and len(valor) == 2:
                        df_filtrado = df_filtrado[
                            (df_filtrado[col_base] >= float(valor[0])) & 
                            (df_filtrado[col_base] <= float(valor[1]))
                        ]
                
                # Filtro de texto con múltiples opciones
                elif isinstance(valor, list):
                    df_filtrado = df_filtrado[df_filtrado[columna].isin(valor)]
                
                # Filtro de texto simple
                elif pd.api.types.is_numeric_dtype(df_filtrado[columna]):
                    try:
                        df_filtrado = df_filtrado[df_filtrado[columna] == float(valor)]
                    except:
                        pass
                else:
                    df_filtrado = df_filtrado[
                        df_filtrado[columna].astype(str).str.contains(str(valor), case=False, na=False)
                    ]
        
        return df_filtrado
    
    @staticmethod
    def calcular_estadisticas_detalladas(df: pd.DataFrame, columnas_numericas: List[str] = None) -> Dict:
        """Calcula estadísticas detalladas de un DataFrame"""
        if df.empty:
            return {}
        
        stats = {
            'registros': len(df),
            'columnas': len(df.columns),
            'nulos_totales': df.isnull().sum().sum(),
            'registros_duplicados': df.duplicated().sum(),
            'memoria_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
        }
        
        if columnas_numericas is None:
            columnas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in columnas_numericas:
            if col in df.columns:
                col_stats = {
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'media': float(df[col].mean()),
                    'mediana': float(df[col].median()),
                    'std': float(df[col].std()),
                    'suma': float(df[col].sum()),
                    'nulos': int(df[col].isnull().sum()),
                    'ceros': int((df[col] == 0).sum())
                }
                stats[col] = col_stats
        
        # Estadísticas de columnas categóricas
        columnas_categoricas = df.select_dtypes(include=['object']).columns.tolist()
        for col in columnas_categoricas[:5]:  # Limitar a 5 columnas
            if col in df.columns:
                unique_vals = df[col].nunique()
                top_val = df[col].mode().iloc[0] if not df[col].mode().empty else None
                stats[f'{col}_categ'] = {
                    'valores_unicos': int(unique_vals),
                    'valor_mas_comun': str(top_val),
                    'nulos': int(df[col].isnull().sum())
                }
        
        return stats
    
    @staticmethod
    def exportar_dataframe(df: pd.DataFrame, formato: str = 'excel', **kwargs) -> bytes:
        """Exporta DataFrame a diferentes formatos"""
        if df.empty:
            return b''
        
        try:
            if formato == 'excel':
                output = pd.ExcelWriter('temp.xlsx', engine='openpyxl')
                df.to_excel(output, index=False, **kwargs)
                output.close()
                
                with open('temp.xlsx', 'rb') as f:
                    data = f.read()
                
                import os
                os.remove('temp.xlsx')
                return data
            
            elif formato == 'csv':
                return df.to_csv(index=False, **kwargs).encode('utf-8')
            
            elif formato == 'json':
                return df.to_json(orient='records', **kwargs).encode('utf-8')
            
            else:
                raise ValueError(f"Formato no soportado: {formato}")
                
        except Exception as e:
            print(f"❌ Error exportando DataFrame: {e}")
            return b''

# ============================================================================
# FUNCIONES DE SEGURIDAD Y HASHING
# ============================================================================

class Security:
    """Clase para funciones de seguridad"""
    
    @staticmethod
    def generar_hash(data: str, algoritmo: str = 'sha256') -> str:
        """Genera hash de datos sensibles"""
        hash_obj = hashlib.new(algoritmo)
        hash_obj.update(data.encode('utf-8'))
        return hash_obj.hexdigest()
    
    @staticmethod
    def enmascarar_datos_sensibles(texto: str, mostrar_primero: int = 4, mostrar_ultimo: int = 4) -> str:
        """Enmascara datos sensibles como NITs, tarjetas, etc."""
        if not texto or len(texto) < (mostrar_primero + mostrar_ultimo):
            return texto
        
        parte_visible = texto[:mostrar_primero] + '*' * (len(texto) - mostrar_primero - mostrar_ultimo) + texto[-mostrar_ultimo:]
        return parte_visible
    
    @staticmethod
    def validar_fuerza_contrasena(contrasena: str) -> Dict:
        """Valida la fuerza de una contraseña"""
        puntaje = 0
        criterios = []
        
        # Longitud mínima
        if len(contrasena) >= 8:
            puntaje += 1
            criterios.append("✓ Longitud mínima 8 caracteres")
        else:
            criterios.append("✗ Longitud mínima 8 caracteres")
        
        # Contiene mayúsculas
        if re.search(r'[A-Z]', contrasena):
            puntaje += 1
            criterios.append("✓ Contiene mayúsculas")
        else:
            criterios.append("✗ Contiene mayúsculas")
        
        # Contiene minúsculas
        if re.search(r'[a-z]', contrasena):
            puntaje += 1
            criterios.append("✓ Contiene minúsculas")
        else:
            criterios.append("✗ Contiene minúsculas")
        
        # Contiene números
        if re.search(r'\d', contrasena):
            puntaje += 1
            criterios.append("✓ Contiene números")
        else:
            criterios.append("✗ Contiene números")
        
        # Contiene caracteres especiales
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', contrasena):
            puntaje += 1
            criterios.append("✓ Contiene caracteres especiales")
        else:
            criterios.append("✗ Contiene caracteres especiales")
        
        # Determinar nivel de seguridad
        if puntaje >= 4:
            nivel = "FUERTE"
            color = "green"
        elif puntaje >= 3:
            nivel = "MEDIA"
            color = "orange"
        else:
            nivel = "DÉBIL"
            color = "red"
        
        return {
            'puntaje': puntaje,
            'nivel': nivel,
            'color': color,
            'criterios': criterios,
            'fortaleza': f"{puntaje}/5"
        }

# ============================================================================
# FUNCIONES DE FECHA Y TIEMPO AVANZADAS
# ============================================================================

class DateUtils:
    """Utilidades avanzadas para fechas"""
    
    @staticmethod
    def obtener_rango_fechas(periodo: str = 'mes_actual') -> Dict:
        """Obtiene rangos de fechas predefinidos"""
        hoy = datetime.now()
        
        rangos = {
            'hoy': {
                'inicio': hoy.strftime('%Y-%m-%d'),
                'fin': hoy.strftime('%Y-%m-%d'),
                'nombre': 'Hoy'
            },
            'ayer': {
                'inicio': (hoy - timedelta(days=1)).strftime('%Y-%m-%d'),
                'fin': (hoy - timedelta(days=1)).strftime('%Y-%m-%d'),
                'nombre': 'Ayer'
            },
            'semana_actual': {
                'inicio': (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d'),
                'fin': hoy.strftime('%Y-%m-%d'),
                'nombre': 'Semana Actual'
            },
            'mes_actual': {
                'inicio': hoy.replace(day=1).strftime('%Y-%m-%d'),
                'fin': hoy.strftime('%Y-%m-%d'),
                'nombre': 'Mes Actual'
            },
            'mes_anterior': {
                'inicio': (hoy.replace(day=1) - timedelta(days=1)).replace(day=1).strftime('%Y-%m-%d'),
                'fin': (hoy.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d'),
                'nombre': 'Mes Anterior'
            },
            'ultimos_7_dias': {
                'inicio': (hoy - timedelta(days=7)).strftime('%Y-%m-%d'),
                'fin': hoy.strftime('%Y-%m-%d'),
                'nombre': 'Últimos 7 días'
            },
            'ultimos_30_dias': {
                'inicio': (hoy - timedelta(days=30)).strftime('%Y-%m-%d'),
                'fin': hoy.strftime('%Y-%m-%d'),
                'nombre': 'Últimos 30 días'
            },
            'ultimos_90_dias': {
                'inicio': (hoy - timedelta(days=90)).strftime('%Y-%m-%d'),
                'fin': hoy.strftime('%Y-%m-%d'),
                'nombre': 'Últimos 90 días'
            },
            'ano_actual': {
                'inicio': hoy.replace(month=1, day=1).strftime('%Y-%m-%d'),
                'fin': hoy.strftime('%Y-%m-%d'),
                'nombre': 'Año Actual'
            }
        }
        
        return rangos.get(periodo, rangos['mes_actual'])
    
    @staticmethod
    def calcular_dias_habiles(fecha_inicio: datetime, fecha_fin: datetime, 
                              feriados: List[datetime] = None) -> int:
        """Calcula días hábiles entre dos fechas"""
        if fecha_inicio > fecha_fin:
            fecha_inicio, fecha_fin = fecha_fin, fecha_inicio
        
        if feriados is None:
            feriados = []
        
        dias_totales = (fecha_fin - fecha_inicio).days + 1
        dias_habiles = 0
        
        for i in range(dias_totales):
            fecha = fecha_inicio + timedelta(days=i)
            
            # No contar fines de semana
            if fecha.weekday() >= 5:  # 5 = sábado, 6 = domingo
                continue
            
            # No contar feriados
            if fecha in feriados:
                continue
            
            dias_habiles += 1
        
        return dias_habiles
    
    @staticmethod
    def es_fecha_valida_negocio(fecha: datetime) -> bool:
        """Verifica si una fecha es válida para operaciones de negocio"""
        # No fines de semana
        if fecha.weekday() >= 5:
            return False
        
        # No festivos principales (Colombia - simplificado)
        festivos = [
            (1, 1),   # Año nuevo
            (5, 1),   # Día del trabajo
            (7, 20),  # Independencia
            (8, 7),   # Batalla de Boyacá
            (12, 8),  # Inmaculada
            (12, 25), # Navidad
        ]
        
        if (fecha.month, fecha.day) in festivos:
            return False
        
        # No después de hoy
        if fecha.date() > datetime.now().date():
            return False
        
        return True
