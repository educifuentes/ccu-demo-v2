import streamlit as st
from src.data_preparation import get_generated_dataframes

try:
    locales_df, censos_df, activos_df, nominas_df, contratos_df = get_generated_dataframes()
except FileNotFoundError as e:
    st.error(f"Error loading data file: {e}. Please make sure the files are in the 'data/raw/' directory.")
    st.stop()

st.title("Explorador de Datos")


st.subheader("Locales")
st.dataframe(locales_df)

st.subheader("Censos")
st.dataframe(censos_df)

st.subheader("Nominas Data")
st.dataframe(nominas_df)

st.subheader("Activos Data")
st.dataframe(activos_df)

st.subheader("Contratos Data")
st.dataframe(contratos_df)
