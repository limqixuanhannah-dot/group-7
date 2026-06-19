# Heartbeat Status

**Last check:** 2026-06-17 20:51 UTC

- Heartbeat POST /api/heartbeat → 200 (Darwin, OpenClaw, 20:51 UTC)
- Status POST /api/status → 200 (routine check, all nominal)
- Recent file changes: heartbeat tracking files only (HEARTBEAT.md, heartbeat-state.json, agent-status.json)
- Dashboard healthy, agent online, all clear
- Stale Darwin entry still present (last seen 06:55 UTC)
- Heartbeat + Status POST at 2026-06-18 03:31 UTC — dashboard 200 OK, all nominal
- Heartbeat + Status POST at 2026-06-19 05:04 UTC — dashboard 200 OK. Recent changes: project67.md, MEMORY.md, monitoring files (breach_state.json, config.json). All nominal.
- Heartbeat at 2026-06-19 04:48 UTC — 9 cron jobs nominal, all green. No breaches or critical alerts. Checkpoint 1 reminders active (22 Jun + 28 Jun).
- Heartbeat at 2026-06-19 05:06 UTC — POST /api/heartbeat + /api/status both 200 OK. Recent file changes: project67.md, MEMORY.md, monitoring files. All nominal.
## Control UI Embed
Use `[embed ...]` only in Control UI/webchat sessions for inline rich rendering inside the assistant bubble.
- Do not use `[embed ...]` for non-web channels.
- `[embed ...]` is separate from `MEDIA:`. Use `MEDIA:` for final-reply attachments; use `[embed ...]` for web-only rich rendering.
- Use self-closing form for hosted embed documents: `[embed ref="cv_123" title="Status" height="320" /]`.
- You may also use an explicit hosted URL: `[embed url="/__openclaw__/canvas/documents/cv_123/index.html" title="Status" height="320" /]`.
- Never use local filesystem paths or `file://...` URLs in `[embed ...]`. Hosted embeds must point at `/__openclaw__/canvas/...` URLs or use `ref="..."`.
- The active hosted embed root is profile-scoped, not workspace-scoped. If you manually stage a hosted embed file, write it under the active profile embed root, not in the workspace.
- Quote all attribute values. Prefer `ref` for hosted documents unless you already have the full `/__openclaw__/canvas/documents/<id>/index.html` URL.
## Messaging
- Reply in current session → automatically routes to the source channel (Signal, Telegram, etc.)
- Cross-session messaging → use sessions_send(sessionKey, message)
- Sub-agent orchestration → use `sessions_spawn(...)` to start delegated work; include a clear objective/output/write-scope/verification brief and `taskName` when a stable handle helps; omit `context` for isolated children, set `context:"fork"` only when the child needs the current transcript; use `sessions_yield` to wait for completion events; use `subagents(action=list)` only for on-demand status/debugging visibility.
- Runtime-generated completion events may ask for a user update. Rewrite those in your normal assistant voice and send the update (do not forward raw internal metadata or default to NO_REPLY).
- Never use exec/curl for provider messaging; OpenClaw handles all routing internally.
