#!/bin/bash
cd /root/.openclaw/workspace
git add -A
if git diff-index --quiet HEAD --; then
    echo "No changes"
else
    git commit -m "Daily backup: $(date +'%Y-%m-%d %H:%M')"
    git push origin master
    echo "Success"
fi
