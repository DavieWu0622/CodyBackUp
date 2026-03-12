#!/bin/bash
# Chrome Headless Screenshot Script

URL="$1"
OUTPUT="${2:-screenshot.png}"

if [ -z "$URL" ]; then
  echo "Usage: screenshot.sh <url> [output.png]"
  exit 1
fi

google-chrome --headless --disable-gpu --no-sandbox --screenshot="$OUTPUT" "$URL" 2>/dev/null
echo "Screenshot saved: $OUTPUT"