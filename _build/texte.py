"""Content-Engine für Leistungs-, Kombi- und Stadtseiten.

Prinzip: Einzigartigkeit entsteht aus ECHTEN Stadtdaten (Wikidata: Einwohner, Fläche, Höhe, PLZ, Kreis,
Stadtteile, Nachbarorte, Entfernung von Herten) + großen Formulierungs-Pools, die je Seite deterministisch
(Seed = Leistung + Stadt) ausgewählt, kombiniert und in der Reihenfolge variiert werden.
Ehrlichkeitsregel: keine erfundenen Zahlen, Projekte oder Bewertungen. Allgemeine Aussagen sind als solche formuliert.
"""
import hashlib
import math
import random

import pools as P

# --------------------------------------------------------------------------- Hilfen

def rng(*keys):
    h = hashlib.md5("|".join(map(str, keys)).encode()).hexdigest()
    return random.Random(int(h[:16], 16))


def zahl(n, nk=0):
    s = f"{n:,.{nk}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def liste(items, und="und"):
    items = [i for i in items if i]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + f" {und} " + items[-1]


RICHTUNG_ADJ = {"Norden": "nördlich", "Nordosten": "nordöstlich", "Osten": "östlich", "Südosten": "südöstlich",
                "Süden": "südlich", "Südwesten": "südwestlich", "Westen": "westlich", "Nordwesten": "nordwestlich"}

RUHR = {"Bochum", "Bottrop", "Dortmund", "Duisburg", "Essen", "Gelsenkirchen", "Hagen", "Hamm", "Herne",
        "Mülheim an der Ruhr", "Oberhausen"}
REGION_KREIS = {
    "Kreis Recklinghausen": "Ruhrgebiet", "Kreis Unna": "Ruhrgebiet", "Ennepe-Ruhr-Kreis": "Ruhrgebiet",
    "Kreis Wesel": "Niederrhein", "Kreis Kleve": "Niederrhein", "Kreis Viersen": "Niederrhein",
    "Kreis Borken": "Münsterland", "Kreis Coesfeld": "Münsterland", "Kreis Steinfurt": "Münsterland",
    "Kreis Warendorf": "Münsterland", "Kreis Mettmann": "Bergisches Land", "Rheinisch-Bergischer Kreis": "Bergisches Land",
    "Oberbergischer Kreis": "Bergisches Land", "Märkischer Kreis": "Sauerland", "Hochsauerlandkreis": "Sauerland",
    "Kreis Olpe": "Sauerland", "Kreis Siegen-Wittgenstein": "Siegerland", "Kreis Soest": "Hellweg-Region",
    "Kreis Gütersloh": "Ostwestfalen", "Kreis Paderborn": "Ostwestfalen", "Rhein-Kreis Neuss": "Rheinland",
    "Rhein-Erft-Kreis": "Rheinland", "Rhein-Sieg-Kreis": "Rheinland", "Kreis Düren": "Rheinland",
    "Kreis Heinsberg": "Rheinland", "Städteregion Aachen": "Rheinland", "Kreis Euskirchen": "Rheinland",
    "Landkreis Grafschaft Bentheim": "Grafschaft Bentheim", "Landkreis Osnabrück": "Osnabrücker Land",
    "Landkreis Emsland": "Emsland", "Landkreis Altenkirchen (Westerwald)": "Westerwald",
}
REGION_KREISFREI = {"Münster": "Münsterland", "Krefeld": "Niederrhein", "Mönchengladbach": "Niederrhein",
                    "Düsseldorf": "Rheinland", "Köln": "Rheinland", "Leverkusen": "Rheinland", "Bonn": "Rheinland",
                    "Wuppertal": "Bergisches Land", "Solingen": "Bergisches Land", "Remscheid": "Bergisches Land",
                    "Bielefeld": "Ostwestfalen", "Osnabrück": "Osnabrücker Land"}


def region(s):
    if s["name"] in RUHR:
        return "Ruhrgebiet"
    if s["name"] in REGION_KREISFREI:
        return REGION_KREISFREI[s["name"]]
    return REGION_KREIS.get(s.get("kreis", ""), "Nordrhein-Westfalen" if s.get("bundesland") == "Nordrhein-Westfalen" else s.get("bundesland", ""))


# Allgemeine, wahre Merkmale der Regionen (ohne Zahlen) – je 3 Formulierungen
REGION_TEXT = {
    "Ruhrgebiet": [
        "Typisch für das Ruhrgebiet sind dicht bebaute Wohnviertel, Mehrfamilienhäuser aus den Nachkriegsjahrzehnten und frühere Zechensiedlungen mit schmalen Treppenhäusern.",
        "Wer im Ruhrgebiet wohnt, kennt das: Viele Häuser haben drei, vier Etagen ohne Aufzug, die Straßen sind eng zugeparkt – genau dafür braucht es eingespielte Abläufe.",
        "Zwischen ehemaligen Zechensiedlungen, Altbauvierteln und neuen Wohngebieten ist das Ruhrgebiet baulich bunt gemischt – jede Adresse bringt eigene Anforderungen mit.",
    ],
    "Münsterland": [
        "Das Münsterland ist geprägt von Einfamilienhäusern, Höfen und weitläufigen Bauerschaften – oft mit großzügigen Kellern, Dachböden und Scheunen.",
        "Im Münsterland liegen viele Adressen außerhalb der Ortskerne, zwischen Feldern und Bauerschaften; Zufahrt und Ladeweg planen wir deshalb vorab.",
        "Ob Hofstelle, Reihenhaus oder Wohnung im Ortskern: Im Münsterland sind die Wege oft länger, die Häuser dafür häufig geräumiger.",
    ],
    "Niederrhein": [
        "Am Niederrhein prägen Klinkerhäuser, Reihenhaussiedlungen und ländliche Ortsteile das Bild – mit oft gut erreichbaren Zufahrten.",
        "Der Niederrhein verbindet kleinstädtische Ortskerne mit weiten, flachen Landschaften – ideal für zügiges Be- und Entladen direkt vor der Tür.",
        "Zwischen Rheinauen und Ortskernen finden sich am Niederrhein viele ältere Einfamilienhäuser mit Kellern und Dachböden, die über Jahrzehnte gefüllt wurden.",
    ],
    "Rheinland": [
        "Im Rheinland treffen Gründerzeit-Altbauten mit hohen Decken auf moderne Wohnanlagen – und Parkraum ist in den Innenstädten oft knapp.",
        "Die rheinischen Städte sind dicht bebaut; Altbauwohnungen in oberen Etagen und enge Straßen erfordern eine sorgfältige Planung von Ladezone und Tragewegen.",
        "Zwischen Altbau-Vierteln, Neubaugebieten und Vororten ist das Rheinland vielfältig – entsprechend unterschiedlich sind die Bedingungen vor Ort.",
    ],
    "Bergisches Land": [
        "Das Bergische Land ist hügelig: Hanglagen, Außentreppen und steile Zufahrten gehören hier vielerorts zum Alltag.",
        "Schiefer, Fachwerk und viele Höhenmeter – im Bergischen Land liegen zahlreiche Häuser am Hang, was Tragewege und Fahrzeugstellplatz beeinflusst.",
        "Wer im Bergischen Land wohnt, hat oft Treppen vor und im Haus; wir planen dafür genug Hände und das passende Equipment ein.",
    ],
    "Sauerland": [
        "Im Sauerland liegen viele Häuser in Hanglage, Zufahrten können steil und schmal sein – das berücksichtigen wir bei Fahrzeug und Personal.",
        "Bergig, waldreich und mit verstreuten Ortsteilen: Im Sauerland lohnt es sich, Anfahrt und Tragewege vorab genau abzustimmen.",
        "Zwischen Tälern und Höhenzügen sind im Sauerland die Wege zwischen den Ortsteilen oft lang – eine gute Planung spart hier viel Zeit.",
    ],
    "Siegerland": [
        "Das Siegerland ist hügelig und waldreich, viele Häuser stehen am Hang – Tragewege und Stellplätze planen wir deshalb besonders sorgfältig.",
        "Hanglagen, Fachwerk und enge Ortsdurchfahrten prägen das Siegerland; mit der richtigen Vorbereitung läuft der Einsatz trotzdem reibungslos.",
        "Im Siegerland sind die Ortsteile oft über Täler verteilt – wir kalkulieren die Wege realistisch ein.",
    ],
    "Hellweg-Region": [
        "Die Hellweg-Region zwischen Ruhrgebiet und Sauerland verbindet historische Ortskerne mit ländlichen Ortsteilen und Einfamilienhaus-Gebieten.",
        "Entlang des Hellwegs finden sich viele ältere Höfe und Häuser mit großen Kellern und Dachböden – typische Einsatzorte für uns.",
        "Zwischen Börde und Haarstrang liegen die Orte der Hellweg-Region oft weit auseinander; die Anfahrt planen wir entsprechend.",
    ],
    "Ostwestfalen": [
        "Ostwestfalen ist geprägt von mittelgroßen Städten, Einfamilienhaus-Siedlungen und ländlichen Ortsteilen mit großzügigen Grundstücken.",
        "In Ostwestfalen sind viele Häuser geräumig, mit Keller, Dachboden und Garage – entsprechend viel kommt bei Umzug oder Räumung zusammen.",
        "Zwischen Teutoburger Wald und Ems liegen in Ostwestfalen viele Ortsteile verstreut; wir planen die Anfahrt mit Puffer.",
    ],
    "Osnabrücker Land": [
        "Das Osnabrücker Land verbindet städtische Wohnlagen mit Dörfern am Teutoburger Wald – teils mit Hanglagen und längeren Wegen.",
        "Im Osnabrücker Land stehen viele Einfamilienhäuser mit Keller und Dachboden; die Anfahrt aus dem Ruhrgebiet planen wir fest ein.",
        "Zwischen Wiehengebirge und Teutoburger Wald sind die Gegebenheiten im Osnabrücker Land sehr unterschiedlich – wir schauen uns alles vorher an.",
    ],
    "Grafschaft Bentheim": [
        "Die Grafschaft Bentheim nahe der niederländischen Grenze ist ländlich geprägt, mit weitläufigen Grundstücken und gut erreichbaren Häusern.",
        "In der Grafschaft Bentheim liegen viele Höfe und Einfamilienhäuser außerhalb der Ortskerne – mit viel Platz für das Fahrzeug.",
        "Ländlich, flach und weit: In der Grafschaft Bentheim planen wir vor allem die Anfahrt sorgfältig ein.",
    ],
    "Westerwald": [
        "Der Westerwald ist hügelig und ländlich, mit Ortsteilen in Hanglage und oft schmalen Zufahrten.",
        "Im Westerwald stehen viele Häuser am Hang; Tragewege und Fahrzeugstellplatz klären wir deshalb vorab.",
        "Zwischen Wäldern und Höhenzügen sind die Wege im Westerwald länger – wir planen sie realistisch ein.",
    ],
}
REGION_TEXT_DEFAULT = [
    "Jede Stadt hat ihre eigenen Gegebenheiten – von der Bebauung bis zur Parksituation. Wir klären das vorab bei der Besichtigung.",
    "Ob Altbau, Reihenhaus oder Neubau: Wir passen Personal und Fahrzeug an die Gegebenheiten vor Ort an.",
    "Wir schauen uns jede Adresse vorher an, damit am Einsatztag nichts dem Zufall überlassen bleibt.",
]


