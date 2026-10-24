"""Zentrale Daten: Firma, Leistungen, Einsatzgebiete, Embeds.

Phase 2 erweitert nur diese Datei (neue Leistungen/Städte) – build.py erzeugt die Seiten daraus.
"""

# TODO: Finale Domain eintragen, sobald sie feststeht (wird für Canonical, OG, JSON-LD und FormSubmit-Redirect genutzt).
SITE_URL = "https://www.ruckzuck-entruempelung-herten.de"

FIRMA = {
    "name": "Ruckzuckräumung Umzüge & Entrümpelung",
    "kurzname": "Ruckzuckräumung",
    "inhaber": "Lucien Fynn Khaouli",
    "strasse": "Josefstr. 69",
    "plz": "45699",
    "ort": "Herten",
    "region": "Kreis Recklinghausen",
    "land": "DE",
    "telefon_anzeige": "0177 6126333",
    "telefon_link": "+491776126333",
    "whatsapp_link": "https://wa.me/491776126333",
    "email": "ruckzuckraeumung@web.de",
    "oeffnungszeiten": "Mo–Sa 8–18 Uhr",
    # TODO: Exakte Koordinaten der Josefstr. 69 prüfen (aktuell Herten-Zentrum)
    "geo": (51.5958, 7.1406),
    "radius_km": 100,
    "social": {
        "Instagram": "https://instagram.com/ruckzuckraeumungumzug",
        "Facebook": "https://www.facebook.com/share/1FHutB7AJP/",
        "TikTok": "https://www.tiktok.com/@ruckzuckramungumz",
    },
}

# FormSubmit: Nach der ersten Aktivierung die E-Mail durch den Alias-Hash ersetzen (siehe README).
FORMSUBMIT_ZIEL = FIRMA["email"]

# GHL-Embeds – nur einbauen, nie erstellen. Leer = Platzhalter + Fehlliste.
GHL_CHAT_WIDGET_SNIPPET = ""      # TODO: {{GHL_CHAT_WIDGET_SNIPPET}}
GHL_BEWERTUNGEN_EMBED = ""        # TODO: {{GHL_BEWERTUNGEN_EMBED}}
GHL_SURVEY_EMBED = ""             # TODO: {{GHL_SURVEY_EMBED}} – Bewertungs-Survey für /bewerten/
GHL_RABATT_FORMULAR_EMBED = ""    # TODO: {{GHL_RABATT_FORMULAR_EMBED}} – Rabatt-Formular für /rabatt/
GHL_KUNDENBEWERTUNG_EMBED = ""    # TODO: {{GHL_KUNDENBEWERTUNG_EMBED}} – Admin-Formular für /kunden-bewertung/ (Seite wird erst gebaut, wenn gesetzt)
GOOGLE_MAPS_EMBED = (             # {{GOOGLE_MAPS_EMBED}} – Standard-Embed ohne API-Key, durch GHL/Maps-Code ersetzbar
    "https://www.google.com/maps?q=Josefstr.+69,+45699+Herten&z=10&output=embed"
)

