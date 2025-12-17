python
"""
Módulos del Sistema de Cartera TD
Contiene:
- database: Funciones de base de datos
- auth: Autenticación de usuarios
- utils: Utilidades generales
"""

__version__ = "2.0.0"
__author__ = "Equipo Cartera TD"

# Importaciones fáciles
from .database import init_db, get_clientes, get_ocs_pendientes
from .auth import authenticate

# Lista de módulos disponibles
__all__ = ['database', 'auth', 'utils']

