Toteutussuunnitelma · Paperit 2 & 3 · 21.8.2026

# Harjulan instrumentti

Miten pelastuslaitoksen simulaatio rakennetaan: yksi jatkuva maastopalotapahtuma, viisitoista päätöspistettä, neljä koeasetelman solua — ja mittausvaatimukset, jotka sanelevat arkkitehtuurin joka kerroksessa.

**88** simulaatiominuuttia · **15** päätöspistettä · **4** solua · 136 osallistujaa · **20** viikkoa kehitystä · **6** löydettyä ristiriitaa

## 01 · Kuusi periaatetta, joista kaikki muu seuraa

> [!NOTE]
> **Tämä on tutkimusinstrumentti joka sisältää simulaation, ei simulaatio johon on lisätty mittaus.** Kun immersio ja mittaus ovat ristiriidassa, mittaus voittaa. Jokainen alla oleva valinta on tämän lauseen seuraus.

#### Erillinen selaininstrumentti, ei XVR-laajennus

*Alusta*

Optioesto, päätöspalkin countdown, näytön pimennys jäädytyksessä, sanatarkka determinismi ja tapahtumatason lokitus eivät ole XVR:n kautta toteutettavissa. XVR sopii korkeintaan harjoituslohkoon.

#### Domain-neutraali moottori

*Rakenne*

Pelastus on sisältöpaketti, armeija on toinen sisältöpaketti. Uhkamalli on rajapinta: etenevä palo ja etenevä vastustaja ovat sama asia identtisellä maastolla.

#### Yksi kello

*Aika*

Simuloitu kello tikittää kiinteällä askeleella, pysähtyy jäädytyksissä eikä koskaan odota osallistujaa. Skenaariot etenevät ajassa — se on vertailukelpoisuuden ehto.

#### Kaksi kerrosta, yksi portti

*Tieto*

Ground truth ei ole saavutettavissa osallistujan buildissa millään reitillä. Kaikki mitä ruudulle päätyy, kulkee havaintoportin läpi ikäänsä vastaavasti haalennettuna.

#### Tieto kertyy ajassa

*Korpus*

Jokaisella merkinnällä on `valid_from` ja mahdollinen korvaaja. Sama kysymys eri hetkellä palauttaa eri vastauksen — ja järjestelmä ei koskaan kerro, että uutta on tullut.

#### Ilman lokia mittausta ei ole

*Mittaus*

Muuttuja lisätään lokispesifikaatioon ennen kuin ominaisuus rakennetaan. Kaikki johdetut muuttujat lasketaan raakatapahtumista skriptillä, joka voidaan ajaa uudelleen.

## 02 · Mitä pelastuslaitoksen puolella tapahtuu

Loppukesän maastopalo. Osallistuja johtaa kaistaa BRAVO — noin 4 × 4 km:n lohkoa 30 × 30 km:n onnettomuusalueen etelä-keskiosassa. Suojattava kohde on Harjulan saha, kilometrin päälinjan takana. Sahan menetys on epäonnistumisehto.

### Roolit ja käskyvalta

| Rooli | Kuka | Näkyy osallistujalle |
|---|---|---|
| Pelastustoiminnan johtaja | Käsikirjoitettu | Radiossa; ohjauksen lähde (G-01, G-03) |
| Operaatiopäällikkö | Käsikirjoitettu | Antaa kaistan tehtävän S01:ssä |
| Kaistanjohtaja BRAVO | **Osallistuja** | — |
| Muodostelmat A, B, C | Agentteja | Käskyvallassa. Sijainti, vesi-%, altistuminen, LCES-tila |
| Sammutusyksikkö, säiliöauto, dozer | Agentteja | Käskyvallassa. Hitaita sitoutumaan |
| Naapurikaistat CHARLIE…JULIET | Agentteja | Ei käskyvallassa. Radio, kartta, korpus |
| KILO-1 / KILO-2 | Agentteja | Ei käskyvallassa. Ylilento-ohjelma, IR-havainnot |

### Neljä tiedon kanavaa — ja se ainoa ero

