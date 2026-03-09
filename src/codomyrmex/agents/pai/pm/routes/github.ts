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
        const result = linkProject(String(body.project || ""), String(body.repo || ""));
        if (result.success) broadcast("github", "link", result);
        return json(result);
    }

    if (path === "/api/github/unlink" && method === "POST") {
        const body = await parseBody(req);
        const result = unlinkProject(String(body.project || ""));
        if (result.success) broadcast("github", "unlink", result);
        return json(result);
    }

    if (path === "/api/github/push" && method === "POST") {
        const body = await parseBody(req);
        const result = body.all ? pushAll() : pushToGitHub(String(body.project || ""), !!body.dryRun);
        if (result.success) broadcast("github", "push", result);
        return json(result);
    }

    if (path === "/api/github/pull" && method === "POST") {
        const body = await parseBody(req);
        const result = body.all ? pullAll() : pullFromGitHub(String(body.project || ""), !!body.dryRun);
        if (result.success) broadcast("github", "pull", result);
        return json(result);
    }

    if (path === "/api/github/sync" && method === "POST") {
        const body = await parseBody(req);
        const result = body.all ? syncAll() : syncBidirectional(String(body.project || ""), !!body.dryRun);
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
        const result = createIssue(
            String(body.project || ""),
            String(body.title || ""),
            body.body ? String(body.body) : undefined,
            String(body.section || "remaining"),
            body.priority ? String(body.priority) : undefined,
        );
        return json(result);
    }

    if (path === "/api/github/issues/close" && method === "POST") {
        const body = await parseBody(req);
        const result = closeIssue(
            String(body.project || ""),
            Number(body.issueNumber || body.issue || 0),
            body.close !== false,
        );
        return json(result);
    }

    if (path === "/api/github/issues/edit" && method === "POST") {
        const body = await parseBody(req);
        const result = editIssue(
            String(body.project || ""),
            Number(body.issueNumber || body.issue || 0),
            {
                title: body.title ? String(body.title) : undefined,
                body: body.body ? String(body.body) : undefined,
                addLabels: body.addLabels,
                removeLabels: body.removeLabels,
                assignee: body.assignee ? String(body.assignee) : undefined,
                section: body.section ? String(body.section) : undefined,
            },
        );
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
        const result = createRepo(
            String(body.name || ""),
            body.isPrivate !== false,
            body.description ? String(body.description) : undefined,
            body.owner ? String(body.owner) : undefined,
        );
        return json(result);
    }

    if (path === "/api/github/cleanup-test-issues" && method === "POST") {
        const body = await parseBody(req);
        const result = cleanupTestIssues(String(body.repo || ""), !!body.dryRun);
        return json(result);
    }

    return null;
}
