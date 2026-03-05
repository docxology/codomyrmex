/**
 * awareness.ts - Dashboard + Awareness route handlers
 *
 * Handles /api/dashboard and /api/awareness endpoints —
 * reads mission/project/telos/memory data and builds metrics + Mermaid graphs.
 */

import { loadDashboardData } from "../PMDashboard.ts";
import { json } from "../helpers.ts";

export async function handleAwarenessRoutes(
    path: string,
    method: string,
    _req: Request,
    _url: URL,
): Promise<Response | null> {

    if (path === "/api/dashboard" && method === "GET") {
        const data = loadDashboardData();
        return json(data);
    }

    if (path === "/api/awareness" && method === "GET") {
        // Server-side cache with 60s TTL
        if (!globalThis._awarenessCache) globalThis._awarenessCache = { data: null, timestamp: 0 };
        const now = Date.now();
        if (globalThis._awarenessCache.data && (now - globalThis._awarenessCache.timestamp) < 60000) {
            return json(globalThis._awarenessCache.data);
        }

        const fs = await import("fs");
        const path_mod = await import("path");
        const yaml_mod = await import("js-yaml");

        const PAI_ROOT = path_mod.join(process.env.HOME || "", ".claude");

        // Read missions
        const missionsDir = path_mod.join(PAI_ROOT, "MEMORY", "STATE", "missions");
        const missions: any[] = [];
        try {
            const entries = fs.readdirSync(missionsDir, { withFileTypes: true });
            for (const entry of entries) {
                if (!entry.isDirectory()) continue;
                const missionFile = path_mod.join(missionsDir, entry.name, "MISSION.yaml");
                if (!fs.existsSync(missionFile)) continue;
                try {
                    const raw = fs.readFileSync(missionFile, "utf-8");
                    const data: any = yaml_mod.load(raw);
                    if (!data || typeof data !== "object") continue;
                    let progress: any = {};
                    const progressFile = path_mod.join(missionsDir, entry.name, "progress.json");
                    if (fs.existsSync(progressFile)) {
                        try { progress = JSON.parse(fs.readFileSync(progressFile, "utf-8")); } catch { }
                    }
                    missions.push({
                        id: entry.name, title: data.title || entry.name, status: data.status || "unknown",
                        priority: data.priority || "MEDIUM", description: data.description || "",
                        linked_projects: data.linked_projects || [], completion_percentage: progress.completion_percentage || 0,
                    });
                } catch { }
            }
        } catch { }
        const priorityOrder: Record<string, number> = { HIGH: 0, MEDIUM: 1, LOW: 2 };
        missions.sort((a, b) => (priorityOrder[a.priority] ?? 99) - (priorityOrder[b.priority] ?? 99));

        // Read projects
        const projectsDir = path_mod.join(PAI_ROOT, "MEMORY", "STATE", "projects");
        const projects: any[] = [];
        try {
            const entries = fs.readdirSync(projectsDir, { withFileTypes: true });
            for (const entry of entries) {
                if (!entry.isDirectory()) continue;
                const projectFile = path_mod.join(projectsDir, entry.name, "PROJECT.yaml");
                if (!fs.existsSync(projectFile)) continue;
                try {
                    const raw = fs.readFileSync(projectFile, "utf-8");
                    const data: any = yaml_mod.load(raw);
                    if (!data || typeof data !== "object") continue;
                    let progress: any = {};
                    const progressFile = path_mod.join(projectsDir, entry.name, "progress.json");
                    if (fs.existsSync(progressFile)) {
                        try { progress = JSON.parse(fs.readFileSync(progressFile, "utf-8")); } catch { }
                    }
                    projects.push({
                        id: entry.name, title: data.title || entry.name, status: data.status || "unknown",
                        goal: data.goal || "", priority: data.priority || "MEDIUM",
                        parent_mission: data.parent_mission || "", completion_percentage: progress.completion_percentage || 0,
                        task_counts: progress.task_counts || {},
                    });
                } catch { }
            }
        } catch { }

        // Read TELOS
        const telosDir = path_mod.join(PAI_ROOT, "skills", "PAI", "USER", "TELOS");
        const telos: any[] = [];
        try {
            const entries = fs.readdirSync(telosDir, { withFileTypes: true });
            for (const entry of entries) {
                if (!entry.isFile() || !entry.name.endsWith(".md")) continue;
                try {
                    const content = fs.readFileSync(path_mod.join(telosDir, entry.name), "utf-8");
                    telos.push({ name: entry.name.replace(/\.md$/, ""), filename: entry.name, preview: content.slice(0, 200) });
                } catch { telos.push({ name: entry.name.replace(/\.md$/, ""), filename: entry.name, preview: "" }); }
            }
        } catch { }
        telos.sort((a, b) => a.name.localeCompare(b.name));

        // Read Memory overview
        const memoryDir = path_mod.join(PAI_ROOT, "MEMORY");
        const directories: any[] = [];
        let totalFiles = 0;
        try {
            const entries = fs.readdirSync(memoryDir, { withFileTypes: true });
            for (const entry of entries) {
                if (!entry.isDirectory()) { totalFiles++; continue; }
                const dirPath = path_mod.join(memoryDir, entry.name);
                let fileCount = 0;
                try {
                    const walk = (d: string) => {
                        for (const f of fs.readdirSync(d, { withFileTypes: true })) {
                            if (f.isFile()) fileCount++;
                            else if (f.isDirectory()) walk(path_mod.join(d, f.name));
                        }
                    };
                    walk(dirPath);
                } catch { }
                totalFiles += fileCount;
                directories.push({ name: entry.name, file_count: fileCount });
            }
        } catch { }

        // Metrics — progress.json uses individual keys, not 'total'
        let totalTasks = 0, completedTasks = 0;
        for (const p of projects) {
            const tc = p.task_counts || {};
            totalTasks += (tc.completed || 0) + (tc.in_progress || 0) + (tc.remaining || 0) + (tc.blocked || 0) + (tc.optional || 0);
            completedTasks += tc.completed || 0;
        }

        // Mermaid graph
        const sanitize = (t: string) => t.replace(/[^a-zA-Z0-9_]/g, "_");
        const escLabel = (t: string) => t.replace(/"/g, "'").replace(/</g, "").replace(/>/g, "");
        const mermaidLines = ["graph TD"];
        mermaidLines.push("    classDef active fill:#10b981,stroke:#059669,color:#fff");
        mermaidLines.push("    classDef paused fill:#f59e0b,stroke:#d97706,color:#fff");
        mermaidLines.push("    classDef completed fill:#6b7280,stroke:#4b5563,color:#fff");
        mermaidLines.push("    classDef in_progress fill:#3b82f6,stroke:#2563eb,color:#fff");
        mermaidLines.push("    classDef blocked fill:#ef4444,stroke:#dc2626,color:#fff");
        mermaidLines.push("    classDef unknown fill:#94a3b8,stroke:#64748b,color:#fff");
        const linkedProjectIds = new Set<string>();
        for (const m of missions) {
            const mId = "M_" + sanitize(m.id);
            mermaidLines.push('    ' + mId + '["' + escLabel(m.title) + '"]');
            mermaidLines.push("    class " + mId + " " + sanitize(m.status));
            for (const ref of (m.linked_projects || [])) {
                const pId = "P_" + sanitize(String(ref));
                linkedProjectIds.add(String(ref));
                mermaidLines.push("    " + mId + " --> " + pId);
            }
        }
        for (const p of projects) {
            const pId = "P_" + sanitize(p.id);
            mermaidLines.push('    ' + pId + '["' + escLabel(p.title) + '"]');
            mermaidLines.push("    class " + pId + " " + sanitize(p.status));
            if (p.parent_mission && !linkedProjectIds.has(p.id)) {
                mermaidLines.push("    M_" + sanitize(p.parent_mission) + " --> " + pId);
            }
        }

        const awarenessResult = {
            missions, projects, telos,
            memory: { directories, total_files: totalFiles },
            metrics: {
                mission_count: missions.length, project_count: projects.length,
                total_tasks: totalTasks, completed_tasks: completedTasks,
                telos_files: telos.length,
                overall_completion: totalTasks > 0 ? Math.round(completedTasks / totalTasks * 1000) / 10 : 0,
            },
            mermaid_graph: mermaidLines.join("\n"),
        };
        globalThis._awarenessCache = { data: awarenessResult, timestamp: Date.now() };
        return json(awarenessResult);
    }

    return null;
}
