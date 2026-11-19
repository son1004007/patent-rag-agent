"""Synthetic-only E2E: MCP ASGI -> real E5 embedding -> pgvector.
Run only with the matching disposable, network-isolated test runner.
No endpoint is exposed, no real patent material accepted.
"""
import asyncio,json,os,time
import httpx
import numpy as np
import onnxruntime as ort
import psycopg
from tokenizers import Tokenizer
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

MODEL="intfloat/multilingual-e5-small@614241f622f53c4eeff9890bdc4f31cfecc418b3"
FIXTURES={
    "DEMO-P1":"가상 문헌: 구리 피복 알루미늄 전선 도체의 경량화 및 전기 전도성.",
    "DEMO-P2":"가상 문헌: 해양 케이블의 염수 부식과 내식성 표면 처리.",
    "DEMO-P3":"가상 문헌: 열가소성 절연 재료의 난연 성능과 화재 안전."
}
opts=ort.SessionOptions()
opts.intra_op_num_threads=2
opts.inter_op_num_threads=1
opts.execution_mode=ort.ExecutionMode.ORT_SEQUENTIAL
t0=time.monotonic()
session=ort.InferenceSession("/model/onnx__model.onnx",sess_options=opts,providers=["CPUExecutionProvider"])
tok=Tokenizer.from_file("/model/onnx__tokenizer.json")
tok.enable_truncation(max_length=512)
inputs={x.name for x in session.get_inputs()}
assert {"input_ids","attention_mask"}<=inputs<={"input_ids","attention_mask","token_type_ids"}
print("MODEL_LOADED_MS",round((time.monotonic()-t0)*1000),flush=True)
def embed(text,prefix):
    x=tok.encode(prefix+text)
    ids=np.array([x.ids],dtype=np.int64)
    mask=np.array([x.attention_mask],dtype=np.int64)
    feed={"input_ids":ids,"attention_mask":mask}
    if "token_type_ids" in inputs:feed["token_type_ids"]=np.array([x.type_ids],dtype=np.int64)
    hs=[v for v in session.run(None,feed) if v.shape==(1,ids.shape[1],384)]
    assert len(hs)==1
    pooled=(hs[0]*mask[:,:,None]).sum(axis=1)/mask.sum(axis=1)[:,None]
    vec=pooled[0]/np.linalg.norm(pooled[0])
    assert vec.shape==(384,) and np.isfinite(vec).all() and abs(np.linalg.norm(vec)-1)<1e-5
    return json.dumps(vec.tolist(),allow_nan=False,separators=(",",":"))

def conn(db="patent_demo",user="patent_app",password=None):
    return psycopg.connect(host="127.0.0.1",port=55432,dbname=db,user=user,
        password=os.environ["PATENT_TEST_PASSWORD"] if password is None else password,connect_timeout=4)

mcp=FastMCP("synthetic-patent-vector-v1",stateless_http=True,json_response=True)
read=ToolAnnotations(readOnlyHint=True,destructiveHint=False,openWorldHint=False)
write=ToolAnnotations(readOnlyHint=False,destructiveHint=False,idempotentHint=True,openWorldHint=False)
@mcp.tool(annotations=write)
def save_document(document_id:str,text:str)->dict:
    """Store exactly one approved synthetic fixture, without overwriting."""
    if FIXTURES.get(document_id)!=text:raise ValueError("Only exact synthetic fixtures are allowed")
    v=embed(text,"passage: ")
    with conn() as c:
        cur=c.execute("INSERT INTO documents(id,body,model_id,embedding) VALUES(%s,%s,%s,%s::vector) ON CONFLICT(id) DO NOTHING RETURNING id",(document_id,text,MODEL,v))
        created=cur.fetchone() is not None
        stored=c.execute("SELECT body,model_id FROM documents WHERE id=%s",(document_id,)).fetchone()
        if stored!=(text,MODEL):raise ValueError("Document conflict")
    return {"id":document_id,"created":created,"model_id":MODEL}
@mcp.tool(annotations=read)
def get_document(document_id:str)->dict:
    """Read an approved fixture from the patent test database."""
    if document_id not in FIXTURES:return {"found":False}
    with conn() as c:
        row=c.execute("SELECT id,body,model_id FROM documents WHERE id=%s",(document_id,)).fetchone()
    return {"found":True,"id":row[0],"text":row[1],"model_id":row[2]} if row else {"found":False}
@mcp.tool(annotations=read)
def search_documents(query:str,limit:int=3)->dict:
    """Return synthetic nearest neighbors; distance is not an accuracy probability."""
    if not 1<=len(query.strip())<=200 or not 1<=limit<=3:raise ValueError("Invalid query or limit")
    v=embed(query,"query: ")
    with conn() as c:
        rows=c.execute("SELECT id,body,embedding <=> %s::vector AS distance FROM documents WHERE model_id=%s ORDER BY distance,id LIMIT %s",(v,MODEL,limit)).fetchall()
    return {"results":[{"id":i,"text":b,"distance":float(d)} for i,b,d in rows],"scope":"synthetic_candidates_only"}

