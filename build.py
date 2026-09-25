#!/usr/bin/env python3
"""
Byggebrevet – statisk site-generator.

Kør:  python build.py
Output: ./public/  (det er den mappe, der uploades til Simply)

Tilføj en ny guide: læg en .md-fil i content/guides/ med front matter
(se en eksisterende fil). "topic:" skal matche en slug i TOPICS nedenfor.
Interne links til guides, der ikke findes endnu, vises som almindelig tekst
og bliver automatisk til links, når guiden oprettes.
"""
import html
import json
import os
import re
import shutil
import unicodedata
from datetime import date

import markdown

# ---------------------------------------------------------------- KONFIGURATION
SITE_URL = "https://byggebrevet.dk"
SITE_NAME = "Byggebrevet"
SITE_TAGLINE = "Uafhængige guides til byggeri og renovering"
CONTACT_EMAIL = "kontakt@byggebrevet.dk"
EDITOR_NAME = "Redaktionen på Byggebrevet"   # Skift til dit eget navn for bedre EEAT
PARTNER_ID = "29233"
BANNER_ID = "25692"
TARGET_BASE = "https://www.3byggetilbud.dk/tilbud/"

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "public")

MONTHS = ["januar", "februar", "marts", "april", "maj", "juni", "juli",
          "august", "september", "oktober", "november", "december"]

# ---------------------------------------------------------------- EMNER
HUBS = [
    ("tag-og-facade", "Tag og facade",
     "Nyt tag, tagmaling, facaderenovering og alt det, der beskytter huset udefra."),
    ("vinduer-og-ombygning", "Vinduer, tilbygning og ombygning",
     "Nye vinduer, tilbygninger, udestuer, carporte og større ombygninger."),
    ("energi-og-varme", "Energi og varme",
     "Varmepumper, jordvarme, solceller og isolering, der sænker varmeregningen."),
    ("bad-vvs-og-kloak", "Bad, VVS og kloak",
     "Badeværelser, rør, kloak, dræn, vandskader og sanering."),
    ("have-og-udearealer", "Have og udearealer",
     "Belægning, anlægsarbejde, gartner og hegn."),
    ("haandvaerkere", "Håndværkere og rådgivning",
     "Find den rette håndværker, og få styr på rådgivning og rapporter."),
    ("forening-og-ejendom", "Foreninger og ejendomme",
     "Til bestyrelser i andels- og ejerforeninger: faldstammer, opgange, altaner og planer."),
]

NAV_SHORT = {"tag-og-facade": "Tag og facade", "vinduer-og-ombygning": "Vinduer og byg",
             "energi-og-varme": "Energi", "bad-vvs-og-kloak": "Bad og kloak",
             "have-og-udearealer": "Have", "haandvaerkere": "Håndværkere",
             "forening-og-ejendom": "Foreninger"}

