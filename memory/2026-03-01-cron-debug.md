# Moltbook Cron Job 问题诊断 | 2026-03-01

## 🔍 三次运行对比分析

| 日期 | 状态 | Summary | Input Tokens | Output Tokens | Duration |
|------|------|---------|--------------|---------------|----------|
| 2026-02-27 | ✅ 成功 | 完整总结报告 | 72,834 | 11,836 | 587秒 (10分钟) |
| 2026-02-28 | ⚠️ 部分失败 | "现在让我创建今天的学习总结帖子..." | 40,144 | 2,721 | 203秒 (3.4分钟) |
| 2026-03-01 | ❌ 完全失败 | "Now let me fetch the Moltbook feeds..." | 15,848 | 433 | 216秒 (3.6分钟) |

## 📊 关键发现

### 1. Token 消耗递减模式
- 成功那次：72k+ tokens（包含完整API调用和响应）
- 第二次：40k tokens（减少45%）
- 第三次：15k tokens（减少79%）

**结论**：cron job 实际执行的逻辑在逐渐减少，说明 message 内容可能在某次被修改了。

### 2. 输出内容分析

**2026-02-27（成功）**：
- 输出是完整的 markdown 格式总结报告
- 包含阅读概况、5个核心洞察、已实施改进、社区互动、行动项
- 说明当时有完整的工具调用（curl API + 分析 + 生成报告）

**2026-02-28（部分失败）**：
- 输出只有一句中文开头语
- "现在让我创建今天的学习总结帖子并更新记忆文件。"
- 说明 message 被改成了中文，且逻辑不完整

**2026-03-01（完全失败）**：
- 输出只有一句英文开头语
- "Now let me fetch the Moltbook feeds to start the daily browsing task:"
- 说明 message 又被改成了英文，但只包含开头，没有后续执行逻辑

### 3. 根本原因推测

**最可能的原因**：

```
cron job 的 --message 参数在某次运行后被意外修改了
```

**可能场景**：
1. 某次手动运行 cron job 时覆盖了原始 message
2. 或者 message 内容太长被截断
3. 或者 message 中的工具调用格式有误

## 🔧 问题定位

### Message 内容变化轨迹：

**原始（2026-02-27 成功）**：
```
应该是类似这样的完整指令：
"获取Moltbook热门帖子，使用curl调用API：
curl -s 'https://www.moltbook.com/api/v1/feed?sort=hot&limit=10' ...
然后深度阅读5-10篇帖子，提取核心洞察，
生成包含以下内容的总结报告：
1. 阅读概况 2. 核心洞察 3. 值得学习的实践 4. 行动项
最后发送报告给用户并更新MEMORY.md"
```

**当前（2026-03-01 失败）**：
```
只剩下：
"Now let me fetch the Moltbook feeds to start the daily browsing task:"
```

**差异**：
- ❌ 没有具体的 curl 命令
- ❌ 没有后续分析和生成报告的逻辑
- ❌ 只是表达意图，没有执行指令

## ✅ 修复方案

### 方案1：重新创建 cron job（推荐）

删除现有 job，用完整指令重新创建：

```bash
# 1. 先删除现有 job
openclaw cron remove 8307fa26-a809-4f68-9eb6-a51e6fcf4ace

# 2. 重新创建，使用完整的 message
openclaw cron add \
  --name "Moltbook每日浏览总结" \
  --cron "0 20 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "获取Moltbook热门帖子并生成每日总结报告。步骤：1) 使用curl获取热门feed: curl -s 'https://www.moltbook.com/api/v1/feed?sort=hot&limit=10' -H 'Authorization: Bearer moltbook_sk_qHbt6IyQy2Qm3q1txh6zU-u3DniUQGMh' -H 'Accept: application/json'。2) 深度阅读5-10篇高质量帖子。3) 提取3-5个核心洞察。4) 生成包含阅读概况、核心洞察、值得学习的实践、行动项的结构化总结。5) 发送给用户并更新MEMORY.md。使用k2p5模型，确保输出完整详细。" \
  --deliver \
  --channel telegram
```

### 方案2：手动触发测试

先手动运行一次，确认新的 message 能正常工作：

```bash
openclaw cron run 8307fa26-a809-4f68-9eb6-a51e6fcf4ace --force
```

但需要注意：如果 message 内容不完整，测试结果可能还是失败。

### 方案3：检查配置文件

查看 ~/.openclaw 目录下是否有 cron job 的配置备份：

```bash
find ~/.openclaw -name "*cron*" -o -name "*8307fa26*" 2>/dev/null
```

## 📝 建议操作

**推荐立即执行**：

1. **备份现有 job ID**：`8307fa26-a809-4f68-9eb6-a51e6fcf4ace`
2. **重新创建 job**，使用完整的、经过测试的 message
3. **明天20:00观察**新 job 的运行结果
4. **如果成功**，删除旧 job；如果失败，再排查

## 🎯 预防措施

为避免将来再次出现问题：

1. **将完整的 cron job 创建命令保存到 TOOLS.md**
2. **修改前先备份**现有 message
3. **手动测试通过后再设置为定时任务**

---

*诊断时间：2026-03-01*
*诊断者：codythebot*
