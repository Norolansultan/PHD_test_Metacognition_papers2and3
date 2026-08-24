# 1. Alustan arkkitehtuuri

> Suunnitteluperiaate: **tämä on tutkimusinstrumentti joka sisältää simulaation.** Kun immersio ja
> mittaus ovat ristiriidassa, mittaus voittaa. Käyttöliittymä on kertakäyttötavaraa; projektiomoottori
> ja lokitusskeema eivät ole.

Alusta palvelee molempia keruita. **Tutkimus I (armeija) rakennetaan ensin**, Tutkimus II (pelastus)
on sisältöpaketti, joka ei vaadi moottorimuutoksia.

---

## 1.1 Kokonaiskuva

```
┌─ BUILD-AIKA (Node) ─────────────────────────────────────────────────────────┐
│  sisältölähde → compiler → VALIDAATTORI → content-pack.json + SHA-256       │
│  maastogeneraattori → baker → ruudukko + näkyvyys + assetit + hash          │
│  CMO-ajot → parametritaulukko → asiantuntijavalidointi → model-params.json  │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │ versioidut, muuttumattomat assetit
┌─ SELAIN (osallistuja, oma laite) ───────────────────────────────────────────┐
│  ┌── SIM CORE (puhdas TS, ei DOMia, ei satunnaisuutta) ─────────────────┐   │
│  │  Clock · Scheduler · WorldState · AgentRunner · ThreatModel          │   │
│  │  ErrorInjector · GuidanceDelivery · ProbeScheduler                   │   │
│  └───────────┬──────────────────────────────────┬───────────────────────┘   │
│              │ havaintoportti                   │ tapahtumavirta            │
│  ┌───────────▼─────────┐            ┌───────────▼─────────────────────┐     │
│  │ UI-kerrokset        │            │ TELEMETRIA                      │     │
│  │ kartta · tilannekuva│            │ append-only · idempotentti      │     │
│  │ viesti · kysely     │            │ offline-jono · 30 s snapshot    │     │
│  │ koetin · pimennys   │            └───────────┬─────────────────────┘     │
│  └───────────┬─────────┘                        │                           │
└──────────────┼──────────────────────────────────┼───────────────────────────┘
               │ HTTP, kuittaus <300 ms           │ lataus
┌──────────────▼──────────────────────┐  ┌────────▼────────────────────────────┐
│ PROJEKTIOMOOTTORI (oma palvelu)     │  │ LOKIPALVELU + HALLINTANÄKYMÄ        │
│ jäsennin → tilamalli → esitys       │  │ istuntojen tarkastelu kesken keruuta │
│ virheinjektio · siemen · versiotag  │  │ suodatus · JSON-vienti · terveys     │
└─────────────────────────────────────┘  └─────────────────────────────────────┘
```

**Neljä kovaa rajaa:**

1. **Sim core ei tunne DOMia eikä verkkoa.** Ajettavissa Nodessa 1000× ja hashattavissa. Ainoa tapa
   todistaa determinismi ennen kuin kukaan istuu koneelle.
2. **Projektiomoottori on erillinen palvelu alusta asti.** Ei myöhemmin irrotettavaksi tarkoitettu
   moduuli. Se on ainoa osa, joka elää käyttöliittymän jälkeen, ja se on myös oma menetelmäartikkelinsa.
3. **Havaintoportti on ainoa reitti maailmasta ruudulle.** Ei ohituksia.
4. **Ehdot ovat konfiguraatiota, ei koodia.** Jos ehdon vaihto vaatii käännöksen, se huomataan
   kolmantena keruupäivänä eikä ennen sitä.

## 1.2 Teknologia

