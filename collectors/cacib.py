"""Crédit Agricole CIB : liste complète de jobs.ca-cib.com (Talentsoft, testée le 8/11/2026).
Chaque fiche donne Type de contrat, Ville et « Date prévue de prise de fonction »."""
import re, time
from common import clean, date_mentions, get, in_idf, offre, relevant, save

BASE = "https://jobs.ca-cib.com"


def field(txt, label, stop):
    m = re.search(label + r"\s+(.{1,80}?)\s+(?:" + stop + ")", txt)
    return m.group(1).strip() if m else ""


def run():
    links = {}
    for page in range(1, 8):
        t = get(f"{BASE}/offre-de-emploi/liste-toutes-offres.aspx", params={"all": 1, "mode": "list", "page": page}).text
        found = set(re.findall(r"(/offre-de-emploi/emploi-[a-z0-9-]+_\d+\.aspx)", t))
        if not found or found <= set(links):
            break
        for p in found:
            links[p] = re.sub(r"^/offre-de-emploi/emploi-|_\d+\.aspx$", "", p).replace("-", " ")
        time.sleep(0.7)
    out = []
    for path, titre in links.items():
        if not relevant(titre):
            continue
        r = get(BASE + path)
        h1 = re.search(r"<h1[^>]*>([\s\S]*?)</h1>", r.text)
        titre = clean(h1.group(1)) if h1 else titre
        txt = clean(r.text)
        contrat = field(txt, r"Type de contrat", r"Durée|Date prévue|Poste avec")
        if "stage" not in contrat.lower():
            continue
        ville = field(txt, r"Ville", r"Critères|Niveau")
        if not in_idf(ville):
            continue
        debut = field(txt, r"Date prévue de prise de fonction", r"Poste avec|Critères|Ville|Localisation")
        desc = txt.split("Description de la mission", 1)[-1].split("Ces offres pourraient vous intéresser", 1)[0]
        out.append(offre("Site carrières (CA CIB)", "Crédit Agricole CIB", titre, BASE + path, lieu=ville,
                         contrat="Stage", debut=debut, mentions=date_mentions(desc)))
        time.sleep(0.5)
    return save("cacib", out)
