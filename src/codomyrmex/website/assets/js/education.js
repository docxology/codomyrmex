/**
 * Education module frontend JavaScript
 * Handles: theme toggle, curriculum CRUD, quiz interaction, exam submission,
 * learning path rendering, content browser, and error notifications.
 */

/* ── Theme Toggle ──────────────────────────────────────────────── */

function initTheme() {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
    updateThemeIcon();
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    if (next === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    } else {
        document.documentElement.removeAttribute('data-theme');
    }
    localStorage.setItem('theme', next);
    updateThemeIcon();
}

function updateThemeIcon() {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    btn.querySelector('span').textContent = isDark ? '☀️' : '🌙';
}

// Apply theme immediately (before DOMContentLoaded) to prevent flash
initTheme();

/* ── Notification Banner ───────────────────────────────────────── */

function showNotification(message, type = 'error') {
    const existing = document.querySelector('.notification-banner');
    if (existing) existing.remove();

    const banner = document.createElement('div');
    banner.className = `notification-banner ${type}`;
    banner.setAttribute('role', 'alert');
    banner.textContent = message;
    document.body.appendChild(banner);

    setTimeout(() => banner.remove(), 5000);
}

/* ── API Fetch Wrapper ─────────────────────────────────────────── */

async function apiFetch(url, options = {}) {
    try {
        const resp = await fetch(url, options);
        const json = await resp.json();
        if (!resp.ok || json.status === 'error') {
            showNotification(json.message || `Request failed (${resp.status})`);
            return null;
        }
        // Unwrap {status: "ok", data: <payload>} envelope
        return json.data !== undefined ? json.data : json;
    } catch (err) {
        showNotification('Network error: ' + err.message);
        return null;
    }
}


/* ── Curriculum CRUD ───────────────────────────────────────────── */

async function createCurriculum(e) {
    e.preventDefault();
    const form = e.target;
    const name = form.querySelector('[name="name"]').value.trim();
    const level = form.querySelector('[name="level"]').value;
    if (!name) return;

    const data = await apiFetch('/api/education/curricula', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, level })
    });
    if (data) {
        showNotification('Curriculum created', 'success');
        loadCurriculaList();
        form.reset();
    }
}

async function loadCurriculaList() {
    const list = document.getElementById('curricula-list');
    if (!list) return;

    const data = await apiFetch('/api/education/curricula');
    if (!data) return;

    if (data.length === 0) {
        list.innerHTML = '<p class="empty-state">No curricula yet. Create one above.</p>';
        return;
    }

    list.innerHTML = data.map(c => `
        <div class="card" onclick="loadCurriculum('${c.name.replace(/'/g, "\\'")}')">
            <div class="card-title">
                ${escapeHtml(c.name)}
                <span class="status-badge">${escapeHtml(c.level)}</span>
            </div>
            <p>${c.module_count} modules · ${c.total_duration_minutes} min</p>
        </div>
    `).join('');
}

