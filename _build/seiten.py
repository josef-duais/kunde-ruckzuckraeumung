"""Leistungsseiten, Kombi-Seiten (Leistung × 18 Städte), Einsatzgebiete-Seite + sitemap.xml (max. 200 Unterseiten).

Wird von build.py aufgerufen. Inhalte kommen aus texte.py (Content-Engine), Bausteine aus build.py.
"""
import datetime
import json
import math
from html import escape

import build as B
from daten import BEWERTUNGEN, FIRMA, LEISTUNGEN, SEITEN_STAEDTE, SITE_URL
from texte import L, SPEZ, FAM, kombi, liste, rng, zahl
import pools as P

ALLE_STAEDTE = {s["slug"]: s for s in B.STAEDTE_DATEN}
STAEDTE = [ALLE_STAEDTE[x] for x in SEITEN_STAEDTE]   # nur diese Städte haben eigene Seiten
BY_SLUG = {s["slug"]: s for s in STAEDTE}
SALTS = json.loads((B.ROOT / "_build" / "salts.json").read_text())
FOTOS = json.loads((B.ROOT / "_build" / "stadtbilder.json").read_text()) if (B.ROOT / "_build" / "stadtbilder.json").exists() else {}
HEUTE = datetime.date.today().isoformat()
ic = B.icon

# Bild je Leistung (Karte/Leistungsseite) – Kundenfotos + Stockfotos aus Phase 1
LEISTUNG_BILD = {l["slug"]: (l.get("bild"), l.get("alt")) for l in LEISTUNGEN}
LEISTUNG_BILD["seniorenumzug"] = ("/bilder/kunde/galerie-wohnzimmer-umzug.webp", "Wohnzimmer während eines Umzugs – Möbel und Kartons bereit zum Transport")
LEISTUNG_BILD["messie-wohnung-entruempeln"] = ("/bilder/kunde/galerie-entruempelung-vorher.webp", "Stark zugestellter Raum vor der Entrümpelung")
# Echte Referenzfotos (Kundenbilder) – pro Seite rotierend ausgewählt
REFERENZ = [
    ("galerie-transporter-beladen", "Voll beladener Transporter bei einem Umzug"), ("galerie-schrankmontage", "Aufbau eines weißen Kleiderschranks"),
    ("galerie-entruempelung-vorher", "Vollgestellter Raum vor der Entrümpelung"), ("galerie-keller-besenrein", "Kellerraum besenrein nach der Räumung"),
    ("galerie-moebel-verpacken", "Möbel werden für den Transport in Folie verpackt"), ("galerie-wohnzimmer-umzug", "Wohnzimmer während eines Umzugs"),
    ("galerie-sideboard-montage", "Montage eines weißen Sideboards"), ("galerie-wohnung-besenrein", "Leere, besenreine Wohnung nach der Räumung"),
    ("galerie-verladen-transporter", "Mitarbeiter verlädt einen Schrank in den Transporter"), ("galerie-kartons-wohnung", "Gestapelte Umzugskartons in einer Wohnung"),
    ("galerie-tv-wand-abbau", "Abbau einer TV-Wand vor dem Umzug"), ("galerie-moebeltransport", "Gesicherte Möbel im Transporter"),
]
FAM_REF = {"umzug": [0, 4, 5, 8, 9, 10, 11, 1], "raeumung": [2, 3, 7, 0, 9, 11], "montage": [1, 6, 10, 4, 8]}


def kurl(lslug, sslug):
    return f"/{lslug}-{sslug}/"


def surl(sslug):
    """Stadt-Anker auf der Einsatzgebiete-Seite (eigene Stadt-Archive entfallen – max. 200 Unterseiten)."""
    return f"/einsatzgebiete/#{sslug}"


# --------------------------------------------------------------------------- Bausteine Phase 2

def breadcrumb(items):
    """items = [(Name, URL)], letzter Eintrag = aktuelle Seite."""
    li = []
    for i, (n, u) in enumerate(items):
        if i == len(items) - 1:
            li.append(f'<li aria-current="page">{escape(n)}</li>')
        else:
            li.append(f'<li><a href="{u}">{escape(n)}</a></li>')
    html = f'<nav class="crumbs" aria-label="Brotkrumen"><ol class="wrap">{"".join(li)}</ol></nav>'
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList",
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + u} for i, (n, u) in enumerate(items)]}
    return html, ld


def faq_html(faqs, h2):
    items = "".join(f'<details class="faq-item"><summary>{escape(q)}</summary><p>{escape(a)}</p></details>' for q, a in faqs)
    return f"""<section class="sec sec-light" aria-labelledby="faq-h">
  <div class="wrap narrow">
    <p class="eyebrow center">Häufige Fragen</p>
    <h2 id="faq-h" class="center">{escape(h2)}</h2>
    <div class="faq">{items}</div>
  </div>
</section>"""


def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}


