# Documentation Déploiement — L'Oracle des Plumes
## Date : Avril 2026

---

## Stack de déploiement

| Composant | Service |
|---|---|
| Application | Render (free tier) |
| Base de données | Supabase (PostgreSQL) |
| Branche de prod | `main` |
| Branche de dev | `dev` |

---

## Déploiement Render

### Configuration
- **Start command** : `python app.py`
- **Port** : variable d'environnement `PORT` (auto-détecté par Render)
- **Déploiement automatique** : activé sur push `dev` puis merge sur `main`

### Variables d'environnement
| Variable | Description |
|---|---|
| `POSTGRES_HOST` | Host pooler Supabase |
| `POSTGRES_PORT` | 5432 (géré en dur dans db.py → 6543) |
| `POSTGRES_DB` | postgres |
| `POSTGRES_USER` | postgres.xxxx (format pooler) |
| `POSTGRES_PASSWORD` | Mot de passe Supabase |
| `GOOGLE_BOOKS_API_KEY` | Clé API Google Books |
| `HARDCOVER_API_KEY` | Token JWT Hardcover |

---

## Connexion base de données

### Choix technique : Pooler Supabase
Render utilise IPv6 — la connexion directe Supabase (port 5432) échoue 
avec une erreur DNS. Le port pooler (6543) est forcé directement dans 
`src/db.py` car Render ne permet pas de modifier le port dans ses variables.

```python
# Je force le port pooler Supabase — Render impose le port 5432 en variable
port=6543
```

---

## Choix techniques notables

### Options filtres dynamiques (catalogue.py)
Les options des dropdowns (langue, année) sont chargées via callback Dash 
et non au démarrage du module. Ce choix garantit que les données sont 
toujours à jour sans redémarrage de l'app — essentiel en production après 
un data cleaning ou un ETL.

### KPIs dynamiques (accueil.py)
Les KPIs sont rechargés toutes les 60 secondes via `dcc.Interval` — 
ils reflètent toujours l'état réel de la base sans redémarrage.

---

## Migration Supabase
La migration de la base locale vers Supabase est documentée dans 
`docs/doc_migration_supabase.md`.

---

## Merge final
```bash
# Quand dev est stable
git checkout main
git merge --squash dev
git commit -m "Release - L'Oracle des Plumes v1.0"
git push origin main
```

---

*Documentation produite dans le cadre du projet L'Oracle des Plumes — DataMuse.*