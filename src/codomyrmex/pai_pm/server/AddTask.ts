#!/usr/bin/env bun
/**
 * AddTask.ts - Add a task to a project with rich metadata
 *
 * Adds a task to a project's TASKS.md with optional priority, due date,
 * and assignee metadata. Updates progress.json accordingly.
 *
 * Usage:
 *   bun ~/.claude/skills/PAI/Tools/AddTask.ts <project-slug> "task text" [options]
 *   bun ~/.claude/skills/PAI/Tools/AddTask.ts --help
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

import { type Priority, type TaskSection, VALID_PRIORITIES, VALID_TASK_SECTIONS } from "./DataModels.ts";

interface AddTaskResult {
  added: boolean;
  project: string;
  task: string;
  section: string;
  metadata: Record<string, string>;
  error?: string;
}

// ============================================================================
// Help
// ============================================================================

function showHelp(): void {
  console.log(`
AddTask - Add a task to a project with rich metadata

USAGE:
  bun ~/.claude/skills/PAI/Tools/AddTask.ts <project-slug> "task text" [options]

ARGUMENTS:
  <project-slug>              Project identifier (required)
  "task text"                 Task description (required, second positional arg)

OPTIONS:
  --priority HIGH|MEDIUM|LOW  Task priority
  --due YYYY-MM-DD            Due date
  --assignee "name"           Person assigned
  --spec "criteria"           Acceptance criteria / definition of done
  --depends-on "task title"   Prerequisite task (can be repeated)
  --section remaining|in_progress|blocked|optional  Target section (default: remaining)
  --blocked-by "reason"       Block reason (auto-sets section to blocked)
  --help, -h                  Show this help message

EXAMPLES:
  bun ~/.claude/skills/PAI/Tools/AddTask.ts my-project "Implement feature X"
  bun ~/.claude/skills/PAI/Tools/AddTask.ts my-project "Write tests" --priority HIGH --due 2026-03-01
  bun ~/.claude/skills/PAI/Tools/AddTask.ts my-project "Deploy" --section blocked --blocked-by "Waiting for API key"

OUTPUT:
  JSON: { "added": true, "project": "...", "task": "...", "section": "...", "metadata": {...} }
`);
  process.exit(0);
}

// ============================================================================
// TASKS.md Parsing & Writing
// ============================================================================

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
    header: "",
    completed: [],
    in_progress: [],
    remaining: [],
    blocked: [],
    optional: [],
    footer: "",
  };

  let currentSection: keyof Omit<ParsedTasks, "header" | "footer"> | null = null;
  const headerLines: string[] = [];
  let foundFirstSection = false;
  let inFooter = false;
  const footerLines: string[] = [];
  let currentTask: string[] = [];

  function flushTask() {
    if (currentTask.length > 0 && currentSection) {
      result[currentSection].push(currentTask.join("\n"));
      currentTask = [];
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
      if (lower.startsWith("## summary")) {
        inFooter = true;
        currentSection = null;
        footerLines.push(line);
        continue;
      }
      if (inFooter) { footerLines.push(line); continue; }
      continue;
    }

    if (inFooter) { footerLines.push(line); continue; }
    if (!foundFirstSection) { headerLines.push(line); continue; }

    // Task items with metadata sub-items
    if (currentSection) {
      // New task item (not indented - sub-items start with 2+ spaces)
      if ((trimmed.startsWith("- [") || trimmed.startsWith("- ")) && !line.startsWith("  ") && !line.startsWith("\t")) {
        flushTask();
        // Extract task text
        let taskText = trimmed;
        if (trimmed.startsWith("- [x] ")) taskText = trimmed.slice(6);
        else if (trimmed.startsWith("- [ ] ")) taskText = trimmed.slice(6);
        else if (trimmed.startsWith("- [~] ")) taskText = trimmed.slice(6);
        else if (trimmed.startsWith("- ")) taskText = trimmed.slice(2);
        currentTask.push(taskText);
      } else if (trimmed.startsWith("- ") && currentTask.length > 0) {
        // Sub-item (metadata line, indented with 2+ spaces)
        currentTask.push(trimmed);
      }
    }
  }

  flushTask();
  result.header = headerLines.join("\n");
  result.footer = footerLines.join("\n");
  return result;
}

function writeTasksMd(projectDir: string, tasks: ParsedTasks): void {
  const lines: string[] = [];

  lines.push(tasks.header.trimEnd());
  lines.push("");

  lines.push("## Completed");
  for (const t of tasks.completed) {
    const taskLines = t.split("\n");
    lines.push(`- [x] ${taskLines[0]}`);
    for (let i = 1; i < taskLines.length; i++) {
      lines.push(`  ${taskLines[i]}`);
    }
  }
  lines.push("");

  lines.push("## In Progress");
  for (const t of tasks.in_progress) {
    const taskLines = t.split("\n");
    lines.push(`- [ ] ${taskLines[0]}`);
    for (let i = 1; i < taskLines.length; i++) {
      lines.push(`  ${taskLines[i]}`);
    }
  }
  lines.push("");

  lines.push("## Remaining");
  for (const t of tasks.remaining) {
    const taskLines = t.split("\n");
    lines.push(`- [ ] ${taskLines[0]}`);
    for (let i = 1; i < taskLines.length; i++) {
      lines.push(`  ${taskLines[i]}`);
    }
  }
  lines.push("");

  lines.push("## Blocked");
  for (const t of tasks.blocked) {
    const taskLines = t.split("\n");
    lines.push(`- [ ] ${taskLines[0]}`);
    for (let i = 1; i < taskLines.length; i++) {
      lines.push(`  ${taskLines[i]}`);
    }
  }
  lines.push("");

  lines.push("## Optional/Deferred");
  for (const t of tasks.optional) {
    const taskLines = t.split("\n");
    lines.push(`- [ ] ${taskLines[0]}`);
    for (let i = 1; i < taskLines.length; i++) {
      lines.push(`  ${taskLines[i]}`);
    }
  }
  lines.push("");

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

export function addTask(projectSlug: string, taskText: string, options: {
  priority?: Priority;
  due?: string;
  assignee?: string;
  section?: TaskSection;
  blockedBy?: string;
  spec?: string;
  dependsOn?: string[];
}): AddTaskResult {
  const projectDir = join(PROJECTS_DIR, projectSlug);
  const tasksPath = join(projectDir, "TASKS.md");
  const progressPath = join(projectDir, "progress.json");
  const yamlPath = join(projectDir, "PROJECT.yaml");

  if (!existsSync(yamlPath)) {
    return { added: false, project: projectSlug, task: taskText, section: "", metadata: {}, error: `Project not found: ${projectSlug}` };
  }

  // Load or initialize TASKS.md
  let tasks: ParsedTasks;
  if (existsSync(tasksPath)) {
    tasks = parseTasksMd(readFileSync(tasksPath, "utf-8"));
  } else {
    tasks = {
      header: `# Tasks\n\n---`,
      completed: [],
      in_progress: [],
      remaining: [],
      blocked: [],
      optional: [],
      footer: "",
    };
  }

  // Build task with metadata
  const metadataLines: string[] = [];
  const metadataObj: Record<string, string> = {};

  if (options.priority) {
    metadataLines.push(`- Priority: ${options.priority}`);
    metadataObj.priority = options.priority;
  }
  if (options.due) {
    metadataLines.push(`- Due: ${options.due}`);
    metadataObj.due = options.due;
  }
  if (options.assignee) {
    metadataLines.push(`- Assignee: ${options.assignee}`);
    metadataObj.assignee = options.assignee;
  }

  const today = new Date().toISOString().split("T")[0];
  metadataLines.push(`- Created: ${today}`);
  metadataObj.created = today;

  // Determine section
  let section = options.section || "remaining";
  if (options.blockedBy) {
    section = "blocked";
    metadataLines.push(`- Blocked by: ${options.blockedBy}`);
    metadataObj.blocked_by = options.blockedBy;
  }

  const fullTask = [taskText, ...metadataLines].join("\n");

  // Add spec and depends_on as additional metadata
  const finalLines = [taskText];
  if (options.spec) {
    finalLines.push(`- Spec: ${options.spec}`);
    metadataObj.spec = options.spec;
  }
  if (options.dependsOn && options.dependsOn.length > 0) {
    finalLines.push(`- Depends on: ${options.dependsOn.join(", ")}`);
    metadataObj.depends_on = options.dependsOn.join(", ");
  }
  finalLines.push(...metadataLines);
  const fullTaskFinal = finalLines.join("\n");

  // Add to section
  tasks[section].push(fullTaskFinal);

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

  progress.recent_activity.unshift({
    timestamp: now,
    action: "added",
    task: taskText,
  });

  if (progress.recent_activity.length > 20) {
    progress.recent_activity = progress.recent_activity.slice(0, 20);
  }

  writeFileSync(progressPath, JSON.stringify(progress, null, 2) + "\n");

  return {
    added: true,
    project: projectSlug,
    task: taskText,
    section,
    metadata: metadataObj,
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

  // Parse positional args: <project-slug> "task text"
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
    console.log(JSON.stringify({ added: false, error: "Missing required argument: <project-slug>" }));
    process.exit(1);
  }

  if (!taskText) {
    console.log(JSON.stringify({ added: false, error: "Missing required argument: task text" }));
    process.exit(1);
  }

  const priorityRaw = getArg(args, "--priority");
  let priority: Priority | undefined;
  if (priorityRaw) {
    priority = priorityRaw.toUpperCase() as Priority;
    if (!VALID_PRIORITIES.includes(priority)) {
      console.log(JSON.stringify({ added: false, error: `Invalid priority: ${priorityRaw}` }));
      process.exit(1);
    }
  }

  const sectionRaw = getArg(args, "--section");
  let section: TaskSection | undefined;
  if (sectionRaw) {
    section = sectionRaw.toLowerCase() as TaskSection;
    if (!VALID_TASK_SECTIONS.includes(section)) {
      console.log(JSON.stringify({ added: false, error: `Invalid section: ${sectionRaw}` }));
      process.exit(1);
    }
  }

  const result = addTask(projectSlug, taskText, {
    priority,
    due: getArg(args, "--due"),
    assignee: getArg(args, "--assignee"),
    section,
    blockedBy: getArg(args, "--blocked-by"),
    spec: getArg(args, "--spec"),
    dependsOn: args.reduce((acc: string[], arg, i) => {
      if (arg === "--depends-on" && i + 1 < args.length) acc.push(args[i + 1]);
      return acc;
    }, []),
  });

  console.log(JSON.stringify(result, null, 2));
  process.exit(result.added ? 0 : 1);
}

if (import.meta.main) {
  main().catch((err) => {
    console.log(JSON.stringify({ added: false, error: String(err) }));
    process.exit(1);
  });
}
