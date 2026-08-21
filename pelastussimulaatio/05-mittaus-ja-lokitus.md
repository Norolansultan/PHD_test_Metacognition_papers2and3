# 5. Mittaus, lokitus ja analyysipolku

> Työkirjan periaate, joka kannattaa naulata seinään: **jos muuttuja ei ole lokispesifikaatiossa,
> sitä ei ole olemassa.** Muuttuja lisätään listalle ennen kuin ominaisuus rakennetaan, ei sen jälkeen.

---

## 5.1 Tapahtumavirta on ainoa totuus

Instrumentti ei kirjoita "mittaustuloksia". Se kirjoittaa **tapahtumia**, ja jokainen analyysin
muuttuja johdetaan niistä skriptillä. Tämä on peliteollisuuden telemetriamalli ja se ratkaisee
kolme ongelmaa kerralla: uusinta on mahdollinen, johdettu muuttuja voidaan määritellä uudelleen
jälkikäteen ilman uutta aineistonkeruuta, ja loki on auditoitavissa.

```ts
interface LogEvent {
  event_id: string;        // UUID, client-generated → uudelleenlähetys ei tuota duplikaattia
  schema_version: string;  // skeema MUUTTUU kesken tutkimuksen; se on jokaisessa tapahtumassa
  participant_id: string;  // FI-BA-001  (domain-ryhmä-juokseva)
  session_id: string;      // myös keskeytyneille istunnoille
  t_sim_s: number;         // ensisijainen aika-akseli
  t_wall_iso: string;      // järjestys ja äänen synkronointi
  dp_id: string | null;    // S01–S15 tai null päätöspisteiden välissä
  phase: 'P1'|'P2'|'P3'|'P4'|'P5';
  actor: 'participant'|'system'|'agent'|'researcher';
  event_type: EventType;
  payload: unknown;
}
```

### Tapahtumatyypit, jotka on oltava vaiheessa 1

| Tyyppi | Payload | Palvelee |
|---|---|---|
| `dp_onset` / `dp_close` | dp, delivery, windowSec | Kaikki |
| `option_view` | option_id, dwell_ms | `option_count`, harkinnan leveys |
| `decision_commit` | option_id, latency_ms, time_remaining_s, confidence | H2.1, H2.2, H3.1 |
| `non_decision` | dp, default_rule_id, resulting_state_delta | Ei-päätös on löydös, ei puuttuva arvo |
| `uncued_action` | action, latency_from_window_open_s | S06, S08:n esioireet |
| `view_switch` | from, to, dwell_ms | Huomion allokointi paikallisen ja alueellisen välillä |
| `clock_state` | countdown_visible, remaining_s | `time_remaining_at_commit` johdettavuus |
| `state_snapshot` | koko maailmatila | 30 s välein, toipuminen ja uusinta |

### Vaiheen 2 tapahtumatyypit

| Tyyppi | Payload | Palvelee |
|---|---|---|
| `query` | slot_who, slot_what, slot_when, raw_text?, matched_intent, no_match | H2.3, uudelleenkyselyväli |
| `query_response` | response_ids[], observed_at[], latency_ms | Vanhentuneisuuden luettavuus |
| `answer_dwell` | response_id, dwell_ms | Lukeminen vs. vilkaisu |
| `guidance_shown` | rule_id, arm | Manipulaatiotarkistus |
| `block_shown` / `override_opened` / `override_cancelled` / `override_committed` | option_id, rule_id, free_text | H3.3, kitkan mittaus |
| `probe_item` | instrument, item_id, pool_id, level, accept_latency_ms, answer | SPAM/SAGAT |
| `freeze_start` / `freeze_end` | freeze_id, channels_locked | Todiste kanavien lukituksesta |

## 5.2 Johdetut muuttujat — kaikki lasketaan skriptillä, ei kerätä

`analysis/derive.ts` lukee raakatapahtumat ja tuottaa analyysitaulukon. Se on **puhdas funktio**:
sama loki tuottaa samat muuttujat, ja muuttujan määritelmän muutos ajetaan uudelleen koko aineistolle.

| Muuttuja | Johtaminen |
|---|---|
| `detection_latency_s` | Ensimmäinen itään/KILOon/säähän kohdistuva kysely **tai** radiovihjeen jälkeinen toiminta, mitattuna taaksepäin hetkestä 2880 s (0:48) |
| `precursor_route` | `query` \| `radio` \| `none` — mikä reitti tuli ensin. **Havaintoviive raportoidaan reitin mukaan ehdollistettuna**, muuten ajoituksen tuuri sekoittuu mittariin |
| `adaptation_latency_dp` | Päätöspisteiden määrä S08:sta ensimmäiseen kalibroituun poikkeamaan |
| `overcompliance` | S09–S12: valittiin ohjauksen mukainen optio, vaikka data tuki poikkeamaa |
| `deviation_flag` × `decision_quality` | H4.2: **poikkeaman kalibrointi**, ei sen yleisyys |
| `requery_interval_s` | Mediaani simuloitu aika peräkkäisten samaa aihetta koskevien kyselyjen välillä |
| `topic_revisit_breadth` | Useammin kuin kerran kysyttyjen aiheiden lukumäärä |
| `stale_belief_flag` | Osallistuja toimii pisteessä N tiedolla, joka haettiin ennen sen korvaamista |
| `rationale_query_count` | Kyselyt, joissa `slot_what ∈ {rationale, confidence}` — **vain ehto B**, analysoidaan erikseen |
| `comparable_query_count` | Kyselyt kentistä, jotka molemmilla ehdoilla on. **H2.3 ajetaan vain tällä** (auditin kohta 18(7)) |
| `time_remaining_at_commit` | Countdown-tilasta commitin hetkellä |
| `sagat_inferable_flag` | Projektio-oraakkelin `inferableSet` vs. annettu vastaus |
| `window_use_pct` | Latenssi / ikkunan pituus — **pilotin viritysmittari**, tavoite mediaani 50–70 % |