def groesse(einw):
    if einw >= 500_000:
        return "Millionen- und Großstadt" if einw >= 1_000_000 else "große Großstadt"
    if einw >= 100_000:
        return "Großstadt"
    if einw >= 50_000:
        return "große Mittelstadt"
    if einw >= 20_000:
        return "Mittelstadt"
    return "Kleinstadt"


def fakten(s):
    """Echte Kennzahlen + abgeleitete Werte einer Stadt."""
    einw = s.get("einwohner") or 0
    fl = s.get("flaeche_km2") or 0
    f = {
        "stadt": s["name"],
        "einw": zahl(einw) if einw else "",
        "einw_n": einw,
        "stand": (s.get("pop_datum") or "")[:4],
        "flaeche": zahl(fl, 1) if fl else "",
        "dichte": zahl(einw / fl) if einw and fl else "",
        "dichte_n": einw / fl if einw and fl else 0,
        "hoehe": zahl(s["hoehe_m"]) if s.get("hoehe_m") else "",
        "hoehe_n": s.get("hoehe_m") or 0,
        "flaeche_n": fl,
        "plz": liste(s.get("plz", [])[:3]) + (" u. a." if len(s.get("plz", [])) > 3 else ""),
        "plz1": (s.get("plz") or [""])[0].split("–")[0],
        "kreis": s.get("kreis") or "",
        "regbez": s.get("regbez") or "",
        "bl": s.get("bundesland") or "",
        "dist_n": s["dist"],
        "dist": f"rund {zahl(round(s['dist']))} km" if s["dist"] >= 3 else "",
        "richtung": RICHTUNG_ADJ.get(s.get("richtung", ""), ""),
        "region": region(s),
        "groesse": groesse(einw),
        "status": s.get("status", "Stadt"),
        "nachbarn": s.get("nachbarn", []),
        "teile": s.get("stadtteile", []),
        "heimat": s["dist"] < 3,
    }
    f["kreis_txt"] = f"im {f['kreis']}" if f["kreis"].startswith("Kreis") or f["kreis"].startswith("Landkreis") or f["kreis"].startswith("Hochsauerland") or f["kreis"].endswith("Kreis") else (f"in der {f['kreis']}" if f["kreis"].startswith("Städteregion") else (f"im Kreis {f['kreis']}" if f["kreis"] else ""))
    if f["kreis"].endswith("-Kreis") or f["kreis"].endswith("kreis"):
        f["kreis_txt"] = f"im {f['kreis']}"
    return f


# --------------------------------------------------------------------------- Leistungen (Grammatik + Pools)

L = {
    "umzug": dict(fam="umzug", kw="Umzug", akk="Ihren Umzug", dat="Ihrem Umzug", gen="Ihres Umzugs", art="der Umzug",
                  objekt="Möbel, Kartons und Hausrat", kunden="Familien, Paare, Singles und Studierende",
                  ziel="die neue Wohnung", ergebnis="ein Umzug ohne Chaos"),
    "firmenumzug": dict(fam="umzug", kw="Firmenumzug", akk="Ihren Firmenumzug", dat="Ihrem Firmenumzug", gen="Ihres Firmenumzugs",
                        art="der Firmenumzug", objekt="Büromöbel, Akten, IT und Archiv", kunden="Büros, Praxen, Kanzleien und Ladengeschäfte",
                        ziel="die neuen Geschäftsräume", ergebnis="ein Betrieb, der schnell wieder läuft"),
    "seniorenumzug": dict(fam="umzug", kw="Seniorenumzug", akk="Ihren Seniorenumzug", dat="Ihrem Seniorenumzug", gen="Ihres Seniorenumzugs",
                          art="der Seniorenumzug", objekt="liebgewonnene Möbel, Erinnerungsstücke und Hausrat",
                          kunden="Seniorinnen, Senioren und ihre Angehörigen", ziel="die neue, oft kleinere Wohnung oder das Seniorenheim",
                          ergebnis="ein Neuanfang ohne Stress"),
    "entruempelung": dict(fam="raeumung", kw="Entrümpelung", akk="Ihre Entrümpelung", dat="Ihrer Entrümpelung", gen="Ihrer Entrümpelung",
                          art="die Entrümpelung", objekt="Sperrmüll, Altmöbel, Elektrogeräte und Hausrat",
                          kunden="Mieter, Eigentümer, Vermieter und Erben", ziel="freie, besenreine Räume", ergebnis="endlich wieder Platz"),
    "haushaltsaufloesung": dict(fam="raeumung", kw="Haushaltsauflösung", akk="Ihre Haushaltsauflösung", dat="Ihrer Haushaltsauflösung",
                                gen="Ihrer Haushaltsauflösung", art="die Haushaltsauflösung", objekt="einen kompletten Haushalt samt Möbeln, Hausrat und Erinnerungsstücken",
                                kunden="Erben, Angehörige, Betreuer und Vermieter", ziel="eine übergabefertige Immobilie", ergebnis="ein geregelter Abschluss"),
    "wohnungsaufloesung": dict(fam="raeumung", kw="Wohnungsauflösung", akk="Ihre Wohnungsauflösung", dat="Ihrer Wohnungsauflösung",
                               gen="Ihrer Wohnungsauflösung", art="die Wohnungsauflösung", objekt="Möbel, Einbauten, Hausrat und Bodenbeläge",
                               kunden="Mieter, Vermieter, Hausverwaltungen und Erben", ziel="eine leere, übergabefertige Wohnung", ergebnis="eine Übergabe ohne Beanstandung"),
    "kellerentruempelung": dict(fam="raeumung", kw="Kellerentrümpelung", akk="Ihre Kellerentrümpelung", dat="Ihrer Kellerentrümpelung",
                                gen="Ihrer Kellerentrümpelung", art="die Kellerentrümpelung", objekt="Keller-, Dachboden- und Garageninhalte",
                                kunden="Hauseigentümer, Mieter und Hausverwaltungen", ziel="einen freien, nutzbaren Keller", ergebnis="wieder nutzbarer Stauraum"),
    "messie-wohnung-entruempeln": dict(fam="raeumung", kw="Messie-Wohnung entrümpeln", kw_kurz="Messie-Entrümpelung",
                                       akk="die Entrümpelung Ihrer Messie-Wohnung", dat="der Entrümpelung einer Messie-Wohnung",
                                       gen="der Messie-Entrümpelung", art="die Messie-Entrümpelung", objekt="stark vermüllte oder zugestellte Wohnräume",
                                       kunden="Betroffene, Angehörige, Betreuer und Vermieter", ziel="eine wieder bewohnbare Wohnung", ergebnis="ein diskreter Neustart"),
    "moebelmontage": dict(fam="montage", kw="Möbelmontage", akk="Ihre Möbelmontage", dat="Ihrer Möbelmontage", gen="Ihrer Möbelmontage",
                          art="die Möbelmontage", objekt="Schränke, Betten, Regale und Kommoden", kunden="Privathaushalte, Büros und Vermieter",
                          ziel="fertig aufgebaute, stabile Möbel", ergebnis="Möbel, die passen und halten"),
    "kuechenmontage": dict(fam="montage", kw="Küchenmontage", akk="Ihre Küchenmontage", dat="Ihrer Küchenmontage", gen="Ihrer Küchenmontage",
                           art="die Küchenmontage", objekt="Küchenzeilen, Hängeschränke, Arbeitsplatten und Blenden",
                           kunden="Eigentümer, Mieter und Vermieter", ziel="eine exakt ausgerichtete, fertige Küche", ergebnis="eine Küche, die sofort nutzbar ist"),
}
for _s, _d in L.items():
    _d.setdefault("kw_kurz", _d["kw"])
    _d["slug"] = _s


