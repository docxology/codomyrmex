'use strict';
// Browser harness for test_dashboard_single_binding.py.
//
// Drives the rendered dashboard pages in Chromium (via the Node `playwright`
// package), answers every request from disk or canned JSON so no real test
// run, LLM call or config write happens, performs each user action once and
// reports how many API requests each action produced, what the UI showed
// afterwards, and any console errors.
//
// Usage: node dashboard_request_counts.cjs <rendered-site-dir>
// Prints one JSON object on stdout.

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const SITE = path.resolve(process.argv[2]);
const ORIGIN = 'http://dashboard.test';
const TYPES = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css' };

// Serve the real markdown/sanitizer bundles when they are installed next to
// playwright or on the module path; otherwise the CDN script is empty and the
// docs page falls back to plain-text rendering.
const LIB_DIRS = [path.resolve(path.dirname(require.resolve('playwright')), '..'), ...require.resolve.paths('playwright')];
function optionalLib(spec) {
    const file = LIB_DIRS.map((dir) => path.join(dir, spec)).find((candidate) => fs.existsSync(candidate));
    return file ? fs.readFileSync(file, 'utf8') : '';
}
const CDN_SCRIPTS = {
    'marked.umd.js': optionalLib('marked/lib/marked.umd.js'),
    'purify.min.js': optionalLib('dompurify/dist/purify.min.js'),
};

const HEALTH = {
    uptime: '2h canned',
    status_text: 'Healthy',
    status_class: 'ok',
    modules: { total: 7, api_spec_pct: 11, test_coverage_pct: 22, mcp_spec_pct: 33 },
    git: { branch: 'canned-branch', commit_count: 42, status: 'clean', dirty_files: 0, last_commit: 'def canned' },
};
const TEST_RESULTS = { passed: 3, failed: 0, errors: 0, skipped: 1, total: 4, success: true, output: 'canned pytest output' };

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function api(method, pathname) {
    const p = decodeURIComponent(pathname);
    if (method === 'GET' && p === '/api/llm/config') return { body: { available_models: ['m1', 'm2'], default_model: 'm2' } };
    if (method === 'POST' && p === '/api/chat') return { delay: 300, body: { success: true, response: 'canned reply', model: 'm2' } };
    if (method === 'POST' && p === '/api/tests') return { status: 202, body: { status: 'running' } };
    if (method === 'GET' && p === '/api/tests/status') return { body: { status: 'done', results: TEST_RESULTS } };
    if (method === 'GET' && p === '/api/health') return { body: HEALTH };
    if (method === 'GET' && p === '/api/security/posture') {
        return { body: { status: 'ok', risk_score: 10, compliance_rate: 0.9, secret_findings_count: 0, total_checks: 5, markdown: '# r' } };
    }
    if (method === 'GET' && p.startsWith('/api/docs/')) return { body: { content: `# Doc\n\nDoc for ${p.slice('/api/docs/'.length)}` } };
    if (method === 'GET' && p.startsWith('/api/config/')) return { body: { content: `# config of ${p.slice('/api/config/'.length)}` } };
    if (method === 'POST' && p.startsWith('/api/config')) return { body: { success: true } };
    if (method === 'POST' && p === '/api/execute') return { body: { success: true, stdout: 'script ok', stderr: '' } };
    if (method === 'POST' && p === '/api/refresh') return { body: { success: true } };
    return { status: 404, body: { error: `no canned response for ${method} ${p}` } };
}