Radioverkko, rutiini-SITREPit, kyselyrakentaja ja karttanäkymä. Kolme ensimmäistä ovat **identtiset kaikissa neljässä solussa**. Ainoa ero ehtojen välillä on, että ehto B saa kyselyrakentajaan kentät **perustelu** ja **luottamus**.

> [!NOTE]
> Manipulaatio ei ole pääsy naapurien *tietoon* vaan pääsy heidän **päättelyynsä**. Yksikään SITREP-formaatti ei kanna lausetta *valitsin tämän koska arvioin X, ja olin siitä 60 % varma*. Siksi ehto A ei ole tiedosta paitsiossa — ja siksi tulos on luettavissa perustelun saatavuuden ansioksi.

### Toimintotaksonomia ja LCES-portti

Päätöspalkki tarjoaa 3–6 kiinteää optiota. Optiot koostetaan yhdeksästä toimintoluokasta: sijoittelu, sammutustapa, ankkurointi, kohteen suojaus, vetäytyminen, tiedustelu, huolto, turvallisuus ja pyyntö ylöspäin. Kymmenes vaihtoehto on aina olemassa: **ei toimintaa**, jolloin oletustoiminta laukeaa.

> [!IMPORTANT]
> **LCES on portti, ei ulottuvuus.** Jos sitoutuva toiminto ei säilytä tähystystä, viestiyhteyksiä, poistumisteitä ja turva-alueita jokaiselle osalliselle muodostelmalle, päätöksen laatu on 0 riippumatta muista ulottuvuuksista. Jokaisella optiolla on siksi LCES-tila jo sisältötiedostossa.

### Kolme toimitustyyppiä

#### Tapahtuma pakottaa huomion

*Cued · 8 skenaariota*

Päätöspalkki aukeaa, countdown juoksee. Mitataan valintaa tunnettujen vaatimusten alla.

#### Vihje ilman merkitystä

*Ambiguous · 5 skenaariota*

Palkki aukeaa, mutta kehystys on neutraali. Mitataan tulkintaa.

#### Ei mitään

*Uncued · 2 skenaariota*

Ei palkkia, ei ikonia, ei ääntä, ei countdownia. Näkymätön ikkuna on olemassa vain lokissa. Palkin avaaminen S06:ssa kertoisi, että hiljaisuus vaatii päätöksen — ja tuhoaisi mittarin.

**Jokainen ikkuna umpeutuu.** Muodostelmat jatkavat viimeisillä käskyillä, radiossa kerrotaan mitä nyt tapahtuu, ja lokiin menee ei-päätös sääntöineen. Kaistan tasolla ei ole varajohtajaa keksimässä mitään. Osallistuja, joka ei koskaan päätä, tuottaa löydöksen — ei rikkinäistä tietuetta.

## 03 · 88 minuuttia, viisi vaihetta, yksi käännös

Ohjaus annetaan S05:ssä, sen premissi tuhoutuu S08:ssa ja se vedetään pois S13:ssa. Sama tuulen käännös mitätöi yhtä aikaa ohjauksen ja kaikki naapurien ennakkotapaukset — siksi kaksi paperia mahtuu yhteen tapahtumaan.

<!-- Aikajanakaavio (SVG): ks. harjulan-instrumentti.html -->

päätöspiste · SAGAT-jäädytys, kello pysähtyy · häiriön esioire · näkymätön ikkuna

### Viisitoista päätöspistettä

