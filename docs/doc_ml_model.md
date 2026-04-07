# Module ML — Score Predictif d'Emergence
## L'Oracle des Plumes — DataMuse
## Date : Avril 2026

---

## Objectif

Predire la probabilite qu'un auteur emergent perce dans les prochains mois, en s'appuyant sur des signaux mesurables existants dans le dataset. Ce module enrichit le classement de la page Auteurs Emergents avec une dimension predictive.

---

## Fichiers concernes

- `src/ml_model.py` — logique ML (entrainement + prediction)
- `pages/auteurs.py` — integration dans le dashboard

---

## Type de modele

**Classification binaire** avec `RandomForestClassifier` (scikit-learn)

| Element | Valeur |
|---|---|
| Algorithme | Random Forest |
| Nombre d'arbres | 100 |
| Equilibrage des classes | `class_weight="balanced"` |
| Split entrainement/test | 80% / 20% |
| Graine aleatoire | 42 |

---

## Variable cible

```python
seuil = df["score"].median()
df["va_percer"] = (df["score"] > seuil).astype(int)
```

- `1` — l'auteur a un score superieur a la mediane → va percer
- `0` — l'auteur a un score inferieur a la mediane → pas encore

Le seuil est dynamique — il s'adapte automatiquement au dataset.

---

## Features utilisees

| Feature | Type | Justification |
|---|---|---|
| `note` | Numerique | Qualite percue par les lecteurs |
| `nb_avis` | Numerique | Popularite communautaire |
| `nb_livres` | Numerique | Rarete — peu de livres = plus emergent |
| `nationalite_encoded` | Categoriel encode | Contexte geographique |
| `derniere_publication` | Numerique | Recence — plus recent = plus pertinent |

### Feature exclue intentionnellement

**`langue`** — exclue car notre dataset presente un biais anglophone (70%+ de livres en anglais). L'inclure aurait penalise artificiellement les auteurs non anglophones.

---

## Resultats

```
accuracy : 0.98
macro avg precision : 0.98
macro avg recall : 0.98
```

**Interpretation :**
Le modele predit correctement dans 98% des cas sur le jeu de test. Ce resultat eleve s'explique en partie par la taille limitee du dataset — il se stabilisera au fur et a mesure de l'enrichissement des donnees.

---

## Raisonnement sur le class_weight="balanced"

Sans equilibrage, le modele favorise les nationalites surrepresentees (USA, Royaume-Uni). Le parametre `class_weight="balanced"` compense ce biais en donnant plus de poids aux classes minoritaires.

**Effet observe :**
- Avant equilibrage : France = probabilite faible (biais anglophone)
- Apres equilibrage : France = probabilite comparable aux autres nationalites

**Limite actuelle :** avec un dataset peu diversifie, l'equilibrage peut sur-corriger. Le modele s'ameliorera naturellement avec un dataset plus riche.

---

## Integration dans le dashboard

Le modele est entraine une fois au lancement de l'application :

```python
model, le_nationalite = entrainer_modele()
```

La probabilite est calculee pour chaque auteur via `df.apply()` :

```python
df["probabilite_succes"] = df.apply(
    lambda row: predire(model, le_nationalite, ...),
    axis=1
)
```

Le tableau est trie par niveau d'emergence puis par probabilite decroissante :
1. Signal faible — tres emergent (pépites prioritaires)
2. Signal moyen — emergent confirme
3. Signal fort — commence a percer

---

## Limites connues

- Dataset de 689 livres avec notes — relativement petit pour du ML
- Biais anglophone residuel malgre l'equilibrage
- Le modele ne prend pas en compte la dynamique temporelle (auteur en progression vs en stagnation)
- Absence de donnees contractuelles — un auteur peut deja etre sous contrat
- Le modele se reentrainera a chaque redemarrage de l'app — pas de persistance du modele

---

## Pistes d'amelioration

- Persister le modele avec `joblib` pour eviter le reentrainement a chaque lancement
- Enrichir le dataset avec des sources francophones pour reduire le biais
- Ajouter une feature temporelle (evolution du score dans le temps)
- Automatiser le reentrainement periodique avec un script ETL

---

*Documentation produite dans le cadre du projet L'Oracle des Plumes — DataMuse pour Editions Novae.*
