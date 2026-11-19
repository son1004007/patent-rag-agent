-- Owner-confirmed WIPS metadata-only per-search cap: 100 rows.
-- Additive check widening; no new data, role, credentials, service restart.
BEGIN;
SET LOCAL lock_timeout='2s';
SET LOCAL statement_timeout='15s';
DO $$
BEGIN
 IF current_database()<>'patent_private_ingest_v1' THEN RAISE EXCEPTION 'wrong database'; END IF;
 IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname='patent_archive') THEN RAISE EXCEPTION 'missing archive schema'; END IF;
 IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='patent_archive_writer_v1' AND NOT rolcanlogin AND NOT rolsuper AND NOT rolcreaterole) THEN RAISE EXCEPTION 'writer preflight'; END IF;
 IF (SELECT count(*) FROM patent_archive.search_pages)!=0 THEN RAISE EXCEPTION 'nonempty archive needs separate plan'; END IF;
END $$;
ALTER TABLE patent_archive.search_pages DROP CONSTRAINT search_pages_page_size_check;
ALTER TABLE patent_archive.search_pages ADD CONSTRAINT search_pages_page_size_check CHECK(page_size BETWEEN 1 AND 100);
ALTER TABLE patent_archive.page_hits DROP CONSTRAINT page_hits_rank_check;
ALTER TABLE patent_archive.page_hits ADD CONSTRAINT page_hits_rank_check CHECK(rank BETWEEN 1 AND 100);
COMMIT;