# Spezifische Inhalte je Leistung (Kernnutzen, Umfang, eigene FAQs)
SPEZ = {
    "umzug": {
        "hook": ["Ein Umzug ist mehr als Kisten schleppen: Es geht um Ihre Möbel, Ihre Zeit und Ihre Nerven.",
                 "Der Umzugstag soll ein guter Tag werden – nicht einer, an den man sich mit Rückenschmerzen erinnert.",
                 "Neue Wohnung, neuer Abschnitt: Damit der Start gelingt, übernehmen wir die schwere Arbeit."],
        "umfang": ["Möbelabbau in der alten und Aufbau in der neuen Wohnung", "Verpacken zerbrechlicher Gegenstände auf Wunsch",
                   "Sicherer Transport im eigenen Transporter", "Schutz von Möbeln mit Decken und Folie",
                   "Tragen über Treppenhäuser, auch ohne Aufzug", "Mitnahme und Entsorgung aussortierter Möbel",
                   "Besenreine Übergabe der alten Wohnung auf Wunsch", "Beiladungen und Teilumzüge"],
        "faq": [("Wie früh sollte ich einen Umzug in {stadt} anfragen?",
                 ["Je früher, desto besser – besonders zum Monatsende und in den Sommermonaten sind Termine gefragt. Eine kurze Anfrage genügt, den genauen Ablauf klären wir bei der kostenlosen Besichtigung.",
                  "Am besten, sobald Ihr Umzugsdatum feststeht. Monatsenden sind beliebt; mit etwas Vorlauf können wir Ihren Wunschtermin in {stadt} am ehesten einplanen."]),
                ("Bauen Sie Möbel beim Umzug ab und wieder auf?",
                 ["Ja. Schränke, Betten und Regale bauen wir in der alten Wohnung ab und in {ziel} wieder auf – das ist für uns Standard.",
                  "Ja, Ab- und Aufbau gehören bei uns dazu. Sie sagen uns, was mitkommt – wir kümmern uns um Schrauben, Beschläge und das Ausrichten."]),
                ("Kann ich beim Umzug auch alte Möbel entsorgen lassen?",
                 ["Ja. Was nicht mit in die neue Wohnung soll, nehmen wir mit und entsorgen es fachgerecht – so sparen Sie sich die Fahrt zum Wertstoffhof.",
                  "Gerne. Umzug und Entrümpelung aus einer Hand sind unsere Stärke: Aussortiertes nehmen wir direkt mit."])],
        "nutzen": [("Ein Team für alles", "Tragen, Transport, Abbau und Aufbau – ohne dass Sie mehrere Firmen koordinieren müssen."),
                   ("Schonender Transport", "Decken, Folie und sichere Ladungssicherung schützen Ihre Möbel auf dem Weg.")],
    },
    "firmenumzug": {
        "hook": ["Jeder Tag, an dem Ihr Betrieb stillsteht, kostet Geld – deshalb planen wir Firmenumzüge mit klarem Zeitplan.",
                 "Ein Büroumzug muss vor allem eines sein: schnell erledigt, damit Ihr Team weiterarbeiten kann.",
                 "Akten, Arbeitsplätze, Technik: Beim Firmenumzug zählt, dass am nächsten Arbeitstag alles an seinem Platz steht."],
        "umfang": ["Abbau und Aufbau von Schreibtischen, Schränken und Regalen", "Beschriftungssystem für Kartons und Arbeitsplätze",
                   "Transport von Akten und Archivkartons", "Umzug außerhalb der Geschäftszeiten nach Absprache",
                   "Entsorgung alter Büromöbel", "Teilumzüge einzelner Abteilungen", "Möbelschutz in Treppenhaus und Aufzug",
                   "Besenreine Übergabe der alten Geschäftsräume"],
        "faq": [("Ist ein Firmenumzug in {stadt} auch am Wochenende möglich?",
                 ["Samstags sind wir regulär im Einsatz (Mo–Sa 8–18 Uhr). So kann Ihr Büro in {stadt} am Montag wieder öffnen.",
                  "Ja, auch samstags. Viele Betriebe nutzen das, um den Umzug ohne Ausfall eines Arbeitstags zu erledigen."]),
                ("Wie organisieren Sie Akten und Arbeitsplätze beim Büroumzug?",
                 ["Mit einem einfachen Beschriftungssystem: Jeder Karton und jedes Möbelstück bekommt sein Ziel im neuen Büro – so steht alles dort, wo es hingehört.",
                  "Wir stimmen vorab einen Raumplan ab und kennzeichnen Kartons und Möbel danach. Beim Aufbau stellen wir alles direkt an den richtigen Platz."]),
                ("Übernehmen Sie auch kleinere Büros und Praxen?",
                 ["Gerade für kleine und mittlere Betriebe sind wir der richtige Partner – vom Einzelbüro bis zur Praxis mit mehreren Räumen.",
                  "Ja. Ob Ein-Raum-Büro, Kanzlei oder Ladengeschäft – wir planen Personal und Fahrzeug passend zur Größe."])],
        "nutzen": [("Kurze Ausfallzeit", "Klare Planung und eingespielte Abläufe halten den Stillstand Ihres Betriebs so kurz wie möglich."),
                   ("Ordnung von Anfang an", "Beschriftete Kartons und ein Raumplan sorgen dafür, dass im neuen Büro alles sofort auffindbar ist.")],
    },
    "seniorenumzug": {
        "hook": ["Ein Umzug im Alter ist oft ein emotionaler Schritt – wir begleiten ihn mit Geduld und Respekt.",
                 "Wenn die Wohnung zu groß oder die Treppe zu steil wird, ist ein Umzug eine echte Erleichterung – wir machen ihn so leicht wie möglich.",
                 "Beim Seniorenumzug zählt Ruhe: ein fester Ansprechpartner, klare Absprachen und Zeit für Ihre Fragen."],
        "umfang": ["Gemeinsames Aussortieren: Was kommt mit, was bleibt?", "Abbau und Aufbau der Möbel in der neuen Wohnung",
                   "Verpacken von Geschirr, Büchern und Erinnerungsstücken", "Transport ins Seniorenheim oder betreute Wohnen",
                   "Auflösung bzw. Räumung der bisherigen Wohnung", "Fachgerechte Entsorgung nicht benötigter Möbel",
                   "Abstimmung mit Angehörigen, auch wenn diese weiter weg wohnen", "Besenreine Übergabe an den Vermieter"],
        "faq": [("Können Angehörige den Seniorenumzug aus der Ferne organisieren?",
                 ["Ja. Wir stimmen uns telefonisch oder per WhatsApp mit Ihnen ab und sind vor Ort der feste Ansprechpartner für Ihre Eltern in {stadt}.",
                  "Gerne. Viele Angehörige wohnen nicht in {stadt} – wir halten Sie auf dem Laufenden und klären alles Wichtige direkt mit Ihnen."]),
                ("Was passiert mit Möbeln, die nicht in die neue Wohnung passen?",
                 ["Die kleinere Wohnung bietet oft nicht für alles Platz. Was bleibt, räumen wir aus und entsorgen es fachgerecht – auf Wunsch in einem Termin mit dem Umzug.",
                  "Wir kombinieren Umzug und Räumung: Mitgenommen wird, was Sie auswählen; den Rest übernehmen wir bei der Auflösung der alten Wohnung."]),
                ("Wie viel Zeit nehmen Sie sich bei einem Seniorenumzug?",
                 ["So viel wie nötig. Wir planen bewusst ruhiger und erklären jeden Schritt – niemand soll sich gedrängt fühlen.",
                  "Wir arbeiten zügig, aber ohne Hektik. Die Besichtigung nutzen wir, um alle Wünsche in Ruhe aufzunehmen."])],
        "nutzen": [("Mit Geduld und Respekt", "Wir nehmen uns Zeit, hören zu und gehen sorgsam mit Erinnerungsstücken um."),
                   ("Umzug + Räumung kombiniert", "Neue Wohnung einrichten und alte Wohnung auflösen – abgestimmt aus einer Hand.")],
    },
    "entruempelung": {
        "hook": ["Volle Räume belasten – eine Entrümpelung schafft Platz und Klarheit.",
                 "Ob Abstellkammer, ganze Etage oder komplettes Haus: Wir räumen, was raus muss.",
                 "Irgendwann ist der Punkt erreicht, an dem es einfach weg muss – dann sind wir da."],
        "umfang": ["Räumung von Wohnung, Haus, Keller, Dachboden und Garage", "Abbau von Möbeln und Einbauten",
                   "Trennung nach Holz, Metall, Elektro und Restmüll", "Fachgerechte Entsorgung über zugelassene Annahmestellen",
                   "Tragen über Treppen und enge Flure", "Besenreine Übergabe", "Kurzfristige Termine nach Absprache",
                   "Entrümpelung von Gartenhaus und Schuppen"],
        "faq": [("Was kostet eine Entrümpelung in {stadt}?",
                 ["Das hängt von Menge, Etage, Tragewegen und Art des Materials ab. Nach der kostenlosen Besichtigung erhalten Sie ein transparentes, verbindliches Angebot.",
                  "Pauschale Preise wären unseriös – zu unterschiedlich sind die Fälle. Deshalb besichtigen wir kostenlos und nennen Ihnen danach einen klaren Preis."]),
                ("Wie schnell kann eine Entrümpelung in {stadt} stattfinden?",
                 ["Oft schon wenige Tage nach der Besichtigung – je nach Auslastung. Sagen Sie uns, bis wann die Räume frei sein müssen.",
                  "Wenn es eilt, sagen Sie es uns direkt bei der Anfrage. Wir prüfen den frühesten möglichen Termin in {stadt}."]),
                ("Muss ich bei der Entrümpelung anwesend sein?",
                 ["Nicht zwingend. Nach der Besichtigung und klaren Absprachen genügt oft die Schlüsselübergabe – wir melden uns, sobald alles erledigt ist.",
                  "Bei der Besichtigung ja, am Einsatztag nicht unbedingt. Viele Kunden übergeben uns den Schlüssel und erhalten die Räume besenrein zurück."])],
        "nutzen": [("Alles raus in einem Termin", "Wir bringen genug Personal und Ladevolumen mit, damit die Räume zügig frei sind."),
                   ("Umweltgerecht getrennt", "Holz, Metall, Elektro und Restmüll werden getrennt und fachgerecht entsorgt.")],
    },
    "haushaltsaufloesung": {
        "hook": ["Eine Haushaltsauflösung kommt selten geplant – oft nach einem Todesfall oder einem Umzug ins Heim. Wir nehmen Ihnen die Arbeit ab.",
                 "Wenn ein ganzes Leben in einer Wohnung steckt, braucht es Fingerspitzengefühl – und ein Team, das anpackt.",
                 "Erben, Angehörige und Vermieter stehen bei einer Haushaltsauflösung vor viel Arbeit. Wir erledigen sie diskret und zuverlässig."],
        "umfang": ["Komplette Räumung aller Zimmer, Keller und Dachboden", "Sichtung auf Dokumente, Fotos und Wertsachen",
                   "Separate Ablage von Dingen, die Sie behalten möchten", "Prüfung, ob Verwertbares angerechnet werden kann",
                   "Abbau von Möbeln und Einbauten", "Fachgerechte Entsorgung", "Besenreine Übergabe an Vermieter oder Käufer",
                   "Abstimmung mit Hausverwaltung oder Betreuer"],
        "faq": [("Was passiert mit Dokumenten und persönlichen Gegenständen?",
                 ["Gefundene Unterlagen, Fotos und Wertsachen legen wir separat beiseite und übergeben sie Ihnen – nichts Wichtiges landet im Container.",
                  "Wir sichten beim Räumen mit offenen Augen. Dokumente und Erinnerungsstücke sammeln wir und übergeben sie an Sie."]),
                ("Kann verwertbares Inventar mit den Kosten verrechnet werden?",
                 ["Wenn sich gut erhaltene Möbel oder Gegenstände verwerten lassen, prüfen wir eine Anrechnung – ehrlich und nachvollziehbar im Angebot.",
                  "Teilweise ja. Bei der Besichtigung schauen wir, was noch einen Wert hat, und berücksichtigen das transparent."]),
                ("Wir wohnen nicht in {stadt} – geht die Haushaltsauflösung trotzdem?",
                 ["Ja. Viele Erben leben weiter weg. Nach Besichtigung und Schlüsselübergabe erledigen wir alles und melden uns mit Fotos zurück.",
                  "Selbstverständlich. Wir stimmen uns telefonisch ab und übergeben die Wohnung in {stadt} besenrein an Sie oder den Vermieter."])],
        "nutzen": [("Diskret und respektvoll", "Wir arbeiten ruhig, sorgfältig und mit Respekt vor dem, was in der Wohnung steckt."),
                   ("Wichtiges wird gesichert", "Dokumente, Fotos und Wertsachen legen wir für Sie beiseite.")],
    },
    "wohnungsaufloesung": {
        "hook": ["Die Wohnung muss bis zum Stichtag leer sein? Dann brauchen Sie ein Team, das liefert.",
                 "Mietende, Verkauf oder Erbfall: Eine Wohnungsauflösung hat fast immer eine Frist – wir halten sie ein.",
                 "Leere Räume, besenrein, pünktlich zur Übergabe – das ist das Ziel jeder Wohnungsauflösung."],
        "umfang": ["Räumung aller Zimmer inklusive Keller- und Dachbodenabteil", "Demontage von Küche, Einbauschränken und Lampen",
                   "Entfernen von Teppichen und Bodenbelägen auf Wunsch", "Entsorgung über zugelassene Annahmestellen",
                   "Tragen aus oberen Etagen ohne Aufzug", "Besenreine Übergabe", "Termin passend zur Wohnungsübergabe",
                   "Abstimmung mit Vermieter oder Hausverwaltung"],
        "faq": [("Entfernen Sie bei der Wohnungsauflösung auch Teppiche und Einbauten?",
                 ["Ja, auf Wunsch. Teppichböden, Einbauschränke, Küchen und Lampen demontieren wir, damit die Wohnung übergabefertig ist.",
                  "Gerne. Was laut Mietvertrag raus muss – Einbauten, Bodenbeläge, Lampen –, entfernen wir mit."]),
                ("Schaffen Sie die Wohnungsauflösung bis zu einem festen Übergabetermin?",
                 ["Ja, darauf planen wir hin. Nennen Sie uns den Übergabetermin in {stadt}, wir legen die Räumung so, dass genug Puffer bleibt.",
                  "Der Stichtag ist für uns die wichtigste Größe. Wir planen den Einsatz rückwärts vom Übergabetermin."]),
                ("Wie hinterlassen Sie die Wohnung?",
                 ["Besenrein: leer, gefegt und ohne Rückstände – so, wie es Vermieter in der Regel erwarten.",
                  "Leer und besenrein. Auf Wunsch machen Sie mit uns einen kurzen Abschlussrundgang."])],
        "nutzen": [("Fristgerecht", "Wir planen rückwärts vom Übergabetermin – damit kein zusätzlicher Monat Miete fällig wird."),
                   ("Übergabefertig", "Leer, demontiert, besenrein – bereit für Vermieter, Käufer oder Nachmieter.")],
    },
    "kellerentruempelung": {
        "hook": ["Der Keller ist voll, der Dachboden auch – und die Garage dient längst nicht mehr dem Auto?",
                 "Was jahrelang im Keller verschwunden ist, holen wir in wenigen Stunden wieder raus.",
                 "Kellerräume sind eng, dunkel und oft nur über schmale Treppen erreichbar – genau dafür sind wir gerüstet."],
        "umfang": ["Entrümpelung von Kellerräumen und Kellerabteilen", "Räumung von Dachboden und Spitzboden", "Garagen- und Schuppenräumung",
                   "Tragen über enge, steile Kellertreppen", "Trennung von Holz, Metall, Elektro und Restmüll", "Entsorgung von Altmöbeln und Sperrmüll",
                   "Besenreine Übergabe", "Räumung von Gemeinschaftskellern nach Absprache mit der Hausverwaltung"],
        "faq": [("Entrümpeln Sie auch Dachboden und Garage?",
                 ["Ja. Keller, Dachboden, Spitzboden, Garage oder Gartenhaus – wir räumen alle Nebenräume, auf Wunsch in einem Termin.",
                  "Selbstverständlich. Oft lohnt es sich, Keller, Dachboden und Garage zusammen zu räumen – das spart Anfahrt und Zeit."]),
                ("Was ist, wenn der Keller feucht oder schwer zugänglich ist?",
                 ["Das klären wir bei der Besichtigung. Feuchte, enge Treppen oder niedrige Decken planen wir bei Personal und Zeit ein.",
                  "Kein Problem – wir sehen uns die Situation vorher an und bringen passende Schutzkleidung und Tragehilfen mit."]),
                ("Wie lange dauert eine Kellerentrümpelung in {stadt}?",
                 ["Ein normaler Kellerraum ist oft in wenigen Stunden erledigt. Den genauen Zeitbedarf nennen wir Ihnen nach der Besichtigung.",
                  "Das hängt von Menge und Zugang ab. Nach der kostenlosen Besichtigung wissen Sie genau, womit Sie rechnen können."])],
        "nutzen": [("Schnell erledigt", "Kellerräume sind meist in wenigen Stunden frei – Sie müssen nichts selbst die Treppe hochtragen."),
                   ("Stauraum zurück", "Danach ist Ihr Keller wieder das, wofür er gedacht ist: nutzbarer Platz.")],
    },
    "messie-wohnung-entruempeln": {
        "hook": ["Wenn eine Wohnung über die Jahre zugewachsen ist, braucht es keine Vorwürfe, sondern Hilfe – diskret und ohne Urteil.",
                 "Eine Messie-Wohnung zu räumen, kostet Überwindung. Wir machen es Ihnen leicht: ruhig, diskret und gründlich.",
                 "Ob für Betroffene, Angehörige oder Vermieter: Wir räumen stark zugestellte Wohnungen zuverlässig und verschwiegen."],
        "umfang": ["Diskrete Anfahrt und unauffälliges Arbeiten", "Räumung stark zugestellter oder vermüllter Räume",
                   "Sortieren nach Wichtigem, Behaltenswertem und Entsorgung", "Schutzkleidung und Handschuhe für das Team",
                   "Fachgerechte Entsorgung aller Abfälle", "Abbau von Möbeln und Einbauten", "Besenreine Übergabe",
                   "Abstimmung mit Angehörigen, Betreuern oder Vermietern"],
        "faq": [("Bleibt die Entrümpelung einer Messie-Wohnung in {stadt} diskret?",
                 ["Ja. Wir arbeiten zurückhaltend, ohne auffällige Beschriftung am Treppenhaus und sprechen mit niemandem über den Auftrag.",
                  "Diskretion ist bei uns selbstverständlich. Nachbarn erfahren von uns nichts – wir erledigen unsere Arbeit leise und zügig."]),
                ("Muss die betroffene Person beim Räumen dabei sein?",
                 ["Das entscheiden Sie. Manche möchten mitsortieren, andere lieber nicht dabei sein – beides ist in Ordnung.",
                  "Nicht zwingend. Wichtig ist, dass vorher klar ist, was behalten werden soll. Das besprechen wir in Ruhe bei der Besichtigung."]),
                ("Räumen Sie auch sehr stark vermüllte Wohnungen?",
                 ["Ja. Wir schauen uns die Situation vorher an und planen Schutzkleidung, Personal und Entsorgung entsprechend.",
                  "Ja. Bei der Besichtigung klären wir den Umfang ehrlich – auch, ob zusätzlich eine Fachreinigung sinnvoll ist."])],
        "nutzen": [("Ohne Urteil", "Wir helfen, statt zu bewerten – mit Respekt vor der Person und ihrer Situation."),
                   ("Diskret", "Unauffälliges Arbeiten und absolute Verschwiegenheit gegenüber Dritten.")],
    },
    "moebelmontage": {
        "hook": ["Die Bauanleitung hat 40 Seiten, die Schrauben sind gemischt und der Schrank wackelt trotzdem? Das muss nicht sein.",
                 "Neue Möbel sollen Freude machen – nicht ein ganzes Wochenende mit Inbusschlüssel kosten.",
                 "Ob neu gekauft oder beim Umzug zerlegt: Wir bauen Ihre Möbel sauber, stabil und gerade auf."],
        "umfang": ["Aufbau von Kleiderschränken, auch Schwebetüren- und Eckschränke", "Montage von Betten, Boxspring- und Etagenbetten",
                   "Aufbau von Regalen, Kommoden und Sideboards", "Wandbefestigung von Hängeschränken und Regalen",
                   "Abbau und Wiederaufbau beim Umzug", "Ausrichten von Türen und Schubladen", "Mitnahme von Verpackungsmaterial",
                   "Montage von Büromöbeln"],
        "faq": [("Bauen Sie auch Möbel aus dem Möbelhaus oder Online-Shop auf?",
                 ["Ja. Ob Möbelhaus, Möbel-Discounter oder Online-Bestellung – wir bauen die Möbel nach Herstellerangaben fachgerecht auf.",
                  "Gerne. Die meisten Systeme kennen wir; die Anleitung nehmen wir trotzdem mit, damit jedes Detail stimmt."]),
                ("Befestigen Sie Schränke und Regale auch an der Wand?",
                 ["Ja, wo es nötig und möglich ist. Hohe Schränke und Regale sichern wir gegen Kippen – das ist besonders mit Kindern wichtig.",
                  "Ja. Kippsicherung und Wandmontage gehören bei hohen Möbeln dazu; wir prüfen vorher die Wandbeschaffenheit."]),
                ("Nehmen Sie das Verpackungsmaterial mit?",
                 ["Auf Wunsch ja. Kartons, Styropor und Folien nehmen wir mit, damit Sie nicht mit Bergen von Verpackung zurückbleiben.",
                  "Gerne – nach der Montage ist der Raum aufgeräumt und die Verpackung ist weg."])],
        "nutzen": [("Gerade und stabil", "Exakt ausgerichtete Türen, feste Verbindungen, sichere Wandbefestigung."),
                   ("Zeit gespart", "Was Sie ein Wochenende kostet, erledigen wir in wenigen Stunden.")],
    },
    "kuechenmontage": {
        "hook": ["Eine Küche ist das teuerste Möbelstück im Haushalt – sie verdient eine Montage, bei der jedes Maß stimmt.",
                 "Beim Umzug muss die Küche mit? Dann bauen wir sie ab, transportieren sie und bauen sie passgenau wieder auf.",
                 "Hängeschränke im Lot, Fronten in einer Flucht, Arbeitsplatte sauber angepasst: So sieht eine gute Küchenmontage aus."],
        "umfang": ["Abbau der Küche in der alten Wohnung", "Transport aller Schränke, Fronten und Geräte", "Aufbau und Ausrichten der Unterschränke",
                   "Montage und Lotrechtes Ausrichten der Hängeschränke", "Anpassen und Montieren der Arbeitsplatte", "Einbau von Blenden und Sockelleisten",
                   "Einstellen von Türen und Schubladen", "Mitnahme von Verpackungsmaterial"],
        "faq": [("Bauen Sie die Küche beim Umzug ab und wieder auf?",
                 ["Ja. Abbau, Transport und Wiederaufbau aus einer Hand – so passt am Ende alles wieder zusammen.",
                  "Genau das ist eine unserer Stärken: Wir kennen jede Schraube, weil wir die Küche selbst abgebaut haben."]),
                ("Passen Sie die Arbeitsplatte an die neue Küche an?",
                 ["Wo es nötig ist, passen wir die Arbeitsplatte an. Was genau möglich ist, klären wir bei der Besichtigung anhand der neuen Räume.",
                  "Ja, im Rahmen der Montage. Bei der Besichtigung prüfen wir die Maße und sagen Ihnen ehrlich, was machbar ist."]),
                ("Schließen Sie auch Wasser und Elektrogeräte an?",
                 ["Das besprechen wir vorab bei der Besichtigung. Arbeiten an Strom- und Wasseranschlüssen dürfen nur entsprechend qualifizierte Fachbetriebe ausführen – darauf achten wir.",
                  "Wir klären bei der Besichtigung, welche Anschlussarbeiten anfallen. Elektro- und Sanitärarbeiten gehören in die Hände eines zugelassenen Fachbetriebs."])],
        "nutzen": [("Millimetergenau", "Unterschränke in Waage, Hängeschränke im Lot, Fronten in einer Flucht."),
                   ("Abbau + Aufbau", "Beim Umzug übernehmen wir die Küche komplett – keine Schnittstellen, keine Ausreden.")],
    },
}

