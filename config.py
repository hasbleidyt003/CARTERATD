"""
Configuración del Sistema de Gestión de Cartera TD
Variables de configuración globales
"""

import os
from pathlib import Path

# ============================================================================
# PATHS Y DIRECTORIOS
# ============================================================================

# Directorio base
BASE_DIR = Path(__file__).parent

# Directorios de datos
DATA_DIR = BASE_DIR / 'data'
BACKUP_DIR = DATA_DIR / 'backups'
LOGS_DIR = DATA_DIR / 'logs'

# Archivos
DATABASE_FILE = DATA_DIR / 'database.db'
CONFIG_FILE = DATA_DIR / 'config.json'
LOG_FILE = LOGS_DIR / 'app.log'

# ============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================================

# Configuración de Streamlit
STREAMLIT_CONFIG = {
    'page_title': 'Control de Cupos - Medicamentos',
    'page_icon': '💊',
    'layout': 'wide',
    'initial_sidebar_state': 'collapsed',
    'menu_items': {
        'Get Help': None,
        'Report a bug': None,
        'About': """
        ## Sistema de Gestión de Cartera TD
        
        **Versión:** 2.0  
        **Propósito:** Control de cupos de crédito para clientes del sector salud  
        **Desarrollado por:** Equipo de Tecnología
        
        Este sistema permite gestionar:
        - Clientes y sus cupos de crédito
        - Órdenes de Compra (OCs) pendientes y autorizadas
        - Movimientos y pagos
        - Reportes y estadísticas
        """
    }
}

# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================================================

DATABASE_CONFIG = {
    'driver': 'sqlite',
    'database': str(DATABASE_FILE),
    'timeout': 30,
    'check_same_thread': False,
    'pool_size': 10,
    'max_overflow': 20
}

# ============================================================================
# CONFIGURACIÓN DE AUTENTICACIÓN
# ============================================================================

AUTH_CONFIG = {
    'session_timeout_minutes': 120,
    'max_login_attempts': 5,
    'lockout_minutes': 15,
    'password_min_length': 8,
    'require_special_chars': True,
    'require_numbers': True,
    'require_uppercase': True
}

# ============================================================================
# CONFIGURACIÓN DE REPORTES
# ============================================================================

REPORT_CONFIG = {
    'auto_backup_days': 7,
    'retention_days': 365,
    'cleanup_days': 90,
    'alert_threshold': 80,
    'critical_threshold': 100,
    'max_rows_export': 100000
}

# ============================================================================
# CONFIGURACIÓN DE NOTIFICACIONES
# ============================================================================

NOTIFICATION_CONFIG = {
    'enabled': False,
    'smtp_server': '',
    'smtp_port': 587,
    'smtp_user': '',
    'smtp_password': '',
    'from_email': '',
    'alert_recipients': [],
    'daily_report_time': '08:00'
}

# ============================================================================
# CONFIGURACIÓN DE ESTILOS
# ============================================================================

STYLE_CONFIG = {
    'primary_color': '#3498db',
    'secondary_color': '#2ecc71',
    'warning_color': '#f39c12',
    'danger_color': '#e74c3c',
    'dark_color': '#2c3e50',
    'light_color': '#ecf0f1',
    'font_family': 'Arial, sans-serif',
    'border_radius': '5px'
}

# ============================================================================
# FUNCIONES DE INICIALIZACIÓN
# ============================================================================

def init_directories():
    """Inicializa los directorios necesarios"""
    directories = [DATA_DIR, BACKUP_DIR, LOGS_DIR]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    return True

def load_config():
    """Carga la configuración desde archivo JSON"""
    try:
        import json
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    
    # Configuración por defecto
    default_config = {
        'version': '2.0.0',
        'last_updated': '',
        'features': {
            'auth_enabled': False,
            'notifications_enabled': False,
            'auto_backup': True,
            'auto_cleanup': True
        }
    }
    
    return default_config

def save_config(config):
    """Guarda la configuración en archivo JSON"""
    try:
        import json
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except:
        return False

# ============================================================================
# VALORES POR DEFECTO
# ============================================================================

DEFAULT_CLIENTES = [
    {
        'nit': '890905166',
        'nombre': 'EMPRESA SOCIAL DEL ESTADO HOSPITAL MENTAL',
        'cupo_sugerido': 7500000000,
        'saldo_actual': 7397192942,
        'cartera_vencida': 3342688638
    },
    {
        'nit': '900746052',
        'nombre': 'NEURUM SAS',
        'cupo_sugerido': 5500000000,
        'saldo_actual': 5184247632,
        'cartera_vencida': 2279333768
    },
    {
        'nit': '800241602',
        'nombre': 'FUNDACION COLOMBIANA DE CANCEROLOGIA',
        'cupo_sugerido': 3500000000,
        'saldo_actual': 3031469552,
        'cartera_vencida': 191990541
    },
    {
        'nit': '890985122',
        'nombre': 'COOPERATIVA DE HOSPITALES DE ANTIOQUIA',
        'cupo_sugerido': 1500000000,
        'saldo_actual': 1291931405,
        'cartera_vencida': 321889542
    },
    {
        'nit': '900099945',
        'nombre': 'GLOBAL SERVICE PHARMACEUTICAL S.A.S.',
        'cupo_sugerido': 1200000000,
        'saldo_actual': 1009298565,
        'cartera_vencida': 434808971
    },
    {
        'nit': '811038014',
        'nombre': 'GRUPO ONCOLOGICO INTERNACIONAL S.A.',
        'cupo_sugerido': 900000000,
        'saldo_actual': 806853666,
        'cartera_vencida': 146804409
    }
]

# ============================================================================
# INICIALIZACIÓN AUTOMÁTICA
# ============================================================================

# Inicializar directorios al importar
init_directories()

# Cargar configuración
APP_CONFIG = load_config()

print(f"✅ Configuración cargada - Versión {APP_CONFIG.get('version', '1.0')}")
