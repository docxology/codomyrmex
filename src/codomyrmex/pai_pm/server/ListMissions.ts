#!/usr/bin/env bun
/**
 * ListMissions.ts - List all missions with status summary
 *
 * Scans MEMORY/STATE/missions/ for mission directories and displays
 * them with filtering, sorting, and multiple output formats.
 *
 * Usage:
 *   bun ~/.claude/skills/PAI/Tools/ListMissions.ts [options]
 *   bun ~/.claude/skills/PAI/Tools/ListMissions.ts --help
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
const MISSIONS_DIR = join(PAI_DIR, "MEMORY", "STATE", "missions");
const PROJECTS_DIR = join(PAI_DIR, "MEMORY", "STATE", "projects");

import { type MissionStatus, type Priority, VALID_MISSION_STATUSES } from "./DataModels.ts";
type OutputFormat = "json" | "table" | "summary";
type SortField = "created" | "priority" | "status" | "completion";

interface MissionInfo {
  id: string;
  title: string;
  status: MissionStatus;
  created: string;
  completed?: string;
  description: string;
  priority: Priority;
  parent_goal?: string;
  success_criteria: string[];
  linked_projects: string[];
  tags: string[];
  linked_project_count: number;
  aggregate_completion: number;
  last_updated?: string;
}

// ============================================================================
// Help
// ============================================================================

function showHelp(): void {
  console.log(`
ListMissions - List all missions with status summary

USAGE:
  bun ~/.claude/skills/PAI/Tools/ListMissions.ts [options]

OPTIONS:
  --status STATUS           Filter by mission status (ACTIVE, PAUSED, COMPLETED, ARCHIVED)
  --format json|table|summary  Output format (default: json)
  --sort created|priority|status|completion  Sort order (default: created)
  --verbose                 Include full details
  --help, -h                Show this help message

EXAMPLES:
  bun ~/.claude/skills/PAI/Tools/ListMissions.ts                     # All missions (JSON)
  bun ~/.claude/skills/PAI/Tools/ListMissions.ts --status ACTIVE     # Filter by status
  bun ~/.claude/skills/PAI/Tools/ListMissions.ts --format table      # Human-readable table
  bun ~/.claude/skills/PAI/Tools/ListMissions.ts --format summary    # One-line per mission
  bun ~/.claude/skills/PAI/Tools/ListMissions.ts --sort priority     # Sort by priority

OUTPUT:
  JSON array of mission objects (default)
  Human-readable table (--format table)
  One-line summary per mission (--format summary)
`);
  process.exit(0);
}

// ============================================================================
// YAML Parsing
// ============================================================================


// ============================================================================
// Core Functions
// ============================================================================

function loadMission(slug: string): MissionInfo | null {
  const missionDir = join(MISSIONS_DIR, slug);
  const yamlPath = join(missionDir, "MISSION.yaml");
  const progressPath = join(missionDir, "progress.json");

  if (!existsSync(yamlPath)) return null;

  try {
    const yamlContent = readFileSync(yamlPath, "utf-8");
    const yaml = parseSimpleYaml(yamlContent);

    let progress: any = {};
    if (existsSync(progressPath)) {
      try {
        progress = JSON.parse(readFileSync(progressPath, "utf-8"));
      } catch { /* ignore */ }
    }

    return {
      id: yaml.id || slug,
      title: yaml.title || slug,
      status: (yaml.status || "ACTIVE") as MissionStatus,
      created: yaml.created || "unknown",
      completed: yaml.completed || undefined,
      description: yaml.description || "",
      priority: (yaml.priority || "MEDIUM") as Priority,
      parent_goal: yaml.parent_goal || undefined,
      success_criteria: Array.isArray(yaml.success_criteria) ? yaml.success_criteria : [],
      linked_projects: Array.isArray(yaml.linked_projects) ? yaml.linked_projects : [],
      tags: Array.isArray(yaml.tags) ? yaml.tags : [],
      linked_project_count: progress.linked_project_count || 0,
      aggregate_completion: progress.aggregate_completion || 0,
      last_updated: progress.last_updated || undefined,
    };
  } catch {
    return null;
  }
}

