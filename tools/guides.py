# Guider – körs från build.py med exec, har tillgång till head, write, FOOT, URLS, e, NAMES, BY_NAME, breadcrumbs_ld
GUIDES = []

def guide(slug, title, desc, h1, lead, body_html):
    path = f"/guider/{slug}/"
    URLS.append(path)
    GUIDES.append((path, h1, desc))
    ld = breadcrumbs_ld([("navi.baby", "/"), ("Guider", "/guider/"), (h1, path)])
    ld += '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": h1,
        "description": desc, "inLanguage": "sv", "dateModified": TODAY, "publisher": {"@type": "Organization", "name": "navi.baby"}},
        ensure_ascii=False) + "</script>\n"
    write(path, head(title, desc, path, ld) + f'''<div class="crumbs"><a href="/">navi.baby</a> › <a href="/guider/">Guider</a> › {h1}</div>
<article class="prose">
<h1>{h1}</h1>
<p class="lead">{lead}</p>
<p class="muted">Uppdaterad {TODAY}</p>
{body_html}
</article>
<div class="box">
  <h2>Redo att hitta namnet?</h2>
  <p>Swipa babynamn var för sig på navi.baby och se bara de namn ni båda gillar.</p>
  <a class="btn" href="/">Börja swipa namn</a>
</div>
''' + FOOT)

def nl(*names):
    return ", ".join(name_link(x) for x in names)

guide("regler-for-namn", "Regler för förnamn i Sverige – så funkar det | navi.baby",
  "Vilka namn får man ge sitt barn i Sverige? Här är reglerna för förnamn och efternamn, hur ansökan går till och vad som händer om ni inte hinner bestämma er.",
  "Regler för förnamn i Sverige",
  "I Sverige är det Skatteverket som registrerar barnets namn. Här går vi igenom vad som gäller – från tidsgränser till vilka namn som inte godkänns.",
  """<h2>Ni har tre månader på er</h2>
<p>När barnets födelse har registrerats skickar Skatteverket en blankett hem till den som har fött barnet. På den fyller vårdnadshavarna i barnets förnamn och efternamn. Ansökan ska vara inne inom tre månader från födseln, och den första ansökan om namn för barnet är gratis.</p>
<p>Om ni inte har skickat in förnamn inom tre månader får ni påminnelser. Kommer ingen ansökan alls kan Skatteverket ta ut en avgift, ett så kallat vite. Det lönar sig alltså att börja fundera i god tid – men tre månader räcker gott för de flesta.</p>

<h2>Hur många förnamn får barnet ha?</h2>
<p>Barnet måste ha minst ett förnamn. Det finns ingen övre gräns för hur många förnamn barnet kan få, så det går bra att ge barnet både sitt eget namn och några släktnamn.</p>

<h2>Vilka namn godkänns inte?</h2>
<p>Skatteverket godkänner inte namn som</p>
<ul>
<li>kan leda till obehag för den som ska bära namnet,</li>
<li>kan uppfattas som stötande av andra, eller</li>
<li>är olämpliga av någon annan anledning – till exempel om namnet är för likt ett efternamn eller innehåller siffror.</li>
</ul>
<p>Skatteverket gör en bedömning i varje enskilt fall. Det finns också en lista över vilka specialtecken som kan registreras, så ett ovanligt stavat namn kan fungera även om det innehåller tecken som inte finns i det svenska alfabetet.</p>

<h2>Får man välja ett namn som traditionellt hör till ett annat kön?</h2>
<p>Ja. Det går bra att ge barnet ett förnamn som traditionellt förknippas med det andra könet. På navi.baby hittar ni dessutom en hel lista med <a href="/konsneutrala-namn/">könsneutrala namn</a>, som Robin, Charlie och Kim.</p>

<h2>Om namnet inte godkänns</h2>
<p>Om Skatteverket säger nej till ett namn får ni ett beslut där det står varför. Beslutet går att överklaga. Ärendena handläggs i den ordning de kommer in, och det kan ta några veckor innan en handläggare tittar på er ansökan.</p>

<h2>Efternamnet</h2>
<p>Barnets efternamn söker ni om på samma blankett. Om ni inte ansöker om efternamn inom tre månader får barnet samma efternamn som den förälder som har fött barnet. Det går att byta efternamn senare. Fundera gärna på hur förnamnet låter ihop med efternamnet – vårt verktyg <a href="/efternamn/">Namn + efternamn</a> kan hjälpa till.</p>

<h2>Byta namn senare</h2>
<p>Den som vill lägga till, byta eller ta bort ett förnamn längre fram kan ansöka om det hos Skatteverket. Den första ansökan för ett nyfött barn är gratis, men senare namnbyten kostar en avgift.</p>

<h2>Källor</h2>
<p class="muted">Uppgifterna kommer från Skatteverket. Reglerna kan ändras, så kontrollera alltid det senaste på <a href="https://skatteverket.se/privat/folkbokforing/namn/ansokomnamnforettnyfottbarn" rel="noopener">skatteverket.se</a> innan ni skickar in er ansökan. Den här texten är en sammanfattning och inte juridisk rådgivning.</p>
""")

