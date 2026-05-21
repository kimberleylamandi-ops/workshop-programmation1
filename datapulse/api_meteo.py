import requests
import pandas as pd

capitales = {
    "France": (48.8566,  2.3522),
    "Germany": (52.5200, 13.4050),
    "Spain": (40.4168, -3.7038),
    "Italy": (41.9028, 12.4964),
    "Netherlands": (52.3676,  4.9041),
}

rows = []

for pays, (lat, lon) in capitales.items():
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,precipitation"
    )
    r = requests.get(url).json()
    rows.append({
        "country"         : pays,
        "temperature_c"   : r["current"]["temperature_2m"],
        "precipitation_mm": r["current"]["precipitation"],
    })
    print(f"  {pays} : {r['current']['temperature_2m']}°C")

df_meteo = pd.DataFrame(rows)
df_meteo.to_csv("meteo.csv", index=False)
