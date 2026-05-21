import requests
import pandas as pd 


pays_novabrand = ["France", "Germany", "Spain", "Italy", "Netherlands"]
rows = []

for pays in pays_novabrand:
# L'unique ajustement pour éviter l'erreur sur les Pays-Bas
    if pays == "Netherlands":
        url = "https://restcountries.com/v3.1/alpha/NLD?fields=name,population,area,currencies,languages"
        data = requests.get(url).json()
        # data = requests.get(url).json()
    else:
        url = f"https://restcountries.com/v3.1/name/{pays}?fields=name,population,area,currencies,languages"
        data = requests.get(url).json()[0]
        # data = requests.get(url).json()[0]
    rows.append({
            "country"   : pays,
            "population": data["population"],
            "area_km2"  : data["area"],
            "currency"  : ", ".join(data["currencies"].keys()),
        "languages" : ", ".join(data["languages"].values()),
})
        
df_countries = pd.DataFrame(rows)
df_countries.to_csv("countries.csv", index=False)
print(f"✅ {len(df_countries)} pays → countries.csv")   