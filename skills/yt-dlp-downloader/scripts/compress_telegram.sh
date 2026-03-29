#!/usr/bin/env bash
set -euo pipefail

INPUT="${1:-}"
OUTPUT="${2:-}"

if [[ -z "$INPUT" ]]; then
  echo "Usage: compress_telegram.sh <input> [output]" >&2
  exit 1
fi

if [[ ! -f "$INPUT" ]]; then
  echo "Input file not found: $INPUT" >&2
  exit 1
fi

if [[ -z "$OUTPUT" ]]; then
  base="${INPUT%.*}"
  OUTPUT="${base}_tg.mp4"
fi

ffmpeg -y -i "$INPUT" \
  -c:v libx264 -profile:v high -level 4.1 \
  -c:a aac -b:a 64k \
  -movflags +faststart \
  -preset faster -crf 28 \
  "$OUTPUT"

echo "$OUTPUT"
