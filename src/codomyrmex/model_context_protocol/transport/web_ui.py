"""
MCP Web UI

Self-contained HTML web interface for browsing and testing MCP tools.
Served at GET / when the HTTP transport is active.
"""


def get_web_ui_html() -> str:
    """Return the complete HTML for the MCP web UI."""
    return _WEB_UI_HTML


_WEB_UI_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Codomyrmex MCP Server</title>
<style>
  :root {
    --bg: #0f1117;
    --surface: #1a1d27;
    --border: #2a2d3a;
    --text: #e1e4ed;
    --text-dim: #8b8fa3;
    --accent: #6c8cff;
    --accent-hover: #8aa4ff;
    --success: #4ade80;
    --error: #f87171;
    --mono: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
  }
  header {
    border-bottom: 1px solid var(--border);
    padding: 1rem 2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  header h1 { font-size: 1.25rem; font-weight: 600; }
  header .badge {
    background: var(--accent);
    color: #fff;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
  }
  header .server-info {
    margin-left: auto;
    font-size: 0.8rem;
    color: var(--text-dim);
  }
  nav {
    display: flex;
    border-bottom: 1px solid var(--border);
    padding: 0 2rem;
    gap: 0;
  }
  nav button {
    background: none;
    border: none;
    color: var(--text-dim);
    padding: 0.75rem 1.25rem;
    cursor: pointer;
    font-size: 0.875rem;
    border-bottom: 2px solid transparent;
    transition: all 0.2s;
  }
  nav button:hover { color: var(--text); }
  nav button.active {
    color: var(--accent);
    border-bottom-color: var(--accent);
  }
  main { padding: 1.5rem 2rem; max-width: 1200px; }
  .tab-content { display: none; }
  .tab-content.active { display: block; }

  /* Tool list */
  .tool-grid { display: flex; flex-direction: column; gap: 0.5rem; }
  .tool-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    cursor: pointer;
    transition: border-color 0.2s;
  }
  .tool-card:hover { border-color: var(--accent); }
  .tool-card.selected { border-color: var(--accent); background: #1e2233; }
  .tool-card h3 {
    font-size: 0.9rem;
    font-family: var(--mono);
    color: var(--accent);
    margin-bottom: 0.25rem;
  }
  .tool-card p {
    font-size: 0.8rem;
    color: var(--text-dim);
    margin-bottom: 0.5rem;
  }
  .tool-card .meta {
    font-size: 0.7rem;
    color: var(--text-dim);
    font-family: var(--mono);
  }
  .tool-status {
    display: inline-block;
    padding: 0.1rem 0.4rem;
    border-radius: 3px;
    font-size: 0.65rem;
    font-weight: 500;
    text-transform: uppercase;
  }
  .tool-status.implemented { background: #1a3a2a; color: var(--success); }
  .tool-status.spec-only { background: #3a2a1a; color: #fbbf24; }

  /* Tool tester */
  .tester-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
    margin-top: 1rem;
  }
  .tester-panel h3 {
    font-family: var(--mono);
    font-size: 0.9rem;
    color: var(--accent);
    margin-bottom: 1rem;
  }
  .form-group { margin-bottom: 0.75rem; }
  .form-group label {
    display: block;
    font-size: 0.8rem;
    color: var(--text-dim);
    margin-bottom: 0.25rem;
    font-family: var(--mono);
  }
  .form-group input, .form-group textarea, .form-group select {
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    font-family: var(--mono);
    font-size: 0.85rem;
  }
  .form-group textarea { min-height: 80px; resize: vertical; }
  .form-group input:focus, .form-group textarea:focus {
    outline: none;
    border-color: var(--accent);
  }
  button.primary {
    background: var(--accent);
    color: #fff;
    border: none;
    padding: 0.5rem 1.25rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 500;
    transition: background 0.2s;
  }
  button.primary:hover { background: var(--accent-hover); }
  button.primary:disabled { opacity: 0.5; cursor: not-allowed; }
  .result-box {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1rem;
    margin-top: 1rem;
    font-family: var(--mono);
    font-size: 0.8rem;
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 400px;
    overflow-y: auto;
  }
  .result-box.success { border-color: var(--success); }
  .result-box.error { border-color: var(--error); }

  /* Resource / Prompt cards */
  .info-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
  }
  .info-card h3 { font-size: 0.9rem; color: var(--accent); margin-bottom: 0.25rem; }
  .info-card p { font-size: 0.8rem; color: var(--text-dim); }

  /* Server info panel */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }
  .stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
  }
  .stat-card .value { font-size: 2rem; font-weight: 700; color: var(--accent); }
  .stat-card .label { font-size: 0.8rem; color: var(--text-dim); }
  .loading { color: var(--text-dim); font-style: italic; }
  .search-box {
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    font-size: 0.85rem;
    margin-bottom: 1rem;
  }
  .search-box:focus { outline: none; border-color: var(--accent); }
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
  @media (max-width: 800px) { .two-col { grid-template-columns: 1fr; } }
