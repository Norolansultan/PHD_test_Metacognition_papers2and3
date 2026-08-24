# 7. Sisältömalli ja validaattori

Ehdot ovat konfiguraatiota, ei koodia. Skenaariot, koettimet, virheinjektio ja maasto ovat dataa,
jonka validaattori tarkistaa jokaisella buildilla.

Validaattori on **komponentti, ei työkalu**, ja se on vaiheen 1 toimitus. Sen tehtävä on estää se
vika, joka tappoi edellisen suunnittelutyökirjan: osien ajautuminen erilleen toisistaan usean
kuukauden aikana. Ihminen ei pysty ylläpitämään sitä invarianttia; kone pystyy.

---

## 7.1 Sisältöpaketin skeema

```ts
interface ContentPack {
  meta: { domain:'army'|'rescue'; study:'I'|'II'; version:string; seed:number; hash:string };

  world: {
    grid: { type:'hex'; cellM:number; w:number; h:number };
    assets: { baseMap:string; terrain:string; visibility:string; hashes:Record<string,string> };
    features: Feature[];            // haarautumat, katveet, reitit, kohde, linjat
  };

  timeline: TimelineEntry[];        // YKSI KELLO
  decisionPoints: DecisionPoint[];
  order?: RadioOrder;               // vain Tutkimus I
  peers: PeerArc[];                 // naapurit: sijainnit, päätökset, aikaleimat
  radio: RadioMessage[];            // teksti + esirenderöity audio + tSim
  probes: { closed: ClosedProbe[]; open: OpenProbe[]; isa: IsaSlot[] };
  distortions: DistortionSpec[];    // virheinjektio
  modelParams: string;              // viittaus validoituun parametritiedostoon
  debrief: DebriefSpec;             // mitä osallistujalle kerrotaan lopuksi
}
```

Kolme yksityiskohtaa, jotka kannattaa lukea tarkkaan:

```ts
interface ClosedProbe {
  id: string; tSim: number;
  level: 1|2|3;                     // Endsley — mittausväline, ei juoni
  text: string;
  groundTruth: 'computed';          // lasketaan tilasta, EI kirjoiteta käsin
  targetAccuracy: [0.65, 0.85];     // pilotissa varmennettava
  confidenceScale: 1|2|3|4;
}

interface DecisionPoint {
  id: string; onsetTSim: number; windowSec: number;
  forcesQuestion: boolean;          // pakotettu haarautuma (K-6)
  precedentValidity: 'apt'|'misleading'|'absent'|'invalidated';   // Tutkimus II
  defaultRule: string;              // mikä toteutuu ikkunan umpeutuessa
  requiredByOrder?: string;         // viittaus funktioon (Tutkimus I ajautumamittari)
}

interface DistortionSpec {
  id: string; type: 'model_error'|'guidance_distortion';
  direction: string;                // systemaattinen skenaarion sisällä
  magnitude: 'low'|'mid'|'high';    // pilotissa kalibroitava
  appliesTo: string[];
}
```

## 7.2 Validaattorin säännöt

