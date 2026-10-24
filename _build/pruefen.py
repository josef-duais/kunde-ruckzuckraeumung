"""Qualitätsprüfung nach dem Build: interne Links, Klicktiefe ab Startseite, Pflicht-Bausteine, Schema, Consent.
Aufruf (aus website/): python3 _build/pruefen.py
"""
import collections
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PHASE3 = set()  # alle Seiten gebaut

seiten = {}
for p in ROOT.rglob("index.html"):
    if "_build" in p.parts:
        continue
    rel = "/" + str(p.parent.relative_to(ROOT)).replace("\\", "/") + "/"
    seiten["/" if rel == "/./" else rel] = p.read_text(encoding="utf-8")

defekt, phase3 = collections.Counter(), collections.Counter()
graph = {}
for url, html in seiten.items():
    links = set()
    for href in re.findall(r'href="(/[^"#?]*)', html):
        if href.endswith((".css", ".js", ".svg", ".png", ".webp", ".jpg", ".xml", ".woff2")):
            if not (ROOT / href.lstrip("/")).exists():
                defekt[href] += 1
            continue
        if href in seiten:
            links.add(href)
        elif href in PHASE3:
            phase3[href] += 1
        else:
            defekt[href] += 1
    for src in re.findall(r'src="(/[^"?]+)', html):
        if not (ROOT / src.lstrip("/")).exists():
            defekt[src] += 1
    graph[url] = links

# Klicktiefe (BFS ab Startseite)
tiefe = {"/": 0}
q = collections.deque(["/"])
while q:
    u = q.popleft()
    for v in graph[u]:
        if v not in tiefe:
            tiefe[v] = tiefe[u] + 1
            q.append(v)
nicht_erreicht = [u for u in seiten if u not in tiefe and u != "/danke/"]  # /danke/ = Ziel der Formular-Weiterleitung
verteilung = collections.Counter(tiefe.values())

# Pflicht-Bausteine + Schema
fehlt = collections.Counter()
for url, html in seiten.items():
    if url == "/":
        continue
    checks = {
        "Formular": 'action="https://formsubmit.co/' in html or url == "/danke/",
        "Bewertungen+Button": ('id="bewertungen"' in html and 'href="/bewerten/"' in html) if url != "/bewerten/" else
                              ('id="bewertungen"' not in html and 'class="cta-band"' in html),
        "Chat": "data-chat-fab" in html, "Sticky-Bar": 'class="sticky-bar"' in html, "Cookie-Banner": 'id="cc-banner"' in html,
        "Breadcrumb-Schema": '"BreadcrumbList"' in html, "Canonical": 'rel="canonical"' in html,
        "kein noindex": "noindex" not in html, "0 iframes vor Consent": "<iframe" not in re.sub(r"<template>[\s\S]*?</template>", "", html),
    }
    if re.match(r"^/[a-z-]+-[a-z0-9-]+/$", url) and not url.startswith("/einsatzgebiete") and url.count("/") == 2 and url.strip("/") not in (
            "messie-wohnung-entruempeln", "ueber-uns", "kunden-bewertung"):
        checks["Service-Schema"] = '"Service"' in html
        checks["FAQPage-Schema"] = '"FAQPage"' in html
    for k, ok in checks.items():
        if not ok:
            fehlt[k] += 1

titles = collections.Counter(re.search(r"<title>(.*?)</title>", h).group(1) for h in seiten.values())
h1s = collections.Counter(re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S).group(1) for h in seiten.values())
sitemap = set(re.findall(r"<loc>https?://[^/]+(/[^<]*)</loc>", (ROOT / "sitemap.xml").read_text()))
oeffentlich = {u for u in seiten if not u.startswith("/kunden-bewertung/")}
robots = (ROOT / "robots.txt").read_text()
footer_ok = all(all(x in h for x in ('href="/impressum/"', 'href="/datenschutz/"', "data-cookie-settings", 'href="/einsatzgebiete/">Alle Einsatzgebiete'))
                for h in seiten.values())
fs_ok = all(h.count('action="https://formsubmit.co/') == h.count('name="_next" value="https://') for h in seiten.values())
print(f"Seiten: {len(seiten)}")
print(f"Sitemap: {len(sitemap)} URLs | öffentliche Seiten fehlen in Sitemap: {sorted(oeffentlich - sitemap)[:5]} | Sitemap-URLs ohne Seite: {sorted(sitemap - set(seiten))[:5]}")
print(f"robots.txt: Disallow nur /kunden-bewertung/: {'Disallow: /kunden-bewertung/' in robots and robots.count('Disallow') == 1} | Sitemap-Verweis: {'Sitemap:' in robots}")
print(f"Footer (Impressum, Datenschutz, Cookie-Einstellungen, Alle Einsatzgebiete →) auf allen Seiten: {footer_ok}")
print(f"FormSubmit-Formulare mit _next → /danke/: {fs_ok}")
print(f"Defekte interne Links/Bilder: {sum(defekt.values())} {dict(defekt.most_common(5))}")
print(f"Links auf Phase-3-Seiten (folgen noch): {dict(phase3)}")
print(f"Klicktiefe ab Startseite: {dict(sorted(verteilung.items()))} | max {max(tiefe.values())} | nicht erreichbar: {len(nicht_erreicht)}")
print(f"Fehlende Bausteine: {dict(fehlt) or 'keine'}")
print(f"Doppelte Titles: {sum(1 for c in titles.values() if c > 1)} | doppelte H1: {sum(1 for c in h1s.values() if c > 1)}")