async function loadCurriculum(name) {
    const detail = document.getElementById('curriculum-detail');
    if (!detail) return;

    const data = await apiFetch(`/api/education/curricula/${encodeURIComponent(name)}`);
    if (!data) return;

    let html = `<h2>${escapeHtml(data.name)} <span class="status-badge">${escapeHtml(data.level)}</span></h2>`;
    html += `<p>${data.modules.length} modules · ${data.total_duration_minutes} min total</p>`;

    // Export buttons
    html += `<div style="margin: 1rem 0; display: flex; gap: 0.5rem;">`;
    html += `<button class="btn btn-secondary" onclick="exportCurriculum('${data.name.replace(/'/g, "\\'")}', 'json')">Export JSON</button>`;
    html += `<button class="btn btn-secondary" onclick="exportCurriculum('${data.name.replace(/'/g, "\\'")}', 'text')">Export Text</button>`;
    html += `</div>`;

    // Module list
    if (data.modules.length > 0) {
        html += '<h3>Modules</h3>';
        data.modules.forEach(m => {
            html += `<div class="card" style="margin-bottom: 0.75rem;">`;
            html += `<div class="card-title">${escapeHtml(m.title)} <span class="status-badge">${m.duration_minutes} min</span></div>`;
            html += `<p>${escapeHtml(m.objectives.join(', '))}</p>`;
            if (m.prerequisites.length > 0) {
                html += `<p style="font-size: 0.85rem; color: var(--text-secondary);">Prerequisites: ${m.prerequisites.map(escapeHtml).join(', ')}</p>`;
            }
            html += `<button class="btn btn-secondary" style="margin-top: 0.5rem;" onclick="showEditModule('${data.name.replace(/'/g, "\\'")}', '${m.title.replace(/'/g, "\\'")}')">Edit</button>`;
            html += `</div>`;
        });
    }

    // Add module form
    html += `
        <h3>Add Module</h3>
        <form id="add-module-form" onsubmit="addModule(event, '${data.name.replace(/'/g, "\\'")}')">
            <div style="display: grid; gap: 0.75rem; max-width: 500px;">
                <input name="title" placeholder="Module title" required>
                <textarea name="content" placeholder="Module content" rows="3" required></textarea>
                <input name="objectives" placeholder="Objectives (comma-separated)">
                <input name="duration_minutes" type="number" placeholder="Duration (minutes)" value="30" min="1">
                <input name="prerequisites" placeholder="Prerequisites (comma-separated)">
                <button type="submit" class="btn btn-primary">Add Module</button>
            </div>
        </form>`;

    // Learning path
    html += `
        <h3 style="margin-top: 1.5rem;">Learning Path</h3>
        <div style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.75rem;">
            <label for="level-select">Level:</label>
            <select id="level-select" onchange="loadLearningPath('${data.name.replace(/'/g, "\\'")}')">
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
            </select>
        </div>
        <div id="learning-path"></div>`;

    detail.innerHTML = html;
    detail.classList.remove('hidden');

    loadLearningPath(data.name);
}

async function addModule(e, curriculumName) {
    e.preventDefault();
    const form = e.target;
    const moduleData = {
        name: form.querySelector('[name="title"]').value.trim(),
        content: form.querySelector('[name="content"]').value.trim(),
        objectives: form.querySelector('[name="objectives"]').value.split(',').map(s => s.trim()).filter(Boolean),
        duration_minutes: parseInt(form.querySelector('[name="duration_minutes"]').value) || 30,
        prerequisites: form.querySelector('[name="prerequisites"]').value.split(',').map(s => s.trim()).filter(Boolean),
        exercises: []
    };

    const data = await apiFetch(`/api/education/curricula/${encodeURIComponent(curriculumName)}/modules`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(moduleData)
    });
    if (data) {
        showNotification('Module added', 'success');
        loadCurriculum(curriculumName);
    }
}

