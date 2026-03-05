#!/usr/bin/env bun
/**
 * ListProjects.ts - List all bounded projects with status summary
 *
 * Scans MEMORY/STATE/projects/ for project directories and displays
 * them with filtering, sorting, and multiple output formats.
 *
 * Usage:
 *   bun ~/.claude/skills/PAI/Tools/ListProjects.ts [options]
 *   bun ~/.claude/skills/PAI/Tools/ListProjects.ts --help
 *
 * @author PAI System
 * @version 1.0.0
 */

import { existsSync, readdirSync, readFileSync } from "fs";
import { join } from "path";
import { homedir } from "os";
import { parseSimpleYaml } from "./YamlUtils.ts";

// ============================================================================
// Constants
// ============================================================================

const HOME = process.env.HOME || homedir();
const PAI_DIR = process.env.PAI_DIR || join(HOME, ".claude");
const PROJECTS_DIR = join(PAI_DIR, "MEMORY", "STATE", "projects");

import { type ProjectStatus, type Priority, VALID_PROJECT_STATUSES } from "./DataModels.ts";
type OutputFormat = "json" | "table" | "summary";
type SortField = "created" | "priority" | "status" | "completion";

interface ProjectInfo {
  id: string;
  title: string;
  status: ProjectStatus;
  created: string;
  goal: string;
  target?: string;
  priority: Priority;
  parent_role?: string;
  success_criteria: string[];
  tags: string[];
  task_counts?: {
    completed: number;
    in_progress: number;
    remaining: number;
    blocked: number;
    optional: number;
  };
  completion_percentage: number;
  last_updated?: string;
}

// ============================================================================
// Help
// ============================================================================

function showHelp(): void {
  console.log(`
ListProjects - List all bounded projects with status summary

USAGE:
  bun ~/.claude/skills/PAI/Tools/ListProjects.ts [options]

OPTIONS:
  --status STATUS          Filter by project status (PLANNING, IN_PROGRESS, COMPLETED, PAUSED, BLOCKED)
  --format json|table|summary  Output format (default: json)
  --sort created|priority|status|completion  Sort order (default: created)
  --verbose                Include full task counts and recent activity
  --help, -h               Show this help message

EXAMPLES:
  bun ~/.claude/skills/PAI/Tools/ListProjects.ts                       # All projects (JSON)
  bun ~/.claude/skills/PAI/Tools/ListProjects.ts --status IN_PROGRESS  # Filter by status
  bun ~/.claude/skills/PAI/Tools/ListProjects.ts --format table        # Human-readable table
  bun ~/.claude/skills/PAI/Tools/ListProjects.ts --format summary      # One-line per project
  bun ~/.claude/skills/PAI/Tools/ListProjects.ts --sort priority       # Sort by priority

OUTPUT:
  JSON array of project objects (default)
  Human-readable table (--format table)
  One-line summary per project (--format summary)
`);
  process.exit(0);
}

// ============================================================================
// YAML Parsing
// ============================================================================



// ============================================================================
// Core Functions
// ============================================================================

function loadProject(slug: string): ProjectInfo | null {
  const projectDir = join(PROJECTS_DIR, slug);
  const yamlPath = join(projectDir, "PROJECT.yaml");
  const progressPath = join(projectDir, "progress.json");

  if (!existsSync(yamlPath)) return null;

  try {
    const yamlContent = readFileSync(yamlPath, "utf-8");
    const yaml = parseSimpleYaml(yamlContent);

    let progress: any = {};
    if (existsSync(progressPath)) {
      try {
        progress = JSON.parse(readFileSync(progressPath, "utf-8"));
      } catch {
        // Ignore invalid progress.json
      }
    }

    return {
      id: yaml.id || slug,
      title: yaml.title || slug,
      status: (yaml.status || "PLANNING") as ProjectStatus,
      created: yaml.created || "unknown",
      goal: yaml.goal || "",
      target: yaml.target || undefined,
      priority: (yaml.priority || "MEDIUM") as Priority,
      parent_role: yaml.parent_role || undefined,
      success_criteria: Array.isArray(yaml.success_criteria) ? yaml.success_criteria : [],
      tags: Array.isArray(yaml.tags) ? yaml.tags : [],
      task_counts: progress.task_counts || undefined,
      completion_percentage: progress.completion_percentage || 0,
      last_updated: progress.last_updated || undefined,
    };
  } catch {
    return null;
  }
}

