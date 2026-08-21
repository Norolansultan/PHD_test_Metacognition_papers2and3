# 4. Kartta ja maasto — prototyypistä instrumentin renderöijäksi

`harjulakartta.html` (siemen 20260821) on **hyvä prototyyppi ja väärä ajoaikainen ratkaisu**.
Se on tehnyt tehtävänsä: se todistaa, että proseduraalinen maasto voi näyttää peruskartalta, se on
deterministinen samalla siemenellä, ja sen operatiivinen kerros istuu `Shared World` -välilehden
maastoon oikein. Se ei kuitenkaan ole muoto, jossa kartta menee kolmensadan osallistujan eteen.

Tämä dokumentti kertoo, mikä siinä pidetään, mikä siirretään ja mikä rakennetaan uudestaan.

---

## 4.1 Mitä prototyyppi tekee oikein — nämä pidetään sellaisenaan

| Piirre | Miksi se on oikein |
|---|---|
| **Deterministinen kenttä siemenestä** (`mulberry32` + permutaatiotaulu + fBm) | Sama siemen, sama maasto, aina. Tämä on koko instrumentin perusvaatimus. |
| **Maasto ennen ihmisen jälkeä** — korkeus → luokitus → tiet harjulla → rakennukset teiden varsilla | Oikea kausaalijärjestys. Suomalainen tie kulkee harjulla, ja tässä se kulkee, koska `ROADS[0]` on johdettu `ESKERS[0]`:sta. Sama ratkaisu on peleissä nimellä "grammar over decoration". |
| **Peruskarttagrafiikka**: korkeuskäyrät marching squares -menetelmällä, suon vaakaviivoitus, tien kaksoisviiva reunuksella, kursivoidut siniset vesinimet | Käytännön asiantuntija tunnistaa kartan lajityypin sekunnissa. Tämä on realismivalidointiportin läpäisyn edellytys. |
| **Kaksi mittakaavaa** (1:120 000 ja 1:16 000) ja niiden sisäkkäisyys | Vastaa täsmälleen `Shared World` -välilehden ratkaisua. Sektori 13,2–17,2 × 16,2–20,2 km = tasan 4 × 4 km. |
| **Operatiivinen kerros erikseen kytkettävänä** | Oikea idea: pohjakartta ja tilannekuva ovat eri kerroksia. |
| **Maaston ja skenaarion yhteensopivuus** | Linja harjun laella, saha linjan eteläpuolella (≈0,8 km), varalinja takana, Louhensuo lounaassa takamaastossa, palorintama pohjoisessa. Tämä *on* työkirjan maailma, ei jotain sinne päin. |

Kanoninen naapurinimistö (CHARLIE…JULIET) on kartassa jo oikein — se ratkaisee `REVIEW NOTES` #10:n
nimeämisristiriidan kartan hyväksi.

## 4.2 Mikä estää sen käytön sellaisenaan

**1. Se generoi maaston ajoaikana, ja se on hidas.** Mittasin generaattorin irrotettuna Nodeen:
`elev()` + `classify()` 470 × 470 -ruudukolle vie **1,54 s** (200 000 pelkkää `elev()`-kutsua: 275 ms).
Päälle tulevat korkeuskäyrät marching squaresilla noin 17–34 tasolla, teiden ja nimistön piirto.
Selaimessa yhden näkymän tuottaminen on sekuntien luokkaa — tiedosto näyttää siksi itsekin tekstin
"GENEROIDAAN MAASTOA…". Instrumentissa kartan on oltava pystyssä välittömästi ja pysyttävä
responsiivisena, kun sen päälle piirretään yksiköitä, rintamaa ja vanhentuneisuutta 4 Hz:llä.

**2. Determinismi ei kanna selaimesta toiseen.** `Math.exp`, `Math.hypot` ja `Math.sin` ovat
ECMAScriptissä toteutuskohtaisia viimeisten bittien osalta. Sama siemen tuottaa saman kartan
*samassa* selaimessa, muttei takuulla identtistä korkeuskäyräpolkua Chromen ja Firefoxin välillä tai
edes Chromen versioiden välillä. Osallistujien on nähtävä pikselintarkasti sama kartta koko
aineistonkeruun ajan, myös kahden vuoden päästä.

**3. Maailma ja renderöinti ovat samassa tiedostossa.** `ESKERS`, `LAKES`, `ROADS`, `FACTORY`,
`NAMES`, `SECT` ja `OPS` ovat vakioita piirtokoodin seassa. `OPS` sisältää linjan, varalinjan,
komentopaikan ja naapurien sijainnit — eli **skenaariodataa**, joka kuuluu sisältöpakettiin ja jonka
validaattorin on nähtävä. Nyt se on kahdessa paikassa heti kun skenaariot kirjoitetaan.

