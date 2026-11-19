-- Additive migration only; no restart, no existing row rewrite.
BEGIN;
SET LOCAL lock_timeout='2s';
SET LOCAL statement_timeout='15s';
ALTER TABLE private_docs.chunks DROP CONSTRAINT chunks_section_check;
ALTER TABLE private_docs.chunks ADD CONSTRAINT chunks_section_check
 CHECK(section IN ('title','abstract','representative_claim','detailed_description','all_claims'));
CREATE TABLE private_docs.section_sources(
 document_id text NOT NULL REFERENCES private_docs.documents(id),
 section text NOT NULL CHECK(section IN ('detailed_description','all_claims')),
 provider text NOT NULL CHECK(provider='WIPS'),
 language text NOT NULL CHECK(language IN ('KR','US','JP','CN')),
 claim_count int NOT NULL CHECK(claim_count>=0),
 body text NOT NULL CHECK(length(body)>0),
 raw_payload jsonb NOT NULL,
 source_sha256 text NOT NULL CHECK(source_sha256 ~ '^[0-9a-f]{64}$'),
 body_sha256 text NOT NULL CHECK(body_sha256 ~ '^[0-9a-f]{64}$'),
 policy_id text NOT NULL CHECK(policy_id='owner-attested-paid-material-private-v1'),
 created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(document_id,section)
);
REVOKE ALL ON private_docs.section_sources FROM PUBLIC;
GRANT SELECT,INSERT ON private_docs.section_sources TO patent_ingest_writer_v1;
COMMIT;
