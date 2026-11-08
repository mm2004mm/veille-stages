"""Welcome to the Jungle : boutiques M&A / debt advisory, fonds, banques qui y publient leurs stages.
La liste des offres d'une entreprise s'affiche avec un navigateur -> lue via Firecrawl (1 crédit par entreprise).
Chaque fiche contient un bloc JobPosting lu gratuitement. Lancé lundi, mercredi et vendredi pour économiser les crédits."""
import os, re, time
from datetime import datetime, timezone
from common import clean, date_mentions, firecrawl_markdown, get, in_idf, jobposting, jp_location, offre, save

# slug = la partie de l'adresse welcometothejungle.com/fr/companies/<slug>
COMPANIES = ["cambon-partners", "capitalmind", "investec", "alantra", "largilliere-finance", "scalene-partners",
             "blanche-capital", "avolta-partners", "sefico-nexia", "clipperton", "inflexion-points-technology",
             "naxicap", "raise", "tikehau-capital", "ardian", "natixis", "la-banque-postale"]
BASE = "https://www.welcometothejungle.com"
STAGE = re.compile(r"stage|stagiaire|intern|analyst|analyste|césure|cesure", re.I)


def run():
    if datetime.now(timezone.utc).weekday() not in (0, 2, 4) and not os.environ.get("FORCE_ALL"):
        return None  # pas aujourd'hui : on garde le dernier résultat
    out, erreurs = [], []
    for slug in COMPANIES:
        try:
            md = firecrawl_markdown(f"{BASE}/fr/companies/{slug}/jobs")
        except Exception as e:
            erreurs.append(f"{slug}: {e}")
            continue
        for titre, url in re.findall(r"\[\*\*(.+?)\*\*\]\((https://www\.welcometothejungle\.com/fr/companies/[^)\s]+/jobs/[^)\s]+)\)", md):
            if not STAGE.search(titre):
                continue
            try:
                r = get(url)
                jp = jobposting(r.text) or {}
            except Exception as e:
                erreurs.append(f"{url}: {e}")
                continue
            lieu = jp_location(jp)
            if lieu and not in_idf(lieu):
                continue
            desc = clean(jp.get("description") or "")
            out.append(offre("Welcome to the Jungle", (jp.get("hiringOrganization") or {}).get("name") or slug,
                             jp.get("title") or titre, url, lieu=lieu, contrat=str(jp.get("employmentType") or ""),
                             mentions=date_mentions(titre + ". " + desc), publie=jp.get("datePosted") or ""))
            time.sleep(0.5)
    return save("wttj", out, note="; ".join(erreurs)[:2000])
