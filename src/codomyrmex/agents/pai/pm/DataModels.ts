/**
 * DataModels.ts - Shared Type Definitions for PAI System
 * 
 * Centralizes the schema definitions for Missions, Projects, and Tasks to ensure
 * consistency across CLI tools (Layer 1) and PMServer (Layer 2).
 */

// ============================================================================
// Enums & Unions
// ============================================================================

export type Priority = "HIGH" | "MEDIUM" | "LOW";

export type MissionStatus = "ACTIVE" | "PLANNING" | "IN_PROGRESS" | "PAUSED" | "COMPLETED" | "ARCHIVED";

export type ProjectStatus = "PLANNING" | "IN_PROGRESS" | "COMPLETED" | "PAUSED" | "BLOCKED";

export type TaskSection = "completed" | "in_progress" | "remaining" | "blocked" | "optional";

// ============================================================================
// Interfaces
// ============================================================================

export interface Mission {
    id: string; // slug
    title: string;
    description: string;
    status: MissionStatus;
    priority: Priority;
    created: string; // ISO Date YYYY-MM-DD
    completed?: string | null; // ISO Date YYYY-MM-DD, set on completion
    vision?: string | null;
    parent_goal?: string | null;
    success_criteria: string[];
    tags: string[];
    linked_projects: string[]; // storage only, runtime might hydrate
}

export interface Project {
    id: string; // slug
    title: string;
    goal: string;
    status: ProjectStatus;
    priority: Priority;
    created: string; // ISO Date YYYY-MM-DD
    target?: string | null; // ISO Date YYYY-MM-DD
    blocked_by?: string | null; // What's blocking progress (if BLOCKED)
    paused_reason?: string | null; // Why paused (if PAUSED)
    parent_role?: string | null;
    parent_mission?: string | null;
    success_criteria: string[];
    tags: string[];
}

export interface Task {
    text: string;
    section: TaskSection;
    priority?: Priority;
    due?: string;
    assignee?: string;
    blocked_by?: string;
    created?: string;
    spec?: string;           // acceptance criteria / definition of done
    depends_on?: string[];   // titles of prerequisite tasks in same project
}

// ============================================================================
// Validation Helpers
// ============================================================================

export const VALID_PRIORITIES: Priority[] = ["HIGH", "MEDIUM", "LOW"];

export const VALID_MISSION_STATUSES: MissionStatus[] = ["ACTIVE", "PLANNING", "IN_PROGRESS", "PAUSED", "COMPLETED", "ARCHIVED"];

export const VALID_PROJECT_STATUSES: ProjectStatus[] = ["PLANNING", "IN_PROGRESS", "COMPLETED", "PAUSED", "BLOCKED"];

export const VALID_TASK_SECTIONS: TaskSection[] = ["completed", "in_progress", "remaining", "blocked", "optional"];

export function isValidSlug(slug: string): boolean {
    return /^[a-z0-9]+(-[a-z0-9]+)*$/.test(slug);
}
