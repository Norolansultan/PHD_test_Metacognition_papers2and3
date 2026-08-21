# 1. Toiminnan kuvaus — pelastuslaitoksen näkökulma

Tämä dokumentti kuvaa, mitä simulaatiossa tapahtuu *operatiivisesti*: kuka johtaa mitä, millä
resursseilla, millä viestivälineillä, mitä osallistuja voi tehdä ja mitä hän näkee minuutti
minuutilta. Se on käytännön asiantuntijoiden (kolme kokenutta kaistanjohtajaa) arvioitava dokumentti
ennen kuin riviäkään sisältöä kirjoitetaan lopulliseen muotoon.

Kaikki mitä tässä on, on johdettu työkirjan välilehdistä `Shared World`, `Scenario Spine`,
`Scenario Flow`, `Master Timeline`, `Peer Timeline`, `Agent Spec`, `Guidance Texts` ja
`Disruption Spec`. Missä olen joutunut täydentämään, se on merkitty **[TÄYDENNYS]** ja vaatii
hyväksynnän.

---

## 1.1 Tapahtuma yhdellä kappaleella

Loppukesän maastopalo Harjulan alueella. Palokompleksi kattaa 30 × 30 km:n onnettomuusalueen
pohjois- ja koillisosan; useita kaistoja on kiinni sen kehällä. Osallistuja johtaa **kaistaa BRAVO**,
noin 4 × 4 km:n lohkoa alueen etelä-keskiosassa. Kaistan sisällä on suojattava kohde — Harjulan saha,
pieni teollisuuskiinteistö noin kilometrin päälinjan takana. Sahan menetys on epäonnistumisehto.
Päälinja kulkee itä–länsi-suuntaisen harjun laella; harjulla kulkee tie, joka on samalla huoltoreitti
ja poistumistie. 88 simulaatiominuutin aikana tuuli kääntyy noin 60° (S08), itäinen kytevä
lähestymissuunta lähtee juoksemaan ja koukkaa linjan itäpään ympäri kohti huoltoreittiä — suuntaan,
jota kukaan ei ollut katsomassa.

## 1.2 Roolit ja johtosuhteet

Työkirja käyttää ICS-termistöä. Alla suomennos, jota käytetään kaikessa osallistujalle näkyvässä
tekstissä. **[TÄYDENNYS — terminologia vahvistettava Pelastusopiston kanssa]**

| ICS (työkirja) | Simulaatiossa käytettävä suomenkielinen termi | Kuka on | Näkyy osallistujalle |
|---|---|---|---|
| Incident Commander | Pelastustoiminnan johtaja (PTJ) | Käsikirjoitettu | Radiossa, ohjauksen lähteenä |
| Operations Section Chief | Operaatiopäällikkö | Käsikirjoitettu | Radiossa, tehtävänannon antajana |
| Division supervisor | **Kaistanjohtaja** | **Osallistuja** | — |
| Adjacent divisions | Naapurikaistat CHARLIE, ECHO, FOXTROT, GOLF, HOTEL, INDIA, JULIET | Agentteja | Radiossa, kartalla, korpuksessa |
| Strike team | Muodostelma (iskuryhmä) A, B, C | Agentteja | Tilannepaneelissa, radiossa |
| Engine company | Sammutusyksikkö | Agentti | Tilannepaneelissa |
| Air asset | Miehittämätön tiedustelualus KILO-1, KILO-2 | Agentteja | Ylilento-ohjelmana, havaintoina |

**Osallistujan käskyvalta ulottuu** omiin muodostelmiin, sammutusyksikköön, säiliöautoon ja
maansiirtokoneeseen. **Ei ulotu** naapurikaistoihin, KILO-alustoihin eikä kaistarajan yli tehtäviin
(näiden osalta hän voi vain *pyytää*, ja pyyntö menee käsikirjoitettuun vastaukseen).

