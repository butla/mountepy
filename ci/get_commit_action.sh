#!/bin/bash
set -e

COMMIT_SUMMARY=$(git log -1 --format=%s)
COMMIT_TYPE=$(echo $COMMIT_SUMMARY | cut -d "(" -f 1)

case $COMMIT_TYPE in
    feat|fix|refactor|perf) printf build_code;;
    # Doc changes sometimes go hand in hand with other minor tweaks.
    # We won't risk anything when reuploading the docs just to be sure.
    docs|style|test|chore) printf build_docs;;
    *) >&2 echo "Invalid commit format! Use AngularJS convention."; exit 2;
esac