def service_ld(name, url, beschreibung, area):
    return {"@context": "https://schema.org", "@type": "Service", "name": name, "serviceType": name, "url": SITE_URL + url,
            "description": beschreibung, "provider": {"@id": SITE_URL + "/#firma"}, "areaServed": area,
            "offers": {"@type": "Offer", "description": "Kostenlose Besichtigung, 10 % Neukunden-Rabatt auf den ersten Auftrag"}}


def area_city(s):
    a = {"@type": "City", "name": s["name"]}
    if s.get("wikipedia"):
        a["sameAs"] = s["wikipedia"]
    return a


def bewertung_badge():
    """Sterne nur mit ECHTEN Bewertungen (daten.BEWERTUNGEN). Ohne Daten: nichts anzeigen – keine erfundenen Zahlen."""
    if not BEWERTUNGEN:
        return ""
    sterne = ic("star") * 5
    schnitt = str(BEWERTUNGEN["schnitt"]).replace(".", ",")
    return (f'<a class="hero-rating" href="{escape(BEWERTUNGEN.get("url", "#"))}" target="_blank" rel="noopener">'
            f'<span class="stars-gold">{sterne}</span> {schnitt} · {BEWERTUNGEN["anzahl"]} {escape(BEWERTUNGEN.get("quelle", ""))}-Bewertungen</a>')


def hero_credit(slug):
    m = FOTOS.get(slug)
    if not m:
        return ""
    return (f'<p class="hero-credit">Foto: {escape(m["urheber"])} · <a href="{escape(m["lizenz_url"] or m["quelle"])}" rel="noopener nofollow" '
            f'target="_blank">{escape(m["lizenz"])}</a> · Wikimedia Commons</p>')


def sub_hero(eyebrow, h1, lead, checks, form_html, fid="anfrage", bg=None, credit="", urgency=None):
    """Hero wie auf der Startseite: Hintergrundbild, klare H1, Formular rechts, Inhaber + Telefon, Dringlichkeit."""
    cl = "".join(f"<li>{ic('check')}<span>{escape(c)}</span></li>" for c in checks)
    style = f' style="--hero-bg:url(\'{bg}\')"' if bg else ""
    urg = urgency or ["Kurzfristige Termine möglich – auch samstags", "10 % Neukunden-Rabatt auf den ersten Auftrag"]
    return f"""<section class="hero hero-sub{' has-bg' if bg else ''}"{style} aria-labelledby="hero-h">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      {bewertung_badge()}
      <p class="eyebrow eyebrow-light">{escape(eyebrow)}</p>
      <h1 id="hero-h">{escape(h1)}</h1>
      <p class="hero-lead">{escape(lead)}</p>
      <ul class="hero-checks">{cl}</ul>
      <div class="owner-card">
        <span class="owner-av" aria-hidden="true">LK</span>
        <p><strong>{escape(FIRMA['inhaber'])}</strong> · Inhaber<br><span>Ihr fester Ansprechpartner – direkt erreichbar per Telefon &amp; WhatsApp.</span></p>
        <a class="owner-call" href="{B.TEL}" aria-label="Inhaber direkt anrufen">{ic('phone')}</a>
      </div>
      <div class="hero-btns">
        <a class="btn btn-primary btn-lg" href="#{fid}">Kostenloses Angebot anfordern</a>
        <a class="btn btn-ghost btn-lg" href="{B.TEL}">{ic('phone')} {B.TEL_TXT}</a>
      </div>
      <ul class="hero-urgency"><li>{ic('clock')}{escape(urg[0])}</li><li>{ic('tag')}{escape(urg[1])}</li></ul>
    </div>
    <div class="hero-form" id="{fid}">{form_html}</div>
  </div>
  {credit}
</section>"""


GARANTIE_BASIS = [
    ("check", "Kostenlos &amp; unverbindlich", "Besichtigung und Angebot kosten Sie nichts. Sie entscheiden danach in Ruhe – ohne Verpflichtung."),
    ("tag", "Preis steht vorher fest", "Sie erhalten vor dem Einsatz ein schriftliches Angebot. Keine versteckten Kosten, keine Überraschungen."),
]
GARANTIE_FAM = {
    "umzug": ("truck", "Sorgfältiger Transport", "Möbel werden mit Decken, Folie und Gurten geschützt – und am Ziel wieder aufgebaut."),
    "raeumung": ("leaf", "Besenreine Übergabe", "Wir übergeben die Räume leer und besenrein – fachgerecht getrennt und entsorgt."),
    "montage": ("tools", "Sauber &amp; stabil montiert", "Aufbau nach Herstellerangaben, ausgerichtet und befestigt – die Verpackung nehmen wir mit."),
}


