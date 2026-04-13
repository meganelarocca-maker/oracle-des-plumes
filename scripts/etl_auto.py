import requests
import os
import time
import logging
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from src.db import query

load_dotenv()
API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
HARDCOVER_TOKEN = os.getenv("HARDCOVER_API_KEY")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger(__name__)


def get_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


def livre_existe(titre, auteurs, isbn=None):
    titre_safe = titre.replace("'", "''")
    auteurs_safe = auteurs.replace("'", "''")

    if isbn:
        result = query(f"SELECT COUNT(*) as nb FROM livres WHERE isbn = '{isbn}'")
    else:
        result = query(f"SELECT COUNT(*) as nb FROM livres WHERE titre = '{titre_safe}' AND auteurs = '{auteurs_safe}'")
    return result["nb"][0] > 0


def extraire_livres(annee):
    logger.info(f"Extraction Google Books pour {annee}...")

    tous_les_livres = []
    url = "https://www.googleapis.com/books/v1/volumes"

    queries = [
        f"novel {annee}",
        f"roman {annee}",
        f"novela {annee}",
        f"romanzo {annee}",
        f"Roman {annee}",
        f"romance {annee}",
        f"小説 {annee}",
        f"رواية {annee}",
        f"roman {annee}",
        f"powieść {annee}",
        f"roman {annee}",
        f"kitap {annee}",
    ]

    for q in queries:
        params = {
            "q": q,
            "maxResults": 40,
            "orderBy": "newest",
            "printType": "books",
            "key": API_KEY
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            items = response.json().get("items", [])
            tous_les_livres.extend(items)
            logger.info(f"  {q} → {len(items)} livres")
            time.sleep(1)
        except Exception as e:
            logger.error(f"Erreur extraction {q} : {e}")

    logger.info(f"Total extrait : {len(tous_les_livres)} livres")
    return tous_les_livres


def nettoyer_et_inserer(livres_bruts):
    logger.info("Nettoyage et insertion des nouveaux livres...")

    inseres = 0
    skips = 0

    for item in livres_bruts:
        info = item.get("volumeInfo", {})

        titre = info.get("title")
        auteurs = ", ".join(info.get("authors", []))
        date = info.get("publishedDate", "")[:4]
        editeur = info.get("publisher")
        langue = info.get("language")
        note = info.get("averageRating")
        nb_avis = info.get("ratingsCount")
        isbn_list = info.get("industryIdentifiers", [])
        isbn = next((i["identifier"] for i in isbn_list if i["type"] == "ISBN_13"), None)

        # Filtres qualite
        if not titre or not auteurs:
            skips += 1
            continue

        annee_courante = datetime.today().year
        if not date or int(date) < annee_courante - 2:  # Je garde une fenêtre glissante de 2 an
            skips += 1
            continue

        if livre_existe(titre, auteurs, isbn):
            skips += 1
            continue

        # Insertion
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO livres (titre, auteurs, date, editeur, langue, note, nb_avis, isbn)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (titre, auteurs, date or None, editeur, langue, note or None, nb_avis or None, isbn))
            conn.commit()
            cur.close()
            conn.close()
            inseres += 1
            logger.info(f"  ✅ Insere : {titre}")
        except Exception as e:
            logger.error(f"  ❌ Erreur insertion {titre} : {e}")

    logger.info(f"Inseres : {inseres} | Skips : {skips}")

def enrichir_hardcover():
    logger.info("Mise a jour notes/avis via Hardcover..")
    
    # Donc tous les livres — pas seulement ceux sans note
    df = query("SELECT id, titre FROM livres LIMIT 100")
    
    enrichis = 0
    
    for _, row in df.iterrows():
        query_gql = """
        query {
          books(
            where: {title: {_ilike: "%""" + row["titre"].replace('"', '') + """%"}}
            limit: 1
          ) {
            rating
            users_count
          }
        }
        """
        try:
            response = requests.post(
                "https://api.hardcover.app/v1/graphql",
                json={"query": query_gql},
                headers={
                    "Authorization": f"Bearer {HARDCOVER_TOKEN}",
                    "Content-Type": "application/json"
                },
                timeout=10
            )
            livres = response.json().get("data", {}).get("books", [])
            
            if livres and livres[0].get("rating"):
                note = livres[0]["rating"]
                nb_avis = livres[0]["users_count"]
                
                conn = get_conn()
                cur = conn.cursor()
                cur.execute(
                    "UPDATE livres SET note = %s, nb_avis = %s WHERE id = %s",
                    (note, nb_avis, row["id"])
                )
                conn.commit()
                cur.close()
                conn.close()
                enrichis += 1
            
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Erreur Hardcover {row['titre']} : {e}")
    
    logger.info(f"Notes enrichies : {enrichis}")