# Familien-Pools: Einleitung, Warum, Ablauf, FAQ – mit Platzhaltern
FAM = {
    "umzug": {
        "intro": [
            "{stadt} ist mit {einw} Einwohnern eine {groesse} {region_txt} – und jeder Umzug hier hat seine eigenen Wege, Treppen und Parkplätze. Wir planen {akk} so, dass am Ende alles in {ziel} steht.",
            "Von Herten aus sind wir {dist_txt} schnell bei Ihnen in {stadt}. Ob Altbau oder Neubau, Erdgeschoss oder vierte Etage: {art} läuft bei uns mit festem Ansprechpartner und klarer Planung.",
            "Wer in {stadt} umzieht, möchte vor allem eins: dass {objekt} heil und pünktlich ankommen. Genau darauf ist unser Team ausgelegt – für {kunden} gleichermaßen.",
            "In {stadt} verteilen sich {einw} Menschen auf {flaeche} km². Das bedeutet: Zwischen den Stadtteilen liegen mal wenige Straßen, mal einige Kilometer – wir kalkulieren {akk} entsprechend realistisch.",
            "Sie ziehen innerhalb von {stadt} um, aus {stadt} weg oder neu hierher? Für alle drei Fälle übernehmen wir das Tragen, den Transport und den Aufbau – mit einem Team aus der Region.",
            "{art_gross} in {stadt} beginnt bei uns mit einer kostenlosen Besichtigung. Danach wissen Sie genau, was passiert, wann es passiert und was es kostet – ohne Überraschungen am Umzugstag.",
        ],
        "warum": [
            "Weil wir aus der Region kommen: {stadt} liegt {richtung_txt} unseres Standorts in Herten, {dist_txt} entfernt{kreis_klammer}.",
            "Weil {akk} eine Planung braucht, die zur Stadt passt. In einer {groesse} wie {stadt} heißt das: Ladezone klären, Tragewege prüfen, Zeitpuffer einplanen.",
            "Weil Sie mit uns nur einen Ansprechpartner haben – vom ersten Anruf bis zum letzten aufgebauten Schrank in {ziel}.",
            "Weil wir Umzug, Montage und Entsorgung kombinieren. Was in {stadt} nicht mit umziehen soll, nehmen wir direkt mit.",
            "Weil ein junges, eingespieltes Team schneller und sorgfältiger arbeitet als zusammengewürfelte Helfer – das merken Sie am Umzugstag.",
        ],
        "ablauf": [
            [("Anfrage", "Sie schildern kurz, was umzieht – per Formular, Telefon oder WhatsApp."),
             ("Kurz anfragen", "Formular ausfüllen oder anrufen: Start- und Zieladresse, Termin, grobe Wohnungsgröße."),
             ("Erster Kontakt", "Ein paar Eckdaten genügen: Wann, von wo nach wo, welche Etage?")],
            [("Besichtigung", "Wir schauen uns Wohnung, Treppenhaus und Zugang an – kostenlos und unverbindlich."),
             ("Termin vor Ort", "Bei der Besichtigung erfassen wir Möbel, Kartons und Besonderheiten."),
             ("Kostenlose Besichtigung", "Wir sehen uns alles an und beantworten Ihre Fragen direkt vor Ort.")],
            [("Festes Angebot", "Sie erhalten ein transparentes Angebot und einen verbindlichen Termin."),
             ("Klarer Plan", "Personal, Fahrzeug, Uhrzeit – alles ist vorher abgestimmt."),
             ("Angebot & Termin", "Schriftliches Angebot, fester Termin, keine versteckten Positionen.")],
            [("Umzugstag", "Wir tragen, transportieren und bauen auf – Sie behalten den Überblick."),
             ("Durchführung", "Abbau, Transport und Aufbau in einem Zug, am Ende besenrein."),
             ("Ankommen", "Möbel stehen, Kartons sind im richtigen Raum, die alte Wohnung ist leer.")],
        ],
        "faq": [
            ("Bieten Sie {kw} in {stadt} auch samstags an?",
             ["Ja. Wir sind Montag bis Samstag von 8 bis 18 Uhr im Einsatz – auch in {stadt}.",
              "Ja, samstags sind wir regulär unterwegs. Viele nutzen das, um für {akk} keinen Urlaubstag zu opfern."]),
            ("Wie läuft die Besichtigung für {akk} ab?",
             ["Wir kommen zu Ihnen nach {stadt}, sehen uns Räume, Möbel und Zugänge an und beantworten Ihre Fragen. Das ist kostenlos und unverbindlich.",
              "Ein Termin vor Ort in {stadt} genügt: Wir erfassen, was umzieht, prüfen Treppenhaus und Ladeweg und erstellen danach Ihr Angebot."]),
            ("Was beeinflusst den Preis für {akk}?",
             ["Vor allem Menge, Etagen, Tragewege, Entfernung und gewünschte Zusatzleistungen wie Montage oder Entsorgung. Ihr Angebot nennt alles transparent.",
              "Umfang, Stockwerke, Aufzug ja oder nein, Strecke und Extras. Nach der Besichtigung bekommen Sie einen klaren Preis."]),
            ("Brauche ich in {stadt} eine Halteverbotszone?",
             ["Das hängt von der Straße ab. In dicht bebauten Straßen ist sie oft sinnvoll; zuständig ist die Straßenverkehrsbehörde der Stadt {stadt}. Bei der Besichtigung sagen wir Ihnen, ob es nötig ist.",
              "Nicht immer. Wenn vor dem Haus kaum Platz ist, empfehlen wir sie – beantragt wird sie bei der Stadt {stadt}. Wir beraten Sie dazu bei der Besichtigung."]),
            ("Übernehmen Sie {akk} auch über größere Entfernungen?",
             ["Ja. Unser Einsatzgebiet reicht rund 100 km um Herten – {stadt} liegt {dist_txt} entfernt. Auch Ziele außerhalb besprechen wir gern.",
              "Ja. Ob innerhalb von {stadt} oder in eine andere Stadt: Wir planen die Strecke fest ein."]),
            ("Kann ich selbst mit anpacken, um Kosten zu sparen?",
             ["Gerne. Wenn Sie zum Beispiel selbst packen, berücksichtigen wir das im Angebot.",
              "Ja. Viele packen ihre Kartons selbst – wir übernehmen das Tragen, den Transport und den Aufbau."]),
            ("Sind meine Möbel während {gen} geschützt?",
             ["Wir sichern Möbel mit Decken, Folie und Gurten und tragen mit Sorgfalt durch Treppenhäuser und Türen.",
              "Ja. Polsterdecken, Stretchfolie und eine ordentliche Ladungssicherung gehören bei uns zum Standard."]),
            ("Wie lange dauert {art} in {stadt} ungefähr?",
             ["Das hängt von Menge und Zugang ab. Eine typische Mietwohnung ist häufig an einem Tag erledigt – die genaue Einschätzung bekommen Sie bei der Besichtigung.",
              "Nach der Besichtigung nennen wir Ihnen eine realistische Dauer. Kleinere Umzüge sind oft schon in wenigen Stunden erledigt."]),
            ("Gibt es einen Rabatt für Neukunden?",
             ["Ja. Als Neukunde erhalten Sie 10 % auf Ihren ersten Auftrag – geben Sie es einfach bei der Anfrage an.",
              "Ja – 10 % Neukunden-Rabatt auf den ersten Auftrag. Einfach im Formular vermerken."]),
        ],
    },
    "raeumung": {
        "intro": [
            "In {stadt} leben {einw} Menschen – und in vielen Kellern, Wohnungen und Häusern sammelt sich über die Jahre mehr an, als man allein bewältigen kann. Für {akk} bringen wir Personal, Fahrzeug und Erfahrung mit.",
            "{art_gross} in {stadt} beginnt bei uns mit einem ehrlichen Blick: kostenlose Besichtigung, klares Angebot, fester Termin. Danach räumen wir zügig und hinterlassen {ziel}.",
            "Ob Altbauetage, Reihenhaus oder Hof am Stadtrand: In {stadt} ist jede Räumung anders. Wir planen {akk} passend zu Zugang, Menge und Frist.",
            "Von unserem Standort in Herten sind es {dist_txt} bis {stadt}. Das ist für uns kurz genug, um zuverlässig und pünktlich zu sein – auch bei mehrtägigen Räumungen.",
            "{objekt}: Was in {stadt} raus muss, holen wir raus, sortieren es und entsorgen es fachgerecht. Sie müssen nichts selbst tragen und keine Container bestellen.",
            "Für {kunden} in {stadt} übernehmen wir {akk} komplett – vom Ausräumen über die Demontage bis zur besenreinen Übergabe.",
        ],
        "warum": [
            "Weil wir aus der Region kommen: {stadt} liegt {richtung_txt} von Herten, {dist_txt} entfernt{kreis_klammer}.",
            "Weil Sie bei uns ein verbindliches Angebot nach der Besichtigung bekommen – statt einer Pauschale, die am Ende nicht stimmt.",
            "Weil wir umweltgerecht trennen: Holz, Metall, Elektroschrott und Restmüll gehen dorthin, wo sie hingehören.",
            "Weil wir besenrein übergeben – so, dass Vermieter, Käufer oder Nachmieter in {stadt} nichts zu beanstanden haben.",
            "Weil wir auch mit großen Mengen und schwierigen Zugängen umgehen können: enge Treppen, verwinkelte Keller, Dachböden ohne Licht.",
        ],
        "ablauf": [
            [("Anfrage", "Kurz schildern, was geräumt werden soll – gern mit Fotos per WhatsApp."),
             ("Kontakt", "Formular, Anruf oder WhatsApp: Adresse, Räume, gewünschter Termin."),
             ("Erstes Gespräch", "Wir klären Umfang, Frist und Besonderheiten am Telefon.")],
            [("Besichtigung", "Wir schauen uns Räume, Menge und Zugang an – kostenlos."),
             ("Termin vor Ort", "Wir sehen, was raus muss, und prüfen Treppen, Wege und Stellplatz."),
             ("Kostenloser Check", "Vor Ort erkennen wir, was verwertbar ist und was entsorgt wird.")],
            [("Verbindliches Angebot", "Klarer Preis, klare Leistung, fester Termin."),
             ("Angebot & Termin", "Sie wissen vorher genau, was passiert und was es kostet."),
             ("Planung", "Personal, Fahrzeug und Entsorgung sind vorab abgestimmt.")],
            [("Räumung", "Wir räumen, trennen, entsorgen – und übergeben besenrein."),
             ("Durchführung", "Zügig, sorgfältig, mit genug Händen für einen Termin."),
             ("Übergabe", "Leere, besenreine Räume – auf Wunsch mit Abschlussrundgang.")],
        ],
        "faq": [
            ("Wird bei {dat} in {stadt} umweltgerecht entsorgt?",
             ["Ja. Wir trennen nach Holz, Metall, Elektro und Restmüll und bringen alles zu zugelassenen Annahmestellen.",
              "Ja. Fachgerechte Trennung und Entsorgung ist für uns selbstverständlich – nichts landet irgendwo am Straßenrand."]),
            ("Wie wird {art} in {stadt} berechnet?",
             ["Nach Menge, Art des Materials, Etage, Tragewegen und Entsorgungsaufwand. Nach der Besichtigung erhalten Sie einen festen Preis.",
              "Wir besichtigen kostenlos und nennen danach einen verbindlichen Preis – abhängig von Volumen, Zugang und Entsorgung."]),
            ("Übergeben Sie die Räume besenrein?",
             ["Ja. Nach der Räumung wird gefegt – leer und besenrein, bereit für die Übergabe.",
              "Ja, besenrein ist bei uns Standard. Auf Wunsch gehen wir gemeinsam einen Abschlussrundgang."]),
            ("Was passiert mit noch brauchbaren Gegenständen?",
             ["Gut erhaltene Dinge prüfen wir auf Verwertbarkeit. Wenn das möglich ist, berücksichtigen wir es fair im Angebot.",
              "Was noch brauchbar ist, landet nicht automatisch im Müll – wir prüfen eine sinnvolle Verwertung."]),
            ("Können Sie {akk} kurzfristig übernehmen?",
             ["Wenn es eilt, sagen Sie es direkt bei der Anfrage. Wir prüfen den frühesten freien Termin in {stadt}.",
              "Oft ja. Je nach Auslastung finden wir auch kurzfristig einen Termin – fragen Sie einfach an."]),
            ("Räumen Sie auch aus oberen Etagen ohne Aufzug?",
             ["Ja. Treppenhäuser ohne Aufzug sind für uns Alltag – wir planen entsprechend Personal ein.",
              "Ja, auch aus der vierten Etage ohne Aufzug. Bei der Besichtigung prüfen wir den Tragewege und planen genug Hände ein."]),
            ("Brauche ich für {akk} einen Container?",
             ["Nein. Wir laden direkt in unseren Transporter und fahren zur Entsorgung – Sie müssen nichts bestellen oder genehmigen lassen.",
              "In der Regel nicht. Wir transportieren das Material selbst ab; einen Container stellen wir nur in Ausnahmefällen in Abstimmung mit Ihnen."]),
            ("Muss ich vorher selbst aussortieren?",
             ["Nein. Sagen Sie uns, was bleiben soll – den Rest übernehmen wir. Wichtiges, das wir finden, legen wir beiseite.",
              "Nicht nötig. Markieren Sie, was Sie behalten möchten; alles andere räumen wir."]),
            ("Gibt es einen Rabatt für Neukunden?",
             ["Ja, 10 % auf Ihren ersten Auftrag. Einfach bei der Anfrage angeben.",
              "Ja. Neukunden sparen 10 % – vermerken Sie es im Formular."]),
        ],
    },
    "montage": {
        "intro": [
            "In {stadt} wohnen {einw} Menschen – und in sehr vielen Haushalten steht irgendwann ein Karton mit Einzelteilen und einer Anleitung im Flur. Für {akk} kommen wir mit Werkzeug und Erfahrung zu Ihnen.",
            "{art_gross} in {stadt}: Wir bauen {objekt} sauber, stabil und gerade auf – egal ob neu gekauft oder beim Umzug zerlegt.",
            "Von Herten aus sind wir {dist_txt} bei Ihnen in {stadt}. Sie sagen uns, was aufgebaut werden soll – wir bringen Werkzeug, Zeit und ein geübtes Auge mit.",
            "Für {kunden} in {stadt} übernehmen wir {akk}: ausgerichtet, befestigt und sofort nutzbar.",
            "Wer in {stadt} umzieht oder neu einrichtet, braucht oft vor allem eins: jemanden, der {objekt} fachgerecht montiert. Genau das ist unser Job.",
            "{art_gross} ist Präzisionsarbeit. In {stadt} erledigen wir sie mit dem Anspruch, dass nichts wackelt, klemmt oder schief hängt.",
        ],
        "warum": [
            "Weil wir aus der Nähe kommen: {stadt} liegt {richtung_txt} von Herten, {dist_txt} entfernt{kreis_klammer}.",
            "Weil wir Montage mit Umzug und Entsorgung verbinden können – alte Möbel raus, neue rein, alles an einem Termin.",
            "Weil wir sauber arbeiten: Verpackung nehmen wir auf Wunsch mit, der Raum ist danach aufgeräumt.",
            "Weil wir auf Stabilität achten: Kippsicherung, Wandbefestigung, ausgerichtete Türen und Fronten.",
            "Weil Sie einen festen Ansprechpartner haben, der vorher genau zuhört, was Sie brauchen.",
        ],
        "ablauf": [
            [("Anfrage", "Was soll aufgebaut werden? Gern mit Foto oder Link zum Möbelstück."),
             ("Kontakt", "Formular, Anruf oder WhatsApp – mit Hersteller oder Modell, wenn bekannt."),
             ("Kurz schildern", "Welche Möbel, welche Räume, welcher Wunschtermin?")],
            [("Abstimmung", "Wir klären Umfang, Wandbeschaffenheit und Zugang – bei Bedarf vor Ort."),
             ("Besichtigung", "Bei größeren Projekten schauen wir uns die Räume kostenlos an."),
             ("Check", "Maße, Wände, Anschlüsse: Wir prüfen, was nötig ist.")],
            [("Angebot", "Transparenter Preis und fester Termin."),
             ("Termin", "Verbindlicher Termin mit realistischer Zeitplanung."),
             ("Planung", "Werkzeug, Befestigungsmaterial und Zeit sind eingeplant.")],
            [("Montage", "Aufbau, Ausrichten, Befestigen – und Aufräumen."),
             ("Fertig", "Alles steht, alles hält, Verpackung ist weg."),
             ("Übergabe", "Gemeinsamer Check: Türen, Schubladen, Stabilität.")],
        ],
        "faq": [
            ("Bringen Sie für {akk} in {stadt} eigenes Werkzeug mit?",
             ["Ja, komplett – vom Akkuschrauber bis zur Wasserwaage.",
              "Ja. Werkzeug und gängiges Befestigungsmaterial haben wir dabei."]),
            ("Wie lange dauert {art}?",
             ["Das hängt vom Umfang ab. Einzelne Möbel sind oft in kurzer Zeit erledigt; größere Projekte planen wir nach Besichtigung realistisch ein.",
              "Nach der Abstimmung nennen wir Ihnen eine realistische Dauer – ohne Schönrechnen."]),
            ("Kann ich Montage und Umzug kombinieren?",
             ["Ja. Abbau in der alten, Transport und Aufbau in der neuen Wohnung – alles aus einer Hand.",
              "Genau dafür sind wir da: Umzug und Montage aus einer Hand, ohne Abstimmung zwischen mehreren Firmen."]),
            ("Was kostet {art} in {stadt}?",
             ["Das hängt von Anzahl, Größe und Komplexität der Möbel ab. Sie erhalten vorab ein transparentes Angebot.",
              "Nach kurzer Abstimmung oder Besichtigung bekommen Sie einen klaren Preis – keine Überraschungen."]),
            ("Montieren Sie auch samstags?",
             ["Ja, wir sind Montag bis Samstag von 8 bis 18 Uhr im Einsatz.",
              "Ja. Samstagstermine sind bei Berufstätigen in {stadt} besonders beliebt."]),
            ("Entsorgen Sie auch die alten Möbel?",
             ["Gerne. Alte Möbel bauen wir ab und entsorgen sie fachgerecht – direkt beim Montagetermin.",
              "Ja. Raus mit dem Alten, rein mit dem Neuen – in einem Termin."]),
            ("Gibt es einen Rabatt für Neukunden?",
             ["Ja, 10 % auf den ersten Auftrag – einfach bei der Anfrage angeben.",
              "Ja. Neukunden erhalten 10 % Rabatt auf ihren ersten Auftrag."]),
        ],
    },
}