| Kerros | Valinta | Perustelu |
|---|---|---|
| Kieli | TypeScript, strict | Yksi kieli buildille, ytimelle, UI:lle ja johdannaisskripteille |
| Ydin | Puhdas TS, ei riippuvuuksia | Testattavissa headlessina, hashattavissa |
| UI | React + tapahtumapohjainen store | Tilamuutokset ovat jo tapahtumia; sama virta menee lokiin |
| Kartta | Canvas 2D, kolme kerrosta | Ruutu-/heksapohjainen 2D. WebGL olisi ylimitoitettu |
| Moottori | Node/Fastify, oma palvelu | HTTP-rajapinta, ei jaettua tilaa käyttöliittymän kanssa |
| Jäsennin | Sääntöpohjainen + LLM varalla (lämpötila 0) | Ks. K-2 vaikutusanalyysissä |
| Tila levyllä | IndexedDB, append-only + snapshot | Etäkeruussa verkko katkeaa; istuntoa ei saa menettää |
| Tunniste | **URL-parametri** | Ei kirjautumista, ei käyttäjähallintaa |
| Ääni | Esirenderöity per radioviesti | Sanatarkka determinismi koskee myös ääntä |

**Pois rajattu:** kirjautuminen, käyttäjähallinta, responsiivisuus, 3D, fotorealismi, ajoaikainen
generatiivinen päättely, kauneus ennen kuin pilotti osoittaa tarpeen.

## 1.3 Etäkeruu — mitä se muuttaa

Etäosallistuminen omalla laitteella oli ratkaiseva mahdollistaja sadan osallistujan otokselle. Se
maksaa neljä asiaa, jotka on ratkaistava koodissa eikä ohjeissa.

| Ongelma | Ratkaisu |
|---|---|
| **Ruudun pimennys** ei ole enää valvotun tilan asia | Fullscreen API + `visibilitychange` + `blur`. Jäädytys alkaa vasta kun fullscreen on aktiivinen. Jokainen poistuminen lokitetaan `focus_lost`-tapahtumana ja on poissulkukriteerin syöte |
| **Toinen näyttö** on mahdoton estää | Ei yritetäkään estää. Mitataan: välilehden vaihto, ikkunan koon muutos, fokuksen menetys jäädytyksen aikana. Raportoidaan rajoitteena |
| **Selainkirjo on hallitsematon** | Maasto ja kartta **leivotaan** asseteiksi ja hashataan. Ajoaikana ei generoida mitään. Minimiviewport tarkistetaan ennen aloitusta ja istunto estetään sen alle |
| **Kato on suurempi** | Suunnittele 80 käyttökelpoiselle, rekrytoi 100–110. Keskeytyneet istunnot tallentuvat ja ovat analysoitavissa keskeytyskohtaan asti |

Valvotun istunnon tutkijakonsoli korvautuu **hallintanäkymällä**: keskustelujen ja lokien tarkastelu
kesken aineistonkeruun, suodatus, JSON-vienti, istunnon terveystila. Tutkija ei ohjaa istuntoa vaan
seuraa sitä.

## 1.4 Kello ja aikaperusta

```ts
type Clock = { tSimMs: number; running: boolean; rate: 1 };  // 250 ms askel, ei delta-timea
```

Kello pysähtyy vain jäädytyksessä. **Jäädytyksen aikana pysähtyy myös kyselymahdollisuus** — moottori
kieltäytyy vastaamasta, ja kieltäytyminen lokitetaan. Kaikki aikaleimat ovat skenaarioaikaa;
seinäkelloaika kulkee rinnalla vain järjestystä ja ääniraidan synkronointia varten.

Skenaario etenee ajassa, ei osallistujan toiminnasta. Ajastin ei odota koskaan.

## 1.5 Ehtojen hallinta

```ts
interface SessionConfig {
  participantId: string;          // URL-parametrista
  study: 'I' | 'II' | 'PILOT' | 'CALIBRATION';
  channel?: 'human_mediated' | 'ai_mediated';       // vain Tutkimus I, muuttumaton
  socialInfo?: 'none' | 'raw_peer' | 'peer_in_projection';  // vain Tutkimus II
  // täsmälleen toinen näistä on asetettu; validaattori tarkistaa
  probeDensity: 'dense' | 'sparse';                 // reaktiivisuuskontrolli
  scenarioId: string; seed: number; contentVersion: string;
}
```