</style>
</head>
<body>

<header>
  <h1>Codomyrmex MCP Server</h1>
  <span class="badge">MCP 2025-06-18</span>
  <span class="server-info" id="server-info">Connecting...</span>
</header>

<nav>
  <button class="active" onclick="showTab('tools')">Tools</button>
  <button onclick="showTab('resources')">Resources</button>
  <button onclick="showTab('prompts')">Prompts</button>
  <button onclick="showTab('server')">Server Info</button>
</nav>

<main>
  <!-- TOOLS TAB -->
  <div id="tab-tools" class="tab-content active">
    <input type="text" class="search-box" id="tool-search"
           placeholder="Search tools..." oninput="filterTools()">
    <div class="two-col">
      <div>
        <div class="tool-grid" id="tool-list">
          <p class="loading">Loading tools...</p>
        </div>
      </div>
      <div>
        <div class="tester-panel" id="tool-tester" style="display:none">
          <h3 id="tester-title">Select a tool</h3>
          <div id="tester-form"></div>
          <button class="primary" id="tester-run" onclick="runTool()" disabled>
            Execute Tool
          </button>
          <div class="result-box" id="tester-result" style="display:none"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- RESOURCES TAB -->
  <div id="tab-resources" class="tab-content">
    <div id="resource-list"><p class="loading">Loading resources...</p></div>
  </div>

  <!-- PROMPTS TAB -->
  <div id="tab-prompts" class="tab-content">
    <div id="prompt-list"><p class="loading">Loading prompts...</p></div>
  </div>

  <!-- SERVER INFO TAB -->
  <div id="tab-server" class="tab-content">
    <div class="stats-grid" id="stats-grid">
      <p class="loading">Loading server info...</p>
    </div>
  </div>
</main>

<script>
const state = {
  tools: [],
  resources: [],
  prompts: [],
  health: null,
  selectedTool: null,
};

// Tab switching
function showTab(name) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  event.target.classList.add('active');
}

// Fetch helpers
async function api(path, opts) {
  const res = await fetch(path, opts);
  return res.json();
}

// Load data
async function loadAll() {
  try {
    const [health, toolsData, resourcesData, promptsData] = await Promise.all([
      api('/health'),
      api('/tools'),
      api('/resources'),
      api('/prompts'),
    ]);
    state.health = health;
    state.tools = toolsData.tools || [];
    state.resources = resourcesData.resources || [];
    state.prompts = promptsData.prompts || [];

    document.getElementById('server-info').textContent =
      health.server_name + ' v' + health.server_version;

    renderTools();
    renderResources();
    renderPrompts();
    renderServerInfo();
  } catch (e) {
    document.getElementById('server-info').textContent = 'Connection error';
    console.error('Failed to load:', e);
  }
}

// Render tools
function renderTools() {
  const container = document.getElementById('tool-list');
  if (!state.tools.length) {
    container.innerHTML = '<p class="loading">No tools registered</p>';
    return;
  }
  container.innerHTML = state.tools.map((t, i) => {
    const params = Object.keys(t.inputSchema?.properties || {});
    const status = t._implementation_status || 'implemented';
    const statusClass = status === 'spec_only' ? 'spec-only' : 'implemented';
    return '<div class="tool-card" data-index="' + i + '" onclick="selectTool(' + i + ')">' +
      '<h3>' + esc(t.name) + '</h3>' +
      '<p>' + esc(t.description || 'No description') + '</p>' +
      '<span class="meta">' +
        (params.length ? params.join(', ') : 'no params') +
      '</span> ' +
      '<span class="tool-status ' + statusClass + '">' + status.replace('_', ' ') + '</span>' +
    '</div>';
  }).join('');
}

function filterTools() {
  const q = document.getElementById('tool-search').value.toLowerCase();
  document.querySelectorAll('.tool-card').forEach(card => {
    const text = card.textContent.toLowerCase();
    card.style.display = text.includes(q) ? '' : 'none';
  });
}

