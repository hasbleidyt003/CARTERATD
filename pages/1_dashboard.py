"""
Dashboard Principal del Sistema de Cupos TD
"""

import streamlit as st

# Redirigir a la página principal
st.query_params['page'] = 'dashboard'
st.rerun()
