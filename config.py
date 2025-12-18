"""
Configuración del Sistema de Gestión de Cupos TD
Versión Profesional - Futurista
"""

import os
from pathlib import Path

# ============================================================================
# CONFIGURACIÓN GLOBAL
# ============================================================================

class Config:
    # Rutas del sistema
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / 'data'
    ASSETS_DIR = BASE_DIR / 'assets'
    LOGS_DIR = DATA_DIR / 'logs'
    
    # Archivos
    DATABASE_PATH = DATA_DIR / 'cupos_td.db'
    BACKUP_DIR = DATA_DIR / 'backups'
    
    # Configuración de la aplicación
    APP_NAME = "Sistema de Gestión de Cupos TD"
    APP_VERSION = "3.0.0"
    APP_DESCRIPTION = "Sistema profesional para gestión y seguimiento de cupos de crédito"
    
    # Colores del tema (Futurista)
    COLORS = {
        'primary': '#2563eb',      # Azul futurista
        'secondary': '#7c3aed',    # Púrpura
        'success': '#10b981',      # Verde esmeralda
        'warning': '#f59e0b',      # Ámbar
        'danger': '#ef4444',       # Rojo
        'dark': '#1e293b',         # Azul oscuro
        'light': '#f8fafc',        # Blanco azulado
        'accent': '#0ea5e9',       # Cian
        'gradient_start': '#2563eb',
        'gradient_end': '#7c3aed'
    }
    
    # Clientes iniciales (Datos reales proporcionados)
    CLIENTES_INICIALES = [
        {
            'nit': '901212102',
            'nombre': 'AUNA COLOMBIA S.A.S',
            'total_cartera': 19493849830,
            'cupo_sugerido': 21693849830,
            'disponible': 2200000000
        },
        {
            'nit': '890905166',
            'nombre': 'EMPRESA SOCIAL DEL ESTADO HOSPITAL MENTAL DE ANTIOQ',
            'total_cartera': 7397192942,
            'cupo_sugerido': 7500000000,
            'disponible': 102807058
        },
        {
            'nit': '900249425',
            'nombre': 'PHARMASAN S.A.S',
            'total_cartera': 5710785209,
            'cupo_sugerido': 5910785209,
            'disponible': 200000000
        },
        {
            'nit': '900748052',
            'nombre': 'NEUROM SAS',
            'total_cartera': 5184247623,
            'cupo_sugerido': 5500000000,
            'disponible': 315752377
        },
        {
            'nit': '800241602',
            'nombre': 'FUNDACION COLOMBIANA DE CANCEROLOGIA CLINICA VIDA',
            'total_cartera': 3031469552,
            'cupo_sugerido': 3500000000,
            'disponible': 468530448
        },
        {
            'nit': '890985122',
            'nombre': 'COOPERATIVA DE HOSPITALES DE ANTIOQUIA',
            'total_cartera': 1221931405,
            'cupo_sugerido': 1500000000,
            'disponible': 278068595
        },
        {
            'nit': '811038014',
            'nombre': 'GRUPO ONCOLOGICO INTERNACIONAL S.A.',
            'total_cartera': 806853666,
            'cupo_sugerido': 900000000,
            'disponible': 93146334
        }
    ]

# Instancia global de configuración
config = Config()

# Crear directorios necesarios
os.makedirs(config.DATA_DIR, exist_ok=True)
os.makedirs(config.BACKUP_DIR, exist_ok=True)
os.makedirs(config.LOGS_DIR, exist_ok=True)
