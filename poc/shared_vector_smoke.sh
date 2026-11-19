#!/bin/bash
# Disposable synthetic pgvector integration test. Run only inside a new isolated container.
set -euo pipefail
umask 077
test "$(id -un)" = postgres
export PGDATA=/tmp/shared-vector-test
port=55432
pw() { od -An -N24 -tx1 /dev/urandom | tr -d ' \n'; }
admin_pw=$(pw)
patent_pw=$(pw)
study_pw=$(pw)
printf '%s\n' "$admin_pw" > /tmp/pg-init-pw
initdb -D "$PGDATA" --username=postgres --auth-local=peer --auth-host=scram-sha-256 --pwfile=/tmp/pg-init-pw --no-locale --encoding=UTF8 >/tmp/init.log
rm /tmp/pg-init-pw
start(){ pg_ctl -D "$PGDATA" -l /tmp/pg-test.log -o "-h 127.0.0.1 -k /tmp -p $port -c shared_buffers=32MB -c max_connections=12" -w start >/dev/null; }
stop(){ pg_ctl -D "$PGDATA" -m fast -w stop >/dev/null; }
trap 'pg_ctl -D "$PGDATA" -m fast -w stop >/dev/null 2>&1 || true' EXIT
start
admin(){ psql -X -qAt -v ON_ERROR_STOP=1 -h /tmp -p "$port" -U postgres "$@"; }
admin -d postgres -v p="$patent_pw" -v s="$study_pw" <<'SQL'
CREATE ROLE patent_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD :'p';
CREATE ROLE study_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD :'s';
CREATE DATABASE patent_demo;
CREATE DATABASE study_demo;
REVOKE ALL ON DATABASE patent_demo FROM PUBLIC;
REVOKE ALL ON DATABASE study_demo FROM PUBLIC;
GRANT CONNECT ON DATABASE patent_demo TO patent_app;
GRANT CONNECT ON DATABASE study_demo TO study_app;
SQL
for db in patent_demo study_demo; do
  role=patent_app
  if [ "$db" = study_demo ]; then role=study_app; fi
  admin -d "$db" -v role="$role" <<'SQL'
CREATE EXTENSION vector;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE TABLE documents (
    id text PRIMARY KEY CHECK(id LIKE 'DEMO-%'),
    body text NOT NULL,
    model_id text NOT NULL CHECK(model_id='synthetic-384-v1'),
    embedding vector(384) NOT NULL
);
GRANT SELECT,INSERT ON documents TO :"role";
CREATE INDEX documents_cosine_hnsw ON documents USING hnsw (embedding vector_cosine_ops);
SQL
done
run_as(){ local role=$1 db=$2 password=$3; shift 3; PGPASSWORD="$password" psql -X -qAt -v ON_ERROR_STOP=1 -h 127.0.0.1 -p "$port" -U "$role" -d "$db" "$@"; }
pat(){ run_as patent_app patent_demo "$patent_pw" "$@"; }
study(){ run_as study_app study_demo "$study_pw" "$@"; }
n=0
expect(){ local label=$1 got=$2 wanted=$3; if [ "$got" != "$wanted" ]; then echo "FAIL $label"; exit 1; fi; n=$((n+1)); echo "PASS $label"; }
deny(){ local label=$1 error_pattern=$2; shift 2; if "$@" >/tmp/deny.out 2>/tmp/deny.err; then echo "FAIL $label allowed"; exit 1; fi; if ! grep -Fq "$error_pattern" /tmp/deny.err; then echo "FAIL $label unexpected_error"; cat /tmp/deny.err; exit 1; fi; n=$((n+1)); echo "PASS $label"; }
expect version "$(admin -d patent_demo -c "SELECT extversion FROM pg_extension WHERE extname='vector'")" 0.8.7
pat <<'SQL'
INSERT INTO documents VALUES ('DEMO-P1','Synthetic conductor','synthetic-384-v1',(ARRAY[1::real,0::real]||array_fill(0::real,ARRAY[382]))::vector),
('DEMO-P2','Synthetic coating','synthetic-384-v1',(ARRAY[0.8::real,0.6::real]||array_fill(0::real,ARRAY[382]))::vector),
('DEMO-P3','Synthetic insulation','synthetic-384-v1',(ARRAY[0::real,1::real]||array_fill(0::real,ARRAY[382]))::vector);
SQL
study <<'SQL'
INSERT INTO documents VALUES ('DEMO-S1','Synthetic study topic','synthetic-384-v1',(ARRAY[1::real,0::real]||array_fill(0::real,ARRAY[382]))::vector);
SQL
expect patent_count "$(pat -c 'SELECT count(*) FROM documents')" 3
expect study_count "$(study -c 'SELECT count(*) FROM documents')" 1
expect exact_fetch "$(pat -c "SELECT body FROM documents WHERE id='DEMO-P1'")" 'Synthetic conductor'
expect vector_dimension "$(pat -c "SELECT vector_dims(embedding) FROM documents WHERE id='DEMO-P1'")" 384
expect cosine_order "$(pat -c "SELECT string_agg(id,',' ORDER BY distance) FROM (SELECT id,embedding <=> (ARRAY[1::real,0::real]||array_fill(0::real,ARRAY[382]))::vector AS distance FROM documents) q")" DEMO-P1,DEMO-P2,DEMO-P3
expect exact_distance "$(pat -c "SELECT embedding <=> embedding FROM documents WHERE id='DEMO-P1'")" 0
pat -c "INSERT INTO documents SELECT * FROM documents WHERE id='DEMO-P1' ON CONFLICT(id) DO NOTHING"
expect duplicate_count "$(pat -c 'SELECT count(*) FROM documents')" 3
expect no_study_leak "$(pat -c "SELECT count(*) FROM documents WHERE id='DEMO-S1'")" 0
deny cross_patent_to_study 'permission denied for database' run_as patent_app study_demo "$patent_pw" -c 'SELECT count(*) FROM documents'
deny cross_study_to_patent 'permission denied for database' run_as study_app patent_demo "$study_pw" -c 'SELECT count(*) FROM documents'
deny bad_password 'password authentication failed' run_as patent_app patent_demo "not-the-password" -c 'SELECT 1'
deny no_delete 'permission denied for table' pat -c "DELETE FROM documents WHERE id='DEMO-P1'"
deny no_update 'permission denied for table' study -c "UPDATE documents SET body='changed' WHERE id='DEMO-S1'"
deny no_ddl 'permission denied for schema' pat -c 'CREATE TABLE forbidden(id int)'
deny invalid_dimension 'expected 384 dimensions' pat -c "INSERT INTO documents VALUES ('DEMO-BAD','x','synthetic-384-v1','[1,2]')"
stop
start
expect restart_patent_count "$(pat -c 'SELECT count(*) FROM documents')" 3
expect restart_study_count "$(study -c 'SELECT count(*) FROM documents')" 1
echo "SHARED_VECTOR_SMOKE_PASS checks=$n"
echo 'Scope: ephemeral same cluster; SQL + synthetic vectors; MCP/real embeddings/production volumes NOT RUN'
