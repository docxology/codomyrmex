#!/usr/bin/env bun
/**
 * CreateProject.ts - Scaffold a new bounded project
 *
 * Creates a new bounded project directory with PROJECT.yaml, TASKS.md,
 * and progress.json following the PAI Project Ontology schema.
 *
 * Usage:
 *   bun ~/.claude/skills/PAI/Tools/CreateProject.ts <slug> --title "Title" --goal "Goal" [options]
 *   bun ~/.claude/skills/PAI/Tools/CreateProject.ts --help
 *
 * @author PAI System
 * @version 1.0.0
 */

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "fs";
import { join } from "path";
import { homedir } from "os";

// ============================================================================
// Constants
// ============================================================================

const HOME = process.env.HOME || homedir();
const PAI_DIR = process.env.PAI_DIR || join(HOME, ".claude");
const PROJECTS_DIR = join(PAI_DIR, "MEMORY", "STATE", "projects");

import { type ProjectStatus, type Priority, isValidSlug, VALID_PRIORITIES, VALID_PROJECT_STATUSES } from "./DataModels.ts";
import { parseSimpleYaml, writeYamlFile } from "./YamlUtils.ts";

interface CreateOptions {
  slug: string;
  title: string;
  goal: string;
  target?: string;
  priority: Priority;
  parentRole?: string;
  parentMission?: string;
  criteria: string[];
  tags: string[];
  status: ProjectStatus;
}

interface CreateResult {
  created: boolean;
  path?: string;
  project?: Record<string, any>;
  error?: string;
}

// ============================================================================
// Help
// ============================================================================

function showHelp(): void {
  console.log(`
CreateProject - Scaffold a new bounded project

USAGE:
  bun ~/.claude/skills/PAI/Tools/CreateProject.ts <slug> --title "Title" --goal "Goal" [options]

ARGUMENTS:
  <slug>                    Kebab-case project identifier (required)

OPTIONS:
  --title "Title"           Human-readable title (required)
  --goal "Goal"             One-sentence goal statement (required)
  --target YYYY-MM-DD       Target completion date
  --priority HIGH|MEDIUM|LOW Priority level (default: MEDIUM)
  --parent-role "Role"      Link to TELOS Life Role
  --mission <slug>          Link to parent mission (bidirectional)
  --criteria "text"         Success criterion (repeatable)
  --tags tag1,tag2          Comma-separated tags
  --status PLANNING|IN_PROGRESS  Initial status (default: PLANNING)
  --help, -h                Show this help message

EXAMPLES:
  bun ~/.claude/skills/PAI/Tools/CreateProject.ts my-project --title "My Project" --goal "Build X"
  bun ~/.claude/skills/PAI/Tools/CreateProject.ts my-project --title "My Project" --goal "Build X" --priority HIGH --criteria "Feature works" --criteria "Tests pass"
  bun ~/.claude/skills/PAI/Tools/CreateProject.ts my-project --title "My Project" --goal "Build X" --tags "research,ml" --parent-role "Personal Research"

OUTPUT:
  JSON: { "created": true, "path": "...", "project": {...} }
`);
  process.exit(0);
}

// ============================================================================
// Core Functions
// ============================================================================

function getISOTimestamp(): string {
  return new Date().toISOString();
}

function getDateString(): string {
  return new Date().toISOString().split("T")[0];
}

