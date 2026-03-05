#!/usr/bin/env bun
/**
 * UpdateProject.ts - Update project metadata, status, or tasks
 *
 * Modifies an existing bounded project's PROJECT.yaml, TASKS.md,
 * and progress.json based on the requested changes.
 *
 * Usage:
 *   bun ~/.claude/skills/PAI/Tools/UpdateProject.ts <slug> [options]
 *   bun ~/.claude/skills/PAI/Tools/UpdateProject.ts --help
 *
 * @author PAI System
 * @version 1.0.0
 */

import { existsSync, readFileSync, appendFileSync, writeFileSync } from "fs";
import { join } from "path";
import { homedir } from "os";

// ============================================================================
// Constants
// ============================================================================

const HOME = process.env.HOME || homedir();
const PAI_DIR = process.env.PAI_DIR || join(HOME, ".claude");
const PROJECTS_DIR = join(PAI_DIR, "MEMORY", "STATE", "projects");

import { type ProjectStatus, type Priority, type TaskSection, VALID_PRIORITIES, VALID_PROJECT_STATUSES, VALID_TASK_SECTIONS } from "./DataModels.ts";
import { parseSimpleYaml, writeYamlFile } from "./YamlUtils.ts";

interface UpdateResult {
  updated: boolean;
  changes: string[];
  project?: Record<string, any>;
  error?: string;
}

// ============================================================================
// Help
// ============================================================================

function showHelp(): void {
  console.log(`
UpdateProject - Update project metadata, status, or tasks

USAGE:
  bun ~/.claude/skills/PAI/Tools/UpdateProject.ts <slug> [options]

ARGUMENTS:
  <slug>                       Project identifier (required)

METADATA OPTIONS:
  --status STATUS              Change project status (PLANNING, IN_PROGRESS, COMPLETED, PAUSED, BLOCKED)
  --title "..."                Update title
  --goal "..."                 Update goal
  --target YYYY-MM-DD          Update target date
  --priority HIGH|MEDIUM|LOW   Update priority
  --blocked-by "reason"        Set blocked_by (auto-sets status to BLOCKED)
  --add-criteria "text"        Add a success criterion

TASK OPTIONS:
  --add-task "text"            Add a new task
  --section remaining|in_progress|blocked|optional  Section for --add-task (default: remaining)
  --complete-task "text"       Mark a task as completed (moves to Completed section)
  --block-task "text"          Move a task to Blocked section
  --start-task "text"          Move a task to In Progress section

ACTIVITY OPTIONS:
  --log "message"              Add activity entry to progress.json

GENERAL OPTIONS:
  --help, -h                   Show this help message

EXAMPLES:
  bun ~/.claude/skills/PAI/Tools/UpdateProject.ts my-project --status IN_PROGRESS
  bun ~/.claude/skills/PAI/Tools/UpdateProject.ts my-project --add-task "Implement feature X"
  bun ~/.claude/skills/PAI/Tools/UpdateProject.ts my-project --complete-task "Implement feature X"
  bun ~/.claude/skills/PAI/Tools/UpdateProject.ts my-project --log "Finished initial prototype"
  bun ~/.claude/skills/PAI/Tools/UpdateProject.ts my-project --add-task "Deploy" --section blocked --blocked-by "Waiting for API key"

OUTPUT:
  JSON: { "updated": true, "changes": [...], "project": {...} }
`);
  process.exit(0);
}

// ============================================================================
// YAML Parsing & Writing
// ============================================================================

