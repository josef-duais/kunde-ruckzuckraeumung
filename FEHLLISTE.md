# Fehlliste – Erst-Entwurf (Stand 24.10.2026)

## Fehlt vom Kunden
| # | Was | Wo eintragen | Aktuell |
|---|-----|-------------|---------|
| 1 | GHL Chat-Widget-Snippet | `_build/daten.py` → `GHL_CHAT_WIDGET_SNIPPET` | Chat-Button öffnet WhatsApp |
| 2 | GHL Bewertungs-Widget | `GHL_BEWERTUNGEN_EMBED` | Bewertungs-Abschnitt ausgeblendet |
| 3 | GHL Bewertungs-Survey | `GHL_SURVEY_EMBED` | `/bewerten/` nutzt natives FormSubmit-Formular |
| 4 | GHL Rabatt-Formular | `GHL_RABATT_FORMULAR_EMBED` | `/rabatt/` nutzt natives FormSubmit-Formular |
| 5 | GHL Kunden-Bewertung (Admin) | `GHL_KUNDENBEWERTUNG_EMBED` | `/kunden-bewertung/` **nicht gebaut** |
| 6 | Finale Domain | `SITE_URL` | aktuell ruckzuckraumung.wachstum-medien.de – bei finaler Domain in `SITE_URL` + `robots.txt` ändern |
| 7 | Exakte Geo-Koordinaten Josefstr. 69 | `FIRMA["geo"]` | Herten-Zentrum |
| 8 | Echte Bewertungen (z. B. Google-Profil) | `BEWERTUNGEN` in `daten.py` | noch keine – Sterne erscheinen automatisch, sobald eingetragen |
| 9 | Logo als Vektor/PNG transparent | `bilder/logo/` | aus dem Rund-Logo freigestellt |
| 10 | Porträtfoto des Inhabers | `/ueber-uns/`, Startseite | Initialen „LK“ als Platzhalter (kein Stockfoto) |
| 11 | Rabattbedingungen (Mindestwert? kombinierbar?) | `/rabatt/` | „10 % für Neukunden auf den ersten Auftrag“ |

## ⚠️ Vor dem Start von Google Ads bestätigen
- **Garantie-Texte** (auf jeder Unterseite): „Kostenlos & unverbindlich“, „Preis steht vorher fest – schriftliches Angebot,
  keine versteckten Kosten“, „Besenreine Übergabe“ / „Sorgfältiger Transport“ / „Sauber & stabil montiert“.
  Garantien in der Werbung sind rechtlich bindend (UWG) – Inhaber muss sie so leisten können. Texte: `_build/seiten.py` (`GARANTIE_*`).
- **Dringlichkeit:** „Kurzfristige Termine möglich – auch samstags“ – nur behalten, wenn das real zutrifft.
- **Keine Sterne ohne echte Bewertungen** – erfundene Bewertungszahlen wären irreführend (UWG) und verstoßen gegen die
  Google-Ads-Richtlinien (Falschdarstellung → Kontosperre).

## ⚠️ Rechtliches – vor Livegang klären
- **Datenschutzerklärung ist veraltet.** Sie ist wortgetreu aus dem Bestand übernommen (Stand 11.09.2026) und nennt
  **STRATO** als Hoster und „keine eingebetteten Karten“. Die neue Seite nutzt Hostinger, FormSubmit (Formularversand),
  Google Maps und GHL (nach Einwilligung), einen Cookie-Consent (localStorage) und lokal gehostete Wikimedia-Bilder.
  → Datenschutzerklärung vom Kunden/Rechtsberatung aktualisieren lassen und in `_build/kernseiten.py` (`DATENSCHUTZ`) ersetzen.
  Es wurden bewusst **keine Rechtstexte erfunden**.
- **Firmenname uneinheitlich:** Impressum „Ruckzuckräumung & Umzüge-Entrümpelung“, Briefing „Ruckzuckräumung Umzüge und
  Entrümpelung“. Website-NAP nutzt „Ruckzuckräumung Umzüge & Entrümpelung“. Für Local SEO eine Schreibweise festlegen (`FIRMA["name"]`).
- Impressum ohne USt-IdNr. (laut Bestand „liegt derzeit nicht vor“) – übernommen wie geliefert.

## Abweichungen von der Vorgabe (bewusst)
- `/bewerten/` und `/rabatt/` sind trotz fehlender GHL-Embeds gebaut – mit nativem FormSubmit-Formular als Ersatz.
  Grund: Sie sind von jeder Seite verlinkt (Bewerten-Button, Rabatt-Karte); ohne Seite gäbe es tausende defekte Links.
  Sobald der GHL-Code eingetragen ist, ersetzt er das Ersatzformular automatisch (consent-gated).
- `/danke/` hat kein Anfrageformular (Besucher hat gerade eins abgeschickt) – stattdessen Click-to-Call + „Zurück zur Startseite“.
- Referenzbild `unterseite.png` wurde nie geliefert – Unterseiten folgen dem Aufbau der Startseite.
- Seitenumfang auf 200 URLs reduziert (18 Städte × 10 Leistungen); Stadt-Archive und `/bewertungen/` entfallen.
- Hero-Hintergrundbild nur ab 900 px Breite; mobil dunkler Verlauf (Performance-Vorgabe aus Phase 1).

## Phase 2 – generisch
- Ortsbezug ausschließlich aus öffentlichen Daten (Wikidata) – keine Pro-Stadt-Erfahrungen des Kunden.
- Alle 18 Seiten-Städte haben ein hochauflösendes, frei lizenziertes Stadtfoto (Nachweis auf jeder Seite).

## Inhaltliche Annahmen (bitte bestätigen)
- 10 % Rabatt für **alle Neukunden** auf den ersten Auftrag.
- Einsatzradius **100 km** um Herten; eigene Seiten für 18 Städte (Kreis Recklinghausen + Nachbarstädte).
- Leistungen: Umzug, Firmenumzug, Seniorenumzug, Entrümpelung, Haushaltsauflösung, Wohnungsauflösung, Kellerentrümpelung,
  Messie-Wohnung entrümpeln, Möbelmontage, Küchenmontage.
- Keine erfundenen Zahlen, Jahre, Zertifikate oder Bewertungen.
