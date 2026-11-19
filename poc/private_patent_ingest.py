"""Bounded private patent ingestion (owner-attested purchased materials).
Run locally in an isolated worker. Never log document text, identifiers or credentials.
No live MCP endpoint, no provider API keys, no implicit bulk download.
"""
import hashlib,json,re,sys,unicodedata
from pathlib import Path

MODEL="intfloat/multilingual-e5-small@614241f622f53c4eeff9890bdc4f31cfecc418b3"
POLICY="owner-attested-paid-material-private-v1"
FIELDS=("SKEY","XN_D","CC","KC_D","TIK","ABK","CLK")
def digest(s):return hashlib.sha256(s.encode("utf-8")).hexdigest()
def validate(rows):
    if not isinstance(rows,list) or not 1<=len(rows)<=3:raise ValueError("batch size")
    docs=[]
    ids=set()
    for row in rows:
        if not isinstance(row,dict) or set(row)!=set(FIELDS):raise ValueError("field scope")
        if any(not isinstance(v,str) or "\x00" in v or len(v)>24000 for v in row.values()):raise ValueError("field type/length")
        if not all(row[k].strip() for k in ("SKEY","XN_D","CC","KC_D","TIK","ABK")):raise ValueError("required source fields")
        if not re.fullmatch(r"[A-Z]{2}",row["CC"]):raise ValueError("country")
        if sum(len(v.encode("utf-8")) for v in row.values())>48000:raise ValueError("document byte cap")
        # Preserve provider text verbatim and hash only selected, approved fields.
        raw=json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(",",":"))
        identity="|".join(unicodedata.normalize("NFKC",row[k]).strip().upper() for k in ("CC","XN_D","KC_D"))
        doc_id="PAT-"+digest(identity)
        if doc_id in ids:raise ValueError("duplicate batch identity")
        ids.add(doc_id);docs.append((doc_id,digest(raw),raw,row))
    return docs

def chunks(text,token_count):
    start=0
    while start<len(text):
        end=min(len(text),start+520)
        while token_count("passage: "+text[start:end])>450:
            end=start+(end-start)//2
            if end<=start:raise ValueError("tokenizer overflow")
        if not text[start:end].strip():
            start=end;continue
        yield start,end,text[start:end]
        if end==len(text):break
        start=max(start+1,end-70)

