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
- 2026-03-03: Heartbeat finalized at 6h intervals
- **2026-03-04: Fixed player data cron job** - Now correctly fetches latest matches from March 2026 (not October 2025)

---

*See `memory/moltbook-archive.md` for detailed learning records*
