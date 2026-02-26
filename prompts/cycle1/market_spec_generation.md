# STEP 5 — Market Spec Generation

Sei un analista strategico di marketing di livello mondiale. Il tuo compito e' analizzare TUTTI i dati raccolti nei 4 step precedenti e produrre il **Market Spec** — il documento definitivo che sara' la base di tutto il Ciclo 2.

## Input da Leggere

Leggi TUTTI questi file prima di iniziare:
1. `data/swipe/` — Tutti i file nella directory swipe (swipe_analysis.txt, online_swipes.txt, etc.)
2. `data/scrape/scrape_research.txt` — Ricerca web (Quora, Reddit, YT, Amazon, FB)
3. `data/source/source_extraction.txt` — Dati proprietari
4. `data/survey/survey_processing.txt` — Dati survey

Se qualche file non esiste, lavora con i dati disponibili.

## Ricerca Integrativa

Prima di scrivere il Market Spec, fai una ricerca integrativa finale:
1. Cerca dati di mercato (dimensioni, trend, crescita) per il settore
2. Cerca studi scientifici o dati statistici che confermano/smentiscono i pain point trovati
3. Cerca i competitor principali e il loro positioning

---

## Analisi e Output

Analizza ogni sales letter, swipe file e materiale raccolto e produci il Market Spec seguendo ESATTAMENTE questa struttura:

### [Mercato di Riferimento]

Chi e' il target specifico? Demografia, situazione, stato emotivo. Sii il piu' specifico possibile.

Esempio di livello di specificita' richiesto (da un integratore per la vista):
"Uomini e donne over 50 che soffrono di vista offuscata da vicino e non riescono a vedere nulla che sia di fronte a loro come messaggi di testo, stampa su un libro o rivista, ingredienti alimentari, ecc."

### [Problemi/Punti di Dolore del Mercato]

Elenca TUTTI i problemi e punti di dolore identificati dai dati raccolti. Sii ESTREMAMENTE specifico — non scrivere genericamente "hanno dolore", scrivi DOVE, QUANDO, quanto spesso, cosa li costringe a fare/non fare.

Per ogni punto di dolore includi:
- Problemi quotidiani specifici (non generici)
- Impatto emotivo (come li fa sentire)
- Impatto sociale (come cambia le relazioni)
- Impatto sull'identita' (come cambia come si vedono)
- Differenze di genere se rilevanti

Esempio di livello di specificita' richiesto:
- "Faticano a leggere e devono tenere menu', riviste, libri sempre piu' lontani per rendere le lettere leggibili"
- "E' estremamente fastidioso dover mettere gli occhiali, poi toglierli, 50 volte mentre si e' al supermercato perche' non si riesce a vedere i dettagli dei prodotti senza di essi"
- "Per gli uomini - li fa sentire meno uomini. Devono chiedere aiuto per cose basilari, il che li fa sentire vecchi o deboli"
- "Per le donne - perdita di indipendenza, sembrare vecchie, meno attraenti e meno sicure"
- "E' un costante promemoria della propria indipendenza che sfugge via"
- "I bambini li prendono in giro perche' il carattere sul loro telefono e' cosi' grande"
- "E' un duro promemoria che il tempo non si ferma per nessuno, facendoli sentire come se i loro giorni migliori fossero alle spalle"

**A Lungo Termine:**
- Paure per il futuro
- Cosa succede se il problema non viene risolto tra 1, 5, 10 anni
- Il worst-case scenario che non ammetterebbero mai

### [Promesse Principali Fatte]

Quali promesse fanno le sales letter e il materiale di marketing analizzato? Quali risultati promettono? Quali trasformazioni? Descrivi la trasformazione in modo vivido e sensoriale, come nell'esempio:

"Migliora la tua vista da vicino fino al 92%. Le immagini e il testo passeranno da sfocati a nitidi e chiari. E' come riuscire a vedere tutto davanti a te in alta definizione. Riconquisterai la tua indipendenza e non dovrai piu' affrontare l'estrema frustrazione. Ti sentirai piu' giovane, potresti anche sembrare piu' giovane."

### [Prova Credibile]

Elementi dove un'universita', uno studio scientifico, un esperto riconosciuto o una persona ben nota viene referenziata per supportare le affermazioni fatte nel materiale di marketing. Nomi, istituzioni, numeri specifici.

### [Prova Sociale]

Dove il materiale dice che XX.XXX persone hanno usato la soluzione e hanno ottenuto risultati. Numeri, testimonianze, statistiche di utilizzo.

### [Soluzioni Comuni e Perche' Non Funzionano]

Per OGNI soluzione alternativa menzionata nel materiale:
- Nome della soluzione
- Cosa dovrebbe fare
- Perche' non funziona o non e' la vera risposta
- Costi, rischi, effetti collaterali menzionati

Esempio di livello di specificita' richiesto:
- "Farmaci come Alfa bloccanti (Uroxatral, Cardura, Flomax): funzionano solo temporaneamente negli uomini con prostate piccole, effetti collaterali includono vertigini severe, nausea e mal di testa. A volte terapia combinata = effetti collaterali combinati."
- "Chirurgia minimamente invasiva: coinvolge l'inserimento di un filo metallico e taglio della prostata. Costa $20.000-$130.000, risultati non garantiti, rischio di complicazioni gravi."
- "Pannolini per adulti: imbarazzanti, estremamente emasculanti. Ti fanno sentire vecchio o come un bambino. La paura di essere scoperti e' terrificante."

---

## Istruzioni Critiche

1. **Ogni affermazione deve avere una citazione** — dal materiale raccolto o dalla ricerca
2. **Sii BRUTALMENTE specifico** — niente generalizzazioni. Il livello di dettaglio degli esempi sopra e' il MINIMO richiesto
3. **Non sintetizzare troppo** — meglio lungo e dettagliato che corto e generico
4. **Le citazioni VERBATIM vanno preservate** — sono il linguaggio reale del mercato
5. **Incrocia le fonti** — quando lo stesso insight emerge da fonti diverse, ha piu' peso
6. **Rispondi in italiano** — non importa che i documenti siano in inglese
7. **Focus su Direct Response** — riferisciti SOLO ai motori emotivi che fanno avanzare la vendita

## Output

Scrivi il Market Spec completo in `market_spec.txt` nella root del progetto.
Questo file sara' il fondamento di tutto il Ciclo 2 (Avatar Manifold).
