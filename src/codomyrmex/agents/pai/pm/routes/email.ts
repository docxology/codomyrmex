/**
 * email.ts - Email route handlers (AgentMail + Gmail + LLM Compose + Bike Ride)
 *
 * Handles /api/email/*, /api/gmail/*, /api/bikeride/* endpoints.
 */

import { json, error, parseBody, escapeHtmlServer, stripAnsi } from "../helpers.ts";
import { PORT, LLM_BACKEND, LLM_MODEL, LLM_TIMEOUT } from "../config.ts";
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
        const backend = String(body.backend || LLM_BACKEND);
        const model = String(body.model || LLM_MODEL);
        const customPrompt = String(body.prompt || "");

        // Gather rich context data from real sources
        let contextData = "";
        const now = new Date();
        const dateStr = now.toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" });
        const timeStr = now.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
        contextData += `# Context Snapshot — ${dateStr} at ${timeStr}\n\n`;

        try {
            const missions = listMissions({ verbose: true });
            const projects = listProjects({ verbose: true });
            const stats = loadDashboardData()?.stats || {};

            contextData += `## Overview\n`;
            contextData += `- Active Missions: ${stats.active_missions || missions.length}\n`;
            contextData += `- Total Projects: ${projects.length}\n`;
            contextData += `- Total Tasks: ${stats.total_tasks || 0}\n`;
            contextData += `- Completed Tasks: ${stats.completed_tasks || 0}\n`;
            contextData += `- Overdue Tasks: ${stats.overdue_tasks || 0}\n`;
            contextData += `- Blocked Tasks: ${stats.blocked_tasks || 0}\n\n`;

            // Missions with full detail
            if (missions.length > 0 && (template !== "project-summary" || !projectSlug)) {
                contextData += `## Missions\n`;
                for (const m of missions) {
                    contextData += `### ${m.title || m.slug} [${m.status || "ACTIVE"}]\n`;
                    if (m.description) contextData += `  Description: ${m.description}\n`;
                    if (m.vision) contextData += `  Vision: ${m.vision}\n`;
                    if (m.priority) contextData += `  Priority: ${m.priority}\n`;
                    const linked = m.projects || m.linked_projects || [];
                    if (linked.length > 0) contextData += `  Linked Projects: ${linked.join(", ")}\n`;
                    if (m.criteria?.length) contextData += `  Success Criteria: ${m.criteria.join("; ")}\n`;
                    contextData += `\n`;
                }
            }

            // Projects with tasks
            const targetProjects = projectSlug
                ? projects.filter((p: any) => p.slug === projectSlug || (p.title || "").toLowerCase().includes(projectSlug.toLowerCase()))
                : projects;
            const isDailySchedule = template === "daily-schedule";

            if (targetProjects.length > 0) {
                contextData += `## Projects\n`;
                for (const proj of targetProjects) {
                    try {
                        const tasks = listTasks({ project: proj.slug });
                        const metaPrefixes = ["priority:", "created:", "due:", "assignee:", "blocked by:", "spec:", "depends on:"];
                        const realTasks = (tasks || []).filter((t: any) => {
                            const title = (t.title || t.text || "").toLowerCase().trim();
                            return !metaPrefixes.some(p => title.startsWith(p));
                        });
                        const completed = realTasks.filter((t: any) => (t.section || "").toLowerCase() === "completed").length;
                        const inProgress = realTasks.filter((t: any) => ["in_progress", "in progress", "active"].includes((t.section || "").toLowerCase()));
                        const overdue = realTasks.filter((t: any) => t.due && new Date(t.due) < now && (t.section || "").toLowerCase() !== "completed");
                        const pct = realTasks.length > 0 ? Math.round((completed / realTasks.length) * 100) : 0;

                        if (isDailySchedule && inProgress.length === 0 && overdue.length === 0) continue;

                        contextData += `### ${proj.title || proj.slug} [${proj.status || "UNKNOWN"}] — ${pct}% complete\n`;
                        if (proj.goal) contextData += `  Goal: ${proj.goal}\n`;

                        if (isDailySchedule) {
                            if (inProgress.length > 0) {
                                contextData += `  In Progress:\n`;
                                for (const t of inProgress.slice(0, 5)) {
                                    contextData += `    - ${t.title || t.text}${t.priority ? " [" + t.priority + "]" : ""}${t.due ? " (due: " + t.due + ")" : ""}\n`;
                                }
                            }
                            if (overdue.length > 0) {
                                contextData += `  OVERDUE:\n`;
                                for (const t of overdue.slice(0, 3)) {
                                    contextData += `    - ${t.title || t.text} (due: ${t.due})\n`;
                                }
                            }
                        } else {
                            if (proj.target) contextData += `  Target: ${proj.target}\n`;
                            if (proj.priority) contextData += `  Priority: ${proj.priority}\n`;
                            if (proj.blocked_by) contextData += `  Blocked By: ${proj.blocked_by}\n`;
                            contextData += `  Progress: ${completed}/${realTasks.length} tasks (${pct}%)\n`;
                            const sections: Record<string, any[]> = {};
                            for (const t of realTasks) {
                                const sec = (t.section || "backlog").toLowerCase();
                                if (!sections[sec]) sections[sec] = [];
                                sections[sec].push(t);
                            }
                            for (const [sec, secTasks] of Object.entries(sections)) {
                                contextData += `  [${sec.toUpperCase()}] (${secTasks.length}):\n`;
                                for (const t of secTasks.slice(0, 15)) {
                                    let line = `    - ${t.title || t.text}`;
                                    if (t.priority) line += ` [${t.priority}]`;
                                    if (t.due) line += ` (due: ${t.due})`;
                                    if (t.assignee) line += ` @${t.assignee}`;
                                    contextData += line + `\n`;
                                }
                                if (secTasks.length > 15) contextData += `    ... and ${secTasks.length - 15} more\n`;
                            }
                        }
                    } catch { contextData += `  Tasks: unable to load\n`; }
                    contextData += `\n`;
                }
            }

            // Calendar events
            if (template === "daily-schedule" || template === "all-projects") {
                try {
                    const tomorrow = new Date(now);
                    tomorrow.setDate(tomorrow.getDate() + 1);
                    tomorrow.setHours(23, 59, 59, 999);
                    const events = await gcalFetch(`/calendars/primary/events?timeMin=${now.toISOString()}&timeMax=${tomorrow.toISOString()}&singleEvents=true&orderBy=startTime&maxResults=30`);
                    if (events?.items?.length) {
                        contextData += `## Calendar Events\n`;
                        let currentDay = "";
                        for (const ev of events.items) {
                            const start = ev.start?.dateTime || ev.start?.date || "";
                            const end = ev.end?.dateTime || ev.end?.date || "";
                            const evDate = start ? new Date(start).toLocaleDateString() : "";
                            if (evDate !== currentDay) {
                                currentDay = evDate;
                                contextData += `\n### ${evDate === now.toLocaleDateString() ? "Today" : "Tomorrow"} (${evDate})\n`;
                            }
                            let line = "- ";
                            if (ev.start?.dateTime) {
                                line += `${new Date(start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
                                if (ev.end?.dateTime) line += ` – ${new Date(end).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
                                line += ": ";
                            }
                            line += ev.summary || "(untitled)";
                            if (ev.location) line += ` [${ev.location}]`;
                            contextData += line + `\n`;
                        }
                        contextData += `\n`;
                    } else {
                        contextData += `## Calendar: No events scheduled for today/tomorrow\n\n`;
                    }
                } catch (e: any) {
                    contextData += `## Calendar: Not connected (${e.message})\n\n`;
                }
            }

            // Interview context
            if (template === "interview-followup") {
                contextData += `## Interview Context\n`;
                if (projectSlug) {
                    const proj = projects.find((p: any) => p.slug === projectSlug);
                    if (proj) {
                        contextData += `Related project: ${proj.title || proj.slug}\n`;
                        if (proj.goal) contextData += `Project goal: ${proj.goal}\n`;
                    }
                }
                contextData += `Date: ${dateStr}\n\n`;
            }
        } catch (e: any) {
            contextData += `Note: Some data sources unavailable: ${e.message}\n`;
        }

        // Build LLM prompt
        const templatePrompts: Record<string, string> = {
            "daily-schedule": `You are writing a "Daily Schedule Summary" email for ${dateStr}. You MUST reference the SPECIFIC calendar events, project names, and task names from the context below. Structure: 1. Today's Calendar 2. Active Work 3. Overdue/Blocked items 4. Key priorities. Use the EXACT names from the data below.`,
            "all-projects": `You are writing an "All Projects Status Summary" email. Reference EVERY project by its EXACT name from the context. Include actual completion %, specific in-progress tasks, and any blockers. Structure as a per-project breakdown with a brief executive summary.`,
            "project-summary": `You are writing a "Project Status Update" email. Use the EXACT project name, goal, task titles, and completion data from the context. Include: current status, specific completed/in-progress tasks, blockers, and concrete next steps.`,
            "interview-followup": `Write a warm, professional interview follow-up email. Thank the interviewer, express genuine enthusiasm for the role. If project context is provided, reference it naturally. Keep it concise but personal.`,
            "custom": `Write an email based on this instruction: ${customPrompt}\n\nUse any relevant data from the context below.`,
        };

        const systemPrompt = templatePrompts[template] || templatePrompts["custom"];
        const MAX_CONTEXT = backend === "ollama" ? 4000 : 8000;
        if (contextData.length > MAX_CONTEXT) {
            contextData = contextData.substring(0, MAX_CONTEXT) + "\n\n... (context truncated)\n";
        }

        const fullPrompt = `${systemPrompt}\n\nIMPORTANT: Return ONLY valid JSON with exactly these keys: {"subject": "...", "body": "...", "to": "..."}\nThe "to" field should be empty string unless you can infer a recipient.\nThe "body" should be plain text email content (no HTML). Use the SPECIFIC data below.\n\n--- CONTEXT DATA ---\n${contextData}`;

        try {
            let responseText = "";
            let stderrText = "";
            const tmpPromptPath = `/tmp/pai_email_prompt_${Date.now()}.txt`;
            await Bun.write(tmpPromptPath, fullPrompt);

            if (backend === "ollama") {
                const ollamaPath = Bun.which("ollama");
                if (!ollamaPath) return error("ollama not found in PATH");
                const proc = Bun.spawnSync(["sh", "-c", `cat "${tmpPromptPath}" | ${ollamaPath} run ${model}`], {
                    env: { ...process.env, NO_COLOR: "1", TERM: "dumb" }, timeout: 90_000,
                });
                responseText = stripAnsi(new TextDecoder().decode(proc.stdout));
                stderrText = stripAnsi(new TextDecoder().decode(proc.stderr));
            } else if (backend === "gemini") {
                const geminiPath = Bun.which("gemini");
                if (!geminiPath) return error("gemini CLI not found in PATH");
                const proc = Bun.spawnSync(["sh", "-c", `cat "${tmpPromptPath}" | ${geminiPath} -m gemini-2.5-flash --output-format text`], {
                    env: { ...process.env }, timeout: 90_000,
                });
                responseText = new TextDecoder().decode(proc.stdout).trim();
                stderrText = new TextDecoder().decode(proc.stderr).trim();
            } else if (backend === "claude") {
                const claudePath = Bun.which("claude");
                if (!claudePath) return error("claude CLI not found in PATH");
                const proc = Bun.spawnSync([claudePath, "-p", "--output-format", "text", fullPrompt.substring(0, 8000)], {
                    env: { ...process.env, NO_COLOR: "1" }, timeout: LLM_TIMEOUT,
                });
                responseText = new TextDecoder().decode(proc.stdout).trim();
                stderrText = new TextDecoder().decode(proc.stderr).trim();
            } else {
                return error(`Unknown backend: ${backend}`);
            }

            try { require("fs").unlinkSync(tmpPromptPath); } catch { }

            if (!responseText) {
                console.error("[email] LLM returned empty response. stderr:", stderrText.substring(0, 500));
                return error(`LLM returned empty response. Backend: ${backend}. ${stderrText ? "Error: " + stderrText.substring(0, 200) : "Check that the model is running."}`, 500);
            }

            console.log(`[email] LLM compose (${backend}/${template}): ${responseText.length} chars`);

            // Parse JSON from LLM response
            let parsed: any = null;
            try {
                const jsonMatch = responseText.match(/```(?:json)?\s*([\s\S]*?)```/) || responseText.match(/(\{[\s\S]*\})/);
                const jsonStr = jsonMatch ? jsonMatch[1].trim() : responseText;
                parsed = JSON.parse(jsonStr);
            } catch {
                parsed = { subject: `${template.replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase())} — ${new Date().toLocaleDateString()}`, body: responseText, to: "" };
            }

            return json({
                success: true,
                subject: parsed.subject || `${template.replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase())} — ${new Date().toLocaleDateString()}`,
                body: parsed.body || responseText,
                to: parsed.to || "",
                template,
                backend,
            });
        } catch (e: any) {
            console.error("[email] LLM compose error:", e instanceof Error ? e.message : String(e));
            return error(`LLM compose failed: ${e.message}`, 500);
        }
    }

    // ---- BIKE RIDE (Awaiting-reply threads + LLM summary + TTS) ----

    // 1. LLM helper (used by load and improve)
    async function runLlm(prompt: string, backend: string = LLM_BACKEND, model: string = LLM_MODEL): Promise<string> {
        const tmpPath = `/tmp/pai_bikeride_${Date.now()}_${Math.random().toString(36).slice(2)}.txt`;
        await Bun.write(tmpPath, prompt);
        let responseText = "";
        try {
            if (backend === "ollama") {
                const ollamaPath = Bun.which("ollama");
                if (ollamaPath) {
                    const proc = Bun.spawnSync(["sh", "-c", `cat "${tmpPath}" | ${ollamaPath} run ${model}`], {
                        env: { ...process.env, NO_COLOR: "1", TERM: "dumb" }, timeout: LLM_TIMEOUT,
                    });
                    responseText = stripAnsi(new TextDecoder().decode(proc.stdout));
                }
            } else if (backend === "gemini") {
                const geminiPath = Bun.which("gemini");
                if (geminiPath) {
                    const proc = Bun.spawnSync(["sh", "-c", `cat "${tmpPath}" | ${geminiPath} -m gemini-2.5-flash --output-format text`], {
                        env: { ...process.env }, timeout: LLM_TIMEOUT,
                    });
                    responseText = new TextDecoder().decode(proc.stdout).trim();
                }
            } else if (backend === "claude") {
                const claudePath = Bun.which("claude");
                if (claudePath) {
                    const proc = Bun.spawnSync([claudePath, "-p", "--output-format", "text", prompt.substring(0, 4000)], {
                        env: { ...process.env, NO_COLOR: "1" }, timeout: LLM_TIMEOUT,
                    });
                    responseText = new TextDecoder().decode(proc.stdout).trim();
                }
            }
        } catch { }
        try { require("fs").unlinkSync(tmpPath); } catch { }
        return responseText || "";
    }

    if (path === "/api/bikeride/load" && method === "POST") {
        const body = await parseBody(req);
        const backend = String(body.backend || LLM_BACKEND);
        const model = String(body.model || LLM_MODEL);
        try {
            // 1. Fetch Gmail threads
            const q = "in:inbox";
            const threadList = await gmailFetch(`/users/me/threads?maxResults=30&q=${encodeURIComponent(q)}`);
            const allThreads = threadList.threads || [];

            const getHeader = (msg: any, name: string): string => {
                const headers = msg?.payload?.headers || [];
                const h = headers.find((h: any) => h.name.toLowerCase() === name.toLowerCase());
                return h ? h.value : "";
            };

            const getBody = (msg: any): string => {
                if (msg.snippet) return msg.snippet;
                const payload = msg?.payload;
                if (!payload) return "";
                if (payload.body?.data) {
                    try { return atob(payload.body.data.replace(/-/g, "+").replace(/_/g, "/")); } catch { return ""; }
                }
                const parts = payload.parts || [];
                for (const p of parts) {
                    if (p.mimeType === "text/plain" && p.body?.data) {
                        try { return atob(p.body.data.replace(/-/g, "+").replace(/_/g, "/")); } catch { return ""; }
                    }
                }
                return msg.snippet || "";
            };

            // 2. Filter for awaiting-reply threads
            const awaitingReply: any[] = [];
            for (const thread of allThreads) {
                try {
                    const threadDetail = await gmailFetch(`/users/me/threads/${encodeURIComponent(thread.id)}?format=full`);
                    const msgs = threadDetail.messages || [];
                    if (msgs.length < 2) continue;

                    const parsedMsgs = msgs.map((m: any) => ({
                        from: getHeader(m, "From"),
                        subject: getHeader(m, "Subject"),
                        date: getHeader(m, "Date"),
                        snippet: m.snippet || "",
                        body: getBody(m),
                    }));

                    const fbSent = parsedMsgs.some((m: any) => m.from.toLowerCase().includes("fristonblanket"));
                    if (!fbSent) continue;
                    const otherReplied = parsedMsgs.some((m: any) => !m.from.toLowerCase().includes("fristonblanket"));
                    if (!otherReplied) continue;
                    const lastMsg = parsedMsgs[parsedMsgs.length - 1];
                    if (lastMsg.from.toLowerCase().includes("fristonblanket")) continue;

                    awaitingReply.push({
                        id: thread.id,
                        subject: parsedMsgs[0].subject || "(no subject)",
                        lastReplyFrom: lastMsg.from,
                        lastReplyDate: lastMsg.date,
                        messages: parsedMsgs,
                    });
                } catch { continue; }
            }

            // 3. Calendar availability for tomorrow (option C)
            let calendarSlots = "";
            try {
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                const dayStart = new Date(tomorrow.getFullYear(), tomorrow.getMonth(), tomorrow.getDate(), 8, 0);
                const dayEnd = new Date(tomorrow.getFullYear(), tomorrow.getMonth(), tomorrow.getDate(), 18, 0);
                const calData = await gcalFetch(`/calendars/primary/events?timeMin=${encodeURIComponent(dayStart.toISOString())}&timeMax=${encodeURIComponent(dayEnd.toISOString())}&singleEvents=true&orderBy=startTime&maxResults=50`);
                const busyEvents = (calData.items || []).filter((e: any) => e.start?.dateTime);
                const freeSlots: string[] = [];
                for (let hour = 8; hour < 18; hour++) {
                    for (const min of [0, 30]) {
                        const slotStart = new Date(dayStart);
                        slotStart.setHours(hour, min, 0, 0);
                        const slotEnd = new Date(slotStart);
                        slotEnd.setMinutes(slotEnd.getMinutes() + 30);
                        const isBusy = busyEvents.some((e: any) => {
                            const eStart = new Date(e.start.dateTime);
                            const eEnd = new Date(e.end?.dateTime || e.start.dateTime);
                            return slotStart < eEnd && slotEnd > eStart;
                        });
                        if (!isBusy) freeSlots.push(slotStart.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", hour12: true }));
                    }
                }
                const dayLabel = tomorrow.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" });
                if (freeSlots.length > 0) {
                    const picks = freeSlots.length <= 3 ? freeSlots : [freeSlots[0], freeSlots[Math.floor(freeSlots.length / 2)], freeSlots[freeSlots.length - 1]];
                    calendarSlots = `Available times on ${dayLabel}: ${picks.join(", ")}`;
                } else {
                    calendarSlots = `${dayLabel} appears fully booked — suggest the following day instead`;
                }
            } catch {
                calendarSlots = "tomorrow (I'll check my calendar and follow up with specific times)";
            }

            // 5. Generate summary + A/B/C draft responses for each thread
            for (const t of awaitingReply) {
                try {
                    const convoText = t.messages.map((m: any) =>
                        `From: ${m.from || "unknown"}\nDate: ${m.date || ""}\nSubject: ${m.subject || ""}\n\n${m.body || m.snippet || ""}`
                    ).join("\n---\n");
                    const convoTruncated = convoText.substring(0, 3000);

                    // Add raw text for improve endpoint
                    t.rawText = convoTruncated;

                    t.summary = await runLlm(
                        `Summarize this email thread in 2-3 concise sentences for an audio briefing. Focus on: who wrote, what they want, and what action is needed from you. Be direct and conversational.\n\n${convoTruncated}`,
                        backend, model
                    ) || "(summary unavailable)";

                    const draftA = await runLlm(`You are FristonBlanket replying to this email thread. Write a SHORT (2-3 sentence) friendly acknowledgment/thank-you response. Be warm but brief. Reply ONLY with the email body text, no subject line or headers.\n\n${convoTruncated}`, backend, model);
                    const draftB = await runLlm(`You are FristonBlanket replying to this email thread. Write a SHORT (3-5 sentence) substantive response that directly addresses the points raised. Be helpful and actionable. Reply ONLY with the email body text, no subject line or headers.\n\n${convoTruncated}`, backend, model);
                    const draftC = await runLlm(`You are FristonBlanket replying to this email thread. Write a SHORT (3-4 sentence) response that acknowledges the email and suggests scheduling a meeting to discuss further. Use these REAL available calendar slots: ${calendarSlots}. Propose specific times from those slots. Reply ONLY with the email body text, no subject line or headers.\n\n${convoTruncated}`, backend, model);

                    t.drafts = [
                        { label: "A", title: "Quick Reply", text: draftA || "Thanks for your email! I'll get back to you soon." },
                        { label: "B", title: "Substantive Reply", text: draftB || "Thank you for the detailed email. I've reviewed the points and will follow up shortly." },
                        { label: "C", title: "Schedule Meeting", text: draftC || `Thanks for reaching out. I'd love to discuss this further — would you be available for a quick call? ${calendarSlots}` },
                    ];
                    t.replyTo = t.messages[t.messages.length - 1].from;
                    t.threadSubject = t.messages[0].subject || "(no subject)";
                } catch {
                    t.summary = t.summary || "(summary unavailable)";
                    t.drafts = [
                        { label: "A", title: "Quick Reply", text: "Thanks for your email! I appreciate you reaching out." },
                        { label: "B", title: "Substantive Reply", text: "Thank you for the detailed email. I'll review and follow up shortly." },
                        { label: "C", title: "Schedule Meeting", text: `I'd love to discuss this further. Are you free ${calendarSlots}?` },
                    ];
                }
                delete t.messages;
            }

            console.log(`[bikeride] Found ${awaitingReply.length} awaiting-reply Gmail threads (of ${allThreads.length} total)`);
            return json({ success: true, threads: awaitingReply, calendarSlots });
        } catch (e: any) {
            console.error("[bikeride] load error:", e instanceof Error ? e.message : String(e));
            return error(e.message, e.message?.includes("Not authenticated") ? 401 : 500);
        }
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

    if (path === "/api/bikeride/improve" && method === "POST") {
        try {
            const body = await parseBody(req);
            const { draft, threadContext, backend, model } = body as any;
            if (!draft) return error("Missing: draft");

            const prompt = `You are editing a draft email reply. Retain ALL original information and meaning from the draft. Only improve: spelling, grammar, formatting, flow, and clarity. Use the email thread context below for reference to ensure facts are correct. Output ONLY the improved email body text without any preamble, subject line, or headers.

Draft:
${draft}

Thread context:
${threadContext || "(no context provided)"}`;

            const improved = await runLlm(prompt, backend || LLM_BACKEND, model || LLM_MODEL);
            return json({ success: true, improved: improved || draft });
        } catch (e: any) {
            return error(`Improve failed: ${e.message}`, 500);
        }
    }

    return null;
}