Ehto määrätään istunnon alussa ja **kirjoitetaan lokin ensimmäiselle riville**. Alusta ei tarjoa
mitään reittiä kanavan vaihtamiseen kesken session — ei tutkijalle, ei osallistujalle. Kanavan
koherenssi on koeasetelman ehto (K-5), joten sen rikkoutuminen ei saa olla teknisesti mahdollista.

## 1.6 Kerrokset

| Kerros | Sisältö | Mittausvaatimus |
|---|---|---|
| **Kartta** | 2D ylhäältä, ruutu tai heksa, maasto, näkyvyys | Ei paljasta havaitsematonta zoomaamalla |
| **Tilannekuva** | Yksikkömerkit, tunnettu vs. tuntematon, tiedustelutiedon vanheneminen visuaalisesti | Vanhentuneisuus on näkyvä ja luettava |
| **Viesti** | Radioviestit (teksti tai ääni), alhaalta tulevat raportit, ylhäältä tuleva käsky | Epämääräinen käsky saapuu identtisenä kaikille, ei toistu |
| **Kysely** | Vapaa tekstisyöte, vastaus moottorista | Kuittaus <300 ms, ei keinotekoista viivettä |
| **Koetin** | Jäädytys, pimennys, koettimet, luottamusarvio, ISA | Mikään ei ennakoi koetinta |
| **Jälkiselvitys** | Mitä manipuloitiin, miten omat päätökset suhteutuivat käskyyn | Vaiheen 1 toimitus, ei viimeisen viikon lisä |

## 1.7 Kaksikerroksinen maailma

```
GROUND TRUTH (sim core)              PERCEIVED (osallistuja)
─────────────────────────            ────────────────────────────────
todellinen vihollistilanne           viimeksi raportoitu + ikä
yksiköiden todellinen tila           viimeksi raportoitu tila
sään ja maaston totuus               havaittu, katvealueet tuntemattomia
projektion oikea tulos               projektion esitetty tulos (virhelipulla)
alkuperäinen radiokäsky              käskyn esitetty tulkinta
```

Kaksi viimeistä riviä ovat uusia ja ne ovat koko Tutkimus I:n ydin. **Alkuperäinen käsky säilyy
totuuskerroksessa muuttumattomana**, ja se on ainoa asia, jota vasten ajautuma mitataan. Jos se
elää missään muualla kuin totuuskerroksessa, mittaria ei ole.

Automaattitesti: buildaa osallistujaversio, aja istunto headless-selaimessa, greppaa verkkoliikenne
ja `window`-puu totuuskerroksen ja virheinjektion tunnisteiden varalta. Punainen = build ei mene läpi.

## 1.8 Domain-neutraalius

| Ytimessä | Sisältöpaketissa |
|---|---|
| Kello, ajastin, vaiheet | Skenaarion tapahtumat ja tekstit |
| Kaksikerroksinen maailma, havaintoportti | Yksikkötyypit, maaston merkitys |
| Projektiomoottorin rajapinta | Tilamallin parametrit (20–40 per domain) |
| Virheinjektio ja sen lokitus | Vääristymien suunta ja suuruus per skenaario |
| Koetinjärjestelmä, pisteytysrajapinta | Koetinpankki, vaikeustasot, avoimet L3-osiot |
| Käskynvälitys ja ajautumamittari | Käskyjen sanamuodot |
| Lokitus, jälkiselvitys, vienti | Kartta-assetit, piirteiden rekisteri |

```ts
interface ThreatModel {
  stateAt(tSim: number): ThreatState;      // etenevä vastustaja | etenevä palo
  exposureFor(unit: Unit, tSim: number): ExposureLevel;
  displayStyle: 'enemy' | 'fire';
}
```

Rajapinta rakennetaan vaiheessa 1 vaikka toinen domain tulisi vasta vuoden päästä. Jättämättä
jättäminen maksaa myöhemmin uuden projektin verran; tekeminen maksaa nyt päivän.