**4. Ruudukon koordinaatit eivät ole uskottavia.** Pystylinjat saavat tekstin `6820+x` ja
vaakalinjat `7420−y`. ETRS-TM35FIN:ssä itäkoordinaatti on kilometreinä kolminumeroinen (n. 100–750)
ja pohjoiskoordinaatti seitsennumeroinen metreinä (6 600–7 800 km). Nelinumeroinen "itäkoordinaatti"
6820 ei ole mahdollinen. Käytännön asiantuntija huomaa tämän, ja realismivalidointiportti on juuri
se paikka, jossa se huomataan. (Sivuhuomio: `padStart(4)` nelimerkkiselle merkkijonolle ei tee mitään.)

**5. Ei koordinaattirajapintaa, ei osumatestausta, ei kerroksia.** `X()`/`Y()` ovat sulkeumia
render-funktion sisällä. Instrumentti tarvitsee palvelun: maailma-km ↔ TM35FIN ↔ ruutupikseli,
kaikissa mittakaavoissa, plus käänteismuunnos klikkauksille ja etäisyys-/aikalaskennalle.

**6. Ei havaintokerrosta.** Kartta piirtää kaiken, mitä se tietää. Instrumentin kartta saa piirtää
vain sen, mitä *tämä* osallistuja on havainnut, ja senkin ikäänsä vastaavasti haalennettuna.

## 4.3 Kohdearkkitehtuuri: leivo kerran, renderöi nopeasti

```
tools/terrain-bake.ts            (Node, ajetaan kerran, tulos versionhallintaan)
  ├─ syöte: seed 20260821 + maastoparametrit (samat funktiot kuin prototyypissä)
  ├─ elev()/classify() koko alueelle, kaksi resoluutiota
  └─ tuotos
       ├─ base_incident.png        1:120 000 pohjakartta, valmiiksi piirretty
       ├─ base_sector.png          1:16 000 pohjakartta
       ├─ terrain_incident.bin     luokitusruudukko  (Uint8, 30 km / 60 m)
       ├─ terrain_sector.bin       luokitusruudukko  (Uint8, 4 km / 8 m)
       ├─ elevation_sector.bin     korkeus (Float32, rinteet palomalliin)
       ├─ vectors.json             tiet, rannat, korkeuskäyrät, nimistö, rakennukset
       └─ manifest.json            seed, parametrit, jokaisen tiedoston SHA-256
```

**Sama versiolukko kuin MML-aineistolla olisi ollut.** Työkirja vaatii, että karttalähde jäädytetään
ja hashataan toistettavuuden vuoksi. Generoidulla maastolla vaatimus ei katoa — se vain siirtyy
siemenestä leivottuihin assetteihin. Jos generaattoria muutetaan kesken aineistonkeruun, manifestin
hash muuttuu, build huomaa sen ja kieltäytyy jatkamasta ilman uutta sisältöversiota.

**Ajoaikainen renderöijä on kolmikerroksinen canvas:**

```
kerros 0  pohjakartta        leivottu PNG, piirretään kerran, ei koskaan uudelleen
kerros 1  havaittu maailma   rintama, naapurit, tiedustelupeitto, vanhentuneisuushaalennus  (4 Hz)
kerros 2  oma tilanne        muodostelmat, linja, varalinja, kohde, valinnat, mittanauha    (4 Hz)
```

Kerrokset 1–2 piirtävät joitakin satoja vektorielementtejä. Se on canvas 2D:lle olematon kuorma,
ja koko 1,5 sekunnin generointikustannus katoaa ajoajasta kokonaan.

## 4.4 Koordinaattipalvelu

```ts
// yksi moduuli, yksi totuus, käytössä myös palomallissa ja lokissa
class Coords {
  worldToTM35(x_km: number, y_km: number): [E: number, N: number];   // affiini, origo manifestista
  worldToScreen(x_km, y_km, view: 'incident'|'sector'): [px, py];
  screenToWorld(px, py, view): [x_km, y_km];
  distanceKm(a: Pos, b: Pos): number;
  travelTimeMin(a: Pos, b: Pos, mode: 'road'|'foot'): number;         // 40–60 km/h | 3–4 km/h
}
```

