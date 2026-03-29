# YouTube 下载 Skill v2 工作流（2026-03-28）

## 目标
把 YouTube 下载从“手工排障文档”收口成“默认简单、失败再升级”的 skill。

## 统一入口
```bash
bash /root/.openclaw/workspace/skills/yt-dlp-downloader/scripts/run.sh "YOUTUBE_URL" [download|audio|ios|telegram] [cookie_file] [out_dir]
```

### 模式说明
- `download`：只下载视频
- `audio`：只提取音频
- `ios`：下载后自动转 iPhone 兼容 MP4
- `telegram`：下载 → iOS 转码 → Telegram 压缩

## 内部脚本
- `scripts/download.sh`
- `scripts/transcode_ios.sh`
- `scripts/compress_telegram.sh`
- `scripts/cleanup.sh`
- `scripts/run.sh`

## 决策顺序
1. 先 direct 下载
2. 失败后 deno + impersonate
3. 仍失败且用户提供 cookies，再走 cookies
4. 仅在目标明确时转码或压缩

## 使用建议
### 普通下载
```bash
bash .../run.sh "URL" download
```

### 发 Telegram
```bash
bash .../run.sh "URL" telegram
```

### 只导音频
```bash
bash .../run.sh "URL" audio
```

## 为什么这版更好用
- 不再要求一开始就提供 cookies
- 不再把“下载 / 转码 / 文案”绑死
- 不再每次手拼长命令
- 统一入口更适合 agent 和人工都复用
