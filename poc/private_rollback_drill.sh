#!/bin/sh
# Isolated three-phase HTTP rollback drill. Production containers are never stopped.
set -eu
umask 077
D=/usr/local/bin/docker
B=$STAGE_ROOT
M=$MODEL_ROOT
W=$WHEEL_ROOT
DB=patent-rag-mcp-stage-db
API=patent-rag-mcp-stage-api
LABEL=patent-rag.test=rollback-v1
test -z "$("$D" ps -aq --filter "label=$LABEL")"
test "$("$D" inspect "$DB" --format '{{.State.Running}} {{.HostConfig.NetworkMode}}')" = 'true none'
test -d "$M"; test -d "$W"
dbimage=$("$D" inspect "$DB" --format '{{.Image}}')
apiimage=$("$D" inspect "$API" --format '{{.Image}}')
test "$dbimage" = sha256:b0108689bf51bd54d3129130967d4adf7ba58b395a9ff6653aa598b5fe7d7ba3
test "$apiimage" = sha256:183e5ad42322fea6f731433ae7f6be7498812b31d2eaf05537ffed838dd1ba7c
before=$("$D" ps -q)
states(){ for id in $before; do "$D" inspect "$id" --format '{{.Id}} {{.State.StartedAt}} {{.State.Running}}'; done; }
orig_states=$(states)
sql(){ "$D" exec "$1" psql -X -qAt -v ON_ERROR_STOP=1 -h /tmp -p 55432 -U postgres -d "$2" -c "$3"; }
fingerprint(){ sql "$1" patent_private_ingest_v1 "SELECT (SELECT count(*)||':'||md5(string_agg(md5(to_jsonb(d)::text),'|' ORDER BY id)) FROM private_docs.documents d)||'|'||(SELECT count(*)||':'||md5(string_agg(md5(to_jsonb(s)::text),'|' ORDER BY document_id,section)) FROM private_docs.section_sources s)||'|'||(SELECT count(*)||':'||md5(string_agg(md5(to_jsonb(c)::text),'|' ORDER BY document_id,section,start_offset)) FROM private_docs.chunks c)"; }
demo(){ sql "$1" patent_demo "SELECT count(*)||':'||md5(string_agg(md5(to_jsonb(d)::text),'|' ORDER BY id)) FROM documents d"; }
archive_state(){
 db=patent_private_ingest_v1
 present=$(sql "$1" "$db" "SELECT (to_regnamespace('patent_archive') IS NOT NULL)::int")
 if [ "$present" = 0 ]; then echo absent; return; fi
 test "$present" = 1
 sql "$1" "$db" "SELECT (SELECT count(*)||':'||coalesce(md5(string_agg(md5(to_jsonb(t)::text),'|' ORDER BY identity)),'empty') FROM patent_archive.documents t)||'|'||(SELECT count(*)||':'||coalesce(md5(string_agg(md5(to_jsonb(t)::text),'|' ORDER BY identity,metadata_sha256)),'empty') FROM patent_archive.metadata_revisions t)||'|'||(SELECT count(*)||':'||coalesce(md5(string_agg(md5(to_jsonb(t)::text),'|' ORDER BY batch_sha256)),'empty') FROM patent_archive.search_pages t)||'|'||(SELECT count(*)||':'||coalesce(md5(string_agg(md5(to_jsonb(t)::text),'|' ORDER BY batch_sha256,rank)),'empty') FROM patent_archive.page_hits t); SELECT coalesce(string_agg(c.relname||':'||c.relkind::text||':'||c.relowner::regrole::text||':'||coalesce(c.relacl::text,''),'|' ORDER BY c.relname),'') FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='patent_archive' AND c.relkind IN ('r','v'); SELECT coalesce(nspacl::text,'') FROM pg_namespace WHERE nspname='patent_archive'; SELECT coalesce(string_agg(indexdef,'|' ORDER BY indexname),'') FROM pg_indexes WHERE schemaname='patent_archive'; SELECT coalesce((SELECT pg_get_viewdef('patent_archive.fulltext_status'::regclass,true)),''); SELECT count(*)||':'||coalesce(md5(string_agg(md5(to_jsonb(v)::text),'|' ORDER BY country,publication,kind)),'empty') FROM patent_archive.fulltext_status v;"
}
archive_acl_ok(){
 db=patent_private_ingest_v1
 if [ "$(sql "$1" "$db" "SELECT (to_regnamespace('patent_archive') IS NOT NULL)::int")" = 0 ]; then return; fi
 test "$(sql "$1" "$db" "SELECT has_database_privilege('patent_archive_writer_v1',current_database(),'CONNECT') AND NOT EXISTS(SELECT 1 FROM pg_database d CROSS JOIN LATERAL aclexplode(coalesce(d.datacl,acldefault('d',d.datdba))) a WHERE d.datname=current_database() AND a.grantee=0 AND a.privilege_type='CONNECT') AND NOT has_schema_privilege('patent_archive_writer_v1','private_docs','USAGE') AND NOT has_schema_privilege('patent_ingest_reader_v1','patent_archive','USAGE') AND NOT has_schema_privilege('patent_ingest_writer_v1','patent_archive','USAGE') AND has_table_privilege('patent_archive_writer_v1','patent_archive.fulltext_status','SELECT') AND NOT has_table_privilege('patent_archive_writer_v1','patent_archive.fulltext_status','INSERT') AND NOT EXISTS(SELECT 1 FROM pg_tables t WHERE schemaname='patent_archive' AND (NOT has_table_privilege('patent_archive_writer_v1',format('%I.%I',schemaname,tablename),'SELECT') OR NOT has_table_privilege('patent_archive_writer_v1',format('%I.%I',schemaname,tablename),'INSERT') OR has_table_privilege('patent_archive_writer_v1',format('%I.%I',schemaname,tablename),'UPDATE') OR has_table_privilege('patent_archive_writer_v1',format('%I.%I',schemaname,tablename),'DELETE')))")" = t
}

