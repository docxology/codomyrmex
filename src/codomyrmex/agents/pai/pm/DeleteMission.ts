#!/usr/bin/env bun
/**
 * DeleteMission.ts - Delete a mission with safety checks
 *
 * Removes a mission directory from MEMORY/STATE/missions/<slug>/ and
 * cleans up bidirectional links from all linked projects.
 * Optionally cascades to delete all linked projects.
 *
 * Usage:
 *   bun ~/.claude/skills/PAI/Tools/DeleteMission.ts <slug> --confirm [options]
 *   bun ~/.claude/skills/PAI/Tools/DeleteMission.ts --help
 *
 * @author PAI System
 * @version 1.0.0
 */

import { existsSync, readFileSync, rmSync } from "fs";
import { join } from "path";
import { homedir } from "os";

// ============================================================================
// Constants
// ============================================================================

const HOME = process.env.HOME || homedir();
const PAI_DIR = process.env.PAI_DIR || join(HOME, ".claude");
const MISSIONS_DIR = join(PAI_DIR, "MEMORY", "STATE", "missions");
const PROJECTS_DIR = join(PAI_DIR, "MEMORY", "STATE", "projects");

import { parseSimpleYaml, writeYamlFile } from "./YamlUtils.ts";

interface DeleteResult {
  deleted: boolean;
  slug: string;
  deleted_files: string[];
  cleaned_links: string[];
  cascade_deleted: string[];
  error?: string;
}

// ============================================================================
// Help
// ============================================================================

function showHelp(): void {
  console.log(`
DeleteMission - Delete a mission with safety checks

USAGE:
  bun ~/.claude/skills/PAI/Tools/DeleteMission.ts <slug> --confirm [options]

ARGUMENTS:
  <slug>              Mission identifier (required)

OPTIONS:
  --confirm           Required flag to confirm deletion
  --dry-run           Preview what would be deleted without actually deleting
  --cascade           Also delete all linked projects
  --help, -h          Show this help message

EXAMPLES:
  bun ~/.claude/skills/PAI/Tools/DeleteMission.ts my-mission --confirm
  bun ~/.claude/skills/PAI/Tools/DeleteMission.ts my-mission --dry-run
  bun ~/.claude/skills/PAI/Tools/DeleteMission.ts my-mission --confirm --cascade

OUTPUT:
  JSON: { "deleted": true, "slug": "...", "deleted_files": [...], "cleaned_links": [...], "cascade_deleted": [...] }
`);
  process.exit(0);
}

// ============================================================================
// YAML Parsing
// ============================================================================

function writeProjectYaml(projectDir: string, yaml: Record<string, any>): void {
  writeYamlFile(join(projectDir, "PROJECT.yaml"), yaml, {
    title: yaml.title,
    orderedKeys: ["id", "title", "status", "created", "completed", "target", "goal", "blocked_by", "paused_reason", "parent_role", "parent_mission"],
    multiLineKeys: ["outcome", "notes"]
  });
}

// ============================================================================
// Core Functions
// ============================================================================

export function deleteMission(slug: string, options: {
  confirm?: boolean;
  dryRun?: boolean;
  cascade?: boolean;
}): DeleteResult {
  const missionDir = join(MISSIONS_DIR, slug);

  if (!existsSync(missionDir)) {
    return { deleted: false, slug, deleted_files: [], cleaned_links: [], cascade_deleted: [], error: `Mission not found: ${slug}` };
  }

  if (!options.confirm && !options.dryRun) {
    return { deleted: false, slug, deleted_files: [], cleaned_links: [], cascade_deleted: [], error: "Safety: --confirm flag required to delete (or use --dry-run to preview)" };
  }

  // Determine what files exist
  const deleted_files: string[] = [];
  const cleaned_links: string[] = [];
  const cascade_deleted: string[] = [];

  const yamlPath = join(missionDir, "MISSION.yaml");
  const progressPath = join(missionDir, "progress.json");

  if (existsSync(yamlPath)) deleted_files.push("MISSION.yaml");
  if (existsSync(progressPath)) deleted_files.push("progress.json");

  // Find linked projects
  let linkedProjects: string[] = [];
  if (existsSync(yamlPath)) {
    try {
      const yaml = parseSimpleYaml(readFileSync(yamlPath, "utf-8"));
      linkedProjects = Array.isArray(yaml.linked_projects) ? yaml.linked_projects : [];
    } catch { /* ignore */ }
  }

  // Determine cleanup actions for linked projects
  for (const projectSlug of linkedProjects) {
    if (options.cascade) {
      const projectDir = join(PROJECTS_DIR, projectSlug);
      if (existsSync(projectDir)) {
        cascade_deleted.push(projectSlug);
      }
    } else {
      const projectDir = join(PROJECTS_DIR, projectSlug);
      const projYamlPath = join(projectDir, "PROJECT.yaml");
      if (existsSync(projYamlPath)) {
        cleaned_links.push(`project:${projectSlug} (removed parent_mission)`);
      }
    }
  }

  // Dry run - return preview without deleting
  if (options.dryRun) {
    return { deleted: false, slug, deleted_files, cleaned_links, cascade_deleted };
  }

  // Perform the deletion

  // 1. Handle linked projects
  for (const projectSlug of linkedProjects) {
    const projectDir = join(PROJECTS_DIR, projectSlug);

    if (options.cascade) {
      // Delete the project entirely
      if (existsSync(projectDir)) {
        rmSync(projectDir, { recursive: true, force: true });
      }
    } else {
      // Just remove parent_mission from the project
      const projYamlPath = join(projectDir, "PROJECT.yaml");
      if (existsSync(projYamlPath)) {
        try {
          const projYaml = parseSimpleYaml(readFileSync(projYamlPath, "utf-8"));
          delete projYaml.parent_mission;
          writeProjectYaml(projectDir, projYaml);
        } catch { /* best effort */ }
      }
    }
  }

  // 2. Remove the mission directory
  rmSync(missionDir, { recursive: true, force: true });

  return { deleted: true, slug, deleted_files, cleaned_links, cascade_deleted };
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
  const cascade = hasFlag(args, "--cascade");

  const result = deleteMission(slug, { confirm, dryRun, cascade });

  console.log(JSON.stringify(result, null, 2));
  process.exit(result.deleted || dryRun ? 0 : 1);
}

if (import.meta.main) {
  main().catch((err) => {
    console.log(JSON.stringify({ deleted: false, error: String(err) }));
    process.exit(1);
  });
}