| S | Alkaa | Ikkuna | Tyyppi | Tilanne | Ohjaus | Ennakkotapaus |
|---|---|---|---|---|---|---|
| S01 | 0:02 | 5 min | cued | Kaistan tehtävä; ensimmäinen resurssien sitominen | — | ei ole |
| S02 | 0:08 | 4 min | cued | Paine sitoa reservi ennen arviointia | — | osuva |
| S03 | 0:13 | 4 min | ambiguous | Tilaisuusikkuna; naapurit sitoutuvat kuuluvasti. Ilmapäivitys tulossa | — | harhaanjohtava |
| S04 | 0:18 | 4 min | ambiguous | Muodostelma C: heikentynyt näkyvyys idässä. Yksi lähde, vahvistamaton | — | ei ole |
| F1 | 0:22 | 3 min | jäädytys | Vakiintunut kuva, heikko vastasignaali mukana mutta integroimatta | L1×3 · L2×2 · L3×1 | |
| S05 | 0:23 | 5 min | cued | Ankkurivalinta; ohjaus annetaan ja vesi alittaa 40 % samassa minuutissa | konflikti | harhaanjohtava |
| S07 | 0:34 | 5 min | ambiguous | Itähavainnot muuttuvat haettaviksi. Uskomuksen revisio — vahvin ennustaja | epämääräinen | osuva |
| S06 | 0:36 | 8 min | uncued | JULIETin SITREP ei tule. Hiljaisuus on havaittava verkon rytmiä vasten | epämääräinen | ei ole |
| S08 | 0:48 | 4 min | unc → cued | **Tuulen käännös ~60°.** Itäsuunta lähtee juoksuun ja koukkaa linjan itäpään ympäri | — | mitätöity |
| S09 | 0:53 | 3 min | cued | Ankkuri ei pidä, ohjaus sanoo yhä pidä. **Paperi 3 ensisijainen** | konflikti | osuva |
| F2 | 0:56 | 4 min | jäädytys | Kuva heti kehyksen murruttua — asetelman arvokkain | L1×2 · L2×3 · L3×3 | |
| S10 | 0:57 | 4 min | ambiguous | Sitoutuminen huonosti havaittuun takamaastoon. Korpus palauttaa lähes tyhjää | epämääräinen | ei ole |
| S11 | 1:02 | 3 min | cued | Lyhyt ikkuna juoksun pysäyttämiseen; naapurit hyökkäävät, ohjaus hillitsee | konflikti | harhaanjohtava |
| S12 | 1:06 | 4 min | cued | Ohjaus ja paikallinen harkinta samaa mieltä. **Kontrolli** | yhtenevä | ei ole |
| S13 | 1:11 | 5 min | cued | Ohjaus vedetään pois; kaikki estot avautuvat | — | ei ole |
| S14 | 1:17 | 4 min | ambiguous | Myöhäinen tieto tekee aiemmasta sitoumuksesta väärän. Peruminen yhä mahdollista | — | osuva |
| F3 | 1:21 | 3 min | jäädytys | Toipuminen ilman ohjausta | L1×2 · L2×2 · L3×2 | |
| S15 | 1:22 | 6 min | cued | Vuoronvaihto tulevalle kaistanjohtajalle, vapaa teksti | — | ei ole |

> [!IMPORTANT]
> **Mitä S08:ssa tarkoituksella jätetään antamatta:** ei ilmoitusta siitä että ohjaus on nyt pätemätön, ei uudelleenannettua ohjausta, ei naapurimerkintöjen merkitsemistä vanhentuneiksi, ei yhteenvetoa muutoksesta. Pätemättömyyden tunnistaminen *on* mitattava käyttäytyminen. Jokainen myöhemmin lisätty *avulias* ilmoitus tuhoaa sen hiljaa.

## 04 · Arkkitehtuuri

Kolme kovaa rajaa pitävät rakennelman kasassa: ydin ei tunne DOMia eikä verkkoa, havaintoportti on ainoa reitti maailmasta käyttöliittymään, ja sisältöpaketti on dataa eikä koodia.

**Build-aika · Node · tulos hashataan ja lukitaan**

Excel → YAML -tuonti · Sisältövalidaattori · Maaston leipominen · Palorintaman leipominen · content-pack.json + SHA-256

↓ versioidut, muuttumattomat assetit

**Sim core · puhdas TypeScript · ei DOMia, ei I/O:ta, ei satunnaisuutta**

Kello + ajastin · Maailmatila · Agenttiajuri · Resurssimalli · Aikaindeksoitu korpus · Projektio-oraakkeli · Uhkamalli (rajapinta) · Oletustoimintamoottori

↓ havaintoportti — mitä *tämä* osallistuja tietää, milloin, kuinka vanhana

**Käyttöliittymä · React + canvas**

