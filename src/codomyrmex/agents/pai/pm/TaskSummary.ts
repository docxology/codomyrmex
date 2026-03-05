#!/usr/bin/env bun
/**
 * TaskSummary.ts - Cross-project task summary report
 *
 * Generates aggregate task statistics across all projects or within
 * a mission's linked projects. Shows counts, overdue, blocked, and
 * priority breakdown.
 *
 * Usage:
 *   bun ~/.claude/skills/PAI/Tools/TaskSummary.ts [options]
 *   bun ~/.claude/skills/PAI/Tools/TaskSummary.ts --help
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
const MISSIONS_DIR = join(PAI_DIR, "MEMORY", "STATE", "missions");

type OutputFormat = "json" | "markdown";

interface TaskStats {
  total: number;
  completed: number;
  in_progress: number;
  remaining: number;
  blocked: number;
  optional: number;
  overdue: number;
  high_priority: number;
  medium_priority: number;
  low_priority: number;
  due_this_week: number;
}

interface ProjectTaskStats {
  project: string;
  title: string;
  stats: TaskStats;
}

interface SummaryData {
  generated: string;
  scope: string;
  aggregate: TaskStats;
  projects: ProjectTaskStats[];
  overdue_tasks: Array<{ project: string; title: string; due: string }>;
  blocked_tasks: Array<{ project: string; title: string; blocked_by?: string }>;
}

// ============================================================================
// Help
// ============================================================================

function showHelp(): void {
  console.log(`
TaskSummary - Cross-project task summary report

USAGE:
  bun ~/.claude/skills/PAI/Tools/TaskSummary.ts [options]

OPTIONS:
  --mission <slug>           Scope to mission's linked projects
  --project <slug>           Scope to single project
  --format json|markdown     Output format (default: markdown)
  --help, -h                 Show this help message

EXAMPLES:
  bun ~/.claude/skills/PAI/Tools/TaskSummary.ts                        # All projects
  bun ~/.claude/skills/PAI/Tools/TaskSummary.ts --mission my-mission   # Mission scope
  bun ~/.claude/skills/PAI/Tools/TaskSummary.ts --project my-project   # Single project
  bun ~/.claude/skills/PAI/Tools/TaskSummary.ts --format json          # JSON output

OUTPUT:
  Markdown summary (default) or JSON data structure
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

  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;

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

    if (!value || value === "|") {
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

  return result;
}

// ============================================================================
// Task Parsing
// ============================================================================

interface TaskEntry {
  title: string;
  section: string;
  priority?: string;
  due?: string;
  blocked_by?: string;
  overdue: boolean;
}

function parseTasksFromProject(projectSlug: string): { tasks: TaskEntry[]; title: string } {
  const tasksPath = join(PROJECTS_DIR, projectSlug, "TASKS.md");
  const yamlPath = join(PROJECTS_DIR, projectSlug, "PROJECT.yaml");

  let projectTitle = projectSlug;
  if (existsSync(yamlPath)) {
    try {
      const yaml = parseSimpleYaml(readFileSync(yamlPath, "utf-8"));
      projectTitle = yaml.title || projectSlug;
    } catch { /* ignore */ }
  }

  if (!existsSync(tasksPath)) return { tasks: [], title: projectTitle };

  const content = readFileSync(tasksPath, "utf-8");
  const tasks: TaskEntry[] = [];
  const today = new Date().toISOString().split("T")[0];

  // Calculate "this week" boundary (7 days from now)
  const weekFromNow = new Date();
  weekFromNow.setDate(weekFromNow.getDate() + 7);
  const weekBoundary = weekFromNow.toISOString().split("T")[0];

  let currentSection: string | null = null;
  let currentTaskTitle: string | null = null;
  let currentMetadata: Record<string, string> = {};

  function flushTask() {
    if (currentTaskTitle && currentSection) {
      const entry: TaskEntry = {
        title: currentTaskTitle,
        section: currentSection,
        overdue: false,
      };
      if (currentMetadata.priority) entry.priority = currentMetadata.priority;
      if (currentMetadata.due) {
        entry.due = currentMetadata.due;
        if (currentMetadata.due < today && currentSection !== "completed") {
          entry.overdue = true;
        }
      }
      if (currentMetadata.blocked_by) entry.blocked_by = currentMetadata.blocked_by;
      tasks.push(entry);
    }
    currentTaskTitle = null;
    currentMetadata = {};
  }

  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    const lower = trimmed.toLowerCase();

    if (lower.startsWith("## completed")) { flushTask(); currentSection = "completed"; continue; }
    if (lower.startsWith("## in progress")) { flushTask(); currentSection = "in_progress"; continue; }
    if (lower.startsWith("## remaining")) { flushTask(); currentSection = "remaining"; continue; }
    if (lower.startsWith("## blocked")) { flushTask(); currentSection = "blocked"; continue; }
    if (lower.startsWith("## optional") || lower.startsWith("## deferred")) { flushTask(); currentSection = "optional"; continue; }
    if (lower.startsWith("## summary") || (trimmed === "---" && currentSection)) { flushTask(); currentSection = null; continue; }

    if (!currentSection) continue;

    if (trimmed.startsWith("- [") || (trimmed.startsWith("- ") && !line.startsWith("  ") && !line.startsWith("\t"))) {
      flushTask();
      let text = trimmed;
      if (trimmed.startsWith("- [x] ")) text = trimmed.slice(6);
      else if (trimmed.startsWith("- [ ] ")) text = trimmed.slice(6);
      else if (trimmed.startsWith("- [~] ")) text = trimmed.slice(6);
      else if (trimmed.startsWith("- ")) text = trimmed.slice(2);
      currentTaskTitle = text;
      continue;
    }

    if (currentTaskTitle && trimmed.startsWith("- ")) {
      const metaText = trimmed.slice(2).trim();
      const colonIdx = metaText.indexOf(":");
      if (colonIdx !== -1) {
        const key = metaText.slice(0, colonIdx).trim().toLowerCase().replace(/ /g, "_");
        const value = metaText.slice(colonIdx + 1).trim();
        currentMetadata[key] = value;
      }
    }
  }

  flushTask();
  return { tasks, title: projectTitle };
}

