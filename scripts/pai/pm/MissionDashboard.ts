#!/usr/bin/env bun
/**
 * MissionDashboard.ts - Rich overview of all missions
 *
 * Generates a comprehensive dashboard showing all missions with their
 * linked projects, aggregate progress, and activity.
 *
 * Usage:
 *   bun ~/.claude/skills/PAI/Tools/MissionDashboard.ts [options]
 *   bun ~/.claude/skills/PAI/Tools/MissionDashboard.ts --help
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
const MISSIONS_DIR = join(PAI_DIR, "MEMORY", "STATE", "missions");
const PROJECTS_DIR = join(PAI_DIR, "MEMORY", "STATE", "projects");

type MissionStatus = "ACTIVE" | "PAUSED" | "COMPLETED" | "ARCHIVED";

interface ProjectSummary {
  id: string;
  title: string;
  status: string;
  completion_percentage: number;
  priority: string;
}

interface MissionData {
  id: string;
  title: string;
  status: MissionStatus;
  created: string;
  completed?: string;
  description: string;
  vision?: string;
  priority: string;
  parent_goal?: string;
  success_criteria: string[];
  linked_projects: string[];
  tags: string[];
  aggregate_completion: number;
  project_summaries: ProjectSummary[];
  recent_activity: Array<{ timestamp: string; action: string; detail: string }>;
}

interface MissionDashboardData {
  generated: string;
  summary: {
    total: number;
    active: number;
    paused: number;
    completed: number;
    archived: number;
    total_linked_projects: number;
  };
  missions: MissionData[];
}

// ============================================================================
// Help
// ============================================================================

function showHelp(): void {
  console.log(`
MissionDashboard - Rich overview of all missions

USAGE:
  bun ~/.claude/skills/PAI/Tools/MissionDashboard.ts [options]

OPTIONS:
  --format markdown|json    Output format (default: markdown)
  --active                  Only show non-completed missions
  --mission <slug>          Deep-dive into a single mission
  --tag <tag>               Filter missions by tag
  --quiet                   Minimal output (counts only)
  --help, -h                Show this help message

EXAMPLES:
  bun ~/.claude/skills/PAI/Tools/MissionDashboard.ts                     # Full markdown dashboard
  bun ~/.claude/skills/PAI/Tools/MissionDashboard.ts --format json       # Machine-readable JSON
  bun ~/.claude/skills/PAI/Tools/MissionDashboard.ts --active            # Non-completed only
  bun ~/.claude/skills/PAI/Tools/MissionDashboard.ts --mission my-mission  # Single mission deep-dive
  bun ~/.claude/skills/PAI/Tools/MissionDashboard.ts --tag work          # Filter by tag
  bun ~/.claude/skills/PAI/Tools/MissionDashboard.ts --quiet             # Just counts

OUTPUT:
  Markdown dashboard (default) or JSON data structure
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
// Core Functions
// ============================================================================

function loadProjectSummary(slug: string): ProjectSummary | null {
  const projectDir = join(PROJECTS_DIR, slug);
  const yamlPath = join(projectDir, "PROJECT.yaml");
  const progressPath = join(projectDir, "progress.json");

  if (!existsSync(yamlPath)) return null;

  try {
    const yaml = parseSimpleYaml(readFileSync(yamlPath, "utf-8"));
    let completion = 0;
    if (existsSync(progressPath)) {
      try {
        const progress = JSON.parse(readFileSync(progressPath, "utf-8"));
        completion = progress.completion_percentage || 0;
      } catch { /* ignore */ }
    }

    return {
      id: yaml.id || slug,
      title: yaml.title || slug,
      status: yaml.status || "PLANNING",
      completion_percentage: completion,
      priority: yaml.priority || "MEDIUM",
    };
  } catch {
    return null;
  }
}

function loadMissionData(slug: string): MissionData | null {
  const missionDir = join(MISSIONS_DIR, slug);
  const yamlPath = join(missionDir, "MISSION.yaml");
  const progressPath = join(missionDir, "progress.json");

  if (!existsSync(yamlPath)) return null;

  try {
    const yaml = parseSimpleYaml(readFileSync(yamlPath, "utf-8"));

    let progress: any = {
      recent_activity: [],
      aggregate_completion: 0,
    };
    if (existsSync(progressPath)) {
      try {
        progress = JSON.parse(readFileSync(progressPath, "utf-8"));
      } catch { /* use defaults */ }
    }

    const linkedProjects: string[] = Array.isArray(yaml.linked_projects) ? yaml.linked_projects : [];

    // Load project summaries
    const projectSummaries = linkedProjects
      .map(p => loadProjectSummary(p))
      .filter((p): p is ProjectSummary => p !== null);

    // Calculate aggregate completion from actual project data
    const aggCompletion = projectSummaries.length > 0
      ? Math.round(projectSummaries.reduce((sum, p) => sum + p.completion_percentage, 0) / projectSummaries.length)
      : 0;

    return {
      id: yaml.id || slug,
      title: yaml.title || slug,
      status: (yaml.status || "ACTIVE") as MissionStatus,
      created: yaml.created || "unknown",
      completed: yaml.completed || undefined,
      description: yaml.description || "",
      vision: yaml.vision || undefined,
      priority: yaml.priority || "MEDIUM",
      parent_goal: yaml.parent_goal || undefined,
      success_criteria: Array.isArray(yaml.success_criteria) ? yaml.success_criteria : [],
      linked_projects: linkedProjects,
      tags: Array.isArray(yaml.tags) ? yaml.tags : [],
      aggregate_completion: aggCompletion,
      project_summaries: projectSummaries,
      recent_activity: progress.recent_activity || [],
    };
  } catch {
    return null;
  }
}

