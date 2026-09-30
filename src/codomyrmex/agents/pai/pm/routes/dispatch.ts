/**
 * dispatch.ts - Dispatch execution, queue, and context sidecar route handlers
 *
 * Handles /api/dispatch/* endpoints for LLM dispatch (Claude/Ollama/Gemini),
 * job tracking, dispatch queue, and project/mission context storage.
 */

import { json, error, parseBody, broadcast, buildSafeEnv, stripAnsi } from "../helpers.ts";
import { PORT, LLM_BACKEND, LLM_MODEL, LLM_TIMEOUT, PAI_DIR, PROJECTS_DIR, MISSIONS_DIR } from "../config.ts";
import { listMissions } from "../ListMissions.ts";
import { listProjects } from "../ListProjects.ts";
import { listTasks } from "../ListTasks.ts";
import { loadDashboardData } from "../PMDashboard.ts";
import { existsSync, readFileSync, writeFileSync } from "fs";
import { join } from "path";

const yaml = await import("js-yaml");
const TIMEOUT_MS = LLM_TIMEOUT * 2; // dispatch gets 2× the LLM timeout

export async function handleDispatchRoutes(
    path: string,
    method: string,
    req: Request,
    url: URL,
): Promise<Response | null> {

    // ---- DISPATCH EXECUTION ----

    if (path === "/api/dispatch/execute" && method === "POST") {
        const body = await parseBody(req);
        const backend = String(body.backend || LLM_BACKEND);
        const action = String(body.action || "");
        const jobId = `dispatch-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`;

        if (!globalThis._dispatchJobs) globalThis._dispatchJobs = new Map();

        const job: any = { id: jobId, status: "running", output: "", action, backend, startedAt: Date.now() };
        globalThis._dispatchJobs.set(jobId, job);

        // Build prompt from context
        let prompt = action;
        if (body.context) prompt = `Context:\n${JSON.stringify(body.context, null, 2)}\n\nAction: ${action}`;

        const startTime = Date.now();

        // Execute in background
        (async () => {
            try {
                let cmd: string[] = [];
                let modelName = "";

                if (backend === "ollama") {
                    const ollamaPath = Bun.which("ollama") ?? "ollama";
                    const model = String(body.model || LLM_MODEL);
                    cmd = [ollamaPath, "run", model, prompt];
                    modelName = model;
                } else if (backend === "claude") {
                    const claudePath = Bun.which("claude") ?? "claude";
                    cmd = [claudePath, "-p", "--output-format", "stream-json", prompt];
                    modelName = "Claude (Sonnet)";
                } else if (backend === "gemini") {
                    const geminiPath = Bun.which("gemini") ?? "gemini";
                    cmd = [geminiPath, "-m", "gemini-2.5-flash", "--output-format", "text", prompt];
                    modelName = "Gemini 2.5 Flash";
                } else {
                    throw new Error(`Unknown backend: ${backend}`);
                }

                job.output = `⏳ Starting ${backend} (model: ${modelName})...\n`;
                broadcast("dispatch", "progress", { id: jobId, output: job.output });

                const proc = Bun.spawn(cmd, { stdout: "pipe", stderr: "pipe", env: buildSafeEnv() });
                const reader = proc.stdout.getReader();
                const decoder = new TextDecoder();
                let tokenCount = 0;
                let lastBroadcast = Date.now();

                const readStream = async () => {
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        const chunk = decoder.decode(value, { stream: true });
                        job.output += chunk;
                        tokenCount += chunk.split(/\s+/).filter(Boolean).length;

                        if (Date.now() - lastBroadcast > 300) {
                            const elapsed = (Date.now() - startTime) / 1000;
                            broadcast("dispatch", "progress", {
                                id: jobId, output: job.output, tokens: tokenCount,
                                tokensPerSec: (tokenCount / elapsed).toFixed(1), elapsed: elapsed.toFixed(1), model: modelName,
                            });
                            lastBroadcast = Date.now();
                        }
                        if (Date.now() - startTime > TIMEOUT_MS) { proc.kill(); throw new Error("Timeout: exceeded 2 minutes"); }
                    }
                };

                await Promise.race([readStream(), new Promise((_, reject) => setTimeout(() => reject(new Error("Timeout")), TIMEOUT_MS))]);

                const stderr = await new Response(proc.stderr).text();
                const exitCode = await proc.exited;
                const elapsed = (Date.now() - startTime) / 1000;

                if (stderr && exitCode !== 0) job.output += `\n\n⚠️ STDERR:\n${stderr}`;
                job.output += `\n\n---\n✅ Model: ${modelName}\n📊 Tokens: ~${tokenCount} (${(tokenCount / elapsed).toFixed(1)} tok/s)\n⏱️ Time: ${elapsed.toFixed(1)}s`;
                job.status = exitCode === 0 ? "complete" : "error";
                job.error = exitCode !== 0 ? `Exit code: ${exitCode}` : undefined;
                job.completedAt = Date.now();
                if (globalThis._dispatchJobs.size > 100) {
                    const oldest = [...globalThis._dispatchJobs.keys()].slice(0, globalThis._dispatchJobs.size - 100);
                    oldest.forEach((k: string) => globalThis._dispatchJobs.delete(k));
                }
                broadcast("dispatch", "job", { id: jobId, status: job.status, action, tokens: tokenCount, elapsed });
            } catch (err: any) {
                job.output += `\n\n❌ Error: ${err.message}`;
                job.status = "error"; job.error = err.message; job.completedAt = Date.now();
                broadcast("dispatch", "job", { id: jobId, status: "error", error: err.message });
            }
        })();

        return json({ success: true, jobId, status: "running", message: `Dispatch job started with ${backend}` }, 202);
    }

    // GET /api/dispatch/status/:id
    if (path.match(/^\/api\/dispatch\/status\/([^/]+)$/) && method === "GET") {
        const jobId = path.split("/")[4];
        const job = globalThis._dispatchJobs?.get(jobId);
        if (!job) return error(`Job not found: ${jobId}`, 404);
        return json(job);
    }

    // GET /api/dispatch/jobs
    if (path === "/api/dispatch/jobs" && method === "GET") {
        const jobs = Array.from(globalThis._dispatchJobs?.values() || [])
            .sort((a: any, b: any) => b.startedAt - a.startedAt).slice(0, 20);
        return json({ jobs });
    }

    // ---- CONTEXT SIDECAR ----

    if (!globalThis._dispatchContexts) {
        globalThis._dispatchContexts = new Map<string, any>();
    }

    const projectContextMatch = path.match(/^\/api\/projects\/([^/]+)\/context$/);
    if (projectContextMatch && method === "PUT") {
        const projectId = decodeURIComponent(projectContextMatch[1]);
        const body = await parseBody(req);
        globalThis._dispatchContexts.set(`project:${projectId}`, {
            links: body.links || [], summary: body.summary || "", notes: body.notes || "", dispatch_history: body.dispatch_history || {},
        });
        const projectFile = join(PROJECTS_DIR, projectId, "project.yaml");
        if (existsSync(projectFile)) {
            const data = yaml.load(readFileSync(projectFile, "utf8")) as any;
            data.dispatch_context = globalThis._dispatchContexts.get(`project:${projectId}`);
            writeFileSync(projectFile, yaml.dump(data));
        }
        broadcast("project", "update", { id: projectId });
        return json({ success: true });
    }

    if (projectContextMatch && method === "GET") {
        const projectId = decodeURIComponent(projectContextMatch[1]);
        const ctx = globalThis._dispatchContexts.get(`project:${projectId}`) || { links: [], summary: "", notes: "", dispatch_history: {} };
        return json(ctx);
    }

    const missionContextMatch = path.match(/^\/api\/missions\/([^/]+)\/context$/);
    if (missionContextMatch && method === "PUT") {
        const missionId = decodeURIComponent(missionContextMatch[1]);
        const body = await parseBody(req);
        globalThis._dispatchContexts.set(`mission:${missionId}`, {
            links: body.links || [], summary: body.summary || "", notes: body.notes || "", dispatch_history: body.dispatch_history || {},
        });
        const missionsFile = join(MISSIONS_DIR, "missions.yaml");
        if (existsSync(missionsFile)) {
            const missions = (yaml.load(readFileSync(missionsFile, "utf8")) as any[]) || [];
            const m = missions.find((x: any) => x.id === missionId);
            if (m) { m.dispatch_context = globalThis._dispatchContexts.get(`mission:${missionId}`); writeFileSync(missionsFile, yaml.dump(missions)); }
        }
        broadcast("mission", "update", { id: missionId });
        return json({ success: true });
    }

    if (missionContextMatch && method === "GET") {
        const missionId = decodeURIComponent(missionContextMatch[1]);
        const ctx = globalThis._dispatchContexts.get(`mission:${missionId}`) || { links: [], summary: "", notes: "", dispatch_history: {} };
        return json(ctx);
    }

    // ---- DISPATCH QUEUE ----

    if (!globalThis._dispatchQueue) globalThis._dispatchQueue = [] as any[];

    if (path === "/api/dispatch/queue" && method === "POST") {
        const body = await parseBody(req);
        if (!body.entityType || !body.entityId || !body.action) return error("Missing: entityType, entityId, action");
        const queueItem = {
            id: `queue-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
            entityType: body.entityType, entityId: body.entityId, action: body.action,
            backend: body.backend || LLM_BACKEND, model: body.model || LLM_MODEL, addedAt: Date.now(),
        };
        globalThis._dispatchQueue.push(queueItem);
        broadcast("dispatch", "queue", { action: "add", item: queueItem });
        return json({ success: true, item: queueItem }, 201);
    }

    if (path === "/api/dispatch/queue" && method === "GET") {
        return json({ queue: globalThis._dispatchQueue || [] });
    }

    const queueDeleteMatch = path.match(/^\/api\/dispatch\/queue\/([^/]+)$/);
    if (queueDeleteMatch && method === "DELETE") {
        const itemId = queueDeleteMatch[1];
        const idx = globalThis._dispatchQueue.findIndex((q: any) => q.id === itemId);
        if (idx === -1) return error("Queue item not found", 404);
        globalThis._dispatchQueue.splice(idx, 1);
        broadcast("dispatch", "queue", { action: "remove", id: itemId });
        return json({ success: true });
    }

    if (path === "/api/dispatch/queue/run" && method === "POST") {
        if (globalThis._queueRunning) return error("Queue run already in progress", 409);
        globalThis._queueRunning = true;
        const queue = [...(globalThis._dispatchQueue || [])];
        globalThis._dispatchQueue = [];
        broadcast("dispatch", "queue", { action: "running", count: queue.length });
        (async () => {
            for (const item of queue) {
                const jobId = `dispatch-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`;
                globalThis._dispatchJobs.set(jobId, {
                    id: jobId, status: "running", output: `Queue item: ${item.action} on ${item.entityType}/${item.entityId}`,
                    action: item.action, backend: item.backend, startedAt: Date.now(),
                });
                broadcast("dispatch", "queue", { action: "item-start", item, jobId });
                await new Promise(resolve => setTimeout(resolve, 100));
            }
            broadcast("dispatch", "queue", { action: "complete", count: queue.length });
            globalThis._queueRunning = false;
        })().catch(() => { globalThis._queueRunning = false; });
        return json({ success: true, message: `Running ${queue.length} queued items` });
    }

    return null;
}