function showEditModule(curriculumName, moduleName) {
    const detail = document.getElementById('curriculum-detail');
    const existing = document.getElementById('edit-module-overlay');
    if (existing) existing.remove();

    const overlay = document.createElement('div');
    overlay.id = 'edit-module-overlay';
    overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:200;display:flex;align-items:center;justify-content:center;';
    overlay.innerHTML = `
        <div class="card" style="max-width:500px;width:90%;">
            <h3>Edit: ${escapeHtml(moduleName)}</h3>
            <form id="edit-module-form" style="display:grid;gap:0.75rem;">
                <textarea name="content" placeholder="New content" rows="3"></textarea>
                <input name="objectives" placeholder="New objectives (comma-separated)">
                <input name="duration_minutes" type="number" placeholder="Duration (minutes)" min="1">
                <input name="prerequisites" placeholder="Prerequisites (comma-separated)">
                <div style="display:flex;gap:0.5rem;">
                    <button type="submit" class="btn btn-primary">Save</button>
                    <button type="button" class="btn btn-secondary" onclick="document.getElementById('edit-module-overlay').remove()">Cancel</button>
                </div>
            </form>
        </div>`;
    document.body.appendChild(overlay);

    overlay.querySelector('form').addEventListener('submit', async (ev) => {
        ev.preventDefault();
        const form = ev.target;
        const updates = {};
        const content = form.querySelector('[name="content"]').value.trim();
        if (content) updates.content = content;
        const obj = form.querySelector('[name="objectives"]').value.trim();
        if (obj) updates.objectives = obj.split(',').map(s => s.trim()).filter(Boolean);
        const dur = form.querySelector('[name="duration_minutes"]').value;
        if (dur) updates.duration_minutes = parseInt(dur);
        const prereqs = form.querySelector('[name="prerequisites"]').value.trim();
        if (prereqs !== '') updates.prerequisites = prereqs.split(',').map(s => s.trim()).filter(Boolean);

        const data = await apiFetch(`/api/education/curricula/${encodeURIComponent(curriculumName)}/modules/${encodeURIComponent(moduleName)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        });
        if (data) {
            overlay.remove();
            showNotification('Module updated', 'success');
            loadCurriculum(curriculumName);
        }
    });
}

async function exportCurriculum(name, format) {
    const data = await apiFetch(`/api/education/curricula/${encodeURIComponent(name)}/export?format=${format}`);
    if (!data) return;

    const blob = new Blob([typeof data.content === 'string' ? data.content : JSON.stringify(data.content, null, 2)], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `${name}.${format === 'json' ? 'json' : 'txt'}`;
    a.click();
    URL.revokeObjectURL(a.href);
}

async function loadLearningPath(curriculumName) {
    const container = document.getElementById('learning-path');
    if (!container) return;

    const levelSelect = document.getElementById('level-select');
    const level = levelSelect ? levelSelect.value : 'beginner';

    const data = await apiFetch(`/api/education/curricula/${encodeURIComponent(curriculumName)}/learning-path?level=${level}`);
    if (!data || !data.path) {
        container.innerHTML = '<p class="empty-state">No learning path available.</p>';
        return;
    }

    if (data.path.length === 0) {
        container.innerHTML = '<p class="empty-state">No modules in path for this level.</p>';
        return;
    }

    const ol = document.createElement('ol');
    ol.style.cssText = 'padding-left: 1.5rem;';
    data.path.forEach((mod, i) => {
        const li = document.createElement('li');
        li.style.cssText = 'margin-bottom: 0.5rem; padding: 0.25rem 0;';
        li.textContent = mod;
        if (i > 0) {
            const arrow = document.createElement('span');
            arrow.style.cssText = 'color: var(--text-secondary); font-size: 0.8rem; margin-left: 0.5rem;';
            arrow.textContent = '← requires: ' + data.path[i - 1];
            li.appendChild(arrow);
        }
        ol.appendChild(li);
    });
    container.innerHTML = '';
    container.appendChild(ol);
}


/* ── Quiz Interaction ──────────────────────────────────────────── */

let currentQuizQuestions = [];

async function loadTopics() {
    const select = document.getElementById('topic-select');
    if (!select) return;

    const data = await apiFetch('/api/education/topics');
    if (!data) return;

    select.innerHTML = data.map(t => `<option value="${escapeHtml(t)}">${escapeHtml(t)}</option>`).join('');
}

async function createSession(e) {
    e.preventDefault();
    const form = e.target;
    const student_name = form.querySelector('[name="student_name"]').value.trim();
    const topic = form.querySelector('[name="topic"]').value;
    if (!student_name || !topic) return;

    const data = await apiFetch('/api/education/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_name, topic })
    });
    if (data) {
        showNotification('Session started', 'success');
        document.getElementById('session-id').value = data.session_id;
        document.getElementById('session-info').classList.remove('hidden');
        document.getElementById('session-topic').textContent = data.topic;
        loadSessionProgress(data.session_id);
    }
}

async function generateQuiz(e) {
    e.preventDefault();
    const form = e.target;
    const topic = document.getElementById('topic-select').value;
    const difficulty = form.querySelector('[name="difficulty"]').value;
    const count = parseInt(form.querySelector('[name="count"]').value) || 5;

    const data = await apiFetch('/api/education/quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, difficulty, count })
    });
    if (!data) return;

    currentQuizQuestions = data;
    renderQuiz(data);
}

function renderQuiz(questions) {
    const container = document.getElementById('quiz-container');
    if (!container) return;

    if (questions.length === 0) {
        container.innerHTML = '<p class="empty-state">No questions available for this difficulty.</p>';
        return;
    }

    let html = '';
    questions.forEach((q, i) => {
        html += `<div class="card" style="margin-bottom: 0.75rem;" id="question-${i}">`;
        html += `<p><strong>Q${i + 1}.</strong> ${escapeHtml(q.question)} <span class="status-badge">${escapeHtml(q.difficulty)}</span></p>`;
        if (q.choices && q.choices.length > 0) {
            q.choices.forEach((choice, ci) => {
                const inputId = `q${i}-c${ci}`;
                html += `<div style="margin: 0.25rem 0;">`;
                html += `<input type="radio" name="q${i}" id="${inputId}" value="${escapeHtml(choice)}">`;
                html += ` <label for="${inputId}">${escapeHtml(choice)}</label>`;
                html += `</div>`;
            });
        }
        html += `<button class="btn btn-primary" style="margin-top: 0.5rem;" onclick="submitAnswer(${i})">Submit Answer</button>`;
        html += `<div id="feedback-${i}" style="margin-top: 0.5rem;"></div>`;
        html += `</div>`;
    });
    container.innerHTML = html;
}

async function submitAnswer(questionIndex) {
    const q = currentQuizQuestions[questionIndex];
    if (!q) return;

    const selected = document.querySelector(`input[name="q${questionIndex}"]:checked`);
    if (!selected) {
        showNotification('Please select an answer');
        return;
    }

    const sessionId = document.getElementById('session-id')?.value;
    const payload = {
        question_id: q.id,
        answer: selected.value
    };
    if (sessionId) payload.session_id = sessionId;

    const data = await apiFetch('/api/education/quiz/answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    if (!data) return;

    const feedbackEl = document.getElementById(`feedback-${questionIndex}`);
    if (feedbackEl) {
        const color = data.correct ? 'var(--success-color)' : 'var(--error-color)';
        feedbackEl.innerHTML = `<p style="color: ${color}; font-weight: 500;">${data.correct ? '✓ Correct' : '✗ Incorrect'}</p>`;
        feedbackEl.innerHTML += `<p style="font-size: 0.9rem; color: var(--text-secondary);">${escapeHtml(data.feedback)}</p>`;
    }

    // Disable the submit button
    const card = document.getElementById(`question-${questionIndex}`);
    if (card) {
        const btn = card.querySelector('.btn');
        if (btn) { btn.disabled = true; btn.textContent = 'Answered'; }
    }

    // Refresh progress
    if (sessionId) loadSessionProgress(sessionId);
}

async function loadSessionProgress(sessionId) {
    const panel = document.getElementById('session-progress');
    if (!panel) return;

    const data = await apiFetch(`/api/education/sessions/${encodeURIComponent(sessionId)}/progress`);
    if (!data) return;

    panel.innerHTML = `
        <div class="card">
            <div class="card-title">Session Progress</div>
            <div class="metric-grid">
                <div class="metric"><span class="metric-value">${data.questions_asked}</span><span class="metric-label">Questions</span></div>
                <div class="metric"><span class="metric-value status-ok">${data.correct_answers}</span><span class="metric-label">Correct</span></div>
                <div class="metric"><span class="metric-value">${(data.accuracy * 100).toFixed(1)}%</span><span class="metric-label">Accuracy</span></div>
            </div>
        </div>`;
}


/* ── Exam / Assessment ─────────────────────────────────────────── */

let currentExam = null;

async function createExam(e) {
    e.preventDefault();
    const form = e.target;
    const curriculum_name = form.querySelector('[name="curriculum_name"]').value;
    const moduleFilter = form.querySelector('[name="module_names"]')?.value.trim();
    const payload = { curriculum_name };
    if (moduleFilter) {
        payload.module_names = moduleFilter.split(',').map(s => s.trim()).filter(Boolean);
    }

    const data = await apiFetch('/api/education/exams', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    if (!data) return;

    currentExam = data;
    renderExam(data);
}

function renderExam(exam) {
    const container = document.getElementById('exam-container');
    if (!container) return;

    let html = `<h3>Exam: ${escapeHtml(exam.curriculum_name)}</h3>`;
    html += `<form id="exam-submit-form" onsubmit="submitExam(event)">`;
    html += `<input type="hidden" name="exam_id" value="${exam.exam_id}">`;

    exam.questions.forEach((q, i) => {
        html += `<div class="card" style="margin-bottom: 0.75rem;">`;
        html += `<p><strong>${escapeHtml(q.module)}</strong> (${q.points} pts)</p>`;
        html += `<p>${escapeHtml(q.prompt)}</p>`;
        html += `<input name="answer-${q.id}" placeholder="Your answer" style="width: 100%; margin-top: 0.5rem;" required>`;
        html += `</div>`;
    });

    html += `<button type="submit" class="btn btn-primary">Submit Exam</button>`;
    html += `</form>`;
    container.innerHTML = html;
}

async function submitExam(e) {
    e.preventDefault();
    if (!currentExam) return;

    const form = e.target;
    const answers = {};
    currentExam.questions.forEach(q => {
        const input = form.querySelector(`[name="answer-${q.id}"]`);
        if (input) answers[q.id] = input.value;
    });

    const data = await apiFetch(`/api/education/exams/${encodeURIComponent(currentExam.exam_id)}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ curriculum_name: currentExam.curriculum_name, answers })
    });
    if (!data) return;

    renderExamResults(data);
}

