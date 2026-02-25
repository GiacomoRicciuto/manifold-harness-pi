/**
 * Pi Coding Agent Client
 * =======================
 * Spawns pi-coding-agent processes in print mode.
 *
 * KEY FIX: Writes prompt to temp file and uses @file syntax
 * to avoid shell argument length limits. System prompt also
 * written to file and passed via --system-prompt flag reading from file.
 */

import { spawn } from "node:child_process";
import { createInterface } from "node:readline";
import { join, resolve } from "node:path";
import { existsSync, writeFileSync, mkdirSync, unlinkSync, cpSync } from "node:fs";
import { PI_TOOLS, PI_THINKING_LEVEL, SESSION_TIMEOUT } from "./config.mjs";

// ---------------------------------------------------------------------------
// System Prompt — identical across all 20 sessions
// ---------------------------------------------------------------------------
export const SYSTEM_PROMPT = `\
Sei un ricercatore e analista di marketing di livello mondiale.
Il tuo compito è produrre analisi di mercato psicologicamente profonde, empiricamente fondate e straordinariamente specifiche.

PRINCIPI DI ANALISI:
1. Contraddizione principale: identifica sempre la tensione tra ciò che il mercato
   dice e ciò che fa, ciò che crede e ciò che è vero.
2. Validazione empirica: ogni affermazione va verificata con ricerca online.
   Usa bash con curl per cercare e leggere pagine web.
3. Occam's Razor: la spiegazione più semplice che copre tutti i dati è quella giusta.
4. Specificità: mai generalizzare. Cita sempre la fonte. Usa citazioni VERBATIM.
5. Spirale dialettica: ogni contraddizione risolta ne rivela una più profonda.
   Segui la catena fino alla radice.

HAI ACCESSO A:
- bash per eseguire comandi (curl per web, grep per cercare, etc.)
- read/write/edit per gestire i file del progetto
- grep/find/ls per esplorare file e contenuti

DEVI SEMPRE:
- Leggere il contesto fornito nel prompt (market_spec, manifold precedente, dati input)
- Fare ricerca autonoma per validare e arricchire ogni analisi
- Scrivere output nei file indicati dal prompt
- Essere specifico, empirico, mai generico
- Citare le fonti di ogni affermazione
- Preservare le citazioni VERBATIM dal materiale di ricerca`;

// ---------------------------------------------------------------------------
// Pi session runner
// ---------------------------------------------------------------------------

/**
 * Run a single pi-coding-agent session.
 *
 * Writes prompt to a temp file and uses @file syntax to avoid CLI arg limits.
 * Uses --mode json for event streaming, -p for print (non-interactive) mode.
 */
