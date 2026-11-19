"""Owner-local stdin transport for one approved packet, not an MCP or HTTP service.
Run only from the trusted NAS host. Never forward arbitrary command, path, or
Docker target from a model or provider. stdout is a bounded status only.
"""
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

DOCKER = "/usr/local/bin/docker"
DB_IMAGE = "sha256:b0108689bf51bd54d3129130967d4adf7ba58b395a9ff6653aa598b5fe7d7ba3"
WORKER_IMAGE = "sha256:183e5ad42322fea6f731433ae7f6be7498812b31d2eaf05537ffed838dd1ba7c"
CODE = {
    "mvp03_ingest_adapter.py":"1e721830441d39eeba895944f61277164d0e990d",
    "private_patent_ingest.py":"9f0be1e44afc613c9520f13e7a68740b94448ccb",
    "private_patent_increment.py":"b8ec437f4245eee61f2ae4e3e3af3df6d57425d6",
}
CAP = 900000
START = """set -eu
umask 077
python -m pip install --disable-pip-version-check --no-index --no-cache-dir --find-links=/wheels --target /tmp/deps 'psycopg[binary]==3.3.9' onnxruntime==1.20.1 numpy==1.26.4 tokenizers==0.21.4 >/tmp/pip.log 2>&1
export PYTHONPATH=/tmp/deps
exec python /code/mvp03_ingest_adapter.py "$1"
"""

def private_path(path, mode, directory=False):
    p = Path(path)
    s = p.lstat()
    if (p.resolve() != p or s.st_uid != os.geteuid() or stat.S_IMODE(s.st_mode) != mode
        or not (stat.S_ISDIR(s.st_mode) if directory else stat.S_ISREG(s.st_mode))
        or (not directory and s.st_nlink != 1)):
        raise PermissionError("private path")
    return p

def asset_path(value):
    p = Path(value)
    if not p.is_absolute() or p.resolve()!=p or not p.is_dir():
        raise ValueError("asset path")
    return p

def docker_json(args):
    r = subprocess.run([DOCKER]+args,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
                       check=True,timeout=15)
    return json.loads(r.stdout)[0]

def bind(path, target):
    if any(c in str(path) for c in (",",":","\n","\r")):
        raise ValueError("mount path")
    return ["--mount","type=bind,src="+str(path)+",dst="+target+",readonly"]

def command(mode):
    if mode not in ("--check","--apply"): raise ValueError("mode")
    if os.geteuid()==0: raise PermissionError("nonroot owner required")
    root = private_path(os.environ["PATENT_INGEST_ROOT"],0o700,True)
    code = private_path(root/"code",0o700,True)
    auth = private_path(root/"auth",0o700,True)
    locks = private_path(root/"locks",0o700,True)
    if set(p.name for p in code.iterdir()) != set(CODE): raise ValueError("code scope")
    for name,want in CODE.items():
        p=private_path(code/name,0o600)
        data=p.read_bytes()
        if hashlib.sha1(("blob "+str(len(data))+"\0").encode()+data).hexdigest()!=want:
            raise ValueError("code pin")
    approval=private_path(auth/"ingest_approval.json",0o600)
    writer=private_path(auth/"writer_password",0o600)
    private_path(locks/"ingest.lock",0o600)
    model=asset_path(os.environ["PATENT_MODEL_ROOT"])
    wheels=asset_path(os.environ["PATENT_WHEEL_ROOT"])
    dbid=os.environ["PATENT_DB_CONTAINER_ID"]
    if not re.fullmatch("[a-f0-9]{64}",dbid): raise ValueError("target pin")
    db=docker_json(["inspect","--type","container",dbid])
    host=db["HostConfig"]
    if (db["Id"]!=dbid or db["Image"]!=DB_IMAGE or not db["State"]["Running"]
        or host["NetworkMode"]!="none" or host.get("PortBindings") or not host["ReadonlyRootfs"]):
        raise ValueError("DB isolation or image")
    if docker_json(["image","inspect",WORKER_IMAGE])["Id"]!=WORKER_IMAGE:
        raise ValueError("worker image")
    argv=[DOCKER,"run","--rm","-i","--pull","never","--log-driver","none",
          "--label","patent-rag.worker=approved-local-one-shot",
          "--network","container:"+dbid,"--read-only","--cap-drop","ALL",
          "--security-opt","no-new-privileges","--user",str(os.geteuid())+":"+str(os.getegid()),
          "--memory","3g","--cpu-shares","128","--tmpfs","/tmp:rw,exec,nosuid,nodev,size=450m",
          "-e","HOME=/tmp","-e","OPENBLAS_NUM_THREADS=1","-e","TOKENIZERS_PARALLELISM=false",
          "-e","PYTHONDONTWRITEBYTECODE=1"]
    for src,target in ((code,"/code"),(approval,"/auth/ingest_approval.json"),
                       (writer,"/auth/writer_password"),(locks,"/locks"),
                       (model,"/model"),(wheels,"/wheels")):
        argv+=bind(src,target)
    return argv+["--entrypoint","/bin/sh",WORKER_IMAGE,"-ec",START,"worker",mode]