export function listMissions(options: {
  status?: MissionStatus;
  sort?: SortField;
  verbose?: boolean;
}): MissionInfo[] {
  if (!existsSync(MISSIONS_DIR)) return [];

  const slugs = readdirSync(MISSIONS_DIR, { withFileTypes: true })
    .filter(e => e.isDirectory())
    .map(e => e.name);

  let missions = slugs
    .map(slug => loadMission(slug))
    .filter((m): m is MissionInfo => m !== null);

  // Apply status filter
  if (options.status) {
    missions = missions.filter(m => m.status === options.status);
  }

  // Apply sorting
  const sortField = options.sort || "created";
  const priorityOrder: Record<string, number> = { HIGH: 0, MEDIUM: 1, LOW: 2 };
  const statusOrder: Record<string, number> = { ACTIVE: 0, PAUSED: 1, ARCHIVED: 2, COMPLETED: 3 };

  missions.sort((a, b) => {
    switch (sortField) {
      case "priority":
        return (priorityOrder[a.priority] || 1) - (priorityOrder[b.priority] || 1);
      case "status":
        return (statusOrder[a.status] || 2) - (statusOrder[b.status] || 2);
      case "completion":
        return b.aggregate_completion - a.aggregate_completion;
      case "created":
      default:
        return a.created.localeCompare(b.created);
    }
  });

  // Strip verbose fields if not requested
  if (!options.verbose) {
    missions = missions.map(m => {
      const { last_updated, ...rest } = m;
      return rest as MissionInfo;
    });
  }

  return missions;
}

// ============================================================================
// Output Formatters
// ============================================================================

function formatTable(missions: MissionInfo[]): string {
  if (missions.length === 0) return "No missions found.";

  const statusIcons: Record<string, string> = {
    ACTIVE: "🚀",
    PAUSED: "⏸️",
    COMPLETED: "✅",
    ARCHIVED: "📦",
  };

  const lines: string[] = [];
  lines.push("  " + "Mission".padEnd(24) + "Status".padEnd(14) + "Priority".padEnd(10) + "Projects".padEnd(10) + "Completion".padEnd(12) + "Description");
  lines.push("  " + "─".repeat(100));

  for (const m of missions) {
    const icon = statusIcons[m.status] || "❓";
    const completion = m.aggregate_completion + "%";
    const projects = String(m.linked_projects.length);
    const descTrunc = m.description.length > 30 ? m.description.slice(0, 27) + "..." : m.description;
    lines.push(
      "  " +
      m.id.padEnd(24) +
      `${icon} ${m.status}`.padEnd(14) +
      m.priority.padEnd(10) +
      projects.padEnd(10) +
      completion.padEnd(12) +
      descTrunc
    );
  }

  lines.push("");
  lines.push(`  Total: ${missions.length} mission(s)`);
  return lines.join("\n");
}

function formatSummary(missions: MissionInfo[]): string {
  if (missions.length === 0) return "No missions found.";

  const statusIcons: Record<string, string> = {
    ACTIVE: "🚀",
    PAUSED: "⏸️",
    COMPLETED: "✅",
    ARCHIVED: "📦",
  };

  return missions
    .map(m => `${statusIcons[m.status] || "❓"} ${m.id} — ${m.title} [${m.linked_projects.length} projects, ${m.aggregate_completion}%]`)
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
  const status = statusRaw ? statusRaw.toUpperCase() as MissionStatus : undefined;
  if (status && !VALID_MISSION_STATUSES.includes(status)) {
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

  const missions = listMissions({ status, sort, verbose });

  switch (format) {
    case "table":
      console.log(formatTable(missions));
      break;
    case "summary":
      console.log(formatSummary(missions));
      break;
    case "json":
    default:
      console.log(JSON.stringify(missions, null, 2));
      break;
  }
}

if (import.meta.main) {
  main().catch((err) => {
    console.log(JSON.stringify({ success: false, error: String(err) }));
    process.exit(1);
  });
}
