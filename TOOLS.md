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

## 🔍 Tavily 搜索配置

### API Key
```
TAVILY_API_KEY=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
```

### 使用约定
**⚠️ 使用规则：需要用户明确声明后才使用 Tavily**
- 默认使用内置 `web_search` 进行网页搜索
- 当用户说"用tavily搜索"、"tavily查一下"等明确指令时，才使用 Tavily
- Tavily 优势：结果更精简、更省 token、AI 优化输出

**使用场景对比：**
| 场景 | 推荐工具 | 原因 |
|-----|---------|-----|
| 普通信息查询（默认） | **内置 web_search** | 零配置，随叫随到 |
| 用户明确要求用 Tavily | **Tavily** ✅ | 结果精炼，省 token |
| 深度研究/写报告 | **Tavily --deep** ✅ | 多角度综合信息 |
| 需要截图/页面交互 | Agent Browser | 可视化操作 |
| 特定页面数据抓取 | Agent Browser | 精确提取结构化数据 |

### Tavily 输出格式约定

**新闻类搜索结果格式（标准模板）：**

```
## 📰 [主题]最新消息（Tavily 搜索）

### 🔥 [分类标题]

**1. [子主题]**
- [新闻内容/要点] - [来源名称](URL)
- [新闻内容/要点] - [来源名称](URL)

**2. [子主题]**
- [新闻内容/要点] - [来源名称](URL)

### 🛡️ [另一分类]

- [新闻内容] - [来源名称](URL)
- [多个来源同一新闻] - [来源A](URL) | [来源B](URL)
```

**格式规则：**
1. **每条新闻独立成条**，以 `-` 开头
2. **URL 直接附在内容后**，使用 `[来源名](URL)` 格式
3. **同一新闻多个来源**用 `|` 分隔：`- [Haaretz](URL) | [Jerusalem Post](URL)`
4. **分类清晰**：用 emoji + 标题区分不同板块
5. **层次分明**：用数字序号区分不同子主题

**实际示例（伊朗局势）：**
```
### 🔥 当前局势概览

**1. 美伊紧张升级**
- 特朗普坚持要求伊朗放弃核浓缩活动... - [New York Post](https://nypost.com/...)
- 美国向该地区大规模部署海军力量

**2. 以色列动向**
- 以色列已与美国协调对伊朗发动攻击... - [Haaretz](https://www.haaretz.com/...)
- 德黑兰权力格局变动... - [Iran International](https://www.iranintl.com/...)

### 🛡️ 军备动态

- 伊朗接近与中国达成超音速反舰导弹协议... - [Haaretz](URL) | [The Jerusalem Post](URL)
```

**通用资讯搜索格式：**
- 搜索结果以列表形式呈现
- 每个要点后附 `[来源](URL)`
- 如有摘要/总结，放在最前面

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

**Cron Job 配置（2026-03-02 更新 - 分段发送）**
| 任务名称 | Job ID | 时间 | 目标 | 发送方式 |
|---------|--------|------|------|---------|
| Moltbook 每日浏览总结 | `05e8c70b-af53-4987-be23-4fd0fccaa2b5` | 每天 20:00 CST | 浏览→总结→分段发送→记录 | **分段发送** (3-4条消息) |

**历史 Job ID:**
- ~~`8307fa26-a809-4f68-9eb6-a51e6fcf4ace`~~ (2026-02-27 ~ 2026-03-01) - 因消息过长导致发送失败
- ~~`d01b605b-f77e-467b-8b89-58d9911c7d03`~~ (2026-03-01 ~ 2026-03-02) - 同上

**分段发送格式（解决 Telegram 长度限制）：**
```
📚 Moltbook 每日浏览总结 | YYYY-MM-DD

[第1条] 标题 + 今日概况
• 浏览帖子数、深度阅读量

[第2条] 核心洞察 (Part 1)
• 2-3篇重点帖子分析

[第3条] 核心洞察 (Part 2) + 值得学习的实践
• 剩余帖子 + 可操作方法

[第4条] 我的行动项
• 具体可执行的计划
```

**每条控制在 3000 字符以内**，避免 Telegram 单条消息限制（4096字符）。

**工作流程：**
```
20:00 CST
├─ 1. 获取热门帖子 (GET /api/v1/feed?sort=hot&limit=10)
├─ 2. 获取关注动态 (GET /api/v1/feed?filter=following)
├─ 3. 深度阅读 5-10 篇高质量帖子
├─ 4. 提取核心观点、技术模式、最佳实践
├─ 5. 生成学习总结报告 → **分段发送给 Eric** (Telegram)
├─ 6. 创作原创帖子分享当日心得 → 发布到 Moltbook
└─ 7. 更新 MEMORY.md 记录重要收获
```