Kartta, 2 mittakaavaa · Päätöspalkki + countdown · Kyselyrakentaja · Radioloki · Tilannepaneeli · Ohjauspaneeli · Koetinkerros

↓ jokainen tilamuutos on jo tapahtuma

**Telemetria ja tutkijan työkalut**

Append-only tapahtumajono · 30 s tilannekuva · Offline-lataus + hash · Tutkijakonsoli · Uusinta, ehtomerkinnät riisuttuna · derive.ts → CSV

### Kyselymoottori — viisi askelta, aina samassa järjestyksessä

1. Rakenna kyselyavain paikoista **KUKA × MITÄ × MILLOIN** (tai kartoita vapaa teksti aikomukseksi).
2. Suodata korpus ajassa: `validFrom ≤ tSim`. Kaikki muu on olematonta.
3. Suodata kyselypolulla; poimi myös häiriösyötit — tavoitesuhde 3:1.
4. **Ehtoportti:** ehdossa A kentät `rationale` ja `confidence` eivät ole tyhjiä vaan *olemattomia*.
5. Palauta kiinteän 2,5 s viiveen jälkeen, aina havaintoaikaleiman kanssa.

### Palon leviäminen on käsikirjoitettu, ei simuloitu

Ajoaikainen leviämismalli rikkoisi kolme asiaa kerralla: determinismin (liukuluvut eroavat selainten välillä), tapahtuma-ajoituksen (S08:n on osuttava sekunnilleen samaan hetkeen kaikilla) ja validoinnin (kukaan ei hyväksy mallia, jonka tulos riippuu osallistujan toimista). Rintama on siksi **aikaleimattu polygonisarja** — yksi kehä per simulaatiominuutti — tuotettuna offline maastotietoisella mallilla ja käytännön asiantuntijoiden hyväksymänä.

Paikallinen seuraus säilyy silti: osallistujan päätökset eivät liikuta rintamaa, mutta ne ratkaisevat **mitä rintama kohtaa** — onko linja pidetty, onko murroslinja raivattu, onko saha suojattu, missä muodostelmat ovat.

## 05 · Sisältöputki ja validaattori

Työkirja kertoo itse, mikä edellisen version tappoi: välilehdet ajautuivat erilleen toisistaan. Ihminen ei pysty ylläpitämään sitä invarianttia kolmenkymmenen välilehden yli kuukausien ajan. Kone pystyy — siksi validaattori on komponentti, ei työkalu, ja se on vaiheen 1 toimitus.

`Excel` → `YAML (versionhallinnassa)` → `validaattori` → `content-pack.json + hash`. Excel pysyy kirjoitusalustana, koska ohjaajat lukevat sitä. YAML on totuus buildille, koska siitä saa diffit ja katselmukset.

#### Validaattorin kovimmat säännöt

| # | Sääntö | Mitä se estää |
|---|---|---|
| R3 | Ikkunoiden summa + jäädytykset = 98 min | Aritmetiikkavian, joka löytyi jo kerran auditissa |
| R4 | Uncued ⇒ ei palkkia, ei countdownia, ei aikajanamerkintää | Negatiivisen vihjeen mittarin tuhoutumisen |
| R5 | SPAM-osio kaikkien ikkunoiden ulkopuolella — myös näkymättömien | Koettimen kilpailun mitattavan päätöksen kanssa |
| R6 | Mikään ei ennakoi jäädytystä tai koetinta | Mittarin muuttumisen harjoitteluksi |
| R9 | S08:n esioireella ≥ 3 kyselypolkua | Havaintoviiveen muuttumisen ajoituksen tuuriksi |
| R11 | Ehto A ei tavoita perustelu- eikä luottamuskenttää millään ajanhetkellä | Manipulaation vuotamisen |
| R12 | Takamaasto palauttaa ≤ N merkintää ennen 1:01 | S10:n hiljaisen täyttämisen |
| R13 | Ei ohjaustapahtumaa välillä 0:48–1:11 | Mitattavan hiljaisuuden rikkoutumisen |
| R16 | Uusinta ei paljasta haaraa | Sokkokoodauksen pilaantumisen |

