"""Real PostgreSQL archive integration, disposable DB only."""
import os,copy,unittest
import psycopg
from mvp37_archive import archive_page,prepare,number_key,POLICY
from mvp37_archive_cli import authorize_from_policy

def row(n,title="Synthetic patent"):
    return {"SKEY":str(n),"CC":"KR","XN_D":"10-2000-%07d"%n,"KC_D":"A",
            "TIK":title,"APSTH":"Fixture applicant","XD":"20000101","ABK":"DO NOT STORE", "CLK":"DO NOT STORE"}
def packet(rows,total=83,query="synthetic query",page=1,size=10):
    return {"query":query,"page":page,"page_size":size,"response":{"success":True,"data":{"total_count":total,"row_list":rows}}}
def allowed(scope): return scope["policy"]==POLICY and scope["purpose"]=="metadata_only"
class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=psycopg.connect(os.environ["TEST_DSN"],autocommit=True)
    @classmethod
    def tearDownClass(cls): cls.c.close()
    def setUp(self):
        # All DB setup/reset is performed by test-only SQL in the isolated clone,
        # and every test has its own synthetic number range.
        self.c.execute("SET ROLE patent_archive_writer_v1")
    def count(self,t):return self.c.execute("SELECT count(*) FROM patent_archive."+t).fetchone()[0]
    def test_01_block(self):
        before=self.count("documents")
        self.assertEqual(archive_page(self.c,packet([row(1)]),lambda _:False)["status"],"BLOCKED_POLICY")
        self.assertEqual(self.count("documents"),before)
    def test_02_page_and_reuse(self):
        p=packet([row(2),row(3),row(2)])
        before=self.count("documents")
        r=archive_page(self.c,p,allowed)
        self.assertEqual((r["total_count"],r["returned_count"],r["unique_count"],r["saved"],r["body_writes"]),(83,3,2,2,0))
        counts=[self.count(t) for t in ("documents","metadata_revisions","search_pages","page_hits")]
        self.assertEqual(self.count("documents"),before+2)
        r=archive_page(self.c,p,allowed)
        self.assertEqual((r["status"],r["saved"],r["reused"]),("REUSED_VERIFIED",0,2))
        self.assertEqual(counts,[self.count(t) for t in ("documents","metadata_revisions","search_pages","page_hits")])
        meta=self.c.execute("SELECT metadata FROM patent_archive.metadata_revisions WHERE identity=%s",(number_key("KR",row(2)["XN_D"],"A"),)).fetchone()[0]
        self.assertNotIn("ABK",meta); self.assertNotIn("CLK",meta)
    def test_03_revision(self):
        archive_page(self.c,packet([row(4)]),allowed)
        b=self.count("metadata_revisions")
        r=archive_page(self.c,packet([row(4,"Corrected title")]),allowed)
        self.assertEqual((r["saved"],r["reused"]),(0,1))
        self.assertEqual(self.count("metadata_revisions"),b+1)
    def test_04_conflict_atomic(self):
        archive_page(self.c,packet([row(5)]),allowed)
        b=[self.count(t) for t in ("documents","search_pages","metadata_revisions")]
        bad=row(6); bad["SKEY"]="5"
        with self.assertRaises(ValueError):archive_page(self.c,packet([row(7),bad]),allowed)
        self.assertEqual(b,[self.count(t) for t in ("documents","search_pages","metadata_revisions")])
    def test_05_validation(self):
        for p in (packet([row(8)],total=0),packet([row(8)],size=51),
                  packet([row(8)],page=10,total=10),packet([row(8),row(8,"Conflict")])):
            with self.assertRaises(ValueError):prepare(p)
    def test_06_fulltext_separate(self):
        r=archive_page(self.c,packet([row(991),row(992),row(993)]),allowed)
        self.assertEqual((r["fulltext_complete"],r["fulltext_partial"],r["fulltext_missing"]),(1,1,1))
    def test_07_access_denied(self):
        for q in ("SELECT * FROM private_docs.readable_catalog","SELECT * FROM private_docs.readable_evidence",
                  "UPDATE patent_archive.documents SET kind=kind","DELETE FROM patent_archive.page_hits"):
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):self.c.execute(q)
    def test_08_empty(self):
        r=archive_page(self.c,packet([],total=0),allowed)
        self.assertEqual((r["status"],r["returned_count"],r["saved"]),("PASS",0,0))
    def test_09_cross_page(self):
        archive_page(self.c,packet([row(9)],query="first"),allowed)
        r=archive_page(self.c,packet([row(9)],query="another",page=2),allowed)
        self.assertEqual((r["saved"],r["reused"]),(0,1))
    def test_10_exact_approval(self):
        p=packet([row(10)])
        batch,_,_=prepare(p)
        auth=authorize_from_policy({"policy":POLICY,"purpose":"metadata_only","approved_batches":[batch],"max_rows":1})
        self.assertEqual(archive_page(self.c,packet([row(11)]),auth)["status"],"BLOCKED_POLICY")
        self.assertEqual(archive_page(self.c,p,auth)["status"],"PASS")
        self.assertEqual(archive_page(self.c,p,auth)["status"],"REUSED_VERIFIED")
        with self.assertRaises(ValueError):authorize_from_policy({"policy":POLICY,"purpose":"metadata_only","approved_batches":["*"],"max_rows":1})
    def test_11_autosave_100_first_page_only(self):
        policy={"policy":POLICY,"purpose":"metadata_only","mode":"owner-approved-autosave-100-v1","max_rows":100}
        auth=authorize_from_policy(policy)
        p=packet([row(n) for n in range(2000,2100)],total=102,query="first 100",page=1,size=100)
        prepared=prepare(p)
        self.assertEqual(len(prepared[2]),100)
        out=archive_page(self.c,p,auth)
        self.assertEqual((out["saved"],out["returned_count"]),(100,100))
        self.assertEqual(archive_page(self.c,p,auth)["status"],"REUSED_VERIFIED")
        with self.assertRaises(ValueError):prepare(packet([row(n) for n in range(3000,3101)],total=101,query="invalid 101",size=101))
        self.assertEqual(archive_page(self.c,packet([row(1999)],total=102,query="next",page=2,size=1),auth)["status"],"BLOCKED_POLICY")
        for invalid in (
            dict(policy,max_rows=101),
            dict(policy,mode="anything"),
            dict(policy,max_rows=True),
            dict(policy,other=True)):
            with self.assertRaises(ValueError):authorize_from_policy(invalid)
if __name__=="__main__": unittest.main(verbosity=2)
