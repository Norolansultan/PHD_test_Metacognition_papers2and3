# 5. Tutkimus I — armeija, paperit 1 ja B

Yksi jatkuva skenaario, ei keinotekoista vaiheistusta. **Vaiheraja syntyy itsestään siitä, milloin
ohjaus saapuu.** Tämä on ensimmäisenä rakennettava sisältöpaketti.

---

## 5.1 Rakenne

| | Vaihe 1 — paperi 1 | Vaihe 2 — paperi B |
|---|---|---|
| Tilanne | Hyökkäys alkaa, tilanne kehittyy | Radiokäsky: joukot vetäytyvät, siirtyminen alueelle X |
| Tietolähde | Vain alhaalta tuleva tilannetieto omilta yksiköiltä | Sama + ylhäältä tullut käsky |
| Manipulaatio | Ihmisvälitteinen vs. AI-välitteinen **tilannekuva** | Kuka tulkitsee epämääräisen käskyn: ihminen itse vai AI hänen puolestaan |
| Ryhmä 1 | Ihmisvälitteinen kuva | Jää oman tulkintansa varaan |
| Ryhmä 2 | AI-välitteinen kuva | Näkee tulkinnan tarkentuvan projektioissa, joita **itse pyytää** |

**Kanava on vakio osallistujan sisällä koko session.** Organisaatio ei vaihda välityskanavaa kesken
taistelun. Manipuloitava muuttuja ei siis ole "ohjauksen kanava" vaan **AI-välitteinen komentoketju
vs. ihmisvälitteinen komentoketju** — ehjä konstrukti, joka vastaa ydinkysymykseen paremmin kuin
yksittäisen viestin kanava.

## 5.2 Radiokäsky

**Sama hämärä käsky kaikille. Ei toistu.**

Tämä yksi valinta poistaa kolme sekoittunutta muuttujaa, jotka aiemmassa suunnitelmassa olivat
sisällä: työnnetty vs. vedetty ohjaus, eri ajoitus eri osallistujille, ja eri sisältö eri ehdoissa.
Se on myös ekologisesti tarkka: todellinen käsky on usein epämääräinen, ja komentajan työ on tulkita
se omaan tilanteeseensa. **Juuri tuo tulkintatyö on se, minkä tekoäly voi ottaa haltuunsa
huomaamatta.**

Käskyn kirjoitusvaatimukset:

* Epämääräisyys on **suunniteltua ja mitattua**: pilotissa varmistetaan, että ihmisen oma tulkinta
  hajoaa riittävästi mutta ei rajattomasti. Liian tarkka käsky ei jätä tulkintavaraa, liian
  epämääräinen tuottaa satunnaista hajontaa.
* **`requiredByOrder(order, worldState)` on kirjoitettavissa** jokaiselle päätöskohdalle, jossa
  ajautumaa mitataan (dokumentti 2.5). Jos ei ole, kohta ei tuota ajautumadataa.
* Alkuperäinen käsky säilyy totuuskerroksessa muuttumattomana. Se on ainoa asia, jota vasten
  ajautuma mitataan.

## 5.3 Pakotettu kysymyshetki

Vedetty ohjaus on vahvin versio kysymyksestä: itse haettu tieto koetaan omaksi päättelyksi tavalla,
jota annettu tieto ei ole. Sen hinta on itsevalikoituva altistuminen. Kolme ratkaisua, kaikki
rakennetaan (K-6):

1. **Skenaarion haarautuma.** Tilanne haarautuu niin, ettei etenemistä ole ilman että jotain
   kysytään: kaksi yhtä uskottavaa suuntaa ja riittämätön tieto valita. Maaston suunnitteluvaatimus
   (dokumentti 4.2), ei käyttöliittymän ominaisuus.
2. **Radiovarmistus.** Jos kysymystä ei ole tullut hetkeen T mennessä, sama ohjaus saapuu radiossa.
   Lokiin `guidance_route: query | radio_fallback`.
3. **Kysymiskäyttäytyminen on mittari** — metakognitiivinen kontrollipäätös, kerätään joka tapauksessa.

**Analyysiseuraus:** altistumisreitti on kovariaatti kaikissa vaiheen 2 malleissa. Radiovarmistuksen
kautta altistuneet eivät ole sama ryhmä kuin itse kysyneet, vaikka sisältö on identtinen.

## 5.4 Järjestys ja sen rajoitteet

* **Vaihe 1 aina ensin, ei vastapainotusta.** Perustaso ei saa vuotaa tietoa ohjauksesta.
  Raportoidaan rajoitteena.
* **Oppimisvaikutus vaiheeseen 2** on olemassa ja mainitaan — mutta se on ekologisesti oikea:
  todellinen käyttäjä ei kohtaa järjestelmää ensi kertaa kriisissä.
* **Skenaarion kesto 60–90 min**, yksi sessio. Vaiheiden raja (käskyn saapuminen) sijoittuu
  suunnilleen puoliväliin, jotta molemmista vaiheista kertyy koettimia ja vähintään yksi jäädytys.
* **Kalibraatiopatteri ajetaan erikseen etukäteen omalla ajalla.** Istuntorakenne on dokumentissa 3.11.
  Tämä ratkaisee samalla sen, ettei puolta tuntia tarvitse leikata upseerin päivästä.

## 5.5 Mitä alustalta vaaditaan Tutkimus I:tä varten

| Vaatimus | Dokumentti |
|---|---|
| Kanava lukittuna istunnon alussa, ei vaihdettavissa | 1.5 |
| Alkuperäinen käsky totuuskerroksessa, `requiredByOrder`-funktio | 1.7, 2.5 |
| Virheinjektio kahtena erillisenä tyyppinä, ~20 % / ~20 % / 0 % | 2.4 |
| Vapaa tekstisyöte, kuittaus <300 ms | 2.3 |
| Pakotettu haarautuma maastossa + radiovarmistus | 4.2, 5.3 |
| 15–25 koetinta, luottamus jokaisen perässä, ISA jokaisessa jäädytyksessä | 3.2, 3.5 |
| Kolme jäädytystä; avoin L3-koetin kahdessa tai kolmessa | 3.4 |
| Havaitsemispatteri yksisuuntaisena istunnon jälkeen | 3.6 |
| Ruudun pimennys, joka kestää etäkeruun | 1.3 |
| Jälkiselvitysnäkymä | 0.6 |

## 5.6 Avoin: echelon (A-1)

Päivitetty suunnitelma ei nimeä echelonia. Se on **estävä päätös**, koska siitä seuraa maaston
mittakaava, solukoko, siirtymänopeudet, käskyjen sanamuoto, yksikkötyypit ja koko koetinpankin
vaikeustaso.

| Vaihtoehto | Seuraus |
|---|---|
| **Komppanian päällikkö** | Pienempi maasto (n. 10 × 10 km), lyhyemmät siirtymät, tiheämmät päätöskohdat, helpompi rekrytointi sadalle |
| **Pataljoonan komentaja** | Vastaa vanhan paperin 1 asetelmaa KESI:llä MPKK:lla, isompi maasto (n. 30 × 30 km), harvemmat mutta raskaammat päätökset, vaikeampi rekrytointi |

Suositus: **valitse yksi ja pysy siinä.** Echelonien sekoittaminen tuottaa varianssia, jota ei voi
mallintaa sadan osallistujan otoksessa. Jos rekrytointi tulee kurssikohorteista, kohortin taso
ratkaisee valinnan puolestasi — selvitä se ensin.
