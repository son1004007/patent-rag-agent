"""Trusted owner-local CLI. Never mount these credentials into a reader MCP.
The operator owns the exact scope file. No automatic creation of approvals.
"""
import json,os,stat,sys
from pathlib import Path
from mvp37_archive import archive_page,prepare,POLICY,MAX_ROWS

def read_private(path,cap):
    p=Path(path)
    fd=os.open(str(p),os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(fd,"rb") as f:
        s=os.fstat(f.fileno())
        if not stat.S_ISREG(s.st_mode) or stat.S_IMODE(s.st_mode)!=0o600 or s.st_uid!=os.geteuid() or s.st_nlink!=1:
            raise PermissionError("private file")
        raw=f.read(cap+1)
        if len(raw)>cap:raise ValueError("file cap")
        return raw

def authorize_from_policy(p):
    if not isinstance(p,dict) or p.get("policy")!=POLICY or p.get("purpose")!="metadata_only":
        raise ValueError("policy")
    # User-confirmed metadata-only automatic collection, first page only,
    # max 100 distinct returned WIPS rows per search; no auto-pagination.
    if set(p)=={"policy","purpose","mode","max_rows"}:
        if p["mode"]!="owner-approved-autosave-100-v1" or type(p["max_rows"]) is not int or p["max_rows"]!=100:
            raise ValueError("autosave scope")
        return lambda scope:(scope["policy"]==POLICY and scope["purpose"]=="metadata_only"
            and scope["page"]==1 and scope["rows"]<=100)
    # Legacy exact-packet approval is still supported for targeted operations.
    if set(p)!={"policy","purpose","approved_batches","max_rows"}:
        raise ValueError("policy fields")
    batches=p["approved_batches"]
    if not isinstance(batches,list) or not 1<=len(batches)<=100 or any(not isinstance(x,str) or len(x)!=64 or any(c not in "0123456789abcdef" for c in x) for x in batches):
        raise ValueError("batch approval")
    if type(p["max_rows"]) is not int or not 1<=p["max_rows"]<=MAX_ROWS:
        raise ValueError("row cap")
    return lambda scope:(scope["policy"]==POLICY and scope["purpose"]=="metadata_only"
        and scope["batch_sha256"] in batches and scope["rows"]<=p["max_rows"])

def main():
    if sys.argv[1:]!=["--archive"]:raise ValueError("mode")
    raw=sys.stdin.buffer.read(600001)
    if not raw or len(raw)>600000:raise ValueError("packet cap")
    packet=json.loads(raw)
    batch,clean,hits=prepare(packet)
    authorize=authorize_from_policy(json.loads(read_private("/auth/archive_policy.json",16000)))
    scope={"policy":POLICY,"purpose":"metadata_only","batch_sha256":batch,"identities":tuple(sorted({k for _,k,_,_ in hits})),"page":clean["page"],"rows":len(hits)}
    if authorize(scope) is not True:
        print('{"status":"BLOCKED_POLICY","verified":false,"saved":0}')
        return 1
    # No raw output, arbitrary DSN or provider-supplied database targets.
    password=read_private("/auth/archive_writer_password",512).decode("utf-8").strip()
    if not password:raise ValueError("password")
    import psycopg
    with psycopg.connect(host="127.0.0.1",port=55432,dbname="patent_private_ingest_v1",
                         user="patent_archive_writer_v1",password=password,connect_timeout=5,
                         options="-c statement_timeout=15000 -c lock_timeout=5000",autocommit=True) as c:
        result=archive_page(c,packet,authorize)
    print(json.dumps(result),flush=True)
    return 0 if result.get("verified") is True else 1

if __name__=="__main__":
    try:sys.exit(main())
    except Exception:
        print('{"status":"FAILED_OR_UNCONFIRMED","verified":false}',flush=True)
        sys.exit(1)
