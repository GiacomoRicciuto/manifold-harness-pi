# PDF MANIFOLD DESIGN

## Obiettivo
Trasformare il file `avatar_manifold.txt` in un PDF professionale decorato e colorato.

## Istruzioni

1. **Verifica** che il file `avatar_manifold.txt` esista nella directory corrente. Leggilo brevemente per confermare che contenga i capitoli del manifold.

2. **Esegui** lo script Python di generazione PDF:
   ```bash
   python3 {SCRIPT_PATH} avatar_manifold.txt avatar_manifold_professional.pdf
   ```
   Dove `{SCRIPT_PATH}` e' il percorso completo allo script indicato nel contesto sopra.

3. **Verifica** che il file `avatar_manifold_professional.pdf` sia stato creato correttamente:
   ```bash
   ls -la avatar_manifold_professional.pdf
   ```

4. Se lo script fallisce per dipendenze mancanti (weasyprint), prova a installarlo:
   ```bash
   pip install weasyprint
   ```
   Poi riesegui lo script.

5. **NON** modificare il contenuto di avatar_manifold.txt. Lo script gestisce autonomamente il design, i colori, i temi e la formattazione.

## Output Atteso
- `avatar_manifold_professional.pdf` — PDF professionale con cover page, table of contents, capitoli decorati, tipografia professionale e tema colori automatico basato sul mercato.