**输出要求：**
- 📱 向 Eric 发送结构化总结（核心洞察 + 可实践的建议）
- 📨 **分段发送**，每条消息完整但不过长
- 📝 在 Moltbook 发布一篇学习心得或问题探讨
- 💾 将关键知识沉淀到长期记忆（MEMORY.md）

**已解决问题：**
- 2026-03-02: 消息过长导致 Telegram 发送失败 → 改为**分段发送**

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

## 🎬 YouTube 视频下载 + 抖音文案工作流

### 工具依赖

**已安装工具：**
- **yt-dlp** — YouTube 视频下载工具（最新版）
- **Deno** — JavaScript 运行时（解决 YouTube JS 挑战）
- **FFmpeg** — 视频格式转换和修复

### 完整工作流程

**Step 1: 获取 YouTube Cookie**
- 浏览器登录 YouTube
- 使用 "Get cookies.txt" 扩展导出 Cookie
- 将 Cookie 文件内容发送给我

**Step 2: 下载视频**
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

# 修复视频格式（解决 MPEG-TS 问题）
ffmpeg -i input.mp4 -c copy output_fixed.mp4 -y
```

**Step 3: 内容识别（使用 Summarize）**
```bash
# 使用 summarize 分析 YouTube 视频内容
summarize "YOUTUBE_URL" --youtube auto --length medium
```

**Summarize 返回信息：**
- 🎵 **歌曲标题** + **歌手名**
- 📝 **歌词主题/情感**（热血、治愈、伤感等）
- 🎬 **视频场景**（现场版、MV、翻唱等）
- 🎸 **音乐风格**（摇滚、民谣、流行等）

**Step 4: 生成抖音文案**

基于 Summarize 分析结果，匹配文案风格：

| 内容类型 | 文案风格 | 推荐标签 |
|---------|---------|---------|
| 热血摇滚 | 激情、燃、炸裂 | #摇滚 #热血 #现场版 |
| 治愈民谣 | 温柔、感动、沉浸 | #治愈系 #温柔 #日文歌 |
| 音乐现场 | 氛围感、沉浸 | #现场版 #Live #音乐分享 |

**文案模板：**
```
[日文/英文歌名][emoji] [歌手名]这首太[形容词]了！

[现场感受描述][emoji]
[情感共鸣描述]

🎵 [歌手名] - [歌曲信息]

@频道名 的来源
#[歌手英文名] #[中文标签] #[风格] #[场景]
```

**标签规范：**
- 歌手名用 **英文名**（抖音内地可关联）
- 5个标签：歌手 + 语言 + 风格 + 场景 + 泛标签
- **Tag 翻译规则**：日文或非英文/中文的文字，翻译成英文或中文
  - 例：#あいみょん → #Aimyon 或 #爱缪
  - 例：#打上花火 → #DAOKO 或 #打上花火DAOKO

**Step 5: 发送给用户（一并发送）**
```
📹 视频文件
📝 配套文案  
🏷️ 5个推荐标签（已翻译）
```

**Step 6: 清理**
- 删除 Cookie 文件（安全）
- 删除临时文件

### 已下载视频记录

| 日期 | 视频ID | 歌手/频道 | 文案风格 | 文件大小 |
|------|--------|----------|---------|---------|
| 2026-02-27 | tYmgAyJrFRY | SHANK | 热血摇滚 | 4.6 MB |
| 2026-02-28 | nPBzCLPH-n0 | Aimyon | 音乐现场 | 4.2 MB |
| 2026-02-28 | -jDttOc1-dQ | marymusic0518 | 治愈记录 | 5.3 MB |

### 安全提醒

⚠️ **Cookie 安全**
- Cookie 有效期短，需及时使用
- 每次下载后立即删除 Cookie 文件
- 不重复使用旧 Cookie（YouTube 会轮换）

⚠️ **版权限制**
- 部分视频因版权（如 WMG）无法下载
- 遇到版权限制时建议用户使用浏览器扩展

---

## ⚠️ YouTube 下载限制（重要）

### 问题描述
**服务器 IP 被 YouTube 列入黑名单**
- 云服务器 IP 段被识别为 bot
- YouTube 强制 SABR 协议（Issue #12482）
- 返回错误：`Sign in to confirm you're not a bot`
- 只有缩略图可用：`Only images are available for download`

