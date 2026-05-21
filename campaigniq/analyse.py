import pandas as pd 
import numpy as np

# Lire le CSV généré
df = pd.read_csv('campaigns.csv')

print("Dimensions :", df.shape) #(5050, 11)
print(df.head()) # 5 premières lignes
print(df.info()) # types de données et valeurs manquantes
print(df.describe()) # statistiques descriptives
print(df.isnull().sum()) # nombre de valeurs manquantes par colonne
print(df.duplicated().sum()) # nombre de lignes dupliquées