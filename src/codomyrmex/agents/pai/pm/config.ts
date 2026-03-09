import { join } from "path";
import { homedir } from "os";

// ============================================================================
// Server
// ============================================================================

const portArgIdx = process.argv.indexOf("--port");
/** HTTP server port. */
export const PORT = parseInt(
    process.argv.find(a => a.startsWith("--port="))?.split("=")[1] ||
    (portArgIdx !== -1 ? process.argv[portArgIdx + 1] : undefined) ||
    process.env.PAI_PM_PORT || "8889"
);

// ============================================================================
// Core Paths
// ============================================================================

/** Root PAI installation directory. */
export const PAI_DIR = process.env.PAI_DIR || join(homedir(), ".claude");

/** Mission/project/task YAML state directory. */
export const STATE_DIR = process.env.PAI_STATE_DIR || join(PAI_DIR, "MEMORY", "STATE");

export const MISSIONS_DIR = join(STATE_DIR, "missions");
export const PROJECTS_DIR = join(STATE_DIR, "projects");
export const SYNC_DIR = process.env.PAI_SYNC_DIR || join(STATE_DIR, "sync");

// ============================================================================
// External Service Defaults
// ============================================================================

/** Default GitHub owner/org for listing repos. */
export const GITHUB_DEFAULT_OWNER = process.env.GITHUB_DEFAULT_OWNER || "";

// ============================================================================
// Token/Credential Paths
// ============================================================================

/** Base directory for credential storage. */
export const CODOMYRMEX_CONFIG_DIR = join(homedir(), ".codomyrmex");

export const GCAL_TOKEN_PATH = join(CODOMYRMEX_CONFIG_DIR, "gcal_token.json");
export const GCAL_LINKS_PATH = join(CODOMYRMEX_CONFIG_DIR, "gcal_links.json");
export const GMAIL_TOKEN_PATH = join(CODOMYRMEX_CONFIG_DIR, "gmail_token.json");

// ============================================================================
// LLM Defaults (configurable via env)
// ============================================================================

/** Default LLM backend for bikeride/email features. */
export const LLM_BACKEND = process.env.PAI_PM_LLM_BACKEND || "ollama";

/** Default LLM model for bikeride/email features. gemma3 preferred over qwen3 (no thinking artifacts). */
export const LLM_MODEL = process.env.PAI_PM_LLM_MODEL || "gemma3:4b";

/** LLM subprocess timeout in milliseconds. */
export const LLM_TIMEOUT = parseInt(process.env.PAI_PM_LLM_TIMEOUT || "60000");

