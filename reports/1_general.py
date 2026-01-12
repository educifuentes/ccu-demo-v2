import pandas as pd
import streamlit as st
import plotly.express as px
import altair as alt
from src.data_preparation import get_generated_dataframes

st.title("Cumplimiento de Competencia CCU - Demo App")

st.markdown("Lectura de datos desde [Google Sheets](https://docs.google.com/spreadsheets/d/11JgW2Z9cFrHvNFw21-zlvylTHHo5tvizJeA9oxHcDHU/edit?gid=2068995815#gid=2068995815)")



CLASIFICACION_COLORS = {
    "En regla": "#83c9ff", 
    "No en regla": "#ffabab",
    "No aplica": "#CBDCEB",
    "Sin comodato o terminado": "#9F8383"
}

try:
    locales_df, censos_df, activos_df, nominas_df, contratos_df = get_generated_dataframes()
except FileNotFoundError as e:
    st.error(f"Error loading data file: {e}. Please make sure the files are in the 'data/raw/' directory.")
    st.stop()


# -----------------------------------------------------------------------------
# FILTERS
# -----------------------------------------------------------------------------


periodos = sorted(censos_df['periodo'].unique(), reverse=True)
selected_periodo = st.selectbox("Seleccionar Periodo", periodos, width=200)

censos_df_anual = censos_df[censos_df['periodo'] == selected_periodo]




# -----------------------------------------------------------------------------
# PANEL METRICAS
# -----------------------------------------------------------------------------

# --- KMETRICASPIs ---
st.header("Clasificacion")

# Calculate KPIs based on the clasificacion of all census records.
clasificacion_counts = censos_df_anual['clasificacion'].value_counts()

en_regla = clasificacion_counts.get("En regla", 0)
no_en_regla = clasificacion_counts.get("No en regla", 0)
sin_comodato = clasificacion_counts.get("Sin comodato o terminado", 0)
no_aplica = clasificacion_counts.get("No aplica", 0)

col1, col2, col3 = st.columns([1, 1, 2])

# col1, col2, col3, col4 = st.columns(4)
col1.metric("En Regla", f"{en_regla}")
col2.metric("No en Regla", f"{no_en_regla}")
# col3.metric("Sin Comodato o Terminado", f"{sin_comodato}")
# col4.metric("No Aplica", f"{no_aplica}")

with col3:
    # Chart 1 - Pie Chart of Clasificacion Distribution

    fig = px.pie(
        censos_df,
        names='clasificacion',
        color='clasificacion',
        hole=.3,
        color_discrete_map=CLASIFICACION_COLORS,
        height=300
    )
    fig.update_traces(textinfo='percent+label', pull=[0.05, 0.05, 0.05, 0.05])
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# --- Visualization ---




# Chart 2 - Bar Chart of clasificacion by date
st.header("Cumplimiento por Periodo - Censos")
chart = alt.Chart(censos_df).mark_bar().encode(
    x=alt.X('periodo:O', title='Periodo'),
    y=alt.Y('count():Q', title='Número de Locales'),
    color=alt.Color(
        'clasificacion:N',
        title='Clasificacion',
    )
)

st.altair_chart(chart, use_container_width=True, height=200)

st.subheader("Revision de Cumplimiento")
st.markdown("Avisa si local necesita revision de cumplimiento segun info de nominas.")


# # --- Table ---


# st.header("Datos de Censos - Salidas")

# subset_columns = [
#     'local_id', 'periodo', 'salidas_total', 'salidas_ccu',
#     'salidas_otras', 'salidas_target', 'clasificacion'
# ]
# st.dataframe(censos_df[subset_columns])

# st.header("Datos Schoperas - censos")
# st.text(censos_df.size)
# st.dataframe(censos_df[['local_id', 'periodo','schoperas_total', 'salidas_total']].sort_values(by=['local_id', 'periodo']))
