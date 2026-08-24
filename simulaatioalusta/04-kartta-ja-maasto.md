# 4. Kartta ja maasto

Kaksi päätöstä on tehty ja ne pitävät: **fiktiivinen maasto** ja **karttalogiikka KESI:n hahmoa
mukaillen**. Molemmat ovat oikeita, ja molemmilla on seurauksia, jotka eivät ole ilmeisiä.

---

## 4.1 Fiktiivinen maasto — kolme etua yhdellä päätöksellä

1. **OPSEC-ongelma katoaa kokonaan.** Ei harkintaa siitä, mitä todellisesta maastosta saa näyttää.
2. **Maasto voidaan suunnitella koeasetelman ehdoilla.** Tämä on tärkein etu, ja se on aliarvostettu:
   haarautumiskohdat, näkyvyyskatveet ja kaksi yhtä uskottavaa reittiä eivät ole löydettävissä
   todellisesta maastosta, ne on rakennettava.
3. **Skenaariot ovat julkaistavissa liitteinä.** Se on toistettavuutta, ja se on myös
   menetelmäartikkelin edellytys.

Todellinen maasto ei tuo mitään, mitä tarvitaan.

## 4.2 Maasto on koeasetelman osa, ei kulissi

Tämä on suurin muutos aiempaan suunnitelmaan. Aiemmin maaston vaatimus oli **näyttää oikealta**.
Nyt sen ensimmäinen vaatimus on **tuottaa mitattavia tilanteita**, ja realismi tulee toisena.

| Vaadittu maastopiirre | Mitä se palvelee | Ilman sitä |
|---|---|---|
| **Pakotettu haarautuma** — kaksi yhtä uskottavaa suuntaa ja riittämätön tieto valita | Vedetyn ohjauksen altistumisen takaaminen (K-6) | Itsevalikoituva altistuminen, satunnaistus rikkoutuu |
| **Näkyvyyskatveet** | Tiedon epätäydellisyys on maaston ominaisuus eikä käyttöliittymän kikka | Osallistuja näkee kaiken, projektiolle ei ole tarvetta |
| **Kaksi reittiä, eri riskiprofiili** | Vääristetty ohjaus voi kallistaa valintaa mitattavasti | Ajautumalla ei ole suuntaa jota mitata |
| **Etäisyydet, jotka tekevät ajasta kustannuksen** | Siirtymäaika on todellinen päätösmuuttuja | Sijoittelupäätökset ovat ilmaisia eivätkä mittaa mitään |
| **Ennustettava mutta ei ilmeinen kehitys** | Koettimien vaikeustaso 65–85 % | Kaikki oikein tai kaikki väärin — herkkyyttä ei voi laskea |

**Rakennusjärjestys seuraa tästä:** maasto suunnitellaan skenaarion päätöskohdat edellä, ei toisin
päin. Piirteiden rekisteri kirjoitetaan ensin, maasto sovitetaan siihen.

## 4.3 Ruudukko, näkyvyys ja mittakaava

2D ylhäältä, **ruutu- tai heksapohja**. Ei 3D, ei fotorealismia.

| Valinta | Suositus | Perustelu |
|---|---|---|
| Ruutu vai heksa | **Heksa** | Kuusi naapuria antaa tasavälisen liikkeen ja rehellisemmän etäisyyslaskennan kuin ruudukon diagonaalit. Näkyvyyslaskenta on yksinkertaisempi. Kustannus renderöinnissä on pieni |
| Solun koko | 250 m armeija, 100 m pelastus | Sidottava echelonipäätökseen A-1 |
| Näkyvyys | Esilaskettu näkyvyysmatriisi | Ajoaikainen LOS jokaiselle yksikölle joka tikillä on turha kuorma, kun maasto on staattinen |
| Vanheneminen | Solukohtainen `lastObserved` | Tiedustelutiedon vanheneminen on visuaalinen ja luettava, ei piilotettu |

Näkyvyysmatriisi lasketaan leipomisvaiheessa: jokaiselle solulle joukko soluja, jotka siitä näkyvät.
Muistivaatimus on hallittavissa harvana esityksenä, ja se poistaa ajoaikaisen laskennan kokonaan.

## 4.4 Karttalogiikka KESI:n hahmoa mukaillen

KESI on MPKK:n komentaja- ja esikuntasimulaattori: konstruktiivinen, karttapohjainen, käskyt annetaan
simulaatiomaailman ulkopuolelta, ei suoraa havaintoa. **Se on täsmälleen tämän tutkimuksen
välitysasetelma** — komentaja ei näe, hän saa välitetyn kuvan.

Menetelmäosaan: *"ympäristö noudattaa konstruktiivisen komentajasimulaattorin peruslogiikkaa"*.
Vahva ekologisen validiteetin perustelu, eikä vaadi pääsyä järjestelmään — vain kuvauksen.
**Kysy Salmiselta**, että kuvaus on oikea ennen kuin se menee menetelmäosaan.

