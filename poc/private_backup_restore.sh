#!/bin/sh
# Private logical backup and fresh, network-isolated restore. No production restart.
set -eu
umask 077
D=/usr/local/bin/docker
B=$STAGE_ROOT
DB=patent-rag-mcp-stage-db
NAME=patent_private_ingest_v1
LABEL=patent-rag.test=private-restore-v1
test -d "$B/backups"
test -z "$("$D" ps -aq --filter "label=$LABEL")"
test "$("$D" inspect "$DB" --format '{{.State.Running}} {{.HostConfig.NetworkMode}}')" = 'true none'
image=$("$D" inspect "$DB" --format '{{.Image}}')
test "$image" = sha256:b0108689bf51bd54d3129130967d4adf7ba58b395a9ff6653aa598b5fe7d7ba3
before=$("$D" ps -q)
states(){ for id in $before; do "$D" inspect "$id" --format '{{.Id}} {{.State.StartedAt}} {{.State.Running}}'; done; }
before_states=$(states)
sql(){ "$D" exec "$1" psql -X -qAt -v ON_ERROR_STOP=1 -h /tmp -p 55432 -U postgres -d "$2" -c "$3"; }
fingerprint(){ sql "$1" "$NAME" "SELECT (SELECT count(*)||':'||md5(string_agg(md5(to_jsonb(d)::text),'|' ORDER BY id)) FROM private_docs.documents d)||'|'||(SELECT count(*)||':'||md5(string_agg(md5(to_jsonb(s)::text),'|' ORDER BY document_id,section)) FROM private_docs.section_sources s)||'|'||(SELECT count(*)||':'||md5(string_agg(md5(to_jsonb(c)::text),'|' ORDER BY document_id,section,start_offset)) FROM private_docs.chunks c)"; }
acl(){ sql "$1" "$NAME" "SELECT string_agg(n.nspname||'.'||c.relname||':'||c.relkind::text||':'||c.relowner::regrole::text||':'||coalesce(c.relacl::text,''),'|' ORDER BY c.relname) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='private_docs' AND c.relkind IN ('r','v'); SELECT datacl::text FROM pg_database WHERE datname=current_database(); SELECT nspacl::text FROM pg_namespace WHERE nspname='private_docs';"; }
indexes(){ sql "$1" "$NAME" "SELECT string_agg(indexdef,'|' ORDER BY indexname) FROM pg_indexes WHERE schemaname='private_docs'"; }
rank(){ sql "$1" "$NAME" "WITH q AS (SELECT embedding FROM private_docs.chunks ORDER BY document_id,section,start_offset LIMIT 1), ranked AS (SELECT DISTINCT ON(c.document_id) c.document_id,c.embedding OPERATOR(private_docs.<=>) q.embedding AS distance FROM private_docs.chunks c CROSS JOIN q ORDER BY c.document_id,distance,c.section,c.start_offset), top3 AS (SELECT document_id,distance FROM ranked ORDER BY distance,document_id LIMIT 3) SELECT count(*)||':'||md5(string_agg(document_id||':'||distance::text,'|' ORDER BY distance,document_id)) FROM top3"; }
original=$(fingerprint "$DB"); test -n "$original"
orig_acl=$(acl "$DB"); orig_index=$(indexes "$DB"); orig_rank=$(rank "$DB")
test "$(printf '%s' "$orig_rank" | cut -d: -f1)" = 3
stamp=$(date -u +%Y%m%dT%H%M%SZ)
dump="$B/backups/private-patent-mvp05-$stamp.dump"
tmp="$dump.partial"
test ! -e "$dump"; test ! -e "$tmp"
restore=
cleanup(){ if [ -n "$restore" ]; then "$D" stop -t 5 "$restore" >/dev/null 2>&1 || true; fi; if [ -f "$tmp" ]; then rm -f "$tmp"; fi; }
trap cleanup EXIT
"$D" exec "$DB" pg_dump -Fc -h /tmp -p 55432 -U postgres -d "$NAME" >"$tmp"
test -s "$tmp"; test "$(fingerprint "$DB")" = "$original"
mv "$tmp" "$dump"
python3 - "$dump" <<'PY'
import pathlib,stat,sys
p=pathlib.Path(sys.argv[1])
assert stat.S_IMODE(p.stat().st_mode)==0o600
print("ONLINE_BACKUP_PASS bytes="+str(p.stat().st_size))
PY
restore=$("$D" run --pull never -d --rm --label "$LABEL" --network none --read-only --cap-drop ALL --security-opt no-new-privileges --user postgres --memory 512m --cpu-shares 128 --tmpfs /tmp:rw,exec,nosuid,nodev,size=256m,mode=1777 --entrypoint bash "$image" -ec 'umask 077; export PGDATA=/tmp/restore-pgdata; od -An -N24 -tx1 /dev/urandom | tr -d " \n" >/tmp/pw; initdb -D "$PGDATA" --username=postgres --auth-local=peer --auth-host=scram-sha-256 --pwfile=/tmp/pw --no-locale --encoding=UTF8 >/dev/null; rm /tmp/pw; exec postgres -D "$PGDATA" -h 127.0.0.1 -k /tmp -p 55432 -c shared_buffers=32MB -c max_connections=8')
n=0
until "$D" exec "$restore" pg_isready -q -h /tmp -p 55432; do n=$((n+1)); [ "$n" -lt 40 ] || exit 1; sleep 1; done
test "$("$D" inspect "$restore" --format '{{.HostConfig.NetworkMode}} {{.HostConfig.ReadonlyRootfs}}')" = 'none true'
sql "$restore" postgres 'CREATE ROLE patent_ingest_reader_v1 NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS; CREATE ROLE patent_ingest_writer_v1 NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS; CREATE ROLE patent_app NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS' >/dev/null
if ! "$D" exec -i "$restore" pg_restore --exit-on-error --create -h /tmp -p 55432 -U postgres -d postgres <"$dump" >/dev/null 2>&1; then echo RESTORE_FAILED; exit 1; fi
test "$(fingerprint "$restore")" = "$original"; echo RESTORED_ALL_TABLE_FINGERPRINT_PASS
test "$(acl "$restore")" = "$orig_acl"; test "$(indexes "$restore")" = "$orig_index"; echo ACL_AND_INDEX_DEFINITION_PASS
test "$(rank "$restore")" = "$orig_rank"; echo VECTOR_TOP3_EQUAL_PASS
test "$(sql "$restore" "$NAME" "SELECT min(private_docs.vector_dims(embedding))=384 AND max(private_docs.vector_dims(embedding))=384 FROM private_docs.chunks")" = t
test "$(sql "$restore" "$NAME" "SELECT count(*) FROM pg_indexes WHERE schemaname='private_docs' AND indexdef LIKE '%USING hnsw%'")" = 1
test "$(sql "$restore" "$NAME" "SELECT count(*) FROM private_docs.section_sources s WHERE NOT EXISTS (SELECT 1 FROM private_docs.chunks c WHERE c.document_id=s.document_id AND c.section=s.section)")" = 0
echo DIMENSION_HNSW_SECTION_COVERAGE_PASS
test "$(sql "$restore" "$NAME" "SET ROLE patent_ingest_reader_v1; SELECT (SELECT count(*) FROM private_docs.readable_catalog)||'|'||(SELECT count(*) FROM private_docs.readable_evidence)")" = "$(sql "$DB" "$NAME" "SELECT (SELECT count(*) FROM private_docs.readable_catalog)||'|'||(SELECT count(*) FROM private_docs.readable_evidence)")"
for table in documents section_sources chunks; do
 if sql "$restore" "$NAME" "SET ROLE patent_ingest_reader_v1; SELECT count(*) FROM private_docs.$table" >/dev/null 2>&1; then exit 1; fi
 test "$(sql "$restore" "$NAME" "SELECT has_table_privilege('patent_ingest_writer_v1','private_docs.$table','SELECT') AND has_table_privilege('patent_ingest_writer_v1','private_docs.$table','INSERT') AND NOT has_table_privilege('patent_ingest_writer_v1','private_docs.$table','UPDATE') AND NOT has_table_privilege('patent_ingest_writer_v1','private_docs.$table','DELETE') AND NOT has_table_privilege('patent_ingest_reader_v1','private_docs.$table','INSERT')")" = t
