# BOOTSTRAP.md - Session Recovery Guide

## Purpose
Use this file when a new session starts, context was compacted, or state needs to be recovered quickly.

## Read Order
1. `AGENTS.md`
2. `SOUL.md`
3. `USER.md`
4. `MEMORY.md`
5. `memory/YYYY-MM-DD.md`（今天 + 昨天）
6. `TOOLS.md`（需要查工作流/命令/路径时）

## Current Stable Workflows
- **Accounting skill**: local bookkeeping is usable (`skills/accounting/`)
- **YouTube skill v2**: download / impersonate / cookies / normalize cookies / Telegram-compatible output 已打通 (`skills/yt-dlp-downloader/`)
- **Moltbook**: API-level posting is usable, but web permalink is not reliably confirmable yet
- **Yang Hansen cron**: optimized for “today’s conclusion first”, split NBA vs G League, with jump links
- **Weather cron**: optimized for quick morning reading, going-out takeaway first

## Current Open Items / Known Issues
- **Moltbook web layer**: `/api/v1/posts?...` currently returns 500; do not assume `/p/<id>` or `/posts/<id>` is the real public link
- **Browser tool / Chrome integration**: historically unstable; command-line Chrome / headless fallback is often more reliable
- **YouTube Shorts**: some links still require valid cookies even when impersonation is available

## Default Working Style
- 先结论，再展开
- 优先给可落地方案，不空谈
- 能收口成 skill / workflow / cron 的，尽量收口
- 做完后优先同步 `TOOLS.md` / `memory/*.md`
- 复杂问题先分层定性，再决定下一步

## Important Paths
- `~/.openclaw/cron/jobs.json`
- `/root/.openclaw/workspace/skills/accounting/`
- `/root/.openclaw/workspace/skills/yt-dlp-downloader/`
- `/root/.openclaw/workspace/docs/youtube-download-workflow.md`
- `/root/.openclaw/workspace/TOOLS.md`
- `/root/.openclaw/workspace/memory/`

## Quick Reminder
If a task feels “already solved before”, first check:
1. `MEMORY.md`
2. `TOOLS.md`
3. related skill folder under `skills/`
4. recent daily memory files
