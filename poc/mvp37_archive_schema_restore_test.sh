#!/bin/sh
set -eu
umask 077
D=/usr/local/bin/docker
R=$TEST_ROOT
case "$R" in /tmp/patent-archive-test.*) ;; *) exit 1;; esac
test ! -L "$R"; test -d "$R/code"; test ! -e "$R/auth"; test -d "$WHEEL_ROOT"
DB=patent-rag-mcp-stage-db
API=patent-rag-mcp-stage-api
LABEL=patent-rag.test=archive-schema-restore-v1
test -z "$("$D" ps -aq --filter "label=$LABEL")"
di=$("$D" inspect "$DB" --format '{{.Image}}')
ai=$("$D" inspect "$API" --format '{{.Image}}')
test "$di" = sha256:b0108689bf51bd54d3129130967d4adf7ba58b395a9ff6653aa598b5fe7d7ba3
test "$ai" = sha256:183e5ad42322fea6f731433ae7f6be7498812b31d2eaf05537ffed838dd1ba7c
sqlsrc(){ "$D" exec "$DB" psql -X -qAt -v ON_ERROR_STOP=1 -h /tmp -p 55432 -U postgres -d patent_private_ingest_v1 -c "$1"; }
fp(){ sqlsrc "SELECT (SELECT count(*)||':'||md5(string_agg(md5(to_jsonb(d)::text),'|' ORDER BY id)) FROM private_docs.documents d)||'|'||(SELECT count(*)||':'||md5(string_agg(md5(to_jsonb(s)::text),'|' ORDER BY document_id,section)) FROM private_docs.section_sources s)||'|'||(SELECT count(*)||':'||md5(string_agg(md5(to_jsonb(c)::text),'|' ORDER BY document_id,section,start_offset)) FROM private_docs.chunks c)"; }
states(){ for id in $*; do "$D" inspect "$id" --format '{{.Id}} {{.State.StartedAt}} {{.State.Running}}'; done; }
existing=$("$D" ps -q); target=$("$D" ps -q --filter name=patent-rag)
initial=$(states $existing); target_initial=$(states $target); original=$(fp)
sqlsrc "SELECT count(*) FROM private_docs.readable_catalog;"
sqlsrc "SELECT count(*) FROM pg_namespace WHERE nspname='patent_archive';"
clone=; app=; recovered=
cleanup(){ if [ -n "$recovered" ]; then "$D" stop -t 5 "$recovered" >/dev/null 2>&1 || true; fi; if [ -n "$app" ]; then "$D" stop -t 5 "$app" >/dev/null 2>&1 || true; fi; if [ -n "$clone" ]; then "$D" stop -t 5 "$clone" >/dev/null 2>&1 || true; fi; }
trap cleanup EXIT
mkdir "$R/auth"
python3 -c 'import secrets,sys;open(sys.argv[1],"w").write(secrets.token_hex(32))' "$R/auth/archive_writer_password"
clone=$("$D" run --pull never -d --rm --label "$LABEL" --network none --read-only --cap-drop ALL --security-opt no-new-privileges --user postgres --memory 512m --cpu-shares 128 --tmpfs /tmp:rw,exec,nosuid,nodev,size=256m,mode=1777 --entrypoint bash "$di" -ec 'umask 077; export PGDATA=/tmp/test-pgdata; od -An -N24 -tx1 /dev/urandom | tr -d " \n" >/tmp/pw; initdb -D "$PGDATA" --username=postgres --auth-local=peer --auth-host=scram-sha-256 --pwfile=/tmp/pw --no-locale --encoding=UTF8 >/dev/null; rm /tmp/pw; exec postgres -D "$PGDATA" -h 127.0.0.1 -k /tmp -p 55432 -c shared_buffers=32MB -c max_connections=12')
n=0; until "$D" exec "$clone" pg_isready -q -h /tmp -p 55432; do n=$((n+1)); [ "$n" -lt 40 ] || exit 1; sleep 1; done
# Copy ONLY the current schema/ACL, never operating rows or credentials.
"$D" exec "$DB" pg_dump -Fc --schema-only -h /tmp -p 55432 -U postgres -d patent_private_ingest_v1 >"$R/schema.dump"
test -s "$R/schema.dump"
roles(){ "$D" exec "$1" psql -X -q -v ON_ERROR_STOP=1 -h /tmp -p 55432 -U postgres -d postgres -c 'CREATE ROLE patent_ingest_reader_v1 NOLOGIN NOINHERIT; CREATE ROLE patent_ingest_writer_v1 NOLOGIN NOINHERIT; CREATE ROLE patent_app NOLOGIN NOINHERIT;' >/dev/null; }
roles "$clone"
"$D" exec -i "$clone" pg_restore --exit-on-error --create -h /tmp -p 55432 -U postgres -d postgres <"$R/schema.dump" >/dev/null
echo ACTUAL_SCHEMA_ONLY_RESTORE_PASS
sql(){ "$D" exec -i "$clone" psql -X -q -v ON_ERROR_STOP=1 -h /tmp -p 55432 -U postgres -d patent_private_ingest_v1 "$@"; }
# Synthetic constraints-compatible records on the actual restored view definitions.
sql <<'SQL'
INSERT INTO private_docs.documents(id,source_sha256,source_payload,policy_id)
VALUES ('PAT-'||repeat('a',64),repeat('b',64),'{"XN_D":"10-2000-0000991","CC":"KR","KC_D":"A","TIK":"Synthetic One"}','owner-attested-paid-material-private-v1'),
('PAT-'||repeat('c',64),repeat('d',64),'{"XN_D":"10-2000-0000992","CC":"KR","KC_D":"A","TIK":"Synthetic Two"}','owner-attested-paid-material-private-v1');
INSERT INTO private_docs.chunks(document_id,section,start_offset,end_offset,content_sha256,body,model_id,embedding)
SELECT id,section,0,1,repeat('e',64),'x','intfloat/multilingual-e5-small@614241f622f53c4eeff9890bdc4f31cfecc418b3',
('['||array_to_string(array_fill(1,ARRAY[384]),',')||']')::private_docs.vector
FROM (VALUES ('PAT-'||repeat('a',64),'all_claims'),('PAT-'||repeat('a',64),'detailed_description'),('PAT-'||repeat('c',64),'detailed_description')) t(id,section);
SQL
sql < "$R/code/mvp37_archive.sql"
python3 - "$R/auth/archive_writer_password" <<'PY' | sql >/dev/null
import pathlib,sys,re
pw=pathlib.Path(sys.argv[1]).read_text(); assert re.fullmatch('[a-f0-9]{64}',pw)
print("ALTER ROLE patent_archive_writer_v1 LOGIN PASSWORD '"+pw+"';")
PY
PYTHONPATH="$R/code" PYTHONDONTWRITEBYTECODE=1 python3 - "$R" <<'PY'
import pathlib,sys,json
from mvp37_archive import prepare,POLICY
p=pathlib.Path(sys.argv[1])
packet={"query":"isolated CLI fixture","page":1,"page_size":3,"response":{"success":True,"data":{"total_count":12,"row_list":[{"SKEY":"1201","CC":"KR","XN_D":"10-2000-0001201","KC_D":"A","TIK":"Synthetic CLI"}]}}}
h,_,_=prepare(packet)
(p/"auth"/"archive_policy.json").write_text(json.dumps({"policy":POLICY,"purpose":"metadata_only","approved_batches":[h],"max_rows":1}))
(p/"packet.json").write_text(json.dumps(packet))
PY
app=$("$D" run --pull never -d --rm --label "$LABEL" --network "container:$clone" --read-only --cap-drop ALL --security-opt no-new-privileges --user "$(id -u):$(id -g)" --memory 512m --cpu-shares 128 --tmpfs /tmp:rw,exec,nosuid,nodev,size=250m -e HOME=/tmp -e PYTHONDONTWRITEBYTECODE=1 -v "$R/code:/code:ro" -v "$R/auth:/auth:ro" -v "$WHEEL_ROOT:/wheels:ro" "$ai" sh -ec 'while [ ! -e /tmp/finish ]; do sleep 1; done')
"$D" exec "$app" sh -ec 'python -m pip install --disable-pip-version-check --no-index --no-cache-dir --find-links=/wheels --target /tmp/deps "psycopg[binary]==3.3.9" >/tmp/pip.log 2>&1; export PYTHONPATH=/tmp/deps; export TEST_DSN="host=127.0.0.1 port=55432 dbname=patent_private_ingest_v1 user=patent_archive_writer_v1 password=$(cat /auth/archive_writer_password)"; python /code/test_mvp37_archive.py'
r=$("$D" exec -i -e PYTHONPATH=/tmp/deps "$app" python /code/mvp37_archive_cli.py --archive <"$R/packet.json")
printf '%s' "$r" | python3 -c 'import json,sys;r=json.load(sys.stdin);assert r["status"]=="PASS" and r["saved"]==1 and r["body_writes"]==0; print("CLI_ARCHIVE_PASS")'
r=$("$D" exec -i -e PYTHONPATH=/tmp/deps "$app" python /code/mvp37_archive_cli.py --archive <"$R/packet.json")
printf '%s' "$r" | python3 -c 'import json,sys;r=json.load(sys.stdin);assert r["status"]=="REUSED_VERIFIED" and r["saved"]==0; print("CLI_REUSE_PASS")'
# Logical backup of the isolated migrated DB, then restore into a fresh cluster.
q(){ "$D" exec "$1" psql -X -qAt -v ON_ERROR_STOP=1 -h /tmp -p 55432 -U postgres -d patent_private_ingest_v1 -c "$2"; }
archive_fp(){ q "$1" "SELECT (SELECT count(*)||':'||md5(string_agg(md5(to_jsonb(t)::text),'|' ORDER BY identity)) FROM patent_archive.documents t)||'|'||(SELECT count(*)||':'||md5(string_agg(md5(to_jsonb(t)::text),'|' ORDER BY identity,metadata_sha256)) FROM patent_archive.metadata_revisions t)||'|'||(SELECT count(*)||':'||md5(string_agg(md5(to_jsonb(t)::text),'|' ORDER BY batch_sha256)) FROM patent_archive.search_pages t)||'|'||(SELECT count(*)||':'||md5(string_agg(md5(to_jsonb(t)::text),'|' ORDER BY batch_sha256,rank)) FROM patent_archive.page_hits t)"; }
check_acl(){ q "$1" "SELECT has_database_privilege('patent_archive_writer_v1',current_database(),'CONNECT') AND NOT EXISTS(SELECT 1 FROM pg_database d CROSS JOIN LATERAL aclexplode(coalesce(d.datacl,acldefault('d',d.datdba))) a WHERE d.datname=current_database() AND a.grantee=0 AND a.privilege_type='CONNECT') AND NOT has_schema_privilege('patent_archive_writer_v1','private_docs','USAGE') AND NOT has_schema_privilege('patent_ingest_reader_v1','patent_archive','USAGE') AND NOT has_schema_privilege('patent_ingest_writer_v1','patent_archive','USAGE') AND has_table_privilege('patent_archive_writer_v1','patent_archive.fulltext_status','SELECT') AND NOT has_table_privilege('patent_archive_writer_v1','patent_archive.fulltext_status','INSERT') AND NOT EXISTS(SELECT 1 FROM pg_tables t WHERE schemaname='patent_archive' AND (NOT has_table_privilege('patent_archive_writer_v1',format('%I.%I',schemaname,tablename),'SELECT') OR NOT has_table_privilege('patent_archive_writer_v1',format('%I.%I',schemaname,tablename),'INSERT') OR has_table_privilege('patent_archive_writer_v1',format('%I.%I',schemaname,tablename),'UPDATE') OR has_table_privilege('patent_archive_writer_v1',format('%I.%I',schemaname,tablename),'DELETE')))"; }
test "$(check_acl "$clone")" = t
echo MIGRATION_EXPLICIT_CONNECT_AND_ROLE_ISOLATION_PASS
before_archive=$(archive_fp "$clone")
test -n "$before_archive"
"$D" exec "$clone" pg_dump -Fc -h /tmp -p 55432 -U postgres -d patent_private_ingest_v1 >"$R/migrated.dump"
test -s "$R/migrated.dump"
recovered=$("$D" run --pull never -d --rm --label "$LABEL" --network none --read-only --cap-drop ALL --security-opt no-new-privileges --user postgres --memory 512m --cpu-shares 128 --tmpfs /tmp:rw,exec,nosuid,nodev,size=256m,mode=1777 --entrypoint bash "$di" -ec 'umask 077; export PGDATA=/tmp/restore-pgdata; od -An -N24 -tx1 /dev/urandom | tr -d " \n" >/tmp/pw; initdb -D "$PGDATA" --username=postgres --auth-local=peer --auth-host=scram-sha-256 --pwfile=/tmp/pw --no-locale --encoding=UTF8 >/dev/null; rm /tmp/pw; exec postgres -D "$PGDATA" -h 127.0.0.1 -k /tmp -p 55432 -c shared_buffers=32MB -c max_connections=12')
n=0; until "$D" exec "$recovered" pg_isready -q -h /tmp -p 55432; do n=$((n+1)); [ "$n" -lt 40 ] || exit 1; sleep 1; done
roles "$recovered"
"$D" exec "$recovered" psql -X -q -v ON_ERROR_STOP=1 -h /tmp -p 55432 -U postgres -d postgres -c 'CREATE ROLE patent_archive_writer_v1 NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS' >/dev/null
"$D" exec -i "$recovered" pg_restore --exit-on-error --create -h /tmp -p 55432 -U postgres -d postgres <"$R/migrated.dump" >/dev/null
test "$(archive_fp "$recovered")" = "$before_archive"
test "$(check_acl "$recovered")" = t
test "$(q "$recovered" "SET ROLE patent_archive_writer_v1; SELECT count(*) FILTER(WHERE has_description AND has_claims),count(*) FILTER(WHERE has_description AND NOT has_claims) FROM patent_archive.fulltext_status")" = '1|1'
echo MIGRATED_ARCHIVE_RESTORE_DATA_ACL_VIEW_PASS
"$D" stop -t 5 "$recovered" >/dev/null; recovered=
test "$(fp)" = "$original"; echo SOURCE_FINGERPRINT_UNCHANGED
test "$(states $target)" = "$target_initial"; echo PATENT_CONTAINERS_UNCHANGED
if [ "$(states $existing)" = "$initial" ]; then echo ALL_EXISTING_CONTAINERS_UNCHANGED; else echo OTHER_CONTAINER_STATE_DIFFERENCE_OBSERVED; fi
"$D" stop -t 5 "$app" >/dev/null; app=
"$D" stop -t 5 "$clone" >/dev/null; clone=
n=0; while [ -n "$("$D" ps -aq --filter "label=$LABEL")" ]; do n=$((n+1)); [ "$n" -lt 20 ] || exit 1; sleep 1; done
echo ISOLATED_ARCHIVE_CLEANUP_PASS
