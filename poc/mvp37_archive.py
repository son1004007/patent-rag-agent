"""Bounded, metadata-only WIPS archive; no network, embeddings or document writes.

Storage authorization is supplied by the trusted local operator, never by a
provider row or user/model-generated packet. PostgreSQL holds immutable
metadata revisions and page hits. Existing fulltext catalog is read only.
"""
import hashlib
import json
import re
import unicodedata
from datetime import datetime
from collections.abc import Mapping

MAX_ROWS = 50
MAX_BYTES = 512000
POLICY = "owner-approved-wips-metadata-local-v1"
FIELDS = ("SKEY", "XN_D", "CC", "KC_D", "TIK", "APSTH", "XD")
REQUIRED = FIELDS[:5]

def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)

def digest(x):
    return hashlib.sha256(canonical(x).encode("utf-8")).hexdigest()

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def number_key(country, number, kind):
    require(isinstance(country,str) and re.fullmatch("[A-Z]{2}",country), "country")
    require(isinstance(kind,str) and re.fullmatch("[A-Z][A-Z0-9]{0,4}",kind), "kind")
    require(isinstance(number,str) and len(number)<=80, "number")
    n=unicodedata.normalize("NFKC",number).upper()
    # Do not silently remove arbitrary letters or punctuation.
    require(re.fullmatch(r"[A-Z0-9 /.-]+",n), "number chars")
    n=re.sub("[ /.-]","",n)
    require(bool(n), "empty number")
    return country+"|"+n+"|"+kind

def clean_row(r):
    require(isinstance(r,Mapping),"row")
    out={}
    for k in FIELDS:
        v=r.get(k)
        if k not in REQUIRED and v is None: v=""
        require(isinstance(v,str) and len(v)<= (1000 if k=="TIK" else 2000 if k=="APSTH" else 80), "field "+k)
        require(not any(ord(c)<32 or ord(c)==127 for c in v),"control char")
        require(k not in REQUIRED or bool(v.strip()), "missing "+k)
        out[k]=v
    require(re.fullmatch("[0-9]{1,24}",out["SKEY"]),"skey")
    if out["XD"]:
        require(re.fullmatch("[0-9]{8}",out["XD"]),"date")
        datetime.strptime(out["XD"],"%Y%m%d")
    return number_key(out["CC"],out["XN_D"],out["KC_D"]),out

def prepare(packet):
    require(isinstance(packet,dict) and set(packet)=={"query","page","page_size","response"},"packet fields")
    q=packet["query"]; page=packet["page"]; size=packet["page_size"]
    require(isinstance(q,str) and 0<len(q.strip())<=2000 and not any(ord(c)<32 or ord(c)==127 for c in q),"query")
    require(type(page) is int and 1<=page<=10000 and type(size) is int and 1<=size<=MAX_ROWS,"page")
    r=packet["response"]
    require(isinstance(r,dict) and r.get("success") is True and isinstance(r.get("data"),dict),"provider failed")
    total=r["data"].get("total_count"); rows=r["data"].get("row_list")
    require(type(total) is int and 0<=total<=2**31-1 and isinstance(rows,list) and len(rows)<=size,"response shape")
    require(len(rows)<=max(0,total-(page-1)*size),"page count")
    seen={}; keys={}; hits=[]
    for rank,raw in enumerate(rows,1):
        k,row=clean_row(raw)
        h=digest(row); s=row["SKEY"]
        require(s not in seen or seen[s]==(k,h),"skey conflict")
        require(k not in keys or keys[k]==(s,h),"identity conflict")
        seen[s]=(k,h); keys[k]=(s,h); hits.append((rank,k,h,row))
    # Never persist the raw query, abstracts, full responses, or unknown fields.
    clean={"provider":"WIPS","query_sha256":digest(q),"page":page,"page_size":size,
           "total_count":total,"hits":[{"rank":rank,"identity":k,"metadata":r} for rank,k,h,r in hits]}
    require(len(canonical(clean).encode("utf-8"))<=MAX_BYTES,"packet cap")
    return digest(clean), clean, hits

