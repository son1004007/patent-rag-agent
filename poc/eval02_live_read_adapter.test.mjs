import assert from 'node:assert/strict';
import {runNasReadOnlyReview,REASON} from './eval02_live_read_adapter.mjs';
const A='a'.repeat(64),B='b'.repeat(64);
const ev={section:'representative_claim',start_offset:0,end_offset:37,chunk_sha256:B,
  excerpt:'Synthetic photovoltaic encapsulant keeps water outside the panel'};
const row={document_id:'PAT-'+A,publication:'2026-00001',country:'KR',kind:'A',
 title:'Synthetic solar encapsulant',provider:'SYNTHETIC',source_sha256:A,
 section:ev.section,start_offset:ev.start_offset,end_offset:ev.end_offset,chunk_sha256:ev.chunk_sha256,
 excerpt:ev.excerpt,distance:0.17};
const searchResult=rows=>({scope:'private_purchased_patents_local_only',
 ranking:'exact_cosine_best_chunk_per_document',results:rows});
const doc={...row,found:true,evidence:[ev]};
const input=(x={})=>({caseId:'Q01',group:'IN',query:'Synthetic solar moisture proofing',
 search:async()=>searchResult([row]),detail:async()=>doc,
 review:async()=>({rank:1,label:2,section:ev.section,chunkSha256:B,
 quote:'Synthetic photovoltaic encapsulant',rationale:'This patent explicitly describes synthetic solar moisture protection.'}),...x});
let n=0;
async function check(name,fn){assert.ok(await fn(),name);n++;console.log('PASS',name);}
await check('real adapter accepts signed claim',async()=>{const a=await runNasReadOnlyReview(input());return a.decision===REASON.VALID&&a.aiGrounded===true&&a.calls.nasSearch===2&&a.calls.nasDetail===1});
await check('never reveals patent identifiers',async()=>{const a=await runNasReadOnlyReview(input());return !JSON.stringify(a).includes('PAT-')&&!JSON.stringify(a).includes('Synthetic photovoltaic')});
await check('freshness bypasses all external reads',async()=>{let used=0;const a=await runNasReadOnlyReview(input({freshnessRequired:true,search:async()=>{used++;return searchResult([row])}}));return a.decision===REASON.FRESH&&used===0});
await check('missing reviewer never reads private data',async()=>{let used=0;const a=await runNasReadOnlyReview(input({review:null,search:async()=>{used++;return searchResult([row])}}));return a.decision===REASON.REVIEW&&used===0});
await check('candidate without direct claim is held',async()=>{const a=await runNasReadOnlyReview(input({review:async()=>null}));return a.decision===REASON.MISSING&&!a.aiGrounded});
await check('rank null held',async()=>{const a=await runNasReadOnlyReview(input({review:async()=>({rank:null})}));return a.decision===REASON.MISSING});
await check('unverified label held',async()=>{const a=await runNasReadOnlyReview(input({review:async()=>({rank:1,label:1})}));return a.decision===REASON.MISSING});
await check('unverified rank held',async()=>{const a=await runNasReadOnlyReview(input({review:async()=>({rank:2,label:2})}));return a.decision===REASON.MISSING});
await check('quote mismatch blocks',async()=>{const a=await runNasReadOnlyReview(input({review:async()=>({rank:1,label:2,section:ev.section,chunkSha256:B,quote:'This claim is not actually present here',rationale:'Twenty characters of an invalid rationale text'})}));return a.decision===REASON.GROUND});
await check('hash mismatch blocks',async()=>{const a=await runNasReadOnlyReview(input({review:async()=>({rank:1,label:2,section:ev.section,chunkSha256:A,quote:'Synthetic photovoltaic encapsulant',rationale:'Twenty characters of another example'})}));return a.decision===REASON.GROUND});
await check('short rationale blocks',async()=>{const a=await runNasReadOnlyReview(input({review:async()=>({rank:1,label:2,section:ev.section,chunkSha256:B,quote:'Synthetic photovoltaic encapsulant',rationale:'short'})}));return a.decision===REASON.GROUND});
await check('changed document source blocks',async()=>{const a=await runNasReadOnlyReview(input({detail:async()=>({...doc,source_sha256:B})}));return a.decision===REASON.BAD});
await check('changed publication blocks',async()=>{const a=await runNasReadOnlyReview(input({detail:async()=>({...doc,publication:'OTHER'})}));return a.decision===REASON.BAD});
await check('missing source blocks',async()=>{const a=await runNasReadOnlyReview(input({search:async()=>searchResult([{...row,document_id:'SECRET'}])}));return a.decision===REASON.BAD});
await check('reordering between reads blocks',async()=>{let calls=0;const a=await runNasReadOnlyReview(input({search:async()=>{calls++;return searchResult(calls===1?[row,{...row,document_id:'PAT-'+B,source_sha256:B,chunk_sha256:A}]:[{...row,document_id:'PAT-'+B,source_sha256:B,chunk_sha256:A},row])}}));return a.decision===REASON.BAD});
await check('read failure returns no error details',async()=>{const a=await runNasReadOnlyReview(input({search:async()=>{throw Error('SENSITIVE_PRIVATE_BACKEND_NAME')}}));return a.decision===REASON.SEARCH&&!JSON.stringify(a).includes('SENSITIVE')});
await check('detail failure has no leak',async()=>{const a=await runNasReadOnlyReview(input({detail:async()=>{throw Error('CREDENTIAL')}}));return a.decision===REASON.DETAIL&&!JSON.stringify(a).includes('CREDENTIAL')});
await check('review failure has no leak',async()=>{const a=await runNasReadOnlyReview(input({review:async()=>{throw Error('PRIVATE')}}));return a.decision===REASON.REVIEW&&!JSON.stringify(a).includes('PRIVATE')});
await check('source with no matches holds',async()=>{const a=await runNasReadOnlyReview(input({search:async()=>searchResult([])}));return a.decision===REASON.MISSING&&a.calls.nasDetail===0});
await check('bad query rejects',async()=>{try{await runNasReadOnlyReview(input({query:''}));return false}catch{return true}});
await check('malformed detail zero evidence blocks',async()=>{const a=await runNasReadOnlyReview(input({detail:async()=>({...doc,evidence:[]})}));return a.decision===REASON.BAD});
await check('tool text wrapper accepted',async()=>{const a=await runNasReadOnlyReview(input({search:async()=>({text:JSON.stringify(searchResult([row]))}),detail:async()=>({text:JSON.stringify(doc)})}));return a.decision===REASON.VALID});
await check('no network/token/write APIs embedded',async()=>{const a=await runNasReadOnlyReview(input());return a.calls.wips===0&&a.source==='NAS_LOCAL_READ_ONLY'});

