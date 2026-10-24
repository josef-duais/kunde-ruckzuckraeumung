"""Phase 3: Kernseiten (Über uns, Galerie, Kontakt, Bewertungen, Impressum, Datenschutz) + Funnel (/bewerten/, /rabatt/, /danke/).

/kunden-bewertung/ (Admin) wird nur gebaut, wenn GHL_KUNDENBEWERTUNG_EMBED in daten.py gesetzt ist.
Impressum und Datenschutz sind wortgetreu aus den gelieferten Rechtstexten übernommen (keine eigenen Rechtstexte).
"""
from html import escape

import build as B
import seiten as S
from daten import (FIRMA, FORMSUBMIT_ZIEL, GHL_BEWERTUNGEN_EMBED, GHL_KUNDENBEWERTUNG_EMBED, GHL_RABATT_FORMULAR_EMBED,
                   GHL_SURVEY_EMBED, GOOGLE_MAPS_EMBED, SITE_URL)

ic = B.icon
EMAIL = FIRMA["email"]

# Echte Kundenfotos für die Galerie: (Datei, Kategorie, Beschreibung des Sichtbaren)
GALERIE = [
    ("img_0060", "Umzug & Transport", "Voll beladener Transporter mit Kartons und Möbeln"),
    ("img_0640", "Umzug & Transport", "Gesicherte Möbel und Platten im Transporter"),
    ("img_0641", "Umzug & Transport", "Mitarbeiter verlädt einen weißen Schrank in den Transporter"),
    ("img_0645", "Umzug & Transport", "Zwei Mitarbeiter verpacken Möbel in einer hellen Wohnung"),
    ("img_0646", "Umzug & Transport", "Möbel werden für den Transport in Stretchfolie gewickelt"),
    ("img_0053", "Umzug & Transport", "Gestapelte Umzugskartons in einer Wohnung"),
    ("img_0515", "Umzug & Transport", "Wohnzimmer mitten im Umzug"),
    ("img_0065", "Entrümpelung", "Vollgestellter Raum vor der Entrümpelung"),
    ("img_0063", "Entrümpelung", "Zugestellte Kammer vor der Räumung"),
    ("img_0068", "Entrümpelung", "Kellerraum nach der Räumung – besenrein"),
    ("img_0538", "Entrümpelung", "Leeres, besenreines Zimmer nach der Wohnungsauflösung"),
    ("img_0513", "Montage", "Aufbau eines großen Kleiderschranks"),
    ("img_0523", "Montage", "Mitarbeiter montiert ein weißes Sideboard"),
    ("img_0051", "Montage", "Abbau einer TV-Wand vor dem Umzug"),
]


def seite(url, title, desc, crumbs_items, body, jsonld=None, review_block=True, cta=None):
    crumbs, crumb_ld = S.breadcrumb(crumbs_items)
    tail = B.bewertungen() if review_block else ""
    if cta:
        tail += S.cta_band(*cta)
    return B.page(B.head(title, desc[:158], url, jsonld=[crumb_ld] + (jsonld or [])), f"{crumbs}\n{body}\n{tail}")


def formular(fid, titel, untertitel, quelle, source):
    return B.anfrage_formular(fid, titel, untertitel, quelle, source)


def native_form(fid, subject, titel, untertitel, felder_html, button, source):
    """Natives FormSubmit-Formular (Fallback, solange kein GHL-Embed hinterlegt ist)."""
    return f"""<form class="lead-form" id="{fid}" action="https://formsubmit.co/{FORMSUBMIT_ZIEL}" method="POST">
  <p class="lead-title">{titel}</p>
  <p class="lead-sub">{untertitel}</p>
  <input type="hidden" name="_subject" value="{escape(subject)}">
  <input type="hidden" name="_next" value="{SITE_URL}/danke/?source={source}">
  <input type="hidden" name="_template" value="table">
  <input type="hidden" name="_captcha" value="false">
  <input type="hidden" name="Quelle" value="{source}">
  <div class="hp" aria-hidden="true"><label>Bitte leer lassen <input type="text" name="_honey" tabindex="-1" autocomplete="off"></label></div>
  {felder_html}
  <label class="f-check"><input type="checkbox" name="Datenschutz" value="akzeptiert" required>
    <span>Ich habe die <a href="/datenschutz/">Datenschutzerklärung</a> gelesen und stimme der Verarbeitung meiner Daten zu.*</span></label>
  <button class="btn btn-primary btn-block btn-lg" type="submit">{button} {ic('arrow')}</button>
</form>"""