# --------------------------------------------------------------------------- Generatoren

def _felder(s, lslug, r):
    f = fakten(s)
    l = L[lslug]
    teile = list(f["teile"])
    r.shuffle(teile)
    f.update(l)
    f["art_gross"] = l["art"][0].upper() + l["art"][1:]
    f["region_txt"] = (f"im {f['region']}" if f["region"] in ("Ruhrgebiet", "Münsterland", "Rheinland", "Bergischen Land", "Sauerland",
                                                               "Siegerland", "Westerwald", "Emsland", "Osnabrücker Land")
                       else ("im Bergischen Land" if f["region"] == "Bergisches Land" else
                             ("am Niederrhein" if f["region"] == "Niederrhein" else
                              ("in der " + f["region"] if f["region"] in ("Hellweg-Region", "Grafschaft Bentheim") else
                               ("in Ostwestfalen" if f["region"] == "Ostwestfalen" else f"in {f['region']}")))))
    f["dist_txt"] = f["dist"] or "nur wenige Minuten"
    f["richtung_txt"] = f["richtung"] or "direkt bei"
    f["kreis_klammer"] = f" ({f['kreis']})" if f["kreis"] else (f" – kreisfrei, {f['regbez']}" if f["regbez"] else "")
    f["kreis_komma"] = f" ({f['kreis']})" if f["kreis"] else ""
    f["teile_sel"] = teile[: min(8, len(teile))]
    f["teile_faq"] = liste(teile[:3]) if teile else f["stadt"]
    f["teile_txt"] = liste(teile[:3]) if teile else ""
    return f