export async function runPiSession({
  message,
  projectDir,
  model,
  provider,
}) {
  const absDir = resolve(projectDir);

  // Write prompt to temp file (avoids CLI arg length limits)
  const tmpDir = join(absDir, ".tmp");
  mkdirSync(tmpDir, { recursive: true });

  const promptFile = join(tmpDir, "prompt.md");
  writeFileSync(promptFile, message);

  // Write SYSTEM.md into project .pi/ so pi picks it up from cwd
  const piDir = join(absDir, ".pi");
  mkdirSync(piDir, { recursive: true });
  writeFileSync(join(piDir, "SYSTEM.md"), SYSTEM_PROMPT);

  return new Promise((resolvePromise) => {
    const args = [
      "-p",                              // Print mode (non-interactive, single-shot)
      "--mode", "json",                   // Stream all events as JSON lines
      "--tools", PI_TOOLS.join(","),      // Available tools
      "--thinking", "off",               // No thinking for faster execution
      "--no-extensions",                  // Clean environment
      "--no-skills",                      // No auto-discovered skills
      "--no-session",                     // Ephemeral — don't save session files
    ];

    // Model specification: "provider/model" format
    if (provider && model) {
      args.push("--model", `${provider}/${model}`);
    } else if (model) {
      args.push("--model", model);
    }

    // Pass prompt via @file to avoid shell argument length limits
    args.push(`@${promptFile}`);

    console.log("  Spawning pi-coding-agent session...");
    console.log(`  Model: ${provider ? provider + "/" : ""}${model}`);
    console.log(`  Prompt file: ${promptFile} (${(message.length / 1024).toFixed(1)}KB)\n`);

    const proc = spawn("pi", args, {
      cwd: absDir,
      env: {
        ...process.env,
        PI_CODING_AGENT_DIR: process.env.PI_CODING_AGENT_DIR || join(process.env.HOME, ".pi", "agent"),
      },
      stdio: ["pipe", "pipe", "pipe"],
    });

    let responseText = "";
    let lastError = "";
    let toolCalls = 0;

    // Parse JSON event stream from stdout
    const rl = createInterface({ input: proc.stdout });

    rl.on("line", (line) => {
      if (!line.trim()) return;

      let event;
      try {
        event = JSON.parse(line);
      } catch {
        // Non-JSON output (e.g., pi startup messages), print as-is
        process.stdout.write(line + "\n");
        return;
      }

      switch (event.type) {
        case "session":
          console.log("  [pi] Session created");
          break;

        case "agent_start":
          console.log("  [pi] Agent started — waiting for model response...");
          break;

        case "turn_start":
          console.log("  [pi] Turn started");
          break;

        case "message_start":
          if (event.message?.role === "assistant") {
            console.log("  [pi] Assistant responding...");
          }
          break;

        case "message_update":
          if (event.assistantMessageEvent?.delta) {
            const delta = event.assistantMessageEvent.delta;
            responseText += delta;
            process.stdout.write(delta);
          }
          break;

        case "message_end":
          break;

        case "tool_execution_start":
          toolCalls++;
          const toolName = event.toolName || event.name || "unknown";
          process.stdout.write(`\n  [Tool: ${toolName}]`);
          if (event.input) {
            const s = JSON.stringify(event.input);
            process.stdout.write(`  ${s.substring(0, 200)}${s.length > 200 ? "..." : ""}`);
          }
          process.stdout.write("\n");
          break;

        case "tool_execution_end":
          process.stdout.write("  [Done]\n");
          break;

        case "tool_execution_update":
          break;

        case "turn_end":
          console.log("  [pi] Turn ended");
          break;

        case "agent_end":
          console.log("  [pi] Agent finished");
          break;

        case "error":
          lastError = event.message || event.error || JSON.stringify(event);
          console.error(`  [Error] ${lastError}`);
          break;

        default:
          // Log unknown events for debugging
          console.log(`  [pi:${event.type}]`);
          break;
      }
    });

    // Capture stderr
    let stderrBuf = "";
    proc.stderr.on("data", (chunk) => {
      const text = chunk.toString();
      stderrBuf += text;
      // Print stderr in real-time for debugging
      process.stderr.write(text);
    });

    // Timeout safety
    const timeout = setTimeout(() => {
      console.error(`\n  [TIMEOUT] Session exceeded ${SESSION_TIMEOUT / 1000}s — killing`);
      proc.kill("SIGTERM");
    }, SESSION_TIMEOUT);

    proc.on("close", (code) => {
      clearTimeout(timeout);
      rl.close();

      // Cleanup temp files
      try { unlinkSync(promptFile); } catch {}
      try { unlinkSync(systemFile); } catch {}

      console.log("\n" + "-".repeat(70) + "\n");

      if (code === 0) {
        console.log(`  Session complete. Tool calls: ${toolCalls}`);
        resolvePromise({ status: "continue", responseText });
      } else {
        const errMsg = lastError || stderrBuf.substring(0, 500) || `Exit code ${code}`;
        console.error(`  Session error (code ${code}): ${errMsg}`);
        resolvePromise({ status: "error", responseText: errMsg });
      }
    });

    proc.on("error", (err) => {
      clearTimeout(timeout);
      console.error(`  Failed to spawn pi: ${err.message}`);
      resolvePromise({ status: "error", responseText: err.message });
    });
  });
}
