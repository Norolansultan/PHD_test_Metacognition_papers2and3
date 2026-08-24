# 0. Vaikutusanalyysi — mitä päivitetty väitöskirjasuunnitelma muuttaa

Elokuun 2026 väitöskirjasuunnitelma ei ole päivitys aiempaan rakennussuunnitelmaan. Se vaihtaa
tutkimuksen rakenteen, ensisijaisen domainin, koeasetelman, mittausapparaatin ja toimitustavan.
Tämä dokumentti kertoo mikä muuttui, mitä siitä seuraa toteutukselle, mitkä ristiriidat jäivät
ratkaistavaksi ja miten ne on tässä paketissa ratkaistu.

Lue tämä ennen muita dokumentteja. Muut on kirjoitettu uudelleen tämän mukaisiksi.

---

## 0.1 Rakenteellinen muutos

| | Aiempi rakennussuunnitelma (työkirja) | Päivitetty väitöskirjasuunnitelma |
|---|---|---|
| Rakenne | Paperit 2 ja 3 ristiin yhdessä simulaatiossa | Kaksi keruuta, neljä paperia (1, B, A, D) |
| Ensisijainen domain | Pelastus | **Armeija** (Tutkimus I, ~100 osallistujaa) |
| Pelastuksen rooli | Koko tutkimus | **Tutkimus II:n sisältöpaketti** (paperi A, CATCH) |
| Osallistujat | 136 kaistanjohtajaa, 4 solua | ~100 armeijasta; suunnittele 80 käyttökelpoiselle |
| Toimitus | XVR Pelastusopistolla, valvottu istunto | **Selain, etäosallistuminen omalla laitteella** |
| Tekoälykanava | Käsikirjoitettu korpus + kyselyrakentaja | **Projektiomoottori**, vapaa tekstisyöte, LLM vain jäsentää |
| Manipulaatio (Tutkimus I) | — | Ihmisvälitteinen vs. **AI-välitteinen komentoketju** |
| Manipulaatio (Tutkimus II) | Wiki-pääsy × ohjauksen sitovuus | Ei sosiaalista tietoa / **vertaispäätökset raakana** / **vertaispäätökset projektion syötteenä** |
| Häiriö | Tuulen käännös mitätöi ohjauksen ja ennakkotapaukset | **Virheinjektio** kahtena erillisenä tyyppinä + epämääräinen radiokäsky |
| Tilannetietoisuus | SPAM ensisijaisena (CATCH), 3 SAGAT-jäädytystä | **Metakognitio ensisijaisena**: meta-d′, Brier, M-ratio |
| Päätöksen laatu | LCES-portti + 5 ulottuvuutta, ICC-portti | Ei ensisijainen. Korvautuu **ajautumamittarilla** |
| Kehystys | — | **Havaitsemisen ja suojautumisen näkökulma, ei huomaamattomuuden** |

## 0.2 Mikä aiemmasta suunnitelmasta säilyy

Neljä asiaa kestivät muutoksen, ja ne kannattaa tunnistaa, koska ne ovat kalleimmat rakentaa:

1. **Domain-neutraali ydin ja sisältöpakettimalli.** Uusi rakenne vaatii kaksi domainia yhdellä
   alustalla, joten ratkaisu ei vain kestä muutosta — se on nyt pakollinen. Uhkamallin rajapinta
   (etenevä palo / etenevä vastustaja) on edelleen se yksi asia, joka pitää toisen domainin
   kustannuksen sisällöntuotannossa.
2. **Yksi kello ja aikaperusta.** Kaikki skenaarioaikaan, kello pysähtyy jäädytyksessä, ja
   jäädytyksen aikana pysähtyy myös kyselymahdollisuus. Päivitetty suunnitelma vaatii tämän sanasta
   sanaan samoin.
3. **Kaksikerroksinen maailma ja havaintoportti.** "Ruudun pimennys on pakollinen: ilman sitä
   osallistuja lukee vastauksen kartalta" on sama vaatimus kuin totuus- ja havaintokerroksen
   erottaminen, ja etäkeruussa se on teknisesti vaikeampi.
4. **Determinismi ja assettien leipominen.** Etäkeruu omilla laitteilla tekee tästä tiukemman, ei
   löysemmän: nyt selainkirjo on hallitsematon, joten ajoaikainen maastogenerointi on lopullisesti
   pois laskuista.

