/**
 * Express Web Server for Manifold Harness (Pi Edition)
 * =====================================================
 * Translated from FastAPI (Python) → Express (Node.js)
 *
 * Endpoints:
 *   POST   /api/jobs              Create job + spawn worker
 *   GET    /api/jobs              List all jobs
 *   GET    /api/jobs/:id/status   Step-by-step progress
 *   GET    /api/jobs/:id/logs     Stream worker logs (offset-based)
 *   GET    /api/jobs/:id/download Download ZIP of outputs
 *   POST   /api/jobs/:id/stop     Kill worker process
 *   POST   /api/jobs/:id/resume   Respawn worker from checkpoint
 *   DELETE /api/jobs/:id          Delete job + files
 *   GET    /                      Serve frontend SPA
 */

import express from "express";
import multer from "multer";
import archiver from "archiver";
import { fork } from "node:child_process";
import {
  existsSync, readFileSync, mkdirSync, writeFileSync,
  statSync, readdirSync, rmSync, copyFileSync,
  openSync, readSync, closeSync,
} from "node:fs";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { createJob, getJob, updateJob, deleteJob, listJobs } from "./jobs.mjs";
import { ALL_STEPS, DEFAULT_MODEL, DEFAULT_PROVIDER } from "../src/config.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = join(__dirname, "..");
const GENERATIONS_DIR = join(PROJECT_ROOT, "generations");
const FRONTEND_DIR = join(PROJECT_ROOT, "frontend");

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Multer for file uploads (store in temp, copy to project dir)
const upload = multer({ dest: join(PROJECT_ROOT, ".tmp_uploads") });

// Track child processes
const childProcesses = new Map();

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function getStepsStatus(job) {
  const projectDir = job.project_dir;
  const stateFile = join(projectDir, ".manifold_state.json");

  let completedSteps = [];
  let currentStepIndex = 0;

  if (existsSync(stateFile)) {
    try {
      const state = JSON.parse(readFileSync(stateFile, "utf-8"));
      completedSteps = state.completed_steps || [];
      currentStepIndex = state.current_step_index || 0;
    } catch {}
  }

  return ALL_STEPS.map(([cycle, step], i) => {
    let status;
    if (completedSteps.includes(step.id)) {
      status = "done";
    } else if (i === currentStepIndex && job.status === "running") {
      status = "running";
    } else {
      status = "pending";
    }
    return { index: i, id: step.id, name: step.name, status };
  });
}

function spawnWorker(jobId, clientName, productInfo, projectDir, model, provider) {
  const workerPath = join(__dirname, "worker.mjs");
  const child = fork(workerPath, [
    jobId, clientName, productInfo, projectDir,
    model || DEFAULT_MODEL,
    provider || DEFAULT_PROVIDER,
  ], {
    cwd: PROJECT_ROOT,
    detached: true, // Create new process group (like os.setpgrp)
    stdio: "ignore",
  });
  child.unref();
  childProcesses.set(jobId, child);
  return child.pid;
}

// ---------------------------------------------------------------------------
// API Routes
// ---------------------------------------------------------------------------

// POST /api/jobs — Create job
app.post("/api/jobs", upload.array("files"), (req, res) => {
  const { client_name, product_info, model, provider } = req.body;

  if (!client_name || !product_info) {
    return res.status(400).json({ error: "client_name and product_info required" });
  }

  // Create project directory
  let projectDir = join(GENERATIONS_DIR, client_name.replace(/\s+/g, "_"));
  let counter = 1;
  const base = projectDir;
  while (existsSync(projectDir)) {
    projectDir = `${base}_${counter}`;
    counter++;
  }
  mkdirSync(projectDir, { recursive: true });

  // Copy uploaded files
  if (req.files && req.files.length > 0) {
    const inputDir = join(projectDir, "input");
    mkdirSync(inputDir, { recursive: true });
    for (const f of req.files) {
      copyFileSync(f.path, join(inputDir, f.originalname));
      // Clean up temp
      try { rmSync(f.path); } catch {}
    }
  }

  const jobId = createJob(client_name, product_info, projectDir);
  const pid = spawnWorker(jobId, client_name, product_info, projectDir, model, provider);
  updateJob(jobId, { pid });

  res.json({ job_id: jobId, status: "queued" });
});

// GET /api/jobs — List all jobs
app.get("/api/jobs", (req, res) => {
  const jobs = listJobs();
  const result = jobs.map((job) => {
    const steps = getStepsStatus(job);
    const completed = steps.filter((s) => s.status === "done").length;
    return {
      job_id: job.job_id,
      client_name: job.client_name,
      status: job.status,
      created_at: job.created_at,
      progress: `${completed}/${steps.length}`,
      error: job.error,
    };
  });
  res.json(result);
});

