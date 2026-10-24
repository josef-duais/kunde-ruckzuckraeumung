"""Lädt pro Stadt ein echtes Stadtfoto von Wikimedia Commons (Wikidata P18) inkl. Lizenz/Urheber.

Aufruf (aus website/):  python3 _build/stadtbilder_holen.py
Ergebnis: bilder/staedte/<slug>.webp (800x500) + _build/stadtbilder.json (Urheber, Lizenz, Quelle für die Bildnachweise)
Nur freie Lizenzen (CC0, Public Domain, CC BY, CC BY-SA) werden übernommen.
"""
import io
import json
import pathlib
import re
import subprocess
import time
import urllib.parse

from PIL import Image, ImageOps

from staedte_holen import UA, sparql

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "_build" / ".cache" / "stadtbilder"
OUT_DIR = ROOT / "bilder" / "staedte"
META = ROOT / "_build" / "stadtbilder.json"
FREI = re.compile(r"^(cc0|public domain|pd|attribution|cc by(-sa)? ?\d?(\.\d)?.*)$", re.I)


def curl_json(url, tries=6):
    for i in range(tries):
        r = subprocess.run(["curl", "-s", "-m", "60", "-A", UA, url], capture_output=True, text=True)
        try:
            return json.loads(r.stdout)
        except json.JSONDecodeError:
            time.sleep(4 * (i + 1))  # Commons drosselt – warten und erneut versuchen
    raise RuntimeError("Commons-API antwortet nicht")


def strip_html(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()


def main():
    staedte = json.loads((ROOT / "_build" / "staedte.json").read_text())
    meta = json.loads(META.read_text()) if META.exists() else {}
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # P18 (Bild) aller Städte
    bilder = {}
    ids = [s["qid"] for s in staedte]
    for i in range(0, len(ids), 60):
        vals = " ".join(f"wd:{q}" for q in ids[i:i + 60])
        for r in sparql(f"SELECT ?item ?img WHERE {{ VALUES ?item {{ {vals} }} ?item wdt:P18 ?img . }}"):
            bilder.setdefault(r["item"].rsplit("/", 1)[-1], urllib.parse.unquote(r["img"].rsplit("/", 1)[-1]))

    for s in staedte:
        slug, datei = s["slug"], bilder.get(s["qid"])
        ziel = OUT_DIR / f"{slug}.webp"
        if not datei or (slug in meta and ziel.exists()):
            continue
        titel = "File:" + datei
        api = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo"
               "&iiprop=url|extmetadata&iiurlwidth=1200&titles=" + urllib.parse.quote(titel))
        try:
            page = next(iter(curl_json(api)["query"]["pages"].values()))
            info = page["imageinfo"][0]
        except Exception as e:  # noqa: BLE001
            print("  ! kein imageinfo:", s["name"], e)
            continue
        em = info.get("extmetadata", {})
        lizenz = strip_html(em.get("LicenseShortName", {}).get("value", ""))
        if not FREI.match(lizenz):
            print(f"  ! Lizenz nicht frei ({lizenz}): {s['name']}")
            continue
        urheber = strip_html(em.get("Artist", {}).get("value", "")) or "Unbekannt"
        urheber = re.sub(r"\s+", " ", urheber)[:80]
        roh = CACHE / f"{slug}.jpg"
        if not roh.exists():
            subprocess.run(["curl", "-s", "-L", "-m", "90", "-A", UA, "-o", str(roh), info["thumburl"]], check=True)
            time.sleep(1.5)
        time.sleep(1.2)
        try:
            img = ImageOps.exif_transpose(Image.open(roh)).convert("RGB")
        except Exception as e:  # noqa: BLE001
            print("  ! Bild defekt:", s["name"], e)
            continue
        ImageOps.fit(img, (800, 500), Image.LANCZOS, centering=(0.5, 0.5)).save(ziel, "WEBP", quality=72, method=6)
        meta[slug] = {"datei": datei, "urheber": urheber, "lizenz": lizenz,
                      "lizenz_url": strip_html(em.get("LicenseUrl", {}).get("value", "")),
                      "quelle": info.get("descriptionurl", "")}
        print(f"  {slug}.webp  {lizenz}  {urheber[:40]}")
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(meta)} von {len(staedte)} Städten mit freiem Stadtfoto")


if __name__ == "__main__":
    main()
