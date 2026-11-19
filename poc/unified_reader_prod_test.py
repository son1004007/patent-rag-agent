"""Real socket MCP test; no tokens printed."""
import json,sys,time,urllib.request,urllib.error
from pathlib import Path
base="http://127.0.0.1:8765/mcp"
token=Path("/secrets/mcp_token").read_text().strip()
n=0
def ck(name,ok):
    global n
    if not ok:raise AssertionError(name)
    n+=1;print("PASS",name,flush=True)
def req(msg,auth=True,extra=None,raw=None):
    h={"Accept":"application/json, text/event-stream","Content-Type":"application/json"}
    if auth:h["Authorization"]="Bearer "+token
    if extra:h.update(extra)
    data=json.dumps(msg).encode() if raw is None else raw
    try:
        with urllib.request.urlopen(urllib.request.Request(base,data=data,headers=h),timeout=12) as r:return r.status,r.read()
    except urllib.error.HTTPError as e:return e.code,e.read()
def rpc(method,params=None,rid=1):
    msg={"jsonrpc":"2.0","method":method}
    if rid is not None:msg["id"]=rid
    if params is not None:msg["params"]=params
    status,data=req(msg,extra={"MCP-Protocol-Version":"2025-11-25"})
    if rid is None:
        assert status==202,status;return None
    assert status==200,status
    return json.loads(data)["result"]
def call(name,**kwargs):return rpc("tools/call",{"name":name,"arguments":kwargs})
def body(r):
    assert not r.get("isError")
    return r.get("structuredContent") or json.loads(r["content"][0]["text"])
init={"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"local-test","version":"1.0"}}
msg={"jsonrpc":"2.0","id":1,"method":"initialize","params":init}
for attempt in range(60):
    try:
        status,_=req(msg,auth=False)
        if status==401:break
    except OSError:pass
    time.sleep(1)
else:raise RuntimeError("service not ready")
ck("missing_token",status==401)
ck("wrong_token",req(msg,extra={"Authorization":"Bearer invalid"})[0]==401)
ck("bad_host",req(msg,extra={"Host":"untrusted.example"})[0]==403)
ck("bad_origin",req(msg,extra={"Origin":"https://untrusted.example"})[0]==403)
ck("oversize",req(msg,raw=b"x"*16385)[0]==413)
ck("initialize",bool(rpc("initialize",init)["protocolVersion"]))
rpc("notifications/initialized",rid=None)
tools=rpc("tools/list")["tools"]
ck("read_only_tool_catalog",{x["name"] for x in tools if x["annotations"]["readOnlyHint"]}=={"search_patents","get_patent","get_document","search_documents"} and {x["name"] for x in tools if not x["annotations"]["readOnlyHint"]}=={"save_document"})
ck("unknown_document",body(call("get_patent",document_id="PAT-"+"0"*64))["found"] is False)
ck("foreign_document",body(call("get_patent",document_id="DEMO-P4"))["found"] is False)
ck("invalid_query",call("search_patents",query=" ").get("isError") is True)
ck("invalid_limit",call("search_patents",query="test",limit=4).get("isError") is True)
t=time.monotonic()
r=body(call("search_patents",query="태양광 모듈 봉지재의 내습성과 광투과율",limit=3))
latency=1000*(time.monotonic()-t)
rows=r["results"]
ck("scope",r["scope"]=="private_purchased_patents_local_only")
ck("three_distinct_real_patents",len(rows)==3 and len({x["document_id"] for x in rows})==3)
ck("bounded_evidence",all(x["provider"]=="WIPS" and x["publication"] and x["title"] and 0<len(x["excerpt"])<=300 and len(x["source_sha256"])==64 and len(x["chunk_sha256"])==64 and 0<=x["distance"]<=2 for x in rows))
ck("distance_order",all(rows[i]["distance"]<=rows[i+1]["distance"] for i in range(len(rows)-1)))
g=body(call("get_patent",document_id=rows[0]["document_id"]))
ck("exact_fetch",g["found"] and g["publication"]==rows[0]["publication"] and g["title"]==rows[0]["title"])
ck("evidence_scope",1<=len(g["evidence"])<=3 and all(0<len(x["excerpt"])<=300 for x in g["evidence"]))
ck("raw_payload_absent",not ({"source_payload","embedding","SKEY"}&set(g)))
import psycopg
def db(database="patent_private_ingest_v1"):
    return psycopg.connect(host="127.0.0.1",port=55432,dbname=database,user="patent_ingest_reader_v1",password=Path("/secrets/reader_password").read_text().strip(),connect_timeout=4)
def denied(sql):
    try:
        with db() as c:
            c.execute("SET TRANSACTION READ WRITE")
            c.execute(sql)
    except psycopg.errors.InsufficientPrivilege:return True
    return False
with db() as c:ck("role_default_readonly",c.execute("SHOW default_transaction_read_only").fetchone()[0]=="on")
ck("raw_source_denied",denied("SELECT source_payload FROM private_docs.documents"))
ck("raw_chunk_denied",denied("SELECT body FROM private_docs.chunks"))
ck("raw_sections_denied",denied("SELECT body FROM private_docs.section_sources"))
ck("write_denied",denied("UPDATE private_docs.documents SET policy_id=policy_id"))
try:
    with db("patent_demo"):pass
except psycopg.Error as e:
    ck("cross_domain_denied",e.sqlstate=="42501" or "permission denied for database" in str(e))
else:raise AssertionError("cross domain access allowed")
print("SEARCH_LATENCY_MS",round(latency,2),flush=True)
print("PRIVATE_READER_MCP_PASS checks="+str(n),flush=True)
