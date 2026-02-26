/**
 * Job Registry
 * =============
 * Simple JSON-file based job tracking with atomic writes.
 */

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { randomUUID } from "node:crypto";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = join(__dirname, "..");
const GENERATIONS_DIR = join(PROJECT_ROOT, "generations");
// Store jobs.json inside generations/ so it persists with the Railway volume
const JOBS_FILE = join(GENERATIONS_DIR, "jobs.json");

function readJobs() {
  if (existsSync(JOBS_FILE)) {
    try {
      return JSON.parse(readFileSync(JOBS_FILE, "utf-8"));
    } catch {
      return {};
    }
  }
  return {};
}

function writeJobs(jobs) {
  writeFileSync(JOBS_FILE, JSON.stringify(jobs, null, 2));
}

export function createJob(clientName, productInfo, projectDir) {
  const jobId = randomUUID().replace(/-/g, "").substring(0, 12);
  const jobs = readJobs();
  jobs[jobId] = {
    job_id: jobId,
    client_name: clientName,
    product_info: productInfo,
    project_dir: projectDir,
    status: "queued",
    created_at: new Date().toISOString(),
    pid: null,
    error: null,
  };
  writeJobs(jobs);
  return jobId;
}

export function updateJob(jobId, updates) {
  const jobs = readJobs();
  if (jobs[jobId]) {
    Object.assign(jobs[jobId], updates);
    writeJobs(jobs);
  }
}

export function getJob(jobId) {
  const jobs = readJobs();
  return jobs[jobId] || null;
}

export function deleteJob(jobId) {
  const jobs = readJobs();
  delete jobs[jobId];
  writeJobs(jobs);
}

export function listJobs() {
  const jobs = readJobs();
  return Object.values(jobs).sort(
    (a, b) => new Date(b.created_at) - new Date(a.created_at)
  );
}