# slug på Byggebrevet, navn, hub, sti hos 3byggetilbud, kort beskrivelse
TOPICS = [
    ("nyt-tag", "Nyt tag", "tag-og-facade", "tagrenovering", "Priser på tagmaterialer, levetid og hvornår taget skal skiftes."),
    ("tagmaling", "Tagmaling og tagrens", "tag-og-facade", "tagmaling", "Forlæng tagets levetid med rens og maling."),
    ("algerens", "Algerens", "tag-og-facade", "algerens", "Fjern alger fra tag, facade og fliser."),
    ("facaderenovering", "Facaderenovering", "tag-og-facade", "facaderenovering", "Pudsning, efterisolering og reparation af facaden."),
    ("facademaling", "Facademaling", "tag-og-facade", "facademaling", "Mal facaden rigtigt, og få den til at holde."),
    ("omfugning", "Omfugning", "tag-og-facade", "omfugning", "Nye fuger holder fugten ude af murværket."),
    ("sandblaesning", "Sandblæsning af hus", "tag-og-facade", "sandblaesning", "Rens facaden i bund før maling eller fugning."),
    ("nye-vinduer", "Nye vinduer", "vinduer-og-ombygning", "vinduer", "Træ, plast eller træ/alu: priser, energikrav og montering."),
    ("glarmester", "Glarmester", "vinduer-og-ombygning", "glarmester", "Nye ruder, termoruder og glasopgaver."),
    ("tilbygning", "Tilbygning", "vinduer-og-ombygning", "tilbygning", "Pris pr. m², byggetilladelse og planlægning."),
    ("udestue", "Udestue", "vinduer-og-ombygning", "udestue", "Kold eller varm udestue, og hvad det koster."),
    ("carport-og-garage", "Carport og garage", "vinduer-og-ombygning", "carport-garage", "Regler, materialer og priser på carport og garage."),
    ("totalentreprise", "Totalentreprise", "vinduer-og-ombygning", "totalentreprise", "Én aftale for hele byggeriet – fordele og faldgruber."),
    ("fundament", "Fundament", "vinduer-og-ombygning", "fundament", "Støbning og reparation af fundament."),
    ("nedrivning", "Nedrivning", "vinduer-og-ombygning", "nedrivning", "Nedrivning af hus, skur eller indvendige vægge."),
    ("gulvarbejde", "Gulvarbejde", "vinduer-og-ombygning", "gulvarbejde", "Nye gulve, slibning og lægning."),
    ("varmepumpe-luft-til-vand", "Luft-til-vand varmepumpe", "energi-og-varme", "varmepumpe-luft-til-vand", "Pris, besparelse og hvad du skal vide før du skifter fyret ud."),
    ("varmepumpe-luft-til-luft", "Luft-til-luft varmepumpe", "energi-og-varme", "varmepumper", "Billig supplerende varme og køling om sommeren."),
    ("jordvarme", "Jordvarme", "energi-og-varme", "jordvarme", "Jordslange eller boring – pris og tilbagebetaling."),
    ("solceller", "Solceller", "energi-og-varme", "solceller", "Anlægsstørrelse, pris og tilbagebetalingstid."),
    ("isolering", "Isolering", "energi-og-varme", "isolering", "Hvor i huset isolering giver mest for pengene."),
    ("loftisolering", "Loftisolering", "energi-og-varme", "loftisolering", "Efterisolering af loftet – et af de billigste energitiltag."),
    ("hulmursisolering", "Hulmursisolering", "energi-og-varme", "hulmursisolering", "Indblæsning af isolering i hulmuren."),
    ("energimaerke", "Energimærke", "energi-og-varme", "energimaerke", "Hvornår du skal have et energimærke, og hvad det koster."),
    ("badevaerelse-renovering", "Badeværelsesrenovering", "bad-vvs-og-kloak", "badevaerelse", "Pris pr. m², vådrumsregler og tidsplan."),
    ("vvs", "VVS-arbejde", "bad-vvs-og-kloak", "vvs", "Autoriseret VVS til rør, varme og sanitet."),
    ("kloakrenovering", "Kloakrenovering", "bad-vvs-og-kloak", "kloak", "Opgravning eller strømpeforing af kloakken."),
    ("stroempeforing", "Strømpeforing", "bad-vvs-og-kloak", "strompeforing", "Renovering af rør uden at grave eller bryde op."),
    ("tv-inspektion-kloak", "TV-inspektion af kloak", "bad-vvs-og-kloak", "tv-inspektion", "Se kloakkens tilstand, før du køber eller renoverer."),
    ("omfangsdraen", "Omfangsdræn", "bad-vvs-og-kloak", "omfangsdraen", "Hold kælderen tør med nyt dræn."),
    ("faskine", "Faskine og regnvandsanlæg", "bad-vvs-og-kloak", "regnvandsanlaeg", "Led regnvandet væk på egen grund."),
    ("vandskade", "Vandskade", "bad-vvs-og-kloak", "vandskade", "Første skridt, affugtning og forsikring."),
    ("skimmelsvamp", "Skimmelsvamp", "bad-vvs-og-kloak", "skimmelsvamp", "Find årsagen, og få svampen fjernet korrekt."),
    ("asbestsanering", "Asbestsanering", "bad-vvs-og-kloak", "asbest", "Regler og priser for sikker fjernelse af asbest."),
    ("belaegning", "Belægning og brolægning", "have-og-udearealer", "belaegning", "Fliser, sten og indkørsel."),
    ("anlaegsarbejde", "Anlægsarbejde", "have-og-udearealer", "anlaeg", "Jordarbejde, terræn og haveanlæg."),
    ("gartner", "Gartner", "have-og-udearealer", "gartner", "Havepleje og nyanlæg."),
    ("hegn", "Hegn", "have-og-udearealer", "hegn", "Hegnsregler, materialer og priser."),
    ("toemrer", "Tømrer", "haandvaerkere", "toemrer", "Timepriser og typiske tømreropgaver."),
    ("murer", "Murer", "haandvaerkere", "murer", "Murerarbejde, fliser og reparationer."),
    ("maler", "Maler", "haandvaerkere", "malere", "Pris på indvendig og udvendig maling."),
    ("elektriker", "Elektriker", "haandvaerkere", "elektriker", "Autoriseret el-arbejde og priser."),
    ("eltjek", "Eltjek", "haandvaerkere", "eltjek", "Gennemgang af husets el-installationer."),
    ("handyman", "Handyman", "haandvaerkere", "handyman", "Små opgaver i hus og have."),
    ("haandvaerkertilbud", "Håndværkertilbud", "haandvaerkere", "haandvaerker", "Sådan sammenligner du tilbud fra håndværkere."),
    ("byggetilbud", "Byggetilbud", "haandvaerkere", "byggetilbud", "Indhent og vurder tilbud på større byggeprojekter."),
    ("bygherreraadgivning", "Bygherrerådgivning", "haandvaerkere", "bygherreraadgivning", "Få en rådgiver på din side af bordet."),
    ("byggesagkyndig", "Byggesagkyndig", "haandvaerkere", "byggesagkyndig", "Uvildig gennemgang af huset eller byggeriet."),
    ("tilstandsrapport", "Tilstandsrapport", "haandvaerkere", "tilstandsrapport", "Hvad rapporten dækker, og hvad den koster."),
    ("faldstammerenovering", "Faldstammerenovering", "forening-og-ejendom", "faldstammerenovering", "Planlægning, pris pr. lejlighed og beboerhensyn."),
    ("renovering-af-opgang", "Renovering af opgang", "forening-og-ejendom", "opgang", "Maling, gulve, lys og brandsikring i opgangen."),
    ("doertelefonanlaeg", "Dørtelefonanlæg", "forening-og-ejendom", "dortelefonanlaeg", "Lyd, video eller app – pris pr. lejlighed."),
    ("vedligeholdelsesplan", "Vedligeholdelsesplan", "forening-og-ejendom", "vedligeholdelsesplaner", "10-årsplan og budget for foreningens bygninger."),
    ("altaner", "Altaner", "forening-og-ejendom", "altaner", "Altanprojekter i etageejendomme fra idé til montering."),
    ("ejendomsservice", "Ejendomsservice", "forening-og-ejendom", "ejendomsservice", "Vicevært og drift af foreningens ejendom."),
]
TOPIC = {t[0]: dict(slug=t[0], name=t[1], hub=t[2], target=t[3], blurb=t[4]) for t in TOPICS}
HUB = {h[0]: dict(slug=h[0], name=h[1], blurb=h[2]) for h in HUBS}


