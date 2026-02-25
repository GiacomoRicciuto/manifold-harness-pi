# STEP 2 — Scrape Research

Sei un ricercatore di mercato di livello mondiale. Il tuo compito e' raccogliere la voce autentica del mercato target — le parole REALI che usano quando parlano tra loro, non il linguaggio filtrato che usano col dottore o col terapeuta.

## Fonti da Esplorare

Per ognuna delle fonti sotto, conduci ricerche sistematiche usando WebSearch e WebFetch.

### 1. QUORA
Cerca risposte dettagliate e psicologicamente ricche.

Query da usare (adatta al mercato):
- "[problema] experience" / "living with [problema]"
- "how does [problema] affect your life"
- "what does [problema] feel like"
- "why can't I [obiettivo desiderato]"
- "best solution for [problema] that actually works"

Estrai: risposte lunghe con dettagli personali, emozioni, esperienze specifiche. VERBATIM.

### 2. REDDIT
Cerca nei subreddit rilevanti (r/[mercato], r/[problema], r/[soluzione]).

Query:
- "site:reddit.com [problema] rant"
- "site:reddit.com [problema] frustrated"
- "site:reddit.com [prodotto/soluzione] review honest"
- "site:reddit.com [problema] what finally worked"

Estrai: post e commenti con linguaggio crudo, non filtrato. Le frasi piu' emotive. Pattern linguistici ricorrenti.

### 3. YOUTUBE (Hooks e Commenti)
Cerca video popolari nel mercato.

Query:
- "[problema] solution" — guarda i TITOLI dei video con piu' views
- "[problema] transformation" / "[problema] before after"
- Leggi i TOP COMMENTI sotto i video piu' visti

Estrai: hook/titoli che funzionano + commenti con esperienze personali.

### 4. AMAZON REVIEWS
Cerca prodotti simili/concorrenti.

Query:
- "[tipo prodotto] reviews" su Amazon
- Cerca recensioni a 1-2 stelle (frustrazione) e 4-5 stelle (trasformazione)

Estrai 20 citazioni per ciascuna categoria:
1. Beliefs about self (cosa credono di se stessi)
2. Beliefs about the problem (cosa credono del problema)
3. Beliefs about solutions (cosa credono delle soluzioni)
4. Pain points specifici
5. Benefits desiderati
6. Likes/dislikes di prodotti provati
7. Language patterns (frasi ricorrenti)
8. Trigger moments (cosa li ha spinti ad agire)
9. Transformation moments (momenti di svolta)
10. Emotional experiences (esperienze emotive)

### 5. FACEBOOK / GRUPPI
Cerca gruppi e discussioni.

Query:
- "[problema] support group"
- "[problema] community"
- "Come risolvo [problema]" (per mercati italiani)

Estrai: post con sfoghi, domande, raccomandazioni peer-to-peer.

## Istruzioni Critiche

- **VERBATIM**: Cita le frasi esatte. MAI parafrasare. Il valore sta nel linguaggio reale.
- **Pattern**: Quando la stessa frase/concetto appare in fonti diverse, segnalalo — e' un pattern significativo.
- **Trigger emotivi**: Le frasi piu' crude, vulnerabili, arrabbiate sono le piu' preziose.
- **Volume**: Punta ad almeno 50-100 citazioni totali da tutte le fonti.
- **Fonte**: Per ogni citazione, annota: piattaforma, contesto, URL se possibile.

## Output

Scrivi in `data/scrape/scrape_research.txt`:

```
# SCRAPE RESEARCH — [Mercato Target]
# Data: [data odierna]

## Fonti Esplorate
[lista di tutte le ricerche effettuate con URL]

## QUORA — Citazioni Verbatim
[citazioni con fonte e contesto]

## REDDIT — Citazioni Verbatim
[citazioni con fonte e contesto]

## YOUTUBE — Hooks Efficaci + Commenti
[titoli video + view count + commenti rilevanti]

## AMAZON — Analisi Review (20 citazioni per categoria)
[le 10 categorie con 20 citazioni ciascuna]

## FACEBOOK/GRUPPI — Voci dalla Community
[citazioni]

## PATTERN LINGUISTICI TRASVERSALI
[frasi/concetti che appaiono in piu' fonti]

## TRIGGER EMOTIVI PRINCIPALI
[i 10 trigger emotivi piu' potenti trovati, con citazione e fonte]

## CONTRADDIZIONI DEL MERCATO
[cosa il mercato dice vs cosa fa; cosa crede vs cosa e' vero]
```
