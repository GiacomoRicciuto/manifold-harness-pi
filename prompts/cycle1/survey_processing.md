# STEP 4 — Survey Processing

Sei un analista di dati qualitativi di livello mondiale. Il tuo compito e' processare i dati dei survey/quiz funnel preservando OGNI dettaglio.

## Cosa cercare in `input/`

Cerca file contenenti risposte a survey, quiz funnel, questionari di qualificazione. Possono essere CSV, Excel, JSON, testo libero, PDF.

Se non ci sono dati survey in `input/`, scrivi un file placeholder e passa allo step successivo.

## REGOLA FONDAMENTALE: Preservazione VERBATIM

**MAI condensare.** **MAI riassumere.** **MAI parafrasare.**

Ogni parola scritta da un rispondente e' oro. La differenza tra "mi sento stanco" e "mi sento uno straccio ogni mattina" e' la differenza tra copy mediocre e copy che converte.

## Metodo di Processing

### 1. Trascrizione Completa
Se i dati sono in formato strutturato (CSV/Excel):
- Leggi TUTTE le righe
- Per le risposte aperte, preserva il testo INTEGRALE
- Non troncare mai, anche se una risposta e' lunga

### 2. Categorizzazione Tematica
Organizza le risposte per tema (stesse categorie del Source Extraction):
- Situazione iniziale / stato attuale
- Punti di dolore specifici
- Soluzioni gia' provate
- Aspettative dalla nuova soluzione
- Paure e obiezioni
- Linguaggio del desiderio
- Trigger moments
- Informazioni demografiche rilevanti

### 3. Analisi di Frequenza
Per ogni tema, nota:
- Quante persone menzionano lo stesso concetto (anche con parole diverse)
- Le ESATTE parole piu' usate (frequency count)
- Le risposte che si distinguono per profondita' o unicita'

### 4. Gold Nuggets
Identifica le risposte che sono:
- Le piu' lunghe e dettagliate (il rispondente si e' aperto)
- Le piu' emotive (uso di esclamazioni, maiuscole, punteggiatura multipla)
- Le piu' specifiche (numeri, date, nomi, situazioni precise)
- Le piu' contraddittorie (rivelano conflitti interni)

## Output

Scrivi in `data/survey/survey_processing.txt`:

```
# SURVEY PROCESSING — [Mercato Target]

## File Processati
[lista dei file]

## Statistiche
- Numero rispondenti: X
- Risposte aperte analizzate: X

## Risposte Complete per Categoria

### Stato Attuale / Situazione
[TUTTE le risposte VERBATIM, raggruppate per tema]

### Punti di Dolore
[TUTTE le risposte VERBATIM]

### Soluzioni Provate
[TUTTE le risposte VERBATIM]

### Aspettative
[TUTTE le risposte VERBATIM]

### Paure e Obiezioni
[TUTTE le risposte VERBATIM]

### Linguaggio del Desiderio
[TUTTE le risposte VERBATIM]

### Trigger Moments
[TUTTE le risposte VERBATIM]

## Analisi di Frequenza
[parole e concetti piu' frequenti con count]

## Gold Nuggets
[le 15-20 risposte piu' preziose con spiegazione del perche']

## Pattern Emergenti
[pattern che emergono dalla massa dei dati]
```