function renderExamResults(results) {
    const container = document.getElementById('exam-results');
    if (!container) return;

    const passClass = results.passed ? 'status-ok' : 'status-err';
    let html = `
        <div class="card">
            <div class="card-title">Results <span class="status-badge ${results.passed ? 'active' : 'error'}">${results.passed ? 'PASSED' : 'FAILED'}</span></div>
            <div class="metric-grid">
                <div class="metric"><span class="metric-value">${results.earned_points}/${results.total_points}</span><span class="metric-label">Points</span></div>
                <div class="metric"><span class="metric-value ${passClass}">${results.score_percent.toFixed(1)}%</span><span class="metric-label">Score</span></div>
            </div>`;

    if (results.breakdown && results.breakdown.length > 0) {
        html += `<h3 style="margin-top: 1rem;">Breakdown</h3>`;
        results.breakdown.forEach(b => {
            html += `<p>${escapeHtml(b.module)}: ${b.points_earned}/${b.points_possible}</p>`;
        });
    }
    html += `</div>`;
    container.innerHTML = html;
}

async function generateCertificate(e) {
    e.preventDefault();
    const form = e.target;
    const payload = {
        student: form.querySelector('[name="student"]').value.trim(),
        curriculum_name: form.querySelector('[name="curriculum_name"]').value,
        score: parseFloat(form.querySelector('[name="score"]').value)
    };

    const data = await apiFetch('/api/education/certificates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    if (data) {
        showNotification('Certificate generated', 'success');
        loadCertificates();
    }
}