await check('multi excerpt requirements from same patent accepted',async()=>{
 const req=['solar_target','water_protection'];
 const e1={section:'abstract',start_offset:0,end_offset:48,chunk_sha256:A,excerpt:'Synthetic solar encapsulant blocks incoming moisture at the edge'};
 const detailed={...doc,evidence:[ev,e1]};
 const x=input({requiredFeatures:req,detail:async()=>detailed,review:async()=>({
   rank:1,label:2,section:ev.section,chunkSha256:ev.chunk_sha256,quote:'Synthetic photovoltaic encapsulant',
   rationale:'The claim and abstract support distinct aspects of this same synthetic construction.',
   featureEvidence:[{feature:'solar_target',section:ev.section,chunkSha256:B,quote:'Synthetic photovoltaic encapsulant'},
    {feature:'water_protection',section:'abstract',chunkSha256:A,quote:'encapsulant blocks incoming moisture'}]
 })});
 const r=await runNasReadOnlyReview(x);
 return r.decision===REASON.VALID&&r.verifiedFeatureCount===2&&!JSON.stringify(r).includes('blocks incoming');
});
await check('multiple features missing one source blocked',async()=>{
 const r=await runNasReadOnlyReview(input({requiredFeatures:['target','mechanism']}));
 return r.decision===REASON.GROUND;
});
await check('duplicate feature evidence blocked',async()=>{
 const r=await runNasReadOnlyReview(input({requiredFeatures:['target','mechanism'],review:async()=>({
 rank:1,label:2,section:ev.section,chunkSha256:B,quote:'Synthetic photovoltaic encapsulant',
 rationale:'Evidence is not enough to demonstrate two distinct technical requirements.',
 featureEvidence:[{feature:'target',section:ev.section,chunkSha256:B,quote:'Synthetic photovoltaic encapsulant'},
 {feature:'target',section:ev.section,chunkSha256:B,quote:'Synthetic photovoltaic encapsulant'}]
 })}));
 return r.decision===REASON.GROUND;
});
await check('invalid extra features rejected before NAS',async()=>{
 try{await runNasReadOnlyReview(input({requiredFeatures:['target','target']}));return false}catch{return true}
});
await check('invalid feature identifier rejected',async()=>{
 try{await runNasReadOnlyReview(input({requiredFeatures:['__proto__']}));return false}catch{return true}
});
await check('feature evidence from a different chunk blocked',async()=>{
 const r=await runNasReadOnlyReview(input({requiredFeatures:['target'],review:async()=>({
 rank:1,label:2,section:ev.section,chunkSha256:B,quote:'Synthetic photovoltaic encapsulant',
 rationale:'This evidence has a fabricated feature citation and must not be accepted.',
 featureEvidence:[{feature:'target',section:ev.section,chunkSha256:A,quote:'Synthetic photovoltaic encapsulant'}]
 })}));
 return r.decision===REASON.GROUND;
});

console.log('EVAL02_LIVE_ADAPTER_PASS',n);
