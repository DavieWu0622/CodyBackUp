---
name: youtube-workflow
description: YouTube video analysis via Apify (configured). TikTok text generation + local download command.
homepage: https://github.com/user/youtube-workflow
metadata: {"clawdbot":{"emoji":"📹","requires":{"bins":["summarize"],"env":["APIFY_API_TOKEN"]},"primaryEnv":"APIFY_API_TOKEN"}}
allowed-tools: Bash(summarize:*)
---

# YouTube Workflow

Analyze YouTube videos via Apify and generate TikTok-style text.

## Quick Start

```bash
summarize "YOUTUBE_URL" --youtube auto --length medium
```

## Workflow

### Step 1: Analyze YouTube Video
```bash
summarize "https://youtube.com/watch?v=XXX" --youtube auto --length medium
```

**Returns:**
- 🎵 Song title + Artist
- 📝 Lyrics theme/emotion
- 🎬 Video scene
- 🎸 Music style

### Step 2: Generate TikTok Text

**Template:**
```
📹 YouTube 视频分析

🎵 歌曲信息
• 标题: [Song Name]
• 歌手: [Artist]
• 风格: [Style]
• 场景: [Scene]
• 情感: [Emotion]

📝 抖音文案
[Song name][emoji] [Artist]这首太[adj]了！

[Scene description][emoji]
[Emotion resonance]

🎵 [Artist] - [Song info]
@Channel source
#[ArtistEN] #[Tag1] #[Tag2] #[Style] #[Scene]

💻 本地下载命令（复制到终端执行）
```bash
yt-dlp "YOUTUBE_URL" -o "%(title)s.%(ext)s" --remux-video mp4
```

📋 在线下载备选: y2mate.is | yt1s.com | y2meta.app
```

## Tag Translation Rules

- 日文 → 英文/中文
- #あいみょん → #Aimyon
- #打上花火 → #DAOKO #打上花火
- 5 tags total: Artist + Language + Style + Scene + Generic

## Config

APIFY_API_TOKEN is configured in systemd environment.
