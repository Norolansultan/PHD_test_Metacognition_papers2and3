# 3. Sisältömalli, sisältöputki ja validaattori

Työkirjan oma "ei-neuvoteltava sääntö" kuuluu: jokainen välilehti avautuu samoihin tunnisteisiin
S01–S15, ja jos päätöspiste muuttuu, se muuttuu ensin Scenario Spinellä ja etenee sieltä.
Se sanoo myös suoraan, mikä edellisen työkirjan tappoi: **välilehdet ajautuivat erilleen toisistaan.**

Ihminen ei pysty ylläpitämään sitä invarianttia kolmenkymmenen välilehden yli useiden kuukausien
ajan. Kone pystyy. Siksi tässä suunnitelmassa **sisältövalidaattori on komponentti, ei työkalu**,
ja se on vaiheen 1 toimitus siinä missä kellokin.

---

## 3.1 Sisällön lähde: Excel pysyy, mutta se käännetään

Excel on oikea kirjoitusalusta — ohjaajat lukevat sitä, se kantaa värikoodauksen ja
tarkistushistorian, eikä sitä kannata korvata. Mutta se ei ole ajettava muoto.

```
PhD_Simulation_Scenarios.xlsx      (kirjoitusalusta — sinä ja sisällöntuottaja)
        │  npm run content:import      (SheetJS-pohjainen lukija)
        ▼
content/*.yaml                     (versionhallinnassa, diffattavissa, katselmoitavissa)
        │  npm run content:build
        ▼
VALIDAATTORI  ──▶ punainen = build pysähtyy, raportti kertoo minkä säännön ja missä solussa
        ▼
dist/content-pack.pelastus.json    + SHA-256 + sisällön versionumero
```

Miksi YAML välissä: Excelistä ei saa kunnollisia diffejä eikä katselmuksia. YAML on
versionhallinnassa, ja jokainen sisältömuutos näkyy pull requestina, jonka voi hyväksyä.
Excel jää lähteeksi, YAML on totuus buildille, ja tuonti on yksisuuntainen ja idempotentti.

## 3.2 Sisältöpaketin skeema

```ts
interface ContentPack {
  meta: { domain: 'rescue'|'army'; version: string; seed: number; builtAt: string; hash: string; };

  world: {
    incident: { widthKm: 30; heightKm: 30; crs: 'ETRS-TM35FIN'; originE: number; originN: number; };
    sector:   { x0: 13.2; y0: 16.2; x1: 17.2; y1: 20.2 };   // harjulakartta.html:n mukaisesti
    features: Feature[];          // 14 kiinteää piirrettä, kukin id + geometria + rooli
    assets:   { baseMapIncident: string; baseMapSector: string; terrainGrid: string; hashes: {} };
  };

  timeline: TimelineEntry[];      // Master Timeline — YKSI KELLO
  scenarios: DecisionPoint[];     // S01–S15
  guidance: GuidanceRule[];       // G-01..G-03
  corpus: CorpusEntry[];          // wiki + havainnot + häiriösyötit, aikaindeksoitu
  agents: AgentArc[];             // naapurikaistat, KILO, omat muodostelmat
  radio: RadioMessage[];          // teksti + esirenderöity audiotiedosto + tSim
  probes: { spam: SpamItem[]; sagat: { freezes: Freeze[]; pools: SagatPool[] } };
  threat: { perimeters: string; fuelParams: string; };   // leivotut assetit
  rubric: DecisionQualityRubric;  // LCES-portti + 5 ulottuvuutta painoineen
}
```

Kolme skeeman yksityiskohtaa, jotka kannattaa lukea tarkkaan:

```ts
interface DecisionOption {
  id: string;                     // 'S05_forward_dozer'
  label: string;
  lces: { lookouts: boolean; comms: boolean; escape: boolean; safetyZone: boolean };
  resourceCost: { waterPct?: number; timeMin?: number; commits?: string[] };
  effects: StateDelta[];          // deterministinen vaikutus maailmaan
  qualityAnchor: 0|1|2|3;         // asiantuntijoiden konsensuksesta, EI teoriasta
  blockedBy?: string[];           // ['G-01'] — sitova haara estää
  alignedWithPrecedent?: string;  // naapurin päätös, johon tätä verrataan (decision_alignment)
}

interface AgentArc {
  id: 'CHARLIE'|'ECHO'|...|'KILO-2';
  style: 'methodical'|'aggressive'|'follower'|'aggressive_low_insight'|'conservative'|'analytical'|'terse';
  beats: { tSim: number; position?: [number,number]; action?: string;
           writesCorpus?: string[]; radio?: string }[];
}

interface SpamItem {
  id: string; tSim: number; level: 1|2|3;
  text: string; groundTruthQuery: string;   // vastaus lasketaan tilasta, ei kirjoiteta käsin
  mustBeInGap: true;                        // validaattori tarkistaa
}
```

## 3.3 Validaattorin säännöt

Nämä ovat toteutettavia tarkistuksia, eivät toiveita. Jokainen on yksi funktio ja yksi testi.

