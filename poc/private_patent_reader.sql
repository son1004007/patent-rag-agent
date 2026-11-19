BEGIN;
CREATE SCHEMA IF NOT EXISTS private_docs;
CREATE ROLE patent_ingest_reader_v1 LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD :'pw';
GRANT CONNECT ON DATABASE patent_private_ingest_v1 TO patent_ingest_reader_v1;
ALTER ROLE patent_ingest_reader_v1 IN DATABASE patent_private_ingest_v1 SET default_transaction_read_only = on;
ALTER ROLE patent_ingest_reader_v1 IN DATABASE patent_private_ingest_v1 SET statement_timeout = '5s';
CREATE VIEW private_docs.readable_catalog WITH (security_barrier=true) AS
SELECT id,source_payload->>'XN_D' AS publication,source_payload->>'CC' AS country,source_payload->>'KC_D' AS kind,
left(source_payload->>'TIK',500) AS title,source_sha256
FROM private_docs.documents WHERE policy_id='owner-attested-paid-material-private-v1';
CREATE VIEW private_docs.readable_evidence WITH (security_barrier=true) AS
SELECT c.document_id,c.section,c.start_offset,least(c.end_offset,c.start_offset+300) AS end_offset,left(c.body,300) AS excerpt,c.content_sha256,c.model_id,c.embedding
FROM private_docs.chunks c JOIN private_docs.documents d ON d.id=c.document_id
WHERE d.policy_id='owner-attested-paid-material-private-v1';
REVOKE ALL ON private_docs.readable_catalog,private_docs.readable_evidence FROM PUBLIC;
GRANT USAGE ON SCHEMA private_docs TO patent_ingest_reader_v1;
GRANT SELECT ON private_docs.readable_catalog,private_docs.readable_evidence TO patent_ingest_reader_v1;
COMMIT;
