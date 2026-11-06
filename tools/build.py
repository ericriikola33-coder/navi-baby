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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
{extra}</head>
<body>
<header class="top"><div class="wrap">
  <a class="logo" href="/">navi<span>.</span>baby</a>
  <nav><a class="hide-s" href="/flicknamn/">Flicknamn</a><a class="hide-s" href="/pojknamn/">Pojknamn</a><a href="/namn/">Alla namn</a><a class="cta" href="/">Swipa ♥</a></nav>
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
<h2>Annonser</h2>
<p>Om vi i framtiden visar annonser kommer denna policy att uppdateras, och du kommer att få möjlighet att ge eller neka samtycke innan några annonscookies används.</p>
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
write("/robots.txt", f"User-agent: *\nAllow: /\nDisallow: /tools/\n\nSitemap: {SITE}/sitemap.xml\n")

# ---------- index.html: update NAMES + static section ----------
idx_path = os.path.join(ROOT, "index.html")
idx = open(idx_path, encoding="utf-8").read()
arr = "const NAMES = [\n" + ",\n".join("  " + json.dumps([n["name"], n["g"], n["meaning"], n["origin"], n["style"]], ensure_ascii=False) for n in NAMES) + "\n];"
idx, k = re.subn(r"const NAMES = \[\n.*?\n\];", lambda mm: arr, idx, count=1, flags=re.S)
assert k == 1
open(idx_path, "w", encoding="utf-8").write(idx)

print(f"Klart: {len(NAMES)} namnsidor, {len(URLS)} URL:er i sitemap")