def fmt(t, f):
    return t.format(**f)


def _abstand(a, b):
    return math.hypot((a["lat"] - b["lat"]) * 111.2, (a["lon"] - b["lon"]) * 69.2)


def _bedingung(code, f):
    return {"hoehe_n>=200": f["hoehe_n"] >= 200, "dichte_n>=2000": f["dichte_n"] >= 2000,
            "flaeche_n>=120": f["flaeche_n"] >= 120, "klein": 0 < f["einw_n"] < 20000, "heimat": f["heimat"],
            "weit": f["dist_n"] >= 60, "nah": 3 <= f["dist_n"] < 25, "teile": len(f["teile"]) >= 2,
            "plz": bool(f["plz"])}[code]


def kombi(s, lslug, alle_staedte, salt=0):
    """Alle Inhalte einer Kombi-Seite Leistung × Stadt. `salt` variiert die Auswahl (Ähnlichkeits-Optimierung)."""
    r = rng("kombi", lslug, s["slug"], salt)
    f = _felder(s, lslug, r)
    l, sp, fam = L[lslug], SPEZ[lslug], FAM[L[lslug]["fam"]]
    famk = l["fam"]
    stadt = s["name"]
    naechste = sorted((x for x in alle_staedte if x["slug"] != s["slug"]), key=lambda x: _abstand(x, s))[:8]
    nb = naechste[:]
    r.shuffle(nb)
    f.update(n1=nb[0]["name"], n2=nb[1]["name"], d1=zahl(round(_abstand(nb[0], s))), d2=zahl(round(_abstand(nb[1], s))),
             richtung_name=s.get("richtung", ""))
    tt = f["teile_sel"] + [stadt] * 3
    f.update(t1=tt[0], t2=tt[1], t3=tt[2])

    # Überschriften
    if famk == "montage":
        h1_zusatz = r.choice(["– präzise und stabil aufgebaut", "vom Montage-Team aus der Region", "– sauber, gerade, sofort nutzbar",
                              "– mit Werkzeug, Zeit und Erfahrung", "– fachgerecht und termintreu", "– Aufbau ohne Ärger"])
    else:
        h1_zusatz = r.choice(["– zuverlässig, sauber, mit festem Ansprechpartner", "vom Team aus der Region", "– kostenlose Besichtigung inklusive",
                              "– schnell erledigt und besenrein", "mit Planung, die zur Stadt passt", "– ehrlich kalkuliert, pünktlich erledigt",
                              "– ein Team, ein Ansprechpartner", "– fair, sorgfältig, termintreu"])
    h1 = f"{l['kw']} {stadt} {h1_zusatz}"

    # Einleitung: Hook + 2 Absätze aus großem Pool
    hooks = list(sp["hook"]) + list(P.HOOK[famk])
    intros = list(fam["intro"]) + list(P.INTRO[famk])
    r.shuffle(intros)
    intro = [r.choice(hooks) + " " + fmt(intros[0], f), fmt(intros[1], f)]

    # Stadtabschnitt: Region + echte Daten in variabler Reihenfolge
    reg = REGION_TEXT.get(f["region"], REGION_TEXT_DEFAULT)
    satz = [r.choice(reg)]
    if f["einw"]:
        g = fmt(r.choice(P.GROESSE_SATZ[f["groesse"]]), f)
        if f["flaeche"]:
            g += " " + r.choice([
            f"Auf {f['flaeche']} km² ergibt das rund {f['dichte']} Einwohner je Quadratkilometer.",
            f"Die Stadtfläche beträgt {f['flaeche']} km², die Bevölkerungsdichte etwa {f['dichte']} Menschen pro km².",
            f"Verteilt auf {f['flaeche']} km² sind das im Schnitt {f['dichte']} Einwohner je km².",
        ])
        satz.append(g)
    if f["kreis"]:
        satz.append(fmt(r.choice([k for k in P.KREIS_SATZ if f["regbez"] or "{regbez}" not in k]), f))
    elif f["regbez"]:
        satz.append(fmt(r.choice(P.KREISFREI_SATZ), f))
    if f["hoehe"]:
        hk = "hoch" if f["hoehe_n"] >= 200 else ("mittel" if f["hoehe_n"] >= 100 else "flach")
        satz.append(fmt(r.choice(P.HOEHE_SATZ[hk]), f))
    satz = [x for x in satz if x and "{" not in x]
    kopf, rest = satz[0], satz[1:]
    r.shuffle(rest)
    stadt_absatz = " ".join([kopf] + rest)

    # Stadtteile / Nachbarn / Anfahrt
    if len(f["teile_sel"]) >= 3:
        teile_absatz = fmt(r.choice(P.TEILE_SATZ), f)
    elif f["teile_sel"]:
        teile_absatz = fmt(r.choice(P.TEILE_SATZ_KURZ), f)
    else:
        teile_absatz = ""
    umfeld = [fmt(r.choice(P.NACHBAR_SATZ), f)]
    if not f["heimat"]:
        umfeld.append(fmt(r.choice(P.ANFAHRT_SATZ), f))
    if f["plz"]:
        umfeld.append(fmt(r.choice(P.PLZ_SATZ), f))
    r.shuffle(umfeld)
    umfeld_absatz = " ".join(umfeld)

    stadt_h2 = r.choice([f"{l['kw_kurz']} in {stadt}: Das sollten Sie wissen", f"Warum {l['kw_kurz']} in {stadt} gute Planung braucht",
                         f"{stadt} und {l['art']}: lokale Besonderheiten", f"Was {l['art']} in {stadt} besonders macht",
                         f"{l['kw_kurz']} in {stadt} – die Gegebenheiten vor Ort", f"So ist {stadt} – und das bedeutet es für {l['akk']}"])
    teile_h2 = r.choice([f"In diesen Stadtteilen von {stadt} sind wir im Einsatz", f"{l['kw_kurz']} in allen Ortsteilen von {stadt}",
                         f"Unterwegs in {stadt} und Umgebung", f"Ihr Stadtteil in {stadt}? Wir kommen hin"])

    # Warum-Block: 4 von 10 Themen, je 1 von 3 Formulierungen
    themen = list(P.WARUM[famk])
    r.shuffle(themen)
    warum = [fmt(r.choice(t), f) for t in themen[:4]]
    if f["heimat"]:
        warum = [w for w in warum if "{dist_txt}" not in w and "entfernt" not in w] or warum
    warum_h2 = r.choice([f"Warum {stadt} auf uns setzt", f"Deshalb lohnt sich unser Team für {l['akk']} in {stadt}",
                         f"Ihre Vorteile in {stadt}", f"Darum mit Ruckzuckräumung in {stadt}", f"Was Sie in {stadt} von uns erwarten können",
                         f"Gute Gründe für uns in {stadt}"])

    umfang = list(sp["umfang"])
    r.shuffle(umfang)
    umfang = umfang[: r.choice([5, 6])]
    umfang_h2 = r.choice([f"Leistungsumfang für {l['akk']} in {stadt}", f"Das ist bei {l['dat']} in {stadt} enthalten",
                          f"Was wir in {stadt} für Sie übernehmen", f"So umfassend ist {l['art']} bei uns", f"Unsere Leistungen für {l['akk']}"])

    nz = list(P.NUTZEN[famk]) + [(t, [x]) for t, x in sp["nutzen"]]
    r.shuffle(nz)
    nutzen = [(t, fmt(r.choice(v), f)) for t, v in nz[:4]]

    ablauf = [r.choice(step) for step in fam["ablauf"]]

    faq_pool = list(fam["faq"]) + list(sp["faq"])
    r.shuffle(faq_pool)
    faqs = [(fmt(q, f), fmt(r.choice(a), f)) for q, a in faq_pool[:4]]
    sf = [x for x in P.STADT_FAQ if _bedingung(x[0], f)]
    r.shuffle(sf)
    faqs += [(fmt(r.choice(q), f), fmt(r.choice(a), f)) for _c, q, a in sf[:3]]
    r.shuffle(faqs)

    title = r.choice([f"{l['kw']} {stadt} | kostenlose Besichtigung | Ruckzuckräumung",
                      f"{l['kw']} {stadt} – Team aus der Region | Ruckzuckräumung",
                      f"{l['kw']} in {stadt} | fester Ansprechpartner | Ruckzuckräumung",
                      f"{l['kw']} {stadt}: fair & termintreu | Ruckzuckräumung"])
    if len(title) > 68:
        title = f"{l['kw']} {stadt} | Ruckzuckräumung"
    desc_t = r.choice([
        "{kw} in {stadt}: kostenlose Besichtigung, transparentes Angebot, besenreine Übergabe. Mo–Sa 8–18 Uhr. ☎ 0177 6126333",
        "Sie suchen {kw} in {stadt}? Wir übernehmen {akk} zuverlässig – mit festem Ansprechpartner und 10 % Neukunden-Rabatt.",
        "{kw} {stadt} vom Team aus Herten: {objekt} – fachgerecht, pünktlich, fair kalkuliert. Jetzt kostenlos anfragen.",
        "{kw} {stadt}: Wir planen {akk} passend zur Stadt – kostenlose Besichtigung, klares Angebot, Termin Mo–Sa.",
    ])
    desc = fmt(desc_t, f)
    if len(desc) > 158:
        desc = desc[:155].rsplit(" ", 1)[0] + " …"

    fakt = [("Einwohner", f"{f['einw']}" + (f" (Stand {f['stand']})" if f["stand"] else "")), ("Fläche", f"{f['flaeche']} km²" if f["flaeche"] else ""),
            ("Einwohner je km²", f["dichte"]), ("Höhe", f"{f['hoehe']} m ü. NN" if f["hoehe"] else ""), ("Postleitzahl", f["plz"]),
            ("Kreis / Status", f["kreis"] or (f["status"] if f["status"] == "kreisfreie Stadt" else "")), ("Regierungsbezirk", f["regbez"]),
            ("Entfernung von Herten", f"{f['dist']} {f['richtung']}".strip() if f["dist"] else "Firmensitz")]
    fakt = [(k, v) for k, v in fakt if v]

    return dict(fakten=fakt, f=f, h1=h1, title=title, desc=desc, intro=intro, stadt_h2=stadt_h2, stadt_absatz=stadt_absatz,
                teile_h2=teile_h2, teile_absatz=teile_absatz, umfeld_absatz=umfeld_absatz,
                warum_h2=warum_h2, warum=warum, umfang_h2=umfang_h2, umfang=umfang, nutzen=nutzen, ablauf=ablauf,
                faqs=faqs, naechste=naechste, teile=f["teile_sel"],
                block_order=r.sample(["stadt", "umfang", "warum"], 3))