def garantien(titel, fam="raeumung", stadt=None):
    """Garantie + Dringlichkeit (für Google-Ads-Besucher). Texte vor Ads-Start vom Inhaber bestätigen lassen (siehe FEHLLISTE)."""
    items = GARANTIE_BASIS + [GARANTIE_FAM[fam]]
    karten = "".join(f'<article class="adv garantie"><span class="adv-ic">{ic(i)}</span><h3>{t}</h3><p>{d}</p></article>' for i, t, d in items)
    wo = f" in {escape(stadt)}" if stadt else ""
    return f"""<section class="sec sec-light garantien" aria-labelledby="gar-h">
  <div class="wrap">
    <div class="center"><p class="eyebrow">Unser Versprechen</p><h2 id="gar-h">{titel}</h2></div>
    <div class="adv-grid adv-grid-3">{karten}</div>
    <div class="urgency-bar">
      <p>{ic('clock')}<strong>Kurzfristige Termine{wo} möglich</strong> – Mo–Sa 8–18 Uhr. Je früher Sie anfragen, desto eher klappt Ihr Wunschtermin.</p>
      <a class="btn btn-primary" href="#anfrage">Jetzt Termin sichern {ic('arrow')}</a>
    </div>
  </div>
</section>"""


GALERIE_FOTOS = [
    ("img_0060", "Voll beladener Transporter mit Kartons und Möbeln"), ("img_0645", "Zwei Mitarbeiter verpacken Möbel in einer hellen Wohnung"),
    ("img_0513", "Aufbau eines großen Kleiderschranks"), ("img_0065", "Vollgestellter Raum vor der Entrümpelung"),
    ("img_0068", "Kellerraum nach der Räumung – besenrein"), ("img_0641", "Mitarbeiter verlädt einen weißen Schrank"),
    ("img_0538", "Leeres, besenreines Zimmer nach der Wohnungsauflösung"), ("img_0523", "Montage eines weißen Sideboards"),
    ("img_0646", "Möbel werden in Stretchfolie gewickelt"), ("img_0640", "Gesicherte Möbel im Transporter"),
    ("img_0053", "Gestapelte Umzugskartons in einer Wohnung"), ("img_0515", "Wohnzimmer mitten im Umzug"),
    ("img_0063", "Zugestellte Kammer vor der Räumung"), ("img_0051", "Abbau einer TV-Wand vor dem Umzug"),
]


def referenzen(seed, n=8, titel="Referenzen: echte Aufträge aus der Region"):
    """Referenz-Galerie mit echten Kundenfotos – auf jeder Unterseite."""
    r = rng("referenzen", seed)
    fotos = list(GALERIE_FOTOS)
    r.shuffle(fotos)
    figs = "".join(f'<figure><a href="/bilder/kunde/gross/{d}.webp" data-lightbox><img src="/bilder/kunde/gross/{d}-klein.webp" '
                   f'alt="{escape(a)}" width="600" height="600" loading="lazy" decoding="async"></a><figcaption>{escape(a)}</figcaption></figure>'
                   for d, a in fotos[:n])
    return f"""<section class="sec sec-soft referenzen" aria-labelledby="ref-h">
  <div class="wrap">
    <div class="center"><p class="eyebrow">Referenzen</p><h2 id="ref-h">{escape(titel)}</h2>
      <p class="sec-sub">Keine Symbolbilder: Diese Fotos stammen aus unseren eigenen Umzügen, Entrümpelungen und Montagen.</p></div>
    <div class="gallery gallery-cap">{figs}</div>
    <div class="center"><a class="btn btn-primary" href="/galerie/">Alle Referenzen ansehen {ic('arrow')}</a></div>
  </div>
</section>"""


def stadt_karte(s, titel, href, unter=""):
    return (f'<article class="city-card" id="{s["slug"]}"><a class="city-img" href="{href}"><img src="/bilder/staedte/{s["slug"]}.webp" '
            f'alt="Stadtansicht {escape(s["name"])}" width="800" height="500" loading="lazy" decoding="async"></a>'
            f'<div class="city-body"><h3><a href="{href}">{escape(titel)}</a></h3>{unter}</div></article>')


def entfernung_txt(s):
    return "Unser Firmensitz" if s["dist"] < 3 else f"{zahl(round(s['dist']))} km {s.get('richtung', '').lower().replace('norden', 'nördlich').replace('süden', 'südlich').replace('osten', 'östlich').replace('westen', 'westlich')} von Herten"


def bildnachweise(slugs):
    items = []
    for sl in slugs:
        m = FOTOS.get(sl)
        if m:
            items.append(f'<li>{escape(ALLE_STAEDTE[sl]["name"])}: {escape(m["urheber"])}, <a href="{escape(m["lizenz_url"] or m["quelle"])}" '
                         f'rel="noopener nofollow" target="_blank">{escape(m["lizenz"])}</a>, <a href="{escape(m["quelle"])}" rel="noopener nofollow" target="_blank">Wikimedia Commons</a></li>')
    if not items:
        return ""
    return f'<details class="credits wrap"><summary>Bildnachweise Stadtfotos</summary><ul>{"".join(items)}</ul></details>'


