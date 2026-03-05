#!/usr/bin/env bun
/**
 * UpdateTask.ts - Update task status, metadata, or move between sections
 *
 * Modifies a task within a project's TASKS.md, supporting moves between
 * sections and metadata updates.
 *
 * Usage:
 *   bun ~/.claude/skills/PAI/Tools/UpdateTask.ts <project-slug> "task text" [options]
 *   bun ~/.claude/skills/PAI/Tools/UpdateTask.ts --help
 *
 * @author PAI System
 * @version 1.0.0
 */

import { existsSync, readFileSync, writeFileSync } from "fs";
import { join } from "path";
import { homedir } from "os";

// ============================================================================
// Constants
// ============================================================================

const HOME = process.env.HOME || homedir();
const PAI_DIR = process.env.PAI_DIR || join(HOME, ".claude");
const PROJECTS_DIR = join(PAI_DIR, "MEMORY", "STATE", "projects");

type TaskSection = "completed" | "in_progress" | "remaining" | "blocked" | "optional";

interface UpdateTaskResult {
  updated: boolean;
  project: string;
  task: string;
  changes: string[];
  error?: string;
}

// ============================================================================
// Help
// ============================================================================

function showHelp(): void {
  console.log(`
UpdateTask - Update task status, metadata, or move between sections

USAGE:
  bun ~/.claude/skills/PAI/Tools/UpdateTask.ts <project-slug> "task text" [options]

ARGUMENTS:
  <project-slug>              Project identifier (required)
  "task text"                 Task to match (required, partial match supported)

OPTIONS:
  --move-to <section>         Move task to section (completed, in_progress, remaining, blocked, optional)
  --priority HIGH|MEDIUM|LOW  Update or set priority
  --due YYYY-MM-DD            Update or set due date
  --assignee "name"           Update or set assignee
  --blocked-by "reason"       Set block reason (auto-moves to blocked)
  --spec "criteria"           Set acceptance criteria / definition of done
  --depends-on "task title"   Set dependency (can be repeated)
  --rename "new text"         Rename the task
  --help, -h                  Show this help message

EXAMPLES:
  bun ~/.claude/skills/PAI/Tools/UpdateTask.ts my-project "Implement feature" --move-to completed
  bun ~/.claude/skills/PAI/Tools/UpdateTask.ts my-project "Write tests" --priority HIGH --due 2026-03-01
  bun ~/.claude/skills/PAI/Tools/UpdateTask.ts my-project "Deploy" --move-to blocked --blocked-by "Waiting for API key"

OUTPUT:
  JSON: { "updated": true, "project": "...", "task": "...", "changes": [...] }
`);
  process.exit(0);
}

// ============================================================================
// TASKS.md Parsing & Writing
// ============================================================================

interface ParsedTask {
  title: string;
  metadata: Record<string, string>;
  rawLines: string[];
}

interface ParsedTasks {
  header: string;
  completed: ParsedTask[];
  in_progress: ParsedTask[];
  remaining: ParsedTask[];
  blocked: ParsedTask[];
  optional: ParsedTask[];
  footer: string;
}

function parseTasksMd(content: string): ParsedTasks {
  const result: ParsedTasks = {
    header: "",
    completed: [],
    in_progress: [],
    remaining: [],
    blocked: [],
    optional: [],
    footer: "",
  };

  let currentSection: TaskSection | null = null;
  const headerLines: string[] = [];
  let foundFirstSection = false;
  let inFooter = false;
  const footerLines: string[] = [];
  let currentTask: ParsedTask | null = null;

  function flushTask() {
    if (currentTask && currentSection) {
      result[currentSection].push(currentTask);
      currentTask = null;
    }
  }

  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    const lower = trimmed.toLowerCase();

    if (lower.startsWith("## completed")) { flushTask(); currentSection = "completed"; foundFirstSection = true; continue; }
    if (lower.startsWith("## in progress")) { flushTask(); currentSection = "in_progress"; foundFirstSection = true; continue; }
    if (lower.startsWith("## remaining")) { flushTask(); currentSection = "remaining"; foundFirstSection = true; continue; }
    if (lower.startsWith("## blocked")) { flushTask(); currentSection = "blocked"; foundFirstSection = true; continue; }
    if (lower.startsWith("## optional") || lower.startsWith("## deferred") || lower.startsWith("## skipped")) { flushTask(); currentSection = "optional"; foundFirstSection = true; continue; }

    if (lower.startsWith("## summary") || (trimmed === "---" && foundFirstSection && currentSection)) {
      flushTask();
      if (lower.startsWith("## summary")) { inFooter = true; currentSection = null; footerLines.push(line); continue; }
      if (inFooter) { footerLines.push(line); continue; }
      continue;
    }

    if (inFooter) { footerLines.push(line); continue; }
    if (!foundFirstSection) { headerLines.push(line); continue; }

    if (!currentSection) continue;

    // New task item (not indented sub-items which start with 2+ spaces)
    if (trimmed.startsWith("- [") || (trimmed.startsWith("- ") && !line.startsWith("  ") && !line.startsWith("\t"))) {
      flushTask();

      let text = trimmed;
      if (trimmed.startsWith("- [x] ")) text = trimmed.slice(6);
      else if (trimmed.startsWith("- [ ] ")) text = trimmed.slice(6);
      else if (trimmed.startsWith("- [~] ")) text = trimmed.slice(6);
      else if (trimmed.startsWith("- ")) text = trimmed.slice(2);

      currentTask = { title: text, metadata: {}, rawLines: [text] };
      continue;
    }

    // Metadata sub-items
    if (currentTask && trimmed.startsWith("- ")) {
      const metaText = trimmed.slice(2).trim();
      const colonIdx = metaText.indexOf(":");
      if (colonIdx !== -1) {
        const key = metaText.slice(0, colonIdx).trim().toLowerCase().replace(/ /g, "_");
        const value = metaText.slice(colonIdx + 1).trim();
        currentTask.metadata[key] = value;
        currentTask.rawLines.push(trimmed);
      }
    }
  }

  flushTask();
  result.header = headerLines.join("\n");
  result.footer = footerLines.join("\n");
  return result;
}

