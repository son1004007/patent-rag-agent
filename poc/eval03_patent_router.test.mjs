import assert from 'node:assert/strict';
import {runPatentRouter,ROUTE} from './eval03_patent_router.mjs';
const A='a'.repeat(64),B='b'.repeat(64),Q='Solar encapsulant edge protection';
const E={section:'abstract',start_offset:0,end_offset:35,chunk_sha256:B,
  excerpt:'Synthetic solar encapsulant has a waterproof sealing edge around the solar module'};
const row={document_id:'PAT-'+A,publication:'2026-00001',country:'KR',kind:'A',
  title:'Synthetic solar encapsulant edge protection',provider:'SYNTHETIC',
  source_sha256:A,section:E.section,chunk_sha256:B,start_offset:0,end_offset:35,
  excerpt:E.excerpt,distance:0.15};
const nas=items=>({scope:'private_purchased_patents_local_only',
  ranking:'exact_cosine_best_chunk_per_document',results:items});
const info={found:true,...row,evidence:[E]};
const goodWips={success:true,data:{total_count:1,row_list:[{SKEY:'1234567890123',TIK:'Synthetic example',
  XN_D:'2026-00003',CC:'KR',KC_D:'A',ABK:'Public test abstract',CLK:'Public test claim'}]}};
const args=(x={})=>({caseId:'Q01',group:'IN',query:Q,wipsQuery:'(solar).ti,ab.',
  searchNas:async()=>nas([row]),detailNas:async()=>info,
  reviewNas:async()=>({rank:1,label:2,section:E.section,chunkSha256:B,
    quote:'Synthetic solar encapsulant',rationale:'The synthetic technical evidence explicitly explains the requested encapsulant and edge design.'}),
  searchWips:async()=>goodWips,...x});
let n=0;
async function check(name,fn){assert.ok(await fn(),name);console.log('PASS',name);n++;}
await check('local evidence routes to NAS only',async()=>{
  let remote=0;const r=await runPatentRouter(args({searchWips:async()=>{remote++;return goodWips}}));
  return r.decision===ROUTE.LOCAL&&remote===0&&r.calls.nasSearch===2&&r.calls.nasDetail===1&&r.calls.wips===0;
});
await check('missing relevant local evidence falls back to WIPS once',async()=>{
  const r=await runPatentRouter(args({reviewNas:async()=>null}));
  return r.decision===ROUTE.REMOTE&&r.source==='WIPS_MCP'&&r.calls.wips===1&&r.returnedCount===1;
});
await check('no NAS hits goes to WIPS',async()=>{
  const r=await runPatentRouter(args({searchNas:async()=>nas([])}));
  return r.decision===ROUTE.REMOTE&&r.calls.nasSearch===2&&r.calls.nasDetail===0;
});
await check('unstable local evidence must not be called absent',async()=>{
  let i=0,w=0;const r=await runPatentRouter(args({searchNas:async()=>i++?nas([]):nas([row]),
    searchWips:async()=>{w++;return goodWips}}));
  return r.decision===ROUTE.BLOCK&&r.calls.wips===0&&w===0;
});
await check('NAS tool failure blocks WIPS',async()=>{
  const r=await runPatentRouter(args({searchNas:async()=>{throw Error('private error')}}));
  return r.decision===ROUTE.BLOCK&&r.calls.wips===0;
});
await check('missing reviewer blocks both providers',async()=>{
  let i=0;const r=await runPatentRouter(args({reviewNas:null,
    searchNas:async()=>{i++;return nas([])}}));
  return r.decision===ROUTE.BLOCK&&i===0&&r.calls.wips===0;
});
await check('freshness requirement blocks both providers',async()=>{
  const r=await runPatentRouter(args({freshnessRequired:true}));
  return r.decision===ROUTE.BLOCK&&r.calls.nasSearch===0&&r.calls.wips===0;
});
await check('wips tool exception returns safe hold',async()=>{
  const r=await runPatentRouter(args({reviewNas:async()=>null,
    searchWips:async()=>{throw Error('credential_very_secret')}}));
  return r.decision===ROUTE.ERROR&&!JSON.stringify(r).includes('credential');
});
await check('invalid WIPS data returns hold',async()=>{
  const r=await runPatentRouter(args({reviewNas:async()=>null,
    searchWips:async()=>({success:true,data:{total_count:2,row_list:[{SKEY:'x'}]}})}));
  return r.decision===ROUTE.ERROR;
});
await check('no WIPS matches is explicit no results',async()=>{
  const r=await runPatentRouter(args({reviewNas:async()=>null,
    searchWips:async()=>({success:true,data:{total_count:0,row_list:[]}})}));
  return r.decision===ROUTE.EMPTY&&r.returnedCount===0&&r.calls.wips===1;
});
await check('router never outputs private evidence or provider identifiers',async()=>{
  const r=await runPatentRouter(args({reviewNas:async()=>null}));
  return !JSON.stringify(r).includes('PAT-')&&!JSON.stringify(r).includes('1234567890123')&&
    !JSON.stringify(r).includes('waterproof sealing edge');
});
await check('no false WIPS when quotation is fabricated',async()=>{
  const r=await runPatentRouter(args({reviewNas:async()=>({rank:1,label:2,section:E.section,
    chunkSha256:B,quote:'fabricated quote value',rationale:'This text is not in evidence and must not trigger automatic WIPS.'})}));
  return r.decision===ROUTE.BLOCK&&r.calls.wips===0;
});
await check('router rejects blank WIPS query',async()=>{
  try{await runPatentRouter(args({wipsQuery:''}));return false}catch{return true}
});
await check('remote query is independent of NAS private query',async()=>{
  let passed=null;await runPatentRouter(args({query:'Private query must never be sent to WIPS',
    reviewNas:async()=>null,searchWips:async p=>{passed=p;return goodWips}}));
  return passed?.query==='(solar).ti,ab.'&&!JSON.stringify(passed).includes('Private query');
});
console.log('EVAL03_ROUTER_PASS',n);
