import assert from "node:assert/strict";
import {planQuestion,idKey,research,makeIngestOne} from "./mvp03_research_flow.mjs";
const row=(n)=>({SKEY:String(n),XN_D:"TEST-"+n,CC:"KR",KC_D:"A",TIK:"synthetic title",ABK:"synthetic abstract",CLK:"synthetic claim"});
const existing=(n,enriched=true)=>({country:"KR",publication:"TEST-"+n,kind:"A",enriched});
const local=(catalog)=>({scope:"private_purchased_patents_local_only",catalog,results:catalog.slice(0,3).map(x=>({...x,distance:.2}))});
const wips=(rows)=>({success:true,data:{row_list:rows}});
const q="태양광 모듈의 습기 침투 저감 소재";
const groups=[["태양광","태양전지"],["봉지재","밀봉재"],["내습성","방습"]];
let calls=[];
const make=(c,r,allow=true,write={verified:true,documentsAdded:0,sectionsAdded:2})=>({searchLocal:async x=>{calls.push(["local",x]);return local(c)},searchWips:async x=>{calls.push(["wips",x]);return wips(r)},allowExternalSearch:async()=>true,allowLocalWrite:async()=>allow,ingestOne:async x=>{calls.push(["write",x]);return write}});
let n=0;function check(name,ok){assert.ok(ok,name);n++;console.log("PASS",name);}
check("query_compile",planQuestion(q,groups).wipsQuery==="(태양광 태양전지).ti,ab. AND (봉지재 밀봉재).ti,ab. AND (내습성 방습).ti,ab.");
for(const [name,bad] of [["operator",[["태양광"],["OR"]]],["injection",[["태양광"],["x).SKEY."]]],["unbounded",[["a","b","c","d","e"],["f"]]],["empty",[["a"],[]]]]){assert.throws(()=>planQuestion(q,bad));check(name,true)}
check("normalized_identity",idKey("KR","TEST-1","A")===idKey("KR","TEST1","A"));
check("kind_separation",idKey("KR","TEST1","A")!==idKey("KR","TEST1","B1"));
calls=[];let r=await research(q,groups,make([existing(1,false)],[row(1),row(2)]));check("prioritize_missing_sections",r.write==="PASS"&&r.known===1&&r.newCandidates===1&&calls[2][1].mode==="enrich");
check("sequential_and_bounded",calls.length===3&&calls[0][0]==="local"&&calls[1][0]==="wips"&&calls[1][1].pgrow===3);
calls=[];r=await research(q,groups,make([existing(1)],[row(1)]));check("reuse_no_write",r.write==="NOT_NEEDED"&&calls.length===2);
calls=[];r=await research(q,groups,make([existing(1)],[row(2),row(3)],true,{verified:true,documentsAdded:1,sectionsAdded:2}));check("new_only_one",r.writeCount===1&&calls[2][1].mode==="new");
calls=[];r=await research(q,groups,make([],[row(1)],false));check("policy_denial",r.write==="BLOCKED_POLICY"&&calls.length===2);
calls=[];let a=make([],[row(1)]);a.searchLocal=async()=>{throw Error("unavailable")};r=await research(q,groups,a);check("local_failure_no_write",r.write==="BLOCKED_SOURCE_FAILURE");
a=make([],[row(1)]);a.searchWips=async()=>({success:false});r=await research(q,groups,a);check("provider_failure_no_write",r.write==="BLOCKED_SOURCE_FAILURE");
r=await research(q,groups,make([],[row(1),{...row(1),TIK:"altered"}]));check("conflicting_provider_row",r.wips==="FAILED"&&r.write==="BLOCKED_SOURCE_FAILURE");
r=await research(q,groups,make([],[row(1)],true,{verified:false,documentsAdded:1,sectionsAdded:2}));check("unverified_write",r.write==="FAILED_OR_PARTIAL");
a=make([],[row(1)]);a.searchLocal=async()=>({scope:"synthetic_candidates_only",results:[],catalog:[]});r=await research(q,groups,a);check("synthetic_scope_denied",r.write==="BLOCKED_SOURCE_FAILURE");
r=await research(q,groups,make([],[row(1),row(2),row(3),row(4)]));check("provider_cap",r.write==="BLOCKED_SOURCE_FAILURE");
r=await research(q,groups,make([],[row(1)],true,{staged:true,verified:false}));check("staged_is_not_committed",r.write==="STAGED_PENDING_VERIFICATION"&&r.writeCount===0);
calls=[];a=make([existing(1)],[row(2)]);a.allowExternalSearch=async()=>false;r=await research(q,groups,a);check("external_denied_local_only",r.nas==="PASS"&&r.wips==="BLOCKED_POLICY"&&r.write==="BLOCKED_POLICY"&&calls.length===1);
calls=[];a=make([],[row(2)]);a.allowLocalWrite=async()=>{throw Error("policy unavailable")};r=await research(q,groups,a);check("policy_failure_closed",r.write==="BLOCKED_POLICY"&&calls.length===2);

