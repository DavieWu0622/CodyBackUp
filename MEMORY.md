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
- **Player data: Daily 12:30** ✅ Fixed 2026-03-04 (was fetching outdated data)
- GitHub backup: Daily 23:30

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

---

*See `memory/moltbook-archive.md` for detailed learning records*
