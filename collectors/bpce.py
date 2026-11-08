"""BPCE : Natixis CIB, BRED, Caisse d'Epargne IDF, Banque Populaire Rives de Paris, Palatine...
Recherche publique de recrutement.bpce.fr (testée le 8/11/2026)."""
import time
from common import S, clean, date_mentions, in_idf, offre, save

BASE = "https://recrutement.bpce.fr"


def run():
    items = {}
    for kw in ["stage", "juillet 2027", "juin 2027", "septembre 2027", "july 2027"]:
        r = S.post(BASE + "/app/wp-json/bpce/v1/search/jobs", json={"keyword": kw, "size": 1000}, timeout=60)
        r.raise_for_status()
        for it in r.json()["data"]["items"]:
            items[it["post_id"]] = it
        time.sleep(1)
    out = []
    for it in items.values():
        if not any("stage" in c.lower() for c in it.get("contract") or []):
            continue
        locs = it.get("localisations") or []
        lieu = it.get("localisation") or ""
        if not in_idf(lieu, *[f"{l.get('region','')} {l.get('zipcode','')} {l.get('city','')}" for l in locs]):
            continue
        try:
            j = S.get(f"{BASE}/app/wp-json/bpce/v1/posts/?lang=fr&_uid=job-{it['post_id']}", timeout=60).json()
            # seulement le texte de l'offre elle-même (pas les « offres similaires » de la page)
            txt = clean(((j.get("content") or {}).get("main") or {}).get("text") or "")
            mentions = date_mentions(txt)
        except Exception as e:
            mentions = [f"(description illisible : {e})"]
        out.append(offre("Site carrières (BPCE)", ", ".join(it.get("brand") or []), it.get("title"),
                         BASE + it["link"]["url"], lieu=lieu, contrat="Stage", mentions=mentions))
        time.sleep(0.4)
    return save("bpce", out)
