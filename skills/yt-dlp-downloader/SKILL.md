---
name: yt-dlp-downloader
description: Download YouTube videos or Shorts with a practical fallback workflow. Use when the user wants to download a YouTube link, save a short locally, extract audio, make a file iPhone/Telegram compatible, or recover from yt-dlp failures with deno / impersonation / cookies.
metadata: {"clawdbot":{"emoji":"⬇️","requires":{"bins":["yt-dlp","ffmpeg"]}}}
allowed-tools: Bash(yt-dlp:*)
---

# yt-dlp Downloader

这个 skill 负责把 **YouTube 下载流程产品化**，默认简单、失败再升级。

## 何时使用

当用户出现这些需求时使用：

- “下载这个 YouTube 视频”
- “把这个 shorts 下下来”
- “提取这个视频音频”
- “转成 iPhone / Telegram 兼容格式”
- “yt-dlp 下载失败了，帮我排查”

## 处理顺序

默认按下面顺序，不要一上来就走最重流程：

1. **先直接下载**
2. 失败后再尝试 **deno + impersonate chrome**
3. 还失败，且用户已提供 cookies 时，再走 **cookies fallback**
4. 只有在目标是 iPhone / Telegram / 用户反馈播放异常时，才做 **H.264 + AAC 转码**
5. 只有在用户明确要音频时，才走 **audio 模式**

## 核心脚本

- `scripts/download.sh`：主下载脚本，内置 3 层 fallback
- `scripts/transcode_ios.sh`：转 iPhone / 通用兼容 MP4
- `scripts/compress_telegram.sh`：压缩到更适合 Telegram 的版本
- `scripts/cleanup.sh`：清理 cookies / 临时文件
- `scripts/normalize_cookies.py`：把用户发来的可读 cookies 文本转成 yt-dlp 可接受的 Netscape 格式

## 新版体验改进

- `download.sh` 会自动识别当前环境是否支持 impersonation
- 用户给的是“可读文本 cookies”时，会先自动标准化再下载
- 成功时会输出更干净的成功结果，不要求用户理解全部中间细节

## 推荐用法

### 1. 先下载
```bash
bash scripts/download.sh "YOUTUBE_URL"
```

### 2. 如果用户只要音频
```bash
bash scripts/download.sh "YOUTUBE_URL" "$HOME/.openclaw/workspace/media" "" audio
```

### 3. 如果需要 iPhone/Telegram 兼容
```bash
bash scripts/transcode_ios.sh "input.mp4"
```

### 4. 如果文件过大，进一步压缩
```bash
bash scripts/compress_telegram.sh "input_ios.mp4"
```

### 5. 如果必须使用 cookies
```bash
bash scripts/download.sh "YOUTUBE_URL" "$HOME/.openclaw/workspace/media" "/tmp/youtube_cookies.txt"
```

## 交互原则

- 默认先走“最低心智负担”路径
- 不要先要求用户导 cookies，除非前两层下载都失败
- 成功后要明确告诉用户：
  - 文件路径
  - 是否已转码
  - 是否适合 Telegram / iPhone
- 失败后要明确告诉用户：
  - 已尝试到哪一步
  - 下一步需要什么（例如 cookies）

## 常见判断

### 什么时候要转码？
仅在这些情况：
- 用户说要发 Telegram
- 用户说 iPhone 播放有问题
- 下载下来是 VP9/WebM，且目标是移动端播放

### 什么时候要压缩？
- 文件明显过大
- 目标是 Telegram 发送
- 用户明确要“压小一点”

### 什么时候需要 cookies？
- direct + deno fallback 都失败
- 年龄限制 / 地域限制 / 登录态校验

## 输出格式建议

### 下载成功
- 下载成功
- 文件路径：`...`
- 当前格式：`...`
- 是否建议转码：是 / 否

### 下载失败
- 失败阶段：direct / deno / cookies
- 可能原因：反爬 / 年龄限制 / cookies 失效 / 网络
- 下一步建议：请提供最新 cookies.txt

## 注意事项

- cookies 只做临时使用，用完删除
- 不要默认把“需要 cookies”当作第一步
- 不要把“下载 / 转码 / 文案生成”强绑成一个单流程
- 如果用户只是要下载，就只做下载
