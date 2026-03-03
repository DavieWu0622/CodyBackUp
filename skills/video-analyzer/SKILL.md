---
name: video-analyzer
description: Analyze uploaded video files and generate TikTok-style text. Requires audio transcription API.
homepage: https://github.com/user/video-analyzer
metadata: {"clawdbot":{"emoji":"🎬","requires":{"bins":["summarize"]},"read_when":["User uploads video file","Analyzing local video files"]},"optional_env":["GROQ_API_KEY","OPENAI_API_KEY"]}
---

# Video Analyzer

Analyze uploaded video files and generate TikTok-style text.

## ⚠️ Requirement: Audio Transcription

Video analysis requires an audio transcription API. Options:

| Provider | Cost | Speed | Setup |
|----------|------|-------|-------|
| **Groq** ⭐ | Free tier (~1000 min/month) | Very fast | Register at groq.com |
| OpenAI | Pay per use | Fast | Use existing OpenAI key |
| FAL | Free tier | Medium | Register at fal.ai |

## When to Use

- User uploads video file AND transcription is configured
- Otherwise, recommend YouTube link analysis instead

## Workflow (If Configured)

### Step 1: Check Transcription Config

Check if GROQ_API_KEY or OPENAI_API_KEY is available:
```bash
echo $GROQ_API_KEY $OPENAI_API_KEY
```

### Step 2: Analyze Video

```bash
# With Groq (recommended)
summarize "/path/to/video.mp4" --transcriber whisper --length medium

# With default
echo $GROQ_API_KEY && summarize "/path/to/video.mp4" --length medium
```

### Step 3: Generate TikTok Text

```
🎬 视频分析

📋 内容摘要
• 类型: [Music/Vlog/etc]
• 主题: [Main content]
• 情感: [Mood]

📝 抖音文案
[Generated text]

🏷️ Tags: #[Artist] #[Style] #[Mood]
```

## Alternative: YouTube Link (No Transcription Needed)

If transcription not configured, ask user to:
1. Use YouTube link instead
2. Or provide Groq API key

```
💡 提示：视频文件分析需要音频转录 API。

可选方案：
1. 发送 YouTube 链接（无需额外配置）
2. 配置 Groq API Key（免费，1000分钟/月）
   注册: https://console.groq.com
```

## User Setup (Groq)

```bash
# Register at https://console.groq.com
# Get API key
export GROQ_API_KEY="gsk_xxxxxxxx"
```

Add to systemd service or ~/.bashrc
