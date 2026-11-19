#!/bin/sh
# Preview by default. No restart/stop commands. Explicit --start-stopped only after owner approval.
set -eu
D=/usr/local/bin/docker
mode=${1:---check}
case "$mode" in --check|--start-stopped) ;; *) exit 2;; esac
B=${STAGE_ROOT:?set private stage root}
DB=patent-rag-mcp-stage-db
API=patent-rag-mcp-stage-api
RELAY=patent-rag-mcp-stage-relay
TUN=patent-rag-mcp-tunnel
for c in "$DB" "$API" "$RELAY" "$TUN";do
 test "$("$D" inspect "$c" --format '{{len .HostConfig.PortBindings}}')" = 0
 "$D" inspect "$c" --format '{{.Name}} {{.State.Status}} {{.HostConfig.NetworkMode}}'
done
dbid=$("$D" inspect "$DB" --format '{{.Id}}')
test "$("$D" inspect "$DB" --format '{{.HostConfig.NetworkMode}}')" = none
for c in "$API" "$RELAY";do test "$("$D" inspect "$c" --format '{{.HostConfig.NetworkMode}}')" = "container:$dbid";done
test "$("$D" inspect "$TUN" --format '{{.HostConfig.NetworkMode}}')" = bridge
if [ "$mode" = --check ];then echo NO_MUTATION_STARTUP_PLAN_PASS;exit 0;fi
start(){ if [ "$("$D" inspect "$1" --format '{{.State.Running}}')" != true ];then "$D" start "$1" >/dev/null;fi; }
start "$DB"
n=0;until "$D" exec "$DB" pg_isready -q -h /tmp -p 55432;do n=$((n+1));[ "$n" -lt 60 ] || exit 1;sleep 1;done
start "$API"
"$D" exec "$API" python /code/stage_http_test.py restart
# A stale socket after abrupt termination must be reviewed manually; never unlink it here.
if [ "$("$D" inspect "$RELAY" --format '{{.State.Running}}')" != true ];then
 test ! -e "$B/tunnel/relay/mcp.sock" || { echo STALE_SOCKET_REVIEW_REQUIRED;exit 1; }
fi
start "$RELAY"
n=0;until test -S "$B/tunnel/relay/mcp.sock";do n=$((n+1));[ "$n" -lt 30 ] || exit 1;sleep 1;done
python3 "$B/tunnel/code/tunnel_unix_smoke.py" "$B"
start "$TUN"
echo SEQUENTIAL_START_REQUESTED_VERIFY_TUNNEL_POLL_AND_CHATGPT
