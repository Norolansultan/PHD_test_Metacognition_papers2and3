# 2. Projektiomoottori

Sama moottori kaikkiin tutkimuksiin. Käyttöliittymä on kertakäyttötavaraa; moottori ei ole.
Julkaistuna se on oma menetelmäartikkelinsa ja liite apurahahakemuksiin ennen varsinaisia tuloksia.

---

## 2.1 Mitä moottori tekee ja mitä se ei tee

**Tekee tasan kolme asiaa:** jäsentää kysymyksen parametreiksi → ajaa tilamallin → esittää tuloksen.

**Ei tee:** generatiivista päättelyä, omaa perustelua mallin ulkopuolelta, suositusta toimintatavasta,
eikä pidä tilaa siitä mitä osallistujan pitäisi tehdä. Jäsennyksen epäonnistuessa se pyytää selvennystä
vakiomuotoisella tekstillä eikä arvaa.

Tämä rajaus on koko tutkimuksen pätevyyden ehto. Jos moottori perustelee omin sanoin, vastaus ei ole
enää malli vaan kielimalli, eikä kahden osallistujan saama vastaus ole vertailukelpoinen.

## 2.2 Tilamalli

20–40 parametria per domain. Ei enempää: malli pitää pystyä selittämään asiantuntijalle yhdellä
sivulla, tai face validity -validointi ei onnistu.

| Armeija (Tutkimus I) | Pelastus (Tutkimus II) |
|---|---|
| Liikenopeudet maastotyypeittäin | Palon leviämisnopeus tuulen, polttoaineen ja rinteen funktiona |
| Tulivoiman vaikutus | Siirtymäajat |
| Huollon kesto | Vesihuolto ja täydennysajat |
| Tiedustelutiedon vanheneminen | Evakuointikapasiteetti |
| Näkyvyys ja katvealueet | Näkyvyys ja savun vaikutus |
| Ryhmittymis- ja perustamisajat | Muodostelmien perustamisajat |

```ts
interface ProjectionRequest {
  sessionId: string; tSim: number; seed: number;
  params: ModelParams;              // jäsennetty, ei raakatekstiä
  domain: 'army' | 'rescue';
  modelVersion: string;
}
interface ProjectionResponse {
  outcome: ModelOutcome;            // ajat, todennäköisyydet, tilat
  presentation: string;             // mallin tulos sanoiksi, mallipohjasta
  errorFlag: null | 'model_error' | 'guidance_distortion';
  modelVersion: string; seed: number;
}
```

**Determinismi:** samat parametrit + sama siemen → sama tuloste, poikkeuksetta. Siemen on kiinteä
per skenaario, ei per istunto — sama what-if tuottaa saman vastauksen jokaiselle osallistujalle.

## 2.3 Jäsennin — kolme tasoa

Kielimalli ei ole deterministinen, mutta vastausten on oltava identtisiä. Ratkaisu (vaikutusanalyysin
K-2) on kerroksittainen:

```
1. NORMALISOINTI        pienet kirjaimet, välimerkit pois, synonyymit kanonisoidaan
                        ↓
2. VÄLIMUISTI           normalisoitu teksti → parametrit. Osuma = deterministinen, aina.
                        ↓ ohi
3. SÄÄNTÖPOHJAINEN      slot-jäsennin: KUKA × MITÄ × MISSÄ × MILLOIN
   JÄSENNIN             kattaa valtaosan kysymyksistä ilman mallia lainkaan
                        ↓ ei osumaa
4. LLM-VARAJÄSENNIN     lämpötila 0, tehtävä: teksti → SAMA parametriskeema.
                        Tulos kirjoitetaan välimuistiin → toistuu identtisenä.
                        ↓ epäonnistuu
5. SELVENNYSPYYNTÖ      vakiomuotoinen teksti, ei arvausta
```

**Mitä luvataan menetelmäosassa:** identtinen kysymysteksti tuottaa identtiset parametrit ja
identtisen vastauksen jokaiselle osallistujalle koko keruun ajan. **Mitä ei luvata:** kaksi eri
tavalla muotoiltua kysymystä voivat jäsentyä eri parametreiksi. Siksi jokainen jäsennys lokitetaan
reitteineen (`cache | rule | llm | failed`), ja jäsennysvaihtelu raportoidaan.

**Vasteaika alle 300 ms.** Koska moottori laskee eikä generoi, se on nopeampi kuin aito kielimalli —
etu, joka pidetään. Sääntöjäsennin ja välimuisti ovat mikrosekunteja; LLM-varareitti on hitaampi,
joten sen osuessa kuittaus lähetetään heti ja tulos striimataan perässä. Keinotekoista viivettä ei
ole missään.

## 2.4 Virheinjektio ensimmäisen luokan ominaisuutena

Kaksi virhetyyppiä. **Ne eivät koskaan esiinny samassa koettelussa**, ja niillä on eri lokiliput.

| Koettelutyyppi | Osuus | Paljastaa | Lokilippu |
|---|---|---|---|
| Projektio oikein, ohjaus oikein | ~55 % | perustaso | `null` |
| **Projektio väärin**, ohjaus oikein | ~20 % | delegoitu projisointi — luotettavuuskysymys | `model_error` |
| Projektio oikein, **ohjaus vääristynyt** | ~20 % | komentoketjun ajautuminen — eheyskysymys | `guidance_distortion` |
| Molemmat väärin | 0 % | — | kielletty, validaattori estää |

