# Page Catalogue — Documentation
## L'Oracle des Plumes — DataMuse
## Date : Avril 2026

---

## Objectif de la page

La page catalogue permet d'explorer visuellement l'ensemble des romans du dataset. Elle est pensée comme une vitrine editoriale — l'utilisateur parcourt les couvertures, filtre selon ses criteres et survole une carte pour obtenir les details d'un livre.

---

## Fonctionnalites implementees

### Filtres dynamiques
Trois filtres disponibles en bandeau en haut de page :
- **Langue** — menu deroulant, options recuperees dynamiquement depuis PostgreSQL
- **Annee** — menu deroulant, options recuperees dynamiquement depuis PostgreSQL
- **Note minimale** — slider de 0 a 5 par pas de 0.5

Les filtres sont connectes a PostgreSQL via des callbacks Dash. La requete SQL est construite dynamiquement selon les selections de l'utilisateur.

### Grille de couvertures
- Affichage en grille flexible (flexbox)
- 27 livres par page
- Couvertures recuperees depuis la colonne `cover_url` de PostgreSQL
- Image placeholder `no_cover.png` affichee si `cover_url` est NULL (25% des livres)
- Melange aleatoire des livres via `ORDER BY RANDOM()`

### Pagination
- Boutons Precedent / Suivant
- Indicateur de page courante
- Gestion via `dcc.Store` et callback dedie
- Offset SQL calcule dynamiquement : `LIMIT 27 OFFSET page * 27`

### Tooltip au survol
- Affichage des details au passage de la souris sur une couverture
- Implementé via CSS (`assets/catalogue.css`) sans JavaScript
- Informations affichees : titre, auteur, note, nationalite, annee, nombre d'avis
- Style : fond berry semi-transparent, police Georgia, texte creme

---

## Architecture technique

### Fichiers concernes
- `pages/catalogue.py` — logique Python et layout Dash
- `assets/catalogue.css` — styles tooltip et carte

### Callbacks
| Callback | Inputs | Output | Role |
|---|---|---|---|
| `changer_page` | btn-precedent, btn-suivant, filtres | page-courante | Gere la pagination |
| `afficher_livres` | filtres, page-courante | grille-livres, numero-page | Affiche les cartes |

### Requete SQL principale
```sql
SELECT titre, auteurs, nationalite, date, editeur, cover_url, note, nb_avis
FROM livres
WHERE 1=1
[AND langue = '...']
[AND date = '...']
[AND note >= ...]
ORDER BY RANDOM()
LIMIT 27 OFFSET {page * 27}
```

---

## Choix techniques

**Pourquoi 27 livres par page ?**
27 = 9 x 3 — permet d'avoir des lignes completes avec des cartes de 220px sur un ecran large.

**Pourquoi ORDER BY RANDOM() ?**
Pour melanger les livres avec et sans couverture et eviter des blocs de placeholders peu esthetiques.

**Pourquoi CSS externe plutot qu'inline ?**
Le tooltip necessite la pseudo-classe `:hover` qui n'est pas disponible en style inline Python. Un fichier CSS dans `assets/` est charge automatiquement par Dash.

---

## Limites connues
- `ORDER BY RANDOM()` regenere un ordre different a chaque changement de page — l'utilisateur peut voir des doublons entre pages
- 25% des livres sans couverture — limitation des APIs Google Books et Open Library sur les titres recents
- Le filtre note exclut les livres sans note (NULL) quand une valeur > 0 est selectionnee

---

*Documentation produite dans le cadre du projet L'Oracle des Plumes — DataMuse pour Editions Novae.*
