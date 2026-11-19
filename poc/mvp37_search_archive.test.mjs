import {searchAndArchive} from './mvp37_search_archive.mjs';
const tests=await (async()=>{
const ok=(b,n)=>{if(!b)throw Error(n);return n};
const q={query:"synthetic research",page:1,page_size:3};
const row={SKEY:"001",XN_D:"10-2000-0000001",CC:"KR",KC_D:"A",TIK:"Fixture",ABK:"private body"};
const reply={success:true,data:{total_count:83,row_list:[row]}};
const verified={status:"PASS",verified:true,total_count:83,returned_count:1,unique_count:1,saved:1,reused:0,body_writes:0,fulltext_complete:0,fulltext_partial:0,fulltext_missing:1};
const tests=[];
let calls=0;
const base={allowSearch:async()=>true,searchWips:async()=>reply,archivePage:async(p)=>{calls++;ok(!("ABK" in p.response.data.row_list[0]),"strip text");return verified}};
let a=await searchAndArchive(q,base);
tests.push(ok(a.archive==="PASS"&&a.storage.saved===1&&a.total_count===83&&a.returned_count===1&&!("ABK" in a.rows[0])&&calls===1,"actual returned page only, automatic callback"));
a=await searchAndArchive(q,{...base,allowSearch:async()=>false});tests.push(ok(a.search==="BLOCKED_POLICY"&&calls===1,"search denial"));
a=await searchAndArchive(q,{...base,searchWips:async()=>{throw Error()}});tests.push(ok(a.search==="FAILED"&&calls===1,"source throw"));
a=await searchAndArchive(q,{...base,searchWips:async()=>({success:false})});tests.push(ok(a.archive==="NOT_RUN"&&calls===1,"bad provider"));
a=await searchAndArchive(q,{...base,archivePage:async()=>({status:"BLOCKED_POLICY"})});tests.push(ok(a.archive==="BLOCKED_POLICY"&&a.returned_count===1,"policy hold preserves list"));
a=await searchAndArchive(q,{...base,archivePage:async()=>({...verified,saved:2})});tests.push(ok(a.archive==="FAILED_OR_UNCONFIRMED","false success denied"));
a=await searchAndArchive(q,{...base,archivePage:async()=>({...verified,status:"REUSED_VERIFIED",saved:0,reused:1})});tests.push(ok(a.archive==="REUSED_VERIFIED"&&a.storage.saved===0,"reuse"));
a=await searchAndArchive(q,{...base,archivePage:async()=>({...verified,fulltext_missing:0})});tests.push(ok(a.archive==="FAILED_OR_UNCONFIRMED","state counts checked"));
let bad=false;try{await searchAndArchive({...q,page_size:51},base)}catch{bad=true}
tests.push(ok(bad,"cap"));
return tests;
})();
console.log(tests.length+'/'+tests.length+' PASS');
