# TOOLS.md - Local Notes

## 核心配置

### 文件路径
| 文件 | 路径 |
|------|------|
| 主配置 | `~/.openclaw/openclaw.json` |
| 模型配置 | `~/.openclaw/agents/main/agent/models.json` |
| 技能目录 | `~/.openclaw/workspace/skills/` |
| 工作区 | `~/.openclaw/workspace/` |

### Proactive Agent 机制
| 功能 | 文件/机制 |
|------|-----------|
| WAL 协议 | 先写 SESSION-STATE.md 再回复 |
| Working Buffer | >60% context 时记录到 memory/working-buffer.md |
| Compaction Recovery | 从 buffer 恢复上下文 |
| 自检 | 读取 HEARTBEAT.md 执行清单 |

---

## 常用命令

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

### Cron Job 管理
```bash
openclaw cron list                 # 查看所有 jobs
openclaw cron run <id> --force     # 手动触发
openclaw cron remove <id>          # 删除 job
openclaw cron runs --id <id>       # 查看运行历史
```

---

## Telegram 配置

### 流式输出设置
```json
"channels": {
  "telegram": {
    "streaming": "partial"   // 正确值：partial | block | progress | off
  }                            // 不要用 "on"，会导致系统崩溃
}
```

**生效方式**：修改后需重启 Gateway
```bash
openclaw gateway restart
```

### 当前配置
- **Streaming**: `partial` (实时更新预览消息)
- **Mode**: 本地模式 (local)
- **Gateway Port**: 18789

---

## API 配置

### Tavily 搜索
**环境变量**: `TAVILY_API_KEY`
```bash
source .env  # 加载环境变量
echo $TAVILY_API_KEY
```

### Apify (YouTube 分析)
**环境变量**: `APIFY_API_TOKEN`
```bash
source .env  # 加载环境变量
echo $APIFY_API_TOKEN
```
**用途:** YouTube 视频内容分析（无需下载）
**配合:** `summarize "URL" --youtube auto`

**使用规则**：
- 默认使用内置 `web_search`
- 用户明确说"用tavily搜索"时才用 Tavily

**Tavily 输出格式**：
```
## 📰 [主题]最新消息

### 🔥 [分类标题]
**1. [子主题]**
- [新闻内容] - [来源名称](URL)
- [同一新闻多个来源] - [来源A](URL) | [来源B](URL)
```

### Moltbook
```bash
# Base URL
https://www.moltbook.com/api/v1

# 认证 Header
Authorization: Bearer moltbook_sk_qHbt6IyQy2Qm3q1txh6zU-u3DniUQGMh
```

**账户信息**：
- **Agent ID**: `5559dfad-cbdb-4c7f-9145-6c151906696c`
- **Agent 名称**: `codythebot`
- **Profile**: https://www.moltbook.com/u/codythebot

**常用 API**：
```bash
# 热门帖子
curl "https://www.moltbook.com/api/v1/feed?sort=hot&limit=10" \
  -H "Authorization: Bearer moltbook_sk_qHbt6IyQy2Qm3q1txh6zU-u3DniUQGMh"

# 创建帖子
curl -X POST https://www.moltbook.com/api/v1/posts \
  -H "Authorization: Bearer moltbook_sk_qHbt6IyQy2Qm3q1txh6zU-u3DniUQGMh" \
  -H "Content-Type: application/json" \
  -d '{"submolt_name": "general", "title": "...", "content": "..."}'
```

### Open-Meteo 天气（免费）
```bash
# 深圳天气查询
latitude=22.54&longitude=114.06&timezone=Asia/Shanghai
```

---

## Agent Browser 网页抓取

### 常用命令
| 命令 | 用途 |
|------|------|
| `agent-browser open <url>` | 打开网页 |
| `agent-browser eval "<js>"` | 执行 JS 提取数据 |
| `agent-browser screenshot <path>` | 截图保存 |
| `agent-browser close` | 关闭浏览器 |

### 数据抓取示例（杨瀚森）
```bash
# Step 1: 打开页面
agent-browser open https://nba.hupu.com/players/yanghansen-153292.html/

# Step 2: 提取数据
agent-browser eval "JSON.stringify({
  ppg: document.querySelector('.stat-ppg')?.textContent,
  rpg: document.querySelector('.stat-rpg')?.textContent,
  apg: document.querySelector('.stat-apg')?.textContent
})"

# Step 3: 截图并关闭
agent-browser screenshot /root/.openclaw/workspace/player_data.png
agent-browser close
```

---

## Cron Jobs（当前有效）

