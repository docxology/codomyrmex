/**
 * tasks.ts - Task CRUD route handlers
 *
 * Handles /api/tasks/* endpoints.
 */

import { addTask } from "../AddTask.ts";
import { updateTask } from "../UpdateTask.ts";
import { listTasks } from "../ListTasks.ts";
import { getTaskSummary } from "../TaskSummary.ts";
import { json, error, parseBody, broadcast } from "../helpers.ts";

export async function handleTaskRoutes(
    path: string,
    method: string,
    req: Request,
    url: URL,
): Promise<Response | null> {

    // POST /api/tasks - Add task
    if (path === "/api/tasks" && method === "POST") {
        const body = await parseBody(req);
        if (!body.project || !body.title) return error("Missing: project, title");
        const result = addTask(body as any);
        if (!result.error) {
            broadcast("task", "create", result);
            return json(result, 201);
        }
        return error(result.error || "Failed to add task");
    }

    // GET /api/tasks - List
    if (path === "/api/tasks" && method === "GET") {
        const project = url.searchParams.get("project") || undefined;
        const section = url.searchParams.get("section") || undefined;
        if (!project) return error("Missing query param: project");
        const result = listTasks({ project, section });
        return json(result);
    }

    // PUT /api/tasks/:project/:task - Update
    const updateMatch = path.match(/^\/api\/tasks\/([^/]+)\/(.+)$/);
    if (updateMatch && method === "PUT") {
        const project = decodeURIComponent(updateMatch[1]);
        const taskRef = decodeURIComponent(updateMatch[2]);
        const body = await parseBody(req);
        const result = updateTask(project, taskRef, body as any);
        if (!result.error) {
            broadcast("task", "update", result);
            return json(result);
        }
        return error(result.error || "Failed to update task");
    }

    // GET /api/tasks/summary - Task summary
    if (path === "/api/tasks/summary" && method === "GET") {
        const project = url.searchParams.get("project") || undefined;
        const mission = url.searchParams.get("mission") || undefined;
        const result = getTaskSummary({ project, mission });
        return json(result);
    }

    return null;
}
