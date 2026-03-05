#!/usr/bin/env bun
/**
 * ProjectDashboard.ts - Rich overview of all bounded projects
 *
 * Generates a comprehensive dashboard showing all projects with their
 * status, progress, tasks, and activity for display or context injection.
 *
 * Usage:
 *   bun ~/.claude/skills/PAI/Tools/ProjectDashboard.ts [options]
 *   bun ~/.claude/skills/PAI/Tools/ProjectDashboard.ts --help
 *
 * @author PAI System
 * @version 1.0.0
 */

import { existsSync, readdirSync, readFileSync } from "fs";
import { join } from "path";
import { homedir } from "os";

// ============================================================================
// Constants
// ============================================================================

const HOME = process.env.HOME || homedir();
const PAI_DIR = process.env.PAI_DIR || join(HOME, ".claude");
const PROJECTS_DIR = join(PAI_DIR, "MEMORY", "STATE", "projects");

type ProjectStatus = "PLANNING" | "IN_PROGRESS" | "COMPLETED" | "PAUSED" | "BLOCKED";

interface ProjectData {
  id: string;
  title: string;
  status: ProjectStatus;
  created: string;
  completed?: string;
  goal: string;
  target?: string;
  priority: string;
  parent_role?: string;
  success_criteria: string[];
  tags: string[];
  task_counts: {
    completed: number;
    in_progress: number;
    remaining: number;
    blocked: number;
    optional: number;
  };
  completion_percentage: number;
  last_updated?: string;
  recent_activity: Array<{ timestamp: string; action: string; task: string }>;
  tasks_content?: string;
}

interface DashboardData {
  generated: string;
  summary: {
    total: number;
    active: number;
    completed: number;
    blocked: number;
    paused: number;
    planning: number;
  };
  projects: ProjectData[];
}

// ============================================================================
// Help
// ============================================================================

function showHelp(): void {
  console.log(`
ProjectDashboard - Rich overview of all bounded projects

USAGE:
  bun ~/.claude/skills/PAI/Tools/ProjectDashboard.ts [options]

OPTIONS:
  --format markdown|json   Output format (default: markdown)
  --active                 Only show non-completed projects
  --project <slug>         Deep-dive into a single project
  --tag <tag>              Filter projects by tag
  --quiet                  Minimal output (counts only)
  --help, -h               Show this help message

EXAMPLES:
  bun ~/.claude/skills/PAI/Tools/ProjectDashboard.ts                    # Full markdown dashboard
  bun ~/.claude/skills/PAI/Tools/ProjectDashboard.ts --format json      # Machine-readable JSON
  bun ~/.claude/skills/PAI/Tools/ProjectDashboard.ts --active           # Non-completed only
  bun ~/.claude/skills/PAI/Tools/ProjectDashboard.ts --project my-proj  # Single project deep-dive
  bun ~/.claude/skills/PAI/Tools/ProjectDashboard.ts --tag work         # Filter by tag
  bun ~/.claude/skills/PAI/Tools/ProjectDashboard.ts --quiet            # Just counts

OUTPUT:
  Markdown dashboard (default) or JSON data structure
`);
  process.exit(0);
}

// ============================================================================
// YAML Parsing
// ============================================================================

