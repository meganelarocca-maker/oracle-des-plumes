# Enrichissement Couvertures & ISBN
## L'Oracle des Plumes — DataMuse
## Date : Mars 2026

---

## Contexte

Apres construction du dataset principal (1 395 livres), une phase d'enrichissement a ete menee pour recuperer les couvertures de chaque livre et les stocker directement dans PostgreSQL. L'objectif est d'alimenter la page Catalogue du dashboard sans appel API en temps reel.

---

## Modifications du schema PostgreSQL

Deux colonnes ont ete ajoutees a la table `livres` :

```sql
ALTER TABLE livres ADD COLUMN cover_url TEXT;
ALTER TABLE livres ADD COLUMN isbn TEXT;
```

| Colonne | Type | Description |
|---|---|---|
| `cover_url` | TEXT | URL de la couverture du livre |
| `isbn` | TEXT | Identifiant ISBN du livre |

---

## Pipeline d'enrichissement

### Phase 1 — Google Books API

**Script :** `src/enrich_covers.py`  
**Source :** API Google Books (REST)  
**Methode :** Recherche par `intitle` + `inauthor`

```
https://www.googleapis.com/books/v1/volumes?q=intitle:{titre}+inauthor:{auteur}
```

**Resultat :** 861 couvertures trouvees sur 1 395 livres

---

### Phase 2 — Open Library API

**Script :** `src/enrich_covers_v2.py`  
**Source :** API Open Library (REST, sans cle)  
**Methode :** Recherche par `title` + `author`

```
https://openlibrary.org/search.json?title={titre}&author={auteur}
```

Deux strategies de recuperation de couverture :
- Via `cover_i` → `https://covers.openlibrary.org/b/id/{cover_i}-M.jpg`
- Via `isbn` → `https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg`

**Resultat :** ~180 couvertures supplementaires trouvees sur les 534 restants

---

## Resultats finaux

| Indicateur | Valeur |
|---|---|
| Livres avec couverture | ~1 041 |
| Livres sans couverture | ~354 |
| Taux de couverture | ~75% |

### Pourquoi 25% sans couverture ?

Les livres sans couverture sont majoritairement :
- Des titres tres recents (2024-2025) non encore indexes
- Des auteurs emergents peu references numeriquement
- Des titres en japonais ou arabe mal reconnus par les APIs

Ce resultat est coherent avec le caractere emergent des auteurs du dataset.

---

## Gestion des livres sans couverture

Une image placeholder a ete creee et integree dans les assets du dashboard :

**Fichier :** `assets/no_cover.png`  
**Style :** Bibliotheque fantasy, plume doree sur fond parchemin  
**Usage :** Affichee automatiquement quand `cover_url IS NULL`

---

## Schema SQL mis a jour

```sql
CREATE TABLE livres (
    id          SERIAL PRIMARY KEY,
    titre       TEXT,
    auteurs     TEXT,
    date        INTEGER,
    editeur     TEXT,
    langue      VARCHAR(10),
    note        NUMERIC(4,2),
    nb_avis     INTEGER,
    nationalite TEXT,
    naissance   INTEGER,
    sexe        TEXT,
    cover_url   TEXT,
    isbn        TEXT
);
```

---

## Commit Git associe

```
git commit -m "Enrichissement couvertures + ISBN - Google Books + Open Library"
```

---

*Documentation produite dans le cadre du projet L'Oracle des Plumes — DataMuse pour Editions Novae.*
