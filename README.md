# Ruckzuckräumung – Website (Erst-Entwurf, Phase 1–3)

Statische Website (HTML5 + CSS + Vanilla-JS) für **Ruckzuckräumung & Umzüge-Entrümpelung**, Herten.
Läuft direkt aus `public_html` auf Hostinger – kein Framework, kein Server-Build. Repo-Root = Web-Root.

## Gebaute Seiten (200 URLs = Startseite + 199 Unterseiten, alle in `sitemap.xml`)

Bewusst auf **max. 200 Unterseiten** begrenzt (neue Domain → Google indexiert lieber wenige starke Seiten).

| Bereich | Anzahl | URLs |
|---|---|---|
| Startseite | 1 | `/` |
| Kernseiten | 5 | `/ueber-uns/`, `/galerie/`, `/kontakt/`, `/impressum/`, `/datenschutz/` |
| Funnel-Seiten | 3 | `/bewerten/`, `/rabatt/`, `/danke/` |
| Leistungsseiten | 10 | `/umzug/`, `/firmenumzug/`, `/seniorenumzug/`, `/entruempelung/`, `/haushaltsaufloesung/`, `/wohnungsaufloesung/`, `/kellerentruempelung/`, `/messie-wohnung-entruempeln/`, `/moebelmontage/`, `/kuechenmontage/` |
| Kombi-Seiten (Leistung × Stadt) | 180 | `/<leistung>-<stadt>/` für 18 Städte, z. B. `/umzug-essen/`, `/entruempelung-marl/` |
| Einsatzgebiete | 1 | `/einsatzgebiete/` (18 Städte als Bildkarten + 100-km-Radius) |
| **Nicht gebaut** | – | `/kunden-bewertung/` (Admin) – GHL-Embed fehlt |

Städte mit eigenen Seiten (`SEITEN_STAEDTE` in `daten.py`): Herten, Recklinghausen, Marl, Gladbeck, Dorsten, Castrop-Rauxel,
Datteln, Oer-Erkenschwick, Haltern am See, Waltrop (= ganzer Kreis Recklinghausen) + Gelsenkirchen, Bochum, Essen, Dortmund,
Herne, Bottrop, Oberhausen, Lünen. Einsatzgebiet bleibt 100 km.

Jede Unterseite: Hero mit scharfem Hintergrundbild (Stadtfoto bzw. Leistungs-/Kundenfoto), klare H1 mit Leistung + Stadt,
Formular rechts, Inhaber + Telefon, Umfang · Stadt · Dringlichkeit · Garantie, Referenzen-Abschnitt mit echten Kundenfotos.

**Bewertungs-Sterne:** werden nur angezeigt, wenn echte Bewertungen existieren – `BEWERTUNGEN` in `daten.py` eintragen
(Anzahl, Schnitt, Quelle, Link). Dann erscheinen goldene Sterne oben auf jeder Seite. Keine erfundenen Zahlen.

## Struktur

```
kunde-ruckzuckraeumung/        ← Repo-Root = public_html
├── index.html, <seite>/index.html   ← generiertes HTML (wird committet)
├── styles.css, main.js, icons.svg   ← gemeinsam für alle Seiten
├── sitemap.xml, robots.txt, .htaccess, favicon.svg, apple-touch-icon.png
├── fonts/archivo.woff2              ← einzige Webfont, selbst gehostet
├── bilder/logo|kunde|stock|staedte/ ← Logo, echte Kundenfotos, Unsplash-Stock, Stadtfotos (Wikimedia, Nachweis am Bild)
└── _build/                          ← Generator (per .htaccess gesperrt, wird nicht ausgeliefert)
    ├── daten.py        ← Firma, Leistungen, ALLE GHL-Codes, Domain   ← HIER pflegen
    ├── build.py        ← geteilte Bausteine + Startseite, startet alles
    ├── seiten.py       ← Leistungs-, Kombi-, Stadt-, Hub-Seiten + Sitemap
    ├── kernseiten.py   ← Über uns, Galerie, Kontakt, Bewertungen, Impressum, Datenschutz, /bewerten/, /rabatt/, /danke/
    ├── texte.py, pools.py ← Content-Engine (Texte aus echten Stadtdaten)
    ├── optimierung.py, salts.json ← hält jede Seite < 25 % Ähnlichkeit
    ├── pruefen.py, aehnlichkeit.py ← Qualitätsprüfung
    ├── staedte_holen.py, stadtbilder_holen.py, hero_bilder.py, bilder.py ← Daten/Bilder (nur bei Bedarf neu holen)
    └── kunden-bewertung.htaccess.beispiel ← Basic-Auth-Vorlage für den Admin-Bereich
```

## Bauen & prüfen

```bash
cd kunde-ruckzuckraeumung
python3 _build/optimierung.py        # nur nach Text-/Daten-Änderungen
python3 _build/build.py              # erzeugt alle Seiten + sitemap.xml
python3 _build/pruefen.py            # Links, Klicktiefe, Bausteine, Schema, Sitemap, robots
python3 _build/aehnlichkeit.py html  # Ähnlichkeit aller Kombi-Paare (< 25 %)
```

Nach CSS/JS-Änderungen `ASSET_VERSION` in `_build/build.py` erhöhen (Cache-Busting). Vorschau lokal:
`python3 -m http.server 8765 --directory kunde-ruckzuckraeumung` → http://localhost:8765

