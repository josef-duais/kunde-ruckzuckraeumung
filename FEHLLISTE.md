# Fehlliste – Erst-Entwurf (Stand 24.10.2026)

## Fehlt vom Kunden
| # | Was | Wo eintragen | Aktuell |
|---|-----|-------------|---------|
| 1 | GHL Chat-Widget-Snippet | `_build/daten.py` → `GHL_CHAT_WIDGET_SNIPPET` | Chat-Button öffnet WhatsApp |
| 2 | GHL Bewertungs-Widget | `GHL_BEWERTUNGEN_EMBED` | Hinweis „Noch keine Online-Bewertungen“ + Button |
| 3 | GHL Bewertungs-Survey | `GHL_SURVEY_EMBED` | `/bewerten/` nutzt natives FormSubmit-Formular |
| 4 | GHL Rabatt-Formular | `GHL_RABATT_FORMULAR_EMBED` | `/rabatt/` nutzt natives FormSubmit-Formular |
| 5 | GHL Kunden-Bewertung (Admin) | `GHL_KUNDENBEWERTUNG_EMBED` | `/kunden-bewertung/` **nicht gebaut** |
| 6 | Finale Domain | `SITE_URL` | vorläufig www.ruckzuck-entruempelung-herten.de (auch in `robots.txt`) |
| 7 | Exakte Geo-Koordinaten Josefstr. 69 | `FIRMA["geo"]` | Herten-Zentrum |
| 8 | Google-Bewertungen / Google-Unternehmensprofil | – | noch keine – daher nirgends Sterne-Rating |
| 9 | Logo als Vektor/PNG transparent | `bilder/logo/` | aus dem Rund-Logo freigestellt |
| 10 | Porträtfoto des Inhabers | `/ueber-uns/`, Startseite | Initialen „LK“ als Platzhalter (kein Stockfoto) |
| 11 | Rabattbedingungen (Mindestwert? kombinierbar?) | `/rabatt/` | „10 % für Neukunden auf den ersten Auftrag“ |

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

## Phase 2 – generisch
- Ortsbezug ausschließlich aus öffentlichen Daten (Wikidata) – keine Pro-Stadt-Erfahrungen des Kunden.
- Herne, Münster, Frechen ohne freies Stadtfoto (Lizenz) → Leistungsfoto als Ersatz.

## Inhaltliche Annahmen (bitte bestätigen)
- 10 % Rabatt für **alle Neukunden** auf den ersten Auftrag.
- Einsatzradius **100 km** um Herten, 206 Städte mit Stadtrecht.
- Leistungen: Umzug, Firmenumzug, Seniorenumzug, Entrümpelung, Haushaltsauflösung, Wohnungsauflösung, Kellerentrümpelung,
  Messie-Wohnung entrümpeln, Möbelmontage, Küchenmontage.
- Keine erfundenen Zahlen, Jahre, Zertifikate oder Bewertungen.
