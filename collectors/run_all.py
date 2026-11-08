"""Lance tous les collecteurs ; une source en panne n'empêche pas les autres. Écrit results/_etat.json."""
import json, os, sys, traceback
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
import bpce, bnp, cacib, wttj, pages  # noqa: E402

etat = {"collecte": datetime.now(timezone.utc).isoformat(timespec="seconds"), "sources": {}}
for nom, mod in [("bpce", bpce), ("bnp", bnp), ("cacib", cacib), ("wttj", wttj), ("pages", pages)]:
    try:
        n = mod.run()
        etat["sources"][nom] = {"ok": True, "nb": n, "note": "pas prévu aujourd'hui" if n is None else ""}
    except Exception as e:
        etat["sources"][nom] = {"ok": False, "erreur": f"{type(e).__name__}: {e}"[:500],
                                "trace": traceback.format_exc()[-1500:]}
    print(nom, etat["sources"][nom].get("nb"), etat["sources"][nom].get("erreur", ""))
os.makedirs("results", exist_ok=True)
with open("results/_etat.json", "w", encoding="utf-8") as f:
    json.dump(etat, f, ensure_ascii=False, indent=1)
