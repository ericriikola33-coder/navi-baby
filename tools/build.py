#!/usr/bin/env python3
"""Bygger navi.baby: namnsidor, listsidor, infosidor, sitemap och uppdaterar namnlistan i index.html.

Kör från repots rot:  python3 tools/build.py
Namnen ligger i tools/names.txt (namn|kön f/m/u|betydelse|ursprung|stil k/n).
VIKTIGT: lägg bara till nya namn SIST i names.txt – delade länkar bygger på ordningen.
"""
import hashlib, html, json, os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://navi.baby"
CONTACT_EMAIL = "kontakt@navi.baby"
TODAY = datetime.date.today().isoformat()

# ---------- data ----------
NAMES = []
for line in open(os.path.join(ROOT, "tools", "names.txt"), encoding="utf-8"):
    line = line.rstrip("\n")
    if not line.strip():
        continue
    n, g, m, o, s = line.split("|")
    NAMES.append(dict(name=n, g=g, meaning=m, origin=o, style=s))

def slugify(s):
    s = s.lower()
    for a, b in (("å", "a"), ("ä", "a"), ("ö", "o"), ("é", "e"), ("ü", "u")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

for n in NAMES:
    n["slug"] = slugify(n["name"])
slugs = [n["slug"] for n in NAMES]
assert len(slugs) == len(set(slugs)), "dubbla slugs"

ORIGIN = {
    "Fornnordiskt": ("fornnordiskt", "Fornnordiska namn kommer från språket som talades i Norden under vikingatiden och tidig medeltid. Många är sammansatta av två led – ofta ord för gudar, strid, seger, skydd eller djur som örn och varg."),
    "Germanskt": ("germanskt", "Germanska namn har sina rötter hos de germanska folken i Mellaneuropa. Många kom till Sverige under medeltiden och senare genom kontakter med Tyskland."),
    "Hebreiskt": ("hebreiskt", "Hebreiska namn kommer ofta från Bibeln och spreds över Europa tillsammans med kristendomen. Flera av dem innehåller ett ord för Gud."),
    "Grekiskt": ("grekiskt", "Grekiska namn kom till Sverige främst genom kristendomen och helgonnamnen. Många har gamla betydelser kopplade till egenskaper som visdom, renhet eller seger."),
    "Latin": ("latinskt", "Latinska namn kommer från romarnas språk. En del kom till Sverige via kyrkan och helgonkalendern, andra är nyare namn byggda på latinska ord."),
    "Fornengelskt": ("fornengelskt", "Fornengelska namn kommer från det språk som talades i England under tidig medeltid, före den normandiska erövringen."),
    "Svenskt": ("svenskt", "Namnet har formats i Sverige – ofta från ett svenskt ord eller som en svensk form av ett äldre namn."),
    "Engelskt": ("engelskt", "Namnet har kommit till Sverige via engelskan, ofta som kortform eller smeknamnsform av ett längre namn."),
    "Irländskt": ("irländskt", "Irländska namn kommer från iriskan, det keltiska språk som talas på Irland."),
    "Iriskt": ("irländskt", "Irländska namn kommer från iriskan, det keltiska språk som talas på Irland."),
    "Keltiskt": ("keltiskt", "Keltiska namn kommer från de keltiska språken som talades i stora delar av Västeuropa, bland annat på Irland och i Skottland."),
    "Arabiskt": ("arabiskt", "Arabiska namn används i stora delar av världen och bärs av många i Sverige idag."),
    "Italienskt": ("italienskt", "Namnet har sitt ursprung i italienskan."),
    "Franska": ("franskt", "Namnet har sitt ursprung i franskan."),
    "Ryskt": ("ryskt", "Namnet har sitt ursprung i ryskan, där smeknamnsformer ofta blivit egna namn."),
    "Spanskt": ("spanskt", "Namnet har sitt ursprung i spanskan."),
    "Persiskt": ("persiskt", "Namnet har sitt ursprung i persiskan."),
    "Walesiskt": ("walesiskt", "Namnet har sitt ursprung i walesiskan, ett keltiskt språk som talas i Wales."),
    "Turkiskt": ("turkiskt", "Namnet har sitt ursprung i turkiskan."),
    "Slaviskt": ("slaviskt", "Namnet har sitt ursprung i de slaviska språken."),
    "Isländskt": ("isländskt", "Namnet har sitt ursprung i isländskan."),
    "Hawaiiskt": ("hawaiiskt", "Namnet har sitt ursprung i hawaiiskan."),
    "Danskt": ("danskt", "Namnet har sitt ursprung i danskan."),
    "Arameiskt": ("arameiskt", "Namnet har sitt ursprung i arameiskan, ett språk som talades i Mellanöstern under antiken."),
}
G_NOUN = {"f": "flicknamn", "m": "pojknamn", "u": "könsneutralt namn"}
G_LABEL = {"f": "Flicknamn", "m": "Pojknamn", "u": "Könsneutralt"}
S_LABEL = {"k": "Klassiskt", "n": "Modernt"}
DESC_PREFIX = ("kortform", "variant", "smeknamnsform", "svensk form", "nordisk form", "spansk form", "rysk form",
               "rysk smeknamnsform", "arabisk form", "engelsk variant", "irländsk kortform", "form av", "efter",
               "kopplat", "känt", "modernt", "bibliskt", "av den", "personifikationen", "gud i", "gudinna", "titan",
               "kärlekens", "den första", "gudinnan", "romersk gudinna", "ofta kopplat", "smeknamn för", "åskans gud",
               "berättelse")

CATS = [
    # slug, rubrik, kort, filter, intro
    ("flicknamn", "Flicknamn", "klassiska och moderna", lambda n: n["g"] == "f",
     "Här hittar du alla flicknamn på navi.baby – från klassiska namn som Astrid, Ingrid och Märta till moderna namn som Nova, Tindra och Mila. Tryck på ett namn för att läsa om dess betydelse och ursprung, eller swipa namnen tillsammans med din partner för att se vilka ni båda gillar."),
    ("pojknamn", "Pojknamn", "klassiska och moderna", lambda n: n["g"] == "m",
     "Här hittar du alla pojknamn på navi.baby – från klassiska namn som Arvid, Gösta och Hjalmar till moderna namn som Levi, Matteo och Atlas. Tryck på ett namn för betydelse och ursprung, eller swipa namnen tillsammans med din partner."),
    ("konsneutrala-namn", "Könsneutrala namn", "passar alla", lambda n: n["g"] == "u",
     "Könsneutrala namn används av både flickor och pojkar. Många är kortformer av längre namn, som Robin, Charlie och Kim, andra är ord som blivit namn, som River och Sky."),
    ("klassiska-namn", "Klassiska namn", "tidlösa farmors- och farfarsnamn", lambda n: n["style"] == "k",
     "Klassiska namn har en lång historia och en tidlös känsla. Här finns många av de namn som våra far- och morföräldrar bar – som Greta, Dagny, Bertil och Sixten – och som passar lika bra idag."),
    ("moderna-namn", "Moderna namn", "fräscha och samtida", lambda n: n["style"] == "n",
     "Moderna namn har en fräsch och samtida känsla. Här finns både nya namn och gamla namn i ny form – som Nova, Juni, Loke och Ezra."),
    ("nordiska-namn", "Nordiska namn", "från vikingatiden", lambda n: n["origin"] == "Fornnordiskt",
     "Nordiska namn har sina rötter i fornnordiskan, språket som talades i Norden under vikingatiden. Många av dem bär betydelser kopplade till gudar, natur och styrka – som Astrid, Freja, Arvid och Ylva."),
]

# ---------- helpers ----------
e = html.escape

def h(seed):
    return int(hashlib.md5(seed.encode()).hexdigest(), 16)

def pick(pool, k, seed):
    return sorted(pool, key=lambda n: h(seed + n["name"]))[:k]

def meaning_sentence(n):
    m = n["meaning"]
    if m.lower().startswith(DESC_PREFIX):
        return "Bakgrund: " + m[0].upper() + m[1:] + "."
    return "Namnet betyder ”" + m + "”."

def head(title, desc, path, extra=""):
    return f"""<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="only light">
<meta name="darkreader-lock">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="website">
<meta property="og:locale" content="sv_SE">
<meta property="og:site_name" content="navi.baby">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE}/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F6F1EA">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23F6F1EA'/%3E%3Ctext x='29' y='46' font-family='Georgia,serif' font-weight='700' font-size='40' text-anchor='middle' fill='%232B2A28'%3En%3C/text%3E%3Ccircle cx='49' cy='43' r='5' fill='%23D98B7A'/%3E%3C/svg%3E">
<script data-goatcounter="https://navibaby.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
<meta name="google-adsense-account" content="ca-pub-9723217552460349">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9723217552460349" crossorigin="anonymous"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
{extra}</head>
<body>
<header class="top"><div class="wrap">
  <a class="logo" href="/">navi<span>.</span>baby</a>
  <nav><a class="hide-s" href="/flicknamn/">Flicknamn</a><a class="hide-s" href="/pojknamn/">Pojknamn</a><a href="/namn/">Namn</a><a href="/verktyg/">Verktyg</a><a class="cta" href="/">Swipa ♥</a></nav>
</div></header>
<main><div class="wrap">
"""

FOOT = """</div></main>
<footer class="site"><div class="wrap">
  <div class="cols">
    <a href="/">Swipa namn</a><a href="/namn/">Alla namn A–Ö</a>
    <a href="/flicknamn/">Flicknamn</a><a href="/pojknamn/">Pojknamn</a>
    <a href="/konsneutrala-namn/">Könsneutrala namn</a><a href="/nordiska-namn/">Nordiska namn</a>
    <a href="/klassiska-namn/">Klassiska namn</a><a href="/moderna-namn/">Moderna namn</a>
    <a href="/namngenerator/">Namngenerator</a><a href="/syskonnamn/">Syskonnamn</a>
    <a href="/efternamn/">Namn + efternamn</a><a href="/namnquiz/">Namnquiz</a>
    <a href="/om/">Om navi.baby</a><a href="/integritet/">Integritetspolicy</a>
    <a href="/kontakt/">Kontakt</a>
  </div>
  <div class="small">© """ + str(datetime.date.today().year) + """ navi.baby · Hitta namnet ni båda gillar</div>
</div></footer>
</body>
</html>
"""

def breadcrumbs_ld(items):
    return '<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": nm, "item": SITE + p}
                            for i, (nm, p) in enumerate(items)]}, ensure_ascii=False) + "</script>\n"