### Kuusi ristiriitaa, jotka validaattori löytää työkirjasta tänään

Yksikään ei näy yhdeltä välilehdeltä. Kaikki ovat halpoja korjata nyt ja kalliita korjata pilotin jälkeen.

#### V-1 · Kolmen haaran termistö elää yhä kolmella välilehdellä

*Peer Wiki Content* puhuu ryhmästä C, *Agent Spec* sanoo *Group C sees these; groups A and B do not*, ja *Development Spec* määrittelee wikin renderöinnin muodossa *none / summary / full*. Päätös 21.8. on kaksi haaraa: A = vakiotieto, B = A + perustelu ja luottamus.

**korjaus** Korvaa kaikki C-viittaukset ja kolmiportainen renderöinti muodolla `standard / +rationale`. Tämä on rakennusvirhe odottamassa tapahtumistaan: kehittäjä toteuttaisi kolme tasoa.

#### V-2 · SPAM-osio 1 on päätösikkunan sisällä

Master Timeline sijoittaa osion hetkeen 0:10 merkinnällä *in the gap before S03*. S02:n ikkuna on 0:08–0:12 — osio osuu sen keskelle, vastoin aikajanan omaa sääntöä.

**korjaus** Siirrä S03:n alku 0:14:ään ja SPAM 1 hetkeen 0:12:45. Vaatii aikajanan uudelleenlaskennan — juuri siksi aikajana on yksi tiedosto.

#### V-3 · G-02 on merkitty annettavaksi S06:ssa, joka on uncued

Master Timelinellä ei ole ohjaustapahtumaa S06:ssa. Jos G-02 lähetettäisiin verkkoon, se olisi vihje siitä että S06:ssa tapahtuu jotain — ja tuhoaisi koko negatiivisen vihjeen mittarin.

**korjaus** G-02 on **voimassa oleva rajoitetila**, joka on ohjauspaneelissa S05:stä lähtien. Mitään ei lähetetä S06:ssa.

#### V-4 · SPAM-osio 3 osuu S06:n näkymättömän ikkunan päätepisteeseen

Osio on 0:44, ikkuna 0:36–0:44. Sääntö *vain ikkunoiden väleissä* kirjoitettiin näkyviä ikkunoita ajatellen, mutta uncued-ikkuna on mittaava ikkuna siinä missä muutkin: koetin juuri sen sulkeutuessa voi joko herättää huomaamaan hiljaisuuden tai peittää sen.

**korjaus** Siirrä 0:45:een — tai poista ja siirrä tason 3 mittaus jäädytykseen F2.

#### V-5 · Esioire ei ole S07:n aikana, vaikka aikajana niin selittää

Esioire on 0:40; S07:n ikkuna on 0:34–0:39. Kirjoitettu perustelu — että varoitus saapuu kesken toista tehtävää — on oikea, mutta luvut eivät tue sitä.

**korjaus** Pidennä S07:n ikkuna 0:41:een. Silloin esioire saapuu kesken aktiivista tulkintatehtävää, mikä on juuri se realismi jota selitys tavoittelee.

#### V-6 · Kaksi mittaria viittaa käyttöliittymään jota ei enää ole

`wiki_open_count` ja `wiki_dwell_ms` ovat jäänteitä erillisestä wiki-paneelista. Päätös 21.8. yhdisti naapurit, IR:n ja ohjauksen yhdeksi kyselypinnaksi, joten näillä muuttujilla ei ole lähdettä.

**korjaus** Korvaa muuttujalla `rationale_query_count` ja jo listalla olevalla `answer_dwell_ms`.

> [!NOTE]
> **Sisältötyö on kriittisellä polulla vähintään yhtä paljon kuin koodi.** Tekemättä on ~60 korpusmerkintää, ~180 häiriösyöttiä, ~70 optiota LCES-tiloineen, 12 SPAM-osiota, ~40 SAGAT-osiota ja ~120 radioviestiä äänityksineen: 10–14 viikkoa osa-aikaisena. Laatuankkurit vaativat asiantuntijatyöpajan, ja niillä on koko projektin pisin läpimenoaika — aloita niistä.