Rakennusseuraus: **suoraa havaintoa ei ole missään.** Kaikki mitä osallistuja tietää, tulee
raporttina, käskynä tai projektiona. Kartta ei ole ikkuna maailmaan vaan esitys siitä, mitä on
raportoitu. Tämä on sama vaatimus kuin havaintoportti (dokumentti 1.7), ja KESI-vertaus on sen
perustelu ulospäin.

## 4.5 Leipominen — miksi ajoaikainen generointi on nyt lopullisesti pois

Aiemmassa suunnitelmassa maasto generoitiin selaimessa siemenestä. Mittasin sen: 470 × 470 -ruudukon
luokitus vei 1,54 s pelkkänä kenttälaskentana, päälle korkeuskäyrät ja nimistö. Valvotussa
istunnossa se olisi ollut siedettävää. **Etäkeruussa se ei ole**, kolmesta syystä:

1. `Math.exp`, `Math.hypot` ja `Math.sin` ovat ECMAScriptissä toteutuskohtaisia viimeisten bittien
   osalta. Kun selainkirjo on hallitsematon, sama siemen ei takaa identtistä karttaa.
2. Osallistujan laitteen suorituskyky on tuntematon; sekunnin generointi voi olla kymmenen.
3. Kartan on oltava identtinen myös kahden vuoden päästä, kun selainversiot ovat toisia.

```
tools/terrain-bake.ts
  syöte : siemen + maastoparametrit + piirteiden rekisteri (haarautumat, katveet, reitit)
  tuotos: base_map.png · terrain.bin (heksaluokitus) · visibility.bin · features.json
          + manifest.json (siemen, parametrit, jokaisen tiedoston SHA-256)
```

Ajoaikana ladataan valmis kuva ja valmiit ruudukot. Generointia ei tapahdu.

## 4.6 Aiemman karttaprototyypin kohtalo

`harjulakartta.html` (siemen 20260821) rakennettiin pelastusdomainin peruskarttamaastoksi. Se ei
mene hukkaan, mutta sen rooli muuttuu.

| Osa | Kohtalo |
|---|---|
| `mulberry32`, `PERM`, `vnoise`, `fbm` | **Säilyy** — deterministinen kohinakirjasto molemmille domaineille |
| `elev`, `ESKERS`, `LAKES`, `BOGS`, `classify` | **Säilyy** pelastuspaketin maastolähteenä (Tutkimus II) |
| `drawContour`, peruskarttatyyli, nimistön typografia | **Siirtyy leipomisskriptiin, mutta kevennettynä.** "Ei kaunista ennen kuin pilotti osoittaa tarpeen" koskee tätä suoraan — peruskarttatason viimeistely on gold-platingia ennen pilottia |
| Kilometriruudukon nimiöt (`6820+x` itäkoordinaattina) | **Korjattava.** ETRS-TM35FIN:ssä itäkoordinaatti on kilometreinä kolminumeroinen; nelinumeroinen ei ole mahdollinen. Fiktiivisellä maastolla helpoin ratkaisu on paikallinen ruudukko ilman TM35FIN-viittausta |
| `SECT`, `OPS` (linja, varalinja, naapurit) | **Sisältöpakettiin**, ei koodiin |
| `render`, `VIEWS`, UI-napit | Korvautuu renderöijällä |

**Mitä prototyypistä puuttuu ja on lisättävä:** heksaruudukko, näkyvyysmatriisi, pakotettu
haarautuma, ja armeijadomainin oma maasto. Prototyyppi ratkaisi sen, miltä maasto näyttää; se ei
ratkaissut sitä, mitä maastolla mitataan.

## 4.7 Validointi

Kaksi porttia, tässä järjestyksessä. Järjestys on uusi ja se on tärkeä.

**1. Koeasetelman portti (ensin).** Konetarkistukset jokaisella leipomisella:

```
✓ pakotettu haarautuma on olemassa: kaksi reittiä, joiden ennakoitu kustannusero
  on saatavilla olevalla tiedolla alle kynnyksen
✓ vähintään N näkyvyyskatvetta, joissa uhka voi kehittyä havaitsematta
✓ siirtymäajat päätöskohtien välillä 5–20 min — kustannus, joka on maksettava mutta maksettavissa
✓ jokainen piirteiden rekisterin geometria osuu sille sopivalle maastoluokalle
✓ näkyvyysmatriisi on symmetrinen ja katteeltaan odotetulla välillä
```

**2. Realismiportti (toisena).** Asiantuntijakatselmus: *"voisiko tämä olla uskottava maasto, ja
voisiko tilanne kehittyä näin?"* Sama portti kuin projektiomoottorin parametreilla, samat
asiantuntijat. Iteroi kunnes vastaus on kyllä.

Jos portit ovat ristiriidassa, **koeasetelman portti voittaa** ja poikkeama realismista raportoidaan
menetelmäosassa. Maasto, joka on uskottava mutta ei tuota mitattavia tilanteita, on kaunis kulissi
tyhjän tutkimuksen ympärillä.
