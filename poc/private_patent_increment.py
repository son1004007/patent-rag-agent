"""Private, bounded incremental ingest. No raw data or identifiers in output.
Compatible with v1 document identity and existing read-only evidence views.
Use only selected provider fields within owner-authorized local storage.
"""
import copy,hashlib,json,re,sys,unicodedata
from pathlib import Path
from private_patent_ingest import MODEL,POLICY,validate,digest
MAX_BODY=180000
MAX_CHUNKS=600
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def norm_num(x):return re.sub(r"[^A-Z0-9]","",unicodedata.normalize("NFKC",x).upper())
def check_text(x,cap):
    if not isinstance(x,str) or not x.strip() or len(x)>cap or "\x00" in x:raise ValueError("text scope")
    return x
def sections(rows):
    if not isinstance(rows,list) or not 1<=len(rows)<=2:raise ValueError("section batch")
    out=[];keys=set()
    for row in rows:
        if set(row)!={"skey","response"} or not re.fullmatch(r"[0-9]{1,24}",row["skey"]):raise ValueError("identity")
        response=row["response"]
        if response.get("success") is not True:raise ValueError("provider status")
        d=response["data"]; section=response["section"]
        ctry=check_text(d["ctry"],2);number=check_text(d["doc_num"],80)
        lang=d["lang_cd"]
        if lang not in ("KR","US","JP","CN"):raise ValueError("language")
        count=0
        if section=="dtl_desc":
            records=d["dtl_desc_list"]
            if not isinstance(records,list) or not 1<=len(records)<=12:raise ValueError("description records")
            for rec in records:
                if str(rec["skey"])!=row["skey"] or rec["lang_cd"]!=lang:raise ValueError("description identity")
            body="\n\n".join(check_text(x["dtl_desc"],MAX_BODY) for x in records)
            payload={"ctry":ctry,"doc_num":number,"lang_cd":lang,"dtl_desc_list":records}
            name="detailed_description"
        elif section=="all_claim":
            records=d["cl_list"]
            if not isinstance(records,list) or not 1<=len(records)<=500:raise ValueError("claims")
            parts=[];seen=set()
            for rec in records:
                if rec["lang_cd"]!=lang:raise ValueError("claim language")
                num=check_text(str(rec["cl_num"]),30)
                partial=rec.get("partial_cd","")
                if not isinstance(partial,str) or len(partial)>30 or (partial,num) in seen:raise ValueError("claim identity")
                seen.add((partial,num))
                parts.append("청구항 "+num+(" ["+partial+"]" if partial else "")+"\n"+check_text(rec["cl"],MAX_BODY))
            counts=d.get("cl_cnt_list",[])
            if counts and (not isinstance(counts,list) or sum(int(x["cnt"]) for x in counts)!=len(records)):raise ValueError("claim count")
            count=len(records);body="\n\n".join(parts);name="all_claims"
            payload={"ctry":ctry,"doc_num":number,"lang_cd":lang,"cl_list":records,"cl_cnt_list":counts,"cl_remark_list":d.get("cl_remark_list",[]),"partial_cd_list":d.get("partial_cd_list",[])}
        else:raise ValueError("section scope")
        check_text(body,MAX_BODY)
        key=(row["skey"],name)
        if key in keys:raise ValueError("duplicate section")
        keys.add(key)
        out.append((row["skey"],ctry,number,name,lang,count,body,canonical(payload)))
    return out
def chunk_ranges(text,token_count):
    start=0
    while start<len(text):
        end=min(len(text),start+1000)
        while token_count("passage: "+text[start:end])>450:
            end=start+(end-start)//2
            if end<=start:raise ValueError("token overflow")
        if text[start:end].strip():yield start,end,text[start:end]
        if end==len(text):break
        start=max(start+1,end-70)
