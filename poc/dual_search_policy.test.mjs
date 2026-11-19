import {FIXTURES,PUBLIC_QUERY,syntheticSaveRequest,dualSearch} from './dual_search_policy.mjs';
import assert from 'node:assert/strict';
const ledger=[
["known_synthetic",()=>syntheticSaveRequest({source:"synthetic",id:"DEMO-P4",text:FIXTURES["DEMO-P4"]}).allowed],
["wips_deny",()=>!syntheticSaveRequest({source:"wips",id:"DEMO-P4",text:FIXTURES["DEMO-P4"]}).allowed],
["self_claimed_approval_deny",()=>!syntheticSaveRequest({source:"wips",id:"DEMO-P4",text:FIXTURES["DEMO-P4"],approved:true,license:"allow-all"}).allowed],
["unknown_provider_deny",()=>!syntheticSaveRequest({source:"public",id:"DEMO-P4",text:FIXTURES["DEMO-P4"]}).allowed],
["missing_provider_deny",()=>!syntheticSaveRequest({id:"DEMO-P4",text:FIXTURES["DEMO-P4"]}).allowed],
["unknown_id_deny",()=>!syntheticSaveRequest({source:"synthetic",id:"DEMO-P5",text:"arbitrary"}).allowed],
["modified_fixture_deny",()=>!syntheticSaveRequest({source:"synthetic",id:"DEMO-P4",text:"changed"}).allowed],
["prototype_id_deny",()=>!syntheticSaveRequest({source:"synthetic",id:"toString",text:"arbitrary"}).allowed],
["null_deny",()=>!syntheticSaveRequest(null).allowed],
["no_extra_fields_in_write",()=>Object.keys(syntheticSaveRequest({source:"synthetic",id:"DEMO-P4",text:FIXTURES["DEMO-P4"],extra:"ignored"}).args).sort().join(",")==="document_id,text"],
["sequential_no_cross_transfer",async()=>{const calls=[];const result=await dualSearch(async args=>{calls.push(["w",args]);return {success:true,data:{row_list:[{SKEY:"EXTERNAL_TEST_SENTINEL"}]}}},async args=>{calls.push(["n",args]);return {scope:"synthetic_candidates_only",results:[{id:"DEMO-P4",distance:.1}]}});return calls.length===2&&calls[0][0]==="w"&&calls[1][0]==="n"&&calls[1][1].query===PUBLIC_QUERY.nas&&result.external.count===1&&result.local.topId==="DEMO-P4"&&!JSON.stringify({calls,result}).includes("EXTERNAL_TEST_SENTINEL")&&result.storage==="NOT_ATTEMPTED"}],
["wips_failure_local_available",async()=>{const r=await dualSearch(async()=>{throw Error("external failure")},async()=>({scope:"synthetic_candidates_only",results:[{id:"DEMO-P4",distance:.1}]}));return !r.external.ok&&r.local.ok}],
["local_failure_external_available",async()=>{const r=await dualSearch(async()=>({success:true,data:{row_list:[]}}),async()=>{throw Error("local failure")});return r.external.ok&&!r.local.ok}],
["malformed_scope_deny",async()=>{const r=await dualSearch(async()=>({success:true,data:{row_list:[]}}),async()=>({scope:"production",results:[{id:"DEMO-P4",distance:.1}]}));return !r.local.ok}],
["unknown_local_id_deny",async()=>{const r=await dualSearch(async()=>({success:true,data:{row_list:[]}}),async()=>({scope:"synthetic_candidates_only",results:[{id:"REAL-001",distance:.1}]}));return !r.local.ok}],
["oversized_provider_response_deny",async()=>{const r=await dualSearch(async()=>({success:true,data:{row_list:[1,2,3,4]}}),async()=>({scope:"synthetic_candidates_only",results:[]}));return !r.external.ok&&r.local.ok}],
["malformed_distance_deny",async()=>{const r=await dualSearch(async()=>({success:true,data:{row_list:[]}}),async()=>({scope:"synthetic_candidates_only",results:[{id:"DEMO-P4",distance:NaN}]}));return !r.local.ok}]
];
for(const [name,fn] of ledger){assert.equal(await fn(),true,name);console.log('PASS',name);}
console.log('DUAL_SEARCH_POLICY_PASS',ledger.length);