Kolmas rivi on väitöskirjan tärkein solu: käyttäjä noudattaa käskyä, jota ei annettu. Hän ei riko
mitään, hän voi perustella päätöksensä johdonmukaisesti, ja komentoketju on silti ajautunut ilman
että kukaan huomaa.

**Vääristymän kalibrointi on pilotin tehtävä.** Liian pieni ei erotu ihmisen omasta hajonnasta,
liian suuri havaitaan ristiriitana. Kolme tasoa, 5–8 henkeä kutakin. Suunta pysyy systemaattisena
skenaarion sisällä ja tasapainottuu skenaarioiden yli — jos suunta vaihtelee kesken skenaarion,
osallistuja kohtaa keskenään ristiriitaisia tulkintoja ja havaitsee manipulaation rakenteesta eikä
sisällöstä.

```ts
interface DistortionSpec {
  scenarioId: string;
  direction: 'north_bias' | 'south_bias' | 'early_bias' | 'late_bias';  // systemaattinen
  magnitude: 'low' | 'mid' | 'high';    // pilotissa kalibroitava
  appliesTo: string[];                  // mihin projektioihin
}
```

## 2.5 Ajautumamittari

Ajautuma = ero sen välillä, mitä osallistuja teki, ja mitä **alkuperäinen radiokäsky** olisi hänen
tilanteessaan edellyttänyt.

```
ajautuma(osallistuja) = etäisyys( päätös , käskyn edellyttämä toiminta tässä tilanteessa )
vertailukohta        = ei-projektioryhmän oma tulkintajakauma samassa tilanteessa
```

Ilman ei-projektioryhmää ajautumaa ei voi mitata: ihmisen oma tulkinta hajoaa muutenkin, ja ilman
sitä jakaumaa mikä tahansa poikkeama näyttäisi ajautumalta. Tämä on rakennusvaatimus: **käskyn
edellyttämä toiminta on laskettava funktio maailmantilasta**, ei koodaajan jälkikäteinen arvio.

```ts
requiredByOrder(order: RadioOrder, worldState: WorldState): ActionSet
```

Jos tätä funktiota ei voi kirjoittaa jollekin skenaariokohdalle, kyseinen kohta ei tuota
ajautumadataa — ja se on parempi tietää sisältöä kirjoitettaessa kuin analyysivaiheessa.

## 2.6 Parametrien lähde

Lukuja ei keksitä. Kaksi reittiä, molemmat tarvitaan:

1. **Command: Modern Operations -ajot.** Skenaariot ajetaan CMO:ssa ja niistä johdetaan
   siirtymäajat, tulivaikutukset ja tiedustelun vanheneminen. "Parametrit johdettu CMO-ajoista"
   on menetelmäosassa vahva perustelu, ja MPKK:n väki tuntee työkalun. **Varmistettava
   Salmiselta, pitävätkö he sen maasotaosuutta uskottavana** — jos eivät, tämä reitti ei kanna.
2. **Asiantuntijavalidointi.** Projektiot ajetaan 3–5 asiantuntijalla läpi (Salminen, Huttner).
   Face validity raportoidaan sellaisenaan, myös jos se on osin kielteinen.

CMO ei sovi itse koeympäristöksi: jäädytys on epäluotettava, karttaa ei voi pimentää, vapaata
tekstisyötettä ei ole, ja sadan osallistujan lisensointi ja asennus tekisi etäkeruusta mahdotonta.
Se on parametrilähde ja totuusarvojen tuottaja, ei alusta.

## 2.7 Lokitus per projektio

Jokaisesta projektiosta kirjataan:

| Kenttä | Miksi |
|---|---|
| `t_sim` | Aikaperusta on skenaarioaika |
| `raw_text` | Kysymyksen muotoilu on dataa: se kertoo mitä osallistuja luuli tarvitsevansa |
| `parse_route` | `cache \| rule \| llm \| failed` — jäsennysvaihtelun raportointi |
| `params` | Mitä mallilta oikeasti kysyttiin |
| `model_version`, `seed` | Toistettavuus kahden vuoden päästä |
| `outcome`, `presentation` | Mitä osallistuja näki, sanatarkasti |
| `error_flag`, `distortion_spec_id` | Altistuksen rekonstruointi jälkiselvitystä ja etiikkaa varten |
| `next_action`, `latency_to_next_ms` | Hyväksymisviive — sujuvuusharhan tunnusmerkki |
| `verification_followed` | Tarkistiko osallistuja tiedon toisesta lähteestä |

Kaksi viimeistä ovat paperin D proxyjen raaka-ainetta. Ne on lokitettava alusta asti: proxyjä ei voi
lisätä jälkikäteen kerättyyn aineistoon.

## 2.8 Valmiin määritelmä

- Sama kysymysteksti samassa skenaariokohdassa palauttaa sanatarkasti saman vastauksen kahdessa eri
  istunnossa, eri selaimissa, eri päivinä.
- Virheinjektio on kytkettävissä konfiguraatiosta, ja molemmat tyypit ovat toisensa poissulkevia
  koettelun tasolla — testattuna, ei sovittuna.
- Jäsennin kattaa pilottiaineiston kysymyksistä ≥ 80 % sääntöreitillä. Alle sen LLM-varareitti
  hallitsee liian suurta osuutta ja jäsennysvaihtelusta tulee mittarin ongelma.
- Jokainen projektio on rekonstruoitavissa lokista: sama syöte, sama versio, sama siemen → sama tulos.
- Kuittaus alle 300 ms 95 %:ssa kutsuista tavallisella kotiyhteydellä.