| # | Sääntö | Miksi |
|---|---|---|
| R1 | Jokainen `dp_id` esiintyy täsmälleen kerran Scenario Spinellä, Scenario Flow'ssa, Paper 2 -taulukossa ja Paper 3 -taulukossa | Välilehtien eriytyminen |
| R2 | Aikajanan ikkunat eivät saa mennä päällekkäin **paitsi** dokumentoiduilla poikkeuksilla (S06 × S07) | Kuormitus on suunniteltua, ei vahinko |
| R3 | Ikkunoiden summa + jäädytykset = istuntolohkon pituus (88 sim + 10 jäädytys = 98) | Aritmetiikkavika löytyi jo kerran auditissa |
| R4 | `delivery === 'uncued'` ⇒ ei `options`-palkkia, ei `confidencePrompt`, ei countdownia, eikä yhtään aikajanan tapahtumaa, joka merkitsee kyseisen ikkunan | Negatiivisen vihjeen mittari |
| R5 | Jokainen SPAM-osio on **kaikkien** päätösikkunoiden ulkopuolella, myös näkymättömien | Ei kilpaile mitattavan päätöksen kanssa |
| R6 | Mikään ei ajoitu jäädytystä tai SPAM-osiota **edeltävään** 60 s ikkunaan, joka voisi vihjata siitä | Ennakoinnin esto |
| R7 | Jokaisella `blockedOptions`-viitteellä on olemassa oleva optio-id | Sitova haara ei saa estää olematonta |
| R8 | Neuvovan ja sitovan tekstin pituusero ≤ 15 % ja tarkkuustasot vastaavat | Manipulaation puhtaus |
| R9 | Jokaisella korpusmerkinnällä on `validFrom`, ≥ 1 kyselypolku ja lähde; S08:n esioireella ≥ 3 polkua | Löydettävyys ei saa olla ajoituksen tuuria |
| R10 | Häiriösyöttien suhde relevantteihin ≥ 3:1 kussakin vaiheessa | Haulla oltava kustannus |
| R11 | Ehdon A tulos ei sisällä `rationale`- eikä `confidence`-avainta missään kyselyssä millään ajanhetkellä | Manipulaation eheys |
| R12 | Takamaaston kyselyt palauttavat ≤ N merkintää ennen 1:01 | S10 pysyy tyhjänä |
| R13 | Ei `guidance`-tapahtumaa välillä 0:48–1:11 | Hiljaisuus on mitattava |
| R14 | Jokaisella optiolla on LCES-tila ja laatuankkuri | Portti ei saa jäädä pisteyttämättä |
| R15 | Naapurikaistojen kaaret eivät ole ristiriitaisia missään tSim-hetkessä (sijainti, tila, korpusmerkintä) | Jatkuvuus |
| R16 | Ehtomerkinnät ovat riisuttavissa: replay-näkymä ei sisällä yhtään merkkijonoa, josta haaran voi päätellä | Sokkokoodaus |
| R17 | Vain sanastossa määritellyt ehtotermit (A/B, neuvova/sitova) — **ei** kolmen haaran termistöä | Ks. V-1 alla |

## 3.4 Ristiriidat, jotka validaattori löytää työkirjasta tänään

Kävin työkirjan välilehdet ristiin samalla tavalla kuin auditti 18 kuvaa. Kuusi asiaa on
epäsynkassa juuri nyt. Yksikään ei näy yhdeltä välilehdeltä, ja kaikki ovat halpoja korjata nyt ja
kalliita korjata pilotin jälkeen.