def ghl_oder_fallback(embed, titel, fallback_html, min_h=620):
    """GHL-Embed consent-gated (min-height), sonst natives Formular."""
    if embed:
        return B.consent_embed("functional", embed, titel,
                               "Dieses Formular wird über unseren Partner HighLevel geladen. Dabei werden Daten an den Anbieter übertragen.",
                               min_h=min_h)
    return fallback_html


def hero_slim(eyebrow, h1, lead, extra=""):
    return f"""<section class="hero hero-sub hero-slim" aria-labelledby="hero-h">
  <div class="wrap"><p class="eyebrow eyebrow-light">{escape(eyebrow)}</p><h1 id="hero-h">{escape(h1)}</h1>
    {f'<p class="hero-lead">{escape(lead)}</p>' if lead else ''}{extra}</div>
</section>"""


def mit_formular_rechts(inhalt, form):
    return f"""<section class="sec sec-light">
  <div class="wrap split split-form">
    <div class="prose rechtstext">{inhalt}</div>
    <aside class="aside-form" id="anfrage">{form}</aside>
  </div>
</section>"""


# --------------------------------------------------------------------------- Über uns

def ueber_uns():
    form = formular("form-ueber", "Lernen Sie uns kennen", "Kostenlose Besichtigung – wir melden uns persönlich.", "Über uns", "ueber-uns")
    body = f"""{S.sub_hero("Über uns · Ruckzuckräumung aus Herten", "Ein junges Team aus Herten – motiviert und für jeden Auftrag bereit",
                    f"Hinter Ruckzuckräumung steht Inhaber {FIRMA['inhaber']} mit einem jungen, motivierten Team. Unser Versprechen steht schon im Logo: schnell, sauber, zuverlässig.",
                    ["Fester Ansprechpartner: der Inhaber", "Aus der Region. Für die Region.", "Kostenlose Besichtigung"], form)}
{S.trustbar()}
<section class="sec sec-light" aria-labelledby="story-h">
  <div class="wrap split split-img">
    <div class="prose">
      <p class="eyebrow">Unsere Geschichte</p>
      <h2 id="story-h">Umzüge, Entrümpelungen und Montagen – aus einer Hand</h2>
      <p>Ruckzuckräumung ist ein Einzelunternehmen aus Herten im Kreis Recklinghausen. Wir sind ein junges Team, das anpackt: Wir ziehen Menschen um, entrümpeln Wohnungen, Häuser, Keller und Garagen, lösen Haushalte auf und bauen Möbel und Küchen ab und wieder auf – für Privat- und Gewerbekunden.</p>
      <p>Unser Anspruch ist einfach: Sie haben einen festen Ansprechpartner, Sie bekommen nach einer kostenlosen Besichtigung ein klares Angebot, und am Ende übergeben wir alles besenrein. Was entsorgt werden muss, trennen wir umweltgerecht.</p>
      <p>Von Herten aus sind wir im Umkreis von bis zu {FIRMA['radius_km']} km im Einsatz – Montag bis Samstag von 8 bis 18 Uhr.</p>
    </div>
    <figure class="about-img"><img src="/bilder/kunde/ueber-uns-team.webp" alt="Das Team von Ruckzuckräumung verpackt Möbel für den Transport" width="720" height="860" loading="lazy" decoding="async">
      <figcaption>Echtes Foto: Unser Team bei der Arbeit.</figcaption></figure>
  </div>
</section>
<section class="sec sec-soft" aria-labelledby="inhaber-h">
  <div class="wrap split">
    <div class="founder-card">
      <!-- TODO: Porträtfoto des Inhabers einsetzen (kein Stockfoto) -->
      <span class="founder-av" aria-hidden="true">LK</span>
      <div><p class="founder-name">{escape(FIRMA['inhaber'])}</p><p class="founder-role">Inhaber · Ruckzuckräumung</p>
        <a class="btn btn-primary btn-sm" href="{B.TEL}">{ic('phone')} {B.TEL_TXT}</a></div>
    </div>
    <div class="prose">
      <h2 id="inhaber-h">Ihr Ansprechpartner: der Inhaber persönlich</h2>
      <p>Bei uns landen Sie nicht in einer Warteschleife. Inhaber {escape(FIRMA['inhaber'])} nimmt Ihre Anfrage selbst auf, kommt zur Besichtigung und plant den Einsatz – erreichbar per Telefon und WhatsApp.</p>
    </div>
  </div>
</section>
<section class="sec sec-light" aria-labelledby="werte-h">
  <div class="wrap"><div class="center"><p class="eyebrow">Wofür wir stehen</p><h2 id="werte-h">Schnell. Sauber. Zuverlässig.</h2></div>
    <div class="adv-grid">
      <article class="adv"><span class="adv-ic">{ic('truck')}</span><h3>Schnell</h3><p>Eingespieltes Team, eigener Transporter, klare Planung – damit Ihr Auftrag zügig erledigt ist.</p></article>
      <article class="adv"><span class="adv-ic">{ic('leaf')}</span><h3>Sauber</h3><p>Besenreine Übergabe und umweltgerechte Entsorgung – getrennt nach Holz, Metall, Elektro und Restmüll.</p></article>
      <article class="adv"><span class="adv-ic">{ic('check')}</span><h3>Zuverlässig</h3><p>Kostenlose Besichtigung, transparentes Angebot, fester Termin – und ein Ansprechpartner, der erreichbar ist.</p></article>
      <article class="adv adv-hi"><span class="adv-ic">{ic('tag')}</span><h3>10 % Neukunden-Rabatt</h3><p>Auf Ihren ersten Auftrag – einfach bei der Anfrage angeben.</p><a class="more" href="/rabatt/">Rabatt sichern {ic('arrow')}</a></article>
    </div></div>
</section>"""
    return seite("/ueber-uns/", "Über uns | Ruckzuckräumung – junges Team aus Herten",
                 f"Ruckzuckräumung aus Herten: Inhaber {FIRMA['inhaber']} und ein junges, motiviertes Team für Umzüge, Entrümpelungen und Montagen. Schnell. Sauber. Zuverlässig.",
                 [("Startseite", "/"), ("Über uns", "/ueber-uns/")], body,
                 jsonld=[{"@context": "https://schema.org", "@type": "AboutPage", "url": SITE_URL + "/ueber-uns/", "about": {"@id": SITE_URL + "/#firma"}}],
                 cta=("Lernen Sie uns kennen – bei einer kostenlosen Besichtigung", "Antwort vom Inhaber persönlich · Mo–Sa 8–18 Uhr"))