def sanitize(output, returncode, mode):
    # Never relay raw process output, even if a dependency logs raw inputs.
    try:
        if len(output)>4096: raise ValueError()
        r=json.loads(output)
        status=r["status"]
        if returncode==0 and mode=="--check" and status=="DRY_RUN" and r.get("writes")==0 and type(r.get("exists")) is bool and type(r.get("sections")) is int and 0<=r["sections"]<=2:
            return 0,{"status":status,"writes":0,"exists":r["exists"],"sections":r["sections"]}
        if returncode==0 and mode=="--apply" and status=="REUSED_VERIFIED" and r.get("verified") is True and r.get("writes")==0:
            return 0,{"status":status,"verified":True,"writes":0}
        if returncode==0 and mode=="--apply" and status=="PASS" and r.get("verified") is True and type(r.get("documentsAdded")) is int and r["documentsAdded"] in (0,1) and type(r.get("sectionsAdded")) is int and r["sectionsAdded"] in (1,2) and type(r.get("writes")) is int and r["writes"] in (1,2):
            return 0,{"status":status,"verified":True,"writes":r["writes"],"documentsAdded":r["documentsAdded"],"sectionsAdded":r["sectionsAdded"]}
        if returncode!=0 and status=="BLOCKED" and r.get("error_type")=="IngestBusy":
            return 1,{"status":"BLOCKED_PREFLIGHT","reason":"BUSY","verified":False}
        if returncode!=0 and status in ("BLOCKED","BLOCKED_PREFLIGHT"):
            return 1,{"status":"BLOCKED_PREFLIGHT","verified":False}
    except (ValueError,TypeError,KeyError,AttributeError):
        pass
    return 1,{"status":"FAILED_OR_PARTIAL","verified":False}

def main():
    if sys.argv[1:] not in (["--check"],["--apply"]): raise ValueError("explicit mode")
    mode=sys.argv[1]
    raw=sys.stdin.buffer.read(CAP+1)
    if not raw or len(raw)>CAP: raise ValueError("packet cap")
    argv=command(mode)
    # The local pipe is the only packet transport, no shell, no argv or env payload.
    try:
        r=subprocess.run(argv,input=raw,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,check=False)
    except OSError:
        print('{"status":"FAILED_OR_PARTIAL","verified":false}',flush=True)
        return 1
    code,result=sanitize(r.stdout,r.returncode,mode)
    print(json.dumps(result),flush=True)
    return code

if __name__=="__main__":
    try: sys.exit(main())
    except Exception:
        print('{"status":"BLOCKED_PREFLIGHT","verified":false}',flush=True)
        sys.exit(1)
