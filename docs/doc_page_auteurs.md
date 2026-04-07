# Page Auteurs Emergents — Documentation
## L'Oracle des Plumes — DataMuse
## Date : Avril 2026

---

## Objectif de la page

La page Auteurs Emergents est le coeur metier du projet. Elle permet a un editeur d'identifier rapidement les auteurs a fort potentiel editorial grace a un score composite objectif et mesurable. C'est un veritable outil d'aide a la decision — pas un simple classement.

---

## Fonctionnalites implementees

### Filtres dynamiques
Deux filtres disponibles en bandeau :
- **Nationalite** — menu deroulant, options recuperees dynamiquement depuis PostgreSQL
- **Niveau d'emergence** — menu deroulant avec 3 categories fixes

### Tableau de classement
- Tri possible sur toutes les colonnes (`sort_action="native"`)
- Pagination 20 lignes par page
- Couleurs conditionnelles par niveau d'emergence
- Colonnes : Auteur, Nationalite, Dernier livre, Nb livres, Note moyenne, Total avis, Score, Statut Wikidata, Niveau emergence

### Export CSV
- Bouton "Exporter CSV" — telecharge le tableau filtre
- Le fichier exporte respecte les filtres actifs
- Nom du fichier : `auteurs_emergents.csv`

---

## Score d'emergence — Methodologie

```
Score = AVG(note) x LOG(SUM(nb_avis) + 1) / COUNT(livres)
```

| Composante | Role |
|---|---|
| AVG(note) | Qualite percue par les lecteurs |
| LOG(SUM(nb_avis) + 1) | Popularite lissee — evite de sur-valoriser les volumes extremes |
| / COUNT(livres) | Penalisation prolifique — favorise les auteurs peu publies |

### Criteres de selection

| Critere | Valeur | Justification |
|---|---|---|
| note >= 4.2 | Seuil qualite eleve | On ne recommande que des auteurs bien recus |
| nb_avis BETWEEN 30 AND 300 | Fenetre emergence | Assez connu pour avoir des lecteurs, pas encore mainstream |
| nb_livres <= 2 | Rarete | Un auteur avec peu de publications est plus emergent |
| date >= 2023 | Recence | On cible la production recente uniquement |

### Niveaux d'emergence

| Niveau | Critere | Interpretation |
|---|---|---|
| Signal faible — tres emergent | nb_avis < 100 | Pépite rare, peu de lecteurs encore |
| Signal moyen — emergent confirme | nb_avis BETWEEN 100 AND 300 | Commence a percer, moment ideal pour contacter |
| Signal fort — commence a percer | nb_avis > 300 | Deja repere, agir vite |

---

## Architecture technique

### Fichiers concernes
- `pages/auteurs.py` — logique Python, layout et callbacks

### Callbacks

| Callback | Inputs | Output | Role |
|---|---|---|---|
| `afficher_auteurs` | filtre-nationalite, filtre-emergence | tableau-auteurs | Affiche le tableau filtre |
| `exporter_csv` | btn-export, filtres | download-csv | Telecharge le CSV |

### Fonction partagee
La fonction `get_df(nationalite, emergence)` centralise la requete SQL et les filtres Pandas — utilisee par les deux callbacks pour eviter la duplication de code.

### Requete SQL principale
```sql
SELECT 
    l.auteurs, l.nationalite, l.langue,
    MAX(l.date) as dernier_livre,
    COUNT(*) as nb_livres,
    ROUND(AVG(l.note)::numeric, 2) as note_moyenne,
    SUM(l.nb_avis) as total_avis,
    ROUND((AVG(l.note) * LOG(SUM(l.nb_avis) + 1) / COUNT(*))::numeric, 2) as score_emergence,
    CASE WHEN l.nationalite IS NOT NULL THEN 'Reference Wikidata' ELSE 'Non reference Wikidata' END as statut_wikidata,
    CASE
        WHEN SUM(l.nb_avis) < 100 THEN 'Signal faible — tres emergent'
        WHEN SUM(l.nb_avis) BETWEEN 100 AND 300 THEN 'Signal moyen — emergent confirme'
        ELSE 'Signal fort — commence a percer'
    END as niveau_emergence
FROM livres l
WHERE l.note IS NOT NULL AND l.date >= '2023'
GROUP BY l.auteurs, l.nationalite, l.langue
HAVING COUNT(*) <= 2 AND SUM(l.nb_avis) BETWEEN 30 AND 300 AND AVG(l.note) >= 4.2
ORDER BY score_emergence DESC
LIMIT 50
```

---

## Proposition de valeur client

L'Oracle des Plumes ne remplace pas le flair editorial — il l'alimente avec des donnees objectives avant que la concurrence ne repere les memes auteurs.

Par rapport aux outils existants :
- **Babelio / Goodreads** — plateformes de lecteurs, pas d'analyse ni de scoring
- **Electre** — base de donnees payante, sans scoring automatique
- **Intuition editoriale** — subjective et non reproductible

L'Oracle apporte un signal objectif, filtrable, exportable et mis a jour automatiquement.

---

## Limites connues
- Biais anglophone — majorite des auteurs identifies ecrivent en anglais
- Absence de donnees contractuelles — un auteur emergent peut deja etre sous contrat
- Le score ne prend pas en compte la dynamique temporelle (auteur en progression vs en stagnation)
- LIMIT 50 dans la requete — les auteurs au-dela du top 50 ne sont pas vus

---

*Documentation produite dans le cadre du projet L'Oracle des Plumes — DataMuse pour Editions Novae.*