# --------------------------------------------------------------------------- Galerie

def galerie():
    form = formular("form-galerie", "So soll es bei Ihnen auch laufen?", "Kostenlos &amp; unverbindlich anfragen.", "Galerie", "galerie")
    kats = []
    for kat in ("Umzug & Transport", "Entrümpelung", "Montage"):
        figs = "".join(
            f'<figure><a href="/bilder/kunde/gross/{d}.webp" target="_blank" rel="noopener"><img src="/bilder/kunde/gross/{d}-klein.webp" alt="{escape(a)}" width="600" height="600" loading="lazy" decoding="async"></a><figcaption>{escape(a)}</figcaption></figure>'
            for d, k, a in GALERIE if k == kat)
        kats.append(f'<h2 class="gal-h">{escape(kat)}</h2><div class="gallery gallery-cap">{figs}</div>')
    body = f"""{S.sub_hero("Galerie · Referenzen", "Galerie: echte Fotos aus unseren Aufträgen",
                    "Keine Stockfotos, keine Symbolbilder: Hier sehen Sie, wie es bei unseren Umzügen, Entrümpelungen und Montagen tatsächlich aussieht.",
                    ["Echte Aufträge", "Vorher & nachher", "Umzug · Entrümpelung · Montage"], form)}
{S.trustbar()}
<section class="sec sec-light" aria-label="Fotos">
  <div class="wrap">{''.join(kats)}<p class="ref-note dark">Klicken Sie auf ein Foto für die große Ansicht.</p></div>
</section>"""
    return seite("/galerie/", "Galerie & Referenzen | Ruckzuckräumung Herten",
                 "Echte Fotos aus unseren Aufträgen: Umzüge, Entrümpelungen, Haushaltsauflösungen und Möbelmontagen in Herten und Umgebung.",
                 [("Startseite", "/"), ("Galerie", "/galerie/")], body,
                 jsonld=[{"@context": "https://schema.org", "@type": "ImageGallery", "url": SITE_URL + "/galerie/", "name": "Galerie Ruckzuckräumung"}],
                 cta=("Ihr Auftrag als Nächstes?", "Besichtigung kostenlos · 10 % Neukunden-Rabatt"))


