import pandas as pd
import numpy as np
import math
import streamlit as st
from streamlit_gsheets import GSheetsConnection



# =============================================================================
# SECTION: DATA LOADING
# =============================================================================

def load_data_gsheets():
    """Return DataFrames for given worksheet names."""
    
    conn = st.connection("gsheets", type=GSheetsConnection)
    worksheets = ["locales", "censos", "nominas", "contratos"]

    return tuple(conn.read(worksheet=w) for w in worksheets)

# =============================================================================
# SECTION: HELPER FUNCTIONS
# =============================================================================
def assign_status(row):
    """Assigns compliance status based on rules."""
    if not row['applies?']:
        return "No aplica"
    # The original data does not have a direct way to identify "Sin comodato o terminado"
    # We are defaulting to the other statuses for now.
    if row['complies?'] == True:
        return "En regla"
    elif row['complies?'] == False:
        return "No en regla"
    return "Sin comodato o terminado"

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

    # status: Categorical variable for compliance status.
    censos_df['status'] = censos_df.apply(assign_status, axis=1)
    
    return censos_df

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


def process_activos(censos_df, nominas_df):
    """Builds and processes the activos dataframe."""
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

# =============================================================================
# SECTION: MAIN EXECUTION
# =============================================================================
def get_generated_dataframes():
    """Main function to load and prepare all dataframes. Adds a generated activos_df"""
    # 1. Load Data - from CSV or Google Sheets
    locales_df, censos_df, nominas_df, contratos_df = load_data_gsheets()
    
    # 2. Process Census Data
    censos_df = process_censos(censos_df)
    
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