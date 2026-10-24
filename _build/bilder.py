"""Bild-Pipeline: Logo freistellen, Kundenbilder + Stockbilder als WebP in passenden Größen erzeugen.

Aufruf (aus dem Ordner website/):  python3 _build/bilder.py
Quellen:
  - Kundenbilder: ZIP-Dateien im Kunden-Ordner (eine Ebene über website/)
  - Stockbilder: Unsplash (Unsplash-Lizenz, kommerziell frei), IDs in STOCK unten
Ergebnis: /bilder/logo, /bilder/kunde, /bilder/stock  (+ bilder/stock/LIZENZEN.md)
"""
import io
import pathlib
import subprocess
import zipfile

import numpy as np
from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent          # website/
KUNDE = ROOT.parent                                            # Kunden-Ordner
CACHE = ROOT / "_build" / ".cache"
OUT = ROOT / "bilder"

# Kundenbild -> (Zielname, Breite, Höhe)  — Crop zentriert auf Seitenverhältnis
KUNDENBILDER = {
    "IMG_0051.jpeg": [("galerie-tv-wand-abbau", 600, 600)],
    "IMG_0053.jpeg": [("galerie-kartons-wohnung", 600, 600)],
    "IMG_0060.jpeg": [("galerie-transporter-beladen", 600, 600)],
    "IMG_0065.jpeg": [("galerie-entruempelung-vorher", 600, 600), ("leistung-entruempelung", 640, 480)],
    "IMG_0068.jpeg": [("galerie-keller-besenrein", 600, 600), ("leistung-kellerentruempelung", 640, 480)],
    "IMG_0513.jpeg": [("galerie-schrankmontage", 600, 600), ("leistung-moebelmontage", 640, 480)],
    "IMG_0515.jpeg": [("galerie-wohnzimmer-umzug", 600, 600)],
    "IMG_0523.jpeg": [("galerie-sideboard-montage", 600, 600)],
    "IMG_0538.jpeg": [("galerie-wohnung-besenrein", 600, 600), ("leistung-wohnungsaufloesung", 640, 480)],
    "IMG_0640.jpeg": [("galerie-moebeltransport", 600, 600)],
    "IMG_0641.jpeg": [("galerie-verladen-transporter", 600, 600)],
    "IMG_0645.jpeg": [("ueber-uns-team", 720, 860)],
    "IMG_0646.jpeg": [("galerie-moebel-verpacken", 600, 600)],
}

# Stockbilder (Unsplash) -> (Zielname, Breite, Höhe)
STOCK = {
    "1730154838368-c37b1fdebcf6": [("hero-umzugskartons", 1600, 1000)],
    "1714647211902-bb711d643a17": [("leistung-umzug", 640, 480)],
    "1763307411415-096281389c41": [("leistung-firmenumzug", 640, 480)],
    "1725278484721-b20373781f43": [("leistung-haushaltsaufloesung", 640, 480)],
    "1772475385442-9e2c59cab288": [("leistung-kuechenmontage", 640, 480)],
}


def save_webp(img, path, w, h, q=78):
    img = ImageOps.fit(img.convert("RGB"), (w, h), Image.LANCZOS, centering=(0.5, 0.45))
    img.save(path, "WEBP", quality=q, method=6)
    print(f"  {path.relative_to(ROOT)}  {w}x{h}  {path.stat().st_size // 1024} KB")


def kunden_quellen():
    files = {}
    for z in sorted(KUNDE.glob("Bilder*.zip")):
        with zipfile.ZipFile(z) as zf:
            for name in zf.namelist():
                files[pathlib.Path(name).name] = zf.read(name)
    return files


