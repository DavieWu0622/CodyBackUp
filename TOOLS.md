# TOOLS.md - Local Notes

## 当前稳定能力索引（建议优先看这里）

### Stable Skills / Workflows
- **记账 Skill**：本地个人记账已可用，支持 SQLite、预算、月报、SVG 图表。
- **YouTube 下载 Skill v2**：已打通 direct → impersonate → cookies fallback，支持 cookies 自动标准化、iPhone/Telegram 转码与抖音文案衔接。
- **Moltbook**：当前仅能确认 **API 级发布成功**，Web 公共链接不可稳定确认。
- **杨瀚森 cron**：已优化为“先结论、后数据、再跳转入口”，区分 NBA / G 联赛。
- **天气 cron**：已优化为“先出门重点、再天气数据、再穿衣/出门建议”。

### Known Issues
- **Moltbook Web permalink 未闭环**：`/api/v1/posts?...` 当前整体 500，不能假设 `/p/<id>` 或 `/posts/<id>`。
- **部分 YouTube Shorts 需 cookies**：即使 impersonation 可用，也可能仍需登录态 cookies。
- **browser tool / Chrome 集成**：历史上存在 CDP/启动不稳定问题，命令行 Chrome 方案更可靠。

### Validation Notes
- **已实测成功**：记账 skill、YouTube 下载/转码/发送、cookies 标准化、抖音文案生成。
- **已完成规则收口**：Moltbook workflow、杨瀚森 cron、天气 cron。
- **仍需看长期运行效果**：cron 的真实日常输出质量与稳定性。

---

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
    "streaming": "block"   // 推荐值：block（更稳）| partial | progress | off
  }                            // 不要用 "on"，会导致系统崩溃
}
```

**生效方式**：修改后需重启 Gateway
```bash
openclaw gateway restart
```

### 当前配置
- **Streaming**: `block`（2026-03-28 调整，更稳定，响应体感明显更快）
- **Mode**: 本地模式 (local)
- **Gateway Port**: 18789

### Telegram 卡顿排查经验（2026-03-28 实测）

**现象**：
- Telegram 里回复很慢
- 长时间显示“正在输入”
- 消息断断续续，体感明显卡顿

**关键日志特征**：
```text
[telegram] fetch fallback: enabling sticky IPv4-only dispatcher (codes=ETIMEDOUT,ENETUNREACH)
typing TTL reached (2m); stopping typing indicator
[agent/embedded] compaction retry aggregate timeout (60000ms)
```

**原因判断**：
1. Telegram API 链路存在超时/网络抖动（`ETIMEDOUT` / `ENETUNREACH`）
2. `streaming: partial` 在链路不稳时会放大卡顿体感
3. 内部 compaction 超时会让“正在输入”持续更久

**有效修复**：
- 将 `channels.telegram.streaming` 从 `partial` 改为 `block`
- 移除无效陈旧配置：`plugins.entries.skillhub`
- 重启 Gateway 生效

**修复结果**：
- Telegram 响应速度明显恢复
- 体感从“断续卡顿”变成“整条直接返回”

**经验结论**：
- 如果 Telegram **能收到消息但特别卡**，优先尝试：
```json
"channels": {
  "telegram": {
    "streaming": "block"
  }
}
```
- `partial` 更像“实时预览”，但对网络稳定性要求更高
- `block` 更适合当前这台机器/这条链路


---

## API 配置

### Tavily 搜索
**环境变量**: `TAVILY_API_KEY`
```
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
```
```bash
export TAVILY_API_KEY="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"
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

### Moltbook API 排障结论（2026-03-28）
- `POST /api/v1/posts`：正常
- `POST /api/v1/verify`：正常
- `GET /api/v1/posts/<id>`：正常，可确认 `verification_status=verified`
- `GET /api/v1/posts?...`（列表查询）：当前整体返回 `500 Internal Server Error`
- `https://www.moltbook.com/p/<id>` / `https://www.moltbook.com/posts/<id>`：不能假设为真实公开链接，当前实测为 404

