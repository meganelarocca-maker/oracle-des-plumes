-- KPI 1 : Vue d'ensemble du dataset-Carte d'identité dataset livres
SELECT 
    COUNT(*) as nb_livres,
    COUNT(DISTINCT auteurs) as nb_auteurs,
    COUNT(DISTINCT nationalite) as nb_nationalites,
    MIN(date) as annee_min,
    MAX(date) as annee_max
FROM livres;

--KPI 2 enrichi — "Qualité par langue"-"Dans quelle langue écrivent les auteurs les mieux notés ?"-je garde les niches potentielle car, à mon sens, ils peuvent détenir une péptite
SELECT 
    langue,
    COUNT(*) as nb_livres,
    ROUND(AVG(note)::numeric, 2) as note_moyenne,
    SUM(nb_avis) as total_avis
FROM livres
WHERE note IS NOT NULL
GROUP BY langue
HAVING COUNT(*) >= 5
ORDER BY note_moyenne DESC; nb_livres DESC;

-- KPI 3 : auteurs émergents
SELECT auteurs,
       COUNT(*) as nb_livres,
       AVG(note) as note_moyenne,
       SUM(nb_avis) as total_avis,
       ROUND((AVG(note) * LOG(SUM(nb_avis) + 1) / COUNT(*))::numeric, 2) AS score
FROM livres
WHERE note IS NOT NULL
  AND date >= 2023
GROUP BY auteurs
HAVING COUNT(*) <= 2
   AND SUM(nb_avis) BETWEEN 30 AND 300
   AND AVG(note) >= 4.2
ORDER BY score DESC
LIMIT 15;