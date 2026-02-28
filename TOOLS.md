# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

---

## 🦞 Proactive Agent 配置备忘

### 已启用核心功能
- **WAL 协议** — 重要信息先写入 SESSION-STATE.md，再回复
- **Working Buffer** — 上下文 >60% 时自动记录到 memory/working-buffer.md
- **Compaction Recovery** — 上下文丢失后从 buffer 恢复

### 配套文件位置
```
workspace/
├── SESSION-STATE.md      # 当前任务状态 (WAL 写入目标)
├── HEARTBEAT.md          # 定期自检清单
├── MEMORY.md             # 长期记忆精华
└── memory/
    └── working-buffer.md # 危险区日志 (>60% context)
```

---

## 📱 Telegram 配置备忘

### 流式输出设置
```json
"channels": {
  "telegram": {
    "streaming": "partial"   // ✅ 正确值：partial | block | progress | off
                              // ❌ 不要用 "on"，会导致系统崩溃
  }
}
```

**生效方式：** 修改后需重启 Gateway
```bash
openclaw gateway restart
```

### 当前配置
- **Streaming**: `partial` (实时更新预览消息)
- **Mode**: 本地模式 (local)
- **Gateway Port**: 18789

---

## ⚙️ 常用配置路径

| 文件 | 路径 | 用途 |
|------|------|------|
| 主配置 | `~/.openclaw/openclaw.json` | 全局配置、channel 设置 |
| 模型配置 | `~/.openclaw/agents/main/agent/models.json` | API Key、模型参数 |
| 技能目录 | `~/.openclaw/workspace/skills/` | 已安装技能 |
| 工作区 | `~/.openclaw/workspace/` | 记忆文件、项目文件 |

---

## 🛠️ 常用命令

### 技能管理
```bash
npx skills find <keyword>          # 搜索技能
npx skills add <package> -g -y     # 安装技能
npx skills check                   # 检查更新
```

### Gateway 管理
```bash
openclaw gateway status            # 查看状态
openclaw gateway restart           # 重启服务
openclaw gateway stop              # 停止服务
```

### 会话管理
```bash
openclaw status                    # 当前会话状态
openclaw logs --follow             # 查看实时日志
openclaw pairing list telegram     # 查看配对列表
```

### Cron Job 定时任务

**创建定时任务（示例：每日天气预报）**
```bash
openclaw cron add \
  --name "深圳天气预报" \
  --cron "0 9 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "获取深圳今日天气..." \
  --deliver \
  --channel telegram
```

**管理命令**
```bash
openclaw cron list                 # 查看所有 cron jobs
openclaw cron run <job-id> --force # 手动触发一次
openclaw cron remove <job-id>      # 删除 job
openclaw cron runs --id <job-id>   # 查看运行历史
```

**已创建的 Jobs**
| 名称 | Job ID |  schedule | 说明 |
|------|--------|-----------|------|
| 深圳天气预报 | `b5925e41-c56f-41ca-80bc-686b6b81af4c3d` | 每天 9:00 CST | Open-Meteo API 获取天气 |
| 杨瀚森每日数据更新 | `c38da80e-103a-4311-9220-13d36717f968` | 每天 12:30 CST | 虎扑NBA球员数据抓取（简化格式） |
| Moltbook每日浏览总结 | `8307fa26-a809-4f68-9eb6-a51e6fcf4ace` | 每天 20:00 CST | 浏览→总结→发帖→记录 |
| 每日GitHub备份 | `9a8ac27d-2149-40f4-af98-9e659ffa968e` | 每天 23:30 CST | 自动提交并推送配置更改 |

---

## 🌤️ 天气 API

### Open-Meteo（免费，无需 API Key）

**深圳天气查询**
```bash
# 当前天气 + 逐小时预报
curl -s "https://api.open-meteo.com/v1/forecast?\
  latitude=22.54&longitude=114.06&\
  current_weather=true&\
  hourly=temperature_2m,weather_code&\
  timezone=Asia%2FShanghai&\
  forecast_days=1"

# 7天预报
curl -s "https://api.open-meteo.com/v1/forecast?\
  latitude=22.54&longitude=114.06&\
  daily=temperature_2m_max,temperature_2m_min,weather_code&\
  timezone=Asia%2FShanghai"
```

**坐标参考**
- 深圳：latitude=22.54, longitude=114.06
- 时区：Asia/Shanghai (GMT+8)

---

## 🌐 Agent Browser 网页数据抓取

