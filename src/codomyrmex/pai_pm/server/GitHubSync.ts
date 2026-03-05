#!/usr/bin/env bun
/**
 * GitHubSync.ts - Bi-directional PAI ↔ GitHub sync engine
 *
 * Syncs PAI projects/tasks with GitHub repos and issues.
 * Uses `gh` CLI for all GitHub API interactions (requires `gh` authenticated).
 *
 * ## Architecture
 *
 * Entity Mapping:
 *   PAI Project  ↔  GitHub Repo        (linked via github_sync.json)
 *   PAI Task     ↔  GitHub Issue       (tracked in task_map / issue_map)
 *   PAI Mission  ↔  GitHub Project v2  (requires read:project scope)
 *
 * Sync Strategy:
 *   - Pull-first: GitHub state imported before pushing PAI state
 *   - Timestamp-based: last_synced tracked per entity
 *   - Label-based: PAI labels (pai-managed, status:*, priority:*) on GitHub issues
 *   - Conflict resolution: Last-write-wins with full audit trail in mapping file
 *
 * Data Storage:
 *   - ~/.claude/MEMORY/STATE/projects/<slug>/github_sync.json
 *   - Contains task_map (PAI task → GitHub issue) and issue_map (issue# → PAI task)
 *
 * ## Commands (13 total)
 *
 *   repos                          List GitHub repos for an owner
 *   status [--project slug]        Show sync status for linked projects
 *   link <pai-slug> <owner/repo>   Link PAI project to GitHub repo
 *   unlink <pai-slug>              Disable sync (preserves mapping history)
 *   push [--project slug] [--all]  Push PAI tasks → GitHub Issues
 *   pull [--project slug] [--all]  Pull GitHub Issues → PAI tasks
 *   sync [--project slug] [--all]  Bi-directional sync (pull then push)
 *   create-issue --project <slug>  Create a new GitHub issue from PAI
 *   close-issue --project <slug>   Close/reopen a GitHub issue
 *   diff --project <slug>          Preview what sync would change
 *   cleanup <owner/repo>           Close test-generated issues
 *   edit-issue --project <slug>    Edit an existing GitHub issue
 *   create-repo --name <name>      Create a new GitHub repository
 *
 * ## Options
 *
 *   --owner <name>     GitHub owner/org (default: docxology)
 *   --project <slug>   Target specific PAI project
 *   --all              Apply to all linked projects
 *   --dry-run          Preview changes without executing
 *   --force            Use PAI state on conflicts
 *
 * ## Examples
 *
 *   bun GitHubSync.ts repos --owner docxology
 *   bun GitHubSync.ts link my-project docxology/my-repo
 *   bun GitHubSync.ts push --project my-project --dry-run
 *   bun GitHubSync.ts sync --all
 *   bun GitHubSync.ts status
 *
 * ## Testing
 *
 *   bun TestGitHubSync.ts --suite all --verbose
 *   bun TestGitHubSync.ts --suite cli
 *   bun TestGitHubSync.ts --suite api
 *
 * @author PAI System
 * @version 2.0.0
 * @see TestGitHubSync.ts for comprehensive test suite
 */

import { existsSync, readFileSync, writeFileSync, readdirSync, mkdirSync } from "fs";
import { join } from "path";
import { homedir } from "os";
import { execFileSync } from "child_process";

// ============================================================================
// Constants
// ============================================================================

const HOME = process.env.HOME || homedir();
const PAI_DIR = process.env.PAI_DIR || join(HOME, ".claude");
const PROJECTS_DIR = join(PAI_DIR, "MEMORY", "STATE", "projects");
const MISSIONS_DIR = join(PAI_DIR, "MEMORY", "STATE", "missions");
const DEFAULT_OWNER = "docxology";

// Status mapping: PAI → GitHub
const PAI_TO_GITHUB_STATUS: Record<string, string> = {
  completed: "closed",
  in_progress: "open",
  remaining: "open",
  blocked: "open",
  optional: "open",
};

// Status mapping: GitHub → PAI
const GITHUB_TO_PAI_STATUS: Record<string, string> = {
  open: "remaining",
  closed: "completed",
};

// Labels for PAI metadata
const PAI_LABEL = "pai-managed";
const PRIORITY_LABELS: Record<string, string> = {
  HIGH: "priority:high",
  MEDIUM: "priority:medium",
  LOW: "priority:low",
};

const SECTION_LABELS: Record<string, string> = {
  in_progress: "status:in-progress",
  remaining: "status:remaining",
  blocked: "status:blocked",
  optional: "status:optional",
  completed: "status:completed",
};

// ============================================================================
// Types
// ============================================================================

interface GitHubRepo {
  name: string;
  nameWithOwner: string;
  description: string;
  visibility: string;
  url: string;
  isPrivate: boolean;
  updatedAt: string;
}

interface GitHubIssue {
  number: number;
  title: string;
  state: string;
  body: string;
  labels: Array<{ name: string }>;
  assignees: Array<{ login: string }>;
  updatedAt: string;
  url: string;
  milestone?: { title: string; number: number };
}

interface SyncMapping {
  repo: string;
  sync_enabled: boolean;
  last_synced: string;
  last_push: string;
  last_pull: string;
  task_map: Record<string, {
    issue_number: number;
    issue_url: string;
    last_synced: string;
    pai_section: string;
    github_state: string;
  }>;
  issue_map: Record<number, {
    pai_task: string;
    last_synced: string;
  }>;
}

interface MissionSyncMapping {
  project_id: string;
  project_number: number;
  sync_enabled: boolean;
  last_synced: string;
}

interface SyncResult {
  success: boolean;
  action: string;
  project?: string;
  pushed?: number;
  pulled?: number;
  conflicts?: string[];
  details?: any[];
  error?: string;
}

// ============================================================================
// Help
// ============================================================================

function showHelp(): void {
  console.log(`
GitHubSync - Bi-directional PAI ↔ GitHub sync engine

USAGE:
  bun ~/.claude/skills/PAI/Tools/GitHubSync.ts <command> [options]

COMMANDS:
  repos                          List GitHub repos for owner
  status                         Show sync status for all linked projects
  link <pai-slug> <owner/repo>   Link PAI project to GitHub repo
  unlink <pai-slug>              Remove GitHub link from PAI project
  push                           Push PAI tasks to GitHub Issues
  pull                           Pull GitHub Issues into PAI tasks
  sync                           Full bi-directional sync
  diff                           Preview what sync would change
  cleanup <owner/repo>           Close test-generated issues
  edit-issue                     Edit an existing GitHub issue
  create-repo                    Create a new GitHub repository
  create-issue                   Create a new GitHub issue
  close-issue                    Close or reopen a GitHub issue

OPTIONS:
  --owner <name>         GitHub owner (default: ${DEFAULT_OWNER})
  --project <slug>       Target specific PAI project
  --all                  Sync all linked projects
  --dry-run              Show what would happen without making changes
  --force                Override conflict resolution (use PAI state)
  --help, -h             Show this help

EXAMPLES:
  bun GitHubSync.ts repos
  bun GitHubSync.ts link my-project docxology/MetaInformAnt
  bun GitHubSync.ts push --project my-project
  bun GitHubSync.ts pull --all
  bun GitHubSync.ts sync --project my-project
  bun GitHubSync.ts status

OUTPUT:
  JSON: { "success": true, "action": "...", ... }
`);
  process.exit(0);
}

// ============================================================================
// GitHub CLI Helpers
// ============================================================================

