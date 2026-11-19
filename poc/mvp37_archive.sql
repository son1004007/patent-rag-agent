-- Separate archive schema; apply only as approved DB administrator after backup.
-- Roles are deliberately NOLOGIN until scoped deployment/credential provisioning.
BEGIN;
CREATE ROLE patent_archive_writer_v1 NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE SCHEMA patent_archive;
REVOKE ALL ON SCHEMA patent_archive FROM PUBLIC;
CREATE TABLE patent_archive.documents(
 identity text PRIMARY KEY, skey text NOT NULL UNIQUE, country text NOT NULL,
 publication text NOT NULL, kind text NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE patent_archive.metadata_revisions(
 identity text REFERENCES patent_archive.documents(identity),
 metadata_sha256 text CHECK(length(metadata_sha256)=64),
 metadata jsonb NOT NULL CHECK(jsonb_typeof(metadata)='object'),
 created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(identity,metadata_sha256)
);
CREATE TABLE patent_archive.search_pages(
 batch_sha256 text PRIMARY KEY CHECK(length(batch_sha256)=64),
 query_sha256 text NOT NULL CHECK(length(query_sha256)=64),
 page int NOT NULL CHECK(page BETWEEN 1 AND 10000),
 page_size int NOT NULL CHECK(page_size BETWEEN 1 AND 50),
 total_count int NOT NULL CHECK(total_count>=0),
 returned_count int NOT NULL CHECK(returned_count BETWEEN 0 AND page_size),
 policy_id text NOT NULL CHECK(policy_id='owner-approved-wips-metadata-local-v1'),
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE patent_archive.page_hits(
 batch_sha256 text REFERENCES patent_archive.search_pages(batch_sha256),
 rank int CHECK(rank BETWEEN 1 AND 50), identity text NOT NULL,
 metadata_sha256 text NOT NULL, PRIMARY KEY(batch_sha256,rank),
 FOREIGN KEY(identity,metadata_sha256) REFERENCES patent_archive.metadata_revisions(identity,metadata_sha256)
);
CREATE VIEW patent_archive.fulltext_status WITH (security_barrier=true) AS
SELECT d.publication,d.country,d.kind,
 EXISTS(SELECT 1 FROM private_docs.readable_evidence e WHERE e.document_id=d.id AND e.section='detailed_description') AS has_description,
 EXISTS(SELECT 1 FROM private_docs.readable_evidence e WHERE e.document_id=d.id AND e.section='all_claims') AS has_claims
FROM private_docs.readable_catalog d;
REVOKE ALL ON ALL TABLES IN SCHEMA patent_archive FROM PUBLIC;
GRANT USAGE ON SCHEMA patent_archive TO patent_archive_writer_v1;
GRANT SELECT,INSERT ON patent_archive.documents,patent_archive.metadata_revisions,patent_archive.search_pages,patent_archive.page_hits TO patent_archive_writer_v1;
GRANT SELECT ON patent_archive.fulltext_status TO patent_archive_writer_v1;
COMMIT;
