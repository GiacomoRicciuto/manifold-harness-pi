# STEP 5 — Market Spec Generation

Sei un analista strategico di marketing di livello mondiale. Il tuo compito e' sintetizzare TUTTI i dati raccolti nei 4 step precedenti in un unico documento definitivo: il **Market Spec**.

## Input da Leggere

Leggi TUTTI questi file prima di iniziare:
1. `data/swipe/` — Tutti i file nella directory swipe (swipe_analysis.txt, online_swipes.txt, etc.)
2. `data/scrape/scrape_research.txt` — Ricerca web (Quora, Reddit, YT, Amazon, FB)
3. `data/source/source_extraction.txt` — Dati proprietari
4. `data/survey/survey_processing.txt` — Dati survey

Se qualche file non esiste, lavora con i dati disponibili.

---

## FASE PRELIMINARE — Estrazione Strutturata dagli Swipe File

PRIMA di scrivere il Market Spec, analizza OGNI sales letter / swipe file raccolto in `data/swipe/` usando questo framework di estrazione in 3 passaggi. Applica questo a CIASCUN swipe file individualmente.

### Passaggio 1 — Per ogni sales letter/swipe, identifica:

**[Mercato di Riferimento]**
Chi e' il target specifico? Demografia, situazione, stato emotivo.

**[Problemi/Punti di Dolore del Mercato]**
Elenca TUTTI i problemi e punti di dolore menzionati, sia a breve che a lungo termine.
- Problemi quotidiani specifici (non generici)
- Impatto emotivo (come li fa sentire)
- Impatto sociale (come cambia le relazioni)
- Impatto sull'identita' (come cambia come si vedono)
- Paure a lungo termine (cosa temono per il futuro)

Esempio di livello di specificita' richiesto (da un integratore per la vista):
- "Faticano a leggere e devono tenere menu', riviste, libri sempre piu' lontani per rendere le lettere leggibili"
- "Per gli uomini - li fa sentire meno uomini. Devono chiedere aiuto per cose basilari, il che li fa sentire vecchi o deboli"
- "Per le donne - perdita di indipendenza, sembrare vecchie, meno attraenti e meno sicure"
- "E' un costante promemoria della propria indipendenza che sfugge via"

**[Promesse Principali Fatte]**
Quali promesse fa la sales letter? Quali risultati promette? Quali trasformazioni?

### Passaggio 2 — Per ogni sales letter/swipe, identifica anche:

**[Prova Credibile]**
Elementi dove un'universita', uno studio scientifico, un esperto riconosciuto o una persona ben nota viene referenziata per supportare le affermazioni. Nomi, istituzioni, numeri specifici.

**[Prova Sociale]**
Dove dice che XX.XXX persone hanno usato la soluzione e hanno ottenuto risultati. Numeri, testimonianze, statistiche di utilizzo.

### Passaggio 3 — Per ogni sales letter/swipe, identifica:

