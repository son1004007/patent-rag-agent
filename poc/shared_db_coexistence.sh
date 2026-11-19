#!/bin/bash
# Synthetic coexistence rehearsal only; run inside disposable network-none PostgreSQL container.
# Only the approved synthetic patent archive is mounted read-only; never mount study data.
set -euo pipefail
umask 077
test "$(id -un)" = postgres
test -f /fixture/patent.dump
export PGDATA=/tmp/shared-pg
port=55432
pw(){ od -An -N24 -tx1 /dev/urandom | tr -d ' \n'; }
pw >/tmp/init-pw
initdb -D "$PGDATA" --username=postgres --auth-local=peer --auth-host=scram-sha-256 --pwfile=/tmp/init-pw --no-locale --encoding=UTF8 >/dev/null
rm /tmp/init-pw
pg_ctl -D "$PGDATA" -l /tmp/pg.log -o "-h 127.0.0.1 -k /tmp -p $port -c shared_buffers=32MB -c max_connections=16" -w start >/dev/null
trap 'pg_ctl -D "$PGDATA" -m fast -w stop >/dev/null 2>&1 || true' EXIT
admin(){ psql -X -qAt -v ON_ERROR_STOP=1 -h /tmp -p "$port" -U postgres "$@"; }
p=$(pw); s=$(pw)
admin -d postgres -v p="$p" -v s="$s" <<'SQL'
CREATE ROLE patent_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD :'p';
CREATE ROLE study_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD :'s';
SQL
pg_restore --exit-on-error --create -h /tmp -p "$port" -U postgres -d postgres /fixture/patent.dump
admin -d postgres <<'SQL'
CREATE DATABASE study_demo;
REVOKE ALL ON DATABASE study_demo FROM PUBLIC;
GRANT CONNECT ON DATABASE study_demo TO study_app;
SQL
admin -d study_demo <<'SQL'
CREATE SCHEMA study;
REVOKE ALL ON SCHEMA study FROM PUBLIC;
CREATE EXTENSION vector WITH SCHEMA study;
CREATE TABLE study.notes(id int PRIMARY KEY, title text NOT NULL, embedding study.vector(384) NOT NULL);
CREATE TABLE study.private_chunks(id int PRIMARY KEY, body text NOT NULL);
INSERT INTO study.private_chunks VALUES (1,'synthetic sentinel: do not return');
-- Generated numerical fixtures, not real embeddings or study materials.
INSERT INTO study.notes SELECT i,'synthetic study topic '||i,
 ARRAY(SELECT sin((i*17+j*13)::double precision)::real FROM generate_series(1,384) j)::study.vector
 FROM generate_series(1,512) i;
CREATE INDEX study_notes_hnsw ON study.notes USING hnsw (embedding study.vector_cosine_ops);
CREATE VIEW study.allowed_notes AS SELECT id,title,embedding FROM study.notes;
GRANT USAGE ON SCHEMA study TO study_app;
GRANT SELECT ON study.allowed_notes TO study_app;
REVOKE ALL ON study.private_chunks,study.notes FROM PUBLIC,study_app;
ANALYZE study.notes;
SQL
admin -d patent_demo <<'SQL'
CREATE TABLE bench_vectors(id int PRIMARY KEY, embedding vector(384) NOT NULL);
INSERT INTO bench_vectors SELECT i, ARRAY(SELECT cos((i*17+j*13)::double precision)::real FROM generate_series(1,384) j)::vector
 FROM generate_series(1,512) i;
