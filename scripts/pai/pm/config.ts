/**
 * config.ts - Externalized Configuration for PAI PM Tools
 *
 * Centralizes all path and configuration references so they can be
 * overridden via environment variables. This replaces the hardcoded
 * `~/.claude` paths scattered across individual CLI tools.
 *
 * Environment Variables:
 *   PAI_DIR           - Root PAI directory (default: ~/.claude)
 *   PAI_STATE_DIR     - Mission/project/task state (default: $PAI_DIR/MEMORY/STATE)
 *   PAI_SYNC_DIR      - GitHub sync mappings (default: $PAI_STATE_DIR/sync)
 *   GITHUB_DEFAULT_OWNER - Default GitHub org (default: from env or "")
 */

import { join } from "path";
import { homedir } from "os";

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
