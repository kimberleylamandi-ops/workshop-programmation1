import pandas as pd
import requests
from datetime import date
from sqlalchemy import create_engine
from datetime import date

aujourd_hui = date.today().strftime("%d/%m/%Y")

# 1. Charger le dataset NovaBrand
df = pd.read_csv("campaigns_clean.csv")
df["date"] = pd.to_datetime(df["date"])

# 2. Agréger par pays — 7 derniers jours
date_limite = df["date"].max() - pd.Timedelta(days=7)
df_s = df[df["date"] >= date_limite]
kpi_pays = df_s.groupby("country").agg(
    nb_campagnes  = ("campaign_id", "count"),
    spend_eur     = ("spend",  "sum"),     
    revenue_eur   = ("revenue",    "sum"),
    conversions   = ("conversions", "sum"),
    roas_moyen    = ("roas",  "mean"),      
).round(2).reset_index()

# 3. Taux de change EUR/USD
taux_data = requests.get(
    "https://api.frankfurter.dev/v1/2024-01-15?base=EUR&symbols=USD"
).json()
taux_usd = taux_data["rates"]["USD"]
kpi_pays["spend_usd"]   = (kpi_pays["spend_eur"]   * taux_usd).round(2)
kpi_pays["revenue_usd"] = (kpi_pays["revenue_eur"] * taux_usd).round(2)

# 4. Météo actuelle par capitale
capitales = {
    "France": (48.8566, 2.3522), "Germany": (52.52, 13.405),
    "Spain": (40.4168, -3.7038), "Italy": (41.9028, 12.4964),
    "Netherlands": (52.3676, 4.9041),
}
meteo_rows = []
for pays, (lat, lon) in capitales.items():
    r = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,precipitation"
    ).json()
    meteo_rows.append({"country": pays,
                        "temperature_c": r["current"]["temperature_2m"],
                        "precipitation_mm": r["current"]["precipitation"]})
df_meteo = pd.DataFrame(meteo_rows) 

# 5. Merger tout ensemble
rapport = kpi_pays.merge(df_meteo, on="country", how="left")
rapport["taux_eur_usd"] = taux_usd
rapport["date_rapport"] = str(date.today())
rapport = rapport.sort_values("revenue_eur", ascending=False)
print(rapport)

rapport.to_csv("rapport_enrichi.csv", index=False)
print(f"✅ rapport_enrichi.csv ({len(rapport)} lignes)")

lignes = [
    f"══════════════════════════════════════",
    f"  RAPPORT NOVABRAND — {aujourd_hui}",
    f"══════════════════════════════════════",
    "",
    f"  Taux EUR/USD : {taux_usd} (BCE)",
    f"  Campagnes    : {len(df_s)}",
    "",
    f"  {'PAYS':<14} {'SPEND €':>9} {'REVENUE €':>11} {'ROAS':>6} {'T°':>5}",
    f"  {'─'*48}",
]
for _, row in rapport.iterrows():
    lignes.append(
        f" {row['country']:<14} {row['spend_eur']:>9,.0f}"
        f" {row['revenue_eur']:>11,.0f} {row['roas_moyen']:>6.2f}"
        f" {row['temperature_c']:>4.1f}°C"
    )
lignes += [
    f"  {'─'*48}", "",
    f"  TOTAL SPEND   : {rapport['spend_eur'].sum():,.0f} EUR",
    f"  TOTAL REVENUE : {rapport['revenue_eur'].sum():,.0f} EUR",
    f"  ROAS GLOBAL   : {rapport['revenue_eur'].sum()/rapport['spend_eur'].sum():.2f}",
]

rapport_texte = "\n".join(lignes)
with open("rapport_semaine.txt", "w", encoding="utf-8") as f:
    f.write(rapport_texte)
print("✅ rapport_semaine.txt généré")

engine = create_engine("postgresql+psycopg2://postgres:@localhost:5432/campaigniq")
rapport.to_sql("rapport_hebdo", con=engine, if_exists="replace", index=False)
print("✅ Table rapport_hebdo chargée")
engine.dispose()
print("Connexion fermée")