function parseSimpleYaml(content: string): Record<string, any> {
  const result: Record<string, any> = {};
  let currentArrayKey: string | null = null;
  const currentArray: string[] = [];
  let multiLineKey: string | null = null;
  const multiLineValue: string[] = [];

  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      if (multiLineKey && line.startsWith("  ")) {
        multiLineValue.push(line.slice(2));
      }
      continue;
    }

    if (multiLineKey && (line.startsWith("  ") || line.startsWith("\t"))) {
      multiLineValue.push(trimmed);
      continue;
    }

    if (multiLineKey) {
      result[multiLineKey] = multiLineValue.join("\n");
      multiLineKey = null;
      multiLineValue.length = 0;
    }

    if (trimmed.startsWith("- ") && currentArrayKey) {
      let value = trimmed.slice(2).trim();
      if ((value.startsWith('"') && value.endsWith('"')) ||
          (value.startsWith("'") && value.endsWith("'"))) {
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

    if (value === "|") {
      multiLineKey = key;
      continue;
    }

    if (!value) {
      currentArrayKey = key;
      continue;
    }

    if ((value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }

    result[key] = value;
  }

  if (currentArrayKey && currentArray.length > 0) {
    result[currentArrayKey] = [...currentArray];
  }
  if (multiLineKey) {
    result[multiLineKey] = multiLineValue.join("\n");
  }

  return result;
}

// ============================================================================
// Core Functions
// ============================================================================

function loadProjectData(slug: string, includeTasksContent: boolean = false): ProjectData | null {
  const projectDir = join(PROJECTS_DIR, slug);
  const yamlPath = join(projectDir, "PROJECT.yaml");
  const progressPath = join(projectDir, "progress.json");
  const tasksPath = join(projectDir, "TASKS.md");

  if (!existsSync(yamlPath)) return null;

  try {
    const yamlContent = readFileSync(yamlPath, "utf-8");
    const yaml = parseSimpleYaml(yamlContent);

    let progress: any = {
      task_counts: { completed: 0, in_progress: 0, remaining: 0, blocked: 0, optional: 0 },
      completion_percentage: 0,
      recent_activity: [],
    };
    if (existsSync(progressPath)) {
      try {
        progress = JSON.parse(readFileSync(progressPath, "utf-8"));
      } catch { /* use defaults */ }
    }

    const data: ProjectData = {
      id: yaml.id || slug,
      title: yaml.title || slug,
      status: (yaml.status || "PLANNING") as ProjectStatus,
      created: yaml.created || "unknown",
      completed: yaml.completed || undefined,
      goal: yaml.goal || "",
      target: yaml.target || undefined,
      priority: yaml.priority || "MEDIUM",
      parent_role: yaml.parent_role || undefined,
      success_criteria: Array.isArray(yaml.success_criteria) ? yaml.success_criteria : [],
      tags: Array.isArray(yaml.tags) ? yaml.tags : [],
      task_counts: progress.task_counts || { completed: 0, in_progress: 0, remaining: 0, blocked: 0, optional: 0 },
      completion_percentage: progress.completion_percentage || 0,
      last_updated: progress.last_updated || undefined,
      recent_activity: progress.recent_activity || [],
    };

    if (includeTasksContent && existsSync(tasksPath)) {
      data.tasks_content = readFileSync(tasksPath, "utf-8");
    }

    return data;
  } catch {
    return null;
  }
}

export function getDashboardData(options: {
  active?: boolean;
  projectSlug?: string;
  tag?: string;
}): DashboardData {
  const now = new Date().toISOString();

  if (!existsSync(PROJECTS_DIR)) {
    return {
      generated: now,
      summary: { total: 0, active: 0, completed: 0, blocked: 0, paused: 0, planning: 0 },
      projects: [],
    };
  }

  let slugs = readdirSync(PROJECTS_DIR, { withFileTypes: true })
    .filter(e => e.isDirectory())
    .map(e => e.name);

  // Single project mode
  if (options.projectSlug) {
    slugs = slugs.filter(s => s === options.projectSlug);
  }

  const includeTasksContent = !!options.projectSlug;
  let projects = slugs
    .map(slug => loadProjectData(slug, includeTasksContent))
    .filter((p): p is ProjectData => p !== null);

  // Filter active only
  if (options.active) {
    projects = projects.filter(p => p.status !== "COMPLETED");
  }

  // Filter by tag
  if (options.tag) {
    const tag = options.tag.toLowerCase();
    projects = projects.filter(p => p.tags.some(t => t.toLowerCase() === tag));
  }

  // Sort: blocked first, then in_progress, planning, paused, completed
  const statusOrder: Record<string, number> = { BLOCKED: 0, IN_PROGRESS: 1, PLANNING: 2, PAUSED: 3, COMPLETED: 4 };
  projects.sort((a, b) => (statusOrder[a.status] ?? 5) - (statusOrder[b.status] ?? 5));

  const summary = {
    total: projects.length,
    active: projects.filter(p => p.status === "IN_PROGRESS").length,
    completed: projects.filter(p => p.status === "COMPLETED").length,
    blocked: projects.filter(p => p.status === "BLOCKED").length,
    paused: projects.filter(p => p.status === "PAUSED").length,
    planning: projects.filter(p => p.status === "PLANNING").length,
  };

  return { generated: now, summary, projects };
}

// ============================================================================
// Markdown Formatting
// ============================================================================

function formatMarkdownDashboard(data: DashboardData, quiet: boolean = false): string {
  const lines: string[] = [];
  const { summary, projects } = data;

  if (quiet) {
    lines.push(`Projects: ${summary.total} total | ${summary.active} active | ${summary.completed} completed | ${summary.blocked} blocked | ${summary.paused} paused | ${summary.planning} planning`);
    return lines.join("\n");
  }

  lines.push(`# Project Dashboard`);
  lines.push(``);
  lines.push(`**Generated:** ${data.generated.split("T")[0]}`);
  lines.push(``);

  // Summary bar
  lines.push(`## Summary`);
  lines.push(``);
  lines.push(`| Metric | Count |`);
  lines.push(`|--------|-------|`);
  lines.push(`| Total Projects | ${summary.total} |`);
  lines.push(`| Active (IN_PROGRESS) | ${summary.active} |`);
  lines.push(`| Planning | ${summary.planning} |`);
  lines.push(`| Blocked | ${summary.blocked} |`);
  lines.push(`| Paused | ${summary.paused} |`);
  lines.push(`| Completed | ${summary.completed} |`);
  lines.push(``);

  if (projects.length === 0) {
    lines.push(`No projects found.`);
    return lines.join("\n");
  }

  const statusIcons: Record<string, string> = {
    PLANNING: "📋",
    IN_PROGRESS: "🔄",
    COMPLETED: "✅",
    PAUSED: "⏸️",
    BLOCKED: "🚫",
  };

  // Single project deep-dive
  if (projects.length === 1 && projects[0].tasks_content) {
    const p = projects[0];
    lines.push(`## ${statusIcons[p.status] || "❓"} ${p.title}`);
    lines.push(``);
    lines.push(`| Field | Value |`);
    lines.push(`|-------|-------|`);
    lines.push(`| **ID** | \`${p.id}\` |`);
    lines.push(`| **Status** | ${p.status} |`);
    lines.push(`| **Priority** | ${p.priority} |`);
    lines.push(`| **Created** | ${p.created} |`);
    if (p.target) lines.push(`| **Target** | ${p.target} |`);
    if (p.completed) lines.push(`| **Completed** | ${p.completed} |`);
    lines.push(`| **Completion** | ${p.completion_percentage}% |`);
    if (p.parent_role) lines.push(`| **Parent Role** | ${p.parent_role} |`);
    lines.push(``);
    lines.push(`**Goal:** ${p.goal}`);
    lines.push(``);

    // Success criteria
    if (p.success_criteria.length > 0) {
      lines.push(`### Success Criteria`);
      lines.push(``);
      for (const c of p.success_criteria) {
        const achieved = c.includes("ACHIEVED") || c.includes("✓");
        lines.push(`- ${achieved ? "✅" : "⬜"} ${c}`);
      }
      lines.push(``);
    }

    // Task counts
    lines.push(`### Task Counts`);
    lines.push(``);
    lines.push(`| Section | Count |`);
    lines.push(`|---------|-------|`);
    lines.push(`| Completed | ${p.task_counts.completed} |`);
    lines.push(`| In Progress | ${p.task_counts.in_progress} |`);
    lines.push(`| Remaining | ${p.task_counts.remaining} |`);
    lines.push(`| Blocked | ${p.task_counts.blocked} |`);
    lines.push(`| Optional | ${p.task_counts.optional} |`);
    lines.push(``);

    // Tasks content
    if (p.tasks_content) {
      lines.push(`### Tasks`);
      lines.push(``);
      lines.push(p.tasks_content);
      lines.push(``);
    }

    // Recent activity
    if (p.recent_activity.length > 0) {
      lines.push(`### Recent Activity`);
      lines.push(``);
      for (const a of p.recent_activity.slice(0, 10)) {
        const date = a.timestamp ? a.timestamp.split("T")[0] : "unknown";
        lines.push(`- **${date}** [${a.action}] ${a.task}`);
      }
      lines.push(``);
    }

    // Tags
    if (p.tags.length > 0) {
      lines.push(`**Tags:** ${p.tags.join(", ")}`);
      lines.push(``);
    }

    return lines.join("\n");
  }

  // Multi-project list
  lines.push(`## Projects`);
  lines.push(``);

  for (const p of projects) {
    const icon = statusIcons[p.status] || "❓";
    lines.push(`### ${icon} ${p.title}`);
    lines.push(``);
    lines.push(`- **ID:** \`${p.id}\``);
    lines.push(`- **Status:** ${p.status} | **Priority:** ${p.priority} | **Completion:** ${p.completion_percentage}%`);
    lines.push(`- **Goal:** ${p.goal}`);
    if (p.target) lines.push(`- **Target:** ${p.target}`);
    if (p.parent_role) lines.push(`- **Parent Role:** ${p.parent_role}`);

    // Show task summary
    const tc = p.task_counts;
    const taskParts: string[] = [];
    if (tc.completed > 0) taskParts.push(`${tc.completed} done`);
    if (tc.in_progress > 0) taskParts.push(`${tc.in_progress} active`);
    if (tc.remaining > 0) taskParts.push(`${tc.remaining} remaining`);
    if (tc.blocked > 0) taskParts.push(`${tc.blocked} blocked`);
    if (taskParts.length > 0) {
      lines.push(`- **Tasks:** ${taskParts.join(", ")}`);
    }

    // Show recent activity (last 5)
    if (p.recent_activity.length > 0) {
      const recent = p.recent_activity.slice(0, 5);
      lines.push(`- **Recent:** ${recent.map(a => `[${a.action}] ${a.task}`).join("; ")}`);
    }

    lines.push(``);
  }

  return lines.join("\n");
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

  const format = getArg(args, "--format") || "markdown";
  if (!["markdown", "json"].includes(format)) {
    console.log(JSON.stringify({ success: false, error: `Invalid format: ${format}. Must be markdown or json` }));
    process.exit(1);
  }

  const active = hasFlag(args, "--active");
  const projectSlug = getArg(args, "--project");
  const tag = getArg(args, "--tag");
  const quiet = hasFlag(args, "--quiet");

  const data = getDashboardData({ active, projectSlug, tag });

  if (projectSlug && data.projects.length === 0) {
    console.log(JSON.stringify({ success: false, error: `Project not found: ${projectSlug}` }));
    process.exit(1);
  }

  switch (format) {
    case "json":
      console.log(JSON.stringify(data, null, 2));
      break;
    case "markdown":
    default:
      console.log(formatMarkdownDashboard(data, quiet));
      break;
  }
}

if (import.meta.main) {
  main().catch((err) => {
    console.log(JSON.stringify({ success: false, error: String(err) }));
    process.exit(1);
  });
}