| # | Sääntö | Mitä estää |
|---|---|---|
| R1 | Jokainen `dp_id` esiintyy täsmälleen kerran jokaisessa siihen viittaavassa taulukossa | Osien eriytymisen |
| R2 | Aikajanan tapahtumat mahtuvat skenaarion kestoon; ikkunat eivät mene päällekkäin ilman dokumentoitua poikkeusta | Aritmetiikkavian |
| R3 | **Mikään koetin tai jäädytys ei saa ennakoitua merkkiä, ikonia eikä countdownia** | Mittarin muuttumisen harjoitteluksi |
| R4 | Koettimia 15–25 per osallistuja; välit 2–6 min; ei päätösikkunan viimeisen 60 s aikana eikä 30 s sisällä projektiovastauksesta | Kuormakäyrän puuttumisen, liiallisen reaktiivisuuden ja sitoutumishetken häirinnän |
| R5 | Jokaisen suljetun koettimen ground truth on **laskettava tilasta**, ei kirjoitettu | Käsin kirjoitetun totuuden ajautumisen maailmantilasta |
| R6 | Pilottiaineistossa koettimen tarkkuus 65–85 %; ulkopuoliset korvataan | Herkkyyden laskemisen mahdottomuuden |
| R7 | **`model_error` ja `guidance_distortion` eivät koskaan samassa koettelussa** | Kahden virhetyypin sekoittumisen |
| R8 | Virhetyyppien osuudet ~55 / ~20 / ~20 / 0 %, tarkistettuna koko skenaarion yli | Osuuksien liukumisen |
| R9 | Vääristymän suunta on systemaattinen skenaarion sisällä ja tasapainotettu skenaarioiden yli | Manipulaation havaitsemisen rakenteesta |
| R10 | Vähintään yksi `forcesQuestion: true` -päätöskohta ennen ohjauksen saapumista | Itsevalikoituvan altistumisen |
| R11 | Radiovarmistus on määritelty jokaiselle ohjaukselle, joka on vedettyä | Altistumisaukon |
| R12 | Tutkimus I: `requiredByOrder` on olemassa jokaiselle ajautumaa mittaavalle kohdalle | Ajautuman mittaamattomuuden |
| R13 | Tutkimus II: takamaastoa koskevat projektiot palauttavat ≤ N tulosta ennen kohtaa 10 | Tyhjän sektorin hiljaisen täyttämisen |
| R14 | Ehtokohtaiset sisällöt eivät vuoda toisiinsa: ehto 1 ei tavoita vertaispäätöksiä millään reitillä | Manipulaation vuotamisen |
| R15 | Jokainen lokikenttä, johon tila-avaruusdokumentin sarake 3 viittaa, on olemassa skeemassa | Proxyjen mittaamattomuuden jälkikäteen |
| R16 | Jälkiselvitysteksti kattaa jokaisen skenaariossa käytetyn vääristymätyypin | Puutteellisen jälkiselvityksen |
| R17 | Vain sanastossa määritellyt ehtotermit | Vanhentuneen termistön |

**R15 on tärkein ja epäintuitiivisin.** Tila-avaruusdokumentin kolmas sarake (online-proxy +
lokikentät) määrää lokitusskeeman, eikä sitä voi korjata jälkikäteen kerättyyn aineistoon. Siksi
validaattori tarkistaa ristiin, että jokainen proxy, jonka olet luvannut paperissa D, on
lokitettavissa.

## 7.3 Sisältöputki

```
kirjoitusalusta (taulukko/YAML)
   │ npm run content:build
   ▼
VALIDAATTORI ──▶ punainen = build pysähtyy, raportti kertoo säännön ja kohdan
   ▼
dist/content-pack.{army|rescue}.json + SHA-256 + sisältöversio
```

YAML versionhallinnassa, jotta jokainen sisältömuutos näkyy diffinä ja on katselmoitavissa.
Taulukkomuotoinen kirjoitusalusta on sallittu lähde, mutta tuonti on yksisuuntainen ja idempotentti.

## 7.4 Sisällöntuotannon työmäärä

| Sisältö | Tutkimus I | Tutkimus II | Huom |
|---|---|---|---|
| Skenaarion tapahtumat ja radioviestit | ~100 viestiä | ~100 viestiä | + äänitys, jos ääni valitaan |
| Epämääräinen käsky + `requiredByOrder` | 1 + n funktiota | — | Kirjoitusvaatimus 5.2 |
| Vertaispäätösten aikajana | — | 7 kaistaa × ~10 päätöstä | Korvaa vanhat perustelumerkinnät |
| Suljetut koettimet | 40–60 (pankki) | 40–60 | Pilotoitava tarkkuuteen |
| Avoimet L3-koettimet | 2–3 | 2–3 | + koodauskehikko |
| Kalibraatiopatteri | 200–400 koettelua | 200–400 | Domainkohtainen |
| Vääristymäspesifikaatiot | per skenaario × 3 tasoa | päätettävä (A-7) | Pilotissa kalibroitava |
| Jälkiselvitystekstit | 1 | 1 | Kattaa kaikki vääristymätyypit |

**Kevenemä aiempaan:** ~60 perustelumerkintää ja ~180 häiriösyöttiä poistuivat kokonaan. Tilalle
tuli koetinpankkien pilotointi, joka on työläämpää kuin miltä näyttää, koska tarkkuustavoite
65–85 % joudutaan hakemaan iteroimalla.

**Pisin läpimenoaika on edelleen asiantuntijoiden saatavuus** — parametrivalidointi, maaston
realismiportti ja käskyn epämääräisyyden tarkistus vaativat kaikki samoja ihmisiä. Aloita siitä.
