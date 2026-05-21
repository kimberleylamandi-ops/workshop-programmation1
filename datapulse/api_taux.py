import requests, pandas as pd

url = "https://api.frankfurter.dev/v1/latest?base=EUR&symbols=USD,GBP,CHF,JPY"
data = requests.get(url).json()
print(f"Date des taux : {data['date']}")
print(data["rates"])

df_taux = pd.DataFrame([{"date": data["date"], **data["rates"]}])
df_taux.to_csv("taux_change.csv", index=False)

# Taux historique — comparaison sur 1 an
url_h = "https://api.frankfurter.dev/v1/2024-01-15?base=EUR&symbols=USD"
data_h = requests.get(url_h).json()
taux_actuel = data["rates"]["USD"]
taux_ancien = data_h["rates"]["USD"]

variation = ((taux_actuel - taux_ancien) / taux_ancien) * 100
print(f"Variation EUR/USD sur 1 an : {variation:+.2f}%")