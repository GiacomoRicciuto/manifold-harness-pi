#!/usr/bin/env node
/**
 * Agent Manifold — CLI Entry Point (pi-coding-agent version)
 * ===========================================================
 *
 * Usage:
 *   node src/cli.mjs --client "TestoMax" --product-info "Testosterone booster for men 40+"
 *   node src/cli.mjs --client "TestoMax" --input-dir ./dati_cliente --max-iterations 1
 *   node src/cli.mjs --client "TestoMax" --product-info "..." --provider openai --model gpt-4o
 *
 * Environment Variables:
 *   ANTHROPIC_API_KEY    (for Anthropic models)
 *   OPENAI_API_KEY       (for OpenAI models)
 *   GOOGLE_GEMINI_API_KEY (for Google models)
 *
 * Pi advantage: multi-provider support out of the box!
 */

import { parseArgs } from "node:util";
import { readFileSync, mkdirSync, readdirSync, copyFileSync, statSync, existsSync } from "node:fs";
import { join, resolve } from "node:path";
import { runManifoldAgent } from "./agent.mjs";
import { DEFAULT_MODEL, DEFAULT_PROVIDER } from "./config.mjs";

// ---------------------------------------------------------------------------
// CLI argument parsing
// ---------------------------------------------------------------------------

function printHelp() {
  console.log(`
Agent Manifold — AI Manifold Brief Generator (pi-coding-agent)
==============================================================

Usage:
  node src/cli.mjs --client <name> --product-info <text> [options]

Required:
  --client <name>           Client/project name (directory under generations/)
  --product-info <text>     Product/market description
  OR
  --product-info-file <path> Path to file with product description

Options:
  --input-dir <path>        Directory with input files (swipes, surveys, etc.)
  --max-iterations <n>      Max number of sessions (default: unlimited)
  --model <id>              Model to use (default: ${DEFAULT_MODEL})
  --provider <name>         Provider (default: ${DEFAULT_PROVIDER})
                            Options: anthropic, openai, google, mistral, groq, etc.
  --help                    Show this help

Examples:
  node src/cli.mjs --client "TestoMax" --product-info "Testosterone booster supplement targeting men over 40"
  node src/cli.mjs --client "TestoMax" --provider openai --model gpt-4o --product-info "..."
  node src/cli.mjs --client "TestoMax" --max-iterations 1  # dry run (single session)
`);
}

function parseCliArgs() {
  const { values } = parseArgs({
    options: {
      client: { type: "string" },
      "product-info": { type: "string", default: "" },
      "product-info-file": { type: "string" },
      "input-dir": { type: "string" },
      "max-iterations": { type: "string" },
      model: { type: "string", default: DEFAULT_MODEL },
      provider: { type: "string", default: DEFAULT_PROVIDER },
      help: { type: "boolean", default: false },
    },
    strict: true,
  });
  return values;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  let args;
  try {
    args = parseCliArgs();
  } catch (e) {
    console.error(`Error: ${e.message}`);
    printHelp();
    process.exit(1);
  }

  if (args.help) {
    printHelp();
    process.exit(0);
  }

  if (!args.client) {
    console.error("Error: --client is required");
    printHelp();
    process.exit(1);
  }

  // Resolve product info
  let productInfo = args["product-info"];
  if (args["product-info-file"]) {
    productInfo = readFileSync(resolve(args["product-info-file"]), "utf-8");
  }
  if (!productInfo) {
    console.error("Error: provide --product-info or --product-info-file");
    process.exit(1);
  }

  // Check for API key based on provider
  const provider = args.provider;
  const keyMap = {
    anthropic: "ANTHROPIC_API_KEY",
    openai: "OPENAI_API_KEY",
    google: "GOOGLE_GEMINI_API_KEY",
    mistral: "MISTRAL_API_KEY",
    groq: "GROQ_API_KEY",
  };
  const envKey = keyMap[provider];
  if (envKey && !process.env[envKey]) {
    console.error(`Error: ${envKey} not set for provider '${provider}'`);
    console.error(`Set it with: export ${envKey}=your-key-here`);
    process.exit(1);
  }

  // Project directory
  const projectDir = join("generations", args.client);
  mkdirSync(projectDir, { recursive: true });

  // Copy input files
  if (args["input-dir"]) {
    const inputDir = resolve(args["input-dir"]);
    if (existsSync(inputDir)) {
      const dest = join(projectDir, "input");
      mkdirSync(dest, { recursive: true });
      for (const f of readdirSync(inputDir)) {
        const srcPath = join(inputDir, f);
        if (statSync(srcPath).isFile()) {
          copyFileSync(srcPath, join(dest, f));
          console.log(`  Copied: ${f} -> input/`);
        }
      }
    }
  }

  // Run
  const maxIterations = args["max-iterations"] ? parseInt(args["max-iterations"], 10) : null;

  try {
    await runManifoldAgent({
      projectDir,
      model: args.model,
      provider,
      clientName: args.client,
      productInfo,
      maxIterations,
    });
  } catch (e) {
    if (e.code === "ERR_USE_AFTER_CLOSE") {
      // Graceful shutdown
    } else {
      console.error(`\nFatal error: ${e.message}`);
      console.error("\nRun again to resume from last completed step.");
      process.exit(1);
    }
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
