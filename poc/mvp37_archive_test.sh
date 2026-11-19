#!/bin/sh
set -eu
umask 077
D=/usr/local/bin/docker
R=$TEST_ROOT
case "$R" in /tmp/patent-archive-test.*) ;; *) exit 1;; esac
test ! -L "$R"; test -d "$R/code"; test ! -e "$R/auth"; test -d "$WHEEL_ROOT"
DB=patent-rag-mcp-stage-db
API=patent-rag-mcp-stage-api
LABEL=patent-rag.test=archive-isolated-v1
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
clone=; app=
cleanup(){ if [ -n "$app" ]; then "$D" stop -t 5 "$app" >/dev/null 2>&1 || true; fi; if [ -n "$clone" ]; then "$D" stop -t 5 "$clone" >/dev/null 2>&1 || true; fi; }
trap cleanup EXIT
mkdir "$R/auth"
python3 -c 'import secrets,sys;open(sys.argv[1],"w").write(secrets.token_hex(32))' "$R/auth/archive_writer_password"
clone=$("$D" run --pull never -d --rm --label "$LABEL" --network none --read-only --cap-drop ALL --security-opt no-new-privileges --user postgres --memory 512m --cpu-shares 128 --tmpfs /tmp:rw,exec,nosuid,nodev,size=256m,mode=1777 --entrypoint bash "$di" -ec 'umask 077; export PGDATA=/tmp/test-pgdata; od -An -N24 -tx1 /dev/urandom | tr -d " \n" >/tmp/pw; initdb -D "$PGDATA" --username=postgres --auth-local=peer --auth-host=scram-sha-256 --pwfile=/tmp/pw --no-locale --encoding=UTF8 >/dev/null; rm /tmp/pw; exec postgres -D "$PGDATA" -h 127.0.0.1 -k /tmp -p 55432 -c shared_buffers=32MB -c max_connections=12')
n=0; until "$D" exec "$clone" pg_isready -q -h /tmp -p 55432; do n=$((n+1)); [ "$n" -lt 40 ] || exit 1; sleep 1; done
"$D" exec "$clone" createdb -h /tmp -p 55432 -U postgres patent_private_ingest_v1
sql(){ "$D" exec -i "$clone" psql -X -q -v ON_ERROR_STOP=1 -h /tmp -p 55432 -U postgres -d patent_private_ingest_v1 "$@"; }
# Mirror only the production reader-view column contract with synthetic fixtures.
sql <<'SQL'
CREATE SCHEMA private_docs;
REVOKE ALL ON SCHEMA private_docs FROM PUBLIC;
CREATE TABLE private_docs.catalog_fixture(id text,publication text,country text,kind text);
CREATE TABLE private_docs.evidence_fixture(document_id text,section text);
INSERT INTO private_docs.catalog_fixture VALUES ('one','10-2000-0000991','KR','A'),('two','10-2000-0000992','KR','A');
INSERT INTO private_docs.evidence_fixture VALUES ('one','all_claims'),('one','detailed_description'),('two','detailed_description');
CREATE VIEW private_docs.readable_catalog AS SELECT * FROM private_docs.catalog_fixture;
CREATE VIEW private_docs.readable_evidence AS SELECT * FROM private_docs.evidence_fixture;
REVOKE ALL ON ALL TABLES IN SCHEMA private_docs FROM PUBLIC;
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
test "$(fp)" = "$original"; echo SOURCE_FINGERPRINT_UNCHANGED
test "$(states $target)" = "$target_initial"; echo PATENT_CONTAINERS_UNCHANGED
if [ "$(states $existing)" = "$initial" ]; then echo ALL_EXISTING_CONTAINERS_UNCHANGED; else echo OTHER_CONTAINER_STATE_DIFFERENCE_OBSERVED; fi
"$D" stop -t 5 "$app" >/dev/null; app=
"$D" stop -t 5 "$clone" >/dev/null; clone=
n=0; while [ -n "$("$D" ps -aq --filter "label=$LABEL")" ]; do n=$((n+1)); [ "$n" -lt 20 ] || exit 1; sleep 1; done
echo ISOLATED_ARCHIVE_CLEANUP_PASS
