from sqlalchemy import create_engine, text
import pandas as pd

df = pd.read_csv('campaigns_clean.csv')

# ── Créer le moteur de connexion à PostgreSQL Portable ──────────
# Format de l'URL : dialect+driver: user:password@host:port/database
engine = create_engine(
    "postgresql+psycopg2://postgres:@localhost:5432/campaigniq"
)

# Tester la connexion
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print("Connexion OK —", result.fetchone()[0])
except Exception as e:
    print("Erreur de connexion :", e)

# ── Charger le DataFrame nettoyé dans PostgreSQL ────────────────
df.to_sql(
    name='campaigns',   # nom de la table à créer    
    con=engine,    # moteur SQLAlchemy          
    if_exists='replace',    # 'replace' : supprimer et recréer si existe déjà
    index=False,   # ne pas écrire l'index pandas comme colonne         
    chunksize=500,           # insérer par lots de 500 lignes (plus stable)
    method='multi' # insertion multi-valeurs — plus rapide
)
print("Table 'campaigns' chargée dans PostgreSQL ✅")

sql = (
    "SELECT channel, COUNT(*) as nb,"
    "ROUND(AVG(roas)::numeric, 2) as roas_moyen "
    "FROM campaigns GROUP BY channel ORDER BY roas_moyen DESC"
)
df_check = pd.read_sql(sql,
    con=engine
)
print(df_check)

# Compter le nombre total de lignes
nb_lignes = pd.read_sql("SELECT COUNT(*) as total FROM campaigns", con=engine)
print(f"Total lignes en base : {nb_lignes['total'][0]}")

engine.dispose()
print("Connexion fermée")