export function listProjects(options: {
  status?: ProjectStatus;
  sort?: SortField;
  verbose?: boolean;
}): ProjectInfo[] {
  if (!existsSync(PROJECTS_DIR)) return [];

  const slugs = readdirSync(PROJECTS_DIR, { withFileTypes: true })
    .filter(e => e.isDirectory())
    .map(e => e.name);

  let projects = slugs
    .map(slug => loadProject(slug))
    .filter((p): p is ProjectInfo => p !== null);

  // Apply status filter
  if (options.status) {
    projects = projects.filter(p => p.status === options.status);
  }

  // Apply sorting
  const sortField = options.sort || "created";
  const priorityOrder: Record<string, number> = { HIGH: 0, MEDIUM: 1, LOW: 2 };
  const statusOrder: Record<string, number> = { BLOCKED: 0, IN_PROGRESS: 1, PLANNING: 2, PAUSED: 3, COMPLETED: 4 };

  projects.sort((a, b) => {
    switch (sortField) {
      case "priority":
        return (priorityOrder[a.priority] || 1) - (priorityOrder[b.priority] || 1);
      case "status":
        return (statusOrder[a.status] || 2) - (statusOrder[b.status] || 2);
      case "completion":
        return b.completion_percentage - a.completion_percentage;
      case "created":
      default:
        return a.created.localeCompare(b.created);
    }
  });

  // Strip verbose fields if not requested
  if (!options.verbose) {
    projects = projects.map(p => {
      const { task_counts, last_updated, ...rest } = p;
      return rest as ProjectInfo;
    });
  }

  return projects;
}

// ============================================================================
// Output Formatters
// ============================================================================

function formatTable(projects: ProjectInfo[]): string {
  if (projects.length === 0) return "No projects found.";

  const statusIcons: Record<string, string> = {
    PLANNING: "📋",
    IN_PROGRESS: "🔄",
    COMPLETED: "✅",
    PAUSED: "⏸️",
    BLOCKED: "🚫",
  };

  const lines: string[] = [];
  lines.push("  " + "Project".padEnd(22) + "Status".padEnd(16) + "Priority".padEnd(10) + "Completion".padEnd(12) + "Goal");
  lines.push("  " + "─".repeat(90));

  for (const p of projects) {
    const icon = statusIcons[p.status] || "❓";
    const completion = p.completion_percentage + "%";
    const goalTrunc = p.goal.length > 35 ? p.goal.slice(0, 32) + "..." : p.goal;
    lines.push(
      "  " +
      p.id.padEnd(22) +
      `${icon} ${p.status}`.padEnd(16) +
      p.priority.padEnd(10) +
      completion.padEnd(12) +
      goalTrunc
    );
  }

  lines.push("");
  lines.push(`  Total: ${projects.length} project(s)`);
  return lines.join("\n");
}

function formatSummary(projects: ProjectInfo[]): string {
  if (projects.length === 0) return "No projects found.";

  const statusIcons: Record<string, string> = {
    PLANNING: "📋",
    IN_PROGRESS: "🔄",
    COMPLETED: "✅",
    PAUSED: "⏸️",
    BLOCKED: "🚫",
  };

  return projects
    .map(p => `${statusIcons[p.status] || "❓"} ${p.id} — ${p.title} (${p.completion_percentage}%)`)
    .join("\n");
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

  if (hasFlag(args, "--help") || hasFlag(args, "-h")) {
    showHelp();
  }

  const statusRaw = getArg(args, "--status");
  const status = statusRaw ? statusRaw.toUpperCase() as ProjectStatus : undefined;
  if (status && !VALID_PROJECT_STATUSES.includes(status)) {
    console.log(JSON.stringify({ success: false, error: `Invalid status: ${statusRaw}` }));
    process.exit(1);
  }

  const format = (getArg(args, "--format") || "json") as OutputFormat;
  if (!["json", "table", "summary"].includes(format)) {
    console.log(JSON.stringify({ success: false, error: `Invalid format: ${format}. Must be json, table, or summary` }));
    process.exit(1);
  }

  const sort = (getArg(args, "--sort") || "created") as SortField;
  if (!["created", "priority", "status", "completion"].includes(sort)) {
    console.log(JSON.stringify({ success: false, error: `Invalid sort: ${sort}. Must be created, priority, status, or completion` }));
    process.exit(1);
  }

  const verbose = hasFlag(args, "--verbose");

  const projects = listProjects({ status, sort, verbose });

  switch (format) {
    case "table":
      console.log(formatTable(projects));
      break;
    case "summary":
      console.log(formatSummary(projects));
      break;
    case "json":
    default:
      console.log(JSON.stringify(projects, null, 2));
      break;
  }
}

if (import.meta.main) {
  main().catch((err) => {
    console.log(JSON.stringify({ success: false, error: String(err) }));
    process.exit(1);
  });
}