# --------------------------------------------------------------------------- Kontakt

def kontakt():
    form = formular("form-kontaktseite", "Kostenloses Angebot anfordern", "Antwort vom Inhaber persönlich – kostenlos &amp; unverbindlich.",
                    "Kontaktseite", "kontakt")
    maps = (f'<iframe src="{GOOGLE_MAPS_EMBED}" title="Google Maps: Standort {escape(FIRMA["name"])}" '
            'loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>')
    body = f"""{S.sub_hero("Kontakt", "Kontakt: So erreichen Sie Ruckzuckräumung",
                    "Rufen Sie an, schreiben Sie per WhatsApp oder nutzen Sie das Formular – wir melden uns persönlich und vereinbaren eine kostenlose Besichtigung.",
                    [f"Telefon & WhatsApp: {B.TEL_TXT}", FIRMA['oeffnungszeiten'], "Besichtigung kostenlos"], form)}
<section class="sec sec-light" aria-labelledby="nap-h">
  <div class="wrap split">
    <div>
      <h2 id="nap-h">Kontaktdaten</h2>
      <address class="nap-card">
        <strong>{escape(FIRMA['name'])}</strong><br>Inh. {escape(FIRMA['inhaber'])}<br>{escape(FIRMA['strasse'])}<br>{FIRMA['plz']} {escape(FIRMA['ort'])}
      </address>
      <ul class="contact-list contact-list-dark">
        <li><a href="{B.TEL}">{ic('phone')} {B.TEL_TXT}</a></li>
        <li><a href="{B.WA}" target="_blank" rel="noopener">{ic('whatsapp')} WhatsApp: {B.TEL_TXT}</a></li>
        <li><a href="mailto:{EMAIL}">{ic('mail')} {EMAIL}</a></li>
        <li>{ic('clock')} Öffnungszeiten: {FIRMA['oeffnungszeiten']}</li>
        <li>{ic('pin')} Einsatzgebiet: bis zu {FIRMA['radius_km']} km rund um Herten</li>
      </ul>
      <div class="hero-btns"><a class="btn btn-primary btn-lg" href="{B.TEL}">{ic('phone')} Jetzt anrufen</a>
        <a class="btn btn-outline btn-lg" href="{B.WA}" target="_blank" rel="noopener">{ic('whatsapp')} WhatsApp</a></div>
    </div>
    <div class="area-card">
      <p class="area-title">Anfahrt &amp; Standort</p>
      {B.consent_embed('functional', maps, 'Google Maps laden', 'Beim Laden der Karte werden Daten an Google übertragen.', min_h=360, cls='maps-embed maps-embed-lg')}
    </div>
  </div>
</section>"""
    return seite("/kontakt/", "Kontakt | Ruckzuckräumung Herten – ☎ 0177 6126333",
                 f"Kontakt zu Ruckzuckräumung: {FIRMA['strasse']}, {FIRMA['plz']} {FIRMA['ort']}. Telefon & WhatsApp {B.TEL_TXT}, {FIRMA['oeffnungszeiten']}. Kostenlose Besichtigung.",
                 [("Startseite", "/"), ("Kontakt", "/kontakt/")], body,
                 jsonld=[{"@context": "https://schema.org", "@type": "ContactPage", "url": SITE_URL + "/kontakt/", "about": {"@id": SITE_URL + "/#firma"}}])


# --------------------------------------------------------------------------- Bewertungen