async function handle(route, requests, broken) {
    const request = route.request();
    const url = new URL(request.url());
    if (url.origin === ORIGIN && url.pathname.startsWith('/api/')) {
        requests.push({ method: request.method(), path: decodeURIComponent(url.pathname) });
        if (broken.some((prefix) => decodeURIComponent(url.pathname).startsWith(prefix))) {
            return route.fulfill({ status: 502, contentType: 'text/html', body: '<html>Bad gateway</html>' });
        }
        const canned = api(request.method(), url.pathname);
        if (canned.delay) await sleep(canned.delay);
        return route.fulfill({ status: canned.status || 200, contentType: 'application/json', body: JSON.stringify(canned.body) });
    }
    if (url.origin === ORIGIN) {
        const file = path.join(SITE, decodeURIComponent(url.pathname));
        if (!file.startsWith(SITE) || !fs.existsSync(file) || !fs.statSync(file).isFile()) return route.fulfill({ status: 404, body: '' });
        let body = fs.readFileSync(file);
        // CDN requests are answered locally (below), so the bytes cannot match
        // the pages' Subresource Integrity hashes and Chromium would refuse
        // them. SRI itself is covered by test_template_external_assets.py.
        if (path.extname(file) === '.html') body = body.toString('utf8').replace(/\sintegrity="[^"]*"/g, '');
        return route.fulfill({ status: 200, contentType: TYPES[path.extname(file)] || 'application/octet-stream', body });
    }
    if (url.host === 'localhost:8080') {
        return route.fulfill({
            status: 200,
            contentType: 'application/json',
            headers: { 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify({ status: 'ok', tool_count: 1, resource_count: 2, prompt_count: 3 }),
        });
    }
    if (url.host.startsWith('fonts.') || url.pathname.endsWith('.css')) return route.fulfill({ status: 200, contentType: 'text/css', body: '' });
    if (url.host === 'cdn.jsdelivr.net') {
        return route.fulfill({ status: 200, contentType: 'application/javascript', body: CDN_SCRIPTS[path.basename(url.pathname)] || '' });
    }
    return route.abort();
}

async function open(browser, file, { clock = false, broken = [] } = {}) {
    const context = await browser.newContext();
    const page = await context.newPage();
    page.setDefaultTimeout(10000);
    const requests = [];
    const errors = [];
    page.on('console', (msg) => {
        if (msg.type() === 'error') errors.push(msg.text());
    });
    page.on('pageerror', (err) => errors.push(String(err)));
    await page.routeWebSocket(/:8890\//, () => {});
    await page.route('**/*', (route) => handle(route, requests, broken));
    if (clock) await page.clock.install();
    await page.goto(`${ORIGIN}/${file}`);
    const count = (method, prefix, since = 0) =>
        requests.slice(since).filter((r) => r.method === method && r.path.startsWith(prefix)).length;
    return { context, page, requests, errors, count };
}

async function chat(browser) {
    const { context, page, requests, errors, count } = await open(browser, 'chat.html');
    await page.waitForSelector('#model-select option[value="m2"]', { state: 'attached' });
    await sleep(400);
    const out = { llmConfigOnLoad: count('GET', '/api/llm/config') };
    const mark = requests.length;
    await page.fill('#chat-input', 'hello');
    await page.click('#chat-submit-btn');
    out.whileSending = await page.evaluate(() => ({
        logBusy: document.getElementById('chat-messages').getAttribute('aria-busy'),
        buttonDisabled: document.getElementById('chat-submit-btn').disabled,
        inputDisabled: document.getElementById('chat-input').disabled,
    }));
    await page.waitForFunction(() => [...document.querySelectorAll('.message.assistant')].some((m) => m.textContent === 'canned reply'));
    await sleep(500);
    out.chatPosts = count('POST', '/api/chat', mark);
    out.chatBodies = requests.slice(mark).filter((r) => r.path === '/api/chat').length;
    out.after = await page.evaluate(() => ({
        userMessages: [...document.querySelectorAll('.message.user')].filter((m) => m.textContent === 'hello').length,
        replies: [...document.querySelectorAll('.message.assistant')].filter((m) => m.textContent === 'canned reply').length,
        selectedModel: document.getElementById('model-select').value,
        logBusy: document.getElementById('chat-messages').getAttribute('aria-busy'),
        buttonDisabled: document.getElementById('chat-submit-btn').disabled,
        replyClass: [...document.querySelectorAll('.message.assistant')].pop().className,
    }));
    out.errors = errors;
    await context.close();
    return out;
}

async function health(browser) {
    const { context, page, requests, errors, count } = await open(browser, 'health.html', { clock: true });
    await page.waitForFunction(() => document.getElementById('security-posture-content').textContent.includes('Checks Run'));
    await sleep(300);
    const out = { healthOnLoad: count('GET', '/api/health'), postureOnLoad: count('GET', '/api/security/posture') };
    let mark = requests.length;
    await page.click('#run-tests-btn');
    await page.waitForFunction(() => document.getElementById('test-results').textContent.includes('polling'));
    out.buttonDisabledWhileRunning = await page.$eval('#run-tests-btn', (b) => b.disabled);
    await page.clock.runFor(2000);
    await page.waitForFunction(() => document.getElementById('test-results').textContent.includes('PASS'));
    await sleep(500);
    out.testPosts = count('POST', '/api/tests', mark);
    out.statusPolls = requests.slice(mark).filter((r) => r.method === 'GET' && r.path === '/api/tests/status').length;
    out.afterTests = await page.evaluate(() => ({
        output: document.getElementById('test-output').textContent,
        outputHidden: document.getElementById('test-output').classList.contains('hidden'),
        buttonDisabled: document.getElementById('run-tests-btn').disabled,
    }));
    mark = requests.length;
    await page.clock.runFor(30000);
    await sleep(500);
    out.healthGetsPer30s = count('GET', '/api/health', mark);
    out.afterRefresh = await page.evaluate(() => {
        const text = (id) => document.getElementById(id).textContent.trim();
        return {
            uptime: text('uptime'),
            modules: text('module-count'),
            status: text('system-status'),
            branch: text('git-branch'),
            commits: text('git-commits'),
            lastCommit: text('git-last-commit'),
            apiPct: text('api-spec-pct'),
            apiBarNow: document.getElementById('api-spec-bar').getAttribute('aria-valuenow'),
            connection: text('connection-text'),
        };
    });
    out.errors = errors;
    await context.close();
    return out;
}

async function docs(browser) {
    const { context, page, requests, errors, count } = await open(browser, 'docs.html');
    await page.waitForFunction(() => document.getElementById('doc-content').textContent.includes('Doc for guides/intro.md'));
    await sleep(400);
    const out = { docGetsOnLoad: count('GET', '/api/docs/') };
    const mark = requests.length;
    await page.click('.doc-link[data-path="guides/a b#c.md"]');
    await page.waitForFunction(() => document.getElementById('doc-content').textContent.includes('Doc for guides/a b'));
    await sleep(500);
    out.docGetsPerClick = count('GET', '/api/docs/', mark);
    out.docPathsRequested = requests.slice(mark).map((r) => r.path);
    out.docShown = await page.$eval('#doc-content', (el) => el.textContent.trim());
    out.renderedMarkdown = await page.$eval('#doc-content', (el) => Boolean(el.querySelector('h1')));
    out.clickedLinkWeight = await page.$eval('.doc-link[data-path="guides/a b#c.md"]', (a) => getComputedStyle(a).fontWeight);
    const folderState = () =>
        page.$eval('.doc-tree .folder', (f) => ({ expanded: f.getAttribute('aria-expanded'), display: f.nextElementSibling.style.display }));
    out.folderInitial = await folderState();
    await page.click('.doc-tree .folder');
    out.folderAfterClick = await folderState();
    await page.focus('.doc-tree .folder');
    await page.keyboard.press('Enter');
    out.folderAfterEnter = await folderState();
    out.errors = errors;
    await context.close();
    return out;
}

async function config(browser) {
    const { context, page, requests, errors, count } = await open(browser, 'config.html');
    await page.waitForFunction(() => document.getElementById('config-editor').value === '# config of pyproject.toml');
    await sleep(500);
    const out = { configGetsOnLoad: count('GET', '/api/config/') };
    let mark = requests.length;
    await page.click('.config-file-link[data-filename="settings.yaml"]');
    await page.waitForFunction(() => document.getElementById('config-editor').value === '# config of settings.yaml');
    await sleep(500);
    out.configGetsPerClick = count('GET', '/api/config/', mark);
    out.afterLoad = await page.evaluate(() => ({
        label: document.getElementById('current-config-file').textContent,
        saveDisabled: document.getElementById('save-config-btn').disabled,
        editorDisabled: document.getElementById('config-editor').disabled,
    }));
    mark = requests.length;
    await page.fill('#config-editor', 'key = 1');
    await page.click('#save-config-btn');
    await page.waitForFunction(() => document.getElementById('save-status').textContent.includes('Saved'));
    await sleep(500);
    out.configPostsPerSave = count('POST', '/api/config', mark);
    out.savePathsRequested = requests.slice(mark).map((r) => `${r.method} ${r.path}`);
    out.afterSave = await page.evaluate(() => ({
        status: document.getElementById('save-status').textContent,
        saveDisabled: document.getElementById('save-config-btn').disabled,
        saveLabel: document.getElementById('save-config-btn').textContent.trim(),
    }));
    out.errors = errors;
    await context.close();
    return out;
}

async function scripts(browser) {
    const { context, page, requests, errors, count } = await open(browser, 'scripts.html');
    await sleep(200);
    const mark = requests.length;
    await page.fill('#script-args-1', '--flag');
    await page.click('form.script-form button');
    await page.waitForFunction(() => document.getElementById('output-1').textContent.includes('script ok'));
    await sleep(400);
    const out = {
        executePosts: count('POST', '/api/execute', mark),
        buttonLabel: (await page.$eval('form.script-form button', (b) => b.textContent)).trim(),
        errors,
    };
    await context.close();
    return out;
}

async function index(browser) {
    const { context, page, requests, errors, count } = await open(browser, 'index.html');
    await page.waitForFunction(() => document.getElementById('dash-last-updated').textContent.includes('Last updated'));
    await sleep(300);
    const out = {
        healthOnLoad: count('GET', '/api/health'),
        navCurrent: await page.$eval('.nav-link[href="index.html"]', (a) => [a.classList.contains('active'), a.getAttribute('aria-current')]),
        mcpBadge: await page.$eval('#mcp-badge', (b) => b.textContent.trim()),
    };
    const mark = requests.length;
    await Promise.all([page.waitForEvent('load'), page.click('#refresh-data-btn')]);
    out.refreshPosts = count('POST', '/api/refresh', mark);
    await Promise.all([page.waitForURL('**/health.html'), page.keyboard.press('Alt+2')]);
    out.altShortcutUrl = new URL(page.url()).pathname;
    out.errors = errors;
    await context.close();
    return out;
}

// Non-JSON (HTML 502) replies must surface as readable errors, not parser exceptions.
async function nonJson(browser) {
    const out = {};
    const text = (page, sel) => page.$eval(sel, (el) => el.textContent.trim());
    let s = await open(browser, 'chat.html', { broken: ['/api/chat'] });
    await s.page.fill('#chat-input', 'hello');
    await s.page.click('#chat-submit-btn');
    await s.page.waitForFunction(() => !document.getElementById('chat-submit-btn').disabled);
    out.chat = (await s.page.$$eval('.message.assistant', (ms) => ms.map((m) => m.textContent))).pop();
    out.chatLogBusy = await s.page.$eval('#chat-messages', (el) => el.getAttribute('aria-busy'));
    await s.context.close();

    s = await open(browser, 'health.html', { clock: true, broken: ['/api/tests', '/api/health'] });
    await s.page.click('#run-tests-btn');
    await s.page.waitForFunction(() => !document.getElementById('run-tests-btn').disabled);
    out.tests = await text(s.page, '#test-results');
    await s.page.clock.runFor(5000);
    await sleep(300);
    out.connectionAfterOneFailure = await text(s.page, '#connection-text');
    await s.page.clock.runFor(5000);
    await sleep(300);
    out.connectionAfterTwoFailures = await text(s.page, '#connection-text');
    await s.context.close();

    s = await open(browser, 'docs.html', { broken: ['/api/docs/'] });
    await s.page.waitForFunction(() => document.getElementById('doc-content').textContent.includes('Error'));
    out.docs = await text(s.page, '#doc-content');
    await s.context.close();

    s = await open(browser, 'config.html', { broken: ['/api/config'] });
    await s.page.waitForFunction(() => document.getElementById('save-status').textContent.includes('Error'));
    out.config = await text(s.page, '#save-status');
    out.configSaveDisabled = await s.page.$eval('#save-config-btn', (b) => b.disabled);
    await s.context.close();
    return out;
}

(async () => {
    const browser = await chromium.launch();
    try {
        const result = {};
        for (const [name, scenario] of Object.entries({ chat, health, docs, config, scripts, index, nonJson })) {
            // A scenario that cannot complete (e.g. the UI never updates) is
            // reported on its own so the other scenarios still produce counts.
            try {
                result[name] = await scenario(browser);
            } catch (err) {
                result[name] = { harnessError: String(err && err.message ? err.message : err) };
            }
        }
        process.stdout.write(JSON.stringify(result, null, 2));
    } finally {
        await browser.close();
    }
})().catch((err) => {
    process.stderr.write(String(err && err.stack ? err.stack : err));
    process.exit(1);
});
