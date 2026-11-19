"""Synthetic-only local MCP staging service. No real patent material accepted."""
import asyncio,json,os,time,hmac
from pathlib import Path
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
        password=Path("/secrets/db_password").read_text().strip() if password is None else password,connect_timeout=4)

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

# Local-only static bearer. Do not use as public OAuth or disable SDK Host checks.
TOKEN=Path("/secrets/mcp_token").read_text().strip().encode()
assert len(TOKEN)>=48
class LocalGuard:
    def __init__(self,app):self.app=app
    async def __call__(self,scope,receive,send):
        if scope["type"]=="lifespan":return await self.app(scope,receive,send)
        if scope["type"]!="http":return
        async def reject(status):
            data=b'{"error":"request rejected"}'
            await send({"type":"http.response.start","status":status,"headers":[(b"content-type",b"application/json"),(b"cache-control",b"no-store"),(b"content-length",str(len(data)).encode())]})
            await send({"type":"http.response.body","body":data})
        headers={}
        for k,v in scope["headers"]:
            if k in (b"host",b"origin",b"authorization",b"content-length",b"transfer-encoding") and k in headers:return await reject(400)
            headers[k]=v
        if headers.get(b"host")!=b"127.0.0.1:8765" or headers.get(b"origin",b"http://127.0.0.1:8765")!=b"http://127.0.0.1:8765":return await reject(403)
        if not hmac.compare_digest(headers.get(b"authorization",b""),b"Bearer "+TOKEN):return await reject(401)
        if scope["path"]!="/mcp":return await reject(404)
        if scope["method"]!="POST":return await reject(405)
        length=headers.get(b"content-length",b"")
        if not length.isdigit() or b"transfer-encoding" in headers:return await reject(411)
        if int(length)>16384:return await reject(413)
        chunks=[];size=0
        try:
            async with asyncio.timeout(5):
                while True:
                    msg=await receive()
                    if msg["type"]=="http.disconnect":return
                    data=msg.get("body",b"");size+=len(data)
                    if size>16384:return await reject(413)
                    chunks.append(data)
                    if not msg.get("more_body",False):break
        except TimeoutError:return await reject(408)
        if size!=int(length):return await reject(400)
        consumed=False
        async def replay():
            nonlocal consumed
            if not consumed:
                consumed=True
                return {"type":"http.request","body":b"".join(chunks),"more_body":False}
            return await receive()
        await self.app(scope,replay,send)
application=LocalGuard(mcp.streamable_http_app())
if __name__=="__main__":
    import uvicorn
    uvicorn.run(application,host="127.0.0.1",port=8765,access_log=False,log_level="warning",proxy_headers=False,ws="none",limit_concurrency=8,timeout_keep_alive=5)
