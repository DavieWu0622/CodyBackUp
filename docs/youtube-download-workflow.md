# YouTube 视频下载 → 抖音文案 完整工作流

**日期**：2026-03-08  
**实测视频**：https://youtube.com/shorts/KZOECjxaCaA

---

## 📋 完整流程概览

| 步骤 | 操作 | 工具/命令 |
|------|------|-----------|
| 1 | 用户发送 YouTube 链接 | Telegram |
| 2 | 用户提供 Cookie（首次/失效时） | Chrome 扩展导出 |
| 3 | 下载视频（VP9+Opus） | yt-dlp + deno |
| 4 | 转码为 iOS 兼容格式 | ffmpeg (H.264+AAC) |
| 5 | 压缩体积（可选） | ffmpeg (-crf 26) |
| 6 | 发送视频给用户 | Telegram |
| 7 | 用户保存相册播放 | 手机照片应用 |
| 8 | 生成抖音文案 | AI 生成 |
| 9 | 清理临时文件 | rm |

---

## 🔧 详细步骤

### Step 1：Cookie 准备

**场景**：YouTube 下载被拦截，需要登录态

**操作**：
1. Chrome 浏览器安装扩展 "Get cookies.txt LOCALLY"
2. 打开 YouTube 视频页面
3. 点击扩展 → 导出 cookies.txt
4. 发送文件给 AI

**保存位置**：`/tmp/youtube_cookies.txt`（用完即删）

---

### Step 2：下载视频

```bash
export PATH="$HOME/.deno/bin:$PATH"

yt-dlp "YOUTUBE_URL" \
  -o "~/.openclaw/workspace/media/%(title)s_%(id)s.%(ext)s" \
  --remux-video mp4 \
  --cookies /tmp/youtube_cookies.txt \
  --js-runtimes deno \
  -R 10 --fragment-retries 10 \
  --no-check-certificates
```

**关键点**：
- `--remux-video mp4`：合并为 MP4 容器
- `--js-runtimes deno`：解决 YouTube JS 挑战
- `-R 10`：网络错误重试 10 次

---

### Step 3：iOS 兼容转码

**问题**：VP9 编码在 iOS 上可能卡顿/无声

```bash
cd ~/.openclaw/workspace/media

ffmpeg -y -i "input.mp4" \
  -c:v libx264 -profile:v high -level 4.1 \
  -c:a aac -b:a 96k \
  -movflags +faststart \
  -preset faster -crf 26 \
  "output_ios.mp4"
```

**参数说明**：
| 参数 | 作用 |
|------|------|
| `-c:v libx264` | H.264 编码（iOS 兼容） |
| `-profile:v high` | 高质量配置 |
| `-movflags +faststart` | 优化流媒体播放 |
| `-crf 26` | 压缩率（26 ≈ 较小体积） |
| `-b:a 96k` | 音频码率 |

---

### Step 4：发送视频

**Telegram 限制**：16MB

```bash
# 检查文件大小
ls -lh output_ios.mp4

# 超过 16MB 需要进一步压缩
ffmpeg -y -i "output_ios.mp4" -c:v libx264 -crf 28 -c:a aac -b:a 64k "final.mp4"
```

**发送**：
```bash
openclaw message send --channel telegram --target 5856737445 --media "final.mp4"
```

**重要**：视频在 Telegram 播放器显示异常是正常的，保存到相册后用照片应用播放即可

---

### Step 5：生成抖音文案

**基于视频内容生成**，避免同质化

**模板结构**：
```
【歌曲名称】中文 / 日文 / 英文
【演唱者】歌手名

【文案】
第1行：歌词/金句/情感触发
第2行：听后感/情绪表达
第3行：歌手/风格总结

【Tag】
#歌手名 #语种 #风格 #内容类型 #平台热门
```

**实测案例**：
```
🎵 歌曲：いっせーのーで！ 「ノット・オーケー」(一二三！Not Okay)
🎤 演唱：あいみょん (Aimyon)

"一二三，假装一切都好"
明明已经很努力了，却还是说不出那句"我很好"
这就是Aimyon啊，听完只想安静地EMO🎧

#Aimyon #爱缪 #日语歌 #J-Pop #音乐现场
```

---

### Step 6：清理

```bash
# 删除 Cookie
rm -f /tmp/youtube_cookies.txt

# 删除临时视频（可选）
rm -f ~/.openclaw/workspace/media/*.mp4
```

---

## ⚠️ 已知问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 下载被拦截 | 需要 Cookie | 用户提供最新 Cookie |
| 视频卡在第一帧 | VP9 不兼容 iOS | 转码 H.264 |
| 视频无法保存相册 | VP9 编码问题 | 同上，转码后解决 |
| Telegram 播放显示 1:1 | 播放器问题 | 视频正常，保存相册播放 |
| 文件超过 16MB | Telegram 限制 | 降低码率：-crf 28 -b:a 64k |

---

## 🛠️ 环境要求

| 工具 | 版本 | 用途 |
|------|------|------|
| yt-dlp | 2026.03.03+ | 视频下载 |
| deno | 2.7+ | JS 运行时 |
| ffmpeg | N-122997+ | 转码/合并 |
| curl-cffi | 可选 | 浏览器模拟（可选） |

---

## 📦 文件位置

| 类型 | 路径 |
|------|------|
| 视频存储 | `~/.openclaw/workspace/media/` |
| Cookie 临时 | `/tmp/youtube_cookies.txt` |
| 配置文件 | `~/.openclaw/workspace/TOOLS.md` |

---

*Last updated: 2026-03-08*