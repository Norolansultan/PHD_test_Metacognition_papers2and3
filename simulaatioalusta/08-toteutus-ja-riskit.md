# 8. Toteutus, testaus, riskit ja päätökset

## 8.0 Työmääräarvio — ja ristiriita, joka on ratkaistava

Väitöskirjasuunnitelman arvio on **4–6 kuukautta osa-aikaisena** (moottori + jäsennin + kartta +
käyttöliittymä + lokitus + jäädytysmekaniikka). Kun sama työ puretaan alla oleviin vaiheisiin ja
valmiin määritelmiin, alhaalta ylöspäin laskettu summa on **noin 20 henkilötyöviikkoa eli ~5
kuukautta kokopäiväisenä**. Osa-aikaisena (50 %) se on 9–10 kuukautta, ei 4–6.

Ero ei johdu siitä, että toinen arvio olisi väärä, vaan siitä että ne kattavat eri asiat. Yläraja
4–6 kk osuu, jos **nämä jätetään pois**:

| Pois jätettävä | Seuraus |
|---|---|
| Sisältövalidaattori (R1–R17) | Osat ajautuvat erilleen kuukausien aikana — tämä vika on nähty kerran jo |
| Jälkiselvitysnäkymä | Eettinen toimikunta ja jälkiselvitysvelvoite jäävät käsityön varaan |
| Kalibraatiopatterin oma ajoympäristö | Paperin D proxy-validointi menettää ankkurinsa |
| Hallintanäkymä | Keruun aikainen valvonta jää lokitiedostojen lukemiseksi |
| Automaattitestit (determinismi, vuoto, pimennys) | Determinismilupausta ei voi todistaa menetelmäosassa |

**Suositus: älä leikkaa näistä.** Leikkaa sen sijaan skenaarioiden määrästä ja karttagrafiikan
viimeistelystä, ja hyväksy 8–10 kuukauden osa-aikainen kaari — tai osta 2–3 kuukautta
kokopäiväistä työaikaa vaiheisiin 1 ja 2, jolloin kalenteriaika painuu takaisin 5–6 kuukauteen.
Kumpi tahansa valitaan, **päätä se ennen pilottipäivän lyömistä lukkoon**, koska pilottipäivä on
sen jälkeen ainoa mittari, joka kertoo laajuuden karanneen.

Sisältötyö kulkee rinnalla ja on kriittisellä polulla vähintään yhtä paljon kuin koodi
(dokumentti 7.4).

---

## 8.1 Vaiheet

**Vaihe 0 — ennen koodia (2–3 viikkoa)**

| Toimitus | Miksi ennen koodia |
|---|---|
| **Tila-avaruusdokumentti** 4–6 tilaa × 4 saraketta | Kolmas sarake määrää lokitusskeeman, jota ei voi korjata jälkikäteen |
| **Echelonipäätös (A-1)** | Määrää maaston, solukoon, nopeudet, käskyt, koetinvaikeuden |
| **Piirteiden rekisteri**: haarautumat, katveet, reitit | Maasto suunnitellaan päätöskohdat edellä |
| **CMO-ajot ja parametritaulukko** | Moottorin lukuja ei keksitä |
| **hmetad-palautussimulaatio** | Ainoa otoskokoluku, jonka arvioija hyväksyy kyselemättä |
| **Pilottipäivämäärä** | Päätetään nyt. Jos lipsuu kahdesti, ongelma on laajuudessa eikä aikataulussa |

**Vaihe 1 — ajettava, deterministinen skenaario (n. 8 viikkoa)**

| Komponentti | Valmis kun |
|---|---|
| Skenaariomoottori ja kello | Täysi ajo kahdesti identtisesti; tapahtumavirran hash täsmää |
| Kaksikerroksinen maailma + havaintoportti | Totuuskerros saavuttamaton osallistujan buildissa (automaattitesti) |
| Maastoputki | Kartta ja näkyvyysmatriisi regeneroituvat bittitarkasti; manifestin hashit täsmäävät |
| **Projektiomoottori omana palveluna** | Sama kysymysteksti → sama vastaus kahdessa istunnossa, eri selaimissa |
| **Virheinjektio** | Kaksi tyyppiä, toisensa poissulkevia, konfiguraatiosta kytkettävissä, lokitettuina |
| Päätöskohdat + oletustoimintamoottori | Nollasyötteen ajo tuottaa ei-päätöksen ja tilamuutoksen jokaisessa kohdassa |
| Lokitus + offline-jono | Simuloitu verkkokatko ei hukkaa tapahtumia eikä tuota duplikaatteja |
| **Jälkiselvitysnäkymä** | Osallistujan altistus rekonstruoituu lokista ja näytetään hänelle |
| **Validaattori CI:ssä** | Säännöt R1–R17 ajossa, punainen pysäyttää buildin |
| `ThreatModel`-rajapinta | Ydin ei tunne sanaa "palo" eikä "vihollinen" |

