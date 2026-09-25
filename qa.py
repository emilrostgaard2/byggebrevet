#!/usr/bin/env python3
"""Kvalitetskontrol af det byggede site i ./public. Kør efter python build.py."""
import glob, html, json, os, re, collections, itertools
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(ROOT, "public")
VALID_TARGETS = {
    "tagrenovering", "vinduer", "varmepumpe-luft-til-vand", "dortelefonanlaeg", "facaderenovering",
    "faldstammerenovering", "vedligeholdelsesplaner", "altaner", "opgang", "badevaerelse", "totalentreprise",
    "tilbygning", "omfangsdraen", "omfugning", "ejendomsservice", "solceller", "malere", "facademaling",
    "jordvarme", "carport-garage", "belaegning", "varmepumper", "regnvandsanlaeg", "anlaeg", "kloak",
    "strompeforing", "tv-inspektion", "skimmelsvamp", "gartner", "bygherreraadgivning", "isolering",
    "loftisolering", "hulmursisolering", "gulvarbejde", "hegn", "fundament", "vandskade", "haandvaerker",
    "byggetilbud", "tilstandsrapport", "vvs", "energimaerke", "eltjek", "byggesagkyndig", "glarmester",
    "elektriker", "murer", "toemrer", "sandblaesning", "udestue", "algerens", "tagmaling", "nedrivning",
    "asbest", "handyman"}

issues = collections.defaultdict(list)
titles, descs = {}, {}
pages = sorted(glob.glob(os.path.join(PUB, "**", "*.html"), recursive=True))
existing = set()
for f in pages:
    rel = "/" + os.path.relpath(f, PUB).replace("index.html", "")
    existing.add(rel)

aff_count = 0
for f in pages:
    rel = "/" + os.path.relpath(f, PUB).replace("index.html", "")
    raw = open(f, "rb").read()
    try:
        doc = raw.decode("utf-8")
    except UnicodeDecodeError:
        issues["Ugyldig UTF-8"].append(rel); continue
    if re.search("Ã|Â|\ufffd", doc):
        issues["Tegnfejl (mojibake)"].append(rel)

    h1 = re.findall(r"<h1[ >]", doc)
    if len(h1) != 1 and not rel.endswith("404.html"):
        issues["Antal H1 ≠ 1"].append(f"{rel} ({len(h1)})")

    t = re.search(r"<title>(.*?)</title>", doc)
    d = re.search(r'<meta name="description" content="(.*?)">', doc)
    if t:
        tt = html.unescape(t.group(1)); titles.setdefault(tt, []).append(rel)
        if len(tt) > 65: issues["Titel over 65 tegn"].append(f"{rel} ({len(tt)})")
    else:
        issues["Mangler titel"].append(rel)
    if d:
        dd = html.unescape(d.group(1)); descs.setdefault(dd, []).append(rel)
        if not 70 <= len(dd) <= 160 and not rel.endswith("404.html"): issues["Meta description udenfor 70–160 tegn"].append(f"{rel} ({len(dd)})")
    else:
        issues["Mangler meta description"].append(rel)

    # Overskriftsstruktur: ingen spring fra h2 til h4, ingen h3 før første h2 i artiklen
    prose = re.search(r'<div class="prose">(.*?)</div>\s*(<section|</div>)', doc, re.S)
    if prose:
        levels = [int(x) for x in re.findall(r"<h([2-6])", prose.group(1))]
        prev = 1
        for lv in levels:
            if lv > prev + 1:
                issues["Spring i overskriftsniveau"].append(rel); break
            prev = lv

    # Affiliate-links
    for tag in re.findall(r'<a\b[^>]*partner-ads\.com[^>]*>', doc):
        href = re.search(r'href="([^"]+)"', tag).group(1); attrs = tag
        aff_count += 1
        url = html.unescape(href)
        q = parse_qs(urlparse(url).query)
        if q.get("partnerid") != ["29233"] or q.get("bannerid") != ["25692"]:
            issues["Forkert partner- eller banner-id"].append(rel)
        target = url.split("htmlurl=")[-1]
        m = re.match(r"https://www\.3byggetilbud\.dk/tilbud/([a-z0-9-]+)/$", target)
        if not m or m.group(1) not in VALID_TARGETS:
            issues["Ugyldigt affiliate-mål"].append(f"{rel} -> {target}")
        if 'rel="sponsored nofollow noopener"' not in attrs:
            issues["Affiliate-link mangler rel=sponsored"].append(rel)
    # Affiliate i prisfinder-JSON
    fj = re.search(r'<script id="finder-data" type="application/json">(.*?)</script>', doc, re.S)
    if fj:
        for k, v in json.loads(fj.group(1)).items():
            tgt = v["aff"].split("htmlurl=")[-1]
            m = re.match(r"https://www\.3byggetilbud\.dk/tilbud/([a-z0-9-]+)/$", tgt)
            if not m or m.group(1) not in VALID_TARGETS:
                issues["Ugyldigt mål i prisfinder"].append(f"{k} -> {tgt}")

    # Interne links og ankre
    ids = set(re.findall(r'id="([^"]+)"', doc))
    for href in re.findall(r'href="(/[^"]*)"', doc):
        path, _, frag = href.partition("#")
        if path.startswith("/static/") or path in ("/favicon.svg", "/favicon.ico", "/apple-touch-icon.png"):
            continue
        if path and path not in existing:
            issues["Døde interne links"].append(f"{rel} -> {href}")
    for frag in re.findall(r'href="#([^"]+)"', doc):
        if frag not in ids:
            issues["Døde ankre"].append(f"{rel} -> #{frag}")

    # Schema skal kunne parses
    for js in re.findall(r'<script type="application/ld\+json">(.*?)</script>', doc, re.S):
        try: json.loads(js)
        except Exception: issues["Ugyldig JSON-LD"].append(rel)

    # Typografi
    text = re.sub(r"<script.*?</script>", "", doc, flags=re.S)
    text = re.sub(r"</?(a|strong|em|span|abbr)\b[^>]*>", "", text)
    text = re.sub(r"<[^>]+>", " ", text)
    if re.search(r"\w ,|\.\.(?!\.)| \.", html.unescape(text)):
        issues["Tegnsætningsfejl"].append(rel)

