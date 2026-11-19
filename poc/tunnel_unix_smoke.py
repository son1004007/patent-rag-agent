"""Host-side HTTP/MCP over a permission-restricted Unix socket."""
import http.client,json,os,socket,stat,sys
from pathlib import Path

base=Path(sys.argv[1])
path=base/"tunnel"/"relay"/"mcp.sock"
token=(base/"secrets"/"mcp_token").read_text().strip()
class UnixHTTP(http.client.HTTPConnection):
    def connect(self):
        self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        self.sock.settimeout(12)
        self.sock.connect(str(path))
n=0
def check(name,ok):
    global n
    assert ok,name
    n+=1;print("PASS",name,flush=True)
def req(msg,auth=True,extra=None,body=None):
    headers={"Accept":"application/json, text/event-stream","Content-Type":"application/json","Connection":"close","MCP-Protocol-Version":"2025-11-25"}
    if auth:headers["Authorization"]="Bearer "+token
    if extra:headers.update(extra)
    client=UnixHTTP("127.0.0.1",8765,timeout=12)
    try:
        client.request("POST","/mcp",body=json.dumps(msg).encode() if body is None else body,headers=headers)
        response=client.getresponse()
        return response.status,response.read(1048577)
    finally:client.close()
def rpc(method,params=None,rid=1):
    msg={"jsonrpc":"2.0","method":method}
    if rid is not None:msg["id"]=rid
    if params is not None:msg["params"]=params
    status,data=req(msg)
    if rid is None:
        assert status==202;return None
    assert status==200,status
    return json.loads(data)["result"]
def call(name,**kwargs):
    return rpc("tools/call",{"name":name,"arguments":kwargs})
def result(r):
    assert not r.get("isError")
    return r.get("structuredContent") or json.loads(r["content"][0]["text"])
s=path.lstat()
check("unix_socket_owner_mode",stat.S_ISSOCK(s.st_mode) and stat.S_IMODE(s.st_mode)==0o600 and s.st_uid==os.getuid())
check("private_dir_mode",stat.S_IMODE(path.parent.stat().st_mode)==0o700)
init={"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"unix-smoke","version":"1"}}
msg={"jsonrpc":"2.0","method":"initialize","id":1,"params":init}
check("missing_bearer",req(msg,False)[0]==401)
check("invalid_bearer",req(msg,extra={"Authorization":"Bearer invalid"})[0]==401)
check("invalid_host",req(msg,extra={"Host":"invalid.example"})[0]==403)
check("invalid_origin",req(msg,extra={"Origin":"https://invalid.example"})[0]==403)
check("oversize",req(msg,body=b"x"*16385)[0]==413)
check("initialize",bool(rpc("initialize",init)["protocolVersion"]))
rpc("notifications/initialized",rid=None)
check("tools",{x["name"] for x in rpc("tools/list")["tools"]}=={"save_document","get_document","search_documents"})
v=result(call("get_document",document_id="DEMO-P1"))
check("get",v["found"] and v["id"]=="DEMO-P1")
check("idempotent_save",result(call("save_document",document_id="DEMO-P1",text=v["text"]))["created"] is False)
check("denied_nonfixture",call("save_document",document_id="REAL-001",text="unapproved").get("isError") is True)
check("foreign_scope",result(call("get_document",document_id="DEMO-S1"))["found"] is False)
check("semantic_search",result(call("search_documents",query="바닷물 환경에서 케이블 부식 방지"))["results"][0]["id"]=="DEMO-P2")
print("LOCAL_UNIX_MCP_PASS checks="+str(n))