| ID | Löydös | Missä | Sääntö | Ehdotettu ratkaisu |
|---|---|---|---|---|
| **V-1** | **Kolmen haaran termistö elää yhä kolmella välilehdellä.** `Peer Wiki Content` sanoo "Group C sees in full; Group B sees the outcome line only", `Agent Spec` sanoo "Group C sees these; groups A and B do not", ja `Development Spec` määrittelee wikin renderöinnin muodossa "none / summary / full". Päätös 21.8. on kaksi haaraa: A = vakiotieto, B = A + perustelu ja luottamus. | 3 välilehteä | R17 | Korvaa kaikki C-viittaukset B:llä ja "none/summary/full" muodolla "standard / +rationale". **Tämä on rakennusvirhe odottamassa tapahtumistaan**: kehittäjä toteuttaisi kolmiportaisen renderöinnin. |
| **V-2** | **SPAM-osio 1 on päätösikkunan sisällä.** Master Timeline: SPAM 1 klo 0:10, merkintä "in the gap before S03". S02:n ikkuna on 0:08–0:12. Osio osuu ikkunan keskelle. | Master Timeline vs. oma sääntönsä | R5 | Siirrä SPAM 1 hetkeen 0:12:30 (S02:n sulkeutumisen ja S03:n alun 0:13 väliin on vain 30 s) — tai realistisemmin: siirrä S03:n alkua 0:14:ään ja SPAM 1 hetkeen 0:12:45. Vaatii aikajanan uudelleenlaskennan, mikä on juuri se syy, miksi aikajana on yksi tiedosto. |
| **V-3** | **G-02 on merkitty annettavaksi S06:ssa, joka on uncued.** Master Timelinellä ei ole ohjaustapahtumaa S06:ssa. Jos G-02 lähetettäisiin verkkoon, se olisi vihje siitä, että S06:ssa tapahtuu jotain — ja tuhoaisi koko negatiivisen vihjeen mittarin. | Guidance Texts vs. Master Timeline vs. Scenario Flow | R4, R13 | G-02 on **voimassa oleva rajoitetila** (`delivery: 'standing_state'`), joka on ohjauspaneelissa S05:stä lähtien. Mitään ei lähetetä S06:ssa. Kirjattu dokumenttiin 1 kohtaan 1.10. |
| **V-4** | **SPAM-osio 3 (0:44) osuu S06:n näkymättömän ikkunan (0:36–0:44) päätepisteeseen.** Sääntö "vain ikkunoiden väleissä" kirjoitettiin näkyviä ikkunoita ajatellen, mutta uncued-ikkuna on mittaava ikkuna siinä missä muutkin — ja koetin juuri sen sulkeutuessa voi joko herättää huomaamaan hiljaisuuden tai peittää sen. | Master Timeline | R5 | Siirrä SPAM 3 hetkeen 0:45. Kapea rako (S06 sulkeutuu 0:44, radiovihje 0:46) — vaihtoehtoisesti poista SPAM 3 kokonaan ja siirrä sen taso 3 -mittaus jäädytykseen F2. |
| **V-5** | **Esioire "kirjoitetaan S07:n aikana" ei pidä paikkaansa aikajanan omilla luvuilla.** Esioire on 0:40; S07:n ikkuna on 0:34–0:39. 0:40 on S07:n sulkeuduttua ja S06:n näkymättömän ikkunan sisällä. | Master Timelinen selitysteksti vs. sen taulukko | R2 | Joko pidennä S07:n ikkuna 0:41:een (jolloin selitys pitää) tai korjaa selitys muotoon "S06:n näkymättömän ikkunan aikana". Suositus: **pidennä S07** — silloin esioire saapuu kesken aktiivista tulkintatehtävää, mikä on juuri se realismi, jota selitysteksti tavoittelee. |
| **V-6** | **`wiki_open_count` ja `wiki_dwell_ms` ovat jäänteitä erillisestä wiki-paneelista.** Päätös 21.8. (`REVIEW NOTES` #5) yhdisti naapurit, IR:n ja ohjauksen yhdeksi kyselypinnaksi. Erillistä avattavaa wikiä ei ole, joten näillä muuttujilla ei ole lähdettä. | Measures vs. Information Access | R1 | Määrittele uudelleen: `rationale_query_count` (montako kyselyä koski perustelu- tai luottamuskenttää) ja `answer_dwell_ms` (on jo listalla). Poista wiki-muuttujat, tai analyysi viittaa muuttujiin joita ei ole. |

Näiden lisäksi yksi **ei-vika mutta rakennusriski**: `Measures`-välilehti nimeää `query_count`-muuttujan
hypoteesin H2.3 mittariksi, kun taas analyysisuunnitelma rajaa vertailun vain molemmille ehdoille
yhteisiin kenttiin. Loki on siis eriteltävä kentittäin alusta asti (`query_slot_what` on jo listalla) —
jos kyselyt lokitetaan vain yhtenä lukumääränä, H2.3:a ei voi laskea jälkikäteen.

## 3.5 Sisällöntuotannon työmäärä — mikä on oikeasti tekemättä

Työkirja sanoo itse, että noin 70 % sisältövälilehdistä on pohjia. Se ei ole yksityiskohta vaan
usean viikon kirjoitustyö, ja se on tämän projektin todennäköisin aikataulun kaataja — ei koodi.

| Sisältö | Tarvitaan | Valmiina | Arvio |
|---|---|---|---|
| Korpusmerkinnät (relevantit) | ~60 | 2 | 3–4 vk |
| Häiriösyötit (3:1) | ~180 | 0 | 1–2 vk (osin generoitavissa mallipohjista) |
| Ohjaustekstit | 3 paria | 3 paria | valmis, kielentarkistus |
| Optiojoukot 15 pisteeseen | ~70 optiota LCES-tiloineen | 0 | 2 vk + asiantuntijakatselmus |
| SPAM-osiot | 12 | 4 esimerkkiä | 1 vk |
| SAGAT-altaat (tasoittain) | ~40 osiota | 0 | 1–2 vk |
| Radioviestit + äänitys | ~120 viestiä | 0 | 2 vk + studiopäivä |
| Laatuankkurit | 15 pistettä × 4 tasoa | 0 | Asiantuntijatyöpaja, **pisin läpimenoaika** |

**Aloita laatuankkureista ja asiantuntijoiden rekrytoinnista tänään.** Ne ovat ainoa kohta, jonka
läpimenoaikaa et voi itse lyhentää, ja ne portittavat kaksi hypoteesia.
