#!/usr/bin/env bash
set -euo pipefail

URL="${1:-}"
TARGET="${2:-download}"
COOKIE_FILE="${3:-}"
OUT_DIR="${4:-$HOME/.openclaw/workspace/media}"

if [[ -z "$URL" ]]; then
  echo "Usage: run.sh <url> [download|audio|ios|telegram] [cookie_file] [out_dir]" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$OUT_DIR"

latest_media_file() {
  find "$OUT_DIR" -maxdepth 1 -type f \( -name '*.mp4' -o -name '*.webm' -o -name '*.mkv' -o -name '*.mp3' -o -name '*.m4a' \) -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -n1 | cut -d' ' -f2-
}

case "$TARGET" in
  download)
    bash "$SCRIPT_DIR/download.sh" "$URL" "$OUT_DIR" "$COOKIE_FILE"
    ;;
  audio)
    bash "$SCRIPT_DIR/download.sh" "$URL" "$OUT_DIR" "$COOKIE_FILE" audio
    ;;
  ios)
    bash "$SCRIPT_DIR/download.sh" "$URL" "$OUT_DIR" "$COOKIE_FILE"
    INPUT="$(latest_media_file)"
    [[ -n "$INPUT" ]] || { echo "No downloaded file found for ios transcode" >&2; exit 2; }
    bash "$SCRIPT_DIR/transcode_ios.sh" "$INPUT"
    ;;
  telegram)
    bash "$SCRIPT_DIR/download.sh" "$URL" "$OUT_DIR" "$COOKIE_FILE"
    INPUT="$(latest_media_file)"
    [[ -n "$INPUT" ]] || { echo "No downloaded file found for telegram transcode" >&2; exit 2; }
    IOS_FILE="$(bash "$SCRIPT_DIR/transcode_ios.sh" "$INPUT")"
    bash "$SCRIPT_DIR/compress_telegram.sh" "$IOS_FILE"
    ;;
  *)
    echo "Unknown target: $TARGET" >&2
    echo "Expected: download | audio | ios | telegram" >&2
    exit 1
    ;;
esac