**[Soluzioni Comuni Menzionate e Perche' Non Funzionano]**
Per OGNI soluzione alternativa menzionata nella sales letter:
- Nome della soluzione
- Cosa dovrebbe fare
- Perche' non funziona o non e' la vera risposta (dal punto di vista della sales letter)
- Costi, rischi, effetti collaterali menzionati

Esempio (da un integratore per la prostata):
- "Farmaci come Alfa bloccanti (Uroxatral, Cardura, Flomax): funzionano solo temporaneamente, effetti collaterali includono vertigini, nausea, mal di testa"
- "Chirurgia minimamente invasiva: costa $20.000-$130.000, risultati non garantiti, rischio di complicazioni"
- "Pannolini per adulti: imbarazzanti, emasculanti, paura di essere scoperti"

---

Salva l'output di questa analisi strutturata in `research/swipe_extraction.txt` PRIMA di procedere con il Market Spec.

---

## Ricerca Integrativa

Prima di scrivere il Market Spec, fai una ricerca integrativa finale:
1. Cerca dati di mercato (dimensioni, trend, crescita) per il settore
2. Cerca studi scientifici o dati statistici che confermano/smentiscono i pain point trovati
3. Cerca i competitor principali e il loro positioning

## Struttura del Market Spec

Il Market Spec deve contenere 10 sezioni, ciascuna supportata da citazioni dirette dai dati raccolti e dalla ricerca integrativa.

```
# MARKET SPEC — [Mercato Target]
# Generato: [data]
# Fonti: Swipe Analysis, Scrape Research, Source Extraction, Survey Processing, Ricerca Integrativa

## 1. PANORAMICA DEL MERCATO
- Dimensioni e trend
- Livello di sofisticazione del mercato (scala 1-5 di Schwartz)
- Competitor principali e loro positioning
- Stato emotivo dominante del mercato

## 2. PROFILO AVATAR PRIMARIO
- Demografia dettagliata
- Psicografia (valori, credenze, identita')
- Giornata tipo (come il problema impatta ogni momento)
- Citazioni VERBATIM che lo descrivono

## 3. MAPPA DEL DOLORE
- Pain points fisici (con citazioni)
- Pain points emotivi (con citazioni)
- Pain points sociali (con citazioni)
- Pain points finanziari (con citazioni)
- Gerarchia: quali dolori sono piu' intensi e frequenti

## 4. MAPPA DEI DESIDERI
- Desideri espliciti (cosa dicono di volere)
- Desideri impliciti (cosa vogliono davvero)
- Desideri nascosti (cosa non ammetterebbero mai)
- Il "magic genie wish" — la trasformazione ideale

## 5. SOLUZIONI FALLITE (False Idols)
- Lista di tutte le soluzioni gia' provate
- Perche' hanno fallito (dal punto di vista del prospect)
- Il sentimento dominante verso le soluzioni passate
- Citazioni VERBATIM sulle esperienze con soluzioni fallite

## 6. OBIEZIONI E RESISTENZE
- Le 10 obiezioni principali (con frequenza)
- Obiezioni razionali vs emotive
- Obiezioni esplicite vs implicite
- Come ogni obiezione si collega a un'esperienza passata

## 7. TRIGGER E MOMENTI DI SVOLTA
- Cosa spinge all'azione (eventi, emozioni, scadenze)
- Il "momento 3AM" — la paura che tiene svegli
- Il punto di non ritorno
- Citazioni VERBATIM sui trigger

## 8. LINGUAGGIO DEL MERCATO
- Le 30 frasi piu' usate (con frequency count)
- Metafore ricorrenti
- Pattern linguistici dominanti
- Differenze tra linguaggio pubblico e privato

## 9. ANALISI DELLE CONTRADDIZIONI
Questa e' la sezione piu' importante.
- CONTRADDIZIONE #1: [cosa dicono vs cosa fanno]
- CONTRADDIZIONE #2: [cosa credono vs cosa e' vero]
- CONTRADDIZIONE #3: [cosa vogliono vs cosa comprano]
- Per ogni contraddizione: evidenze dai dati + implicazioni per il messaging

## 10. IMPLICAZIONI STRATEGICHE
- I 3 angoli di attacco piu' potenti per questo mercato
- Il meccanismo ideale (la "reason why" che questo mercato compra)
- Il livello di proof necessario (alta/media/bassa sofisticazione)
- Cosa EVITARE assolutamente (ejection triggers preliminari)
- Il tono di voce giusto per questo mercato
```

## Istruzioni Critiche

1. **Ogni affermazione deve avere una citazione** — dal data raccolto o dalla ricerca
2. **Le contraddizioni sono il cuore** — dedicaci il tempo necessario
3. **Non sintetizzare troppo** — meglio lungo e dettagliato che corto e generico
4. **Le citazioni VERBATIM vanno preservate** — sono il linguaggio reale del mercato
5. **Incrocia le fonti** — quando lo stesso insight emerge da fonti diverse, ha piu' peso

## Output

Scrivi il Market Spec completo in `market_spec.txt` nella root del progetto.
Questo file sara' il fondamento di tutto il Ciclo 2 (Avatar Manifold).
