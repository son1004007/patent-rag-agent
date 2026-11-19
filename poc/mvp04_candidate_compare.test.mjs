import {integrateCandidates} from "./mvp04_candidate_compare.mjs";
function runTests(f){
  const h="a".repeat(64),e={section:"abstract",start_offset:0,end_offset:32,excerpt:"Seal film reduces moisture and improves optical transmission",chunk_sha256:h};
  const n={document_id:"PAT-"+h,publication:"123-456",country:"KR",kind:"B1",title:"Seal film",provider:"WIPS",source_sha256:h,distance:.1,...e};
  const N={scope:"private_purchased_patents_local_only",ranking:"exact_cosine_best_chunk_per_document",results:[n]};
  const w={SKEY:"1",XN_D:"123456",CC:"KR",KC_D:"B1",TIK:"Seal film",ABK:"moisture and optical transmission",CLK:"seal film"};
  const W={success:true,data:{row_list:[w]}},C={target:["seal"],properties:[{name:"moisture",terms:["moisture"]},{name:"optical",terms:["optical"]}],excludeTitle:["recycling"]},D={...n,found:true,evidence:[e]};
  let count=0;const ok=b=>{if(!b)throw Error("assertion "+(count+1));count++};const bad=fn=>{let t=false;try{fn()}catch{t=true}ok(t)};
  let r=f(N,W,[D],C);ok(r.counts.unique===1&&r.counts.duplicates===1);ok(r.candidates[0].sources.NAS.rank===1&&r.candidates[0].sources.WIPS.rank===1);ok(r.candidates[0].decision==="REVIEW_CANDIDATE");ok(r.candidates[0].evidence.length===3);ok(r.candidates[0].properties.every(p=>p.mentions.length>0));ok(r.warning.includes("not validated"));
  r=f(N,{success:true,data:{row_list:[{...w,KC_D:"A"}]}},[],C);ok(r.counts.unique===2);
  r=f(N,{success:true,data:{row_list:[{...w,CC:"JP"}]}},[],C);ok(r.counts.unique===2);
  ok(f(null,W,[],C).candidates[0].decision==="HOLD");ok(f(N,null,[],C).candidates[0].decision==="HOLD");
  ok(f(null,W,[],{...C,target:["unrelated"]}).candidates[0].decision==="EXCLUDE");
  ok(f(null,{success:true,data:{row_list:[{...w,TIK:"seal recycling"}]}},[],C).candidates[0].reason==="EXCLUDED_TITLE");
  ok(f(N,W,[],{...C,properties:[{name:"missing",terms:["xyzxyz"]}]}).candidates[0].reason==="PROPERTY_EVIDENCE_MISSING");
  r=f(null,{success:true,data:{row_list:[{...w,ABK:"x".repeat(400)}]}},[],C);ok(r.candidates[0].evidence[0].truncated&&r.candidates[0].evidence[0].end===300);ok(f(null,null,[],C).counts.unique===0);
  bad(()=>f({...N,scope:"synthetic"},W,[],C));bad(()=>f({...N,results:[n,n]},W,[],C));bad(()=>f(N,{success:true,data:{row_list:[w,w]}},[],C));bad(()=>f(N,W,[{...D,source_sha256:"b".repeat(64)}],C));bad(()=>f(N,W,[{...D,document_id:"PAT-"+"b".repeat(64)}],C));bad(()=>f(N,W,[{...D,evidence:[{...e,end_offset:301}]}],C));bad(()=>f(N,W,[{...D,evidence:[{...e,excerpt:"x".repeat(301)}]}],C));bad(()=>f(N,{success:false},[],C));bad(()=>f(N,W,[],{...C,target:[]}));bad(()=>f(N,W,[D,D],C));bad(()=>f(N,{success:true,data:{row_list:[{...w,XN_D:"123@456"}]}},[],C));bad(()=>f({...N,results:[{...n,distance:NaN}]},W,[],C));return count;
}
console.log("PASS",runTests(integrateCandidates));
