from erreur_api.gestion_erreurs_api import get_api

url = "https://api.frankfurter.dev/v2/rates?base=EUR&symbols=USD,GBP,CHF,JPY"

print("test URL")
data = get_api(url)

print(f"Résultat stocké dans la variable 'data' : {data}")