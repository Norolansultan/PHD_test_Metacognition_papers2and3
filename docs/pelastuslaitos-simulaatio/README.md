# Pelastuslaitoksen simulaatio — arkkitehtuurikeskustelun dokumentit

Tämä hakemisto sisältää **Harjulan instrumentti** -toteutussuunnitelman, joka syntyi
21.8.2026 käydyssä arkkitehtuurikeskustelussa (Claude Code -sessio
*"Pelastuslaitos simulaation arkkitehtuuri"*). Dokumentti kuvaa, miten väitöskirjan
papereiden 2 ja 3 mittausinstrumentti rakennetaan: yksi jatkuva maastopalotapahtuma,
15 päätöspistettä, neljä koeasetelman solua ja arkkitehtuuri, jonka jokainen kerros
on johdettu mittausvaatimuksista.

## Tiedostot

| Tiedosto | Sisältö |
|---|---|
| [`harjulan-instrumentti.md`](harjulan-instrumentti.md) | Koko suunnitelma Markdownina — luettavissa suoraan GitHubissa |
| [`harjulan-instrumentti.html`](harjulan-instrumentti.html) | Sama dokumentti alkuperäisenä, taitettuna sivuna: sisältää aikajanakaavion (SVG) ja arkkitehtuurikerrosten visualisoinnin |

Markdown-versio on koneellisesti muunnettu HTML-lähteestä; sisältö on identtinen,
mutta aikajanan SVG-kaavio näkyy vain HTML-versiossa (Markdownissa sen tiedot ovat
taulukossa *Viisitoista päätöspistettä*).

## Rakenne

1. **Periaatteet** — kuusi valintaa, joista kaikki muu seuraa
2. **Toiminta** — roolit, käskyvalta, tiedon kanavat, toimintotaksonomia, LCES-portti
3. **Aikajana** — 88 minuuttia, 15 päätöspistettä, kolme SAGAT-jäädytystä, tuulen käännös S08
4. **Arkkitehtuuri** — build-aika, sim core, havaintoportti, käyttöliittymä, telemetria
5. **Sisältöputki ja validaattori** — Excel → YAML → validaattori → content-pack; kuusi löydettyä ristiriitaa (V-1…V-6)
6. **Kartta** — prototyypistä (`harjulakartta.html`) instrumentin renderöijäksi
7. **Mittaus ja lokitus** — otsikkomittarit ja niiden johtaminen tapahtumista
8. **Vaiheet, riskit ja päätökset** — 20 viikkoa kolmessa vaiheessa, päätökset T-1…T-6

## Lähteet ja tila

- Lähdeaineisto: `PhD_Simulation_Scenarios_P2P3_1.xlsx` (30 välilehteä, 21.8.2026) ja
  `harjulakartta.html` (siemen 20260821) — kumpikaan ei ole tässä repositoriossa.
- Alkuperäinen julkaistu versio: <https://claude.ai/code/artifact/e21290a4-16ca-4ea0-863d-02c6dfcb9a26>
- Keskustelussa viitataan laajempaan `pelastussimulaatio/`-hakemistoon. Ne tiedostot
  jäivät alkuperäisen session konttiin, eikä niitä saatu pushattua (403 write access);
  tähän hakemistoon on talletettu se osa työstä, joka oli palautettavissa.
- Kaikki paikannimet ja organisaatiot ovat kuvitteellisia.
