"""Synthetic-only tests. No network or real DB credentials."""
import copy
import hashlib
import unittest
from mvp03_ingest_adapter import execute, prepare, canonical, POLICY


def fixture():
    row = {"SKEY":"123", "XN_D":"123-456", "CC":"KR", "KC_D":"B1", "TIK":"Synthetic seal", "ABK":"Synthetic barrier", "CLK":"Synthetic claim"}
    base = {"ctry":"KR","doc_num":"123-456","lang_cd":"KR"}
    d = dict(base, dtl_desc_list=[{"skey":"123","lang_cd":"KR","dtl_desc":"Synthetic description"}])
    c = dict(base, cl_list=[{"lang_cd":"KR","cl_num":"1","cl":"Synthetic claim"}],cl_cnt_list=[{"cnt":1}])
    return {"row":row,"sections":[{"skey":"123","response":{"success":True,"section":"dtl_desc","data":d}},{"skey":"123","response":{"success":True,"section":"all_claim","data":c}}]}


def approve(p, mode="new"):
    return {"policy": POLICY,"packet_sha256":hashlib.sha256(canonical(p).encode()).hexdigest(),"mode":mode}


class Fake:
    def __init__(self, exists=False, existing=(), fail=None, no_commit=False):
        self.exists=exists
        self.sections=set(existing)
        self.calls=[]
        self.fail=fail
        self.no_commit=no_commit
    def snapshot(self, plan):
        if self.fail=="snapshot":
            raise ValueError("conflict")
        return {"exists":self.exists,"sections":sorted(self.sections)}
    def apply(self, mode, rows):
        self.calls.append(mode)
        if self.fail==mode:
            raise RuntimeError("failure")
        if self.no_commit:
            return
        if mode=="metadata":
            self.exists=True
        else:
            self.sections.update({"dtl_desc":"detailed_description","all_claim":"all_claims"}[x["response"]["section"]] for x in rows)


class Tests(unittest.TestCase):
    def setUp(self):
        self.p=fixture()
        self.a=approve(self.p)
    def test_new(self):
        b=Fake()
        r=execute(self.p,self.a,b)
        self.assertEqual((r["status"],r["documentsAdded"],r["sectionsAdded"],b.calls),("PASS",1,2,["metadata","sections"]))
    def test_reuse(self):
        b=Fake(True,("detailed_description","all_claims"))
        self.assertEqual(execute(self.p,self.a,b)["status"],"REUSED_VERIFIED")
        self.assertEqual(b.calls,[])
    def test_repeat(self):
        b=Fake()
        execute(self.p,self.a,b)
        self.assertEqual(execute(self.p,self.a,b)["status"],"REUSED_VERIFIED")
        self.assertEqual(b.calls,["metadata","sections"])
    def test_enrich(self):
        b=Fake(True)
        r=execute(self.p,approve(self.p,"enrich"),b)
        self.assertEqual((r["status"],r["documentsAdded"],r["sectionsAdded"],b.calls),("PASS",0,2,["sections"]))
    def test_partial_resume(self):
        b=Fake(True,("detailed_description",))
        r=execute(self.p,approve(self.p,"enrich"),b)
        self.assertEqual((r["status"],r["sectionsAdded"]),("PASS",1))
    def test_enrich_missing(self):
        b=Fake()
        self.assertEqual(execute(self.p,approve(self.p,"enrich"),b)["status"],"BLOCKED_PREFLIGHT")
        self.assertFalse(b.calls)
    def test_dry_run(self):
        b=Fake()
        self.assertEqual(execute(self.p,self.a,b,True)["status"],"DRY_RUN")
        self.assertFalse(b.calls)
    def test_policy(self):
        b=Fake()
        with self.assertRaises(PermissionError):
            execute(self.p,dict(self.a,policy="wrong"),b)
        self.assertFalse(b.calls)
    def test_approval_tamper(self):
        self.p["row"]["TIK"]+=" change"
        with self.assertRaises(PermissionError):
            prepare(self.p,self.a)
    def test_extra_fields(self):
        self.p["admin"]=True
        with self.assertRaises(ValueError):
            prepare(self.p,approve(self.p))
    def test_wrong_section_identity(self):
        self.p["sections"][1]["response"]["data"]["doc_num"]="123-999"
        with self.assertRaises(ValueError):
            prepare(self.p,approve(self.p))
    def test_wrong_skey(self):
        self.p["sections"][1]["skey"]="999"
        with self.assertRaises(ValueError):
            prepare(self.p,approve(self.p))
    def test_one_section(self):
        self.p["sections"].pop()
        with self.assertRaises(ValueError):
            prepare(self.p,approve(self.p))
    def test_duplicate_section(self):
        self.p["sections"][1]=copy.deepcopy(self.p["sections"][0])
        with self.assertRaises(ValueError):
            prepare(self.p,approve(self.p))
    def test_mixed_language(self):
        d=self.p["sections"][1]["response"]["data"]
        d["lang_cd"]="US"
        d["cl_list"][0]["lang_cd"]="US"
        with self.assertRaises(ValueError):
            prepare(self.p,approve(self.p))
    def test_bad_provider_status(self):
        self.p["sections"][0]["response"]["success"]=False
        with self.assertRaises(ValueError):
            prepare(self.p,approve(self.p))
    def test_bad_count(self):
        self.p["sections"][1]["response"]["data"]["cl_cnt_list"][0]["cnt"]=2
        with self.assertRaises(ValueError):
            prepare(self.p,approve(self.p))
    def test_invalid_id(self):
        self.p["row"]["XN_D"]="123@456"
        with self.assertRaises(ValueError):
            prepare(self.p,approve(self.p))
    def test_preflight_conflict(self):
        b=Fake(fail="snapshot")
        self.assertEqual(execute(self.p,self.a,b)["status"],"BLOCKED_PREFLIGHT")
        self.assertEqual(b.calls,[])
    def test_metadata_failure(self):
        b=Fake(fail="metadata")
        r=execute(self.p,self.a,b)
        self.assertEqual((r["status"],b.calls),("FAILED_OR_PARTIAL",["metadata"]))
    def test_section_failure(self):
        b=Fake(fail="sections")
        r=execute(self.p,self.a,b)
        self.assertEqual(r["status"],"FAILED_OR_PARTIAL")
        self.assertTrue(b.exists)
        b.fail=None
        self.assertEqual(execute(self.p,self.a,b)["status"],"PASS")
    def test_false_success(self):
        b=Fake(no_commit=True)
        self.assertEqual(execute(self.p,self.a,b)["status"],"FAILED_OR_PARTIAL")
        self.assertEqual(b.calls,["metadata"])
    def test_false_section_success(self):
        b=Fake(True,no_commit=True)
        self.assertEqual(execute(self.p,approve(self.p,"enrich"),b)["status"],"FAILED_OR_PARTIAL")


if __name__ == "__main__":
    unittest.main()
