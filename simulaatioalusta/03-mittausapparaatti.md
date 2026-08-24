# 3. Mittausapparaatti

Metakognitio on ensisijainen. Endsleyn tasot ovat mittausvälineitä, eivät juonta.

---

## 3.1 Kolme erotettavaa asiaa

| Käsite | Mittaa | Mittari |
|---|---|---|
| **Herkkyys** | erotteleeko luottamus oikeat vääristä | meta-d′, AUROC2 |
| **Kalibraatio** | onko taso systemaattisesti väärä | Brier, yli-/aliluottamus |
| **Efektiivisyys** | herkkyys suhteessa suoritukseen | M-ratio |

Tekoäly voi parantaa tarkkuutta ja samalla romuttaa herkkyyden. Sitä ei näe tarkkuudesta eikä
luottamuksen keskiarvosta — vain näiden kolmen erottelusta.

**Estimointi:** HMeta-d, `hmetad`-paketti R:llä. Yksilöerot ja kovariaatit **mallin sisään
regressiovariantilla**, ei jälkikäteisenä korrelaationa: hierarkkinen kutistuminen vaimentaisi
yhteyden ja tekisi todellisesta efektistä näkymättömän.

## 3.2 Koettimien arkkitehtuuri

**Monta pientä koetinta, ei harvoja isoja.** Binäärinen tai harvaluokkainen, ground truth tiedossa,
luottamusarvio 1–4 jokaisen perässä erikseen — **ei jäädytystä kohti**.

| | Määrä | Mihin riittää |
|---|---|---|
| Kalibraatiopatteri, erikseen etukäteen | 200–400 koettelua | Yksilötason M-ratio, proxy-validoinnin ankkuri |
| Skenaario, per osallistuja | **15–25 koetinta** | Ks. perustelu alla |
| Skenaario, per ehto yhteensä | 600–1000 koettelua | Ryhmätason ehtovertailu, kuormakäyrä, ajallinen kehitys |

**Miksi 15–25 eikä 2.** Päivitetty suunnitelma sanoo "50–80 koetinta per ehto skenaariotehtävässä".
Kirjaimellisesti luettuna se on ehdon **yhteismäärä**, jolloin 40 osallistujaa ehtoa kohti tarkoittaisi
kahta koetinta osallistujaa kohti — mikä on ristiriidassa saman luvun ohjeen "monta pientä koetinta"
kanssa. Rakennetaan tiukemman lukutavan mukaan: koetin noin 3–4 minuutin välein 60–90 minuutin
skenaariossa. Silloin alaraja ylittyy kummallakin lukutavalla, kuormakäyrä on olemassa ja ehdon
sisäinen ajallinen kehitys on analysoitavissa. Yksilötason meta-d′ tulee silti vain patterista.

**Sijoitussääntö.** Aiempi suunnitelma kielsi koettimet päätösikkunoiden sisällä. Se ei ole enää
mahdollista: 15–25 koetinta ei mahdu skenaarion väleihin, kun päätöskohtia on toistakymmentä.
Koettimet saavat siis olla ikkunoiden sisällä, mutta **eivät ikkunan viimeisen 60 sekunnin aikana**
eivätkä **30 sekunnin sisällä projektiovastauksesta** — edellinen kilpailisi sitoutumishetken kanssa,
jälkimmäinen sotkisi feeling of rightness -arvion ja vastauksen lukuajan. Sääntö on validaattorissa (R4).

**Vaikeustaso 65–85 %:n tarkkuuteen.** Tämä on edellytys, ei suositus: ilman vääriä vastauksia
herkkyyttä ei voi laskea lainkaan. Koetinpankki pilotoidaan ja kalibroidaan ennen keruuta, ja
koettimet, jotka osuvat tavoitealueen ulkopuolelle, korvataan.

## 3.3 Arviotyypit

| Ajankohta | Arvio | Mitä se kertoo |
|---|---|---|
| Ennen | feeling-of-knowing / judgment of solvability | Arvioiko osallistuja tehtävän ratkaistavaksi |
| Heti vastauksen jälkeen | **feeling of rightness** | Ennustaa kuinka kauan ajattelua jatketaan. Sujuva AI-vastaus nostaa sitä sisällöstä riippumatta — tämä on sujuvuusharhan suora mittari |
| Jälkeen | retrospektiivinen luottamus | Vakiomittari meta-d′:lle |
| Lopuksi | globaali itsearvio | "Kuinka monta arvioit saaneesi oikein" — globaalin ja paikallisen metakognition ero |

