"""
CONFIGURACIÓN GENERAL DEL SISTEMA
Variables de configuración y constantes
"""

import os
from datetime import datetime

# ==================== CONFIGURACIÓN GENERAL ====================

APP_NAME = "Tododrogas - Sistema de Gestión de Cupos"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Equipo de Automatización"

# ==================== CONFIGURACIÓN DE BASE DE DATOS ====================

DATABASE_PATH = "data/database.db"
BACKUP_PATH = "data/backups"

# ==================== CONFIGURACIÓN DE SEGURIDAD ====================

SESSION_TIMEOUT = 3600  # 1 hora en segundos
MAX_LOGIN_ATTEMPTS = 3
PASSWORD_MIN_LENGTH = 8

# ==================== CONFIGURACIÓN DE EMPRESA ====================

EMPRESA_NOMBRE = "TODODROGAS S.A.S"
EMPRESA_NIT = "900.000.000-1"
EMPRESA_DIRECCION = "Calle 123 #45-67, Medellín, Colombia"
EMPRESA_TELEFONO = "+57 (4) 123 4567"

# ==================== UMBRALES DE ALERTA ====================

UMBRAL_ALERTA = 80  # Porcentaje para estado ALERTA
UMBRAL_CRITICO = 90  # Porcentaje para estado CRÍTICO

# ==================== CONFIGURACIÓN DE OCs ====================

OC_MIN_VALUE = 1000000  # Valor mínimo para una OC (1 millón)
OC_MAX_VALUE = 10000000000  # Valor máximo para una OC (10 mil millones)

# ==================== CONFIGURACIÓN DE REPORTES ====================

REPORT_RETENTION_DAYS = 30
EXPORT_FORMAT = "excel"  # excel, csv, pdf

# ==================== CONFIGURACIÓN DE LOGS ====================

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "logs/system.log"

# ==================== FUNCIONES DE CONFIGURACIÓN ====================

def get_config():
    """Obtiene toda la configuración como diccionario"""
    config_dict = {}
    
    # Obtener todas las variables que no son funciones
    for key, value in globals().items():
        if not key.startswith('_') and not callable(value) and key.isupper():
            config_dict[key] = value
    
    return config_dict

def validate_config():
    """Valida que la configuración sea correcta"""
    errors = []
    
    # Validar umbrales
    if UMBRAL_CRITICO <= UMBRAL_ALERTA:
        errors.append("UMBRAL_CRITICO debe ser mayor que UMBRAL_ALERTA")
    
    if UMBRAL_ALERTA < 0 or UMBRAL_ALERTA > 100:
        errors.append("UMBRAL_ALERTA debe estar entre 0 y 100")
    
    if UMBRAL_CRITICO < 0 or UMBRAL_CRITICO > 100:
        errors.append("UMBRAL_CRITICO debe estar entre 0 y 100")
    
    # Validar valores de OC
    if OC_MIN_VALUE <= 0:
        errors.append("OC_MIN_VALUE debe ser mayor que 0")
    
    if OC_MAX_VALUE <= OC_MIN_VALUE:
        errors.append("OC_MAX_VALUE debe ser mayor que OC_MIN_VALUE")
    
    return errors

# ==================== INICIALIZACIÓN ====================

# Crear directorios necesarios
os.makedirs("data/backups", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Validar configuración
config_errors = validate_config()
if config_errors:
    print("⚠️ Errores en configuración:")
    for error in config_errors:
        print(f"  - {error}")
