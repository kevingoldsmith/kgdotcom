#!/bin/bash
#
# Sync the photos/ tree with S3. Photos are kept out of git (the repo is public)
# and instead live in a private S3 bucket; see CLAUDE.md.
#
#   scripts/photos.sh pull   non-destructive download (rclone copy): brings in new/
#                            changed photos, never deletes local files. Run before a
#                            build so generated galleries reflect the latest photos.
#   scripts/photos.sh push   mirror local -> S3 (rclone sync), including deletions.
#                            Local is treated as the source of truth, so only run this
#                            from a machine whose photos/ is current.
#
# Override the bucket with PHOTOS_REMOTE, e.g.
#   PHOTOS_REMOTE=s3:my-other-bucket scripts/photos.sh pull
#
set -euo pipefail

REMOTE="${PHOTOS_REMOTE:-s3:kgsitephotos-956701070452-us-west-2-an}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL="$ROOT/photos"
FILTER="$ROOT/scripts/photos-filter.txt"

if ! command -v rclone >/dev/null 2>&1; then
    echo "rclone not found; skipping photo sync. Install rclone to sync photos." >&2
    exit 1
fi

case "${1:-}" in
    pull)
        rclone copy "$REMOTE" "$LOCAL" --filter-from "$FILTER" --progress
        ;;
    push)
        rclone sync "$LOCAL" "$REMOTE" --filter-from "$FILTER" --progress
        ;;
    *)
        echo "Usage: scripts/photos.sh {pull|push}" >&2
        exit 1
        ;;
esac