def bewertungen_seite():
    form = formular("form-bewertungen", "Überzeugen Sie sich selbst", "Kostenlose Besichtigung – Antwort vom Inhaber.", "Bewertungen", "bewertungen")
    body = f"""{S.sub_hero("Bewertungen", "Bewertungen unserer Kunden",
                    "Wir sind neu online und sammeln gerade unsere ersten Bewertungen. Ehrlich und ungeschönt – so, wie unsere Kunden es erlebt haben.",
                    ["Echte Kundenstimmen", "Keine gekauften Bewertungen", "Ihre Meinung zählt"], form)}
<section class="sec sec-light" aria-labelledby="schon-h">
  <div class="wrap narrow center">
    <p class="eyebrow">Schon mit uns gearbeitet?</p>
    <h2 id="schon-h">Schon mit uns gearbeitet? Bewerten Sie uns!</h2>
    <p class="sec-sub">Ihre Bewertung hilft anderen Kundinnen und Kunden aus der Region – und uns, noch besser zu werden. Es dauert nur eine Minute.</p>
    <a class="btn btn-primary btn-lg" href="/bewerten/">{ic('star')} Jetzt bewerten</a>
  </div>
</section>"""
    return seite("/bewertungen/", "Bewertungen | Ruckzuckräumung Herten",
                 "Bewertungen und Erfahrungen mit Ruckzuckräumung aus Herten – Umzüge, Entrümpelungen und Montagen. Schon mit uns gearbeitet? Bewerten Sie uns.",
                 [("Startseite", "/"), ("Bewertungen", "/bewertungen/")], body)


# --------------------------------------------------------------------------- Rechtstexte (wortgetreu)

IMPRESSUM = """<h2>Angaben gemäß § 5 DDG</h2>
<p><strong>Ruckzuckräumung &amp; Umzüge-Entrümpelung</strong><br>Inhaber: Lucien Fynn Khaouli<br>Josefstr. 69<br>45699 Herten<br>Deutschland</p>
<h2>Kontakt</h2>
<p>Telefon: <a href="tel:+491776126333">0177 6126333</a><br>E-Mail: <a href="mailto:ruckzuckraeumung@web.de">ruckzuckraeumung@web.de</a></p>
<h2>Rechtsform</h2>
<p>Einzelunternehmen.</p>
<h2>Umsatzsteuer</h2>
<p>Eine Umsatzsteuer-Identifikationsnummer liegt derzeit nicht vor. Eine Steuernummer wird hier nicht veröffentlicht.</p>
<h2>Verbraucherstreitbeilegung</h2>
<p>Wir sind nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
<p><a href="/datenschutz/">Datenschutzerklärung</a></p>"""

