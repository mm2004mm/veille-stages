"""Pages carrières simples (petites boutiques, CIC, Bpifrance) lues via Firecrawl, le lundi seulement.
On relève les liens qui ressemblent à des offres de stage ; la veille Claude ouvre ensuite les fiches."""
import os, re
from datetime import datetime, timezone
from common import firecrawl_markdown, offre, save

PAGES = {
    "CIC (stages)": "https://recrutement.cic.fr/fr/nos_offres.html?offres=true&tc=3",
    "Bpifrance": "https://talents.bpifrance.fr/nos-opportunites/",
    "In Extenso Finance": "https://finance.inextenso.fr/nous-rejoindre/",
    "Oaklins France": "https://www.oaklins.com/fr/en/career/",
    "Natixis Partners": "https://www.natixispartners.com/en/careers/",
    "Clearwater": "https://www.clearwatercf.com/careers/",
    "ODDO BHF": "https://www.oddo-bhf.com/discover-our-internship-opportunities/",
}
STAGE = re.compile(r"stage|stagiaire|intern|analyst|analyste|césure|cesure", re.I)


def run():
    if datetime.now(timezone.utc).weekday() != 0 and not os.environ.get("FORCE_ALL"):
        return None
    out, erreurs = [], []
    for nom, url in PAGES.items():
        try:
            md = firecrawl_markdown(url, wait_ms=3000)
        except Exception as e:
            erreurs.append(f"{nom}: {e}")
            continue
        for texte, lien in re.findall(r"\[([^\]\n]{4,160})\]\((https?://[^)\s]+)\)", md):
            if STAGE.search(texte) and not re.search(r"linkedin|facebook|twitter|instagram|youtube", lien):
                out.append(offre("Page carrières", nom, texte.replace("*", ""), lien))
    return save("pages", out, note="; ".join(erreurs)[:2000])
