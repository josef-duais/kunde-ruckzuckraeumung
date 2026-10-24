"""Statischer Seiten-Generator (geteilte Bausteine + Homepage; Phase-2-Seiten in seiten.py).

Aufruf (aus dem Ordner website/):  python3 _build/build.py
Erzeugt reines HTML in den Projekt-Root (index.html, später /<slug>/index.html).
Das generierte HTML wird committet; Hostinger liefert nur statische Dateien aus.
"""
import json
import math
import pathlib
from html import escape

from daten import (FIRMA, FORMSUBMIT_ZIEL, GHL_BEWERTUNGEN_EMBED, GHL_CHAT_WIDGET_SNIPPET, GOOGLE_MAPS_EMBED,
                   KARTE_LABELS, LEISTUNGEN, SITE_URL)

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSET_VERSION = "3"  # bei CSS/JS-Änderungen erhöhen (Cache-Busting)

# Einsatzgebiete: alle Städte mit Stadtrecht im 100-km-Radius (echte Daten, siehe staedte_holen.py)
STAEDTE_DATEN = json.loads((ROOT / "_build" / "staedte.json").read_text(encoding="utf-8"))
NAV_STAEDTE = ["Herten", "Recklinghausen", "Gelsenkirchen", "Marl", "Gladbeck", "Bochum", "Essen", "Dortmund"]
STADT_SLUG = {s["name"]: s["slug"] for s in STAEDTE_DATEN}
STAEDTE = [(s["name"], s["lat"], s["lon"], s["name"] in NAV_STAEDTE) for s in STAEDTE_DATEN]

TEL = f'tel:{FIRMA["telefon_link"]}'
TEL_TXT = FIRMA["telefon_anzeige"]
WA = FIRMA["whatsapp_link"]


def stadt_url(name):
    return f"/einsatzgebiete/{STADT_SLUG[name]}/"


def leistung(slug):
    return next(l for l in LEISTUNGEN if l["slug"] == slug)


# --------------------------------------------------------------------------- Icons (Sprite)

ICONS = {
    "phone": '<path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1L6.6 10.8z"/>',
    "whatsapp": '<path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.15l-.3-.18-3 .78.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.25-.12-1.46-.72-1.69-.8s-.39-.12-.55.12-.63.8-.78.96-.29.19-.53.06a6.7 6.7 0 0 1-3.32-2.9c-.25-.43.25-.4.72-1.33a.45.45 0 0 0-.02-.43c-.06-.12-.55-1.33-.76-1.82s-.4-.41-.55-.42h-.47a.9.9 0 0 0-.65.3 2.74 2.74 0 0 0-.85 2.03 4.76 4.76 0 0 0 1 2.53 10.9 10.9 0 0 0 4.17 3.68c1.55.67 2.16.73 2.94.61a2.5 2.5 0 0 0 1.65-1.16 2 2 0 0 0 .14-1.16c-.06-.1-.22-.16-.46-.28z"/>',
    "check": '<path d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/>',
    "arrow": '<path d="M13.2 5.3 19.9 12l-6.7 6.7-1.4-1.4 4.3-4.3H4v-2h12.1l-4.3-4.3z"/>',
    "chevron": '<path d="M7.4 8.6 12 13.2l4.6-4.6L18 10l-6 6-6-6z"/>',
    "mail": '<path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4-8 5-8-5V6l8 5 8-5z"/>',
    "pin": '<path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/>',
    "clock": '<path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16zm.5-13H11v6l5.2 3.2.8-1.3-4.5-2.7z"/>',
    "chat": '<path d="M20 2H4a2 2 0 0 0-2 2v18l4-4h14a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2zM6 9h12v2H6zm8 5H6v-2h8zm4-6H6V6h12z"/>',
    "star": '<path d="M12 17.3 18.2 21l-1.6-7L22 9.2l-7.2-.6L12 2 9.2 8.6 2 9.2 7.5 14l-1.7 7z"/>',
    "menu": '<path d="M3 6h18v2H3zm0 5h18v2H3zm0 5h18v2H3z"/>',
    "close": '<path d="M19 6.4 17.6 5 12 10.6 6.4 5 5 6.4 10.6 12 5 17.6 6.4 19 12 13.4 17.6 19 19 17.6 13.4 12z"/>',
    "truck": '<path d="M20 8h-3V4H3a2 2 0 0 0-2 2v11h2a3 3 0 0 0 6 0h6a3 3 0 0 0 6 0h2v-5zm-.5 1.5 2 2.5H17V9.5zM6 18.5A1.5 1.5 0 1 1 6 15.5a1.5 1.5 0 0 1 0 3zm12 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3z"/>',
    "box": '<path d="M21 7.5 12 2 3 7.5v9L12 22l9-5.5zM12 4.3l6.4 3.9L12 12 5.6 8.2zM5 9.9l6 3.6v6.1l-6-3.6zm8 9.7v-6.1l6-3.6v6.1z"/>',
    "tools": '<path d="m22.7 19-9.1-9.1a6 6 0 0 0-7.9-7.9l3.9 3.9-2.8 2.8-4-3.9a6 6 0 0 0 7.9 7.9l9.1 9.1a1 1 0 0 0 1.4 0l1.5-1.5a1 1 0 0 0 0-1.3z"/>',
    "leaf": '<path d="M17 8C8 10 5.9 16.2 3.8 21.3l1.9.7 1-2.3c.5.2 1 .3 1.3.3C19 20 22 3 22 3c-1 2-8 2.3-13 3.3S2 11.5 2 13.5s1.8 3.8 1.8 3.8C7 8 17 8 17 8z"/>',
    "user": '<path d="M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10zm0 2c-3.3 0-10 1.7-10 5v3h20v-3c0-3.3-6.7-5-10-5z"/>',
    "tag": '<path d="M21.4 11.6 12.4 2.6A2 2 0 0 0 11 2H4a2 2 0 0 0-2 2v7a2 2 0 0 0 .6 1.4l9 9a2 2 0 0 0 2.8 0l7-7a2 2 0 0 0 0-2.8zM6.5 8A1.5 1.5 0 1 1 6.5 5a1.5 1.5 0 0 1 0 3z"/>',
    "instagram": '<path d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5zm0 2a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3zm5 3.5a4.5 4.5 0 1 1 0 9 4.5 4.5 0 0 1 0-9zm0 2a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM17.3 5.5a1.2 1.2 0 1 1 0 2.4 1.2 1.2 0 0 1 0-2.4z"/>',
    "facebook": '<path d="M14 8V6.3c0-.8.2-1.3 1.4-1.3H17V2h-2.6C11.3 2 10 3.7 10 6.2V8H8v3h2v11h4V11h2.7l.3-3z"/>',
    "tiktok": '<path d="M16.6 2h-3.3v13.4a2.9 2.9 0 1 1-2.1-2.8V9.2a6.2 6.2 0 1 0 5.4 6.2V8.6a7.7 7.7 0 0 0 4.4 1.4V6.7a4.4 4.4 0 0 1-4.4-4.7z"/>',
}


