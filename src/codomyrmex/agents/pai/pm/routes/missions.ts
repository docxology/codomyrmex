/**
 * missions.ts - Mission CRUD route handlers
 *
 * Handles /api/missions/* endpoints for creating, updating, listing,
 * and deleting missions.
 */

import { createMission } from "../CreateMission.ts";
import { updateMission } from "../UpdateMission.ts";
import { listMissions } from "../ListMissions.ts";
import { getMissionDashboardData } from "../MissionDashboard.ts";
import { deleteMission } from "../DeleteMission.ts";
import { json, error, parseBody, broadcast } from "../helpers.ts";

export async function handleMissionRoutes(
    path: string,
    method: string,
    req: Request,
    url: URL,
): Promise<Response | null> {

    // POST /api/missions - Create
    if (path === "/api/missions" && method === "POST") {
        const body = await parseBody(req);
        const result = createMission(body as any);
        if (result.created) {
            broadcast("mission", "create", result.mission);
            return json(result, 201);
        }
        return error(result.error || "Failed to create mission");
    }

    // GET /api/missions - List
    if (path === "/api/missions" && method === "GET") {
        const status = url.searchParams.get("status") || undefined;
        const sort = url.searchParams.get("sort") || undefined;
        const result = listMissions({ status, sort, verbose: true });
        return json(result);
    }

    // GET /api/missions/:id - Single mission detail
    const singleMatch = path.match(/^\/api\/missions\/([^/]+)$/);
    if (singleMatch && method === "GET") {
        const slug = decodeURIComponent(singleMatch[1]);
        const result = getMissionDashboardData(slug);
        return json(result);
    }

    // PUT /api/missions/:id - Update
    if (singleMatch && method === "PUT") {
        const slug = decodeURIComponent(singleMatch[1]);
        const body = await parseBody(req);
        const result = updateMission(slug, body as any);
        if (result.updated) {
            broadcast("mission", "update", result.mission);
            return json(result);
        }
        return error(result.error || "Failed to update mission");
    }

    // DELETE /api/missions/:id - Delete
    if (singleMatch && method === "DELETE") {
        const slug = decodeURIComponent(singleMatch[1]);
        const body = await parseBody(req).catch(() => ({}));
        const result = deleteMission(slug, body as any);
        if (!result.error) {
            broadcast("mission", "delete", { id: slug });
            return json(result);
        }
        return error(result.error || "Failed to delete mission");
    }

    return null; // Not handled
}