const spec=(skey,section)=>({success:true,section,data:{ctry:"KR",doc_num:"TEST-"+skey,lang_cd:"KR",...(section==="dtl_desc"?{dtl_desc_list:[{skey,lang_cd:"KR",dtl_desc:"synthetic"}]}:{cl_list:[{lang_cd:"KR",cl_num:"1",cl:"synthetic"}]})}});
let detailCalls=0,submits=0;
const mk=(allowed=true,reply={status:"PASS",verified:true,writes:2,documentsAdded:1,sectionsAdded:2})=>({
 allowCollection:async scope=>allowed&&scope.count===1&&scope.skey==="2",
 getSpec:async p=>{detailCalls++;return spec(p.skey,p.section)},
 submitApprovedPacket:async p=>{submits++;assert.ok(p.packet.sections.length===2);return reply}
});
let i=makeIngestOne(mk(false));
r=await i({mode:"new",row:row(2)});
check("target_specific_collection_denied",r.status==="BLOCKED_POLICY"&&detailCalls===0&&submits===0);
i=makeIngestOne(mk());
r=await i({mode:"new",row:row(2)});
check("bounded_detail_packet",r.status==="PASS"&&detailCalls===2&&submits===1);
let adapter=mk();adapter.getSpec=async p=>({...spec(p.skey,p.section),data:{...spec(p.skey,p.section).data,doc_num:"OTHER"}});
try{await makeIngestOne(adapter)({mode:"new",row:row(2)});throw Error("missing rejection");}catch(e){check("provider_identity_rejected",e.message==="SPEC_IDENTITY_OR_STATUS"&&submits===1)}
r=await makeIngestOne(mk(true,{status:"REUSED_VERIFIED",verified:true,writes:0}))({mode:"new",row:row(2)});
check("verified_noop",r.status==="REUSED_VERIFIED"&&r.writes===0);
r=await research(q,groups,make([],[row(2)],true,r));
check("orchestrator_noop",r.write==="REUSED_VERIFIED"&&r.writeCount===0);
r=await research(q,groups,make([existing(2,false)],[row(2)],true,{verified:true,documentsAdded:0,sectionsAdded:1}));
check("orchestrator_partial_resume",r.write==="PASS"&&r.writeCount===1);
r=await research(q,groups,make([],[row(2)],true,{status:"BLOCKED_POLICY",verified:false}));
check("orchestrator_target_policy",r.write==="BLOCKED_POLICY"&&r.writeCount===0);
try{await makeIngestOne(mk(true,{status:"PASS",verified:false,writes:2,documentsAdded:1,sectionsAdded:2}))({mode:"new",row:row(2)});throw Error("missing rejection");}catch(e){check("unverified_transport_rejected",e.message==="UNVERIFIED_LOCAL_RESULT")}

console.log("MVP03_POLICY_TEST_PASS",n);
