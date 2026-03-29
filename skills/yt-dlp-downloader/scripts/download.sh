#!/usr/bin/env bash
set -euo pipefail

URL="${1:-}"
OUT_DIR="${2:-$HOME/.openclaw/workspace/media}"
COOKIE_FILE="${3:-}"
MODE="${4:-auto}"
LOG_FILE="${5:-}"

if [[ -z "$URL" ]]; then
  echo "Usage: download.sh <url> [out_dir] [cookie_file] [auto|audio] [log_file]" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"
export PATH="$HOME/.deno/bin:$PATH:$PATH"

BASE_ARGS=(
  --no-playlist
  -R 5
  --fragment-retries 5
  --no-check-certificates
  --restrict-filenames
  -o "$OUT_DIR/%(title)s_%(id)s.%(ext)s"
)

if [[ "$MODE" == "audio" ]]; then
  BASE_ARGS+=( -x --audio-format mp3 )
else
  BASE_ARGS+=( --remux-video mp4 )
fi

log() {
  local msg="$1"
  echo "$msg"
  [[ -n "$LOG_FILE" ]] && echo "$msg" >> "$LOG_FILE"
}

has_impersonate_chrome() {
  yt-dlp --list-impersonate-targets 2>/dev/null | grep -Eq '^Chrome([-A-Za-z0-9]+)?[[:space:]]+'
}

latest_file() {
  find "$OUT_DIR" -maxdepth 1 -type f -printf '%T@ %p\n' | sort -nr | head -n1 | cut -d' ' -f2-
}

try_download() {
  local strategy="$1"
  shift
  log "[yt] strategy=$strategy"
  local tmp_log
  tmp_log="$(mktemp)"
  if yt-dlp "${BASE_ARGS[@]}" "$@" "$URL" > >(tee -a "$tmp_log" >/dev/null) 2> >(tee -a "$tmp_log" >&2); then
    if [[ -n "$LOG_FILE" ]]; then cat "$tmp_log" >> "$LOG_FILE"; fi
    rm -f "$tmp_log"
    return 0
  fi
  if [[ -n "$LOG_FILE" ]]; then cat "$tmp_log" >> "$LOG_FILE"; fi
  rm -f "$tmp_log"
  return 1
}

normalize_cookie_if_needed() {
  local source_file="$1"
  if [[ -z "$source_file" || ! -f "$source_file" ]]; then
    return 1
  fi
  if awk 'BEGIN{ok=1} !/^#/ && NF>0 { if (index($0, "\t") == 0) ok=0 } END{ exit ok ? 0 : 1 }' "$source_file"; then
    echo "$source_file"
    return 0
  fi
  local normalized
  normalized="$(mktemp /tmp/ytcookies_norm_XXXXXX.txt)"
  python3 "$(dirname "$0")/normalize_cookies.py" "$source_file" "$normalized" >/dev/null
  echo "$normalized"
  return 0
}

CLEANUP_COOKIE=""

if try_download direct; then
  FILE="$(latest_file)"
  log "[yt] success=direct file=${FILE:-unknown}"
  exit 0
fi

if has_impersonate_chrome; then
  if try_download deno-impersonate --js-runtimes deno --impersonate Chrome; then
    FILE="$(latest_file)"
    log "[yt] success=deno-impersonate file=${FILE:-unknown}"
    exit 0
  fi
else
  log "[yt] skip=deno-impersonate reason=chrome-impersonate-unavailable"
fi

if [[ -n "$COOKIE_FILE" && -f "$COOKIE_FILE" ]]; then
  EFFECTIVE_COOKIE="$(normalize_cookie_if_needed "$COOKIE_FILE")"
  if [[ "$EFFECTIVE_COOKIE" != "$COOKIE_FILE" ]]; then
    CLEANUP_COOKIE="$EFFECTIVE_COOKIE"
    log "[yt] cookies=normalized"
  fi
  if has_impersonate_chrome; then
    if try_download cookies --cookies "$EFFECTIVE_COOKIE" --js-runtimes deno --impersonate Chrome; then
      FILE="$(latest_file)"
      log "[yt] success=cookies+impersonate file=${FILE:-unknown}"
      [[ -n "$CLEANUP_COOKIE" ]] && rm -f "$CLEANUP_COOKIE"
      exit 0
    fi
  else
    if try_download cookies --cookies "$EFFECTIVE_COOKIE" --js-runtimes deno; then
      FILE="$(latest_file)"
      log "[yt] success=cookies file=${FILE:-unknown}"
      [[ -n "$CLEANUP_COOKIE" ]] && rm -f "$CLEANUP_COOKIE"
      exit 0
    fi
  fi
  [[ -n "$CLEANUP_COOKIE" ]] && rm -f "$CLEANUP_COOKIE"
else
  log "[yt] skip=cookies reason=no-cookie-file"
fi

log "[yt] failed=all"
echo "Download failed after environment-aware fallback." >&2
if ! has_impersonate_chrome; then
  echo "Next step: provide a fresh cookies.txt (current environment does not support Chrome impersonation)." >&2
fi
exit 2
