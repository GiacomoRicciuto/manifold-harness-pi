/**
 * Startup Script
 * ==============
 * Seeds initial data from seed/ directory into generations/ on first run.
 * Then starts the main server.
 *
 * This ensures that when a Railway volume is mounted at /app/generations,
 * the seed data is copied on first deploy and persists across redeploys.
 */

import { existsSync, mkdirSync, cpSync, readFileSync, writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = join(__dirname, "..");
const GENERATIONS_DIR = join(PROJECT_ROOT, "generations");
const SEED_DIR = join(PROJECT_ROOT, "seed");
const JOBS_FILE = join(GENERATIONS_DIR, "jobs.json");

// Ensure generations directory exists
mkdirSync(GENERATIONS_DIR, { recursive: true });

// Seed data from seed/ if generations is empty (first deploy with volume)
if (existsSync(SEED_DIR)) {
  const { readdirSync } = await import("node:fs");
  const seedProjects = readdirSync(SEED_DIR).filter(f => !f.startsWith("."));

  for (const projectName of seedProjects) {
    const destDir = join(GENERATIONS_DIR, projectName);

    if (!existsSync(destDir)) {
      console.log(`[startup] Seeding project: ${projectName}`);
      cpSync(join(SEED_DIR, projectName), destDir, { recursive: true });

      // Create job entry if jobs.json doesn't have it
      let jobs = {};
      if (existsSync(JOBS_FILE)) {
        try { jobs = JSON.parse(readFileSync(JOBS_FILE, "utf-8")); } catch {}
      }

      // Check if this project already has a job entry
      const hasJob = Object.values(jobs).some(j => j.project_dir === destDir);
      if (!hasJob) {
        // Read state to get client info
        const stateFile = join(destDir, ".manifold_state.json");
        let clientName = projectName.replace(/_/g, " ");
        let productInfo = "";
        if (existsSync(stateFile)) {
          try {
            const state = JSON.parse(readFileSync(stateFile, "utf-8"));
            clientName = state.client_name || clientName;
            productInfo = state.product_info || "";
          } catch {}
        }

        const jobId = projectName.substring(0, 12).toLowerCase().replace(/[^a-z0-9]/g, "");
        jobs[jobId] = {
          job_id: jobId,
          client_name: clientName,
          product_info: productInfo,
          project_dir: destDir,
          status: "stopped",
          created_at: new Date().toISOString(),
          pid: null,
          error: null,
        };
        writeFileSync(JOBS_FILE, JSON.stringify(jobs, null, 2));
        console.log(`[startup] Created job entry: ${jobId} → ${clientName}`);
      }
    }
  }
}

// Now start the actual server
console.log("[startup] Starting server...");
await import("./server.mjs");
