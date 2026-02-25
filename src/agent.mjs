/**
 * Agent Session Runner
 * ====================
 * Core loop: load state → determine next step → build prompt → run pi session → advance.
 *
 * TRANSLATION: Python async loop → Node.js async/await with pi spawn
 */

import { resolve } from "node:path";
import { runPiSession } from "./client.mjs";
import { AUTO_CONTINUE_DELAY } from "./config.mjs";
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
    });

    if (status === "continue") {
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
  console.log(`  Chapters: ${absDir}/chapters/`);
  printProgressSummary(state);
  console.log("\nDone!");
}
