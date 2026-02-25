/**
 * Pi Coding Agent Client
 * =======================
 * Spawns pi-coding-agent processes in JSON streaming mode.
 *
 * TRANSLATION MAP:
 *   ClaudeSDKClient.query(msg) → spawn("pi", ["-p", "--mode", "json", msg])
 *   ClaudeSDKClient.receive_response() → readline on stdout JSON events
 *   system_prompt → --system-prompt flag
 *   allowed_tools → --tools flag
 *   mcp_servers → replaced by skills (brave-search, browser-tools)
 *   hooks/security → damage-control extension
 *
 * Pi advantages over Claude Code SDK:
 *   - Multi-provider (anthropic, openai, google, etc.)
 *   - Thinking levels (off → xhigh)
 *   - Session persistence with tree branching
 *   - In-process extensions (vs external hooks)
 *   - No sandbox needed (damage-control handles security)
 */

import { spawn } from "node:child_process";
import { createInterface } from "node:readline";
import { join, resolve } from "node:path";
import { existsSync } from "node:fs";
import { PI_TOOLS, PI_THINKING_LEVEL, SESSION_TIMEOUT } from "./config.mjs";

// ---------------------------------------------------------------------------
// System Prompt — identical across all 20 sessions
// Adapted: WebSearch/WebFetch/Puppeteer → bash+curl, brave-search, browser-tools
// ---------------------------------------------------------------------------
export const SYSTEM_PROMPT = `\
Sei un ricercatore e analista di marketing di livello mondiale.
Il tuo compito è produrre analisi di mercato psicologicamente profonde, empiricamente fondate e straordinariamente specifiche.

PRINCIPI DI ANALISI:
1. Contraddizione principale: identifica sempre la tensione tra ciò che il mercato
   dice e ciò che fa, ciò che crede e ciò che è vero.
2. Validazione empirica: ogni affermazione va verificata con ricerca online.
   Usa bash con curl per cercare e leggere pagine web. Se brave-search è disponibile, usalo.
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
 * Spawns `pi` in print+json mode, streams events, returns response text.
 *
 * @param {Object} options
 * @param {string} options.message - The full prompt to send
 * @param {string} options.projectDir - Working directory for this session
 * @param {string} options.model - Model identifier (e.g., "claude-opus-4-5")
 * @param {string} [options.provider] - Provider name (e.g., "anthropic")
 * @param {string} [options.piConfigDir] - Path to .pi/ config directory
 * @returns {Promise<{status: string, responseText: string}>}
 */
export async function runPiSession({
  message,
  projectDir,
  model,
  provider,
  piConfigDir,
}) {
  return new Promise((resolvePromise, reject) => {
    const args = [
      "-p",                    // Print mode (non-interactive, single-shot)
      "--mode", "json",        // Stream all events as JSON lines
      "--tools", PI_TOOLS.join(","),
      "--thinking", PI_THINKING_LEVEL,
      "--system-prompt", SYSTEM_PROMPT,
      "--no-extensions",       // We'll load extensions explicitly if needed
      "--no-skills",           // Clean environment per session
    ];

    // Model specification
    if (provider && model) {
      args.push("--model", `${provider}/${model}`);
    } else if (model) {
      args.push("--model", model);
    }

    // Pi config directory (for extensions, skills, settings)
    if (piConfigDir && existsSync(piConfigDir)) {
      // Pi reads .pi/ from cwd, so we set cwd to project dir
      // and place .pi/ config there
    }

    // The prompt goes as the last positional argument
    args.push(message);

    console.log("  Spawning pi-coding-agent session...\n");

    const proc = spawn("pi", args, {
      cwd: resolve(projectDir),
      env: {
        ...process.env,
        // Ensure pi can find its global config
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
        // Non-JSON output, print as-is
        process.stdout.write(line + "\n");
        return;
      }

      // Handle different event types from pi's JSON stream
      switch (event.type) {
        case "message_start":
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
          // Streaming tool output (e.g., bash)
          break;

        case "turn_start":
        case "turn_end":
        case "agent_start":
        case "agent_end":
          break;

        case "error":
          lastError = event.message || event.error || JSON.stringify(event);
          console.error(`  [Error] ${lastError}`);
          break;

        default:
          // Unknown events — log at debug level
          break;
      }
    });

    // Capture stderr for diagnostics
    let stderrBuf = "";
    proc.stderr.on("data", (chunk) => {
      stderrBuf += chunk.toString();
    });

    // Timeout safety
    const timeout = setTimeout(() => {
      console.error(`\n  [TIMEOUT] Session exceeded ${SESSION_TIMEOUT / 1000}s — killing`);
      proc.kill("SIGTERM");
    }, SESSION_TIMEOUT);

    proc.on("close", (code) => {
      clearTimeout(timeout);
      rl.close();

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