def icon(name, cls="ic"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="/icons.svg?v={ASSET_VERSION}#i-{name}"/></svg>'


def sprite():
    """Icons liegen als /icons.svg (einmal geladen, gecacht) – hält jede der ~2.300 Seiten schlank."""
    return ""


def write_icons():
    symbols = "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items())
    (ROOT / "icons.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg">{symbols}</svg>', encoding="utf-8")


# --------------------------------------------------------------------------- <head>

def head(title, description, path, preload_hero=False, jsonld=None, preload_img=None):
    canonical = SITE_URL + path
    pre = ""
    if preload_hero:
        preload_img = "/bilder/stock/hero-umzugskartons.webp"
    if preload_img:  # Hero-Hintergrund (nur Desktop – mobil dunkler Verlauf, siehe styles.css)
        pre = (f'<link rel="preload" as="image" type="image/webp" href="{preload_img}" '
               'media="(min-width: 900px)" fetchpriority="high">')
    if isinstance(jsonld, dict):
        jsonld = [jsonld]
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in (jsonld or []))
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#121915">
<meta property="og:type" content="website">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="{escape(FIRMA['kurzname'])}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}/bilder/logo/logo-rund.jpg">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/fonts/archivo.woff2" as="font" type="font/woff2" crossorigin>
{pre}
<link rel="stylesheet" href="/styles.css?v={ASSET_VERSION}">
{ld}
</head>"""


# --------------------------------------------------------------------------- Baustein 1: Header / Navigation

def header():
    gruppen = {}
    for l in LEISTUNGEN:
        gruppen.setdefault(l["gruppe"], []).append(l)
    mega = "".join(
        f'<div class="mega-col"><p class="mega-title">{escape(g)}</p><ul>'
        + "".join(f'<li><a href="/{l["slug"]}/">{escape(l["name"])}</a></li>' for l in items)
        + "</ul></div>"
        for g, items in gruppen.items()
    )
    top = [s for s in STAEDTE if s[3]]
    orte = "".join(f'<li><a href="/umzug-{STADT_SLUG[s[0]]}/">{escape(s[0])}</a></li>' for s in top)
    return f"""<a class="skip" href="#inhalt">Zum Inhalt springen</a>
<div class="topbar">
  <div class="wrap topbar-in">
    <p class="topbar-claim">{icon('check')} Kostenlose Besichtigung &amp; Angebot <span class="sep">·</span> {icon('clock')} {FIRMA['oeffnungszeiten']}</p>
    <div class="topbar-links">
      <a href="{WA}" rel="noopener" target="_blank">{icon('whatsapp')} WhatsApp</a>
      <a href="{TEL}">{icon('phone')} {TEL_TXT}</a>
      <a class="topbar-cta" href="/kontakt/" data-cta>Kostenloses Angebot {icon('arrow')}</a>
    </div>
  </div>
</div>
<header class="site-header" id="top">
  <div class="wrap header-in">
    <a class="brand" href="/" aria-label="{escape(FIRMA['kurzname'])} – zur Startseite">
      <img src="/bilder/logo/logo-hell.webp" alt="{escape(FIRMA['name'])}" width="640" height="86">
    </a>
    <nav class="nav" id="hauptnav" aria-label="Hauptnavigation">
      <ul class="nav-list">
        <li class="has-sub">
          <a href="/#leistungen" class="nav-link">Leistungen</a>
          <button class="sub-toggle" aria-expanded="false" aria-label="Leistungen-Menü öffnen">{icon('chevron')}</button>
          <div class="sub mega">{mega}</div>
        </li>
        <li class="has-sub">
          <a href="/#einsatzgebiete" class="nav-link">Einsatzgebiete</a>
          <button class="sub-toggle" aria-expanded="false" aria-label="Einsatzgebiete-Menü öffnen">{icon('chevron')}</button>
          <div class="sub sub-orte"><ul>{orte}</ul><a class="sub-all" href="/#einsatzgebiete">Weitere Orte {icon('arrow')}</a></div>
        </li>
        <li><a href="/galerie/" class="nav-link">Galerie</a></li>
        <li><a href="/ueber-uns/" class="nav-link">Über uns</a></li>
        <li><a href="/kontakt/" class="nav-link">Kontakt</a></li>
      </ul>
      <div class="nav-mobile-cta">
        <a class="btn btn-primary btn-block" href="/kontakt/" data-cta>Kostenloses Angebot anfordern</a>
        <a class="btn btn-ghost btn-block" href="{TEL}">{icon('phone')} {TEL_TXT}</a>
      </div>
    </nav>
    <a class="header-phone" href="{TEL}">{icon('phone')}<span>{TEL_TXT}</span></a>
    <a class="btn btn-primary header-cta" href="/kontakt/" data-cta>Angebot<br>anfordern</a>
    <button class="nav-burger" aria-controls="hauptnav" aria-expanded="false" aria-label="Menü öffnen">{icon('menu', 'ic ic-open')}{icon('close', 'ic ic-close')}</button>
  </div>
</header>"""


# --------------------------------------------------------------------------- Baustein 2: Anfrageformular (FormSubmit)

def anfrage_formular(fid, titel, untertitel, quelle, source=""):
    """source = Seitenkennung (z. B. kombi-umzug-essen) – landet in der Mail und im Danke-Redirect."""
    optionen = "".join(f'<option>{escape(l["name"])}</option>' for l in LEISTUNGEN) + "<option>Sonstiges / mehrere Leistungen</option>"
    return f"""<form class="lead-form" id="{fid}" action="https://formsubmit.co/{FORMSUBMIT_ZIEL}" method="POST">
  <p class="lead-title">{titel}</p>
  <p class="lead-sub">{untertitel}</p>
  <input type="hidden" name="_subject" value="Neue Anfrage über die Webseite">
  <input type="hidden" name="_next" value="{SITE_URL}/danke/{'?source=' + source if source else ''}">
  <input type="hidden" name="Quelle" value="{escape(source or 'startseite')}">
  <input type="hidden" name="_template" value="table">
  <input type="hidden" name="_captcha" value="false">
  <input type="hidden" name="Formular" value="{escape(quelle)}">
  <div class="hp" aria-hidden="true"><label>Bitte leer lassen <input type="text" name="_honey" tabindex="-1" autocomplete="off"></label></div>
  <div class="f-row">
    <div class="f-field"><label for="{fid}-name">Name*</label><input id="{fid}-name" name="Name" type="text" autocomplete="name" placeholder="Ihr Name" required></div>
    <div class="f-field"><label for="{fid}-tel">Telefon*</label><input id="{fid}-tel" name="Telefon" type="tel" autocomplete="tel" inputmode="tel" placeholder="Ihre Telefonnummer" required></div>
  </div>
  <div class="f-field"><label for="{fid}-mail">E-Mail</label><input id="{fid}-mail" name="email" type="email" autocomplete="email" placeholder="Ihre E-Mail-Adresse (optional)"></div>
  <div class="f-field"><label for="{fid}-leistung">Welche Leistung benötigen Sie?</label>
    <select id="{fid}-leistung" name="Leistung"><option value="">Bitte wählen …</option>{optionen}</select></div>
  <div class="f-field"><label for="{fid}-msg">Kurze Beschreibung (optional)</label>
    <textarea id="{fid}-msg" name="Nachricht" rows="3" placeholder="z. B. 3-Zimmer-Wohnung, 2. OG ohne Aufzug, Umzug von Herten nach Marl"></textarea></div>
  <label class="f-check"><input type="checkbox" name="Datenschutz" value="akzeptiert" required>
    <span>Ich habe die <a href="/datenschutz/">Datenschutzerklärung</a> gelesen und stimme der Verarbeitung meiner Daten zur Bearbeitung der Anfrage zu.*</span></label>
  <button class="btn btn-primary btn-block btn-lg" type="submit">Kostenloses Angebot anfordern {icon('arrow')}</button>
  <p class="lead-note">{icon('check')} 100 % kostenlos &amp; unverbindlich <span class="sep">·</span> {icon('tag')} 10 % Neukunden-Rabatt</p>
</form>"""


# --------------------------------------------------------------------------- Consent-gated Embeds

def consent_embed(kategorie, inhalt_html, titel, hinweis, min_h=420, cls=""):
    """Platzhalter, der erst nach Einwilligung den echten Inhalt (Template) einsetzt. Vorher 0 iframes/Skripte."""
    return f"""<div class="consent-embed {cls}" data-consent="{kategorie}" style="min-height:{min_h}px">
  <template>{inhalt_html}</template>
  <div class="consent-ph">
    <p class="consent-ph-title">{titel}</p>
    <p>{hinweis}</p>
    <button type="button" class="btn btn-outline btn-sm" data-consent-accept="{kategorie}">Akzeptieren &amp; laden</button>
    <button type="button" class="link-btn" data-cookie-settings>Cookie-Einstellungen</button>
  </div>
</div>"""


# --------------------------------------------------------------------------- Baustein 4: Bewertungen

def bewertungen():
    """Bewertungs-Abschnitt NUR mit echtem GHL-Widget (consent-gated). Ohne Widget: nichts anzeigen – keine Platzhalter."""
    if not GHL_BEWERTUNGEN_EMBED:
        return ""
    widget = consent_embed("functional", GHL_BEWERTUNGEN_EMBED, "Bewertungen anzeigen",
                           "Hier werden Bewertungen über unseren Partner HighLevel geladen. Dabei werden Daten an den Anbieter übertragen.",
                           min_h=360)
    return f"""<section class="sec sec-soft" id="bewertungen" aria-labelledby="bew-h">
  <div class="wrap center">
    <p class="eyebrow">Bewertungen</p>
    <h2 id="bew-h">Bewertungen aus der Region</h2>
    <div class="reviews-widget">{widget}</div>
    <a class="btn btn-dark" href="/bewerten/">{icon('star')} Bewerten Sie uns</a>
  </div>
</section>"""


# --------------------------------------------------------------------------- Baustein 3: Footer

def footer():
    l_links = "".join(f'<li><a href="/{l["slug"]}/">{escape(l["name"])}</a></li>' for l in LEISTUNGEN)
    o_links = "".join(f'<li><a href="/umzug-{STADT_SLUG[s[0]]}/">{escape(s[0])}</a></li>' for s in STAEDTE if s[3])
    social = "".join(
        f'<a href="{url}" target="_blank" rel="noopener" aria-label="{n}">{icon(n.lower())}</a>'
        for n, url in FIRMA["social"].items()
    )
    return f"""<footer class="site-footer">
  <div class="wrap footer-grid">
    <div class="f-brand">
      <img src="/bilder/logo/logo-hell.webp" alt="{escape(FIRMA['name'])}" width="640" height="86" loading="lazy">
      <p>Umzüge, Entrümpelungen, Haushaltsauflösungen sowie Möbel- und Küchenmontage – für Privat- und Gewerbekunden in Herten, im Kreis Recklinghausen und im Umkreis von bis zu {FIRMA['radius_km']} km.</p>
      <div class="social">{social}</div>
    </div>
    <div>
      <p class="f-title">Leistungen</p>
      <ul class="f-list">{l_links}</ul>
    </div>
    <div>
      <p class="f-title">Einsatzgebiete</p>
      <ul class="f-list">{o_links}</ul>
      <a class="f-more" href="/einsatzgebiete/">Alle Einsatzgebiete {icon('arrow')}</a>
    </div>
    <div>
      <p class="f-title">Kontakt</p>
      <address class="f-nap">
        <strong>{escape(FIRMA['name'])}</strong><br>
        Inh. {escape(FIRMA['inhaber'])}<br>
        {escape(FIRMA['strasse'])}<br>{FIRMA['plz']} {escape(FIRMA['ort'])}
      </address>
      <ul class="f-list f-contact">
        <li><a href="{TEL}">{icon('phone')} {TEL_TXT}</a></li>
        <li><a href="{WA}" target="_blank" rel="noopener">{icon('whatsapp')} WhatsApp</a></li>
        <li><a href="mailto:{FIRMA['email']}">{icon('mail')} {FIRMA['email']}</a></li>
        <li>{icon('clock')} {FIRMA['oeffnungszeiten']}</li>
      </ul>
    </div>
  </div>
  <div class="wrap footer-bottom">
    <p>© <span data-year>2026</span> {escape(FIRMA['name'])}</p>
    <nav aria-label="Rechtliches" class="legal">
      <a href="/kontakt/">Kontakt</a>
      <a href="/bewerten/">Bewertung abgeben</a>
      <a href="/impressum/">Impressum</a>
      <a href="/datenschutz/">Datenschutz</a>
      <button type="button" class="link-btn" data-cookie-settings>Cookie-Einstellungen</button>
    </nav>
  </div>
</footer>"""


# --------------------------------------------------------------------------- Bausteine 5–7: Chat, Sticky-Bar, Cookie-Consent

def chat_widget():
    snippet = GHL_CHAT_WIDGET_SNIPPET or "<!-- TODO: {{GHL_CHAT_WIDGET_SNIPPET}} -->"
    return f"""<!-- Chat-Widget (GHL) – lädt erst nach Einwilligung "Funktional". Ohne Snippet/Einwilligung: WhatsApp-Fallback -->
<template id="chat-snippet" data-consent="functional">{snippet}</template>
<a class="chat-fab" href="{WA}" target="_blank" rel="noopener" aria-label="Chat starten (WhatsApp)" data-chat-fab>{icon('chat')}</a>"""


def sticky_bar():
    return f"""<div class="sticky-bar" role="region" aria-label="Schnellkontakt">
  <a class="sb-call" href="{TEL}">{icon('phone')} Anrufen</a>
  <a class="sb-cta" href="/kontakt/" data-cta>Angebot anfordern</a>
</div>"""


def cookie_consent():
    def cat(key, title, desc, fixed=False):
        attr = 'checked disabled' if fixed else f'data-cat="{key}"'
        return f"""<label class="cc-cat"><span class="cc-cat-text"><strong>{title}</strong><span>{desc}</span></span>
<span class="cc-switch"><input type="checkbox" {attr}><span></span></span></label>"""
    return f"""<div class="cc-banner" id="cc-banner" role="dialog" aria-live="polite" aria-label="Cookie-Hinweis" hidden>
  <div class="cc-banner-in">
    <p><strong>Ihre Privatsphäre ist uns wichtig.</strong> Wir verwenden nur technisch notwendige Speicherungen. Externe Inhalte wie Chat, Bewertungen und Google Maps laden wir erst nach Ihrer Einwilligung. Mehr in der <a href="/datenschutz/">Datenschutzerklärung</a>.</p>
    <div class="cc-actions">
      <button type="button" class="btn btn-ghost-dark btn-sm" data-cc="settings">Einstellungen</button>
      <button type="button" class="btn btn-ghost-dark btn-sm" data-cc="reject">Alle ablehnen</button>
      <button type="button" class="btn btn-primary btn-sm" data-cc="accept">Alle akzeptieren</button>
    </div>
  </div>
</div>
<dialog class="cc-dialog" id="cc-dialog" aria-labelledby="cc-h">
  <form method="dialog" class="cc-form">
    <p class="cc-h" id="cc-h">Cookie-Einstellungen</p>
    <p class="cc-intro">Wählen Sie, welche Dienste wir laden dürfen. Ihre Auswahl können Sie jederzeit über „Cookie-Einstellungen“ im Footer ändern.</p>
    {cat('necessary', 'Notwendig', 'Speichert Ihre Cookie-Auswahl. Immer aktiv.', fixed=True)}
    {cat('functional', 'Funktional', 'Chat-Widget, Bewertungs-Widget und Google Maps (Drittanbieter).')}
    {cat('statistics', 'Statistik', 'Anonyme Besucherstatistik zur Verbesserung der Website (derzeit nicht im Einsatz).')}
    {cat('marketing', 'Marketing', 'Werbe- und Conversion-Messung (derzeit nicht im Einsatz).')}
    <div class="cc-actions">
      <button type="button" class="btn btn-ghost-dark btn-sm" data-cc="reject">Alle ablehnen</button>
      <button type="button" class="btn btn-outline btn-sm" data-cc="save">Auswahl speichern</button>
      <button type="button" class="btn btn-primary btn-sm" data-cc="accept">Alle akzeptieren</button>
    </div>
    <p class="cc-links"><a href="/datenschutz/">Datenschutz</a> · <a href="/impressum/">Impressum</a></p>
  </form>
</dialog>"""


def page(head_html, body_html):
    return f"""{head_html}
<body>
{sprite()}
{header()}
<main id="inhalt">
{body_html}
</main>
{footer()}
{sticky_bar()}
{chat_widget()}
{cookie_consent()}
<script src="/main.js?v={ASSET_VERSION}" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------------------- Homepage-Sektionen

def radius_karte():
    """Leichte SVG-Karte des Einsatzgebiets (kein Drittanbieter, sofort sichtbar)."""
    lat0, lon0 = FIRMA["geo"]
    size, c, k = 440, 220, 1.9  # px pro km
    kx, ky = 111.2 * math.cos(math.radians(lat0)), 111.2
    dots = []
    for name, lat, lon, _top in STAEDTE:
        x = c + (lon - lon0) * kx * k
        y = c - (lat - lat0) * ky * k
        main = name == "Herten"
        r = 6 if main else (3.6 if name in KARTE_LABELS else 2.6)
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="{"m-home" if main else "m-dot"}"/>')
        if main:
            dots.append(f'<text x="{x:.1f}" y="{y - 12:.1f}" text-anchor="middle" class="m-home-t">{escape(name)}</text>')
        elif name in KARTE_LABELS:
            anchor = "end" if x > c + 120 else "start"
            dx = -7 if anchor == "end" else 7
            dots.append(f'<text x="{x + dx:.1f}" y="{y + 4:.1f}" text-anchor="{anchor}" class="m-t">{escape(name)}</text>')
    r50, r100 = 50 * k, 100 * k
    return f"""<svg class="radius-map" viewBox="0 0 {size} {size}" role="img" aria-label="Karte: Einsatzgebiet bis {FIRMA['radius_km']} km rund um Herten">
  <circle cx="{c}" cy="{c}" r="{r100 - 2}" class="m-r100"/>
  <circle cx="{c}" cy="{c}" r="{r50}" class="m-r50"/>
  <text x="{c}" y="{c - r50 + 16:.0f}" text-anchor="middle" class="m-km">50 km</text>
  <text x="{c}" y="{c - r100 + 20:.0f}" text-anchor="middle" class="m-km">100 km</text>
  {''.join(dots)}
</svg>"""


def homepage():
    grid = [l for l in LEISTUNGEN if l["grid"]]
    karten = "".join(f"""<article class="svc-card">
  <a href="/{l['slug']}/" class="svc-img"><img src="{l['bild']}" alt="{escape(l['alt'])}" width="640" height="480" loading="lazy" decoding="async"></a>
  <div class="svc-body">
    <h3><a href="/{l['slug']}/">{escape(l['name'])}</a></h3>
    <p>{escape(l['text'])}</p>
    <a class="more" href="/{l['slug']}/" aria-label="Mehr erfahren: {escape(l['name'])}">Mehr erfahren {icon('arrow')}</a>
  </div>
</article>""" for l in grid)

    seo_links = [("Umzug Herten", "/umzug-herten/"), ("Entrümpelung Herten", "/entruempelung-herten/"),
                 ("Haushaltsauflösung Herten", "/haushaltsaufloesung-herten/"), ("Umzug Recklinghausen", "/umzug-recklinghausen/"),
                 ("Entrümpelung Recklinghausen", "/entruempelung-recklinghausen/"), ("Umzug Gelsenkirchen", "/umzug-gelsenkirchen/"),
                 ("Entrümpelung Gelsenkirchen", "/entruempelung-gelsenkirchen/"), ("Möbelmontage Herten", "/moebelmontage-herten/"),
                 ("Küchenmontage Herten", "/kuechenmontage-herten/"), ("Seniorenumzug", "/seniorenumzug/"),
                 ("Messie-Wohnung entrümpeln", "/messie-wohnung-entruempeln/")]
    seo_line = " · ".join(f'<a href="{u}">{t}</a>' for t, u in seo_links)

    galerie = [
        ("galerie-transporter-beladen", "Voll beladener Transporter bei einem Umzug"),
        ("galerie-schrankmontage", "Aufbau eines weißen Kleiderschranks"),
        ("galerie-entruempelung-vorher", "Vollgestellter Raum vor der Entrümpelung"),
        ("galerie-keller-besenrein", "Kellerraum besenrein nach der Entrümpelung"),
        ("galerie-moebel-verpacken", "Möbel werden für den Transport in Folie verpackt"),
        ("galerie-wohnzimmer-umzug", "Wohnzimmer während eines Umzugs"),
        ("galerie-sideboard-montage", "Montage eines weißen Sideboards"),
        ("galerie-wohnung-besenrein", "Leere, besenreine Wohnung nach der Räumung"),
        ("galerie-verladen-transporter", "Mitarbeiter verlädt einen Schrank in den Transporter"),
        ("galerie-kartons-wohnung", "Gestapelte Umzugskartons in einer Wohnung"),
        ("galerie-tv-wand-abbau", "Abbau einer TV-Wand vor dem Umzug"),
        ("galerie-moebeltransport", "Gesicherte Möbel im Transporter"),
    ]
    galerie_html = "".join(
        f'<figure><img src="/bilder/kunde/{f}.webp" alt="{escape(a)}" width="600" height="600" loading="lazy" decoding="async"></figure>'
        for f, a in galerie)

    import seiten as S
    karten = "".join(S.stadt_karte(x, x["name"], f"/umzug-{x['slug']}/", f'<p>{escape(S.entfernung_txt(x))}</p>') for x in S.STAEDTE)

    schritte = [
        ("Anfrage stellen", "Formular ausfüllen, anrufen oder per WhatsApp schreiben – in unter einer Minute erledigt."),
        ("Kostenlose Besichtigung", "Wir schauen uns alles in Ruhe vor Ort an und beantworten Ihre Fragen – unverbindlich."),
        ("Angebot & fester Termin", "Sie erhalten ein transparentes Angebot und einen Termin, auf den Sie sich verlassen können."),
        ("Erledigt & besenrein", "Wir packen an, transportieren, montieren oder räumen – und übergeben alles besenrein."),
    ]
    schritte_html = "".join(
        f'<li class="step"><span class="step-n">{i}</span><h3>{t}</h3><p>{d}</p></li>'
        for i, (t, d) in enumerate(schritte, 1))

    vorteile = [
        ("box", "Alles aus einer Hand", "Umzug, Entrümpelung und Montage von einem Team. Keine Koordination mehrerer Firmen, kein Abstimmungschaos.", ""),
        ("user", "Direkter Draht zum Inhaber", f"Sie sprechen mit {FIRMA['inhaber']} persönlich – per Telefon oder WhatsApp, ohne Callcenter und Warteschleife.", ""),
        ("leaf", "Besenrein & umweltgerecht", "Wir hinterlassen alles übergabefertig und entsorgen fachgerecht getrennt – Recycling statt Restmüll.", ""),
        ("tag", "10 % Neukunden-Rabatt", "Als Neukunde sparen Sie 10 % auf Ihren ersten Auftrag. Einfach bei der Anfrage angeben.",
         f'<a class="more" href="/rabatt/">Rabatt sichern {icon("arrow")}</a>'),
    ]
    vorteile_html = "".join(
        f'<article class="adv{" adv-hi" if i == 3 else ""}"><span class="adv-ic">{icon(ic)}</span><h3>{t}</h3><p>{d}</p>{extra}</article>'
        for i, (ic, t, d, extra) in enumerate(vorteile))

    maps_iframe = (f'<iframe src="{GOOGLE_MAPS_EMBED}" title="Google Maps: Standort {escape(FIRMA["name"])}" '
                   'loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>')

    return f"""
<section class="hero" aria-labelledby="hero-h">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <p class="eyebrow eyebrow-light">Umzüge · Entrümpelung · Montage – Herten &amp; Ruhrgebiet</p>
      <p class="hero-chip">{icon('check')} Besichtigung &amp; Angebot kostenlos</p>
      <h1 id="hero-h"><span class="l">Umzug &amp; Entrümpelung</span> <span class="l akzent">schnell, sauber, zuverlässig</span> <span class="l">in Herten &amp; Umgebung</span></h1>
      <p class="hero-lead">Vom ersten Karton bis zur besenreinen Übergabe: Wir ziehen Sie um, entrümpeln Wohnung, Haus oder Keller und bauen Möbel und Küchen fachgerecht ab und auf. Ein Team, ein Ansprechpartner – Besichtigung und Angebot sind kostenlos.</p>
      <div class="owner-card">
        <span class="owner-av" aria-hidden="true">LK</span>
        <p><strong>{escape(FIRMA['inhaber'])}</strong> · Inhaber<br><span>Ihr fester Ansprechpartner – direkt erreichbar per Telefon &amp; WhatsApp.</span></p>
        <a class="owner-call" href="{TEL}" aria-label="Inhaber direkt anrufen">{icon('phone')}</a>
      </div>
      <div class="hero-btns">
        <a class="btn btn-primary btn-lg" href="#anfrage">Kostenloses Angebot anfordern</a>
        <a class="btn btn-ghost btn-lg" href="{TEL}">{icon('phone')} {TEL_TXT}</a>
      </div>
    </div>
    <div class="hero-form" id="anfrage">
      {anfrage_formular('form-hero', 'In 60 Sekunden zum Angebot', 'Kostenlos &amp; unverbindlich – wir melden uns zeitnah persönlich bei Ihnen.', 'Startseite – Hero')}
    </div>
  </div>
</section>

<section class="trustbar" aria-label="Unsere Versprechen">
  <ul class="wrap trust-grid">
    <li><strong>Kostenlos</strong><span>Besichtigung &amp; Angebot</span></li>
    <li><strong>Mo–Sa</strong><span>8–18 Uhr erreichbar</span></li>
    <li><strong>Aus einer Hand</strong><span>Umzug, Entrümpelung &amp; Montage</span></li>
    <li><strong>{FIRMA['radius_km']} km</strong><span>Einsatzradius rund um Herten</span></li>
  </ul>
</section>

<section class="sec sec-soft" id="leistungen" aria-labelledby="lei-h">
  <div class="wrap">
    <div class="center">
      <p class="eyebrow">Unsere Leistungen</p>
      <h2 id="lei-h">Umzug, Entrümpelung &amp; Montage – alles aus einer Hand</h2>
      <p class="sec-sub">Ein Ansprechpartner für Ihr komplettes Projekt – privat und gewerblich, in Herten, im Kreis Recklinghausen und im ganzen Ruhrgebiet.</p>
    </div>
    <div class="svc-grid">{karten}</div>
  </div>
</section>
<nav class="seo-links" aria-label="Beliebte Leistungen in der Region"><p class="wrap">{seo_line}</p></nav>

<section class="sec sec-dark" id="ueber-uns" aria-labelledby="about-h">
  <div class="wrap about-grid">
    <figure class="about-img">
      <img src="/bilder/kunde/ueber-uns-team.webp" alt="Das Team von Ruckzuckräumung verpackt Möbel sicher für den Transport" width="720" height="860" loading="lazy" decoding="async">
      <figcaption>Echtes Foto: Unser Team beim sicheren Verpacken von Möbeln.</figcaption>
    </figure>
    <div>
      <p class="eyebrow">Über uns</p>
      <h2 id="about-h">Ein junges Team, das anpackt – und Wort hält</h2>
      <p>Hinter Ruckzuckräumung steht Inhaber {escape(FIRMA['inhaber'])} mit einem jungen, motivierten Team aus Herten. Wir sind für jeden Auftrag bereit – ob Ein-Zimmer-Wohnung, komplette Haushaltsauflösung oder Büro. Unser Anspruch: ein fester Ansprechpartner, Termine, die halten, und eine Übergabe, bei der Sie nichts mehr tun müssen.</p>
      <ul class="checks">
        <li>{icon('check')}<div><strong>Kostenlose Besichtigung &amp; transparentes Angebot</strong><span>Sie wissen vorher genau, woran Sie sind – ohne Überraschungen.</span></div></li>
        <li>{icon('check')}<div><strong>Ein Ansprechpartner von der Anfrage bis zur Übergabe</strong><span>Direkt per Telefon oder WhatsApp – keine Weiterleitung, kein Callcenter.</span></div></li>
        <li>{icon('check')}<div><strong>Besenreine Übergabe &amp; umweltgerechte Entsorgung</strong><span>Fachgerecht getrennt und recycelt – übergabefertig für Vermieter oder Käufer.</span></div></li>
      </ul>
      <a class="btn btn-primary" href="/ueber-uns/">Mehr über uns {icon('arrow')}</a>
    </div>
  </div>
</section>

<section class="sec sec-light" aria-labelledby="steps-h">
  <div class="wrap">
    <div class="center">
      <p class="eyebrow">So einfach geht's</p>
      <h2 id="steps-h">In vier Schritten zum erledigten Auftrag</h2>
    </div>
    <ol class="steps">{schritte_html}</ol>
  </div>
</section>

{bewertungen()}

<section class="sec sec-light" id="galerie" aria-labelledby="gal-h">
  <div class="wrap">
    <div class="center">
      <p class="eyebrow">Referenzen</p>
      <h2 id="gal-h">Ausgewählte Arbeiten</h2>
      <p class="sec-sub">Echte Fotos aus unseren Aufträgen – Umzüge, Entrümpelungen und Montagen in Herten und Umgebung.</p>
    </div>
    <div class="gallery">{galerie_html}</div>
    <div class="center"><a class="btn btn-primary" href="/galerie/">Zur ganzen Galerie {icon('arrow')}</a></div>
  </div>
</section>

<section class="sec sec-soft" id="einsatzgebiete" aria-labelledby="area-h">
  <div class="wrap">
    <div class="center">
      <p class="eyebrow">Einsatzgebiete</p>
      <h2 id="area-h">Für Sie unterwegs in Herten, im Kreis Recklinghausen &amp; im ganzen Ruhrgebiet</h2>
    </div>
    <div class="area-grid">
      <div class="area-card">
        <p class="area-title">Unser Standort</p>
        <address>{escape(FIRMA['name'])}<br>{escape(FIRMA['strasse'])}<br>{FIRMA['plz']} {escape(FIRMA['ort'])}</address>
        <p class="area-radius">{icon('truck')} Einsatzradius bis {FIRMA['radius_km']} km – vom Münsterland bis ins Rheinland.</p>
        {radius_karte()}
        {consent_embed('functional', maps_iframe, 'Google Maps laden', 'Beim Laden der Karte werden Daten an Google übertragen.', min_h=0, cls='maps-embed')}
      </div>
      <div>
        <p class="area-title dark">Unsere wichtigsten Einsatzorte</p>
        <div class="city-grid city-grid-mini">{karten}</div>
        <a class="more" href="/einsatzgebiete/">Ihr Ort ist nicht dabei? Alle Einsatzgebiete ansehen {icon('arrow')}</a>
      </div>
    </div>
  </div>
</section>

<section class="sec sec-light" aria-labelledby="adv-h">
  <div class="wrap">
    <div class="center">
      <p class="eyebrow">Ihre Vorteile</p>
      <h2 id="adv-h">Weniger Aufwand, weniger Risiko für Sie</h2>
    </div>
    <div class="adv-grid">{vorteile_html}</div>
  </div>
</section>

<section class="sec sec-dark cta-final" id="kontakt" aria-labelledby="cta-h">
  <div class="wrap cta-grid">
    <div>
      <p class="eyebrow">Kostenlos &amp; unverbindlich</p>
      <h2 id="cta-h">Holen Sie sich Ihr kostenloses Angebot</h2>
      <p>Beschreiben Sie uns kurz Ihr Vorhaben – wir melden uns persönlich bei Ihnen, vereinbaren eine kostenlose Besichtigung und machen Ihnen ein faires, transparentes Angebot.</p>
      <ul class="checks checks-compact">
        <li>{icon('check')}<div><strong>Kostenlose Besichtigung vor Ort</strong></div></li>
        <li>{icon('check')}<div><strong>Transparentes, unverbindliches Angebot</strong></div></li>
        <li>{icon('check')}<div><strong>10 % Rabatt für Neukunden</strong></div></li>
      </ul>
      <ul class="contact-list">
        <li><a href="{TEL}">{icon('phone')} {TEL_TXT}</a></li>
        <li><a href="{WA}" target="_blank" rel="noopener">{icon('whatsapp')} WhatsApp: {TEL_TXT}</a></li>
        <li><a href="mailto:{FIRMA['email']}">{icon('mail')} {FIRMA['email']}</a></li>
        <li>{icon('clock')} {FIRMA['oeffnungszeiten']}</li>
      </ul>
    </div>
    <div class="cta-form">
      {anfrage_formular('form-kontakt', 'Schnellanfrage', 'Antwort vom Inhaber persönlich – kostenlos &amp; unverbindlich.', 'Startseite – Abschluss-CTA')}
    </div>
  </div>
</section>
{S.bildnachweise([x['slug'] for x in S.STAEDTE])}
"""


def jsonld_firma():
    lat, lon = FIRMA["geo"]
    return {
        "@context": "https://schema.org",
        "@type": "MovingCompany",
        "@id": SITE_URL + "/#firma",
        "name": FIRMA["name"],
        "alternateName": FIRMA["kurzname"],
        "url": SITE_URL + "/",
        "logo": SITE_URL + "/bilder/logo/logo-rund.jpg",
        "image": SITE_URL + "/bilder/kunde/ueber-uns-team.webp",
        "telephone": FIRMA["telefon_link"],
        "email": FIRMA["email"],
        "founder": {"@type": "Person", "name": FIRMA["inhaber"]},
        "address": {"@type": "PostalAddress", "streetAddress": FIRMA["strasse"], "postalCode": FIRMA["plz"],
                    "addressLocality": FIRMA["ort"], "addressRegion": "Nordrhein-Westfalen", "addressCountry": FIRMA["land"]},
        "geo": {"@type": "GeoCoordinates", "latitude": lat, "longitude": lon},
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                       "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                                       "opens": "08:00", "closes": "18:00"}],
        "areaServed": {"@type": "GeoCircle", "geoMidpoint": {"@type": "GeoCoordinates", "latitude": lat, "longitude": lon},
                       "geoRadius": FIRMA["radius_km"] * 1000},
        "sameAs": list(FIRMA["social"].values()),
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Leistungen",
                            "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": l["name"],
                                                                                   "url": f'{SITE_URL}/{l["slug"]}/'}}
                                                for l in LEISTUNGEN]},
    }


