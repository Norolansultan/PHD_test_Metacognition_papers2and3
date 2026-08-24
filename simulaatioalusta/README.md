# Simulaatioalusta — rakennussuunnitelma

**Väitöskirjan koeympäristö, paperit 1, B, A ja D** · versio 2.0 · elokuu 2026

Perustuu elokuun 2026 väitöskirjasuunnitelmaan, joka korvasi aiemman neljän erillisen paperin
rakenteen. Aiempi, työkirjaan (Paperit 2 ja 3 ristiin, XVR, pelastus) perustunut rakennussuunnitelma
on korvattu kokonaan; mikä siitä säilyi ja miksi, on dokumentissa 0.

---

## Mikä tämä on

Toteutussuunnitelma, ei tutkimussuunnitelma. Väitöskirjasuunnitelma kertoo *mitä* mitataan ja
*miksi*; tämä paketti kertoo *mitä koodataan*, *missä järjestyksessä* ja *mikä katsotaan valmiiksi*.

Lähtöoletus: kaikki koeympäristö, kartat ja toiminnallisuus rakennetaan itse. Selainpohjainen,
jotta etäosallistuminen omalla laitteella onnistuu — se on koko sadan osallistujan otoksen ehto.

Työmäärä: väitöskirjasuunnitelman arvio on 4–6 kk osa-aikaisena; alhaalta ylöspäin laskettuna
vaiheet 0–3 ovat ~20 henkilötyöviikkoa eli ~5 kk kokopäiväisenä. Ero ja sen ratkaisu ovat
dokumentissa 8.0 — se on päätettävä ennen pilottipäivän lyömistä lukkoon.

## Lukujärjestys

| # | Dokumentti | Sisältö |
|---|---|---|
| **0** | [00-muutosanalyysi.md](00-muutosanalyysi.md) | **Lue ensin.** Mitä uusi väitöskirjasuunnitelma muuttaa, mikä poistuu, kuusi ratkaistua ristiriitaa (K-1…K-6) ja avoimet kysymykset (A-1…A-6) |
| 1 | [01-alustan-arkkitehtuuri.md](01-alustan-arkkitehtuuri.md) | Moduulit, kello, kaksikerroksinen maailma, etäkeruun seuraukset, domain-neutraalius |
| 2 | [02-projektiomoottori.md](02-projektiomoottori.md) | Tilamalli, kolmitasoinen jäsennin, virheinjektio, ajautumamittari, parametrien lähde |
| 3 | [03-mittausapparaatti.md](03-mittausapparaatti.md) | meta-d′ / Brier / M-ratio, koetinarkkitehtuuri, avoin L3, ISA, havaitsemismittarit, metakognitiiviset tilat, lokitusskeema |
| 4 | [04-kartta-ja-maasto.md](04-kartta-ja-maasto.md) | Fiktiivinen maasto koeasetelman ehdoilla, heksaruudukko, näkyvyys, KESI-logiikka, leipominen |
| 5 | [05-tutkimus-I-armeija.md](05-tutkimus-I-armeija.md) | Paperit 1 ja B: kaksi vaihetta, epämääräinen käsky, pakotettu kysymyshetki |
| 6 | [06-tutkimus-II-pelastus.md](06-tutkimus-II-pelastus.md) | Paperi A: kolme ehtoa, Harjulan tapahtuma, ennakkotapauksen pätevyys |
| 7 | [07-sisaltomalli-ja-validaattori.md](07-sisaltomalli-ja-validaattori.md) | Skeemat, sisältöputki, validaattorin 17 sääntöä, sisältötyön määrä |
| 8 | [08-toteutus-ja-riskit.md](08-toteutus-ja-riskit.md) | Vaiheet 0–3, testistrategia, laajuuden vartijat, riskit, estävät päätökset |

## Kymmenen linjausta

1. **Kehystyssääntö on myös rakennussääntö.** Kysymys on siitä, milloin ihminen havaitsee tulleensa
   ohjatuksi. Siksi havaitsemismittarit rakennetaan ennen manipulaatiota, altistus on
   rekonstruoitavissa lokista, ja jälkiselvitysnäkymä on vaiheen 1 toimitus.
2. **Tutkimus I (armeija) rakennetaan ensin.** Tutkimus II (pelastus) on sisältöpaketti, joka ei
   vaadi moottorimuutoksia.
3. **Projektiomoottori on erillinen palvelu alusta asti.** Käyttöliittymä on kertakäyttötavaraa;
   moottori on oma menetelmäartikkelinsa.
4. **Moottori tekee tasan kolme asiaa**: jäsentää, ajaa mallin, esittää tuloksen. Ei generatiivista
   päättelyä, ei omaa perustelua.
5. **Determinismi luvataan täsmällisesti.** Sama kysymysteksti → samat parametrit → sama vastaus.
   Eri muotoilut voivat jäsentyä eri tavoin, ja se mitataan eikä piiloteta.
6. **Virheinjektio on ensimmäisen luokan ominaisuus**, kaksi tyyppiä erikseen, ei koskaan samassa
   koettelussa, molemmat lokitettuina.
7. **Maasto on koeasetelman osa, ei kulissi.** Pakotettu haarautuma, näkyvyyskatveet ja kaksi
   uskottavaa reittiä ovat vaatimuksia; realismi tulee toisena.
8. **Alle 300 ms kuittaus, ei keinotekoista viivettä.** Aikapaineen alla tyhjä odotus on sekä
   ärsyke että sekoittava tekijä.
9. **Ilman lokia mittausta ei ole.** Tila-avaruusdokumentin kolmas sarake määrää lokitusskeeman, ja
   sitä ei voi korjata jälkikäteen.
10. **Vaihe 0 on ennen koodia.** Tila-avaruus, echelonipäätös, piirteiden rekisteri, CMO-parametrit,
    palautussimulaatio, pilottipäivä. Ensimmäinen koodirivi on tilamalli, ei käyttöliittymä.

## Tila

Suunnitelma on kirjoitettu elokuun 2026 väitöskirjasuunnitelman mukaiseksi. **Seitsemän päätöstä on
auki** (A-1…A-7), ja kaksi niistä — armeijadomainin echelon ja Tutkimus II:n domain — estävät
sisällön aloittamisen. Ne ovat dokumenteissa 0.5 ja 8.5.
