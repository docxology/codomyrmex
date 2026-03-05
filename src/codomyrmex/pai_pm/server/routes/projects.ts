/**
 * projects.ts - Project CRUD + Gantt route handlers
 *
 * Handles /api/projects/* and /api/gantt/* endpoints.
 */

import { createProject } from "../CreateProject.ts";
import { updateProject } from "../UpdateProject.ts";
import { listProjects } from "../ListProjects.ts";
import { completeProject } from "../CompleteProject.ts";
import { getDashboardData } from "../ProjectDashboard.ts";
import { deleteProject } from "../DeleteProject.ts";
import { listTasks } from "../ListTasks.ts";
import { json, error, parseBody, broadcast } from "../helpers.ts";

export async function handleProjectRoutes(
    path: string,
    method: string,
    req: Request,
    url: URL,
): Promise<Response | null> {

    // POST /api/projects - Create
    if (path === "/api/projects" && method === "POST") {
        const body = await parseBody(req);
        const result = createProject(body as any);
        if (result.created) {
            broadcast("project", "create", result.project);
            return json(result, 201);
        }
        return error(result.error || "Failed to create project");
    }

    // GET /api/projects - List
    if (path === "/api/projects" && method === "GET") {
        const status = url.searchParams.get("status") || undefined;
        const sort = url.searchParams.get("sort") || undefined;
        const result = listProjects({ status, sort, verbose: true });
        return json(result);
    }

    // GET /api/projects/:id - Single project detail
    const singleMatch = path.match(/^\/api\/projects\/([^/]+)$/);
    if (singleMatch && method === "GET") {
        const slug = decodeURIComponent(singleMatch[1]);
        const result = getDashboardData(slug);
        return json(result);
    }

    // PUT /api/projects/:id - Update
    if (singleMatch && method === "PUT") {
        const slug = decodeURIComponent(singleMatch[1]);
        const body = await parseBody(req);
        const result = updateProject(slug, body as any);
        if (result.updated) {
            broadcast("project", "update", result.project);
            return json(result);
        }
        return error(result.error || "Failed to update project");
    }

    // DELETE /api/projects/:id - Delete
    if (singleMatch && method === "DELETE") {
        const slug = decodeURIComponent(singleMatch[1]);
        const body = await parseBody(req).catch(() => ({}));
        const result = deleteProject(slug, body as any);
        if (!result.error) {
            broadcast("project", "delete", { id: slug });
            return json(result);
        }
        return error(result.error || "Failed to delete project");
    }

    // POST /api/projects/:id/complete - Complete project
    const completeMatch = path.match(/^\/api\/projects\/([^/]+)\/complete$/);
    if (completeMatch && method === "POST") {
        const slug = decodeURIComponent(completeMatch[1]);
        const body = await parseBody(req).catch(() => ({}));
        const result = completeProject(slug, body as any);
        if (!result.error) {
            broadcast("project", "complete", result);
            return json(result);
        }
        return error(result.error || "Failed to complete project");
    }

    // GET /api/gantt/:id - Per-project Gantt data
    const ganttMatch = path.match(/^\/api\/gantt\/([^/]+)$/);
    if (ganttMatch && method === "GET") {
        const slug = decodeURIComponent(ganttMatch[1]);
        const tasks = listTasks({ project: slug });
        const project = getDashboardData(slug);
        return json({ project, tasks });
    }

    return null;
}