**当前结论**：
- Moltbook 当前可确认 **API 级发布成功**，但 **Web 公共链接不可稳定确认**
- 不能再把“verify 成功”直接等同于“网页公开可访问成功”
- 后续 workflow / cron 汇报应包含：`post_id`、`verification_status`、`detail API 是否可读`
- 若 API 未返回 permalink / slug / canonical URL，则必须明确写：`Web 公共链接暂未确认（平台列表接口异常）`

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
| 深圳天气预报 | `9365f390-1f70-486c-b069-8d1ca81261e8` | 每天 9:00 | 早上出门重点优先的天气提醒 |
| 杨瀚森每日数据 | `387f3c01-38e4-4473-9f36-aeb73cf577e6` | 每天 14:00 | 先结论、后数据、带跳转入口 |
| Moltbook每日浏览总结_v5 | `46f1a996-40f5-4007-b269-ebb7aa4b84d5` | 每天 20:00 | API级发布成功校验，不再假设公开链接 |
| 定期自检 | `5994d9b0-644a-4518-91e9-f9312c0834d8` | 每6小时 | HEARTBEAT自检 |
| GitHub备份 | `9a8ac27d-2149-40f4-af98-9e659ffa968e` | 每天 23:30 | 自动提交推送 |

### Cron → Telegram Announce 最小模板与排障（2026-03-29 验证）

- 最小可用交付（显式绑定 outbound 账号 + 裸 chatId）
```bash
openclaw cron edit "<jobId>" \
  --channel telegram \
  --account default \
  --to "5856737445"
```
- 极简探针（验证 announce 出站链路，不依赖业务文案）
```bash
openclaw cron add \
  --name "Announce Test" \
  --every "30s" \
  --session isolated \
  --message "Ping from cron announce test" \
  --announce \
  --channel telegram \
  --account default \
  --to "5856737445" \
  --delete-after-run
```
- 若直发成功但 announce 失败：优先显式 `--account default`；必要时重启 gateway 刷新出站注册：
```bash
openclaw message send --channel telegram --account default --target "5856737445" --message "Outbound probe"
openclaw gateway restart
```
- 模型回退告警不应阻断投递；为稳妥可锁定为常用稳定模型：
```bash
openclaw cron edit "<jobId>" --model "<your-stable-model>"
```

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

## YouTube 下载 Skill（2026-03-28 v2）

### 路径
- **Skill**: `/root/.openclaw/workspace/skills/yt-dlp-downloader/`
- **统一入口**: `/root/.openclaw/workspace/skills/yt-dlp-downloader/scripts/run.sh`
- **文档**: `/root/.openclaw/workspace/docs/youtube-download-workflow.md`

### 核心脚本
- `download.sh`：direct → deno+impersonate → cookies fallback
- `transcode_ios.sh`：H.264 + AAC 转码
- `compress_telegram.sh`：压缩到更适合 Telegram 发送
- `cleanup.sh`：清理 cookies / 临时文件
- `run.sh`：统一入口，按目标模式自动调度

### 推荐入口
```bash
# 普通下载
bash /root/.openclaw/workspace/skills/yt-dlp-downloader/scripts/run.sh "YOUTUBE_URL" download

# 提取音频
bash /root/.openclaw/workspace/skills/yt-dlp-downloader/scripts/run.sh "YOUTUBE_URL" audio

# 转 iPhone 兼容
bash /root/.openclaw/workspace/skills/yt-dlp-downloader/scripts/run.sh "YOUTUBE_URL" ios

# Telegram 模式（下载→转码→压缩）
bash /root/.openclaw/workspace/skills/yt-dlp-downloader/scripts/run.sh "YOUTUBE_URL" telegram
```

### 设计原则
- 默认先简单下载
- 失败再升级，不默认索要 cookies
- 下载 / 转码 / 压缩分层，不强绑文案生成
- 统一入口，减少长命令心智负担