CREATE INDEX bench_vectors_hnsw ON bench_vectors USING hnsw (embedding vector_cosine_ops);
GRANT SELECT ON bench_vectors TO patent_app;
ANALYZE bench_vectors;
SQL
as_role(){ local db=$1 role=$2 password=$3;shift 3;PGPASSWORD="$password" psql -X -qAt -v ON_ERROR_STOP=1 -h 127.0.0.1 -p "$port" -U "$role" -d "$db" "$@"; }
pat(){ as_role patent_demo patent_app "$p" "$@"; }
study(){ as_role study_demo study_app "$s" "$@"; }
n=0
pass(){ n=$((n+1));echo "PASS $1"; }
expect(){ if [ "$2" != "$3" ];then echo "FAIL $1";exit 1;fi;pass "$1"; }
deny(){ local label=$1 pattern=$2;shift 2;if "$@" >/tmp/deny.out 2>/tmp/deny.err;then echo "FAIL $label allowed";exit 1;fi;if ! grep -Fq "$pattern" /tmp/deny.err;then echo "FAIL $label unexpected_error";exit 1;fi;pass "$label"; }
fp_pat(){ admin -d "$1" -c "SELECT count(*)||'|'||md5(string_agg(md5(json_build_array(id,body,model_id,embedding::text)::text),'|' ORDER BY id)) FROM documents"; }
fp_study(){ admin -d "$1" -c "SELECT count(*)||'|'||md5(string_agg(md5(json_build_array(id,title,embedding::text)::text),'|' ORDER BY id)) FROM study.notes"; }
a=$(fp_pat patent_demo); b=$(fp_study study_demo)
expect patent_count "$(pat -c 'SELECT count(*) FROM documents')" 4
expect patent_p4_vector "$(pat -c "SELECT vector_dims(embedding) FROM documents WHERE id='DEMO-P4'")" 384
expect study_count "$(study -c 'SELECT count(*) FROM study.allowed_notes')" 512
expect study_dimension "$(study -c 'SELECT study.vector_dims(embedding) FROM study.allowed_notes LIMIT 1')" 384
expect patent_bench_count "$(pat -c 'SELECT count(*) FROM bench_vectors')" 512
deny patent_cross_db 'permission denied for database' as_role study_demo patent_app "$p" -c 'SELECT 1'
deny study_cross_db 'permission denied for database' as_role patent_demo study_app "$s" -c 'SELECT 1'
deny study_private 'permission denied for table' study -c 'SELECT * FROM study.private_chunks'
deny study_base 'permission denied for table' study -c 'SELECT * FROM study.notes'
deny study_view_write 'permission denied for view' study -c "UPDATE study.allowed_notes SET title='blocked' WHERE id=1"
deny study_schema_ddl 'permission denied for schema' study -c 'CREATE TABLE study.blocked(id int)'
deny patent_delete 'permission denied for table' pat -c "DELETE FROM documents WHERE id='DEMO-P1'"
deny wrong_password 'password authentication failed' as_role study_demo study_app 'incorrect-test-password' -c 'SELECT 1'
expect patent_exact_knn "$(pat -c "SELECT id FROM bench_vectors ORDER BY embedding <=> (SELECT embedding FROM bench_vectors WHERE id=42) LIMIT 1")" 42
expect study_exact_knn "$(study -c "SELECT id FROM study.allowed_notes ORDER BY embedding OPERATOR(study.<=>) (SELECT embedding FROM study.allowed_notes WHERE id=42) LIMIT 1")" 42
# Deterministic 400 read-only vector transactions: 2 clients each domain, 100 tx/client.
cat >/tmp/pat.bench <<'SQL'
\set x random(1,512)
SELECT id FROM bench_vectors ORDER BY embedding <=> (SELECT embedding FROM bench_vectors WHERE id=:x) LIMIT 5;
SQL
cat >/tmp/study.bench <<'SQL'
\set x random(1,512)
SELECT id FROM study.allowed_notes ORDER BY embedding OPERATOR(study.<=>) (SELECT embedding FROM study.allowed_notes WHERE id=:x) LIMIT 5;
SQL
PGPASSWORD="$p" pgbench -n -h 127.0.0.1 -p "$port" -U patent_app -d patent_demo -c 2 -j 2 -t 100 -f /tmp/pat.bench >/tmp/pat.out 2>&1 & pa=$!
PGPASSWORD="$s" pgbench -n -h 127.0.0.1 -p "$port" -U study_app -d study_demo -c 2 -j 2 -t 100 -f /tmp/study.bench >/tmp/study.out 2>&1 & sa=$!
rc=0;wait "$pa" || rc=1;wait "$sa" || rc=1
for domain in pat study;do
 echo "BENCHMARK $domain"
 grep -E '^number of transactions actually processed:|^number of failed transactions:|^latency average =|^tps =' "/tmp/$domain.out" || true
 grep -Eq '^number of transactions actually processed: 200/200' "/tmp/$domain.out" || exit 1
 grep -Eq '^number of failed transactions: 0([[:space:]]|$)' "/tmp/$domain.out" || exit 1
done
test "$rc" = 0
pass simultaneous_400_queries
expect patent_unchanged "$(fp_pat patent_demo)" "$a"
expect study_unchanged "$(fp_study study_demo)" "$b"
# Each database can be recovered independently. Restore into new database names
# in this disposable cluster, not onto the live DB.
for db in patent_demo study_demo;do
 pg_dump -Fc -h /tmp -p "$port" -U postgres -d "$db" >"/tmp/$db.dump"
 admin -d postgres -c "CREATE DATABASE ${db}_recovery"
 admin -d postgres -c "REVOKE ALL ON DATABASE ${db}_recovery FROM PUBLIC"
 pg_restore --exit-on-error -h /tmp -p "$port" -U postgres -d "${db}_recovery" "/tmp/$db.dump"
done
expect patent_restore "$(fp_pat patent_demo_recovery)" "$a"
expect study_restore "$(fp_study study_demo_recovery)" "$b"
expect restored_study_view_acl "$(admin -d study_demo_recovery -c "SELECT has_table_privilege('study_app','study.allowed_notes','SELECT') AND NOT has_table_privilege('study_app','study.private_chunks','SELECT') AND NOT has_table_privilege('study_app','study.allowed_notes','UPDATE')")" t
expect restored_patent_acl "$(admin -d patent_demo_recovery -c "SELECT has_table_privilege('patent_app','documents','INSERT') AND NOT has_table_privilege('patent_app','documents','DELETE')")" t
expect study_restore_index "$(admin -d study_demo_recovery -c "SELECT count(*) FROM pg_indexes WHERE schemaname='study' AND indexname='study_notes_hnsw'")" 1
expect patent_restore_index "$(admin -d patent_demo_recovery -c "SELECT count(*) FROM pg_indexes WHERE indexname='documents_hnsw'")" 1
echo "SHARED_DB_COEXISTENCE_PASS checks=$n"
echo "Scope: synthetic dual DB rehearsal, no technical study data, no existing service restarts, no production cutover."
