/**
 * Agent Session Runner
 * ====================
 * Core loop: load state → determine next step → build prompt → run pi session → advance.
 *
 * TRANSLATION: Python async loop → Node.js async/await with pi spawn
 */

import { resolve, join } from "node:path";
import { readdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { runPiSession } from "./client.mjs";
import { AUTO_CONTINUE_DELAY, CYCLE_MANIFOLD } from "./config.mjs";
import {
  loadState, saveState, initState,
  getNextAction, advanceStep,
  printSessionHeader, printProgressSummary,
} from "./progress.mjs";
import { buildPrompt } from "./prompts.mjs";

function sleep(seconds) {
  return new Promise((r) => setTimeout(r, seconds * 1000));
}

/**
 * Assemble avatar_manifold.txt from all chapter files in chapters/ directory.
 * This replaces the previous approach where the agent had to manually append.
 */
function assembleManifold(projectDir, clientName, productInfo) {
  const chaptersDir = join(projectDir, "chapters");
  if (!existsSync(chaptersDir)) return;

  const files = readdirSync(chaptersDir)
    .filter((f) => f.endsWith(".txt"))
    .sort();

  if (files.length === 0) return;

  // Extract market from productInfo (first line or short summary)
  const productLines = (productInfo || "").split("\n").filter(l => l.trim());
  const marketLine = productLines[0] || clientName || "Market Research Brief";

  // Header format expected by generate_pdf.py parser:
  // - "# Title" → doc_title (first # line that is NOT CAPITOLO)
  // - Line with "— " → doc_subtitle
  // - Line with "Mercato" → doc_market
  const title = clientName || "Avatar Manifold";
  const subtitle = `${title} — Ricerca di Mercato Professionale`;
  const market = `Mercato: ${marketLine}`;
  const date = new Date().toLocaleDateString("it-IT", { month: "long", year: "numeric" });

  const header = `# ${title}\n${subtitle}\n# ${market}\n# Data: ${date}\n# Capitoli: ${files.length}\n\n`;

  const content = files.map((f) => {
    return readFileSync(join(chaptersDir, f), "utf-8");
  }).join("\n\n" + "=".repeat(80) + "\n\n");

  writeFileSync(join(projectDir, "avatar_manifold.txt"), header + content);
  console.log(`  [Auto-assembled avatar_manifold.txt from ${files.length} chapters]`);
}

/**
 * Main autonomous loop for manifold generation.
 */
export async function runManifoldAgent({
  projectDir,
  model,
  provider,
  clientName,
  productInfo,
  maxIterations,
}) {
  const absDir = resolve(projectDir);

  console.log("\n" + "=".repeat(70));
  console.log("  AGENT MANIFOLD — AI Manifold Brief Generator (pi-coding-agent)");
  console.log("=".repeat(70));
  console.log(`\n  Client: ${clientName}`);
  console.log(`  Project: ${absDir}`);
  console.log(`  Model: ${provider ? provider + "/" : ""}${model}`);
  if (maxIterations) console.log(`  Max iterations: ${maxIterations}`);
  console.log();

  // Load or init state
  let state = loadState(absDir);
  if (!state) {
    console.log("  Initializing new project...");
    state = initState(absDir, clientName, productInfo);
  } else {
    console.log("  Resuming existing project...");
    printProgressSummary(state);
  }

  let iteration = 0;

  while (true) {
    iteration++;

    if (maxIterations && iteration > maxIterations) {
      console.log(`\nReached max iterations (${maxIterations})`);
      break;
    }

    // Determine next step
    const action = getNextAction(state);
    if (!action) {
      console.log("\n  All steps completed!");
      break;
    }

    const { cycle, step, index } = action;
    printSessionHeader(iteration, step.name);

    // Build prompt with context injection
    const prompt = buildPrompt(cycle, step, absDir, productInfo);

    // Run pi session
    const { status, responseText } = await runPiSession({
      message: prompt,
      projectDir: absDir,
      model,
      provider,
      cycle,
    });

    if (status === "continue") {
      // Auto-assemble avatar_manifold.txt from all chapter files after each Cycle 2 step
      // (skip assembly for pdf_generation — it consumes the already-assembled file)
      if (cycle === CYCLE_MANIFOLD && step.id !== "pdf_generation") {
        assembleManifold(absDir, clientName, productInfo);
      }
      state = advanceStep(absDir, state);
      printProgressSummary(state);
      console.log(`\nNext session in ${AUTO_CONTINUE_DELAY}s...`);
      await sleep(AUTO_CONTINUE_DELAY);
    } else if (status === "error") {
      console.log("\nSession error — retrying same step...");
      saveState(absDir, state);
      await sleep(AUTO_CONTINUE_DELAY);
    }
  }

  // Final summary
  console.log("\n" + "=".repeat(70));
  console.log("  MANIFOLD GENERATION COMPLETE");
  console.log("=".repeat(70));
  console.log(`\n  Output: ${absDir}`);
  console.log(`  Market Spec: ${absDir}/market_spec.txt`);
  console.log(`  Avatar Manifold: ${absDir}/avatar_manifold.txt`);
  console.log(`  PDF: ${absDir}/avatar_manifold_professional.pdf`);
  console.log(`  Chapters: ${absDir}/chapters/`);
  printProgressSummary(state);
  console.log("\nDone!");
}
