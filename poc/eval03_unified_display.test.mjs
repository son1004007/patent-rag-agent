import assert from 'node:assert/strict';
import {lookupPatentForUser,getUnifiedPatentDetail} from './eval03_unified_display.mjs';
const S='a'.repeat(64),H='b'.repeat(64);
const e1={section:'abstract',start_offset:0,end_offset:50,chunk_sha256:H,
 excerpt:'Synthetic solar encapsulant waterproof sealing around the edges'},
e2={section:'representative_claim',start_offset:60,end_offset:115,chunk_sha256:H,
 excerpt:'Synthetic claim for photovoltaic encapsulant sealing technology'};
const local={found:true,document_id:'PAT-'+S,publication:'10-2026-1234',
 country:'KR',kind:'A',title:'Solar encapsulant <b>edge</b> sealing',
 provider:'SYNTHETIC',source_sha256:S,evidence:[e1,e2]};
const row={...local,section:e1.section,chunk_sha256:e1.chunk_sha256,
 start_offset:0,end_offset:50,excerpt:e1.excerpt,distance:0.08};
const nas=rows=>({scope:'private_purchased_patents_local_only',
 ranking:'exact_cosine_best_chunk_per_document',results:rows});
const wips={success:true,data:{total_count:9,row_list:[{
 SKEY:'1234567890123',XN_D:'10-2026-4444',CC:'KR',KC_D:'A',TIK:'Battery electrolyte',
 ABK:'Lithium electrolyte heat resistance',CLK:'Lithium battery safety claim'}]}};
const detailMeta={ctry:'KR',doc_num:'10-2026-4444',lang_cd:'KR'};
const desc={success:true,section:'dtl_desc',data:{...detailMeta,
 dtl_desc_list:[{lang_cd:'KR',dtl_desc:'<p>Battery electrolyte technical description</p>'}]}};
const claims={success:true,section:'all_claim',data:{...detailMeta,
 cl_list:[{lang_cd:'KR',cl_num:'1',cl:'A first synthetic battery claim'}]}};
const base=(other={})=>({caseId:'Q01',group:'IN',query:'solar encapsulant',
 wipsQuery:'(solar).ti,ab.',searchNas:async()=>nas([row]),
 detailNas:async()=>local,
 reviewNas:async()=>({rank:1,label:2,section:'abstract',chunkSha256:H,
 quote:'Synthetic solar encapsulant',rationale:'Synthetic evidence supports the selected encapsulant sealing technology.'}),
 searchWips:async()=>wips,...other});
