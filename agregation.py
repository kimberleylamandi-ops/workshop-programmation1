import pandas as pd
import numpy as np
from tomlkit import datetime

# Lire le CSV généré
df = pd.read_csv('campaigns_clean.csv', parse_dates=['date'])

# - agrégation simple : performance par canal -
perf_canal = df.groupby('channel').agg(
    nb_campagnes   = ('campaign_id', 'count'),
    spend_total    = ('spend', 'sum'),   
    revenue_total  = ('revenue', 'sum'),    
    conversions = ('conversions', 'sum'),
    ctr_moyen   = ('ctr', 'mean'),
    roas_moyen  = ('roas', 'mean')
).round(2)

print(perf_canal.sort_values('roas_moyen', ascending=False))

# ── Agrégation multi-niveaux : canal × pays ──────────────────────
# On regroupe sur deux colonnes simultanément
perf_canal_pays = df.groupby(['channel', 'country']).agg(
    spend_total   = ('spend',    'sum'),
    revenue_total = ('revenue', 'sum'),
    roas_moyen    = ('roas',  'mean'),  
).round(2)

# Trouver le meilleur ROAS par pays (indépendamment du canal)
meilleur_roas_pays = df.groupby('country')['roas'].mean().sort_values(ascending=False)
print(meilleur_roas_pays)

# ── Top 5 campagnes par revenue ──────────────────────────────────
cols = ['campaign_name', 'channel', 'country', 'revenue', 'roas']
top5 = df.nlargest(5, 'revenue')[cols]
print(top5)

# Tableau croisé : canal (lignes) × segment (colonnes) → ROAS moyen
tableau_roas = pd.pivot_table(
    df,
    values='roas',
    index='channel',
    columns='segment',
    aggfunc='mean'
).round(2)

print(tableau_roas) 

# Spend total par canal × pays
tableau_spend = pd.pivot_table(
    df,
    values='spend',
    index='channel',
    columns='country',
    aggfunc='sum',
    margins=True,          # ajouter une ligne de total général
    margins_name='Total'
).round(0)

print(tableau_spend)

# Définir la date comme index pour resample
df_ts = df.set_index('date').sort_index()

# ── Revenus par semaine ──────────────────────────────────────────
revenus_semaine = df_ts['revenue'].resample('W').sum()
print(revenus_semaine.tail(8))      # 8 dernières semaines

# ── Spend et revenue par mois ────────────────────────────────────
mensuel = df_ts[['spend', 'revenue', 'conversions']].resample('ME').sum()
# 'ME' = Month End — dernier jour du mois (pandas  
# Ancienne syntaxe : 'M' (toujours valide)

# Calculer le ROAS mensuel depuis les totaux mensuels
mensuel['roas_mensuel'] = (mensuel['revenue'] / mensuel['spend']).round(2)
print(mensuel.tail(6))             # 6 derniers mois

# ── Croiser resample et groupby ──────────────────────────────────
# Revenus mensuels par canal — un peu plus avancé
mensuel_canal = (
    df.groupby([pd.Grouper(key='date', freq='ME'), 'channel'])
    ['revenue'].sum().unstack()
)
print(mensuel_canal.tail(3))     

# ── Rapport de synthèse complet ──────────────────────────────────
print("="*50)
print("RAPPORT CAMPAIGNIQ — SYNTHÈSE")
print("="*50)
print(f"Période analysée : {df['date'].min().date()} → {df['date'].max().date()}")
print(f"Nombre de campagnes    : {len(df):,}")
print(f"Spend total            : {df['spend'].sum():,.0f} €")
print(f"Revenue total          : {df['revenue'].sum():,.0f} €")
print(f"ROAS global            : {df['revenue'].sum()/df['spend'].sum():.2f}")
print(f"Total conversions      : {df['conversions'].sum():,}")
print(f"CAC moyen              : {df['cac'].median():.2f} €")
print(f"Meilleur canal (ROAS)  : {df.groupby('channel')['roas'].mean().idxmax()}")
print(f"Meilleur pays (revenue): {df.groupby('country')['revenue'].sum().idxmax()}")