def aff(target, uid=""):
    """Partner-ads deeplink til 3byggetilbud."""
    url = f"https://www.partner-ads.com/dk/klikbanner.php?partnerid={PARTNER_ID}&bannerid={BANNER_ID}"
    if uid:
        url += "&uid=" + re.sub(r"[^a-z0-9-]", "", uid)
    return url + "&htmlurl=" + TARGET_BASE + target + "/"


def esc(s):
    return html.escape(s, quote=True)


def fmt_date(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d}. {MONTHS[m-1]} {y}"


def slugify(value, separator="-"):
    value = value.lower().replace("æ", "ae").replace("ø", "oe").replace("å", "aa")
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^\w\s-]", "", value).strip()
    return re.sub(r"[\s_-]+", separator, value)


# ---------------------------------------------------------------- INDLÆSNING
def read_md(path):
    raw = open(path, encoding="utf-8").read()
    meta, body = {}, raw
    if raw.startswith("---"):
        _, fm, body = raw.split("---", 2)
        for line in fm.strip().splitlines():
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            k, v = k.strip(), v.strip()
            if k in ("fact",):
                meta.setdefault(k, []).append(v)
            else:
                meta[k] = v
    return meta, body.strip()


# ---------------------------------------------------------------- SHORTCODES
def cta_html(topic_slug, uid, heading=None, button=None, variant=""):
    t = TOPIC[topic_slug]
    heading = heading or f"Få op til 3 tilbud på {t['name'].lower()}"
    button = button or "Få 3 gratis tilbud"
    return (
        f'\n<aside class="cta {variant}">'
        f'<span class="cta-stamp" aria-hidden="true">Gratis<br>og uforpligtende</span>'
        f'<p class="cta-title">{esc(heading)}</p>'
        f'<p class="cta-text">Beskriv opgaven én gang på 3byggetilbud.dk, og få op til tre tilbud '
        f'fra håndværkere i dit område. Du vælger selv, om du vil gå videre.</p>'
        f'<a class="btn btn-cta" href="{esc(aff(t["target"], uid))}" rel="sponsored nofollow noopener" target="_blank">{esc(button)}</a>'
        f'<p class="cta-ad">Annonce. Vi modtager provision, hvis du indhenter tilbud via linket.</p>'
        f'</aside>\n'
    )


def apply_shortcodes(body, page_topic, uid):
    # [[cta]]  [[cta:slug]]  [[cta:slug|Overskrift]]
    def rep(m):
        arg = (m.group(1) or "").strip()
        slug, heading = page_topic, None
        if arg:
            parts = arg.split("|")
            if parts[0].strip():
                slug = parts[0].strip()
            if len(parts) > 1:
                heading = parts[1].strip()
        return cta_html(slug, uid, heading)
    return re.sub(r"\[\[cta(?::([^\]]*))?\]\]", rep, body)


MD_EXT = ["tables", "toc", "attr_list", "sane_lists"]
MD_CFG = {"toc": {"slugify": slugify, "toc_depth": "2"}}


