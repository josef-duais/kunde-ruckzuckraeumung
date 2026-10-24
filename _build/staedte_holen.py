"""Holt echte, öffentliche Stadtdaten aus Wikidata (CC0) für alle Städte mit Stadtrecht im Umkreis von Herten.

Aufruf (aus website/):  python3 _build/staedte_holen.py
Ergebnis: _build/staedte.json  (wird committet, damit der Build offline reproduzierbar ist)

Pro Stadt: Name, AGS, Koordinaten, Einwohner (+ Stichtag), Fläche, Höhe, PLZ, Kreis, Regierungsbezirk,
Stadtteile/Stadtbezirke, Nachbargemeinden, Typ (kreisfrei / Große kreisangehörige Stadt / Stadt).
"""
import csv
import io
import json
import math
import pathlib
import re
import subprocess
import time

from daten import FIRMA, slugify

OUT = pathlib.Path(__file__).resolve().parent / "staedte.json"
UA = "RuckzuckSiteBuilder/1.0 (static site generator; contact: site owner)"
STADT_STATUS = {"Q42744322", "Q1548518", "Q22865"}  # Stadt / Große kreisangehörige Stadt / kreisfreie Stadt


# Amtlicher Gemeindeschlüssel (AGS): Stellen 1–2 = Land, 3 = Regierungsbezirk
BUNDESLAND = {"05": "Nordrhein-Westfalen", "03": "Niedersachsen", "07": "Rheinland-Pfalz", "06": "Hessen"}
REGBEZ = {"051": "Regierungsbezirk Düsseldorf", "053": "Regierungsbezirk Köln", "055": "Regierungsbezirk Münster",
          "057": "Regierungsbezirk Detmold", "059": "Regierungsbezirk Arnsberg"}

KREIS_AGS = {"03456": "Landkreis Grafschaft Bentheim", "03459": "Landkreis Osnabrück", "07132": "Landkreis Altenkirchen (Westerwald)"}


def sparql(q, tries=4):
    for i in range(tries):
        r = subprocess.run(["curl", "-s", "-m", "180", "-G", "https://query.wikidata.org/sparql",
                            "--data-urlencode", f"query={q}", "-H", "Accept: text/csv", "-A", UA],
                           capture_output=True, text=True)
        if r.stdout.startswith(r.stdout.split("\n")[0]) and "," in r.stdout.split("\n")[0] and "Exception" not in r.stdout[:400]:
            return list(csv.DictReader(io.StringIO(r.stdout)))
        time.sleep(5 * (i + 1))
    raise RuntimeError("SPARQL fehlgeschlagen:\n" + r.stdout[:500])


def qid(uri):
    return uri.rsplit("/", 1)[-1]


