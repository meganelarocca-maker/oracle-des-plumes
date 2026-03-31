import requests
import psycopg2
import time
import os
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

# Recupere les livres sans couverture
conn = get_conn()
cursor = conn.cursor()
cursor.execute("SELECT id, titre, auteurs FROM livres WHERE cover_url IS NULL")
livres = cursor.fetchall()
cursor.close()
conn.close()

print(f"📚 {len(livres)} livres a enrichir")

enrichis = 0
non_trouves = 0

for i, (livre_id, titre, auteurs) in enumerate(livres):
    print(f"🔍 Traitement {i+1}/{len(livres)} : {titre[:40]}")
    try:
        r = requests.get(
            "https://openlibrary.org/search.json",
            params={"title": titre, "author": auteurs, "limit": 1},
            timeout=20
        )

        if r.status_code != 200:
            non_trouves += 1
            continue

        docs = r.json().get("docs", [])

        if not docs:
            non_trouves += 1
            continue

        doc = docs[0]
        cover_i = doc.get("cover_i")
        isbn = (doc.get("isbn") or [None])[0]

        if cover_i:
            cover_url = f"https://covers.openlibrary.org/b/id/{cover_i}-M.jpg"
        elif isbn:
            cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"
        else:
            non_trouves += 1
            continue

        # Commit livre par livre
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "UPDATE livres SET cover_url = %s, isbn = %s WHERE id = %s",
            (cover_url, isbn, livre_id)
        )
        conn.commit()
        cur.close()
        conn.close()

        enrichis += 1
        if enrichis % 10 == 0:
            print(f"⏳ {enrichis} couvertures trouvees...")

    except Exception as e:
        print(f"❌ {titre[:40]} : {e}")
        non_trouves += 1

    time.sleep(0.5)

print(f"✅ {enrichis} couvertures trouvees")
print(f"⚠️ {non_trouves} sans couverture")