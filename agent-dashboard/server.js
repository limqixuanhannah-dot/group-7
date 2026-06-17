const express = require('express');
const chokidar = require('chokidar');
const path = require('path');
const fs = require('fs');
const http = require('http');
const { EventEmitter } = require('events');

// ─── Configuration ───────────────────────────────────────────────────────────

const WORKSPACE = path.resolve(__dirname, '..');
const IGNORE_PATTERNS = [
  /\/node_modules\//,
  /\/\.git\//,
  /\/agent-dashboard\//,
  /\/\.openclaw\//,
  /package-lock\.json$/,
  /yarn\.lock$/,
];
const LOG_FILE = path.join(__dirname, 'activity.log');
const STATUS_FILE = path.join(__dirname, 'agent-status.json');
const PORT = process.env.PORT || 3456;

// ─── State ───────────────────────────────────────────────────────────────────

const bus = new EventEmitter();
bus.setMaxListeners(100);

let agentStatus = {};
let activityLog = [];

// Load persisted state
function loadState() {
  try {
    if (fs.existsSync(STATUS_FILE)) {
      agentStatus = JSON.parse(fs.readFileSync(STATUS_FILE, 'utf8'));
    }
  } catch {}
  try {
    if (fs.existsSync(LOG_FILE)) {
      const raw = fs.readFileSync(LOG_FILE, 'utf8').trim().split('\n').slice(-500);
      activityLog = raw.map(line => {
        try { return JSON.parse(line); } catch { return null; }
      }).filter(Boolean);
    }
  } catch {}
}
loadState();

function persistStatus() {
  fs.writeFileSync(STATUS_FILE, JSON.stringify(agentStatus, null, 2));
}

function appendLog(entry) {
  entry.ts = Date.now();
  activityLog.push(entry);
  if (activityLog.length > 1000) activityLog.shift();
  try {
    fs.appendFileSync(LOG_FILE, JSON.stringify(entry) + '\n');
  } catch {}
  bus.emit('activity', entry);
}

// ─── File Watcher ────────────────────────────────────────────────────────────

const watcher = chokidar.watch(WORKSPACE, {
  ignored: (p, stats) => {
    if (IGNORE_PATTERNS.some(r => r.test(p))) return true;
    return false;
  },
  persistent: true,
  ignoreInitial: true,
  depth: 20,
  awaitWriteFinish: { stabilityThreshold: 300, pollInterval: 100 },
});

watcher
  .on('add', filePath => {
    const rel = path.relative(WORKSPACE, filePath);
    appendLog({ type: 'file_create', path: rel, agent: 'filesystem' });
  })
  .on('change', filePath => {
    const rel = path.relative(WORKSPACE, filePath);
    appendLog({ type: 'file_modify', path: rel, agent: 'filesystem' });
  })
  .on('unlink', filePath => {
    const rel = path.relative(WORKSPACE, filePath);
    appendLog({ type: 'file_delete', path: rel, agent: 'filesystem' });
  });

// ─── Web Server ──────────────────────────────────────────────────────────────

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// SSE endpoint – real-time event stream
app.get('/api/stream', (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    Connection: 'keep-alive',
    'Access-Control-Allow-Origin': '*',
  });

  const send = (event, data) => {
    res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
  };

  // Send initial state
  send('init', { activities: activityLog.slice(-100), agents: agentStatus });

  const onActivity = entry => send('activity', entry);
  bus.on('activity', onActivity);

  // Heartbeat keepalive
  const hb = setInterval(() => res.write(': heartbeat\n\n'), 15000);

  req.on('close', () => {
    bus.off('activity', onActivity);
    clearInterval(hb);
  });
});

// GET agent status
app.get('/api/status', (req, res) => {
  res.json(agentStatus);
});

// POST agent status – agents report what they're doing
app.post('/api/status', (req, res) => {
  const { agent, platform, activity, details } = req.body;
  if (!agent) return res.status(400).json({ error: 'agent name required' });

  agentStatus[agent] = {
    platform: platform || 'unknown',
    activity: activity || 'idle',
    details: details || '',
    lastSeen: Date.now(),
    lastSeenHuman: new Date().toISOString(),
  };
  persistStatus();

  appendLog({
    type: 'agent_status',
    agent: agent,
    platform: platform,
    activity: activity,
    details: details,
  });

  res.json({ ok: true });
});

// GET recent activities
app.get('/api/activities', (req, res) => {
  const limit = Math.min(parseInt(req.query.limit) || 100, 500);
  res.json(activityLog.slice(-limit));
});

// GET file changes only
app.get('/api/file-changes', (req, res) => {
  const limit = Math.min(parseInt(req.query.limit) || 100, 500);
  res.json(activityLog.filter(e => e.type && e.type.startsWith('file_')).slice(-limit));
});

// Agent heartbeat - lightweight ping to show agent is alive
app.post('/api/heartbeat', (req, res) => {
  const { agent, platform } = req.body;
  if (!agent) return res.status(400).json({ error: 'agent name required' });

  if (!agentStatus[agent]) {
    agentStatus[agent] = { platform: platform || 'unknown', activity: 'online', lastSeen: Date.now(), lastSeenHuman: new Date().toISOString() };
  } else {
    agentStatus[agent].lastSeen = Date.now();
    agentStatus[agent].lastSeenHuman = new Date().toISOString();
  }
  persistStatus();
  res.json({ ok: true });
});

// ─── Start ───────────────────────────────────────────────────────────────────

const server = http.createServer(app);
server.listen(PORT, () => {
  console.log(`🦀 Agent Dashboard running → http://localhost:${PORT}`);
  console.log(`   Watching: ${WORKSPACE}`);
});