async function loadCertificates() {
    const list = document.getElementById('certificates-list');
    if (!list) return;

    const data = await apiFetch('/api/education/certificates');
    if (!data) return;

    if (data.length === 0) {
        list.innerHTML = '<p class="empty-state">No certificates yet.</p>';
        return;
    }

    list.innerHTML = data.map(c => `
        <div class="card" style="margin-bottom: 0.75rem;">
            <div class="card-title">${escapeHtml(c.student)} <span class="status-badge ${c.passed ? 'active' : 'error'}">${c.passed ? 'PASSED' : 'FAILED'}</span></div>
            <p>${escapeHtml(c.curriculum)} · ${c.score.toFixed(1)}%</p>
            <p style="font-size: 0.8rem; color: var(--text-secondary);">Issued: ${escapeHtml(c.issued_at)} · Hash: ${escapeHtml(c.verification_hash.substring(0, 12))}…</p>
        </div>
    `).join('');
}


/* ── Content Browser ───────────────────────────────────────────── */

async function loadContentTree(path = '') {
    const tree = document.getElementById('content-tree');
    if (!tree) return;

    const data = await apiFetch(`/api/content/tree?path=${encodeURIComponent(path)}`);
    if (!data) return;

    renderContentTree(tree, data, path);
}

function renderContentTree(container, data, currentPath) {
    if (!data.entries || data.entries.length === 0) {
        container.innerHTML = '<p class="empty-state">No files found.</p>';
        return;
    }

    const ul = document.createElement('ul');
    ul.style.cssText = 'list-style: none; padding-left: 1rem;';

    data.entries.forEach(entry => {
        const li = document.createElement('li');
        li.style.cssText = 'padding: 0.25rem 0; cursor: pointer;';

        const entryPath = currentPath ? `${currentPath}/${entry.name}` : entry.name;

        if (entry.type === 'directory') {
            const dirName = entry.name.replace(/\/$/, '');
            li.innerHTML = `<span style="color: var(--accent-color);">📁 ${escapeHtml(dirName)}</span>`;
            li.addEventListener('click', (e) => {
                e.stopPropagation();
                // Toggle: if already expanded, collapse
                const childUl = li.querySelector('ul');
                if (childUl) {
                    childUl.remove();
                } else {
                    loadSubTree(li, entryPath.replace(/\/$/, ''));
                }
            });
        } else {
            li.innerHTML = `<span>📄 ${escapeHtml(entry.name)}</span> <span style="font-size: 0.8rem; color: var(--text-secondary);">${entry.size ? formatSize(entry.size) : ''}</span>`;
            li.addEventListener('click', (e) => {
                e.stopPropagation();
                loadFilePreview(entryPath);
            });
        }
        ul.appendChild(li);
    });

    container.innerHTML = '';
    container.appendChild(ul);
}