## 3.4 Avoin L3-koetin

Suljetut koettimet eivät mittaa projektioiden **ainutlaatuisuutta**: vastausavaruus on annettu. Yksi
avoin koetin: *"mitä arvioit tapahtuvan seuraavan 30 min aikana ja miksi"*, 30–60 s.

**Jäädytyksiä on kolme.** ISA-koetin on jokaisessa; avoin L3-koetin on kahdessa tai kolmessa sen
mukaan, mitä aikabudjetti pilotissa kestää. Suljetut koettimet eivät ole jäädytyksissä vaan
jakautuvat skenaarioon (3.2).

Kolme johdettua mittaria:

| Mittari | Laskenta |
|---|---|
| **Hajonta** | Kuinka paljon L3-vastaukset varioivat osallistujien välillä ehdoittain — semanttinen etäisyys upotuksilla |
| **Kattavuus** | Montako erillistä uhkaa tai kehityskulkua koko otos tunnisti |
| **Yksinäiset havainnot** | Kuinka moni tunnisti jotain, mitä kukaan muu ei |

**Hypoteesi ja sen kaksi lukutapaa:** AI-välitteinen tilannekuva tuottaa yhdenmukaisempia
projektioita. Yhdenmukaisuus **+ parempi tarkkuus** = tekoäly vähentää kohinaa. Yhdenmukaisuus
**+ sama tarkkuus** = hajautettu redundanssi on menetetty, ja komentoketjussa se on turvallisuuskysymys,
ei tilastollinen nollatulos.

**Resurssiehto:** vaatii koodauskehikon ja toisen koodaajan (Cohenin kappa). Ratkaistava ennen
keruuta — jälkikäteen kehikkoa ei voi rakentaa aineistoon, joka on jo kerätty ilman sitä.

## 3.5 Kognitiivinen kuorma

* **ISA-koetin (1–5) jokaisessa jäädytyksessä.** Kaksi sekuntia, tuottaa kuormakäyrän koko session yli.
* **NASA-TLX vain jälkikäteisenä ankkurina**, ei kesken session.

Kiinnostavin analyysi ja suoraan CATCHin ytimessä: **millä kuormatasolla metakognitiivinen
efektiivisyys romahtaa.** Taitekohta on se, mihin adaptiivinen järjestelmä viritetään — eli tämä
analyysi on paperin D syöte, ei sivutuote.

## 3.6 Havaitsemismittarit

Kanavamanipulaatio ilman havaitsemismittaria on puolikas tutkimus. Kolme osaa, **tässä järjestyksessä,
ilman paluumahdollisuutta**:

1. **Vapaa attribuutio** — "mitkä tekijät vaikuttivat päätökseesi" — ennen kuin mitään lähteitä mainitaan
2. **Pakotettu tunnistus** — lista tekijöitä, arvioi kunkin vaikutus
3. **Käyttäytymissiirtymä** — riippumatta kohdista 1 ja 2

Järjestys on rakennusvaatimus: kyselylomake on yksisuuntainen, edellisiin vastauksiin ei pääse
takaisin, eikä kohdan 2 lista saa olla näkyvissä kohdassa 1. Jos se vuotaa, vapaa attribuutio on
pilalla eikä sitä voi kerätä uudelleen.

**Kiinnostavin solu: suuri siirtymä, nolla attribuutio.** Osallistuja on muuttanut toimintaansa
mutta ei nimeä kanavaa vaikuttajaksi.

## 3.7 Reaktiivisuus — vakava varaus

Luottamuksen kysyminen on itsessään cognitive forcing -interventio: se pakottaa metakognitiiviseen
tarkasteluun, jota ei muuten tapahtuisi. Tämä ei ole pikkuseikka, ja se on kirjattava rajoitteena
riippumatta siitä mitä tehdään.

**Lievennys, molemmat (K-4):**

1. **Harva-koetin-ryhmä, n ≈ 20, ei ristiin pääasetelman kanssa.** 2–3 koetinta koko session.
   Käytetään vain sen tarkistamiseen, eroaako heidän kyselytiheytensä, verifiointinsa ja
   päätösviiveensä tiheästi koeteltujen vastaavista. Ristiin vietynä se puolittaisi solut.