function writeProjectYaml(projectDir: string, yaml: Record<string, any>): void {
  writeYamlFile(join(projectDir, "PROJECT.yaml"), yaml, {
    title: yaml.title,
    orderedKeys: ["id", "title", "status", "created", "goal", "target", "parent_mission", "parent_role", "completed"]
  });
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
  const footerLines: string[] = [];
  let foundFirstSection = false;
  let inFooter = false;

  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    const lower = trimmed.toLowerCase();

    // Detect section headers
    if (lower.startsWith("## completed")) {
      currentSection = "completed";
      foundFirstSection = true;
      continue;
    } else if (lower.startsWith("## in progress")) {
      currentSection = "in_progress";
      foundFirstSection = true;
      continue;
    } else if (lower.startsWith("## remaining")) {
      currentSection = "remaining";
      foundFirstSection = true;
      continue;
    } else if (lower.startsWith("## blocked")) {
      currentSection = "blocked";
      foundFirstSection = true;
      continue;
    } else if (lower.startsWith("## optional") || lower.startsWith("## deferred") || lower.startsWith("## skipped")) {
      currentSection = "optional";
      foundFirstSection = true;
      continue;
    } else if (lower.startsWith("## summary") || (trimmed === "---" && currentSection && foundFirstSection)) {
      if (lower.startsWith("## summary")) {
        inFooter = true;
        currentSection = null;
        footerLines.push(line);
        continue;
      }
      // A --- separator: if we're past a section, could be footer
      if (inFooter) {
        footerLines.push(line);
        continue;
      }
      // Just a section separator
      continue;
    }

    if (inFooter) {
      footerLines.push(line);
      continue;
    }

    if (!foundFirstSection) {
      headerLines.push(line);
      continue;
    }

    // Parse task items
    if (currentSection && (trimmed.startsWith("- [") || trimmed.startsWith("- "))) {
      // Extract the task text
      let taskText = trimmed;
      if (trimmed.startsWith("- [x] ")) {
        taskText = trimmed.slice(6);
      } else if (trimmed.startsWith("- [ ] ")) {
        taskText = trimmed.slice(6);
      } else if (trimmed.startsWith("- [~] ")) {
        taskText = trimmed.slice(6);
      } else if (trimmed.startsWith("- ")) {
        taskText = trimmed.slice(2);
      }

      result[currentSection].push(taskText);
    }
  }

  result.header = headerLines.join("\n");
  result.footer = footerLines.join("\n");
  return result;
}

function writeTasksMd(projectDir: string, tasks: ParsedTasks): void {
  const lines: string[] = [];

  // Header
  lines.push(tasks.header.trimEnd());
  lines.push("");

  // Completed
  lines.push("## Completed");
  if (tasks.completed.length > 0) {
    for (const t of tasks.completed) {
      lines.push(`- [x] ${t}`);
    }
  }
  lines.push("");

  // In Progress
  lines.push("## In Progress");
  if (tasks.in_progress.length > 0) {
    for (const t of tasks.in_progress) {
      lines.push(`- [ ] ${t}`);
    }
  }
  lines.push("");

  // Remaining
  lines.push("## Remaining");
  if (tasks.remaining.length > 0) {
    for (const t of tasks.remaining) {
      lines.push(`- [ ] ${t}`);
    }
  }
  lines.push("");

  // Blocked
  lines.push("## Blocked");
  if (tasks.blocked.length > 0) {
    for (const t of tasks.blocked) {
      lines.push(`- [ ] ${t}`);
    }
  }
  lines.push("");

  // Optional/Deferred
  lines.push("## Optional/Deferred");
  if (tasks.optional.length > 0) {
    for (const t of tasks.optional) {
      lines.push(`- [ ] ${t}`);
    }
  }
  lines.push("");

  // Footer
  lines.push("---");
  lines.push("");
  lines.push(`*Updated: ${new Date().toISOString().split("T")[0]}*`);
  lines.push("");

  writeFileSync(join(projectDir, "TASKS.md"), lines.join("\n"));
}

// ============================================================================
// Core Functions
// ============================================================================

function getISOTimestamp(): string {
  return new Date().toISOString();
}

function removeTaskFromAllSections(tasks: ParsedTasks, taskText: string): boolean {
  const normalizedTarget = taskText.toLowerCase().trim();
  let found = false;

  for (const section of ["completed", "in_progress", "remaining", "blocked", "optional"] as const) {
    const idx = tasks[section].findIndex(t => t.toLowerCase().trim() === normalizedTarget);
    if (idx !== -1) {
      tasks[section].splice(idx, 1);
      found = true;
    }
  }

  // Also try partial matching (contains)
  if (!found) {
    for (const section of ["completed", "in_progress", "remaining", "blocked", "optional"] as const) {
      const idx = tasks[section].findIndex(t => t.toLowerCase().includes(normalizedTarget) || normalizedTarget.includes(t.toLowerCase()));
      if (idx !== -1) {
        tasks[section].splice(idx, 1);
        found = true;
        break;
      }
    }
  }

  return found;
}

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