async function loadSubTree(parentLi, path) {
    const data = await apiFetch(`/api/content/tree?path=${encodeURIComponent(path)}`);
    if (!data) return;

    const ul = document.createElement('ul');
    ul.style.cssText = 'list-style: none; padding-left: 1rem;';

    if (!data.entries || data.entries.length === 0) {
        const li = document.createElement('li');
        li.style.color = 'var(--text-secondary)';
        li.textContent = '(empty)';
        ul.appendChild(li);
    } else {
        data.entries.forEach(entry => {
            const li = document.createElement('li');
            li.style.cssText = 'padding: 0.25rem 0; cursor: pointer;';
            const entryPath = `${path}/${entry.name}`;

            if (entry.type === 'directory') {
                const dirName = entry.name.replace(/\/$/, '');
                li.innerHTML = `<span style="color: var(--accent-color);">📁 ${escapeHtml(dirName)}</span>`;
                li.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const childUl = li.querySelector('ul');
                    if (childUl) { childUl.remove(); } else { loadSubTree(li, entryPath.replace(/\/$/, '')); }
                });
            } else {
                li.innerHTML = `<span>📄 ${escapeHtml(entry.name)}</span> <span style="font-size: 0.8rem; color: var(--text-secondary);">${entry.size ? formatSize(entry.size) : ''}</span>`;
                li.addEventListener('click', (e) => {
                    e.stopPropagation();
                    loadFilePreview(entryPath);
                });
            }
            ul.appendChild(li);
        });
    }
    parentLi.appendChild(ul);
}

async function loadFilePreview(filepath) {
    const preview = document.getElementById('file-preview');
    if (!preview) return;

    const data = await apiFetch(`/api/content/file?path=${encodeURIComponent(filepath)}`);
    if (!data) return;

    let html = `<h3>${escapeHtml(filepath)}</h3>`;

    if (data.type === 'text') {
        html += `<pre class="console" style="color: var(--text-primary); background: var(--bg-tertiary);">${escapeHtml(data.content)}</pre>`;
    } else if (data.type === 'image') {
        html += `<img src="/api/content/file?path=${encodeURIComponent(filepath)}" alt="${escapeHtml(filepath)}" style="max-width: 100%; border-radius: 8px;">`;
    } else if (data.type === 'html') {
        html += `<p><a href="/api/content/file?path=${encodeURIComponent(filepath)}" target="_blank" class="btn btn-secondary">Open in new tab</a></p>`;
    } else {
        html += `<p>Preview not available for this file type.</p>`;
        html += `<p><a href="/api/content/file?path=${encodeURIComponent(filepath)}" target="_blank" class="btn btn-secondary">Download</a></p>`;
    }

    preview.innerHTML = html;
}

/* ── Utilities ─────────────────────────────────────────────────── */

function escapeHtml(str) {
    if (typeof str !== 'string') return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

/* ── DOMContentLoaded Init ─────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
    // Theme toggle button
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

    // Curriculum page init
    const curriculumForm = document.getElementById('create-curriculum-form');
    if (curriculumForm) {
        curriculumForm.addEventListener('submit', createCurriculum);
        loadCurriculaList();
    }

    // Tutoring page init
    const sessionForm = document.getElementById('session-form');
    if (sessionForm) {
        sessionForm.addEventListener('submit', createSession);
        loadTopics();
    }
    const quizForm = document.getElementById('quiz-form');
    if (quizForm) quizForm.addEventListener('submit', generateQuiz);

    // Assessment page init
    const examForm = document.getElementById('exam-form');
    if (examForm) examForm.addEventListener('submit', createExam);
    const certForm = document.getElementById('certificate-form');
    if (certForm) {
        certForm.addEventListener('submit', generateCertificate);
        loadCertificates();
    }

    // Content browser init
    const contentTree = document.getElementById('content-tree');
    if (contentTree) loadContentTree();
});