2. **Proxy-painotus tiukan tempon osuuksissa.** Siellä missä koetin häiritsisi eniten, mitataan
   käyttäytymisestä eikä kysymällä.

## 3.8 Metakognitiiviset tilat

Määritellään **suhteellisesti** — poikkeamana henkilön omasta perustasosta tai persentiilinä oman
otoksen jakaumassa. Silloin taksonomia siirtyy tutkimusten välillä vaikka luvut eivät.

| Tila | Tunnusmerkit |
|---|---|
| Kalibroitunut hallinta | herkkyys korkea, bias pieni, verifiointi ∝ epävarmuus |
| **Delegoitu projisointi** | korkea luottamus, ei verifiointia, vastaus = AI:n |
| **Sujuvuusharha** | korkea FOR, lyhyt hyväksymisviive, ei omia what-if:ejä, perustelee AI:n sanoin |
| Romahtanut monitorointi | luottamusjakauma litistyy, herkkyys → 0, kuormavetoinen |
| Hyödytön epäily | matala luottamus myös oikeissa, ylimääräinen verifiointi |
| **Tuottava konflikti** | matala FOR, aktiivinen tarkistus, hypoteesin vaihto |
| Sosiaalisesti johdettu varmuus | luottamus ∝ vertaiskonsensus (vain Tutkimus II) |

**Siirtymät ovat kiinnostavampia kuin tilat.** Lokitus tuottaa trajektorin, ei tilannekuvia.
Adaptiivisen järjestelmän onnistumisen mittari on, kuinka usein se siirtää käyttäjän delegoidusta
projisoinnista tai sujuvuusharhasta tuottavaan konfliktiin.

### Tila-avaruusdokumentti on rakennettava ennen koodia

4–6 tilaa × 4 saraketta:

| Määritelmä | Offline-tunnistus | **Online-proxy + lokikentät** | Mitä AI:n pitäisi tehdä |
|---|---|---|---|
| käsitteellinen | miten tila todetaan jälkikäteen aineistosta | mitkä reaaliaikaiset signaalit ja **mitkä lokikentät niihin tarvitaan** | interventio (saa olla arvaus) |

Neljäs sarake saa olla arvaus. **Kolmas määrää lokitusskeeman, jota ei voi korjata jälkikäteen** —
ja siksi tila-avaruusdokumentti on vaiheen 1 blokkaava toimitus, ei suunnitteludokumentti.

## 3.9 Paperin D proxyt

Logiikka: meta-d′ on jälkikäteen laskettava eikä voi ajaa reaaliaikaista järjestelmää. Siksi kerätään
kallis kultastandardi offline (kalibraatiopatteri) ja halvat käyttäytymisproxyt online **samasta
sessiosta** — ja proxyjen validointi kultastandardia vastaan **on** algoritmin kirjoittaminen.

| Proxy | Lokikentät, jotka sen mahdollistavat |
|---|---|
| Verifiointikäyttäytyminen | `verification_followed`, lähdeviittaus, aikaväli projektiosta |
| Kyselyn monimuotoisuus | `params`-avaruuden variointi peräkkäisissä projektioissa |
| Hypoteesin hylkääminen | Testattiinko vain AI:n ehdotusta vai myös omaa vaihtoehtoa |
| **Hyväksymisviive** | `latency_to_next_ms` + luottamus. Lyhyt viive + korkea luottamus = varoitusmerkki |
| Päätöksen peruuttaminen | Peruutustapahtuma ja sen ajoitus |
| Luottamus–verifiointi-irtikytkentä | Johdettu: korrelaatio romahtaa |

**Siirrettävyyssääntö: piirteet siirtyvät, kertoimet eivät.** Malli sovitetaan regiimikohtaisesti.
Tästä seuraa väite, joka on itsessään kontribuutio: adaptiivinen järjestelmä tarvitsee joko regiimin
tunnistuksen tai erilliset kalibroinnit työtilaa kohti — yhtä geneeristä metakognitiomallia ei voi
kentättää. Tämä väite on empiirisesti tuettavissa **vain jos kaksi regiimiä kerätään** (A-2).

## 3.10 Lokitusskeema

