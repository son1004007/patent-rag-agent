"""Owner-operated, bounded one-shot patent ingest; never expose as an MCP tool.
Approval is provisioned by a trusted local operator, not accepted from a model.
Raw packet/approval must remain in a private local boundary.
"""
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

from private_patent_ingest import MODEL, POLICY, validate, digest
from private_patent_increment import sections, norm_num, canonical

CAP = 900000
APPROVAL = Path("/auth/ingest_approval.json")


def prepare(packet, approval):
    if not isinstance(packet, dict) or set(packet) != {"row", "sections"}:
        raise ValueError("packet scope")
    encoded = canonical(packet).encode("utf-8")
    if len(encoded) > CAP:
        raise ValueError("packet cap")
    if not isinstance(approval, dict) or set(approval) != {"policy", "packet_sha256", "mode"}:
        raise PermissionError("approval scope")
    if approval["policy"] != POLICY or approval["mode"] not in ("new", "enrich") or approval["packet_sha256"] != hashlib.sha256(encoded).hexdigest():
        raise PermissionError("approval mismatch")
    row = packet["row"]
    if not isinstance(row, dict) or not re.fullmatch(r"[0-9]{1,24}", row.get("SKEY", "")) or not re.fullmatch(r"[A-Z][A-Z0-9]{0,4}", row.get("KC_D", "")) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 ./-]{0,79}", row.get("XN_D", "")):
        raise ValueError("identity")
    doc, source_hash, _, _ = validate([row])[0]
    items = sections(packet["sections"])
    if len(items) != 2 or {x[3] for x in items} != {"detailed_description", "all_claims"}:
        raise ValueError("both sections required")
    for skey, country, number, name, lang, count, body, raw in items:
        if skey != row["SKEY"] or country != row["CC"] or norm_num(number) != norm_num(row["XN_D"]):
            raise ValueError("section identity")
    if len({x[4] for x in items}) != 1:
        raise ValueError("mixed language")
    return {"doc": doc, "source_hash": source_hash, "row": row, "items": items, "packet": packet, "mode": approval["mode"]}


def execute(packet, approval, backend, dry_run=False):
    plan = prepare(packet, approval)
    completed = []
    try:
        before = backend.snapshot(plan)
        if not before["exists"] and plan["mode"] == "enrich":
            raise ValueError("enrich target missing")
        if dry_run:
            return {"status": "DRY_RUN", "writes": 0, "exists": before["exists"], "sections": len(before["sections"])}
        if before["exists"] and len(before["sections"]) == 2:
            return {"status": "REUSED_VERIFIED", "writes": 0, "verified": True}
        if not before["exists"]:
            completed.append("metadata_attempted")
            backend.apply("metadata", [plan["row"]])
            mid = backend.snapshot(plan)
            if not mid["exists"]:
                raise ValueError("metadata not verified")
        else:
            mid = before
        missing = {"detailed_description", "all_claims"} - set(mid["sections"])
        if missing:
            rows = [r for r in packet["sections"] if {"dtl_desc": "detailed_description", "all_claim": "all_claims"}[r["response"]["section"]] in missing]
            completed.append("sections_attempted")
            backend.apply("sections", rows)
        after = backend.snapshot(plan)
        if not after["exists"] or set(after["sections"]) != {"detailed_description", "all_claims"}:
            raise ValueError("final verification incomplete")
        return {"status": "PASS", "verified": True, "writes": len(completed), "documentsAdded": int(not before["exists"]), "sectionsAdded": 2-len(before["sections"])}
    except Exception as exc:
        # Failed worker may have committed before its own post-check failed.
        # Do not blindly retry or claim rollback. Never print identifiers or source text.
        return {"status": "FAILED_OR_PARTIAL" if completed else "BLOCKED_PREFLIGHT", "attempted": completed, "error_type": type(exc).__name__, "verified": False}