DATENSCHUTZ = """<p>Stand: 11.09.2026</p>
<h2>1. Verantwortlicher</h2>
<p>Ruckzuckräumung &amp; Umzüge-Entrümpelung<br>Inhaber: Lucien Fynn Khaouli<br>Josefstr. 69<br>45699 Herten<br>Deutschland<br>Telefon: <a href="tel:+491776126333">0177 6126333</a><br>E-Mail: <a href="mailto:ruckzuckraeumung@web.de">ruckzuckraeumung@web.de</a></p>
<h2>2. Hosting und Server-Logfiles</h2>
<p>Diese Website wird bei STRATO gehostet. Beim Aufruf der Website können technisch erforderliche Verbindungs- und Serverdaten verarbeitet werden, insbesondere IP-Adresse, Datum und Uhrzeit des Zugriffs, aufgerufene Seite bzw. Datei, übertragene Datenmenge sowie technische Angaben zum Browser und Betriebssystem. Die Verarbeitung erfolgt zur sicheren und stabilen Bereitstellung der Website und zur Abwehr von Missbrauch.</p>
<h2>3. Kontakt per Telefon, E-Mail und WhatsApp</h2>
<p>Wenn Sie uns telefonisch, per E-Mail oder über WhatsApp kontaktieren, verarbeiten wir die von Ihnen mitgeteilten Daten, insbesondere Name, Kontaktdaten und Angaben zu Ihrem Anliegen, soweit dies zur Bearbeitung Ihrer Anfrage und zur Vorbereitung oder Durchführung eines Auftrags erforderlich ist.</p>
<p>Bei der Kontaktaufnahme über WhatsApp gelten zusätzlich die Datenschutzbestimmungen des jeweiligen Anbieters. Die Nutzung von WhatsApp erfolgt freiwillig. Wenn Sie das nicht möchten, können Sie uns telefonisch oder per E-Mail kontaktieren.</p>
<h2>4. Rechtsgrundlagen</h2>
<p>Die Verarbeitung erfolgt – je nach Zweck – auf Grundlage von Art. 6 Abs. 1 lit. b DSGVO zur Anbahnung oder Durchführung eines Vertrags, Art. 6 Abs. 1 lit. c DSGVO zur Erfüllung gesetzlicher Pflichten oder Art. 6 Abs. 1 lit. f DSGVO zur Wahrung berechtigter Interessen, insbesondere für einen sicheren Websitebetrieb.</p>
<h2>5. Weitergabe und Empfänger</h2>
<p>Eine Weitergabe personenbezogener Daten erfolgt nur, soweit dies für die genannten Zwecke erforderlich ist, eine gesetzliche Pflicht besteht oder Sie eingewilligt haben. Für das Hosting kann STRATO als technischer Dienstleister personenbezogene Daten im Rahmen der gesetzlichen Vorgaben verarbeiten.</p>
<h2>6. Speicherdauer</h2>
<p>Personenbezogene Daten werden nur so lange gespeichert, wie es für den jeweiligen Zweck erforderlich ist oder gesetzliche Aufbewahrungspflichten bestehen.</p>
<h2>7. Ihre Rechte</h2>
<ul>
<li>Auskunft über die verarbeiteten personenbezogenen Daten</li>
<li>Berichtigung unrichtiger Daten</li>
<li>Löschung unter den gesetzlichen Voraussetzungen</li>
<li>Einschränkung der Verarbeitung</li>
<li>Widerspruch gegen bestimmte Verarbeitungen</li>
<li>Datenübertragbarkeit, soweit die gesetzlichen Voraussetzungen erfüllt sind</li>
<li>Widerruf einer erteilten Einwilligung mit Wirkung für die Zukunft</li>
</ul>
<p>Zur Ausübung Ihrer Rechte genügt eine Nachricht an <a href="mailto:ruckzuckraeumung@web.de">ruckzuckraeumung@web.de</a>.</p>
<h2>8. Beschwerderecht</h2>
<p>Sie haben das Recht, sich bei einer Datenschutz-Aufsichtsbehörde über die Verarbeitung Ihrer personenbezogenen Daten zu beschweren.</p>
<h2>9. Cookies, Tracking und externe Inhalte</h2>
<p>Diese Website verwendet nach dem derzeitigen Stand keine eigenen Analyse- oder Trackingdienste und keine eingebetteten Google-Schriftarten, Videos oder Karten. Beim Anklicken von Telefon-, E-Mail- oder WhatsApp-Links verlassen Sie die Website bzw. öffnen eine externe Anwendung; dort gelten die Datenschutzbestimmungen des jeweiligen Anbieters.</p>
<p><a href="/impressum/">Impressum</a></p>"""


def rechtsseite(url, name, h1, inhalt, desc):
    form = formular(f"form-{url.strip('/')}", "Kostenloses Angebot", "Kostenlos &amp; unverbindlich.", name, url.strip("/"))
    body = f"""{hero_slim("Rechtliches", h1, "")}
{mit_formular_rechts(inhalt, form)}"""
    return seite(url, f"{name} | Ruckzuckräumung", desc, [("Startseite", "/"), (name, url)], body)


# --------------------------------------------------------------------------- Funnel

