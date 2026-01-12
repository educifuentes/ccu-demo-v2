import pandas as pd
import numpy as np
import math
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from utils.config import TTL_VALUE


# =============================================================================
# SECTION: DATA LOADING
# =============================================================================

@st.cache_data
def load_data_gsheets():
    """Return DataFrames for given worksheet names."""
    
    conn = st.connection("gsheets", type=GSheetsConnection, ttl=TTL_VALUE)
    worksheets = ["locales", "censos", "nominas", "contratos"]

    return tuple(conn.read(worksheet=w) for w in worksheets)

# =============================================================================
# SECTION: HELPER FUNCTIONS
# =============================================================================
def assign_clasificacion(row):
    """Assigns compliance classification based on rules."""
    if not row['applies?']:
        return "No aplica"
    # The original data does not have a direct way to identify "Sin comodato o terminado"
    # We are defaulting to the other classifications for now.
    if row['complies?'] == True:
        return "En regla"
    elif row['complies?'] == False:
        return "No en regla"
    return "Sin comodato o terminado"

def build_marcas_list(row):
    """Builds a list of offered brands based on boolean columns."""
    categorias = []
    if row.get("marcas_abenv"):
        categorias.append("ABInBev")
    if row.get("marcas_kross"):
        categorias.append("Kross")
    if row.get("marcas_otras"):
        categorias.append("Otros")
    return categorias

# =============================================================================
# SECTION: DATA PROCESSING
# =============================================================================

def process_censos(censos_df):
    """Processes censos data to add calculated columns."""
    # applies?: A venue must have more than 3 taps to be considered for compliance.
    censos_df['applies?'] = censos_df['salidas_total'] > 3

    # salidas_target: The minimum number of non-CCU brand taps required.
    # Formula: floor(salidas_total / 4)
    censos_df['salidas_target'] = np.nan
    censos_df.loc[censos_df['applies?'] == True, 'salidas_target'] = censos_df['salidas_total'].apply(lambda x: math.floor(x / 4) if x > 3 else 0)

    # complies?: Checks if the number of other brand taps meets the target.
    # Formula: salidas_otras >= salidas_target
    censos_df['complies?'] = np.nan
    censos_df.loc[censos_df['applies?'] == True, 'complies?'] = (censos_df['salidas_otras'] >= censos_df['salidas_target'])

    # clasificacion: Categorical variable for compliance classification.
    censos_df['clasificacion'] = censos_df.apply(assign_clasificacion, axis=1)

    # Ensure periodo is a clean string (remove .0 if it became float)
    censos_df['periodo'] = censos_df['periodo'].astype(str).str.replace(".0", "", regex=False)

    # marcas
    censos_df['marcas_abenv'] = censos_df['marcas_abenv'] == 1
    censos_df['marcas_kross'] = censos_df['marcas_kross'] == 1
    censos_df['marcas_otras'] = censos_df['marcas_otras'] == 1


    # disponibilizo & instalo: Boolean flags for actions.
    censos_df['disponibilizo'] = censos_df['disponibilizo'] == 1
    censos_df['instalo'] = censos_df['instalo'] == 1

    # accion: Recommendation based on availability and installation status.
    conditions = [
        (censos_df['disponibilizo'] & ~censos_df['instalo']),
        (~censos_df['disponibilizo'] & censos_df['instalo'])
    ]
    choices = ['disponibilizo', 'instalo']
    censos_df['accion'] = np.select(conditions, choices, default=None)




    # build marcas column
    censos_df['marcas'] = censos_df.apply(build_marcas_list, axis=1)
    
    return censos_df


def process_contratos(contratos_df):
    """Processes contratos data to add calculated columns."""
    # Ensure date columns are datetime objects
    contratos_df['fecha_fin'] = pd.to_datetime(contratos_df['fecha_fin'])
    today = pd.Timestamp.today().normalize()

    # vigente: Boolean flag for active contracts.
    # Assuming 'vigente' column in source is 1 for active.
    contratos_df['vigente'] = (contratos_df['vigente'] == 1)

    # dias_restantes: Number of days until contract expiration.
    contratos_df['dias_restantes'] = (contratos_df['fecha_fin'] - today).dt.days

    # proximo_a_vencer: True if contract expires within 30 days and is not yet expired.
    contratos_df['proximo_a_vencer'] = (contratos_df['dias_restantes'] <= 30) & (contratos_df['dias_restantes'] >= 0)

    return contratos_df

