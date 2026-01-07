document.addEventListener('DOMContentLoaded', () => {
    // Determine active tab based on URL
    const updateActiveTab = () => {
        const path = window.location.pathname.split('/').pop() || 'index.html';
        document.querySelectorAll('.nav-link').forEach(link => {
            if (link.getAttribute('href') === path) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    };
    updateActiveTab();

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

    // Chat Logic
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        const messagesContainer = document.getElementById('chat-messages');
        const chatInput = document.getElementById('chat-input');

        // Load history? Not for this simple version.

        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (!message) return;

            // Add User Message
            appendMessage('user', message);
            chatInput.value = '';

            // Show Typing Indicator
            const typingId = appendMessage('assistant', 'Thinking...', true);

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        model: 'llama3', // Default to llama3, could be configurable
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
            }
        });
    }

    // Config Editor Logic
    const configFileLinks = document.querySelectorAll('.config-file-link');
    const configEditor = document.getElementById('config-editor');
    const currentConfigFileLabel = document.getElementById('current-config-file');
    const saveConfigBtn = document.getElementById('save-config-btn');
    let currentConfigFilename = null;

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
                    alert("Saved successfully!");
                } else {
                    alert("Error saving: " + data.error);
                }
            } catch (err) {
                alert("Network Error: " + err.message);
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
                // Use config API to fetch the document content
                const response = await fetch(`/api/config/${path}`);
                const data = await response.json();

                if (data.content !== undefined) {
                    // Render markdown with marked.js and sanitize with DOMPurify
                    if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
                        const rawHtml = marked.parse(data.content);
                        const cleanHtml = DOMPurify.sanitize(rawHtml);
                        docContentForBrowser.innerHTML = cleanHtml;

                        // Apply syntax highlighting to any code blocks
                        if (typeof hljs !== 'undefined') {
                            docContentForBrowser.querySelectorAll('pre code').forEach((block) => {
                                hljs.highlightElement(block);
                            });
                        }
                    } else {
                        // Fallback: display as preformatted text
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
});

function appendMessage(role, text, isTemp = false) {
    const container = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role} fade-in`;
    msgDiv.textContent = text;

    // Markdown parsing could go here (e.g., marked.js)

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