```ts
interface LogEvent {
  event_id: string;          // UUID, idempotenssi
  schema_version: string;    // skeema muuttuu kesken tutkimuksen
  participant_id: string;    // URL-parametrista
  session_id: string;
  study: 'I' | 'II' | 'PILOT' | 'CALIBRATION';
  condition: SessionConfig;  // ensimmäisellä rivillä, muuttumaton
  t_sim_s: number;           // ensisijainen aika-akseli
  t_wall_iso: string;
  phase: 'baseline' | 'post_order';
  actor: 'participant' | 'system' | 'agent';
  event_type: EventType;
  payload: unknown;
}
```

Tapahtumatyypit vaiheessa 1: `projection`, `probe_item`, `confidence`, `isa`, `freeze_start`,
`freeze_end`, `decision`, `order_delivered`, `guidance_route`, `focus_lost`, `verification`,
`state_snapshot`, `debrief_shown`.

**Sääntö:** jos muuttuja ei ole tässä skeemassa, sitä ei ole olemassa. Muuttuja lisätään skeemaan
ennen kuin ominaisuus rakennetaan.

## 3.11 Istunnon rakenne

Kaksi erillistä istuntoa, koska kalibraatiopatteri ei mahdu skenaariopäivään eikä saa syödä
upseerin aikaa siitä.

**Istunto A — kalibraatiopatteri (erikseen, omalla ajalla, oma linkki)**

| # | Lohko | Kesto | Huom |
|---|---|---|---|
| 1 | Suostumus, tunniste URL-parametrista | 5 min | Ei kirjautumista |
| 2 | Ohjeistus ja harjoituskoettelut | 5 min | Luottamusasteikko opetetaan kriteeriin asti |
| 3 | **200–400 koettelua**, luottamus jokaisen perässä | 30–45 min | Yksilötason M-ratio |

**Istunto B — skenaario**

| # | Lohko | Kesto | Huom |
|---|---|---|---|
| 1 | Suostumus, sama tunniste | 5 min | Ehto määrätään ja lukitaan tässä |
| 2 | Käyttöliittymäkoulutus | 10–12 min | Kartta, kyselykenttä, luottamusarvio, jäädytyksen mekaniikka. **Jäädytysten ajankohtia ei mainita** |
| 3 | Harjoitusskenaario | 8 min | Eri maasto; `practice = TRUE` |
| 4 | **Skenaario** | 60–90 min | 15–25 koetinta, 3 jäädytystä (ISA + avoin L3) |
| 5 | **Havaitsemispatteri** | 8 min | Yksisuuntainen: vapaa attribuutio → pakotettu tunnistus (3.6) |
| 6 | NASA-TLX, taustatiedot | 5 min | TLX vain tässä, ei kesken session |
| 7 | **Jälkiselvitys** | 5 min | Mitä manipuloitiin, miten omat päätökset suhteutuivat käskyyn |

Yhteensä istunto B ≈ 1 h 45 min – 2 h 15 min. Etäkeruussa tämä on yläraja: pidempi istunto kasvattaa
katoa, ja kato on jo suurempi kuin valvotussa keruussa.

**Järjestys on sitova.** Havaitsemispatteri on ennen TLX:ää ja jälkiselvitystä; jälkiselvitys on
viimeisenä, koska se paljastaa manipulaation ja pilaisi kaikki sitä edeltävät mittarit.

## 3.12 Mitoitus ja esirekisteröinti

* Suunnittele **80 käyttökelpoiselle**, rekrytoi 100–110. Etäkeruussa katoa tulee enemmän kuin valvotussa.
* **Oikea luku tulee omasta simulaatiosta**: parametrien palautussimulaatio `hmetad`-paketilla omilla
  odotetuilla arvoilla. Päivän työ, ja ainoa numero, jonka arvioija hyväksyy kyselemättä.
* Sadalla saat päävaikutukset luotettavasti, interaktion vain jos se on suuri. **Älä rakenna
  kummankaan paperin pääväitettä interaktion varaan.**
* **Esirekisteröinti (OSF/AsPredicted)** kannattaa sadalla osallistujalla: ilmainen, päivän työ, ja
  vahvistaa paperia erityisesti kun teet harhautusta ja virheinjektiota — juuri niissä arvioija
  muuten epäilee jälkikäteistä hypoteesien sovittelua. Palautussimulaation tulos menee siihen sellaisenaan.
* **Jokainen tutkimus kantaa oman patterinsa.** Eri osallistujat, ei yhteistä ankkuria.