def trustbar():
    return f"""<section class="trustbar" aria-label="Unsere Versprechen">
  <ul class="wrap trust-grid">
    <li><strong>Kostenlos</strong><span>Besichtigung &amp; Angebot</span></li>
    <li><strong>Mo–Sa</strong><span>8–18 Uhr erreichbar</span></li>
    <li><strong>Aus einer Hand</strong><span>Umzug, Entrümpelung &amp; Montage</span></li>
    <li><strong>{FIRMA['radius_km']} km</strong><span>Einsatzradius rund um Herten</span></li>
  </ul>
</section>"""


def cta_band(titel, text):
    return f"""<section class="cta-band" aria-label="Angebot anfordern">
  <div class="wrap cta-band-in">
    <div><p class="cta-band-h">{escape(titel)}</p><p>{escape(text)}</p></div>
    <div class="cta-band-btns">
      <a class="btn btn-primary btn-lg" href="#anfrage">Kostenloses Angebot</a>
      <a class="btn btn-ghost btn-lg" href="{B.WA}" target="_blank" rel="noopener">{ic('whatsapp')} WhatsApp</a>
    </div>
  </div>
</section>"""


def mini_karte(s, naechste):
    """Kleine SVG-Lagekarte: Herten, Zielstadt und Nachbarorte (echte Koordinaten)."""
    lat0, lon0 = FIRMA["geo"]
    kx = 111.2 * math.cos(math.radians(lat0))
    pts = [s] + naechste[:6]
    xs = [(p["lon"] - lon0) * kx for p in pts] + [0]
    ys = [-(p["lat"] - lat0) * 111.2 for p in pts] + [0]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    span = max(maxx - minx, maxy - miny, 20) * 1.25
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    W = 360
    def P_(p_lon, p_lat):
        x = ((p_lon - lon0) * kx - cx) / span * W + W / 2
        y = (-(p_lat - lat0) * 111.2 - cy) / span * W + W / 2
        return x, y
    hx, hy = P_(lon0, lat0)
    tx, ty = P_(s["lon"], s["lat"])
    g = [f'<line x1="{hx:.0f}" y1="{hy:.0f}" x2="{tx:.0f}" y2="{ty:.0f}" class="mk-line"/>']
    for n in naechste[:6]:
        x, y = P_(n["lon"], n["lat"])
        if 8 < x < W - 8 and 8 < y < W - 8:
            g.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="3" class="m-dot"/><text x="{x + 6:.0f}" y="{y + 4:.0f}" class="m-t">{escape(n["name"])}</text>')
    g.append(f'<circle cx="{hx:.0f}" cy="{hy:.0f}" r="6" class="m-home"/><text x="{hx:.0f}" y="{hy - 11:.0f}" text-anchor="middle" class="m-home-t">Herten</text>')
    if s["dist"] >= 3:
        g.append(f'<circle cx="{tx:.0f}" cy="{ty:.0f}" r="7" class="mk-ziel"/><text x="{tx:.0f}" y="{ty + 22:.0f}" text-anchor="middle" class="m-home-t">{escape(s["name"])}</text>')
    return (f'<svg class="radius-map mini-map" viewBox="0 0 {W} {W}" role="img" '
            f'aria-label="Lage von {escape(s["name"])}: {zahl(round(s["dist"]))} km {escape(s.get("richtung", ""))} von Herten">{"".join(g)}</svg>')


def stadtfoto(s, cls="city-photo"):
    m = FOTOS.get(s["slug"])
    if not m:
        return ""
    credit = (f'Foto: {escape(m["urheber"])}, <a href="{escape(m["lizenz_url"] or m["quelle"])}" rel="noopener nofollow" target="_blank">{escape(m["lizenz"])}</a>, '
              f'via <a href="{escape(m["quelle"])}" rel="noopener nofollow" target="_blank">Wikimedia Commons</a>')
    return (f'<figure class="{cls}"><img src="/bilder/staedte/{s["slug"]}.webp" alt="Stadtansicht {escape(s["name"])}" width="800" height="500" '
            f'loading="lazy" decoding="async"></figure>')  # Nachweis: /bildnachweise/


def fakten_box(fakten, stadt):
    rows = "".join(f"<tr><th scope=\"row\">{escape(k)}</th><td>{escape(v)}</td></tr>" for k, v in fakten)
    return f"""<div class="facts"><p class="facts-h">{escape(stadt)} auf einen Blick</p>
<table>{rows}</table><p class="facts-src">Quelle: Wikidata (amtliche Einwohnerzahlen), Entfernung = Luftlinie ab Herten</p></div>"""