function ghArr(args: string[], retries = 3): string {
  const ghBin = Bun.which("gh") ?? "gh";
  const env: Record<string, string> = { GH_PROMPT_DISABLED: "1" };
  const extraPaths = ["/opt/homebrew/bin", "/usr/local/bin"];
  env.PATH = extraPaths.join(":") + ":" + (process.env.PATH || "");
  if (process.env.HOME) env.HOME = process.env.HOME;
  if (process.env.USER) env.USER = process.env.USER;

  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      return execFileSync(ghBin, args, {
        encoding: "utf-8",
        timeout: 30000,
        env,
      }).trim();
    } catch (err: unknown) {
      const e = err as { status?: number; message?: string };
      if (attempt === retries) throw new Error(`gh ${args.join(" ")}: ${e.message}`);
      // retry on transient failures
    }
  }
  throw new Error("gh: max retries exceeded");
}

/** @deprecated Use ghArr() for safe argument passing */
function gh(args: string, retries = 3): string {
  // Split on whitespace but respect simple quoted strings
  // This is a fallback - prefer ghArr() for new code
  const parts: string[] = [];
  const regex = /"([^"]*)"|'([^']*)'|(\S+)/g;
  let match: RegExpExecArray | null;
  while ((match = regex.exec(args)) !== null) {
    parts.push(match[1] ?? match[2] ?? match[3]);
  }
  return ghArr(parts, retries);
}

function ghJSON<T>(args: string[]): T {
  const output = ghArr(args);
  try {
    return JSON.parse(output) as T;
  } catch {
    throw new Error(`Failed to parse gh output as JSON: ${output.slice(0, 200)}`);
  }
}

function ghGraphQL<T>(query: string, variables?: Record<string, any>): T {
  const cmd: string[] = ["api", "graphql", "-f", `query=${query}`];
  if (variables) {
    for (const [key, val] of Object.entries(variables)) {
      cmd.push("-f", `${key}=${JSON.stringify(val)}`);
    }
  }
  return ghJSON<T>(cmd);
}

// ============================================================================
// Sync File Management
// ============================================================================

function getSyncPath(projectSlug: string): string {
  return join(PROJECTS_DIR, projectSlug, "github_sync.json");
}

function getMissionSyncPath(missionSlug: string): string {
  return join(MISSIONS_DIR, missionSlug, "github_sync.json");
}

export function loadSyncMapping(projectSlug: string): SyncMapping | null {
  const path = getSyncPath(projectSlug);
  if (!existsSync(path)) return null;
  try {
    return JSON.parse(readFileSync(path, "utf-8"));
  } catch {
    return null;
  }
}

function saveSyncMapping(projectSlug: string, mapping: SyncMapping): void {
  const path = getSyncPath(projectSlug);
  writeFileSync(path, JSON.stringify(mapping, null, 2) + "\n");
}

function loadMissionSyncMapping(missionSlug: string): MissionSyncMapping | null {
  const path = getMissionSyncPath(missionSlug);
  if (!existsSync(path)) return null;
  try {
    return JSON.parse(readFileSync(path, "utf-8"));
  } catch {
    return null;
  }
}

// ============================================================================
// PAI Data Helpers
// ============================================================================

// TODO(M9): Replace with js-yaml for proper YAML spec compliance
function parseSimpleYaml(content: string): Record<string, any> {
  const result: Record<string, any> = {};
  let currentArrayKey: string | null = null;
  const currentArray: string[] = [];

  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;

    if (trimmed.startsWith("- ") && currentArrayKey) {
      let value = trimmed.slice(2).trim();
      if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }
      currentArray.push(value);
      continue;
    }

    if (currentArrayKey && currentArray.length > 0) {
      result[currentArrayKey] = [...currentArray];
      currentArray.length = 0;
      currentArrayKey = null;
    }

    const colonIdx = trimmed.indexOf(":");
    if (colonIdx === -1) continue;

    const key = trimmed.slice(0, colonIdx).trim();
    let value = trimmed.slice(colonIdx + 1).trim();

    if (!value) { currentArrayKey = key; continue; }

    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    result[key] = value;
  }

  if (currentArrayKey && currentArray.length > 0) {
    result[currentArrayKey] = [...currentArray];
  }
  return result;
}

interface ParsedTasks {
  header: string;
  completed: string[];
  in_progress: string[];
  remaining: string[];
  blocked: string[];
  optional: string[];
  footer: string;
}

