"""Collecteur BPCE (Natixis CIB, BRED, Caisse d'Epargne IDF, Banque Populaire Rives de Paris, Palatine...).

Interroge la recherche publique de recrutement.bpce.fr, garde les stages en Ile-de-France,
lit la description de chaque offre et en extrait les phrases qui parlent de la date de debut.
Resultat : results/bpce.json (liste d'offres au meme format pour toutes les sources).
"""
import html, json, re, sys, time
from datetime import datetime, timezone
import requests

BASE = "https://recrutement.bpce.fr"
SEARCH = BASE + "/app/wp-json/bpce/v1/search/jobs"
DETAIL = BASE + "/app/wp-json/bpce/v1/posts/?lang=fr&_uid=job-{}"
HEADERS = {"User-Agent": "veille-stages (usage personnel, lecture seule)", "Content-Type": "application/json"}
IDF_ZIP = ("75", "77", "78", "91", "92", "93", "94", "95")
IDF_CITIES = ("paris", "la defense", "la défense", "puteaux", "courbevoie", "charenton", "montrouge",
              "neuilly", "boulogne", "issy", "levallois", "saint-denis", "nanterre", "fontenay", "joinville")
DATE_RE = re.compile(r"[^.]{0,120}\b(janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[uû]t|septembre|octobre|"
                     r"novembre|d[ée]cembre|january|february|march|april|may|june|july|august|september|october|"
                     r"november|december|s[12]|h[12]|semestre|date de d[ée]but|prise de fonction|[àa] pourvoir|"
                     r"[àa] compter|d[èe]s que)\b[^.]{0,120}(20\d\d)?[^.]{0,40}", re.I)


def search(keyword):
    r = requests.post(SEARCH, headers=HEADERS, json={"keyword": keyword, "size": 1000}, timeout=60)
    r.raise_for_status()
    return r.json()["data"]["items"]


def in_idf(item):
    for loc in item.get("localisations") or []:
        if (loc.get("region") or "").lower().replace("î", "i") == "ile-de-france":
            return True
        if str(loc.get("zipcode") or "").startswith(IDF_ZIP):
            return True
    city = (item.get("localisation") or "").lower()
    return any(c in city for c in IDF_CITIES)


def _strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from _strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from _strings(v)


def detail_text(post_id):
    r = requests.get(DETAIL.format(post_id), headers=HEADERS, timeout=60)
    r.raise_for_status()
    raw = " ".join(_strings(r.json()))
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def main():
    items = {}
    for kw in ["stage", "juillet 2027", "juin 2027", "septembre 2027", "july 2027"]:
        for it in search(kw):
            items[it["post_id"]] = it
        time.sleep(1)
    stages = [it for it in items.values()
              if any("stage" in c.lower() for c in it.get("contract") or []) and in_idf(it)]
    out = []
    for it in stages:
        try:
            txt = detail_text(it["post_id"])
            dates = sorted({m.group(0).strip() for m in DATE_RE.finditer(txt)})[:6]
        except Exception as e:  # une fiche en erreur ne bloque pas les autres
            dates = [f"(description illisible : {e})"]
        out.append({
            "source": "Site carrières (BPCE)",
            "entreprise": ", ".join(it.get("brand") or []),
            "titre": html.unescape(it.get("title") or ""),
            "lieu": it.get("localisation"),
            "url": BASE + it["link"]["url"].rstrip("/"),
            "mentions_date": dates,
        })
        time.sleep(0.5)
    res = {"collecte": datetime.now(timezone.utc).isoformat(timespec="seconds"), "nb": len(out), "offres": out}
    with open("results/bpce.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(f"{len(items)} offres BPCE vues, {len(out)} stages en Ile-de-France")


if __name__ == "__main__":
    sys.exit(main())
