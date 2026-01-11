import pandas as pd
from pathlib import Path

# Define the input directory relative to this script
input_dir = Path(__file__).parent / "inputs"

# Load DataFrames with ad-hoc names
print("Loading dataframes...")

df_censo_2023 = pd.read_csv(input_dir / "censo_2023.csv")
df_censo_2024 = pd.read_csv(input_dir / "censo_2024.csv")
df_censo_2025 = pd.read_csv(input_dir / "censo_2025.csv")
df_contratos = pd.read_csv(input_dir / "contratos.csv")
df_locales = pd.read_csv(input_dir / "locales.csv")
df_nominas_2025_q2 = pd.read_csv(input_dir / "nominas_2025_q2.csv")
df_nominas_2025_q3 = pd.read_csv(input_dir / "nominas_2025_q3.csv")

print("Done. Loaded:")
print("-" * 50)
print(f"- df_censo_2023: {len(df_censo_2023)} rows")
print(f"  Columns: {list(df_censo_2023.columns)}")
print("-" * 50)
print(f"- df_censo_2024: {len(df_censo_2024)} rows")
print(f"  Columns: {list(df_censo_2024.columns)}")
print("-" * 50)
print(f"- df_censo_2025: {len(df_censo_2025)} rows")
print(f"  Columns: {list(df_censo_2025.columns)}")
print("-" * 50)
print(f"- df_contratos: {len(df_contratos)} rows")
print(f"  Columns: {list(df_contratos.columns)}")
print("-" * 50)
print(f"- df_locales: {len(df_locales)} rows")
print(f"  Columns: {list(df_locales.columns)}")
print("-" * 50)
print(f"- df_nominas_2025_q2: {len(df_nominas_2025_q2)} rows")
print(f"  Columns: {list(df_nominas_2025_q2.columns)}")
print("-" * 50)
print(f"- df_nominas_2025_q3: {len(df_nominas_2025_q3)} rows")
print(f"  Columns: {list(df_nominas_2025_q3.columns)}")
print("-" * 50)