def render_md(body):
    md = markdown.Markdown(extensions=MD_EXT, extension_configs=MD_CFG)
    out = md.convert(body)
    out = re.sub(r"<table>", '<div class="table-wrap"><table>', out)
    out = re.sub(r"</table>", "</table></div>", out)
    # Eksterne links (ikke affiliate) åbner i ny fane
    out = re.sub(r'<a href="(https?://(?!www\.partner-ads)[^"]+)">',
                 r'<a href="\1" target="_blank" rel="noopener">', out)
    return out, md.toc_tokens


def extract_faq(html_body):
    m = re.search(r'<h2 id="[^"]*">Ofte stillede spørgsmål</h2>(.*?)(?=<h2|$)', html_body, re.S)
    if not m:
        return []
    faq = []
    for q, a in re.findall(r"<h3[^>]*>(.*?)</h3>(.*?)(?=<h3|$)", m.group(1), re.S):
        text = re.sub(r"<[^>]+>", "", a).strip()
        faq.append((re.sub(r"<[^>]+>", "", q).strip(), re.sub(r"\s+", " ", text)))
    return faq


def word_count(html_body):
    text = re.sub(r"<[^>]+>", " ", html_body)
    return len(re.findall(r"\w+", text))


# ---------------------------------------------------------------- LAYOUT
LOGO_MARK = (
    '<svg class="logo-mark" viewBox="0 0 32 32" aria-hidden="true">'
    '<path d="M3 14 16 3l13 11v15H3z" fill="#1F3A4D"/>'
    '<path d="M3 14l13 9 13-9" fill="none" stroke="#F4B400" stroke-width="2.6" stroke-linejoin="round"/>'
    '</svg>'
)


def nav_html(active_hub=None):
    cur = ' aria-current="page"'
    items = "".join(
        f'<li><a href="/{h[0]}/"{cur if h[0] == active_hub else ""}>{esc(NAV_SHORT.get(h[0], h[1]))}</a></li>'
        for h in HUBS)
    return f'''
<header class="site-header">
  <div class="wrap header-inner">
    <a class="logo" href="/" aria-label="{SITE_NAME} – forside">{LOGO_MARK}<span>Byggebrevet</span></a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav">Emner</button>
    <nav id="site-nav" class="site-nav" aria-label="Emner"><ul>{items}</ul></nav>
    <a class="btn btn-cta header-cta" href="{esc(aff('byggetilbud','header'))}" rel="sponsored nofollow noopener" target="_blank">Få 3 tilbud</a>
  </div>
</header>'''


def footer_html():
    hubs = "".join(f'<li><a href="/{h[0]}/">{esc(h[1])}</a></li>' for h in HUBS)
    year = date.today().year
    return f'''
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <a class="logo logo-footer" href="/">{LOGO_MARK}<span>Byggebrevet</span></a>
      <p>{SITE_TAGLINE}. Vi forklarer priser, regler og faldgruber, så du står stærkere, når du indhenter tilbud.</p>
      <p class="small">Byggebrevet indeholder annoncelinks til 3byggetilbud.dk. <a href="/annonceoplysning/">Sådan tjener vi penge</a>.</p>
    </div>
    <div><p class="footer-h">Emner</p><ul>{hubs}</ul></div>
    <div><p class="footer-h">Om Byggebrevet</p><ul>
      <li><a href="/om-byggebrevet/">Om os og kontakt</a></li>
      <li><a href="/redaktionel-proces/">Redaktionel proces</a></li>
      <li><a href="/annonceoplysning/">Annonceoplysning</a></li>
      <li><a href="/privatlivspolitik/">Privatliv og cookies</a></li>
    </ul></div>
  </div>
  <div class="wrap footer-bottom small">© {year} Byggebrevet. Priserne på sitet er vejledende. Indhent altid konkrete tilbud.</div>
</footer>'''


def page(title, description, canonical, body, schema=None, active_hub=None, sticky=None, noindex=False):
    # Hold titlen inden for det, Google viser: drop brand-suffikset, hvis titlen er lang
    if len(title) > 65 and title.endswith(f" | {SITE_NAME}"):
        title = title[: -len(f" | {SITE_NAME}")]
    schema_tags = ""
    for s in (schema or []):
        schema_tags += f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>\n'
    sticky_html = ""
    if sticky:
        sticky_html = (f'<div class="sticky-cta" hidden><span>{esc(sticky[0])}</span>'
                       f'<a class="btn btn-cta" href="{esc(sticky[1])}" rel="sponsored nofollow noopener" target="_blank">Få 3 tilbud</a></div>')
    robots = '<meta name="robots" content="noindex">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large">'
    return f'''<!doctype html>
<html lang="da">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{SITE_URL}{canonical}">
{robots}
<meta property="og:type" content="website">
<meta property="og:locale" content="da_DK">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{SITE_URL}{canonical}">
<meta property="og:image" content="{SITE_URL}/static/img/og.png">
<meta name="theme-color" content="#1F3A4D">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/static/fonts/archivo.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/static/fonts/serif.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/static/style.css?v={CSS_VERSION}">
{schema_tags}</head>
<body>
<a class="skip" href="#main">Spring til indhold</a>
{nav_html(active_hub)}
<main id="main">
{body}
</main>
{footer_html()}
{sticky_html}
<script src="/static/site.js?v={CSS_VERSION}" defer></script>
</body>
</html>'''


