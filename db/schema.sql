-- ============================================================
-- L'ORACLE DES PLUMES — Schema de la base de données
-- ============================================================

-- Supprime les tables si elles existent deja (pour pouvoir relancer proprement)
DROP TABLE IF EXISTS livres CASCADE;

-- Table principale
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
    sexe        TEXT
)