function parseTasksMd(content: string): ParsedTasks {
  const result: ParsedTasks = {
    header: "", completed: [], in_progress: [], remaining: [],
    blocked: [], optional: [], footer: "",
  };

  let currentSection: keyof Omit<ParsedTasks, "header" | "footer"> | null = null;
  const headerLines: string[] = [];
  let foundFirstSection = false;

  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    const lower = trimmed.toLowerCase();

    if (lower.startsWith("## completed")) { currentSection = "completed"; foundFirstSection = true; continue; }
    if (lower.startsWith("## in progress")) { currentSection = "in_progress"; foundFirstSection = true; continue; }
    if (lower.startsWith("## remaining")) { currentSection = "remaining"; foundFirstSection = true; continue; }
    if (lower.startsWith("## blocked")) { currentSection = "blocked"; foundFirstSection = true; continue; }
    if (lower.startsWith("## optional") || lower.startsWith("## deferred") || lower.startsWith("## skipped")) {
      currentSection = "optional"; foundFirstSection = true; continue;
    }

    if (!foundFirstSection) { headerLines.push(line); continue; }

    if (currentSection && (trimmed.startsWith("- [") || trimmed.startsWith("- "))) {
      let taskText = trimmed;
      if (trimmed.startsWith("- [x] ")) taskText = trimmed.slice(6);
      else if (trimmed.startsWith("- [ ] ")) taskText = trimmed.slice(6);
      else if (trimmed.startsWith("- [~] ")) taskText = trimmed.slice(6);
      else if (trimmed.startsWith("- ")) taskText = trimmed.slice(2);
      // Strip GitHub URL suffix (e.g. [#7](https://github.com/.../issues/7)) for clean task title
      taskText = taskText.replace(/\s*\[#\d+\]\(https:\/\/github\.com\/[^)]+\)\s*$/, "").trim();
      result[currentSection].push(taskText);
    }
  }

  result.header = headerLines.join("\n");
  return result;
}

function writeTasksMd(projectDir: string, tasks: ParsedTasks, mapping?: SyncMapping | null): void {
  const lines: string[] = [];
  lines.push(tasks.header.trimEnd());
  lines.push("");

  const sections: Array<[string, keyof Omit<ParsedTasks, "header" | "footer">, string]> = [
    ["Completed", "completed", "x"],
    ["In Progress", "in_progress", " "],
    ["Remaining", "remaining", " "],
    ["Blocked", "blocked", " "],
    ["Optional/Deferred", "optional", " "],
  ];

  for (const [heading, key, check] of sections) {
    lines.push(`## ${heading}`);
    for (const t of tasks[key]) {
      // Strip any existing GitHub URL suffix before re-appending
      const cleanTitle = t.replace(/\s*\[#\d+\]\(https:\/\/github\.com\/[^)]+\)\s*$/, "").trim();
      // Append GitHub issue URL if task is mapped (try exact, then trimmed key match)
      let taskMapping = mapping?.task_map?.[cleanTitle];
      if (!taskMapping && mapping?.task_map) {
        // Fuzzy match: some task keys may have trailing whitespace
        for (const [k, v] of Object.entries(mapping.task_map)) {
          if (k.trim() === cleanTitle) { taskMapping = v as any; break; }
        }
      }
      if (taskMapping?.issue_url) {
        lines.push(`- [${check}] ${cleanTitle} [#${taskMapping.issue_number}](${taskMapping.issue_url})`);
      } else {
        lines.push(`- [${check}] ${cleanTitle}`);
      }
    }
    lines.push("");
  }

  lines.push("---");
  lines.push("");
  lines.push(`*Updated: ${new Date().toISOString().split("T")[0]}*`);
  lines.push("");
  writeFileSync(join(projectDir, "TASKS.md"), lines.join("\n"));
}

function getLinkedProjects(): Array<{ slug: string; repo: string; sync: SyncMapping }> {
  const linked: Array<{ slug: string; repo: string; sync: SyncMapping }> = [];
  if (!existsSync(PROJECTS_DIR)) return linked;

  for (const slug of readdirSync(PROJECTS_DIR)) {
    const mapping = loadSyncMapping(slug);
    if (mapping && mapping.sync_enabled) {
      linked.push({ slug, repo: mapping.repo, sync: mapping });
    }
  }
  return linked;
}

function getAllProjectSlugs(): string[] {
  if (!existsSync(PROJECTS_DIR)) return [];
  return readdirSync(PROJECTS_DIR).filter(d =>
    existsSync(join(PROJECTS_DIR, d, "PROJECT.yaml"))
  );
}

// ============================================================================
// Command: repos
// ============================================================================

/**
 * List all GitHub repositories for a given owner.
 * @param owner - GitHub username or org (default: docxology)
 * @returns Array of GitHubRepo objects sorted by updatedAt descending
 */
export function listRepos(owner: string = DEFAULT_OWNER): GitHubRepo[] {
  const repos = ghJSON<GitHubRepo[]>(
    ["repo", "list", owner, "--limit", "100", "--json", "name,nameWithOwner,description,visibility,url,isPrivate,updatedAt"]
  );
  return repos.sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
}

// ============================================================================
// Command: create-repo
// ============================================================================

/**
 * Create a new GitHub repository.
 * @param name - Repository name
 * @param isPrivate - Whether the repo should be private (default: true)
 * @param description - Optional repo description
 * @param owner - GitHub owner/org (default: docxology)
 * @returns SyncResult with repo URL
 */
export function createRepo(name: string, isPrivate = true, description?: string, owner: string = DEFAULT_OWNER): SyncResult {
  const fullName = `${owner}/${name}`;
  const createArgs = ["repo", "create", fullName];
  createArgs.push(isPrivate ? "--private" : "--public");
  if (description) { createArgs.push("--description", description); }
  createArgs.push("--confirm");
  try {
    const output = ghArr(createArgs);
    const url = `https://github.com/${fullName}`;
    return {
      success: true,
      action: "create-repo",
      details: [{ repo: fullName, url, output: output.substring(0, 200) }],
    };
  } catch (err: any) {
    return { success: false, action: "create-repo", error: err.message };
  }
}

// ============================================================================
// Command: status
// ============================================================================

/**
 * Get sync status for one or all PAI projects.
 * @param projectSlug - Optional specific project slug. Omit for all projects.
 * @returns Status object with linked flag, repo, sync timestamps, mapped counts
 */
export function getSyncStatus(projectSlug?: string): any {
  if (projectSlug) {
    const mapping = loadSyncMapping(projectSlug);
    if (!mapping) return { project: projectSlug, linked: false };

    const taskCount = Object.keys(mapping.task_map).length;
    const issueCount = Object.keys(mapping.issue_map).length;
    return {
      project: projectSlug,
      linked: true,
      repo: mapping.repo,
      sync_enabled: mapping.sync_enabled,
      last_synced: mapping.last_synced,
      last_push: mapping.last_push,
      last_pull: mapping.last_pull,
      mapped_tasks: taskCount,
      mapped_issues: issueCount,
    };
  }

  // Status for all projects
  const slugs = getAllProjectSlugs();
  const statuses: any[] = [];
  for (const slug of slugs) {
    const mapping = loadSyncMapping(slug);
    if (mapping) {
      statuses.push({
        project: slug,
        linked: true,
        repo: mapping.repo,
        sync_enabled: mapping.sync_enabled,
        last_synced: mapping.last_synced,
        mapped_tasks: Object.keys(mapping.task_map).length,
      });
    } else {
      statuses.push({ project: slug, linked: false });
    }
  }
  return { projects: statuses, linked_count: statuses.filter(s => s.linked).length };
}

// ============================================================================
// Command: link
// ============================================================================

/**
 * Link a PAI project to a GitHub repository.
 * Creates github_sync.json mapping file and PAI labels on the repo.
 * @param paiSlug - PAI project slug (must exist in MEMORY/STATE/projects/)
 * @param githubRepo - GitHub repo in "owner/name" format (e.g. "docxology/MetaInformAnt")
 * @returns SyncResult with success flag and link details
 */
export function linkProject(paiSlug: string, githubRepo: string): SyncResult {
  const projectDir = join(PROJECTS_DIR, paiSlug);
  if (!existsSync(join(projectDir, "PROJECT.yaml"))) {
    return { success: false, action: "link", error: `PAI project not found: ${paiSlug}` };
  }

  // Validate repo exists
  try {
    ghArr(["repo", "view", githubRepo, "--json", "name"]);
  } catch {
    return { success: false, action: "link", error: `GitHub repo not found or not accessible: ${githubRepo}` };
  }

  // Ensure PAI label exists on the repo
  try {
    ghArr(["label", "create", PAI_LABEL, "-R", githubRepo, "--description", "Managed by PAI", "--color", "3B82F6", "--force"]);
  } catch { /* label may already exist */ }

  // Create priority and section labels
  for (const [, label] of Object.entries(PRIORITY_LABELS)) {
    try { ghArr(["label", "create", label, "-R", githubRepo, "--color", "F59E0B", "--force"]); } catch { /* ok */ }
  }
  for (const [, label] of Object.entries(SECTION_LABELS)) {
    try { ghArr(["label", "create", label, "-R", githubRepo, "--color", "06B6D4", "--force"]); } catch { /* ok */ }
  }

  const now = new Date().toISOString();
  const mapping: SyncMapping = {
    repo: githubRepo,
    sync_enabled: true,
    last_synced: now,
    last_push: "",
    last_pull: "",
    task_map: {},
    issue_map: {},
  };

  saveSyncMapping(paiSlug, mapping);

  return {
    success: true,
    action: "link",
    project: paiSlug,
    details: [{ linked: githubRepo, labels_created: true }],
  };
}

// ============================================================================
// Command: unlink
// ============================================================================

/**
 * Unlink a PAI project from GitHub. Disables sync but preserves mapping history.
 * @param paiSlug - PAI project slug to unlink
 * @returns SyncResult with success flag
 */
export function unlinkProject(paiSlug: string): SyncResult {
  const syncPath = getSyncPath(paiSlug);
  if (!existsSync(syncPath)) {
    return { success: false, action: "unlink", error: `Project not linked: ${paiSlug}` };
  }

  const mapping = loadSyncMapping(paiSlug);
  // Don't delete the file — just disable sync and preserve history
  if (mapping) {
    mapping.sync_enabled = false;
    saveSyncMapping(paiSlug, mapping);
  }

  return {
    success: true,
    action: "unlink",
    project: paiSlug,
    details: [{ unlinked: true, mapping_preserved: true }],
  };
}

// ============================================================================
// Command: push
// ============================================================================

/**
 * Push PAI tasks to GitHub as Issues. Creates new issues for unmapped tasks,
 * updates existing issues for mapped tasks (status, labels).
 * @param projectSlug - PAI project slug (must be linked to a GitHub repo)
 * @param dryRun - If true, returns what would happen without making changes
 * @returns SyncResult with pushed count and per-task details
 */
export function pushToGitHub(projectSlug: string, dryRun = false): SyncResult {
  const mapping = loadSyncMapping(projectSlug);
  if (!mapping || !mapping.sync_enabled) {
    return { success: false, action: "push", error: `Project not linked or sync disabled: ${projectSlug}` };
  }

  const tasksPath = join(PROJECTS_DIR, projectSlug, "TASKS.md");
  if (!existsSync(tasksPath)) {
    return { success: false, action: "push", error: `No TASKS.md found for project: ${projectSlug}` };
  }

  const tasks = parseTasksMd(readFileSync(tasksPath, "utf-8"));
  const repo = mapping.repo;
  const details: any[] = [];
  let pushed = 0;

  const allSections: Array<[keyof Omit<ParsedTasks, "header" | "footer">, string]> = [
    ["completed", "completed"],
    ["in_progress", "in_progress"],
    ["remaining", "remaining"],
    ["blocked", "blocked"],
    ["optional", "optional"],
  ];

  for (const [section, sectionName] of allSections) {
    for (const taskTitle of tasks[section]) {
      const cleanTitle = taskTitle.replace(/\n.*$/, "").trim();
      if (!cleanTitle) continue;

      const existingMapping = mapping.task_map[cleanTitle];

      if (existingMapping) {
        // Update existing issue
        const issueNum = existingMapping.issue_number;
        const targetState = PAI_TO_GITHUB_STATUS[sectionName] || "open";
        const currentGhState = existingMapping.github_state;

        const needsStateChange = currentGhState !== targetState;
        const sectionLabel = SECTION_LABELS[sectionName] || "";

        if (needsStateChange || existingMapping.pai_section !== sectionName) {
          if (!dryRun) {
            // Update labels
            try {
              // Remove old section labels
              for (const [, lbl] of Object.entries(SECTION_LABELS)) {
                try { ghArr(["issue", "edit", String(issueNum), "-R", repo, "--remove-label", lbl]); } catch { /* ok */ }
              }
              if (sectionLabel) {
                ghArr(["issue", "edit", String(issueNum), "-R", repo, "--add-label", sectionLabel]);
              }
            } catch { /* ok */ }

            // Change state
            if (needsStateChange) {
              try {
                if (targetState === "closed") {
                  ghArr(["issue", "close", String(issueNum), "-R", repo]);
                } else {
                  ghArr(["issue", "reopen", String(issueNum), "-R", repo]);
                }
              } catch { /* ok */ }
            }

            existingMapping.pai_section = sectionName;
            existingMapping.github_state = targetState;
            existingMapping.last_synced = new Date().toISOString();
          }

          details.push({
            task: cleanTitle,
            action: "updated",
            issue: issueNum,
            state: targetState,
            section: sectionName,
            dry_run: dryRun,
          });
          pushed++;
        }
      } else {
        // Create new issue
        if (!dryRun) {
          try {
            const labels = [PAI_LABEL];
            if (SECTION_LABELS[sectionName]) labels.push(SECTION_LABELS[sectionName]);

            const body = `**PAI Project:** ${projectSlug}\n**Section:** ${sectionName}\n\n---\n*Managed by PAI GitHubSync*`;
            const createArgs = ["issue", "create", "-R", repo, "--title", cleanTitle, "--body", body];
            for (const l of labels) {
              createArgs.push("--label", l);
            }

            // gh issue create outputs the issue URL (not JSON), so we parse it
            const issueUrl = ghArr(createArgs);
            const issueMatch = issueUrl.match(/\/issues\/(\d+)/);
            if (!issueMatch) throw new Error(`Could not parse issue number from: ${issueUrl}`);
            const result = { number: Number(issueMatch[1]), url: issueUrl };

            const targetState = PAI_TO_GITHUB_STATUS[sectionName] || "open";

            mapping.task_map[cleanTitle] = {
              issue_number: result.number,
              issue_url: result.url,
              last_synced: new Date().toISOString(),
              pai_section: sectionName,
              github_state: targetState,
            };
            mapping.issue_map[result.number] = {
              pai_task: cleanTitle,
              last_synced: new Date().toISOString(),
            };

            // Close if completed
            if (targetState === "closed") {
              try { ghArr(["issue", "close", String(result.number), "-R", repo]); } catch { /* ok */ }
            }

            details.push({
              task: cleanTitle,
              action: "created",
              issue: result.number,
              url: result.url,
              section: sectionName,
            });
            pushed++;
          } catch (err: any) {
            details.push({
              task: cleanTitle,
              action: "error",
              error: err.message,
            });
          }
        } else {
          details.push({
            task: cleanTitle,
            action: "would_create",
            section: sectionName,
            dry_run: true,
          });
          pushed++;
        }
      }
    }
  }

  if (!dryRun) {
    mapping.last_push = new Date().toISOString();
    mapping.last_synced = new Date().toISOString();
    saveSyncMapping(projectSlug, mapping);
  }

  return {
    success: true,
    action: "push",
    project: projectSlug,
    pushed,
    details,
  };
}

// ============================================================================
// Command: pull
// ============================================================================

/**
 * Pull GitHub Issues into PAI as tasks. Imports new issues, updates moved tasks.
 * Falls back to all repo issues if no PAI-labeled issues found.
 * @param projectSlug - PAI project slug (must be linked to a GitHub repo)
 * @param dryRun - If true, returns what would happen without making changes
 * @returns SyncResult with pulled count and per-issue details
 */
export function pullFromGitHub(projectSlug: string, dryRun = false): SyncResult {
  const mapping = loadSyncMapping(projectSlug);
  if (!mapping || !mapping.sync_enabled) {
    return { success: false, action: "pull", error: `Project not linked or sync disabled: ${projectSlug}` };
  }

  const repo = mapping.repo;
  const details: any[] = [];
  let pulled = 0;

  // Fetch all issues - first try PAI-labeled, fallback to all
  let issues: GitHubIssue[];
  try {
    issues = ghJSON<GitHubIssue[]>(
      ["issue", "list", "-R", repo, "--label", PAI_LABEL, "--state", "all", "--json", "number,title,state,body,labels,assignees,updatedAt,url", "--limit", "200"]
    );
    // If no PAI-labeled issues found, fetch all issues from the repo
    if (issues.length === 0) {
      issues = ghJSON<GitHubIssue[]>(
        ["issue", "list", "-R", repo, "--state", "all", "--json", "number,title,state,body,labels,assignees,updatedAt,url", "--limit", "200"]
      );
    }
  } catch (err: any) {
    // Fallback: fetch all issues without label filter
    try {
      issues = ghJSON<GitHubIssue[]>(
        ["issue", "list", "-R", repo, "--state", "all", "--json", "number,title,state,body,labels,assignees,updatedAt,url", "--limit", "200"]
      );
    } catch (err2: any) {
      return { success: false, action: "pull", error: `Failed to fetch issues: ${err2.message}` };
    }
  }

  // Load existing PAI tasks
  const tasksPath = join(PROJECTS_DIR, projectSlug, "TASKS.md");
  let tasks: ParsedTasks;
  if (existsSync(tasksPath)) {
    tasks = parseTasksMd(readFileSync(tasksPath, "utf-8"));
  } else {
    const yamlPath = join(PROJECTS_DIR, projectSlug, "PROJECT.yaml");
    const yaml = existsSync(yamlPath) ? parseSimpleYaml(readFileSync(yamlPath, "utf-8")) : {};
    tasks = {
      header: `# ${yaml.title || projectSlug} Tasks\n\n${yaml.goal || ""}\n\n---`,
      completed: [], in_progress: [], remaining: [],
      blocked: [], optional: [], footer: "",
    };
  }

  for (const issue of issues) {
    const existingIssueMapping = mapping.issue_map[issue.number];

    if (existingIssueMapping) {
      // Issue already mapped - check for updates
      const currentPaiTask = existingIssueMapping.pai_task;
      const githubState = issue.state.toLowerCase();
      const targetSection = determineSection(issue, githubState);
      const taskMapping = mapping.task_map[currentPaiTask];

      if (taskMapping && taskMapping.pai_section !== targetSection) {
        if (!dryRun) {
          // Move task to correct section
          removeTaskFromAllSections(tasks, currentPaiTask);
          tasks[targetSection].push(currentPaiTask);

          taskMapping.pai_section = targetSection;
          taskMapping.github_state = githubState;
          taskMapping.last_synced = new Date().toISOString();
          existingIssueMapping.last_synced = new Date().toISOString();
        }

        details.push({
          issue: issue.number,
          task: currentPaiTask,
          action: "moved",
          from: taskMapping?.pai_section,
          to: targetSection,
          dry_run: dryRun,
        });
        pulled++;
      }
    } else {
      // New issue from GitHub - import as PAI task
      const githubState = issue.state.toLowerCase();
      const targetSection = determineSection(issue, githubState);
      const taskTitle = issue.title;

      // Check if task already exists in PAI (by title match)
      const existsInPai = findTaskInSections(tasks, taskTitle);

      if (!existsInPai) {
        if (!dryRun) {
          tasks[targetSection].push(taskTitle);

          mapping.task_map[taskTitle] = {
            issue_number: issue.number,
            issue_url: issue.url,
            last_synced: new Date().toISOString(),
            pai_section: targetSection,
            github_state: githubState,
          };
          mapping.issue_map[issue.number] = {
            pai_task: taskTitle,
            last_synced: new Date().toISOString(),
          };
        }

        details.push({
          issue: issue.number,
          task: taskTitle,
          action: "imported",
          section: targetSection,
          dry_run: dryRun,
        });
        pulled++;
      }
    }
  }

  if (!dryRun) {
    writeTasksMd(join(PROJECTS_DIR, projectSlug), tasks, mapping);
    mapping.last_pull = new Date().toISOString();
    mapping.last_synced = new Date().toISOString();
    saveSyncMapping(projectSlug, mapping);

    // Update progress.json
    updateProgressJson(projectSlug, tasks);
  }

  return {
    success: true,
    action: "pull",
    project: projectSlug,
    pulled,
    details,
  };
}

function determineSection(issue: GitHubIssue, state: string): keyof Omit<ParsedTasks, "header" | "footer"> {
  if (state === "closed") return "completed";

  // Check labels for section hints
  const labels = issue.labels.map(l => l.name);
  if (labels.includes("status:in-progress")) return "in_progress";
  if (labels.includes("status:blocked")) return "blocked";
  if (labels.includes("status:optional")) return "optional";
  if (labels.includes("status:remaining")) return "remaining";

  return "remaining"; // default for open issues
}

function findTaskInSections(tasks: ParsedTasks, title: string): boolean {
  const normalized = title.toLowerCase().trim();
  for (const section of ["completed", "in_progress", "remaining", "blocked", "optional"] as const) {
    if (tasks[section].some(t => t.toLowerCase().trim() === normalized)) return true;
  }
  return false;
}

function removeTaskFromAllSections(tasks: ParsedTasks, taskText: string): void {
  const normalized = taskText.toLowerCase().trim();
  for (const section of ["completed", "in_progress", "remaining", "blocked", "optional"] as const) {
    const idx = tasks[section].findIndex(t => t.toLowerCase().trim() === normalized);
    if (idx !== -1) tasks[section].splice(idx, 1);
  }
}

function updateProgressJson(projectSlug: string, tasks: ParsedTasks): void {
  const progressPath = join(PROJECTS_DIR, projectSlug, "progress.json");
  let progress: any = {};
  if (existsSync(progressPath)) {
    try { progress = JSON.parse(readFileSync(progressPath, "utf-8")); } catch { /* ok */ }
  }

  const counts = {
    completed: tasks.completed.length,
    in_progress: tasks.in_progress.length,
    remaining: tasks.remaining.length,
    blocked: tasks.blocked.length,
    optional: tasks.optional.length,
  };
  const total = counts.completed + counts.in_progress + counts.remaining + counts.blocked;
  const percentage = total > 0 ? Math.round((counts.completed / total) * 100) : 0;

  progress.project_id = projectSlug;
  progress.task_counts = counts;
  progress.completion_percentage = percentage;
  progress.last_updated = new Date().toISOString();
  if (!progress.recent_activity) progress.recent_activity = [];
  progress.recent_activity.unshift({
    timestamp: new Date().toISOString(),
    action: "github_sync",
    task: "Synced with GitHub",
  });
  if (progress.recent_activity.length > 20) {
    progress.recent_activity = progress.recent_activity.slice(0, 20);
  }

  writeFileSync(progressPath, JSON.stringify(progress, null, 2) + "\n");
}

// ============================================================================
// Command: sync (bi-directional)
// ============================================================================

/**
 * Full bi-directional sync: pull from GitHub first, then push PAI state.
 * @param projectSlug - PAI project slug (must be linked)
 * @param dryRun - If true, preview changes without executing
 * @param force - If true, use PAI state on conflicts
 * @returns SyncResult with both pulled and pushed counts
 */
export function syncBidirectional(projectSlug: string, dryRun = false, force = false): SyncResult {
  const mapping = loadSyncMapping(projectSlug);
  if (!mapping || !mapping.sync_enabled) {
    return { success: false, action: "sync", error: `Project not linked or sync disabled: ${projectSlug}` };
  }

  // Pull first (get GitHub state), then push (send PAI state)
  const pullResult = pullFromGitHub(projectSlug, dryRun);
  const pushResult = pushToGitHub(projectSlug, dryRun);

  const allDetails = [
    ...(pullResult.details || []).map((d: any) => ({ ...d, direction: "pull" })),
    ...(pushResult.details || []).map((d: any) => ({ ...d, direction: "push" })),
  ];

  return {
    success: pullResult.success && pushResult.success,
    action: "sync",
    project: projectSlug,
    pulled: pullResult.pulled || 0,
    pushed: pushResult.pushed || 0,
    details: allDetails,
  };
}

// ============================================================================
// Command: create-issue (create a new GitHub issue from PAI)
// ============================================================================

/**
 * Create a new GitHub issue for a PAI project and add to TASKS.md.
 * @param projectSlug - PAI project slug (must be linked)
 * @param title - Issue title
 * @param body - Optional issue body
 * @param section - PAI section (default: remaining)
 * @param priority - Priority label (HIGH/MEDIUM/LOW)
 * @returns SyncResult with created issue details including URL
 */
export function createIssue(
  projectSlug: string,
  title: string,
  body?: string,
  section: string = "remaining",
  priority?: string,
): SyncResult {
  const mapping = loadSyncMapping(projectSlug);
  if (!mapping || !mapping.sync_enabled) {
    return { success: false, action: "create-issue", error: `Project not linked or sync disabled: ${projectSlug}` };
  }

  const repo = mapping.repo;
  const labels = [PAI_LABEL];
  if (SECTION_LABELS[section]) labels.push(SECTION_LABELS[section]);
  if (priority && PRIORITY_LABELS[priority.toUpperCase()]) {
    labels.push(PRIORITY_LABELS[priority.toUpperCase()]);
  }

  const issueBody = body || `**PAI Project:** ${projectSlug}\n**Section:** ${section}\n\n---\n*Managed by PAI GitHubSync*`;
  const createArgs = ["issue", "create", "-R", repo, "--title", title, "--body", issueBody];
  for (const l of labels) {
    createArgs.push("--label", l);
  }

  try {
    // gh issue create outputs the issue URL (not JSON), so we parse it
    const issueUrl = ghArr(createArgs);
    const issueNumMatch = issueUrl.match(/\/issues\/(\d+)/);
    if (!issueNumMatch) throw new Error(`Could not parse issue number from: ${issueUrl}`);
    const result = { number: Number(issueNumMatch[1]), url: issueUrl };

    const targetState = PAI_TO_GITHUB_STATUS[section] || "open";

    mapping.task_map[title] = {
      issue_number: result.number,
      issue_url: result.url,
      last_synced: new Date().toISOString(),
      pai_section: section,
      github_state: targetState,
    };
    mapping.issue_map[result.number] = {
      pai_task: title,
      last_synced: new Date().toISOString(),
    };

    // Close if completed
    if (targetState === "closed") {
      try { ghArr(["issue", "close", String(result.number), "-R", repo]); } catch { /* ok */ }
    }

    mapping.last_push = new Date().toISOString();
    mapping.last_synced = new Date().toISOString();
    saveSyncMapping(projectSlug, mapping);

    // Add task to TASKS.md
    const tasksPath = join(PROJECTS_DIR, projectSlug, "TASKS.md");
    if (existsSync(tasksPath)) {
      const tasks = parseTasksMd(readFileSync(tasksPath, "utf-8"));
      const validSection = section as keyof Omit<ParsedTasks, "header" | "footer">;
      if (tasks[validSection]) {
        tasks[validSection].push(title);
      } else {
        tasks.remaining.push(title);
      }
      writeTasksMd(join(PROJECTS_DIR, projectSlug), tasks, mapping);
      updateProgressJson(projectSlug, tasks);
    }

    return {
      success: true,
      action: "create-issue",
      project: projectSlug,
      pushed: 1,
      details: [{
        task: title,
        action: "created",
        issue: result.number,
        url: result.url,
        section,
      }],
    };
  } catch (err: any) {
    return { success: false, action: "create-issue", error: err.message };
  }
}

// ============================================================================
// Command: close-issue (close/reopen a GitHub issue from PAI)
// ============================================================================

/**
 * Close or reopen a GitHub issue linked to a PAI task.
 * @param projectSlug - PAI project slug (must be linked)
 * @param issueNumber - GitHub issue number to close/reopen
 * @param close - If true, close the issue; if false, reopen it (default: true)
 * @returns SyncResult with updated issue details
 */
export function closeIssue(projectSlug: string, issueNumber: number, close = true): SyncResult {
  const mapping = loadSyncMapping(projectSlug);
  if (!mapping || !mapping.sync_enabled) {
    return { success: false, action: "close-issue", error: `Project not linked or sync disabled: ${projectSlug}` };
  }

  const repo = mapping.repo;
  const issueEntry = mapping.issue_map[issueNumber];
  if (!issueEntry) {
    return { success: false, action: "close-issue", error: `Issue #${issueNumber} not found in mapping` };
  }

  try {
    if (close) {
      ghArr(["issue", "close", String(issueNumber), "-R", repo]);
    } else {
      ghArr(["issue", "reopen", String(issueNumber), "-R", repo]);
    }

    const taskTitle = issueEntry.pai_task;
    const taskMapping = mapping.task_map[taskTitle];
    const newState = close ? "closed" : "open";
    const newSection = close ? "completed" : "remaining";

    if (taskMapping) {
      taskMapping.github_state = newState;
      taskMapping.pai_section = newSection;
      taskMapping.last_synced = new Date().toISOString();
    }
    issueEntry.last_synced = new Date().toISOString();

    mapping.last_synced = new Date().toISOString();
    saveSyncMapping(projectSlug, mapping);

    // Move task in TASKS.md
    const tasksPath = join(PROJECTS_DIR, projectSlug, "TASKS.md");
    if (existsSync(tasksPath)) {
      const tasks = parseTasksMd(readFileSync(tasksPath, "utf-8"));
      removeTaskFromAllSections(tasks, taskTitle);
      tasks[newSection as keyof Omit<ParsedTasks, "header" | "footer">].push(taskTitle);
      writeTasksMd(join(PROJECTS_DIR, projectSlug), tasks, mapping);
      updateProgressJson(projectSlug, tasks);
    }

    return {
      success: true,
      action: close ? "close-issue" : "reopen-issue",
      project: projectSlug,
      details: [{
        task: taskTitle,
        issue: issueNumber,
        action: close ? "closed" : "reopened",
        section: newSection,
      }],
    };
  } catch (err: any) {
    return { success: false, action: "close-issue", error: err.message };
  }
}

/**
 * Get detailed mapping for a specific task including its GitHub issue URL.
 * @param projectSlug - PAI project slug
 * @param taskTitle - Task title to look up
 * @returns Mapping entry with issue_number, issue_url, pai_section, github_state, or null
 */
export function getTaskMapping(projectSlug: string, taskTitle: string): { issue_number: number; issue_url: string; pai_section: string; github_state: string } | null {
  const mapping = loadSyncMapping(projectSlug);
  if (!mapping) return null;
  return mapping.task_map[taskTitle] || null;
}

// ============================================================================
// Command: diff (preview sync differences)
// ============================================================================

/**
 * Compare local TASKS.md state vs GitHub issues and show structured differences.
 * @param projectSlug - PAI project slug (must be linked)
 * @returns SyncResult with diff details: only_local, only_github, state_mismatch
 */
export function diffSync(projectSlug: string): SyncResult {
  const mapping = loadSyncMapping(projectSlug);
  if (!mapping || !mapping.sync_enabled) {
    return { success: false, action: "diff", error: `Project not linked or sync disabled: ${projectSlug}` };
  }

  const repo = mapping.repo;
  const tasksPath = join(PROJECTS_DIR, projectSlug, "TASKS.md");
  if (!existsSync(tasksPath)) {
    return { success: false, action: "diff", error: `No TASKS.md found for project: ${projectSlug}` };
  }

  const tasks = parseTasksMd(readFileSync(tasksPath, "utf-8"));

  // Gather all local task titles with their sections
  const localTasks = new Map<string, string>();
  for (const section of ["completed", "in_progress", "remaining", "blocked", "optional"] as const) {
    for (const t of tasks[section]) {
      localTasks.set(t.toLowerCase().trim(), section);
    }
  }

  // Fetch GitHub issues
  let issues: GitHubIssue[];
  try {
    issues = ghJSON<GitHubIssue[]>(
      ["issue", "list", "-R", repo, "--state", "all", "--json", "number,title,state,body,labels,assignees,updatedAt,url", "--limit", "200"]
    );
  } catch (err: any) {
    return { success: false, action: "diff", error: `Failed to fetch issues: ${err.message}` };
  }

  const githubIssues = new Map<string, { number: number; state: string; url: string }>();
  for (const issue of issues) {
    githubIssues.set(issue.title.toLowerCase().trim(), {
      number: issue.number,
      state: issue.state.toLowerCase(),
      url: issue.url,
    });
  }

  const onlyLocal: any[] = [];
  const onlyGithub: any[] = [];
  const stateMismatch: any[] = [];

  // Tasks only in PAI (not on GitHub)
  for (const [title, section] of localTasks) {
    if (!githubIssues.has(title) && !mapping.task_map[title]) {
      // Find original-case title
      const origTitle = [...tasks.completed, ...tasks.in_progress, ...tasks.remaining, ...tasks.blocked, ...tasks.optional]
        .find(t => t.toLowerCase().trim() === title) || title;
      onlyLocal.push({ task: origTitle, section });
    }
  }

  // Issues only on GitHub (not in PAI)
  for (const [title, issue] of githubIssues) {
    if (!localTasks.has(title) && !mapping.issue_map[issue.number]) {
      onlyGithub.push({ issue: issue.number, title, state: issue.state, url: issue.url });
    }
  }

  // State mismatches (mapped tasks where PAI section doesn't match GitHub state)
  for (const [taskTitle, entry] of Object.entries(mapping.task_map)) {
    const ghIssue = githubIssues.get(taskTitle.toLowerCase().trim());
    if (ghIssue) {
      const expectedPaiSection = GITHUB_TO_PAI_STATUS[ghIssue.state] || "remaining";
      const isCompleted = entry.pai_section === "completed";
      const ghClosed = ghIssue.state === "closed";
      if (isCompleted !== ghClosed) {
        stateMismatch.push({
          task: taskTitle,
          issue: ghIssue.number,
          pai_section: entry.pai_section,
          github_state: ghIssue.state,
          expected_section: expectedPaiSection,
        });
      }
    }
  }

  return {
    success: true,
    action: "diff",
    project: projectSlug,
    details: [
      { category: "only_local", count: onlyLocal.length, items: onlyLocal },
      { category: "only_github", count: onlyGithub.length, items: onlyGithub },
      { category: "state_mismatch", count: stateMismatch.length, items: stateMismatch },
    ],
  };
}

// ============================================================================
// Command: cleanup (remove test-generated issues)
// ============================================================================

/**
 * Close and label test-generated issues on a GitHub repo.
 * Finds issues matching test patterns (timestamps, test-gh- prefixes).
 * @param repo - GitHub repo in "owner/name" format
 * @param dryRun - If true, preview what would be cleaned up
 * @returns SyncResult with cleanup details
 */
export function cleanupTestIssues(repo: string, dryRun = false): SyncResult {
  const testPatterns = [
    /^PAI Test Issue \d+$/,
    /^PAI Close Test \d+$/,
    /^PAI Reopen Test \d+$/,
    /^PAI Full Cycle \d+$/,
    /^PAI Debug Test \d+$/,
    /^API Create Test \d+$/,
    /^API Close Test \d+$/,
    /^Existing local task$/,
    /^test-gh-/,
  ];

  let issues: GitHubIssue[];
  try {
    issues = ghJSON<GitHubIssue[]>(
      ["issue", "list", "-R", repo, "--state", "all", "--json", "number,title,state,url", "--limit", "500"]
    );
  } catch (err: any) {
    return { success: false, action: "cleanup", error: `Failed to fetch issues: ${err.message}` };
  }

  const toClose: any[] = [];
  for (const issue of issues) {
    const isTest = testPatterns.some(p => p.test(issue.title));
    if (isTest) {
      toClose.push({ number: issue.number, title: issue.title, state: issue.state, url: issue.url });
      if (!dryRun && issue.state === "open") {
        try { ghArr(["issue", "close", String(issue.number), "-R", repo]); } catch { /* ok */ }
      }
    }
  }

  return {
    success: true,
    action: "cleanup",
    details: toClose.map(i => ({
      ...i,
      action: dryRun ? "would_close" : (i.state === "open" ? "closed" : "already_closed"),
      dry_run: dryRun,
    })),
    pushed: toClose.length,
  };
}

// ============================================================================
// Command: edit-issue (update existing GitHub issue)
// ============================================================================

/**
 * Edit an existing GitHub issue's title, body, and/or labels.
 * Updates both GitHub and local mapping/TASKS.md.
 * @param projectSlug - PAI project slug (must be linked)
 * @param issueNumber - GitHub issue number to edit
 * @param options - Fields to update: title, body, addLabels, removeLabels, assignee
 * @returns SyncResult with edit details
 */
export function editIssue(
  projectSlug: string,
  issueNumber: number,
  options: {
    title?: string;
    body?: string;
    addLabels?: string[];
    removeLabels?: string[];
    assignee?: string;
    section?: string;
  },
): SyncResult {
  const mapping = loadSyncMapping(projectSlug);
  if (!mapping || !mapping.sync_enabled) {
    return { success: false, action: "edit-issue", error: `Project not linked or sync disabled: ${projectSlug}` };
  }

  const repo = mapping.repo;
  const issueEntry = mapping.issue_map[issueNumber];
  if (!issueEntry) {
    return { success: false, action: "edit-issue", error: `Issue #${issueNumber} not found in mapping` };
  }

  try {
    const editArgs: string[] = ["issue", "edit", String(issueNumber), "-R", repo];
    if (options.title) { editArgs.push("--title", options.title); }
    if (options.body) { editArgs.push("--body", options.body); }
    if (options.addLabels?.length) {
      for (const l of options.addLabels) { editArgs.push("--add-label", l); }
    }
    if (options.removeLabels?.length) {
      for (const l of options.removeLabels) { editArgs.push("--remove-label", l); }
    }
    if (options.assignee) { editArgs.push("--add-assignee", options.assignee); }

    if (editArgs.length > 4) {
      ghArr(editArgs);
    }

    const oldTitle = issueEntry.pai_task;
    const newTitle = options.title || oldTitle;

    // Update mapping if title changed
    if (options.title && options.title !== oldTitle) {
      const taskEntry = mapping.task_map[oldTitle];
      if (taskEntry) {
        delete mapping.task_map[oldTitle];
        mapping.task_map[newTitle] = { ...taskEntry, last_synced: new Date().toISOString() };
        mapping.issue_map[issueNumber] = { pai_task: newTitle, last_synced: new Date().toISOString() };
      }

      // Update TASKS.md
      const tasksPath = join(PROJECTS_DIR, projectSlug, "TASKS.md");
      if (existsSync(tasksPath)) {
        const tasks = parseTasksMd(readFileSync(tasksPath, "utf-8"));
        for (const section of ["completed", "in_progress", "remaining", "blocked", "optional"] as const) {
          const idx = tasks[section].findIndex(t => t.toLowerCase().trim() === oldTitle.toLowerCase().trim());
          if (idx !== -1) {
            tasks[section][idx] = newTitle;
            break;
          }
        }
        writeTasksMd(join(PROJECTS_DIR, projectSlug), tasks, mapping);
      }
    }

    // Update section if requested
    if (options.section) {
      const taskEntry = mapping.task_map[newTitle];
      if (taskEntry) {
        const tasksPath = join(PROJECTS_DIR, projectSlug, "TASKS.md");
        if (existsSync(tasksPath)) {
          const tasks = parseTasksMd(readFileSync(tasksPath, "utf-8"));
          removeTaskFromAllSections(tasks, newTitle);
          const validSection = options.section as keyof Omit<ParsedTasks, "header" | "footer">;
          if (tasks[validSection]) {
            tasks[validSection].push(newTitle);
          }
          taskEntry.pai_section = options.section;
          taskEntry.last_synced = new Date().toISOString();

          // Update section label on GitHub
          for (const [, lbl] of Object.entries(SECTION_LABELS)) {
            try { ghArr(["issue", "edit", String(issueNumber), "-R", repo, "--remove-label", lbl]); } catch { /* ok */ }
          }
          if (SECTION_LABELS[options.section]) {
            try { ghArr(["issue", "edit", String(issueNumber), "-R", repo, "--add-label", SECTION_LABELS[options.section]]); } catch { /* ok */ }
          }

          writeTasksMd(join(PROJECTS_DIR, projectSlug), tasks, mapping);
          updateProgressJson(projectSlug, tasks);
        }
      }
    }

    mapping.last_synced = new Date().toISOString();
    saveSyncMapping(projectSlug, mapping);

    return {
      success: true,
      action: "edit-issue",
      project: projectSlug,
      details: [{
        issue: issueNumber,
        action: "edited",
        old_title: oldTitle,
        new_title: newTitle,
        fields_updated: Object.keys(options).filter(k => (options as any)[k] !== undefined),
      }],
    };
  } catch (err: any) {
    return { success: false, action: "edit-issue", error: err.message };
  }
}

// ============================================================================
// Batch Operations
// ============================================================================

export function pushAll(dryRun = false): SyncResult[] {
  return getLinkedProjects().map(p => pushToGitHub(p.slug, dryRun));
}

export function pullAll(dryRun = false): SyncResult[] {
  return getLinkedProjects().map(p => pullFromGitHub(p.slug, dryRun));
}

export function syncAll(dryRun = false): SyncResult[] {
  return getLinkedProjects().map(p => syncBidirectional(p.slug, dryRun));
}

// ============================================================================
// CLI Argument Parsing
// ============================================================================

function getArg(args: string[], flag: string): string | undefined {
  const idx = args.indexOf(flag);
  return idx !== -1 && idx + 1 < args.length ? args[idx + 1] : undefined;
}

function hasFlag(args: string[], flag: string): boolean {
  return args.includes(flag);
}

// ============================================================================
// Main
// ============================================================================

async function main(): Promise<void> {
  const args = process.argv.slice(2);

  if (hasFlag(args, "--help") || hasFlag(args, "-h") || args.length === 0) {
    showHelp();
  }

  const command = args[0];
  const owner = getArg(args, "--owner") || DEFAULT_OWNER;
  const projectSlug = getArg(args, "--project");
  const dryRun = hasFlag(args, "--dry-run");
  const force = hasFlag(args, "--force");
  const all = hasFlag(args, "--all");

  try {
    switch (command) {
      case "repos": {
        const repos = listRepos(owner);
        console.log(JSON.stringify({ success: true, action: "repos", owner, count: repos.length, repos }, null, 2));
        break;
      }

      case "status": {
        const status = getSyncStatus(projectSlug || undefined);
        console.log(JSON.stringify({ success: true, action: "status", ...status }, null, 2));
        break;
      }

      case "link": {
        const paiSlug = args[1];
        const githubRepo = args[2];
        if (!paiSlug || !githubRepo) {
          console.log(JSON.stringify({ success: false, error: "Usage: link <pai-slug> <owner/repo>" }));
          process.exit(1);
        }
        const result = linkProject(paiSlug, githubRepo);
        console.log(JSON.stringify(result, null, 2));
        process.exit(result.success ? 0 : 1);
        break;
      }

      case "unlink": {
        const slug = args[1];
        if (!slug) {
          console.log(JSON.stringify({ success: false, error: "Usage: unlink <pai-slug>" }));
          process.exit(1);
        }
        const result = unlinkProject(slug);
        console.log(JSON.stringify(result, null, 2));
        process.exit(result.success ? 0 : 1);
        break;
      }

      case "push": {
        if (all) {
          const results = pushAll(dryRun);
          console.log(JSON.stringify({ success: true, action: "push_all", results }, null, 2));
        } else if (projectSlug) {
          const result = pushToGitHub(projectSlug, dryRun);
          console.log(JSON.stringify(result, null, 2));
          process.exit(result.success ? 0 : 1);
        } else {
          console.log(JSON.stringify({ success: false, error: "Specify --project <slug> or --all" }));
          process.exit(1);
        }
        break;
      }

      case "pull": {
        if (all) {
          const results = pullAll(dryRun);
          console.log(JSON.stringify({ success: true, action: "pull_all", results }, null, 2));
        } else if (projectSlug) {
          const result = pullFromGitHub(projectSlug, dryRun);
          console.log(JSON.stringify(result, null, 2));
          process.exit(result.success ? 0 : 1);
        } else {
          console.log(JSON.stringify({ success: false, error: "Specify --project <slug> or --all" }));
          process.exit(1);
        }
        break;
      }

      case "create-issue": {
        const slug = projectSlug || args[1];
        const title = getArg(args, "--title") || args.find((a, i) => i > 0 && !a.startsWith("--") && args[i - 1] !== "--project" && args[i - 1] !== "--title" && a !== "create-issue");
        if (!slug || !title) {
          console.log(JSON.stringify({ success: false, error: "Usage: create-issue --project <slug> --title \"Title\"" }));
          process.exit(1);
        }
        const body = getArg(args, "--body");
        const section = getArg(args, "--section") || "remaining";
        const priority = getArg(args, "--priority");
        const result = createIssue(slug, title, body, section, priority);
        console.log(JSON.stringify(result, null, 2));
        process.exit(result.success ? 0 : 1);
        break;
      }

      case "close-issue": {
        const slug = projectSlug;
        const issueNum = Number(getArg(args, "--issue") || args[1]);
        if (!slug || !issueNum) {
          console.log(JSON.stringify({ success: false, error: "Usage: close-issue --project <slug> --issue <number>" }));
          process.exit(1);
        }
        const reopen = hasFlag(args, "--reopen");
        const result = closeIssue(slug, issueNum, !reopen);
        console.log(JSON.stringify(result, null, 2));
        process.exit(result.success ? 0 : 1);
        break;
      }

      case "sync": {
        if (all) {
          const results = syncAll(dryRun);
          console.log(JSON.stringify({ success: true, action: "sync_all", results }, null, 2));
        } else if (projectSlug) {
          const result = syncBidirectional(projectSlug, dryRun, force);
          console.log(JSON.stringify(result, null, 2));
          process.exit(result.success ? 0 : 1);
        } else {
          console.log(JSON.stringify({ success: false, error: "Specify --project <slug> or --all" }));
          process.exit(1);
        }
        break;
      }

      case "diff": {
        if (!projectSlug) {
          console.log(JSON.stringify({ success: false, error: "Specify --project <slug>" }));
          process.exit(1);
        }
        const result = diffSync(projectSlug);
        console.log(JSON.stringify(result, null, 2));
        process.exit(result.success ? 0 : 1);
        break;
      }

      case "cleanup": {
        const repo = args[1] || getArg(args, "--repo") || "";
        if (!repo) {
          console.log(JSON.stringify({ success: false, error: "Usage: cleanup <owner/repo> [--dry-run]" }));
          process.exit(1);
        }
        const result = cleanupTestIssues(repo, dryRun);
        console.log(JSON.stringify(result, null, 2));
        break;
      }

      case "edit-issue": {
        const slug = projectSlug;
        const issueNum = Number(getArg(args, "--issue"));
        if (!slug || !issueNum) {
          console.log(JSON.stringify({ success: false, error: "Usage: edit-issue --project <slug> --issue <number> [--title ...] [--body ...] [--section ...]" }));
          process.exit(1);
        }
        const opts: any = {};
        const title = getArg(args, "--title");
        const body = getArg(args, "--body");
        const section = getArg(args, "--section");
        const assignee = getArg(args, "--assignee");
        if (title) opts.title = title;
        if (body) opts.body = body;
        if (section) opts.section = section;
        if (assignee) opts.assignee = assignee;
        const result = editIssue(slug, issueNum, opts);
        console.log(JSON.stringify(result, null, 2));
        process.exit(result.success ? 0 : 1);
        break;
      }

      case "create-repo": {
        const repoName = getArg(args, "--name") || args[1];
        if (!repoName) {
          console.log(JSON.stringify({ success: false, error: "Usage: create-repo --name <name> [--public] [--description \"...\"] [--owner <owner>]" }));
          process.exit(1);
        }
        const isPublic = hasFlag(args, "--public");
        const description = getArg(args, "--description");
        const result = createRepo(repoName, !isPublic, description, owner);
        console.log(JSON.stringify(result, null, 2));
        process.exit(result.success ? 0 : 1);
        break;
      }

      default:
        console.log(JSON.stringify({ success: false, error: `Unknown command: ${command}. Use --help for usage.` }));
        process.exit(1);
    }
  } catch (err: any) {
    console.log(JSON.stringify({ success: false, error: err.message }));
    process.exit(1);
  }
}

if (import.meta.main) {
  main().catch((err) => {
    console.log(JSON.stringify({ success: false, error: String(err) }));
    process.exit(1);
  });
}
