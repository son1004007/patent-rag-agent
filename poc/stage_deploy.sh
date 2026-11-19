#!/bin/sh
# First deployment only: private local synthetic MCP stage. No existing volume mounts or public ports.
set -eu
umask 077
D=/usr/local/bin/docker
ROOT="$HOME/impe-rag"
M="$ROOT/models/multilingual-e5-small-614241f"
W="$ROOT/api-runtime-v1/wheels"
BASE=/volume1/docker/patent-rag-agent/mcp-stage-v1
VOL=patent-rag-mcp-stage-v1
LABEL=patent-rag.stage=mcp-v1
test ! -e "$BASE"
test -z "$("$D" ps -aq --filter "label=$LABEL")"
if "$D" volume inspect "$VOL" >/dev/null 2>&1;then echo EXISTING_VOLUME;exit 1;fi
before=$("$D" ps -q)
mkdir -m 700 "$BASE"
mkdir -m 700 "$BASE/code" "$BASE/secrets" "$BASE/backups"
python3 -c 'import json,sys,pathlib,secrets
p=pathlib.Path(sys.argv[1])
bundle=json.load(sys.stdin)
assert set(bundle)=={"stage_service.py","stage_http_test.py"}
for name,content in bundle.items():
    compile(content,name,"exec")
    (p/"code"/name).write_text(content,encoding="utf-8")
for name in ("db_password","mcp_token"):
    (p/"secrets"/name).write_text(secrets.token_hex(32))
print("SOURCE_SYNTAX_AND_LOCAL_SECRET_SETUP_PASS")' "$BASE"
db=
app=
success=0
cleanup(){ if [ "$success" = 0 ];then
    [ -z "$app" ] || "$D" stop -t 5 "$app" >/dev/null 2>&1 || true
    [ -z "$db" ] || "$D" stop -t 5 "$db" >/dev/null 2>&1 || true
    echo STAGE_STOPPED_ON_FAILURE
fi; }
trap cleanup EXIT
"$D" volume create --label "$LABEL" "$VOL" >/dev/null
db=$("$D" run --pull never -d --name patent-rag-mcp-stage-db --label "$LABEL" --network none --read-only --cap-drop ALL --security-opt no-new-privileges --user postgres --memory 512m --cpu-shares 128 --tmpfs /tmp:rw,exec,nosuid,nodev,size=128m,mode=1777 --mount "type=volume,src=$VOL,dst=/var/lib/postgresql/data" --entrypoint bash sha256:b0108689bf51bd54d3129130967d4adf7ba58b395a9ff6653aa598b5fe7d7ba3 -ec 'umask 077; export PGDATA=/var/lib/postgresql/data/stage; if [ ! -s "$PGDATA/PG_VERSION" ];then od -An -N24 -tx1 /dev/urandom | tr -d " \n" >/tmp/pw; initdb -D "$PGDATA" --username=postgres --auth-local=peer --auth-host=scram-sha-256 --pwfile=/tmp/pw --no-locale --encoding=UTF8 >/dev/null; rm /tmp/pw;fi; exec postgres -D "$PGDATA" -h 127.0.0.1 -k /tmp -p 55432 -c shared_buffers=32MB -c max_connections=12')
waitdb(){ n=0; until "$D" exec "$db" pg_isready -q -h /tmp -p 55432;do n=$((n+1));[ "$n" -lt 40 ] || exit 1;sleep 1;done; }
waitdb
admin(){ "$D" exec -i "$db" psql -X -qAt -v ON_ERROR_STOP=1 -h /tmp -p 55432 -U postgres "$@"; }
password=$(cat "$BASE/secrets/db_password")
admin -d postgres <<SQL
CREATE ROLE patent_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD '$password';
CREATE DATABASE patent_demo;
REVOKE ALL ON DATABASE patent_demo FROM PUBLIC;
GRANT CONNECT ON DATABASE patent_demo TO patent_app;
SQL
unset password
admin -d patent_demo <<'SQL'
CREATE EXTENSION vector;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE TABLE documents (id text PRIMARY KEY CHECK(id LIKE 'DEMO-P%'),body text NOT NULL,model_id text NOT NULL CHECK(model_id='intfloat/multilingual-e5-small@614241f622f53c4eeff9890bdc4f31cfecc418b3'),embedding vector(384) NOT NULL);
GRANT SELECT,INSERT ON documents TO patent_app;
CREATE INDEX documents_hnsw ON documents USING hnsw (embedding vector_cosine_ops);
SQL
echo DB_PROVISION_PASS
app=$("$D" run --pull never -d --name patent-rag-mcp-stage-api --label "$LABEL" --network "container:$db" --read-only --cap-drop ALL --security-opt no-new-privileges --user "$(id -u):$(id -g)" --memory 3g --cpu-shares 128 --tmpfs /tmp:rw,exec,nosuid,nodev,size=450m -e HOME=/tmp -e OPENBLAS_NUM_THREADS=1 -e TOKENIZERS_PARALLELISM=false -e PYTHONDONTWRITEBYTECODE=1 -v "$BASE/code:/code:ro" -v "$BASE/secrets:/secrets:ro" -v "$M:/model:ro" -v "$W:/wheels:ro" sha256:183e5ad42322fea6f731433ae7f6be7498812b31d2eaf05537ffed838dd1ba7c sh -ec 'python -m pip install --disable-pip-version-check --no-index --no-cache-dir --find-links=/wheels --target /tmp/deps mcp==1.30.0 httpx==0.28.1 "psycopg[binary]==3.3.9" onnxruntime==1.20.1 numpy==1.26.4 tokenizers==0.21.4 uvicorn==0.54.0 >/dev/null; PYTHONPATH=/tmp/deps exec python /code/stage_service.py')
"$D" exec "$app" python /code/stage_http_test.py initial
fingerprint(){ admin -d "$1" -c "SELECT count(*)||'|'||md5(string_agg(id||body||model_id||embedding::text,'|' ORDER BY id)) FROM documents"; }
orig=$(fingerprint patent_demo)
test "${orig%%|*}" = 3
"$D" exec "$db" pg_dump -Fc -h /tmp -p 55432 -U postgres -d patent_demo > "$BASE/backups/patent-demo.dump"
test -s "$BASE/backups/patent-demo.dump"
admin -d postgres <<'SQL'
CREATE DATABASE restore_probe;
REVOKE ALL ON DATABASE restore_probe FROM PUBLIC;
SQL
"$D" exec -i "$db" pg_restore --exit-on-error --no-acl -h /tmp -p 55432 -U postgres -d restore_probe < "$BASE/backups/patent-demo.dump"
test "$(fingerprint restore_probe)" = "$orig"
admin -d postgres -c 'DROP DATABASE restore_probe'
echo BACKUP_RESTORE_FINGERPRINT_PASS
"$D" stop -t 10 "$app" >/dev/null
"$D" restart -t 10 "$db" >/dev/null
waitdb
"$D" start "$app" >/dev/null
"$D" exec "$app" python /code/stage_http_test.py restart
test "$(fingerprint patent_demo)" = "$orig"
echo RESTART_FINGERPRINT_PASS
for c in "$db" "$app";do
  test "$("$D" inspect "$c" --format '{{.State.Running}}')" = true
  test "$("$D" inspect "$c" --format '{{len .HostConfig.PortBindings}}')" = 0
done
for c in $before;do test "$("$D" inspect "$c" --format '{{.State.Running}}')" = true;done
success=1
echo PRIVATE_STAGE_RUNNING_NO_PUBLISHED_PORTS
echo 'Manual startup order DB then API; daemon reboot and external ChatGPT are NOT RUN'
