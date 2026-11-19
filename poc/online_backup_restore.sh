#!/bin/sh
# Online logical backup + restore into a NEW isolated disposable cluster.
# Never stops/restarts any existing service. Run as the stage owner on NAS.
set -eu
umask 077
D=/usr/local/bin/docker
B=${STAGE_ROOT:?set private stage root}
DB=patent-rag-mcp-stage-db
LABEL=patent-rag.test=online-restore-v2
test -d "$B/backups"
test -z "$("$D" ps -aq --filter "label=$LABEL")"
test "$("$D" inspect "$DB" --format '{{.State.Running}} {{.HostConfig.NetworkMode}}')" = 'true none'
before=$("$D" ps -q)
before_states=$(for id in $before;do "$D" inspect "$id" --format '{{.Id}} {{.State.StartedAt}}';done)
started=$("$D" inspect "$DB" --format '{{.State.StartedAt}}')
sql(){ "$D" exec "$1" psql -X -qAt -v ON_ERROR_STOP=1 -h /tmp -p 55432 -U postgres -d "$2" -c "$3"; }
fingerprint(){ sql "$1" "$2" "SELECT count(*)||'|'||min(vector_dims(embedding))||'|'||md5(string_agg(md5(json_build_array(id,body,model_id,embedding::text)::text),'|' ORDER BY id)) FROM documents"; }
original=$(fingerprint "$DB" patent_demo)
test "${original%%|*}" = 4
stamp=$(date -u +%Y%m%dT%H%M%SZ)
dump="$B/backups/patent-demo-$stamp.dump"
test ! -e "$dump"
tmp="$dump.partial"
test ! -e "$tmp"
restore=
cleanup(){ if [ -n "$restore" ];then "$D" stop -t 5 "$restore" >/dev/null 2>&1 || true;fi; [ ! -f "$tmp" ] || rm -f "$tmp"; }
trap cleanup EXIT
"$D" exec "$DB" pg_dump -Fc -h /tmp -p 55432 -U postgres -d patent_demo >"$tmp"
test -s "$tmp"
test "$(fingerprint "$DB" patent_demo)" = "$original"
mv "$tmp" "$dump"
echo ONLINE_BACKUP_PASS
restore=$("$D" run --pull never -d --rm --label "$LABEL" --network none --read-only --cap-drop ALL --security-opt no-new-privileges --user postgres --memory 512m --cpu-shares 128 --tmpfs /tmp:rw,exec,nosuid,nodev,size=256m,mode=1777 --entrypoint bash sha256:b0108689bf51bd54d3129130967d4adf7ba58b395a9ff6653aa598b5fe7d7ba3 -ec 'umask 077; export PGDATA=/tmp/restore-pgdata; od -An -N24 -tx1 /dev/urandom | tr -d " \n" >/tmp/pw; initdb -D "$PGDATA" --username=postgres --auth-local=peer --auth-host=scram-sha-256 --pwfile=/tmp/pw --no-locale --encoding=UTF8 >/dev/null; rm /tmp/pw; exec postgres -D "$PGDATA" -h 127.0.0.1 -k /tmp -p 55432 -c shared_buffers=32MB -c max_connections=8')
n=0
until "$D" exec "$restore" pg_isready -q -h /tmp -p 55432;do n=$((n+1));[ "$n" -lt 40 ] || exit 1;sleep 1;done
sql "$restore" postgres 'CREATE ROLE patent_app NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS' >/dev/null
# Restore original database privileges via --create. Destination is the isolated test cluster.
"$D" exec -i "$restore" pg_restore --exit-on-error --create -h /tmp -p 55432 -U postgres -d postgres <"$dump"
test "$(fingerprint "$restore" patent_demo)" = "$original"
test "$(sql "$restore" patent_demo "SELECT has_table_privilege('patent_app','documents','SELECT') AND has_table_privilege('patent_app','documents','INSERT') AND NOT has_table_privilege('patent_app','documents','UPDATE') AND NOT has_table_privilege('patent_app','documents','DELETE') AND NOT EXISTS (SELECT 1 FROM pg_database d CROSS JOIN LATERAL aclexplode(coalesce(d.datacl,acldefault('d',d.datdba))) a WHERE d.datname='patent_demo' AND a.grantee=0 AND a.privilege_type='CONNECT')")" = t
test "$(sql "$restore" patent_demo "SELECT count(*) FROM pg_indexes WHERE tablename='documents' AND indexdef LIKE '%USING hnsw%'")" = 1
test "$(sql "$restore" patent_demo "SELECT vector_dims(embedding) FROM documents WHERE id='DEMO-P4'")" = 384
test "$(fingerprint "$DB" patent_demo)" = "$original"
test "$("$D" inspect "$DB" --format '{{.State.StartedAt}}')" = "$started"
for id in $before;do test "$("$D" inspect "$id" --format '{{.State.Running}}')" = true;done
 test "$(for id in $before;do "$D" inspect "$id" --format '{{.Id}} {{.State.StartedAt}}';done)" = "$before_states"
"$D" stop -t 5 "$restore" >/dev/null
restore=
echo FRESH_CLUSTER_RESTORE_FINGERPRINT_ACL_INDEX_PASS
echo EXISTING_SERVICES_NOT_RESTARTED
python3 - "$dump" <<'PY'
import pathlib,hashlib,stat,sys
p=pathlib.Path(sys.argv[1]); d=p.read_bytes()
assert stat.S_IMODE(p.stat().st_mode)==0o600
print("BACKUP_BYTES",len(d),"SHA256",hashlib.sha256(d).hexdigest())
PY
