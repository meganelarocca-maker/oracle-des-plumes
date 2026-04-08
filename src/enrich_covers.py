# ============================================================
# L'ORACLE DES PLUMES — Enrichissement couvertures Google Books
# ============================================================

import requests
import psycopg2
import time
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)
cursor = conn.cursor()

# On recupere tous les livres sans couverture
cursor.execute("SELECT id, titre, auteurs FROM livres WHERE cover_url IS NULL")
livres = cursor.fetchall()
print(f"📚 {len(livres)} livres à enrichir")

enrichis = 0
non_trouves = 0

for livre_id, titre, auteurs in livres:
    try:
        params = {
            "q": f"intitle:{titre} inauthor:{auteurs}",
            "maxResults": 1,
            "key": API_KEY
        }
        response = requests.get("https://www.googleapis.com/books/v1/volumes", params=params, timeout=5)
        data = response.json()
        items = data.get("items", [])

        if items:
            image_links = items[0].get("volumeInfo", {}).get("imageLinks", {})
            cover_url = image_links.get("thumbnail") or image_links.get("smallThumbnail")

            if cover_url:
                cursor.execute("UPDATE livres SET cover_url = %s WHERE id = %s", (cover_url, livre_id))
                enrichis += 1
                if enrichis % 10 == 0:
                    print(f"⏳ {enrichis} couvertures trouvees...")
            else:
                non_trouves += 1
        else:
            non_trouves += 1

        time.sleep(0.3)

    except Exception as e:
        print(f"❌ Erreur pour {titre} : {e}")
        non_trouves += 1

conn.commit()
cursor.close()
conn.close()

print(f"✅ {enrichis} couvertures trouvees")
print(f"⚠️ {non_trouves} livres sans couverture")