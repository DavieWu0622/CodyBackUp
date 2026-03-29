#!/usr/bin/env python3
"""Normalize a human-pasted YouTube cookies text file into Netscape tab-separated format."""

from __future__ import annotations

import sys
from pathlib import Path


def normalize_line(line: str) -> str | None:
    line = line.strip()
    if not line:
        return None
    if line.startswith('#'):
        return line

    parts = line.split()
    if len(parts) < 7:
        return None

    domain = parts[0]
    include_subdomains = parts[1].upper()
    path = parts[2]
    secure = parts[3].upper()
    expires = parts[4]
    name = parts[5]
    value = ' '.join(parts[6:])

    return '\t'.join([domain, include_subdomains, path, secure, expires, name, value])


def main() -> int:
    if len(sys.argv) < 3:
        print('Usage: normalize_cookies.py <input> <output>', file=sys.stderr)
        return 1

    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])

    if not src.exists():
        print(f'Input file not found: {src}', file=sys.stderr)
        return 1

    out_lines = []
    for raw in src.read_text(encoding='utf-8', errors='ignore').splitlines():
        normalized = normalize_line(raw)
        if normalized is not None:
            out_lines.append(normalized)

    if not out_lines:
        print('No valid cookie lines found after normalization', file=sys.stderr)
        return 2

    dst.write_text('\n'.join(out_lines) + '\n', encoding='utf-8')
    print(str(dst))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
