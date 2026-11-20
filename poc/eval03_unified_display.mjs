// EVAL-03 P0-3: unified read-only ChatGPT presentation.
// Both MCPs must already be authorized in the invoking ChatGPT session.
// NAS excerpts are only those verified during AI review; WIPS fallback never
// receives private NAS content. This does not install a persistent MCP server.
import {runPatentRouter,ROUTE} from './eval03_patent_router.mjs';
import {getSelectedWipsPatentDetail} from './eval03_wips_detail.mjs';

function clean(input,max=300){
  if(typeof input!=='string')return null;
  const value=input.replace(/<script\b[^>]*>[\s\S]*?<\/script\s*>/gi,' ')
    .replace(/<style\b[^>]*>[\s\S]*?<\/style\s*>/gi,' ')
    .replace(/<[^>]*>/g,' ').replace(/[\u0000-\u001f\u007f]/g,' ')
    .replace(/\s+/g,' ').trim();
  return [...value].slice(0,max).join('')||null;
}
function nasPatent({selected,rank}){
  const safeTitle=clean(selected.title,240);
  if(!safeTitle||typeof selected.publication!=='string'||!selected.publication.trim()||
    typeof selected.country!=='string'||!selected.country||
    typeof selected.kind!=='string'||!selected.kind)throw Error('BAD_LOCAL_PATENT');
  const evidence=selected.evidence.map(e=>({
    section:e.section,excerpt:clean(e.excerpt,300)
  }));
  if(evidence.some(x=>!x.excerpt))throw Error('BAD_NAS_EVIDENCE');
  const abstract=evidence.find(x=>x.section==='abstract')?.excerpt??null;
  const claim=evidence.find(x=>x.section==='representative_claim')?.excerpt??null;
  return {rank:1,source:'NAS_RAG',country:selected.country,
    publicationNumber:selected.publication,documentKind:selected.kind,title:safeTitle,
    abstract,representativeClaim:claim,evidence,detailLevel:'EXCERPTS_ONLY',
    truncated:{title:[...selected.title].length>240,
      abstract:false,representativeClaim:false},
    localResultRank:rank};
}
function wipsPatent(x){
  return {rank:x.rank,source:'WIPS_MCP',country:x.country,
    publicationNumber:x.publicationNumber,documentKind:x.documentKind,
    title:x.title,abstract:x.abstract,representativeClaim:x.representativeClaim,
    evidence:[],detailLevel:'PREVIEW_ONLY',truncated:x.truncated};
}
const EMPTY={patents:[]};
export async function lookupPatentForUser(args={}){
  let approved=null;
  const router=await runPatentRouter({...args,
    onNasAccepted:async hit=>{
      // A validated onAccepted callback is called only after full provenance
      // and required-feature quote checks. Never persist this local reference.
      approved=nasPatent(hit);
    }});
  if(router.decision===ROUTE.LOCAL){
    if(!approved)return {status:'HOLD',source:'HOLD',...EMPTY,
      reason:'VERIFIED_NAS_RESULT_NOT_AVAILABLE',calls:router.calls};
    return {status:'PASS',source:'NAS_RAG',patents:[approved],
      resultCount:1,calls:router.calls,review:'AI_REVIEWED_GROUNDED',
      limitations:['NAS_EXCERPTS_ONLY','AI_NOT_INDEPENDENT_GOLD','NO_PDF_OR_DRAWINGS']};
  }
  if(router.decision===ROUTE.REMOTE||router.decision===ROUTE.EMPTY){
    const patents=(router.patents??[]).map(wipsPatent);
    return {status:router.decision===ROUTE.EMPTY?'NO_RESULTS':'PASS',
      source:'WIPS_MCP',patents,resultCount:patents.length,
      totalCount:router.totalCount??0,calls:router.calls,
      review:'WIPS_CANDIDATES_NOT_INDEPENDENTLY_VERIFIED',
      limitations:router.limitations??[]};
  }
  return {status:'HOLD',source:'HOLD',patents:[],
    resultCount:0,calls:router.calls,reason:router.decision};
}
export async function getUnifiedPatentDetail({
  lookup,index=1,getSpecText,pageSize=3000,descriptionOffset=0,claimsOffset=0
}={}){
  if(!lookup||lookup.status!=='PASS'||!Array.isArray(lookup.patents)||
    !Number.isSafeInteger(index)||index<1||index>lookup.patents.length)
    throw Error('BAD_DETAIL_SELECTION');
  const p=lookup.patents[index-1];
  if(p.rank!==index||!['NAS_RAG','WIPS_MCP'].includes(p.source)||
    p.source!==lookup.source)throw Error('BAD_DETAIL_SOURCE');
  if(p.source==='NAS_RAG'){
    // The NAS MCP intentionally exposes only bounded excerpts; it has no
    // fulltext reader. Do NOT use external WIPS to expand a private result.
    return {status:'EXCERPT_ONLY',source:'NAS_RAG',patent:p,
      description:{available:false,text:null,hasMore:false,nextOffset:null},
      claims:{available:false,text:null,hasMore:false,nextOffset:null},
      evidence:p.evidence,limitations:['NO_NAS_FULLTEXT_READER',
        'ORIGINAL_FULLTEXT_NOT_ACCESSED','NO_PDF_OR_DRAWING']};
  }
  const detail=await getSelectedWipsPatentDetail({
    selection:{country:p.country,publicationNumber:p.publicationNumber,
      documentKind:p.documentKind},pageSize,descriptionOffset,claimsOffset,
    getSpecText
  });
  if(!['PASS','PARTIAL_SECTION_UNAVAILABLE'].includes(detail.status))
    return {status:'HOLD',source:'WIPS_MCP',patent:p,
      reason:detail.status,limitations:['DETAIL_READ_FAILED_OR_UNVERIFIED']};
  return {status:detail.status,source:'WIPS_MCP',patent:p,
    description:detail.description,claims:detail.claims,evidence:[],
    limitations:detail.limitations};
}