def archive_page(conn, packet, authorize):
    batch,clean,hits=prepare(packet)
    # Authorizer can deny any row/scope; it MUST be trusted local configuration.
    # It cannot be a caller-supplied boolean and must not grant collection rights.
    scope={"policy":POLICY,"purpose":"metadata_only","batch_sha256":batch,
           "identities":tuple(sorted({k for _,k,_,_ in hits})),
           "rows":len(hits)}
    if not callable(authorize) or authorize(scope) is not True:
        return {"status":"BLOCKED_POLICY","verified":False,"saved":0}
    with conn.transaction():
        # Serialize this small archive only; no lock on private_docs.
        conn.execute("SELECT pg_advisory_xact_lock(193744210, 1)")
        previous=conn.execute("SELECT total_count,returned_count FROM patent_archive.search_pages WHERE batch_sha256=%s",(batch,)).fetchone()
        if previous:
            require(tuple(previous)==(clean["total_count"],len(hits)),"stored page conflict")
            saved=0
        else:
            conn.execute("INSERT INTO patent_archive.search_pages(batch_sha256,query_sha256,page,page_size,total_count,returned_count,policy_id) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                         (batch,clean["query_sha256"],clean["page"],clean["page_size"],clean["total_count"],len(hits),POLICY))
            saved=0
        known=0; catalog_complete=0; catalog_partial=0
        for k in sorted({k for _,k,_,_ in hits}):
            row=next(r for _,kk,_,r in hits if kk==k)
            h=digest(row)
            # Enforce both provider key and canonical publication identity.
            old=conn.execute("SELECT identity,skey FROM patent_archive.documents WHERE identity=%s OR skey=%s",(k,row["SKEY"])).fetchall()
            require(len(old)<=1 and (not old or tuple(old[0])==(k,row["SKEY"])),"stored identity conflict")
            if not old and not previous:
                conn.execute("INSERT INTO patent_archive.documents(identity,skey,country,publication,kind) VALUES (%s,%s,%s,%s,%s)",(k,row["SKEY"],row["CC"],row["XN_D"],row["KC_D"]))
                saved+=1
            require(bool(old) or not previous,"stored identity missing")
            if not previous:
                conn.execute("INSERT INTO patent_archive.metadata_revisions(identity,metadata_sha256,metadata) VALUES (%s,%s,%s::jsonb) ON CONFLICT DO NOTHING",(k,h,canonical(row)))
            actual=conn.execute("SELECT metadata FROM patent_archive.metadata_revisions WHERE identity=%s AND metadata_sha256=%s",(k,h)).fetchone()
            require(actual is not None and actual[0]==row,"metadata integrity")
            # The catalog view is a separate, read-only grant. Identity comparison
            # strips only the punctuation handled by number_key; anomalies fail closed.
            matches=conn.execute("SELECT publication,country,kind,has_description,has_claims FROM patent_archive.fulltext_status WHERE country=%s AND kind=%s",(row["CC"],row["KC_D"])).fetchall()
            matched=[m for m in matches if number_key(m[1],m[0],m[2])==k]
            require(len(matched)<=1,"fulltext identity conflict")
            if matched:
                known+=1
                if matched[0][3] and matched[0][4]: catalog_complete+=1
                else: catalog_partial+=1
        if not previous:
            for rank,k,h,_ in hits:
                conn.execute("INSERT INTO patent_archive.page_hits(batch_sha256,rank,identity,metadata_sha256) VALUES (%s,%s,%s,%s)",(batch,rank,k,h))
        actual=conn.execute("SELECT rank,identity,metadata_sha256 FROM patent_archive.page_hits WHERE batch_sha256=%s ORDER BY rank",(batch,)).fetchall()
        require([tuple(x) for x in actual]==[(rank,k,h) for rank,k,h,_ in hits],"page hit integrity")
        return {"status":"REUSED_VERIFIED" if previous else "PASS","verified":True,
                "total_count":clean["total_count"],"returned_count":len(hits),"unique_count":len({k for _,k,_,_ in hits}),
                "saved":saved,"reused":len({k for _,k,_,_ in hits})-saved,
                "fulltext_known":known,"fulltext_complete":catalog_complete,"fulltext_partial":catalog_partial,
                "fulltext_missing":len({k for _,k,_,_ in hits})-known,"body_writes":0}
