/**
 * oauth.ts - Google OAuth service layer for Calendar + Gmail
 *
 * Extracted from PMServer.ts. Provides authentication, token refresh,
 * and API fetch wrappers for Google Calendar and Gmail APIs.
 */

import { GCAL_TOKEN_PATH, GCAL_LINKS_PATH, GMAIL_TOKEN_PATH } from "../config.ts";

// ============================================================================
// OAuth State (module-level, for CSRF protection)
// ============================================================================

export let _calendarOauthState: string | null = null;
export let _gmailOauthState: string | null = null;

export function setCalendarOauthState(state: string | null) { _calendarOauthState = state; }
export function setGmailOauthState(state: string | null) { _gmailOauthState = state; }

// ============================================================================
// Google Calendar
// ============================================================================

export async function gcalSaveToken(data: unknown): Promise<void> {
    const fs = await import("fs");
    const path_mod = await import("path");
    const dir = path_mod.dirname(GCAL_TOKEN_PATH);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    const tmpPath = GCAL_TOKEN_PATH + ".tmp";
    fs.writeFileSync(tmpPath, JSON.stringify(data, null, 2), { mode: 0o600 });
    fs.renameSync(tmpPath, GCAL_TOKEN_PATH);
}

export async function gcalGetAccessToken(): Promise<string> {
    const fs = await import("fs");
    if (!fs.existsSync(GCAL_TOKEN_PATH)) throw new Error("Not authenticated with Google Calendar");
    let token: any = JSON.parse(fs.readFileSync(GCAL_TOKEN_PATH, "utf-8"));
    const expiresAt = (token.saved_at || 0) + ((token.expires_in || 3600) * 1000);
    if (Date.now() > expiresAt - 60000 && token.refresh_token) {
        const clientId = process.env.GOOGLE_CLIENT_ID || "";
        const clientSecret = process.env.GOOGLE_CLIENT_SECRET || "";
        if (clientId && clientSecret) {
            const res = await fetch("https://oauth2.googleapis.com/token", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: new URLSearchParams({ refresh_token: token.refresh_token, client_id: clientId, client_secret: clientSecret, grant_type: "refresh_token" }),
            });
            const refreshed: any = await res.json();
            if (!refreshed.error) { token = { ...token, ...refreshed, saved_at: Date.now() }; await gcalSaveToken(token); }
        }
    }
    if (!token.access_token) throw new Error("No access token available");
    return token.access_token;
}

export async function gcalFetch(endpoint: string, options: RequestInit = {}): Promise<any> {
    const accessToken = await gcalGetAccessToken();
    const res = await fetch("https://www.googleapis.com/calendar/v3" + endpoint, {
        ...options,
        headers: { "Authorization": "Bearer " + accessToken, "Content-Type": "application/json", ...(options.headers || {}) },
    });
    if (!res.ok) { const err: any = await res.json().catch(() => ({})); throw new Error(err.error?.message || "Google Calendar API error " + res.status); }
    if (res.status === 204) return {};
    return res.json();
}

export function gcalLoadLinks(): Record<string, string> {
    try {
        const fs = require("fs");
        if (!fs.existsSync(GCAL_LINKS_PATH)) return {};
        return JSON.parse(fs.readFileSync(GCAL_LINKS_PATH, "utf-8"));
    } catch { return {}; }
}

export function gcalSaveLinks(links: Record<string, string>): void {
    try {
        const fs = require("fs");
        const path_mod = require("path");
        const dir = path_mod.dirname(GCAL_LINKS_PATH);
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
        fs.writeFileSync(GCAL_LINKS_PATH, JSON.stringify(links, null, 2));
    } catch { }
}

// ============================================================================
// Gmail
// ============================================================================

export async function gmailSaveToken(data: unknown): Promise<void> {
    const fs = await import("fs");
    const path_mod = await import("path");
    const dir = path_mod.dirname(GMAIL_TOKEN_PATH);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    const tmpPath = GMAIL_TOKEN_PATH + ".tmp";
    fs.writeFileSync(tmpPath, JSON.stringify(data, null, 2), { mode: 0o600 });
    fs.renameSync(tmpPath, GMAIL_TOKEN_PATH);
}

export async function gmailGetAccessToken(): Promise<string> {
    const fs = await import("fs");
    if (!fs.existsSync(GMAIL_TOKEN_PATH)) throw new Error("Not authenticated with Gmail");
    let token: any = JSON.parse(fs.readFileSync(GMAIL_TOKEN_PATH, "utf-8"));
    const expiresAt = (token.saved_at || 0) + ((token.expires_in || 3600) * 1000);
    if (Date.now() > expiresAt - 60000 && token.refresh_token) {
        const clientId = process.env.GMAIL_CLIENT_ID || process.env.GOOGLE_CLIENT_ID || "";
        const clientSecret = process.env.GMAIL_CLIENT_SECRET || process.env.GOOGLE_CLIENT_SECRET || "";
        if (clientId && clientSecret) {
            const res = await fetch("https://oauth2.googleapis.com/token", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: new URLSearchParams({ refresh_token: token.refresh_token, client_id: clientId, client_secret: clientSecret, grant_type: "refresh_token" }),
            });
            const refreshed: any = await res.json();
            if (!refreshed.error) { token = { ...token, ...refreshed, saved_at: Date.now() }; await gmailSaveToken(token); }
        }
    }
    if (!token.access_token) throw new Error("No Gmail access token available");
    return token.access_token;
}

export async function gmailFetch(endpoint: string, options: RequestInit = {}): Promise<any> {
    const accessToken = await gmailGetAccessToken();
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 30_000);
    try {
        const res = await fetch("https://gmail.googleapis.com/gmail/v1" + endpoint, {
            ...options,
            signal: controller.signal,
            headers: { "Authorization": "Bearer " + accessToken, "Content-Type": "application/json", ...((options.headers as Record<string, string>) || {}) },
        });
        if (!res.ok) { const err: any = await res.json().catch(() => ({})); throw new Error(err.error?.message || "Gmail API error " + res.status); }
        if (res.status === 204) return {};
        return res.json();
    } finally {
        clearTimeout(timer);
    }
}

// ============================================================================
// AgentMail
// ============================================================================

const AGENTMAIL_BASE = "https://api.agentmail.to/v0";

export function getAgentMailDefaultInbox(): string {
    return process.env.AGENTMAIL_DEFAULT_INBOX || "fristonblanket@agentmail.to";
}

export async function agentMailFetch(path: string, options: RequestInit = {}): Promise<any> {
    const apiKey = process.env.AGENTMAIL_API_KEY;
    if (!apiKey) throw new Error("AGENTMAIL_API_KEY not set");
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 30_000);
    try {
        const res = await fetch(`${AGENTMAIL_BASE}${path}`, {
            ...options,
            signal: controller.signal,
            headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json", ...((options.headers as Record<string, string>) || {}) },
        });
        if (!res.ok) throw new Error(`AgentMail ${res.status}: ${await res.text()}`);
        return res.json();
    } finally {
        clearTimeout(timer);
    }
}