orig_archive=$(archive_state "$DB"); archive_acl_ok "$DB"
orig=$(fingerprint "$DB"); origdemo=$(demo "$DB")
root=$(mktemp -d "$B/rollback-test.XXXXXX")
restore=
app=
cleanup(){
 if [ -n "$app" ]; then "$D" stop -t 5 "$app" >/dev/null 2>&1 || true; fi
 if [ -n "$restore" ]; then "$D" stop -t 5 "$restore" >/dev/null 2>&1 || true; fi
 if [ -n "$root" ] && [ -d "$root" ]; then rm -rf -- "$root"; fi
}
trap cleanup EXIT
mkdir "$root/code" "$root/secrets"
cp "$B/code/stage_service.before-unified.py" "$root/code/legacy.py"
cp "$B/code/stage_service.py" "$root/code/current.py"
cp "$B/code/unified_legacy_prod_test.py" "$root/code/legacy_test.py"
cp "$B/code/unified_reader_prod_test.py" "$root/code/reader_test.py"
python3 - "$root" <<'PY'
import sys,pathlib,secrets
p=pathlib.Path(sys.argv[1]); code=p/'code'
t=(code/'legacy_test.py').read_text()
old=',"search_patents","get_patent"'
assert t.count(old)==1
(code/'old_test.py').write_text(t.replace(old,''))
for name in ('db_password','reader_password','mcp_token','writer_password'):
    (p/'secrets'/name).write_text(secrets.token_hex(32))
for f in code.glob('*.py'): compile(f.read_text(),f.name,'exec')
print('EPHEMERAL_CODE_AND_CREDENTIALS_PASS')
PY
archive=$(python3 - "$B/backups" <<'PY'
import pathlib,stat,hashlib,sys
p=pathlib.Path(sys.argv[1]); a=sorted(p.glob('private-patent-mvp05-*.sha256')); assert a
x=a[-1]; d=x.with_suffix('.dump')
assert stat.S_IMODE(d.stat().st_mode)==0o600 and hashlib.sha256(d.read_bytes()).hexdigest()==x.read_text().strip()
print(d)
PY
)
"$D" exec "$DB" pg_dump -Fc -h /tmp -p 55432 -U postgres -d patent_demo >"$root/demo.dump"
test -s "$root/demo.dump"
restore=$("$D" run --pull never -d --rm --label "$LABEL" --network none --read-only --cap-drop ALL --security-opt no-new-privileges --user postgres --memory 512m --cpu-shares 128 --tmpfs /tmp:rw,exec,nosuid,nodev,size=256m,mode=1777 --entrypoint bash "$dbimage" -ec 'umask 077; export PGDATA=/tmp/restore-pgdata; od -An -N24 -tx1 /dev/urandom | tr -d " \n" >/tmp/pw; initdb -D "$PGDATA" --username=postgres --auth-local=peer --auth-host=scram-sha-256 --pwfile=/tmp/pw --no-locale --encoding=UTF8 >/dev/null; rm /tmp/pw; exec postgres -D "$PGDATA" -h 127.0.0.1 -k /tmp -p 55432 -c shared_buffers=32MB -c max_connections=12')
n=0; until "$D" exec "$restore" pg_isready -q -h /tmp -p 55432; do n=$((n+1)); [ "$n" -lt 40 ] || exit 1; sleep 1; done
# Test-only random credentials, never print SQL or mount original secrets.
python3 - "$root/secrets" <<'PY' | "$D" exec -i "$restore" psql -X -q -v ON_ERROR_STOP=1 -h /tmp -p 55432 -U postgres -d postgres >/dev/null 2>&1
import pathlib,sys,re
p=pathlib.Path(sys.argv[1])
for role,f in [('patent_app','db_password'),('patent_ingest_reader_v1','reader_password'),('patent_ingest_writer_v1','writer_password')]:
    pw=(p/f).read_text(); assert re.fullmatch('[a-f0-9]{64}',pw)
    print("CREATE ROLE "+role+" LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD '"+pw+"';")