class LocalBackend:
    """Uses existing scoped writer only; snapshots explicitly read-only.
    Operator must serialize *all* local writers; not a concurrent ingest service.
    """
    def snapshot(self, plan):
        import psycopg
        password = Path("/auth/writer_password").read_text().strip()
        row = plan["row"]
        with psycopg.connect(host="127.0.0.1", port=55432, dbname="patent_private_ingest_v1",
                             user="patent_ingest_writer_v1", password=password, connect_timeout=5,
                             options="-c default_transaction_read_only=on -c statement_timeout=10000 -c lock_timeout=2000") as c:
            found = c.execute("""SELECT id,source_sha256,source_payload,policy_id FROM private_docs.documents
                WHERE id=%s OR source_payload->>'SKEY'=%s OR
                (source_payload->>'CC'=%s AND source_payload->>'KC_D'=%s
                AND regexp_replace(upper(source_payload->>'XN_D'),'[^A-Z0-9]','','g')=%s)
                LIMIT 2""", (plan["doc"], row["SKEY"], row["CC"], row["KC_D"], norm_num(row["XN_D"]))).fetchall()
            if not found:
                return {"exists": False, "sections": []}
            if len(found) != 1 or found[0] != (plan["doc"], plan["source_hash"], row, POLICY):
                raise ValueError("metadata or alias conflict")
            doc = plan["doc"]
            wanted = {k: row[v] for k,v in (("title","TIK"),("abstract","ABK"),("representative_claim","CLK")) if row[v].strip()}
            available = []
            existing = c.execute("""SELECT section,provider,language,claim_count,body,raw_payload,source_sha256,body_sha256,policy_id
                FROM private_docs.section_sources WHERE document_id=%s""", (doc,)).fetchall()
            expected = {x[3]: x for x in plan["items"]}
            for name, provider, lang, count, body, raw, source_hash, body_hash, policy in existing:
                if name not in expected:
                    raise ValueError("unexpected section")
                item = expected[name]
                if (provider,lang,count,body,raw,source_hash,body_hash,policy) != ("WIPS",item[4],item[5],item[6],json.loads(item[7]),digest(item[7]),digest(item[6]),POLICY):
                    raise ValueError("section conflict")
                available.append(name)
                wanted[name] = body
            chunks = c.execute("""SELECT section,start_offset,end_offset,content_sha256,body,model_id,
                private_docs.vector_dims(embedding) FROM private_docs.chunks WHERE document_id=%s ORDER BY section,start_offset""",(doc,)).fetchall()
            coverage = {k: 0 for k in wanted}
            for name, start, end, h, body, model, dim in chunks:
                if name not in wanted or not 0 <= start < end <= len(wanted[name]) or body != wanted[name][start:end] or digest(body) != h or model != MODEL or dim != 384:
                    raise ValueError("chunk integrity")
                pos = coverage[name]
                if start > pos and wanted[name][pos:start].strip():
                    raise ValueError("chunk gap")
                coverage[name] = max(pos, end)
            if any(not pos or wanted[name][pos:].strip() for name,pos in coverage.items()):
                raise ValueError("chunk completeness")
            return {"exists": True, "sections": sorted(available)}

    def apply(self, mode, rows):
        data = canonical({"mode": mode, "rows": rows}).encode("utf-8")
        if len(data) > CAP:
            raise ValueError("worker cap")
        p = subprocess.run([sys.executable, str(Path(__file__).resolve().with_name("private_patent_increment.py"))],
                           input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600, check=False)
        if p.returncode != 0 or not p.stdout.rstrip().endswith(b"INCREMENTAL_INGEST_PASS"):
            raise RuntimeError("worker failed")
        # Never forward worker stdout/stderr; independently re-read persisted state.


def read_approval():
    # Deployment must bind-mount this fixed file read-only from operator custody.
    # Reject symlinks and group/world-readable or writable authorization files.
    fd = os.open(str(APPROVAL), os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(fd, "rb") as f:
        s = os.fstat(f.fileno())
        if not stat.S_ISREG(s.st_mode) or s.st_mode & 0o077:
            raise PermissionError("approval permissions")
        raw = f.read(2049)
    if len(raw) > 2048:
        raise ValueError("approval cap")
    return json.loads(raw)


def main():
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise ValueError("explicit mode required")
    raw = sys.stdin.buffer.read(CAP + 1)
    if len(raw) > CAP:
        raise ValueError("input cap")
    result = execute(json.loads(raw), read_approval(), LocalBackend(), dry_run=sys.argv[1] == "--check")
    print(json.dumps(result), flush=True)
    return 0 if result["status"] in ("DRY_RUN", "PASS", "REUSED_VERIFIED") else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps({"status": "BLOCKED", "error_type": type(exc).__name__}), flush=True)
        sys.exit(1)