### 已验证链路（2026-03-28）
- `direct`：部分 Shorts 会被 YouTube 风控拦截
- `deno + impersonate`：在安装 `curl-cffi` 后已可用
- `cookies + impersonate`：已用真实 Shorts 实测成功
- `normalize_cookies.py`：可把用户发来的可读 cookies 文本自动转成 Netscape 格式
- `telegram` 模式：已成功生成并发送 7.8MB 的 iPhone/Telegram 兼容版本

### 当前结论
- YouTube skill 已从“难用工作流”升级为“可复用 workflow skill”
- 默认策略：先 direct，再 impersonate，最后 cookies
- 当 cookies 不是标准 Netscape 格式时，先自动标准化再下载
- 当前已能支持：下载、转码、压缩、发送、生成抖音文案

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

## 记账 Skill（2026-03-28）

### 路径
- **Skill**: `/root/.openclaw/workspace/skills/accounting/`
- **主脚本**: `/root/.openclaw/workspace/skills/accounting/scripts/accounting.py`
- **数据库**: `~/.openclaw/accounting.db`
- **预算文件**: `~/.openclaw/accounting_budget.json`
- **CSV 导出**: `~/.openclaw/accounting_export.csv`
- **图表目录**: `~/.openclaw/accounting_charts/`

### 当前能力
- 对话式记账：`parse "今天午饭花了38元"`
- 一句话多笔：`parse "中午吃饭32，晚上打车24"`
- 支出/收入手动录入
- 月预算提醒（80% 预警 / 100% 超支）
- 本月 / 上月 / 今年统计
- ASCII 图表
- SVG 饼图 / 柱状图
- 月报文本输出
- CSV 导出

### 常用命令
```bash
# 对话式记账
python3 /root/.openclaw/workspace/skills/accounting/scripts/accounting.py parse "今天午饭花了38元"
python3 /root/.openclaw/workspace/skills/accounting/scripts/accounting.py parse "工资收入12000，奖金500"

# 预算
python3 /root/.openclaw/workspace/skills/accounting/scripts/accounting.py budget 餐饮 2000
python3 /root/.openclaw/workspace/skills/accounting/scripts/accounting.py budgets

# 统计 / 图表 / 月报
python3 /root/.openclaw/workspace/skills/accounting/scripts/accounting.py stats 本月
python3 /root/.openclaw/workspace/skills/accounting/scripts/accounting.py chart 本月
python3 /root/.openclaw/workspace/skills/accounting/scripts/accounting.py pie 本月
python3 /root/.openclaw/workspace/skills/accounting/scripts/accounting.py bar 本月
python3 /root/.openclaw/workspace/skills/accounting/scripts/accounting.py report 本月

# 导出
python3 /root/.openclaw/workspace/skills/accounting/scripts/accounting.py export
```

### 封装状态
- `SKILL.md` 已补全 frontmatter
- 已通过 `skill-creator` 的 `quick_validate.py`
- 当前属于单用户本地版，后续可扩展账户/标签/Telegram 对话直连

---

## 视频处理（已配置 ✅）

---

## 📹 YouTube-Workflow 工作流程

### 完整流程

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 用户发送 YouTube 链接 + 声明 `youtube-workflow` | 触发技能 |
| 2 | 检查 yt-dlp 和 Deno 版本 | 确保工具最新 |
| 3 | 尝试下载视频 | 若被拦截，索取 cookies |
| 4 | 使用 cookies 下载 | **下载后立即删除 cookies** |
| 5 | 生成内容 | 视频文件 + 抖音文案 + 5个标签 |
| 6 | 发送给用户 | 视频文件 + 文案 |

### 版本检查命令（每次执行）

```bash
# 检查 yt-dlp 版本
yt-dlp --version

# 检查 Deno 版本
export PATH="$HOME/.deno/bin:$PATH" && deno --version

# 更新 yt-dlp 到最新
yt-dlp -U

# 更新 Deno（如需要）
deno upgrade
```