def main():
    lat0, lon0 = FIRMA["geo"]
    base = sparql(f"""SELECT ?item ?ags ?loc ?dist WHERE {{
      SERVICE wikibase:around {{ ?item wdt:P625 ?loc . bd:serviceParam wikibase:center "Point({lon0} {lat0})"^^geo:wktLiteral .
        bd:serviceParam wikibase:radius "{FIRMA['radius_km']}" . bd:serviceParam wikibase:distance ?dist . }}
      ?item wdt:P439 ?ags . }}""")
    items = {}
    for r in base:
        q = qid(r["item"])
        lon, lat = map(float, r["loc"].replace("Point(", "").rstrip(")").split())
        items.setdefault(q, {"qid": q, "ags": r["ags"], "lat": lat, "lon": lon, "dist": float(r["dist"])})
    ids = list(items)
    print(f"{len(ids)} Gemeinden mit AGS im Radius")

    def batch(template, n=60):
        rows = []
        for i in range(0, len(ids), n):
            values = " ".join(f"wd:{x}" for x in ids[i:i + n])
            rows += sparql(template.replace("%VALUES%", values))
            time.sleep(1)
        return rows

    for r in batch("""SELECT ?item ?label ?type WHERE { VALUES ?item { %VALUES% }
        ?item rdfs:label ?label . FILTER(LANG(?label)="de") OPTIONAL { ?item wdt:P31 ?type } }"""):
        it = items[qid(r["item"])]
        it["name"] = r["label"]
        it.setdefault("typen", set()).add(qid(r["type"]) if r["type"] else "")

    for r in batch("""SELECT ?item ?pop ?date WHERE { VALUES ?item { %VALUES% }
        ?item p:P1082 ?st . ?st ps:P1082 ?pop . OPTIONAL { ?st pq:P585 ?date } }"""):
        it = items[qid(r["item"])]
        d = r["date"][:10] if r["date"] else ""
        if d >= it.get("pop_datum", "") or "einwohner" not in it:
            it["einwohner"], it["pop_datum"] = int(float(r["pop"])), d

    for prop, key, cast in (("P2046", "flaeche_km2", float), ("P2044", "hoehe_m", float)):
        for r in batch(f"""SELECT ?item ?v WHERE {{ VALUES ?item {{ %VALUES% }} ?item wdt:{prop} ?v . }}"""):
            items[qid(r["item"])].setdefault(key, cast(r["v"]))

    for r in batch("""SELECT ?item ?plz WHERE { VALUES ?item { %VALUES% } ?item wdt:P281 ?plz . }"""):
        items[qid(r["item"])].setdefault("plz", set()).add(r["plz"])

    # Kreis + Regierungsbezirk (P131-Kette)
    for r in batch("""SELECT ?item ?k ?kLabel ?kt ?rb ?rbLabel WHERE { VALUES ?item { %VALUES% }
        ?item wdt:P131 ?k . OPTIONAL { ?k wdt:P31 ?kt } OPTIONAL { ?k wdt:P131 ?rb . ?rb wdt:P31 wd:Q22721 }
        SERVICE wikibase:label { bd:serviceParam wikibase:language "de". } }"""):
        it = items[qid(r["item"])]
        kt = qid(r["kt"]) if r["kt"] else ""
        if kt in ("Q106658", "Q85482556", "Q20738811") or "kreis" in r["kLabel"].lower():
            it["kreis"] = r["kLabel"]
        if "Regierungsbezirk" in r.get("kLabel", ""):
            it["regbez"] = r["kLabel"]
        if r.get("rbLabel"):
            it["regbez"] = r["rbLabel"]

    for r in batch("""SELECT ?item ?nLabel WHERE { VALUES ?item { %VALUES% } ?item wdt:P47 ?n . ?n wdt:P439 ?x .
        SERVICE wikibase:label { bd:serviceParam wikibase:language "de". } }"""):
        items[qid(r["item"])].setdefault("nachbarn", set()).add(r["nLabel"])

    for r in batch("""SELECT ?item ?tLabel WHERE { VALUES ?item { %VALUES% } ?item wdt:P150 ?t .
        FILTER NOT EXISTS { ?t wdt:P576 ?e }
        SERVICE wikibase:label { bd:serviceParam wikibase:language "de". } }""", n=40):
        lbl = r["tLabel"]
        if not lbl.startswith("Q"):
            items[qid(r["item"])].setdefault("stadtteile", set()).add(lbl)

    # Ortsteile, die per P131 in der Stadt liegen (ergänzt das oft lückenhafte P150)
    for r in batch("""SELECT ?item ?tLabel WHERE { VALUES ?item { %VALUES% }
        ?t wdt:P131 ?item . ?t wdt:P31 ?ty . ?ty rdfs:label ?tyl . FILTER(LANG(?tyl)="de")
        FILTER(REGEX(?tyl, "Ortsteil|Stadtteil|Stadtbezirk|Ortschaft|Bauerschaft|Stadtviertel|Wohnplatz|Dorf"))
        FILTER NOT EXISTS { ?t wdt:P576 ?e }
        SERVICE wikibase:label { bd:serviceParam wikibase:language "de". } }""", n=25):
        if not r["tLabel"].startswith("Q"):
            items[qid(r["item"])].setdefault("stadtteile", set()).add(r["tLabel"])

    for r in batch("""SELECT ?item ?wp WHERE { VALUES ?item { %VALUES% }
        ?wp schema:about ?item ; schema:isPartOf <https://de.wikipedia.org/> . }"""):
        items[qid(r["item"])]["wikipedia"] = r["wp"]

    out = []
    for it in items.values():
        typen = it.pop("typen", set())
        if not typen & STADT_STATUS or "Q116457956" in typen:
            continue
        it["status"] = ("kreisfreie Stadt" if "Q22865" in typen or it["ags"].endswith("000") else
                        "Große kreisangehörige Stadt" if "Q1548518" in typen else "Stadt")
        if not it.get("kreis") and it["status"] == "kreisfreie Stadt":
            it["kreis"] = ""
        it["bundesland"] = BUNDESLAND.get(it["ags"][:2], "")
        if not it.get("kreis") and it["ags"][:5] in KREIS_AGS:
            it["kreis"] = KREIS_AGS[it["ags"][:5]]
        if it["ags"][:3] in REGBEZ:
            it["regbez"] = REGBEZ[it["ags"][:3]]
        it["stadtteile"] = {t2 for t2 in (re.sub(r"^(Stadtbezirk|Stadtteil|Ortsteil|Ortschaft|Bezirk) ", "", t) for t in it.get("stadtteile", set()))
                            if t2 != it["name"] and not t2.startswith("Q")}
        for k in ("plz", "nachbarn", "stadtteile"):
            it[k] = sorted(it.get(k, set()))
        it["slug"] = slugify(it["name"])
        dy = (it["lat"] - lat0) * 111.2
        dx = (it["lon"] - lon0) * 111.2 * math.cos(math.radians(lat0))
        it["richtung"] = ["Norden", "Nordosten", "Osten", "Südosten", "Süden", "Südwesten", "Westen", "Nordwesten"][
            round((math.degrees(math.atan2(dx, dy)) % 360) / 45) % 8]
        it["dist"] = round(it["dist"], 1)
        out.append(it)

    # Doppelte Slugs (z. B. gleichnamige Städte) eindeutig machen
    seen = {}
    for it in sorted(out, key=lambda x: x["dist"]):
        if it["slug"] in seen:
            it["slug"] = f'{it["slug"]}-{slugify(it.get("kreis", "") or it["ags"])}'
        seen[it["slug"]] = it
    out.sort(key=lambda x: x["dist"])
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(out)} Städte mit Stadtrecht → {OUT.name}")


if __name__ == "__main__":
    main()