**Vaihe 2 — mittarit ja manipulaatiot (n. 6 viikkoa)**

| Komponentti | Valmis kun |
|---|---|
| Koetinjärjestelmä | 15–25 koetinta, luottamus jokaisen perässä, ei mitään ennakoivaa merkkiä |
| Jäädytys + ruudun pimennys | Kanava todistettavasti saavuttamaton; toimii etälaitteella; fokuksen menetys lokittuu |
| ISA jokaisessa jäädytyksessä | Kuormakäyrä syntyy koko sessiosta |
| Avoin L3-koetin | Vastaus tallentuu, koodauskehikko olemassa, toinen koodaaja sovittu |
| Kanavaehto lukittuna | Ei teknistä reittiä vaihtaa kanavaa kesken session |
| Vertaispäätösten kolme ehtoa (Tutkimus II) | Ehto 1 ei tavoita vertaissisältöä millään reitillä |
| Havaitsemispatteri | Yksisuuntainen: vapaa attribuutio ennen kuin lähteitä mainitaan |
| Harva-koetin-ehto | Konfiguraatiosta, ei koodihaarasta |

**Vaihe 3 — tutkijan työkalut ja pilotti (n. 4 viikkoa)**

| Komponentti | Valmis kun |
|---|---|
| Hallintanäkymä | Istuntojen tarkastelu kesken keruun, suodatus, JSON-vienti, terveystila |
| Vienti + johdannaisskripti | Muuttujat toistuvat raakatapahtumista bittitasolla samoina |
| Kalibraatiopatteri erillisenä ajona | 200–400 koettelua, omalla ajallaan, oma linkki |
| **Käyttöliittymän jäädytys ja versiointi** | Kuvakaappaukset menetelmäosaan; mallin versiotunniste jokaisella lokirivillä |
| Pilotti | Vääristymän kolme tasoa 5–8 hengellä; koetinvaikeus; käskyn epämääräisyys |

## 8.2 Testistrategia

| Testi | Miten | Miksi |
|---|---|---|
| **Determinismi** | Aja ydin headlessina 100×, vertaa tapahtumavirran hashia | Ehtojen keskiarvot eivät muuten ole vertailukelpoisia |
| **Jäsennysvakaus** | Aja pilotin kysymyskorpus 3×; sama teksti → sama parametrisarja | K-2:n lupaus menetelmäosassa |
| **Kultainen ajo** | Tallennettu syötesarja + odotettu tapahtumavirta versionhallinnassa | Havaitsee, jos sisältömuutos muuttaa vahingossa toista kohtaa |
| **Nollasyöte** | Ajo ilman yhtään syötettä | Oletustoimintamoottori kattaa kaikki kohdat |
| **Vuoto** | Greppaa verkkoliikenne ja `window`-puu totuuskerroksen, virheinjektion ja vertaissisällön tunnisteiden varalta | Manipulaation eheys |
| **Pimennys etälaitteella** | Fullscreen + fokustestit kolmella selaimella | Etäkeruun kriittisin mekanismi |
| **Virhetyyppien erillisyys** | Ajo läpi, tarkista ettei yksikään koettelu kanna molempia lippuja | R7 |
| **Lokikattavuus** | Jokainen tila-avaruusdokumentin proxy on laskettavissa testiajon lokista | R15 |

## 8.3 Laajuuden vartijat

Nämä ovat päätöksiä, ei toiveita. Jokainen niistä on kohta, jossa projekti tyypillisesti karkaa.

* **Yksi domain ensin.** Toinen vasta kun ensimmäinen kerää dataa.
* **Ei kirjautumista, ei käyttäjähallintaa, ei responsiivisuutta.** URL-parametri riittää.
* **Ei kaunista ennen kuin pilotti osoittaa tarpeen.** Koskee erityisesti karttagrafiikkaa.
* **Backend erillisenä palveluna alusta asti.** Ei "irrotetaan myöhemmin".
* **Ehdot konfiguraationa.** Jos ehdon vaihto vaatii käännöksen, virhe on jo tehty.
* **Pilottipäivä lyödään lukkoon nyt.** Kahdesti lipsunut päivä on laajuusongelma.

