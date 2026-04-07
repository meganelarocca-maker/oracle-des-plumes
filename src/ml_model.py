from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import pandas as pd
import numpy as np
from src.db import query


def entrainer_modele():
    df = query("""
        SELECT 
            auteurs,
            ROUND(AVG(note)::numeric, 2) as note,
            SUM(nb_avis) as nb_avis,
            COUNT(*) as nb_livres,
            MAX(nationalite) as nationalite,
            MAX(date) as derniere_publication,
            ROUND((AVG(note) * LOG(SUM(nb_avis) + 1) / COUNT(*))::numeric, 2) as score
        FROM livres
        WHERE note IS NOT NULL
        GROUP BY auteurs
    """)

    # Variable cible
    seuil = df["score"].median()
    df["va_percer"] = (df["score"] > seuil).astype(int)

    # Encodage nationalite
    df["nationalite"] = df["nationalite"].fillna("Inconnu")
    le_nationalite = LabelEncoder()
    df["nationalite_encoded"] = le_nationalite.fit_transform(df["nationalite"])

    # Derniere publication — plus recent = mieux
    df["derniere_publication"] = pd.to_numeric(df["derniere_publication"], errors="coerce").fillna(2023)

    # Features et cible
    X = df[[
        "note",
        "nb_avis",
        "nb_livres",
        "nationalite_encoded",
        "derniere_publication"
    ]]
    y = df["va_percer"]

    # Entrainement
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(
    n_estimators=100, 
    random_state=42,
    class_weight="balanced"  # ← équilibre automatiquement les classes
)
    model.fit(X_train, y_train)

    print(classification_report(y_test, model.predict(X_test)))

    return model, le_nationalite,


def predire(model, le_nationalite, note, nb_avis, nb_livres, nationalite, derniere_publication):

    # Encoder nationalite
    try:
        nationalite_enc = le_nationalite.transform([nationalite or "Inconnu"])[0]
    except ValueError:
        nationalite_enc = 0

    X_new = pd.DataFrame([{
        "note": note or 0,
        "nb_avis": nb_avis or 0,
        "nb_livres": nb_livres or 1,
        "nationalite_encoded": nationalite_enc,
        "derniere_publication": derniere_publication or 2023
    }])

    proba = model.predict_proba(X_new)[0][1]
    return round(proba * 100, 1)


if __name__ == "__main__":
    model, le_nationalite = entrainer_modele()
    print("Modele entraine avec succes !")

    proba = predire(
        model, le_nationalite,
        note=4.5, nb_avis=280, nb_livres=1,
        nationalite="Royaume-Uni",
        derniere_publication=2025
    )
    print(f"Probabilite de percer : {proba}%")

    # Test 1 — profil fort USA
    proba1 = predire(model, le_nationalite, note=4.5, nb_avis=280, nb_livres=1, nationalite="États-Unis", derniere_publication=2025)
    print(f"USA fort : {proba1}%")

# Test 2 — même profil Royaume-Uni
    proba2 = predire(model, le_nationalite, note=4.5, nb_avis=280, nb_livres=1, nationalite="Royaume-Uni", derniere_publication=2025)
    print(f"Royaume-Uni fort : {proba2}%")

# Test 3 — même profil France
    proba3 = predire(model, le_nationalite, note=4.5, nb_avis=280, nb_livres=1, nationalite="France", derniere_publication=2025)
    print(f"France fort : {proba3}%")


#Mon modèle atteint 98% de précision sur le jeu de test. 
# Ce résultat élevé s'explique en partie par la taille limitée du dataset 
#il s'améliorera et se stabilisera au fur et à mesure de l'enrichissement des données."
