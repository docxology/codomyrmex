#!/usr/bin/env bun
/**
 * ListTasks.ts - Cross-project task listing with filters
 *
 * Lists tasks across one or all projects, with filtering by section,
 * priority, due date, and overdue status.
 *
 * Usage:
 *   bun ~/.claude/skills/PAI/Tools/ListTasks.ts [options]
 *   bun ~/.claude/skills/PAI/Tools/ListTasks.ts --help
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

type OutputFormat = "json" | "table" | "summary";

interface TaskEntry {
  project: string;
  section: string;
  title: string;
  priority?: string;
  due?: string;
  assignee?: string;
  created?: string;
  blocked_by?: string;
  overdue: boolean;
}

// ============================================================================
// Help
// ============================================================================

function showHelp(): void {
  console.log(`
ListTasks - Cross-project task listing with filters

USAGE:
  bun ~/.claude/skills/PAI/Tools/ListTasks.ts [options]

OPTIONS:
  --project <slug>           Filter to single project
  --section <name>           Filter by section (completed, in_progress, remaining, blocked, optional)
  --priority HIGH|MEDIUM|LOW Filter by priority
  --overdue                  Show only overdue tasks
  --due-before YYYY-MM-DD   Show tasks due before date
  --assignee "name"          Filter by assignee
  --format json|table|summary  Output format (default: json)
  --help, -h                 Show this help message

EXAMPLES:
  bun ~/.claude/skills/PAI/Tools/ListTasks.ts                                # All tasks, all projects
  bun ~/.claude/skills/PAI/Tools/ListTasks.ts --project my-proj              # Tasks in one project
  bun ~/.claude/skills/PAI/Tools/ListTasks.ts --section blocked --format table  # Blocked tasks
  bun ~/.claude/skills/PAI/Tools/ListTasks.ts --overdue                      # Overdue tasks
  bun ~/.claude/skills/PAI/Tools/ListTasks.ts --priority HIGH                # High priority

OUTPUT:
  JSON array of task objects (default)
`);
  process.exit(0);
}

// ============================================================================
// Task Parsing
// ============================================================================

function parseTasksFromMd(content: string, projectSlug: string): TaskEntry[] {
  const tasks: TaskEntry[] = [];
  let currentSection: string | null = null;
  let currentTaskTitle: string | null = null;
  let currentMetadata: Record<string, string> = {};
  const today = new Date().toISOString().split("T")[0];

  function flushTask() {
    if (currentTaskTitle && currentSection) {
      const entry: TaskEntry = {
        project: projectSlug,
        section: currentSection,
        title: currentTaskTitle,
        overdue: false,
      };
      if (currentMetadata.priority) entry.priority = currentMetadata.priority;
      if (currentMetadata.due) {
        entry.due = currentMetadata.due;
        if (currentMetadata.due < today && currentSection !== "completed") {
          entry.overdue = true;
        }
      }
      if (currentMetadata.assignee) entry.assignee = currentMetadata.assignee;
      if (currentMetadata.created) entry.created = currentMetadata.created;
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
    if (lower.startsWith("## optional") || lower.startsWith("## deferred") || lower.startsWith("## skipped")) { flushTask(); currentSection = "optional"; continue; }
    if (lower.startsWith("## summary") || (trimmed === "---" && currentSection)) { flushTask(); currentSection = null; continue; }

    if (!currentSection) continue;

    // New task item (not indented sub-items which start with 2+ spaces)
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

    // Metadata sub-items (indented "- Key: Value")
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
  return tasks;
}

// ============================================================================
// Core Functions
// ============================================================================

export function listTasks(options: {
  project?: string;
  section?: string;
  priority?: string;
  overdue?: boolean;
  dueBefore?: string;
  assignee?: string;
}): TaskEntry[] {
  if (!existsSync(PROJECTS_DIR)) return [];

  let projectSlugs: string[];

  if (options.project) {
    projectSlugs = [options.project];
  } else {
    projectSlugs = readdirSync(PROJECTS_DIR, { withFileTypes: true })
      .filter(e => e.isDirectory())
      .map(e => e.name);
  }

  let allTasks: TaskEntry[] = [];

  for (const slug of projectSlugs) {
    const tasksPath = join(PROJECTS_DIR, slug, "TASKS.md");
    if (!existsSync(tasksPath)) continue;

    const content = readFileSync(tasksPath, "utf-8");
    const tasks = parseTasksFromMd(content, slug);
    allTasks.push(...tasks);
  }

  // Apply filters
  if (options.section) {
    allTasks = allTasks.filter(t => t.section === options.section);
  }

  if (options.priority) {
    const targetPriority = options.priority.toUpperCase();
    allTasks = allTasks.filter(t => t.priority === targetPriority);
  }

  if (options.overdue) {
    allTasks = allTasks.filter(t => t.overdue);
  }

  if (options.dueBefore) {
    allTasks = allTasks.filter(t => t.due && t.due < options.dueBefore!);
  }

  if (options.assignee) {
    const targetAssignee = options.assignee.toLowerCase();
    allTasks = allTasks.filter(t => t.assignee && t.assignee.toLowerCase().includes(targetAssignee));
  }

  return allTasks;
}

// ============================================================================
// Output Formatters
// ============================================================================

function formatTable(tasks: TaskEntry[]): string {
  if (tasks.length === 0) return "No tasks found.";

  const sectionIcons: Record<string, string> = {
    completed: "✅",
    in_progress: "🔄",
    remaining: "📋",
    blocked: "🚫",
    optional: "💡",
  };

  const lines: string[] = [];
  lines.push("  " + "Project".padEnd(20) + "Section".padEnd(16) + "Priority".padEnd(10) + "Due".padEnd(12) + "Task");
  lines.push("  " + "─".repeat(90));

  for (const t of tasks) {
    const icon = sectionIcons[t.section] || "❓";
    const priority = (t.priority || "—").padEnd(10);
    const due = t.due ? (t.overdue ? `⚠️ ${t.due}` : t.due) : "—";
    const titleTrunc = t.title.length > 35 ? t.title.slice(0, 32) + "..." : t.title;
    lines.push(
      "  " +
      t.project.padEnd(20) +
      `${icon} ${t.section}`.padEnd(16) +
      priority +
      due.padEnd(12) +
      titleTrunc
    );
  }

  lines.push("");
  lines.push(`  Total: ${tasks.length} task(s)`);
  return lines.join("\n");
}

function formatSummary(tasks: TaskEntry[]): string {
  if (tasks.length === 0) return "No tasks found.";

  const sectionIcons: Record<string, string> = {
    completed: "✅",
    in_progress: "🔄",
    remaining: "📋",
    blocked: "🚫",
    optional: "💡",
  };

  return tasks
    .map(t => {
      const icon = sectionIcons[t.section] || "❓";
      const parts = [`${icon} [${t.project}]`, t.title];
      if (t.priority) parts.push(`(${t.priority})`);
      if (t.due) parts.push(t.overdue ? `⚠️ DUE: ${t.due}` : `due: ${t.due}`);
      return parts.join(" ");
    })
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

  const format = (getArg(args, "--format") || "json") as OutputFormat;
  if (!["json", "table", "summary"].includes(format)) {
    console.log(JSON.stringify({ success: false, error: `Invalid format: ${format}` }));
    process.exit(1);
  }

  const tasks = listTasks({
    project: getArg(args, "--project"),
    section: getArg(args, "--section"),
    priority: getArg(args, "--priority"),
    overdue: hasFlag(args, "--overdue"),
    dueBefore: getArg(args, "--due-before"),
    assignee: getArg(args, "--assignee"),
  });

  switch (format) {
    case "table":
      console.log(formatTable(tasks));
      break;
    case "summary":
      console.log(formatSummary(tasks));
      break;
    case "json":
    default:
      console.log(JSON.stringify(tasks, null, 2));
      break;
  }
}

if (import.meta.main) {
  main().catch((err) => {
    console.log(JSON.stringify({ success: false, error: String(err) }));
    process.exit(1);
  });
}
