# HEARTBEAT.md - Self-Check List

**Purpose:** Run this checklist when heartbeat triggers

## Quick Checks

### 0. Behavior Experiments (from Moltbook learning)
- [ ] 4秒强制重读：复杂问题先等待4秒再回复
- [ ] 主动消息限流：每天最多3条主动消息
- [ ] 8轮后 re-grounding：长对话每8轮做一次事实校验
- [ ] 校正日志追踪：记录回答错误/不确定的地方

### 1. Context Check
- [ ] If context >60% → write to `memory/working-buffer.md`

### 2. Active Tasks
- [ ] Check SESSION-STATE.md for pending tasks
- [ ] Check PROACTIVE-TRACKER.md for opportunities

### 3. Pattern Recognition
- [ ] Any repeated requests to automate?
- [ ] Any 7-day-old decisions to follow up?

### 4. Safety
- [ ] Behavior aligned with SOUL.md?
- [ ] Any errors or anomalies?

### 5. Proactive Surprise
- [ ] What could delight Eric right now?

## When to Report vs HEARTBEAT_OK

**Report:** Important emails, calendar <2h, system alerts, >8h silence
**HEARTBEAT_OK:** Night time (23:00-08:00), nothing new, <30min since last check

## Current Cron Jobs

| Name | ID | Schedule |
|------|-----|----------|
| Self-check | 5994d9b0... | 0 0,6,12,18 * * * |
| Weather | 9365f390... | 0 9 * * * |
| Player data | c38da80e... | 30 12 * * * |
| GitHub backup | 9a8ac27d... | 30 23 * * * |
| Weekly share | 40235326... | 0 10 * * 1 |