def enrichir_covers():
    logger.info("Enrichissement couvertures via Open Library...")
    
    df = query("SELECT id, titre, auteurs FROM livres WHERE cover_url IS NULL LIMIT 100")
    
    enrichis = 0
    
    for _, row in df.iterrows():
        try:
            response = requests.get(
                "https://openlibrary.org/search.json",
                params={
                    "title": row["titre"],
                    "author": row["auteurs"],
                    "limit": 1
                },
                timeout=15
            )
            
            if response.status_code != 200 or not response.text.strip():
                continue
                
            docs = response.json().get("docs", [])
            
            if not docs:
                continue
            
                    # Je filtre les éditeurs académiques et non-romanesques
            editeurs_exclus = ['springer', 'elsevier', 'wiley', 'archaeopress', 'sbl press', 
                            'crc press', 'narr francke', 'trans tech']
            if editeur and any(e in editeur.lower() for e in editeurs_exclus):
                skips += 1
                continue
            
            doc = docs[0]
            cover_i = doc.get("cover_i")
            isbn_list = doc.get("isbn", [])
            isbn = isbn_list[0] if isbn_list else None
            
            if cover_i:
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_i}-M.jpg"
            elif isbn:
                cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"
            else:
                continue
            
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(
                "UPDATE livres SET cover_url = %s, isbn = %s WHERE id = %s",
                (cover_url, isbn, row["id"])
            )
            conn.commit()
            cur.close()
            conn.close()
            enrichis += 1
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Erreur covers {row['titre']} : {e}")
    
    logger.info(f"Couvertures enrichies : {enrichis}")

def enrichir_wikidata():
    logger.info("Enrichissement auteurs via Wikidata...")
    
    df = query("SELECT DISTINCT auteurs FROM livres WHERE nationalite IS NULL LIMIT 50")
    
    enrichis = 0
    
    for _, row in df.iterrows():
        auteur = row["auteurs"].split(",")[0].strip()
        
        sparql_query = f"""
        SELECT ?nationaliteLabel ?naissance ?sexeLabel
        WHERE {{
          ?auteur wdt:P31 wd:Q5.
          ?auteur rdfs:label "{auteur}"@en.
          OPTIONAL {{ ?auteur wdt:P27 ?nationalite. }}
          OPTIONAL {{ ?auteur wdt:P569 ?naissance. }}
          OPTIONAL {{ ?auteur wdt:P21 ?sexe. }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "fr,en". }}
        }}
        LIMIT 1
        """
        
        try:
            response = requests.get(
                "https://query.wikidata.org/sparql",
                params={"query": sparql_query, "format": "json"},
                headers={
                    "Accept": "application/json",
                    "User-Agent": "OracleDesPlumes/1.0"
                },
                timeout=10
            )
            
            results = response.json().get("results", {}).get("bindings", [])
            
            if results:
                r = results[0]
                nationalite = r.get("nationaliteLabel", {}).get("value")
                naissance = r.get("naissance", {}).get("value", "")[:4]
                sexe = r.get("sexeLabel", {}).get("value")
                
                conn = get_conn()
                cur = conn.cursor()
                cur.execute(
                    "UPDATE livres SET nationalite = %s, naissance = %s, sexe = %s WHERE auteurs LIKE %s",
                    (nationalite, naissance or None, sexe, f"%{auteur}%")
                )
                conn.commit()
                cur.close()
                conn.close()
                enrichis += 1
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Erreur Wikidata {auteur} : {e}")
    
    logger.info(f"Auteurs enrichis : {enrichis}")

def run():
    logger.info("Debut du pipeline ETL automatise")

    annee = datetime.today().year
    livres_bruts = extraire_livres(annee)
    nettoyer_et_inserer(livres_bruts)
    enrichir_hardcover() 
    enrichir_covers()
    enrichir_wikidata()

    logger.info("Fin du pipeline ETL automatise")


if __name__ == "__main__":
    run()