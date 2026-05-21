import pandas as pd
import numpy as np
from tomlkit import datetime

# Lire le CSV généré
df = pd.read_csv('campaigns.csv')

# Convertir la colonne date en datetime
df['date'] = pd.to_datetime(df['date'])

# Vérification
print(df['date'].dtype)     # datetime64[ns]  ✅
print(df['date'].min())     # date la plus ancienne
print(df['date'].max())     # date la plus récente

# ── Stratégie 1 : supprimer les lignes où country est inconnu ───
# On ne peut pas analyser les performances par pays sans le pays
df = df.dropna(subset=['country'])
print("Après dropna country :", len(df), "lignes")

# ── Stratégie 2 : imputer les valeurs manquantes de spend par la médiane ──
# On suppose que les campagnes sans spend ont une dépense typique pour ce type de campagne.
# On ne veut pas perdre des lignes pour un budget manquant.
# La médiane est plus robuste que la moyenne face aux valeurs extrêmes.
mediane_spend = df['spend'].median()
df['spend'] = df['spend'].fillna(mediane_spend)
print(f"spend NaN remplacés par la médiane : {mediane_spend:.2f} €")

# Vérification — plus aucun NaN
print(df[['spend', 'country']].isnull().sum())

# Supprimer les 50 lignes dupliquées
df = df.drop_duplicates()
df = df.reset_index(drop=True)   

# réindexer proprement après suppression
print("Après dédoublonnage :", len(df), "lignes")

# Vérification
print("Doublons restants :", df.duplicated().sum())   # doit afficher 0

# Compter les lignes de clics aberrants avant filtrage
# 10 lignes
print("Clics négatifs :", (df['clicks'] < 0).sum())         
print("Clics > impressions :", (df['clicks'] > df['impressions']).sum())

# Filtrer : garder seulement les lignes de clics valides
df = df[df['clicks'] >= 0]
df = df[df['clicks'] <= df['impressions']]
df = df.reset_index(drop=True)
print("Après nettoyage aberrations :", len(df), "lignes")

# ── Calcul des KPIs ─────────────────────────────────────────────

# CTR — éviter la division par zéro avec np.where
df['ctr'] = np.where(
    df['impressions'] > 0,
    df['clicks'] / df['impressions'],
    0
)

# CAC — coût par conversion (NaN si 0 conversions — normal, on garde)
df['cac'] = df['spend'] / df['conversions'].replace(0, np.nan)

# ROAS — retour sur investissement publicitaire
df['roas'] = df['revenue'] / df['spend'].replace(0, np.nan)

# CVR — taux de conversion
df['cvr'] = np.where(
    df['clicks'] > 0,
    df['conversions'] / df['clicks'],
    0
)

# Vérification des nouvelles colonnes
print(df[['ctr', 'cac', 'roas', 'cvr']].describe().round(3))

# Extraire des composantes temporelles depuis la date
df['year']   = df['date'].dt.year    
df['month']  = df['date'].dt.month  
df['week']   = df['date'].dt.isocalendar().week.astype(int)
df['day_of_week'] = df['date'].dt.day_name()   # 'Monday', 'Tuesday', etc. 
 
# Sauvegarder le dataset nettoyé et enrichi
df.to_csv('campaigns_clean.csv', index=False)
print(f"Dataset nettoyé : {len(df)} lignes, {len(df.columns)} colonnes")
print("Colonnes :", df.columns.tolist())