def contratos_update_from_nominas(contratos_df, nominas_df):
    """
    Updates contratos_df with 'reportado_inactivo_ccu', 'motivo_termino' and 'periodo_termino' 
    based on the latest status from nominas_df.
    """
    # Ensure date objects
    nominas_df = nominas_df.copy()
    nominas_df['fecha'] = pd.to_datetime(nominas_df['fecha'])

    # Ensure periodo column exists
    if 'periodo' not in nominas_df.columns:
        nominas_df['periodo'] = (
            nominas_df['fecha'].dt.year.astype(str)
            + "-Q"
            + nominas_df['fecha'].dt.quarter.astype(str)
        )

    # Get the latest nomination record for each local_id
    latest_nominas = (
        nominas_df.sort_values('fecha', ascending=False)
        .drop_duplicates('local_id')
    )

    # Merge this latest info into contratos_df
    # We include 'periodo' to capture when the 'termino' occurred
    contratos_df = pd.merge(
        contratos_df,
        latest_nominas[['local_id', 'situacion', 'motivo', 'periodo']],
        on='local_id',
        how='left'
    )

    # Apply logic from prompt
    # reportado_inactivo_ccu: True if latest situacion is 'termino', False otherwise
    contratos_df['reportado_inactivo_ccu'] = contratos_df['situacion'] == 'termino'
    
    # motivo_termino: nominas_df.motivo if situacion is 'termino', NaN otherwise
    contratos_df['motivo_termino'] = np.where(
        contratos_df['situacion'] == 'termino',
        contratos_df['motivo'],
        np.nan
    )

    # periodo_termino: nominas_df.periodo if situacion is 'termino', NaN otherwise
    contratos_df['periodo_termino'] = np.where(
        contratos_df['situacion'] == 'termino',
        contratos_df['periodo'],
        np.nan
    )

    # Clean up temporary columns from merge
    contratos_df = contratos_df.drop(columns=['situacion', 'motivo', 'periodo'])

    return contratos_df


def build_activos_trimestres(censos_df: pd.DataFrame,
                                   nominas_df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye un dataframe activos_trimestrales a nivel de local_id y trimestre.

    Para cada local_id y trimestre (fecha), calcula:
    - estado
    - motivo
    - schoperas_totales
    - salidas_totales

    La lógica es secuencial y cronológica por local.
    """

    # asegurar tipos y orden
    censos_df = censos_df.copy()
    nominas_df = nominas_df.copy()

    # Convert date columns to datetime objects for proper sorting and manipulation
    censos_df["fecha"] = pd.to_datetime(censos_df["fecha"])
    nominas_df["fecha"] = pd.to_datetime(nominas_df["fecha"])

    # Sort nominas by local_id and date to ensure chronological processing
    nominas_df = nominas_df.sort_values(["local_id", "fecha"])

    rows = []

    # Iterate over each venue (local_id)
    for local_id, nom_local in nominas_df.groupby("local_id"):
        nom_local = nom_local.sort_values("fecha")

        # valores base iniciales desde censo
        # We assume there is at least one census record per venue
        censo_local = censos_df.loc[censos_df["local_id"] == local_id].iloc[0]

        prev_schoperas = censo_local["schoperas_total"]
        prev_salidas = censo_local["salidas_total"]

        # Iterate through the payroll/changes (nominas) for this venue
        for _, row in nom_local.iterrows():
            fecha = row["fecha"]

            # If the situation is a variation, we update the totals based on deltas
            if row["situacion"] == "variacion":
                schoperas_totales = prev_schoperas + row["delta_schoperas"]
                salidas_totales = prev_salidas + row["delta_salidas"]
                estado = "activo"
                motivo = None

                # actualizar bases para el siguiente trimestre
                # Update base values for the next quarter/iteration
                prev_schoperas = schoperas_totales
                prev_salidas = salidas_totales

            else:
                schoperas_totales = None
                salidas_totales = None
                estado = "inactivo"
                motivo = row["motivo"]

                # las bases NO cambian si está inactivo
                # Base values do NOT change if inactive (they persist for when it becomes active again or stay frozen)

            rows.append({
                "local_id": local_id,
                "fecha": fecha,
                "estado": estado,
                "motivo": motivo,
                "schoperas_totales": schoperas_totales,
                "salidas_totales": salidas_totales,
            })

    activos_trimestrales = pd.DataFrame(rows)
    return activos_trimestrales

# def create_revision_cumplimiento(activos_df):
    # si esta en riesgo de no cumplir, definir cumplimeinto


def process_activos(censos_df, nominas_df):
    """Builds and processes the activos dataframe tracking totals of salidas and schoperas by local_id and periodo"""
    # Generate the quarterly assets data
    activos_df = build_activos_trimestres(censos_df, nominas_df)

    # construir columna periodo
    activos_df["fecha"] = pd.to_datetime(activos_df["fecha"])

    # Create a 'periodo' column (e.g., "2023-Q1")
    activos_df["periodo"] = (
        activos_df["fecha"].dt.year.astype(str)
        + "-Q"
        + activos_df["fecha"].dt.quarter.astype(str)
    )
    return activos_df

def build_contratos_from_nominas(contratos_df, nominas_df):
  

    return contratos_df 

# =============================================================================
# SECTION: MAIN EXECUTION
# =============================================================================
def get_generated_dataframes():
    """Main function to load and prepare all dataframes. Adds a generated activos_df"""
    # 1. Load Data - from CSV or Google Sheets
    locales_df, censos_df, nominas_df, contratos_df = load_data_gsheets()
    
    # 2. Process Census Data
    censos_df = process_censos(censos_df)
    
    # 3. Process Contratos Data
    contratos_df = process_contratos(contratos_df)
    contratos_df = contratos_update_from_nominas(contratos_df, nominas_df)

    # 4. Process Assets (Activos) Data
    activos_df = process_activos(censos_df, nominas_df)

    # --- Data Merge ---
    # Perform a left join to add venue information to each census record.
    # Join keys: censos_df.local_id = locales_df.id
    censos_df = pd.merge(
        censos_df,
        locales_df,
        left_on='local_id',
        right_on='id',
        how='left'
    )

    activos_df = pd.merge(
        activos_df,
        locales_df,
        left_on='local_id',
        right_on='id',
        how='left'
    )
    
    return locales_df, censos_df, activos_df, nominas_df, contratos_df