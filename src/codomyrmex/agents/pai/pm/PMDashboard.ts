#!/usr/bin/env bun
/**
 * PMDashboard.ts - Generate interactive HTML dashboard for Mission/Project/Task hierarchy
 *
 * Reads all missions, projects, and tasks from MEMORY/STATE and generates
 * a single-page HTML dashboard with visual progress indicators, status badges,
 * and hierarchical navigation.
 *
 * Usage:
 *   bun ~/.claude/skills/PAI/Tools/PMDashboard.ts [options]
 *   bun ~/.claude/skills/PAI/Tools/PMDashboard.ts --help
 *
 * @author PAI System
 * @version 1.0.0
 */

import { existsSync, readdirSync, readFileSync, writeFileSync } from "fs";
import { join } from "path";
import { homedir } from "os";

// ============================================================================
// Constants
// ============================================================================

const HOME = process.env.HOME || homedir();
const PAI_DIR = process.env.PAI_DIR || join(HOME, ".claude");
const MISSIONS_DIR = join(PAI_DIR, "MEMORY", "STATE", "missions");
const PROJECTS_DIR = join(PAI_DIR, "MEMORY", "STATE", "projects");
const DEFAULT_OUTPUT = join(PAI_DIR, "MEMORY", "STATE", "dashboard.html");

// ============================================================================
// Help
// ============================================================================

