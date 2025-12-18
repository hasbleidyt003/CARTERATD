"""
Página de Gestión de Clientes
"""

import streamlit as st

# Redirigir a la página principal
st.query_params['page'] = 'clientes'
st.rerun()
