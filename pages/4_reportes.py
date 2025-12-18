"""
Página de Reportes y Análisis
"""

import streamlit as st

# Redirigir a la página principal
st.query_params['page'] = 'reportes'
st.rerun()
