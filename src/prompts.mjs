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

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROMPTS_DIR = join(__dirname, "..", "prompts");

// ---------------------------------------------------------------------------
// Research preamble — adapted for Pi tools
// ---------------------------------------------------------------------------
const RESEARCH_PREAMBLE = `\
--- ISTRUZIONI DI RICERCA AUTONOMA ---

Per questa analisi DEVI:
1. Usare bash per cercare dati reali online:
   - Per ricerche web: usa il comando bash con curl o wget per cercare informazioni
   - Per leggere pagine web: usa bash con curl per scaricare e leggere contenuti
2. Se la skill brave-search è disponibile, usala per ricerche strutturate.
3. Se browser-tools è disponibile, usalo per navigare siti interattivi.
4. Incrociare le fonti: mai fidarsi di una singola fonte.
5. Citare SEMPRE la fonte (URL, autore, data) per ogni dato utilizzato.

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

function buildC2Prompt(step, projectDir, productInfo) {
  const template = loadTemplate(step.prompt_file);
  const marketSpec = readFileIfExists(projectDir, "market_spec.txt");
  const manifold = readFileIfExists(projectDir, "avatar_manifold.txt");
  const chapterFile = step.chapter_file;

  const context = `\
--- CONTESTO PROGETTO ---

PRODOTTO/MERCATO:
${productInfo}

--- MARKET SPEC (output del Ciclo 1 — la tua base dati empirica) ---
${marketSpec || "(non ancora generato)"}
--- FINE MARKET SPEC ---

--- AVATAR MANIFOLD (capitoli precedenti — costruisci su questo) ---
${manifold || "(primo capitolo — nessun manifold precedente)"}
--- FINE AVATAR MANIFOLD ---

${RESEARCH_PREAMBLE}

--- ISTRUZIONI OUTPUT ---
1. Scrivi il capitolo completo in: ${chapterFile}
2. Dopo aver scritto il capitolo, APPENDILO anche a avatar_manifold.txt
   (usa read per leggere il contenuto attuale, poi write per aggiungere il tuo capitolo in fondo).
3. Salva eventuali ricerche in: research/
4. Consulta i capitoli precedenti per coerenza e costruisci su ciò che è stato scoperto.
--- FINE ISTRUZIONI OUTPUT ---

--- FINE CONTESTO ---

`;
  return context + template;
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export function buildPrompt(cycle, step, projectDir, productInfo) {
  if (cycle === CYCLE_RESEARCH) {
    return buildC1Prompt(step, projectDir, productInfo);
  } else if (cycle === CYCLE_MANIFOLD) {
    return buildC2Prompt(step, projectDir, productInfo);
  }
  throw new Error(`Cycle ${cycle} not yet implemented`);
}
