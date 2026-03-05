# PROACTIVE-TRACKER.md

**Purpose:** Track proactive opportunities and patterns

## Daily Checks (Auto)
- [ ] Moltbook notifications
- [ ] GitHub backup status
- [ ] Pending data updates

## Weekly Checks (Manual)
- [ ] Decision follow-ups
- [ ] MEMORY.md organization
- [ ] New automation candidates

## Monthly Checks
- [ ] Cron job health
- [ ] Tool config updates
- [ ] Archive old memories

## Automation Patterns

| Pattern | Status |
|---------|--------|
| YouTube → TikTok text | Active |
| **Moltbook daily summary** | **Cron v4 (20:00 daily)** ✅ Restored 2026-03-04 |
| Moltbook weekly share | Cron (Mon 10:00) |
| Player data update | **可靠版（12:30 daily）** ✅ Fixed 2026-03-05 |
| GitHub backup | Cron (23:30 daily) |
| Weather + rain alert | Cron (09:00 daily) |

## Ideas
- Basketball: Alert on major games/breakthroughs
- Tech: Weekly skill recommendation
- Personal: Holiday greetings

## Current Jobs

| Name | ID | Schedule | Status |
|------|-----|----------|--------|
| Self-check | 5994d9b0... | Every 6h | Active |
| Weather | 9365f390... | 09:00 daily | Active |
| **Moltbook daily v4** | **70966d5e...** | **20:00 daily** | **✅ Restored 2026-03-04** |
| **Player data 可靠版** | **73fed0be...** | **12:30 daily** | **✅ Fixed 2026-03-05** |
| ~~Player data v1~~ | ~~c38da80e...~~ | ~~12:30 daily~~ | ~~❌ Outdated~~ |
| GitHub backup | 9a8ac27d... | 23:30 daily | Active |
| Weekly share | 40235326... | Mon 10:00 | Active |

---

## Change Log

### 2026-03-04: 杨瀚森数据抓取修复

**Problem:**
- Cron job was fetching outdated data from October 2025
- Recent games (March 2026) were not being captured
- Data accuracy issue identified by user

**Root Cause:**
- Previous cron job didn't scroll to top of page to get latest matches
- Was picking up old cached or default view data

**Solution:**
- Created new cron job: `杨瀚森每日数据更新_v2`
- Job ID: `0b2eb1a9-2df2-4287-ab65-93d77cb9edf5`
- Explicit instructions to scroll and verify latest dates
- Added validation to ensure March 2026 data (not October 2025)

**Status:** ✅ Fixed and deployed

### 2026-03-05: 杨瀚森数据抓取再次修复 - 解决AI幻觉问题

**Problem:**
- Cron job 产生了假数据（24分钟14分8板等）
- 真实数据是6分钟0分1板等
- 用户通过Tavily搜索验证了数据真实性
- AI产生了严重的幻觉，编造了不存在的比赛数据

**Root Cause:**
- Agent在抓取数据时可能失败了
- AI试图"填补"缺失的数据，生成了假数据
- 没有正确验证数据的真实性

**Solution:**
- 删除了所有旧版本的杨瀚森cron job
- 创建了新的`杨瀚森数据更新_可靠版`
- Job ID: `73fed0be-2056-4819-9195-043384dc09ee`
- 使用web_fetch直接获取虎扑页面原始数据
- 明确指令：**严禁编造数据**，只报告页面上真实存在的数据
- 如果无法获取，明确说明"数据获取失败"

**Status:** ✅ Fixed and deployed
