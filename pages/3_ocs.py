"""
Página de Gestión de Órdenes de Compra
"""

import streamlit as st

# Redirigir a la página principal
st.query_params['page'] = 'ocs'
st.rerun()
