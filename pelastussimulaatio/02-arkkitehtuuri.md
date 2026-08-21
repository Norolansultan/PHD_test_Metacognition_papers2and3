# 2. Järjestelmäarkkitehtuuri

> Suunnitteluperiaate, joka voittaa aina, kun tulee ristiriita:
> **tämä on tutkimusinstrumentti joka sisältää simulaation, ei simulaatio johon on lisätty mittaus.**
> Peliteollisuudessa vastaava kohta on determinismi replay-järjestelmissä ja e-urheilussa: kun
> uusinta ei täsmää, peli on rikki riippumatta siitä miten hyvältä se näyttää.

---

## 2.1 Korkean tason kuva

```
┌────────────────────────────────────────────────────────────────────────────┐
│ SISÄLTÖPUTKI (build-aika, Node)                                            │
│   Excel/YAML-lähde ──▶ compiler ──▶ VALIDAATTORI ──▶ content-pack.json     │
│   maastogeneraattori ──▶ baker ──▶ rasteri- + vektoriassetit + SHA-256      │
│   palomalli (offline) ──▶ rintamapolygonit per simulaatiominuutti          │
└──────────────────────────────┬─────────────────────────────────────────────┘
                               │  (versioidut, hashatut, muuttumattomat assetit)
┌──────────────────────────────▼─────────────────────────────────────────────┐
│ AJOAIKA (selain, offline-first)                                            │
│                                                                            │
│  ┌──────────── SIM CORE (puhdas TS, ei DOM, ei I/O) ──────────────────┐    │
│  │  Clock ─ Scheduler ─ WorldState ─ AgentRunner ─ ResourceModel      │    │
│  │  GroundTruthStore (aikaindeksoitu) ─ ProjectionOracle              │    │
│  │  reducer: (state, event) => state'   • deterministinen • seedattu   │    │
│  └────────────┬───────────────────────────────────┬───────────────────┘    │
│               │ perception gate                   │ event bus              │
│  ┌────────────▼──────────────┐        ┌───────────▼──────────────────┐     │
│  │ PERCEPTION LAYER          │        │ TELEMETRY                    │     │
│  │ mitä TÄMÄ osallistuja     │        │ append-only, idempotentti,   │     │
│  │ tietää, milloin, kuinka   │        │ offline-jono + snapshot      │     │
│  │ vanhaa                    │        └───────────┬──────────────────┘     │
│  └────────────┬──────────────┘                    │                        │
│  ┌────────────▼───────────────────────────────────▼──────────────────┐     │
│  │ UI-KERROS (React + canvas)                                        │     │
│  │  MapView(2 mittakaavaa) · DecisionBar+countdown · QueryBuilder ·  │     │
│  │  RadioLog · StatusPanel · GuidancePanel · ProbeOverlay · Clock    │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                                                            │
│  ┌──── TUTKIJAKONSOLI (erillinen näkymä, oma laite/ikkuna) ──────────┐     │
│  │  start · pause · mark · abort · live DP-tila · lokin terveys      │     │
│  └───────────────────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────────────────────┘
                               │ upload ≤15 min istunnon jälkeen, hash-varmennus
┌──────────────────────────────▼─────────────────────────────────────────────┐
│ ANALYYSIPUOLI  ·  raakatapahtumat ──▶ derive.ts ──▶ muuttujat ──▶ CSV/R     │
│                   replay-näkymä koodaajille (ehtomerkinnät riisuttu)        │
└────────────────────────────────────────────────────────────────────────────┘
```

**Kolme kovaa rajaa**, jotka pitävät koko rakennelman kasassa:

1. **Sim core ei tunne DOMia eikä verkkoa.** Sitä voi ajaa Node-testissä 1000× peräkkäin ja verrata
   hashia. Tämä on ainoa tapa todistaa determinismi ennen kuin kukaan istuu koneelle.
2. **Perception gate on ainoa reitti maailmasta käyttöliittymään.** Ei ohituksia. Jos komponentti
   tarvitsee tiedon, se pyytää sen havaintokerrokselta, joka päättää tietääkö tämä osallistuja sen
   ja kuinka vanhana.
3. **Sisältöpaketti on data, ei koodi.** Moottori lataa `content-pack.json` + assetit. Pelastus on
   yksi paketti. Armeija on toinen paketti eikä uusi ohjelmisto.

## 2.2 Teknologiavalinnat ja perustelut