**Pohjoinen on ylhäällä molemmissa mittakaavoissa** (prototyypissä jo, koska ruudukon
pohjoiskoordinaatti kasvaa ylöspäin). Valitse manifestiin uskottava fiktiivinen origo, esim.
E 420 km / N 6 850 km, ja renderöi ruudukon nimiöt siitä. Fiktiivisiä nimiä oikean näköisillä
koordinaateilla — sisältää täsmälleen sen realismin, jota tarvitaan, eikä yhtään paikallistuntemuksen
sekoittavaa tekijää (`OPEN DECISIONS` #10 on tämän jo ratkaissut generoinnin hyväksi).

## 4.5 Operatiivinen kerros muuttuu datasta piirretyksi

Prototyypin `OPS`-objekti puretaan sisältöpakettiin piirteiden rekisteriksi:

```yaml
features:
  - { id: main_line,     type: line,    role: anchor,     geom: [[13.5,19.25],...] }
  - { id: fallback_line, type: line,    role: fallback,   geom: [[13.7,19.6],...] }
  - { id: cmd_post,      type: point,   role: command,    geom: [14.85,19.35] }
  - { id: objective,     type: polygon, role: objective,  geom: [...], name: "Harjulan saha" }
  - { id: sector_bravo,  type: bbox,    role: sector,     geom: [13.2,16.2,17.2,20.2] }
  - { id: rear_sw,       type: polygon, role: rear_ground,geom: [...] }   # tähän käännös puree
peers:
  - { id: CHARLIE, sectorCentre: [9.5,18.6] }   # ...
```

Sen jälkeen kartta ei tiedä skenaariosta mitään: se piirtää sen, mitä sisältöpaketti sanoo ja mitä
havaintokerros päästää läpi. Validaattori voi tarkistaa, että jokainen skenaariotekstissä mainittu
piirre on olemassa geometriana — mikä on juuri se ristiinlukeminen, jota työkirja peräänkuuluttaa.

## 4.6 Palorintaman leipominen

```
tools/fire-bake.ts
  syöte : terrain_sector.bin + elevation_sector.bin + polttoaineparametrit + tuulikäsikirjoitus
  malli : anisotrooppinen leviäminen; nopeus polttoaineluokan ja rinteen mukaan;
          suunta tuulesta; turve kytee hitaasti ja voi nousta uudelleen
  tapahtuma : tuulen käännös 60° hetkellä 2880 s (0:48)
  tuotos: fire_perimeters.json — kehä per simulaatiominuutti (89 polygonia) + SHA-256
  portti: asiantuntijakatselmus otoksista 0:20, 0:50, 1:15 ennen käyttöä
```

Kolme asiaa, jotka leivotun rintaman on todistettava ennen hyväksyntää:

1. **Ennen käännöstä** pääjuoksu tulee pohjoisesta avomaata ja tiekäytävää pitkin, ja itäinen
   peitteinen suunta vain kytee — havaittavissa mutta ei uhkaavan näköisenä.
2. **Käännöksessä** itäinen suunta tulee linjaan uuden tuulen kanssa ja lähtee juoksuun.
3. **Käännöksen jälkeen** juoksu **koukkaa linjan itäpään ympäri** kohti huoltoreittiä ja
   takamaastoa. Palo ei koskaan ilmesty linjan taakse; se kiertää sen. Työkirjan auditin kohta 18(6)
   löysi tämän ja korjasi sanamuodon — se on korjattava myös geometriassa, tai käytännön asiantuntija
   hylkää koko skenaarion yhdellä katseella.

## 4.7 Realismivalidointiportti

Sama portti kuin polttoaine- ja leviämisparametreilla: **kolme kokenutta kaistanjohtajaa, yksi
kysymys** — "voisiko tämä olla peruskarttalehti, ja voisiko palo käyttäytyä näin tällä maastolla?"
Iteroi siementä ja parametreja kunnes vastaus on kyllä. Portti läpäistään kerran, ja sen jälkeen
siemen ja assetit lukitaan istuntoon nro 1 asti.

Konetarkistukset, jotka ajetaan jokaisella leivonnalla (prototyyppi on jo varmennettu headlessina
vastaavilla luvuilla, ne siirretään testeiksi):

```
✓ harjun reliefi ympäröivään maastoon ≥ +18 m
✓ päälinjan solut harjun laella 100–110 m
✓ kohde rakennettavalla maalla, linjan eteläpuolella, etäisyys 0,7–1,1 km
✓ takamaastossa lounaassa suoreunaista maastoa (Louhensuo) ja suolampi
✓ nolla tie- tai rakennussolua vedessä
✓ vesi 4–6 %, suo 6–9 %, pelto 2–5 % onnettomuusalueella
✓ jokainen piirteiden rekisterin geometria osuu sille sopivalle maastoluokalle
```

## 4.8 Mitä prototyypistä siirretään koodina

| Prototyypin osa | Kohde |
|---|---|
| `mulberry32`, `PERM`, `vnoise`, `fbm` | `packages/terrain/noise.ts` — sellaisenaan |
| `ESKERS`, `elev`, `LAKES`, `BOGS`, `WATER_LEVEL`, `classify` | `packages/terrain/field.ts` — sellaisenaan, testien alle |
| `drawContour` (marching squares) | `tools/terrain-bake.ts` — vain build-aikaan, tuottaa vektoreita |
| Peruskarttatyyli (värit, suon viivoitus, tien reunus, nimistön typografia) | `tools/terrain-bake.ts` — pohjakartan piirto |
| `ROADS`, `FARMS`, `FACTORY`, `NAMES` | Leivotaan `vectors.json`:iin |
| `SECT`, `OPS` | **Sisältöpakettiin**, ei koodiin |
| `render`, `cache`, `VIEWS`, UI-napit | Korvataan renderöijällä ja React-käyttöliittymällä |
| `compass`, `scalebar` | Siirretään kerrokseen 2, mittakaava lasketaan koordinaattipalvelusta |

Työmääräarvio maastoputkelle kokonaisuudessaan: **1,5–2 viikkoa**, josta suurin osa on
pohjakartan piirtokoodin siirtoa ja assettien varmentamista. Prototyyppi on säästänyt tästä
jo helposti viikon — se on tehnyt vaikeimman osan, joka on löytää parametrit joilla maasto
näyttää suomalaiselta.