done
test "$(sql "$restore" "$NAME" "SELECT NOT has_database_privilege('patent_app',current_database(),'CONNECT') AND has_database_privilege('patent_ingest_reader_v1',current_database(),'CONNECT') AND has_database_privilege('patent_ingest_writer_v1',current_database(),'CONNECT') AND NOT EXISTS(SELECT 1 FROM pg_database d CROSS JOIN LATERAL aclexplode(coalesce(d.datacl,acldefault('d',d.datdba))) a WHERE d.datname=current_database() AND a.grantee=0 AND a.privilege_type='CONNECT')")" = t
echo READER_VIEW_BASE_DENIED_WRITER_APPEND_ONLY_DB_ACL_PASS
sql "$restore" "$NAME" "SELECT (SELECT count(*) FROM private_docs.documents),(SELECT count(*) FROM private_docs.section_sources),(SELECT count(*) FROM private_docs.chunks), (SELECT extversion FROM pg_extension WHERE extname='vector')"
test "$(fingerprint "$DB")" = "$original" || { echo SOURCE_FINGERPRINT_CHANGED; exit 1; }
echo SOURCE_FINGERPRINT_UNCHANGED
test "$(acl "$DB")" = "$orig_acl" || { echo SOURCE_ACL_CHANGED; exit 1; }
test "$(indexes "$DB")" = "$orig_index" || { echo SOURCE_INDEX_CHANGED; exit 1; }
echo SOURCE_ACL_INDEX_UNCHANGED
test "$(states)" = "$before_states" || { echo EXISTING_CONTAINER_STATE_CHANGED; exit 1; }
echo EXISTING_CONTAINER_STATES_UNCHANGED
"$D" stop -t 5 "$restore" >/dev/null || { echo TEMP_STOP_FAILED; exit 1; }
restore=
n=0
while [ -n "$("$D" ps -aq --filter "label=$LABEL")" ]; do n=$((n+1)); [ "$n" -lt 20 ] || { echo TEMP_CLEANUP_TIMEOUT; exit 1; }; sleep 1; done
echo TEMP_CONTAINER_CLEANUP_PASS
python3 - "$dump" <<'PY'
import pathlib,hashlib,sys
p=pathlib.Path(sys.argv[1]); d=hashlib.sha256(p.read_bytes()).hexdigest()
out=p.with_suffix(".sha256")
with out.open("x") as f: f.write(d+"\n")
assert out.read_text().strip()==hashlib.sha256(p.read_bytes()).hexdigest()
print("LOCAL_BACKUP_SHA256_PASS")
PY
echo PRODUCTION_UNCHANGED_AND_TEMP_CLEANUP_PASS
