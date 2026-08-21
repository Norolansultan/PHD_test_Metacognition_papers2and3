# Pelastuslaitoksen simulaatio — rakennussuunnitelma

**Tutkimusinstrumentti Papereille 2 ja 3** · versio 1.0 · 21.8.2026
Lähteet: `PhD_Simulation_Scenarios_P2P3_1.xlsx` (30 välilehteä) ja `harjulakartta.html` (siemen 20260821).

---

## Mikä tämä paketti on

Tämä on **toteutussuunnitelma**, ei tutkimussuunnitelma. Työkirja kertoo *mitä* mitataan ja *miksi*;
tämä paketti kertoo *mitä koodataan*, *missä järjestyksessä* ja *mikä katsotaan valmiiksi*.
Kirjoitettu siitä näkökulmasta, että instrumentin rakentaa yksi kokenut kehittäjä + osa-aikainen
sisällöntuottaja noin 5–6 kuukaudessa, ja että se on ajettava Pelastusopiston koneilla selaimessa
ilman asennuksia.

Simulaatiossa on kaksi domainia (pelastuslaitos, armeija). **Tämä paketti kattaa
pelastuslaitoksen kokonaisuudessaan** ja määrittelee samalla rajapinnan, jonka takana armeijadomain
on pelkkä sisältöpaketti eikä uusi ohjelmisto.

## Lukujärjestys

| # | Dokumentti | Kenelle |
|---|---|---|
| 1 | [01-toiminnan-kuvaus.md](01-toiminnan-kuvaus.md) | Ohjaajat, käytännön asiantuntijat. Koko pelastustoiminnan kuvaus: roolit, resurssit, radioliikenne, päätösvalikoimat, minuutti minuutilta S01–S15. |
| 2 | [02-arkkitehtuuri.md](02-arkkitehtuuri.md) | Kehittäjä. Moduulit, deterministinen kello, kaksikerroksinen maailmamalli, kyselymoottori, ohjauskerros. |
| 3 | [03-sisaltomalli.md](03-sisaltomalli.md) | Kehittäjä + sisällöntuottaja. Skeemat, sisältöputki Excelistä buildiin, **sisältövalidaattori ja sen jo löytämät 6 ristiriitaa**. |
| 4 | [04-kartta-ja-maasto.md](04-kartta-ja-maasto.md) | Kehittäjä. `harjulakartta.html`:n arviointi ja refaktorointi instrumentin renderöijäksi; maastoputki ja palorintaman leipominen. |
| 5 | [05-mittaus-ja-lokitus.md](05-mittaus-ja-lokitus.md) | Kehittäjä + tilastotieteilijä. Tapahtumaloki, johdetut muuttujat, replay ja sokkokoodaus, vienti. |
| 6 | [06-toteutus-ja-riskit.md](06-toteutus-ja-riskit.md) | Sinä ja ohjaajat. Vaiheistus, valmiin määritelmä, testistrategia, työmäärä, riskit, avoimet päätökset. |

## Kymmenen riviä, jos luet vain tämän

1. **Rakenna erillinen selainpohjainen instrumentti, älä XVR-laajennusta.** Sitovan ohjauksen
   optioesto, päätöspalkin countdown, näytön pimennys SAGAT-jäädytyksessä, determinismi sanatarkkuuteen
   ja tapahtumataso­lokitus eivät ole XVR:n kautta toteutettavissa. Avoin päätös #1 dokumentissa 6.
2. **Moottori on domain-neutraali; pelastus on sisältöpaketti.** Mikään `if (domain === 'rescue')`
   ei mene ytimeen. Tämä on ainoa asia, joka pitää armeijadomainin kustannuksen sisällöntuotannossa
   eikä uudessa projektissa.
3. **Yksi kello.** `Master Timeline` on totuus. Kello on simuloitu, tikittää kiinteällä askeleella,
   pysähtyy jäädytyksissä, eikä koskaan riipu osallistujan toiminnasta.
4. **Kaksi kerrosta: GROUND TRUTH ja PERCEIVED.** Osallistujan buildissa totuuskerros ei ole
   saavutettavissa millään reitillä — ei URL:llä, ei DevToolsilla, ei verkkovastauksesta.
5. **Aikaindeksoitu korpus.** Jokaisella tiedolla on `valid_from`, mahdollinen `superseded_by` ja
   joukko kyselypolkuja. Kysely suodattuu simuloidun sekunnin mukaan. Tämä on Paperin 2 mekanismi,
   ei optimointi.
6. **Maasto leivotaan offline.** `harjulakartta.html` on erinomainen ulkoasuprototyyppi mutta väärä
   ajoaikainen ratkaisu: generointi siirtyy Node-buildiin, joka tuottaa hashatut rasteri- ja
   vektoriassetit. Ajossa ei generoida mitään.
7. **Palon leviäminen on käsikirjoitettu, ei simuloitu.** Rintama on aikaleimattu polygonisarja,
   joka on tuotettu offline maastotietoisella mallilla ja käytännön asiantuntijoiden hyväksymä.
   Ajossa vain interpoloidaan.
8. **Ilman lokia mittausta ei ole.** Muuttuja lisätään `Logging Spec` -listaan ennen kuin ominaisuus
   rakennetaan. Loki on append-only tapahtumavirta, josta kaikki johdetut muuttujat lasketaan skriptillä.
9. **Sisältövalidaattori on pakollinen komponentti, ei työkalu.** Se estää juuri sen vian, joka tappoi
   edellisen työkirjan: välilehtien eriytymisen. Se löytää tänään kuusi ristiriitaa — ks. dokumentti 3.
10. **Vaihe 1 ei sisällä yhtään manipulaatiota.** Ensin kello, maailma, päätöspalkki, oletustoiminta
    ja loki. Manipulaatiot (wiki-kentät, sitova ohjaus, mittarit) vasta vaiheessa 2. Jos vaihe 1 ei ole
    determinististä, mikään vaiheen 2 asia ei ole mitattavaa.