## 0.3 Mikä poistetaan suunnitelmasta

Nämä on nyt poistettu dokumenteista, jottei kukaan rakenna niitä vahingossa:

| Poistettu | Miksi |
|---|---|
| XVR kokonaan | Ympäristö rakennetaan itse; etäosallistuminen on koko mitoituksen mahdollistaja |
| Ohjauksen sitovuus (neuvova/sitova), optioesto, ohituskitka | Vanha paperi 4 sulautui paperiin B; ero on esitystavassa, ei pakottavuudessa |
| Wiki-ehdot A/B ja perustelu- ja luottamuskentät | Tutkimus II:n manipulaatio on sosiaalisen tiedon **kanava**, ei perustelun saatavuus |
| Kiinteä 2,5 s kyselyviive | Suora ristiriita uuden <300 ms vaatimuksen kanssa. Ks. **K-1** |
| LCES-portti ensisijaisena pisteytyssääntönä | Päätöksen laatu ei ole enää ensisijainen mittari. Säilyy sisällön ominaisuutena |
| SPAM ensisijaisena SA-mittarina | Metakognitio on ensisijainen; SA-tasot ovat mittausvälineitä, eivät juonta |
| 136 osallistujaa, neljä solua | Mitoitus tulee nyt hmetad-palautussimulaatiosta |
| Päätöspalkin näkyvä countdown | Kuului aikapainemanipulaatioon, jota ei enää ole. Tapahtuman kello jää, jäljellä oleva aika lokitetaan |
| Tutkijakonsoli huoneessa | Korvautuu **etähallintanäkymällä**: istuntojen tarkastelu kesken keruun |

## 0.4 Ratkaisua vaatineet ristiriidat

Kuusi kohtaa, joissa päivitetty suunnitelma on joko itsensä tai vanhan suunnitelman kanssa
ristiriidassa. Jokaiselle on tehty ratkaisu, joka näkyy muissa dokumenteissa. Jos et hyväksy
ratkaisua, se muuttuu yhdessä paikassa eikä seitsemässä.

### K-1 · Vasteaika: 2,5 s vs. alle 300 ms

Vanha suunnitelma peri kyselystä kiinteän 2,5 sekunnin viiveen, jotta kysymisellä olisi
aikakustannus. Uusi suunnitelma vaatii kuittauksen alle 300 ms:ssä, koska "aikapaineen alla tyhjä
odotus on sekä ärsyke että sekoittava tekijä".

**Ratkaisu: uusi vaatimus voittaa.** Keinotekoinen viive poistetaan. Kysymisen kustannus ei
kuitenkaan katoa, se vain siirtyy: skenaarion kello käy koko ajan, ja kysymyksen **muotoilu** vie
aikaa ja työmuistia. Seuraus, joka on kirjattava: kyselymäärä nousee verrattuna vanhaan malliin,
eikä sitä voi enää tulkita "hakuhalukkuutena aikakustannusta vastaan". Kyselykäyttäytymisen mittarit
painottuvat siksi ajoitukseen, kohteeseen ja uudelleenkysymiseen — ei määrään.

### K-2 · LLM jäsentää, mutta vastausten pitää olla identtisiä

Uusi suunnitelma antaa LLM:lle tasan kolme tehtävää: jäsennä kysymys parametreiksi, aja malli, esitä
tulos. Samalla vaaditaan, että sama what-if tuottaa saman vastauksen jokaiselle. Kielimalli ei ole
deterministinen, joten vaatimukset eivät sellaisenaan sovi yhteen.

**Ratkaisu: determinismi taataan kolmella tasolla, ja luvataan täsmälleen se mikä pystytään.**

