"""Synthetic-only real DB integration test; run ONLY inside the disposable namespace.
No provider request or production authorization. Test approval is fixture-scoped.
"""
import copy, json, os, subprocess, sys
from pathlib import Path
from mvp03_ingest_adapter import execute, LocalBackend, canonical, prepare
from test_mvp03_ingest_adapter import fixture, approve
import psycopg

def connect(role, secret):
    return psycopg.connect(host="127.0.0.1",port=55432,dbname="patent_private_ingest_v1",
                           user=role,password=Path(secret).read_text().strip(),connect_timeout=5)
def writer(): return connect("patent_ingest_writer_v1","/auth/writer_password")
def reader(): return connect("patent_ingest_reader_v1","/auth/reader_password")
def counts():
    with writer() as c:
        return c.execute("SELECT (SELECT count(*) FROM private_docs.documents),(SELECT count(*) FROM private_docs.section_sources),(SELECT count(*) FROM private_docs.chunks)").fetchone()
def check(name, condition):
    if not condition: raise AssertionError(name)
    print("PASS",name,flush=True)
def cli(packet, mode):
    p=subprocess.run([sys.executable,"/code/mvp03_ingest_adapter.py",mode],input=canonical(packet).encode(),
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180)
    return p.returncode,json.loads(p.stdout)
def fingerprint():
    with writer() as c:
        return c.execute("""SELECT (SELECT md5(string_agg(md5(to_jsonb(d)::text),'|' ORDER BY id)) FROM private_docs.documents d),
        (SELECT md5(string_agg(md5(to_jsonb(s)::text),'|' ORDER BY document_id,section)) FROM private_docs.section_sources s),
        (SELECT md5(string_agg(md5(to_jsonb(c)::text),'|' ORDER BY document_id,section,start_offset)) FROM private_docs.chunks c)""").fetchone()
def main():
    f=fixture()
    # Fixed test approval generated offline for only this exact synthetic fixture.
    check("empty_disposable_database",counts()==(0,0,0))
    code,res=cli(f,"--check")
    check("cli_dry_run_zero_writes",code==0 and res["status"]=="DRY_RUN" and res["writes"]==0 and counts()==(0,0,0))
    altered=copy.deepcopy(f);altered["row"]["TIK"]+=" tampered"
    code,res=cli(altered,"--apply")
    check("tampered_approval_denied",code!=0 and res["status"]=="BLOCKED" and counts()==(0,0,0))
    code,res=cli(f,"--apply")
    check("actual_new_insert",code==0 and res=={"status":"PASS","verified":True,"writes":2,"documentsAdded":1,"sectionsAdded":2})
    new_counts=counts()
    check("new_counts",new_counts[:2]==(1,2) and new_counts[2]>=5)
    fp=fingerprint()
    code,res=cli(f,"--apply")
    check("cli_reuse_zero_writes",code==0 and res["status"]=="REUSED_VERIFIED" and res["writes"]==0 and fingerprint()==fp)
    # New synthetic identity, seed metadata + one section, then only missing section via real backend.
    g=copy.deepcopy(f);g["row"].update(SKEY="124",XN_D="124-457",TIK="Synthetic second seal")
    for x in g["sections"]:
        x["skey"]="124";x["response"]["data"]["doc_num"]="124-457"
        if x["response"]["section"]=="dtl_desc":x["response"]["data"]["dtl_desc_list"][0]["skey"]="124"
    b=LocalBackend();b.apply("metadata",[g["row"]]);b.apply("sections",[g["sections"][0]])
    partial=counts();check("partial_seed",partial[:2]==(2,3))
    plan=prepare(g,approve(g,"enrich"))
    check("partial_real_snapshot",b.snapshot(plan)=={"exists":True,"sections":["detailed_description"]})
    res=execute(g,approve(g,"enrich"),b)
    check("actual_partial_resume",res["status"]=="PASS" and res["documentsAdded"]==0 and res["sectionsAdded"]==1 and res["writes"]==1)
    end=counts();check("partial_delta",end[:2]==(2,4) and end[2]>partial[2])
    final=fingerprint()
    res=execute(g,approve(g,"enrich"),b)
    check("partial_reuse_zero_writes",res["status"]=="REUSED_VERIFIED" and res["writes"]==0 and fingerprint()==final)
    conflict=copy.deepcopy(g);conflict["row"]["TIK"]+=" conflict"
    res=execute(conflict,approve(conflict,"enrich"),b)
    check("metadata_conflict_denied",res["status"]=="BLOCKED_PREFLIGHT" and fingerprint()==final)
    conflict=copy.deepcopy(g);conflict["sections"][1]["response"]["data"]["cl_list"][0]["cl"]+=" conflict"
    res=execute(conflict,approve(conflict,"enrich"),b)
    check("section_conflict_denied",res["status"]=="BLOCKED_PREFLIGHT" and fingerprint()==final)
    with reader() as c:
        check("reader_default_readonly",c.execute("SHOW transaction_read_only").fetchone()[0]=="on")
        check("reader_view_visibility",c.execute("SELECT count(*) FROM private_docs.readable_catalog").fetchone()[0]==2 and c.execute("SELECT count(*) FROM private_docs.readable_evidence").fetchone()[0]==end[2])
        check("real_vector_dimensions",c.execute("SELECT min(private_docs.vector_dims(embedding)),max(private_docs.vector_dims(embedding)) FROM private_docs.readable_evidence").fetchone()==(384,384))
    for action in ("UPDATE private_docs.documents SET policy_id=policy_id","DELETE FROM private_docs.documents"):
        try:
            with writer() as c:c.execute(action)
        except psycopg.errors.InsufficientPrivilege:pass
        else:raise AssertionError("writer privilege")
    check("writer_update_delete_denied",fingerprint()==final)
    print("ISOLATED_INGEST_PASS",json.dumps({"documents":end[0],"sections":end[1],"chunks":end[2],"dimensions":384}),flush=True)
if __name__=="__main__":
    try:main()
    except Exception as e:
        print("TEST_FAILED",type(e).__name__,str(e) if isinstance(e,AssertionError) else "",flush=True)
        sys.exit(1)