export function createProject(options: CreateOptions): CreateResult {
  const { slug, title, goal, target, priority, parentRole, parentMission, criteria, tags, status } = options;

  // Validate slug format
  if (!isValidSlug(slug)) {
    return { created: false, error: "Slug must be kebab-case (lowercase letters, numbers, hyphens only)" };
  }

  if (!VALID_PRIORITIES.includes(priority)) {
    return { created: false, error: `Invalid priority: ${priority}. Must be HIGH, MEDIUM, or LOW` };
  }

  if (!VALID_PROJECT_STATUSES.includes(status)) {
    return { created: false, error: `Invalid initial status: ${status}. Must be PLANNING or IN_PROGRESS` };
  }

  // Ensure projects directory exists
  if (!existsSync(PROJECTS_DIR)) {
    mkdirSync(PROJECTS_DIR, { recursive: true });
  }

  // Check for collision
  const projectDir = join(PROJECTS_DIR, slug);
  if (existsSync(projectDir)) {
    return { created: false, error: `Project already exists: ${slug}` };
  }

  // Create project directory
  mkdirSync(projectDir, { recursive: true });

  const created = getDateString();
  const now = getISOTimestamp();

  // Write PROJECT.yaml
  const yamlData: any = {
    id: slug,
    title,
    status,
    created: created,
    goal,
  };

  if (target) yamlData.target = target;
  if (parentMission) yamlData.parent_mission = parentMission;
  if (parentRole) yamlData.parent_role = parentRole;

  if (criteria.length > 0) yamlData.success_criteria = criteria;
  else yamlData.success_criteria = ["Define success criteria"];

  if (tags.length > 0) yamlData.tags = tags;

  yamlData.priority = priority;

  writeYamlFile(join(projectDir, "PROJECT.yaml"), yamlData, {
    title,
    orderedKeys: ["id", "title", "status", "created", "goal", "target", "parent_mission", "parent_role", "priority", "success_criteria", "tags"]
  });

  // If --mission specified, link project to mission (bidirectional)
  if (parentMission) {
    const missionsDir = join(PAI_DIR, "MEMORY", "STATE", "missions");
    const missionYamlPath = join(missionsDir, parentMission, "MISSION.yaml");
    const missionProgressPath = join(missionsDir, parentMission, "progress.json");

    if (existsSync(missionYamlPath)) {
      // Read and update mission YAML to add this project to linked_projects
      const missionContent = readFileSync(missionYamlPath, "utf-8");
      const missionYaml = parseSimpleYaml(missionContent);

      if (!Array.isArray(missionYaml.linked_projects)) {
        missionYaml.linked_projects = [];
      }

      if (!missionYaml.linked_projects.includes(slug)) {
        missionYaml.linked_projects.push(slug);

        writeYamlFile(missionYamlPath, missionYaml, {
          title: missionYaml.title,
          orderedKeys: ["id", "title", "status", "created", "completed", "priority", "parent_goal", "description"],
          multiLineKeys: ["vision"]
        });
      }

      // Update mission progress.json
      if (existsSync(missionProgressPath)) {
        try {
          const missionProgress = JSON.parse(readFileSync(missionProgressPath, "utf-8"));
          if (!missionProgress.recent_activity) missionProgress.recent_activity = [];
          missionProgress.recent_activity.unshift({
            timestamp: now,
            action: "linked",
            detail: `New project linked: ${slug}`,
          });
          missionProgress.linked_project_count = (missionProgress.linked_project_count || 0) + 1;
          missionProgress.last_updated = now;
          if (missionProgress.recent_activity.length > 20) {
            missionProgress.recent_activity = missionProgress.recent_activity.slice(0, 20);
          }
          writeFileSync(missionProgressPath, JSON.stringify(missionProgress, null, 2) + "\n");
        } catch { /* ignore */ }
      }
    }
  }

  // Write TASKS.md
  const tasksContent = `# ${title} Tasks

${goal}

---

## Completed

## In Progress

## Remaining

## Blocked

## Optional/Deferred

---

*Created: ${created}*
`;

  writeFileSync(join(projectDir, "TASKS.md"), tasksContent);

  // Write progress.json
  const progressData = {
    project_id: slug,
    last_updated: now,
    task_counts: {
      completed: 0,
      in_progress: 0,
      remaining: 0,
      blocked: 0,
      optional: 0,
    },
    completion_percentage: 0,
    recent_activity: [
      {
        timestamp: now,
        action: "created",
        task: `Project created: ${title}`,
      },
    ],
  };

  writeFileSync(join(projectDir, "progress.json"), JSON.stringify(progressData, null, 2) + "\n");

  const project = {
    id: slug,
    title,
    status,
    created,
    goal,
    target: target || null,
    priority,
    parent_role: parentRole || null,
    success_criteria: criteria.length > 0 ? criteria : ["Define success criteria"],
    tags: tags.length > 0 ? tags : [],
  };

  return {
    created: true,
    path: projectDir,
    project,
  };
}

// ============================================================================
// CLI Argument Parsing
// ============================================================================

function getArg(args: string[], flag: string): string | undefined {
  const idx = args.indexOf(flag);
  return idx !== -1 && idx + 1 < args.length ? args[idx + 1] : undefined;
}

function getAllArgs(args: string[], flag: string): string[] {
  const values: string[] = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === flag && i + 1 < args.length) {
      values.push(args[i + 1]);
      i++;
    }
  }
  return values;
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
  const title = getArg(args, "--title");
  const goal = getArg(args, "--goal");

  if (!slug) {
    console.log(JSON.stringify({ created: false, error: "Missing required argument: <slug>" }));
    process.exit(1);
  }

  if (!title) {
    console.log(JSON.stringify({ created: false, error: "Missing required flag: --title" }));
    process.exit(1);
  }

  if (!goal) {
    console.log(JSON.stringify({ created: false, error: "Missing required flag: --goal" }));
    process.exit(1);
  }

  const target = getArg(args, "--target");
  const priorityRaw = getArg(args, "--priority") || "MEDIUM";
  const priority = priorityRaw.toUpperCase() as Priority;
  if (!VALID_PRIORITIES.includes(priority)) {
    console.log(JSON.stringify({ created: false, error: `Invalid priority: ${priorityRaw}. Must be HIGH, MEDIUM, or LOW` }));
    process.exit(1);
  }

  const parentRole = getArg(args, "--parent-role");
  const parentMission = getArg(args, "--mission");
  const criteria = getAllArgs(args, "--criteria");
  const tagsRaw = getArg(args, "--tags");
  const tags = tagsRaw ? tagsRaw.split(",").map(t => t.trim()).filter(Boolean) : [];

  const statusRaw = getArg(args, "--status") || "PLANNING";
  const status = statusRaw.toUpperCase() as ProjectStatus;
  if (!VALID_PROJECT_STATUSES.includes(status)) {
    console.log(JSON.stringify({ created: false, error: `Invalid initial status: ${statusRaw}. Must be PLANNING or IN_PROGRESS` }));
    process.exit(1);
  }

  const result = createProject({
    slug,
    title,
    goal,
    target,
    priority,
    parentRole,
    parentMission,
    criteria,
    tags,
    status,
  });

  console.log(JSON.stringify(result, null, 2));
  process.exit(result.created ? 0 : 1);
}

if (import.meta.main) {
  main().catch((err) => {
    console.log(JSON.stringify({ created: false, error: String(err) }));
    process.exit(1);
  });
}