CSS_VERSION = "1"


def org_schema():
    return {"@context": "https://schema.org", "@type": "Organization", "name": SITE_NAME,
            "url": SITE_URL, "logo": f"{SITE_URL}/apple-touch-icon.png", "email": CONTACT_EMAIL}


def breadcrumb(items):
    crumbs = " <span aria-hidden=\"true\">/</span> ".join(
        f'<a href="{u}">{esc(n)}</a>' if u else f'<span aria-current="page">{esc(n)}</span>' for n, u in items)
    schema = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, **({"item": SITE_URL + u} if u else {})}
        for i, (n, u) in enumerate(items)]}
    return f'<nav class="crumbs" aria-label="Brødkrummer">{crumbs}</nav>', schema


# ---------------------------------------------------------------- SIDER
def build_guide(meta, body_md, guides, subs, key):
    t = TOPIC[meta["topic"]]
    slug = t["slug"]
    uid = key.replace("/", "-")
    is_sub = "/" in key
    hub = HUB[t["hub"]]
    body_md = apply_shortcodes(body_md, slug, uid)
    content, toc_tokens = render_md(body_md)
    words = word_count(content)
    minutes = max(1, round(words / 200))
    faq = extract_faq(content)

    toc_items = "".join(f'<li><a href="#{tok["id"]}">{esc(html.unescape(tok["name"]))}</a></li>' for tok in toc_tokens)
    toc = f'<details class="toc" data-open-desktop><summary>Indhold på siden</summary><ol>{toc_items}</ol></details>'

    facts = ""
    for f in meta.get("fact", []):
        k, v = [x.strip() for x in f.split("|", 1)]
        facts += f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>"

    children_html = ""
    kids = [(k, m) for k, m in subs.get(slug, []) if k != key]
    if kids:
        head = f"Dybere guides om {t['name'].lower()}" if not is_sub else f"Flere guides om {t['name'].lower()}"
        lis = ""
        if is_sub:
            lis += f'<li><a href="/{slug}/">{esc(TOPIC[slug]["name"])}: den samlede guide</a><span>{esc(t["blurb"])}</span></li>'
        lis += "".join(f'<li><a href="/{k}/">{esc(m.get("short", m["title"]))}</a><span>{esc(m["description"][:140])}</span></li>' for k, m in kids)
        children_html = f'<section class="related"><h2>{esc(head)}</h2><ul>{lis}</ul></section>'
    elif is_sub:
        children_html = (f'<section class="related"><h2>Den samlede guide</h2><ul><li><a href="/{slug}/">{esc(t["name"])}</a>'
                         f'<span>{esc(t["blurb"])}</span></li></ul></section>')

    related = [g for g in guides if TOPIC[g]["hub"] == t["hub"] and g != slug][:4]
    others = [s for s in TOPIC if TOPIC[s]["hub"] == t["hub"] and s != slug and s not in guides][:4]
    related_html = ""
    if related or others:
        lis = "".join(f'<li><a href="/{g}/">{esc(TOPIC[g]["name"])}</a><span>{esc(TOPIC[g]["blurb"])}</span></li>' for g in related)
        lis += "".join(
            f'<li><a href="{esc(aff(TOPIC[s]["target"], uid+"-rel"))}" rel="sponsored nofollow noopener" target="_blank">Tilbud på {esc(TOPIC[s]["name"].lower())}</a><span>{esc(TOPIC[s]["blurb"])}</span></li>'
            for s in others)
        related_html = f'<section class="related"><h2>Mere om {esc(hub["name"].lower())}</h2><ul>{lis}</ul></section>'
    related_html = children_html + related_html

    trail = [("Forside", "/"), (hub["name"], f"/{hub['slug']}/")]
    if is_sub:
        trail.append((t["name"], f"/{slug}/"))
    crumbs, crumb_schema = breadcrumb(trail + [(meta.get("short", meta["title"]), None)])
    updated = meta.get("updated", date.today().isoformat())
    published = meta.get("published", updated)

    body = f'''
<div class="wrap guide-layout">
  <article class="guide">
    {crumbs}
    <h1>{esc(meta["title"])}</h1>
    <p class="meta"><span>Opdateret {fmt_date(updated)}</span><span>Af <a href="/om-byggebrevet/">{esc(EDITOR_NAME)}</a></span><span>{minutes} min. læsning</span></p>
    <p class="disclosure">Siden indeholder annoncelinks til 3byggetilbud.dk. Det påvirker ikke vores vurderinger. <a href="/annonceoplysning/">Læs mere</a></p>
    {toc}
    <div class="prose">
{content}
    </div>
    <section class="author-box">
      <p class="author-name">{esc(EDITOR_NAME)}</p>
      <p>Vi gennemgår priser, regler og byggetekniske anvisninger og opdaterer guiden, når noget ændrer sig. Priserne er vejledende intervaller og skal altid holdes op mod konkrete tilbud. <a href="/redaktionel-proces/">Sådan arbejder vi</a>.</p>
    </section>
    {related_html}
  </article>
  <aside class="guide-side">
    <div class="side-sticky">
      <div class="facts"><p class="facts-h">Hurtigt overblik</p><dl>{facts}</dl></div>
      {cta_html(slug, uid + "-side", f"Få tilbud på {t['name'].lower()}", variant="cta-side")}
    </div>
  </aside>
</div>'''

    article_schema = {
        "@context": "https://schema.org", "@type": "Article", "headline": meta["title"],
        "description": meta["description"], "datePublished": published, "dateModified": updated,
        "inLanguage": "da-DK", "mainEntityOfPage": f"{SITE_URL}/{key}/",
        "author": {"@type": "Organization", "name": EDITOR_NAME, "url": f"{SITE_URL}/om-byggebrevet/"},
        "publisher": org_schema(), "wordCount": words,
    }
    schema = [article_schema, crumb_schema]
    if faq:
        schema.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})

    out = page(meta.get("seo_title", meta["title"]), meta["description"], f"/{key}/", body, schema,
               active_hub=t["hub"], sticky=(f"Tilbud på {t['name'].lower()}", aff(t["target"], uid + "-sticky")))
    return out, words