def poster_svg(n):
    size = 46 if len(n["name"]) > 7 else 56
    ny = 120 if size < 50 else 126
    leaves = ""
    for k, (y, s) in enumerate([(250, -1), (230, 1), (210, -1), (190, 1), (170, -1), (150, 1)]):
        lx, ly = 150 + s * 22, y - 10
        leaves += f'<path d="M150 {y} Q {150+s*8} {y-22} {lx} {ly} Q {150+s*20} {y+4} 150 {y}Z" fill="#C9A27E" opacity="{0.55+k*0.06:.2f}"/>'
    m = n["meaning"]
    m = m[0].upper() + m[1:]
    return f'''<svg viewBox="0 0 300 400" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Namntavla med namnet {e(n["name"])}">
<rect width="300" height="400" fill="#F3EBDF"/><rect x="14" y="14" width="272" height="372" fill="none" stroke="#C9A27E" stroke-width="1" opacity=".6"/>
<g transform="translate(0,6)"><path d="M150 268 C 150 220, 152 180, 150 138" stroke="#C9A27E" stroke-width="2" fill="none" stroke-linecap="round"/>{leaves}<circle cx="150" cy="134" r="4" fill="#C9A27E"/></g>
<text x="150" y="56" text-anchor="middle" font-family="DM Sans, sans-serif" font-size="9" letter-spacing="3" fill="#3B3530" opacity=".7">{e(n["origin"].upper())}</text>
<text x="150" y="{ny}" text-anchor="middle" font-family="Fraunces, serif" font-weight="600" font-size="{size}" fill="#3B3530" letter-spacing="-1">{e(n["name"])}</text>
<line x1="130" y1="300" x2="170" y2="300" stroke="#C9A27E" stroke-width="1.5"/>
<foreignObject x="40" y="310" width="220" height="60"><div xmlns="http://www.w3.org/1999/xhtml" style="font-family:'DM Sans',sans-serif;font-size:11px;line-height:1.45;color:#3B3530;text-align:center;opacity:.85">{e(m)}</div></foreignObject>
</svg>'''

