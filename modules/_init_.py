"""
Módulos del Sistema de Gestión de Cupos - Tododrogas

Contiene:
- database: Funciones de base de datos
- auth: Autenticación y seguridad
- utils: Utilidades generales
"""

__version__ = "1.0.0"
__author__ = "Equipo Tododrogas"

# Importaciones principales
from .database import init_db, get_clientes, get_ocs_pendientes, crear_oc, autorizar_oc
from .auth import authenticate, create_user, get_users, change_password
from .utils import format_currency, calculate_percentage, validate_nit

__all__ = ['database', 'auth', 'utils']
