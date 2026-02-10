document.addEventListener('DOMContentLoaded', () => {
    // Determine active tab based on URL — with aria-current support
    const updateActiveTab = () => {
        const path = window.location.pathname.split('/').pop() || 'index.html';
        document.querySelectorAll('.nav-link').forEach(link => {
            if (link.getAttribute('href') === path) {
                link.classList.add('active');
                link.setAttribute('aria-current', 'page');
            } else {
                link.classList.remove('active');
                link.removeAttribute('aria-current');
            }
        });
    };
    updateActiveTab();

    // Keyboard shortcuts: Alt+1 through Alt+9 for nav tabs
    document.addEventListener('keydown', (e) => {
        if (e.altKey && ((e.key >= '1' && e.key <= '9') || e.key === '0')) {
            const link = document.querySelector(`.nav-link[data-shortcut="${e.key}"]`);
            if (link) {
                e.preventDefault();
                window.location.href = link.getAttribute('href');
            }
        }
    });

    // Script Execution Logic
    const scriptForms = document.querySelectorAll('.script-form');
    scriptForms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = form.querySelector('button');
            const outputArea = document.getElementById(`output-${form.dataset.scriptId}`);
            const scriptName = form.dataset.scriptName;

            // Collect args if any (simple implementation: one input for all args)
            const argsInput = form.querySelector('input[name="args"]');
            const args = argsInput && argsInput.value ? argsInput.value.split(' ') : [];

            btn.disabled = true;
            btn.innerHTML = '<span class="loader"></span> Running...';
            outputArea.textContent = 'Executing...';
            outputArea.classList.remove('hidden');

            try {
                const response = await fetch('/api/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ script: scriptName, args: args })
                });

                const data = await response.json();

                if (data.success) {
                    outputArea.textContent = data.stdout + (data.stderr ? `\nSTDERR:\n${data.stderr}` : '');
                } else {
                    outputArea.textContent = `Error (${data.returncode}):\n${data.stderr}\n${data.stdout}`;
                }
            } catch (err) {
                outputArea.textContent = `Network Error: ${err.message}`;
            } finally {
                btn.disabled = false;
                btn.textContent = 'Run Script';
            }
        });
    });

    // Chat Logic — with aria-busy management
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        const messagesContainer = document.getElementById('chat-messages');
        const chatInput = document.getElementById('chat-input');

        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (!message) return;

            // Add User Message
            appendMessage('user', message);
            chatInput.value = '';

            // Show Typing Indicator + aria-busy
            if (messagesContainer) messagesContainer.setAttribute('aria-busy', 'true');
            const typingId = appendMessage('assistant', 'Thinking...', true);

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        model: 'llama3',
                        messages: [{ role: 'user', content: message }],
                        stream: false
                    })
                });

                const data = await response.json();

                // Remove Typing Indicator
                document.getElementById(typingId).remove();

                if (data.success && data.response) {
                    appendMessage('assistant', data.response);
                } else if (data.error) {
                    appendMessage('system', `Error: ${data.error}`);
                } else {
                    appendMessage('system', 'Unknown error occurred.');
                }

            } catch (err) {
                document.getElementById(typingId).remove();
                appendMessage('system', `Network Error: ${err.message}`);
            } finally {
                if (messagesContainer) messagesContainer.removeAttribute('aria-busy');
            }
        });
    }

    // Config Editor Logic — with inline toast instead of alert()
    const configFileLinks = document.querySelectorAll('.config-file-link');
    const configEditor = document.getElementById('config-editor');
    const currentConfigFileLabel = document.getElementById('current-config-file');
    const saveConfigBtn = document.getElementById('save-config-btn');
    const saveStatus = document.getElementById('save-status');
    let currentConfigFilename = null;

    function showSaveStatus(message, isError) {
        if (!saveStatus) return;
        saveStatus.textContent = message;
        saveStatus.className = 'save-status ' + (isError ? 'error' : 'success');
        setTimeout(() => { saveStatus.textContent = ''; saveStatus.className = 'save-status'; }, 3000);
    }

    configFileLinks.forEach(link => {
        link.addEventListener('click', async (e) => {
            e.preventDefault();
            // Reset active state
            configFileLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            const filename = link.dataset.filename;
            currentConfigFilename = filename;
            currentConfigFileLabel.textContent = filename;
            configEditor.value = "Loading...";
            saveConfigBtn.disabled = true;

            try {
                const response = await fetch(`/api/config/${filename}`);
                const data = await response.json();

                if (data.content !== undefined) {
                    configEditor.value = data.content;
                    saveConfigBtn.disabled = false;
                } else {
                    configEditor.value = "Error loading content: " + (data.error || "Unknown error");
                }
            } catch (err) {
                configEditor.value = "Network Error: " + err.message;
            }
        });
    });

    if (saveConfigBtn) {
        saveConfigBtn.addEventListener('click', async () => {
            if (!currentConfigFilename) return;

            saveConfigBtn.innerHTML = '<span class="loader"></span> Saving...';
            saveConfigBtn.disabled = true;

            try {
                const response = await fetch(`/api/config/${currentConfigFilename}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content: configEditor.value })
                });
                const data = await response.json();

                if (data.success) {
                    showSaveStatus('Saved successfully!', false);
                } else {
                    showSaveStatus('Error saving: ' + data.error, true);
                }
            } catch (err) {
                showSaveStatus('Network Error: ' + err.message, true);
            } finally {
                saveConfigBtn.innerHTML = 'Save Changes';
                saveConfigBtn.disabled = false;
            }
        });
    }

    // Documentation Browser Logic
    // Configure marked.js if available
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            highlight: function (code, lang) {
                if (typeof hljs !== 'undefined' && lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(code, { language: lang }).value;
                    } catch (e) { }
                }
                return code;
            },
            breaks: true,
            gfm: true
        });
    }

    document.querySelectorAll('.doc-link').forEach(link => {
        link.addEventListener('click', async (e) => {
            e.preventDefault();
            document.querySelectorAll('.doc-link').forEach(l => l.style.fontWeight = 'normal');
            link.style.fontWeight = 'bold';

            const path = link.dataset.path;
            const docContentForBrowser = document.getElementById('doc-content');
            docContentForBrowser.innerHTML = '<h3>Loading...</h3>';

            try {
                const response = await fetch(`/api/docs/${path}`);
                const data = await response.json();

                if (data.content !== undefined) {
                    if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
                        const rawHtml = marked.parse(data.content);
                        const cleanHtml = DOMPurify.sanitize(rawHtml);
                        docContentForBrowser.innerHTML = cleanHtml;

                        if (typeof hljs !== 'undefined') {
                            docContentForBrowser.querySelectorAll('pre code').forEach((block) => {
                                hljs.highlightElement(block);
                            });
                        }
                    } else {
                        docContentForBrowser.innerHTML = `<pre style="white-space: pre-wrap; font-family: inherit;">${data.content.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>`;
                    }
                } else {
                    docContentForBrowser.innerHTML = `<p style="color: var(--error-color)">Error loading document: ${data.error}</p>`;
                }
            } catch (err) {
                docContentForBrowser.innerHTML = `<p style="color: var(--error-color)">Network Error: ${err.message}</p>`;
            }
        });
    });

    // ===== Health Page Logic =====
    if (document.querySelector('.health-grid')) {
        let healthFailCount = 0;
        let healthIsRunning = false;

        // Test Runner (Fix #4: XSS-safe, Fix #13: double-click protection)
        const runTestsBtn = document.getElementById('run-tests-btn');
        if (runTestsBtn) {
            runTestsBtn.addEventListener('click', async () => {
                if (runTestsBtn.disabled || healthIsRunning) return;
                healthIsRunning = true;

                const moduleSelect = document.getElementById('test-module');
                const resultsDiv = document.getElementById('test-results');
                const outputDiv = document.getElementById('test-output');

                runTestsBtn.disabled = true;
                runTestsBtn.innerHTML = '<span class="loader"></span> Running...';
                resultsDiv.innerHTML = '<p style="color: var(--accent-color);">Running tests...</p>';
                outputDiv.classList.add('hidden');

                try {
                    const body = moduleSelect.value ? { module: moduleSelect.value } : {};
                    const response = await fetch('/api/tests', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(body)
                    });
                    const data = await response.json();

                    if (data.error) {
                        // Fix #4: use textContent instead of innerHTML for error
                        resultsDiv.textContent = '';
                        const errP = document.createElement('p');
                        errP.className = 'status-err';
                        errP.textContent = data.error;
                        resultsDiv.appendChild(errP);
                    } else {
                        // Safe: only numeric values from API are interpolated
                        const statusClass = data.success ? 'status-ok' : 'status-err';
                        const summary = document.createElement('div');
                        summary.className = 'test-summary';

                        const stats = [
                            { value: data.passed, label: 'Passed', cls: 'status-ok' },
                            { value: data.failed, label: 'Failed', cls: 'status-err' },
                            { value: data.skipped, label: 'Skipped', cls: '' },
                            { value: data.total, label: 'Total', cls: '' },
                            { value: data.success ? 'PASS' : 'FAIL', label: 'Result', cls: statusClass },
                        ];

                        stats.forEach(s => {
                            const stat = document.createElement('div');
                            stat.className = 'test-stat';
                            const val = document.createElement('span');
                            val.className = 'test-stat-value' + (s.cls ? ' ' + s.cls : '');
                            val.textContent = String(s.value);
                            const lbl = document.createElement('span');
                            lbl.className = 'test-stat-label';
                            lbl.textContent = s.label;
                            stat.appendChild(val);
                            stat.appendChild(lbl);
                            summary.appendChild(stat);
                        });

                        resultsDiv.textContent = '';
                        resultsDiv.appendChild(summary);

                        if (data.output) {
                            outputDiv.textContent = data.output;
                            outputDiv.classList.remove('hidden');
                        }
                    }
                } catch (err) {
                    // Fix #4: use textContent for network error
                    resultsDiv.textContent = '';
                    const errP = document.createElement('p');
                    errP.className = 'status-err';
                    errP.textContent = 'Network error: ' + err.message;
                    resultsDiv.appendChild(errP);
                } finally {
                    runTestsBtn.disabled = false;
                    runTestsBtn.textContent = 'Run Tests';
                    healthIsRunning = false;
                }
            });
        }

        // Auto-refresh ALL health data (Fix #2: connection indicator, Fix #11: full refresh)
        const uptimeEl = document.getElementById('uptime');
        if (uptimeEl) {
            setInterval(async () => {
                try {
                    const resp = await fetch('/api/health');
                    const data = await resp.json();
                    healthFailCount = 0;

                    // Update connection status
                    const statusEl = document.getElementById('connection-status');
                    const textEl = document.getElementById('connection-text');
                    if (statusEl) {
                        statusEl.className = 'connection-status connection-ok';
                        textEl.textContent = 'Connected';
                    }

                    // Update all metrics
                    uptimeEl.textContent = data.uptime;

                    const moduleCountEl = document.getElementById('module-count');
                    if (moduleCountEl) moduleCountEl.textContent = data.modules.total;

                    const systemStatusEl = document.getElementById('system-status');
                    if (systemStatusEl) {
                        systemStatusEl.textContent = data.status_text;
                        systemStatusEl.className = 'metric-value status-' + data.status_class;
                    }

                    // Git
                    const branchEl = document.getElementById('git-branch');
                    if (branchEl && data.git) branchEl.textContent = data.git.branch;
                    const commitsEl = document.getElementById('git-commits');
                    if (commitsEl && data.git) commitsEl.textContent = data.git.commit_count;
                    const gitStatusEl = document.getElementById('git-status');
                    if (gitStatusEl && data.git) {
                        gitStatusEl.textContent = data.git.status;
                        gitStatusEl.className = 'metric-value ' + (data.git.dirty_files === 0 ? 'status-ok' : 'status-warn');
                    }
                    const lastCommitEl = document.getElementById('git-last-commit');
                    if (lastCommitEl && data.git) lastCommitEl.textContent = data.git.last_commit;

                    // Coverage bars
                    const updateBar = (barId, pctId, value) => {
                        const bar = document.getElementById(barId);
                        const pct = document.getElementById(pctId);
                        if (bar) {
                            const fill = bar.querySelector('.coverage-fill');
                            if (fill) fill.style.width = value + '%';
                            bar.setAttribute('aria-valuenow', value);
                        }
                        if (pct) pct.textContent = value + '%';
                    };
                    if (data.modules) {
                        updateBar('api-spec-bar', 'api-spec-pct', data.modules.api_spec_pct);
                        updateBar('test-coverage-bar', 'test-coverage-pct', data.modules.test_coverage_pct);
                        updateBar('mcp-spec-bar', 'mcp-spec-pct', data.modules.mcp_spec_pct);
                    }

                } catch (e) {
                    healthFailCount++;
                    const statusEl = document.getElementById('connection-status');
                    const textEl = document.getElementById('connection-text');
                    if (statusEl && healthFailCount >= 2) {
                        statusEl.className = 'connection-status connection-err';
                        textEl.textContent = 'Connection lost';
                    }
                }
            }, 30000);
        }
    }

    // Refresh Data button (dashboard)
    const refreshBtn = document.getElementById('refresh-data-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async () => {
            refreshBtn.disabled = true;
            refreshBtn.textContent = 'Refreshing...';
            try {
                const resp = await fetch('/api/refresh', { method: 'POST' });
                if (resp.ok) {
                    window.location.reload();
                } else {
                    refreshBtn.textContent = 'Refresh failed';
                    setTimeout(() => { refreshBtn.textContent = 'Refresh Data'; refreshBtn.disabled = false; }, 2000);
                }
            } catch (err) {
                refreshBtn.textContent = 'Network error';
                setTimeout(() => { refreshBtn.textContent = 'Refresh Data'; refreshBtn.disabled = false; }, 2000);
            }
        });
    }

    // Doc tree keyboard navigation — Enter/Space toggles folders
    document.querySelectorAll('.doc-tree .folder').forEach(folder => {
        folder.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const siblingUl = folder.nextElementSibling;
                if (siblingUl && siblingUl.tagName === 'UL') {
                    const isExpanded = folder.getAttribute('aria-expanded') === 'true';
                    folder.setAttribute('aria-expanded', String(!isExpanded));
                    siblingUl.style.display = isExpanded ? 'none' : '';
                }
            }
        });
        // Also handle click toggle
        folder.addEventListener('click', () => {
            const siblingUl = folder.nextElementSibling;
            if (siblingUl && siblingUl.tagName === 'UL') {
                const isExpanded = folder.getAttribute('aria-expanded') === 'true';
                folder.setAttribute('aria-expanded', String(!isExpanded));
                siblingUl.style.display = isExpanded ? 'none' : '';
            }
        });
    });
});

function appendMessage(role, text, isTemp = false) {
    const container = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role} fade-in`;
    msgDiv.textContent = text;

    if (isTemp) {
        const id = 'temp-' + Date.now();
        msgDiv.id = id;
        container.appendChild(msgDiv);
        container.scrollTop = container.scrollHeight;
        return id;
    }

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}
