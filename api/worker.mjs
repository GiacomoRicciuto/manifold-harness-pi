/**
 * Worker Process
 * ===============
 * Runs manifold agent in a forked child process, updating job status.
 * Redirects stdout/stderr to worker.log for live UI streaming.
 *
 * This file is executed via fork() from the server.
 * It receives job params via process.argv.
 *
 * Usage (called by server, not directly):
 *   node api/worker.mjs <jobId> <clientName> <productInfo> <projectDir> <model> <provider>
 */

import { createWriteStream, mkdirSync } from "node:fs";
import { join, resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = join(__dirname, "..");

// Parse args from parent process
const [,, jobId, clientName, productInfo, projectDir, model, provider] = process.argv;

if (!jobId || !clientName || !productInfo || !projectDir) {
  console.error("Worker: missing arguments");
  process.exit(1);
}

// Import job registry
const jobsPath = join(PROJECT_ROOT, "api", "jobs.mjs");
const { updateJob } = await import(jobsPath);

// Import agent
const agentPath = join(PROJECT_ROOT, "src", "agent.mjs");
const { runManifoldAgent } = await import(agentPath);

// Setup project dir and logging
const absDir = resolve(projectDir);
mkdirSync(absDir, { recursive: true });

const logFile = join(absDir, "worker.log");
const logStream = createWriteStream(logFile, { flags: "a" }); // append mode

// Redirect stdout/stderr to worker.log
const origWrite = process.stdout.write.bind(process.stdout);
const origErrWrite = process.stderr.write.bind(process.stderr);

process.stdout.write = (chunk, encoding, callback) => {
  logStream.write(chunk, encoding, callback);
  // Also write to actual stdout for debugging
  origWrite(chunk, encoding);
  return true;
};

process.stderr.write = (chunk, encoding, callback) => {
  logStream.write(chunk, encoding, callback);
  origErrWrite(chunk, encoding);
  return true;
};

// Run
try {
  updateJob(jobId, { status: "running", pid: process.pid });

  await runManifoldAgent({
    projectDir: absDir,
    model: model || "claude-opus-4-5",
    provider: provider || "anthropic",
    clientName,
    productInfo,
    maxIterations: null,
  });

  updateJob(jobId, { status: "done" });
} catch (err) {
  console.error("Worker fatal error:", err.stack || err.message);
  updateJob(jobId, { status: "error", error: err.message });
} finally {
  logStream.end();
}
