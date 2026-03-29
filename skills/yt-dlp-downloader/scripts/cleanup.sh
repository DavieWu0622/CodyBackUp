#!/usr/bin/env bash
set -euo pipefail

for file in "$@"; do
  if [[ -n "$file" && -e "$file" ]]; then
    rm -f "$file"
    echo "removed: $file"
  fi
done