def build_hub(hub_slug, meta, body_md, guides, subs=None):
    subs = subs or {}
    hub = HUB[hub_slug]
    intro, _ = render_md(apply_shortcodes(body_md, next(s for s in TOPIC if TOPIC[s]["hub"] == hub_slug), hub_slug)) if body_md else ("", None)
    cards = ""
    for s, t in TOPIC.items():
        if t["hub"] != hub_slug:
            continue
        if s in guides:
            cards += (f'<li class="topic has-guide"><a class="topic-link" href="/{s}/">{esc(t["name"])}</a>'
                      f'<p>{esc(t["blurb"])}</p><span class="topic-meta">Læs guiden{f" og {len(subs[s])} uddybende artikler" if len(subs.get(s, [])) > 1 else (" og 1 uddybende artikel" if subs.get(s) else "")}</span></li>')
        else:
            cards += (f'<li class="topic"><span class="topic-name">{esc(t["name"])}</span><p>{esc(t["blurb"])}</p>'
                      f'<a class="topic-aff" href="{esc(aff(t["target"], hub_slug))}" rel="sponsored nofollow noopener" target="_blank">Få 3 tilbud</a></li>')
    crumbs, crumb_schema = breadcrumb([("Forside", "/"), (hub["name"], None)])
    body = f'''
<div class="wrap hub">
  {crumbs}
  <h1>{esc(meta.get("title", hub["name"]))}</h1>
  <p class="lead">{esc(meta.get("lead", hub["blurb"]))}</p>
  <ul class="topic-grid">{cards}</ul>
  <div class="prose hub-prose">{intro}</div>
</div>'''
    return page(meta.get("seo_title", f"{hub['name']}: priser og guides | {SITE_NAME}"),
                meta.get("description", hub["blurb"]), f"/{hub_slug}/", body, [crumb_schema], active_hub=hub_slug)


def build_simple(meta, body_md, slug):
    content, _ = render_md(body_md.replace("{EMAIL}", CONTACT_EMAIL))
    crumbs, crumb_schema = breadcrumb([("Forside", "/"), (meta["title"], None)])
    body = f'<div class="wrap simple">{crumbs}<h1>{esc(meta["title"])}</h1><div class="prose">{content}</div></div>'
    return page(meta.get("seo_title", f"{meta['title']} | {SITE_NAME}"), meta["description"], f"/{slug}/", body, [crumb_schema])


