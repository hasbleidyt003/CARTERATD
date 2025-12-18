"""
Paquete modules para CarteraTD

Este paquete contiene los módulos principales de la aplicación:
- database: Manejo de base de datos
- auth: Autenticación de usuarios  
- utils: Funciones utilitarias
"""

__version__ = "1.0.0"
__author__ = "Tu Nombre"
__email__ = "tu@email.com"

# Importaciones principales para facilitar el acceso
from modules.database import (
    get_connection,
    create_tables,
    execute_query,
    fetch_all,
    fetch_one
)

from modules.auth import (
    hash_password,
    verify_login,
    check_authentication,
    login_form,
    logout_button
)

from modules.utils import (
    format_currency,
    format_date,
    export_to_excel,
    validate_email,
    calculate_age
)

# Lista de módulos disponibles
__all__ = [
    # Database
    'get_connection',
    'create_tables', 
    'execute_query',
    'fetch_all',
    'fetch_one',
    
    # Auth
    'hash_password',
    'verify_login',
    'check_authentication',
    'login_form',
    'logout_button',
    
    # Utils
    'format_currency',
    'format_date',
    'export_to_excel',
    'validate_email',
    'calculate_age'
]

# Mensaje de inicialización
print(f"Inicializando módulos CarteraTD v{__version__}")
