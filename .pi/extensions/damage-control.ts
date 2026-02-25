/**
 * Damage Control Extension — Security for Manifold Harness
 * =========================================================
 * Translates the Python bash_security_hook into Pi's native extension system.
 *
 * Pi advantage: in-process TypeScript (vs external shell hooks in Claude Code)
 * - Real-time interception of tool calls
 * - Type-safe event narrowing
 * - No subprocess overhead
 */

import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import { isToolCallEventType } from "@mariozechner/pi-coding-agent";

// Allowlist — same as original security.py
const ALLOWED_COMMANDS = new Set([
  // File inspection
  "ls", "cat", "head", "tail", "wc", "grep", "find",
  // File operations
  "cp", "mkdir",
  // Directory
  "pwd",
  // Sleep / process
  "sleep", "ps",
  // Node (for skills)
  "npx", "npm", "node",
  // Web research (Pi replacement for WebSearch/WebFetch)
  "curl", "wget",
]);

// Destructive patterns to always block
const BLOCKED_PATTERNS = [
  /\brm\s+(-[^\s]*)*-[rRf]/,    // rm -rf
  /\bgit\s+reset\s+--hard\b/,    // git reset --hard
  /\bgit\s+push\s+--force\b/,    // git push --force
  /\bchmod\b/,                     // permission changes
  /\bchown\b/,                     // ownership changes
  /\bsudo\b/,                      // privilege escalation
  /\b(mv|rm)\s+\/[^\s]/,          // operations on root paths
];

function extractCommands(cmd: string): string[] {
  const commands: string[] = [];
  // Split on pipes, &&, ||, ;
  const segments = cmd.split(/\s*(?:&&|\|\||;|\|)\s*/);

  for (const segment of segments) {
    const trimmed = segment.trim();
    if (!trimmed) continue;

    // Extract first word (the command)
    const parts = trimmed.split(/\s+/);
    let cmdName = parts[0];

    // Handle env vars prefix (e.g., "FOO=bar command")
    while (cmdName && cmdName.includes("=") && !cmdName.startsWith("=")) {
      parts.shift();
      cmdName = parts[0];
    }

    if (cmdName) {
      // Get basename
      const basename = cmdName.split("/").pop() || cmdName;
      commands.push(basename);
    }
  }

  return commands;
}

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    if (!isToolCallEventType("bash", event)) return { block: false };

    const command = event.input?.command || "";
    if (!command) return { block: false };

    // Check destructive patterns first
    for (const pattern of BLOCKED_PATTERNS) {
      if (pattern.test(command)) {
        return {
          block: true,
          reason: `Blocked destructive pattern: ${pattern.source}`,
        };
      }
    }

    // Extract and validate commands
    const cmds = extractCommands(command);
    if (cmds.length === 0) {
      return { block: true, reason: `Could not parse command: ${command}` };
    }

    for (const cmd of cmds) {
      if (!ALLOWED_COMMANDS.has(cmd)) {
        return {
          block: true,
          reason: `Command '${cmd}' is not in the allowlist`,
        };
      }
    }

    return { block: false };
  });
}