def referenz_streifen(lslug, sslug, n=3):
    r = rng("ref", lslug, sslug)
    idx = list(FAM_REF[L[lslug]["fam"]])
    r.shuffle(idx)
    figs = "".join(f'<figure><img src="/bilder/kunde/{REFERENZ[i][0]}.webp" alt="{escape(REFERENZ[i][1])}" width="600" height="600" loading="lazy" decoding="async"></figure>'
                   for i in idx[:n])
    return f'<div class="ref-strip">{figs}</div><p class="ref-note">Echte Fotos aus unseren Aufträgen.</p>'


ANDERE_TXT = ["{ergebnis_gross}", "Für {kunden}", "{objekt_gross}", "Ziel: {ziel}", "Kostenlose Besichtigung in {stadt}",
              "{art_gross} mit festem Ansprechpartner"]
for _l in L.values():
    _l["ergebnis_gross"] = _l["ergebnis"][0].upper() + _l["ergebnis"][1:]
    _l["objekt_gross"] = _l["objekt"][0].upper() + _l["objekt"][1:]
    _l["art_gross"] = _l["art"][0].upper() + _l["art"][1:]


# --------------------------------------------------------------------------- Kombi-Seite

def kombi_seite(s, lslug, salt=None):
    salt = SALTS.get(f"{lslug}|{s['slug']}", 0) if salt is None else salt
    k = kombi(s, lslug, STAEDTE, salt)
    r = rng("render", lslug, s["slug"], salt)
    l, f = L[lslug], k["f"]
    stadt, url = s["name"], kurl(lslug, s["slug"])
    src = f"kombi-{lslug}-{s['slug']}"
    crumbs, crumb_ld = breadcrumb([("Startseite", "/"), ("Einsatzgebiete", "/einsatzgebiete/"), (stadt, surl(s["slug"])), (l["kw"], url)])
    bild, alt = LEISTUNG_BILD[lslug]
    hero_bg = f"/bilder/hero/stadt-{s['slug']}.webp"
    form = B.anfrage_formular("form-kombi", f"Angebot für {l['akk']} in {stadt}",
                              "Kostenlos &amp; unverbindlich – Antwort vom Inhaber persönlich.", f"{l['kw']} {stadt}", src)

    nutzen = "".join(f'<article class="adv"><h3>{escape(t)}</h3><p>{escape(d)}</p></article>' for t, d in k["nutzen"])
    umfang = "".join(f"<li>{ic('check')}<span>{escape(u)}</span></li>" for u in k["umfang"])
    warum = "".join(f"<li>{ic('check')}<span>{escape(w)}</span></li>" for w in k["warum"])
    blocks = {
        "stadt": f"""<section class="sec sec-soft" aria-labelledby="stadt-h">
  <div class="wrap split">
    <div class="prose"><h2 id="stadt-h">{escape(k['stadt_h2'])}</h2><p>{escape(k['stadt_absatz'])}</p></div>
    <div>{fakten_box(r.sample(k['fakten'], min(len(k['fakten']), r.choice([5, 6]))), stadt)}</div>
  </div>
</section>""",
        "umfang": f"""<section class="sec sec-light" aria-labelledby="umfang-h">
  <div class="wrap">
    <h2 id="umfang-h">{escape(k['umfang_h2'])}</h2>
    <ul class="check-grid">{umfang}</ul>
    <div class="adv-grid adv-grid-4">{nutzen}</div>
  </div>
</section>""",
        "warum": f"""<section class="sec sec-dark" aria-labelledby="warum-h">
  <div class="wrap split">
    <div><h2 id="warum-h">{escape(k['warum_h2'])}</h2><ul class="checks checks-plain">{warum}</ul>
      <a class="btn btn-primary" href="#anfrage">Jetzt Angebot anfordern {ic('arrow')}</a></div>
    <div>{referenz_streifen(lslug, s['slug'])}</div>
  </div>
</section>""",
    }
    schritte = "".join(f'<li class="step"><span class="step-n">{i}</span><h3>{escape(t)}</h3><p>{escape(d)}</p></li>'
                       for i, (t, d) in enumerate(k["ablauf"], 1))
    teile_liste = "".join(f"<li>{ic('check')}<span>{escape(t)}</span></li>" for t in k["teile"])
    nahe_l = list(k["naechste"][:5])
    r.shuffle(nahe_l)
    nahe = "".join(stadt_karte(n, f"{l['kw_kurz']} {n['name']}", kurl(lslug, n["slug"]), f'<p>{escape(entfernung_txt(n))}</p>') for n in nahe_l[:3])
    andere_l = [o for o in L if o != lslug]
    r.shuffle(andere_l)
    andere = "".join(
        f'<li><a href="{kurl(o, s["slug"])}"><strong>{escape(L[o]["kw"])} {escape(stadt)}</strong>'
        f'<span>{escape(r.choice(ANDERE_TXT).format(**L[o], stadt=stadt))}</span></a></li>'
        for o in andere_l)

    body = f"""{crumbs}
{sub_hero(f"{l['kw_kurz']} · {stadt}" + (f" · {f['kreis']}" if f['kreis'] else ''), k['h1'], k['intro'][0],
          [f"{l['objekt_gross']} – alles aus einer Hand", f"Vor Ort in {stadt}" + (f" und Stadtteilen wie {k['teile'][0]}" if k['teile'] else " und Umgebung"),
           "Schriftliches Angebot vorab – kostenlos & unverbindlich"], form,
          bg=hero_bg,
          urgency=[f"Kurzfristige Termine in {stadt} – auch samstags", "10 % Neukunden-Rabatt auf den ersten Auftrag"])}
{trustbar()}
<section class="sec sec-light" aria-labelledby="intro-h">
  <div class="wrap split split-img">
    <div class="prose">
      <p class="eyebrow">{escape(l['kw_kurz'])} in {escape(stadt)}</p>
      <h2 id="intro-h">{escape(l['art'][0].upper() + l['art'][1:])} in {escape(stadt)} – so arbeiten wir</h2>
      <p>{escape(k['intro'][1])}</p>
      <p>{escape(k['umfeld_absatz'])}</p>
    </div>
    {stadtfoto(s, "city-photo city-photo-lg") or f'<figure class="svc-figure"><img src="{bild}" alt="{escape(alt)}" width="640" height="480" loading="lazy" decoding="async"></figure>'}
  </div>
</section>
{''.join(blocks[b] for b in k['block_order'])}
{garantien(f"Unsere Garantien für {escape(l['akk'])} in {escape(stadt)}", l['fam'], stadt)}
<section class="sec sec-soft" aria-labelledby="ablauf-h">
  <div class="wrap">
    <div class="center"><p class="eyebrow">Ablauf</p><h2 id="ablauf-h">In vier Schritten zum Ziel: {escape(l['ergebnis'])}</h2></div>
    <ol class="steps">{schritte}</ol>
  </div>
</section>
<section class="sec sec-light" aria-labelledby="teile-h">
  <div class="wrap split">
    <div class="prose">
      <h2 id="teile-h">{escape(k['teile_h2'])}</h2>
      {f'<p>{escape(k["teile_absatz"])}</p>' if k['teile_absatz'] else ''}
      {f'<ul class="check-grid">{teile_liste}</ul>' if teile_liste else ''}
    </div>
    <div>{mini_karte(s, k['naechste'])}</div>
  </div>
</section>
{referenzen(f"{lslug}-{s['slug']}", titel=f"Referenzen: So arbeiten wir – auch in {stadt}")}
{faq_html(k['faqs'], f"Fragen zu {l['dat']} in {stadt}")}
<section class="sec sec-soft" aria-labelledby="nahe-h">
  <div class="wrap">
    <h2 id="nahe-h">{escape(l['kw_kurz'])} in der Nähe von {escape(stadt)}</h2>
    <div class="city-grid city-grid-3">{nahe}</div>
  </div>
</section>
<section class="sec sec-light" aria-labelledby="andere-h">
  <div class="wrap">
    <h2 id="andere-h">Weitere Leistungen in {escape(stadt)}</h2>
    <ul class="svc-links">{andere}</ul>
  </div>
</section>
{cta_band(f"Kostenloses Angebot für {l['akk']} in {stadt}", "Besichtigung kostenlos · Antwort vom Inhaber · 10 % Neukunden-Rabatt")}
"""
    lds = [crumb_ld, service_ld(f"{l['kw']} {stadt}", url, k["desc"], area_city(s)), faq_ld(k["faqs"])]
    return B.page(B.head(k["title"], k["desc"], url, jsonld=lds, preload_img=hero_bg), body)