## 06 · Kartta: prototyypistä instrumentin renderöijäksi

`harjulakartta.html` on hyvä prototyyppi ja väärä ajoaikainen ratkaisu. Se on tehnyt vaikeimman osan — löytänyt parametrit, joilla generoitu maasto näyttää suomalaiselta — ja se on jo yhteensopiva skenaarion maailman kanssa.

| Prototyypissä | Arvio | Toimenpide |
|---|---|---|
| Deterministinen kenttä siemenestä | Oikein. Sama siemen, sama maasto | Siirretään sellaisenaan `packages/terrain` |
| Maasto ennen ihmisen jälkeä | Oikea kausaalijärjestys: tie kulkee harjulla koska harju on ensin | Pidetään |
| Peruskarttagrafiikka | Käytännön asiantuntija tunnistaa lajityypin sekunnissa | Siirretään leipomisskriptiin |
| Kaksi mittakaavaa, sektori 4 × 4 km | Vastaa täsmälleen suunniteltua maailmaa | Pidetään |
| Generointi ajoaikana | **Mitattu: 1,54 s** pelkälle 470×470-luokitukselle, päälle korkeuskäyrät ja nimistö | Siirretään Node-buildiin; ajossa ladataan valmis PNG |
| Selainten välinen determinismi | `Math.exp`, `Math.hypot`, `Math.sin` ovat toteutuskohtaisia | Leivotaan assetiksi ja hashataan — sama kartta kaikille, myös kahden vuoden päästä |
| Maailma ja renderöinti samassa tiedostossa | `OPS` sisältää linjan, varalinjan ja naapurit — se on skenaariodataa | Puretaan sisältöpaketin piirteiden rekisteriksi |
| Ruudukon koordinaatit | Nelinumeroinen *itäkoordinaatti* 6820 ei ole mahdollinen TM35FIN:ssä | Oikea affiini muunnos, uskottava fiktiivinen origo |
| Havaintokerros | Puuttuu: kartta piirtää kaiken minkä tietää | Kolmikerroksinen canvas, vanhentuneisuushaalennus |

> [!NOTE]
> **Realismivalidointiportti.** Sama portti kuin polttoaineparametreilla: kolme kokenutta kaistanjohtajaa, yksi kysymys — *voisiko tämä olla peruskarttalehti, ja voisiko palo käyttäytyä näin tällä maastolla?* Sen lisäksi konetarkistukset joka leivonnalla: harjun reliefi ≥ +18 m, linjan solut 100–110 m, kohde linjan eteläpuolella 0,7–1,1 km, nolla tie- tai rakennussolua vedessä.

## 07 · Mittaus ja lokitus

Instrumentti ei kirjoita mittaustuloksia. Se kirjoittaa tapahtumia, ja jokainen analyysin muuttuja johdetaan niistä skriptillä. Uusinta on mahdollinen, muuttujan määritelmä voidaan vaihtaa jälkikäteen ilman uutta aineistonkeruuta, ja loki on auditoitavissa.

#### Otsikkomittarit ja niiden johtaminen

| Muuttuja | Johtaminen tapahtumista |
|---|---|
| detection_latency_s | Ensimmäinen itään, KILOon tai säähän kohdistuva kysely tai radiovihjeen jälkeinen toiminta, mitattuna taaksepäin hetkestä 0:48 |
| precursor_route | kysely · radio · ei havaintoa. Havaintoviive raportoidaan reitin mukaan ehdollistettuna — muuten ajoituksen tuuri sekoittuu mittariin |
| adaptation_latency_dp | Päätöspisteitä S08:sta ensimmäiseen kalibroituun poikkeamaan |
| requery_interval_s | Mediaani simuloitu aika samaa aihetta koskevien kyselyjen välillä. **Korvaa kyselymäärän** tiedonhaun otsikkomittarina |
| stale_belief_flag | Osallistuja toimii tiedolla, joka haettiin ennen sen korvaamista |
| comparable_query_count | Vain kentät, jotka molemmilla ehdoilla on. H2.3 ajetaan vain tällä, muuten vertailu on kehämäinen |
| time_remaining_at_commit | Countdown-tilasta commitin hetkellä — erottaa varhaisen päättäjän takarajapäättäjästä |
| non_decision | Oletussääntö laukesi. **Ei puuttuva arvo** vaan oma rivinsä syineen |