Nimeämisristiriita, jonka työkirja itse tunnistaa (`REVIEW NOTES` #10), ratkaistaan näin:
**NATO-foneettiset nimet ovat kanonisia**; metodinen/analyyttinen/aggressiivinen ovat *tyylejä*,
jotka ohjaavat kunkin kaistan kirjoitetun perustelun äänensävyä. Karttaprototyyppi käyttää jo
kanonisia nimiä — se pysyy.

## 1.3 Maasto ja mittakaavat

Kaksi sisäkkäistä mittakaavaa, vaihdettavissa milloin tahansa, jokainen vaihto lokitetaan.

**Onnettomuusalue, 30 × 30 km (1:120 000).** Koko palokompleksi, naapurikaistat, tieverkko,
asutuskuvio, ilmatoiminnan tukikohta etelässä ja ylilentoreitit, alueellinen sää, johtopaikka.
Renderöidään karkeasti ja suurin osa siitä on **vanhentunutta tai tuntematonta oletuksena**. Täällä
tilannekuvaa ei havaita vaan rakennetaan — tämä on tarkoituksellista, ja se on juuri sitä käyttäytymistä,
jota Paperi 2 manipuloi.

**Kaista BRAVO, n. 4 × 4 km (1:16 000).** Omat muodostelmat, kohde, ankkuri, lähestymissuunnat,
etummaiset rakennukset, dronen ylilentojalanjälki. Kaikki päätöspisteet ratkeavat tällä mittakaavalla,
satojen metrien tarkkuudella.

Prototyyppikartassa (`harjulakartta.html`) kaista on rajattu ruutuun x 13,2–17,2 / y 16,2–20,2 km,
mikä on tasan 4 × 4 km ja istuu 30 km:n ruudukkoon. Se pitää.

### Kiinteät maastopiirteet ja niiden operatiivinen merkitys

| Piirre | Sijainti kaistassa | Miksi se on olemassa |
|---|---|---|
| Harjun selänne | Keskellä, I–L | Päälinjan ankkuri. Tähystys pohjoiseen avomaalle. Kantaa tien. |
| Päälinja | Selänteen laella, n. 1 km sahasta pohjoiseen | Epäsuoran sammutuksen linja. |
| Harjulan saha (KOHDE) | Etelä-keskiosa | 2–3 rakennusta, piha, aita, tulotie. Menetys = epäonnistuminen. |
| Valmisteltu varalinja | N. 400 m linjan takana | Konservatiivinen vaihtoehto useassa päätöspisteessä. |
| Puro / märkä linja | Linjan edessä | Luonnollinen katko, vedenottopaikka. |
| Pohjoinen lähestymissuunta | Pohjoisesta | Avomaa ja tiekäytävä. Tuulen ajama palo juoksee nopeasti. Odotettu pääsuunta. |
| Itäinen lähestymissuunta | Koillisesta, kaartuu itään | Peitteinen sekametsä ja turve. Kytee ja hiipii — kunnes S08. |
| Takamaasto lounaassa | Muodostelmien ja sahan välissä | **Tässä käännös puree.** Oletettiin turvalliseksi märän turpeen takia. |
| Suot | Hajallaan, erit. LO takamaasto | Ojitettu turve kytee ja nousee uudestaan. |
| Järvi ja puro | Pieni järvi koillisessa | Vedenotto, luonnolliset katkot. |
| Huoltoreitti | Sahalta taakse ja sivuille | Kulkee osin takamaaston läpi — siksi käännös uhkaa huoltoa. |
| Kaistan johtopaikka | Selänteen takana, keskellä | Osallistujan näkymä; huoltotie sahalle selän takana. |

## 1.4 Resurssit ja niiden fysiikka

Nämä ovat **suunnitteluoletuksia**, jotka käytännön asiantuntijat validoivat samassa portissa kuin
leviämisnopeudet ja polttoaineparametrit.

| Resurssi | Määrä | Mallinnettu ominaisuus |
|---|---|---|
| Muodostelma A, B, C | 3 | Sijainti, vesi-%, tehtävä, altistuminen, LCES-tila |
| Sammutusyksikkö | 1 | Rakennussuojaus; hitaampi uudelleensijoittaminen |
| Säiliöauto | 1 | Vesitäydennys; sidottu ajokelpoiseen tiehen |
| Maansiirtokone (dozer) | 1 | Murroslinjan raivaus; hidas, sitoutuu pitkäksi aikaa |
| KILO-1 / KILO-2 | — | Ei käskyvallassa. Ylilento-ohjelma; S08–S11 KILO-1 maassa, KILO-2 nousee korkealle |

**Liike.** Tiellä 40–60 km/h, maastossa jalan 3–4 km/h, plus perustamisaika. Kaistan sisällä
uudelleensijoittaminen maksaa 5–15 min — todellinen mutta maksettava hinta. Kaistarajan yli siirtyminen
on käytännössä peruuttamaton sitoumus. Tämä on suunniteltu tarkoituksella: se tekee sijoittelupäätöksistä
oikeita päätöksiä.

**Vesi.** Kuluu kiinteällä nopeudella tehtävästä riippuen. S05:ssä vesi ylittää 40 % rajan samassa
minuutissa kun ohjaus annetaan — kaksi painetta kerralla, tarkoituksella.

**Palon leviäminen.** Latvapalo suomalaisessa metsässä n. 0,3–2 km/h polttoaineesta ja tuulesta
riippuen, nopeampi avomaalla ja tuulen ajamassa juoksussa. 88 minuutissa palo siirtyy 0,5–3 km,
mikä on suuri osa 4 km:n kaistaa mutta alle 10 % 30 km:n alueesta — juuri siksi mittakaavoja on kaksi.

## 1.5 Viestintä ja tiedonsaanti

Osallistujalla on **neljä** tiedon kanavaa. Kolme ensimmäistä ovat identtiset kaikissa neljässä solussa.

1. **Radioverkko.** Taustaliikennettä matalalla volyymilla plus käsikirjoitetut avainviestit. Volyymi
   nousee tempon mukana. Sekä ääni että vierivä tekstiloki.
2. **Rutiini-SITREPit.** Naapurikaistat raportoivat syklissä. JULIETin sykli *lakkaa* S06:ssa —
   ja hiljaisuus on informaatio.
3. **Kyselyrakentaja.** KUKA × MITÄ × MILLOIN -paikat: (kaista / oma muodostelma / ilma-alus) ×
   (sijainti, päätös, **perustelu**, **luottamus**, havainto) × (nyt, viim. 15 min, käännöksen jälkeen).
   Plus toissijainen vapaa tekstikenttä. Vastausviive kiinteä 2,5 s.
4. **Karttanäkymä**, kaksi mittakaavaa, vanhentuneisuusvarjostuksella.

**Ainoa ero ehtojen A ja B välillä:** ehto B saa kyselyrakentajaan kentät PERUSTELU ja LUOTTAMUS.
Ehto A ei ole tiedosta paitsiossa — se saa täyden radioverkon, SITREPit, naapurien sijainnit ja
toimet. Tämä on työkirjan `REVIEW NOTES` #16 ja se on koko Paperin 2 pätevyyden kannalta ratkaiseva:
manipulaatio on pääsy **naapurin päättelyyn**, ei pääsy tietoon.

**Järjestelmä ei koskaan ilmoita, että uutta tietoa on.** Ei merkkejä, ei ilmoituksia, ei
"uutta sinun edellisen kyselysi jälkeen". Uudelleenkysyminen on osallistujan oma idea tai mittaria
ei ole.

## 1.6 Mitä osallistuja voi tehdä — toimintotaksonomia

Päätöspalkki tarjoaa kussakin päätöspisteessä 3–6 kiinteää optiota. Optiojoukot ovat identtiset
kaikille (paitsi että sitovassa haarassa osa on estetty). Taksonomia, josta optiot koostetaan:

| Toimintoluokka | Esimerkkejä | Vaikuttaa |
|---|---|---|
| Sijoittelu | Siirrä muodostelma X pisteeseen Y; pidä nykyinen | Sijainti, altistuminen, saapumisaika |
| Sammutustapa | Epäsuora linjalla; suora hyökkäys; raivaa murroslinja | Vesi, aika, riski |
| Ankkurointi | Tie/harju-ankkuri; etummainen dozer-ankkuri; varalinja | Linjan pito S08:n jälkeen |
| Kohteen suojaus | Sido sammutusyksikkö sahalle; vapauta se | Epäonnistumisehto |
| Vetäytyminen | Varalinjalle; sahan kehälle | Turvamarginaali |
| Tiedustelu | Lähetä partio itäsuunnalle; pyydä KILO-ylilentoa | Korpuksen sisältö myöhemmin |
| Huolto | Ohjaa säiliöauto; avaa vedenotto | Vesi |
| Turvallisuus | Aseta tähystys; määritä poistumistie; osoita turva-alue | **LCES-portti** |
| Pyyntö ylöspäin | Pyydä lisäresurssia; pyydä ohjauksen tarkennusta | Käsikirjoitettu vastaus |
| Ei toimintaa | (ei valintaa ikkunan sisällä) | **Oletustoiminta laukeaa** |

**LCES on portti, ei ulottuvuus.** Jokainen sitoutuva toiminto tarkastetaan neljää ehtoa vasten:
Lookouts (tähystys), Communications (viestiyhteydet), Escape routes (poistumistiet),
Safety zones (turva-alueet). Jos sitoutuva toiminto ei täytä niitä kaikille osallisille
muodostelmille, päätöksen laatu on 0 riippumatta muista ulottuvuuksista. Tämä on sekä
pisteytyssääntö että sisällön kirjoitussääntö: jokaisella optiolla on tiedostossa LCES-tila.

## 1.7 Miten päätöspiste saapuu — kolme toimitustyyppiä

| Tyyppi | Mitä tapahtuu | Onko päätöspalkkia | Mitä mitataan |
|---|---|---|---|
| **CUED** | Tapahtuma pakottaa huomion | Kyllä, näkyvä countdown | Valinta tunnettujen vaatimusten alla |
| **AMBIGUOUS** | Vihje saapuu, merkitystä ei merkitä | Kyllä, neutraali kehystys | Tulkinta |
| **UNCUED** | Ei mitään. Näkymätön ikkuna | **Ei koskaan** | Spontaani toiminta = negatiivisen vihjeen havaitseminen |

Uncued-pisteissä ei saa olla päätöspalkkia, ikonia, ääntä eikä mitään merkkiä. Palkin avautuminen
S06:ssa kertoisi osallistujalle, että hiljaisuus vaatii päätöksen — ja tuhoaisi koko mittarin.
Tämä oli edellisen luonnoksen rakenteellinen virhe (`REVIEW NOTES` #15).

**Jokainen ikkuna umpeutuu.** Umpeutuessa muodostelmat jatkavat viimeisillä käskyillä ja voimassa
oleva suunnitelma toteutuu. Kaistan tasolla ei ole varajohtajaa keksimässä mitään. Osallistujalle
kerrotaan radiossa mitä nyt tapahtuu, ja tapahtuma kirjataan **NON-DECISION**-tapahtumana omine
kustannuksineen. Tekemättä jättäminen on valinta, ei tapa jäädä pois mittauksesta.

**Paikallinen seuraus on aito, selkäranka on kiinteä.** Skenaarioiden järjestys ja ulkoisten
tapahtumien ajoitus eivät koskaan riipu osallistujan toiminnasta — se pitää haarat vertailukelpoisina.
Mutta muodostelmien sijainnit, vesitilanne, altistuminen, säästyneet tai menetetyt rakennukset ja
myöhemmin saatavilla oleva tieto **riippuvat**. Osallistujan on nähtävä, että hänen päätöksensä
muuttivat jotain, tai hän oppii kahdessakymmenessä minuutissa ettei mikään merkitse ja lakkaa
osallistumasta.

## 1.8 Tapahtuman kulku minuutti minuutilta

Simuloitu kello. Kello **pysähtyy** jäädytyksissä, joten jäädytys ei koskaan syö skenaarioaikaa.
Kokonaisuus: 88 simulaatiominuuttia, 98 minuuttia seinäkelloa.

### Vaihe P1 — ei ohjausta (S01–S04)

| Kello | Tapahtuma | Ikkuna | Mitä osallistuja tekee |
|---|---|---|---|
| 0:00 | Tapahtuma alkaa. Taustaradio, muodostelmat matkalla, molemmat karttanäkymät elossa | — | Orientoituu |
| 0:02 | **S01** Operaatio antaa kaistan radiossa | 5 min, CUED | Ensimmäinen resurssien sitominen. Määrää lähtöasemat koko ajoksi |
| 0:08 | **S02** Pyyntö sitoa reservi | 4 min, CUED | Reservikuri. Vaikuttaa S09:ään |
| 0:10 | SPAM-osio 1 (taso 1) | — | *(ks. huomautus 3.4: tämä osuu S02:n ikkunan sisään)* |
| 0:13 | **S03** Palokäyttäytyminen helpottaa; naapurit sitoutuvat kuuluvasti suoraan hyökkäykseen. Ilmatilannepäivitys luvattu 0:25 | 4 min, AMBIGUOUS | Konformismi tempon alla — kärsivällinen vaihtoehto on olemassa |
| 0:18 | **S04** Muodostelma C raportoi heikentyneestä näkyvyydestä. Sävy rutiini | 4 min, AMBIGUOUS | Heikko signaali vakiintunutta kuvaa vastaan. Itäinen indikaattori kirjoitetaan korpukseen |
| 0:22 | **JÄÄDYTYS 1** (3 min) | Kello seis | L1 ×3, L2 ×2, L3 ×1 |

### Vaihe P2 — ohjaus voimassa (S05–S07)

| Kello | Tapahtuma | Ikkuna | Mitä osallistuja tekee |
|---|---|---|---|
| 0:23 | **G-01 annetaan** ja **S05** alkaa: ankkurivalinta, vesi alittaa 40 % | 5 min, CUED | Ensimmäinen ohjaus vs. oma harkinta. Naapurit jakautuvat kolmeen |
| 0:26 | JULIETin viimeinen SITREP aikataulussa. Seuraava odotettu 0:36 | — | — |
| 0:29 | SPAM-osio 2 (taso 2) | — | — |
| 0:34 | **S07** Kertyneet itähavainnot muuttuvat haettaviksi. Mikään ei merkitse niitä ratkaiseviksi | 5 min, AMBIGUOUS | Uskomuksen revisio vahvistusharhaa vastaan. **Vahvin ennustaja koko asetelmassa** |
| 0:36 | **S06** JULIETin odotettu SITREP ei tule. Mikään ei merkitse tätä | 8 min **näkymätön** | Hiljaisuuden havaitseminen verkon rytmiä vasten |
| 0:40 | KILO-1:n matalan luottamuksen havainto kirjoitetaan korpukseen: piste-sää / IR-anomalia itäsivustalla. **Ei hälytystä, ei kartalle** | — | Löytyy *millä tahansa* itää, KILOa tai säätä koskevalla kyselyllä |
| 0:44 | SPAM-osio 3 (taso 3) | — | *(ks. huomautus 3.4: osuu S06:n näkymättömän ikkunan reunaan)* |
| 0:46 | Katkonainen radiolähete: epävarma raportti savun käyttäytymisen muutoksesta itäsivustalla | — | Kyselyä vaatimaton havaintoreitti — ehto A ei ole rakenteellisesti ulkona |

### Vaihe P3 — häiriö (S08)

| Kello | Tapahtuma | Ikkuna |
|---|---|---|
| 0:48 | **S08 — TUULEN KÄÄNNÖS.** Tuuli kääntyy n. 60° ja voimistuu. Ympäristönäytöt päivittyvät, palokäyttäytyminen muuttuu näkyvästi, naapurikaista raportoi käännöksen radiossa | 4 min, UNCUED → CUED |

Yksi fyysinen syy, kolme seurausta: **uhkasuunta vaihtuu**, **ankkuri lakkaa toimimasta**, ja
**saha tulee saavutettavaksi suunnasta jota kukaan ei katsonut**. Itäinen peitteinen suunta, joka on
kytenyt S04:stä asti, tulee linjaan uuden tuulen kanssa ja lähtee juoksuun; juoksu **koukkaa linjan
itäpään ympäri** kohti huoltoreittiä. Palo ei teleporttaa linjan taakse — se kiertää sen, ja
käytännön asiantuntija tunnistaa ilmiön.

Havaintoviive mitataan **taaksepäin** hetkestä 0:48. Kaksi reittiä varhaiseen havaintoon:
kysely (0:40 alkaen) ja radiovihje (0:46). Kolmas mahdollisuus on olla havaitsematta.

Mitä **ei** anneta: ei ilmoitusta siitä että ohjaus on nyt pätemätön, ei uudelleenannettua ohjausta,
ei naapurimerkintöjen merkitsemistä vanhentuneiksi, ei yhteenvetoa siitä mikä muuttui.
**Pätemättömyyden tunnistaminen ON mitattava käyttäytyminen.**

### Vaihe P4 — häiriön jälkeen (S09–S12)

| Kello | Tapahtuma | Ikkuna | Ydin |
|---|---|---|---|
| 0:53 | **S09** Altistuminen kiistaton; ohjaus sanoo yhä *pidä* | 3 min, CUED | **PAPERI 3 ENSISIJAINEN.** Onko poikkeama kalibroitu vai impulsiivinen |
| 0:56 | **JÄÄDYTYS 2** (4 min) | Kello seis | L1 ×2, L2 ×3, L3 ×3. Asetelman arvokkain jäädytys |
| 0:57 | **S10** Sitoutuminen huonosti havaittuun takamaastoon. Korpus palauttaa lähes tyhjää | 4 min, AMBIGUOUS | Oman tietämättömyyden tunnistaminen. Tuottaako tietoa ennen sitoutumista |
| 1:02 | **S11** Lyhyt ikkuna juoksun pysäyttämiseen; naapurit hyökkäävät näkyvästi; ohjaus hillitsee. Vesi vähissä, poistumistiet epävarmat | 3 min, CUED | Tilaisuus + konformismi vs. ohjaus ja työturvallisuus |
| 1:06 | **S12** Tapaus jossa ohjaus ja ilmeinen paikallinen harkinta ovat samaa mieltä | 4 min, CUED | **Kontrolli.** Erottaa myöntyvyyden samanmielisyydestä |

S12 ei ole valinnainen. Ilman vähintään yhtä yhtenevää häiriönjälkeistä tapausta ei voi tietää,
noudattaako ohjausta seuraava osallistuja ohjetta vai onko hän vain samaa mieltä — ja se
epäselvyys romuttaisi jokaisen yli-noudattamisväitteen.

### Vaihe P5 — ohjaus vedetty pois (S13–S15)

| Kello | Tapahtuma | Ikkuna | Ydin |
|---|---|---|---|
| 1:11 | **S13** Johtokanava vapauttaa kaistat paikalliseen harkintaan (**G-03**). Kaikki estetyt optiot avautuvat sitovassa haarassa | 5 min, CUED | Kimmahdus: viive nousee, luottamus laskee |
| 1:17 | **S14** Myöhäinen tieto tekee aiemmasta sitoumuksesta väärän näköisen; peruminen on yhä mahdollista mutta kallista | 4 min, AMBIGUOUS | Virheen havaitseminen, uponneen kustannuksen vastustus |
| 1:21 | **JÄÄDYTYS 3** (3 min) | Kello seis | L1 ×2, L2 ×2, L3 ×2 |
| 1:22 | **S15** Vuoronvaihto: tuleva kaistanjohtaja soittaa. Osallistuja kertoo tilanteen ja aikomuksensa vapaana tekstinä | 6 min, CUED | Vapaamuotoinen tilannekuvan talteenotto |
| 1:28 | Tapahtuma päättyy | — | — |

## 1.9 Naapurikaistojen kaaret — mitä maailmassa tapahtuu ilman osallistujaa

Nämä ajavat taustalla koko ajan, ja ne ovat sekä radioliikennettä että korpuksen sisältöä.
Ne eivät saa olla keskenään ristiriitaisia missään hetkessä — siksi ne ovat yksi datataulukko,
ei seitsemän erillistä käsikirjoitusta.

| Kaista | Tyyli (ohjaa perustelun äänensävyä) | S01–04 | S05–07 | S08 | S09–12 | S13–15 |
|---|---|---|---|---|---|---|
| CHARLIE | Metodinen, siteeraa lähteitä | Irrottaa ryhmän rakennukselta | Palauttaa linjan itään | **Raportoi käännöksen ensimmäisenä** | Sopeutuu, vetäytyy tielle | Vakaa |
| ECHO | Aggressiivinen, lyhyt, korkea luottamus | Valmistelee suoraa | Sitoutuu suoraan | Jää käännöksen alle, irtautuu | Sopeutuu | Vakaa |
| FOXTROT | Seuraaja, peilaa ECHOa | Valmistelee suoraa | Sitoutuu suoraan | Irtautuu ECHOn mukana | Sopeutuu | Vakaa |
| GOLF | Aggressiivinen, heikko oivallus | Siirtyy dozer-piirteelle | Etenee dozer-ankkuriin | Paljastuu | **Ei sopeudu — vanhentuneen perustelun syötti S11:ssä** | Kääntyy myöhään |
| HOTEL | Konservatiivinen, selittää riskin | Pitää | Vetäytyy | Jo turvassa | Sopeutuu | Vakaa |
| INDIA | Analyyttinen, eksplisiittinen epävarmuus | Odottaa | Pitää | Pitää | Sopeutuu | Vakaa |
| JULIET | Niukka jo ennen hiljaisuutta | Normaali SITREP-sykli | **Hiljenee S06:ssa, 14 min** | Yhä hiljaa | Yhteys palaa S10:ssä | Vakaa |
| KILO-1 | — | Ylilento BRAVOn yli S03+12 min | Uudelleentehtävöity itäsivustalle, kirjaa 0:40 havainnon | **Maassa 0:48–1:05** | Palaa S11:ssä | Käytettävissä |
| KILO-2 | — | Naapurikaista | Viimeisin sijainti JULIETin lähellä | Nousee korkealle | Karkea IR juoksun koosta (S09) | Normaali tehtävöinti |

## 1.10 Ohjaus — mitä osallistuja kuulee ja mitä hän ei voi tehdä

| ID | Annetaan | Neuvova haara | Sitova haara |
|---|---|---|---|
| G-01 | S05 (0:23) | "Kaistoja neuvotaan pitämään epäsuora sammutus tie- ja harjuankkurilla. Sitoutumista ankkurin etupuolelle ei suositella nykyisellä resurssitilanteella." | "Kaistat pitävät epäsuoran sammutuksen tie- ja harjuankkurilla. Sitoutumista ankkurin etupuolelle ei ole valtuutettu." Optiot *Etene dozer-ankkuriin* ja *Suora hyökkäys ankkurin edessä* estetty |
| G-02 | Voimassa oleva rajoite S06:sta | SITREP-kuri; resurssien siirtoa naapurikaistoille ei suositella | Kaistarajan ylittävä tehtävöinti estetty |
| G-03 | S13 (1:11) | "Kaistat vapautetaan paikalliseen harkintaan. Aiempi ohjaus ei ole enää voimassa." | **Identtinen teksti.** Poisveto on sama molemmissa haaroissa |
| — | S08–S13 | **Hiljaisuus.** Ohjausta ei anneta lisää. Hiljaisuus on tarkoituksellinen ja se on mitattava asia | Sama |

**Sitovan haaran ohitus on kitkaa, ei seinä.** Estetty optio on valittavissa, mutta valinta avaa
vahvistusaskeleen ja vaatii vapaamuotoisen perustelun. Seinä mittaa seinää; kitkallinen ohitus mittaa
osallistujaa. Ohituksen jokainen vaihe lokitetaan erikseen (näytetty, avattu, peruttu, vahvistettu).

**Huomio ristiriidasta:** G-02 on työkirjassa merkitty *annettavaksi S06:ssa*, mutta Master Timeline
ei sisällä ohjaustapahtumaa S06:ssa — eikä saa sisältää, koska S06 on uncued. Ratkaisu, joka on
viety sisältömalliin: **G-02 on voimassa oleva rajoitetila, ei lähetetty viesti.** Se on kirjattu
ohjauspaneeliin S05:stä lähtien ja se estää kaistarajan ylitykset, mutta mitään ei koskaan lähetetä
verkkoon S06:ssa. Ks. dokumentti 3, ristiriita **V-3**.

## 1.11 Istunnon kulku huoneessa

| # | Lohko | Min | Vetää |
|---|---|---|---|
| 1 | Vastaanotto, suostumus, tunnuksen luonti | 10 | Tutkija |
| 2 | **Käyttöliittymäkoulutus** | 12 | Tutkija |
| 3 | Harjoitustapahtuma (3 harjoitusskenaariota, eri kaista) | 12 | Järjestelmä |
| 4 | Tauko | 5 | — |
| 5 | **Päätapahtuma S01–S15** | 98 | Järjestelmä |
| 6 | Loppukysely (luottamus, NASA-TLX, ohjauksen legitimiteetti, manipulaatiotarkistukset) | 10 | Järjestelmä |
| 7 | Retrospektiivinen haastattelu 3 skenaariosta, oma toiminta uusintana | 10 | Tutkija |
| | **Yhteensä huoneessa** | **157** | |
| 8 | CTA-haastattelu (n. joka 4.) | 25 | Erillinen aika, ei perään |

Koulutuslohko on mittausteknisesti kriittinen, ei muodollisuus. Sen on opetettava **koko
kyvykkyysjoukko osoitettuun kriteeriin asti** — molemmat karttamittakaavat, kyselyrakentajan kaikki
paikat, luottamusliukuri — ja siihen on sisällyttävä harjoitusesimerkki, jossa **sama kysymys
myöhemmin palauttaa enemmän**. Muuten tutkimus mittaa työkalun tuntemusta eikä puutteen tunnistamista.
Jäädytyksiä ei mainita koskaan.
