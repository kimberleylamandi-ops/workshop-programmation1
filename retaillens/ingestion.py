import pandas as pd
import numpy as np
import openpyxl
from sqlalchemy import create_engine

# Lire les deux feuilles du fichier Excel
print("Chargement du fichier Excel ")
df_2009 = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2009-2010")
df_2010 = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2010-2011")

# Concaténer les deux feuilles
df = pd.concat([df_2009, df_2010], ignore_index=True)
print(f"Dataset chargé : {len(df):,} lignes × {len(df.columns)} colonnes")

# Renommer les colonnes — noms propres en minuscule
df.columns = ["invoice", "stock_code", "description",
              "quantity", "invoice_date", "unit_price",
              "customer_id", "country"]

# Aperçu rapide
print(df.head(3))
print(df.dtypes)
print(df.isnull().sum())

# ── Statistiques avant nettoyage ────────────────────────────────
print(f"Lignes totales         : {len(df):,}")
print(f"CustomerID manquants   : {df['customer_id'].isnull().sum():,}")
print(f"Annulations (C...)     : {df['invoice'].astype(str).str.startswith('C').sum():,}")
print(f"Quantity <=0          : {(df['quantity'] <= 0).sum():,}")
print(f"UnitPrice <=0         : {(df['unit_price'] <= 0).sum():,}")

# ── Nettoyage ────────────────────────────────────────────────────
# 1. Supprimer les lignes sans customer_id (transactions anonymes)
df = df.dropna(subset=["customer_id"])

# 2. Supprimer les annulations (on ne veut que les ventes réelles)
df = df[~df["invoice"].astype(str).str.startswith("C")]

# 3. Garder seulement quantity > 0 et unit_price > 0
df = df[(df["quantity"] > 0) & (df["unit_price"] > 0)]
    
# 4. Convertir customer_id en entier
df["customer_id"] = df["customer_id"].astype(int)

# 5. Calculer le montant total par ligne
df["total_price"] = (df["quantity"] * df["unit_price"]).round(2)

# ── Statistiques après nettoyage ─────────────────────────────────
df = df.reset_index(drop=True)
print(f"\nAprès nettoyage : {len(df):,} lignes")

# ── Connecter à PostgreSQL et charger le DataFrame via SQLAlchemy ───────────────────────────────

engine = create_engine(
"postgresql+psycopg2://postgres:@localhost:5432/campaigniq"
)

print("Chargement dans PostgreSQL ")
df.to_sql(
    name="retail",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=1000,   # insérer 1 000 lignes à la fois 
    method="multi"    # insertion multi-valeurs — plus rapide
)
print("✅ Table 'retail' chargée dans PostgreSQL")
engine.dispose()
print("Connexion fermée")