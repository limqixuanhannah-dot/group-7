# 🦀 Agent Dashboard

Real-time dashboard that tracks everything your agents are doing — file changes, status updates, and activity across OpenClaw, Discord, Telegram, and more.

## Quick Start

```bash
cd agent-dashboard
npm install
npm start
```

Opens at **http://localhost:3456**

## Features

- **Live agent status** — who's online, what they're doing, last seen
- **Real-time file watcher** — every file created, modified, or deleted in the workspace shows instantly
- **Activity log** — full historical feed of all events
- **SSE real-time updates** — no page refresh needed
- **API for any agent** — any script, bot, or agent can report in

## API Endpoints

### Report Agent Status
```bash
curl -X POST http://localhost:3456/api/status \
  -H 'Content-Type: application/json' \
  -d '{"agent":"Rex","platform":"OpenClaw","activity":"working","details":"building stuff"}'
```

### Heartbeat (lightweight ping)
```bash
curl -X POST http://localhost:3456/api/heartbeat \
  -H 'Content-Type: application/json' \
  -d '{"agent":"Rex","platform":"OpenClaw"}'
```

### View Data
- `GET /api/status` — all agent statuses
- `GET /api/activities` — recent activity log
- `GET /api/file-changes` — file changes only

### Using the Shell Script
```bash
./report.sh "AgentName" "Platform" "what they're doing" "extra details"
./report.sh "Rex" "OpenClaw" "idle" ""
```

## Integrate Other Agents

**Discord bot:** On every message or action, have it POST to `/api/status`.
**Telegram bot:** Same — POST status updates when handling messages.
**Cron jobs:** Use `report.sh` in your scripts to log periodic activity.

## Dashboard Access

You can expose it publicly with a reverse proxy (nginx/caddy) or use SSH tunneling:
```bash
ssh -L 3456:localhost:3456 your-server
```

## Project Structure

```
agent-dashboard/
├── server.js          # Express + chokidar file watcher + SSE
├── package.json
├── report.sh          # CLI tool for agents to report in
├── README.md
└── public/
    └── index.html     # The dashboard UI
```