guide("valja-namn-tillsammans", "Så väljer ni babynamn tillsammans – 9 tips | navi.baby",
  "Svårt att enas om babynamnet? Nio praktiska tips för att hitta ett namn ni båda älskar – utan att bråka.",
  "Så väljer ni babynamn tillsammans",
  "Att välja namn är roligt – tills man inte är överens. Här är nio tips som gör det lättare att hitta ett namn ni båda verkligen gillar.",
  """<h2>1. Börja var för sig</h2>
<p>Gör varsin lista innan ni jämför. Då slipper ni påverka varandra, och ni ser direkt var era smaker möts. Det är precis så swipen på navi.baby fungerar: ni swipar på varsin telefon och ser bara de namn ni båda gillade.</p>

<h2>2. Prata om känslan, inte bara om namnen</h2>
<p>Ofta handlar oenigheten mer om stil än om enskilda namn. Vill ni ha något klassiskt eller modernt? Nordiskt eller internationellt? Kort eller långt? Gör gärna vårt <a href="/namnquiz/">namnquiz</a> var för sig och jämför resultaten.</p>

<h2>3. Ge varandra vetorätt</h2>
<p>Bestäm att båda får säga nej till ett namn utan att behöva förklara varför. Det låter hårt men gör samtalet mycket enklare – ingen behöver försvara sina favoriter i timmar.</p>

<h2>4. Säg namnet högt – många gånger</h2>
<p>Ropa det som om ni stod på en lekplats, säg det som om ni skulle presentera barnet, viska det som en godnattsaga. Ett namn som ser fint ut på papper kan låta annorlunda i vardagen.</p>

<h2>5. Testa med efternamnet</h2>
<p>Hur låter för- och efternamnet ihop? Brukar namnet flyta ihop med efternamnet, eller bildas det oväntade ord? Titta också på initialerna. Vårt verktyg <a href="/efternamn/">Namn + efternamn</a> visar förslag med bra rytm.</p>

<h2>6. Tänk på smeknamnen</h2>
<p>De flesta namn får ett smeknamn förr eller senare. Gustav blir ofta Gurra, Ludvig blir Ludde och Nils blir Nisse. Gillar ni smeknamnet också?</p>

<h2>7. Fundera på syskon</h2>
<p>Har ni redan barn, eller vill ni ha fler? Det kan vara fint om syskonens namn passar ihop i stil utan att vara för lika. Prova verktyget <a href="/syskonnamn/">Syskonnamn</a>.</p>

<h2>8. Vänta med att berätta</h2>
<p>Så fort namnet är ute kommer alla att ha åsikter. Många par väljer att hålla namnet hemligt tills barnet är fött – då är det lättare att stå fast vid sitt val.</p>

<h2>9. Ta det lugnt – ni har tid</h2>
<p>I Sverige har ni tre månader efter födseln på er att ansöka om namn hos Skatteverket. Många bestämmer sig först när de har träffat barnet. Läs mer i vår guide om <a href="/guider/regler-for-namn/">regler för förnamn i Sverige</a>.</p>
""")