// ============================================================================
// Core Functions
// ============================================================================

function emptyStats(): TaskStats {
  return {
    total: 0, completed: 0, in_progress: 0, remaining: 0, blocked: 0, optional: 0,
    overdue: 0, high_priority: 0, medium_priority: 0, low_priority: 0, due_this_week: 0,
  };
}

function addStats(target: TaskStats, source: TaskStats): void {
  target.total += source.total;
  target.completed += source.completed;
  target.in_progress += source.in_progress;
  target.remaining += source.remaining;
  target.blocked += source.blocked;
  target.optional += source.optional;
  target.overdue += source.overdue;
  target.high_priority += source.high_priority;
  target.medium_priority += source.medium_priority;
  target.low_priority += source.low_priority;
  target.due_this_week += source.due_this_week;
}

export function getTaskSummary(options: {
  mission?: string;
  project?: string;
}): SummaryData {
  const now = new Date().toISOString();
  const today = new Date().toISOString().split("T")[0];
  const weekFromNow = new Date();
  weekFromNow.setDate(weekFromNow.getDate() + 7);
  const weekBoundary = weekFromNow.toISOString().split("T")[0];

  let projectSlugs: string[] = [];
  let scope = "all projects";

  if (options.project) {
    projectSlugs = [options.project];
    scope = `project: ${options.project}`;
  } else if (options.mission) {
    scope = `mission: ${options.mission}`;
    const missionYamlPath = join(MISSIONS_DIR, options.mission, "MISSION.yaml");
    if (existsSync(missionYamlPath)) {
      const yaml = parseSimpleYaml(readFileSync(missionYamlPath, "utf-8"));
      projectSlugs = Array.isArray(yaml.linked_projects) ? yaml.linked_projects : [];
    }
  } else {
    if (existsSync(PROJECTS_DIR)) {
      projectSlugs = readdirSync(PROJECTS_DIR, { withFileTypes: true })
        .filter(e => e.isDirectory())
        .map(e => e.name);
    }
  }

  const aggregate = emptyStats();
  const projectStats: ProjectTaskStats[] = [];
  const overdueTasks: Array<{ project: string; title: string; due: string }> = [];
  const blockedTasks: Array<{ project: string; title: string; blocked_by?: string }> = [];

  for (const slug of projectSlugs) {
    const { tasks, title } = parseTasksFromProject(slug);
    const stats = emptyStats();

    for (const task of tasks) {
      stats.total++;

      switch (task.section) {
        case "completed": stats.completed++; break;
        case "in_progress": stats.in_progress++; break;
        case "remaining": stats.remaining++; break;
        case "blocked": stats.blocked++; break;
        case "optional": stats.optional++; break;
      }

      if (task.overdue) {
        stats.overdue++;
        overdueTasks.push({ project: slug, title: task.title, due: task.due! });
      }

      if (task.priority === "HIGH") stats.high_priority++;
      else if (task.priority === "MEDIUM") stats.medium_priority++;
      else if (task.priority === "LOW") stats.low_priority++;

      if (task.due && task.due >= today && task.due <= weekBoundary && task.section !== "completed") {
        stats.due_this_week++;
      }

      if (task.section === "blocked") {
        blockedTasks.push({ project: slug, title: task.title, blocked_by: task.blocked_by });
      }
    }

    if (stats.total > 0) {
      projectStats.push({ project: slug, title, stats });
      addStats(aggregate, stats);
    }
  }

  return {
    generated: now,
    scope,
    aggregate,
    projects: projectStats,
    overdue_tasks: overdueTasks,
    blocked_tasks: blockedTasks,
  };
}