1. **Sääntöpohjainen jäsennin ensin.** Suurin osa kysymyksistä osuu kapeaan muottiin ("kauanko
   komppanialta kestää siirtyä X:ään", "mitä tapahtuu jos vihollinen etenee Y:tä pitkin").
   Deterministinen slot-jäsennin kattaa ne ilman mallia lainkaan.
2. **LLM vain varajäsentimenä**, lämpötila 0, ja **jäsennystulos välimuistitetaan normalisoidun
   kysymystekstin avaimella**. Sama teksti tuottaa samat parametrit kaikille osallistujille koko
   keruun ajan, myös eri päivinä.
3. **Malli on aina deterministinen.** Samat parametrit + sama siemen → sama tuloste, poikkeuksetta.

Se mitä **ei** voi luvata: kaksi eri tavalla muotoiltua kysymystä voivat jäsentyä eri parametreiksi.
Tämä on mitattava eikä piilotettava — jäsennysvarmuus ja käytetty reitti (sääntö / LLM / välimuisti)
lokitetaan, ja jäsennysvaihtelu raportoidaan menetelmäosassa.

### K-3 · Koetinbudjetti: 50–80 per ehto — per osallistuja vai yhteensä?

Mitoitustaulukko sanoo "Skenaario, per ehto: 50–80 koettelua → ryhmätason ehtovertailu", ja
kalibraatiopatteri erikseen "200–400 → yksilötason M-ratio". Luettuna kirjaimellisesti ryhmätason
vertailuun riittää 50–80 koettelua **koko ehdossa yhteensä**, mikä 40 osallistujalla ehtoa kohti
tarkoittaisi kahta koetinta osallistujaa kohti. Se on ristiriidassa saman luvun ohjeen kanssa
"monta pientä koetinta, ei harvoja isoja".

**Ratkaisu: rakenna tiukemman lukutavan mukaan, jolloin molemmat täyttyvät.** Tavoite on
**15–25 koetinta osallistujaa kohti** skenaariossa, mikä 60–90 minuutin skenaariossa tarkoittaa
koetinta noin 3–4 minuutin välein. Se antaa 600–1000 koettelua ehtoa kohti eli ylittää alarajan
kummallakin lukutavalla, tuottaa mielekkään kuormakäyrän ja tekee ehtojen sisäisestä ajallisesta
kehityksestä analysoitavan. Yksilötason meta-d′ tulee silti vain patterista.

### K-4 · Reaktiivisuuskontrolli maksaa otosta

Harva-koetin-kontrolliehto on oikea lievennys, mutta ristiin pääasetelman kanssa se puolittaisi
solut sadan osallistujan otoksessa.

**Ratkaisu: harva-koetin-ryhmä ei ole ristiin.** Erillinen pieni ryhmä (n ≈ 20), joka saa 2–3
koetinta koko session ja jota käytetään **vain** reaktiivisuuden tarkistukseen: eroaako heidän
käyttäytymisensä (kyselytiheys, verifiointi, päätösviive) tiheästi koeteltujen vastaavista.
Lisäksi proxy-painotus tiukan tempon osuuksissa. Molemmat, ei toinen — kustannus on 20 osallistujaa,
ja ilman sitä koko luottamusmittaus on avoin sille väitteelle, että mittaaminen tuotti tuloksen.

### K-5 · Kanavakoherenssi kietoo vaiheet 1 ja 2

Kanava pysyy vakiona osallistujan sisällä, joten paperien 1 ja B manipulaatiot eivät ole toisistaan
riippumattomia. Päivitetty suunnitelma hyväksyy tämän ja nimeää muuttujan uudelleen.

**Ratkaisu on jo suunnitelmassa ja se on oikea**, mutta sillä on toteutusseuraus, joka on kirjattava:
**ehto määrätään istunnon alussa ja se on muuttumaton**. Ei ehdon vaihtoa vaiheiden välillä, ei
tutkijan mahdollisuutta korjata ehtoa kesken istunnon, ja ehto on lokin ensimmäisellä rivillä.
Alusta ei saa edes teknisesti kyetä vaihtamaan kanavaa kesken session.

### K-6 · Vedetty ohjaus ja itsevalikoituva altistuminen

Projektio saapuu vain kysyttäessä, joten kysymättä jättävät eivät altistu ja satunnaistus rikkoutuu.
Päivitetty suunnitelma antaa kolme ratkaisua järjestyksessä.

**Ratkaisu: kaikki kolme ovat rakennusvaatimuksia, eivät vaihtoehtoja.**

1. **Pakotettu kysymyshetki** on skenaarion rakennepiirre: haarautuma, jossa kaksi yhtä uskottavaa
   suuntaa ja riittämätön tieto valita. Tämä on maaston suunnitteluvaatimus (ks. dokumentti 4) eikä
   käyttöliittymän ominaisuus.
2. **Radiovarmistus**: jos kysymystä ei ole tullut hetkeen T mennessä, sama ohjaus saapuu radiossa.
   Lokiin `guidance_route: query | radio_fallback`.
3. **Kysymiskäyttäytyminen on mittari**, ei vain altistumisen ehto — se on metakognitiivinen
   kontrollipäätös ja kerätään joka tapauksessa.

Analyysiseuraus: altistumisreitti on kovariaatti kaikissa vaiheen 2 malleissa. Radiovarmistuksen
kautta altistuneet eivät ole sama ryhmä kuin itse kysyneet, vaikka molemmat saivat saman sisällön.

## 0.5 Avoimet kysymykset, joita en voi ratkaista puolestasi

| # | Kysymys | Miksi se on auki | Mitä se estää |
|---|---|---|---|
| A-1 | **Armeijadomainin echelon**: komppania, pataljoona vai jokin muu? | Päivitetty suunnitelma ei nimeä sitä. Vanha paperi 1 oli pataljoonan komentajia KESI:llä MPKK:lla | Maasto, mittakaava, käskyjen sanamuoto, siirtymänopeudet, koko Tutkimus I:n sisältö |
| A-2 | **Onko Tutkimus II pelastus vai armeija?** | Suunnitelma sanoo "pelastus tai armeija" | Toisen domainin sisältötyön aloituksen. Suositus: **pelastus** — se on jo kuvattu, ja se antaa väitöskirjalle kahden regiimin vertailun, joka on paperin D siirrettävyysväitteen ainoa empiirinen tuki |
| A-3 | **Menetetäänkö "pääsy päättelyyn" -konstrukti tarkoituksella?** | Tutkimus II:n uudet ehdot koskevat sosiaalisen tiedon kanavaa, eivät perustelun saatavuutta. Vanha vastaus kysymykseen "miten tämä eroaa SITREP-raportoinnista" katoaa | Ei estä rakentamista, mutta arvioija esittää tämän kysymyksen. Ratkaise se ennen esirekisteröintiä |
| A-4 | **CATCHin oma No AI / Static AI / Adaptive AI -vertailu** | Jos CATCH odottaa omia ehtojaan Tutkimus II:een, asetelma saa kolmannen tekijän jota se ei kanna | Tutkimus II:n solurakenteen |
| A-5 | **Avoimen L3-koettimen toinen koodaaja** | Semanttinen etäisyys ja kappa vaativat resurssin, joka ei ole vielä olemassa | Avoimen koettimen analyysin. Ratkaistava ennen keruuta, ei sen jälkeen |
| A-6 | **CMO:n maasotaosuuden uskottavuus** | Parametrien lähde koko projektiomoottorille | Mallin puolustettavuuden menetelmäosassa. Kysy Salmiselta ennen kuin parametreja lyödään lukkoon |
| A-7 | **Virheinjektio Tutkimus II:ssa** | Pystysuoran käskyn vääristymällä ei ole suoraa vaakasuoraa vastinetta | Lokitusliput ja jälkiselvityksen sisällön. Ehdotus ja vaihtoehto dokumentissa 6.9 |

## 0.6 Kehystyssääntö on myös rakennussääntö

"Kysymys on milloin ihminen havaitsee tulleensa ohjatuksi, ei miten ohjaus saadaan
huomaamattomaksi." Tämä ei koske vain tekstiä, jota kirjoitat. Se koskee myös järjestelmää:

* **Havaitsemismittarit rakennetaan ennen manipulaatiota**, ei sen jälkeen. Ilman
  attribuutiopatteria virheinjektio on manipulaatiokoe ilman mittaria.
* **Jokaisen osallistujan altistus on jälkikäteen rekonstruoitavissa lokista täsmällisesti**:
  mikä projektio, millä virhelipulla, mikä käsky, mikä vääristymän suunta ja suuruus. Tämä on
  jälkiselvityksen ja eettisen toimikunnan vaatimus, ei mukavuus.
* **Jälkiselvitysnäkymä on osa ohjelmistoa**, ei erillinen paperi tutkijan kansiossa. Istunnon
  päätteeksi osallistujalle kerrotaan, mitä manipuloitiin ja miten hänen omat päätöksensä
  suhteutuivat alkuperäiseen käskyyn.

Käytännön seuraus koodissa: virheinjektion lokitus on ensimmäisen luokan ominaisuus, ja
jälkiselvitysnäkymä on vaiheen 1 toimitus — ei viimeisen viikon lisä.
