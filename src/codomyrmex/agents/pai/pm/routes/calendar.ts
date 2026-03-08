/**
 * calendar.ts - Google Calendar route handlers
 *
 * Handles /api/calendar/* endpoints for OAuth, event CRUD, linking, and sync.
 */

import { json, error, parseBody, escapeHtmlServer } from "../helpers.ts";
import { PORT } from "../config.ts";
import {
    gcalSaveToken, gcalFetch, gcalLoadLinks, gcalSaveLinks,
    _calendarOauthState, setCalendarOauthState,
} from "../services/oauth.ts";
import { GCAL_TOKEN_PATH } from "../config.ts";
import { listProjects } from "../ListProjects.ts";

export async function handleCalendarRoutes(
    path: string,
    method: string,
    req: Request,
    url: URL,
): Promise<Response | null> {

    if (path === "/api/calendar/status" && method === "GET") {
        const fs = await import("fs");
        const hasToken = fs.existsSync(GCAL_TOKEN_PATH);
        const clientId = process.env.GOOGLE_CLIENT_ID || "";
        const hasCredentials = !!clientId && !!(process.env.GOOGLE_CLIENT_SECRET || "");
        return json({ authenticated: hasToken && hasCredentials, hasCredentials, hasToken });
    }

    if (path === "/api/calendar/auth" && method === "GET") {
        const clientId = process.env.GOOGLE_CLIENT_ID || "";
        if (!clientId) return error("GOOGLE_CLIENT_ID not set.", 400);
        const scope = "https://www.googleapis.com/auth/calendar";
        const redirect = `http://localhost:${PORT}/api/calendar/callback`;
        const state = crypto.randomUUID();
        setCalendarOauthState(state);
        const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${encodeURIComponent(clientId)}&redirect_uri=${encodeURIComponent(redirect)}&response_type=code&scope=${encodeURIComponent(scope)}&access_type=offline&prompt=consent&state=${encodeURIComponent(state)}`;
        return json({ auth_url: authUrl });
    }

    if (path === "/api/calendar/callback" && method === "GET") {
        const stateParam = url.searchParams.get("state");
        if (!stateParam || stateParam !== _calendarOauthState) return json({ success: false, error: "Invalid OAuth state" }, 400);
        setCalendarOauthState(null);
        const code = url.searchParams.get("code") || "";
        const errParam = url.searchParams.get("error") || "";
        if (errParam) return new Response(`<html><body><script>window.location='http://localhost:${PORT}/#calendar'<\/script><p>Auth error: ${escapeHtmlServer(errParam)}</p></body></html>`, { headers: { "Content-Type": "text/html" } });
        const clientId = process.env.GOOGLE_CLIENT_ID || "";
        const clientSecret = process.env.GOOGLE_CLIENT_SECRET || "";
        if (!code || !clientId || !clientSecret) return error("Missing OAuth parameters", 400);
        try {
            const tokenRes = await fetch("https://oauth2.googleapis.com/token", {
                method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: new URLSearchParams({ code, client_id: clientId, client_secret: clientSecret, redirect_uri: `http://localhost:${PORT}/api/calendar/callback`, grant_type: "authorization_code" }),
            });
            const tokenData: any = await tokenRes.json();
            if (tokenData.error) return new Response(`<html><body><p>OAuth error: ${tokenData.error_description || tokenData.error}</p></body></html>`, { headers: { "Content-Type": "text/html" } });
            await gcalSaveToken({ ...tokenData, saved_at: Date.now() });
            return new Response(`<html><head><meta http-equiv="refresh" content="0;url=http://localhost:${PORT}/#calendar"></head><body><p>Connected!</p></body></html>`, { headers: { "Content-Type": "text/html" } });
        } catch (e: any) { return error("OAuth failed: " + e.message, 500); }
    }

    if (path === "/api/calendar/disconnect" && method === "POST") {
        const fs = await import("fs");
        if (fs.existsSync(GCAL_TOKEN_PATH)) fs.unlinkSync(GCAL_TOKEN_PATH);
        return json({ success: true });
    }

    if (path === "/api/calendar/calendars" && method === "GET") {
        try { const data = await gcalFetch("/users/me/calendarList"); return json({ success: true, calendars: data.items || [] }); }
        catch (e: any) { return error(e.message, e.message.includes("Not authenticated") ? 401 : 500); }
    }

    if (path === "/api/calendar/events" && method === "GET") {
        try {
            const timeMin = url.searchParams.get("timeMin") || new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
            const timeMax = url.searchParams.get("timeMax") || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString();
            const calendarId = url.searchParams.get("calendarId") || "primary";
            const data = await gcalFetch(`/calendars/${encodeURIComponent(calendarId)}/events?timeMin=${encodeURIComponent(timeMin)}&timeMax=${encodeURIComponent(timeMax)}&singleEvents=true&orderBy=startTime&maxResults=250`);
            const links = gcalLoadLinks();
            const events = (data.items || []).map((e: any) => ({ ...e, _pai_link: links[e.id] || null }));
            return json({ success: true, events, calendarName: data.summary });
        } catch (e: any) {
            const isAuth = e.message?.includes("Not authenticated") || e.message?.includes("invalid_grant") || e.message?.includes("Invalid Credentials");
            return json({ success: false, error: e.message, needsReauth: isAuth, events: [] }, isAuth ? 401 : 500);
        }
    }

    if (path === "/api/calendar/events" && method === "POST") {
        try {
            const body = await parseBody(req);
            const data = await gcalFetch("/calendars/primary/events", { method: "POST", body: JSON.stringify(body.event) });
            if (body.linkTo && data.id) { const links = gcalLoadLinks(); links[data.id] = String(body.linkTo); gcalSaveLinks(links); }
            return json({ success: true, event: data });
        } catch (e: any) { return error(e.message, 500); }
    }

    if (path.match(/^\/api\/calendar\/events\/[^/]+$/) && method === "PUT") {
        const eventId = decodeURIComponent(path.split("/").pop() || "");
        try {
            const body = await parseBody(req);
            const data = await gcalFetch(`/calendars/primary/events/${encodeURIComponent(eventId)}`, { method: "PUT", body: JSON.stringify(body.event) });
            return json({ success: true, event: data });
        } catch (e: any) { return error(e.message, 500); }
    }

    if (path.match(/^\/api\/calendar\/events\/[^/]+$/) && method === "DELETE") {
        const eventId = decodeURIComponent(path.split("/").pop() || "");
        try {
            await gcalFetch(`/calendars/primary/events/${encodeURIComponent(eventId)}`, { method: "DELETE" });
            const links = gcalLoadLinks(); delete links[eventId]; gcalSaveLinks(links);
            return json({ success: true });
        } catch (e: any) { return error(e.message, 500); }
    }

    if (path === "/api/calendar/link" && method === "POST") {
        try {
            const body = await parseBody(req);
            const { eventId, projectId } = body as any;
            if (!eventId) return error("eventId required", 400);
            const links = gcalLoadLinks();
            if (!projectId) { delete links[eventId]; } else { links[eventId] = projectId; }
            gcalSaveLinks(links);
            return json({ success: true });
        } catch (e: any) { return error(e.message, 500); }
    }

    if (path === "/api/calendar/sync" && method === "POST") {
        try {
            const projects = listProjects({ status: undefined });
            const links = gcalLoadLinks();
            const linkedProjectIds = new Set(Object.values(links));
            const created: any[] = [];
            for (const project of (projects as any[])) {
                if (!project.target) continue;
                if (linkedProjectIds.has(project.id)) continue;
                const targetDate = new Date(project.target);
                const dateStr = targetDate.toISOString().split("T")[0];
                const event = {
                    summary: `[PAI] ${project.title}`,
                    description: `Goal: ${project.goal || ""}\n\nProject ID: ${project.id}\nStatus: ${project.status}`,
                    start: { date: dateStr }, end: { date: dateStr }, colorId: "5",
                };
                try {
                    const createdEvent = await gcalFetch("/calendars/primary/events", { method: "POST", body: JSON.stringify(event) });
                    links[createdEvent.id] = project.id;
                    created.push({ eventId: createdEvent.id, projectId: project.id, title: project.title });
                } catch { }
            }
            gcalSaveLinks(links);
            return json({ success: true, created: created.length, events: created });
        } catch (e: any) { return error(e.message, 500); }
    }

    return null;
}
