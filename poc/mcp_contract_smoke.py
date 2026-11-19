"""Disposable MCP contract smoke. Synthetic data only; no DB/network persistence."""
import asyncio
import json
import httpx
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

mcp = FastMCP("patent-synthetic-contract", stateless_http=True, json_response=True)
docs: dict[str, str] = {}
readonly = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)
write = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False)

@mcp.tool(annotations=write)
def save_document(document_id: str, text: str) -> dict:
    """Save a synthetic patent fixture to temporary memory; no real patent content."""
    if not document_id.startswith("DEMO-") or not 1 <= len(text) <= 500:
        raise ValueError("synthetic ID or text length rejected")
    if document_id in docs and docs[document_id] != text:
        raise ValueError("existing synthetic ID conflict")
    created = document_id not in docs
    docs[document_id] = text
    return {"id": document_id, "created": created}

@mcp.tool(annotations=readonly)
def get_document(document_id: str) -> dict:
    """Read a synthetic patent fixture by ID."""
    return {"id": document_id, "text": docs[document_id]} if document_id in docs else {"found": False}

@mcp.tool(annotations=readonly)
def search_documents(query: str) -> list[dict]:
    """Find synthetic fixture by substring. This test does not implement vector search."""
    if not query.strip():
        return []
    return [{"id": k, "text": v} for k, v in docs.items() if query.casefold() in v.casefold()]

async def smoke():
    app = mcp.streamable_http_app()
    headers = {"accept": "application/json, text/event-stream",
               "content-type": "application/json"}
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://127.0.0.1:8765", headers=headers) as client:
            async def rpc(method, params=None, id=1):
                msg = {"jsonrpc": "2.0", "method": method}
                if id is not None:
                    msg["id"] = id
                if params is not None:
                    msg["params"] = params
                resp = await client.post("/mcp", json=msg)
                if id is None:
                    assert resp.status_code in (200, 202, 204), resp.status_code
                    return None
                assert resp.status_code == 200, resp.text
                return resp.json()["result"]
            init = await rpc("initialize", {"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"synthetic-smoke","version":"0.1"}})
            client.headers["MCP-Protocol-Version"]=init["protocolVersion"]
            await rpc("notifications/initialized", id=None)
            listing = await rpc("tools/list")
            assert {t["name"] for t in listing["tools"]} == {"save_document","get_document","search_documents"}
            annotations = {t["name"]: t["annotations"] for t in listing["tools"]}
            assert annotations["save_document"]["readOnlyHint"] is False and annotations["get_document"]["readOnlyHint"] is True
            async def call(name, args):
                return await rpc("tools/call", {"name":name,"arguments":args})
            def payload(result):
                return result.get("structuredContent") or json.loads(result["content"][0]["text"])
            ref = {"document_id":"DEMO-001","text":"합성 예시: 전선 도체 소재"}
            first=await call("save_document",ref)
            assert not first.get("isError") and payload(first)["created"] is True
            again=await call("save_document",ref)
            assert not again.get("isError") and payload(again)["created"] is False
            got=await call("get_document",{"document_id":"DEMO-001"})
            assert payload(got)["text"]==ref["text"]
            found=await call("search_documents",{"query":"도체"})
            assert "DEMO-001" in str(found) and not found.get("isError")
            missing=await call("get_document",{"document_id":"IMPE-001"})
            assert payload(missing)["found"] is False
            blocked=await call("save_document",{"document_id":"IMPE-001","text":"fixture"})
            assert blocked["isError"] is True
            conflict=await call("save_document",{"document_id":"DEMO-001","text":"changed"})
            assert conflict["isError"] is True and docs["DEMO-001"]==ref["text"]
            print("MCP_CONTRACT_PASS: initialize, notifications, list, annotations, save, idempotency, get, lexical search, missing, namespace denial, conflict denial")
            print("PROTOCOL="+init["protocolVersion"]+"; synthetic only; DB/vector/tunnel NOT RUN")

if __name__ == "__main__":
    asyncio.run(smoke())