def bewerten():
    sterne = "".join(
        f'<label class="star-opt"><input type="radio" name="Sterne" value="{n} von 5" {"required" if n == 5 else ""}><span>{"★" * n}</span></label>'
        for n in (5, 4, 3, 2, 1))
    felder = f"""<fieldset class="f-field star-field"><legend>Wie zufrieden waren Sie?*</legend><div class="stars-pick">{sterne}</div></fieldset>
  <div class="f-row">
    <div class="f-field"><label for="bw-name">Name*</label><input id="bw-name" name="Name" type="text" autocomplete="name" required placeholder="z. B. Anna M."></div>
    <div class="f-field"><label for="bw-ort">Ort</label><input id="bw-ort" name="Ort" type="text" placeholder="z. B. Herten"></div>
  </div>
  <div class="f-field"><label for="bw-leistung">Welche Leistung haben Sie genutzt?</label>
    <select id="bw-leistung" name="Leistung"><option value="">Bitte wählen …</option>{''.join(f'<option>{escape(l["name"])}</option>' for l in B.LEISTUNGEN)}</select></div>
  <div class="f-field"><label for="bw-text">Ihre Bewertung*</label><textarea id="bw-text" name="Bewertung" rows="4" required placeholder="Wie lief der Auftrag? Was hat Ihnen gefallen?"></textarea></div>
  <label class="f-check"><input type="checkbox" name="Veröffentlichung" value="erlaubt"><span>Meine Bewertung darf mit Vorname und Ort auf der Website veröffentlicht werden.</span></label>"""
    fallback = native_form("form-bewerten", "Neue Kundenbewertung über die Webseite", "Ihre Bewertung",
                           "Dauert nur eine Minute – vielen Dank!", felder, "Bewertung absenden", "bewerten")
    widget = ghl_oder_fallback(GHL_SURVEY_EMBED, "Bewertungs-Formular laden", fallback)
    body = f"""{hero_slim("Bewertungen › Bewerten Sie uns", "Bewerten Sie uns",
                    "Sie haben mit uns gearbeitet? Dann freuen wir uns über Ihre ehrliche Meinung – sie hilft anderen bei der Entscheidung und uns, besser zu werden.")}
<section class="sec sec-light" aria-label="Bewertung abgeben">
  <div class="wrap split split-form">
    <div class="prose">
      <h2>So einfach geht's</h2>
      <ul class="check-grid one">
        <li>{ic('check')}<span>Sterne vergeben</span></li><li>{ic('check')}<span>Ein paar Sätze schreiben</span></li><li>{ic('check')}<span>Absenden – fertig</span></li>
      </ul>
      <p>Jede Bewertung lesen wir persönlich. Kritik nehmen wir ernst: Wenn etwas nicht gepasst hat, melden wir uns bei Ihnen.</p>
    </div>
    <aside class="aside-form" id="anfrage">{widget}</aside>
  </div>
</section>"""
    return seite("/bewerten/", "Bewerten Sie uns | Ruckzuckräumung Herten",
                 "Sie haben mit Ruckzuckräumung gearbeitet? Bewerten Sie unseren Umzug, unsere Entrümpelung oder Montage – es dauert nur eine Minute.",
                 [("Startseite", "/"), ("Bewertungen", "/bewertungen/"), ("Bewerten Sie uns", "/bewerten/")], body,
                 review_block=False,  # kein Selbst-Link: Bewertungsabschnitt durch Abschluss-CTA ersetzt
                 cta=("Lieber direkt sprechen?", f"Rufen Sie uns an: {B.TEL_TXT} · Mo–Sa 8–18 Uhr"))


def rabatt():
    felder = f"""<div class="f-row">
    <div class="f-field"><label for="rb-name">Name*</label><input id="rb-name" name="Name" type="text" autocomplete="name" required placeholder="Ihr Name"></div>
    <div class="f-field"><label for="rb-tel">Telefon*</label><input id="rb-tel" name="Telefon" type="tel" autocomplete="tel" required placeholder="Ihre Telefonnummer"></div>
  </div>
  <div class="f-field"><label for="rb-mail">E-Mail</label><input id="rb-mail" name="email" type="email" autocomplete="email" placeholder="Ihre E-Mail-Adresse (optional)"></div>
  <div class="f-field"><label for="rb-leistung">Für welche Leistung?</label>
    <select id="rb-leistung" name="Leistung"><option value="">Bitte wählen …</option>{''.join(f'<option>{escape(l["name"])}</option>' for l in B.LEISTUNGEN)}</select></div>
  <div class="f-field"><label for="rb-msg">Kurze Beschreibung (optional)</label><textarea id="rb-msg" name="Nachricht" rows="3" placeholder="z. B. Umzug 3-Zimmer-Wohnung von Herten nach Marl"></textarea></div>
  <input type="hidden" name="Rabatt" value="10 % Neukunden-Rabatt">"""
    fallback = native_form("form-rabatt", "Rabatt-Anfrage (10 % Neukunden-Rabatt)", "10 % Rabatt sichern",
                           "Für Ihren ersten Auftrag – wir melden uns persönlich.", felder, "Rabatt sichern", "rabatt")
    widget = ghl_oder_fallback(GHL_RABATT_FORMULAR_EMBED, "Rabatt-Formular laden", fallback)
    body = f"""{hero_slim("Neukunden-Rabatt", "10 % Rabatt auf Ihren ersten Auftrag",
                    "Neu bei Ruckzuckräumung? Dann sparen Sie 10 % – egal ob Umzug, Entrümpelung, Haushaltsauflösung oder Montage.")}
<section class="sec sec-light" aria-label="Rabatt anfordern">
  <div class="wrap split split-form">
    <div class="prose">
      <h2>So sichern Sie sich den Rabatt</h2>
      <ul class="check-grid one">
        <li>{ic('check')}<span>Formular ausfüllen</span></li><li>{ic('check')}<span>Kostenlose Besichtigung vereinbaren</span></li>
        <li>{ic('check')}<span>10 % werden im Angebot abgezogen</span></li>
      </ul>
      <p>Der Rabatt gilt für Neukunden auf den ersten Auftrag.</p>
      <!-- TODO: Rabattbedingungen vom Kunden bestätigen lassen (Mindestauftragswert? Kombinierbarkeit?) -->
    </div>
    <aside class="aside-form" id="anfrage">{widget}</aside>
  </div>
</section>"""
    return seite("/rabatt/", "10 % Neukunden-Rabatt | Ruckzuckräumung Herten",
                 "10 % Rabatt für Neukunden auf den ersten Auftrag: Umzug, Entrümpelung, Haushaltsauflösung oder Montage – jetzt anfordern.",
                 [("Startseite", "/"), ("Rabatt", "/rabatt/")], body)


