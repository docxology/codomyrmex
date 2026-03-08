/**
 * helpers.ts - Shared HTTP + WebSocket helpers for PMServer routes
 *
 * Provides json(), error(), parseBody(), broadcast(), buildSafeEnv(),
 * and escapeHtmlServer() used by all route modules.
 */

import { PORT } from "./config.ts";

// ============================================================================
// WebSocket State
// ============================================================================

export const clients: Set<any> = new Set();

export function broadcast(event: string, entity: string, data: unknown) {
    const message = JSON.stringify({ event, entity, data, timestamp: Date.now() });
    for (const client of clients) {
        try {
            client.send(message);
        } catch {
            clients.delete(client);
        }
    }
}

// ============================================================================
// API Response Helpers
// ============================================================================

export function json(data: unknown, status = 200) {
    return Response.json(data, {
        status,
        headers: { "Access-Control-Allow-Origin": "*" },
    });
}

export function error(message: string, status = 400) {
    return json({ success: false, error: message }, status);
}

export async function parseBody(req: Request): Promise<Record<string, unknown>> {
    const text = await req.text();
    if (!text) return {};
    try {
        const parsed = JSON.parse(text);
        if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
            throw Object.assign(new Error("Request body must be a JSON object"), { _badRequest: true });
        }
        return parsed as Record<string, unknown>;
    } catch (e: unknown) {
        if ((e as { _badRequest?: boolean })._badRequest) throw e;
        throw Object.assign(new Error(`Invalid JSON: ${(e as Error).message}`), { _badRequest: true });
    }
}

export function buildSafeEnv(extra: Record<string, string> = {}): Record<string, string> {
    const safe: Record<string, string> = {};
    const allowlist = ["PATH", "HOME", "USER", "SHELL", "LANG", "LC_ALL", "TERM", "TMPDIR"];
    for (const key of allowlist) {
        if (process.env[key]) safe[key] = process.env[key]!;
    }
    return { ...safe, NO_COLOR: "1", ...extra };
}

export function escapeHtmlServer(s: string): string {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

/**
 * stripAnsi - Remove ANSI escape codes from LLM output.
 */
export function stripAnsi(s: string): string {
    return s.replace(/\x1b\[[0-9;?]*[A-Za-z]/g, "").replace(/\x1b\][^\x07]*\x07/g, "").trim();
}
