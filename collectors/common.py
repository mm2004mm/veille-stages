"""Outils partagés par tous les collecteurs (lecture seule de pages publiques)."""
import html, json, os, re, time
from datetime import datetime, timezone
import requests

UA = {"User-Agent": "Mozilla/5.0 (veille-stages, usage personnel, lecture seule)",
      "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"}
S = requests.Session()
S.headers.update(UA)

IDF_ZIP = ("75", "77", "78", "91", "92", "93", "94", "95")
IDF_WORDS = ("paris", "ile-de-france", "île-de-france", "la defense", "la défense", "puteaux", "courbevoie",
             "charenton", "montrouge", "neuilly", "boulogne", "issy", "levallois", "saint-denis", "nanterre",
             "fontenay", "joinville", "guyancourt", "saint-quentin", "evry", "évry", "vincennes", "maisons-alfort")

# Intitulés qui nous intéressent / à écarter (premier tri, le jugement fin est fait par la veille Claude)
KEEP = re.compile(r"M&A|M&amp;A|fusion|acquisition|merger|coverage|financ|advisory|conseil|leverage|LBO|DCM|ECM|"
                  r"capital market|syndicat|structur|banquier|relationship|corporate|investment|invest|inspect|"
                  r"audit|risque|risk|cr[ée]dit|credit|private|dette|debt|project|infra|origination|"
                  r"charg[ée]e? d.affaires|transaction|analyst|analyste|fundraising|lev[ée]e", re.I)
DROP = re.compile(r"juriste|legal|fiscal|tax\b|d[ée]veloppeu|developer|data|\bIT\b|informatique|marketing|"
                  r"\bRH\b|ressources humaines|talent acquisition|communication|contr[ôo]le de gestion|comptab|"
                  r"middle|back.office|gestionnaire|conformit|compliance|achats|alternan|apprenti|CDI|VIE\b|"
                  r"graphi|design|UX|commercial agence", re.I)

DATE_RE = re.compile(r"[^.;\n]{0,110}\b(janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[uû]t|septembre|octobre|"
                     r"novembre|d[ée]cembre|january|february|march|april|may|june|july|august|september|october|"
                     r"november|december|s[12] ?20\d\d|h[12] ?20\d\d|semestre|date de d[ée]but|prise de fonction|"
                     r"[àa] pourvoir|[àa] compter|d[èe]s que possible|start date|starting)\b[^.;\n]{0,110}", re.I)


def get(url, **kw):
    for essai in range(3):
        try:
            r = S.get(url, timeout=60, **kw)
            if r.status_code == 429:
                time.sleep(10 * (essai + 1))
                continue
            r.raise_for_status()
            return r
        except requests.RequestException:
            if essai == 2:
                raise
            time.sleep(5)


def clean(txt):
    txt = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", txt or "")
    txt = html.unescape(re.sub(r"<[^>]+>", " ", txt))
    return re.sub(r"\s+", " ", txt).strip()


def date_mentions(txt, n=6):
    seen, out = set(), []
    for m in DATE_RE.finditer(txt or ""):
        s = m.group(0).strip(" ,:-")
        if s.lower() not in seen:
            seen.add(s.lower())
            out.append(s)
        if len(out) >= n:
            break
    return out


def in_idf(*texts):
    t = " ".join(x or "" for x in texts).lower()
    return any(w in t for w in IDF_WORDS) or bool(re.search(r"\b(75|77|78|91|92|93|94|95)\d{3}\b", t))


def relevant(title):
    return bool(title) and bool(KEEP.search(title)) and not DROP.search(title)


def jobposting(page_html):
    """Renvoie le bloc JSON-LD JobPosting d'une page (dict) ou None."""
    for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>([\s\S]*?)</script>', page_html or ""):
        try:
            data = json.loads(m.group(1))
        except ValueError:
            continue
        items = data if isinstance(data, list) else data.get("@graph", [data])
        for it in items:
            if isinstance(it, dict) and it.get("@type") == "JobPosting":
                return it
    return None


def jp_location(jp):
    locs = jp.get("jobLocation") or []
    locs = locs if isinstance(locs, list) else [locs]
    parts = []
    for l in locs:
        a = (l or {}).get("address") or {}
        if isinstance(a, dict):
            parts.append(", ".join(str(a.get(k) or "") for k in ("addressLocality", "postalCode", "addressRegion", "addressCountry")))
    return " | ".join(p for p in parts if p.strip(", "))


def firecrawl_markdown(url, wait_ms=4000):
    """Lit une page qui a besoin d'un navigateur, via Firecrawl (1 crédit). Nécessite le secret FIRECRAWL_API_KEY."""
    key = os.environ.get("FIRECRAWL_API_KEY")
    if not key:
        raise RuntimeError("secret FIRECRAWL_API_KEY absent")
    r = requests.post("https://api.firecrawl.dev/v2/scrape", timeout=120,
                      headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                      json={"url": url, "formats": ["markdown"], "waitFor": wait_ms, "onlyMainContent": True})
    r.raise_for_status()
    return (r.json().get("data") or {}).get("markdown") or ""


def offre(source, entreprise, titre, url, lieu="", contrat="", debut="", mentions=None, publie=""):
    return {"source": source, "entreprise": entreprise, "titre": clean(titre), "url": url.split("#")[0].rstrip("/"),
            "lieu": lieu, "contrat": contrat, "debut": debut, "mentions_date": mentions or [], "publie": publie}


def save(name, offres, note=""):
    os.makedirs("results", exist_ok=True)
    res = {"collecte": datetime.now(timezone.utc).isoformat(timespec="seconds"), "nb": len(offres),
           "note": note, "offres": offres}
    with open(f"results/{name}.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    return len(offres)
