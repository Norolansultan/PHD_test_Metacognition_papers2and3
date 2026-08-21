# 6. Toteutussuunnitelma, testaus, riskit ja avoimet päätökset

---

## 6.1 Vaiheistus

Vaiheet noudattavat työkirjan `Development Spec` -jakoa, mutta järjestys on tiukempi: **vaihe 1 ei
sisällä yhtään manipulaatiota.** Jos kello, maailma ja loki eivät ole deterministisiä ja
täydellisiä, mikään vaiheen 2 asia ei ole mitattavaa — se vain näyttää siltä.

### Vaihe 1 — Ajettava, deterministinen tapahtuma (n. 8 viikkoa)

| Komponentti | Valmis kun |
|---|---|
| Skenaariomoottori | Täysi 15 pisteen ajo suoriutuu **kahdesti identtisesti** samalla siemenellä ja samalla syötesarjalla; hashit täsmäävät |
| Kaksikerroksinen maailmamalli + havaintoportti | Totuuskerros ei ole saavutettavissa osallistujan buildissa millään reitillä (automaattitesti) |
| Maastoputki | Molemmat karttanäkymät regeneroituvat bittitarkasti siemenestä ja putkiskripteistä; manifestin hashit täsmäävät |
| Kaksi mittakaavaa | Jokainen näkymänvaihto lokittuu ajan ja viipymän kanssa; zoomaus ei paljasta havaitsematonta |
| Päätöspalkki + countdown | Latenssi, optioiden katselu ja jäljellä oleva aika näkyvät lokissa oikein |
| Oletustoimintamoottori | Täysi ajo **ilman yhtään syötettä** tuottaa 15 ei-päätöstä, 15 tilamuutosta ja 15 radioviestiä. Yksikään ikkuna ei sulkeudu hiljaa |
| Aikaindeksoitu korpus | Sama kysely kahtena eri simuloituna hetkenä palauttaa todistettavasti eri tuloksen, toistettavasti |
| Lokitus + lataus | Simuloitu verkkokatko ei hukkaa yhtään tapahtumaa eikä tuota duplikaatteja |
| **Sisältövalidaattori** | Ajaa CI:ssä; kaatuu punaisena dokumentin 3 kuudesta ristiriidasta ja vihreänä niiden korjauksen jälkeen |
| Uhkarajapinta `ThreatModel` | Palorintama toteuttaa rajapinnan; ydin ei tunne sanaa "palo" |

### Vaihe 2 — Manipulaatiot ja mittarit (n. 8 viikkoa)

| Komponentti | Valmis kun |
|---|---|
| Kyselyrakentaja (KUKA × MITÄ × MILLOIN) + vapaa teksti | Paikat lokittuvat erikseen; sama kysely samassa pisteessä palauttaa sanatarkasti saman tekstin kahdessa istunnossa |
| Ehtoportti (A / B) | Ehto A ei tavoita perustelu- eikä luottamuskenttää millään reitillä, myöskään URL-arvauksella tai verkkovastauksesta |
| Ohjauskerros | Estotapahtumat lokittuvat laukaisseen säännön kanssa; ohituspolku lokittuu vaiheittain; S13 avaa kaiken molemmissa haaroissa samalla tikillä |
| Uncued-käsittely | Osallistuja, joka ei tee mitään S06:ssa, tuottaa ei-päätöksen näkymättömällä ikkunalla, eikä mikään käyttöliittymässä vihjannut ikkunan olemassaolosta |
| Koetinjärjestelmä | Kanava todistettavasti saavuttamaton jäädytyksessä; jäädytyksen sisältö identtinen kaikissa neljässä solussa; arvottu osio lokittuu altaineen |
| Projektio-oraakkeli | Kaksi eri tietohistorian osallistujaa saavat eri hyväksyttävät vastaukset samaan tason 3 osioon, toistettavasti lokista |
| Vastausten aikaleimaus | Käytettävyystarkastus: osallistuja erottaa 5 min vanhan vastauksen 30 min vanhasta, eikä mikään kehota kysymään uudelleen |

### Vaihe 3 — Tutkijan työkalut ja pilottivalmius (n. 4 viikkoa)

| Komponentti | Valmis kun |
|---|---|
| Tutkijakonsoli | Tutkija ajaa istunnon koskematta osallistujan koneeseen |
| Uusinta ja koodausnäkymä | Koodaaja ei pysty päättelemään haaraa (testi vertaa haarojen uusintoja) |
| Vienti | Johdetut muuttujat toistuvat raakadatasta skriptillä, bittitasolla samoina |
| Harjoitustapahtuma | 3 harjoitusskenaariota eri kaistalla; `practice = TRUE`; sisältää esimerkin jossa **sama kysymys myöhemmin palauttaa enemmän** |
| Loppukysely | Luottamus, NASA-TLX, ohjauksen legitimiteetti, manipulaatiotarkistukset, **alueen tunnistamisosio** |

