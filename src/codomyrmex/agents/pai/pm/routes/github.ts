/**
 * github.ts - GitHub Sync route handlers
 *
 * Handles /api/github/* endpoints wrapping GitHubSync.ts operations.
 */

import {
    listRepos, getSyncStatus, linkProject, unlinkProject,
    pushToGitHub, pullFromGitHub, syncBidirectional,
    pushAll, pullAll, syncAll, loadSyncMapping,
    createIssue, closeIssue, getTaskMapping, diffSync,
    cleanupTestIssues, editIssue, createRepo,
} from "../GitHubSync.ts";
import { json, error, parseBody, broadcast } from "../helpers.ts";

export async function handleGitHubRoutes(
    path: string,
    method: string,
    req: Request,
    url: URL,
): Promise<Response | null> {

    if (path === "/api/github/repos" && method === "GET") {
        const owner = url.searchParams.get("owner") || process.env.GITHUB_DEFAULT_OWNER || "";
        const result = listRepos(owner);
        return json(result);
    }

    if (path === "/api/github/status" && method === "GET") {
        const result = getSyncStatus();
        return json(result);
    }

    if (path === "/api/github/link" && method === "POST") {
        const body = await parseBody(req);
        const result = linkProject(body as any);
        if (result.success) broadcast("github", "link", result);
        return json(result);
    }

    if (path === "/api/github/unlink" && method === "POST") {
        const body = await parseBody(req);
        const result = unlinkProject(body as any);
        if (result.success) broadcast("github", "unlink", result);
        return json(result);
    }

    if (path === "/api/github/push" && method === "POST") {
        const body = await parseBody(req);
        const result = body.all ? pushAll() : pushToGitHub(body as any);
        if (result.success) broadcast("github", "push", result);
        return json(result);
    }

    if (path === "/api/github/pull" && method === "POST") {
        const body = await parseBody(req);
        const result = body.all ? pullAll() : pullFromGitHub(body as any);
        if (result.success) broadcast("github", "pull", result);
        return json(result);
    }

    if (path === "/api/github/sync" && method === "POST") {
        const body = await parseBody(req);
        const result = body.all ? syncAll() : syncBidirectional(body as any);
        if (result.success) broadcast("github", "sync", result);
        return json(result);
    }

    if (path === "/api/github/diff" && method === "GET") {
        const project = url.searchParams.get("project") || "";
        const result = diffSync(project);
        return json(result);
    }

    if (path === "/api/github/issues" && method === "POST") {
        const body = await parseBody(req);
        const result = createIssue(body as any);
        return json(result);
    }

    if (path === "/api/github/issues/close" && method === "POST") {
        const body = await parseBody(req);
        const result = closeIssue(body as any);
        return json(result);
    }

    if (path === "/api/github/issues/edit" && method === "POST") {
        const body = await parseBody(req);
        const result = editIssue(body as any);
        return json(result);
    }

    if (path === "/api/github/mapping" && method === "GET") {
        const project = url.searchParams.get("project") || "";
        const result = getTaskMapping(project);
        return json(result);
    }

    if (path === "/api/github/sync-mapping" && method === "GET") {
        const project = url.searchParams.get("project") || "";
        const result = loadSyncMapping(project);
        return json(result || {});
    }

    if (path === "/api/github/repo" && method === "POST") {
        const body = await parseBody(req);
        const result = createRepo(body as any);
        return json(result);
    }

    if (path === "/api/github/cleanup-test-issues" && method === "POST") {
        const body = await parseBody(req);
        const result = cleanupTestIssues(body as any);
        return json(result);
    }

    return null;
}
