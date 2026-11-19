"""Internal MVP-03 local read-only probe. Do not send catalog/results to external search.
Only identity and retrieval distance are returned to the private orchestrator.
Temporary test worker, not an externally reachable MCP tool.
"""
import json,sys
from private_patent_reader import search_patents,conn
def probe(req):
    if not isinstance(req,dict) or set(req)!={"query","limit"}:raise ValueError("scope")
    if type(req["query"]) is not str or not 1<=len(req["query"].strip())<=200 or type(req["limit"]) is not int or not 1<=req["limit"]<=3:raise ValueError("query")
    result=search_patents(req["query"],req["limit"])
    with conn() as c:
        rows=c.execute("""SELECT d.country,d.publication,d.kind,
          EXISTS(SELECT 1 FROM private_docs.readable_evidence e WHERE e.document_id=d.id AND e.section='detailed_description')
          AND EXISTS(SELECT 1 FROM private_docs.readable_evidence e WHERE e.document_id=d.id AND e.section='all_claims')
          FROM private_docs.readable_catalog d ORDER BY d.id LIMIT 1001""").fetchall()
    if len(rows)>1000:raise ValueError("catalog cap")
    return {"scope":result["scope"],"catalog":[{"country":a,"publication":b,"kind":c,"enriched":d} for a,b,c,d in rows],
            "results":[{k:r[k] for k in ("country","publication","kind","distance")} for r in result["results"]]}
if __name__=="__main__":
    try:
        raw=sys.stdin.buffer.read(16385)
        if len(raw)>16384:raise ValueError("input cap")
        print("LOCAL_PROBE_JSON "+json.dumps(probe(json.loads(raw)),ensure_ascii=False),flush=True)
    except Exception as e:
        print("LOCAL_PROBE_FAIL "+type(e).__name__,file=sys.stderr)
        sys.exit(1)
