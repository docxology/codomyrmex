#!/usr/bin/env bun
/**
 * CreateMission.ts - Scaffold a new mission
 *
 * Creates a new mission directory with MISSION.yaml and progress.json
 * following the three-tier hierarchy: Mission -> Project -> Task.
 *
 * Usage:
 *   bun ~/.claude/skills/PAI/Tools/CreateMission.ts <slug> --title "Title" --description "Desc" [options]
 *   bun ~/.claude/skills/PAI/Tools/CreateMission.ts --help
 *
 * @author PAI System
 * @version 1.0.0
 */

import { existsSync, mkdirSync, writeFileSync } from "fs";
import { join } from "path";
import { homedir } from "os";

// ============================================================================
// Constants
// ============================================================================

const HOME = process.env.HOME || homedir();
const PAI_DIR = process.env.PAI_DIR || join(HOME, ".claude");
const MISSIONS_DIR = join(PAI_DIR, "MEMORY", "STATE", "missions");

import { type MissionStatus, type Priority, isValidSlug, VALID_PRIORITIES, VALID_MISSION_STATUSES } from "./DataModels.ts";
import { writeYamlFile } from "./YamlUtils.ts";

interface CreateMissionOptions {
  slug: string;
  title: string;
  description: string;
  vision?: string;
  parentGoal?: string;
  priority: Priority;
  criteria: string[];
  tags: string[];
  status: MissionStatus;
}

interface CreateMissionResult {
  created: boolean;
  path?: string;
  mission?: Record<string, any>;
  error?: string;
}

// ============================================================================
// Help
// ============================================================================

function showHelp(): void {
  console.log(`
CreateMission - Scaffold a new mission

USAGE:
  bun ~/.claude/skills/PAI/Tools/CreateMission.ts <slug> --title "Title" --description "Desc" [options]

ARGUMENTS:
  <slug>                      Kebab-case mission identifier (required)

OPTIONS:
  --title "Title"             Human-readable title (required)
  --description "Desc"        Mission description (required)
  --vision "Vision"           Long-term vision statement
  --parent-goal M0|M1|M2      Link to TELOS goal (M0/M1/M2)
  --priority HIGH|MEDIUM|LOW  Priority level (default: MEDIUM)
  --criteria "text"           Success criterion (repeatable)
  --tags tag1,tag2            Comma-separated tags
  --status ACTIVE|PAUSED      Initial status (default: ACTIVE)
  --help, -h                  Show this help message

EXAMPLES:
  bun ~/.claude/skills/PAI/Tools/CreateMission.ts pai-development --title "PAI Development" --description "Build the PAI system"
  bun ~/.claude/skills/PAI/Tools/CreateMission.ts research-2026 --title "Research 2026" --description "Annual research goals" --priority HIGH --criteria "3 papers published" --criteria "Conference talk"

OUTPUT:
  JSON: { "created": true, "path": "...", "mission": {...} }
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

export function createMission(options: CreateMissionOptions): CreateMissionResult {
  const { slug, title, description, vision, parentGoal, priority, criteria, tags, status } = options;

  // Validate slug format
  if (!isValidSlug(slug)) {
    return { created: false, error: "Slug must be kebab-case (lowercase letters, numbers, hyphens only)" };
  }

  if (!VALID_PRIORITIES.includes(priority)) {
    return { created: false, error: `Invalid priority: ${priority}. Must be HIGH, MEDIUM, or LOW` };
  }

  if (!VALID_MISSION_STATUSES.includes(status)) {
    return { created: false, error: `Invalid initial status: ${status}. Must be ACTIVE or PAUSED` };
  }

  // Ensure missions directory exists
  if (!existsSync(MISSIONS_DIR)) {
    mkdirSync(MISSIONS_DIR, { recursive: true });
  }

  // Check for collision
  const missionDir = join(MISSIONS_DIR, slug);
  if (existsSync(missionDir)) {
    return { created: false, error: `Mission already exists: ${slug}` };
  }

  // Create mission directory
  mkdirSync(missionDir, { recursive: true });

  const created = getDateString();
  const now = getISOTimestamp();

  // Write MISSION.yaml
  const yamlData: any = {
    id: slug,
    title,
    status,
    created: created,
    description,
  };

  if (vision) yamlData.vision = vision;
  if (parentGoal) yamlData.parent_goal = parentGoal;
  if (criteria.length > 0) yamlData.success_criteria = criteria;
  else yamlData.success_criteria = ["Define success criteria"];

  if (tags.length > 0) yamlData.tags = tags;

  yamlData.priority = priority;

  writeYamlFile(join(missionDir, "MISSION.yaml"), yamlData, {
    title,
    orderedKeys: ["id", "title", "status", "created", "description", "vision", "parent_goal", "success_criteria", "linked_projects", "tags", "priority"],
    multiLineKeys: ["vision"]
  });

  // Write progress.json
  const progressData = {
    mission_id: slug,
    last_updated: now,
    linked_project_count: 0,
    aggregate_completion: 0,
    project_statuses: {} as Record<string, string>,
    recent_activity: [
      {
        timestamp: now,
        action: "created",
        detail: `Mission created: ${title}`,
      },
    ],
  };

  writeFileSync(join(missionDir, "progress.json"), JSON.stringify(progressData, null, 2) + "\n");

  const mission = {
    id: slug,
    title,
    status,
    created,
    description,
    vision: vision || null,
    parent_goal: parentGoal || null,
    priority,
    success_criteria: criteria.length > 0 ? criteria : ["Define success criteria"],
    linked_projects: [],
    tags: tags.length > 0 ? tags : [],
  };

  return {
    created: true,
    path: missionDir,
    mission,
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
  const description = getArg(args, "--description");

  if (!slug) {
    console.log(JSON.stringify({ created: false, error: "Missing required argument: <slug>" }));
    process.exit(1);
  }

  if (!title) {
    console.log(JSON.stringify({ created: false, error: "Missing required flag: --title" }));
    process.exit(1);
  }

  if (!description) {
    console.log(JSON.stringify({ created: false, error: "Missing required flag: --description" }));
    process.exit(1);
  }

  const vision = getArg(args, "--vision");
  const parentGoal = getArg(args, "--parent-goal");

  const priorityRaw = getArg(args, "--priority") || "MEDIUM";
  const priority = priorityRaw.toUpperCase() as Priority;

  const criteria = getAllArgs(args, "--criteria");
  const tagsRaw = getArg(args, "--tags");
  const tags = tagsRaw ? tagsRaw.split(",").map(t => t.trim()).filter(Boolean) : [];

  const statusRaw = getArg(args, "--status") || "ACTIVE";
  const status = statusRaw.toUpperCase() as MissionStatus;

  const result = createMission({
    slug,
    title,
    description,
    vision,
    parentGoal,
    priority,
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
