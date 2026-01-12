import streamlit as st

# Page configuration

# Section - Reports
general_page = st.Page("reports/1_general.py", title="General", icon=":material/dashboard:")
locales_page = st.Page("reports/2_locales.py", title="Locales", icon=":material/inventory_2:")

# Section - Tools
explore_page = st.Page("tools/data_explorer.py", title="Explorador de Datos", icon=":material/search:")
validations_page = st.Page("tools/validations.py", title="Validaciones", icon=":material/check_circle:")

# current page
pg = st.navigation({
    "Reportes": [general_page, locales_page],
    "Herramientas": [explore_page, validations_page]
})

with st.sidebar:
    if st.button("Actualizar Datos 🔄", use_container_width=True, help="Forzar la recarga de datos desde Google Sheets"):
        st.cache_data.clear()
        st.rerun()

pg.run()