### Kaksi asiaa, jotka on ratkaistava koodissa eikä analyysissa

**Sokkokoodaus on rakennusvaatimus.** Koodaaja ei saa päätellä haaraa: ohjauspaneelin sanamuoto normalisoidaan, estetyt optiot renderöidään kuten estämättömät, kyselylokista poistetaan perustelu- ja luottamuskentät. Tämä unohtuu helposti ja huomataan vasta kun koodaus on tehty ja pilattu — siksi siitä on automaattitesti, joka vertaa saman päätöksen uusintaa molemmista haaroista.

**Istunto ei saa hävitä.** 157 minuuttia kurssikohortista rekrytoidun osallistujan aikaa on kalleinta mitä tässä projektissa voi menettää. Append-only jono IndexedDB:hen, tilannekuva 30 sekunnin välein, lataus hash-varmennuksella. Testi: katkaise verkko kesken istunnon, jatka 20 minuuttia, palauta verkko — nolla hävinnyttä tapahtumaa, nolla duplikaattia.

## 08 · Vaiheet, riskit ja se mitä sinun pitää päättää

Vaihe 1 ei sisällä yhtään manipulaatiota. Jos kello, maailma ja loki eivät ole deterministisiä ja täydellisiä, mikään vaiheen 2 asia ei ole mitattavaa — se vain näyttää siltä.

#### Vaihe 1 · Ajettava tapahtuma

*≈ 8 viikkoa*

- Skenaariomoottori — täysi ajo kahdesti identtisesti, hashit täsmäävät
- Kaksikerroksinen maailma + havaintoportti
- Maastoputki, molemmat mittakaavat
- Päätöspalkki + countdown
- Oletustoimintamoottori — nollasyötteen ajo tuottaa 15 ei-päätöstä
- Aikaindeksoitu korpus
- Lokitus + verkkokatkon kestävä lataus
- **Sisältövalidaattori CI:ssä**

#### Vaihe 2 · Manipulaatiot ja mittarit

*≈ 8 viikkoa*

- Kyselyrakentaja + vapaa teksti
- Ehtoportti A / B, vuototestattuna
- Ohjauskerros, estot ja kitkallinen ohitus
- Uncued-käsittely S06 ja S08
- SPAM + kolme jäädytystä, kanavat todistettavasti lukossa
- Projektio-oraakkeli tason 3 rehelliseen pisteytykseen
- Vastausten aikaleimaus ilman yhtään ilmoitusta

#### Vaihe 3 · Tutkijan työkalut

*≈ 4 viikkoa*

- Tutkijakonsoli: käynnistä, tauko, merkitse, keskeytä
- Uusinta ja sokkokoodausnäkymä
- Vienti + manifest (sisältö-, skeema- ja karttaversio)
- Harjoitustapahtuma omana sisältöpakettinaan
- Loppukysely ja alueen tunnistamisosio

### Kuusi testiä, joita tavallinen sovellus ei joudu läpäisemään

| Testi | Miten | Miksi |
|---|---|---|
| Determinismi | Aja ydin headlessina 100× samalla siemenellä, vertaa tapahtumavirran hashia | Ilman tätä ehtojen keskiarvot eivät ole vertailukelpoisia |
| Kultainen ajo | Tallennettu syötesarja + odotettu tapahtumavirta versionhallinnassa | Havaitsee, jos sisältömuutos muuttaa vahingossa toista pistettä |
| Nollasyöte | Ajo ilman yhtään syötettä | Todistaa, että oletustoiminta kattaa kaikki 15 pistettä |
| Vuoto | Greppaa verkkoliikenne ja `window`-puu totuuskerroksen tunnisteiden varalta | Manipulaation eheys |
| Sokko | Generoi uusinta molemmista haaroista samalle päätökselle, diffaa | Sokkokoodauksen kelpoisuus |
| Aikajana | Validaattorin säännöt jokaisella buildilla | Estää välilehtien eriytymisen |

