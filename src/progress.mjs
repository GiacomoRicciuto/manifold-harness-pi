/**
 * Progress / State Machine
 * ========================
 * Tracks manifold generation progress in .manifold_state.json.
 * Supports crash recovery: restarts from last completed step.
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { join } from "node:path";
import { STATE_FILE, ALL_STEPS, CYCLE_RESEARCH } from "./config.mjs";

// ---------------------------------------------------------------------------
// State I/O
// ---------------------------------------------------------------------------

function statePath(projectDir) {
  return join(projectDir, STATE_FILE);
}

export function loadState(projectDir) {
  const p = statePath(projectDir);
  if (existsSync(p)) {
    return JSON.parse(readFileSync(p, "utf-8"));
  }
  return null;
}

export function saveState(projectDir, state) {
  const p = statePath(projectDir);
  mkdirSync(join(projectDir), { recursive: true });
  writeFileSync(p, JSON.stringify(state, null, 2));
}

// ---------------------------------------------------------------------------
// Initialisation
// ---------------------------------------------------------------------------

export function initState(projectDir, clientName, productInfo) {
  const state = {
    client: clientName,
    product_info: productInfo,
    current_cycle: CYCLE_RESEARCH,
    current_step_index: 0,
    completed_steps: [],
    status: "running",
  };

  // Create output directories
  for (const subdir of [
    "data/swipe", "data/scrape", "data/source", "data/survey",
    "chapters", "research", "input",
  ]) {
    mkdirSync(join(projectDir, subdir), { recursive: true });
  }

  saveState(projectDir, state);
  return state;
}

// ---------------------------------------------------------------------------
// Navigation
// ---------------------------------------------------------------------------

export function getNextAction(state) {
  const idx = state.current_step_index || 0;
  if (idx >= ALL_STEPS.length) return null;
  const [cycle, step] = ALL_STEPS[idx];
  return { cycle, step, index: idx };
}

export function advanceStep(projectDir, state) {
  const idx = state.current_step_index;
  const [cycle, step] = ALL_STEPS[idx];
  state.completed_steps.push(step.id);
  state.current_step_index = idx + 1;

  if (idx + 1 >= ALL_STEPS.length) {
    state.status = "done";
  } else if (ALL_STEPS[idx + 1][0] !== cycle) {
    state.current_cycle = ALL_STEPS[idx + 1][0];
  }

  saveState(projectDir, state);
  return state;
}

// ---------------------------------------------------------------------------
// Display helpers
// ---------------------------------------------------------------------------

export function printSessionHeader(sessionNum, stepName) {
  console.log("\n" + "=".repeat(70));
  console.log(`  SESSION ${sessionNum} — ${stepName}`);
  console.log("=".repeat(70) + "\n");
}

export function printProgressSummary(state) {
  const completed = (state.completed_steps || []).length;
  const total = ALL_STEPS.length;
  const cycle = state.current_cycle || 1;
  const labels = { 1: "Research (4S)", 2: "Manifold" };
  console.log(`\n  Progress: ${completed}/${total} steps completed | Cycle ${cycle} (${labels[cycle] || "?"})`);
  if (state.status === "done") {
    console.log("  STATUS: COMPLETE");
  }
}
