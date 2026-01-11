# transform_base.py

import pandas as pd
from pathlib import Path

# =============================================================================
# SETTINGS & PATHS
# =============================================================================
INPUT_DIR = Path(__file__).parent / "inputs"
OUTPUT_DIR = Path(__file__).parent / "outputs"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# DATA LOADING
# =============================================================================
print("Loading dataframes...")

df_censo_2023 = pd.read_csv(INPUT_DIR / "censo_2023.csv")
df_censo_2024 = pd.read_csv(INPUT_DIR / "censo_2024.csv")
df_censo_2025 = pd.read_csv(INPUT_DIR / "censo_2025.csv")
df_contratos = pd.read_csv(INPUT_DIR / "contratos.csv")
df_locales = pd.read_csv(INPUT_DIR / "locales.csv")
df_nominas_2025_q2 = pd.read_csv(INPUT_DIR / "nominas_2025_q2.csv")
df_nominas_2025_q3 = pd.read_csv(INPUT_DIR / "nominas_2025_q3.csv")

print("Done. Loaded:")
print(f"- df_censo_2023: {len(df_censo_2023)} rows")
print(f"- df_censo_2024: {len(df_censo_2024)} rows")
print(f"- df_censo_2025: {len(df_censo_2025)} rows")
print(f"- df_contratos: {len(df_contratos)} rows")
print(f"- df_locales: {len(df_locales)} rows")
print(f"- df_nominas_2025_q2: {len(df_nominas_2025_q2)} rows")
print(f"- df_nominas_2025_q3: {len(df_nominas_2025_q3)} rows")


# =============================================================================
# LOCALES TRANSFORMATION
# =============================================================================
locales_df = df_locales.copy()

# 1. Clean column names (snake_case, no accents)
locales_df.columns = [
    c.lower()
    .replace(" ", "_")
    .replace("n°", "n")
    .replace("(", "")
    .replace(")", "")
    .replace(".", "")
    .replace("á", "a")
    .replace("é", "e")
    .replace("í", "i")
    .replace("ó", "o")
    .replace("ú", "u")
    .strip("_")
    for c in locales_df.columns
]

# 2. Map specific names
locales_df = locales_df.rename(columns={
    "id": "local_id",
    "nombre_de_fantasia": "nombre_fantasia",
    "nombre_de_fantasia_2": "nombre_fantasia_2"
})

# 3. Format text columns (Trim & Title)
columns_to_format = ["razon_social", "direccion", "nombre_fantasia", "nombre_fantasia_2", "ciudad", "region"]

for col in columns_to_format:
    if col in locales_df.columns:
        locales_df[col] = locales_df[col].astype(str).str.strip().str.title()

# 4. Save Locales
print("\nLocales head:")
print(locales_df.head())
print("-" * 50)
locales_df.to_csv(OUTPUT_DIR / "locales.csv", index=False)



# =============================================================================
# CENSOS CONSOLIDATION
# =============================================================================

# Define target schema
columns = [
    "local_id", "fecha", "periodo", "agencia", "schoperas_total", 
    "schoperas_ccu", "schoperas_otros", "salidas_total", "salidas_ccu", 
    "salidas_otras", "coolers_total", "marcas_ccu", "marcas_kross", 
    "marcas_otras", "instalo", "disponibilizo",
]

censos_df = pd.DataFrame(columns=columns)
censos_df = censos_df.astype({
    "local_id": "string",
    "periodo": "string",
    "agencia": "string",
    "schoperas_total": "Int64",
    "schoperas_ccu": "Int64",
    "schoperas_otros": "Int64",
    "salidas_total": "Int64",
    "salidas_ccu": "Int64",
    "salidas_otras": "Int64",
    "coolers_total": "Int64",
    "marcas_ccu": "bool",
    "marcas_kross": "bool",
    "marcas_otras": "bool",
    "instalo": "bool",
    "disponibilizo": "bool",
})