function taskToString(task: ParsedTask): string {
  const lines = [task.title];
  if (task.metadata.priority) lines.push(`- Priority: ${task.metadata.priority}`);
  if (task.metadata.due) lines.push(`- Due: ${task.metadata.due}`);
  if (task.metadata.assignee) lines.push(`- Assignee: ${task.metadata.assignee}`);
  if (task.metadata.created) lines.push(`- Created: ${task.metadata.created}`);
  if (task.metadata.blocked_by) lines.push(`- Blocked by: ${task.metadata.blocked_by}`);
  if (task.metadata.spec) lines.push(`- Spec: ${task.metadata.spec}`);
  if (task.metadata.depends_on) lines.push(`- Depends on: ${task.metadata.depends_on}`);
  return lines.join("\n");
}

function writeTasksMd(projectDir: string, tasks: ParsedTasks): void {
  const lines: string[] = [];

  lines.push(tasks.header.trimEnd());
  lines.push("");

  const sections: { name: string; key: TaskSection; prefix: string }[] = [
    { name: "Completed", key: "completed", prefix: "- [x]" },
    { name: "In Progress", key: "in_progress", prefix: "- [ ]" },
    { name: "Remaining", key: "remaining", prefix: "- [ ]" },
    { name: "Blocked", key: "blocked", prefix: "- [ ]" },
    { name: "Optional/Deferred", key: "optional", prefix: "- [ ]" },
  ];

  for (const sec of sections) {
    lines.push(`## ${sec.name}`);
    for (const t of tasks[sec.key]) {
      const taskStr = taskToString(t);
      const taskLines = taskStr.split("\n");
      lines.push(`${sec.prefix} ${taskLines[0]}`);
      for (let i = 1; i < taskLines.length; i++) {
        lines.push(`  ${taskLines[i]}`);
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

// ============================================================================
// Progress Recalculation
// ============================================================================

function recalculateProgress(tasks: ParsedTasks): {
  task_counts: Record<string, number>;
  completion_percentage: number;
} {
  const counts = {
    completed: tasks.completed.length,
    in_progress: tasks.in_progress.length,
    remaining: tasks.remaining.length,
    blocked: tasks.blocked.length,
    optional: tasks.optional.length,
  };

  const total = counts.completed + counts.in_progress + counts.remaining + counts.blocked;
  const percentage = total > 0 ? Math.round((counts.completed / total) * 100) : 0;

  return { task_counts: counts, completion_percentage: percentage };
}

// ============================================================================
// Core Functions
// ============================================================================

function findTaskInSection(tasks: ParsedTask[], searchText: string): number {
  const normalized = searchText.toLowerCase().trim();

  // Exact match first
  let idx = tasks.findIndex(t => t.title.toLowerCase().trim() === normalized);
  if (idx !== -1) return idx;

  // Partial match (contains)
  idx = tasks.findIndex(t => t.title.toLowerCase().includes(normalized) || normalized.includes(t.title.toLowerCase()));
  return idx;
}

export function updateTask(projectSlug: string, taskText: string, options: {
  moveTo?: TaskSection;
  priority?: string;
  due?: string;
  assignee?: string;
  blockedBy?: string;
  rename?: string;
  spec?: string;
  dependsOn?: string[];
}): UpdateTaskResult {
  const projectDir = join(PROJECTS_DIR, projectSlug);
  const tasksPath = join(projectDir, "TASKS.md");
  const progressPath = join(projectDir, "progress.json");

  if (!existsSync(tasksPath)) {
    return { updated: false, project: projectSlug, task: taskText, changes: [], error: `Project or TASKS.md not found: ${projectSlug}` };
  }

  const tasks = parseTasksMd(readFileSync(tasksPath, "utf-8"));
  const changes: string[] = [];

  // Find the task across all sections
  let foundSection: TaskSection | null = null;
  let foundIdx = -1;
  const allSections: TaskSection[] = ["completed", "in_progress", "remaining", "blocked", "optional"];

  for (const section of allSections) {
    const idx = findTaskInSection(tasks[section], taskText);
    if (idx !== -1) {
      foundSection = section;
      foundIdx = idx;
      break;
    }
  }

  if (foundSection === null || foundIdx === -1) {
    return { updated: false, project: projectSlug, task: taskText, changes: [], error: `Task not found: "${taskText}"` };
  }

  const task = tasks[foundSection][foundIdx];

  // Apply metadata updates
  if (options.priority) {
    task.metadata.priority = options.priority.toUpperCase();
    changes.push(`priority set to ${options.priority.toUpperCase()}`);
  }

  if (options.due) {
    task.metadata.due = options.due;
    changes.push(`due date set to ${options.due}`);
  }

  if (options.assignee) {
    task.metadata.assignee = options.assignee;
    changes.push(`assignee set to ${options.assignee}`);
  }

  if (options.blockedBy) {
    task.metadata.blocked_by = options.blockedBy;
    changes.push(`blocked by: ${options.blockedBy}`);
    // Auto-move to blocked if not already there
    if (!options.moveTo) {
      options.moveTo = "blocked";
    }
  }

  if (options.rename) {
    const oldTitle = task.title;
    task.title = options.rename;
    changes.push(`renamed: "${oldTitle}" -> "${options.rename}"`);
  }

  if (options.spec) {
    task.metadata.spec = options.spec;
    changes.push(`spec set`);
  }

  if (options.dependsOn && options.dependsOn.length > 0) {
    task.metadata.depends_on = options.dependsOn.join(", ");
    changes.push(`depends_on set to: ${options.dependsOn.join(", ")}`);
  }

  // Move to new section
  if (options.moveTo && options.moveTo !== foundSection) {
    // Remove from current section
    tasks[foundSection].splice(foundIdx, 1);

    // If moving to completed, clean up blocked_by
    if (options.moveTo === "completed") {
      delete task.metadata.blocked_by;
    }

    // Add to target section
    tasks[options.moveTo].push(task);
    changes.push(`moved: ${foundSection} -> ${options.moveTo}`);
  }

  // Write TASKS.md
  writeTasksMd(projectDir, tasks);

  // Update progress.json
  const now = new Date().toISOString();
  let progress: any = {};
  if (existsSync(progressPath)) {
    try {
      progress = JSON.parse(readFileSync(progressPath, "utf-8"));
    } catch {
      progress = { project_id: projectSlug, recent_activity: [] };
    }
  } else {
    progress = { project_id: projectSlug, recent_activity: [] };
  }

  if (!progress.recent_activity) progress.recent_activity = [];

  const { task_counts, completion_percentage } = recalculateProgress(tasks);
  progress.task_counts = task_counts;
  progress.completion_percentage = completion_percentage;
  progress.last_updated = now;

  // Log activity
  const action = options.moveTo === "completed" ? "completed" :
    options.moveTo === "blocked" ? "blocked" :
      options.moveTo === "in_progress" ? "started" :
        "updated";

  progress.recent_activity.unshift({
    timestamp: now,
    action,
    task: task.title,
  });

  if (progress.recent_activity.length > 20) {
    progress.recent_activity = progress.recent_activity.slice(0, 20);
  }

  writeFileSync(progressPath, JSON.stringify(progress, null, 2) + "\n");

  return {
    updated: true,
    project: projectSlug,
    task: task.title,
    changes,
  };
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

  // Parse positional args
  const positionals: string[] = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith("--")) {
      i++; // skip flag value
      continue;
    }
    if (args[i].startsWith("-")) continue;
    positionals.push(args[i]);
  }

  const projectSlug = positionals[0];
  const taskText = positionals[1];

  if (!projectSlug) {
    console.log(JSON.stringify({ updated: false, error: "Missing required argument: <project-slug>" }));
    process.exit(1);
  }

  if (!taskText) {
    console.log(JSON.stringify({ updated: false, error: "Missing required argument: task text" }));
    process.exit(1);
  }

  const moveToRaw = getArg(args, "--move-to");
  let moveTo: TaskSection | undefined;
  if (moveToRaw) {
    moveTo = moveToRaw.toLowerCase() as TaskSection;
    if (!["completed", "in_progress", "remaining", "blocked", "optional"].includes(moveTo)) {
      console.log(JSON.stringify({ updated: false, error: `Invalid section: ${moveToRaw}` }));
      process.exit(1);
    }
  }

  const result = updateTask(projectSlug, taskText, {
    moveTo,
    priority: getArg(args, "--priority"),
    due: getArg(args, "--due"),
    assignee: getArg(args, "--assignee"),
    blockedBy: getArg(args, "--blocked-by"),
    rename: getArg(args, "--rename"),
    spec: getArg(args, "--spec"),
    dependsOn: args.reduce((acc: string[], arg, i) => {
      if (arg === "--depends-on" && i + 1 < args.length) acc.push(args[i + 1]);
      return acc;
    }, []),
  });

  console.log(JSON.stringify(result, null, 2));
  process.exit(result.updated ? 0 : 1);
}

if (import.meta.main) {
  main().catch((err) => {
    console.log(JSON.stringify({ updated: false, error: String(err) }));
    process.exit(1);
  });
}