let n=0;async function check(s,fn){assert.ok(await fn(),s);console.log('PASS',s);n++}
await check('accepted NAS yields unified document and bounded citations',async()=>{
 const x=await lookupPatentForUser(base());
 const p=x.patents?.[0];
 return x.source==='NAS_RAG'&&x.status==='PASS'&&x.calls.wips===0&&
 p.source==='NAS_RAG'&&p.publicationNumber===local.publication&&
 p.title==='Solar encapsulant edge sealing'&&p.abstract.includes('Synthetic solar')&&
 p.representativeClaim.includes('Synthetic claim')&&p.evidence.length===2&&
 p.detailLevel==='EXCERPTS_ONLY'&&p.localResultRank===1;
});
await check('NAS output contains no private document ID, SHA or provider raw JSON',async()=>{
 const x=await lookupPatentForUser(base()),s=JSON.stringify(x);
 return !s.includes(S)&&!s.includes(H)&&!s.includes('PAT-')&&
 !s.includes('SYNTHETIC"')&&!s.includes('"source_sha256"');
});
await check('accepted NAS does not call WIPS',async()=>{
 let count=0;const x=await lookupPatentForUser(base({searchWips:async()=>{count++;return wips}}));
 return x.status==='PASS'&&x.source==='NAS_RAG'&&count===0;
});
await check('accepted NAS detail only returns authorized excerpts',async()=>{
 const x=await lookupPatentForUser(base());
 const d=await getUnifiedPatentDetail({lookup:x,index:1,getSpecText:async()=>{throw Error('never')}});
 return d.status==='EXCERPT_ONLY'&&d.source==='NAS_RAG'&&d.evidence.length===2&&
 d.description.available===false&&d.claims.available===false;
});
await check('NAS missing evidence falls back to WIPS with uniform keys',async()=>{
 let used=0;const x=await lookupPatentForUser(base({
 reviewNas:async()=>null,searchWips:async()=>{used++;return wips}}));
 const p=x.patents?.[0];return used===1&&x.source==='WIPS_MCP'&&x.status==='PASS'&&
 p.rank===1&&p.country==='KR'&&p.publicationNumber==='10-2026-4444'&&
 p.title==='Battery electrolyte'&&p.abstract.includes('Lithium')&&
 p.representativeClaim.includes('Lithium')&&p.detailLevel==='PREVIEW_ONLY'&&p.evidence.length===0;
});
await check('WIPS detail uses exactly selected returned publication',async()=>{
 const x=await lookupPatentForUser(base({reviewNas:async()=>null})),calls=[];
 const d=await getUnifiedPatentDetail({lookup:x,getSpecText:async a=>{
 calls.push(a);return a.section==='dtl_desc'?desc:claims}});
 return d.status==='PASS'&&d.source==='WIPS_MCP'&&d.description.text.includes('Battery')&&
 d.claims.totalClaims===1&&calls.length===2&&calls.every(a=>
 a.mng_num==='10-2026-4444'&&a.mng_num_type==='M'&&!('skey' in a));
});
await check('wrong WIPS detail identity becomes HOLD',async()=>{
 const x=await lookupPatentForUser(base({reviewNas:async()=>null}));
 const d=await getUnifiedPatentDetail({lookup:x,getSpecText:async a=>a.section==='dtl_desc'?
 desc:{...claims,data:{...claims.data,doc_num:'10-2026-9999'}}});
 return d.status==='HOLD'&&d.reason==='WIPS_DOCUMENT_IDENTITY_OR_RESPONSE_MISMATCH'&&
 !('description' in d);
});
await check('NAS read error is HOLD, not WIPS fallback',async()=>{
 let remote=0;const x=await lookupPatentForUser(base({
 searchNas:async()=>{throw Error('offline')},searchWips:async()=>{remote++;return wips}}));
 return x.status==='HOLD'&&x.patents.length===0&&remote===0;
});
await check('invalid AI quote becomes HOLD, not WIPS fallback',async()=>{
 let remote=0;const x=await lookupPatentForUser(base({
 reviewNas:async()=>({rank:1,label:2,section:'abstract',chunkSha256:H,
 quote:'forged technical evidence here',rationale:'A fake quote cannot permit a local result.'}),
 searchWips:async()=>{remote++;return wips}}));
 return x.status==='HOLD'&&x.patents.length===0&&remote===0;
});
await check('new capture callback failure is fail closed without WIPS',async()=>{
 let remote=0;const x=await lookupPatentForUser(base({
 detailNas:async()=>({...local,publication:null}),
 searchWips:async()=>{remote++;return wips}}));
 return x.status==='HOLD'&&remote===0;
});
await check('missing WIPS results gives empty standardized list',async()=>{
 const x=await lookupPatentForUser(base({reviewNas:async()=>null,
 searchWips:async()=>({success:true,data:{total_count:0,row_list:[]}})}));
 return x.status==='NO_RESULTS'&&x.source==='WIPS_MCP'&&x.patents.length===0;
});
await check('WIPS provider exception is sanitized HOLD',async()=>{
 const x=await lookupPatentForUser(base({reviewNas:async()=>null,
 searchWips:async()=>{throw Error('TOP_SECRET')}}));
 return x.status==='HOLD'&&x.source==='HOLD'&&!JSON.stringify(x).includes('TOP_SECRET');
});
await check('freshness request does not invoke either source',async()=>{
 let calls=0;const x=await lookupPatentForUser(base({freshnessRequired:true,
 searchNas:async()=>{calls++},searchWips:async()=>{calls++}}));
 return x.status==='HOLD'&&x.patents.length===0&&calls===0;
});
await check('invalid selection index rejected, no provider access',async()=>{
 const x=await lookupPatentForUser(base({reviewNas:async()=>null}));
 let used=0;try{await getUnifiedPatentDetail({lookup:x,index:2,
 getSpecText:async()=>{used++}});return false}
 catch(e){return e.message==='BAD_DETAIL_SELECTION'&&used===0}
});
await check('malicious unbound selection cannot request arbitrary WIPS patent',async()=>{
 const x=await lookupPatentForUser(base({reviewNas:async()=>null}));
 const forged={...x,patents:[{...x.patents[0],source:'NAS_RAG'}]};
 try{await getUnifiedPatentDetail({lookup:forged,getSpecText:async()=>{throw Error('unexpected')}});return false}
 catch(e){return e.message==='BAD_DETAIL_SOURCE'}
});
await check('WIPS raw private SKEY never appears in response',async()=>{
 const x=await lookupPatentForUser(base({reviewNas:async()=>null}));
 return !JSON.stringify(x).includes('1234567890123')&&!JSON.stringify(x).includes('SKEY');
});
await check('plain tag handling does not turn markup into executable content',async()=>{
 const p={...local,title:'<script>alert("x")</script>Solar'},
   x=await lookupPatentForUser(base({detailNas:async()=>p,
    searchNas:async()=>nas([{...row,title:p.title}])}));
 return x.status==='PASS'&&x.patents[0].title==='Solar'&&
 !JSON.stringify(x).includes('alert');
});
await check('false evidence callback not invoked until grounding checks passed',async()=>{
 let calls=0;const x=await lookupPatentForUser(base({
 reviewNas:async()=>({rank:1,label:2,section:'abstract',chunkSha256:H,
 quote:'imagined fabricated evidence',rationale:'not grounded in actual evidence.'}),
 searchWips:async()=>{calls++;return wips}}));
 return x.status==='HOLD'&&calls===0;
});
console.log('EVAL03_UNIFIED_PASS',n);