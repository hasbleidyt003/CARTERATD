"""
Página de Configuración del Sistema
"""

import streamlit as st

# Redirigir a la página principal
st.query_params['page'] = 'configuracion'
st.rerun()
