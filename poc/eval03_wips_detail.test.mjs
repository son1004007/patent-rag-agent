import assert from 'node:assert/strict';
import {getSelectedWipsPatentDetail} from './eval03_wips_detail.mjs';
const selection={country:'KR',publicationNumber:'10-2026-0001234',documentKind:'A'};
const meta={ctry:'KR',doc_num:'10-2026-0001234',lang_cd:'KR'};
const d={success:true,section:'dtl_desc',data:{...meta,dtl_desc_list:[
 {lang_cd:'KR',dtl_desc:'<p>기술분야</p><p>전해질의 <b>내열성</b> 개선</p>'}]}};
const c={success:true,section:'all_claim',data:{...meta,cl_list:[
 {lang_cd:'KR',cl_num:'1',cl:'전해질을 포함하는 <b>시험</b> 구성'},
 {lang_cd:'KR',cl_num:'2',cl:'청구항1에 있어서 열안정성을 제공'}]}};
const arg=(extra={})=>({selection,getSpecText:async x=>x.section==='dtl_desc'?d:c,...extra});
let n=0;async function check(label,fn){assert.ok(await fn(),label);console.log('PASS',label);n++}
await check('reads two requested sections by public id, not SKEY',async()=>{
 const calls=[];const r=await getSelectedWipsPatentDetail(arg({getSpecText:async x=>{
 calls.push(x);return x.section==='dtl_desc'?d:c}}));
 return r.status==='PASS'&&calls.length===2&&calls.every(x=>x.mng_num===selection.publicationNumber&&
 x.mng_num_type==='M'&&x.doc_kind==='A'&&!('skey' in x));
});
await check('plain description and all numbered claims present',async()=>{
 const r=await getSelectedWipsPatentDetail(arg());
 return r.description.text.includes('내열성')&&r.claims.text.includes('청구항 1')&&
 r.claims.text.includes('청구항 2')&&r.claims.totalClaims===2&&!JSON.stringify(r).includes('<b>');
});
await check('description Unicode pages reconstruct full text',async()=>{
 const long='🙂전해질'.repeat(450);
 const getSpecText=async x=>x.section==='dtl_desc'?{...d,data:{...d.data,
 dtl_desc_list:[{lang_cd:'KR',dtl_desc:long}]}}:c;
 let a='',off=0,end=null,iterations=0,total=null;
 do{const r=await getSelectedWipsPatentDetail(arg({pageSize:111,descriptionOffset:off,
 getSpecText}));a+=r.description.text;total=r.description.totalChars;
 end=r.description.nextOffset;off=end??0;if(++iterations>40)throw Error('LOOP');}while(end!==null);
 return a===long&&[...a].length===total;
});
await check('claim pages reconstruct every claim with boundaries',async()=>{
 let a='',off=0,end=null,iterations=0,total=null;
 do{const r=await getSelectedWipsPatentDetail(arg({pageSize:17,claimsOffset:off}));
 a+=r.claims.text;total=r.claims.totalChars;end=r.claims.nextOffset;
 off=end??0;if(++iterations>50)throw Error('LOOP');}while(end!==null);
 return a.includes('청구항 1\n')&&a.includes('청구항 2\n')&&[...a].length===total;
});
await check('invalid public ID rejected without provider call',async()=>{
 let calls=0;try{await getSelectedWipsPatentDetail(arg({
 selection:{...selection,publicationNumber:'10-abc; rm -rf /'},getSpecText:async()=>{calls++}}));return false}
 catch(e){return e.message==='INVALID_DETAIL_REQUEST'&&calls===0}
});
await check('invalid offsets and page size rejected',async()=>{
 try{await getSelectedWipsPatentDetail(arg({descriptionOffset:-1}));return false}
 catch(e){if(e.message!=='INVALID_DETAIL_REQUEST')return false}
 try{await getSelectedWipsPatentDetail(arg({pageSize:4001}));return false}
 catch(e){return e.message==='INVALID_DETAIL_REQUEST'}
});
await check('different patent number never accepted',async()=>{
 const r=await getSelectedWipsPatentDetail(arg({getSpecText:async x=>x.section==='dtl_desc'?
 {...d,data:{...d.data,doc_num:'10-9999-9999999'}}:c}));
 return r.status==='WIPS_DOCUMENT_IDENTITY_OR_RESPONSE_MISMATCH'&&!('description' in r);
});
await check('different country never accepted',async()=>{
 const r=await getSelectedWipsPatentDetail(arg({getSpecText:async x=>x.section==='dtl_desc'?
 d:{...c,data:{...c.data,ctry:'US'}}}));
 return r.status==='WIPS_DOCUMENT_IDENTITY_OR_RESPONSE_MISMATCH';
});
await check('incorrect section never accepted',async()=>{
 const r=await getSelectedWipsPatentDetail(arg({getSpecText:async x=>x.section==='dtl_desc'?
 d:{success:true,section:'dtl_desc',data:{...c.data}}}));
 return r.status==='WIPS_DOCUMENT_IDENTITY_OR_RESPONSE_MISMATCH'||
 r.status==='WIPS_DETAIL_INVALID_SECTION';
});
await check('provider thrown secret does not leak',async()=>{
 const r=await getSelectedWipsPatentDetail(arg({getSpecText:async()=>{throw Error('SECRET')}}));
 return r.status==='WIPS_DETAIL_READ_FAILED'&&!JSON.stringify(r).includes('SECRET');
});
await check('malformed claim blocks entire response',async()=>{
 const r=await getSelectedWipsPatentDetail(arg({getSpecText:async x=>x.section==='dtl_desc'?
 d:{...c,data:{...c.data,cl_list:[{cl_num:'1',cl:{secret:true}}]}}}));
 return r.status==='WIPS_DETAIL_INVALID_SECTION'&&!('description' in r);
});
await check('missing claims is explicitly PARTIAL',async()=>{
 const r=await getSelectedWipsPatentDetail(arg({getSpecText:async x=>x.section==='dtl_desc'?
 d:{...c,data:{...c.data,cl_list:[]}}}));
 return r.status==='PARTIAL_SECTION_UNAVAILABLE'&&r.claims.totalClaims===0&&
 r.claims.available===false&&r.description.available===true;
});
await check('missing description is explicitly PARTIAL',async()=>{
 const r=await getSelectedWipsPatentDetail(arg({getSpecText:async x=>x.section==='dtl_desc'?
 {...d,data:{...d.data,dtl_desc_list:[]}}:c}));
 return r.status==='PARTIAL_SECTION_UNAVAILABLE'&&!r.description.available;
});
await check('out of range page fails without text leakage',async()=>{
 const r=await getSelectedWipsPatentDetail(arg({claimsOffset:99999}));
 return r.status==='PAGE_OFFSET_OUT_OF_RANGE'&&!('claims' in r);
});
await check('HTML script and style are not exposed',async()=>{
 const r=await getSelectedWipsPatentDetail(arg({getSpecText:async x=>x.section==='dtl_desc'?
 {...d,data:{...d.data,dtl_desc_list:[{lang_cd:'KR',
 dtl_desc:'A<script>alert(secret)</script>B<style>hidden</style><br>C'}]}}:c}));
 return r.description.text==='A B\nC'&&!JSON.stringify(r).includes('secret');
});
await check('provider raw SKEY/metadata is not returned',async()=>{
 const r=await getSelectedWipsPatentDetail(arg({getSpecText:async x=>x.section==='dtl_desc'?
 {...d,data:{...d.data,dtl_desc_list:[{...d.data.dtl_desc_list[0],skey:'SECRET_PRIVATE'}],
 SECRET:'ACCESS_TOKEN'}}:{...c,raw:'WIPS_PRIVATE'}}));
 return !/SECRET_PRIVATE|ACCESS_TOKEN|WIPS_PRIVATE|skey/.test(JSON.stringify(r));
});
await check('JSON text-wrapper provider supported',async()=>{
 const r=await getSelectedWipsPatentDetail(arg({getSpecText:async x=>({
 text:JSON.stringify(x.section==='dtl_desc'?d:c)})}));
 return r.status==='PASS';
});
await check('response language follows WIPS actual fallback',async()=>{
 const r=await getSelectedWipsPatentDetail(arg({getSpecText:async x=>x.section==='dtl_desc'?
 {...d,data:{...d.data,lang_cd:'US',dtl_desc_list:[{lang_cd:'US',dtl_desc:'English text'}]}}:c}));
 return r.status==='PASS'&&r.description.language==='US'&&r.claims.language==='KR';
});
console.log('EVAL03_DETAIL_PASS',n);