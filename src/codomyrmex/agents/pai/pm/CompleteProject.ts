#!/usr/bin/env bun
/**
 * CompleteProject.ts - Mark a project as completed with final validation
 *
 * Validates that tasks and success criteria are satisfied before
 * marking a bounded project as COMPLETED.
 *
 * Usage:
 *   bun ~/.claude/skills/PAI/Tools/CompleteProject.ts <slug> [options]
 *   bun ~/.claude/skills/PAI/Tools/CompleteProject.ts --help
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

// ============================================================================
// Help
// ============================================================================

function showHelp(): void {
  console.log(`
CompleteProject - Mark a project as completed with final validation

USAGE:
  bun ~/.claude/skills/PAI/Tools/CompleteProject.ts <slug> [options]

ARGUMENTS:
  <slug>              Project identifier (required)

OPTIONS:
  --force             Complete even if tasks remain uncompleted
  --summary "..."     Completion summary (added to progress.json)
  --help, -h          Show this help message

EXAMPLES:
  bun ~/.claude/skills/PAI/Tools/CompleteProject.ts my-project
  bun ~/.claude/skills/PAI/Tools/CompleteProject.ts my-project --force
  bun ~/.claude/skills/PAI/Tools/CompleteProject.ts my-project --summary "All features shipped and tested"

OUTPUT:
  JSON: { "completed": true, "unmet_criteria": [...], "remaining_tasks": N, "project": {...} }

VALIDATION:
  Without --force, warns if:
  - Tasks remain in "Remaining" or "In Progress" sections
  - Success criteria exist that haven't been explicitly marked as achieved
  The project will still be completed, but warnings are surfaced in the output.
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
// TASKS.md Parsing
// ============================================================================

interface TaskCounts {
  completed: number;
  in_progress: number;
  remaining: number;
  blocked: number;
  optional: number;
}

function countTaskSections(content: string): TaskCounts {
  const counts: TaskCounts = { completed: 0, in_progress: 0, remaining: 0, blocked: 0, optional: 0 };
  let currentSection: keyof TaskCounts | null = null;

  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    const lower = trimmed.toLowerCase();

    if (lower.startsWith("## completed")) { currentSection = "completed"; continue; }
    if (lower.startsWith("## in progress")) { currentSection = "in_progress"; continue; }
    if (lower.startsWith("## remaining")) { currentSection = "remaining"; continue; }
    if (lower.startsWith("## blocked")) { currentSection = "blocked"; continue; }
    if (lower.startsWith("## optional") || lower.startsWith("## deferred") || lower.startsWith("## skipped")) { currentSection = "optional"; continue; }
    if (lower.startsWith("## summary")) { currentSection = null; continue; }

    if (currentSection && (trimmed.startsWith("- [") || trimmed.startsWith("- "))) {
      // Only count actual task items, not sub-items
      if (!line.startsWith("    ") && !line.startsWith("\t\t")) {
        counts[currentSection]++;
      }
    }
  }

  return counts;
}

// ============================================================================
// YAML Writing
// ============================================================================

function writeProjectYaml(projectDir: string, yaml: Record<string, any>): void {
  const lines: string[] = [];

  if (yaml.title) lines.push(`# ${yaml.title}`);
  lines.push(``);

  const orderedKeys = ["id", "title", "status", "created", "completed", "target", "goal", "blocked_by", "paused_reason"];
  for (const key of orderedKeys) {
    if (yaml[key] !== undefined && yaml[key] !== null && yaml[key] !== "") {
      const val = yaml[key];
      if (typeof val === "string" && !["id", "status", "created", "completed", "target", "priority"].includes(key)) {
        lines.push(`${key}: "${val}"`);
      } else {
        lines.push(`${key}: ${val}`);
      }
    }
  }

  if (yaml.success_criteria && Array.isArray(yaml.success_criteria)) {
    lines.push(``);
    lines.push(`success_criteria:`);
    for (const c of yaml.success_criteria) {
      lines.push(`  - "${c}"`);
    }
  }

  if (yaml.tags && Array.isArray(yaml.tags) && yaml.tags.length > 0) {
    lines.push(``);
    lines.push(`tags:`);
    for (const t of yaml.tags) {
      lines.push(`  - ${t}`);
    }
  }

  if (yaml.priority) {
    lines.push(``);
    lines.push(`priority: ${yaml.priority}`);
  }

  if (yaml.parent_role) {
    lines.push(`parent_role: "${yaml.parent_role}"`);
  }

  if (yaml.outcome) {
    lines.push(``);
    lines.push(`outcome: |`);
    for (const line of String(yaml.outcome).split("\n")) {
      lines.push(`  ${line}`);
    }
  }

  if (yaml.notes) {
    lines.push(``);
    lines.push(`notes: |`);
    for (const line of String(yaml.notes).split("\n")) {
      lines.push(`  ${line}`);
    }
  }

  lines.push(``);
  writeFileSync(join(projectDir, "PROJECT.yaml"), lines.join("\n"));
}

// ============================================================================
// Core Functions
// ============================================================================

export function completeProject(slug: string, options: {
  force?: boolean;
  summary?: string;
}): {
  completed: boolean;
  unmet_criteria: string[];
  remaining_tasks: number;
  in_progress_tasks: number;
  blocked_tasks: number;
  project?: Record<string, any>;
  error?: string;
  warnings: string[];
} {
  const projectDir = join(PROJECTS_DIR, slug);
  const yamlPath = join(projectDir, "PROJECT.yaml");
  const tasksPath = join(projectDir, "TASKS.md");
  const progressPath = join(projectDir, "progress.json");

  if (!existsSync(yamlPath)) {
    return {
      completed: false,
      unmet_criteria: [],
      remaining_tasks: 0,
      in_progress_tasks: 0,
      blocked_tasks: 0,
      error: `Project not found: ${slug}`,
      warnings: [],
    };
  }

  // Load data
  const yamlContent = readFileSync(yamlPath, "utf-8");
  const yaml = parseSimpleYaml(yamlContent);

  if (yaml.status === "COMPLETED") {
    return {
      completed: false,
      unmet_criteria: [],
      remaining_tasks: 0,
      in_progress_tasks: 0,
      blocked_tasks: 0,
      error: `Project already completed: ${slug}`,
      warnings: [],
    };
  }

  // Count tasks
  let taskCounts: TaskCounts = { completed: 0, in_progress: 0, remaining: 0, blocked: 0, optional: 0 };
  if (existsSync(tasksPath)) {
    const tasksContent = readFileSync(tasksPath, "utf-8");
    taskCounts = countTaskSections(tasksContent);
  }

  const warnings: string[] = [];

  // Validate remaining tasks
  const remaining = taskCounts.remaining;
  const inProgress = taskCounts.in_progress;
  const blocked = taskCounts.blocked;

  if (remaining > 0) {
    warnings.push(`${remaining} task(s) still in Remaining`);
  }
  if (inProgress > 0) {
    warnings.push(`${inProgress} task(s) still In Progress`);
  }
  if (blocked > 0) {
    warnings.push(`${blocked} task(s) still Blocked`);
  }

  // Check success criteria
  const criteria = Array.isArray(yaml.success_criteria) ? yaml.success_criteria : [];
  const unmetCriteria = criteria.filter((c: string) => !c.includes("ACHIEVED") && !c.includes("achieved") && !c.includes("✓") && !c.includes("[x]"));

  if (unmetCriteria.length > 0 && !options.force) {
    warnings.push(`${unmetCriteria.length} success criteria not explicitly marked as achieved`);
  }

  // Proceed with completion
  const now = new Date().toISOString();
  const today = now.split("T")[0];

  yaml.status = "COMPLETED";
  yaml.completed = today;

  // Remove blocked_by and paused_reason
  delete yaml.blocked_by;
  delete yaml.paused_reason;

  writeProjectYaml(projectDir, yaml);

  // Update progress.json
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

  progress.last_updated = now;
  progress.completion_percentage = 100;
  progress.task_counts = taskCounts;

  const activityEntry: any = {
    timestamp: now,
    action: "completed",
    task: options.summary || `Project completed: ${yaml.title || slug}`,
  };
  progress.recent_activity.unshift(activityEntry);

  // Keep only last 20 entries
  if (progress.recent_activity.length > 20) {
    progress.recent_activity = progress.recent_activity.slice(0, 20);
  }

  writeFileSync(progressPath, JSON.stringify(progress, null, 2) + "\n");

  // Update parent mission's progress if project has parent_mission
  if (yaml.parent_mission) {
    const missionsDir = join(PAI_DIR, "MEMORY", "STATE", "missions");
    const missionProgressPath = join(missionsDir, yaml.parent_mission, "progress.json");

    if (existsSync(missionProgressPath)) {
      try {
        const missionProgress = JSON.parse(readFileSync(missionProgressPath, "utf-8"));
        if (!missionProgress.recent_activity) missionProgress.recent_activity = [];

        // Update project status in mission
        if (!missionProgress.project_statuses) missionProgress.project_statuses = {};
        missionProgress.project_statuses[slug] = "COMPLETED";

        // Recalculate aggregate completion from all linked projects
        const missionYamlPath = join(missionsDir, yaml.parent_mission, "MISSION.yaml");
        if (existsSync(missionYamlPath)) {
          const missionYaml = parseSimpleYaml(readFileSync(missionYamlPath, "utf-8"));
          const linkedProjects: string[] = Array.isArray(missionYaml.linked_projects) ? missionYaml.linked_projects : [];
          let totalCompletion = 0;
          let validCount = 0;

          for (const pSlug of linkedProjects) {
            const pProgressPath = join(PROJECTS_DIR, pSlug, "progress.json");
            if (existsSync(pProgressPath)) {
              try {
                const pProgress = JSON.parse(readFileSync(pProgressPath, "utf-8"));
                totalCompletion += pProgress.completion_percentage || 0;
                validCount++;
              } catch { /* skip */ }
            }
          }

          missionProgress.aggregate_completion = validCount > 0 ? Math.round(totalCompletion / validCount) : 0;
        }

        missionProgress.recent_activity.unshift({
          timestamp: now,
          action: "project_completed",
          detail: `Project completed: ${yaml.title || slug}`,
        });
        missionProgress.last_updated = now;

        if (missionProgress.recent_activity.length > 20) {
          missionProgress.recent_activity = missionProgress.recent_activity.slice(0, 20);
        }

        writeFileSync(missionProgressPath, JSON.stringify(missionProgress, null, 2) + "\n");
      } catch { /* ignore mission update errors */ }
    }
  }

  return {
    completed: true,
    unmet_criteria: unmetCriteria,
    remaining_tasks: remaining,
    in_progress_tasks: inProgress,
    blocked_tasks: blocked,
    project: {
      id: yaml.id || slug,
      title: yaml.title,
      status: "COMPLETED",
      created: yaml.created,
      completed: today,
      priority: yaml.priority,
    },
    warnings,
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

  const slug = args.find(a => !a.startsWith("--") && !a.startsWith("-"));

  if (!slug) {
    console.log(JSON.stringify({ completed: false, error: "Missing required argument: <slug>" }));
    process.exit(1);
  }

  const force = hasFlag(args, "--force");
  const summary = getArg(args, "--summary");

  const result = completeProject(slug, { force, summary });

  console.log(JSON.stringify(result, null, 2));
  process.exit(result.completed ? 0 : 1);
}

if (import.meta.main) {
  main().catch((err) => {
    console.log(JSON.stringify({ completed: false, error: String(err) }));
    process.exit(1);
  });
}
