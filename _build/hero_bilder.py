"""Scharfe Hero-Hintergrundbilder (1600 × 760) für alle Unterseiten.

- Städte (18 Kombi-Städte): echtes Stadtfoto von Wikimedia Commons in hoher Auflösung (freie Lizenz, Nachweis auf der Seite)
- Leistungen: Unsplash-Stock (kommerziell frei) oder echte Kundenfotos in Originalauflösung
- Kernseiten: echte Kundenfotos in Originalauflösung

Aufruf (aus website-Root):  python3 _build/hero_bilder.py
Ergebnis: bilder/hero/*.webp
"""
import io
import json
import pathlib
import re
import subprocess
import sys
import time
import urllib.parse

from PIL import Image, ImageOps

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from bilder import kunden_quellen  # noqa: E402
from daten import SEITEN_STAEDTE  # noqa: E402
from stadtbilder_holen import curl_json, strip_html, FREI  # noqa: E402
from staedte_holen import UA  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "bilder" / "hero"
CACHE = ROOT / "_build" / ".cache" / "hero"
META = ROOT / "_build" / "stadtbilder.json"
GROESSE = (1600, 760)

# Ersatzfotos, wenn das Wikidata-Bild nicht frei lizenziert ist
STADT_ERSATZ = {"herne": "Herne town hall.jpg", "essen": "Zeche Zollverein abends.jpg",
                "gelsenkirchen": "Gelsenkirchen - Turfstraße - Schloss Horst 02 ies.jpg", "waltrop": "Stellwerk Bahnhof Waltrop.jpg",
                "castrop-rauxel": "Castrop-Rauxel, Baudenkmal 69, Europaplatz 2020-04-09 5035.jpg"}

# name -> ("unsplash", id) | ("kunde", datei, fokus_y)
QUELLEN = {
    "leistung-umzug": ("unsplash", "1714647211902-bb711d643a17"),
    "leistung-firmenumzug": ("unsplash", "1763307411415-096281389c41"),
    "leistung-seniorenumzug": ("kunde", "IMG_0515.jpeg", 0.55),
    "leistung-entruempelung": ("kunde", "IMG_0065.jpeg", 0.5),
    "leistung-haushaltsaufloesung": ("unsplash", "1725278484721-b20373781f43"),
    "leistung-wohnungsaufloesung": ("kunde", "IMG_0538.jpeg", 0.5),
    "leistung-kellerentruempelung": ("kunde", "IMG_0068.jpeg", 0.55),
    "leistung-messie-wohnung-entruempeln": ("kunde", "IMG_0063.png", 0.5),
    "leistung-moebelmontage": ("kunde", "IMG_0513.jpeg", 0.35),
    "leistung-kuechenmontage": ("unsplash", "1772475385442-9e2c59cab288"),
    "seite-ueber-uns": ("kunde", "IMG_0645.jpeg", 0.45),
    "seite-galerie": ("kunde", "IMG_0060.jpeg", 0.45),
    "seite-kontakt": ("kunde", "IMG_0641.jpeg", 0.45),
    "seite-rabatt": ("kunde", "IMG_0053.jpeg", 0.5),
    "seite-bewerten": ("kunde", "IMG_0646.jpeg", 0.5),
    "seite-danke": ("kunde", "IMG_0640.jpeg", 0.45),
    "seite-recht": ("kunde", "IMG_0051.jpeg", 0.5),
    "seite-einsatzgebiete": ("unsplash", "1730154838368-c37b1fdebcf6"),
}


def speichern(img, name, fokus_y=0.5):
    img = ImageOps.fit(img.convert("RGB"), GROESSE, Image.LANCZOS, centering=(0.5, fokus_y))
    p = OUT / f"{name}.webp"
    img.save(p, "WEBP", quality=74, method=6)
    print(f"  {p.relative_to(ROOT)}  {p.stat().st_size // 1024} KB")


def stadt(s, meta):
    slug = s["slug"]
    datei = STADT_ERSATZ.get(slug) or (meta.get(slug) or {}).get("datei")
    if not datei:
        print("  ! kein Stadtfoto:", slug)
        return
    api = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url|extmetadata|size"
           "&iiurlwidth=2400&titles=" + urllib.parse.quote("File:" + datei))
    info = next(iter(curl_json(api)["query"]["pages"].values()))["imageinfo"][0]
    em = info.get("extmetadata", {})
    lizenz = strip_html(em.get("LicenseShortName", {}).get("value", ""))
    if not FREI.match(lizenz):
        print(f"  ! Lizenz nicht frei ({lizenz}): {slug}")
        return
    roh = CACHE / f"stadt-{slug}.jpg"
    if not roh.exists():
        subprocess.run(["curl", "-s", "-L", "-m", "120", "-A", UA, "-o", str(roh), info["thumburl"]], check=True)
        time.sleep(1.5)
    img = ImageOps.exif_transpose(Image.open(roh))
    if img.width < 1600:
        print(f"  ! zu klein ({img.width}px): {slug}")
    speichern(img, f"stadt-{slug}")
    if slug in STADT_ERSATZ or slug not in meta:
        meta[slug] = {"datei": datei, "urheber": re.sub(r"\s+", " ", strip_html(em.get("Artist", {}).get("value", "")) or "Unbekannt")[:80],
                      "lizenz": lizenz, "lizenz_url": strip_html(em.get("LicenseUrl", {}).get("value", "")),
                      "quelle": info.get("descriptionurl", "")}
        # kleines Stadtfoto für den Inhaltsbereich nachziehen
        ImageOps.fit(img.convert("RGB"), (800, 500), Image.LANCZOS).save(ROOT / "bilder" / "staedte" / f"{slug}.webp", "WEBP", quality=72, method=6)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    meta = json.loads(META.read_text())
    staedte = {s["slug"]: s for s in json.loads((ROOT / "_build" / "staedte.json").read_text())}
    print("Städte:")
    for slug in SEITEN_STAEDTE:
        stadt(staedte[slug], meta)
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Leistungen & Seiten:")
    files = kunden_quellen()
    for name, q in QUELLEN.items():
        if q[0] == "unsplash":
            roh = CACHE / f"{q[1]}.jpg"
            if not roh.exists():
                subprocess.run(["curl", "-sfL", "-m", "120", "-o", str(roh), f"https://images.unsplash.com/photo-{q[1]}?w=2400&q=85&fm=jpg"], check=True)
            speichern(Image.open(roh), name)
        else:
            img = ImageOps.exif_transpose(Image.open(io.BytesIO(files[q[1]])))
            if q[1] == "IMG_0063.png":
                import numpy as np
                a = np.asarray(img.convert("L"))
                rows = np.where(a.mean(axis=1) > 12)[0]
                img = img.crop((0, rows.min(), img.width, rows.max() + 1))
            speichern(img, name, q[2])
    lic = OUT / "LIZENZEN.md"
    lic.write_text("# Hero-Bilder\n\n- stadt-*.webp: Wikimedia Commons (Nachweis siehe _build/stadtbilder.json, auf jeder Seite verlinkt)\n"
                   "- leistung-*/seite-*: echte Kundenfotos bzw. Unsplash (https://unsplash.com/license)\n")


if __name__ == "__main__":
    main()