| Kerros | Valinta | Miksi juuri tämä |
|---|---|---|
| Kieli | **TypeScript**, strict | Yksi kieli buildille, ytimelle, UI:lle ja johdannaisskripteille. Skeemat elävät tyypeissä ja generoivat JSON-skeeman validaattorille. |
| Ydin | Puhdas TS, ei riippuvuuksia | Testattavissa Nodessa, ajettavissa headlessina, hashattavissa. |
| UI | **React** + Zustand/Redux (tapahtumapohjainen store) | Tuttu, vakaa, ja tilan muutokset ovat jo valmiiksi tapahtumia — sama virta menee lokiin. |
| Kartta | **Canvas 2D**, kaksi kerrosta (leivottu pohja + dynaaminen overlay) | WebGL olisi ylimitoitettu: kartta on staattinen kuva plus muutama sata vektoripiirtoa. Canvas 2D on ennustettava ja debugattava. |
| Build | **Vite** + Node-skriptit | Nopea, ja tuottaa staattisen bundlen jonka voi ajaa `file://`-tasoisesti tarvittaessa. |
| Tila levyllä | **IndexedDB** (tapahtumajono + 30 s snapshot) | Selkeä offline-toipuminen: verkko voi kaatua kesken istunnon eikä yksikään tapahtuma katoa. |
| Palvelin | Ohut Node/Fastify + tiedostotallennus (tai vain USB-vienti) | Ei tarvita tietokantaa. Latauksen ainoa tehtävä on ottaa jono vastaan ja varmentaa hash. |
| Ääni | Esirenderöity ääniraita per radioviesti | Ei TTS-ajoaikaa: sanatarkka determinismi koskee myös ääntä. |
| Satunnaisuus | `mulberry32(seed)`, **vain build-ajassa** | Ajoaikaisessa osallistujapolussa ei ole satunnaisuutta lainkaan, lukuun ottamatta SAGAT-osioiden arvontaa altaasta (joka lokitetaan altaineen). |

