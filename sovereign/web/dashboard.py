"""Built-in HTML dashboard for the Sovereign Web UI.

A single-page application that provides a visual interface for managing
agents, tasks, the design engine, and viewing system status.
"""

from __future__ import annotations

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Sovereign - Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
  <style>
    * { font-family: 'Inter', sans-serif; }
    .glass { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(16px); }
    .glow { box-shadow: 0 0 30px rgba(99, 102, 241, 0.15); }
    @keyframes pulse-slow { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
    .animate-pulse-slow { animation: pulse-slow 3s ease-in-out infinite; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
    .fade-in { animation: fadeIn 0.3s ease-out; }
  </style>
</head>
<body class="bg-[#020617] text-slate-100 min-h-screen antialiased">
  <div id="app">
    <!-- Sidebar -->
    <aside class="fixed left-0 top-0 h-full w-64 glass border-r border-slate-800 z-40 flex flex-col">
      <div class="p-6 border-b border-slate-800">
        <h1 class="text-xl font-bold text-indigo-400">Sovereign</h1>
        <p class="text-xs text-slate-500 mt-1">Autonomous Agent Platform</p>
      </div>
      <nav class="flex-1 p-4 space-y-1">
        <button onclick="showTab('overview')" class="nav-btn w-full text-left px-4 py-2.5 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-800/50 hover:text-white transition-colors" data-tab="overview">
          Overview
        </button>
        <button onclick="showTab('tasks')" class="nav-btn w-full text-left px-4 py-2.5 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-800/50 hover:text-white transition-colors" data-tab="tasks">
          Task Queue
        </button>
        <button onclick="showTab('agents')" class="nav-btn w-full text-left px-4 py-2.5 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-800/50 hover:text-white transition-colors" data-tab="agents">
          Agents
        </button>
        <button onclick="showTab('design')" class="nav-btn w-full text-left px-4 py-2.5 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-800/50 hover:text-white transition-colors" data-tab="design">
          Design Engine
        </button>
        <button onclick="showTab('tools')" class="nav-btn w-full text-left px-4 py-2.5 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-800/50 hover:text-white transition-colors" data-tab="tools">
          Tools
        </button>
        <button onclick="showTab('run')" class="nav-btn w-full text-left px-4 py-2.5 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-800/50 hover:text-white transition-colors" data-tab="run">
          Run Goal
        </button>
      </nav>
      <div class="p-4 border-t border-slate-800">
        <div class="flex items-center gap-2">
          <div class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-slow"></div>
          <span class="text-xs text-slate-500">System Active</span>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="ml-64 p-8">
      <!-- Overview Tab -->
      <div id="tab-overview" class="tab-content">
        <h2 class="text-2xl font-bold mb-6">System Overview</h2>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div class="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 glow">
            <p class="text-sm text-slate-500 mb-1">Total Tasks</p>
            <p class="text-3xl font-bold text-white" id="stat-total">-</p>
          </div>
          <div class="p-6 rounded-2xl bg-slate-900/50 border border-slate-800">
            <p class="text-sm text-slate-500 mb-1">Completed</p>
            <p class="text-3xl font-bold text-emerald-400" id="stat-completed">-</p>
          </div>
          <div class="p-6 rounded-2xl bg-slate-900/50 border border-slate-800">
            <p class="text-sm text-slate-500 mb-1">In Progress</p>
            <p class="text-3xl font-bold text-amber-400" id="stat-progress">-</p>
          </div>
          <div class="p-6 rounded-2xl bg-slate-900/50 border border-slate-800">
            <p class="text-sm text-slate-500 mb-1">Failed</p>
            <p class="text-3xl font-bold text-red-400" id="stat-failed">-</p>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="p-6 rounded-2xl bg-slate-900/50 border border-slate-800">
            <h3 class="text-lg font-semibold mb-4">System Config</h3>
            <div id="system-config" class="space-y-2 text-sm text-slate-400">Loading...</div>
          </div>
          <div class="p-6 rounded-2xl bg-slate-900/50 border border-slate-800">
            <h3 class="text-lg font-semibold mb-4">Recent Tasks</h3>
            <div id="recent-tasks" class="space-y-2 text-sm text-slate-400">Loading...</div>
          </div>
        </div>
      </div>

      <!-- Tasks Tab -->
      <div id="tab-tasks" class="tab-content hidden">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold">Task Queue</h2>
          <button onclick="showTab('run')" class="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-500 transition-colors">
            + New Task
          </button>
        </div>
        <div class="flex gap-2 mb-4">
          <button onclick="filterTasks(null)" class="px-3 py-1.5 rounded-lg bg-slate-800 text-xs text-slate-300 hover:bg-slate-700">All</button>
          <button onclick="filterTasks('pending')" class="px-3 py-1.5 rounded-lg bg-slate-800 text-xs text-slate-300 hover:bg-slate-700">Pending</button>
          <button onclick="filterTasks('in_progress')" class="px-3 py-1.5 rounded-lg bg-slate-800 text-xs text-amber-400 hover:bg-slate-700">In Progress</button>
          <button onclick="filterTasks('completed')" class="px-3 py-1.5 rounded-lg bg-slate-800 text-xs text-emerald-400 hover:bg-slate-700">Completed</button>
          <button onclick="filterTasks('failed')" class="px-3 py-1.5 rounded-lg bg-slate-800 text-xs text-red-400 hover:bg-slate-700">Failed</button>
        </div>
        <div id="task-list" class="space-y-3">Loading...</div>
      </div>

      <!-- Agents Tab -->
      <div id="tab-agents" class="tab-content hidden">
        <h2 class="text-2xl font-bold mb-6">Specialized Agents</h2>
        <div id="agent-list" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">Loading...</div>
      </div>

      <!-- Design Tab -->
      <div id="tab-design" class="tab-content hidden">
        <h2 class="text-2xl font-bold mb-6">AI Design Engine</h2>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-400 mb-1">Brand Name</label>
              <input id="design-brand" type="text" placeholder="Your Brand" class="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white focus:border-indigo-500 outline-none"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-400 mb-1">Description</label>
              <textarea id="design-desc" rows="3" placeholder="Describe what the site should be about..." class="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white focus:border-indigo-500 outline-none resize-none"></textarea>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-400 mb-1">Page Type</label>
                <select id="design-type" class="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white focus:border-indigo-500 outline-none">
                  <option value="saas_landing">SaaS Landing</option>
                  <option value="portfolio">Portfolio</option>
                  <option value="agency">Agency</option>
                  <option value="startup">Startup</option>
                  <option value="ecommerce">E-Commerce</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-400 mb-1">Color Palette</label>
                <select id="design-palette" class="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white focus:border-indigo-500 outline-none">
                  <option value="midnight">Midnight</option>
                  <option value="ocean">Ocean</option>
                  <option value="forest">Forest</option>
                  <option value="sunset">Sunset</option>
                  <option value="monochrome">Monochrome</option>
                  <option value="aurora">Aurora</option>
                </select>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-400 mb-1">Sections</label>
              <input id="design-sections" type="text" value="hero,features,pricing,testimonials,cta,footer" class="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white focus:border-indigo-500 outline-none"/>
            </div>
            <button onclick="generateDesign()" id="design-btn" class="w-full py-3 rounded-xl bg-indigo-600 text-white font-semibold hover:bg-indigo-500 transition-colors">
              Generate Design
            </button>
          </div>
          <div>
            <div class="p-4 rounded-2xl bg-slate-900/50 border border-slate-800 h-full min-h-[400px]">
              <div id="design-preview" class="text-slate-500 text-sm text-center py-20">
                Generated design will appear here
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tools Tab -->
      <div id="tab-tools" class="tab-content hidden">
        <h2 class="text-2xl font-bold mb-6">Available Tools</h2>
        <div id="tools-list" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">Loading...</div>
      </div>

      <!-- Run Goal Tab -->
      <div id="tab-run" class="tab-content hidden">
        <h2 class="text-2xl font-bold mb-6">Run a Goal</h2>
        <div class="max-w-2xl">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-400 mb-1">Goal</label>
              <textarea id="run-goal" rows="3" placeholder="Describe what you want Sovereign to do..." class="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white focus:border-indigo-500 outline-none resize-none"></textarea>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-400 mb-1">Priority (1-10)</label>
                <input id="run-priority" type="number" min="1" max="10" value="5" class="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white focus:border-indigo-500 outline-none"/>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-400 mb-1">Budget (USD)</label>
                <input id="run-budget" type="number" step="0.5" placeholder="Optional" class="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white focus:border-indigo-500 outline-none"/>
              </div>
            </div>
            <button onclick="runGoal()" id="run-btn" class="w-full py-3 rounded-xl bg-indigo-600 text-white font-semibold hover:bg-indigo-500 transition-colors">
              Run Goal
            </button>
            <div id="run-result" class="hidden p-4 rounded-xl bg-slate-900 border border-slate-700 text-sm"></div>
          </div>
        </div>
      </div>
    </main>
  </div>

  <script>
    const API = window.location.origin;

    // Tab management
    function showTab(name) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
      document.getElementById('tab-' + name).classList.remove('hidden');
      document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('bg-slate-800/50', 'text-white');
        if (btn.dataset.tab === name) btn.classList.add('bg-slate-800/50', 'text-white');
      });
      if (name === 'overview') loadOverview();
      if (name === 'tasks') loadTasks();
      if (name === 'agents') loadAgents();
      if (name === 'tools') loadTools();
    }

    // API helpers
    async function api(path, opts = {}) {
      const res = await fetch(API + path, {
        headers: { 'Content-Type': 'application/json' },
        ...opts,
      });
      return res.json();
    }

    // Overview
    async function loadOverview() {
      try {
        const status = await api('/status');
        document.getElementById('stat-total').textContent = status.task_queue?.total || 0;
        document.getElementById('stat-completed').textContent = status.task_queue?.completed || 0;
        document.getElementById('stat-progress').textContent = status.task_queue?.in_progress || 0;
        document.getElementById('stat-failed').textContent = status.task_queue?.failed || 0;

        const cfg = status.config || {};
        document.getElementById('system-config').innerHTML = `
          <div class="flex justify-between"><span>Version</span><span class="text-white">${status.version}</span></div>
          <div class="flex justify-between"><span>Default Model</span><span class="text-white">${cfg.default_model}</span></div>
          <div class="flex justify-between"><span>Models</span><span class="text-white">${cfg.models_configured}</span></div>
          <div class="flex justify-between"><span>Budget/Task</span><span class="text-white">$${cfg.budget_per_task}</span></div>
          <div class="flex justify-between"><span>Budget/Day</span><span class="text-white">$${cfg.budget_per_day}</span></div>
        `;

        const tasks = await api('/tasks?limit=5');
        if (tasks.length === 0) {
          document.getElementById('recent-tasks').innerHTML = '<p class="text-slate-500">No tasks yet</p>';
        } else {
          document.getElementById('recent-tasks').innerHTML = tasks.map(t => `
            <div class="flex justify-between items-center p-2 rounded-lg hover:bg-slate-800/50">
              <span class="truncate flex-1">${t.goal}</span>
              <span class="ml-2 px-2 py-0.5 rounded text-xs ${statusColor(t.status)}">${t.status}</span>
            </div>
          `).join('');
        }
      } catch (e) { console.error(e); }
    }

    // Tasks
    async function loadTasks(statusFilter) {
      try {
        const url = statusFilter ? `/tasks?status_filter=${statusFilter}` : '/tasks';
        const tasks = await api(url);
        if (tasks.length === 0) {
          document.getElementById('task-list').innerHTML = '<p class="text-slate-500 text-center py-8">No tasks found</p>';
          return;
        }
        document.getElementById('task-list').innerHTML = tasks.map(t => `
          <div class="p-4 rounded-xl bg-slate-900/50 border border-slate-800 fade-in">
            <div class="flex justify-between items-start mb-2">
              <p class="font-medium text-white">${t.goal}</p>
              <span class="ml-2 px-2 py-0.5 rounded text-xs whitespace-nowrap ${statusColor(t.status)}">${t.status}</span>
            </div>
            <div class="flex gap-4 text-xs text-slate-500">
              <span>Priority: ${t.priority}</span>
              <span>Agent: ${t.agent_role}</span>
              <span>${t.created_at ? new Date(t.created_at).toLocaleString() : ''}</span>
            </div>
            ${t.result_output ? `<p class="mt-2 text-sm text-emerald-400 truncate">${t.result_output}</p>` : ''}
            ${t.result_error ? `<p class="mt-2 text-sm text-red-400 truncate">${t.result_error}</p>` : ''}
          </div>
        `).join('');
      } catch (e) { console.error(e); }
    }
    function filterTasks(status) { loadTasks(status); }

    // Agents
    async function loadAgents() {
      try {
        const agents = await api('/agents');
        const colors = ['indigo', 'cyan', 'emerald', 'amber', 'rose', 'purple', 'teal'];
        document.getElementById('agent-list').innerHTML = agents.map((a, i) => `
          <div class="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-${colors[i % colors.length]}-500/50 transition-all">
            <div class="w-12 h-12 rounded-xl bg-${colors[i % colors.length]}-500/10 flex items-center justify-center mb-4">
              <span class="text-${colors[i % colors.length]}-400 text-lg font-bold">${a.name[0]}</span>
            </div>
            <h3 class="text-lg font-semibold text-white mb-1">${a.name}</h3>
            <p class="text-sm text-slate-400">${a.description}</p>
            <p class="text-xs text-slate-600 mt-2">Role: ${a.role}</p>
          </div>
        `).join('');
      } catch (e) { console.error(e); }
    }

    // Tools
    async function loadTools() {
      try {
        const tools = await api('/tools');
        const catColors = { search: 'cyan', browser: 'indigo', system: 'amber', filesystem: 'emerald', design: 'purple', deploy: 'rose', business: 'teal', communication: 'orange' };
        document.getElementById('tools-list').innerHTML = tools.map(t => `
          <div class="p-4 rounded-xl bg-slate-900/50 border border-slate-800">
            <div class="flex items-center gap-2 mb-2">
              <span class="px-2 py-0.5 rounded text-xs bg-${catColors[t.category] || 'slate'}-500/10 text-${catColors[t.category] || 'slate'}-400">${t.category}</span>
              <span class="font-mono text-sm text-white">${t.name}</span>
            </div>
            <p class="text-sm text-slate-400">${t.description}</p>
          </div>
        `).join('');
      } catch (e) { console.error(e); }
    }

    // Design Engine
    async function generateDesign() {
      const btn = document.getElementById('design-btn');
      btn.textContent = 'Generating...';
      btn.disabled = true;

      try {
        const data = await api('/design', {
          method: 'POST',
          body: JSON.stringify({
            page_type: document.getElementById('design-type').value,
            brand_name: document.getElementById('design-brand').value || 'My Brand',
            description: document.getElementById('design-desc').value || 'A modern website',
            palette: document.getElementById('design-palette').value,
            sections: document.getElementById('design-sections').value,
          }),
        });

        if (data.html_preview) {
          document.getElementById('design-preview').innerHTML =
            '<iframe srcdoc="' + data.html_preview.replace(/"/g, '&quot;') + '" class="w-full h-[600px] rounded-lg border border-slate-700"></iframe>' +
            '<p class="text-xs text-slate-500 mt-2">Output: ' + (data.output_dir || '') + '</p>';
        }
      } catch (e) {
        document.getElementById('design-preview').innerHTML = '<p class="text-red-400">Error: ' + e.message + '</p>';
      }

      btn.textContent = 'Generate Design';
      btn.disabled = false;
    }

    // Run Goal
    async function runGoal() {
      const btn = document.getElementById('run-btn');
      const resultDiv = document.getElementById('run-result');
      btn.textContent = 'Running...';
      btn.disabled = true;

      try {
        const data = await api('/run', {
          method: 'POST',
          body: JSON.stringify({
            goal: document.getElementById('run-goal').value,
            priority: parseInt(document.getElementById('run-priority').value) || 5,
            budget_usd: parseFloat(document.getElementById('run-budget').value) || null,
          }),
        });

        resultDiv.classList.remove('hidden');
        resultDiv.innerHTML = `<p class="text-emerald-400">Task queued: ${data.task_id}</p><p class="text-slate-400 text-xs mt-1">Status: ${data.status}</p>`;
      } catch (e) {
        resultDiv.classList.remove('hidden');
        resultDiv.innerHTML = '<p class="text-red-400">Error: ' + e.message + '</p>';
      }

      btn.textContent = 'Run Goal';
      btn.disabled = false;
    }

    // Helpers
    function statusColor(s) {
      const map = { pending: 'bg-slate-700 text-slate-300', in_progress: 'bg-amber-500/10 text-amber-400', completed: 'bg-emerald-500/10 text-emerald-400', failed: 'bg-red-500/10 text-red-400', cancelled: 'bg-slate-700 text-slate-500' };
      return map[s] || 'bg-slate-700 text-slate-300';
    }

    // Init
    showTab('overview');
  </script>
</body>
</html>"""