## 8.4 Riskit

| Riski | Vastaus |
|---|---|
| **Jäsennysvaihtelu syö determinismin** | Kolmitasoinen jäsennin + välimuisti; sääntöreitin kattavuustavoite ≥ 80 % pilotissa; reitti lokitetaan |
| **Koetinvaikeus ei osu 65–85 %:iin** | Pilotti korvaa osumattomat koettimet. Ilman tätä herkkyyttä ei voi laskea lainkaan — tämä on portti, ei viritys |
| **Reaktiivisuus tuottaa tuloksen** | Harva-koetin-ryhmä (n≈20) + proxy-painotus. Raportoidaan joka tapauksessa rajoitteena |
| **Vääristymä liian pieni tai liian suuri** | Kolme tasoa pilotissa, 5–8 henkeä kutakin. Tämä on pilotin tärkein tehtävä |
| **Itsevalikoituva altistuminen** | Pakotettu haarautuma + radiovarmistus + reitti kovariaattina |
| **Etäkeruun kato** | Suunnittele 80:lle, rekrytoi 100–110; keskeytyneet istunnot analysoitavissa keskeytyskohtaan |
| **Toinen näyttö tai toinen laite** | Ei estettävissä. Mitataan ja raportoidaan |
| **Eettinen toimikunta ja MPKK** | Kehystys havaitsemisen ja suojautumisen näkökulmasta; esirekisteröinti; jälkiselvitys osana ohjelmistoa |
| **Asiantuntijoiden saatavuus** | Pisin läpimenoaika. Parametrit, maasto ja käskyn epämääräisyys tarvitsevat samoja ihmisiä — varaa ajat kerralla |
| **CMO:n maasotaosuus ei kelpaa** | Varmistettava Salmiselta ennen kuin parametrit lyödään lukkoon. Varasuunnitelma: pelkkä asiantuntijajohdanto ja se raportoidaan rajoitteena |

## 8.5 Päätökset, jotka estävät etenemisen

| # | Kysymys | Estää | Suositus |
|---|---|---|---|
| A-1 | Armeijadomainin echelon | Maasto, mittakaava, käskyt, koetinpankki | Sido rekrytoivan kohortin tasoon; valitse yksi |
| A-2 | Onko Tutkimus II pelastus vai armeija | Toisen sisältöpaketin aloituksen | **Pelastus** — se on kuvattu, ja kahden regiimin vertailu on paperin D siirrettävyysväitteen ainoa empiirinen tuki |
| A-3 | Menetetäänkö "pääsy päättelyyn" -konstrukti tarkoituksella | Ei estä rakentamista; arvioija kysyy | Ratkaise ennen esirekisteröintiä |
| A-4 | CATCHin omat ehdot Tutkimus II:ssa | Solurakenteen | Sovi eksplisiittisesti, että nämä pitävät AI-kanavan vakiona |
| A-5 | Avoimen L3-koettimen toinen koodaaja | Avoimen koettimen analyysin | Ratkaistava ennen keruuta |
| A-6 | CMO:n maasotaosuuden uskottavuus | Parametrien puolustettavuuden | Kysy Salmiselta nyt |
| A-7 | Virheinjektio Tutkimus II:ssa | Lokitusliput ja jälkiselvityksen | Ks. dokumentti 6.9 |

## 8.6 Ensimmäiset kaksi viikkoa

1. **Echelonipäätös (A-1)** ja **Tutkimus II:n domain (A-2)**. Kaikki muu riippuu näistä.
2. **Tila-avaruusdokumentti.** Kuusi tilaa, neljä saraketta. Kolmas sarake on lokitusskeeman
   spesifikaatio — kirjoita se niin tarkasti, että kehittäjä voi toteuttaa sen kysymättä.
3. **hmetad-palautussimulaatio.** Päivän työ, ja se numero menee esirekisteröintiin sellaisenaan.
4. **Yhteydenotot:** Salminen (CMO:n uskottavuus, KESI-kuvaus), Huttner (parametrivalidointi),
   toinen koodaaja avoimelle koettimelle.
5. **Piirteiden rekisteri**: haarautumat, katveet, reitit — ennen kuin maastoa generoidaan riviäkään.
6. **Pilottipäivä kalenteriin.**

Vasta sen jälkeen ensimmäinen rivi koodia — ja se rivi on projektiomoottorin tilamalli, ei
käyttöliittymä.