# --- Census 2023 ---
df_2023_tmp = df_censo_2023.rename(columns={
    "id": "local_id",
    "N° Coolers": "coolers_total",
    "N° Columnas (Schoperas)": "schoperas_otros",
    "N° Salidas Schop CCU": "salidas_total"
})
df_2023_tmp["periodo"] = "2023"
censos_df = pd.concat([censos_df, df_2023_tmp[df_2023_tmp.columns.intersection(censos_df.columns)]], ignore_index=True)

# --- Census 2024 ---
df_2024_tmp = df_censo_2024.rename(columns={
    "id": "local_id",
    "CANTIDAD DE SCHOPERAS CCU": "schoperas_ccu",
    "CANTIDAD DE SALIDAS": "salidas_total",
    "CANTIDAD DE SHOPERAS COMPETENCIA ": "schoperas_otros"
})
df_2024_tmp["periodo"] = "2024"
censos_df = pd.concat([censos_df, df_2024_tmp[df_2024_tmp.columns.intersection(censos_df.columns)]], ignore_index=True)

# --- Census 2025 ---
df_2025_tmp = df_censo_2025.rename(columns={
    "id": "local_id",
    "Número de Salidas Actuales ": "salidas_total",
    "CCH": "marcas_abenv",
    "KROSS": "marcas_kross",
    "Otras": "marcas_otras"
})
df_2025_tmp["periodo"] = "2025"
df_2025_tmp["instalo"] = df_censo_2025["instalo"] == 1
df_2025_tmp["disponibilizo"] = df_censo_2025["disponibilizo"] == 1
censos_df = pd.concat([censos_df, df_2025_tmp[df_2025_tmp.columns.intersection(censos_df.columns)]], ignore_index=True)

# 4. Save Censos
print("\nCensos head:")
print(censos_df.head())
print("-" * 50)
censos_df.to_csv(OUTPUT_DIR / "censos.csv", index=False)


# =============================================================================
# CONTRATOS TRANSFORMATION
# =============================================================================
df_contratos = df_contratos.rename(columns={
    "id": "local_id",
    "Fecha Inicio": "fecha_inicio",
    "Fecha Fin": "fecha_fin",
    "VIGENTE/NO VIGENTE": "vigente_sn",
    "Folio": "folio",
    "Activos/No Activos Según CCU (sin detalle)": "activo_ccu_sn",
})

# Convert dates (handles M/D/YYYY like 2/28/2026)
df_contratos["fecha_inicio"] = pd.to_datetime(df_contratos["fecha_inicio"], errors='coerce')
df_contratos["fecha_fin"] = pd.to_datetime(df_contratos["fecha_fin"], errors='coerce')

# Boolean conversions
df_contratos["vigente"] = df_contratos["vigente_sn"] == "VIGENTE"
df_contratos["activo_ccu"] = df_contratos["activo_ccu_sn"] == "Activos"

# Final selection and types
df_contratos = df_contratos.astype({"local_id": "string", "folio": "string"})
df_contratos = df_contratos[["local_id", "fecha_inicio", "fecha_fin", "vigente", "folio", "activo_ccu"]]

print("\nContratos head:")
print(df_contratos.head())
print("-" * 50)
df_contratos.to_csv(OUTPUT_DIR / "contratos.csv", index=False)


# =============================================================================
# NOMINAS TRANSFORMATION (Placeholder)
# =============================================================================
# TODO: Implement nominations logic

# sample

# =============================================================================
# SAMPLE
# =============================================================================

locales_sample = locales_df.sample(15, random_state=42)
locales_sample.to_csv(OUTPUT_DIR / "locales_sample.csv", index=False)

distinct_local_ids = locales_sample["local_id"].unique()

contratos_sample = df_contratos[df_contratos["local_id"].isin(distinct_local_ids)]
contratos_sample.to_csv(OUTPUT_DIR / "contratos_sample.csv", index=False)