def stadtseite(s, salt=0):
    """Inhalte des Stadt-Archivs /einsatzgebiete/<stadt>/."""
    r = rng("stadt", s["slug"], salt)
    f = _felder(s, "umzug", r)
    stadt = s["name"]
    reg = REGION_TEXT.get(f["region"], REGION_TEXT_DEFAULT)
    reg_hero = r.choice(reg)
    saetze = [
        r.choice([f"{stadt} liegt {f['richtung_txt']} von Herten, {f['dist_txt']} von unserem Firmensitz entfernt.",
                  f"Von Herten nach {stadt} sind es {f['dist_txt']} Luftlinie Richtung {s.get('richtung', '')}."] if not f["heimat"] else
                 ["Herten ist unser Firmensitz – hier sind wir zu Hause und am schnellsten vor Ort."]),
        reg_hero,
    ]
    if f["einw"]:
        saetze.append(r.choice([f"Mit {f['einw']} Einwohnern ist {stadt} eine {f['groesse']} {f['region_txt']}.",
                                f"In {stadt} leben {f['einw']} Menschen {f['kreis_txt'] or f['region_txt']}."]))
    r.shuffle(saetze)
    blurb = {}
    for slug, l in L.items():
        rr = rng("karte", slug, s["slug"], salt)
        blurb[slug] = rr.choice([
            f"{l['kw_kurz']} in {stadt}: {l['objekt']} – fachgerecht erledigt.",
            f"Für {l['kunden']} in {stadt}: {l['ergebnis']}.",
            f"{l['art'][0].upper() + l['art'][1:]} in {stadt} mit kostenloser Besichtigung und festem Ansprechpartner.",
            f"Wir übernehmen {l['akk']} in {stadt} – Ziel: {l['ziel']}.",
            f"{stadt}: {l['art']} vom Team aus Herten, {f['dist_txt'] if not f['heimat'] else 'direkt vor Ort'}.",
            f"Ihr Ziel in {stadt}: {l['ziel']}. Wir kümmern uns um den Rest.",
            f"{l['objekt'][0].upper() + l['objekt'][1:]} – in {stadt} übernehmen wir das für Sie.",
            f"Kostenlose Besichtigung in {stadt}, danach ein klares Angebot für {l['akk']}.",
        ])
    # eigener Stadtabsatz + Stadt-FAQs (neutral formuliert, nicht leistungsgebunden)
    f.update(akk="Ihren Auftrag", dat="Ihrem Auftrag", art="der Auftrag", art_gross="Ihr Auftrag")
    tt = f["teile_sel"] + [stadt] * 3
    f.update(t1=tt[0], t2=tt[1], t3=tt[2])
    ort = [r.choice([x for x in reg if x != reg_hero])]
    if f["einw"]:
        ort.append(fmt(r.choice(P.GROESSE_SATZ[f["groesse"]]), f))
    if f["hoehe"]:
        hk = "hoch" if f["hoehe_n"] >= 200 else ("mittel" if f["hoehe_n"] >= 100 else "flach")
        ort.append(fmt(r.choice(P.HOEHE_SATZ[hk]), f))
    if len(f["teile_sel"]) >= 3:
        ort.append(r.choice([f"Stadtteile wie {f['t1']}, {f['t2']} und {f['t3']} fahren wir ebenso an wie das Zentrum.",
                             f"Von {f['t1']} über {f['t2']} bis {f['t3']}: Wir kommen in jeden Teil von {stadt}.",
                             f"Ob {f['t1']}, {f['t2']} oder {f['t3']} – Ihr Stadtteil gehört dazu."]))
    if f["nachbarn"]:
        nb = list(f["nachbarn"]); r.shuffle(nb)
        ort.append(r.choice([f"Angrenzend liegen {liste(nb[:3])}.", f"Nachbarorte von {stadt} sind unter anderem {liste(nb[:3])}.",
                             f"Rund um {stadt} grenzen {liste(nb[:3])} an."]))
    head, rest = ort[0], ort[1:]
    r.shuffle(rest)
    ort_absatz = " ".join([head] + rest)
    sf = [x for x in P.STADT_FAQ if _bedingung(x[0], f)]
    r.shuffle(sf)
    faqs = [(fmt(r.choice(q), f), fmt(r.choice(a), f)) for _c, q, a in sf[:3]]
    faqs.append((r.choice([f"Welche Leistungen bieten Sie in {stadt} an?", f"Was übernehmen Sie in {stadt}?"]),
                 r.choice([f"In {stadt} übernehmen wir Umzüge, Firmen- und Seniorenumzüge, Entrümpelungen, Haushalts- und Wohnungsauflösungen, Kellerentrümpelungen, die Räumung von Messie-Wohnungen sowie Möbel- und Küchenmontagen.",
                           f"Alle {len(L)} Leistungen: vom Umzug über Entrümpelung und Haushaltsauflösung bis zur Möbel- und Küchenmontage – in ganz {stadt}."])))
    h1 = r.choice([f"Umzug, Entrümpelung & Montage in {stadt}", f"Unsere Leistungen in {stadt}",
                   f"Ruckzuckräumung in {stadt}: alle Leistungen", f"{stadt}: Umzüge, Räumungen und Montagen"])
    return dict(f=f, h1=h1, text=" ".join(saetze), blurb=blurb, ort_absatz=ort_absatz, faqs=faqs,
                title=f"Umzug & Entrümpelung {stadt} | alle Leistungen | Ruckzuckräumung"[:70],
                desc=(f"Umzug, Entrümpelung, Haushaltsauflösung und Montage in {stadt}"
                      f"{' (' + f['einw'] + ' Einwohner)' if f['einw'] else ''}: kostenlose Besichtigung, Team aus Herten.")[:158])