def build_home(guides, guide_meta):
    hub_cards = ""
    for h in HUBS:
        n_topics = sum(1 for t in TOPIC.values() if t["hub"] == h[0])
        hub_cards += (f'<li><a href="/{h[0]}/"><span class="hub-name">{esc(h[1])}</span>'
                      f'<span class="hub-blurb">{esc(h[2])}</span><span class="hub-count">{n_topics} emner</span></a></li>')

    featured = [g for g in ["nyt-tag", "varmepumpe-luft-til-vand", "nye-vinduer", "badevaerelse-renovering",
                            "tilbygning", "facaderenovering"] if g in guides]
    price_rows = "".join(
        f'<tr><td><a href="/{g}/">{esc(TOPIC[g]["name"])}</a></td><td>{esc(guide_meta[g].get("price",""))}</td>'
        f'<td>{esc(guide_meta[g].get("price_note",""))}</td></tr>' for g in featured)

    forening = [g for g in ["faldstammerenovering", "vedligeholdelsesplan", "altaner", "renovering-af-opgang",
                            "doertelefonanlaeg"] if g in guides]
    forening_list = "".join(f'<li><a href="/{g}/">{esc(TOPIC[g]["name"])}</a> <span>{esc(TOPIC[g]["blurb"])}</span></li>' for g in forening)

    options = ""
    for h in HUBS:
        opts = "".join(f'<option value="{s}">{esc(t["name"])}</option>' for s, t in TOPIC.items() if t["hub"] == h[0])
        options += f'<optgroup label="{esc(h[1])}">{opts}</optgroup>'
    finder_data = {s: {"name": t["name"], "guide": f"/{s}/" if s in guides else "",
                       "price": guide_meta.get(s, {}).get("price", ""),
                       "note": guide_meta.get(s, {}).get("price_note", ""),
                       "aff": aff(t["target"], "forside-finder")} for s, t in TOPIC.items()}

    body = f'''
<section class="hero">
  <div class="wrap hero-inner">
    <div class="hero-text">
      <h1>Kend prisen, før håndværkeren gør</h1>
      <p class="lead">Byggebrevet samler priser, regler og erfaringer om {len(TOPIC)} typer byggeopgaver. Læs dig klog, og indhent derefter tilbud med ro i maven.</p>
    </div>
    <form class="finder" onsubmit="return false" aria-labelledby="finder-h">
      <p id="finder-h" class="finder-h">Hvad skal du have lavet?</p>
      <label class="sr" for="finder-select">Vælg opgave</label>
      <select id="finder-select"><option value="">Vælg en opgave</option>{options}</select>
      <div class="finder-result" aria-live="polite"></div>
    </form>
  </div>
</section>

<section class="wrap section">
  <h2>Find dit emne</h2>
  <ul class="hub-grid">{hub_cards}</ul>
</section>

<section class="wrap section two-col">
  <div>
    <h2>Hvad koster det typisk?</h2>
    <p>Vejledende prisintervaller fra vores guides. Den endelige pris afhænger af hus, adgangsforhold og materialevalg.</p>
    <div class="table-wrap"><table><thead><tr><th>Opgave</th><th>Typisk pris</th><th>Forudsætning</th></tr></thead><tbody>{price_rows}</tbody></table></div>
  </div>
  <div class="steps-box">
    <h2>Sådan får du et godt tilbud</h2>
    <ol class="steps">
      <li><strong>Læs guiden til din opgave.</strong> Så ved du, hvilket prisniveau og hvilke løsninger du kan forvente.</li>
      <li><strong>Beskriv opgaven præcist.</strong> Mål, materialer, fotos og ønsket tidspunkt giver sammenlignelige tilbud.</li>
      <li><strong>Indhent mindst tre tilbud.</strong> Det er den enkleste måde at se, om en pris er rimelig.</li>
      <li><strong>Sammenlign mere end prisen.</strong> Tjek forbehold, tidsplan, garanti og AB-forbruger-aftalen.</li>
    </ol>
    <a class="btn btn-cta" href="{esc(aff('byggetilbud','forside-steps'))}" rel="sponsored nofollow noopener" target="_blank">Få 3 gratis tilbud</a>
    <p class="cta-ad">Annonce. Linket går til 3byggetilbud.dk.</p>
  </div>
</section>

<section class="band">
  <div class="wrap section two-col">
    <div>
      <h2>Til bestyrelsen i foreningen</h2>
      <p>Store fællesprojekter kræver overblik, generalforsamlingsbeslutninger og ofte rådgivning. Vores guides er skrevet til bestyrelser i andels- og ejerforeninger.</p>
      <p><a href="/forening-og-ejendom/">Se alle emner for foreninger</a></p>
    </div>
    <ul class="plain-list">{forening_list}</ul>
  </div>
</section>

<section class="wrap section narrow">
  <h2>Hvorfor Byggebrevet?</h2>
  <p>Byggebrevet er et uafhængigt dansk guide-site. Vi sælger ikke håndværk og er ikke ejet af et håndværkerfirma. Vi tjener penge, når læsere indhenter tilbud via vores samarbejdspartner 3byggetilbud.dk, og det står tydeligt ved hvert link. Priser og regler i guiderne er tjekket op mod offentlige kilder som Bygningsreglementet, Energistyrelsen og byggebranchens anvisninger. <a href="/redaktionel-proces/">Læs om vores redaktionelle proces</a>.</p>
</section>
<script id="finder-data" type="application/json">{json.dumps(finder_data, ensure_ascii=False)}</script>'''
    schema = [org_schema(), {"@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME, "url": SITE_URL + "/",
                             "inLanguage": "da-DK"}]
    return page(f"{SITE_NAME} – priser og guides til byggeri og renovering",
                "Uafhængige guides med priser, regler og tjeklister til nyt tag, vinduer, varmepumper, badeværelser, tilbygninger og foreningsprojekter.",
                "/", body, schema)


