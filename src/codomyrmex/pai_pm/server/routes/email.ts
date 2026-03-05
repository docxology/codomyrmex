/**
 * email.ts - Email route handlers (AgentMail + Gmail + LLM Compose + Bike Ride)
 *
 * Handles /api/email/*, /api/gmail/*, /api/bikeride/* endpoints.
 */

import { json, error, parseBody, escapeHtmlServer, stripAnsi } from "../helpers.ts";
import { PORT } from "../config.ts";
import { GMAIL_TOKEN_PATH } from "../config.ts";
import {
    agentMailFetch, getAgentMailDefaultInbox,
    gmailSaveToken, gmailFetch,
    gcalFetch,
    _gmailOauthState, setGmailOauthState,
} from "../services/oauth.ts";
import { listMissions } from "../ListMissions.ts";
import { listProjects } from "../ListProjects.ts";
import { listTasks } from "../ListTasks.ts";
import { loadDashboardData } from "../PMDashboard.ts";

export async function handleEmailRoutes(
    path: string,
    method: string,
    req: Request,
    url: URL,
): Promise<Response | null> {

    // ---- AGENTMAIL ----

    if (path === "/api/email/agentmail/status" && method === "GET") {
        try {
            const data = await agentMailFetch("/inboxes");
            return json({ success: true, inboxes: data.inboxes || data || [], connected: true });
        } catch (e: any) { return json({ success: false, connected: false, error: e.message }); }
    }

    if (path === "/api/email/agentmail/inboxes" && method === "GET") {
        try { const data = await agentMailFetch("/inboxes"); return json({ success: true, inboxes: data.inboxes || data || [] }); }
        catch (e: any) { return error(e.message, 500); }
    }

    if (path === "/api/email/agentmail/messages" && method === "GET") {
        try {
            const inbox = url.searchParams.get("inbox") || getAgentMailDefaultInbox();
            const limit = String(Math.min(100, Math.max(1, parseInt(url.searchParams.get("limit") || "10", 10) || 10)));
            const data = await agentMailFetch(`/inboxes/${encodeURIComponent(inbox)}/messages?limit=${limit}`);
            return json({ success: true, messages: data.messages || data || [] });
        } catch (e: any) { return error(e.message, 500); }
    }

    if (path.match(/^\/api\/email\/agentmail\/message\/([^/]+)$/) && method === "GET") {
        const msgId = path.split("/")[5];
        try {
            const inbox = url.searchParams.get("inbox") || getAgentMailDefaultInbox();
            const data = await agentMailFetch(`/inboxes/${encodeURIComponent(inbox)}/messages/${encodeURIComponent(msgId)}`);
            return json({ success: true, message: data });
        } catch (e: any) { return error(e.message, 500); }
    }

    if (path === "/api/email/agentmail/send" && method === "POST") {
        try {
            const body = await parseBody(req);
            if (!body.to || !body.subject) return error("Missing: to, subject");
            const inbox = String(body.inbox || getAgentMailDefaultInbox());
            const payload: any = { to: Array.isArray(body.to) ? body.to : [body.to], subject: body.subject, text: body.text || "" };
            if (body.html) payload.html = body.html;
            if (body.cc) payload.cc = Array.isArray(body.cc) ? body.cc : [body.cc];
            if (body.bcc) payload.bcc = Array.isArray(body.bcc) ? body.bcc : [body.bcc];
            const data = await agentMailFetch(`/inboxes/${encodeURIComponent(inbox)}/messages/send`, { method: "POST", body: JSON.stringify(payload) });
            return json({ success: true, message: data });
        } catch (e: any) { return error(e.message, 500); }
    }

    if (path.match(/^\/api\/email\/agentmail\/reply\/([^/]+)$/) && method === "POST") {
        const msgId = path.split("/")[5];
        try {
            const body = await parseBody(req);
            const inbox = String(body.inbox || getAgentMailDefaultInbox());
            const payload: any = { text: body.text || "" };
            if (body.html) payload.html = body.html;
            if (body.reply_all !== undefined) payload.reply_all = body.reply_all;
            const data = await agentMailFetch(`/inboxes/${encodeURIComponent(inbox)}/messages/${encodeURIComponent(msgId)}/reply`, { method: "POST", body: JSON.stringify(payload) });
            return json({ success: true, message: data });
        } catch (e: any) { return error(e.message, 500); }
    }

    if (path === "/api/email/agentmail/threads" && method === "GET") {
        try {
            const inbox = url.searchParams.get("inbox") || getAgentMailDefaultInbox();
            const limit = String(Math.min(100, Math.max(1, parseInt(url.searchParams.get("limit") || "10", 10) || 10)));
            const data = await agentMailFetch(`/inboxes/${encodeURIComponent(inbox)}/threads?limit=${limit}`);
            return json({ success: true, threads: data.threads || data || [] });
        } catch (e: any) { return error(e.message, 500); }
    }

    // ---- GMAIL AUTH ----

    if (path === "/api/gmail/auth" && method === "GET") {
        const clientId = process.env.GMAIL_CLIENT_ID || process.env.GOOGLE_CLIENT_ID || "";
        if (!clientId) return error("GMAIL_CLIENT_ID not set.", 400);
        const scopes = ["https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.modify"].join(" ");
        const redirect = `http://localhost:${PORT}/api/gmail/callback`;
        const state = crypto.randomUUID();
        setGmailOauthState(state);
        const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${encodeURIComponent(clientId)}&redirect_uri=${encodeURIComponent(redirect)}&response_type=code&scope=${encodeURIComponent(scopes)}&access_type=offline&prompt=consent&state=${encodeURIComponent(state)}`;
        return json({ auth_url: authUrl });
    }

    if (path === "/api/gmail/callback" && method === "GET") {
        const stateParam = url.searchParams.get("state");
        if (!stateParam || stateParam !== _gmailOauthState) return json({ success: false, error: "Invalid OAuth state" }, 400);
        setGmailOauthState(null);
        const code = url.searchParams.get("code") || "";
        const errParam = url.searchParams.get("error") || "";
        if (errParam) return new Response(`<html><body><script>window.location='http://localhost:${PORT}/#email'<\/script><p>Auth error: ${escapeHtmlServer(errParam)}</p></body></html>`, { headers: { "Content-Type": "text/html" } });
        const clientId = process.env.GMAIL_CLIENT_ID || process.env.GOOGLE_CLIENT_ID || "";
        const clientSecret = process.env.GMAIL_CLIENT_SECRET || process.env.GOOGLE_CLIENT_SECRET || "";
        if (!code || !clientId || !clientSecret) return error("Missing OAuth parameters", 400);
        try {
            const tokenRes = await fetch("https://oauth2.googleapis.com/token", {
                method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: new URLSearchParams({ code, client_id: clientId, client_secret: clientSecret, redirect_uri: `http://localhost:${PORT}/api/gmail/callback`, grant_type: "authorization_code" }),
            });
            const tokenData: any = await tokenRes.json();
            if (tokenData.error) return new Response(`<html><body><p>OAuth error: ${tokenData.error_description || tokenData.error}</p></body></html>`, { headers: { "Content-Type": "text/html" } });
            await gmailSaveToken({ ...tokenData, saved_at: Date.now() });
            return new Response(`<html><head><meta http-equiv="refresh" content="0;url=http://localhost:${PORT}/#email"></head><body><p>Connected!</p></body></html>`, { headers: { "Content-Type": "text/html" } });
        } catch (e: any) { return error("OAuth failed: " + e.message, 500); }
    }

    if (path === "/api/gmail/status" && method === "GET") {
        const fs = await import("fs");
        const hasToken = fs.existsSync(GMAIL_TOKEN_PATH);
        const clientId = process.env.GMAIL_CLIENT_ID || process.env.GOOGLE_CLIENT_ID || "";
        const hasCredentials = !!clientId;
        if (!hasToken || !hasCredentials) {
            const redirect = `http://localhost:${PORT}/api/gmail/callback`;
            const scopes = ["https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.modify"].join(" ");
            let authUrl: string | null = null;
            if (hasCredentials) {
                const state = _gmailOauthState ?? crypto.randomUUID();
                setGmailOauthState(state);
                authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${encodeURIComponent(clientId)}&redirect_uri=${encodeURIComponent(redirect)}&response_type=code&scope=${encodeURIComponent(scopes)}&access_type=offline&prompt=consent&state=${encodeURIComponent(state)}`;
            }
            return json({ connected: false, hasCredentials, hasToken, auth_url: authUrl });
        }
        try {
            const profile = await gmailFetch("/users/me/profile");
            return json({ connected: true, email: profile.emailAddress, messages_total: profile.messagesTotal });
        } catch (e: any) { return json({ connected: false, error: e.message }); }
    }

    if (path === "/api/gmail/disconnect" && method === "POST") {
        const fs = await import("fs");
        if (fs.existsSync(GMAIL_TOKEN_PATH)) fs.unlinkSync(GMAIL_TOKEN_PATH);
        return json({ success: true });
    }

    // ---- GMAIL OPERATIONS ----

    if (path === "/api/email/gmail/messages" && method === "GET") {
        try {
            const q = url.searchParams.get("q") || "";
            const limit = String(Math.min(100, Math.max(1, parseInt(url.searchParams.get("limit") || "10", 10) || 10)));
            const listData = await gmailFetch(`/users/me/messages?maxResults=${limit}${q ? "&q=" + encodeURIComponent(q) : ""}`);
            const msgs = listData.messages || [];
            const details = await Promise.all(msgs.slice(0, 10).map((m: any) =>
                gmailFetch(`/users/me/messages/${m.id}?format=metadata&metadataHeaders=Subject&metadataHeaders=From&metadataHeaders=Date`).catch(() => m)
            ));
            return json({ success: true, messages: details });
        } catch (e: any) { return error(e.message, e.message.includes("Not authenticated") ? 401 : 500); }
    }

    if (path.match(/^\/api\/email\/gmail\/message\/([^/]+)$/) && method === "GET") {
        const msgId = path.split("/")[5];
        try {
            const data = await gmailFetch(`/users/me/messages/${encodeURIComponent(msgId)}?format=full`);
            return json({ success: true, message: data });
        } catch (e: any) { return error(e.message, 500); }
    }

    if (path === "/api/email/gmail/send" && method === "POST") {
        try {
            const body = await parseBody(req);
            if (!body.to || !body.subject) return error("Missing: to, subject");
            const to = Array.isArray(body.to) ? body.to.join(", ") : String(body.to);
            const rawMsg = [`To: ${to}`, `Subject: ${body.subject}`, "MIME-Version: 1.0", "Content-Type: text/plain; charset=utf-8", "", String(body.text || "")].join("\r\n");
            const encoded = btoa(unescape(encodeURIComponent(rawMsg))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
            const data = await gmailFetch("/users/me/messages/send", { method: "POST", body: JSON.stringify({ raw: encoded }) });
            return json({ success: true, id: data.id });
        } catch (e: any) { return error(e.message, e.message.includes("Not authenticated") ? 401 : 500); }
    }

    // ---- LLM EMAIL COMPOSE ----

    if (path === "/api/email/compose" && method === "POST") {
        const body = await parseBody(req);
        const template = String(body.template || "custom");
        const projectSlug = String(body.project || "");
        const backend = String(body.backend || "ollama");
        const model = String(body.model || "llama3.2");
        const customPrompt = String(body.prompt || "");

        // (Compose logic — uses listMissions, listProjects, listTasks, gcalFetch, LLM backends)
        // This is a large handler; see PMServer.ts lines 1834-2122 for full logic
        // Keeping as a passthrough for now — the full implementation would be identical
        return error("Email compose endpoint available in monolithic PMServer.ts — migration in progress", 501);
    }

    // ---- BIKE RIDE ----

    if (path === "/api/bikeride/load" && method === "POST") {
        return error("Bike ride endpoint available in monolithic PMServer.ts — migration in progress", 501);
    }

    if (path === "/api/bikeride/send" && method === "POST") {
        try {
            const body = await parseBody(req);
            const { threadId, to, subject, text } = body as any;
            if (!to || !text) return error("Missing: to, text");
            const replySubject = subject?.startsWith("Re:") ? subject : `Re: ${subject || ""}`;
            const rawMsg = [`To: ${to}`, `Subject: ${replySubject}`, `In-Reply-To: ${threadId || ""}`, `References: ${threadId || ""}`, "MIME-Version: 1.0", "Content-Type: text/plain; charset=utf-8", "", text].join("\r\n");
            const encoded = btoa(unescape(encodeURIComponent(rawMsg))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
            const sendPayload: any = { raw: encoded };
            if (threadId) sendPayload.threadId = threadId;
            const data = await gmailFetch("/users/me/messages/send", { method: "POST", body: JSON.stringify(sendPayload) });
            return json({ success: true, id: data.id });
        } catch (e: any) { return error(e.message, e.message?.includes("Not authenticated") ? 401 : 500); }
    }

    if (path === "/api/bikeride/tts" && method === "POST") {
        const body = await parseBody(req);
        const text = String(body.text || "").trim();
        if (!text) return error("Missing: text");
        try {
            const ts = Date.now();
            const aiffPath = `/tmp/pai_tts_${ts}.aiff`;
            const wavPath = `/tmp/pai_tts_${ts}.wav`;
            const sayPath = Bun.which("say");
            if (!sayPath) return error("'say' not found (macOS only)", 500);
            const sayProc = Bun.spawnSync([sayPath, "-o", aiffPath, "--", text.substring(0, 2000)], { timeout: 30_000 });
            if (sayProc.exitCode !== 0) return error("TTS failed: exit code " + sayProc.exitCode, 500);
            const afconvertPath = Bun.which("afconvert");
            if (afconvertPath) Bun.spawnSync([afconvertPath, aiffPath, wavPath, "-d", "LEI16", "-f", "WAVE"], { timeout: 15_000 });
            const audioFile = afconvertPath && require("fs").existsSync(wavPath) ? wavPath : aiffPath;
            const audioData = require("fs").readFileSync(audioFile);
            const base64 = Buffer.from(audioData).toString("base64");
            const mimeType = audioFile.endsWith(".wav") ? "audio/wav" : "audio/aiff";
            try { require("fs").unlinkSync(aiffPath); } catch { }
            try { require("fs").unlinkSync(wavPath); } catch { }
            return json({ success: true, audioUrl: `data:${mimeType};base64,${base64}` });
        } catch (e: any) { return error(`TTS failed: ${e.message}`, 500); }
    }

    return null;
}