**Kolme sudenkuoppaa, jotka on ratkaistava koodissa eikä analyysissa:**

* **Myöhäinen kyselijä saa rikkaampia vastauksia rakenteesta johtuen.** Tiedonhaku analysoidaan
  vaiheen sisällä ja simuloitu aika on kovariaatti. Älä koskaan vertaa raakaa osumatarkkuutta
  S03:ssa ja S12:ssa.
* **Ei-päätös ei ole puuttuva arvo.** Sen on tultava analyysitauluun omana rivinään, syyllä.
* **`query_count` yksinään on verbaalisuuden mittari.** Otsikkomittari on uudelleenkyselyväli.

## 5.3 Kestävyys: istunto ei saa hävitä

Yksi istunto on 157 minuuttia yhden osallistujan aikaa, joka on rekrytoitu kurssikohortista.
Sen menettäminen teknisen vian takia on kalleinta mitä tässä projektissa voi tapahtua.

```
kirjoitus  →  muistijono  →  IndexedDB (append-only)  →  taustalähetys
                                    │
                                    ├─ snapshot 30 s välein (koko maailmatila)
                                    └─ istunnon päätyttyä: paketti + SHA-256 → lataus ≤15 min
                                                             → varmennus → paikallinen poisto
```

* Verkon katkeaminen ei saa keskeyttää istuntoa **eikä** hukata tapahtumia. Testi: katkaise verkko
  kesken istunnon, jatka 20 minuuttia, palauta verkko — nolla hävinnyttä tapahtumaa, nolla
  duplikaattia (idempotenssi `event_id`:llä).
* Selaimen kaatuminen: uudelleenlataus palauttaa viimeisimmästä snapshotista ja toistaa tapahtumat
  sen jälkeen. Palautus lokitetaan; tutkija päättää jatketaanko vai merkitäänkö istunto
  poissuljettavaksi.
* Tiedostot: `{participant_id}_{stream}.csv`, kansio per osallistuja. Poissuljetut tietueet
  **dokumentoidaan, ei koskaan poisteta**.

## 5.4 Tutkijakonsoli

Erillinen näkymä (toinen ikkuna tai toinen laite), joka ei koskaan koske osallistujan ruutuun.

* Käynnistä / tauko / merkitse / keskeytä
* Elävä tila: missä päätöspisteessä ollaan, mikä ikkuna on auki, mitä vaihetta ajetaan
* **Lokin terveys**: jonon pituus, viimeisin snapshot, latauksen tila — vihreä/punainen
* Merkintätoiminto: tutkija merkitsee poikkeaman (osallistuja kysyi jotain ääneen, laite temppuili)
  ja se menee samaan aikajanaan `actor: 'researcher'`

Valmiin määritelmä: tutkija pystyy ajamaan koko istunnon koskematta osallistujan koneeseen.

## 5.5 Uusinta ja sokkokoodaus

Päätöksen laatu on työkirjan oman arvion mukaan **todennäköisimmin epäonnistuva mittari**, ja se
riippuu koodaajien yksimielisyydestä (tavoite ICC ≥ 0,75; alle 0,60 pudottaa mittarin ensisijaisista).
Koodausympäristö on siis oikea ohjelmistokomponentti, ei jälkikäteinen skripti.

**Uusintanäkymä** toistaa yhden päätöksen: tilanne siinä hetkessä, osallistujan käytettävissä ollut
tieto, tarjolla olleet optiot, valinta ja sen perustelu.

**Sokkovaatimus:** koodaaja ei saa pystyä päättelemään haaraa. Tämä tarkoittaa käytännössä:

* ohjauspaneelin teksti riisutaan tai normalisoidaan (neuvova/sitova sanamuoto paljastaa haaran),
* estetyt optiot renderöidään koodausnäkymässä samalla tavalla kuin estämättömät,
* kyselylokista poistetaan perustelu- ja luottamuskentät (ne paljastavat ehdon B),
* ohituksen vapaa perustelu näytetään vain, jos se on itse päätöksen sisältö — muuten se paljastaa
  sitovan haaran.

Tämä on **rakennusvaatimus, joka unohtuu helposti** ja jonka unohtaminen huomataan vasta kun koodaus
on jo tehty ja pilattu. Siksi se on validaattorin sääntö R16 ja siksi siitä on automaattitesti:
generoi uusintanäkymä molemmista haaroista samalle päätökselle ja vertaa — erot saavat olla vain
päätöksen sisällössä.

## 5.6 Vienti

```
npm run export -- --participant FI-BA-001
  → raw/         tapahtumat, muuttumattomina
  → derived/     analyysitaulukko, derive.ts:n tuottamana
  → manifest     sisältöversio, skeemaversio, karttamanifestin hash, derive.ts:n hash
```

Manifestin merkitys: kahden vuoden päästä on pystyttävä sanomaan, minkä sisältöversion ja minkä
maaston kanssa juuri tämä osallistuja ajoi. Ilman sitä yksikin sisältökorjaus kesken keruun tekee
aineistosta selittämätöntä.

**Valmiin määritelmä:** johdetut muuttujat toistuvat raakatapahtumista skriptillä, ilman käsityötä,
ja kahdesti ajettuna ne ovat bittitasolla samat.