**Yhteensä n. 20 viikkoa** yhdellä kokopäiväisellä kehittäjällä, olettaen että sisältö valmistuu
rinnalla. Sisältötyö (dokumentti 3.5) on **10–14 viikkoa osa-aikaisena** ja se on kriittisellä
polulla vähintään yhtä paljon kuin koodi.

## 6.2 Testistrategia

Tavallinen yksikkötestaus ei riitä. Instrumentin on todistettava viisi asiaa, joita tavallinen
sovellus ei koskaan joudu todistamaan.

| Testi | Miten | Miksi |
|---|---|---|
| **Determinismitesti** | Aja ydin headlessina 100× samalla siemenellä ja samalla syötesarjalla; vertaa lopputilan ja koko tapahtumavirran hashia | Ilman tätä ehtojen keskiarvot eivät ole vertailukelpoisia |
| **Kultainen ajo (golden run)** | Yksi tallennettu syötesarja + odotettu tapahtumavirta versionhallinnassa; CI vertaa | Havaitsee, jos sisältömuutos muuttaa vahingossa jonkin muun pisteen käyttäytymistä |
| **Nollasyötteen ajo** | Ajo ilman yhtään syötettä | Todistaa, että oletustoimintamoottori kattaa kaikki 15 pistettä |
| **Vuotitesti** | Buildaa osallistujaversio, aja headless, greppaa verkkoliikenne + `window`-puu totuuskerroksen ja ehto B:n tunnisteiden varalta | Manipulaation eheys ja totuuskerroksen eristys |
| **Sokkotesti** | Generoi uusinta molemmista haaroista samalle päätökselle, diffaa | Sokkokoodauksen kelpoisuus |
| **Aikajanatesti** | Validaattori ajaa säännöt R1–R17 jokaisella buildilla | Estää välilehtien eriytymisen |

Lisäksi **käytettävyystarkastukset** (eivät automatisoitavissa): vanhentuneisuuden erottuvuus,
countdownin luettavuus vilkaisulla, ja se, ettei mikään käyttöliittymässä ennakoi koetinta.

## 6.3 Miehitys

| Rooli | Osuus | Tehtävä |
|---|---|---|
| Kehittäjä (senior, TS) | 100 % / 5 kk | Ydin, renderöijä, validaattori, työkalut |
| Sisällöntuottaja (sinä + avustaja) | 50 % / 3–4 kk | Korpus, optiot, koetinosiot, radiokäsikirjoitus |
| Käytännön asiantuntijat (3 kaistanjohtajaa) | Työpajat | Laatuankkurit, maaston ja palokäyttäytymisen realismiportti, optiojoukkojen tarkistus |
| Tilastotieteilijä | Konsultointi | Voima-analyysi pilotin jälkeen, esirekisteröinti |
| Ääni | 1–2 päivää | Radioviestien äänitys |

## 6.4 Riskit ja se, miten arkkitehtuuri vastaa niihin

| Riski | Vaikutus | Arkkitehtuurinen vastaus |
|---|---|---|
| **Sisällön eriytyminen** (tappoi edellisen työkirjan) | Tutkimus mittaa eri asioita eri välilehdillä | Validaattori vaiheessa 1, CI:ssä, buildin pysäyttävänä |
| **Sisältötyö myöhästyy** (70 % on pohjia) | Pilotti siirtyy, kaikki siirtyy | Sisältö on dataa, ei koodia: se voi valmistua rinnakkain ja viimeisenä. Aloita laatuankkureista |
| **Ajoituksen tuuri sekoittuu havaintoviiveeseen** | Paras ensisijainen mittari pilalla | Esioire 8 min etukäteen, ≥3 kyselypolkua, radiovihje ei-kyselyreittinä, `precursor_route` ehdollistavana muuttujana |
| **Lattiavaikutus kyselyissä** | Paperin 2 mekanismi kuollut | Kyselyrakentaja ensisijaisena; koulutus kriteeriin asti; pilotin go/no-go (mediaani ≥6 kyselyä, nollasta poikkeava käyttö 3/4 puutepisteessä) |
| **Päätöksen laadun reliabiliteetti jää alle 0,60** | Kaksi hypoteesia menee | Esirekisteröity varasuunnitelma: pudota mittari ensisijaisista ja nojaa käyttäytymismittareihin. Ankkurit asiantuntijoilta, ei teoriasta |
| **Voima ei riitä yhdysvaikutukselle** | Solu 4 jää eksploratiiviseksi | Rehellinen esirekisteröinti: päävaikutukset konfirmatorisia, yhdysvaikutus eksploratiivinen. Kaksihaarainen varamalli valmiina |
| **Rekrytointi (136 kaistanjohtajaa) ei toteudu** | Koko asetelma | Vahvista kohorttikoot Pelastusopistolta **ennen** neljään soluun sitoutumista; varamalli: vain neuvova ohjaus, kaksi haaraa |
| **Selainten välinen ero renderöinnissä** | Osallistujat näkevät eri kartan | Assettien leipominen + hash; sama selain ja versio lukittuna koko keruun ajaksi |
| **Istunnon menetys tekniseen vikaan** | Kalleinta mitä voi tapahtua | Append-only jono, 30 s snapshot, offline-first, palautus keskeytyksestä |
| **Ominaisuuden hiipiminen** (uusi hieno ilmoitus, avulias merkki) | Mittari tuhoutuu hiljaa | Säännöt R4, R5, R6, R13 automaattitesteinä. Kaikki "hyödylliset" ilmoitukset ovat kiellettyjä oletuksena |

