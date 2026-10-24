"""Misst die Text-Ähnlichkeit der Kombi-Seiten (5-Wort-Shingles, Anteil gemeinsamer Shingles = Containment).
Aufruf: python3 _build/aehnlichkeit.py [html]   – ohne Argument: Rohtexte aus texte.py; mit 'html': gebaute Seiten (<main>).
"""
import itertools
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from texte import L, kombi  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
STAEDTE = json.loads((ROOT / "_build" / "staedte.json").read_text())


def shingles(text, n=5):
    w = re.findall(r"[\wäöüÄÖÜß%-]+", text.lower())
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def rohtext(k):
    teile = [k["h1"], *k["intro"], k["stadt_h2"], k["stadt_absatz"], k["warum_h2"], *k["warum"], k["umfang_h2"], *k["umfang"]]
    teile += [a + " " + b for a, b in k["nutzen"]] + [a + " " + b for a, b in k["ablauf"]] + [q + " " + a for q, a in k["faqs"]]
    teile += [k["teile_h2"], k["teile_absatz"], k["umfeld_absatz"], " ".join(k["teile"])]
    teile += [f"{a} {b}" for a, b in k["fakten"]]
    teile += [f"{L[k['f']['slug']]['kw']} {n['name']}" for n in k["naechste"]]
    return " ".join(teile)


def html_text(path_or_html):
    """Hauptinhalt einer Seite ohne seitenweite Bausteine (Brotkrumen, Trust-Leiste, Formular, Bewertungen, CTA-Band)."""
    h = path_or_html if isinstance(path_or_html, str) else path_or_html.read_text()
    m = re.search(r'<main id="inhalt">(.*)</main>', h, re.S)
    h = m.group(1) if m else h
    h = re.sub(r"<(script|template|form)[\s\S]*?</\1>", " ", h)   # Formular/Embeds = geteilte Bausteine
    h = re.sub(r'<section class="sec sec-soft" id="bewertungen"[\s\S]*?</section>', " ", h)
    h = re.sub(r'<(nav) class="crumbs"[\s\S]*?</nav>', " ", h)
    h = re.sub(r'<section class="(trustbar|cta-band)"[\s\S]*?</section>', " ", h)
    h = re.sub(r'<div class="hero-btns">[\s\S]*?</div>', " ", h)
    return re.sub(r"<[^>]+>", " ", h)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "roh"
    sets = {}
    for s in STAEDTE:
        for slug in L:
            if mode == "html":
                p = ROOT / f"{slug}-{s['slug']}" / "index.html"
                sets[(slug, s["slug"])] = shingles(html_text(p))
            else:
                sets[(slug, s["slug"])] = shingles(rohtext(kombi(s, slug, STAEDTE)))
    def cont(a, b):
        A, B = sets[a], sets[b]
        return len(A & B) / max(1, min(len(A), len(B)))
    worst, n, summe, ueber = (0, None), 0, 0.0, 0
    keys = list(sets)
    # gleiche Leistung, andere Stadt + gleiche Stadt, andere Leistung (die kritischen Paare)
    for slug in L:
        ks = [k for k in keys if k[0] == slug]
        for a, b in itertools.combinations(ks, 2):
            c = cont(a, b); n += 1; summe += c; ueber += c >= .25
            if c > worst[0]: worst = (c, (a, b))
    for s in STAEDTE:
        ks = [k for k in keys if k[1] == s["slug"]]
        for a, b in itertools.combinations(ks, 2):
            c = cont(a, b); n += 1; summe += c; ueber += c >= .25
            if c > worst[0]: worst = (c, (a, b))
    w = [len(v) for v in sets.values()]
    print(f"Seiten: {len(sets)} | Paare geprüft: {n} | Ø Ähnlichkeit: {summe / n:.1%} | Maximum: {worst[0]:.1%} {worst[1]} | Paare ≥ 25 %: {ueber}")
    print(f"Shingles je Seite: min {min(w)}, Ø {sum(w) // len(w)}")


if __name__ == "__main__":
    main()