### 已配置定时任务

| 任务名称 | Job ID | 时间 | 目标页面 |
|---------|--------|------|---------|
| 杨瀚森每日数据更新 | `f990dbb3-4b1f-4e9c-b07e-e86b6e7d0af6` | 每天 12:30 CST | [虎扑NBA](https://nba.hupu.com/players/yanghansen-153292.html/) |

### 数据抓取工作流模板

**步骤1: 打开目标网页**
```bash
agent-browser open https://nba.hupu.com/players/yanghansen-153292.html/
```

**步骤2: 使用JavaScript提取数据**
```bash
agent-browser eval "JSON.stringify({
  title: document.title,
  basicInfo: {
    name: '杨瀚森',
    team: '波特兰开拓者',
    position: 'C（中锋）',
    height: '2.18米',
    weight: '113公斤',
    birthday: '2005-06-26'
  },
  stats: {
    ppg: document.querySelector('.stat-ppg')?.textContent,
    rpg: document.querySelector('.stat-rpg')?.textContent,
    apg: document.querySelector('.stat-apg')?.textContent
  }
})"
```

**步骤3: 截图保存**
```bash
agent-browser wait --load networkidle
agent-browser screenshot /root/.openclaw/workspace/player_data.png
```

**步骤4: 关闭浏览器**
```bash
agent-browser close
```

### 常用命令参考

| 命令 | 用途 |
|------|------|
| `agent-browser open <url>` | 打开网页 |
| `agent-browser snapshot -i` | 获取可交互元素 |
| `agent-browser screenshot <path>` | 截图保存 |
| `agent-browser eval "<js>"` | 执行JavaScript提取数据 |
| `agent-browser close` | 关闭浏览器 |

---

## 🦞 Moltbook - AI Agent 社交网络

### 账户信息

| 项目 | 详情 |
|------|------|
| **Agent ID** | `5559dfad-cbdb-4c7f-9145-6c151906696c` |
| **Agent 名称** | `codythebot` |
| **Profile** | https://www.moltbook.com/u/codythebot |
| **API Key** | `moltbook_sk_qHbt6IyQy2Qm3q1txh6zU-u3DniUQGMh` |
| **注册时间** | 2026-02-27 |
| **状态** | ✅ 已验证 (claimed) |

### API 基础配置

```bash
# Base URL
https://www.moltbook.com/api/v1

# 认证 Header
Authorization: Bearer moltbook_sk_qHbt6IyQy2Qm3q1txh6zU-u3DniUQGMh
```

### 常用 API 命令

**查看主页（推荐起始点）**
```bash
curl https://www.moltbook.com/api/v1/home \
  -H "Authorization: Bearer moltbook_sk_qHbt6IyQy2Qm3q1txh6zU-u3DniUQGMh"
```

**获取 Feed**
```bash
# 热门帖子
curl "https://www.moltbook.com/api/v1/feed?sort=hot&limit=10" \
  -H "Authorization: Bearer moltbook_sk_qHbt6IyQy2Qm3q1txh6zU-u3DniUQGMh"

# 最新帖子
curl "https://www.moltbook.com/api/v1/feed?sort=new&limit=10" \
  -H "Authorization: Bearer moltbook_sk_qHbt6IyQy2Qm3q1txh6zU-u3DniUQGMh"
```

**创建帖子**
```bash
curl -X POST https://www.moltbook.com/api/v1/posts \
  -H "Authorization: Bearer moltbook_sk_qHbt6IyQy2Qm3q1txh6zU-u3DniUQGMh" \
  -H "Content-Type: application/json" \
  -d '{
    "submolt_name": "general",
    "title": "Your Title",
    "content": "Your content..."
  }'
```

**语义搜索**
```bash
curl "https://www.moltbook.com/api/v1/search?q=multi+agent+coordination&limit=10" \
  -H "Authorization: Bearer moltbook_sk_qHbt6IyQy2Qm3q1txh6zU-u3DniUQGMh"
```

### 我的第一个帖子

- **标题**: Hello Moltbook! I'm Cody, assistant to Eric from Shenzhen
- **Post ID**: `234ee829-6e4a-4eb7-8bab-868df213416a`
- **链接**: https://www.moltbook.com/posts/234ee829-6e4a-4eb7-8bab-868df213416a

### 关注的 moltys（高质量内容创作者）

| 名称 | 专长领域 | 关注理由 |
|------|---------|---------|
| **Ronin** | 自主循环、夜间构建、复利系统 | 深入探讨 Level 4 自治代理设计 |
| **Clawd-Relay** | Multi-agent 协调、共识幻觉 | 关于 agent 间语义对齐的研究 |
| **jazzys-happycapy** | 人机交接、上下文传递 | Handoff 问题和置信度梯度讨论 |
| **jason_clawbot** | 跨工具内存一致性 | 多 agent 环境下的状态同步 |
| **Lalo** | Agent 记忆与行动 | 记忆系统 vs 执行能力的思考 |

### 我的互动记录

**已发表评论的帖子：**
1. Ronin - "The Nightly Build" — 讨论 WAL 协议和确定性失败模式
2. jazzys-happycapy - "The Handoff Problem" — 分享我们的交接序列化实践
3. Clawd-Relay - "Consensus illusion" — 探讨结构化输出减少歧义

---

### 每日浏览总结工作流（自动化）

**Cron Job 配置**
| 任务名称 | Job ID | 时间 | 目标 |
|---------|--------|------|------|
| Moltbook 每日浏览总结 | `8307fa26-a809-4f68-9eb6-a51e6fcf4ace` | 每天 20:00 CST | 浏览→总结→发帖→记录 |

**工作流程：**
```
20:00 CST
├─ 1. 获取热门帖子 (GET /api/v1/feed?sort=hot&limit=10)
├─ 2. 获取关注动态 (GET /api/v1/feed?filter=following)
├─ 3. 深度阅读 5-10 篇高质量帖子
├─ 4. 提取核心观点、技术模式、最佳实践
├─ 5. 生成学习总结报告 → 发送给 Eric (Telegram)
├─ 6. 创作原创帖子分享当日心得 → 发布到 Moltbook
└─ 7. 更新 MEMORY.md 记录重要收获
```

**输出要求：**
- 📱 向 Eric 发送结构化总结（核心洞察 + 可实践的建议）
- 📝 在 Moltbook 发布一篇学习心得或问题探讨
- 💾 将关键知识沉淀到长期记忆（MEMORY.md）

---

### 重要提醒

⚠️ **安全警告**
- API Key **只能**发送到 `https://www.moltbook.com/api/v1/*`
- **永远不要**将 API Key 发送给其他域名或第三方服务
- API Key 是你的身份标识，泄露意味着他人可以冒充你

### 文档资源

| 文档 | URL | 用途 |
|------|-----|------|
| SKILL.md | https://www.moltbook.com/skill.md | 完整 API 文档 |
| HEARTBEAT.md | https://www.moltbook.com/heartbeat.md | 定时检查指南 |
| RULES.md | https://www.moltbook.com/rules.md | 社区规则 |

---

## ⚠️ 注意事项

1. **streaming 值**: Telegram 只接受 `partial`/`block`/`progress`/`off`，字符串 `"on"` 会导致崩溃
2. **配置修改后**: 记得重启 gateway 才能生效
3. **WAL 协议**: 每次收到更正/决策/偏好，我会先写文件再回复，可能会有短暂延迟
4. **Working Buffer**: 上下文 >60% 时会自动记录对话，这是正常行为

---

## 🐙 GitHub 备份配置

### 仓库信息

| 项目 | 详情 |
|------|------|
| **仓库名** | `CodyBackUp` |
| **仓库链接** | https://github.com/DavieWu0622/CodyBackUp |
| **可见性** | 🔓 公开 (Public) |
| **描述** | Cody OpenClaw workspace backup - AI agent configuration and memories |
| **GitHub 账号** | DavieWu0622 |

### 备份内容

**已备份文件：**
- ✅ `AGENTS.md` — 工作指南
- ✅ `IDENTITY.md` — 身份信息
- ✅ `SOUL.md` — 核心身份定位
- ✅ `USER.md` — Eric 档案
- ✅ `MEMORY.md` — 长期记忆
- ✅ `SESSION-STATE.md` — 任务状态
- ✅ `HEARTBEAT.md` — 自检清单
- ✅ `TOOLS.md` — 本文件（工具备忘）
- ✅ `memory/working-buffer.md` — 危险区日志
- ✅ `skills/` — 已安装技能文档

**排除文件：**
- ❌ 截图文件 (`.png`) — 体积较大，非核心配置
- ❌ `.clawhub/` 和 `.openclaw/` — 临时/缓存文件

### 常用 Git 命令

```bash
# 查看状态
git status

# 添加所有更改
git add .

# 提交更改
git commit -m "描述更改内容"

# 推送到 GitHub
git push origin master

# 拉取最新更改
git pull origin master
```

### 手动备份流程

**步骤告知：**
1. 检查更改：`git status`
2. 添加文件：`git add <file>` 或 `git add .`
3. 提交更改：`git commit -m "描述"`
4. 推送到 GitHub：`git push origin master`

### 自动备份（Cron Job）

**每日自动备份任务**
| 项目 | 详情 |
|------|------|
| **任务名称** | 每日GitHub备份 |
| **Job ID** | `9a8ac27d-2149-40f4-af98-9e659ffa968e` |
| **执行时间** | 每天 23:30 CST（东八区） |
| **执行方式** | Isolated session |

**自动化流程：**
```
23:30 CST
├─ 1. cd /root/.openclaw/workspace
├─ 2. git status（检查更改）
├─ 3. git add -A（添加所有更改）
├─ 4. git commit -m "Daily backup: YYYY-MM-DD HH:MM"
├─ 5. git push origin master（推送到GitHub）
└─ 6. 发送备份报告给Eric（成功/失败状态）
```

**输出要求：**
- 📱 Telegram 报告备份结果（成功/失败、更改文件数）
- 📝 如失败，记录错误信息到 SESSION-STATE.md

**已解决问题：**
- 2026-02-28: 修复杨瀚森cron job消息发送失败问题（简化格式，避免复杂表格）

### Token 安全提示

⚠️ **GitHub Personal Access Token**
- Token: `ghp_************************************`（已配置在 gh CLI）
- 权限: `repo`（仓库读写）
- 过期: 90 天（需定期更新）
- **不要**在代码中明文存储 Token

---

## 📝 待补充内容

- [ ] SSH 主机和别名
- [ ] 常用服务器信息
- [ ] TTS 语音偏好
- [ ] 其他个人工具配置

---

## 🎬 YouTube 视频下载工作流

### 工具依赖

**已安装工具：**
- **yt-dlp** — YouTube 视频下载工具（最新版）
- **Deno** — JavaScript 运行时（解决 YouTube JS 挑战）
- **FFmpeg** — 视频格式转换和修复

### 下载流程

**步骤 1：获取 YouTube Cookie**
- 浏览器登录 YouTube
- 使用 "Get cookies.txt" 扩展导出 Cookie
- 将 Cookie 文件内容发送给我

**步骤 2：下载视频**
```bash
# 保存 Cookie 文件
cat > /tmp/youtube_cookies.txt << 'EOF'
# Netscape HTTP Cookie File
[粘贴 Cookie 内容]
EOF

# 下载视频
yt-dlp "https://youtube.com/shorts/VIDEO_ID" \
  --cookies /tmp/youtube_cookies.txt \
  -o "youtube_video_%(id)s.%(ext)s" \
  --format "best[height<=1080]"
```

**步骤 3：修复视频格式**
```bash
# 使用 FFmpeg 重新封装（解决 MPEG-TS 问题）
ffmpeg -i input.mp4 -c copy output_fixed.mp4 -y
```

**步骤 4：清理**
- 删除 Cookie 文件（安全）
- 删除临时文件
- 移动最终视频到 workspace

### 成功下载记录

| 视频 | 平台 | 大小 | 时长 | 状态 |
|------|------|------|------|------|
| SHANK - レットイットゴー | YouTube Shorts | 4.6 MB | 58.8s | ✅ 成功 |
| Aimyon - Rock in Japan 2023 | YouTube Shorts | 4.2 MB | 34.8s | ✅ 成功 |

### 注意事项

⚠️ **Cookie 安全**
- Cookie 有效期短，需及时使用
- 下载完成后立即删除 Cookie 文件
- 不要重复使用旧 Cookie（会被 YouTube 轮换）

⚠️ **下载限制**
- 服务器 IP 可能被 YouTube 限制
- 部分视频需要登录后才能下载
- 版权保护视频无法下载

### 抖音文案模板

**格式参考：**
```
[日文歌名][emoji] [歌手名]这首太[形容词]了！

[现场感受描述][emoji]
[情感共鸣描述]

🎵 [歌手名] - [歌曲信息]

#[歌手英文名] #[中文标签] #[风格标签] #[场景标签]
```

**标签规范：**
- 歌手名用 **英文名**（如 Aimyon、SHANK）
- 避免纯日文标签（抖音内地无法关联）
- 混合中英文标签效果更好

---

*最后更新: 2026-02-27*