## 6.5 Avoimet päätökset — nämä tarvitsevat sinun tai ohjaajien vastauksen

Työkirjan `OPEN DECISIONS` on yhä voimassa (#2, #3, #4, #5, #6, #7, #8, #9 auki). Tässä ne, jotka
**estävät rakentamisen** tai muuttavat arkkitehtuuria.

| # | Kysymys | Miksi se estää | Suositukseni |
|---|---|---|---|
| **T-1** | **XVR vai erillinen selaininstrumentti?** Työkirja sanoo asetelmaksi "XVR simulation environment at Pelastusopisto", mutta `Development Spec` vaatii selainpohjaista toimitusta, deterministisiä vastauksia sanatarkkuudella, optioestoja, näytön pimennystä jäädytyksessä ja tapahtumatason lokitusta. | Tämä on koko toteutuksen perusta. Väärä valinta huomataan vasta kun mittarit eivät toimi. | **Erillinen selaininstrumentti.** Yksikään yllä olevista vaatimuksista ei ole XVR:n kautta luotettavasti toteutettavissa, eikä 3D-immersio ole mittarin kannalta tarpeen — mitattava toiminta on kaistanjohtajan johtamiskäyttäytymistä kartan, radion ja tiedon äärellä. Jos XVR on institutionaalisesti pakollinen, käytä sitä **vain harjoituslohkossa** ja pidä mittaus omassa instrumentissa. |
| **T-2** | Kaistanjohtajat, yksikönjohtajat vai molemmat? (`OPEN DECISIONS` #2) | Muuttaa koko optiotaksonomian, ohjaustekstit ja ankkurit. | Valitse yksi. Optiojoukkoja ei voi kirjoittaa kahdelle tasolle ilman että varianssi kasvaa mallintamattomasti. Suositus: **kaistanjohtaja**, koska koko maailma on rakennettu sille tasolle. |
| **T-3** | Onko harjoitustapahtuma oma sisältöpakettinsa? | Vaikuttaa siihen, ostetaanko sisältöputkeen monipakettituki heti. | **Kyllä, oma paketti.** Se on halpa nyt ja se todistaa samalla domain-neutraaliuden ennen kuin armeijapaketti on olemassa. |
| **T-4** | Milloin armeijapaketti aloitetaan? | Määrää, tehdäänkö `ThreatModel`-rajapinta vaiheessa 1 vai myöhemmin. | Rajapinta **vaiheessa 1** joka tapauksessa. Sisältö vasta pelastusdomainin pilotin jälkeen. |
| **T-5** | Kuka omistaa radiokäsikirjoituksen äänityksen? | ~120 viestiä, studiopäivä, ja ääni on osa determinismiä. | Äänitä kerran, versioi tiedostot sisältöpaketin mukana. Ei TTS:ää ajoaikana. |
| **T-6** | Hyväksytäänkö dokumentin 3.4 kuuden ristiriidan korjaukset? | Aikajanan uudelleenlaskenta (V-2, V-4, V-5) koskettaa `Master Timelinea`, joka on kaiken muun lähde. | Korjaa kaikki kuusi **ennen** sisällön kirjoittamista. Aikajanan siirtäminen maksaa nyt tunnin ja pilotin jälkeen viikon. |

## 6.6 Ensimmäiset kaksi viikkoa — konkreettisesti

1. **Päätä T-1** (XVR vai erillinen). Kaikki muu riippuu siitä.
2. **Korjaa aikajana** (V-2, V-4, V-5) ja **poista kolmen haaran termistö** (V-1) työkirjasta.
   Tämä on sinun työtäsi, ei kehittäjän, ja se kestää yhden iltapäivän.
3. **Ota yhteys käytännön asiantuntijoihin.** Pisin läpimenoaika koko projektissa; portittaa
   laatuankkurit, maaston realismin ja polttoaineparametrit.
4. **Pystytä repositorio ja sisältöputki**: Excel → YAML → validaattori → CI. Validaattorin
   ensimmäinen ajo saa olla punainen — se on todiste siitä, että se toimii.
5. **Leivo maasto** prototyypin funktioista ja aja konetarkistukset (dokumentti 4.7).
6. **Kirjoita S05, S09 ja S10 kokonaan** — ohjauskonflikti, ensisijainen häiriönjälkeinen piste ja
   tyhjä sektori. Nämä kolme kattavat kaikki mekanismit; jos ne toimivat, loput on toistoa.
