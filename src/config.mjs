/**
 * Manifold Harness Configuration
 * ===============================
 * Constants and step definitions for the 2-cycle Manifold generation process.
 * Translated from Python config.py → Node.js ESM for pi-coding-agent.
 */

// ---------------------------------------------------------------------------
// Models — Pi supports multi-provider. Default to Anthropic Claude Opus.
// Override with --model flag (e.g., "openai/gpt-4o", "anthropic/claude-opus-4-5")
// ---------------------------------------------------------------------------
export const DEFAULT_MODEL = "claude-opus-4-5";
export const DEFAULT_PROVIDER = "anthropic";

// ---------------------------------------------------------------------------
// Timing
// ---------------------------------------------------------------------------
export const AUTO_CONTINUE_DELAY = 3; // seconds between sessions
export const SESSION_TIMEOUT = 600000; // 10 min max per session (ms)

// ---------------------------------------------------------------------------
// Pi-specific settings
// ---------------------------------------------------------------------------
export const PI_THINKING_LEVEL = "high"; // off, minimal, low, medium, high, xhigh
export const PI_TOOLS = ["read", "write", "edit", "bash", "grep", "find", "ls"];

// ---------------------------------------------------------------------------
// State file
// ---------------------------------------------------------------------------
export const STATE_FILE = ".manifold_state.json";

// ---------------------------------------------------------------------------
// Cycles
// ---------------------------------------------------------------------------
export const CYCLE_RESEARCH = 1;
export const CYCLE_MANIFOLD = 2;

// ---------------------------------------------------------------------------
// Cycle 1 — 4S Framework Research (5 steps)
// ---------------------------------------------------------------------------
export const C1_STEPS = [
  {
    id: "swipe_analysis",
    name: "Swipe Analysis",
    prompt_file: "cycle1/swipe_analysis.md",
    output_dir: "data/swipe",
  },
  {
    id: "scrape_research",
    name: "Scrape Research",
    prompt_file: "cycle1/scrape_research.md",
    output_dir: "data/scrape",
  },
  {
    id: "source_extraction",
    name: "Source Extraction",
    prompt_file: "cycle1/source_extraction.md",
    output_dir: "data/source",
  },
  {
    id: "survey_processing",
    name: "Survey Processing",
    prompt_file: "cycle1/survey_processing.md",
    output_dir: "data/survey",
  },
  {
    id: "market_spec_generation",
    name: "Market Spec Generation",
    prompt_file: "cycle1/market_spec_generation.md",
    output_file: "market_spec.txt",
  },
];

// ---------------------------------------------------------------------------
// Cycle 2 — Avatar Manifold (15 chapters)
// ---------------------------------------------------------------------------
export const C2_STEPS = [
  { id: "01_buyer_base", name: "01 — Buyer Base", prompt_file: "cycle2/01_buyer_base.md", chapter_file: "chapters/01_buyer_base.txt" },
  { id: "02_pain_matrix", name: "02 — Pain Matrix", prompt_file: "cycle2/02_pain_matrix.md", chapter_file: "chapters/02_pain_matrix.txt" },
  { id: "03_core_wound", name: "03 — Core Wound", prompt_file: "cycle2/03_core_wound.md", chapter_file: "chapters/03_core_wound.txt" },
  { id: "04_benefit_matrix", name: "04 — Benefit Matrix", prompt_file: "cycle2/04_benefit_matrix.md", chapter_file: "chapters/04_benefit_matrix.txt" },
  { id: "05_desire_daisy_chain", name: "05 — Desire Daisy Chain", prompt_file: "cycle2/05_desire_daisy_chain.md", chapter_file: "chapters/05_desire_daisy_chain.txt" },
  { id: "06_resonance_hierarchy", name: "06 — Resonance Hierarchy", prompt_file: "cycle2/06_resonance_hierarchy.md", chapter_file: "chapters/06_resonance_hierarchy.txt" },
  { id: "07_rh_constraints", name: "07 — RH Constraints", prompt_file: "cycle2/07_rh_constraints.md", chapter_file: "chapters/07_rh_constraints.txt" },
  { id: "08_dissolution_frameworks", name: "08 — Dissolution Frameworks", prompt_file: "cycle2/08_dissolution_frameworks.md", chapter_file: "chapters/08_dissolution_frameworks.txt" },
  { id: "09_epiphany_threshold", name: "09 — Epiphany Threshold", prompt_file: "cycle2/09_epiphany_threshold.md", chapter_file: "chapters/09_epiphany_threshold.txt" },
  { id: "10_maze_theory_hooks", name: "10 — Maze Theory Hooks", prompt_file: "cycle2/10_maze_theory_hooks.md", chapter_file: "chapters/10_maze_theory_hooks.txt" },
  { id: "11_story_prompts", name: "11 — Story Prompts", prompt_file: "cycle2/11_story_prompts.md", chapter_file: "chapters/11_story_prompts.txt" },
  { id: "12_interoceptive_mechanisms", name: "12 — Interoceptive Mechanisms", prompt_file: "cycle2/12_interoceptive_mechanisms.md", chapter_file: "chapters/12_interoceptive_mechanisms.txt" },
  { id: "13_language_patterns", name: "13 — Language Patterns", prompt_file: "cycle2/13_language_patterns.md", chapter_file: "chapters/13_language_patterns.txt" },
  { id: "14_ccc", name: "14 — Concentric Circles of Concern", prompt_file: "cycle2/14_ccc.md", chapter_file: "chapters/14_ccc.txt" },
  { id: "15_ejection_triggers", name: "15 — Ejection Triggers", prompt_file: "cycle2/15_ejection_triggers.md", chapter_file: "chapters/15_ejection_triggers.txt" },
];

// ---------------------------------------------------------------------------
// All steps in order: [ [cycle, step], ... ]
// ---------------------------------------------------------------------------
export const ALL_STEPS = [
  ...C1_STEPS.map((step) => [CYCLE_RESEARCH, step]),
  ...C2_STEPS.map((step) => [CYCLE_MANIFOLD, step]),
];