# --------------------------------------------------------------------------- Leistungsseite

def leistung_seite(lslug):
    l, sp, fam = L[lslug], SPEZ[lslug], FAM[L[lslug]["fam"]]
    r = rng("leistung", lslug)
    url = f"/{lslug}/"
    crumbs, crumb_ld = breadcrumb([("Startseite", "/"), (l["kw"], url)])
    bild, alt = LEISTUNG_BILD[lslug]
    form = B.anfrage_formular("form-leistung", f"Angebot für {l['akk']}", "Kostenlos &amp; unverbindlich – Antwort vom Inhaber persönlich.",
                              l["kw"], f"leistung-{lslug}")
    region = {"stadt": "Herten und Umgebung", "dist_txt": "nur wenige Minuten", "richtung_txt": "rund um", "kreis_klammer": "", "kreis_komma": "",
              "art_gross": l["art"][0].upper() + l["art"][1:], **l}
    lead = sp["hook"][0] + f" Wir übernehmen {l['akk']} in Herten, im Kreis Recklinghausen und im Umkreis von bis zu {FIRMA['radius_km']} km – mit kostenloser Besichtigung und festem Ansprechpartner."
    absaetze = [
        sp["hook"][1] + " " + sp["hook"][2],
        f"Für {l['kunden']} ist {l['art']} bei uns in festen Händen: Inhaber {FIRMA['inhaber']} plant den Einsatz persönlich, "
        f"ein junges, eingespieltes Team setzt ihn um. Am Ende steht {l['ergebnis']}.",
        f"Wir sind im Umkreis von bis zu {FIRMA['radius_km']} km um Herten im Einsatz – im ganzen Kreis Recklinghausen und den Nachbarstädten "
        "des Ruhrgebiets ebenso wie darüber hinaus. Unten finden Sie die wichtigsten Orte mit eigener Seite.",
    ]
    umfang = "".join(f"<li>{ic('check')}<span>{escape(u)}</span></li>" for u in sp["umfang"])
    nutzen = "".join(f'<article class="adv"><h3>{escape(t)}</h3><p>{escape(d)}</p></article>' for t, d in sp["nutzen"]) + "".join(
        f'<article class="adv"><h3>{escape(t)}</h3><p>{escape(v[0].replace("{stadt}", "Herten und Umgebung"))}</p></article>'
        for t, v in P.NUTZEN[l["fam"]][:2])
    schritte = "".join(f'<li class="step"><span class="step-n">{i}</span><h3>{escape(st[0][0])}</h3><p>{escape(st[0][1])}</p></li>'
                       for i, st in enumerate(fam["ablauf"], 1))
    ctx = {**l, "stadt": "Ihrer Stadt", "dist_txt": "bis zu 100 km", "art_gross": region["art_gross"]}
    fam_faq = list(fam["faq"])
    r.shuffle(fam_faq)
    faqs = [(q.format(**ctx).replace(" in Ihrer Stadt", ""), r.choice(a).format(**ctx)) for q, a in list(sp["faq"]) + fam_faq[:4]
            if "nicht in {stadt}" not in q]
    karten = "".join(stadt_karte(x, f"{l['kw_kurz']} {x['name']}", kurl(lslug, x["slug"]), f'<p>{escape(entfernung_txt(x))}</p>') for x in STAEDTE)
    hero_bg = f"/bilder/hero/leistung-{lslug}.webp"
    body = f"""{crumbs}
{sub_hero(f"{l['kw_kurz']} · Herten & {FIRMA['radius_km']} km Umkreis", f"{l['kw']} in Herten & Umgebung – vom Team aus der Region", lead,
          [f"{l['objekt_gross']} – alles aus einer Hand", "Kreis Recklinghausen, Ruhrgebiet & 100 km Umkreis",
           "Schriftliches Angebot vorab – kostenlos & unverbindlich"], form, bg=hero_bg)}
{trustbar()}
<section class="sec sec-light" aria-labelledby="intro-h">
  <div class="wrap split split-img">
    <div class="prose"><p class="eyebrow">{escape(l['kw_kurz'])}</p><h2 id="intro-h">Was {escape(l['art'])} bei uns bedeutet</h2>
      {''.join(f'<p>{escape(a)}</p>' for a in absaetze)}</div>
    <figure class="svc-figure"><img src="{bild}" alt="{escape(alt)}" width="640" height="480" loading="lazy" decoding="async"></figure>
  </div>
</section>
<section class="sec sec-soft" aria-labelledby="umfang-h">
  <div class="wrap"><h2 id="umfang-h">Leistungsumfang: {escape(l['kw'])}</h2><ul class="check-grid">{umfang}</ul>
    <div class="adv-grid adv-grid-4">{nutzen}</div></div>
</section>
{garantien(f"Unsere Garantien für {escape(l['akk'])}", l['fam'])}
<section class="sec sec-soft" aria-labelledby="ablauf-h">
  <div class="wrap"><div class="center"><p class="eyebrow">Ablauf</p><h2 id="ablauf-h">So läuft {escape(l['art'])} ab</h2></div><ol class="steps">{schritte}</ol></div>
</section>
{referenzen(f"leistung-{lslug}")}
<section class="sec sec-light" id="staedte" aria-labelledby="orte-h">
  <div class="wrap"><div class="center"><p class="eyebrow">Einsatzorte</p><h2 id="orte-h">{escape(l['kw'])} in Ihrer Stadt</h2>
    <p class="sec-sub">Wählen Sie Ihre Stadt – mit lokalen Informationen, Stadtteilen und häufigen Fragen.</p></div>
    <div class="city-grid">{karten}</div></div>
</section>
{faq_html(faqs, f"Häufige Fragen zu {l['dat']}")}
{cta_band(f"Kostenloses Angebot für {l['akk']}", "Besichtigung kostenlos · Antwort vom Inhaber · 10 % Neukunden-Rabatt")}
"""
    title = f"{l['kw']} in Herten & Umgebung | Ruckzuckräumung"
    desc = f"{l['kw']} vom Team aus Herten: {l['objekt']} – kostenlose Besichtigung, schriftliches Angebot vorab, 10 % Neukunden-Rabatt."
    lds = [crumb_ld, service_ld(l["kw"], url, desc, {"@type": "GeoCircle", "geoMidpoint": {"@type": "GeoCoordinates", "latitude": FIRMA["geo"][0],
           "longitude": FIRMA["geo"][1]}, "geoRadius": FIRMA["radius_km"] * 1000}), faq_ld(faqs)]
    return B.page(B.head(title, desc[:158], url, jsonld=lds, preload_img=hero_bg), body)