guide("nordiska-namn", "Nordiska namn – så hittar du betydelsen | navi.baby",
  "Många nordiska namn är byggda av samma små ord: gud, seger, örn, varg och sten. Lär dig de vanligaste namnleden och förstå vad namnen betyder.",
  "Nordiska namn och deras betydelser",
  "De gamla nordiska namnen är ofta byggda som små pussel av två ord. Kan man de vanligaste bitarna kan man nästan läsa namnens betydelse direkt.",
  f"""<h2>Två ord blir ett namn</h2>
<p>Under vikingatiden och medeltiden skapades många namn genom att sätta ihop två ord – ofta ett ord för en gud, ett djur eller en egenskap med ett ord för skydd, strid eller skönhet. Därför betyder {nl('Arvid')} ”örn + skog” och {nl('Sigrid')} ”seger + vacker”.</p>

<h2>De vanligaste namnleden</h2>
<h3>As- och Os- – gud</h3>
<p>Ordet ás syftar på asarna, de nordiska gudarna. Det finns i {nl('Astrid', 'Asta', 'Oscar')}.</p>
<h3>Sig- – seger</h3>
<p>Fornnordiskans sigr betyder seger och finns i {nl('Sigrid', 'Signe', 'Sigge', 'Sixten')}.</p>
<h3>Tor- och Tur- – åskguden Tor</h3>
<p>Tor var åskans gud, och många namn bär hans namn: {nl('Tor', 'Ture', 'Tove', 'Tyra', 'Torsten', 'Tora')}.</p>
<h3>Ing- – guden Ing</h3>
<p>Ing är ett annat namn på fruktbarhetsguden Frej. Leden finns i {nl('Ingrid', 'Inga', 'Ingeborg', 'Ingemar', 'Ingvar')}.</p>
<h3>Arn- och Ar- – örn</h3>
<p>Örnen var en symbol för styrka, och ordet finns i {nl('Arvid', 'Arne', 'Ari')}.</p>
<h3>Ulf- och -ulf – varg</h3>
<p>Vargen var både fruktad och beundrad. Den syns i {nl('Ulf', 'Ylva')}.</p>
<h3>-sten – sten</h3>
<p>Sten stod för stabilitet och styrka, som i {nl('Sten', 'Torsten', 'Sixten')}.</p>
<h3>-rid och -frid – vacker</h3>
<p>Ordet fríðr betydde vacker och finns i {nl('Astrid', 'Ingrid', 'Sigrid')}.</p>
<h3>-hild och Gun- – strid</h3>
<p>Båda leden betyder strid och finns i {nl('Gunhild', 'Ragnhild', 'Hildur', 'Gunnar')}.</p>
<h3>-borg – skydd</h3>
<p>Borg betyder skydd eller värn, som i {nl('Ingeborg', 'Birger')}.</p>

<h2>Namn från mytologin</h2>
<p>En del nordiska namn kommer direkt från gudarna och gudinnorna: {nl('Freja', 'Saga', 'Idun', 'Siv', 'Loke', 'Tor')}. Andra kommer från ord i naturen, som {nl('Liv', 'Lilja', 'Ylva', 'Embla')} – där Embla enligt mytologin var den första kvinnan.</p>

<h2>Hitta fler</h2>
<p>På navi.baby finns en hel sida med <a href="/nordiska-namn/">nordiska namn</a>, och i <a href="/namngenerator/">namngeneratorn</a> kan du välja ”Nordiskt” för att bara få förslag med nordiskt ursprung.</p>
<p class="muted">Betydelsen av gamla namn är ofta omdiskuterad och kan tolkas på olika sätt. Uppgifterna här är en sammanfattning av vanliga tolkningar.</p>
""")

URLS.append("/guider/")
write("/guider/", head("Guider om babynamn | navi.baby", "Guider om att välja babynamn: regler för förnamn i Sverige, tips för att enas och betydelsen bakom nordiska namn.", "/guider/",
    breadcrumbs_ld([("navi.baby", "/"), ("Guider", "/guider/")])) + '<div class="crumbs"><a href="/">navi.baby</a> › Guider</div>\n<h1>Guider om babynamn</h1>\n<p class="lead">Allt ni behöver veta för att hitta rätt namn – från regler till tips och namnens historia.</p>\n<div class="cats" style="grid-template-columns:1fr">'
    + "".join(f'<a href="{p}"><b>{h}</b><small>{e(d)}</small></a>' for p, h, d in GUIDES) + "</div>\n" + FOOT)