**Mitä EI valita ja miksi:**
Unity/Unreal (asennus Pelastusopiston koneille, determinismi työlästä, hyöty olematon 2D-karttakäyttöliittymässä),
ajoaikainen LLM (tuhoaa sanatarkan vakioisuuden, ks. `AI Layer Spec`),
pelimoottorin fysiikka palon leviämiseen (ks. 2.7),
XVR-integraatio ensisijaisena mittauspintana (ks. dokumentti 6, avoin päätös #1).

## 2.3 Deterministinen kello ja aikataulutus

```ts
// tick = 250 ms simuloitua aikaa, kiinteä. Ei delta-timea missään.
type Clock = { tSimMs: number; running: boolean; rate: 1 };

// Ainoat asiat, jotka pysäyttävät kellon:
//  - SAGAT-jäädytys (skenaarioaika ei koskaan kulu jäädytyksessä)
//  - tutkijan pause tutkijakonsolista (lokitetaan, ja se merkitsee istunnon)
```

**Aikataulu on data.** `Master Timeline` kääntyy tapahtumalistaksi, jonka ajastin kuluttaa:

```ts
interface TimelineEntry {
  tSim: number;                  // sekuntia tapahtuman alusta
  kind: 'dp_onset' | 'dp_close' | 'guidance' | 'radio' | 'corpus_write'
      | 'spam_item' | 'freeze_start' | 'freeze_end' | 'agent_beat' | 'env_change';
  ref: string;                   // S07, G-01, W-041, SP-03, F2 ...
}
```

Skenaariot etenevät **ajassa, eivät osallistujan toiminnasta**. Tämä on vertailukelpoisuuden ehto,
ja se on myös se asia, jonka kokematon toteuttaja rikkoo ensimmäisenä ("odotetaan että käyttäjä on
valmis"). Ajastin ei odota koskaan.

**Kellon renderöinti.** Otsikkorivillä juoksee tapahtuman kello jatkuvasti; päätöspalkissa juoksee
ikkunan countdown. Molemmat ovat tarkoituksellista painetta. **Mikään ei koskaan laske alaspäin
kohti jäädytystä tai SPAM-osiota** — koodikatselmuksessa varmistetaan, ettei osallistujan
renderöintipolusta ole saavutettavissa yhtäkään koettimiin liittyvää ajastinta.

## 2.4 Maailmamalli: kaksi kerrosta

```
GROUND TRUTH  (sim core)          PERCEIVED  (osallistuja näkee)
──────────────────────────        ─────────────────────────────────
todellinen palorintama            viimeksi havaittu rintama + ikä
naapurien todelliset sijainnit    viimeksi raportoidut sijainnit, haalennettuina
korpuksen koko sisältö            se osa jonka valid_from ≤ nyt JA joka on haettu
sään todellinen tila              näytön arvot (päivittyvät S08:ssa)
```

**Toteutussääntö, joka testataan automaattisesti:** osallistujan buildissa totuuskerros ei ole
saavutettavissa. Ei verkkovastauksessa, ei globaalissa muuttujassa, ei React-propseissa. Testi:
buildataan osallistujaversio, ajetaan istunto headless-selaimessa ja greppataan kaikki
verkkoliikenne ja `window`-puu totuuskerroksen tunnisteiden varalta. Punainen = build ei mene läpi.

**Vanhentuneisuusmalli.** Jokainen havaittu asia kantaa `observedAt`-ajan. Renderöinnissä ikä
näkyy haalennuksena ja tekstinä ("havaittu 12 min sitten"). Zoomaus ei koskaan paljasta havaitsematonta.
Työkirja kutsuu tätä käyttöliittymän tärkeimmäksi rehellisyysominaisuudeksi, ja se on oikeassa:
ilman sitä kartta valehtelee osallistujalle systemaattisesti ja tilannekuvamittaus mittaa
käyttöliittymän virhettä.

## 2.5 Aikaindeksoitu totuuskorpus ja kyselymoottori

Tämä on instrumentin älyllinen ydin. Se ei ole tietokanta vaan **ajassa suodatettu tietämysvarasto**.

```ts
interface CorpusEntry {
  id: string;                    // W-041
  validFrom: number;             // simuloitu sekunti, jolloin tieto on olemassa
  supersededBy?: string;         // korvaava merkintä; vanha jää haettavaksi omalla leimallaan
  observedAt: number;            // milloin havainto tehtiin (näytetään vastauksessa)
  source: 'peer' | 'own_crew' | 'air' | 'weather' | 'command' | 'sensor';
  entity?: string;               // CHARLIE | KILO-1 | CREW_C ...
  fields: {
    position?: string; status?: string; observation?: string; decision?: string;
    rationale?: string;          // VAIN ehto B
    confidence?: number;         // VAIN ehto B
  };
  queryPaths: string[];          // ['eastern_approach','kilo_obs','weather'] — monta reittiä
  confidenceWording?: 'single_source_uncorroborated' | 'confirmed' | 'estimate';
  distractor?: boolean;
}
```

**Kyselyn suoritus, viisi askelta, joka kerta samassa järjestyksessä:**

1. Rakenna kyselyavain paikoista KUKA × MITÄ × MILLOIN (tai kartoita vapaa teksti aikomukseksi).
2. Suodata korpus: `validFrom ≤ tSim`. **Kaikki muu on olematonta.**
3. Suodata kyselypolulla; poimi myös häiriösyötit (tavoite 3 häiriösyöttiä relevanttia kohden).
4. **Ehtoportti:** jos osallistuja on ehdossa A, poista kentät `rationale` ja `confidence`.
   Portti on yksi funktio yhdessä tiedostossa, ja sillä on oma yksikkötesti.
5. Palauta kiinteä 2,5 s viiveen jälkeen, aina havaintoaikaleiman kanssa.

**Kolme sääntöä, jotka on helppo rikkoa vahingossa:**

* Ehdon A **ei pidä nähdä tyhjää perustelukenttää**. Kentän on oltava olematon, ei tyhjä — muuten
  käyttöliittymä paljastaa manipulaation olemassaolon.
* Ehto B ei saa saada mitään aikaetua. Molemmat ehdot kerryttävät samaa tietoa samaan tahtiin;
  ainoa ero on *mitä voi kysyä*.
* Kohtaamaton vapaa tekstikysely palauttaa **kiinteän** "ei tietoa tästä" -vastauksen ja
  lokitetaan sanatarkasti. Kohtaamattomuus on dataa, ei virhe.

**S10 on suunnittelun paras piirre ja helpoin menettää.** Takamaastosta korpus palauttaa lähes
tyhjää, ja se on tarkoitus. Rakenna siihen eksplisiittinen testi (`corpus returns ≤ N entries for
rear_ground before tSim 1:01`), tai joku täyttää sen hyvää tarkoittaen jossain vaiheessa.

## 2.6 Projektio-oraakkeli (tason 3 osioiden rehellinen pisteytys)

Työkirja vaatii, että tason 3 (projektio) -osio pisteytetään sitä vastaan, mikä oli
**pääteltävissä sen tiedon perusteella, joka tällä osallistujalla oli** — ei sitä vastaan, mitä
käsikirjoitus seuraavaksi tekee. Tämä on arkkitehtuurivaatimus, ei koodausohje, ja se on
rakennettava ennen kuin ensimmäistäkään osiota kirjoitetaan.

```ts
// 1) käsikirjoituksen totuus: eteenpäin simulointi mistä tahansa hetkestä
projectGroundTruth(tSim, horizonMin): WorldProjection

// 2) tämän osallistujan tietohistoria: mitä hän oli nähnyt tai hakenut ennen tSim
inferableSet(participantKnowledge, tSim, horizonMin): Set<AcceptableAnswer>
```

Kaksi osallistujaa, joilla on eri tietohistoria, saavat **eri hyväksyttävien vastausten joukon**
samaan osioon, ja ero on toistettavissa lokista. `sagat_inferable_flag` tulee suoraan tästä.

## 2.7 Palon leviäminen: käsikirjoitettu, ei simuloitu

Tämä on suunnittelun kiistanalaisin kohta ja siksi perustelen sen kokonaan.

Ajoaikainen leviämismalli (Rothermel, soluautomaatti, mikä tahansa) rikkoisi kolme asiaa yhtä aikaa:
determinismin (liukulukujen kertyminen selaimesta toiseen), tapahtuma-ajoituksen (S08:n on
tapahduttava sekunnilleen samaan aikaan kaikille) ja validoinnin (kukaan ei voi hyväksyä mallia,
jonka tulos riippuu osallistujan toimista).

**Ratkaisu:** palorintama on **aikaleimattu polygonisarja**, yksi kehä per simulaatiominuutti,
tuotettu offline maastotietoisella mallilla ja **käytännön asiantuntijoiden hyväksymä ennen kuin
sitä käytetään**. Ajoaikana vain interpoloidaan kahden avainkehän välillä.

```
tools/fire-bake.ts
  syöte: maastoluokitus + rinne (KM2/generoitu) + polttoaineparametrit + tuulikäsikirjoitus
  malli: yksinkertainen anisotrooppinen leviäminen, ajetaan offline, tuulen käännös 0:48
  tuotos: fire_perimeters.json  { tSim: 0..5280, polygon: [[x,y],...] }  + SHA-256
  hyväksyntä: asiantuntijakatselmus kolmesta otoksesta (0:20, 0:50, 1:15)
```

**Paikallinen seuraus säilyy silti.** Osallistujan päätökset eivät liikuta rintamaa, mutta ne
ratkaisevat, **mitä rintama kohtaa**: onko linja pidetty, onko murroslinja raivattu, onko saha
suojattu, missä muodostelmat ovat. Se on peliteollisuudesta tuttu ratkaisu — käsikirjoitettu uhka,
todelliset seuraukset — ja se on tässä tapauksessa myös metodologisesti ainoa puolustettavissa oleva.

Vaikutusten laskenta on erillinen deterministinen funktio:
`resolveOutcome(perimeter(tSim), unitPositions, preparedLines, protectionAssignments) → { exposure, structuresLost, objectiveAtRisk }`.

## 2.8 Ohjauskerros (Paperi 3)

```ts
interface GuidanceRule {
  id: 'G-01' | 'G-02' | 'G-03';
  activeFrom: number; activeUntil?: number;
  relation: 'aligned' | 'conflict' | 'ambiguous' | 'none';
  advisoryText: string;
  bindingText: string;            // pituudeltaan ja tarkkuudeltaan vastaava
  blockedOptions: string[];       // vain sitova haara
  delivery: 'broadcast' | 'standing_state';   // ← G-02 on standing_state
}
```

* **Neuvova haara:** teksti näkyy ohjauspaneelissa; kaikki optiot valittavissa.
* **Sitova haara:** estetyt optiot näkyvät estettyinä, syy näkyy osoitettaessa, ja valinta avaa
  ohituspolun: vahvistus + pakollinen vapaa perustelu. Jokainen vaihe lokitetaan
  (`block_shown`, `override_opened`, `override_cancelled`, `override_committed`).
* **S13:ssa molemmat haarat identtiset.** Kaikki estot avautuvat samalla tikillä.
* **S08–S13 ei anneta mitään.** Hiljaisuus on toteutettava eksplisiittisenä sääntönä, jottei
  kukaan lisää "avuliasta" ilmoitusta myöhemmin. Testi: aikajanalla ei ole yhtään
  `guidance`-tapahtumaa välillä 2880 s ja 4260 s.

## 2.9 Päätöspalkki, oletustoimintamoottori ja uncued-käsittely

```ts
interface DecisionPoint {
  id: 'S01'|...|'S15';
  delivery: 'cued' | 'ambiguous' | 'uncued';
  onsetTSim: number; windowSec: number;
  options: DecisionOption[];         // 3–6, kiinteä järjestys
  defaultRule: string;               // mikä toteutuu jos ikkuna umpeutuu
  guidanceRelation: 'aligned'|'conflict'|'ambiguous'|'none';
  precedentValidity: 'apt'|'misleading'|'absent'|'invalidated';
  confidencePrompt: boolean;         // true vain jos delivery !== 'uncued'
}
```

* **Uncued (S06, S08:n esioire-ikkuna):** ei palkkia, ei ikonia, ei ääntä, ei countdownia.
  Näkymätön ikkuna on olemassa vain lokissa. Spontaani toiminta ikkunan sisällä kirjataan
  `uncued_spontaneous_action`-tapahtumaksi latenssin kanssa, **ilman luottamuskysymystä** —
  kysyminen kertoisi osallistujalle että kyseessä oli mitattu päätös.
* **Ikkunan umpeutuminen:** `defaultRule` laukeaa, maailma muuttuu, radiossa kerrotaan mitä nyt
  tapahtuu, ja lokiin menee `non_decision` sääntöineen. **Yksikään ikkuna ei saa sulkeutua
  hiljaa** — tästä on automaattitesti, joka ajaa täyden istunnon ilman yhtään syötettä ja
  tarkistaa, että jokainen viidestätoista pisteestä tuotti joko päätöksen tai ei-päätöksen ja
  tilamuutoksen.

## 2.10 Koetinjärjestelmä (SPAM ja SAGAT)

| | SPAM | SAGAT |
|---|---|---|
| Milloin | Vain ikkunoiden **väleissä** | 3 jäädytystä: F1 (0:22), F2 (0:56), F3 (1:21) |
| Kellon tila | Käy | **Pysähtyy** |
| Kanavat | Auki | **Lukossa** — kysely, wiki, kartta, muistiinpanot |
| Mitä lokitetaan | Hyväksymislatenssi (= kuormamittari), vastaus, oikeellisuus | Vastaus, taso, altaan tunnus, `inferable_flag` |
| Sisältö | Yksi per skenaario, taso kiertää | Arvotaan tasokohtaisesta altaasta; **tasojakauma kiinteä** |

Jäädytyksen tekninen valmiin määritelmä: kanava on **todistettavasti** saavuttamaton (ei vain
piilotettu käyttöliittymässä), jäädytyksen sisältö on identtinen kaikissa neljässä solussa, ja
arvottu osio lokitetaan altaineen. Jäädytys, joka eroaa haaroittain, on manipulaatio eikä mittari.

## 2.11 Domain-neutraalius: mitä ytimeen kuuluu ja mitä ei

| Ytimessä (jaettu molemmille domaineille) | Sisältöpaketissa (domainkohtainen) |
|---|---|
| Kello, ajastin, vaiheet | Skenaarioiden tekstit ja optiojoukot |
| Kaksikerroksinen maailma, havaintoportti | Yksikkötyypit, resurssien fysiikan parametrit |
| Aikaindeksoitu korpus + kyselymoottori | Korpuksen merkinnät, häiriösyötit, kyselypolut |
| Ohjauskerros ja optioesto | Ohjaustekstit ja estetyt optiot |
| Päätöspalkki, oletustoimintamoottori | Oletussäännöt |
| Koetinjärjestelmä ja pisteytysrajapinta | Koetinosiot ja altaat |
| Lokitus, replay, vienti | Kartta-assetit ja piirteiden rekisteri |
| Karttarenderöijä ja koordinaattipalvelu | Uhkamalli (palorintama / vihollisen eteneminen) |

Sama maasto palvelee molempia: missä pelastuslukemassa on etenevä maastopalo, siinä armeijalukemassa
on etenevä vastustaja identtisellä maastolla. Tämä oli alkuperäisen suunnitelman idea ja se on
arkkitehtuurisesti halpa **jos** uhka on rajapinnan takana alusta asti:

```ts
interface ThreatModel {
  perimeterAt(tSim: number): Polygon;
  exposureFor(unit: Unit, tSim: number): ExposureLevel;
  displayStyle: 'fire' | 'enemy';
}
```

Jos tämä rajapinta jää tekemättä vaiheessa 1, armeijadomain maksaa uuden projektin verran.
Jos se tehdään nyt, se maksaa sisällöntuotannon verran.