# --------------------------------------------------------------------------- Stadt-Archiv (entfällt – max. 200 Unterseiten)

# --------------------------------------------------------------------------- Hub

def hub_seite():
    url = "/einsatzgebiete/"
    crumbs, crumb_ld = breadcrumb([("Startseite", "/"), ("Einsatzgebiete", url)])
    haupt = ["umzug", "entruempelung", "haushaltsaufloesung"]
    karten = "".join(stadt_karte(
        x, x["name"], kurl("umzug", x["slug"]),
        f'<p>{escape(entfernung_txt(x))}</p><ul class="city-links">'
        + "".join(f'<li><a href="{kurl(h, x["slug"])}">{escape(L[h]["kw_kurz"])}</a></li>' for h in haupt) + "</ul>")
        for x in STAEDTE)
    form = B.anfrage_formular("form-hub", "Angebot für Ihre Stadt", "Kostenlos &amp; unverbindlich – wir melden uns persönlich.",
                              "Einsatzgebiete", "einsatzgebiete")
    hero_bg = "/bilder/hero/seite-einsatzgebiete.webp"
    body = f"""{crumbs}
{sub_hero("Einsatzgebiete", "Umzug & Entrümpelung im Kreis Recklinghausen und im Ruhrgebiet",
          f"Von Herten aus sind wir im Umkreis von bis zu {FIRMA['radius_km']} km im Einsatz. Hier finden Sie unsere wichtigsten Orte mit allen Leistungen – Ihr Ort ist nicht dabei? Fragen Sie einfach an.",
          ["Alle 10 Städte im Kreis Recklinghausen", "Gelsenkirchen, Bochum, Essen, Dortmund & mehr", "Kostenlose Besichtigung vor Ort"], form, bg=hero_bg)}
<section class="sec sec-light" aria-labelledby="hub-h">
  <div class="wrap">
    <div class="center"><p class="eyebrow">Unsere Einsatzorte</p><h2 id="hub-h">{len(STAEDTE)} Städte mit eigener Seite</h2></div>
    <div class="city-grid">{karten}</div>
  </div>
</section>
<section class="sec sec-soft" aria-labelledby="radius-h">
  <div class="wrap split split-map">
    <div class="prose"><h2 id="radius-h">Und darüber hinaus: bis zu {FIRMA['radius_km']} km</h2>
      <p>Unser Einsatzgebiet reicht vom Ruhrgebiet bis ins Münsterland, an den Niederrhein, ins Rheinland und ins Sauerland. Auch wenn Ihr Ort oben nicht steht: Rufen Sie an oder nutzen Sie das Formular – wir sagen Ihnen sofort, ob wir kommen können.</p>
      <a class="btn btn-primary" href="#anfrage">Jetzt anfragen {ic('arrow')}</a></div>
    <div class="area-card"><p class="area-title">Einsatzradius {FIRMA['radius_km']} km</p>{B.radius_karte()}</div>
  </div>
</section>
{garantien("Unsere Garantien – in jeder Stadt", "raeumung")}
{referenzen("hub")}
"""
    title = "Einsatzgebiete: Kreis Recklinghausen & Ruhrgebiet | Ruckzuckräumung"
    desc = "Umzug, Entrümpelung & Montage in Herten, Recklinghausen, Marl, Gelsenkirchen, Bochum, Essen, Dortmund und im Umkreis von 100 km."
    return B.page(B.head(title, desc[:158], url, jsonld=[crumb_ld], preload_img=hero_bg), body)


# --------------------------------------------------------------------------- Alles schreiben

def alle(write, extra_urls=()):
    urls = ["/"] + list(extra_urls)
    for lslug in L:
        write(f"/{lslug}/", leistung_seite(lslug), quiet=True)
        urls.append(f"/{lslug}/")
    write("/einsatzgebiete/", hub_seite(), quiet=True)
    urls.append("/einsatzgebiete/")
    for s in STAEDTE:
        for lslug in L:
            write(kurl(lslug, s["slug"]), kombi_seite(s, lslug), quiet=True)
            urls.append(kurl(lslug, s["slug"]))
    sm = "".join(f"<url><loc>{SITE_URL}{u}</loc><lastmod>{HEUTE}</lastmod></url>" for u in urls)
    (B.ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n', encoding="utf-8")
    return urls
