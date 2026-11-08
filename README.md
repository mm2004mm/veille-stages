# veille-stages

Collecte automatique d'offres de stage pour la veille de Matéo (césure P1, Paris, été 2027).
Lecture seule de pages publiques : aucune candidature, aucun compte, aucune donnée personnelle.

| Script | Source | Fréquence |
|---|---|---|
| `collectors/bpce.py` | BPCE : Natixis CIB, BRED, Caisse d'Epargne IDF, BP Rives de Paris, Palatine | chaque jour |
| `collectors/bnp.py` | BNP Paribas (stages en France) | chaque jour |
| `collectors/cacib.py` | Crédit Agricole CIB | chaque jour |
| `collectors/wttj.py` | Welcome to the Jungle : boutiques M&A / debt advisory, fonds (via Firecrawl) | lundi, mercredi, vendredi |
| `collectors/pages.py` | Pages carrières simples : CIC, Bpifrance, In Extenso, Oaklins, Natixis Partners, Clearwater, Oddo (via Firecrawl) | lundi |

`results/` contient la dernière collecte de chaque source et `results/_etat.json` l'état de chaque script.
Le lancement automatique est dans `.github/workflows/collecte.yml` (vers 16 h 30, heure de Paris).
Les sources Firecrawl ont besoin du secret `FIRECRAWL_API_KEY` (Settings > Secrets and variables > Actions).