print('ALTER ROLE patent_ingest_reader_v1 SET default_transaction_read_only=on;')
PY
if [ "$orig_archive" != absent ]; then sql "$restore" postgres 'CREATE ROLE patent_archive_writer_v1 NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS' >/dev/null; fi
for f in "$root/demo.dump" "$archive"; do
 if ! "$D" exec -i "$restore" pg_restore --exit-on-error --create -h /tmp -p 55432 -U postgres -d postgres <"$f" >/dev/null 2>&1; then echo RESTORE_FAILED; exit 1; fi
done
test "$(fingerprint "$restore")" = "$orig"; test "$(demo "$restore")" = "$origdemo"
test "$(archive_state "$restore")" = "$orig_archive"; archive_acl_ok "$restore"
echo BOTH_DATABASE_CLONES_MATCH
cat >"$root/code/drill.sh" <<'SH'
#!/bin/sh
set -eu
export PYTHONPATH=/tmp/deps
pid=
finish(){ if [ -n "$pid" ]; then kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; fi; }
trap finish EXIT
python -m pip install --disable-pip-version-check --no-index --no-cache-dir --find-links=/wheels --target /tmp/deps mcp==1.30.0 httpx==0.28.1 'psycopg[binary]==3.3.9' onnxruntime==1.20.1 numpy==1.26.4 tokenizers==0.21.4 uvicorn==0.54.0 >/tmp/pip.log 2>&1
phase(){
 name=$1; source=$2; testfile=$3
 python "/code/$source" >/tmp/api.log 2>&1 & pid=$!
 if ! python "/code/$testfile" restart >/tmp/check.log 2>&1; then grep -E '^PASS |^AssertionError: [a-z_]+$' /tmp/check.log || true; echo "$name FAILED"; exit 1; fi
 grep -E '^SOCKET_MCP_PASS checks=' /tmp/check.log
 if [ "$source" = current.py ]; then
   if ! python /code/reader_test.py >/tmp/check.log 2>&1; then grep -E '^PASS |^AssertionError: [a-z_]+$' /tmp/check.log || true; echo "$name READER_FAILED"; exit 1; fi
   grep -E '^PRIVATE_READER_MCP_PASS checks=' /tmp/check.log
 fi
 kill "$pid"; wait "$pid" || true; pid=
 echo "$name PASS"
}
phase CURRENT_BEFORE current.py legacy_test.py
phase LEGACY_ROLLBACK legacy.py old_test.py
phase CURRENT_RECOVERED current.py legacy_test.py
SH
app=$("$D" run --pull never -d --rm --label "$LABEL" --network "container:$restore" --read-only --cap-drop ALL --security-opt no-new-privileges --user "$(id -u):$(id -g)" --memory 3g --cpu-shares 128 --tmpfs /tmp:rw,exec,nosuid,nodev,size=450m -e HOME=/tmp -e OPENBLAS_NUM_THREADS=1 -e TOKENIZERS_PARALLELISM=false -e PYTHONDONTWRITEBYTECODE=1 -v "$root/code:/code:ro" -v "$root/secrets:/secrets:ro" -v "$M:/model:ro" -v "$W:/wheels:ro" "$apiimage" sh -ec 'while [ ! -e /tmp/finish ]; do sleep 1; done')
test "$("$D" inspect "$app" --format '{{len .HostConfig.PortBindings}} {{.HostConfig.ReadonlyRootfs}}')" = '0 true'
"$D" exec "$app" sh /code/drill.sh
test "$(fingerprint "$restore")" = "$orig"; test "$(demo "$restore")" = "$origdemo"
test "$(archive_state "$restore")" = "$orig_archive"; archive_acl_ok "$restore"
echo CLONE_DATA_UNCHANGED
test "$(fingerprint "$DB")" = "$orig"; test "$(demo "$DB")" = "$origdemo"; test "$(states)" = "$orig_states"
test "$(archive_state "$DB")" = "$orig_archive"; archive_acl_ok "$DB"
echo PRODUCTION_DATA_AND_CONTAINER_STATES_UNCHANGED
"$D" stop -t 5 "$app" >/dev/null; app=
"$D" stop -t 5 "$restore" >/dev/null; restore=
n=0; while [ -n "$("$D" ps -aq --filter "label=$LABEL")" ]; do n=$((n+1)); [ "$n" -lt 20 ] || exit 1; sleep 1; done
echo ROLLBACK_DRILL_AND_CLEANUP_PASS
