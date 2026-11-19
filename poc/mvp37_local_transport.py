"""Trusted NAS owner-local stdin adapter for the existing archive CLI.

No MCP listener, provider credentials or HTTP endpoint. A disabled policy
blocks before Docker/DB access. The operator, not this program, provisions
exact approved batches and a separate writer secret.
"""
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import uuid
from pathlib import Path

DOCKER="/usr/local/bin/docker"
DB_IMAGE="sha256:b0108689bf51bd54d3129130967d4adf7ba58b395a9ff6653aa598b5fe7d7ba3"
WORKER_IMAGE="sha256:183e5ad42322fea6f731433ae7f6be7498812b31d2eaf05537ffed838dd1ba7c"
CODE={"mvp37_archive.py":"bc84c3d3c449853008739367ac0125e907cbc74a",
      "mvp37_archive_cli.py":"70ae5d429452ded0615e1f778e54878385cc0e82"}
CAP=600000
BLOCKED={"status":"BLOCKED_POLICY","verified":False,"saved":0}
FAILED={"status":"FAILED_OR_UNCONFIRMED","verified":False}
START="""set -eu
umask 077
python -m pip install --disable-pip-version-check --no-index --no-cache-dir --find-links=/wheels --target /tmp/deps 'psycopg[binary]==3.3.9' >/tmp/pip.log 2>&1
export PYTHONPATH=/tmp/deps
exec python /code/mvp37_archive_cli.py --archive
"""

def path_private(path,mode,directory=False):
    p=Path(path)
    s=p.lstat()
    if p.resolve()!=p or s.st_uid!=os.geteuid() or stat.S_IMODE(s.st_mode)!=mode:
        raise PermissionError("private path")
    if directory:
        if not stat.S_ISDIR(s.st_mode):raise PermissionError("directory")
    elif not stat.S_ISREG(s.st_mode) or s.st_nlink!=1:
        raise PermissionError("file")
    return p

def load_modules(root):
    code=path_private(root/"code",0o700,True)
    for n,want in CODE.items():
        p=path_private(code/n,0o600)
        b=p.read_bytes()
        if hashlib.sha1(("blob "+str(len(b))+"\0").encode()+b).hexdigest()!=want:
            raise ValueError("code pin")
    sys.dont_write_bytecode=True
    sys.path.insert(0,str(code))
    from mvp37_archive import prepare, POLICY
    from mvp37_archive_cli import authorize_from_policy, read_private
    return prepare,POLICY,authorize_from_policy,read_private

def parse_policy(config,authorize_from_policy):
    if config=={"enabled":False} and config["enabled"] is False:
        return None
    return authorize_from_policy(config)

def sanitize(out,rc,expect):
    try:
        if len(out)>4096:raise ValueError()
        r=json.loads(out)
        if rc!=0 and r==BLOCKED:return 1,BLOCKED
        if rc!=0 or r.get("status") not in ("PASS","REUSED_VERIFIED") or r.get("verified") is not True:raise ValueError()
        fields=("total_count","returned_count","unique_count","saved","reused","fulltext_known","fulltext_complete","fulltext_partial","fulltext_missing","body_writes")
        v={k:r[k] for k in fields}
        if not all(type(n) is int and n>=0 for n in v.values()):raise ValueError()
        if (v["total_count"],v["returned_count"],v["unique_count"])!=expect:raise ValueError()
        if v["saved"]+v["reused"]!=v["unique_count"] or v["body_writes"]!=0:raise ValueError()
        if v["fulltext_complete"]+v["fulltext_partial"]!=v["fulltext_known"] or v["fulltext_known"]+v["fulltext_missing"]!=v["unique_count"]:raise ValueError()
        if r["status"]=="REUSED_VERIFIED" and v["saved"]!=0:raise ValueError()
        return 0,{"status":r["status"],"verified":True,**v}
    except (ValueError,TypeError,KeyError,AttributeError):
        return 1,FAILED

def docker_json(args):
    r=subprocess.run([DOCKER]+args,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,check=True,timeout=15)
    return json.loads(r.stdout)[0]

