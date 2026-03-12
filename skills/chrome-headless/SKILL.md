---
name: chrome-headless
description: Headless Chrome browser for web scraping and screenshot. Uses command-line Chrome with headless mode.
homepage: https://github.com/openclaw/openclaw
metadata: {"clawdbot":{"emoji":"🌐","requires":{"bins":["google-chrome"]},"primaryBin":"google-chrome"}}
---

# Chrome Headless

Use headless Chrome to scrape web pages, take screenshots, and extract data.

## Commands

### Scrape HTML
```bash
chrome-headless scrape <url>
```

### Take Screenshot
```bash
chrome-headless screenshot <url> [output.png]
```

### Extract Text
```bash
chrome-headless text <url>
```

## Examples

```bash
# Scrape NBA player page
chrome-headless scrape "https://nba.hupu.com/players/yanghansen-153292.html"

# Take screenshot
chrome-headless screenshot "https://nba.hupu.com" "nba.png"

# Extract text content
chrome-headless text "https://example.com"
```

## Notes
- Runs in headless mode (no GUI)
- Uses --no-sandbox for server environments
- Requires Google Chrome installed at /usr/bin/google-chrome