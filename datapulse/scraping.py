import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
from sqlalchemy import create_engine

base_url = "http://quotes.toscrape.com"
all_quotes = []
page = 1

while True:
    url = f"{base_url}/page/{page}/"
    response = requests.get(url)
    if response.status_code != 200:
        break

    soup = BeautifulSoup(response.text, 'html.parser')
    quote_divs = soup.find_all("div", class_="quote")
    if not quote_divs:
        break

    for div in quote_divs:
        texte = div.find("span", class_="text").text.strip("“”")  # enlever les guillemets
        auteur = div.find("small", class_="author").text.strip()
        tags = [t.text for t in div.find_all("a", class_="tag")]
        all_quotes.append({"page": page, "texte": texte, "author": auteur, "tags": ", ".join(tags)})

    print(f"Page {page}: {len(quote_divs)} citations.")
    page += 1
    time.sleep(0.5)  # pour éviter de surcharger le serveur

df_quotes = pd.DataFrame(all_quotes)
df_quotes.to_csv("quotes.csv", index=False)
print(f"✅ {len(df_quotes)} citations → quotes.csv")

engine = create_engine("postgresql+psycopg2://postgres:@localhost:5432/campaigniq")
df_quotes.to_sql("quotes", con=engine, if_exists="replace", index=False)

print("Table 'quotes' chargée dans PostgreSQL")
engine.dispose()
print("Connexion fermée")