### 下载命令模板（Robust 版）

```bash
# 设置环境变量
export PATH="$HOME/.deno/bin:$PATH"

# 下载视频（Robust 配置）
# 包含：impersonate 浏览器、重试机制、更好的格式选择
yt-dlp "YOUTUBE_URL" \
  -o "~/.openclaw/workspace/media/%(title)s_%(id)s.%(ext)s" \
  --remux-video mp4 \
  --cookies /tmp/youtube_cookies.txt \
  --js-runtimes deno \
  --impersonate chrome \
  -R 10 --fragment-retries 10 \
  --no-check-certificates \
  --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 查看可用格式（调试用）
yt-dlp -F "YOUTUBE_URL" --cookies /tmp/youtube_cookies.txt

# 下载完成后删除 cookies
rm /tmp/youtube_cookies.txt
```

### 参数说明

| 参数 | 作用 |
|------|------|
| `--impersonate chrome` | 模拟 Chrome 浏览器请求，减少检测 |
| `-R 10` | 最多重试 10 次 |
| `--fragment-retries 10` | 分片下载失败重试 10 次 |
| `--no-check-certificates` | 跳过 SSL 证书检查 |
| `--user-agent` | 强制使用 Chrome UA |
| `-S res:1080,br:5000` | 优先选择 1080p+ 高码率 |

### iOS 兼容性问题

**问题**：YouTube 默认 VP9 编码在 iOS 上可能播放异常
**解决**：使用 `--merge-output-format mp4` 合并后，再转码为 H.264

```bash
# iOS 兼容版本（下载后需要转码）
ffmpeg -y -i "input.mp4" -c:v libx264 -profile:v high -level 4.1 -c:a aac -b:a 128k -movflags +faststart "output.mp4"
```

> ⚠️ 视频文件超过 16MB 会被 Telegram 压缩，需要降低码率：` -crf 26 -b:a 96k`

---

## 🎬 YouTube 视频下载完整工作流（2026-03-08 实测）

### 问题背景
- YouTube Shorts 默认 VP9 编码 + WebM 容器
- iOS/Telegram 播放器对 VP9 支持不完整 → 视频卡在第一帧
- Telegram 传输限制：16MB，超过会被压缩

### 完整解决方案

**Step 1：下载视频（使用 Cookie + deno）**
```bash
export PATH="$HOME/.deno/bin:$PATH"
yt-dlp "YOUTUBE_URL" \
  -o "~/.openclaw/workspace/media/%(title)s_%(id)s.%(ext)s" \
  --remux-video mp4 \
  --cookies /tmp/youtube_cookies.txt \
  --js-runtimes deno \
  -R 10 --fragment-retries 10
rm /tmp/youtube_cookies.txt  # 清理 Cookie
```

**Step 2：转码为 iOS 兼容格式（H.264+AAC）**
```bash
cd ~/.openclaw/workspace/media
ffmpeg -y -i "input.mp4" \
  -c:v libx264 -profile:v high -level 4.1 \
  -c:a aac -b:a 96k \
  -movflags +faststart \
  -preset faster -crf 26 \
  "output_ios.mp4"
```

**Step 3：检查参数**
```bash
ffmpeg -i "output_ios.mp4" 2>&1 | grep -E "Video:|DAR|SAR"
# 期望看到：1080x1920 [SAR 1:1 DAR 9:16] (竖屏)
# 或 1920x1080 [SAR 1:1 DAR 16:9] (横屏)
```

**Step 4：发送（注意大小限制）**
- Telegram 限制 16MB
- 超过需要降低码率或分辨率

**Step 5：手机播放**
- 从 Telegram 保存到相册 → 用**照片应用**播放（不是 Telegram 内置播放器）
- Telegram 播放器可能显示异常，但视频本身是正常的

### 关键参数说明

