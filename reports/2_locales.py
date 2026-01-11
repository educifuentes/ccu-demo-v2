import streamlit as st
import altair as alt
from src.data_preparation import get_generated_dataframes

try:
    locales_df, censos_df, activos_df, nominas_df, contratos_df = get_generated_dataframes()
except FileNotFoundError as e:
    st.error(f"Error loading data file: {e}. Please make sure the files are in the 'data/raw/' directory.")
    st.stop()


st.title("Locales")

local_ids = sorted(activos_df['local_id'].unique())
# Map local_id to razon_social for display
id_to_name = activos_df.drop_duplicates('local_id').set_index('local_id')['razon_social'].to_dict()


col1, col2 = st.columns(2)



with col1:
    regions = ["Todas"] + sorted(locales_df['region'].unique().tolist())
    selected_region = st.selectbox(
        "Seleccionar Region", 
        regions,
        format_func=lambda x: x.title()
    )
    if selected_region == "Todas":
        locales_df_region = locales_df
    else:
        locales_df_region = locales_df[locales_df['region'] == selected_region]

with col2:
    # Filter local_ids based on the region selection
    filtered_local_ids = sorted(locales_df_region['id'].unique())
    # st.write(filtered_local_ids)
    selected_local_id = st.selectbox(
        "Seleccionar Local", 
        filtered_local_ids, 
        format_func=lambda x: f"{x} - {locales_df_region.loc[locales_df_region['id'] == x, 'razon_social'].values[0]}",
        width=500
    )


# -----------------------------------------------------------------------------

st.subheader("Informacion")


st.dataframe(locales_df[locales_df['id'] == selected_local_id])

local_info = locales_df[locales_df['id'] == selected_local_id].iloc[0]

multi = f'''
- **Razon Social**: {local_info['razon_social']} | **RUT**: `{local_info['rut']}`
- **Direccion**: {local_info['direccion']} - {local_info['ciudad']} - {local_info['region']}
'''
st.markdown(multi)

# -----------------------------------------------------------------------------

st.subheader("Activos por Trimestre")
st.markdown("Reconstruido usando censos y nominas CCU")

local_stats_df = activos_df[activos_df['local_id'] == selected_local_id].copy()
# Fill NaN values with 0 to ensure they appear in the chart
local_stats_df['salidas_totales'] = local_stats_df['salidas_totales'].fillna(0)


# bar plot
tab1, tab2 = st.tabs(["Shoperas", "Salidas"])

with tab1:
    schoperas_chart = alt.Chart(local_stats_df).mark_bar().encode(
    x='periodo',
    y='schoperas_totales',
    tooltip=['periodo', 'schoperas_totales']
)
    st.altair_chart(schoperas_chart, use_container_width=True)

with tab2:
    salidas_chart = alt.Chart(local_stats_df).mark_bar().encode(
    x='periodo',
    y='salidas_totales',
    tooltip=['periodo', 'salidas_totales']
)
    st.altair_chart(salidas_chart, use_container_width=True)

st.subheader("Censos")


# Get most recent census status
local_censos = censos_df[censos_df['local_id'] == selected_local_id].sort_values('fecha', ascending=False)
if not local_censos.empty:
    latest_status = local_censos.iloc[0]['status']
    st.info(f"**Estado actual (Censo más reciente):** {latest_status}")
st.badge(latest_status, icon="🔍")

st.dataframe(censos_df[censos_df['local_id'] == selected_local_id])


st.subheader("Contrato")
st.badge(icon="🔍", label="Contrato proximo a vencer (x dias)")

st.dataframe(contratos_df[contratos_df['local_id'] == selected_local_id])