for t, lst in titles.items():
    if len(lst) > 1: issues["Dublet-titel"].append(f"{t}: {lst}")
for d, lst in descs.items():
    if len(lst) > 1: issues["Dublet-description"].append(f"{lst}")

# Gentagne sætninger på tværs af guides (ekskl. faste bokse)
sent_pages = collections.defaultdict(set)
for f in glob.glob(os.path.join(ROOT, "content", "guides", "*.md")):
    body = open(f, encoding="utf-8").read().split("---", 2)[2]
    body = body.split("## Kilder og videre læsning")[0]
    for s in re.split(r"(?<=[.!?])\s+|\n", body):
        s = s.strip()
        if len(s.split()) >= 10 and not s.startswith("|"):
            sent_pages[s].add(os.path.basename(f))
dups = {s: p for s, p in sent_pages.items() if len(p) >= 3}
for s, p in sorted(dups.items(), key=lambda x: -len(x[1]))[:15]:
    issues["Sætning gentaget i 3+ guides"].append(f"{len(p)}× {s[:90]}")

print(f"Sider kontrolleret: {len(pages)}   Affiliate-links: {aff_count}")
if not issues:
    print("Ingen fejl fundet.")
for k, v in issues.items():
    print(f"\n{k}: {len(v)}")
    for x in v[:12]:
        print("   ", x)

# ------------------------------------------------ INDHOLDSKONTROL PR. GUIDE
print("\nIndholdskontrol pr. guide:")
content_issues = []
for f in sorted(glob.glob(os.path.join(ROOT, "content", "guides", "*.md"))):
    slug = os.path.basename(f)[:-3]
    raw = open(f, encoding="utf-8").read()
    body = raw.split("---", 2)[2]
    main = body.split("## Ofte stillede spørgsmål")[0]
    tables = len(re.findall(r"^\|---", body, re.M))
    price_table = bool(re.search(r"^\|.*(pris|Pris).*\|", body, re.M))
    howto = bool(re.search(r"^## .*(Sådan|Proces|forløber|gør du|Tjekliste|De første timer)", body, re.M | re.I))
    steps = bool(re.search(r"^1\. ", body, re.M))
    links = set(re.findall(r"\]\((/[^)]+)\)", main))
    faq = len(re.findall(r"^### ", body.split("## Ofte stillede spørgsmål")[-1].split("## Kilder")[0], re.M))
    sources = "## Kilder og videre læsning" in body
    ctas = body.count("[[cta")
    kort = "**Kort fortalt:**" in body
    fejl = []
    if tables < 2: fejl.append(f"kun {tables} tabel(ler)")
    if not price_table: fejl.append("ingen pristabel")
    if not (howto and steps): fejl.append("mangler sådan-gør-du-trin")
    if len(links) < 4: fejl.append(f"kun {len(links)} interne links i teksten")
    if faq < 5: fejl.append(f"kun {faq} FAQ")
    if not sources: fejl.append("ingen kilder")
    if ctas < 2: fejl.append("under 2 CTA'er")
    if not kort: fejl.append("mangler Kort fortalt")
    if fejl: content_issues.append(f"{slug}: {', '.join(fejl)}")
print("  Alle guides opfylder indholdskravene." if not content_issues else "\n".join("  " + c for c in content_issues))