def logo(files):
    """Wortmarke aus dem runden Logo freistellen (Weiß -> transparent) + helle Variante für dunklen Grund."""
    src = Image.open(io.BytesIO(files["8B8A28D5-477E-4D4B-809E-B68CB41BAE55.png"])).convert("RGB")
    s = src.width / 1024
    crop = src.crop((int(80 * s), int(390 * s), int(971 * s), int(510 * s)))
    a = np.asarray(crop).astype(np.float32) / 255
    # grünen Pinselstrich des Rund-Logos oben rechts entfernen (über dem "ung")
    a[: int(14 * s), int((850 - 80) * s):] = 1.0
    alpha = 1 - a.min(axis=2)                                  # "Un-blend" gegen Weiß
    alpha = np.clip((alpha - 0.06) / 0.94, 0, 1)
    safe = np.maximum(alpha, 1e-3)[..., None]
    rgb = np.clip((a - (1 - safe)) / safe, 0, 1)
    rgba = np.dstack([rgb, alpha])
    # helle Variante: unbunte (schwarze) Pixel -> weiß, Grün aufhellen
    sat = rgb.max(axis=2) - rgb.min(axis=2)
    light = rgb.copy()
    grey = sat < 0.18
    light[grey] = 1.0
    light[~grey] = np.clip(rgb[~grey] * 0.55 + np.array([0.18, 0.62, 0.26]) * 0.9, 0, 1)
    for name, data in (("logo", rgba), ("logo-hell", np.dstack([light, alpha]))):
        im = Image.fromarray((data * 255).astype(np.uint8), "RGBA")
        im = im.crop(im.getbbox())
        im.thumbnail((640, 640), Image.LANCZOS)
        p = OUT / "logo" / f"{name}.webp"
        im.save(p, "WEBP", quality=90, method=6)
        im.save(OUT / "logo" / f"{name}.png", optimize=True)
        print(f"  {p.relative_to(ROOT)}  {im.size}")
    # Social-/Schema-Bild: komplettes Rund-Logo
    full = src.copy()
    full.thumbnail((800, 800), Image.LANCZOS)
    full.save(OUT / "logo" / "logo-rund.jpg", "JPEG", quality=85)


def stock():
    CACHE.mkdir(parents=True, exist_ok=True)
    lines = ["# Stockbilder – Lizenz", "", "Quelle: Unsplash (https://unsplash.com/license) – kommerziell frei nutzbar, keine Namensnennung nötig.", ""]
    for pid, targets in STOCK.items():
        cached = CACHE / f"{pid}.jpg"
        if not cached.exists():
            url = f"https://images.unsplash.com/photo-{pid}?w=2000&q=85&fm=jpg"
            subprocess.run(["curl", "-sfL", "-m", "90", "-o", str(cached), url], check=True)
        img = Image.open(cached)
        for name, w, h in targets:
            save_webp(img, OUT / "stock" / f"{name}.webp", w, h)
            if name.startswith("hero"):
                save_webp(img, OUT / "stock" / f"{name}-960.webp", 960, 600, q=72)
            lines.append(f"- `{name}.webp` ← https://images.unsplash.com/photo-{pid}")
    (OUT / "stock" / "LIZENZEN.md").write_text("\n".join(lines) + "\n")


# Große Galerie-Versionen (ohne Zuschnitt, lange Kante 1400 px) – nur echte Kundenfotos
GALERIE_GROSS = ["IMG_0051.jpeg", "IMG_0053.jpeg", "IMG_0060.jpeg", "IMG_0063.png", "IMG_0065.jpeg", "IMG_0068.jpeg",
                 "IMG_0513.jpeg", "IMG_0515.jpeg", "IMG_0523.jpeg", "IMG_0538.jpeg", "IMG_0640.jpeg", "IMG_0641.jpeg",
                 "IMG_0645.jpeg", "IMG_0646.jpeg"]


def galerie_gross(files):
    ziel = OUT / "kunde" / "gross"
    ziel.mkdir(parents=True, exist_ok=True)
    for name in GALERIE_GROSS:
        img = ImageOps.exif_transpose(Image.open(io.BytesIO(files[name]))).convert("RGB")
        if name == "IMG_0063.png":  # Screenshot mit schwarzen Balken -> Inhalt zuschneiden
            a = np.asarray(img).mean(axis=2)
            rows = np.where(a.mean(axis=1) > 12)[0]
            img = img.crop((0, rows.min(), img.width, rows.max() + 1))
        img.thumbnail((1400, 1400), Image.LANCZOS)
        p = ziel / f"{pathlib.Path(name).stem.lower()}.webp"
        img.save(p, "WEBP", quality=76, method=6)
        q = ziel / f"{pathlib.Path(name).stem.lower()}-klein.webp"
        ImageOps.fit(img, (600, 600), Image.LANCZOS, centering=(0.5, 0.45)).save(q, "WEBP", quality=74, method=6)
        print(f"  {p.relative_to(ROOT)}  {img.size}")


def main():
    files = kunden_quellen()
    print("Galerie (groß):")
    galerie_gross(files)
    print("Logo:")
    logo(files)
    print("Kundenbilder:")
    for src, targets in KUNDENBILDER.items():
        img = ImageOps.exif_transpose(Image.open(io.BytesIO(files[src])))
        for name, w, h in targets:
            save_webp(img, OUT / "kunde" / f"{name}.webp", w, h)
    print("Stockbilder:")
    stock()


if __name__ == "__main__":
    main()
