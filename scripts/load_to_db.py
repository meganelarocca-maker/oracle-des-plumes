# L'ORACLE DES PLUMES — Chargement dataset dans PostgreSQL

import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv


# Chargement des variables d'environnement (.env)
load_dotenv()

# Connexion à PostgreSQL
conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)

print("✅ Connexion PostgreSQL établie")

# Lecture du dataset
df = pd.read_csv("data/clean/dataset_final_v2.csv")
print(f"📊 Dataset chargé : {df.shape[0]} lignes")

# -----------------------------
# Nettoyage / conversion des types
# -----------------------------

# Colonnes entières nullable
df["date"] = pd.to_numeric(df["date"], errors="coerce").astype("Int64")
df["nb_avis"] = pd.to_numeric(df["nb_avis"], errors="coerce").astype("Int64")
df["naissance"] = pd.to_numeric(df["naissance"], errors="coerce").astype("Int64")

# Colonne décimale
df["note"] = pd.to_numeric(df["note"], errors="coerce")

# Remplacer les valeurs manquantes pandas par None
# pour obtenir des NULL dans PostgreSQL
df = df.astype(object).where(pd.notnull(df), None)

print("\n🔎 Types après conversion :")
print(df.dtypes)

# -----------------------------
# Insertion dans PostgreSQL
# -----------------------------
cursor = conn.cursor()
inserted = 0

for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO livres (
            titre, auteurs, date, editeur, langue,
            note, nb_avis, nationalite, naissance, sexe
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row["titre"],
        row["auteurs"],
        row["date"],
        row["editeur"],
        row["langue"],
        row["note"],
        row["nb_avis"],
        row["nationalite"],
        row["naissance"],
        row["sexe"]
    ))
    inserted += 1

conn.commit()
cursor.close()
conn.close()

print(f"\n✅ {inserted} livres insérés dans PostgreSQL")