def write(path, html, quiet=False):
    out = ROOT / path.strip("/") / "index.html" if path != "/" else ROOT / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    if not quiet:
        print(f"  {out.relative_to(ROOT)}  ({len(html) // 1024} KB)")


def main():
    print("Seiten:")
    write("/", page(
        head("Umzug & Entrümpelung Herten | Ruckzuckräumung – kostenloses Angebot",
             "Umzüge, Entrümpelungen, Haushaltsauflösungen sowie Möbel- & Küchenmontage in Herten, Kreis Recklinghausen & Ruhrgebiet. "
             "Kostenlose Besichtigung, besenreine Übergabe. ☎ 0177 6126333",
             "/", preload_hero=True, jsonld=jsonld_firma()),
        homepage()))
    write_icons()
    import kernseiten
    import seiten
    kern, admin = kernseiten.alle(write)
    urls = seiten.alle(write, kern)
    print(f"  + {len(kern)} Kern-/Funnel-Seiten, {len(urls) - 1 - len(kern)} Leistungs-/Kombi-/Stadtseiten + sitemap.xml ({len(urls)} URLs)")
    print(f"  Admin-Seite /kunden-bewertung/: {'gebaut (Basic-Auth einrichten!)' if admin else 'NICHT gebaut – GHL_KUNDENBEWERTUNG_EMBED fehlt'}")


if __name__ == "__main__":
    main()