function showHelp(): void {
  console.log(`
PMDashboard - Generate interactive HTML dashboard for Mission/Project/Task hierarchy

USAGE:
  bun ~/.claude/skills/PAI/Tools/PMDashboard.ts [options]

OPTIONS:
  --output <path>     Output HTML file path (default: ~/.claude/MEMORY/STATE/dashboard.html)
  --open              Open in browser after generation
  --json              Output raw JSON data instead of HTML
  --help, -h          Show this help message

EXAMPLES:
  bun ~/.claude/skills/PAI/Tools/PMDashboard.ts                    # Generate dashboard
  bun ~/.claude/skills/PAI/Tools/PMDashboard.ts --open             # Generate and open
  bun ~/.claude/skills/PAI/Tools/PMDashboard.ts --output ~/pm.html # Custom output path
  bun ~/.claude/skills/PAI/Tools/PMDashboard.ts --json             # Raw JSON data

OUTPUT:
  Single HTML file with embedded CSS/JS
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

    if (value === "|") { multiLineKey = key; continue; }
    if (!value) { currentArrayKey = key; continue; }

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
// Task Parsing
// ============================================================================

interface TaskInfo {
  title: string;
  section: string;
  priority?: string;
  due?: string;
  assignee?: string;
  created?: string;
  blocked_by?: string;
  overdue: boolean;
}

function parseTasksFromMd(content: string): TaskInfo[] {
  const tasks: TaskInfo[] = [];
  const today = new Date().toISOString().split("T")[0];
  let currentSection: string | null = null;
  let currentTaskTitle: string | null = null;
  let currentMetadata: Record<string, string> = {};

  function flushTask() {
    if (currentTaskTitle && currentSection) {
      const entry: TaskInfo = {
        title: currentTaskTitle,
        section: currentSection,
        overdue: false,
      };
      if (currentMetadata.priority) entry.priority = currentMetadata.priority;
      if (currentMetadata.due) {
        entry.due = currentMetadata.due;
        if (currentMetadata.due < today && currentSection !== "completed") {
          entry.overdue = true;
        }
      }
      if (currentMetadata.assignee) entry.assignee = currentMetadata.assignee;
      if (currentMetadata.created) entry.created = currentMetadata.created;
      if (currentMetadata.blocked_by) entry.blocked_by = currentMetadata.blocked_by;
      tasks.push(entry);
    }
    currentTaskTitle = null;
    currentMetadata = {};
  }

  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    const lower = trimmed.toLowerCase();

    if (lower.startsWith("## completed")) { flushTask(); currentSection = "completed"; continue; }
    if (lower.startsWith("## in progress")) { flushTask(); currentSection = "in_progress"; continue; }
    if (lower.startsWith("## remaining")) { flushTask(); currentSection = "remaining"; continue; }
    if (lower.startsWith("## blocked")) { flushTask(); currentSection = "blocked"; continue; }
    if (lower.startsWith("## optional") || lower.startsWith("## deferred")) { flushTask(); currentSection = "optional"; continue; }
    if (lower.startsWith("## summary") || (trimmed === "---" && currentSection)) { flushTask(); currentSection = null; continue; }

    if (!currentSection) continue;

    // New task item (not indented sub-items)
    if (trimmed.startsWith("- [") || (trimmed.startsWith("- ") && !line.startsWith("  ") && !line.startsWith("\t"))) {
      flushTask();
      let text = trimmed;
      if (trimmed.startsWith("- [x] ")) text = trimmed.slice(6);
      else if (trimmed.startsWith("- [ ] ")) text = trimmed.slice(6);
      else if (trimmed.startsWith("- [~] ")) text = trimmed.slice(6);
      else if (trimmed.startsWith("- ")) text = trimmed.slice(2);
      currentTaskTitle = text;
      continue;
    }

    if (currentTaskTitle && trimmed.startsWith("- ")) {
      const metaText = trimmed.slice(2).trim();
      const colonIdx = metaText.indexOf(":");
      if (colonIdx !== -1) {
        const key = metaText.slice(0, colonIdx).trim().toLowerCase().replace(/ /g, "_");
        const value = metaText.slice(colonIdx + 1).trim();
        currentMetadata[key] = value;
      }
    }
  }

  flushTask();
  return tasks;
}

// ============================================================================
// Data Loading
// ============================================================================

interface ProjectData {
  id: string;
  title: string;
  status: string;
  created: string;
  completed?: string;
  goal: string;
  priority: string;
  parent_mission?: string;
  success_criteria: string[];
  tags: string[];
  completion_percentage: number;
  tasks: TaskInfo[];
  task_counts: {
    completed: number;
    in_progress: number;
    remaining: number;
    blocked: number;
    optional: number;
  };
}

interface MissionData {
  id: string;
  title: string;
  status: string;
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
  recent_activity: Array<{ timestamp: string; action: string; detail: string }>;
}

interface DashboardData {
  generated: string;
  missions: MissionData[];
  projects: ProjectData[];
  orphan_projects: ProjectData[]; // Projects not linked to any mission
  stats: {
    total_missions: number;
    active_missions: number;
    total_projects: number;
    active_projects: number;
    total_tasks: number;
    completed_tasks: number;
    overdue_tasks: number;
    blocked_tasks: number;
  };
}

function loadProject(slug: string): ProjectData | null {
  const projectDir = join(PROJECTS_DIR, slug);
  const yamlPath = join(projectDir, "PROJECT.yaml");
  const tasksPath = join(projectDir, "TASKS.md");
  const progressPath = join(projectDir, "progress.json");

  if (!existsSync(yamlPath)) return null;

  try {
    const yaml = parseSimpleYaml(readFileSync(yamlPath, "utf-8"));

    let tasks: TaskInfo[] = [];
    if (existsSync(tasksPath)) {
      tasks = parseTasksFromMd(readFileSync(tasksPath, "utf-8"));
    }

    let completion = 0;
    let taskCounts = { completed: 0, in_progress: 0, remaining: 0, blocked: 0, optional: 0 };
    if (existsSync(progressPath)) {
      try {
        const progress = JSON.parse(readFileSync(progressPath, "utf-8"));
        completion = progress.completion_percentage || 0;
        if (progress.task_counts) taskCounts = progress.task_counts;
      } catch { /* ignore */ }
    }

    // Recalculate from actual tasks if no progress.json data
    if (taskCounts.completed === 0 && taskCounts.remaining === 0 && tasks.length > 0) {
      taskCounts = { completed: 0, in_progress: 0, remaining: 0, blocked: 0, optional: 0 };
      for (const t of tasks) {
        if (t.section === "completed") taskCounts.completed++;
        else if (t.section === "in_progress") taskCounts.in_progress++;
        else if (t.section === "remaining") taskCounts.remaining++;
        else if (t.section === "blocked") taskCounts.blocked++;
        else if (t.section === "optional") taskCounts.optional++;
      }
      const total = taskCounts.completed + taskCounts.in_progress + taskCounts.remaining + taskCounts.blocked;
      completion = total > 0 ? Math.round((taskCounts.completed / total) * 100) : 0;
    }

    return {
      id: yaml.id || slug,
      title: yaml.title || slug,
      status: yaml.status || "PLANNING",
      created: yaml.created || "unknown",
      completed: yaml.completed || undefined,
      goal: yaml.goal || "",
      priority: yaml.priority || "MEDIUM",
      parent_mission: yaml.parent_mission || undefined,
      success_criteria: Array.isArray(yaml.success_criteria) ? yaml.success_criteria : [],
      tags: Array.isArray(yaml.tags) ? yaml.tags : [],
      completion_percentage: completion,
      tasks,
      task_counts: taskCounts,
    };
  } catch {
    return null;
  }
}

function loadMission(slug: string): MissionData | null {
  const missionDir = join(MISSIONS_DIR, slug);
  const yamlPath = join(missionDir, "MISSION.yaml");
  const progressPath = join(missionDir, "progress.json");

  if (!existsSync(yamlPath)) return null;

  try {
    const yaml = parseSimpleYaml(readFileSync(yamlPath, "utf-8"));
    let progress: any = { recent_activity: [], aggregate_completion: 0 };
    if (existsSync(progressPath)) {
      try { progress = JSON.parse(readFileSync(progressPath, "utf-8")); } catch { /* ignore */ }
    }

    return {
      id: yaml.id || slug,
      title: yaml.title || slug,
      status: yaml.status || "ACTIVE",
      created: yaml.created || "unknown",
      completed: yaml.completed || undefined,
      description: yaml.description || "",
      vision: yaml.vision || undefined,
      priority: yaml.priority || "MEDIUM",
      parent_goal: yaml.parent_goal || undefined,
      success_criteria: Array.isArray(yaml.success_criteria) ? yaml.success_criteria : [],
      linked_projects: Array.isArray(yaml.linked_projects) ? yaml.linked_projects : [],
      tags: Array.isArray(yaml.tags) ? yaml.tags : [],
      aggregate_completion: progress.aggregate_completion || 0,
      recent_activity: (progress.recent_activity || []).slice(0, 10),
    };
  } catch {
    return null;
  }
}

export function loadDashboardData(): DashboardData {
  const missions: MissionData[] = [];
  const projects: ProjectData[] = [];

  // Load missions
  if (existsSync(MISSIONS_DIR)) {
    for (const dir of readdirSync(MISSIONS_DIR, { withFileTypes: true })) {
      if (dir.isDirectory()) {
        const m = loadMission(dir.name);
        if (m) missions.push(m);
      }
    }
  }

  // Load projects
  if (existsSync(PROJECTS_DIR)) {
    for (const dir of readdirSync(PROJECTS_DIR, { withFileTypes: true })) {
      if (dir.isDirectory()) {
        const p = loadProject(dir.name);
        if (p) projects.push(p);
      }
    }
  }

  // Find orphan projects (not linked to any mission)
  const linkedProjectIds = new Set(missions.flatMap(m => m.linked_projects));
  const orphanProjects = projects.filter(p => !linkedProjectIds.has(p.id));

  // Stats
  let totalTasks = 0, completedTasks = 0, overdueTasks = 0, blockedTasks = 0;
  for (const p of projects) {
    for (const t of p.tasks) {
      totalTasks++;
      if (t.section === "completed") completedTasks++;
      if (t.overdue) overdueTasks++;
      if (t.section === "blocked") blockedTasks++;
    }
  }

  // Sort missions: active first, then by priority
  const statusOrder: Record<string, number> = { ACTIVE: 0, PAUSED: 1, ARCHIVED: 2, COMPLETED: 3 };
  const priorityOrder: Record<string, number> = { HIGH: 0, MEDIUM: 1, LOW: 2 };
  missions.sort((a, b) => (statusOrder[a.status] ?? 5) - (statusOrder[b.status] ?? 5) || (priorityOrder[a.priority] ?? 1) - (priorityOrder[b.priority] ?? 1));

  return {
    generated: new Date().toISOString(),
    missions,
    projects,
    orphan_projects: orphanProjects,
    stats: {
      total_missions: missions.length,
      active_missions: missions.filter(m => m.status === "ACTIVE").length,
      total_projects: projects.length,
      active_projects: projects.filter(p => p.status === "IN_PROGRESS").length,
      total_tasks: totalTasks,
      completed_tasks: completedTasks,
      overdue_tasks: overdueTasks,
      blocked_tasks: blockedTasks,
    },
  };
}

// ============================================================================
// HTML Generation
// ============================================================================

function escapeHtml(text: string): string {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

export function generateHTML(data: DashboardData): string {
  const { stats, missions, projects, orphan_projects } = data;
  const projectMap = new Map(projects.map(p => [p.id, p]));

  function statusBadge(status: string): string {
    const colors: Record<string, string> = {
      ACTIVE: "#10b981", IN_PROGRESS: "#10b981",
      PAUSED: "#f59e0b",
      COMPLETED: "#6366f1",
      ARCHIVED: "#6b7280",
      BLOCKED: "#ef4444",
      PLANNING: "#8b5cf6",
    };
    const icons: Record<string, string> = {
      ACTIVE: "&#9889;", IN_PROGRESS: "&#9889;",
      PAUSED: "&#9208;",
      COMPLETED: "&#10003;",
      ARCHIVED: "&#128230;",
      BLOCKED: "&#9940;",
      PLANNING: "&#128221;",
    };
    const color = colors[status] || "#6b7280";
    const icon = icons[status] || "";
    return `<span class="badge" style="background:${color}">${icon} ${escapeHtml(status)}</span>`;
  }

  function priorityBadge(priority: string): string {
    const colors: Record<string, string> = { HIGH: "#ef4444", MEDIUM: "#f59e0b", LOW: "#6b7280" };
    return `<span class="badge-outline" style="border-color:${colors[priority] || "#6b7280"};color:${colors[priority] || "#6b7280"}">${escapeHtml(priority)}</span>`;
  }

  function progressBar(pct: number, width: string = "100%"): string {
    const color = pct >= 80 ? "#10b981" : pct >= 50 ? "#f59e0b" : pct >= 25 ? "#3b82f6" : "#6b7280";
    return `<div class="progress-bar" style="width:${width}"><div class="progress-fill" style="width:${pct}%;background:${color}"></div><span class="progress-text">${pct}%</span></div>`;
  }

  function taskSectionBadge(section: string): string {
    const colors: Record<string, string> = {
      completed: "#10b981", in_progress: "#3b82f6",
      remaining: "#6b7280", blocked: "#ef4444", optional: "#8b5cf6",
    };
    return `<span class="task-badge" style="background:${colors[section] || "#6b7280"}">${escapeHtml(section.replace("_", " "))}</span>`;
  }

  // Build project cards for a mission
  function renderMissionProjects(linkedProjectIds: string[]): string {
    if (linkedProjectIds.length === 0) return `<div class="empty-state">No linked projects</div>`;
    return linkedProjectIds.map(id => {
      const p = projectMap.get(id);
      if (!p) return `<div class="project-card missing"><span class="project-id">${escapeHtml(id)}</span> <span class="text-muted">(not found)</span></div>`;
      return renderProjectCard(p, true);
    }).join("");
  }

  // Single project card
  function renderProjectCard(p: ProjectData, compact: boolean = false): string {
    const tc = p.task_counts;
    const total = tc.completed + tc.in_progress + tc.remaining + tc.blocked;

    let taskSection = "";
    if (p.tasks.length > 0 && !compact) {
      const taskRows = p.tasks.map(t => `
        <tr class="${t.overdue ? "overdue-row" : ""}">
          <td>${taskSectionBadge(t.section)}</td>
          <td>${escapeHtml(t.title)}</td>
          <td>${t.priority ? priorityBadge(t.priority) : "-"}</td>
          <td>${t.due ? (t.overdue ? `<span class="overdue">${escapeHtml(t.due)}</span>` : escapeHtml(t.due)) : "-"}</td>
        </tr>
      `).join("");
      taskSection = `
        <div class="tasks-section" id="tasks-${escapeHtml(p.id)}" style="display:none">
          <div style="overflow-x:auto;-webkit-overflow-scrolling:touch">
            <table class="task-table">
              <thead><tr><th>Status</th><th>Task</th><th>Priority</th><th>Due</th></tr></thead>
              <tbody>${taskRows}</tbody>
            </table>
          </div>
        </div>
      `;
    }

    return `
      <div class="project-card">
        <button type="button" class="project-header" data-project-id="${escapeHtml(p.id)}"
                aria-expanded="false" aria-controls="tasks-${escapeHtml(p.id)}"
                onclick="toggleTasks(this)">
          <div class="project-title">
            <strong>${escapeHtml(p.title)}</strong>
            <span class="project-id">${escapeHtml(p.id)}</span>
          </div>
          <div class="project-badges">
            ${statusBadge(p.status)} ${priorityBadge(p.priority)}
            <span class="toggle-chevron" aria-hidden="true">&#9654;</span>
          </div>
        </button>
        <div class="project-goal">${escapeHtml(p.goal)}</div>
        <div class="project-progress">
          ${progressBar(p.completion_percentage)}
          <div class="task-counts">
            <span class="count-done">${tc.completed} done</span>
            <span class="count-active">${tc.in_progress} active</span>
            <span class="count-remaining">${tc.remaining} remaining</span>
            ${tc.blocked > 0 ? `<span class="count-blocked">${tc.blocked} blocked</span>` : ""}
          </div>
        </div>
        ${taskSection}
      </div>
    `;
  }

  // Build mission sections
  const missionSections = missions.map(m => `
    <div class="mission-card" id="mission-${escapeHtml(m.id)}">
      <button type="button" class="mission-header" data-mission-id="${escapeHtml(m.id)}"
              aria-expanded="true" aria-controls="mission-body-${escapeHtml(m.id)}"
              onclick="toggleMission(this)">
        <div class="mission-title">
          <h2>${escapeHtml(m.title)}</h2>
          <span class="mission-id">${escapeHtml(m.id)}</span>
        </div>
        <div class="mission-badges">
          ${statusBadge(m.status)} ${priorityBadge(m.priority)}
          ${m.parent_goal ? `<span class="badge-outline" style="border-color:#8b5cf6;color:#8b5cf6">${escapeHtml(m.parent_goal)}</span>` : ""}
          <span class="toggle-chevron" aria-hidden="true">&#9654;</span>
        </div>
      </button>
      <div class="mission-body" id="mission-body-${m.id}">
        <div class="mission-meta">
          <div class="mission-desc">${escapeHtml(m.description)}</div>
          ${m.vision ? `<div class="mission-vision"><strong>Vision:</strong> ${escapeHtml(m.vision)}</div>` : ""}
        </div>
        <div class="mission-progress">
          ${progressBar(m.aggregate_completion)}
          <span class="text-muted">${m.linked_projects.length} project${m.linked_projects.length !== 1 ? "s" : ""} linked</span>
        </div>

        ${m.success_criteria.length > 0 ? `
          <div class="criteria-section">
            <h4>Success Criteria</h4>
            <ul class="criteria-list">
              ${m.success_criteria.map(c => {
    const achieved = c.includes("ACHIEVED") || c.includes("done");
    return `<li class="${achieved ? "achieved" : ""}">${achieved ? "&#10003;" : "&#9633;"} ${escapeHtml(c)}</li>`;
  }).join("")}
            </ul>
          </div>
        ` : ""}

        <div class="linked-projects">
          <h4>Linked Projects</h4>
          ${renderMissionProjects(m.linked_projects)}
        </div>

        ${m.recent_activity.length > 0 ? `
          <div class="activity-section">
            <h4>Recent Activity</h4>
            <ul class="activity-list">
              ${m.recent_activity.slice(0, 5).map(a => `
                <li>
                  <span class="activity-date">${a.timestamp ? a.timestamp.split("T")[0] : "?"}</span>
                  <span class="activity-action">[${escapeHtml(a.action)}]</span>
                  ${escapeHtml(a.detail)}
                </li>
              `).join("")}
            </ul>
          </div>
        ` : ""}

        ${m.tags.length > 0 ? `<div class="tags">${m.tags.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join("")}</div>` : ""}
      </div>
    </div>
  `).join("");

  // Orphan projects section
  const orphanSection = orphan_projects.length > 0 ? `
    <section class="section">
      <h2 class="section-title">Unlinked Projects</h2>
      <div class="orphan-grid">
        ${orphan_projects.map(p => renderProjectCard(p, false)).join("")}
      </div>
    </section>
  ` : "";

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PAI Project Dashboard</title>
<style>
  :root {
    --bg: #0f172a; --surface: #1e293b; --surface2: #334155; --border: #475569;
    --text: #f1f5f9; --text-muted: #94a3b8; --accent: #3b82f6;
    --green: #10b981; --yellow: #f59e0b; --red: #ef4444; --purple: #8b5cf6;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.6;
    max-width: 1200px; margin: 0 auto; padding: 24px;
  }
  h1 { font-size: 1.8rem; margin-bottom: 8px; }
  h2 { font-size: 1.3rem; margin: 0; }
  h4 { font-size: 0.9rem; color: var(--text-muted); margin: 12px 0 8px; text-transform: uppercase; letter-spacing: 0.5px; }

  /* Header */
  .header { margin-bottom: 32px; padding-bottom: 24px; border-bottom: 1px solid var(--border); }
  .header-subtitle { color: var(--text-muted); font-size: 0.9rem; }

  /* Stats Grid */
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 32px; }
  .stat-card {
    background: var(--surface); border-radius: 10px; padding: 16px; text-align: center;
    border: 1px solid var(--border); transition: transform 0.15s;
  }
  .stat-card:hover { transform: translateY(-2px); }
  .stat-value { font-size: 2rem; font-weight: 700; }
  .stat-label { font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }

  /* Badges */
  .badge {
    display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem;
    font-weight: 600; color: #fff; letter-spacing: 0.3px;
  }
  .badge-outline {
    display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem;
    font-weight: 600; border: 1.5px solid; background: transparent;
  }
  .task-badge {
    display: inline-block; padding: 1px 8px; border-radius: 8px; font-size: 0.7rem;
    font-weight: 500; color: #fff;
  }
  .tag { display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; background: var(--surface2); color: var(--text-muted); margin: 2px; }

  /* Progress Bar */
  .progress-bar {
    background: var(--surface2); border-radius: 8px; height: 20px; position: relative;
    overflow: hidden; margin: 8px 0;
  }
  .progress-fill { height: 100%; border-radius: 8px; transition: width 0.5s ease; min-width: 2px; }
  .progress-text {
    position: absolute; right: 8px; top: 50%; transform: translateY(-50%);
    font-size: 0.7rem; font-weight: 600; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,0.5);
  }

  /* Mission Cards */
  .mission-card {
    background: var(--surface); border-radius: 12px; margin-bottom: 20px;
    border: 1px solid var(--border); overflow: hidden;
  }
  .mission-header {
    padding: 20px 24px; cursor: pointer; display: flex; justify-content: space-between;
    align-items: center; transition: background 0.15s; width: 100%;
  }
  .mission-header:hover { background: var(--surface2); }
  .mission-title { display: flex; align-items: center; gap: 12px; }
  .mission-id { font-size: 0.8rem; color: var(--text-muted); font-family: monospace; }
  .mission-badges { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
  .mission-body { padding: 0 24px 20px; }
  .mission-meta { margin-bottom: 12px; }
  .mission-desc { color: var(--text-muted); font-size: 0.95rem; }
  .mission-vision { color: var(--text-muted); font-size: 0.9rem; font-style: italic; margin-top: 4px; }
  .mission-progress { margin: 12px 0; }

  /* Project Cards */
  .project-card {
    background: var(--bg); border-radius: 10px; padding: 16px; margin-bottom: 8px;
    border: 1px solid var(--border); transition: border-color 0.15s;
  }
  .project-card:hover { border-color: var(--accent); }
  .project-card.missing { opacity: 0.5; cursor: default; }
  .project-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
  .project-title { display: flex; align-items: center; gap: 8px; }
  .project-id { font-size: 0.75rem; color: var(--text-muted); font-family: monospace; }
  .project-badges { display: flex; gap: 6px; flex-wrap: wrap; }
  .project-goal { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 8px; }
  .project-progress { }
  .task-counts { display: flex; gap: 12px; font-size: 0.8rem; margin-top: 4px; flex-wrap: wrap; }
  .count-done { color: var(--green); }
  .count-active { color: var(--accent); }
  .count-remaining { color: var(--text-muted); }
  .count-blocked { color: var(--red); }

  /* Task Table */
  .tasks-section { margin-top: 12px; border-top: 1px solid var(--border); padding-top: 12px; }
  .task-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
  .task-table th { text-align: left; padding: 4px 8px; color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; border-bottom: 1px solid var(--border); }
  .task-table td { padding: 6px 8px; border-bottom: 1px solid rgba(71,85,105,0.3); }
  .overdue-row { background: rgba(239,68,68,0.1); }
  .overdue { color: var(--red); font-weight: 600; }

  /* Criteria */
  .criteria-list { list-style: none; padding: 0; }
  .criteria-list li { padding: 4px 0; font-size: 0.9rem; color: var(--text-muted); }
  .criteria-list li.achieved { color: var(--green); text-decoration: line-through; }

  /* Activity */
  .activity-list { list-style: none; padding: 0; }
  .activity-list li { padding: 4px 0; font-size: 0.85rem; color: var(--text-muted); }
  .activity-date { font-family: monospace; font-size: 0.8rem; margin-right: 8px; }
  .activity-action { font-weight: 600; color: var(--accent); margin-right: 4px; }

  /* Section */
  .section { margin-top: 32px; }
  .section-title { margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
  .orphan-grid { display: grid; gap: 12px; }
  .text-muted { color: var(--text-muted); font-size: 0.85rem; }
  .empty-state { color: var(--text-muted); font-style: italic; padding: 8px 0; }

  /* Nav Tabs */
  .nav-tabs { display: flex; gap: 4px; margin-bottom: 24px; }
  .nav-tab {
    padding: 8px 20px; border-radius: 8px; cursor: pointer; font-size: 0.9rem;
    background: var(--surface); color: var(--text-muted); border: 1px solid var(--border);
    transition: all 0.15s;
  }
  .nav-tab:hover { background: var(--surface2); color: var(--text); }
  .nav-tab.active { background: var(--accent); color: #fff; border-color: var(--accent); }
  .tab-content { display: none; }
  .tab-content.active { display: block; }

  /* Toggle chevron */
  .toggle-chevron { transition: transform 0.2s; display: inline-block; font-size: 0.7rem; color: var(--text-muted); margin-left: 4px; }
  button[aria-expanded="true"] .toggle-chevron { transform: rotate(90deg); }

  /* Button resets for semantic button elements used as cards/headers */
  button.mission-header, button.project-header {
    background: none; border: none; text-align: left; width: 100%; cursor: pointer;
    color: inherit; font: inherit; padding: 20px 24px;
    display: flex; justify-content: space-between; align-items: center;
    transition: background 0.15s;
  }
  button.mission-header:hover { background: var(--surface2); }
  button.project-header {
    padding: 0; margin-bottom: 8px;
  }
  button.project-header:hover { border-color: var(--accent); }
  button.nav-tab { cursor: pointer; }

  /* Responsive — tablet */
  @media (max-width: 1024px) {
    .stats-grid { grid-template-columns: repeat(4, 1fr); }
    body { padding: 16px; }
  }
  /* Responsive — mobile */
  @media (max-width: 768px) {
    body { padding: 12px; }
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
    .mission-header { flex-direction: column; align-items: flex-start; gap: 8px; }
    .project-header { flex-direction: column; align-items: flex-start; gap: 4px; }
  }
</style>
</head>
<body>

<div class="header">
  <h1>PAI Project Dashboard</h1>
  <div class="header-subtitle">Generated: ${data.generated.split("T")[0]} &mdash; Mission &rarr; Project &rarr; Task Hierarchy</div>
</div>

<!-- Stats -->
<div class="stats-grid">
  <div class="stat-card"><div class="stat-value" style="color:var(--accent)">${stats.total_missions}</div><div class="stat-label">Missions</div></div>
  <div class="stat-card"><div class="stat-value" style="color:var(--green)">${stats.active_missions}</div><div class="stat-label">Active Missions</div></div>
  <div class="stat-card"><div class="stat-value" style="color:var(--accent)">${stats.total_projects}</div><div class="stat-label">Projects</div></div>
  <div class="stat-card"><div class="stat-value" style="color:var(--green)">${stats.active_projects}</div><div class="stat-label">Active Projects</div></div>
  <div class="stat-card"><div class="stat-value">${stats.total_tasks}</div><div class="stat-label">Total Tasks</div></div>
  <div class="stat-card"><div class="stat-value" style="color:var(--green)">${stats.completed_tasks}</div><div class="stat-label">Completed</div></div>
  <div class="stat-card"><div class="stat-value" style="color:${stats.overdue_tasks > 0 ? "var(--red)" : "var(--text-muted)"}">${stats.overdue_tasks}</div><div class="stat-label">Overdue</div></div>
  <div class="stat-card"><div class="stat-value" style="color:${stats.blocked_tasks > 0 ? "var(--red)" : "var(--text-muted)"}">${stats.blocked_tasks}</div><div class="stat-label">Blocked</div></div>
</div>

<!-- Search -->
<div style="margin-bottom:16px">
  <input type="search" id="dashboard-search"
         placeholder="Filter missions &amp; projects..."
         aria-label="Filter missions and projects"
         oninput="applyFilter(this.value)"
         style="width:100%;padding:10px 16px;background:var(--surface);border:1px solid var(--border);border-radius:8px;color:var(--text);font-size:0.9rem;outline:none;">
</div>

<!-- Nav Tabs -->
<div class="nav-tabs" role="tablist">
  <button type="button" class="nav-tab active" role="tab" aria-selected="true" onclick="switchTab('missions', this)">Missions (${missions.length})</button>
  <button type="button" class="nav-tab" role="tab" aria-selected="false" onclick="switchTab('projects', this)">All Projects (${projects.length})</button>
  ${orphan_projects.length > 0 ? `<button type="button" class="nav-tab" role="tab" aria-selected="false" onclick="switchTab('orphans', this)">Unlinked (${orphan_projects.length})</button>` : ""}
</div>

<!-- Missions Tab -->
<div class="tab-content active" id="tab-missions">
  ${missions.length === 0 ? `<div class="empty-state-card" style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:24px;text-align:center;color:var(--text-muted)"><p style="margin-bottom:12px;font-size:1rem">No missions yet.</p><code style="background:var(--surface2);padding:6px 12px;border-radius:6px;font-size:0.8rem;display:block;margin-top:8px">bun ~/.claude/skills/PAI/Tools/CreateMission.ts --slug my-goal --title &quot;My Goal&quot;</code></div>` : missionSections}
</div>

<!-- All Projects Tab -->
<div class="tab-content" id="tab-projects">
  ${projects.length === 0 ? `<div class="empty-state-card" style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:24px;text-align:center;color:var(--text-muted)"><p style="margin-bottom:12px;font-size:1rem">No projects yet.</p><code style="background:var(--surface2);padding:6px 12px;border-radius:6px;font-size:0.8rem;display:block;margin-top:8px">bun ~/.claude/skills/PAI/Tools/CreateProject.ts --slug my-project --title &quot;My Project&quot;</code></div>` : projects.map(p => renderProjectCard(p, false)).join("")}
</div>

<!-- Orphans Tab -->
<div class="tab-content" id="tab-orphans">
  ${orphanSection}
</div>

<script>
function switchTab(name, btn) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(el => { el.classList.remove('active'); el.setAttribute('aria-selected', 'false'); });
  document.getElementById('tab-' + name).classList.add('active');
  btn.classList.add('active');
  btn.setAttribute('aria-selected', 'true');
  // Reset search on tab switch
  var searchInput = document.getElementById('dashboard-search');
  if (searchInput) { searchInput.value = ''; applyFilter(''); }
}

function toggleMission(btn) {
  var id = btn.dataset.missionId;
  var body = document.getElementById('mission-body-' + id);
  var expanded = btn.getAttribute('aria-expanded') === 'true';
  body.style.display = expanded ? 'none' : 'block';
  btn.setAttribute('aria-expanded', expanded ? 'false' : 'true');
}

function toggleTasks(btn) {
  var id = btn.dataset.projectId;
  var el = document.getElementById('tasks-' + id);
  if (el) {
    var expanded = btn.getAttribute('aria-expanded') === 'true';
    el.style.display = expanded ? 'none' : 'block';
    btn.setAttribute('aria-expanded', expanded ? 'false' : 'true');
    event.stopPropagation();
  }
}

function applyFilter(query) {
  var q = query.toLowerCase().trim();
  document.querySelectorAll('.mission-card').forEach(function(card) {
    var text = card.textContent.toLowerCase();
    card.style.display = (!q || text.includes(q)) ? '' : 'none';
  });
  document.querySelectorAll('.project-card').forEach(function(card) {
    var text = card.textContent.toLowerCase();
    card.style.display = (!q || text.includes(q)) ? '' : 'none';
  });
}
</script>
</body>
</html>`;
}

// ============================================================================
// CLI
// ============================================================================

function getArg(args: string[], flag: string): string | undefined {
  const idx = args.indexOf(flag);
  return idx !== -1 && idx + 1 < args.length ? args[idx + 1] : undefined;
}

function hasFlag(args: string[], flag: string): boolean {
  return args.includes(flag);
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);

  if (hasFlag(args, "--help") || hasFlag(args, "-h")) {
    showHelp();
  }

  const outputPath = getArg(args, "--output") || DEFAULT_OUTPUT;
  const openBrowser = hasFlag(args, "--open");
  const jsonMode = hasFlag(args, "--json");

  const data = loadDashboardData();

  if (jsonMode) {
    console.log(JSON.stringify(data, null, 2));
    return;
  }

  const html = generateHTML(data);
  writeFileSync(outputPath, html);

  console.log(JSON.stringify({
    generated: true,
    path: outputPath,
    stats: data.stats,
  }, null, 2));

  if (openBrowser) {
    const proc = Bun.spawn(["open", outputPath]);
    await proc.exited;
  }
}

if (import.meta.main) {
  main().catch((err) => {
    console.log(JSON.stringify({ generated: false, error: String(err) }));
    process.exit(1);
  });
}