export function updateProject(slug: string, options: {
  status?: ProjectStatus;
  title?: string;
  goal?: string;
  target?: string;
  priority?: Priority;
  blockedBy?: string;
  addTask?: string;
  section?: TaskSection;
  completeTask?: string;
  blockTask?: string;
  startTask?: string;
  log?: string;
  addCriteria?: string;
}): UpdateResult {
  const projectDir = join(PROJECTS_DIR, slug);
  const yamlPath = join(projectDir, "PROJECT.yaml");
  const tasksPath = join(projectDir, "TASKS.md");
  const progressPath = join(projectDir, "progress.json");

  if (!existsSync(yamlPath)) {
    return { updated: false, changes: [], error: `Project not found: ${slug}` };
  }

  // Load existing data
  const yamlContent = readFileSync(yamlPath, "utf-8");
  const yaml = parseSimpleYaml(yamlContent);

  let tasksContent = "";
  let tasks: ParsedTasks;
  if (existsSync(tasksPath)) {
    tasksContent = readFileSync(tasksPath, "utf-8");
    tasks = parseTasksMd(tasksContent);
  } else {
    tasks = {
      header: `# ${yaml.title || slug} Tasks\n\n${yaml.goal || ""}\n\n---`,
      completed: [],
      in_progress: [],
      remaining: [],
      blocked: [],
      optional: [],
      footer: "",
    };
  }

  let progress: any = {};
  if (existsSync(progressPath)) {
    try {
      progress = JSON.parse(readFileSync(progressPath, "utf-8"));
    } catch {
      progress = { project_id: slug, recent_activity: [] };
    }
  } else {
    progress = { project_id: slug, recent_activity: [] };
  }

  if (!progress.recent_activity) progress.recent_activity = [];

  const changes: string[] = [];
  const now = getISOTimestamp();
  let yamlModified = false;
  let tasksModified = false;

  // Apply metadata changes
  if (options.status) {
    if (!VALID_PROJECT_STATUSES.includes(options.status)) {
      return { updated: false, changes: [], error: `Invalid status: ${options.status}` };
    }
    const oldStatus = yaml.status;
    yaml.status = options.status;
    changes.push(`status: ${oldStatus} → ${options.status}`);
    yamlModified = true;
  }

  if (options.title) {
    yaml.title = options.title;
    changes.push(`title updated to "${options.title}"`);
    yamlModified = true;
  }

  if (options.goal) {
    yaml.goal = options.goal;
    changes.push(`goal updated`);
    yamlModified = true;
  }

  if (options.target) {
    yaml.target = options.target;
    changes.push(`target set to ${options.target}`);
    yamlModified = true;
  }

  if (options.priority) {
    if (!VALID_PRIORITIES.includes(options.priority)) {
      return { updated: false, changes: [], error: `Invalid priority: ${options.priority}` };
    }
    yaml.priority = options.priority;
    changes.push(`priority set to ${options.priority}`);
    yamlModified = true;
  }

  if (options.blockedBy) {
    yaml.blocked_by = options.blockedBy;
    yaml.status = "BLOCKED";
    changes.push(`blocked by: ${options.blockedBy}`);
    yamlModified = true;
  }

  if (options.addCriteria) {
    if (!Array.isArray(yaml.success_criteria)) {
      yaml.success_criteria = [];
    }
    yaml.success_criteria.push(options.addCriteria);
    changes.push(`added criterion: "${options.addCriteria}"`);
    yamlModified = true;
  }

  // Apply task changes
  if (options.addTask) {
    const section = options.section || "remaining";
    tasks[section].push(options.addTask);
    changes.push(`added task to ${section}: "${options.addTask}"`);
    tasksModified = true;
    progress.recent_activity.unshift({
      timestamp: now,
      action: "added",
      task: options.addTask,
    });
  }

  if (options.completeTask) {
    const removed = removeTaskFromAllSections(tasks, options.completeTask);
    if (removed) {
      tasks.completed.push(options.completeTask);
      changes.push(`completed task: "${options.completeTask}"`);
    } else {
      // Task not found in any section - add to completed anyway
      tasks.completed.push(options.completeTask);
      changes.push(`added completed task: "${options.completeTask}"`);
    }
    tasksModified = true;
    progress.recent_activity.unshift({
      timestamp: now,
      action: "completed",
      task: options.completeTask,
    });
  }

  if (options.blockTask) {
    const removed = removeTaskFromAllSections(tasks, options.blockTask);
    const blockText = options.blockedBy
      ? `${options.blockTask}\n  - Blocked by: ${options.blockedBy}`
      : options.blockTask;
    tasks.blocked.push(blockText);
    changes.push(`blocked task: "${options.blockTask}"`);
    tasksModified = true;
    progress.recent_activity.unshift({
      timestamp: now,
      action: "blocked",
      task: options.blockTask,
    });
  }

  if (options.startTask) {
    removeTaskFromAllSections(tasks, options.startTask);
    tasks.in_progress.push(options.startTask);
    changes.push(`started task: "${options.startTask}"`);
    tasksModified = true;
    progress.recent_activity.unshift({
      timestamp: now,
      action: "started",
      task: options.startTask,
    });
  }

  if (options.log) {
    progress.recent_activity.unshift({
      timestamp: now,
      action: "log",
      task: options.log,
    });
    changes.push(`logged: "${options.log}"`);
  }

  // Recalculate progress
  const { task_counts, completion_percentage } = recalculateProgress(tasks);
  progress.task_counts = task_counts;
  progress.completion_percentage = completion_percentage;
  progress.last_updated = now;

  // Keep only last 20 activity entries
  if (progress.recent_activity.length > 20) {
    progress.recent_activity = progress.recent_activity.slice(0, 20);
  }

  // Write files
  if (yamlModified) {
    writeProjectYaml(projectDir, yaml);
  }

  if (tasksModified) {
    writeTasksMd(projectDir, tasks);
  }

  // Always write progress.json (updated timestamp + counts)
  writeFileSync(progressPath, JSON.stringify(progress, null, 2) + "\n");

  return {
    updated: true,
    changes,
    project: {
      id: yaml.id || slug,
      title: yaml.title,
      status: yaml.status,
      priority: yaml.priority,
      completion_percentage,
      task_counts,
    },
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

  // Parse slug (first positional argument)
  const slug = args.find(a => !a.startsWith("--") && !a.startsWith("-"));

  if (!slug) {
    console.log(JSON.stringify({ updated: false, changes: [], error: "Missing required argument: <slug>" }));
    process.exit(1);
  }

  const statusRaw = getArg(args, "--status");
  let status: ProjectStatus | undefined;
  if (statusRaw) {
    status = statusRaw.toUpperCase() as ProjectStatus;
  }

  const priorityRaw = getArg(args, "--priority");
  let priority: Priority | undefined;
  if (priorityRaw) {
    priority = priorityRaw.toUpperCase() as Priority;
  }

  const sectionRaw = getArg(args, "--section");
  let section: TaskSection | undefined;
  if (sectionRaw) {
    section = sectionRaw.toLowerCase() as TaskSection;
  }

  const result = updateProject(slug, {
    status,
    title: getArg(args, "--title"),
    goal: getArg(args, "--goal"),
    target: getArg(args, "--target"),
    priority,
    blockedBy: getArg(args, "--blocked-by"),
    addTask: getArg(args, "--add-task"),
    section,
    completeTask: getArg(args, "--complete-task"),
    blockTask: getArg(args, "--block-task"),
    startTask: getArg(args, "--start-task"),
    log: getArg(args, "--log"),
    addCriteria: getArg(args, "--add-criteria"),
  });

  console.log(JSON.stringify(result, null, 2));
  process.exit(result.updated ? 0 : 1);
}

if (import.meta.main) {
  main().catch((err) => {
    console.log(JSON.stringify({ updated: false, changes: [], error: String(err) }));
    process.exit(1);
  });
}
