---
name: youtube-workflow
description: YouTube video download via yt-dlp + analysis. TikTok text generation.
homepage: https://github.com/user/youtube-workflow
metadata: {"clawdbot":{"emoji":"📹","requires":{"bins":["yt-dlp"],"optional":["summarize"]}}}
allowed-tools: Bash(yt-dlp:*), Bash(summarize:*), Bash(ffprobe:*)
---

# YouTube Workflow

Download and analyze YouTube videos using yt-dlp (no API needed).

## Quick Start

### Option A: Download + Local Analysis (No API needed)
```bash
# 1. Download video
yt-dlp "YOUTUBE_URL" -o "~/.openclaw/workspace/media/%(title)s_%(id)s.%(ext)s" --remux-video mp4

# 2. Extract metadata
yt-dlp "YOUTUBE_URL" --dump-json --skip-download | jq -r '.title, .uploader, .description'

# 3. Extract audio for transcription
ffmpeg -i "VIDEO_FILE" -vn -acodec mp3 /tmp/audio.mp3 -y
```

### Option B: Online Analysis (Requires API)
```bash
summarize "YOUTUBE_URL" --youtube auto --length medium
```

## Workflow (Download + Analyze)

### Step 1: Download YouTube Video
```bash
yt-dlp "https://youtube.com/watch?v=XXX" -o "~/.openclaw/workspace/media/%(title)s.%(ext)s" --remux-video mp4
```

### Step 2: Extract Metadata
```bash
yt-dlp "YOUTUBE_URL" --dump-json --skip-download | jq -r '{title: .title, uploader: .uploader, duration: .duration_string, tags: .tags}'
```

### Step 3: Generate TikTok Text

**Analysis Template:**
```
📹 YouTube 视频分析

🎵 视频信息（来自元数据）
• 标题: [Title from yt-dlp]
• 频道: [Uploader]
• 时长: [Duration]
• 标签: [Tags]

📝 内容分析
基于视频元数据和描述的分析...

🎵 如果是音乐视频
• 歌曲推测: [Based on title/tags]
• 风格推测: [Based on metadata]
• 情感氛围: [Analysis]

📝 抖音文案（如果适用）
[Title][emoji] [Channel]这首太[adj]了！

[Content description][emoji]
[Emotion resonance]

🎵 [Channel]
@来源
#[Tag1] #[Tag2] #[风格] #[场景]

💻 下载命令（已执行）
```bash
yt-dlp "YOUTUBE_URL" -o "%(title)s.%(ext)s" --remux-video mp4
```
```

## Tag Translation Rules

- 日文 → 英文/中文
- #あいみょん → #Aimyon
- #打上花火 → #DAOKO #打上花火
- 5 tags total: Artist + Language + Style + Scene + Generic

## Config

APIFY_API_TOKEN is configured in systemd environment.
