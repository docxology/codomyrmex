#!/usr/bin/env bun
/**
 * UpdateMission.ts - Update mission metadata, links, or log activity
 *
 * Modifies an existing mission's MISSION.yaml and progress.json.
 * Supports bidirectional project linking (updates both mission and project).
 *
 * Usage:
 *   bun ~/.claude/skills/PAI/Tools/UpdateMission.ts <slug> [options]
 *   bun ~/.claude/skills/PAI/Tools/UpdateMission.ts --help
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
const MISSIONS_DIR = join(PAI_DIR, "MEMORY", "STATE", "missions");
const PROJECTS_DIR = join(PAI_DIR, "MEMORY", "STATE", "projects");

import { type MissionStatus, type Priority, VALID_MISSION_STATUSES, VALID_PRIORITIES } from "./DataModels.ts";
import { parseSimpleYaml, writeYamlFile } from "./YamlUtils.ts";

interface UpdateMissionResult {
  updated: boolean;
  changes: string[];
  mission?: Record<string, any>;
  error?: string;
}

// ============================================================================
// Help
// ============================================================================

function showHelp(): void {
  console.log(`
UpdateMission - Update mission metadata, links, or log activity

USAGE:
  bun ~/.claude/skills/PAI/Tools/UpdateMission.ts <slug> [options]

ARGUMENTS:
  <slug>                        Mission identifier (required)

METADATA OPTIONS:
  --status STATUS               Change status (ACTIVE, PAUSED, COMPLETED, ARCHIVED)
  --title "..."                 Update title
  --description "..."           Update description
  --vision "..."                Update vision statement
  --priority HIGH|MEDIUM|LOW    Update priority
  --parent-goal M0|M1|M2        Update TELOS goal link
  --add-criteria "text"         Add a success criterion

LINKING OPTIONS:
  --link-project <slug>         Link a project to this mission (bidirectional)
  --unlink-project <slug>       Unlink a project from this mission (bidirectional)

ACTIVITY OPTIONS:
  --log "message"               Add activity entry to progress.json

GENERAL OPTIONS:
  --help, -h                    Show this help message

EXAMPLES:
  bun ~/.claude/skills/PAI/Tools/UpdateMission.ts my-mission --status PAUSED
  bun ~/.claude/skills/PAI/Tools/UpdateMission.ts my-mission --link-project my-project
  bun ~/.claude/skills/PAI/Tools/UpdateMission.ts my-mission --unlink-project old-project
  bun ~/.claude/skills/PAI/Tools/UpdateMission.ts my-mission --log "Quarterly review complete"

OUTPUT:
  JSON: { "updated": true, "changes": [...], "mission": {...} }
`);
  process.exit(0);
}

// ============================================================================
// YAML Parsing & Writing
// ============================================================================

function writeMissionYaml(missionDir: string, yaml: Record<string, any>): void {
  writeYamlFile(join(missionDir, "MISSION.yaml"), yaml, {
    title: yaml.title,
    orderedKeys: ["id", "title", "status", "created", "completed", "priority", "parent_goal", "description"],
    multiLineKeys: ["vision"]
  });
}

function writeProjectYaml(projectDir: string, yaml: Record<string, any>): void {
  writeYamlFile(join(projectDir, "PROJECT.yaml"), yaml, {
    title: yaml.title,
    orderedKeys: ["id", "title", "status", "created", "completed", "target", "goal", "blocked_by", "paused_reason", "parent_role", "parent_mission"],
    multiLineKeys: ["outcome", "notes"]
  });
}

// ============================================================================
// Progress Aggregation
// ============================================================================

function aggregateMissionProgress(missionYaml: Record<string, any>): {
  linked_project_count: number;
  aggregate_completion: number;
  project_statuses: Record<string, string>;
} {
  const linkedProjects: string[] = Array.isArray(missionYaml.linked_projects) ? missionYaml.linked_projects : [];
  const projectStatuses: Record<string, string> = {};
  let totalCompletion = 0;
  let validCount = 0;

  for (const projectSlug of linkedProjects) {
    const progressPath = join(PROJECTS_DIR, projectSlug, "progress.json");
    const yamlPath = join(PROJECTS_DIR, projectSlug, "PROJECT.yaml");

    if (existsSync(yamlPath)) {
      const projYaml = parseSimpleYaml(readFileSync(yamlPath, "utf-8"));
      projectStatuses[projectSlug] = projYaml.status || "UNKNOWN";
    }

    if (existsSync(progressPath)) {
      try {
        const progress = JSON.parse(readFileSync(progressPath, "utf-8"));
        totalCompletion += progress.completion_percentage || 0;
        validCount++;
      } catch {
        // skip invalid
      }
    }
  }

  return {
    linked_project_count: linkedProjects.length,
    aggregate_completion: validCount > 0 ? Math.round(totalCompletion / validCount) : 0,
    project_statuses: projectStatuses,
  };
}

// ============================================================================
// Core Functions
// ============================================================================

function getISOTimestamp(): string {
  return new Date().toISOString();
}

export function updateMission(slug: string, options: {
  status?: MissionStatus;
  title?: string;
  description?: string;
  vision?: string;
  priority?: Priority;
  parentGoal?: string;
  addCriteria?: string;
  linkProject?: string;
  unlinkProject?: string;
  log?: string;
}): UpdateMissionResult {
  const missionDir = join(MISSIONS_DIR, slug);
  const yamlPath = join(missionDir, "MISSION.yaml");
  const progressPath = join(missionDir, "progress.json");

  if (!existsSync(yamlPath)) {
    return { updated: false, changes: [], error: `Mission not found: ${slug}` };
  }

  // Load existing data
  const yamlContent = readFileSync(yamlPath, "utf-8");
  const yaml = parseSimpleYaml(yamlContent);

  let progress: any = {};
  if (existsSync(progressPath)) {
    try {
      progress = JSON.parse(readFileSync(progressPath, "utf-8"));
    } catch {
      progress = { mission_id: slug, recent_activity: [] };
    }
  } else {
    progress = { mission_id: slug, recent_activity: [] };
  }

  if (!progress.recent_activity) progress.recent_activity = [];
  if (!Array.isArray(yaml.linked_projects)) yaml.linked_projects = [];

  const changes: string[] = [];
  const now = getISOTimestamp();
  let yamlModified = false;

  // Apply metadata changes
  if (options.status) {
    if (!VALID_MISSION_STATUSES.includes(options.status)) {
      return { updated: false, changes: [], error: `Invalid status: ${options.status}` };
    }
    const oldStatus = yaml.status;
    yaml.status = options.status;
    if (options.status === "COMPLETED") {
      yaml.completed = new Date().toISOString().split("T")[0];
    }
    changes.push(`status: ${oldStatus} -> ${options.status}`);
    yamlModified = true;
  }

  if (options.title) {
    yaml.title = options.title;
    changes.push(`title updated to "${options.title}"`);
    yamlModified = true;
  }

  if (options.description) {
    yaml.description = options.description;
    changes.push(`description updated`);
    yamlModified = true;
  }

  if (options.vision) {
    yaml.vision = options.vision;
    changes.push(`vision updated`);
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

  if (options.parentGoal) {
    yaml.parent_goal = options.parentGoal;
    changes.push(`parent_goal set to ${options.parentGoal}`);
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

  // Link project (bidirectional)
  if (options.linkProject) {
    const projectSlug = options.linkProject;
    const projectDir = join(PROJECTS_DIR, projectSlug);
    const projectYamlPath = join(projectDir, "PROJECT.yaml");

    if (!existsSync(projectYamlPath)) {
      return { updated: false, changes: [], error: `Project not found: ${projectSlug}` };
    }

    // Add to mission's linked_projects if not already there
    if (!yaml.linked_projects.includes(projectSlug)) {
      yaml.linked_projects.push(projectSlug);
      yamlModified = true;
      changes.push(`linked project: ${projectSlug}`);

      // Update project's parent_mission field
      const projectYamlContent = readFileSync(projectYamlPath, "utf-8");
      const projectYaml = parseSimpleYaml(projectYamlContent);
      projectYaml.parent_mission = slug;
      writeProjectYaml(projectDir, projectYaml);

      progress.recent_activity.unshift({
        timestamp: now,
        action: "linked",
        detail: `Linked project: ${projectSlug}`,
      });
    } else {
      changes.push(`project already linked: ${projectSlug}`);
    }
  }

  // Unlink project (bidirectional)
  if (options.unlinkProject) {
    const projectSlug = options.unlinkProject;
    const idx = yaml.linked_projects.indexOf(projectSlug);

    if (idx !== -1) {
      yaml.linked_projects.splice(idx, 1);
      yamlModified = true;
      changes.push(`unlinked project: ${projectSlug}`);

      // Remove parent_mission from project
      const projectDir = join(PROJECTS_DIR, projectSlug);
      const projectYamlPath = join(projectDir, "PROJECT.yaml");
      if (existsSync(projectYamlPath)) {
        const projectYamlContent = readFileSync(projectYamlPath, "utf-8");
        const projectYaml = parseSimpleYaml(projectYamlContent);
        delete projectYaml.parent_mission;
        writeProjectYaml(projectDir, projectYaml);
      }

      progress.recent_activity.unshift({
        timestamp: now,
        action: "unlinked",
        detail: `Unlinked project: ${projectSlug}`,
      });
    } else {
      changes.push(`project not linked: ${projectSlug}`);
    }
  }

  // Log activity
  if (options.log) {
    progress.recent_activity.unshift({
      timestamp: now,
      action: "log",
      detail: options.log,
    });
    changes.push(`logged: "${options.log}"`);
  }

  // Recalculate aggregate progress
  const aggregated = aggregateMissionProgress(yaml);
  progress.linked_project_count = aggregated.linked_project_count;
  progress.aggregate_completion = aggregated.aggregate_completion;
  progress.project_statuses = aggregated.project_statuses;
  progress.last_updated = now;

  // Keep only last 20 activity entries
  if (progress.recent_activity.length > 20) {
    progress.recent_activity = progress.recent_activity.slice(0, 20);
  }

  // Write files
  if (yamlModified) {
    writeMissionYaml(missionDir, yaml);
  }

  writeFileSync(progressPath, JSON.stringify(progress, null, 2) + "\n");

  return {
    updated: true,
    changes,
    mission: {
      id: yaml.id || slug,
      title: yaml.title,
      status: yaml.status,
      priority: yaml.priority,
      linked_projects: yaml.linked_projects,
      aggregate_completion: aggregated.aggregate_completion,
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

  const slug = args.find(a => !a.startsWith("--") && !a.startsWith("-"));

  if (!slug) {
    console.log(JSON.stringify({ updated: false, changes: [], error: "Missing required argument: <slug>" }));
    process.exit(1);
  }

  const statusRaw = getArg(args, "--status");
  let status: MissionStatus | undefined;
  if (statusRaw) {
    status = statusRaw.toUpperCase() as MissionStatus;
  }

  const priorityRaw = getArg(args, "--priority");
  let priority: Priority | undefined;
  if (priorityRaw) {
    priority = priorityRaw.toUpperCase() as Priority;
  }

  const result = updateMission(slug, {
    status,
    title: getArg(args, "--title"),
    description: getArg(args, "--description"),
    vision: getArg(args, "--vision"),
    priority,
    parentGoal: getArg(args, "--parent-goal"),
    addCriteria: getArg(args, "--add-criteria"),
    linkProject: getArg(args, "--link-project"),
    unlinkProject: getArg(args, "--unlink-project"),
    log: getArg(args, "--log"),
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