// ============================================================================
// Markdown Formatting
// ============================================================================

function formatMarkdown(data: SummaryData): string {
  const lines: string[] = [];
  const { aggregate, projects, overdue_tasks, blocked_tasks } = data;

  lines.push(`# Task Summary`);
  lines.push(``);
  lines.push(`**Generated:** ${data.generated.split("T")[0]} | **Scope:** ${data.scope}`);
  lines.push(``);

  // Aggregate stats
  lines.push(`## Overview`);
  lines.push(``);
  lines.push(`| Metric | Count |`);
  lines.push(`|--------|-------|`);
  lines.push(`| Total Tasks | ${aggregate.total} |`);
  lines.push(`| Completed | ${aggregate.completed} |`);
  lines.push(`| In Progress | ${aggregate.in_progress} |`);
  lines.push(`| Remaining | ${aggregate.remaining} |`);
  lines.push(`| Blocked | ${aggregate.blocked} |`);
  lines.push(`| Optional | ${aggregate.optional} |`);
  lines.push(``);

  const completionRate = aggregate.total > 0
    ? Math.round((aggregate.completed / (aggregate.total - aggregate.optional)) * 100)
    : 0;
  lines.push(`**Completion Rate:** ${completionRate}% (excluding optional)`);
  lines.push(``);

  // Priority breakdown
  if (aggregate.high_priority + aggregate.medium_priority + aggregate.low_priority > 0) {
    lines.push(`## Priority Breakdown`);
    lines.push(``);
    lines.push(`| Priority | Count |`);
    lines.push(`|----------|-------|`);
    if (aggregate.high_priority > 0) lines.push(`| HIGH | ${aggregate.high_priority} |`);
    if (aggregate.medium_priority > 0) lines.push(`| MEDIUM | ${aggregate.medium_priority} |`);
    if (aggregate.low_priority > 0) lines.push(`| LOW | ${aggregate.low_priority} |`);
    lines.push(``);
  }

  // Alerts
  if (aggregate.overdue > 0 || aggregate.due_this_week > 0) {
    lines.push(`## Alerts`);
    lines.push(``);
    if (aggregate.overdue > 0) lines.push(`- **${aggregate.overdue} overdue task(s)**`);
    if (aggregate.due_this_week > 0) lines.push(`- ${aggregate.due_this_week} task(s) due this week`);
    lines.push(``);
  }

  // Overdue tasks
  if (overdue_tasks.length > 0) {
    lines.push(`## Overdue Tasks`);
    lines.push(``);
    for (const t of overdue_tasks) {
      lines.push(`- **[${t.project}]** ${t.title} (due: ${t.due})`);
    }
    lines.push(``);
  }

  // Blocked tasks
  if (blocked_tasks.length > 0) {
    lines.push(`## Blocked Tasks`);
    lines.push(``);
    for (const t of blocked_tasks) {
      const reason = t.blocked_by ? ` — ${t.blocked_by}` : "";
      lines.push(`- **[${t.project}]** ${t.title}${reason}`);
    }
    lines.push(``);
  }

  // Per-project breakdown
  if (projects.length > 1) {
    lines.push(`## Per-Project Breakdown`);
    lines.push(``);
    lines.push(`| Project | Total | Done | Active | Remaining | Blocked |`);
    lines.push(`|---------|-------|------|--------|-----------|---------|`);
    for (const p of projects) {
      lines.push(`| ${p.project} | ${p.stats.total} | ${p.stats.completed} | ${p.stats.in_progress} | ${p.stats.remaining} | ${p.stats.blocked} |`);
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

  const format = (getArg(args, "--format") || "markdown") as OutputFormat;
  if (!["json", "markdown"].includes(format)) {
    console.log(JSON.stringify({ success: false, error: `Invalid format: ${format}` }));
    process.exit(1);
  }

  const data = getTaskSummary({
    mission: getArg(args, "--mission"),
    project: getArg(args, "--project"),
  });

  switch (format) {
    case "json":
      console.log(JSON.stringify(data, null, 2));
      break;
    case "markdown":
    default:
      console.log(formatMarkdown(data));
      break;
  }
}

if (import.meta.main) {
  main().catch((err) => {
    console.log(JSON.stringify({ success: false, error: String(err) }));
    process.exit(1);
  });
}
