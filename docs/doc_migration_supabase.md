# Migration Base de Données — Supabase Cloud
## L'Oracle des Plumes — DataMuse
## Date : Avril 2026

---

## Contexte

La base de données PostgreSQL etait jusqu'alors hebergee localement via Docker. Pour permettre le deploiement de l'application sur Render et rendre le dashboard accessible en ligne, la base a ete migree vers Supabase — une solution PostgreSQL cloud gratuite.

---

## Ce qui a change

| Avant | Apres |
|---|---|
| PostgreSQL local via Docker | PostgreSQL cloud via Supabase |
| Accessible uniquement en local | Accessible depuis n'importe où |
| Dependant du PC allume | Disponible 24h/24 |
| `localhost:5432` | `db.zuhdymnaymxlslswxlep.supabase.co:5432` |

---

## Etapes de migration

**1. Creation du projet Supabase**
- Projet : `Oracle_des_plumes`
- Region : Europe
- Base de donnees : `postgres`

**2. Creation du schema**
Le schema SQL a ete execute directement dans l'editeur SQL de Supabase :
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

**3. Export depuis Docker**
```bash
docker exec oracle_des_plumes_db psql -U datamuse -d oracle_des_plumes -c "\COPY livres TO '/var/lib/postgresql/livres.csv' WITH CSV HEADER"
docker cp oracle_des_plumes_db:/var/lib/postgresql/livres.csv ./livres.csv
```

**4. Import dans Supabase**
Import du fichier `livres.csv` via l'interface Table Editor de Supabase.
1 416 lignes importees avec succes.

**5. Mise a jour du .env**
```env
POSTGRES_HOST=db.zuhdymnaymxlslswxlep.supabase.co
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=***
```

---

## Dataset de reference

Le fichier `data/clean/livres.csv` est l'export propre de la base PostgreSQL — types corrects, pas de valeurs flottantes dans les colonnes entieres. C'est la reference pour toute reimportation eventuelle.

---

## Verification

Le dashboard a ete teste et fonctionne correctement avec la base Supabase — toutes les pages s'affichent, les filtres fonctionnent et l'export CSV est operationnel.

---

## Prochaine etape

Deploiement du dashboard sur Render connecte a Supabase.

---

*Documentation produite dans le cadre du projet L'Oracle des Plumes — DataMuse pour Editions Novae.*