def bind(p,target):
    if any(c in str(p) for c in (",",":","\n","\r")):raise ValueError("mount")
    return ["--mount","type=bind,src="+str(p)+",dst="+target+",readonly"]

def worker(root,policy,raw,expect):
    # Only reached after a trusted, exact local policy permits this page.
    secret=path_private(root/"auth"/"archive_writer_password",0o600)
    wheels=Path(os.environ["PATENT_WHEEL_ROOT"])
    if not wheels.is_absolute() or wheels.resolve()!=wheels or not wheels.is_dir():raise ValueError("wheels")
    dbid=os.environ["PATENT_DB_CONTAINER_ID"]
    if not re.fullmatch("[0-9a-f]{64}",dbid):raise ValueError("DB pin")
    db=docker_json(["inspect","--type","container",dbid])
    h=db["HostConfig"]
    if db["Id"]!=dbid or db["Image"]!=DB_IMAGE or not db["State"]["Running"] or h["NetworkMode"]!="none" or h.get("PortBindings") or not h["ReadonlyRootfs"]:raise ValueError("DB boundary")
    if docker_json(["image","inspect",WORKER_IMAGE])["Id"]!=WORKER_IMAGE:raise ValueError("worker pin")
    name="patent-archive-once-"+uuid.uuid4().hex
    label="patent-rag.worker=archive-local-one-shot"
    argv=[DOCKER,"run","--rm","-i","--pull","never","--log-driver","none","--name",name,"--label",label,
          "--network","container:"+dbid,"--read-only","--cap-drop","ALL","--security-opt","no-new-privileges",
          "--user",str(os.geteuid())+":"+str(os.getegid()),"--memory","512m","--cpu-shares","128",
          "--tmpfs","/tmp:rw,exec,nosuid,nodev,size=250m","-e","HOME=/tmp","-e","PYTHONDONTWRITEBYTECODE=1"]
    for n in CODE:argv+=bind(root/"code"/n,"/code/"+n)
    for p,t in ((policy,"/auth/archive_policy.json"),(secret,"/auth/archive_writer_password"),(wheels,"/wheels")):argv+=bind(p,t)
    argv+=["--entrypoint","/bin/sh",WORKER_IMAGE,"-ec",START]
    try:
        r=subprocess.run(argv,input=raw,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=120)
        return sanitize(r.stdout,r.returncode,expect)
    except subprocess.TimeoutExpired:
        # Never retry an unknown commit. Cleanup only the unique owned worker.
        try:
            d=docker_json(["inspect","--type","container",name])
            if d["Name"]=="/"+name and d["Config"]["Labels"].get("patent-rag.worker")=="archive-local-one-shot":
                subprocess.run([DOCKER,"stop","-t","5",name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=15)
        except Exception:pass
        return 1,FAILED

def run(raw,root):
    if not raw or len(raw)>CAP:raise ValueError("packet cap")
    prepare,policy_id,authorize_from_policy,read_private=load_modules(root)
    batch,clean,hits=prepare(json.loads(raw))
    scope={"policy":policy_id,"purpose":"metadata_only","batch_sha256":batch,
           "identities":tuple(sorted({k for _,k,_,_ in hits})),"rows":len(hits)}
    auth=path_private(root/"auth",0o700,True)
    p=path_private(auth/"archive_policy.json",0o600)
    authorize=parse_policy(json.loads(read_private(p,16000)),authorize_from_policy)
    if authorize is None or authorize(scope) is not True:return 1,BLOCKED
    return worker(root,p,raw,(clean["total_count"],len(hits),len(scope["identities"])))

def main():
    if sys.argv[1:]!=["--archive"] or os.geteuid()==0:raise PermissionError("owner only")
    root=path_private(os.environ["PATENT_ARCHIVE_ROOT"],0o700,True)
    rc,result=run(sys.stdin.buffer.read(CAP+1),root)
    print(json.dumps(result),flush=True)
    return rc

if __name__=="__main__":
    try:sys.exit(main())
    except Exception:
        print(json.dumps(FAILED),flush=True)
        sys.exit(1)