def danke():
    body = f"""<section class="hero hero-sub hero-slim danke" aria-labelledby="hero-h">
  <div class="wrap center">
    <span class="danke-ic">{ic('check')}</span>
    <p class="eyebrow eyebrow-light">Anfrage erhalten</p>
    <h1 id="hero-h">Vielen Dank, dass Sie Ihr Formular ausgefüllt haben!</h1>
    <p class="hero-lead">Wir melden uns persönlich bei Ihnen. Sie möchten nicht warten? Rufen Sie uns direkt an.</p>
    <div class="hero-btns center-btns">
      <a class="btn btn-primary btn-lg" href="{B.TEL}">{ic('phone')} {B.TEL_TXT} anrufen</a>
      <a class="btn btn-ghost btn-lg" href="/">Zurück zur Startseite</a>
    </div>
  </div>
</section>"""
    return seite("/danke/", "Vielen Dank | Ruckzuckräumung", "Vielen Dank für Ihre Anfrage bei Ruckzuckräumung. Wir melden uns persönlich bei Ihnen.",
                 [("Startseite", "/"), ("Vielen Dank", "/danke/")], body)


def kunden_bewertung():
    """Admin-only. Nur mit GHL-Embed; Schutz per .htaccess (Basic-Auth), nicht verlinkt, robots-Disallow."""
    widget = B.consent_embed("functional", GHL_KUNDENBEWERTUNG_EMBED, "Formular laden", "Formular über HighLevel.", min_h=700)
    body = f"""{hero_slim("Intern", "Kunden-Bewertung & 1-Jahres-Follow-up", "Nur für den Betreiber: Bestandskunden eintragen.")}
<section class="sec sec-light"><div class="wrap narrow">{widget}</div></section>"""
    return seite("/kunden-bewertung/", "Kunden-Bewertung (intern) | Ruckzuckräumung", "Interner Bereich.",
                 [("Startseite", "/"), ("Kunden-Bewertung", "/kunden-bewertung/")], body, review_block=False)


def alle(write):
    seiten = {
        "/ueber-uns/": ueber_uns(), "/galerie/": galerie(), "/kontakt/": kontakt(), "/bewertungen/": bewertungen_seite(),
        "/impressum/": rechtsseite("/impressum/", "Impressum", "Impressum", IMPRESSUM, "Impressum von Ruckzuckräumung & Umzüge-Entrümpelung, Inhaber Lucien Fynn Khaouli, Josefstr. 69, 45699 Herten."),
        "/datenschutz/": rechtsseite("/datenschutz/", "Datenschutz", "Datenschutzerklärung", DATENSCHUTZ, "Datenschutzerklärung von Ruckzuckräumung & Umzüge-Entrümpelung, Herten."),
        "/bewerten/": bewerten(), "/rabatt/": rabatt(), "/danke/": danke(),
    }
    for url, html in seiten.items():
        write(url, html, quiet=True)
    admin = None
    if GHL_KUNDENBEWERTUNG_EMBED:
        write("/kunden-bewertung/", kunden_bewertung(), quiet=True)
        admin = "/kunden-bewertung/"
    return list(seiten), admin
