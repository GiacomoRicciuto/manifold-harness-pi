# PDF MANIFOLD DESIGN

## Obiettivo
Trasformare il file `avatar_manifold.txt` in un PDF professionale decorato e colorato.

## Istruzioni

1. **Verifica** che il file `avatar_manifold.txt` esista nella directory corrente. Leggilo brevemente per confermare che contenga i capitoli del manifold. Controlla quanti capitoli ci sono (cerca le righe che iniziano con "CAPITOLO").

2. **Esegui** lo script Python di generazione PDF con il comando ESATTO fornito nel contesto sopra (include --title e --subtitle personalizzati). Copia e incolla il comando senza modificarlo.

3. Se lo script fallisce per dipendenze mancanti (weasyprint, pango), installa:
   ```bash
   pip install --break-system-packages weasyprint
   apt-get update -qq && apt-get install -y libpango1.0-0 libpangoft2-1.0-0 libglib2.0-0 libharfbuzz0b libfontconfig1
   ```
   Poi riesegui lo script.

4. **VERIFICA OBBLIGATORIA POST-GENERAZIONE** — Questo step e' CRITICO:
   ```bash
   ls -la avatar_manifold_professional.pdf
   ```

   Il PDF DEVE soddisfare TUTTI questi criteri:
   - **Il file esiste** e ha dimensione > 0
   - **La dimensione e' proporzionata al contenuto**: un manifold con 15 capitoli deve produrre un PDF di almeno 500KB, tipicamente 2-10MB. Se il PDF e' sotto i 100KB, qualcosa e' andato storto.
   - **Controlla il numero di pagine** (se possibile): un manifold completo produce tipicamente 80-200+ pagine.

   Se il PDF e' troppo piccolo (< 500KB per un manifold con 10+ capitoli):
   - Leggi l'output dello script per capire se ci sono errori
   - Controlla se il file HTML intermedio e' stato creato correttamente
   - Il problema piu' comune e' che il parser non riconosce i capitoli — verifica il formato delle intestazioni dei capitoli nel file avatar_manifold.txt

5. **NON** modificare il contenuto di avatar_manifold.txt. Lo script gestisce autonomamente il design, i colori, i temi e la formattazione.

## Output Atteso
- `avatar_manifold_professional.pdf` — PDF professionale con cover page, table of contents, capitoli decorati, tipografia professionale e tema colori automatico basato sul mercato.
- Un manifold completo (15 capitoli) produce tipicamente un PDF di 2-10MB e 100-200+ pagine.
