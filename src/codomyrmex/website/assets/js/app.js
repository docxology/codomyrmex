// Shared behaviour for every dashboard page (loaded by templates/base.html).
// Page-specific controls (chat form, test runner, health refresh, doc tree and
// doc links, config editor) are wired by their own template; binding them here
// as well made every action fire twice. Only bind elements no template owns.
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

                let data;
                try {
                    data = await response.json();
                } catch (_e) {
                    outputArea.textContent = `Server error: non-JSON response (HTTP ${response.status})`;
                    return;
                }

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
});
