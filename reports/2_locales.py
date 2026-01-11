import streamlit as st
import pandas as pd
import altair as alt
from src.data_preparation import get_generated_dataframes

try:
    locales_df, censos_df, activos_df, nominas_df, contratos_df = get_generated_dataframes()
except FileNotFoundError as e:
    st.error(f"Error loading data file: {e}. Please make sure the files are in the 'data/raw/' directory.")
    st.stop()


st.title("Locales")
st.markdown("Informacion de censos y nominas de cada local por periodo")

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

st.subheader("Ficha del Local")

local_info = locales_df[locales_df['id'] == selected_local_id].iloc[0]

# Get most recent census clasificacion for the badge
local_censos = censos_df[censos_df['local_id'] == selected_local_id].sort_values('fecha', ascending=False)
latest_clasificacion = local_censos.iloc[0]['clasificacion'] if not local_censos.empty else "Sin Datos"

with st.container(border=True):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### {local_info['razon_social']}")
        st.caption(f"ID: {selected_local_id} | RUT: {local_info['rut']}")
        st.markdown(f"📍 **{local_info['direccion']}**")
        st.markdown(f"{local_info['ciudad']}, {local_info['region']}")
        
    with col2:
        st.markdown("**Estado de Cumplimiento**")
        if latest_clasificacion != "Sin Datos":
            st.badge(latest_clasificacion, icon="🔍")
        else:
            st.write("No hay censos registrados")

# -----------------------------------------------------------------------------

st.subheader("Activos por Trimestre")
st.markdown("Reconstruido usando censos y nominas CCU. Avisa si local necesita revision de cumplimiento.")

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
st.markdown("Información detallada de censos por periodo: clasificación de cumplimiento, totales de infraestructura y marcas detectadas.")

censos_filtered = censos_df[censos_df['local_id'] == selected_local_id]
display_columns = ['periodo', 'clasificacion', 'salidas_total', 'schoperas_total', 'marcas']
censos_filtered = censos_filtered[display_columns].sort_values('periodo', ascending=False)

st.dataframe(
    censos_filtered,
    column_config={
        "clasificacion": st.column_config.MultiselectColumn(
            "Clasificación",
            help="Estado de cumplimiento del local",
            options=[
                "En regla",
                "No en regla",
                "No aplica",
                "Sin comodato o terminado",
            ],
            color=["#83c9ff", "#ffabab", "#CBDCEB", "#9F8383"],
        ),
        "marcas": st.column_config.MultiselectColumn(
            "Marcas Ofrecidas",
            help="Marcas detectadas en el censo",
            options=[
                "ABInBev",
                "Kross",
                "Otros",
            ],
            color=["#ffa421", "#803df5", "#00c0f2"],
        ),
    },
    hide_index=True,
)


st.subheader("Contrato")
local_contrato = contratos_df[contratos_df['local_id'] == selected_local_id]
if not local_contrato.empty:
    contrato_info = local_contrato.iloc[0]
    
    # Check if reported inactive by CCU
    if contrato_info.get('reportado_inactivo_ccu'):
        st.error(f"🚫 **Contrato finalizado según nominas CCU**")
        if pd.notna(contrato_info.get('motivo_termino')):
            st.markdown(f"**Motivo término:** {contrato_info['motivo_termino']}")
        if pd.notna(contrato_info.get('periodo_termino')):
            st.caption(f"Informado en periodo: {contrato_info['periodo_termino']}")
        st.divider()

    # Check if upcoming expiration
    if contrato_info['proximo_a_vencer']:
        st.badge(
            icon="⚠️", 
            label=f"Contrato próximo a vencer ({contrato_info['dias_restantes']} días)", 
            type="warning"
        )

st.dataframe(local_contrato)