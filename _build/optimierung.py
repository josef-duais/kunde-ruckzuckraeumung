"""Ähnlichkeits-Optimierung: sorgt dafür, dass keine zwei kritischen Kombi-Seiten (gleiche Leistung oder gleiche Stadt)
mehr als ZIEL Text teilen. Seiten über dem Grenzwert werden mit neuem `salt` neu zusammengestellt.

Aufruf (aus website/):  python3 _build/optimierung.py
Ergebnis: _build/salts.json – wird vom Build gelesen (deterministisch, reproduzierbar).
"""
import collections
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from aehnlichkeit import html_text, shingles  # noqa: E402
from texte import L  # noqa: E402
import seiten  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent
STAEDTE = seiten.STAEDTE
SALTS = ROOT / "salts.json"
ZIEL = 0.22  # Sicherheitsabstand zur Vorgabe 25 %


def main():
    salts = json.loads(SALTS.read_text()) if SALTS.exists() else {}
    by_slug = {s["slug"]: s for s in STAEDTE}
    keys = [(l, s["slug"]) for s in STAEDTE for l in L]
    def gen(k):
        return shingles(html_text(seiten.kombi_seite(by_slug[k[1]], k[0], salts.get(f"{k[0]}|{k[1]}", 0))))
    sets = {k: gen(k) for k in keys}
    nachbarn = {k: [x for x in keys if x != k and (x[0] == k[0] or x[1] == k[1])] for k in keys}

    def cont(a, b):
        A, B = sets[a], sets[b]
        return len(A & B) / max(1, min(len(A), len(B)))

    def verstoesse(k):
        return [x for x in nachbarn[k] if cont(k, x) >= ZIEL]

    runde = 0
    while True:
        runde += 1
        schlecht = collections.Counter()
        for k in keys:
            for x in verstoesse(k):
                schlecht[k] += 1
        if not schlecht:
            break
        print(f"Runde {runde}: {len(schlecht)} Seiten mit Paaren ≥ {ZIEL:.0%}")
        if runde > 40:
            print("Abbruch nach 40 Runden")
            break
        erledigt = set()
        for k, _n in schlecht.most_common():
            if k in erledigt:
                continue
            best = (len(verstoesse(k)), salts.get(f"{k[0]}|{k[1]}", 0), sets[k])
            for versuch in range(1, 25):
                neu = best[1] + versuch * 7919 if versuch else 0
                salts[f"{k[0]}|{k[1]}"] = neu
                sets[k] = gen(k)
                v = len(verstoesse(k))
                if v < best[0]:
                    best = (v, neu, sets[k])
                if v == 0:
                    break
            salts[f"{k[0]}|{k[1]}"], sets[k] = best[1], best[2]
            erledigt.add(k)
            erledigt.update(verstoesse(k))
    SALTS.write_text(json.dumps(salts, indent=0, sort_keys=True))
    # Bericht
    mx, n, summe = 0.0, 0, 0.0
    for k in keys:
        for x in nachbarn[k]:
            if x > k:
                c = cont(k, x); n += 1; summe += c; mx = max(mx, c)
    print(f"Fertig: {n} Paare | Ø {summe / n:.1%} | Maximum {mx:.1%}")


if __name__ == "__main__":
    main()