def run():
    import numpy as np
    import onnxruntime as ort
    import psycopg
    from tokenizers import Tokenizer
    raw=sys.stdin.buffer.read(900001)
    if len(raw)>900000:raise ValueError("batch byte limit")
    inp=json.loads(raw)
    if set(inp)!={"mode","rows"} or inp["mode"] not in ("metadata","sections"):raise ValueError("batch envelope")
    mode=inp["mode"]
    data=validate(inp["rows"]) if mode=="metadata" else sections(inp["rows"])
    password=Path("/auth/writer_password").read_text().strip()
    def conn():
        return psycopg.connect(host="127.0.0.1",port=55432,dbname="patent_private_ingest_v1",user="patent_ingest_writer_v1",password=password,connect_timeout=5,options="-c statement_timeout=10000 -c lock_timeout=2000")
    opts=ort.SessionOptions();opts.intra_op_num_threads=2;opts.inter_op_num_threads=1;opts.execution_mode=ort.ExecutionMode.ORT_SEQUENTIAL
    session=ort.InferenceSession("/model/onnx__model.onnx",sess_options=opts,providers=["CPUExecutionProvider"])
    tok=Tokenizer.from_file("/model/onnx__tokenizer.json");tok.no_truncation()
    names={x.name for x in session.get_inputs()}
    assert {"input_ids","attention_mask"}<=names<={"input_ids","attention_mask","token_type_ids"}
    def embed(text,prefix):
        x=tok.encode(prefix+text)
        if len(x.ids)>512:raise ValueError("token limit")
        ids=np.array([x.ids],dtype=np.int64);mask=np.array([x.attention_mask],dtype=np.int64)
        feed={"input_ids":ids,"attention_mask":mask}
        if "token_type_ids" in names:feed["token_type_ids"]=np.array([x.type_ids],dtype=np.int64)
        hs=[v for v in session.run(None,feed) if v.shape==(1,ids.shape[1],384)];assert len(hs)==1
        z=(hs[0]*mask[:,:,None]).sum(axis=1)/mask.sum(axis=1)[:,None]
        v=z[0]/np.linalg.norm(z[0]);assert v.shape==(384,) and np.isfinite(v).all() and abs(np.linalg.norm(v)-1)<1e-5
        return json.dumps(v.tolist(),allow_nan=False,separators=(",",":"))
    def counts(c):
        return tuple(c.execute("SELECT (SELECT count(*) FROM private_docs.documents),(SELECT count(*) FROM private_docs.section_sources),(SELECT count(*) FROM private_docs.chunks)").fetchone())
    def chunk_meta(doc,section,body,metadata):
        # Keep legacy 520-character chunk algorithm byte-compatible.
        from private_patent_ingest import chunks
        fn=chunks if metadata else chunk_ranges
        a=[(doc,section,i,j,digest(t),t,MODEL) for i,j,t in fn(body,lambda t:len(tok.encode(t).ids))]
        if not a or len(a)>MAX_CHUNKS:raise ValueError("chunk count")
        return a
    def existing(c,doc,section):
        return c.execute("SELECT start_offset,end_offset,content_sha256,body,model_id FROM private_docs.chunks WHERE document_id=%s AND section=%s ORDER BY start_offset",(doc,section)).fetchall()
    def write_chunks(c,doc,section,body,metadata,created):
        meta=chunk_meta(doc,section,body,metadata)
        want=[(x[2],x[3],x[4],x[5],x[6]) for x in meta]
        if created:
            for x in meta:
                c.execute("INSERT INTO private_docs.chunks(document_id,section,start_offset,end_offset,content_sha256,body,model_id,embedding) VALUES(%s,%s,%s,%s,%s,%s,%s,%s::private_docs.vector)",(*x,embed(x[5],"passage: ")))
        if existing(c,doc,section)!=want:raise ValueError("chunk conflict or coverage")
        return len(meta) if created else 0
    def ingest(work):
        nd=ns=nc=0
        with conn() as c:
            before=counts(c)
            if mode=="metadata":
                for doc,h,payload,row in work:
                    created=c.execute("INSERT INTO private_docs.documents(id,source_sha256,source_payload,policy_id) VALUES(%s,%s,%s::jsonb,%s) ON CONFLICT(id) DO NOTHING RETURNING id",(doc,h,payload,POLICY)).fetchone() is not None
                    if c.execute("SELECT source_sha256,policy_id,source_payload FROM private_docs.documents WHERE id=%s",(doc,)).fetchone()!=(h,POLICY,row):raise ValueError("metadata conflict")
                    nd+=int(created)
                    for section,key in (("title","TIK"),("abstract","ABK"),("representative_claim","CLK")):
                        if row[key].strip():nc+=write_chunks(c,doc,section,row[key],True,created)
            else:
                for skey,ctry,num,section,lang,claim_count,body,payload in work:
                    rec=c.execute("SELECT id,source_payload->>'CC',source_payload->>'XN_D',policy_id FROM private_docs.documents WHERE source_payload->>'SKEY'=%s",(skey,)).fetchall()
                    if len(rec)!=1 or rec[0][1]!=ctry or norm_num(rec[0][2])!=norm_num(num) or rec[0][3]!=POLICY:raise ValueError("document mismatch")
                    doc=rec[0][0];h=digest(payload);bh=digest(body)
                    created=c.execute("INSERT INTO private_docs.section_sources(document_id,section,provider,language,claim_count,body,raw_payload,source_sha256,body_sha256,policy_id) VALUES(%s,%s,'WIPS',%s,%s,%s,%s::jsonb,%s,%s,%s) ON CONFLICT(document_id,section) DO NOTHING RETURNING document_id",(doc,section,lang,claim_count,body,payload,h,bh,POLICY)).fetchone() is not None
                    stored=c.execute("SELECT provider,language,claim_count,body,raw_payload,source_sha256,body_sha256,policy_id FROM private_docs.section_sources WHERE document_id=%s AND section=%s",(doc,section)).fetchone()
                    if stored!=("WIPS",lang,claim_count,body,json.loads(payload),h,bh,POLICY):raise ValueError("section conflict")
                    ns+=int(created);nc+=write_chunks(c,doc,section,body,False,created)
            after=counts(c)
            if after!=tuple(x+y for x,y in zip(before,(nd,ns,nc))):raise ValueError("count delta conflict")
        return (nd,ns,nc),before,after
    first,before,after=ingest(data)
    duplicate,b,a=ingest(data)
    assert duplicate==(0,0,0) and b==a==after
    altered=copy.deepcopy(inp["rows"])
    if mode=="metadata":altered[0]["TIK"]+=" [synthetic conflict test]"
    else:
        section=altered[0]["response"]["section"];d=altered[0]["response"]["data"]
        if section=="dtl_desc":d["dtl_desc_list"][0]["dtl_desc"]+=" [synthetic conflict test]"
        else:d["cl_list"][0]["cl"]+=" [synthetic conflict test]"
    try:ingest(validate(altered) if mode=="metadata" else sections(altered))
    except ValueError as e:
        assert str(e) in ("metadata conflict","section conflict")
    else:raise AssertionError("conflict was accepted")
    with conn() as c:
        assert counts(c)==after
        dim=c.execute("SELECT min(private_docs.vector_dims(embedding)),max(private_docs.vector_dims(embedding)) FROM private_docs.chunks").fetchone()
        assert dim==(384,384)
        q=embed("태양광 모듈 봉지재의 내습성과 광투과율","query: ")
        near=c.execute("SELECT section,embedding OPERATOR(private_docs.<=>) %s::private_docs.vector AS d FROM private_docs.chunks ORDER BY d LIMIT 3",(q,)).fetchall()
        assert len(near)==3 and all(0<=float(x[1])<=2 for x in near)
        if mode=="sections":
            n=c.execute("SELECT count(*) FROM private_docs.section_sources s WHERE NOT EXISTS(SELECT 1 FROM private_docs.chunks c WHERE c.document_id=s.document_id AND c.section=s.section)").fetchone()[0]
            assert n==0
    print(json.dumps({"mode":mode,"documents_added":first[0],"sections_added":first[1],"chunks_added":first[2],"before":before,"after":after,"duplicate_added":sum(duplicate),"conflict_denied":True,"dimensions":384,"search_candidates":len(near),"claim_count_in_batch":sum(x[5] for x in data) if mode=="sections" else 0}),flush=True)
    print("INCREMENTAL_INGEST_PASS",flush=True)
if __name__=="__main__":
    try:run()
    except Exception as e:
        # No exception contents, provider text, or identifiers in logs.
        print("INCREMENTAL_INGEST_FAILED",type(e).__name__,file=sys.stderr)
        sys.exit(1)