async def smoke():
    n=0
    def check(name,ok):
        nonlocal n
        assert ok,name
        n+=1
        print("PASS",name,flush=True)
    app=mcp.streamable_http_app()
    headers={"accept":"application/json, text/event-stream","content-type":"application/json"}
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url="http://127.0.0.1:8765",headers=headers) as client:
            async def rpc(method,params=None,rid=1):
                msg={"jsonrpc":"2.0","method":method}
                if rid is not None:msg["id"]=rid
                if params is not None:msg["params"]=params
                r=await client.post("/mcp",json=msg)
                if rid is None:
                    assert r.status_code in (200,202,204)
                    return None
                assert r.status_code==200,r.status_code
                return r.json()["result"]
            init=await rpc("initialize",{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"test","version":"1"}})
            client.headers["MCP-Protocol-Version"]=init["protocolVersion"]
            await rpc("notifications/initialized",rid=None)
            check("initialize",bool(init["protocolVersion"]))
            tools=(await rpc("tools/list"))["tools"]
            check("tool_scope",{x["name"] for x in tools}=={"save_document","get_document","search_documents"})
            async def call(name,args):
                return await rpc("tools/call",{"name":name,"arguments":args})
            def body(r):
                assert not r.get("isError"),r.get("isError")
                return r.get("structuredContent") or json.loads(r["content"][0]["text"])
            for k,v in FIXTURES.items():
                r=await call("save_document",{"document_id":k,"text":v})
                check("save_"+k,body(r)["created"] is True)
            check("idempotency",body(await call("save_document",{"document_id":"DEMO-P1","text":FIXTURES["DEMO-P1"]}))["created"] is False)
            check("fetch",body(await call("get_document",{"document_id":"DEMO-P1"}))["text"]==FIXTURES["DEMO-P1"])
            check("missing_study",body(await call("get_document",{"document_id":"DEMO-S1"}))["found"] is False)
            check("reject_nonfixture",(await call("save_document",{"document_id":"DEMO-WIPS","text":"unapproved"})).get("isError") is True)
            check("reject_conflict",(await call("save_document",{"document_id":"DEMO-P1","text":"changed"})).get("isError") is True)
            for q,want in [("구리 사용량을 줄이는 경량 전선 도체","DEMO-P1"),("바닷물 환경에서 케이블 부식 방지","DEMO-P2"),("화재 확산을 막는 절연 소재","DEMO-P3")]:
                t=time.monotonic()
                results=body(await call("search_documents",{"query":q}))["results"]
                print("QUERY_RESULT",want,results[0]["id"],"elapsed_ms",round((time.monotonic()-t)*1000),flush=True)
                check("semantic_"+want,results[0]["id"]==want and len(results)==3)
                check("distance_order_"+want,all(0<=x["distance"]<=2 for x in results) and all(a["distance"]<=b["distance"] for a,b in zip(results,results[1:])))
            check("reject_limit",(await call("search_documents",{"query":"도체","limit":4})).get("isError") is True)
            check("reject_blank",(await call("search_documents",{"query":" "})).get("isError") is True)
    with conn() as c:
        count,dim,models=c.execute("SELECT count(*),min(vector_dims(embedding)),count(DISTINCT model_id) FROM documents").fetchone()
        check("db_rows_dims",(count,dim,models)==(3,384,1))
        check("model_id",c.execute("SELECT DISTINCT model_id FROM documents").fetchone()[0]==MODEL)
        check("no_study_rows",c.execute("SELECT count(*) FROM documents WHERE id='DEMO-S1'").fetchone()[0]==0)
    try:
        with conn(db="study_demo") as c:c.execute("SELECT 1")
    except psycopg.Error as e:check("cross_db_rejected",e.sqlstate=="42501" or "permission denied for database" in str(e))
    else:raise AssertionError("cross_db_open")
    try:
        with conn() as c:c.execute("DELETE FROM documents")
    except psycopg.errors.InsufficientPrivilege:check("delete_denied",True)
    else:raise AssertionError("delete_allowed")
    try:
        with conn() as c:c.execute("UPDATE documents SET body='changed'")
    except psycopg.errors.InsufficientPrivilege:check("update_denied",True)
    else:raise AssertionError("update_allowed")
    print("MCP_E5_PGVECTOR_PASS checks="+str(n),flush=True)
    print("SCOPE: synthetic-only; ASGI, real embeddings and SQL; no production storage/network/Tunnel",flush=True)

if __name__=="__main__":asyncio.run(smoke())
