import pandas as pd
import numpy as np
from faker import Faker
import random

# ── Initialisation ──────────────────────────────────────────────
fake   = Faker()
np.random.seed(42)   # reproductibilité : même seed = mêmes données  
random.seed(42)
N = 5000             # nombre de campagnes à générer

# ── Listes de valeurs possibles ─────────────────────────────────
channels  = ['email', 'social', 'search', 'display']
countries = ['France', 'Germany', 'Spain', 'Italy', 'Netherlands']
segments  = ['new', 'returning', 'vip']

# ── Génération des données ─────────────────────────────────────
rows = []
for i in range(N):
    channel = random.choice(channels)
    country = random.choice(countries)
    segment = random.choice(segments)

    # Impressions selon le canal (search/display ont plus d'impressions)
    if channel in ['search', 'display']:
        impressions = int(np.random.lognormal(10.5, 0.8))
    else:
        impressions = int(np.random.lognormal(9.5, 0.7))

    # CTR (taux de clic) réaliste par canal
    ctr_base = {'email': 0.18, 'social': 0.04,
                'search': 0.08, 'display': 0.002}
    ctr   = max(0, np.random.normal(ctr_base[channel], ctr_base[channel]*0.3))
    clicks = int(impressions * ctr)

    # Taux de conversion et spend
    conv_rate   = max(0, np.random.normal(0.03, 0.01))
    conversions = int(clicks * conv_rate)
    spend       = round(np.random.lognormal(7, 0.6), 2)
    revenue     = round(conversions * np.random.uniform(80, 150), 2)

    rows.append({
        'campaign_id'  : f'CAMP-{i+1:05d}',
        'date'         : fake.date_between(start_date='-2y', end_date='today'),
        'channel'          : channel,
        'campaign_name': f'{fake.catch_phrase()} {channel.title()} {country[:2].upper()}',
        'country'          : country,
        'segment'          : segment,
        'impressions'  : impressions,
        'clicks'       : clicks,
        'conversions'  : conversions,
        'spend'        : spend,
        'revenue'      : revenue,
    }) 

# ── Création du DataFrame ───────────────────────
df = pd.DataFrame(rows) 

# ── Introduire des problèmes de qualité ─────────────────────────

# 1. Valeurs manquantes dans 'spend' et 'country' (~5% des lignes)
idx_spend   = np.random.choice(df.index, size=int(N*0.05), replace=False)
idx_country = np.random.choice(df.index, size=int(N*0.04), replace=False)
df.loc[idx_spend,   'spend']   = np.nan
df.loc[idx_country, 'country'] = np.nan

# 2. Doublons — dupliquer 50 lignes aléatoires
duplicates = df.sample(50, random_state=42)
df = pd.concat([df, duplicates], ignore_index=True)

# 3. Valeurs aberrantes dans 'clicks' — quelques valeurs impossibles
idx_aberrant = np.random.choice(df.index, size=10, replace=False)
df.loc[idx_aberrant, 'clicks'] = -999 # clics négatifs → impossible

# 4. Type incorrect — date stockée comme chaîne dans quelques lignes
df['date'] = df['date'].astype(str)   # tout en string pour simuler un export CSV

# ── Mélanger et sauvegarder ─────────────────────────────────────
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
df.to_csv('campaigns.csv', index=False, encoding='utf-8')

print(f"Dataset généré : {len(df)} lignes × {len(df.columns)} colonnes")
print(f"Fichier sauvegardé : campaigns.csv")
print(df.head(3))


