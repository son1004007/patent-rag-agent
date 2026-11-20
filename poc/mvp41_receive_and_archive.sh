#!/bin/sh
# Owner-authorized Gateway stdin bridge: no listener, no output of provider data.
# Install in the existing private archive root's bin/ directory.
set -eu
umask 077
[ "$#" -eq 0 ] || exit 1
command -v python3 >/dev/null || exit 1
command -v readlink >/dev/null || exit 1
DOCKER=/usr/local/bin/docker
[ -x "$DOCKER" ] || exit 1
THIS_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
ROOT=$(CDPATH= cd -- "$THIS_DIR/.." && pwd -P)
[ -f "$THIS_DIR/mvp37_local_transport.py" ] || exit 1
[ -f "$ROOT/auth/archive_policy.json" ] || exit 1
[ -f "$ROOT/auth/archive_writer_password" ] || exit 1
WHEEL_ROOT=$(readlink -f "${HOME:?}/impe-rag/api-runtime-v1/wheels")
[ -d "$WHEEL_ROOT" ] || exit 1
DB_ID=$($DOCKER inspect patent-rag-mcp-stage-db --format '{{.Id}}')
[ "${#DB_ID}" -eq 64 ] || exit 1
export PATENT_ARCHIVE_ROOT="$ROOT"
export PATENT_WHEEL_ROOT="$WHEEL_ROOT"
export PATENT_DB_CONTAINER_ID="$DB_ID"
export PYTHONDONTWRITEBYTECODE=1
exec python3 "$THIS_DIR/mvp37_local_transport.py" --archive
