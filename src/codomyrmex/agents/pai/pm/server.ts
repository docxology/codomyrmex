#!/usr/bin/env bun
/**
 * server.ts - Modular PAI PM Server
 *
 * This is the decomposed version of PMServer.ts, routing requests to
 * focused handler modules. It serves the same REST API + WebSocket + SPA
 * as the monolithic original but in a maintainable, modular structure.
 *
 * Usage:
 *   bun scripts/pai/pm/server.ts                    # Start on port 8889
 *   bun scripts/pai/pm/server.ts --port 8888        # Custom port
 *
 * @version 2.0.0 (modular decomposition)
 */

import { PORT } from "./config.ts";
import { json, error, clients } from "./helpers.ts";
import { loadDashboardData, generateHTML } from "./PMDashboard.ts";

// Route handlers
import { handleMissionRoutes } from "./routes/missions.ts";
import { handleProjectRoutes } from "./routes/projects.ts";
import { handleTaskRoutes } from "./routes/tasks.ts";
import { handleGitHubRoutes } from "./routes/github.ts";
import { handleDispatchRoutes } from "./routes/dispatch.ts";
import { handleInterviewRoutes } from "./routes/interview.ts";
import { handleAwarenessRoutes } from "./routes/awareness.ts";
import { handleCalendarRoutes } from "./routes/calendar.ts";
import { handleEmailRoutes } from "./routes/email.ts";

// ============================================================================
// Main API router
// ============================================================================

async function handleAPI(req: Request): Promise<Response> {
    const url = new URL(req.url);
    const path = url.pathname;
    const method = req.method;

    // CORS preflight
    if (method === "OPTIONS") {
        return new Response(null, {
            status: 204,
            headers: {
                "Access-Control-Allow-Origin": `http://localhost:${PORT}`,
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        });
    }

    // Health check
    if (path === "/api/health" && method === "GET") {
        return json({ status: "ok", port: PORT, uptime: process.uptime() });
    }

    // State sync
    if (path === "/api/state" && method === "GET") {
        try { return json(loadDashboardData()); }
        catch { return json({ missions: [], projects: [], orphan_projects: [], stats: {} }); }
    }

    // Route to focused handlers (order matters — more specific routes first)
    const handlers = [
        handleMissionRoutes,
        handleProjectRoutes,
        handleTaskRoutes,
        handleGitHubRoutes,
        handleDispatchRoutes,
        handleInterviewRoutes,
        handleAwarenessRoutes,
        handleCalendarRoutes,
        handleEmailRoutes,
    ];

    for (const handler of handlers) {
        const response = await handler(path, method, req, url);
        if (response) return response;
    }

    // Serve SPA for non-API routes
    if (!path.startsWith("/api/")) {
        try {
            const spaPath = new URL("./spa/index.html", import.meta.url).pathname;
            const file = Bun.file(spaPath);
            if (await file.exists()) {
                return new Response(file, {
                    headers: { "Content-Type": "text/html; charset=utf-8" },
                });
            }
            // Fallback: generate from PMDashboard
            const data = loadDashboardData();
            const html = generateHTML(data);
            return new Response(html, {
                status: 200,
                headers: { "Content-Type": "text/html; charset=utf-8" },
            });
        } catch (e: any) {
            return new Response(`Dashboard error: ${e.message}`, {
                status: 500, headers: { "Content-Type": "text/plain" },
            });
        }
    }

    return error("Not found", 404);
}

// ============================================================================
// Server
// ============================================================================

const server = Bun.serve({
    port: PORT,
    async fetch(req) {
        // WebSocket upgrade
        if (req.headers.get("upgrade")?.toLowerCase() === "websocket") {
            const upgraded = server.upgrade(req);
            if (!upgraded) return new Response("WebSocket upgrade failed", { status: 400 });
            return undefined as any;
        }
        try {
            return await handleAPI(req);
        } catch (e: any) {
            console.error("[PMServer] request error:", e);
            return error(e.message || "Internal server error", 500);
        }
    },
    websocket: {
        open(ws: any) { clients.add(ws); },
        close(ws: any) { clients.delete(ws); },
        message(_ws: any, _msg: any) { /* client messages not used */ },
    },
});

console.log(`\n🚀 PAI PM Server (modular) on http://localhost:${PORT}\n`);
console.log(`   Routes: missions, projects, tasks, github, dispatch, interview, awareness, calendar, email`);
console.log(`   WebSocket: ws://localhost:${PORT}\n`);