# ---------------------------------------------------------------- LINK-VASK
def fix_internal_links(html_doc, valid):
    missing = set()

    def rep(m):
        href, text = m.group(1), m.group(2)
        path = href.split("#")[0]
        if path in valid or path.startswith("/static/"):
            return m.group(0)
        missing.add(path)
        return text
    out = re.sub(r'<a href="(/[^"]*)">(.*?)</a>', rep, html_doc, flags=re.S)
    return out, missing


def write(path_rel, content):
    full = os.path.join(OUT, path_rel.strip("/"), "index.html") if not path_rel.endswith((".html", ".xml", ".txt", "htaccess")) else os.path.join(OUT, path_rel.strip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, "static"), os.path.join(OUT, "static"))
    for f in ("favicon.svg", "favicon.ico", "apple-touch-icon.png", ".htaccess"):
        src = os.path.join(ROOT, "root", f)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(OUT, f))

    gdir = os.path.join(ROOT, "content", "guides")
    guide_files = {}
    for fn in sorted(os.listdir(gdir)):
        if fn.endswith(".md"):
            meta, body = read_md(os.path.join(gdir, fn))
            key = meta["topic"] + ("/" + meta["sub"] if meta.get("sub") else "")
            guide_files[key] = (meta, body)
    guides = {k for k in guide_files if "/" not in k}
    guide_meta = {k: v[0] for k, v in guide_files.items() if "/" not in k}
    subs = {}
    for k, (m, _) in sorted(guide_files.items()):
        if "/" in k:
            subs.setdefault(m["topic"], []).append((k, m))

    pages = {}
    report = []
    for slug, (meta, body) in guide_files.items():
        html_doc, words = build_guide(meta, body, guides, subs, slug)
        pages[f"/{slug}/"] = (html_doc, meta.get("updated"))
        report.append((slug, words))

    for h in HUBS:
        p = os.path.join(ROOT, "content", "hubs", f"{h[0]}.md")
        meta, body = read_md(p) if os.path.exists(p) else ({}, "")
        pages[f"/{h[0]}/"] = (build_hub(h[0], meta, body, guides, subs), meta.get("updated"))

    pdir = os.path.join(ROOT, "content", "pages")
    for fn in sorted(os.listdir(pdir)):
        if fn.endswith(".md"):
            meta, body = read_md(os.path.join(pdir, fn))
            slug = fn[:-3]
            pages[f"/{slug}/"] = (build_simple(meta, body, slug), meta.get("updated"))

    pages["/"] = (build_home(guides, guide_meta), None)

    valid = set(pages)
    all_missing = {}
    for path, (doc, _) in pages.items():
        doc, missing = fix_internal_links(doc, valid)
        for m in missing:
            all_missing.setdefault(m, set()).add(path)
        write(path, doc)

    nf = page(f"Siden findes ikke | {SITE_NAME}", "Siden findes ikke.", "/404.html",
              '<div class="wrap simple"><h1>Siden findes ikke</h1><p class="lead">Adressen er forkert, eller siden er flyttet. '
              'Gå til <a href="/">forsiden</a>, eller vælg et emne i menuen.</p></div>', noindex=True)
    write("404.html", nf)

    today = date.today().isoformat()
    urls = "".join(f"<url><loc>{SITE_URL}{p}</loc><lastmod>{u or today}</lastmod></url>" for p, (_, u) in sorted(pages.items()))
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")

    print(f"Byggede {len(pages)} sider i ./public")
    plan = os.path.join(ROOT, "content", "keywordplan.csv")
    if os.path.exists(plan):
        import csv
        rows = list(csv.DictReader(open(plan, encoding="utf-8")))
        done = sum(1 for r in rows if r["url"] in pages)
        print(f"Keyword-plan: {done} af {len(rows)} planlagte guides er skrevet")
    for slug, w in sorted(report, key=lambda x: -x[1]):
        print(f"  {slug:32s} {w:5d} ord")
    if all_missing:
        print("Interne links til sider, der ikke findes endnu (vist som tekst):")
        for m, src in sorted(all_missing.items()):
            print(f"  {m}  <- {len(src)} side(r)")


if __name__ == "__main__":
    main()