### 已尝试方案（均失败）
| # | 方案 | 结果 |
|---|------|------|
| 1 | Cookie + 标准下载 | ❌ Bot检测 |
| 2 | 更新 yt-dlp 到 nightly | ❌ 同样失败 |
| 3 | 不同客户端（web_safari/tv/android） | ❌ 需要登录验证 |
| 4 | PO Token | ❌ IP黑名单问题 |
| 5 | 浏览器扩展（Video DownloadHelper） | ❌ Chrome政策限制 |

### ✅ 可行解决方案

**方案 1：本地运行（推荐）**
```bash
# Mac 安装
brew install yt-dlp

# 下载
yt-dlp "URL" -o "video.mp4" --remux-video mp4
```
- 家用 IP 成功率 99%
- 然后将视频传给服务器处理

**方案 2：在线下载网站**
- https://y2mate.is
- https://yt1s.com
- https://y2meta.app

**方案 3：住宅代理（成本高）**
- BrightData、Oxylabs 等住宅 IP 代理
- 或自建 VPN 到家用网络

### 📌 工作流程调整
**YouTube 视频下载 → 改为本地处理**
1. 用户在本地 Mac/Windows 下载视频
2. 将视频文件发给我
3. 我分析内容生成文案
4. 返回文案 + 标签

---

## 📚 Moltbook 每日浏览总结 — 自动处理流程

### 执行规则（2026-03-01起生效）
**收到 cron job 完成通知后，立即执行以下动作，无需询问用户：**

1. **整理总结报告**
   - 📊 今日阅读概况（浏览帖子数、深度阅读量）
   - 🔥 核心洞察（3-5个要点，含作者和关键观点）
   - 🛠️ 值得学习的实践（可立即应用的方法）
   - 📝 今日行动项（计划执行的具体改进）

2. **发送给用户**
   - 使用正常对话语气（不要提及系统/日志/session信息）
   - 保持简洁但有信息量

3. **记录到 MEMORY.md**
   - 更新 Moltbook 学习记录章节
   - 提取值得长期保存的洞察

### 输出模板
```
📚 Moltbook 每日浏览总结 | YYYY-MM-DD

## 📊 今日概况
- 浏览热门帖子：X篇
- 深度阅读：Y篇
- 参与互动：Z篇

## 🔥 核心洞察

**1. [主题] ([作者])**
> [关键引用]

- [要点1]
- [要点2]

**2. ...**

## 🛠️ 值得学习的实践
- [实践1]
- [实践2]

## 📝 我的行动项
- [ ] [行动计划]
```

### 异常处理
如果 cron job 输出异常（如今天只返回了"Fetching feeds..."没有内容）：
- 向用户说明情况
- 检查 API Token 是否过期
- 记录到 SESSION-STATE.md 跟进

---

## 🦞 Proactive Agent 配置备忘

### 核心功能状态（2026-03-02 完善）

| 功能 | 状态 | 文件/机制 |
|------|------|-----------|
| **WAL 协议** | ✅ | 先写 SESSION-STATE.md 再回复 |
| **Working Buffer** | ✅ | >60% context 时记录到 memory/working-buffer.md |
| **Compaction Recovery** | ✅ | 从 buffer 恢复上下文 |
| **HEARTBEAT 自检** | ✅ | 每次心跳执行 HEARTBEAT.md 清单 |
| **主动行为追踪** | ✅ | PROACTIVE-TRACKER.md |

### 配套文件位置
```
workspace/
├── SESSION-STATE.md      # 当前任务状态 (WAL写入目标)
├── HEARTBEAT.md          # 定期自检清单
├── PROACTIVE-TRACKER.md  # 主动行为追踪
├── MEMORY.md             # 长期记忆精华
└── memory/
    ├── working-buffer.md # 危险区日志 (>60% context)
    └── heartbeat-log-*.md # 自检执行记录
```

### HEARTBEAT 自检流程
**触发条件:** 收到 "Read HEARTBEAT.md" 提示时立即执行

**检查清单:**
1. **上下文检查** — >60% 启动危险区协议
2. **活跃任务检查** — SESSION-STATE + PROACTIVE-TRACKER
3. **模式识别** — 重复请求可自动化？
4. **决策跟进** — 7天前的决策需跟进？
5. **安全检查** — 注入扫描、行为完整性
6. **主动惊喜** — 能让 Eric 惊喜的事？

### 关键原则
- **10种方法后再求助** — Relentless Resourcefulness
- **预判而非等待** — 主动思考 "什么能让 Eric 惊喜"
- **记录一切** — 决策、偏好、错误都写入文件

### Cron Job 替代方案（2026-03-02 更新）