def chips(lst):
    return '<div class="chips">' + "".join(f'<a href="/namn/{x["slug"]}/">{e(x["name"])}</a>' for x in lst) + "</div>"

def write(path, content):
    full = os.path.join(ROOT, path.strip("/"), "index.html") if not path.endswith(".html") and not path.endswith(".xml") and not path.endswith(".txt") else os.path.join(ROOT, path.strip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

def cat_for_gender(g):
    return {"f": ("Flicknamn", "/flicknamn/"), "m": ("Pojknamn", "/pojknamn/"), "u": ("Könsneutrala namn", "/konsneutrala-namn/")}[g]

# ---------- name pages ----------
URLS = ["/"]
for n in NAMES:
    adj, origin_text = ORIGIN[n["origin"]]
    style_word = "klassiskt" if n["style"] == "k" else "modernt"
    cat_name, cat_path = cat_for_gender(n["g"])
    path = f"/namn/{n['slug']}/"
    URLS.append(path)

    same_origin = [x for x in NAMES if x is not n and x["g"] == n["g"] and x["origin"] == n["origin"]]
    same_style = [x for x in NAMES if x is not n and x["g"] == n["g"] and x["style"] == n["style"] and x not in same_origin]
    similar = pick(same_origin, 8, n["name"]) or []
    if len(similar) < 8:
        similar += pick(same_style, 8 - len(similar), n["name"] + "s")
    sib_pool = [x for x in NAMES if x["style"] == n["style"] and (x["g"] != n["g"] if n["g"] != "u" else x["g"] != "u")]
    siblings = pick(sib_pool, 8, n["name"] + "sib")
    same_letter = sorted([x for x in NAMES if x is not n and x["name"][0] == n["name"][0]], key=lambda x: x["name"])[:12]

    style_sentence = ("På navi.baby räknas " + n["name"] + " till de klassiska namnen – namn med lång historia och en tidlös, lite traditionell känsla."
                      if n["style"] == "k" else
                      "På navi.baby räknas " + n["name"] + " till de moderna namnen – namn med en fräsch och samtida känsla.")
    letters = len(n["name"])
    desc = f"{n['name']} är ett {style_word} {G_NOUN[n['g']]} med {adj} ursprung. {meaning_sentence(n)} Se liknande namn och swipa babynamn med din partner."
    title = f"{n['name']} – namnets betydelse och ursprung | navi.baby"
    ld = breadcrumbs_ld([("navi.baby", "/"), (cat_name, cat_path), (n["name"], path)])
    body = f"""<div class="crumbs"><a href="/">navi.baby</a> › <a href="{cat_path}">{cat_name}</a> › {e(n['name'])}</div>
<span class="tag">{G_LABEL[n['g']]}</span><span class="tag">{S_LABEL[n['style']]}</span>
<h1 class="name">{e(n['name'])}</h1>
<p class="lead">{e(n['name'])} är ett {style_word} {G_NOUN[n['g']]} med {adj} ursprung. {e(meaning_sentence(n))}</p>

<div class="facts">
  <div class="fact wide"><b>Betydelse</b><span>{e(n['meaning'][0].upper() + n['meaning'][1:])}</span></div>
  <div class="fact"><b>Ursprung</b><span>{e(adj.capitalize())}</span></div>
  <div class="fact"><b>Kön</b><span>{G_LABEL[n['g']]}</span></div>
  <div class="fact"><b>Stil</b><span>{S_LABEL[n['style']]}</span></div>
  <div class="fact"><b>Bokstäver</b><span>{letters}</span></div>
</div>

<h2>Om namnet {e(n['name'])}</h2>
<p>{e(origin_text)}</p>
<p>{e(style_sentence)}</p>

<div class="box">
  <h2>Ska ni välja namn tillsammans?</h2>
  <p>På navi.baby swipar ni babynamn var för sig – på var sin telefon – och ser sedan bara de namn ni båda gillade. Gratis och utan app.</p>
  <a class="btn" href="/">Börja swipa namn</a>
</div>

<h2>Namn som liknar {e(n['name'])}</h2>
<p class="muted">Andra {cat_name.lower()} med {adj} ursprung eller samma stil.</p>
{chips(similar)}

<h2>Syskonnamn som passar ihop med {e(n['name'])}</h2>
<p class="muted">{'Klassiska' if n['style']=='k' else 'Moderna'} namn i samma stil – för syskon eller som inspiration.</p>
{chips(siblings)}

<h2>{e(n['name'])} som namntavla</h2>
<p>Ett namn på väggen i barnrummet blir en fin detalj. Så här kan en enkel namntavla med {e(n['name'])} se ut:</p>
<div class="poster">{poster_svg(n)}</div>
<p><a class="btn" href="https://riikola.gumroad.com/l/namntavla" target="_blank" rel="noopener" onclick="try{{goatcounter.count({{path:'kop-klick-namnsida',event:true}})}}catch(e){{}}">Köp en namntavla med {e(n['name'])} – 69 kr</a></p>
<p class="muted">Digital fil i tre format (A4/A3, 30×40, 50×70) och fyra färger. Skriv namnet och färgen i kassan – tavlan kommer till din e-post inom 24 timmar.</p>

{'<h2>Fler namn på ' + e(n['name'][0]) + '</h2>' + chips(same_letter) if same_letter else ''}
"""
    write(path, head(title, desc, path, ld) + body + FOOT)

# ---------- list pages ----------
def namelist(lst):
    groups = {}
    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ"
    for x in sorted(lst, key=lambda x: [alpha.index(c) if c in alpha else 100 + ord(c) for c in x["name"].upper()]):
        groups.setdefault(x["name"][0].upper(), []).append(x)
    order = sorted(groups, key=lambda c: "ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ".index(c) if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ" else 99)
    nav = '<div class="letters">' + "".join(f'<a href="#b-{slugify(c) or c}">{c}</a>' for c in order) + "</div>"
    out = nav
    for c in order:
        out += f'<h3 class="letter-h" id="b-{slugify(c) or c}">{c}</h3><ul class="namelist">'
        for x in groups[c]:
            m = x["meaning"]
            out += f'<li><a href="/namn/{x["slug"]}/"><b>{e(x["name"])}</b><small>{e(m[0].upper()+m[1:])} · {e(ORIGIN[x["origin"]][0])}</small></a></li>'
        out += "</ul>"
    return out

for slug, title, short, flt, intro in CATS:
    lst = [n for n in NAMES if flt(n)]
    path = f"/{slug}/"
    URLS.append(path)
    desc = f"{title} med betydelse och ursprung – {len(lst)} namn, {short}. Hitta favoriten och swipa namnen tillsammans med din partner."
    body = f"""<div class="crumbs"><a href="/">navi.baby</a> › {title}</div>
<h1>{title}</h1>
<p class="lead">{e(intro)}</p>
<p class="muted">{len(lst)} namn</p>
<a class="btn alt" href="/">Swipa {title.lower()} med din partner</a>
{namelist(lst)}
"""
    write(path, head(f"{title} – {len(lst)} namn med betydelse | navi.baby", desc, path, breadcrumbs_ld([("navi.baby", "/"), (title, path)])) + body + FOOT)

# all names
path = "/namn/"
URLS.append(path)
cats_html = '<div class="cats">' + "".join(
    f'<a href="/{slug}/"><b>{title}</b><small>{len([n for n in NAMES if flt(n)])} namn · {short}</small></a>' for slug, title, short, flt, _ in CATS) + "</div>"
body = f"""<div class="crumbs"><a href="/">navi.baby</a> › Alla namn</div>
<h1>Alla namn A–Ö</h1>
<p class="lead">Här finns alla {len(NAMES)} namn på navi.baby – med betydelse och ursprung. Välj en kategori eller bläddra i bokstavsordning.</p>
{cats_html}
{namelist(NAMES)}
"""
write(path, head(f"Alla babynamn A–Ö med betydelse – {len(NAMES)} namn | navi.baby",
                 f"Alla {len(NAMES)} babynamn på navi.baby med betydelse och ursprung – flicknamn, pojknamn och könsneutrala namn, klassiska och moderna.",
                 path, breadcrumbs_ld([("navi.baby", "/"), ("Alla namn", path)])) + body + FOOT)

# ---------- info pages ----------
URLS += ["/om/", "/integritet/", "/kontakt/"]
write("/om/", head("Om navi.baby", "navi.baby hjälper blivande föräldrar att hitta ett babynamn som båda gillar.", "/om/") + f"""
<div class="prose">
<h1>Om navi.baby</h1>
<p class="lead">navi.baby är en gratis tjänst för blivande föräldrar som vill hitta ett namn som båda gillar – utan ändlösa diskussioner.</p>
<h2>Så fungerar det</h2>
<p>Ni swipar babynamn var för sig, antingen på var sin telefon via en delad länk eller på samma telefon. Ingen ser den andras svar. När båda är klara visas bara de namn ni båda sa ja till.</p>
<h2>Namnen</h2>
<p>navi.baby innehåller just nu {len(NAMES)} namn – flicknamn, pojknamn och könsneutrala namn, både klassiska och moderna. För varje namn finns en kort beskrivning av betydelse och ursprung. Namnens betydelser är ofta omdiskuterade och kan tolkas på olika sätt; uppgifterna här är en sammanfattning av vanliga tolkningar och ska ses som vägledning.</p>
<h2>Vem står bakom?</h2>
<p>navi.baby är ett fristående projekt skapat i Sverige. Har du förslag på namn som saknas, eller hittat något som är fel? Hör gärna av dig via <a href="/kontakt/">kontaktsidan</a>.</p>
</div>
""" + FOOT)

write("/integritet/", head("Integritetspolicy | navi.baby", "Så hanterar navi.baby dina uppgifter.", "/integritet/") + f"""
<div class="prose">
<h1>Integritetspolicy</h1>
<p class="muted">Senast uppdaterad {TODAY}</p>
<p>Vi vill att du ska kunna använda navi.baby utan att lämna ifrån dig personuppgifter. Här beskriver vi vilka uppgifter som hanteras när du besöker sidan.</p>
<h2>Inget konto, inga cookies från oss</h2>
<p>Du behöver inte skapa något konto. navi.baby sätter inga egna cookies.</p>
<h2>Dina swipar</h2>
<p>Dina svar sparas bara i din egen webbläsare (lokal lagring), så att du kan fortsätta där du var. När du delar en länk med din partner finns svaren inbakade i själva länken, efter tecknet #. Den delen av länken skickas inte till vår server. Den som får länken kan däremot se vilka namn den innehåller, så dela den bara med den du vill.</p>
<h2>Besöksstatistik</h2>
<p>Vi använder GoatCounter för att räkna besök och se vilka delar av sidan som används, till exempel hur många som skapar en delningslänk. GoatCounter använder inga cookies och samlar inte in personuppgifter som namn eller e-post. Statistiken är anonym och används bara för att förbättra sidan.</p>
<h2>Teckensnitt och värdtjänst</h2>
<p>Sidan använder teckensnitt från Google Fonts, vilket innebär att din webbläsare hämtar dem från Googles servrar. Sidan drivs via GitHub Pages. Både Google och GitHub kan, som de flesta webbtjänster, tillfälligt behandla tekniska uppgifter som IP-adress för att leverera innehållet.</p>
<h2>Annonser och cookies</h2>
<p>navi.baby kan visa annonser via Google AdSense. Google och dess partner kan använda cookies för att visa annonser baserat på dina tidigare besök på den här och andra webbplatser. Du kan läsa mer om hur Google använder uppgifter på <a href="https://policies.google.com/technologies/ads">policies.google.com/technologies/ads</a> och välja bort anpassade annonser i Googles <a href="https://adssettings.google.com">annonsinställningar</a>. Besökare i EU/EES får frågan om samtycke innan personanpassade annonser visas.</p>
<h2>Frågor</h2>
<p>Har du frågor om hur uppgifter hanteras? Kontakta oss via <a href="/kontakt/">kontaktsidan</a>.</p>
</div>
""" + FOOT)

contact = (f'<p>Mejla oss på <a href="mailto:{e(CONTACT_EMAIL)}">{e(CONTACT_EMAIL)}</a>. Vi läser allt och svarar så snart vi kan.</p>'
           if CONTACT_EMAIL else
           '<p>En e-postadress för kontakt kommer snart att publiceras här.</p>')
write("/kontakt/", head("Kontakt | navi.baby", "Kontakta navi.baby med frågor, namnförslag eller feedback.", "/kontakt/") + f"""
<div class="prose">
<h1>Kontakt</h1>
<p class="lead">Saknar du ett namn, har du hittat ett fel eller har du en idé om hur navi.baby kan bli bättre? Vi blir glada att höra från dig.</p>
{contact}
</div>
""" + FOOT)

# ---------- tools ----------
with open(os.path.join(ROOT, "assets", "names.js"), "w", encoding="utf-8") as f:
    f.write("const NB = " + json.dumps([[n["name"], n["g"], n["meaning"], n["origin"], n["style"], n["slug"]] for n in NAMES], ensure_ascii=False, separators=(",", ":")) + ";\n")
    f.write("const NB_ORIGIN = " + json.dumps({k: v[0] for k, v in ORIGIN.items()}, ensure_ascii=False) + ";\n")

SCRIPTS = '<script src="/assets/names.js"></script>\n<script src="/assets/tools.js"></script>\n'
CTA = """<div class="box">
  <h2>Hittat några favoriter?</h2>
  <p>Swipa namnen var för sig med din partner och se vilka ni båda gillar.</p>
  <a class="btn" href="/">Börja swipa namn</a>
</div>
"""
def tool_page(path, title, desc, h1, lead, body, script):
    URLS.append(path)
    write(path, head(title, desc, path, breadcrumbs_ld([("navi.baby", "/"), ("Verktyg", "/verktyg/"), (h1, path)]))
          + f'<div class="crumbs"><a href="/">navi.baby</a> › <a href="/verktyg/">Verktyg</a> › {h1}</div>\n<h1>{h1}</h1>\n<p class="lead">{lead}</p>\n'
          + body + CTA + SCRIPTS + "<script>\n" + script + "\n</script>\n" + FOOT)

GSEG = '[["all","Alla"],["f","Flicka"],["m","Pojke"],["u","Neutralt"]]'

tool_page("/namngenerator/", "Namngenerator – slumpa fram ett babynamn | navi.baby",
  "Slumpa fram babynamn med betydelse. Välj flicknamn eller pojknamn, klassiskt eller modernt, nordiskt eller internationellt och max antal bokstäver.",
  "Namngenerator", "Fastnat i namnvalet? Ställ in vad ni gillar och låt slumpen ge er ett förslag – med betydelse och ursprung.",
  """<div class="box tool">
  <label>Kön</label><div class="seg" id="g"></div>
  <label>Stil</label><div class="seg" id="s"></div>
  <label>Ursprung</label><div class="seg" id="o"></div>
  <label>Längd</label><div class="seg" id="len"></div>
  <label for="letter">Börjar på (valfritt)</label><input type="text" id="letter" maxlength="1" placeholder="T.ex. A" autocomplete="off">
  <button class="btn full" id="go">🎲 Ge mig ett namn</button>
  <p class="note" id="count"></p>
</div>
<div id="out"></div>
""", """const st = {g:"all", s:"all", o:"all", len:"all"};
let queue = [];
function pool(){
  const L = $("letter").value.trim().toUpperCase();
  return NB.filter(n => (st.g==="all" || n[1]===st.g) && (st.s==="all" || n[4]===st.s)
    && (st.o==="all" || (st.o==="nord") === NB_NORDIC.includes(n[3]))
    && (st.len==="all" || n[0].length <= +st.len) && (!L || n[0].toUpperCase().startsWith(L)));
}
function reset(){ queue = []; const c = pool().length; $("count").textContent = c + (c===1 ? " namn matchar dina val" : " namn matchar dina val"); }
nbSeg("g", """ + GSEG + """, st, "g", reset);
nbSeg("s", [["all","Alla"],["k","Klassiskt"],["n","Modernt"]], st, "s", reset);
nbSeg("o", [["all","Alla"],["nord","Nordiskt"],["intl","Internationellt"]], st, "o", reset);
nbSeg("len", [["all","Alla"],["4","Max 4"],["5","Max 5"],["6","Max 6"]], st, "len", reset);
$("letter").addEventListener("input", reset);
function go(){
  if(!queue.length) queue = nbShuffle(pool());
  if(!queue.length){ $("out").innerHTML = '<div class="bigcard"><p>Inga namn matchar de valen. Prova att ändra något.</p></div>'; return; }
  const n = queue.pop();
  $("out").innerHTML = `<div class="bigcard"><span class="tag">${{f:"Flicknamn",m:"Pojknamn",u:"Könsneutralt"}[n[1]]}</span><span class="tag">${n[4]==="k"?"Klassiskt":"Modernt"}</span>
    <div class="bn">${n[0]}</div><p>${nbCap(n[2])}</p><p>Ursprung: ${NB_ORIGIN[n[3]]}</p>
    <p><a class="btn alt" href="/namn/${n[5]}/">Läs mer om ${n[0]}</a></p></div>`;
  $("go").textContent = "🎲 Ett namn till";
  nbTrack("verktyg-generator");
}
$("go").onclick = go; reset();""")

tool_page("/syskonnamn/", "Syskonnamn – hitta namn som passar ihop | navi.baby",
  "Skriv in storasyskonets namn och få förslag på syskonnamn i samma stil, med betydelse och ursprung.",
  "Syskonnamn", "Ska bebisen få ett namn som passar ihop med storasyskonets? Skriv in namnet så föreslår vi syskonnamn i samma stil.",
  """<div class="box tool">
  <label for="sib">Storasyskonets namn</label><input type="text" id="sib" placeholder="T.ex. Astrid" autocomplete="off">
  <label>Bebisen är</label><div class="seg" id="g"></div>
  <label>Stil</label><div class="seg" id="s"></div>
  <button class="btn full" id="go">Visa syskonnamn</button>
</div>
<div id="out"></div>
""", """const st = {g:"all", s:"auto"};
nbSeg("g", """ + GSEG.replace('"Alla"', '"Vet inte"') + """, st, "g");
nbSeg("s", [["auto","Samma stil"],["k","Klassiskt"],["n","Modernt"]], st, "s");
function go(){
  const q = $("sib").value.trim();
  if(!q){ $("out").innerHTML = '<p class="note">Skriv in ett namn först.</p>'; return; }
  const ql = q.toLowerCase(), base = NB.find(n => n[0].toLowerCase() === ql);
  const style = st.s !== "auto" ? st.s : (base ? base[4] : null);
  const sy = nbSyll(q), shown = nbEsc(nbCap(q));
  const top = NB.filter(n => n[0].toLowerCase() !== ql && (st.g==="all" || n[1]===st.g)).map(n => {
    let p = Math.random()*1.5;
    if(style && n[4]===style) p += 3;
    if(base && n[3]===base[3]) p += 2;
    if(Math.abs(n[0].length - q.length) <= 1) p += 1;
    if(nbSyll(n[0]) === sy) p += 1;
    if(n[0][0].toLowerCase() === ql[0]) p -= 1.5;
    if(n[0].slice(-2).toLowerCase() === ql.slice(-2)) p -= 1;
    return [p, n];
  }).sort((a,b) => b[0]-a[0]).slice(0, 12).map(x => x[1]);
  const intro = base
    ? `${base[0]} är ett ${base[4]==="k"?"klassiskt":"modernt"} namn med ${NB_ORIGIN[base[3]]} ursprung. Här är namn som passar ihop:`
    : `Vi har inte ${shown} i vår namnlista ännu, så förslagen bygger på namnets längd och rytm. Välj gärna stil ovan för bättre träffar.`;
  $("out").innerHTML = `<p class="note">${intro}</p><ul class="namelist">` +
    top.map(n => nbItem(n, n[0], shown + " & " + n[0] + " · " + n[2])).join("") + "</ul>";
  $("go").textContent = "Visa fler förslag";
  nbTrack("verktyg-syskonnamn");
}
$("go").onclick = go;
$("sib").addEventListener("keydown", e => { if(e.key === "Enter") go(); });""")

tool_page("/efternamn/", "Namn som passar till efternamnet | navi.baby",
  "Skriv in ert efternamn och se hur babynamn ser ut och låter tillsammans med det – med initialer och förslag som har bra rytm.",
  "Namn + efternamn", "Hur låter namnet ihop med efternamnet? Skriv in det så visar vi förslag med bra rytm och klang – och vilka initialer det blir.",
  """<div class="box tool">
  <label for="sn">Efternamn</label><input type="text" id="sn" placeholder="T.ex. Lindberg" autocomplete="off">
  <label>Kön</label><div class="seg" id="g"></div>
  <label>Stil</label><div class="seg" id="s"></div>
  <button class="btn full" id="go">Visa förslag</button>
  <p class="note">Efternamnet stannar i din webbläsare och sparas inte.</p>
</div>
<div id="out"></div>
<h2>Så väljer vi förslagen</h2>
<p>Ett för- och efternamn brukar låta bäst när de har olika antal stavelser, när förnamnet inte slutar på samma ljud som efternamnet börjar med och när de inte rimmar. Förslagen här följer de tumreglerna – men det viktigaste är förstås att ni själva säger namnet högt och känner efter.</p>
""", """const st = {g:"all", s:"all"};
nbSeg("g", """ + GSEG + """, st, "g");
nbSeg("s", [["all","Alla"],["k","Klassiskt"],["n","Modernt"]], st, "s");
const V = "aeiouyåäö";
function go(){
  const raw = $("sn").value.trim();
  if(!raw){ $("out").innerHTML = '<p class="note">Skriv in ett efternamn först.</p>'; return; }
  const sn = nbCap(raw), sl = sn.toLowerCase(), ss = nbSyll(sn), shown = nbEsc(sn);
  const top = NB.filter(n => (st.g==="all" || n[1]===st.g) && (st.s==="all" || n[4]===st.s)).map(n => {
    const f = n[0].toLowerCase(), fs = nbSyll(f);
    let p = Math.random()*1.5;
    if(fs !== ss) p += 2;
    if(f.slice(-1) === sl[0]) p -= 3;
    else if(V.includes(f.slice(-1)) && V.includes(sl[0])) p -= 1.5;
    if(f.slice(-2) === sl.slice(-2)) p -= 2;
    if(ss >= 3 && fs <= 2) p += 1;
    if(ss === 1 && fs >= 2) p += 1;
    return [p, n, fs];
  }).sort((a,b) => b[0]-a[0]).slice(0, 12);
  if(!top.length){ $("out").innerHTML = '<p class="note">Inga namn matchar de valen.</p>'; return; }
  $("out").innerHTML = `<p class="note">Förslag som har bra rytm ihop med ${shown}:</p><ul class="namelist">` +
    top.map(([p,n,fs]) => nbItem(n, n[0] + " " + shown, "Initialer " + n[0][0] + "." + shown[0] + ". · " + fs + " + " + ss + " stavelser · " + n[2])).join("") + "</ul>";
  $("go").textContent = "Visa fler förslag";
  nbTrack("verktyg-efternamn");
}
$("go").onclick = go;
$("sn").addEventListener("keydown", e => { if(e.key === "Enter") go(); });""")

tool_page("/namnquiz/", "Namnquiz – vilken namnstil är ni? | navi.baby",
  "Svara på fem snabba frågor och få veta vilken namnstil ni har – plus tio babynamn som passar er.",
  "Namnquiz: vilken namnstil är ni?", "Fem snabba frågor. Sedan får ni er namnstil och tio namn som passar den.",
  """<div id="quiz"></div>
""", """const Q = [
  ["Vem väntar ni?", [["En flicka", {g:"f"}], ["En pojke", {g:"m"}], ["Vet inte än – eller så spelar det ingen roll", {g:"all"}]]],
  ["Hur ser drömhelgen ut?", [["Stuga i skogen, brasa och stickade sockor", {grp:"nord"}], ["Storstad, caféer och nya smaker", {grp:"intl"}], ["Söndagsmiddag med hela släkten", {grp:"trad"}]]],
  ["Vilket hem känns mest som ert?", [["Ärvda möbler och loppisfynd", {s:"k"}], ["Ljust, stilrent och nytt", {s:"n"}], ["En salig blandning", {s:"all"}]]],
  ["Namnet ska helst vara …", [["Kort och enkelt", {len:"short"}], ["Långt och melodiskt", {len:"long"}], ["Det spelar ingen roll", {len:"all"}]]],
  ["Ska namnet fungera utomlands?", [["Ja, det är viktigt", {abroad:"yes"}], ["Nej, gärna riktigt svenskt", {abroad:"no"}], ["Det spelar ingen roll", {abroad:"all"}]]]
];
const TRAD = ["Hebreiskt","Grekiskt","Latin","Germanskt"];
const LABEL = {
  nord:{k:"Nordisk klassiker", n:"Modern nordisk", all:"Nordisk själ"},
  intl:{k:"Tidlös världsmedborgare", n:"Modern världsmedborgare", all:"Världsmedborgare"},
  trad:{k:"Varm traditionalist", n:"Modern med rötter", all:"Traditionalist"}
};
const TEXT = {
  nord:"Ni dras till namn med rötter i Norden – namn som bär på natur, styrka och gamla berättelser.",
  intl:"Ni gillar namn som känns hemma var som helst i världen och som är lätta att uttala på många språk.",
  trad:"Ni uppskattar namn med lång historia – namn som funnits i generationer och som aldrig går ur tiden."
};
let i = 0, a = {};
function show(){
  if(i >= Q.length) return result();
  const [q, opts] = Q[i];
  $("quiz").innerHTML = `<div class="box"><p class="muted">Fråga ${i+1} av ${Q.length}</p><div class="qbar"><i style="width:${i/Q.length*100}%"></i></div>
    <h2>${q}</h2><div class="qopts">${opts.map((o,k) => `<button data-k="${k}">${o[0]}</button>`).join("")}</div></div>`;
  $("quiz").querySelectorAll("button").forEach(b => b.onclick = () => { Object.assign(a, opts[+b.dataset.k][1]); i++; show(); });
}
function result(){
  const top = NB.filter(n => a.g==="all" || n[1]===a.g).map(n => {
    let p = Math.random();
    const nord = NB_NORDIC.includes(n[3]), sv = /[åäö]/i.test(n[0]);
    if(a.grp==="nord" && nord) p += 3;
    if(a.grp==="trad" && TRAD.includes(n[3])) p += 3;
    if(a.grp==="intl" && !nord) p += TRAD.includes(n[3]) ? 1.5 : 3;
    if(a.s!=="all" && n[4]===a.s) p += 3;
    if(a.len==="short") p += n[0].length<=4 ? 2 : n[0].length===5 ? 1 : 0;
    if(a.len==="long" && n[0].length>=6) p += 2;
    if(a.abroad==="yes" && sv) p -= 3;
    if(a.abroad==="no") p += (sv ? 1 : 0) + (nord ? 1 : 0);
    return [p, n];
  }).sort((x,y) => y[0]-x[0]).slice(0, 10).map(x => x[1]);
  const label = LABEL[a.grp][a.s];
  $("quiz").innerHTML = `<div class="bigcard"><p>Er namnstil är</p><div class="bn" style="font-size:40px">${label}</div><p>${TEXT[a.grp]}</p>
    <p><button class="btn alt" id="share" hidden>Dela resultatet</button></p></div>
    <h2>Tio namn som passar er</h2><ul class="namelist">${top.map(n => nbItem(n)).join("")}</ul>
    <p><button class="btn alt" id="again">Gör om quizet</button></p>`;
  $("again").onclick = () => { i = 0; a = {}; show(); window.scrollTo(0,0); };
  try{ if(navigator.share){ $("share").hidden = false; $("share").onclick = () => navigator.share({title:"Namnquiz – navi.baby", text:"Vår namnstil är ”" + label + "”. Vilken är er?", url:"https://navi.baby/namnquiz/"}).catch(()=>{}); } }catch(e){}
  nbTrack("verktyg-quiz-klar"); window.scrollTo(0,0);
}
show();""")

URLS.append("/verktyg/")
write("/verktyg/", head("Namnverktyg – generator, syskonnamn och quiz | navi.baby",
  "Gratis verktyg för att hitta babynamn: swipa med din partner, slumpa namn, hitta syskonnamn, testa namn med efternamnet och gör namnquizet.", "/verktyg/",
  breadcrumbs_ld([("navi.baby", "/"), ("Verktyg", "/verktyg/")])) + """<div class="crumbs"><a href="/">navi.baby</a> › Verktyg</div>
<h1>Namnverktyg</h1>
<p class="lead">Fem sätt att hitta inspiration till babynamnet. Allt är gratis och fungerar direkt i mobilen, utan konto.</p>
<div class="cats" style="grid-template-columns:1fr">
  <a href="/"><b>💞 Swipa namn tillsammans</b><small>Swipa var för sig och se bara namnen ni båda gillar.</small></a>
  <a href="/namngenerator/"><b>🎲 Namngenerator</b><small>Ställ in stil, ursprung och längd – och låt slumpen ge er ett namn.</small></a>
  <a href="/syskonnamn/"><b>👫 Syskonnamn</b><small>Skriv in storasyskonets namn och få förslag i samma stil.</small></a>
  <a href="/efternamn/"><b>✍️ Namn + efternamn</b><small>Se hur namnen låter med ert efternamn, och vilka initialer det blir.</small></a>
  <a href="/namnquiz/"><b>✨ Namnquiz</b><small>Fem frågor som avslöjar er namnstil och ger tio passande namn.</small></a>
</div>
""" + FOOT)

# 404
write("/404.html", head("Sidan hittades inte | navi.baby", "Sidan finns inte.", "/404.html") + """
<h1>Hoppsan – sidan finns inte</h1>
<p class="lead">Länken kan vara fel eller så har sidan flyttats.</p>
<p><a class="btn" href="/">Till startsidan</a> &nbsp; <a class="btn alt" href="/namn/">Alla namn</a></p>
""" + FOOT)

# sitemap + robots
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u in URLS:
    sm += f"  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod></url>\n"
sm += "</urlset>\n"
write("/sitemap.xml", sm)
write("/ads.txt", "google.com, pub-9723217552460349, DIRECT, f08c47fec0942fa0\n")
write("/robots.txt", f"User-agent: *\nAllow: /\nDisallow: /tools/\n\nSitemap: {SITE}/sitemap.xml\n")

# ---------- index.html: update NAMES + static section ----------
idx_path = os.path.join(ROOT, "index.html")
idx = open(idx_path, encoding="utf-8").read()
arr = "const NAMES = [\n" + ",\n".join("  " + json.dumps([n["name"], n["g"], n["meaning"], n["origin"], n["style"]], ensure_ascii=False) for n in NAMES) + "\n];"
idx, k = re.subn(r"const NAMES = \[\n.*?\n\];", lambda mm: arr, idx, count=1, flags=re.S)
assert k == 1
open(idx_path, "w", encoding="utf-8").write(idx)

print(f"Klart: {len(NAMES)} namnsidor, {len(URLS)} URL:er i sitemap")