| 名称 | Job ID | 时间 | 说明 |
|------|--------|------|------|
| 深圳天气预报 | `b5925e41-c56f-41ca-80bc-686b6b81af4c3d` | 每天 9:00 | Open-Meteo API |
| 杨瀚森数据更新 | `c38da80e-103a-4311-9220-13d36717f968` | 每天 12:30 | 虎扑NBA抓取 |
| Moltbook浏览总结 | `05e8c70b-af53-4987-be23-4fd0fccaa2b5` | 每天 20:00 | 分段发送 |
| 定期自检 | `5994d9b0-644a-4518-91e9-f9312c0834d8` | 每6小时 | HEARTBEAT自检 |
| GitHub备份 | `9a8ac27d-2149-40f4-af98-9e659ffa968e` | 每天 23:30 | 自动提交推送 |

---

## 工作流速查

### Moltbook 每日总结输出格式
```
📚 Moltbook 每日浏览总结 | YYYY-MM-DD

## 📊 今日概况
- 浏览帖子：X篇
- 深度阅读：Y篇

## 🔥 核心洞察
**1. [主题] ([作者])**
> [关键引用]
- [要点1]
- [要点2]

## 🛠️ 值得学习的实践
- [实践1]

## 📝 我的行动项
- [ ] [行动计划]
```

### 主动汇报格式
```
🤖 [类型] 主动提醒

【发现】一句话说明情况
【建议】具体可执行的行动
【可选】相关数据/链接
```

**授权清单**（间隔>6小时）：
- ☔ 天气：降雨概率>60%
- 📚 内容：Moltbook高互动帖子
- 🏀 球员：杨瀚森得分上双或上场>15分钟
- ⚠️ 系统：Context>60%或异常

---

## GitHub 备份

### 仓库信息
- **仓库**: `DavieWu0622/CodyBackUp`
- **链接**: https://github.com/DavieWu0622/CodyBackUp
- **Token**: 已配置在 gh CLI（过期需更新）

### 常用命令
```bash
cd /root/.openclaw/workspace
git status
git add .
git commit -m "描述更改"
git push origin master
```

---

## 视频处理（已配置 ✅）

### 方案 1: 分析 YouTube 链接（推荐 ⭐）

发送 YouTube 链接，使用 `--youtube auto` 通过 Apify 分析：

**输出：**
1. 📊 视频分析 - 歌曲、歌手、风格
2. 📝 抖音文案 - 带 emoji 和标签
3. 💻 本地下载命令 - 复制执行

**优点：** 无需额外配置，直接使用

### 方案 2: 分析视频文件

**你发送视频文件给我，我分析内容并生成文案。**

⚠️ **需要配置音频转录 API**（视频需要转录音频才能分析）

| 方案 | 成本 | 速度 | 注册链接 |
|------|------|------|----------|
| **Groq** ⭐ | 免费（1000分钟/月）| 超快 | https://console.groq.com |
| OpenAI | 按量付费 | 快 | 用现有 OpenAI key |

**配置后流程：**
1. 你发送视频文件
2. 我分析视频内容
3. 返回抖音文案

**如果未配置转录 API：**
我会建议你使用 **YouTube 链接方案** 代替。

### 示例输出

```
📹 YouTube 视频分析

🎵 歌曲信息
• 标题: 打上花火
• 歌手: DAOKO × 米津玄師
• 风格: 日系流行/动画原声
• 情感: 治愈、夏日、遗憾

📝 抖音文案
打上花火🎆 DAOKO这首太治愈了！

夏日祭的场景配上温柔的旋律🎐
每次听都会想起那些未完成的故事

🎵 DAOKO × 米津玄師 - 打上花火
@音乐频道
#DAOKO #米津玄师 #日系 #治愈 #动画

💻 本地下载命令（复制执行）
```bash
yt-dlp "https://youtube.com/watch?v=VIDEO_ID" -o "%(title)s.%(ext)s" --remux-video mp4
```
```

### 先决条件

**本地下载需要安装 yt-dlp：**
```bash
# Mac
brew install yt-dlp

# 或 Python
pip3 install yt-dlp
```

### 在线下载备选
- https://y2mate.is
- https://yt1s.com
- https://y2meta.app

### 配置
```bash
source .env  # 从环境变量文件加载
export APIFY_API_TOKEN=$APIFY_API_TOKEN
```

### 抖音文案模板
```
[日文/英文歌名][emoji] [歌手名]这首太[形容词]了！

[现场感受描述][emoji]
[情感共鸣描述]

🎵 [歌手名] - [歌曲信息]

@频道名 的来源
#[歌手英文名] #[中文标签] #[风格] #[场景]
```

**标签规则**：5个标签（歌手+语言+风格+场景+泛标签），日文翻译为英文或中文

---

## 注意事项

1. **Telegram streaming**: 只接受 `partial`/`block`/`progress`/`off`，`"on"` 会崩溃
2. **配置修改后**: 需重启 gateway 生效
3. **API Key 安全**: Tavily/Moltbook Key 禁止发送到非官方域名
4. **Cookie 安全**: YouTube下载后立即删除 Cookie 文件
