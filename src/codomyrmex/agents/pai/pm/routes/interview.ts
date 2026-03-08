/**
 * interview.ts - Interview system route handlers
 *
 * Handles /api/interview/* endpoints for starting interviews,
 * submitting answers, generating AI-powered questions and summaries.
 */

import { json, error, parseBody, broadcast } from "../helpers.ts";
import { LLM_MODEL } from "../config.ts";

export async function handleInterviewRoutes(
    path: string,
    method: string,
    req: Request,
    _url: URL,
): Promise<Response | null> {

    // Initialize interview sessions
    if (!globalThis._interviewSessions) {
        globalThis._interviewSessions = new Map<string, any>();
    }

    // POST /api/interview/start
    if (path === "/api/interview/start" && method === "POST") {
        const body = await parseBody(req);
        if (!body.entityType || !body.entityId || !body.interviewType) {
            return error("Missing: entityType, entityId, interviewType");
        }

        const sessionId = `interview-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`;
        const entityTitle = String(body.entityTitle || body.entityId);

        const interviewPrompts: Record<string, string> = {
            onboarding: `Generate 5 smart interview questions for onboarding a new ${body.entityType} called "${entityTitle}". Questions should gather: goals, scope, success criteria, key stakeholders, and timeline. Format as JSON array of strings like ["Q1?", "Q2?"].`,
            checkpoint: `Generate 5 checkpoint interview questions for the ${body.entityType} "${entityTitle}". Questions should cover: recent progress, current blockers, resource needs, next priorities, and team morale. Format as JSON array of strings.`,
            retrospective: `Generate 5 retrospective interview questions for the ${body.entityType} "${entityTitle}". Questions should explore: what went well, what could improve, key learnings, process changes, and future recommendations. Format as JSON array of strings.`,
            clarification: `Generate 5 clarification questions to better understand the ${body.entityType} "${entityTitle}". Questions should probe: ambiguous areas, dependencies, assumptions, risks, and definitions. Format as JSON array of strings.`,
        };

        const prompt = interviewPrompts[String(body.interviewType)] || interviewPrompts.checkpoint;

        let questions: string[] = [];
        try {
            const ollamaPath = Bun.which("ollama") ?? "ollama";
            const proc = Bun.spawn([ollamaPath, "run", LLM_MODEL, prompt], {
                stdout: "pipe", stderr: "pipe", env: { ...process.env, NO_COLOR: "1" },
            });
            const output = await new Response(proc.stdout).text();
            const jsonMatch = output.match(/\[[\s\S]*?\]/);
            if (jsonMatch) {
                const parsed = JSON.parse(jsonMatch[0]);
                questions = parsed.map((item: any) => {
                    if (typeof item === "string") return item;
                    if (typeof item === "object" && item !== null) return item.question || item.content || item.text || item.q || JSON.stringify(item);
                    return String(item);
                });
            } else {
                questions = output.split(/\d+[.)]\s*/).filter(q => q.trim().length > 10).slice(0, 5);
            }
        } catch (e) {
            const errMsg = e instanceof Error ? e.message : String(e);
            return error(`Failed to generate interview questions via ollama: ${errMsg}`, 503);
        }

        const session = {
            id: sessionId, entityType: body.entityType, entityId: body.entityId, entityTitle,
            interviewType: body.interviewType,
            questions: questions.map((q: string) => ({ q, a: "" })),
            currentIdx: 0, startedAt: Date.now(),
        };

        globalThis._interviewSessions.set(sessionId, session);
        broadcast("interview", "start", { session });

        return json({ success: true, session, sessionId, totalQuestions: questions.length, currentQuestion: questions[0], currentIdx: 0 }, 201);
    }

    // GET /api/interview/sessions
    if (path === "/api/interview/sessions" && method === "GET") {
        const sessions = Array.from(globalThis._interviewSessions.values())
            .sort((a: any, b: any) => b.startedAt - a.startedAt).slice(0, 50);
        return json({ sessions });
    }

    // GET /api/interview/session/:id
    const sessionMatch = path.match(/^\/api\/interview\/session\/([^/]+)$/);
    if (sessionMatch && method === "GET") {
        const session = globalThis._interviewSessions.get(sessionMatch[1]);
        if (!session) return error("Session not found", 404);
        return json({ session });
    }

    // POST /api/interview/respond
    if (path === "/api/interview/respond" && method === "POST") {
        const body = await parseBody(req);
        if (!body.sessionId || body.answer === undefined) return error("Missing: sessionId, answer");

        const session = globalThis._interviewSessions.get(String(body.sessionId));
        if (!session) return error("Session not found", 404);

        if (session.currentIdx < session.questions.length) {
            session.questions[session.currentIdx].a = body.answer;
            session.questions[session.currentIdx].answeredAt = Date.now();
        }

        session.currentIdx++;
        const isComplete = session.currentIdx >= session.questions.length;

        if (isComplete) {
            session.completedAt = Date.now();
            const qaPairs = session.questions.map((q: any, i: number) => `Q${i + 1}: ${q.q}\nA: ${q.a}`).join("\n\n");
            const summaryPrompt = `Summarize the key insights from this interview about "${session.entityTitle}" (${session.entityType}):\n\n${qaPairs}\n\nProvide a concise 2-3 sentence summary capturing the main takeaways.`;

            try {
                const ollamaPath = Bun.which("ollama") ?? "ollama";
                const proc = Bun.spawn([ollamaPath, "run", LLM_MODEL, summaryPrompt], {
                    stdout: "pipe", stderr: "pipe", env: { ...process.env, NO_COLOR: "1" },
                });
                session.summary = await new Response(proc.stdout).text();
            } catch {
                session.summary = `Interview completed with ${session.questions.length} responses.`;
            }

            // Store in entity context
            if (!globalThis._dispatchContexts) globalThis._dispatchContexts = new Map();
            const contextKey = `${session.entityType}:${session.entityId}`;
            const existing = globalThis._dispatchContexts.get(contextKey) || { links: [], summary: "", notes: "", dispatch_history: {} };
            existing.notes = (existing.notes || "") + `\n\n--- Interview (${session.interviewType}) ${new Date().toISOString().slice(0, 10)} ---\n${session.summary}`;
            globalThis._dispatchContexts.set(contextKey, existing);

            broadcast("interview", "complete", { sessionId: session.id, summary: session.summary });
        }

        return json({
            success: true, isComplete, currentIdx: session.currentIdx,
            currentQuestion: isComplete ? null : session.questions[session.currentIdx]?.q,
            summary: isComplete ? session.summary : undefined,
        });
    }

    // DELETE /api/interview/session/:id
    if (sessionMatch && method === "DELETE") {
        const deleted = globalThis._interviewSessions.delete(sessionMatch[1]);
        return json({ success: deleted });
    }

    return null;
}
