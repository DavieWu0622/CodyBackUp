#!/bin/bash
# Chrome Headless Scrape Script

URL="$1"
if [ -z "$URL" ]; then
  echo "Usage: scrape.sh <url>"
  exit 1
fi

google-chrome --headless --disable-gpu --no-sandbox --dump-dom "$URL" 2>/dev/null