### Kolme riskiä, jotka arkkitehtuuri kantaa — ja kolme, joita se ei

| Riski | Vastaus |
|---|---|
| Sisällön eriytyminen | Validaattori vaiheessa 1, CI:ssä, buildin pysäyttävänä |
| Istunnon menetys tekniseen vikaan | Append-only jono, 30 s tilannekuva, offline-first, palautus |
| Ominaisuuden hiipiminen (uusi *avulias* ilmoitus) | Säännöt R4, R5, R6 ja R13 automaattitesteinä; ilmoitukset kiellettyjä oletuksena |
| Rekrytointi: 136 kaistanjohtajaa | **Ei arkkitehtuurin ratkaistavissa.** Vahvista kohorttikoot ennen neljään soluun sitoutumista; varamalli on kaksi haaraa |
| Päätöksen laadun reliabiliteetti | **Ei arkkitehtuurin ratkaistavissa.** Esirekisteröity varasuunnitelma: pudota ensisijaisista jos ICC < 0,60 |
| Sisältötyö myöhästyy | **Osittain.** Sisältö on dataa eikä koodia, joten se voi valmistua rinnalla — mutta laatuankkureiden läpimenoaikaa ei voi lyhentää |

### Päätökset, jotka estävät rakentamisen

| # | Kysymys | Suositus |
|---|---|---|
| T-1 | XVR vai erillinen selaininstrumentti? | **Erillinen instrumentti.** Yksikään mittausvaatimus ei ole XVR:n kautta luotettavasti toteutettavissa, eikä 3D-immersio ole mittarin kannalta tarpeen. Jos XVR on institutionaalisesti pakollinen, käytä sitä vain harjoituslohkossa |
| T-2 | Kaistanjohtajat, yksikönjohtajat vai molemmat? | **Kaistanjohtaja.** Koko maailma on rakennettu sille tasolle; kahden echelonin sekoittaminen tuo varianssia jota ei voi mallintaa |
| T-4 | Milloin armeijapaketti aloitetaan? | Uhkamallin **rajapinta vaiheessa 1** joka tapauksessa. Sisältö vasta pelastusdomainin pilotin jälkeen. Rajapinnan jättäminen tekemättä maksaa myöhemmin uuden projektin verran |
| T-6 | Hyväksytäänkö kuuden ristiriidan korjaukset? | Korjaa kaikki **ennen** sisällön kirjoittamista. Aikajanan siirtäminen maksaa nyt tunnin ja pilotin jälkeen viikon |

### Ensimmäiset kaksi viikkoa

1. **Päätä T-1.** Kaikki muu riippuu siitä.
2. **Korjaa aikajana** (V-2, V-4, V-5) ja poista kolmen haaran termistö (V-1). Yksi iltapäivä, sinun työtäsi.
3. **Ota yhteys käytännön asiantuntijoihin.** Pisin läpimenoaika koko projektissa.
4. **Pystytä sisältöputki:** Excel → YAML → validaattori → CI. Ensimmäinen ajo saa olla punainen — se on todiste siitä, että se toimii.
5. **Leivo maasto** prototyypin funktioista ja aja konetarkistukset.
6. **Kirjoita S05, S09 ja S10 kokonaan.** Ohjauskonflikti, ensisijainen häiriönjälkeinen piste ja tyhjä sektori kattavat kaikki mekanismit. Jos ne toimivat, loput on toistoa.

Lähteet: PhD_Simulation_Scenarios_P2P3_1.xlsx (30 välilehteä, 21.8.2026) ja harjulakartta.html (siemen 20260821). Maastogeneraattorin suorituskykyluku mitattu irrottamalla kenttäfunktiot Nodeen: 470 × 470 luokitusruudukko 1,54 s.

Kaikki paikannimet ja organisaatiot ovat kuvitteellisia. Suunnitelmadokumentit kokonaisuudessaan: hakemisto `pelastussimulaatio/`.