# Leistungen (freigegeben). grid=True -> Karte im Homepage-Raster (8 Stück, wie Referenz).
LEISTUNGEN = [
    {"slug": "umzug", "name": "Umzug", "gruppe": "Umzüge", "grid": True,
     "bild": "/bilder/stock/leistung-umzug.webp", "alt": "Frau packt Umzugskartons in einer hellen Wohnung",
     "text": "Privatumzüge in Herten und Umgebung – sorgfältig verpackt, sicher transportiert und am neuen Ort wieder aufgebaut."},
    {"slug": "firmenumzug", "name": "Firmenumzug", "gruppe": "Umzüge", "grid": True,
     "bild": "/bilder/stock/leistung-firmenumzug.webp", "alt": "Archivkartons und Aktenschrank für einen Büroumzug",
     "text": "Büro- und Geschäftsumzüge mit klarer Planung – damit Ihr Betrieb schnell wieder arbeitsfähig ist."},
    {"slug": "seniorenumzug", "name": "Seniorenumzug", "gruppe": "Umzüge", "grid": False},
    {"slug": "entruempelung", "name": "Entrümpelung", "gruppe": "Entrümpelung", "grid": True,
     "bild": "/bilder/kunde/leistung-entruempelung.webp", "alt": "Vollgestellter Raum vor der Entrümpelung durch Ruckzuckräumung",
     "text": "Wohnung, Haus, Keller oder Garage: Wir räumen komplett, entsorgen umweltgerecht und übergeben besenrein."},
    {"slug": "haushaltsaufloesung", "name": "Haushaltsauflösung", "gruppe": "Entrümpelung", "grid": True,
     "bild": "/bilder/stock/leistung-haushaltsaufloesung.webp", "alt": "Abstellraum mit altem Herd und Hausrat vor der Haushaltsauflösung",
     "text": "Diskret und respektvoll – auch im Nachlass. Verwertbares wird geprüft, der Rest fachgerecht entsorgt."},
    {"slug": "wohnungsaufloesung", "name": "Wohnungsauflösung", "gruppe": "Entrümpelung", "grid": True,
     "bild": "/bilder/kunde/leistung-wohnungsaufloesung.webp", "alt": "Leeres, besenreines Zimmer nach der Wohnungsauflösung",
     "text": "Komplette Räumung inklusive Demontage – übergabefertig für Vermieter, Erben oder Käufer."},
    {"slug": "kellerentruempelung", "name": "Kellerentrümpelung", "gruppe": "Entrümpelung", "grid": True,
     "bild": "/bilder/kunde/leistung-kellerentruempelung.webp", "alt": "Leerer, besenreiner Kellerraum nach der Entrümpelung",
     "text": "Keller, Dachboden und Garage schnell wieder frei – schwere Lasten und enge Treppen inklusive."},
    {"slug": "messie-wohnung-entruempeln", "name": "Messie-Wohnung entrümpeln", "gruppe": "Entrümpelung", "grid": False},
    {"slug": "moebelmontage", "name": "Möbelmontage", "gruppe": "Montage", "grid": True,
     "bild": "/bilder/kunde/leistung-moebelmontage.webp", "alt": "Monteur von Ruckzuckräumung baut einen Kleiderschrank auf",
     "text": "Schränke, Betten, Regale: Ab- und Aufbau aller gängigen Systeme – sauber, fachgerecht und passgenau."},
    {"slug": "kuechenmontage", "name": "Küchenmontage", "gruppe": "Montage", "grid": True,
     "bild": "/bilder/stock/leistung-kuechenmontage.webp", "alt": "Neu montierte weiße Küche mit Holzschublade",
     "text": "Küchen fachgerecht abbauen, transportieren und am neuen Ort exakt ausgerichtet wieder aufbauen."},
]

# Einsatzgebiete im Umkreis von 50–100 km um Herten (Name, Lat, Lon, Top-Stadt für Navigation)
STAEDTE = [
    ("Herten", 51.595, 7.141, True), ("Recklinghausen", 51.614, 7.197, True), ("Gelsenkirchen", 51.517, 7.086, True),
    ("Marl", 51.656, 7.090, True), ("Gladbeck", 51.571, 6.985, True), ("Bochum", 51.482, 7.216, True),
    ("Essen", 51.456, 7.012, True), ("Dortmund", 51.514, 7.468, True),
    ("Herne", 51.538, 7.219, False), ("Bottrop", 51.524, 6.929, False), ("Dorsten", 51.661, 6.965, False),
    ("Castrop-Rauxel", 51.555, 7.312, False), ("Datteln", 51.654, 7.341, False), ("Oer-Erkenschwick", 51.642, 7.250, False),
    ("Haltern am See", 51.743, 7.183, False), ("Waltrop", 51.624, 7.394, False), ("Oberhausen", 51.496, 6.863, False),
    ("Mülheim an der Ruhr", 51.427, 6.883, False), ("Duisburg", 51.434, 6.762, False), ("Lünen", 51.616, 7.528, False),
    ("Selm", 51.693, 7.474, False), ("Werne", 51.664, 7.634, False), ("Bergkamen", 51.616, 7.645, False),
    ("Kamen", 51.592, 7.665, False), ("Unna", 51.535, 7.689, False), ("Hamm", 51.681, 7.817, False),
    ("Schwerte", 51.444, 7.565, False), ("Witten", 51.443, 7.335, False), ("Hattingen", 51.399, 7.186, False),
    ("Hagen", 51.367, 7.463, False), ("Velbert", 51.340, 7.043, False), ("Wuppertal", 51.256, 7.150, False),
    ("Düsseldorf", 51.227, 6.774, False), ("Moers", 51.451, 6.627, False), ("Krefeld", 51.339, 6.586, False),
    ("Wesel", 51.658, 6.618, False), ("Bocholt", 51.838, 6.616, False), ("Dülmen", 51.830, 7.278, False),
    ("Coesfeld", 51.946, 7.168, False), ("Münster", 51.961, 7.626, False), ("Köln", 50.938, 6.960, False),
]

# Städte, die auf der Radius-Karte beschriftet werden
KARTE_LABELS = {"Herten", "Essen", "Dortmund", "Münster", "Düsseldorf", "Duisburg", "Hamm",
                "Wuppertal", "Köln", "Bocholt", "Haltern am See"}


def slugify(text):
    t = text.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        t = t.replace(a, b)
    out = "".join(c if c.isalnum() else "-" for c in t)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")
