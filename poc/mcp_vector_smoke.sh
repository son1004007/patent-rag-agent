#!/bin/sh
# Run with synthetic Python source on stdin. No persistent DB or external port.
set -eu
D=/usr/local/bin/docker
ROOT="$HOME/impe-rag"
M="$ROOT/models/multilingual-e5-small-614241f"
R="$ROOT/api-runtime-v1"
W="$R/wheels"
LABEL=patent-rag.test=mcp-e5-v1
test -z "$("$D" ps -aq --filter "label=$LABEL")"
# Verify cached assets against previous approved manifest hashes.
python3 - "$M" "$R" <<'PY'
import pathlib,hashlib,json,sys
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()
m,r=map(pathlib.Path,sys.argv[1:])
for d,mf,expected,model in [(m,m/"manifest.json","ead3483744e926a83a3ea13d018c53873c49c655949f6678060455acd9877458",True),(r/"wheels",r/"manifest.json","04ba0397b6d1ab5ad3e15b9ceaa6b1aea241d2c392a06989018c39e96cd1d537",False)]:
    assert not d.is_symlink() and not mf.is_symlink() and sha(mf)==expected
    obj=json.loads(mf.read_text());rows=obj["files"] if model else obj
    for row in rows:
        name=row["file" if model else "filename"];assert pathlib.Path(name).name==name
        p=d/name;assert p.is_file() and not p.is_symlink() and p.stat().st_size==row["bytes"] and sha(p)==row["sha256"]
    if not model:assert {p.name for p in d.iterdir()}=={x["filename"] for x in rows}
print("ASSET_MANIFEST_PASS")
PY
before=$("$D" ps -q | sort)
db=
cleanup(){ if [ -n "$db" ];then "$D" stop -t 5 "$db" >/dev/null 2>&1 || true;fi; }
trap cleanup EXIT
db=$("$D" run --pull never -d --rm --label "$LABEL" --network none --read-only --cap-drop ALL --security-opt no-new-privileges --user postgres --memory 512m --cpu-shares 128 --tmpfs /tmp:rw,exec,nosuid,nodev,size=256m,mode=1777 --entrypoint bash sha256:b0108689bf51bd54d3129130967d4adf7ba58b395a9ff6653aa598b5fe7d7ba3 -ec 'umask 077; export PGDATA=/tmp/pgdata; od -An -N24 -tx1 /dev/urandom | tr -d " \n" >/tmp/pw; initdb -D "$PGDATA" --username=postgres --auth-local=peer --auth-host=scram-sha-256 --pwfile=/tmp/pw --no-locale --encoding=UTF8 >/dev/null; rm /tmp/pw; exec postgres -D "$PGDATA" -h 127.0.0.1 -k /tmp -p 55432 -c shared_buffers=32MB -c max_connections=12')
n=0
until "$D" exec "$db" pg_isready -q -h /tmp -p 55432; do n=$((n+1)); [ "$n" -lt 40 ] || exit 1; sleep 1; done
PATENT_TEST_PASSWORD=$(od -An -N24 -tx1 /dev/urandom | tr -d ' \n')
STUDY_TEST_PASSWORD=$(od -An -N24 -tx1 /dev/urandom | tr -d ' \n')
export PATENT_TEST_PASSWORD
admin(){ "$D" exec -i "$db" psql -X -qAt -v ON_ERROR_STOP=1 -h /tmp -p 55432 -U postgres "$@"; }
admin -d postgres <<SQL
CREATE ROLE patent_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD '$PATENT_TEST_PASSWORD';
CREATE ROLE study_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD '$STUDY_TEST_PASSWORD';
CREATE DATABASE patent_demo;
CREATE DATABASE study_demo;
REVOKE ALL ON DATABASE patent_demo FROM PUBLIC;
REVOKE ALL ON DATABASE study_demo FROM PUBLIC;
GRANT CONNECT ON DATABASE patent_demo TO patent_app;
GRANT CONNECT ON DATABASE study_demo TO study_app;
SQL
unset STUDY_TEST_PASSWORD
admin -d patent_demo <<'SQL'
CREATE EXTENSION vector;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE TABLE documents (id text PRIMARY KEY CHECK(id LIKE 'DEMO-P%'),body text NOT NULL,model_id text NOT NULL CHECK(model_id='intfloat/multilingual-e5-small@614241f622f53c4eeff9890bdc4f31cfecc418b3'),embedding vector(384) NOT NULL);
GRANT SELECT,INSERT ON documents TO patent_app;
CREATE INDEX documents_hnsw ON documents USING hnsw (embedding vector_cosine_ops);
SQL
admin -d study_demo <<'SQL'
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE TABLE documents(id text PRIMARY KEY,body text);
INSERT INTO documents VALUES ('DEMO-S1','Synthetic isolated study sentinel');
GRANT SELECT ON documents TO study_app;
SQL
"$D" run --pull never --rm -i --label "$LABEL" --network "container:$db" --read-only --cap-drop ALL --security-opt no-new-privileges --user "$(id -u):$(id -g)" --memory 3g --cpu-shares 128 --tmpfs /tmp:rw,exec,nosuid,nodev,size=450m -e HOME=/tmp -e OPENBLAS_NUM_THREADS=1 -e TOKENIZERS_PARALLELISM=false -e PYTHONDONTWRITEBYTECODE=1 -e PATENT_TEST_PASSWORD -v "$M:/model:ro" -v "$W:/wheels:ro" sha256:183e5ad42322fea6f731433ae7f6be7498812b31d2eaf05537ffed838dd1ba7c sh -ec 'python -m pip install --disable-pip-version-check --no-index --no-cache-dir --find-links=/wheels --target /tmp/deps mcp==1.30.0 httpx==0.28.1 "psycopg[binary]==3.3.9" onnxruntime==1.20.1 numpy==1.26.4 tokenizers==0.21.4 >/dev/null; PYTHONPATH=/tmp/deps python -'
unset PATENT_TEST_PASSWORD
test "$(admin -d patent_demo -c 'SELECT count(*) FROM documents')" = 3
test "$(admin -d study_demo -c 'SELECT count(*) FROM documents')" = 1
echo DB_POSTCHECK_PASS
cleanup
db=
n=0
while [ -n "$("$D" ps -aq --filter "label=$LABEL")" ];do n=$((n+1)); [ "$n" -lt 15 ] || exit 1; sleep 1;done
after=$("$D" ps -q | sort)
for id in $before;do printf '%s\n' "$after" | grep -qx "$id";done
echo CLEANUP_AND_EXISTING_CONTAINERS_PASS