def run():
    import numpy as np
    import onnxruntime as ort
    import psycopg
    from tokenizers import Tokenizer
    raw=sys.stdin.buffer.read(64001)
    if len(raw)>64000:raise ValueError("batch byte cap")
    docs=validate(json.loads(raw))
    opts=ort.SessionOptions()
    opts.intra_op_num_threads=2;opts.inter_op_num_threads=1
    opts.execution_mode=ort.ExecutionMode.ORT_SEQUENTIAL
    session=ort.InferenceSession("/model/onnx__model.onnx",sess_options=opts,providers=["CPUExecutionProvider"])
    tok=Tokenizer.from_file("/model/onnx__tokenizer.json")
    tok.no_truncation()
    names={i.name for i in session.get_inputs()}
    assert {"input_ids","attention_mask"}<=names<={"input_ids","attention_mask","token_type_ids"}
    def embed(text):
        x=tok.encode(text)
        assert len(x.ids)<=512
        ids=np.array([x.ids],dtype=np.int64);mask=np.array([x.attention_mask],dtype=np.int64)
        feed={"input_ids":ids,"attention_mask":mask}
        if "token_type_ids" in names:feed["token_type_ids"]=np.array([x.type_ids],dtype=np.int64)
        hs=[v for v in session.run(None,feed) if v.shape==(1,ids.shape[1],384)]
        assert len(hs)==1
        z=(hs[0]*mask[:,:,None]).sum(axis=1)/mask.sum(axis=1)[:,None]
        v=z[0]/np.linalg.norm(z[0])
        assert v.shape==(384,) and np.isfinite(v).all()
        return json.dumps(v.tolist(),allow_nan=False,separators=(",",":"))
    work=[]
    for doc_id,h,raw_text,row in docs:
        parts=[]
        for section,key in [("title","TIK"),("abstract","ABK"),("representative_claim","CLK")]:
            for start,end,body in chunks(row[key],lambda t:len(tok.encode(t).ids)):
                parts.append((doc_id,section,start,end,digest(body),body,MODEL,embed("passage: "+body)))
        if not parts or len(parts)>100:raise ValueError("chunk cap")
        work.append((doc_id,h,raw_text,parts))
    password=Path("/auth/writer_password").read_text().strip()
    connect=lambda:psycopg.connect(host="127.0.0.1",port=55432,dbname="patent_private_ingest_v1",user="patent_ingest_writer_v1",password=password,connect_timeout=5)
    def ingest():
        created=0;newchunks=0
        with connect() as c:
            for doc_id,h,raw_text,parts in work:
                row=c.execute("INSERT INTO private_docs.documents (id,source_sha256,source_payload,policy_id) VALUES (%s,%s,%s::jsonb,%s) ON CONFLICT(id) DO NOTHING RETURNING id",(doc_id,h,raw_text,POLICY)).fetchone()
                existing=c.execute("SELECT source_sha256,policy_id FROM private_docs.documents WHERE id=%s",(doc_id,)).fetchone()
                if existing!=(h,POLICY):raise ValueError("existing source or policy conflict")
                if row is not None:
                    created+=1
                    for part in parts:
                        c.execute("INSERT INTO private_docs.chunks(document_id,section,start_offset,end_offset,content_sha256,body,model_id,embedding) VALUES(%s,%s,%s,%s,%s,%s,%s,%s::private_docs.vector)",part)
                        newchunks+=1
                stored=c.execute("SELECT section,start_offset,end_offset,content_sha256,model_id FROM private_docs.chunks WHERE document_id=%s ORDER BY section,start_offset",(doc_id,)).fetchall()
                if stored!=sorted((v[1],v[2],v[3],v[4],v[6]) for v in parts):raise ValueError("chunk coverage mismatch")
        return created,newchunks
    first=ingest();second=ingest()
    assert second==(0,0)
    q=embed("query: 태양광 모듈 봉지재의 내습성과 광투과 특성")
    with connect() as c:
        count=c.execute("SELECT count(*) FROM private_docs.documents").fetchone()[0]
        chunk_count,dimension=c.execute("SELECT count(*),min(private_docs.vector_dims(embedding)) FROM private_docs.chunks").fetchone()
        near=c.execute("SELECT document_id,embedding OPERATOR(private_docs.<=>) %s::private_docs.vector AS d FROM private_docs.chunks ORDER BY d LIMIT 3",(q,)).fetchall()
        assert count==len(docs) and chunk_count==sum(len(x[3]) for x in work) and dimension==384 and near
        assert all(0<=float(d)<=2 for _,d in near)
    for target in ("patent_demo",):
        try:
            with psycopg.connect(host="127.0.0.1",port=55432,dbname=target,user="patent_ingest_writer_v1",password=password,connect_timeout=5):pass
        except psycopg.Error as e:
            assert e.sqlstate=="42501" or "permission denied for database" in str(e)
        else:raise AssertionError("cross database access")
    try:
        with connect() as c:c.execute("UPDATE private_docs.documents SET policy_id=policy_id")
    except psycopg.errors.InsufficientPrivilege:pass
    else:raise AssertionError("update permitted")
    print(json.dumps({"created_documents":first[0],"created_chunks":first[1],"duplicate_created":second[0],"total_documents":count,"total_chunks":chunk_count,"vector_dimension":dimension,"search_candidates":len(near),"best_distance":float(near[0][1]),"cross_db_denied":True,"update_denied":True}),flush=True)
    print("PRIVATE_PATENT_INGEST_PASS",flush=True)
if __name__=="__main__":
    try:run()
    except Exception as e:
        # No exception strings: DB errors may include source text.
        print("INGEST_FAILED",type(e).__name__,file=sys.stderr)
        sys.exit(1)