// GET /api/jobs/:id/status — Detailed step progress
app.get("/api/jobs/:id/status", (req, res) => {
  const job = getJob(req.params.id);
  if (!job) return res.status(404).json({ error: "Job not found" });

  const steps = getStepsStatus(job);
  const completed = steps.filter((s) => s.status === "done").length;

  res.json({
    job_id: job.job_id,
    client_name: job.client_name,
    status: job.status,
    total_steps: steps.length,
    completed_steps: completed,
    steps,
    error: job.error,
  });
});

// GET /api/jobs/:id/logs — Stream logs from offset
app.get("/api/jobs/:id/logs", (req, res) => {
  const job = getJob(req.params.id);
  if (!job) return res.status(404).json({ error: "Job not found" });

  const logFile = join(job.project_dir, "worker.log");
  if (!existsSync(logFile)) {
    return res.json({ content: "", offset: 0 });
  }

  const offset = parseInt(req.query.offset) || 0;
  const size = statSync(logFile).size;

  if (offset >= size) {
    return res.json({ content: "", offset });
  }

  // Read new bytes (cap at 50KB)
  const readSize = Math.min(size - offset, 50_000);
  const fd = openSync(logFile, "r");
  const buf = Buffer.alloc(readSize);
  readSync(fd, buf, 0, readSize, offset);
  closeSync(fd);

  const content = buf.toString("utf-8");
  res.json({ content, offset: offset + Buffer.byteLength(content, "utf-8") });
});

// GET /api/jobs/:id/download — Download ZIP
app.get("/api/jobs/:id/download", (req, res) => {
  const job = getJob(req.params.id);
  if (!job) return res.status(404).json({ error: "Job not found" });
  if (job.status !== "done") return res.status(400).json({ error: "Job not completed" });

  const projectDir = job.project_dir;
  const filename = `manifold_${job.client_name.replace(/\s+/g, "_")}.zip`;

  res.setHeader("Content-Type", "application/zip");
  res.setHeader("Content-Disposition", `attachment; filename=${filename}`);

  const archive = archiver("zip", { zlib: { level: 9 } });
  archive.pipe(res);

  // Main files
  for (const fname of ["avatar_manifold.txt", "market_spec.txt"]) {
    const fpath = join(projectDir, fname);
    if (existsSync(fpath)) archive.file(fpath, { name: fname });
  }

  // Folders
  for (const folder of ["research", "data", "chapters"]) {
    const fdir = join(projectDir, folder);
    if (existsSync(fdir)) archive.directory(fdir, folder);
  }

  archive.finalize();
});

// POST /api/jobs/:id/stop — Kill worker
app.post("/api/jobs/:id/stop", (req, res) => {
  const job = getJob(req.params.id);
  if (!job) return res.status(404).json({ error: "Job not found" });
  if (job.status !== "running") return res.status(400).json({ error: "Job not running" });

  const pid = job.pid;
  if (pid) {
    try {
      // Kill process group (detached child)
      process.kill(-pid, "SIGKILL");
    } catch {
      try { process.kill(pid, "SIGKILL"); } catch {}
    }
  }

  // Also kill tracked child
  const child = childProcesses.get(req.params.id);
  if (child) {
    try { child.kill("SIGKILL"); } catch {}
    childProcesses.delete(req.params.id);
  }

  updateJob(req.params.id, { status: "stopped" });
  res.json({ status: "stopped" });
});

// POST /api/jobs/:id/resume — Respawn worker
app.post("/api/jobs/:id/resume", (req, res) => {
  const job = getJob(req.params.id);
  if (!job) return res.status(404).json({ error: "Job not found" });
  if (!["stopped", "error"].includes(job.status)) {
    return res.status(400).json({ error: "Job cannot be resumed" });
  }

  const pid = spawnWorker(
    req.params.id, job.client_name, job.product_info, job.project_dir
  );
  updateJob(req.params.id, { status: "running", pid, error: null });
  res.json({ status: "running" });
});

// DELETE /api/jobs/:id — Delete job
app.delete("/api/jobs/:id", (req, res) => {
  const job = getJob(req.params.id);
  if (!job) return res.status(404).json({ error: "Job not found" });

  // Stop if running
  if (job.status === "running" && job.pid) {
    try { process.kill(-job.pid, "SIGKILL"); } catch {
      try { process.kill(job.pid, "SIGKILL"); } catch {}
    }
  }

  // Remove files
  if (existsSync(job.project_dir)) {
    rmSync(job.project_dir, { recursive: true, force: true });
  }

  deleteJob(req.params.id);
  res.json({ status: "deleted" });
});

// ---------------------------------------------------------------------------
// Serve frontend
// ---------------------------------------------------------------------------
if (existsSync(FRONTEND_DIR)) {
  app.use(express.static(FRONTEND_DIR));
  app.get("/", (req, res) => {
    res.sendFile(join(FRONTEND_DIR, "index.html"));
  });
}

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------
const PORT = process.env.PORT || 8000;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Manifold Harness (Pi Edition) running on http://0.0.0.0:${PORT}`);
  mkdirSync(GENERATIONS_DIR, { recursive: true });
});