## Commit & Push (Hostinger Auto-Deploy)

```bash
cd kunde-ruckzuckraeumung
git add -A
git commit -m "Website aktualisiert"
git push
```

**Live-Adresse: https://www.ruckzuck-entruempelung-herten.de** (Push → automatisch live, ca. 10 Sekunden)

| Was | Wo | Einstellung |
|---|---|---|
| Domain | STRATO (Domainverwaltung → DNS) | A `@` → `156.67.74.45`, AAAA `@` → `2a02:4780:b:743:0:2a7b:32e8:10`, `www` folgt der Domain; MX/E-Mail unverändert bei STRATO |
| Hosting | Hostinger, Website **ruckzuck-entruempelung-herten.de** | Erweitert → GIT: Repo `kunde-ruckzuckraeumung`, Branch `main`, Root `public_html`, Auto-Deployment aktiv; Lifetime SSL |
| Vorschau (alt) | Hostinger, Ordner `wachstum-medien.de/public_html/ruckzuckraumung` | nicht mehr per Git verbunden (Git der Hauptwebsite nutzt jetzt ein anderes Repo); dortige `.htaccess` leitet alles per 301 auf die Hauptadresse |

- „main“ ist der **Git-Branch**, nicht die Hauptwebsite wachstum-medien.de – die wird nie verändert.
- Die `.htaccess` leitet alle Nebenadressen (ohne www, Subdomain, Unterordner) per 301 auf `https://www.ruckzuck-entruempelung-herten.de`.
- Das alte STRATO-Webhosting („STRATO Hosting Basic“) wird für die Website nicht mehr benötigt – vor einer Kündigung prüfen,
  ob dort noch E-Mail-Postfächer genutzt werden (MX zeigt weiter auf STRATO).

## Wo welcher GHL-Code sitzt (alle in `_build/daten.py`)

| Variable | Platzhalter | Wird eingesetzt auf | Status |
|---|---|---|---|
| `GHL_CHAT_WIDGET_SNIPPET` | `{{GHL_CHAT_WIDGET_SNIPPET}}` | allen Seiten vor `</body>` | fehlt → Chat-Button öffnet WhatsApp |
| `GHL_BEWERTUNGEN_EMBED` | `{{GHL_BEWERTUNGEN_EMBED}}` | Bewertungs-Abschnitt aller Seiten | fehlt → Abschnitt wird ausgeblendet (kein Platzhalter) |
| `GHL_SURVEY_EMBED` | `{{GHL_SURVEY_EMBED}}` | `/bewerten/` | fehlt → natives Bewertungsformular (FormSubmit) |
| `GHL_RABATT_FORMULAR_EMBED` | `{{GHL_RABATT_FORMULAR_EMBED}}` | `/rabatt/` | fehlt → natives Rabatt-Formular (FormSubmit) |
| `GHL_KUNDENBEWERTUNG_EMBED` | `{{GHL_KUNDENBEWERTUNG_EMBED}}` | `/kunden-bewertung/` (Admin) | fehlt → Seite wird nicht gebaut |
| `GOOGLE_MAPS_EMBED` | `{{GOOGLE_MAPS_EMBED}}` | Startseite, `/kontakt/` | Standard-Embed für Josefstr. 69 |
| `SITE_URL` | `{{DOMAIN}}` | Canonical, Sitemap, Schema, FormSubmit-Redirect | vorläufig ruckzuck-entruempelung-herten.de |

Alle GHL-Embeds und Google Maps laden **erst nach Einwilligung** (Kategorie „Funktional“) – vorher 0 iframes.
`form_embed.js` wird bei GHL-Formularen einmal auf Body-Ebene nachgeladen. Nach dem Eintragen: `python3 _build/build.py`, dann pushen.

## Manuelle Schritte nach dem Livegang

### 1. FormSubmit aktivieren (Pflicht – sonst kommen keine Anfragen an)
Alle Anfrageformulare senden per FormSubmit an **ruckzuckraeumung@web.de** und leiten danach auf `/danke/` weiter (`_next`).
1. Seite live → ein Formular einmal selbst absenden.
2. FormSubmit schickt eine **Bestätigungsmail** an ruckzuckraeumung@web.de → Link **einmal anklicken**.
3. Optional (Spamschutz): den Alias-Hash aus der Mail in `daten.py` bei `FORMSUBMIT_ZIEL` statt der E-Mail eintragen und neu bauen.

### 2. GHL-Redirect für das Rabatt-Formular
Sobald das GHL-Rabatt-Formular eingebunden ist: in GHL → Formular → **On Submit → Redirect to URL →**
`https://www.ruckzuck-entruempelung-herten.de/danke/` (Domain ggf. anpassen). Das native FormSubmit-Formular leitet bereits per `_next` weiter.

### 3. Admin-Bereich `/kunden-bewertung/` schützen (sobald gebaut)
Die Seite ist nirgends verlinkt, steht nicht in der Sitemap und ist per `robots.txt` (`Disallow: /kunden-bewertung/`) ausgeschlossen –
**zusätzlich** per Basic-Auth schützen: Vorlage `_build/kunden-bewertung.htaccess.beispiel` als `kunden-bewertung/.htaccess` ablegen
(oder in hPanel → Erweitert → „Passwortgeschützte Verzeichnisse“ den Ordner `kunden-bewertung` schützen).

## Fehlliste
Siehe [FEHLLISTE.md](FEHLLISTE.md).