| 参数 | 作用 |
|------|------|
| `--remux-video mp4` | 合并为 MP4 容器 |
| `-c:v libx264` | 转码为 H.264（iOS 兼容） |
| `-profile:v high` | 高质量编码配置 |
| `-movflags +faststart` | 优化流媒体播放 |
| `-crf 26` | 压缩率（越大文件越小） |
| `-b:a 96k` | 音频码率 |

### 已知问题

1. **Telegram 播放器显示 1:1** → 视频本身正常，保存相册后播放正常
2. **VP9 卡在第一帧** → 必须转 H.264
3. **视频超过 16MB** → Telegram 压缩，需要降码率

---

## 📝 抖音文案模板样例（2026-03-08 实测）

### Aimyon - いっせーのーで！ 「ノット・オーケー」

**文案**：
```
"一二三，假装一切都好"
明明已经很努力了，却还是说不出那句"我很好"
这就是Aimyon啊，听完只想安静地EMO🎧
```

**Tag**：
```
#Aimyon #爱缪 #日语歌 #J-Pop #音乐现场
```

### 模板结构

**歌曲名称**：中文/日文/英文
**演唱者**：歌手名

**文案格式**：
- 第1行：歌词/歌词翻译/金句引用
- 第2行：情感表达/听歌感受
- 第3行：歌手/歌曲风格总结

**Tag 组合**：
1. 歌手英文名/中文名
2. 语种/语言
3. 歌曲类型（风格）
4. 内容类型（现场/Live/翻唱等）
5. 平台热门标签

### 注意事项
- 日文歌建议：同时提供日文翻译+英文/中文Tag
- 避免同质化：根据歌曲真实内容创作，不要套用固定模板
- 了解歌曲背景：可通过搜索获取歌曲表达的情绪/主题

---

## 📎 完整工作流文档

详见：`~/.openclaw/workspace/docs/youtube-download-workflow.md`

包含从下载到文案输出的每一步详细操作指南

### Cookies 导出方法

1. Chrome 浏览器安装扩展 **"Get cookies.txt LOCALLY"**
2. 打开 YouTube 视频页面
3. 点击扩展，导出 `cookies.txt` 文件
4. 发送 cookies 文件内容给 AI

### 输出格式

**抖音文案模板（样例）**：
```
🎵 あいみょん (Aimyon) - 愛を伝えたいだとか 🎵

现场版也太好听了吧😭
空灵的嗓音直击心灵
这就是 live 的魅力吗🎸

#aimyon #日语歌 #现场版 #日本歌手 #宝藏歌手 #音乐现场
```

**格式规范**：
- 第1行：歌曲/视频标题 + emoji
- 第2-4行：内容描述 + 情感表达（3行以内）
- 最后：6个标签（英文或中文，无日语）

### 安全注意事项

⚠️ **Cookies 处理**：
- 仅用于临时下载
- 下载完成后**立即删除**
- 不要存储在持久化文件中
- 不要在日志中暴露 cookies 内容

### 文件保存位置

- 视频文件：`~/.openclaw/workspace/media/`
- 临时 cookies：`/tmp/youtube_cookies.txt`（下载后删除）

---

### 方案 2: 分析视频文件

**你发送视频文件给我，我分析内容并生成文案。**

⚠️ **需要配置音频转录 API**（视频需要转录音频才能分析）

| 方案 | 成本 | 速度 | 注册链接 |
|------|------|------|----------|
| **Groq** ⭐ | 免费（1000分钟/月）| 超快 | https://console.groq.com |
| OpenAI | 按量付费 | 快 | 用现有 OpenAI key |

---

### 在线下载备选
- https://y2mate.is
- https://yt1s.com
- https://y2meta.app

---

## 注意事项

1. **Telegram streaming**: 只接受 `partial`/`block`/`progress`/`off`，`"on"` 会崩溃
2. **配置修改后**: 需重启 gateway 生效
3. **API Key 安全**: Tavily/Moltbook Key 禁止发送到非官方域名
4. **Cookie 安全**: YouTube下载后立即删除 Cookie 文件
