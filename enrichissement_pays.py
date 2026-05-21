import pandas as pd

df_meteo = pd.read_csv("meteo.csv")
df_countries = pd.read_csv("countries.csv")
df_taux = pd.read_csv("taux_change.csv")

# Jointure des données météo avec les pays
df_ref = df_meteo.merge(df_countries, on="country", how="left")

# Ajout des taux de change EUR/USD (même valeur pour tous les pays)
df_ref["eur_usd_rate"] = df_taux["USD"].iloc[0]
df_ref["pop_density"] = (df_ref["population"] / df_ref["area_km2"]).round(1)    

# Sauvegarde du résultat
print(df_ref[["country", "temperature_c", "population", "eur_usd_rate"]])
df_ref.to_csv("pays_reference.csv", index=False)
print(" ✅ pays_reference.csv créé avec succès !")