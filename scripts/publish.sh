#!/bin/bash

# Copy the built site in output/ up to the web host.
#
# Requires SCP_DEST, e.g.
#   SCP_DEST=user@host:/path/to/webroot make publish
#
# Without the guard below an unset SCP_DEST expands to nothing and scp silently
# treats the LAST file in output/ as the destination, copying the rest of the
# site onto it instead of publishing anything.

set -euo pipefail

if [ -z "${SCP_DEST:-}" ]; then
    echo "ERROR: SCP_DEST is not set, nothing was published." >&2
    echo "Set it to the publish target, for example:" >&2
    echo "  SCP_DEST=user@host:/path/to/webroot make publish" >&2
    exit 1
fi

if [ ! -d output ]; then
    echo "ERROR: output/ does not exist. Run 'make build' first." >&2
    exit 1
fi

pushd output > /dev/null
scp -rv "$(pwd)"/* "${SCP_DEST}"
popd > /dev/null
