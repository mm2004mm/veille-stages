# veille-stages

Collecte automatique d'offres de stage pour la veille de Matéo (césure P1, Paris, été 2027).

- `collectors/` : un script par source. Chacun lit uniquement des pages publiques, en lecture seule.
- `results/` : la dernière collecte de chaque source (JSON), relue chaque soir par la veille Claude.
- `.github/workflows/collecte.yml` : lance les scripts chaque jour sur les serveurs de GitHub.

Sources actuelles : BPCE (Natixis CIB, BRED, Caisse d'Epargne IDF, Banque Populaire Rives de Paris, Palatine).
Aucune candidature, aucun compte, aucune donnée personnelle.
