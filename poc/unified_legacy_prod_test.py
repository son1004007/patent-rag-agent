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
ck("tool_scope",{x["name"] for x in rpc("tools/list")["tools"]}=={"save_document","get_document","search_documents","search_patents","get_patent"})
fixtures={"DEMO-P1":"가상 문헌: 구리 피복 알루미늄 전선 도체의 경량화 및 전기 전도성.","DEMO-P2":"가상 문헌: 해양 케이블의 염수 부식과 내식성 표면 처리.","DEMO-P3":"가상 문헌: 열가소성 절연 재료의 난연 성능과 화재 안전."}
if sys.argv[1]=="initial":
    for k,v in fixtures.items():
        ck("save_"+k,body(call("save_document",document_id=k,text=v))["created"] is True)
else:
    for k,v in fixtures.items():
        ck("persisted_"+k,body(call("get_document",document_id=k))["text"]==v)
ck("duplicate",body(call("save_document",document_id="DEMO-P1",text=fixtures["DEMO-P1"]))["created"] is False)
ck("unapproved",call("save_document",document_id="REAL-001",text="unapproved").get("isError") is True)
ck("get",body(call("get_document",document_id="DEMO-P1"))["text"]==fixtures["DEMO-P1"])
ck("foreign",body(call("get_document",document_id="DEMO-S1"))["found"] is False)
ck("search",body(call("search_documents",query="바닷물 환경에서 케이블 부식 방지"))["results"][0]["id"]=="DEMO-P2")
ck("blank",call("search_documents",query=" ").get("isError") is True)
print("SOCKET_MCP_PASS checks="+str(n),flush=True)
