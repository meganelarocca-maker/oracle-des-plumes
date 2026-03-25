# Documentation des KPIs — L'Oracle des Plumes
## DataMuse pour Editions Novae
## Date : Mars 2026

---

## KPI 1 — Vue d'ensemble du dataset

**Objectif metier**
Donner a la maison d'edition une carte d'identite complete du dataset disponible. En une seule requete, l'editeur comprend l'etendue de l'analyse : combien de livres, combien d'auteurs, quelles nationalites, sur quelle periode.

**Requete SQL**
```sql
SELECT 
    COUNT(*) as nb_livres,
    COUNT(DISTINCT auteurs) as nb_auteurs,
    COUNT(DISTINCT nationalite) as nb_nationalites,
    MIN(date) as annee_min,
    MAX(date) as annee_max
FROM livres;
```

**Resultat attendu**

| nb_livres | nb_auteurs | nb_nationalites | annee_min | annee_max |
|---|---|---|---|---|
| 1395 | ~1200 | 30 | 2023 | 2025 |

**Interpretation**
Le dataset couvre 3 annees de production editoriale mondiale, avec une diversite de 30 nationalites representees. C'est la base sur laquelle s'appuient toutes les recommandations produites par l'outil.

**Limites**
Dataset non exhaustif — echantillon des APIs disponibles. Non representatif de la totalite de la production editoriale mondiale.

---

## KPI 2 — Qualite par langue

**Objectif metier**
Identifier dans quelle langue ecrivent les auteurs les mieux notes. Utile pour une maison d'edition qui cherche des auteurs a traduire ou a cibler selon un marche linguistique precis.

**Requete SQL**
```sql
SELECT 
    langue,
    COUNT(*) as nb_livres,
    ROUND(AVG(note)::numeric, 2) as note_moyenne,
    SUM(nb_avis) as total_avis
FROM livres
WHERE note IS NOT NULL
GROUP BY langue
ORDER BY note_moyenne DESC;
```

**Interpretation**
Permet de reperer les marches linguistiques les plus actifs et les mieux notes. Si une langue ressort avec une note elevee et un volume d'avis important, c'est un marche a surveiller pour la decouverte d'auteurs.

**Limites**
La colonne langue est mal renseignee pour une partie du dataset — certains livres issus de Hardcover n'ont pas de langue associee. Le biais anglophone reste dominant.

---

## KPI 3 — Score d'emergence auteur

**Objectif metier**
Identifier les auteurs les plus prometteurs a contacter pour une maison d'edition. Ce KPI est le coeur du projet — il combine qualite, popularite et rarete pour produire un classement actionnable.

**Requete SQL**
```sql
SELECT 
    l.auteurs,
    l.nationalite,
    l.langue,
    MAX(l.date) as dernier_livre,
    COUNT(*) as nb_livres,
    ROUND(AVG(l.note)::numeric, 2) as note_moyenne,
    SUM(l.nb_avis) as total_avis,
    ROUND((AVG(l.note) * LOG(SUM(l.nb_avis) + 1) / COUNT(*))::numeric, 2) as score_emergence,
    CASE 
        WHEN l.nationalite IS NOT NULL THEN 'Reference Wikidata'
        ELSE 'Non reference Wikidata'
    END as statut_wikidata,
    CASE
        WHEN SUM(l.nb_avis) < 100 THEN 'Signal faible — tres emergent'
        WHEN SUM(l.nb_avis) BETWEEN 100 AND 300 THEN 'Signal moyen — emergent confirme'
        ELSE 'Signal fort — commence a percer'
    END as niveau_emergence
FROM livres l
WHERE l.note IS NOT NULL
  AND l.date >= '2023'
GROUP BY l.auteurs, l.nationalite, l.langue
HAVING COUNT(*) <= 2
   AND SUM(l.nb_avis) BETWEEN 30 AND 300
   AND AVG(l.note) >= 4.2
ORDER BY score_emergence DESC
LIMIT 15;
```

**Formule du score**
```
score_emergence = AVG(note) x LOG(SUM(nb_avis) + 1) / COUNT(livres)
```

**Decomposition de la formule**

| Composante | Role | Justification |
|---|---|---|
| AVG(note) | Qualite percue | Reflète la satisfaction des lecteurs |
| LOG(SUM(nb_avis) + 1) | Popularite lissee | Le logarithme evite de sur-valoriser les volumes extremes |
| / COUNT(livres) | Penalisation prolifique | Un auteur avec 1 seul livre tres note est plus emergent qu'un auteur avec 5 livres moyens |

**Criteres de selection**

| Critere | Valeur | Justification |
|---|---|---|
| note >= 4.2 | Seuil qualite eleve | On ne recommande que des auteurs bien recus |
| nb_avis BETWEEN 30 AND 300 | Fenetre emergence | Assez connu pour avoir des lecteurs, pas encore mainstream |
| nb_livres <= 2 | Rarete | Un auteur avec peu de publications est plus emergent |
| date >= 2023 | Recence | On cible la production recente uniquement |

**Indicateurs complementaires**

- `statut_wikidata` : un auteur non reference sur Wikidata est une vraie decouverte — il n'a pas encore de visibilite publique suffisante pour y figurer.
- `niveau_emergence` : lecture humaine du score pour faciliter la prise de decision editoriale sans analyse des chiffres.

**Limites**
- Biais anglophone : la majorite des auteurs identifies ecrivent en anglais (source Hardcover)
- Absence de donnees sur les contrats editoriaux existants — un auteur emergent peut deja etre sous contrat
- Le score ne prend pas en compte la dynamique temporelle (auteur en progression vs en stagnation)

---

## Recapitulatif

| KPI | Question metier | Valeur |
|---|---|---|
| Vue d'ensemble dataset | Quelle est la taille et la diversite de notre base ? | 1 395 livres, 30 nationalites, 2023-2025 |
| Qualite par langue | Dans quelle langue ecrivent les auteurs les mieux notes ? | Classement par langue et note moyenne |
| Score emergence | Quels auteurs contacter en priorite ? | Top 15 classes par score composite |

---

*Documentation produite dans le cadre du projet L'Oracle des Plumes — DataMuse pour Editions Novae.*
*Pipeline : Google Books API + Hardcover API + Open Library API + Wikidata SPARQL → PostgreSQL 15*
*Mise a jour : Mars 2026 — KPIs enrichis suite aux retours d'analyse.*
