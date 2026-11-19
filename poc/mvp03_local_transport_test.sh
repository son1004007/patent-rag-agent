#!/bin/sh
# Schema-only, synthetic-only integration. Never copy production patent rows or credentials.
set -eu
umask 077
D=/usr/local/bin/docker
ROOT=$TEST_ROOT
DB=patent-rag-mcp-stage-db
API=patent-rag-mcp-stage-api
M=$MODEL_ROOT
W=$WHEEL_ROOT
LABEL=patent-rag.test=transport-isolated-v1
case "$ROOT" in /tmp/patent-ingest-test.*) ;; *) echo INVALID_TEST_ROOT; exit 1;; esac
test ! -L "$ROOT"; test -d "$ROOT/code"; test ! -e "$ROOT/auth"; test -d "$M"; test -d "$W"
test -z "$("$D" ps -aq --filter "label=$LABEL")"
test "$("$D" inspect "$DB" --format '{{.State.Running}} {{.HostConfig.NetworkMode}}')" = 'true none'
di=$("$D" inspect "$DB" --format '{{.Image}}')
ai=$("$D" inspect "$API" --format '{{.Image}}')
test "$di" = sha256:b0108689bf51bd54d3129130967d4adf7ba58b395a9ff6653aa598b5fe7d7ba3
test "$ai" = sha256:183e5ad42322fea6f731433ae7f6be7498812b31d2eaf05537ffed838dd1ba7c
existing=$("$D" ps -q)
target=$("$D" ps -q --filter name=patent-rag)
states(){ for id in $*; do "$D" inspect "$id" --format '{{.Id}} {{.State.StartedAt}} {{.State.Running}}'; done; }
source_fp(){ "$D" exec "$DB" psql -X -qAt -v ON_ERROR_STOP=1 -h /tmp -p 55432 -U postgres -d patent_private_ingest_v1 -c "SELECT (SELECT count(*)||':'||md5(string_agg(md5(to_jsonb(d)::text),'|' ORDER BY id)) FROM private_docs.documents d)||'|'||(SELECT count(*)||':'||md5(string_agg(md5(to_jsonb(s)::text),'|' ORDER BY document_id,section)) FROM private_docs.section_sources s)||'|'||(SELECT count(*)||':'||md5(string_agg(md5(to_jsonb(c)::text),'|' ORDER BY document_id,section,start_offset)) FROM private_docs.chunks c)"; }
initial=$(states $existing); target_initial=$(states $target); original=$(source_fp)
clone=; app=
cleanup(){ if [ -n "$app" ]; then "$D" stop -t 5 "$app" >/dev/null 2>&1 || true; fi; if [ -n "$clone" ]; then "$D" stop -t 5 "$clone" >/dev/null 2>&1 || true; fi; }
trap cleanup EXIT
mkdir "$ROOT/auth" "$ROOT/locks"
: > "$ROOT/locks/ingest.lock"
PYTHONPATH="$ROOT/code" python3 - "$ROOT/auth" <<'PY'
import pathlib,sys,secrets,json
from test_mvp03_ingest_adapter import fixture,approve
p=pathlib.Path(sys.argv[1])
for name in ('writer_password','reader_password'):
    (p/name).write_text(secrets.token_hex(32))
(p/'ingest_approval.json').write_text(json.dumps(approve(fixture())))
PY
"$D" exec "$DB" pg_dump -Fc --schema-only -h /tmp -p 55432 -U postgres -d patent_private_ingest_v1 >"$ROOT/schema.dump"
test -s "$ROOT/schema.dump"
clone=$("$D" run --pull never -d --rm --label "$LABEL" --network none --read-only --cap-drop ALL --security-opt no-new-privileges --user postgres --memory 512m --cpu-shares 128 --tmpfs /tmp:rw,exec,nosuid,nodev,size=256m,mode=1777 --entrypoint bash "$di" -ec 'umask 077; export PGDATA=/tmp/test-pgdata; od -An -N24 -tx1 /dev/urandom | tr -d " \n" >/tmp/pw; initdb -D "$PGDATA" --username=postgres --auth-local=peer --auth-host=scram-sha-256 --pwfile=/tmp/pw --no-locale --encoding=UTF8 >/dev/null; rm /tmp/pw; exec postgres -D "$PGDATA" -h 127.0.0.1 -k /tmp -p 55432 -c shared_buffers=32MB -c max_connections=12')
n=0; until "$D" exec "$clone" pg_isready -q -h /tmp -p 55432; do n=$((n+1)); [ "$n" -lt 40 ] || exit 1; sleep 1; done
python3 - "$ROOT/auth" <<'PY' | "$D" exec -i "$clone" psql -X -q -v ON_ERROR_STOP=1 -h /tmp -p 55432 -U postgres -d postgres >/dev/null 2>&1
import pathlib,sys,re
p=pathlib.Path(sys.argv[1])
for role,f in [('patent_ingest_reader_v1','reader_password'),('patent_ingest_writer_v1','writer_password')]:
    pw=(p/f).read_text(); assert re.fullmatch('[a-f0-9]{64}',pw)
    print("CREATE ROLE "+role+" LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD '"+pw+"';")
