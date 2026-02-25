/**
 * Prompt Loader with Context Injection
 * =====================================
 * Loads prompt templates and injects project context.
 *
 * KEY TRANSLATION NOTE:
 * - Original used WebSearch/WebFetch/Puppeteer for research
 * - Pi version uses brave-search skill + browser-tools skill via bash
 * - Research instructions updated to reference pi-native tools
 */

import { readFileSync, readdirSync, existsSync, mkdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { CYCLE_RESEARCH, CYCLE_MANIFOLD } from "./config.mjs";
import { resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROMPTS_DIR = join(__dirname, "..", "prompts");

// ---------------------------------------------------------------------------
// Research preamble — adapted for Pi tools
// ---------------------------------------------------------------------------
const RESEARCH_PREAMBLE = `\
--- ISTRUZIONI DI RICERCA AUTONOMA ---

Per questa analisi DEVI:
1. Usare bash per cercare dati reali online.
2. Incrociare le fonti: mai fidarsi di una singola fonte.
3. Citare SEMPRE la fonte (URL, autore, data) per ogni dato utilizzato.

COME FARE RICERCA WEB — SEGUI QUESTE ISTRUZIONI ESATTAMENTE:

REGOLA #1: Per leggere QUALSIASI pagina web, usa SEMPRE lynx:
  curl -sL "URL" -H "User-Agent: Mozilla/5.0" | lynx -stdin -dump -nolist | head -200
NON usare MAI curl da solo su HTML — spreca token con HTML/CSS/JS inutile.

REGOLA #2: Per cercare sul web, usa DuckDuckGo HTML (Google/YouTube BLOCCANO curl):
  curl -sL "https://html.duckduckgo.com/html/?q=query+terms" -H "User-Agent: Mozilla/5.0" | lynx -stdin -dump -nolist | head -80

REGOLA #3: Per API JSON (es. Reddit), curl diretto va bene:
  curl -s "https://www.reddit.com/r/sub/search.json?q=query&limit=20" -H "User-Agent: Mozilla/5.0"

NON usare google.com/search (ritorna captcha). NON usare youtube.com/results (richiede JS).
Usa SEMPRE html.duckduckgo.com per le ricerche e lynx per leggere le pagine trovate.

PENSIERO CRITICO:
- Identifica la contraddizione principale di questa analisi: cosa il mercato
  crede che sia vero ma non lo è? Cosa dice di volere ma in realtà non vuole?
- Applica l'Occam's Razor: qual è la spiegazione più semplice?
- Segui la spirale dialettica: ogni contraddizione risolta ne rivela una più profonda.

Salva le ricerche significative in: research/
`;

// ---------------------------------------------------------------------------
// Loaders
// ---------------------------------------------------------------------------

function loadTemplate(promptFile) {
  const path = join(PROMPTS_DIR, promptFile);
  if (!existsSync(path)) {
    throw new Error(`Prompt template not found: ${path}`);
  }
  return readFileSync(path, "utf-8");
}

function listInputFiles(projectDir) {
  const inputDir = join(projectDir, "input");
  if (!existsSync(inputDir)) return "(nessun file in input/)";
  const files = readdirSync(inputDir).filter((f) => !f.startsWith(".")).sort();
  if (files.length === 0) return "(nessun file in input/)";
  return files.map((f) => `- input/${f}`).join("\n");
}

function readFileIfExists(projectDir, filename) {
  const p = join(projectDir, filename);
  if (existsSync(p)) return readFileSync(p, "utf-8");
  return "";
}

// ---------------------------------------------------------------------------
// Cycle 1 prompt builder
// ---------------------------------------------------------------------------

function buildC1Prompt(step, projectDir, productInfo) {
  const template = loadTemplate(step.prompt_file);

  if (step.output_dir) {
    mkdirSync(join(projectDir, step.output_dir), { recursive: true });
  }

  const context = `\
--- CONTESTO PROGETTO ---

PRODOTTO/MERCATO:
${productInfo}

FILE INPUT DISPONIBILI:
${listInputFiles(projectDir)}

DIRECTORY OUTPUT PER QUESTO STEP: ${step.output_dir || step.output_file || "N/A"}

${RESEARCH_PREAMBLE}
--- FINE CONTESTO ---

`;
  return context + template;
}

// ---------------------------------------------------------------------------
// Cycle 2 prompt builder
// ---------------------------------------------------------------------------

/**
 * List completed chapters for reference (names only, not content).
 */
function listChapters(projectDir) {
  const chaptersDir = join(projectDir, "chapters");
  if (!existsSync(chaptersDir)) return [];
  return readdirSync(chaptersDir)
    .filter((f) => f.endsWith(".txt"))
    .sort();
}

function buildC2Prompt(step, projectDir, productInfo) {
  const template = loadTemplate(step.prompt_file);
  const chapterFile = step.chapter_file;
  const chapters = listChapters(projectDir);

  const context = `\
--- CONTESTO PROGETTO ---

PRODOTTO/MERCATO:
${productInfo}

FILE DISPONIBILI (leggili con "read" quando necessario — NON sono inclusi in questo prompt):
- market_spec.txt — La tua base dati empirica dal Ciclo 1 (LEGGILO per primo)
${chapters.length > 0 ? `- chapters/ — Capitoli precedenti completati:\n${chapters.map(f => `    - chapters/${f}`).join("\n")}` : "- (primo capitolo — nessun capitolo precedente)"}

${RESEARCH_PREAMBLE}

--- ISTRUZIONI OUTPUT ---
1. PRIMA DI TUTTO: leggi market_spec.txt e gli ultimi 2 capitoli in chapters/ per contesto.
2. Scrivi il capitolo completo in: ${chapterFile}
3. NON appendere ad avatar_manifold.txt (viene assemblato automaticamente a fine processo).
4. Salva eventuali ricerche in: research/
5. Consulta i capitoli precedenti in chapters/ per coerenza e costruisci su ciò che è stato scoperto.
--- FINE ISTRUZIONI OUTPUT ---

--- FINE CONTESTO ---

`;
  return context + template;
}

// ---------------------------------------------------------------------------
// PDF generation prompt builder
// ---------------------------------------------------------------------------

function buildPdfPrompt(step, projectDir, productInfo, clientName) {
  const template = loadTemplate(step.prompt_file);
  const pdfScript = resolve(join(__dirname, "..", "scripts", "generate_pdf.py"));

  const title = clientName || "Market Research Brief";
  const subtitle = (productInfo || "").split("\n")[0] || "";

  const cmd = `python3 "${pdfScript}" avatar_manifold.txt avatar_manifold_professional.pdf --title "${title}" --subtitle "${subtitle}"`;

  const context = `\
COMANDO ESATTO DA ESEGUIRE:
\`\`\`bash
${cmd}
\`\`\`

`;
  return context + template;
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export function buildPrompt(cycle, step, projectDir, productInfo, clientName) {
  if (cycle === CYCLE_RESEARCH) {
    return buildC1Prompt(step, projectDir, productInfo);
  } else if (cycle === CYCLE_MANIFOLD) {
    // PDF generation step — special prompt builder (no research context needed)
    if (step.id === "pdf_generation") {
      return buildPdfPrompt(step, projectDir, productInfo, clientName);
    }
    return buildC2Prompt(step, projectDir, productInfo);
  }
  throw new Error(`Cycle ${cycle} not yet implemented`);
}