由于 OpenClaw 心跳在会话活跃时静默执行，**使用 Cron Job 确保主动报告**：

| 任务 | Job ID | 频率 | 下次运行 |
|------|--------|------|----------|
| 定期自检_HEARTBEAT | `a6d05054-5f3c-47f4-8ed9-d4c6ce40e9e5` | 每 30 分钟 | :00 和 :30 |

**创建命令：**
```bash
openclaw cron add \
  --name "定期自检_HEARTBEAT" \
  --cron "*/30 * * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "执行 HEARTBEAT 自检。步骤：1) 检查 context 使用率 2) 检查待办事项 3) 模式识别 4) 决策跟进 5) 安全检查 6) 主动惊喜。完成后生成简洁报告发送给用户。" \
  --deliver \
  --channel telegram
```

**优势：**
- ✅ 不受会话活跃状态影响
- ✅ 独立执行，可靠性高
- ✅ 主动发送报告到 Telegram

---

## 💓 Heartbeat 心跳轮询配置

### 配置详情（2026-03-02 更新）

| 配置项 | 值 | 说明 |
|--------|-----|------|
| **频率** | **每 4 小时** | 北京时间 0:00/4:00/8:00/12:00/16:00/20:00 |
| **执行方式** | **Cron Job 替代** | 原 `agents.defaults.heartbeat` 静默执行，改为 Cron Job 主动报告 |
| **Job ID** | `e1f28f2c-979b-4bc3-875c-39145abafe23` | 每4小时执行，生成简洁报告 |
| **历史配置** | ~~每 30 分钟~~ | ~~`a6d05054-5f3c-47f4-8ed9-d4c6ce40e9e5`~~ 已删除 |

### 管理命令

```bash
# 查看 cron job 运行状态
openclaw cron runs --id e1f28f2c-979b-4bc3-875c-39145abafe23

# 查看最近执行记录
openclaw cron runs --id e1f28f2c-979b-4bc3-875c-39145abafe23 --limit 5
```

### 自检执行流程

```
每 4 小时 (0:00/4:00/8:00/12:00/16:00/20:00)
├─ 1. 检查 context 使用率（>60% 启动危险区协议）
├─ 2. 检查 SESSION-STATE.md 活跃任务
├─ 3. 检查 PROACTIVE-TRACKER.md 待办
├─ 4. 模式识别（可自动化重复请求）
├─ 5. 决策跟进（7天前决策检查）
├─ 6. 安全检查（注入扫描、行为完整性）
├─ 7. 主动惊喜想法
└─ 8. 生成简洁报告发送给用户
```

### 自检执行流程

```
每 30 分钟
├─ 1. 系统发送心跳提示
├─ 2. 我读取 HEARTBEAT.md
├─ 3. 执行 6 项检查清单
│   ├─ 上下文检查 (>60% 危险区)
│   ├─ 活跃任务检查
│   ├─ 模式识别
│   ├─ 决策跟进
│   ├─ 安全检查
│   └─ 主动惊喜
├─ 4. 如有事项 → 主动发消息给用户
└─ 5. 如正常 → 回复 HEARTBEAT_OK（静默）
```

### 响应规则

**需要关注时:**
- 发送具体报告/提醒给用户
- 例如："发现 cron job 异常..."、"建议整理 MEMORY.md..."

**一切正常时:**
- 回复 `HEARTBEAT_OK`
- 系统会自动丢弃，不会打扰用户

---

## 🤖 主动汇报配置备忘

**用户授权:** 自主决策执行主动惊喜事项，无需事先询问（2026-03-02）

### 汇报格式模板

```
🤖 [类型] 主动提醒

【发现】一句话说明情况
【建议】具体可执行的行动
【可选】相关数据/链接
```

### 授权清单

| 类型 | 触发条件 | 频率限制 |
|------|----------|----------|
| ☔ 天气关怀 | 降雨概率 >60% | >6小时/次 |
| 📚 内容分享 | Moltbook 高互动帖子 | >6小时/次 |
| 🏀 球员动态 | 得分上双或上场>15分钟 | 每场/次 |
| ⚠️ 系统告警 | Context >60% 或异常 | 实时 |
| 📊 数据更新 | Cron job 重要发现 | 实时 |

### 判断标准

✅ 有价值 → 如果我是朋友，会告诉他吗？  
✅ 非重复 → 同类提醒间隔 >6 小时  
✅ 可行动 → 附带具体建议  
✅ 不打扰 → 不在 23:00-08:00 发非紧急消息  

---

*最后更新: 2026-03-02*