print('ALTER ROLE patent_ingest_reader_v1 SET default_transaction_read_only=on;')
PY
if ! "$D" exec -i "$clone" pg_restore --exit-on-error --create -h /tmp -p 55432 -U postgres -d postgres <"$ROOT/schema.dump" >/dev/null 2>&1; then echo SCHEMA_RESTORE_FAILED; exit 1; fi
echo SCHEMA_ONLY_RESTORE_PASS
# All paths and credentials here are synthetic; no production file or row.
O=$ROOT/owner
mkdir "$O" "$O/code" "$O/auth" "$O/locks"
for f in mvp03_ingest_adapter.py private_patent_ingest.py private_patent_increment.py; do cp "$ROOT/code/$f" "$O/code/$f"; chmod 600 "$O/code/$f"; done
for f in writer_password ingest_approval.json; do cp "$ROOT/auth/$f" "$O/auth/$f"; chmod 600 "$O/auth/$f"; done
: >"$O/locks/ingest.lock"
PYTHONPATH="$ROOT/code" python3 -c 'from test_mvp03_ingest_adapter import fixture; from private_patent_increment import canonical; print(canonical(fixture()))' >"$O/packet.json"
# The two containers see the same owner file inode; no DB connection needed.
app=$("$D" run --pull never -d --rm --label "$LABEL" --network none --read-only --cap-drop ALL --security-opt no-new-privileges --user "$(id -u):$(id -g)" --memory 128m -e PYTHONDONTWRITEBYTECODE=1 -v "$O/code:/code:ro" -v "$O/locks:/locks:ro" --entrypoint python "$ai" -c 'import sys,time;sys.path.insert(0,"/code");from mvp03_ingest_adapter import writer_lock
with writer_lock():
 print("LOCK_READY",flush=True)
 time.sleep(60)')
n=0; until "$D" logs "$app" 2>/dev/null | grep -q '^LOCK_READY$'; do n=$((n+1)); [ "$n" -lt 15 ] || exit 1; sleep 1; done
set +e
"$D" run --pull never --rm --label "$LABEL" --network none --read-only --cap-drop ALL --security-opt no-new-privileges --user "$(id -u):$(id -g)" --memory 128m -e PYTHONDONTWRITEBYTECODE=1 -v "$O/code:/code:ro" -v "$O/locks:/locks:ro" --entrypoint python "$ai" -c 'import sys;sys.path.insert(0,"/code");from mvp03_ingest_adapter import writer_lock,IngestBusy
try:
 with writer_lock(): pass
except IngestBusy: sys.exit(17)'
rc=$?
set -e
test "$rc" = 17
echo CROSS_CONTAINER_LOCK_PASS
"$D" stop -t 5 "$app" >/dev/null; app=
export PATENT_INGEST_ROOT="$(readlink -f "$O")" PATENT_MODEL_ROOT="$(readlink -f "$M")" PATENT_WHEEL_ROOT="$(readlink -f "$W")" PATENT_DB_CONTAINER_ID="$clone"
run(){ python3 "$ROOT/code/mvp03_local_transport.py" "$@" <"$O/packet.json"; }
r=$(run --check)
printf '%s' "$r" | python3 -c 'import sys,json; assert json.load(sys.stdin)=={"status":"DRY_RUN","writes":0,"exists":False,"sections":0}'
echo LOCAL_TRANSPORT_CHECK_PASS
r=$(run --apply)
printf '%s' "$r" | python3 -c 'import json,sys; assert json.load(sys.stdin)=={"status":"PASS","verified":True,"writes":2,"documentsAdded":1,"sectionsAdded":2}'
echo LOCAL_TRANSPORT_INSERT_PASS
sql(){ "$D" exec "$clone" psql -X -qAt -v ON_ERROR_STOP=1 -h /tmp -p 55432 -U postgres -d patent_private_ingest_v1 -c "$1"; }
count_sql="SELECT (SELECT count(*) FROM private_docs.documents),(SELECT count(*) FROM private_docs.section_sources),(SELECT count(*) FROM private_docs.chunks),(SELECT min(private_docs.vector_dims(embedding)) FROM private_docs.chunks)"
test "$(sql "$count_sql")" = '1|2|5|384'
echo LOCAL_TRANSPORT_DB_COUNTS_PASS
r=$(run --apply)
printf '%s' "$r" | python3 -c 'import json,sys; assert json.load(sys.stdin)=={"status":"REUSED_VERIFIED","verified":True,"writes":0}'
test "$(sql "$count_sql")" = '1|2|5|384'
echo LOCAL_TRANSPORT_REUSE_PASS
# No executable source tampering or target selection from packet.
printf '\n# tamper\n' >>"$O/code/mvp03_ingest_adapter.py"
set +e
r=$(run --apply)
rc=$?
set -e
test "$rc" = 1
printf '%s' "$r" | python3 -c 'import json,sys; assert json.load(sys.stdin)=={"status":"BLOCKED_PREFLIGHT","verified":False}'
test "$(sql "$count_sql")" = '1|2|5|384'
echo LOCAL_TRANSPORT_CODE_PIN_DENIAL_PASS
test "$(source_fp)" = "$original" || { echo SOURCE_FINGERPRINT_CHANGED; exit 1; }
echo SOURCE_FINGERPRINT_UNCHANGED
test "$(states $target)" = "$target_initial" || { echo PATENT_CONTAINER_STATES_CHANGED; exit 1; }
echo PATENT_CONTAINERS_UNCHANGED
if [ "$(states $existing)" = "$initial" ]; then echo ALL_EXISTING_CONTAINERS_UNCHANGED; else echo OTHER_CONTAINER_STATE_DIFFERENCE_OBSERVED; fi
"$D" stop -t 5 "$clone" >/dev/null; clone=
n=0; while [ -n "$("$D" ps -aq --filter "label=$LABEL")" ]; do n=$((n+1)); [ "$n" -lt 20 ] || exit 1; sleep 1; done
test -z "$("$D" ps -aq --filter label=patent-rag.worker=approved-local-one-shot)"
echo LOCAL_TRANSPORT_CLEANUP_PASS
