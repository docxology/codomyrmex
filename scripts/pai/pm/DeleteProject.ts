#!/usr/bin/env bun
/**
 * DeleteProject.ts - Delete a bounded project with safety checks
 *
 * Removes a project directory from MEMORY/STATE/projects/<slug>/ and
 * cleans up bidirectional links from parent mission if linked.
 *
 * Usage:
 *   bun ~/.claude/skills/PAI/Tools/DeleteProject.ts <slug> --confirm [options]
 *   bun ~/.claude/skills/PAI/Tools/DeleteProject.ts --help
 *
 * @author PAI System
 * @version 1.0.0
 */

import { existsSync, readFileSync, writeFileSync, rmSync, readdirSync } from "fs";
import { join } from "path";
import { homedir } from "os";

// ============================================================================
// Constants
// ============================================================================

const HOME = process.env.HOME || homedir();
const PAI_DIR = process.env.PAI_DIR || join(HOME, ".claude");
const PROJECTS_DIR = join(PAI_DIR, "MEMORY", "STATE", "projects");
const MISSIONS_DIR = join(PAI_DIR, "MEMORY", "STATE", "missions");

import { parseSimpleYaml, writeYamlFile } from "./YamlUtils.ts";

interface DeleteResult {
  deleted: boolean;
  slug: string;
  deleted_files: string[];
  cleaned_links: string[];
  error?: string;
}

// ============================================================================
// Help
// ============================================================================

function showHelp(): void {
  console.log(`
DeleteProject - Delete a bounded project with safety checks

USAGE:
  bun ~/.claude/skills/PAI/Tools/DeleteProject.ts <slug> --confirm [options]

ARGUMENTS:
  <slug>              Project identifier (required)

OPTIONS:
  --confirm           Required flag to confirm deletion
  --dry-run           Preview what would be deleted without actually deleting
  --help, -h          Show this help message

EXAMPLES:
  bun ~/.claude/skills/PAI/Tools/DeleteProject.ts my-project --confirm
  bun ~/.claude/skills/PAI/Tools/DeleteProject.ts my-project --dry-run

OUTPUT:
  JSON: { "deleted": true, "slug": "...", "deleted_files": [...], "cleaned_links": [...] }
`);
  process.exit(0);
}

// ============================================================================
// YAML Parsing
// ============================================================================

function writeMissionYaml(missionDir: string, yaml: Record<string, any>): void {
  writeYamlFile(join(missionDir, "MISSION.yaml"), yaml, {
    title: yaml.title,
    orderedKeys: ["id", "title", "status", "created", "completed", "priority", "parent_goal", "description"],
    multiLineKeys: ["vision"]
  });
}

// ============================================================================
// Core Functions
// ============================================================================

export function deleteProject(slug: string, options: {
  confirm?: boolean;
  dryRun?: boolean;
}): DeleteResult {
  const projectDir = join(PROJECTS_DIR, slug);

  if (!existsSync(projectDir)) {
    return { deleted: false, slug, deleted_files: [], cleaned_links: [], error: `Project not found: ${slug}` };
  }

  if (!options.confirm && !options.dryRun) {
    return { deleted: false, slug, deleted_files: [], cleaned_links: [], error: "Safety: --confirm flag required to delete (or use --dry-run to preview)" };
  }

  // Determine what files exist
  const deleted_files: string[] = [];
  const cleaned_links: string[] = [];

  const yamlPath = join(projectDir, "PROJECT.yaml");
  const tasksPath = join(projectDir, "TASKS.md");
  const progressPath = join(projectDir, "progress.json");

  if (existsSync(yamlPath)) deleted_files.push("PROJECT.yaml");
  if (existsSync(tasksPath)) deleted_files.push("TASKS.md");
  if (existsSync(progressPath)) deleted_files.push("progress.json");

  // Check for parent mission link
  let parentMissionSlug: string | null = null;
  if (existsSync(yamlPath)) {
    try {
      const yaml = parseSimpleYaml(readFileSync(yamlPath, "utf-8"));
      if (yaml.parent_mission) {
        parentMissionSlug = yaml.parent_mission;
      }
    } catch { /* ignore */ }
  }

  // Also scan all missions for any that link to this project
  const missionSlugsToClean: string[] = [];
  if (existsSync(MISSIONS_DIR)) {
    for (const dir of readdirSync(MISSIONS_DIR, { withFileTypes: true })) {
      if (!dir.isDirectory()) continue;
      const mYamlPath = join(MISSIONS_DIR, dir.name, "MISSION.yaml");
      if (!existsSync(mYamlPath)) continue;
      try {
        const mYaml = parseSimpleYaml(readFileSync(mYamlPath, "utf-8"));
        const linked = Array.isArray(mYaml.linked_projects) ? mYaml.linked_projects : [];
        if (linked.includes(slug)) {
          missionSlugsToClean.push(dir.name);
          cleaned_links.push(`mission:${dir.name} (removed from linked_projects)`);
        }
      } catch { /* ignore */ }
    }
  }

  // Dry run - return preview without deleting
  if (options.dryRun) {
    return { deleted: false, slug, deleted_files, cleaned_links };
  }

  // Perform the deletion

  // 1. Clean up mission links
  for (const mSlug of missionSlugsToClean) {
    const missionDir = join(MISSIONS_DIR, mSlug);
    const mYamlPath = join(missionDir, "MISSION.yaml");
    const mProgressPath = join(missionDir, "progress.json");

    try {
      const mYaml = parseSimpleYaml(readFileSync(mYamlPath, "utf-8"));
      if (Array.isArray(mYaml.linked_projects)) {
        mYaml.linked_projects = mYaml.linked_projects.filter((p: string) => p !== slug);
      }
      writeMissionYaml(missionDir, mYaml);

      // Update mission progress.json
      if (existsSync(mProgressPath)) {
        const mProgress = JSON.parse(readFileSync(mProgressPath, "utf-8"));
        mProgress.linked_project_count = Math.max(0, (mProgress.linked_project_count || 1) - 1);
        if (mProgress.project_statuses) {
          delete mProgress.project_statuses[slug];
        }
        if (!mProgress.recent_activity) mProgress.recent_activity = [];
        mProgress.recent_activity.unshift({
          timestamp: new Date().toISOString(),
          action: "unlinked",
          detail: `Project deleted: ${slug}`,
        });
        if (mProgress.recent_activity.length > 20) {
          mProgress.recent_activity = mProgress.recent_activity.slice(0, 20);
        }
        mProgress.last_updated = new Date().toISOString();
        writeFileSync(mProgressPath, JSON.stringify(mProgress, null, 2) + "\n");
      }
    } catch { /* best effort cleanup */ }
  }

  // 2. Remove the project directory
  rmSync(projectDir, { recursive: true, force: true });

  return { deleted: true, slug, deleted_files, cleaned_links };
}

// ============================================================================
// CLI Argument Parsing
// ============================================================================

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
    console.log(JSON.stringify({ deleted: false, error: "Missing required argument: <slug>" }));
    process.exit(1);
  }

  const confirm = hasFlag(args, "--confirm");
  const dryRun = hasFlag(args, "--dry-run");

  const result = deleteProject(slug, { confirm, dryRun });

  console.log(JSON.stringify(result, null, 2));
  process.exit(result.deleted || dryRun ? 0 : 1);
}

if (import.meta.main) {
  main().catch((err) => {
    console.log(JSON.stringify({ deleted: false, error: String(err) }));
    process.exit(1);
  });
}