export function getMissionDashboardData(options: {
  active?: boolean;
  missionSlug?: string;
  tag?: string;
}): MissionDashboardData {
  const now = new Date().toISOString();

  if (!existsSync(MISSIONS_DIR)) {
    return {
      generated: now,
      summary: { total: 0, active: 0, paused: 0, completed: 0, archived: 0, total_linked_projects: 0 },
      missions: [],
    };
  }

  let slugs = readdirSync(MISSIONS_DIR, { withFileTypes: true })
    .filter(e => e.isDirectory())
    .map(e => e.name);

  if (options.missionSlug) {
    slugs = slugs.filter(s => s === options.missionSlug);
  }

  let missions = slugs
    .map(slug => loadMissionData(slug))
    .filter((m): m is MissionData => m !== null);

  if (options.active) {
    missions = missions.filter(m => m.status !== "COMPLETED" && m.status !== "ARCHIVED");
  }

  if (options.tag) {
    const tag = options.tag.toLowerCase();
    missions = missions.filter(m => m.tags.some(t => t.toLowerCase() === tag));
  }

  // Sort: blocked first, then active/in_progress, planning, paused, archived, completed
  const statusOrder: Record<string, number> = { BLOCKED: 0, ACTIVE: 1, IN_PROGRESS: 1, PLANNING: 2, PAUSED: 3, ARCHIVED: 4, COMPLETED: 5 };
  missions.sort((a, b) => (statusOrder[a.status] ?? 9) - (statusOrder[b.status] ?? 9));

  const totalLinkedProjects = missions.reduce((sum, m) => sum + m.linked_projects.length, 0);

  const summary = {
    total: missions.length,
    active: missions.filter(m => m.status === "ACTIVE").length,
    paused: missions.filter(m => m.status === "PAUSED").length,
    completed: missions.filter(m => m.status === "COMPLETED").length,
    archived: missions.filter(m => m.status === "ARCHIVED").length,
    total_linked_projects: totalLinkedProjects,
  };

  return { generated: now, summary, missions };
}

// ============================================================================
// Markdown Formatting
// ============================================================================

