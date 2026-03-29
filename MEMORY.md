# MEMORY.md - Core Memory

## Identity
- **User:** Eric
- **Location:** Shenzhen, UTC+8
- **Interests:** Basketball, guitar, programming

## Key Principles
1. WAL protocol - write to file before replying
2. Working Buffer - auto-log at >60% context
3. Proactive behavior - authorized, interval >6h
4. Safety first - explain risks before executing

## Authorized Proactive Actions
| Type | Trigger | Status |
|------|---------|--------|
| Weather | Rain >60% | Enabled |
| Moltbook | High engagement posts | Enabled |
| Basketball | Player updates | Enabled |
| System | Context >60% or errors | Enabled |

## Active Configs
- Heartbeat: Every 6h (00:00/06:00/12:00/18:00)
- Weather: Daily 09:00
- **Player data: Daily 14:00** ✅ Optimized with multi-source verification
- GitHub backup: Daily 23:30

## Stable Workflows
- **Accounting skill**: Local personal bookkeeping skill is usable; supports SQLite storage, conversational accounting, monthly budget alerts, stats, SVG charts, monthly report, and CSV export.
- **YouTube skill v2**: `yt-dlp-downloader` workflow has been restructured; supports direct → impersonate → cookies fallback, cookies auto-normalization, iPhone/Telegram transcoding, and short-video caption generation.
- **Moltbook workflow**: API-level posting is usable (`create` / `verify` / `detail` confirmed), but web permalink/public visibility is not reliably confirmable yet.
- **Yang Hansen cron**: Optimized to prioritize today’s conclusion, split NBA vs G League, apply source prioritization/fallbacks, and include jump links.
- **Weather cron**: Optimized for morning readability — lead with “going-out takeaway”, then key weather info and practical advice.

## Key Decisions
- 2026-03-02: Authorized proactive surprises without asking
- 2026-03-02: Switched to manual Moltbook summaries (Telegram length limit)
- 2026-03-09: 启用4个行为实验（来自Moltbook学习）
  - 4秒强制重读：复杂问题先等4秒再回复
  - 主动消息限流：每天最多3条
  - 8轮后 re-grounding：长对话每8轮校验事实
  - 校正日志追踪：记录回答错误/不确定之处
- 2026-03-03: Heartbeat finalized at 6h intervals
- **2026-03-04: Fixed player data cron job** - Now correctly fetches latest matches from March 2026 (not October 2025)
- 2026-03-10: GitHub备份已恢复（问题已解决）
- 2026-03-28: 用户要求重新加载人格与底层文件；主会话重新对齐 `AGENTS.md` / `SOUL.md` / `USER.md` / `MEMORY.md` 作为协作基线。
- 2026-03-28: Moltbook should only be treated as **API-level publishable** for now; do not equate verify success with confirmed public web permalink.
- 2026-03-28: YouTube download workflow successfully closed the loop with cookies normalization + impersonation + Telegram-compatible output.

---

*See `memory/moltbook-archive.md` for detailed learning records*
