# Script ETL Automatise — Documentation
## L'Oracle des Plumes — DataMuse
## Date : Avril 2026

---

## Objectif

Maintenir le dataset a jour en detectant et inserant automatiquement les nouveaux romans publies, puis en enrichissant les donnees manquantes (notes, couvertures, informations auteurs).

---

## Fichier concerne

`scripts/etl_auto.py`

---

## Pipeline d'execution

```
1. extraire_livres(annee)      → Google Books API
2. nettoyer_et_inserer()       → Deduplication + insertion PostgreSQL
3. enrichir_hardcover()        → Notes et avis via Hardcover GraphQL
4. enrichir_covers()           → Couvertures via Open Library
5. enrichir_wikidata()         → Nationalite, naissance, sexe via SPARQL
```

---

## Detail des fonctions

### extraire_livres(annee)
Interroge Google Books avec des requetes multilingues pour l'annee en cours.

Langues couvertes : anglais, francais, espagnol, italien, allemand, portugais, japonais, arabe, neerlandais, polonais, turc.

Retourne une liste de livres bruts au format JSON.

### nettoyer_et_inserer(livres_bruts)
Pour chaque livre extrait :

1. Extraction des metadonnees (titre, auteurs, date, editeur, langue, note, isbn)
2. Filtres qualite :
   - Titre et auteur obligatoires
   - Date >= annee en cours (livres recents uniquement)
3. Verification d'unicite avant insertion :
   - Si ISBN present → recherche par ISBN
   - Si pas d'ISBN → recherche par titre + auteurs
4. Insertion dans PostgreSQL si le livre n'existe pas encore

### enrichir_hardcover()
Interroge Hardcover via GraphQL pour recuperer les notes et avis des livres sans note dans la base.

Limite : 100 livres par execution pour ne pas surcharger l'API.

### enrichir_covers()
Interroge Open Library pour recuperer les URLs de couvertures des livres sans image.

Deux strategies : via `cover_i` ou via `isbn`.
Limite : 100 livres par execution.

### enrichir_wikidata()
Interroge Wikidata via SPARQL pour enrichir les auteurs sans nationalite.

Limite : 50 auteurs par execution.

---

## Deduplication — logique detaillee

```python
# Si ISBN disponible
SELECT COUNT(*) FROM livres WHERE isbn = 'XXXXXXX'

# Si pas d'ISBN
SELECT COUNT(*) FROM livres WHERE titre = '...' AND auteurs = '...'
```

Si le resultat est > 0 → le livre existe, on skip.
Si le resultat est 0 → nouveau livre, on insere.

---

## Lancement

```bash
# Lancement manuel
python -m scripts.etl_auto

# Frequence recommandee : toutes les 2 semaines
# Periode privilegiee : rentrees litteraires (janvier, septembre)
```

---

## Logs

Le script genere des logs horodates dans le terminal :

```
2026-04-07 16:27:43 — INFO — Debut du pipeline ETL automatise
2026-04-07 16:27:44 — INFO — Extraction Google Books pour 2026...
2026-04-07 16:27:45 — INFO — Inseres : 0 | Skips : 220
2026-04-07 16:27:45 — INFO — Enrichissement notes/avis via Hardcover...
```

---

## Resultats du premier run (07/04/2026)

| Etape | Resultat |
|---|---|
| Livres extraits | 220 |
| Livres inseres | 0 (deja presents en base) |
| Livres skips | 220 |
| Notes enrichies | En cours |
| Couvertures enrichies | En cours |
| Auteurs enrichis | En cours |

---

## Limites connues

**Deduplication**
- Les livres sans ISBN sont dedupliques par titre + auteur — une variation orthographique peut creer un doublon
- Les apostrophes dans les titres sont echappees mais d'autres caracteres speciaux peuvent poser probleme

**Enrichissement**
- `enrichir_covers` et `enrichir_hardcover` enrichissent tous les livres sans donnees dans la base — pas uniquement les nouveaux inseres
- Si une note ou couverture existante est erronee, le script ne la corrige pas — il ne met a jour que les valeurs NULL
- Limite de 100 livres par execution pour les enrichissements — les bases tres grandes necessiteraient plusieurs executions

**Sources**
- Google Books indexe mal certains livres recents — des faux positifs (vieux livres, catalogues) peuvent s'inserer malgre le filtre de date
- Hardcover est principalement anglophone — peu de notes pour les livres non anglophones
- Open Library couvre environ 40% des nouveaux titres

**Automatisation**
- Le script est actuellement lance manuellement
- Prochaine etape : integration avec Apache Airflow pour une execution planifiee toutes les 2 semaines
- En production : deploiement via cron job Linux ou Airflow DAG

---

## Prochaines etapes

- Integrer Apache Airflow pour l'automatisation planifiee
- Ajouter une source francophone (Babelio scraping)
- Sauvegarder les logs dans un fichier dans `logs/`
- Alertes email en cas d'erreur


## Data Cleaning — Suppression livres non-romanesques (Avril 2026)

### Contexte
Lors de l'analyse du catalogue, 32 livres non-romanesques ont été identifiés
et supprimés de la base : actes de conférence, manuels académiques, guides
astronomiques, annuaires politiques et manuels médicaux.

### Méthode
Identification par éditeur (Springer, Archaeopress, Elsevier, SBL Press, CRC Press)
et par titre (proceedings, guide to the night sky, automation, computer vision).

### Impact
| Avant | Après |
|---|---|
| 1384 livres | 1384 livres |
| 1121 auteurs | À vérifier |

### Requête exécutée
```sql
DELETE FROM livres
WHERE id IN (
    2791, 2793, 2800, 2802, 2816, 2817, 2824, 2825, 2872, 2890,
    2919, 3706, 3700, 3702, 3710, 3712, 3715, 3716, 4187, 2792,
    2803, 2806, 2809, 2818, 2819, 2821, 2822, 2869, 2891, 2972,
    3718, 3868
);
```

## Fix Signal Fort — Auteurs Emergents (Avril 2026)
Correction du filtre HAVING qui limitait nb_avis à 300 max, 
rendant le niveau "Signal fort" inaccessible. 
Limite relevée à 100 auteurs affichés.

### Prévention future
Ajouter dans `nettoyer_et_inserer()` un filtre sur les éditeurs académiques
connus pour éviter leur insertion lors des prochains runs ETL.-FAIT S


*Documentation produite dans le cadre du projet L'Oracle des Plumes — DataMuse pour Editions Novae.*