function formatMarkdownDashboard(data: MissionDashboardData, quiet: boolean = false): string {
  const lines: string[] = [];
  const { summary, missions } = data;

  if (quiet) {
    lines.push(`Missions: ${summary.total} total | ${summary.active} active | ${summary.completed} completed | ${summary.paused} paused | ${summary.archived} archived | ${summary.total_linked_projects} linked projects`);
    return lines.join("\n");
  }

  lines.push(`# Mission Dashboard`);
  lines.push(``);
  lines.push(`**Generated:** ${data.generated.split("T")[0]}`);
  lines.push(``);

  // Summary
  lines.push(`## Summary`);
  lines.push(``);
  lines.push(`| Metric | Count |`);
  lines.push(`|--------|-------|`);
  lines.push(`| Total Missions | ${summary.total} |`);
  lines.push(`| Active | ${summary.active} |`);
  lines.push(`| Paused | ${summary.paused} |`);
  lines.push(`| Completed | ${summary.completed} |`);
  lines.push(`| Archived | ${summary.archived} |`);
  lines.push(`| Total Linked Projects | ${summary.total_linked_projects} |`);
  lines.push(``);

  if (missions.length === 0) {
    lines.push(`No missions found.`);
    return lines.join("\n");
  }

  const statusIcons: Record<string, string> = {
    ACTIVE: "🚀",
    PAUSED: "⏸️",
    COMPLETED: "✅",
    ARCHIVED: "📦",
  };

  const projectStatusIcons: Record<string, string> = {
    PLANNING: "📋",
    IN_PROGRESS: "🔄",
    COMPLETED: "✅",
    PAUSED: "⏸️",
    BLOCKED: "🚫",
  };

  // Single mission deep-dive
  if (missions.length === 1 && data.summary.total <= 1) {
    const m = missions[0];
    lines.push(`## ${statusIcons[m.status] || "❓"} ${m.title}`);
    lines.push(``);
    lines.push(`| Field | Value |`);
    lines.push(`|-------|-------|`);
    lines.push(`| **ID** | \`${m.id}\` |`);
    lines.push(`| **Status** | ${m.status} |`);
    lines.push(`| **Priority** | ${m.priority} |`);
    lines.push(`| **Created** | ${m.created} |`);
    if (m.completed) lines.push(`| **Completed** | ${m.completed} |`);
    if (m.parent_goal) lines.push(`| **Parent Goal** | ${m.parent_goal} |`);
    lines.push(`| **Aggregate Completion** | ${m.aggregate_completion}% |`);
    lines.push(`| **Linked Projects** | ${m.linked_projects.length} |`);
    lines.push(``);
    lines.push(`**Description:** ${m.description}`);
    lines.push(``);

    if (m.vision) {
      lines.push(`**Vision:** ${m.vision}`);
      lines.push(``);
    }

    // Success criteria
    if (m.success_criteria.length > 0) {
      lines.push(`### Success Criteria`);
      lines.push(``);
      for (const c of m.success_criteria) {
        const achieved = c.includes("ACHIEVED") || c.includes("✓");
        lines.push(`- ${achieved ? "✅" : "⬜"} ${c}`);
      }
      lines.push(``);
    }

    // Linked projects table
    if (m.project_summaries.length > 0) {
      lines.push(`### Linked Projects`);
      lines.push(``);
      lines.push(`| Project | Status | Priority | Completion |`);
      lines.push(`|---------|--------|----------|------------|`);
      for (const p of m.project_summaries) {
        const pIcon = projectStatusIcons[p.status] || "❓";
        lines.push(`| \`${p.id}\` — ${p.title} | ${pIcon} ${p.status} | ${p.priority} | ${p.completion_percentage}% |`);
      }
      lines.push(``);
    }

    // Recent activity
    if (m.recent_activity.length > 0) {
      lines.push(`### Recent Activity`);
      lines.push(``);
      for (const a of m.recent_activity.slice(0, 10)) {
        const date = a.timestamp ? a.timestamp.split("T")[0] : "unknown";
        lines.push(`- **${date}** [${a.action}] ${a.detail}`);
      }
      lines.push(``);
    }

    // Tags
    if (m.tags.length > 0) {
      lines.push(`**Tags:** ${m.tags.join(", ")}`);
      lines.push(``);
    }

    return lines.join("\n");
  }

  // Multi-mission list
  lines.push(`## Missions`);
  lines.push(``);

  for (const m of missions) {
    const icon = statusIcons[m.status] || "❓";
    lines.push(`### ${icon} ${m.title}`);
    lines.push(``);
    lines.push(`- **ID:** \`${m.id}\``);
    lines.push(`- **Status:** ${m.status} | **Priority:** ${m.priority} | **Aggregate Completion:** ${m.aggregate_completion}%`);
    lines.push(`- **Description:** ${m.description}`);
    if (m.parent_goal) lines.push(`- **Parent Goal:** ${m.parent_goal}`);

    // Show linked projects summary
    if (m.project_summaries.length > 0) {
      const projectParts = m.project_summaries.map(p => {
        const pIcon = projectStatusIcons[p.status] || "❓";
        return `${pIcon} ${p.id} (${p.completion_percentage}%)`;
      });
      lines.push(`- **Projects:** ${projectParts.join(", ")}`);
    } else {
      lines.push(`- **Projects:** None linked`);
    }

    // Show recent activity (last 5)
    if (m.recent_activity.length > 0) {
      const recent = m.recent_activity.slice(0, 5);
      lines.push(`- **Recent:** ${recent.map(a => `[${a.action}] ${a.detail}`).join("; ")}`);
    }

    lines.push(``);
  }

  return lines.join("\n");
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

  const format = getArg(args, "--format") || "markdown";
  if (!["markdown", "json"].includes(format)) {
    console.log(JSON.stringify({ success: false, error: `Invalid format: ${format}. Must be markdown or json` }));
    process.exit(1);
  }

  const active = hasFlag(args, "--active");
  const missionSlug = getArg(args, "--mission");
  const tag = getArg(args, "--tag");
  const quiet = hasFlag(args, "--quiet");

  const data = getMissionDashboardData({ active, missionSlug, tag });

  if (missionSlug && data.missions.length === 0) {
    console.log(JSON.stringify({ success: false, error: `Mission not found: ${missionSlug}` }));
    process.exit(1);
  }

  switch (format) {
    case "json":
      console.log(JSON.stringify(data, null, 2));
      break;
    case "markdown":
    default:
      console.log(formatMarkdownDashboard(data, quiet));
      break;
  }
}

if (import.meta.main) {
  main().catch((err) => {
    console.log(JSON.stringify({ success: false, error: String(err) }));
    process.exit(1);
  });
}