// Select a tool for testing
function selectTool(index) {
  const tool = state.tools[index];
  state.selectedTool = tool;

  document.querySelectorAll('.tool-card').forEach(c => c.classList.remove('selected'));
  document.querySelector('.tool-card[data-index="' + index + '"]').classList.add('selected');

  const panel = document.getElementById('tool-tester');
  panel.style.display = '';
  document.getElementById('tester-title').textContent = tool.name;
  document.getElementById('tester-run').disabled = false;
  document.getElementById('tester-result').style.display = 'none';

  const props = tool.inputSchema?.properties || {};
  const required = tool.inputSchema?.required || [];
  const formDiv = document.getElementById('tester-form');

  if (!Object.keys(props).length) {
    formDiv.innerHTML = '<p style="color:var(--text-dim);font-size:0.8rem;">No parameters required</p>';
    return;
  }

  formDiv.innerHTML = Object.entries(props).map(([name, schema]) => {
    const isReq = required.includes(name);
    const type = schema.type || 'string';
    const desc = schema.description || name;
    let input;
    if (type === 'boolean') {
      input = '<select id="param-' + name + '">' +
        '<option value="true">true</option>' +
        '<option value="false">false</option></select>';
    } else if (type === 'integer' || type === 'number') {
      input = '<input type="number" id="param-' + name + '" placeholder="' + esc(desc) + '"' +
        (schema.default !== undefined ? ' value="' + schema.default + '"' : '') + '>';
    } else {
      input = '<input type="text" id="param-' + name + '" placeholder="' + esc(desc) + '"' +
        (schema.default !== undefined ? ' value="' + esc(String(schema.default)) + '"' : '') + '>';
    }
    return '<div class="form-group">' +
      '<label>' + esc(name) + (isReq ? ' *' : '') + ' <span style="color:var(--text-dim)">(' + type + ')</span></label>' +
      input +
    '</div>';
  }).join('');
}

// Execute tool
async function runTool() {
  if (!state.selectedTool) return;
  const tool = state.selectedTool;
  const props = tool.inputSchema?.properties || {};
  const args = {};

  for (const [name, schema] of Object.entries(props)) {
    const el = document.getElementById('param-' + name);
    if (!el) continue;
    let val = el.value;
    if (!val && !tool.inputSchema?.required?.includes(name)) continue;
    if (schema.type === 'integer') val = parseInt(val, 10);
    else if (schema.type === 'number') val = parseFloat(val);
    else if (schema.type === 'boolean') val = val === 'true';
    args[name] = val;
  }

  const resultBox = document.getElementById('tester-result');
  resultBox.style.display = '';
  resultBox.className = 'result-box';
  resultBox.textContent = 'Executing...';

  try {
    const res = await api('/tools/' + encodeURIComponent(tool.name) + '/call', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(args),
    });
    resultBox.className = 'result-box ' + (res.isError ? 'error' : 'success');
    resultBox.textContent = JSON.stringify(res, null, 2);
  } catch (e) {
    resultBox.className = 'result-box error';
    resultBox.textContent = 'Error: ' + e.message;
  }
}

// Render resources
function renderResources() {
  const container = document.getElementById('resource-list');
  if (!state.resources.length) {
    container.innerHTML = '<p class="loading">No resources registered</p>';
    return;
  }
  container.innerHTML = state.resources.map(r =>
    '<div class="info-card">' +
      '<h3>' + esc(r.name) + '</h3>' +
      '<p>' + esc(r.description || '') + '</p>' +
      '<p style="font-family:var(--mono);font-size:0.75rem;margin-top:0.25rem">' +
        esc(r.uri) + ' &middot; ' + esc(r.mimeType || 'text/plain') +
      '</p>' +
    '</div>'
  ).join('');
}

// Render prompts
function renderPrompts() {
  const container = document.getElementById('prompt-list');
  if (!state.prompts.length) {
    container.innerHTML = '<p class="loading">No prompts registered</p>';
    return;
  }
  container.innerHTML = state.prompts.map(p => {
    const args = (p.arguments || []).map(a => a.name).join(', ');
    return '<div class="info-card">' +
      '<h3>' + esc(p.name) + '</h3>' +
      '<p>' + esc(p.description || '') + '</p>' +
      (args ? '<p style="font-family:var(--mono);font-size:0.75rem;margin-top:0.25rem">args: ' + esc(args) + '</p>' : '') +
    '</div>';
  }).join('');
}

// Render server info
function renderServerInfo() {
  const h = state.health || {};
  const grid = document.getElementById('stats-grid');
  grid.innerHTML = [
    { label: 'Server Name', value: h.server_name || '-' },
    { label: 'Version', value: h.server_version || '-' },
    { label: 'Protocol', value: h.protocol_version || '-' },
    { label: 'Tools', value: h.tool_count ?? '-' },
    { label: 'Resources', value: h.resource_count ?? '-' },
    { label: 'Prompts', value: h.prompt_count ?? '-' },
    { label: 'Transport', value: h.transport || '-' },
    { label: 'Status', value: h.status || '-' },
  ].map(s =>
    '<div class="stat-card">' +
      '<div class="value">' + esc(String(s.value)) + '</div>' +
      '<div class="label">' + esc(s.label) + '</div>' +
    '</div>'
  ).join('');
}

function esc(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

loadAll();
</script>
</body>
</html>
"""


__all__ = ["get_web_ui_html"]
