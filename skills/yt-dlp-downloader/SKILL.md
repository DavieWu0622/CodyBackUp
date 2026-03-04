---
name: yt-dlp-downloader
description: Download YouTube videos using yt-dlp directly (no API needed).
homepage: https://github.com/yt-dlp/yt-dlp
metadata: {"clawdbot":{"emoji":"⬇️","requires":{"bins":["yt-dlp","ffmpeg"]}}}
allowed-tools: Bash(yt-dlp:*)
---

# yt-dlp Downloader

Download YouTube videos directly without external APIs.

## Quick Start

```bash
# Download best quality (auto merge audio+video)
yt-dlp "YOUTUBE_URL" -o "~/Downloads/%(title)s.%(ext)s"

# Download audio only (MP3)
yt-dlp "YOUTUBE_URL" -x --audio-format mp3 -o "~/Downloads/%(title)s.%(ext)s"

# Download specific quality
yt-dlp "YOUTUBE_URL" -f "bestvideo[height<=1080]+bestaudio/best" --merge-output-format mp4
```

## Common Options

| Option | Description |
|--------|-------------|
| `-x --audio-format mp3` | Extract audio only |
| `-f "best[height<=720]"` | Max 720p quality |
| `--list-formats` | Show available formats |
| `--write-thumbnail` | Download thumbnail |
| `--write-info-json` | Download metadata |
| `--no-playlist` | Single video only |
| `--cookies-from-browser chrome` | Use browser cookies (for age-restricted) |

## Output Template Variables

- `%(title)s` - Video title
- `%(uploader)s` - Channel name
- `%(upload_date)s` - YYYYMMDD format
- `%(id)s` - Video ID
- `%(ext)s` - File extension

## Examples

**Download to workspace:**
```bash
yt-dlp "YOUTUBE_URL" -o "~/.openclaw/workspace/media/%(title)s.%(ext)s" --remux-video mp4
```

**Download shorts (vertical video):**
```bash
yt-dlp "YOUTUBE_SHORTS_URL" -o "~/.openclaw/workspace/media/%(title)s_%(id)s.%(ext)s"
```

**Download playlist:**
```bash
yt-dlp "PLAYLIST_URL" --yes-playlist -o "~/.openclaw/workspace/media/%(playlist_index)s - %(title)s.%(ext)s"
```
