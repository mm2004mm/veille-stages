"""BNP Paribas : stages en France, recherche par mots-clés sur group.bnpparibas (testée le 8/11/2026).
Chaque fiche contient un bloc JobPosting (titre, lieu, description)."""
import re, time
from common import clean, date_mentions, get, in_idf, jobposting, jp_location, offre, relevant, save

BASE = "https://group.bnpparibas"
QUERIES = ["juillet 2027", "july 2027", "juin 2027", "septembre 2027", "M&A", "coverage", "financement",
           "leveraged", "advisory", "inspection", "corporate finance", "debt"]


def run():
    slugs = {}
    for q in QUERIES:
        for page in range(1, 6):
            t = get(f"{BASE}/emploi-carriere/toutes-offres-emploi/stage/france", params={"q": q, "page": page}).text
            found = set(re.findall(r"/emploi-carriere/offre-emploi/([a-z0-9-]+)", t))
            new = found - set(slugs)
            for s in found:
                slugs.setdefault(s, q)
            if not new:
                break
            time.sleep(0.7)
    out = []
    for s in slugs:
        if not relevant(s.replace("-", " ")):
            continue
        url = f"{BASE}/emploi-carriere/offre-emploi/{s}"
        r = get(url)
        if "offre-emploi" not in r.url:  # redirigée vers une liste = offre expirée
            continue
        jp = jobposting(r.text) or {}
        titre = jp.get("title") or s
        desc = clean(jp.get("description") or r.text)
        lieu = jp_location(jp)
        if not in_idf(lieu, desc[:3000]):
            continue
        out.append(offre("Site carrières (BNP Paribas)", (jp.get("hiringOrganization") or {}).get("name") or "BNP Paribas",
                         titre, url, lieu=lieu, contrat=str(jp.get("employmentType") or "Stage"),
                         mentions=date_mentions(desc), publie=jp.get("datePosted") or ""))
        time.sleep(0.5)
    return save("bnp", out)
